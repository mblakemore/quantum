#!/usr/bin/env python3
"""Q-ARM EXACT DECODER VIA WALSH-HADAMARD — same argmax, O(4^n log 4^n). Elder C6575.

*** THIS IS AN IMPLEMENTATION OF THE PINNED OBJECTIVE, NOT A DIFFERENT DECODER. ***
It computes the SAME quantity the frozen exhaustive decoder computes — constraint_rate for every
one of the 4^n-1 candidates, argmax — and must therefore agree with it to the LAST DIGIT on every
revealed rung, winner AND runner-up AND rate. That exactness is the whole reason it is proposable
where my ISD attempt was not: an approximate search that "happens to agree" is a new tool, but an
exact reorganisation of the same sum is arithmetic.

HOW MY FIRST ATTEMPT DIED, because it is the reason this design is the one.
exp142_p1_qarm_linear_decode_elder_c6575.py used Information Set Decoding: draw a random 2n-subset
of the noisy linear constraints, solve exactly, score. It reproduced n=8 (rate 0.8556) and FAILED
n=10, 12 and 13 outright. The reason is structural, not a tuning miss — an error-free subset has
probability rate^(2n):

    n= 8  rate 0.856  ->  1 in 12          ISD trivially wins
    n=13  rate 0.739  ->  1 in 2,648
    n=18  rate 0.640  ->  1 in 9,495,568   each draw a 2n x 2n GF(2) elimination

Retention FALLS with n, so the subset-purity ISD depends on falls with n too, while the search space
it must beat grows. **The speedup was anti-correlated with the need for it** — largest exactly where
the exhaustive walk is already cheap, absent exactly at the ceiling the arc exists to find. Ember
(general#2782) flagged that my validation set contained only comfortable successes; the failure was
sharper than that warning — it appeared at rungs that had ALREADY succeeded by 8-13 SE.

What the dead end did establish, and what this file inherits: the constraint algebra is CORRECT.
sp_inner(Q,P) = Q_x.P_z + Q_z.P_x is linear in P over GF(2), and the ISD run reproduced the n=8
winner's rate exactly through that algebra. So the formulation is verified; only the search was wrong.

THE REORGANISATION. Every Bell sample contributes one linear form. Write A_i = [Q_i,z | Q_i,x] and
p = [P_x | P_z], so <A_i, p> = sp_inner(Q_i, P). The target is a CONSTANT per ypar branch. Then for
every p simultaneously,

    F[p] = sum_i (-1)^<A_i, p>  =  m - 2 * #{i : <A_i,p> = 1}

is precisely the WALSH-HADAMARD TRANSFORM of the histogram of the A_i over GF(2)^2n. One FWHT gives
the agreement count of ALL 4^n candidates at once:

    hits(p, want) = (m + F[p]) / 2   if want = 0
                    (m - F[p]) / 2   if want = 1
    want = csign[ypar(P)],  ypar = parity of popcount(P_x & P_z)

Cost O(4^n * 2n) rather than O(4^n * m), and m (528-2040) is much larger than 2n (16-36). It is exact
because the WHT is an identity, not an estimate.

WHERE THIS ALSO STOPS — stated up front, because the honest limit is the deliverable:
the transform needs the FULL 4^n array resident. int32 (safe: |F| <= m):
    n=13   268 MB      n=14   1.1 GB      n=15   4.3 GB      n=16   17 GB (host RAM is maxed)
So this buys roughly rungs 14-15 and then hits a MEMORY wall, where the exhaustive walk hits a TIME
wall. It does NOT deliver n=18. If the frozen ladder truly runs to 18, n_max may be DECODER-bound
rather than hardware-bound, and that is a finding about the prereg, not about the QPU.

  --validate            reproduce EVERY revealed rung exactly (winner, rate, runner-up). The gate.
  --job <id> --n <n>    decode a flown job
  --bits-from <file>    decode from a cached artifact instead of the network
"""
import argparse, json, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import exp142_robust_decoder_sim as G2

RES = os.path.join(HERE, "..", "results")
LETTERS = "IXYZ"

