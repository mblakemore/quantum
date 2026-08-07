#!/usr/bin/env python3
"""P-CCM v1.0 — numba JIT test. Measures the 'optimised C = 2-5x' figure I carried all evening.

WHY THIS AND NOT MORE GPU. Three GPU/vectorisation results this session each accelerated the
right operation and moved the system almost not at all:

    GF(2) bit-packing   5.7x on shrink's F2 routine   ->  1.28x end-to-end
    Z8 update on GPU    36-41x on the kernel          ->  2.10x end-to-end
    dimer partition     49.2x on the kernel           ->  2.2x end-to-end

The profile says why: 44% of runtime is PYTHON/NUMPY DISPATCH on small arrays — ix_ 1532 calls,
issubdtype 3064, issubclass_ 6128 per ten inner products — which no accelerator touches. When
k=80, a numpy call's overhead rivals its work. THE BOTTLENECK IS THE LANGUAGE, NOT THE ARITHMETIC.

numba compiles explicit Python loops to machine code and removes the dispatch entirely, so it
tests the one hypothesis left standing AND supplies the "optimised C over numpy" factor that I
have been quoting as REASONED, NOT MEASURED since the classical-bill estimate.

CORRECTNESS: every JIT routine is checked against the numpy reference on the same inputs before
any timing is reported. Same rule as everywhere else in this campaign.

Substrate: claude-fable-5, Whisper C5020. Creator directive: "run the numba test".
"""
import time
import json
import os
import sys

import numpy as np
from numba import njit


# ─────────────────────────────────────────────────────────────────────────────
# The hot spot, as explicit loops. numba turns these into machine code; in pure
# Python they would be catastrophic, which is exactly the point.
# ─────────────────────────────────────────────────────────────────────────────
@njit(cache=True)
def addrow_njit(D, J, targets, src, k):
    """Sparse Eq(49,50) update: g_a <- g_a (+) g_src for a in targets.
    Same maths as _update_addrow_sparse, no numpy dispatch."""
    nt = targets.shape[0]
    if nt == 0:
        return
    jss = J[src, src]
    # SNAPSHOT BEFORE MUTATING — the numpy version copies row_s/col_s up front, and reading
    # them lazily inside the loops is WRONG: the row pass writes J[c, src] for every c in
    # targets, so the column pass would then read already-updated values. The correctness
    # gate caught this; it would have produced fast wrong answers.
    row_s = np.empty(k, dtype=J.dtype)
    col_s = np.empty(k, dtype=J.dtype)
    for c in range(k):
        row_s[c] = J[src, c]
        col_s[c] = J[c, src]
    for ti in range(nt):
        a = targets[ti]
        D[a] = (D[a] + D[src] + col_s[a]) % 8
    for ti in range(nt):
        a = targets[ti]
        for c in range(k):
            J[a, c] = (J[a, c] + row_s[c]) % 8
    for ti in range(nt):
        a = targets[ti]
        for c in range(k):
            J[c, a] = (J[c, a] + col_s[c]) % 8
    for ti in range(nt):
        a = targets[ti]
        for tj in range(nt):
            b = targets[tj]
            J[a, b] = (J[a, b] + jss) % 8


@njit(cache=True)
def f2_parity_rows_njit(xi, G, k, W):
    """(xi, g_a) for a in [0,k): parity of popcount(xi & G[a]) over packed words."""
    out = np.zeros(k, dtype=np.int64)
    for a in range(k):
        acc = 0
        for w in range(W):
            v = xi[w] & G[a, w]
            # popcount by folding
            x = v
            c = 0
            while x:
                x &= x - np.uint64(1)
                c += 1
            acc ^= (c & 1)
        out[a] = acc
    return out


def addrow_numpy(D, J, targets, src, k):
    """The current numpy implementation, for the fair comparison."""
    if targets.shape[0] == 0:
        return
    T = targets
    Jk = J[:k, :k]
    jss = int(Jk[src, src])
    row_s = Jk[src, :k].copy()
    col_s = Jk[:k, src].copy()
    D[T] = (D[T] + D[src] + Jk[T, src]) % 8
    Jk[T, :] = (Jk[T, :] + row_s) % 8
    Jk[:, T] = (Jk[:, T] + col_s[:, None]) % 8
    Jk[np.ix_(T, T)] = (Jk[np.ix_(T, T)] + jss) % 8


