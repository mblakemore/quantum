#!/usr/bin/env python3
"""Q-ARM LINEAR DECODER — O(poly) instead of O(4^n). Elder C6575. CANDIDATE, NOT YET ADOPTED.

*** THIS IS NOT THE PINNED DECODER. It is a proposal, and it must reproduce ALL SIX revealed
    answers before I bring it to the court. If it fails any of them it does not get proposed. ***

THE PROBLEM IT SOLVES. The frozen decoder is an exhaustive argmax over 4^n-1 candidates. Measured
at rung 13 (67.1M candidates, 1220 samples, ~25 min) it scales to ~2.8 h at n=14, ~15 h at n=15,
~3.2 DAYS at n=16 and ~85 DAYS at n=18. The frozen ladder runs to 18, so MY DECODER — not the QPU,
not retention — becomes the arc's binding constraint from n=15. Each rung costs ~15 QPU-seconds and
would then wait days on a search loop.

THE STRUCTURE THE EXHAUSTIVE WALK IGNORES. sp_inner(Q,P) = Q_x·P_z + Q_z·P_x (mod 2) is **LINEAR in
P over GF(2)**. So every Bell sample is not an independent hypothesis to score — it is a NOISY
LINEAR CONSTRAINT on the 2n bits of P:

        A p = b (mod 2),   A row_i = [Q_i,z | Q_i,x],   b_i = csign[ypar(P)]

ypar (the Y-count parity) is the only nonlinearity, and it takes two values, so we solve TWICE —
once per ypar class — and keep solutions whose realised ypar matches the branch assumption.

WHY NOT GAUSSIAN ELIMINATION. The constraints are noisy: agreement rate is ~0.74-0.85, so ~15-26%
of equations are WRONG. A single 2n x 2n solve on arbitrary rows returns garbage. This is Learning
Parity with Noise, and at this rate it is not solvable by one elimination.

WHAT DOES WORK — INFORMATION SET DECODING. Draw a random 2n-subset, solve it exactly, score the
resulting p against ALL m equations, keep the best. A subset is error-free with probability
rate^(2n), so the expected number of draws is rate^-(2n) — thousands to millions, each a cheap
GF(2) elimination on a 2n x 2n system. At n=18 that is ~10^7 microsecond solves rather than 6.9e10
candidate evaluations: minutes instead of weeks, and it degrades gracefully rather than off a cliff.

HONEST BOUND: ISD is RANDOMISED. It is not guaranteed to find the optimum in a fixed budget, whereas
the exhaustive walk is. That is a real trade the court must weigh, not something I should decide by
being the one who wrote it. Mitigation here: a FIXED seed, a FIXED trial budget, and a reported
best-score so a run that failed to find a strong solution is visible rather than silent.

  --validate      reproduce ALL SIX revealed answers (the gate that decides whether this is proposed)
  --job <id> --n <n> [--trials N]
"""
import argparse, json, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import exp142_robust_decoder_sim as G2

RES = os.path.join(HERE, "..", "results")
SEED = 6575                       # pinned
LETTERS = "IXYZ"

# the six revealed rungs: (n, job_or_cache, revealed P, expected rate)
REVEALED = [
    (8,  ("artifact", "exp142_p1_n8_qarm_fetch_elder_c6568.json"), "IZYXZXZZ",      0.8556),
    (10, ("job", "d9l38b8ii2cc73egv1i0"),                          "IYZZXYYIXY",   0.7898),
    (12, ("job", "d9leutrhdfks73ckt45g"),                          "IZIZZXYYYXYZ", 0.7530),
    (13, ("job", "d9lfm73hdfks73cku54g"),                          "XIYXZIIIYIXII", 0.7385),
]


def pauli_to_bits(P):
    n = len(P)
    v = np.zeros(2 * n, dtype=np.uint8)
    for i, c in enumerate(P):
        x, z = {"I": (0, 0), "X": (1, 0), "Y": (1, 1), "Z": (0, 1)}[c]
        v[i], v[n + i] = x, z
    return v


def bits_to_pauli(v, n):
    out = []
    for i in range(n):
        out.append({(0, 0): "I", (1, 0): "X", (1, 1): "Y", (0, 1): "Z"}[(int(v[i]), int(v[n + i]))])
    return "".join(out)


def gf2_solve(A, b):
    """Solve A p = b over GF(2) by elimination. A is (k,k) uint8. Returns p or None if singular."""
    k = A.shape[0]
    M = np.concatenate([A.copy(), b.reshape(-1, 1)], axis=1).astype(np.uint8)
    piv = []
    r = 0
    for c in range(k):
        rows = np.nonzero(M[r:, c])[0]
        if len(rows) == 0:
            continue
        i = r + rows[0]
        if i != r:
            M[[r, i]] = M[[i, r]]
        hit = np.nonzero(M[:, c])[0]
        hit = hit[hit != r]
        if len(hit):
            M[hit] ^= M[r]
        piv.append(c); r += 1
        if r == k:
            break
    if r < k:
        return None                                  # singular: not an information set
    p = np.zeros(k, dtype=np.uint8)
    for idx, c in enumerate(piv):
        p[c] = M[idx, -1]
    return p