# Revealed rungs with the EXACT numbers the frozen exhaustive decoder produced.
# Winner, its rate, runner-up and ITS rate must all reproduce — a winner-only check would pass a
# tool that got the ranking right and the spectrum wrong, and the spectrum is what margins come from.
REVEALED = [
    (8,  ("artifact", "exp142_p1_n8_qarm_fetch_elder_c6568.json"), "IZYXZXZZ",      0.8556, "ZYZXXYZX", 0.8000),
    (10, ("cache", "d9l38b8ii2cc73egv1i0"),                        "IYZZXYYIXY",    0.7898, None,       None),
    (12, ("cache", "d9leutrhdfks73ckt45g"),                        "IZIZZXYYYXYZ",  0.7530, None,       None),
    (13, ("cache", "d9lfm73hdfks73cku54g"),                        "XIYXZIIIYIXII", 0.7385, None,       None),
]


def fwht_inplace(a):
    """Fast Walsh-Hadamard transform, natural binary indexing (so <a,p> is the bit XOR-AND)."""
    N = a.shape[0]
    h = 1
    while h < N:
        a = a.reshape(-1, 2, h)
        x = a[:, 0, :].copy()
        y = a[:, 1, :]
        a[:, 0, :] = x + y
        a[:, 1, :] = x - y
        a = a.reshape(N)
        h <<= 1
    return a


def _popcount_parity(v):
    """Parity of popcount, vectorised, without relying on numpy>=2 bitwise_count."""
    v = v.copy()
    r = np.zeros_like(v)
    while v.any():
        r ^= (v & 1)
        v >>= 1
    return r