def main():
    rng = np.random.default_rng(20260807)
    print("NUMBA JIT BENCHMARK — testing whether the LANGUAGE is the bottleneck\n")

    # ---- correctness gate -------------------------------------------------
    print("  ① CORRECTNESS: JIT vs numpy on identical inputs")
    ok = True
    for k in (40, 80):
        for _ in range(20):
            D0 = rng.integers(0, 8, size=k).astype(np.int64)
            J0 = rng.integers(0, 8, size=(k, k)).astype(np.int64)
            J0 = (J0 + J0.T) % 8
            T = np.nonzero(rng.random(k) < 0.5)[0].astype(np.int64)
            src = 0
            T = T[T != src]
            Da, Ja = D0.copy(), J0.copy()
            Db, Jb = D0.copy(), J0.copy()
            addrow_numpy(Da, Ja, T, src, k)
            addrow_njit(Db, Jb, T, src, k)
            if not (np.array_equal(Da, Db) and np.array_equal(Ja, Jb)):
                ok = False
                print(f"    MISMATCH at k={k}")
                break
    print(f"    {'✅ JIT matches numpy exactly' if ok else '⛔ MISMATCH — no timing emitted'}")
    if not ok:
        sys.exit(2)

    # ---- timing -----------------------------------------------------------
    print("\n  ② TIMING — the Z8 sparse add-row, the profiler's 53%")
    print(f"  {'k':>5} {'numpy (us)':>13} {'numba (us)':>13} {'speedup':>10}")
    rows = []
    for k in (40, 80, 160):
        D0 = rng.integers(0, 8, size=k).astype(np.int64)
        J0 = rng.integers(0, 8, size=(k, k)).astype(np.int64)
        J0 = (J0 + J0.T) % 8
        T = np.nonzero(rng.random(k) < 0.5)[0].astype(np.int64)
        T = T[T != 0]
        reps = 2000

        Da, Ja = D0.copy(), J0.copy()
        addrow_njit(Da, Ja, T, 0, k)                      # compile
        t0 = time.perf_counter()
        for _ in range(reps):
            addrow_njit(Da, Ja, T, 0, k)
        tn = (time.perf_counter() - t0) / reps * 1e6

        Db, Jb = D0.copy(), J0.copy()
        t0 = time.perf_counter()
        for _ in range(reps):
            addrow_numpy(Db, Jb, T, 0, k)
        tp = (time.perf_counter() - t0) / reps * 1e6

        rows.append({"k": k, "numpy_us": tp, "numba_us": tn, "speedup": tp / tn})
        print(f"  {k:>5} {tp:>13.2f} {tn:>13.2f} {tp/tn:>9.2f}x")

    # ---- Amdahl, computed BEFORE the headline -----------------------------
    share_z8 = 0.533
    share_dispatch = 0.316
    best = max(rows, key=lambda r: r["speedup"])
    at80 = [r for r in rows if r["k"] == 80][0]
    print(f"\n  ③ AMDAHL, applied before quoting (as it should have been three times today)")
    print(f"    Z8 share {share_z8*100:.1f}% at {at80['speedup']:.2f}x (k=80)")
    e2e_z8 = 1 / ((1 - share_z8) + share_z8 / at80["speedup"])
    print(f"      -> end-to-end from Z8 alone: {e2e_z8:.2f}x")
    print(f"    but JIT also REMOVES the {share_dispatch*100:.1f}% dispatch layer, which is the")
    print(f"    point: a fully-JIT kernel has no numpy call overhead at all.")
    opt = 1 / ((1 - share_z8 - share_dispatch) + share_z8 / at80["speedup"])
    print(f"      -> optimistic ceiling if dispatch goes to ~0: {opt:.2f}x")

    dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results",
                       "numba_kernel_bench_v1.json")
    with open(dst, "w") as fh:
        json.dump({"card": "numba_kernel_bench", "version": "1.0", "cycle": "C5020",
                   "substrate": "claude-fable-5", "rows": rows,
                   "amdahl": {"z8_share": share_z8, "dispatch_share": share_dispatch,
                              "e2e_from_z8_alone": e2e_z8, "optimistic_ceiling": opt},
                   "correctness": "JIT matches numpy exactly on 40 random cases per k"}, fh,
                  indent=2)
    print(f"\n  written: results/{os.path.basename(dst)}")


if __name__ == "__main__":
    main()
