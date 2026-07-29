#!/usr/bin/env python3
"""Exp142 P1 n=10 HYBRID RUNG — C1 walk benchmark sim (Whisper C5013).

Implements §4.2(a) of docs/exp142-p1-n10-hybrid-prereg-DRAFT-whisper-c5013.md:
the NOISELESS-IDEAL classical benchmark — the committed sequential covering walk
(frozen semantics of exp142_p1_c1_decoder_elder_c5003.covering_decode) run over M
uniform sealed-P draws at n=10, reporting walk-median C1 copies + 90% interval.

WHY A REIMPLEMENTATION EXISTS AT ALL: the frozen covering_decode is pure Python and
exact, but at n=10 it walks up to 4^10-1 = 1,048,575 candidates per draw; at M=200
draws that is computationally infeasible verbatim. This file therefore contains a
VECTORIZED walk whose semantics are proven equal to the frozen decoder by the
EQUIVALENCE GATE below (--equivalence): identical fw_shots in -> identical
(P_hat, C1_distinct_copies) out, at n=4 and n=6, across seeded random draws.
The n=10 benchmark is only valid if the equivalence gate passes — the same
known-answer discipline as §4.2c and §4.5.

NOISELESS-IDEAL MODEL (per prereg: C1 benchmark stays noiseless — the floor argument):
  q = 0 (no readout error)  =>  p0 = (1+alpha)/2 = 0.975 for EVERY candidate
  (p_flip(w, 0) = 0, so the per-candidate weight dependence vanishes at q=0).
  For a shot in full-weight basis A on state (I + alpha*P)/2^n:
    - bits at all sites uniform, EXCEPT the parity over supp(P) is even w.p. 0.975
      iff A covers P (agrees with P on P's support);
    - candidates Q != P have EXACTLY fair-coin parity in every basis (if supp(Q) ==
      supp(P) inside a P-covering basis then Q == P; any strict overlap XORs in at
      least one uniform bit) — the C1-side analogue of the #2384/#2386 character-sum
      result on the Q side.

DETERMINISM / SEED RULE (§4.1): master seed = sha256(<freeze-commit-hash>). Per-draw,
per-basis bit blocks come from Philox keyed by sha256(master || draw || basis) — lazy,
memory-light, and identical whether generated for the frozen decoder (dict form) or
the vectorized walk (array form): both call the same _basis_block().

Usage:
  --equivalence                 run the frozen-equivalence gate (n=4 x 20 draws, n=6 x 5)
  --benchmark --commit <hash> --M 200 [--n 10]   run the benchmark (gate must pass first)
"""
import argparse, hashlib, itertools, json, math, os, sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from exp142_p1_c1_decoder_elder_c5003 import (          # FROZEN — imported, not copied
    candidates, covering_decode, covers, full_weight_bases, p0_of, support, wald_AB)

ALPHA = 0.95
SHOTS_PER_BASIS = 256      # ample: wrong-candidate SPRT drift ~-0.82/copy to B~-5.3;
                           # true-P drift ~+0.59/copy to A~18.5 (~31 copies at n=10)

LETTERS = "IXYZ"


# ---------------------------------------------------------------- deterministic bits
def _key(master_hex: str, draw: int, basis: str) -> np.random.Philox:
    h = hashlib.sha256(f"{master_hex}|{draw}|{basis}".encode()).digest()
    return np.random.Philox(key=int.from_bytes(h[:8], "big"))


def _basis_block(master_hex, draw, basis, P, n, shots=SHOTS_PER_BASIS):
    """Shots x n uint8 bit block for one full-weight basis — THE single source of bits
    for both the frozen decoder path and the vectorized path (equivalence by shared
    generation, not by parallel implementations of the noise model)."""
    gen = np.random.Generator(_key(master_hex, draw, basis))
    bits = (gen.random((shots, n)) < 0.5).astype(np.uint8)
    if covers(basis, P):                                   # bias supp(P) parity to even w.p. (1+a)/2
        supp = support(P)
        want_even = gen.random(shots) < (1 + ALPHA) / 2
        par = bits[:, supp].sum(axis=1) % 2
        flip = (par == 1) == want_even                     # parity odd but want even, or even but want odd
        bits[flip, supp[0]] ^= 1
    return bits