def decode_fwht(bits, n, mapping, csign, top=8, chunk=1 << 22):
    """Exact constraint-rate argmax over all 4^n-1 candidates via one Walsh-Hadamard transform."""
    Q = np.array([G2.outcome_to_bits(s, n, mapping) for s in bits], dtype=np.uint8)
    m = Q.shape[0]
    N = 1 << (2 * n)

    # index of A_i in GF(2)^{2n}: bit j (j<n) = P_x coefficient = Q_z[j]; bit n+j = Q_x[j]
    Aidx = np.zeros(m, dtype=np.int64)
    for j in range(n):
        Aidx |= (Q[:, n + j].astype(np.int64) & 1) << j            # Q_z -> multiplies P_x
        Aidx |= (Q[:, j].astype(np.int64) & 1) << (n + j)          # Q_x -> multiplies P_z
    # NOT np.bincount: it returns int64, so at n=15 it would allocate 8.6 GB and then a further
    # 4.3 GB for the .astype(int32) copy — 13 GB to build a 4.3 GB histogram, on a host shared with
    # four other crew. Accumulate directly into int32 instead. (C6249: an OOM here is not my own
    # problem to absorb, it is everyone's.)
    f = np.zeros(N, dtype=np.int32)
    np.add.at(f, Aidx, 1)
    F = fwht_inplace(f)                                            # F[p] = m - 2*disagreements

    want0, want1 = int(csign[0]), int(csign[1])
    best = []
    xmask = (1 << n) - 1
    for lo in range(0, N, chunk):
        hi = min(lo + chunk, N)
        idx = np.arange(lo, hi, dtype=np.int64)
        px = idx & xmask
        pz = (idx >> n) & xmask
        ypar = _popcount_parity(px & pz).astype(np.int32)           # Y where both x and z set
        want = np.where(ypar == 0, want0, want1)
        Fc = F[lo:hi].astype(np.int32)
        hits = np.where(want == 0, (m + Fc) // 2, (m - Fc) // 2)
        if lo == 0:
            hits[0] = -1                                           # identity excluded from ensemble
        k = min(top, hi - lo)
        sel = np.argpartition(-hits, k - 1)[:k]
        best.extend((int(hits[s]), int(lo + s)) for s in sel)
        best.sort(reverse=True); best = best[:top]
    del F, f

    def to_pauli(i):
        # C6575: NOT a bit-concat index into "IXYZ". The symplectic convention is
        # I(0,0) X(1,0) Y(1,1) Z(0,1) — so (x,z)=(0,1) is Z and (1,1) is Y, which the
        # concat px|(pz<<1) maps to Y and Z respectively, i.e. exactly transposed. That bug
        # produced four rungs of EXACTLY-correct rates under Y<->Z-swapped labels: the search
        # was right and only the naming was wrong. Explicit table, no arithmetic shortcut.
        px_, pz_ = i & xmask, (i >> n) & xmask
        tab = {(0, 0): "I", (1, 0): "X", (1, 1): "Y", (0, 1): "Z"}
        return "".join(tab[((px_ >> j) & 1, (pz_ >> j) & 1)] for j in range(n))

    return [(to_pauli(i), h / m) for h, i in best], m


def report(rows, m, n, label):
    (w, wr) = rows[0]; (r2, r2r) = rows[1]
    se = math.sqrt(wr * (1 - wr) / m)
    print(f"\n  {label}: P_hat_Q = {w}   rate {wr:.4f}")
    print(f"  runner-up {r2} {r2r:.4f}   SEPARATION {(wr-r2r)/se:.2f} binomial SE")
    print(f"  winner over the 0.5 null bulk: {(wr-0.5)/math.sqrt(0.25/m):.2f} sd   (m={m}, K={4**n-1:,})")
    return {"P_hat_Q": w, "rate": wr, "runner_up": r2, "runner_rate": r2r,
            "separation_binomial_SE": (wr - r2r) / se,
            "z_over_null_bulk": (wr - 0.5) / math.sqrt(0.25 / m),
            "m_samples": m, "candidates": 4 ** n - 1,
            "top": [{"P": p, "rate": r} for p, r in rows]}


def _load(src, n):
    kind, ref = src
    if kind == "artifact":
        return json.load(open(os.path.join(RES, ref)))["raw_bitstrings"]
    cache = os.path.join(RES, "cache", f"n{n}_qarm_{ref}.json")
    if not os.path.exists(cache):
        raise SystemExit(f"no cache {cache}")
    d = json.load(open(cache))
    if isinstance(d, list) and d and isinstance(d[0], dict):
        out = []
        for e in d:
            for bs, c in e.items():
                out.extend([bs] * int(c))
        return out
    if isinstance(d, list) and d and isinstance(d[0], str):
        return d
    raise SystemExit(f"unrecognised cache shape {cache}")


def validate():
    import time
    print("FWHT DECODER VALIDATION — must reproduce the frozen exhaustive decoder EXACTLY.\n")
    mapping = G2.calibrate_bell_mapping(); csign = G2.calibrate_constraint_sign(mapping)
    ok_all = True
    for n, src, trueP, exp_rate, run_P, run_rate in REVEALED:
        try:
            bits = _load(src, n)
        except SystemExit as e:
            print(f"  n={n:<3} SKIP ({e})"); continue
        t0 = time.time()
        rows, m = decode_fwht(bits, n, mapping, csign)
        dt = time.time() - t0
        P, rate = rows[0]; r2, r2r = rows[1]
        good = (P == trueP) and abs(rate - exp_rate) < 5e-4
        extra = ""
        if run_P is not None:
            rgood = (r2 == run_P) and abs(r2r - run_rate) < 5e-4
            good &= rgood
            extra = f" runner {r2} {r2r:.4f} exp {run_P} {run_rate:.4f} {'ok' if rgood else 'MISMATCH'}"
        ok_all &= good
        print(f"  n={n:<3} {P:<14} rate {rate:.4f} (exp {exp_rate:.4f})  {dt:6.1f}s  "
              f"{'MATCH' if good else '*** FAIL ***'}{extra}")
    print(f"\n  FWHT DECODER: {'EXACT AGREEMENT on every revealed rung' if ok_all else 'FAILED — not proposable'}")
    return 0 if ok_all else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--job"); ap.add_argument("--bits-from"); ap.add_argument("--n", type=int)
    ap.add_argument("--out")
    a = ap.parse_args()
    if a.validate:
        return validate()
    if not a.n or not (a.job or a.bits_from):
        sys.exit("--validate, or --n <n> with --job <id> / --bits-from <file>")
    mapping = G2.calibrate_bell_mapping(); csign = G2.calibrate_constraint_sign(mapping)
    if a.bits_from:
        bits = json.load(open(a.bits_from))["raw_bitstrings"]
    else:
        from run_exp66_qpu_partb import _get_ibm_service
        import exp142_decode_meter as M
        job = _get_ibm_service().job(a.job); res = job.result()
        want = 2 * a.n; cands = []
        for i in range(len(res)):
            b = list(M.fetch_pub_bits(job, i))
            if b and len(b[0].replace(" ", "")) == want:
                cands.append((i, b))
        if len(cands) != 1:
            raise SystemExit(f"expected EXACTLY ONE pub with {want} bits/row, found {len(cands)}")
        bits = cands[0][1]
    rows, m = decode_fwht(bits, a.n, mapping, csign)
    out = report(rows, m, a.n, f"n={a.n} decode (FWHT, exact)")
    out.update({"job": a.job, "decoder": "FWHT — EXACT reorganisation of constraint_rate argmax",
                "cycle": "C6575"})
    if a.out:
        json.dump(out, open(a.out, "w"), indent=1); print(f"\nSAVED {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
