#!/usr/bin/env python3
"""P1 n=10 Q-ARM BLIND DECODE — prereg step 4.5. Elder C6575.

WRITTEN AND VALIDATED WHILE THE FLIGHT IS STILL AIRBORNE, before any n=10 data exists. Two reasons,
the second being the real one:
  1. n=10 will not run on the n=8 code. The n=8 confusion spectrum looped 65,535 candidates in
     Python; n=10 is 1,048,575 candidates x 528 samples ~ 553M symplectic ops, and the naive full
     matrix is 553 MB on a RAM-constrained host. This needed vectorising + chunking, which is not
     work to start when the job lands. Three runbook steps today had no working tool at the moment
     I needed one; this is the fourth, caught before it cost anything.
  2. Writing the decoder before the data exists means it cannot be shaped by the result.

DECODER IS THE PRE-COMMITTED ONE (#2567, posted before the flight): constraint_rate via
G2.calibrate_bell_mapping + calibrate_constraint_sign, argmax over ALL 4^n-1 candidates.
  NOT decode_meter    — the old alpha=1 tool that mis-reads I->Z at position 0 (the C6568 trap).
  NOT LLR-scored      — the Q arm gives EVERY candidate the same m samples, so coverage is equal
                        and raw-rate argmax is correct. The LLR rule is scoped to the C1 arm, where
                        coverage is unequal at m/3^w. Swapping the Q decoder would void the n=6 gate.

VALIDATION GATE (mandatory, and the whole reason this is trustworthy): --validate re-decodes the
REVEALED n=8 job through THIS vectorised path and must reproduce IZYXZXZZ with rate 0.8556 and
runner-up ZYZXXYZX 0.8000. A fast rewrite that does not reproduce the known answer is a new tool,
not the committed one.

REPORTS THE MARGIN, NOT JUST THE WINNER (Dawn's rule, #2445): winner rate, runner-up, separation in
binomial SE, and z over the null bulk. "Correct" and "correct by 1.06 sd" were different facts at
n=8 and will be again.

  --validate                 re-decode revealed n=8, must reproduce (run BEFORE trusting n=10)
  --job <id> --n 10          blind decode the flown job
"""
import argparse, json, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import exp142_robust_decoder_sim as G2

RES = os.path.join(HERE, "..", "results")
CHUNK = 32768                      # candidates per block: 528 x 32768 int8 ~ 17 MB, RAM-safe


def candidate_block(lo, hi, n):
    """Candidates lo..hi as (K,2n) symplectic bit matrix + Y-parity, in the COMMITTED order.
    Committed order = itertools.product('IXYZ') lexicographic minus all-I = base-4 ints 1..4^n-1
    with digit0=I,1=X,2=Y,3=Z. pauli_to_bits: I(0,0) X(1,0) Y(1,1) Z(0,1)."""
    ints = np.arange(lo, hi, dtype=np.int64)
    K = len(ints)
    M = np.zeros((K, 2 * n), dtype=np.int8)
    ypar = np.zeros(K, dtype=np.int8)
    for i in range(n):
        d = (ints >> (2 * (n - 1 - i))) & 3          # digit at qubit i
        M[:, i] = ((d == 1) | (d == 2)).astype(np.int8)      # x bit: X or Y
        M[:, n + i] = ((d == 2) | (d == 3)).astype(np.int8)  # z bit: Y or Z
        ypar ^= (d == 2).astype(np.int8)
    return M, ypar