def draw_P(master_hex, draw, n):
    """Uniform over {I,X,Y,Z}^n minus identity — the p1_allpaulis ensemble."""
    gen = np.random.Generator(_key(master_hex, draw, "__P__"))
    while True:
        s = "".join(LETTERS[i] for i in gen.integers(0, 4, size=n))
        if any(c != "I" for c in s):
            return s


# ---------------------------------------------------------------- vectorized walk
def _cand_int_order(n):
    """Committed candidate order as ints 1..4^n-1: base-4 digits over I<X<Y<Z is exactly
    the frozen lexicographic itertools.product('IXYZ') order, minus all-I (int 0)."""
    return np.arange(1, 4 ** n, dtype=np.int64)


def _int_to_str(v, n):
    return "".join(LETTERS[(v >> (2 * (n - 1 - i))) & 3] for i in range(n))


def _covering_seq(Q):
    """Covering bases of candidate Q in the frozen consumption order (fwb lex order
    restricted to covering) — generator, lazy."""
    opts = [("XYZ" if c == "I" else c) for c in Q]
    for t in itertools.product(*opts):
        yield "".join(t)


def vector_walk(master_hex, draw, n, P, chunk=8192):
    """Vectorized replica of covering_decode semantics on the SAME deterministic bits.
    Returns {P_hat, C1_distinct_copies} exactly as the frozen decoder would."""
    A_wald, B_wald = wald_AB(n)
    p0 = p0_of("X" * n, ALPHA, 0.0)                        # q=0: same for all candidates (0.975)
    s_even, s_odd = math.log(p0 / 0.5), math.log((1 - p0) / 0.5)

    order = _cand_int_order(n)
    highwater = {}                                          # basis -> shots consumed (max index+1)
    block_cache = {}

    def block(basis):
        if basis not in block_cache:
            block_cache[basis] = _basis_block(master_hex, draw, basis, P, n)
        return block_cache[basis]

    P_hat = None
    for lo in range(0, len(order), chunk):
        cand_ints = order[lo:lo + chunk]
        # first covering basis of each candidate: I -> X  (lex-least fill), i.e. digit 0 -> 1
        digits = np.stack([(cand_ints >> (2 * (n - 1 - i))) & 3 for i in range(n)], axis=1)
        first_digits = np.where(digits == 0, 1, digits)
        supp_mask = (digits != 0)

        # group candidates by first covering basis to share bit blocks
        basis_strs = ["".join(LETTERS[d] for d in row) for row in first_digits]
        stops = np.zeros(len(cand_ints), dtype=np.int64)    # copies consumed in first basis
        accept = np.zeros(len(cand_ints), dtype=bool)
        resolved = np.zeros(len(cand_ints), dtype=bool)

        by_basis = {}
        for idx, b in enumerate(basis_strs):
            by_basis.setdefault(b, []).append(idx)
        for b, idxs in by_basis.items():
            bb = block(b)                                   # SHOTS x n
            idxs = np.asarray(idxs)
            pars = (bb[None, :, :] * supp_mask[idxs][:, None, :]).sum(axis=2) % 2  # cand x shots
            llr = np.cumsum(np.where(pars == 0, s_even, s_odd), axis=1)
            hitA = llr >= A_wald
            hitB = llr <= B_wald
            anyA = hitA.any(axis=1); anyB = hitB.any(axis=1)
            iA = np.where(anyA, hitA.argmax(axis=1), SHOTS_PER_BASIS)
            iB = np.where(anyB, hitB.argmax(axis=1), SHOTS_PER_BASIS)
            first = np.minimum(iA, iB)
            resolved[idxs] = first < SHOTS_PER_BASIS
            accept[idxs] = anyA & (iA < iB)                 # crossed A strictly before B
            stops[idxs] = np.minimum(first + 1, SHOTS_PER_BASIS)

        # rare: unresolved within first basis -> frozen-semantics slow path (spillover)
        for idx in np.nonzero(~resolved)[0]:
            Qs = _int_to_str(int(cand_ints[idx]), n)
            llr = 0.0; consumed_here = []
            done = False
            for b in _covering_seq(Qs):
                bb = block(b)
                for si in range(bb.shape[0]):
                    consumed_here.append((b, si))
                    par = int(bb[si][supp_mask[idx]].sum() % 2)
                    llr += s_even if par == 0 else s_odd
                    if llr >= A_wald: accept[idx] = True; done = True; break
                    if llr <= B_wald: done = True; break
                if done: break
            # register slow-path consumption directly into highwater
            per_b = {}
            for b, si in consumed_here:
                per_b[b] = max(per_b.get(b, 0), si + 1)
            for b, hw in per_b.items():
                highwater[b] = max(highwater.get(b, 0), hw)
            stops[idx] = 0                                  # already accounted above

        # walk stops at the FIRST accepting candidate (frozen: break on accept)
        acc_idx = np.nonzero(accept)[0]
        stop_at = acc_idx[0] if len(acc_idx) else None
        upto = (stop_at + 1) if stop_at is not None else len(cand_ints)
        for idx in range(upto):
            if stops[idx]:
                b = basis_strs[idx]
                highwater[b] = max(highwater.get(b, 0), int(stops[idx]))
        if stop_at is not None:
            P_hat = _int_to_str(int(cand_ints[stop_at]), n)
            break

    return {"P_hat": P_hat, "C1_distinct_copies": int(sum(highwater.values()))}


