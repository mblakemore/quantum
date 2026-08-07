#!/usr/bin/env python3
"""P-CCM v1.0 — DELTA SWEEP: is the large-instance error CONTROLLED, or merely bounded?

WHY THIS AND NOT ANOTHER LADDER. A single large run landing inside sqrt(delta) is weak evidence:
the bound at delta = 0.5 is 0.38, which is most of the available range for a probability, so almost
any not-catastrophically-broken solver would pass it. That is the same shape as the C5023 vacuity
catch — a test whose pass criterion is too loose to discriminate.

The discriminating test is whether the error SHRINKS WITH delta, on the same circuit, as the theory
says it must. A correct solver tracks sqrt(delta) downward. A solver with a bug in the projection,
the phase bookkeeping or the exponent u has a floor: its error stops improving once the systematic
term dominates the approximation term, and the curve flattens while the bound keeps falling.

    delta -> chi = 2^k grows -> fidelity rises -> |P_solver - P_oracle| must fall

SAME CIRCUIT, SAME y, SAME ORACLE across the sweep. Only the decomposition changes, so anything
that fails to move with delta is systematic by construction.

Substrate: claude-fable-5, Whisper C5024.
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import magic_sparsify as ms                                                 # noqa: E402
import gadgetize as gd                                                      # noqa: E402
import large_run as lr                                                      # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=5)
    ap.add_argument("--nt", type=int, default=30)
    ap.add_argument("--ks", default="8,9,10,11")
    ap.add_argument("--repeats", type=int, default=5)
    ap.add_argument("--seed", type=int, default=20260807)
    a = ap.parse_args()

    # one circuit, fixed for the whole sweep
    rng0 = np.random.default_rng(a.seed)
    gates, want, y, t = None, None, None, None
    for attempt in range(200):
        r = np.random.default_rng(a.seed + attempt)
        g = lr.build_instance(a.n, a.nt, r)
        _, tt = gd.gadgetize(g, a.n)
        w = gd.brute_force_pout(g, a.n, [0], (0,))
        if abs(w - 0.5) > 0.15 and 1e-9 < w < 1 - 1e-9:
            gates, want, t = g, w, tt
            y = tuple(int(v) for v in r.integers(0, 2, size=tt))
            break
    if gates is None:
        print("no T-sensitive circuit found"); sys.exit(2)

    print("DELTA SWEEP — is the error CONTROLLED, or merely bounded?\n")
    print(f"  ONE circuit, ONE y, ONE oracle: n = {a.n}, t = {t}, P_oracle = {want:.6f}")
    print("  only the decomposition changes, so anything that does not move with delta")
    print("  is systematic by construction.\n")
    ks = [int(x) for x in a.ks.split(",")]

    pre = [gg for j in range(t) for gg in (("SDG", a.n + j), ("H", a.n + j))]
    build, _ = gd.gadgetize(gates, a.n)
    V = pre + build(y)
    ng = [gd.pauli_Z(a.n + t, 0, 0)] + [gd.pauli_Z(a.n + t, a.n + j, y[j]) for j in range(t)]
    dg = [gd.pauli_Z(a.n + t, a.n + j, y[j]) for j in range(t)]
    G, u = gd.heisenberg_reduce(V, a.n, t, ng)
    H, v = gd.heisenberg_reduce(V, a.n, t, dg)
    gg = [(P.k, P.a, P.b) for P in G]
    hh = [(P.k, P.a, P.b) for P in H]

    rows = []
    print(f"  {'k':>3} {'chi':>8} {'R':>3} {'mean fid^2':>11} {'mean |err|':>11} "
          f"{'sd |err|':>10} {'bound':>8} {'wall':>8}")
    for k in ks:
        errs, fids = [], []
        t0 = time.perf_counter()
        for rep in range(a.repeats):
            # INDEPENDENT random subspace per repeat. The first version of this sweep drew ONE L
            # per delta and reported "monotone in fidelity: NO" — but two deltas collapsed to the
            # same k, so that non-monotonicity was L-DRAW NOISE, not a failure of delta control.
            # Averaging over draws is what separates the two.
            rng = np.random.default_rng(a.seed + 97 * k + rep)
            M = ms.random_subspace(t, k, rng)
            Z, _ = ms.z_of_L(ms._pack(M), k)
            fid2 = (2 ** k) * ms.NU ** (2 * t) / Z
            bits = ms.term_bitstrings(M, k)
            coeff = ms.coefficient(k, Z)
            pn = lr.projected_terms(bits, coeff, gg)
            pd = lr.projected_terms(bits, coeff, hh)
            num = 2.0 ** (-u) * lr.norm2_exact(pn, t)
            den = 2.0 ** (-v) * lr.norm2_exact(pd, t)
            got = num / den if abs(den) > 1e-14 else float("nan")
            if math.isfinite(got):
                errs.append(abs(got - want))
                fids.append(fid2)
        el = time.perf_counter() - t0
        if not errs:
            continue
        me, sd = float(np.mean(errs)), float(np.std(errs))
        mf = float(np.mean(fids))
        bound = math.sqrt(max(0.0, 1 - mf))
        rows.append({"k": k, "chi": 2 ** k, "repeats": len(errs), "mean_fid2": mf,
                     "mean_abs_err": me, "sd_abs_err": sd, "bound": bound,
                     "errs": errs, "wall_s": el})
        print(f"  {k:>3} {2**k:>8,} {len(errs):>3} {mf:>11.4f} {me:>11.5f} {sd:>10.5f} "
              f"{bound:>8.4f} {el:>7.1f}s")

    inside = all(r["mean_abs_err"] <= r["bound"] + 1e-9 for r in rows)
    first, last = rows[0], rows[-1]
    shrank = last["mean_abs_err"] < first["mean_abs_err"]
    mono = all(rows[i]["mean_abs_err"] >= rows[i + 1]["mean_abs_err"] - 1e-12
               for i in range(len(rows) - 1))
    ratio = first["mean_abs_err"] / last["mean_abs_err"] if last["mean_abs_err"] > 0 else float("inf")
    print(f"\n  every point inside its bound        : {'YES' if inside else 'NO'}")
    print(f"  mean error fell as chi grew         : {'YES' if shrank else 'NO'}  "
          f"({first['mean_abs_err']:.5f} -> {last['mean_abs_err']:.5f}, {ratio:.1f}x)")
    print(f"  mean error MONOTONE in chi          : {'YES' if mono else 'NO'}")
    print(f"\n  {'GREEN  the error is CONTROLLED by chi, not merely bounded' if (inside and shrank and mono) else ('AMBER  falls but not monotonically' if shrank else 'RED  the error does not track chi - suspect a systematic term')}")
    print("     A bug in the projection, the phases or the exponent u would show a FLOOR:")
    print("     the mean error would stop improving while the bound kept falling.")

    dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results",
                       "delta_sweep_v1.json")
    with open(dst, "w") as fh:
        json.dump({"card": "delta_sweep", "version": "1.0", "cycle": "C5024",
                   "substrate": "claude-fable-5", "n": a.n, "t": t, "P_oracle": want,
                   "rows": rows, "all_inside": bool(inside), "error_fell": bool(shrank),
                   "monotone_in_chi": bool(mono), "shrink_factor": float(ratio)}, fh, indent=2)
    print(f"  written: results/{os.path.basename(dst)}")


if __name__ == "__main__":
    main()