def decode(bits, n, mapping, csign, top=8):
    """Blind argmax of the constraint rate over all 4^n-1 candidates. Chunked over candidates."""
    Q = np.array([G2.outcome_to_bits(s, n, mapping) for s in bits], dtype=np.int8)  # (m,2n)
    m = Q.shape[0]
    Qx, Qz = Q[:, :n].astype(np.int32), Q[:, n:].astype(np.int32)
    want0, want1 = csign[0], csign[1]
    best = []                                        # (rate, int) keep top few
    total = 4 ** n - 1
    for lo in range(1, total + 1, CHUNK):
        hi = min(lo + CHUNK, total + 1)
        M, ypar = candidate_block(lo, hi, n)
        Px, Pz = M[:, :n].astype(np.int32), M[:, n:].astype(np.int32)
        # symplectic inner product for every (sample, candidate): Qx@Pz.T + Qz@Px.T  (mod 2)
        S = ((Qx @ Pz.T) + (Qz @ Px.T)) & 1          # (m, K)
        want = np.where(ypar == 0, want0, want1).astype(np.int32)   # (K,)
        hits = (S == want[None, :]).sum(axis=0)      # (K,)
        rates = hits / m
        k = min(top, len(rates))
        idx = np.argpartition(-rates, k - 1)[:k]
        best.extend((float(rates[j]), int(lo + j)) for j in idx)
        best.sort(reverse=True); best = best[:top]
        if (lo // CHUNK) % 8 == 0:
            print(f"    ...{hi-1:,}/{total:,} candidates, best so far {best[0][0]:.4f}", flush=True)
    LET = "IXYZ"
    to_s = lambda v: "".join(LET[(v >> (2 * (n - 1 - i))) & 3] for i in range(n))
    return [(to_s(v), r) for r, v in best], m


def report(rows, m, n, label):
    (w, wr), (r2, r2r) = rows[0], rows[1]
    se = math.sqrt(wr * (1 - wr) / m)
    null_sd = math.sqrt(0.25 / m)
    print(f"\n  {label}: P_hat_Q = {w}   rate {wr:.4f}")
    print(f"  runner-up {r2} {r2r:.4f}   SEPARATION {wr-r2r:.4f} = {(wr-r2r)/se:.2f} binomial SE")
    print(f"  winner over the 0.5 null bulk: {(wr-0.5)/null_sd:.2f} sd   (m={m}, K={4**n-1:,})")
    print("  top 6:", "  ".join(f"{p}:{x:.4f}" for p, x in rows[:6]))
    return {"P_hat_Q": w, "rate": wr, "runner_up": r2, "runner_rate": r2r,
            "separation": wr - r2r, "separation_binomial_SE": (wr - r2r) / se,
            "z_over_null_bulk": (wr - 0.5) / null_sd, "m_samples": m,
            "candidates": 4 ** n - 1, "top": [{"P": p, "rate": x} for p, x in rows]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--job"); ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--out")
    a = ap.parse_args()
    mapping = G2.calibrate_bell_mapping(); csign = G2.calibrate_constraint_sign(mapping)

    if a.validate:
        print("VALIDATION: re-decoding the REVEALED n=8 job through THIS vectorised path.")
        print("Must reproduce IZYXZXZZ 0.8556, runner-up ZYZXXYZX 0.8000.\n")
        bits = json.load(open(os.path.join(RES, "exp142_p1_n8_qarm_fetch_elder_c6568.json")))["raw_bitstrings"]
        rows, m = decode(bits, 8, mapping, csign)
        res = report(rows, m, 8, "n=8 revalidation")
        ok = (res["P_hat_Q"] == "IZYXZXZZ" and abs(res["rate"] - 0.8556) < 0.001
              and res["runner_up"] == "ZYZXXYZX" and abs(res["runner_rate"] - 0.8000) < 0.001)
        print(f"\n  VALIDATION: {'PASS — vectorised path reproduces the committed decoder exactly'
                                if ok else '*** FAIL — this is a DIFFERENT tool, do not use it ***'}")
        return 0 if ok else 1

    if not a.job:
        sys.exit("--job <id> required (or --validate). Run --validate FIRST.")
    from run_exp66_qpu_partb import _get_ibm_service
    import exp142_decode_meter as M
    print(f"fetching n={a.n} Q job {a.job} ...", flush=True)
    job = _get_ibm_service().job(a.job)
    res = job.result()
    # C6575: SELECT THE Q PUB BY BIT WIDTH, never by index. The flight carries SENTINELS FORE AND AFT,
    # so pub 0 is a 2-bit sentinel, not the Q arm — hardcoding index 0 crashed with IndexError on the
    # first attempt. That is the SAME pub-index bug I found in the C1 driver this morning, made again
    # in a decoder I wrote today while citing that very lesson. Selecting on the structural invariant
    # (a two-copy n-qubit Bell row is exactly 2n bits) cannot break under a different sentinel layout,
    # and asserting exactly one match makes an ambiguous job loud instead of arbitrary.
    want = 2 * a.n
    cands = []
    for i in range(len(res)):
        b = list(M.fetch_pub_bits(job, i))
        w = len(b[0].replace(" ", "")) if b else 0
        print(f"  pub {i}: {len(b)} rows, {w} bits/row{'  <-- Q arm (2n)' if w == want else ''}", flush=True)
        if w == want:
            cands.append((i, b))
    if len(cands) != 1:
        raise SystemExit(f"*** expected EXACTLY ONE pub with {want} bits/row, found {len(cands)} "
                         f"({[i for i, _ in cands]}) — refusing to guess which is the Q arm ***")
    pub_idx, bits = cands[0]
    print(f"  selected pub {pub_idx}: {len(bits)} Bell samples x {want} bits", flush=True)
    rows, m = decode(bits, a.n, mapping, csign)
    res = report(rows, m, a.n, f"n={a.n} BLIND decode")
    res.update({"job": a.job, "decoder": "constraint_rate/G2/csign argmax (pre-committed #2567)",
                "blind": "decoded before reveal", "cycle": "C6575"})
    out = a.out or os.path.join(RES, f"exp142_p1_n{a.n}_qarm_blind_decode_elder_c6575.json")
    json.dump(res, open(out, "w"), indent=1); print(f"\nSAVED {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