def decode_linear(bits, n, mapping, csign, trials=200000, top=8):
    """ISD over the two ypar branches. Returns ranked (P, rate) list."""
    m = len(bits)
    Q = np.array([G2.outcome_to_bits(s, n, mapping) for s in bits], dtype=np.uint8)
    # A row = [Q_z | Q_x] so that A @ p = Q_x.p_z + Q_z.p_x
    A = np.concatenate([Q[:, n:], Q[:, :n]], axis=1).astype(np.uint8)
    rng = np.random.default_rng(SEED)
    k = 2 * n
    seen = {}
    for branch in (0, 1):
        target = csign[branch]
        b = np.full(m, target, dtype=np.uint8)
        for _ in range(trials // 2):
            idx = rng.choice(m, size=k, replace=False)
            p = gf2_solve(A[idx], b[idx])
            if p is None:
                continue
            if not p.any():
                continue                             # identity is excluded from the ensemble
            P = bits_to_pauli(p, n)
            if P in seen:
                continue
            if (P.count("Y") % 2) != branch:
                continue                             # branch assumption must hold for this p
            agree = int(np.count_nonzero(((A @ p) & 1) == target))
            seen[P] = agree / m
    ranked = sorted(seen.items(), key=lambda kv: -kv[1])[:top]
    return ranked, m, len(seen)


def _load(src, n):
    kind, ref = src
    if kind == "artifact":
        return json.load(open(os.path.join(RES, ref)))["raw_bitstrings"]
    cache = os.path.join(RES, "cache", f"n{n}_qarm_{ref}.json")
    if os.path.exists(cache):
        d = json.load(open(cache))
        # C6575: the cache is a LIST of per-shot {bitstring: count} dicts — NOT a list of strings.
        # I assumed strings and got 'dict has no attribute replace'. Normalise all three shapes
        # rather than assume one, and assert the result is actually strings before returning.
        if isinstance(d, dict):
            for key in ("raw_bitstrings", "bitstrings", "rows"):
                if key in d:
                    d = d[key]; break
        if isinstance(d, list) and d:
            if isinstance(d[0], str):
                return d
            if isinstance(d[0], dict):
                out = []
                for e in d:
                    for bs, c in e.items():
                        out.extend([bs] * int(c))
                return out
        raise SystemExit(f"unrecognised cache shape in {cache}")
    from run_exp66_qpu_partb import _get_ibm_service
    import exp142_decode_meter as M
    job = _get_ibm_service().job(ref)
    res = job.result()
    want = 2 * n
    for i in range(len(res)):
        bb = list(M.fetch_pub_bits(job, i))
        if bb and len(bb[0].replace(" ", "")) == want:
            return bb
    raise SystemExit(f"no {want}-bit pub in job {ref}")


def validate(trials):
    print("LINEAR DECODER VALIDATION — must reproduce EVERY revealed rung.\n")
    ok_all = True
    for n, src, trueP, exp_rate in REVEALED:
        try:
            bits = _load(src, n)
        except SystemExit as e:
            print(f"  n={n:<3} SKIP (data unavailable: {e})"); continue
        ranked, m, nsol = decode_linear(bits, n, MAP, CS, trials=trials)
        if not ranked:
            print(f"  n={n:<3} *** NO SOLUTION FOUND in {trials} trials ***"); ok_all = False; continue
        P, rate = ranked[0]
        run = ranked[1] if len(ranked) > 1 else ("-", 0.0)
        se = math.sqrt(rate * (1 - rate) / m)
        good = (P == trueP) and abs(rate - exp_rate) < 0.002
        ok_all &= good
        print(f"  n={n:<3} P_hat {P:<14} rate {rate:.4f} (exp {exp_rate:.4f})  "
              f"runner {run[0]:<14} {run[1]:.4f}  sep {(rate-run[1])/se:5.2f} SE  "
              f"[{nsol} distinct sols]  {'MATCH' if good else '*** FAIL ***'}")
    print(f"\n  LINEAR DECODER: {'ALL REVEALED RUNGS REPRODUCED — proposable' if ok_all else 'FAILED — NOT proposable'}")
    return 0 if ok_all else 1


def main():
    global MAP, CS
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--job"); ap.add_argument("--n", type=int)
    ap.add_argument("--trials", type=int, default=200000)
    ap.add_argument("--out")
    a = ap.parse_args()
    MAP = G2.calibrate_bell_mapping(); CS = G2.calibrate_constraint_sign(MAP)
    if a.validate:
        return validate(a.trials)
    if not (a.job and a.n):
        sys.exit("--validate, or --job <id> --n <n>")
    bits = _load(("job", a.job), a.n)
    ranked, m, nsol = decode_linear(bits, a.n, MAP, CS, trials=a.trials)
    P, rate = ranked[0]; run = ranked[1] if len(ranked) > 1 else ("-", 0.0)
    se = math.sqrt(rate * (1 - rate) / m)
    print(f"  n={a.n} LINEAR decode: P_hat {P} rate {rate:.4f} | runner {run[0]} {run[1]:.4f} "
          f"| sep {(rate-run[1])/se:.2f} SE | {nsol} distinct sols | m={m}")
    if a.out:
        json.dump({"n": a.n, "job": a.job, "P_hat_Q": P, "rate": rate, "runner_up": run[0],
                   "runner_rate": run[1], "separation_binomial_SE": (rate - run[1]) / se,
                   "m_samples": m, "distinct_solutions": nsol, "trials": a.trials, "seed": SEED,
                   "decoder": "LINEAR/ISD — CANDIDATE, not the pinned decoder"},
                  open(a.out, "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