# ---------------------------------------------------------------- equivalence gate
def equivalence_gate():
    """Frozen covering_decode vs vector_walk on IDENTICAL fw_shots: exact match required.
    n=4 x 20 draws, n=6 x 5 draws (frozen decoder cost bounds the count)."""
    master = hashlib.sha256(b"equivalence-gate-fixed-test-seed").hexdigest()
    all_ok = True
    for n, draws in [(4, 20), (6, 5)]:
        for d in range(draws):
            P = draw_P(master, d, n)
            fw = {b: [list(map(int, r)) for r in _basis_block(master, d, b, P, n)]
                  for b in full_weight_bases(n)}
            frozen = covering_decode(fw, n, ALPHA, 0.0)
            fast = vector_walk(master, d, n, P)
            ok = (frozen["P_hat"] == fast["P_hat"]
                  and frozen["C1_distinct_copies"] == fast["C1_distinct_copies"])
            all_ok &= ok
            print(f"  n={n} draw={d:2d} true={P}  frozen=({frozen['P_hat']},{frozen['C1_distinct_copies']})"
                  f"  vector=({fast['P_hat']},{fast['C1_distinct_copies']})  {'OK' if ok else 'MISMATCH'}")
    print(f"\nEQUIVALENCE GATE: {'PASS' if all_ok else 'FAIL'}")
    return all_ok


# ---------------------------------------------------------------- n=10 benchmark
def benchmark(commit_hash, M, n):
    master = hashlib.sha256(commit_hash.encode()).hexdigest()     # §4.1 seed rule
    copies, correct = [], 0
    for d in range(M):
        P = draw_P(master, d, n)
        r = vector_walk(master, d, n, P)
        copies.append(r["C1_distinct_copies"])
        correct += (r["P_hat"] == P)
        if (d + 1) % 10 == 0:
            print(f"  draw {d+1}/{M}: median so far {int(np.median(copies))}", flush=True)
    arr = np.sort(np.array(copies))
    out = {"card": "exp142_p1_n10_c1walk_benchmark", "cycle": "C5013",
           "seed_source_commit": commit_hash, "n": n, "M": M, "alpha": ALPHA,
           "noise": "noiseless-ideal (q=0) per prereg — the floor benchmark",
           "walk_median_C1_copies": int(np.median(arr)),
           "interval_90pct": [int(np.quantile(arr, 0.05)), int(np.quantile(arr, 0.95))],
           "decode_correct": f"{correct}/{M}",
           "equivalence_gate": "must be run and PASS in the same pinned code state"}
    path = os.path.join(HERE, "..", "results", f"exp142_p1_n{n}_c1walk_benchmark_whisper_c5013.json")
    json.dump(out, open(path, "w"), indent=1)
    print(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--equivalence", action="store_true")
    ap.add_argument("--benchmark", action="store_true")
    ap.add_argument("--commit", help="freeze commit hash — the §4.1 seed source")
    ap.add_argument("--M", type=int, default=200)
    ap.add_argument("--n", type=int, default=10)
    a = ap.parse_args()
    if a.equivalence:
        sys.exit(0 if equivalence_gate() else 1)
    if a.benchmark:
        if not a.commit:
            sys.exit("--benchmark requires --commit (seed rule: sha256 of freeze commit)")
        benchmark(a.commit, a.M, a.n)
