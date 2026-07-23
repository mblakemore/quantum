#!/usr/bin/env python3
"""INDEPENDENT 2-of-2 co-verification of Whisper C4974 "The Shot Axis Is a Code".

Ember C4214, substrate claude-opus-4-8. $0 QPU (banked re-fetch only, job d9g4oqsjeosc73fknnbg).

Independent seat (NOT a read of Whisper's JSON):
  * My own marginalization of the banked counts (independent of exp_hss_infodecode_exploratory.py)
  * Commitment check: score s against sha256(s+salt) == 48503776.. (pre-committed => 2^-40 null airtight)
  * Blind majority decoder -> HD(s)  [expect 0,0,1,2 per committed JSON]
  * Binomial-tail significance of each rung's majority HD (the real null: chance HD ~ Binom(40,0.5))
  * BLIND Chase-k decoder (select by soft-likelihood over shots, NEVER distance-to-s) for k in {3,12}:
      resolves the card's uncommitted "Chase-8 HD = 0,0,0,1" column. Reports whether any HD-0 at
      d2q=185 is a real likelihood MARGIN or a knife-edge tie-break (advisor's calibration question).
  * lambda_bit fit from the 4 per-bit-bias points [expect ~0.0030]

Blind discipline: s enters ONLY as the final HD score and the argmax tie audit. Every decoder
ranks candidates by the SHOTS alone.
"""
import json, math, os, hashlib
from collections import Counter
from itertools import combinations
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results")
MAN = json.load(open(os.path.join(RES, "exp_hss_race_flight_manifest.json")))
REV = json.load(open(os.path.join(RES, "exp_hss_race_reveal.json")))
FL = json.load(open(os.path.join(RES, "exp_hss_final_layouts_rebuilt.json")))

S40 = REV["race_n40"]["s_str"]
SALT = REV["race_n40"]["salt"]
FINAL0 = FL["final0"]
NPHYS, N = 156, 40
RHO = 0.5  # card's soft-decoder rho


def commitment_ok():
    h = hashlib.sha256((S40 + SALT).encode()).hexdigest()
    return h, h.startswith("48503776")


def get_counts(res_item):
    return res_item.data[list(res_item.data.keys())[0]].get_counts()


def marginalize(counts, layout):
    # independent re-derivation: physical bit p sits at string index NPHYS-1-p (qiskit little-endian)
    idx = [NPHYS - 1 - p for p in layout]
    out = Counter()
    for s, c in counts.items():
        out["".join(s[i] for i in idx)] += c
    return out


def hd(a, b):
    return sum(x != y for x, y in zip(a, b))


def to_arr(s):
    return np.frombuffer(s.encode(), dtype=np.uint8).astype(np.int64) - 48


def bit_fracs(counts):
    ones = np.zeros(N); tot = 0
    for s, c in counts.items():
        tot += c; ones += c * to_arr(s)
    return ones / tot, tot


def majority(counts):
    frac, tot = bit_fracs(counts)
    return "".join("1" if f > 0.5 else "0" for f in frac), frac, tot


def chase_k(counts, k):
    """Blind Chase-II: majority seed, flip every subset of the k least-reliable bits,
    rank the 2^k candidates by BLIND soft-likelihood sum_shots count*rho^HD(shot,cand).
    Vectorized (candidates x shots). s NEVER used in selection. Returns best candidate,
    its HD to s, and the likelihood margin over the plain-majority string."""
    mhat, frac, tot = majority(counts)
    reliab = np.abs(frac - 0.5)                 # blind reliability
    weak = list(np.argsort(reliab)[:k])         # k least-reliable bit positions
    # shot matrix (n_distinct x 40) + weights
    S = np.stack([to_arr(s) for s in counts.keys()]).astype(np.int8)   # (M, 40)
    W = np.array(list(counts.values()), dtype=np.float64)              # (M,)
    seed = to_arr(mhat).astype(np.int8)
    # enumerate all 2^k flip patterns on the weak bits (including empty = majority seed)
    cands = [seed.copy()]
    for r in range(1, k + 1):
        for combo in combinations(weak, r):
            c = seed.copy()
            for b in combo:
                c[b] ^= 1
            cands.append(c)
    C = np.stack(cands).astype(np.int8)                                # (Ncand, 40)
    # HD(cand, shot) for all pairs -> (Ncand, M); score = sum_m W * rho^HD
    scores = np.empty(len(C))
    for j in range(len(C)):
        hdist = (S != C[j]).sum(axis=1)                                # (M,)
        scores[j] = (W * (RHO ** hdist)).sum()
    best = int(np.argmax(scores))
    cand_str = "".join(str(int(x)) for x in C[best])
    margin = (scores[best] - scores[0]) / scores[0]  # >0 => Chase beat majority on SHOTS (blind)
    return cand_str, hd(cand_str, S40), margin, hd(mhat, S40)


def log_binom_tail_le(hdist, n=N):
    """log10 P(HD <= hdist) for a random 40-bit string vs a fixed target (Binom(n,0.5))."""
    tot = sum(math.comb(n, i) for i in range(hdist + 1))
    return math.log10(tot) - n * math.log10(2)


def main():
    hfull, ok = commitment_ok()
    print(f"COMMITMENT: sha256(s+salt)={hfull[:16]}..  matches 48503776 -> {ok}")
    assert ok, "commitment mismatch — sealed s is NOT the pre-committed string; abort"

    from qiskit_ibm_runtime import QiskitRuntimeService
    svc = QiskitRuntimeService()
    res = svc.job(MAN["job_id"]).result()
    meta = MAN["pubs_meta"]

    folds = {}
    for i, m in enumerate(meta):
        if m["block"] != "rung0":
            continue
        c = marginalize(get_counts(res[i]), FINAL0)
        fd = folds.setdefault(m["fold_m"], {"d2q": m["d2q"], "counts": Counter()})
        fd["counts"].update(c)

    # independent anchor: my marginalization must hit 692/20000 at m=0
    m0 = folds[0]["counts"]; modal0, mc0 = m0.most_common(1)[0]
    anchor = (modal0 == S40 and mc0 == 692)
    print(f"ANCHOR (independent marginalization): m=0 modal==s at {mc0}/20000 -> {'PASS' if anchor else 'FAIL'}")
    assert anchor, f"independent marginalization anchor failed: HD={hd(modal0,S40)} counts={mc0}"

    out = {"card": "exp_hss_infodecode_VERIFY_ember", "cycle": "C4214",
           "substrate": "claude-opus-4-8", "verifies": "Whisper C4974", "job_id": MAN["job_id"],
           "commitment_sha256_s_salt": hfull, "anchor_692_pass": anchor, "rungs": []}
    biases = []
    for fm in sorted(folds):
        d2q = folds[fm]["d2q"]; counts = folds[fm]["counts"]
        mhat, frac, tot = majority(counts)
        hd_maj = hd(mhat, S40)
        agree = np.array([(1 - frac[i]) if S40[i] == "0" else frac[i] for i in range(N)])
        bias = float(2 * agree.mean() - 1); biases.append(bias)
        c3, hd3, mrg3, _ = chase_k(counts, 3)    # "Chase-8" = 2^3 patterns
        c12, hd12, mrg12, _ = chase_k(counts, 12)  # flight-proposed k=12
        rung = {"d2q": d2q, "shots": tot, "HD_majority": hd_maj,
                "log10_null_P_HD_le_maj": round(log_binom_tail_le(hd_maj), 2),
                "sigma_equiv_maj": round(abs(_z_from_log10p(log_binom_tail_le(hd_maj))), 1),
                "HD_chase_k3": hd3, "chase_k3_blind_margin_over_maj": round(mrg3, 4),
                "HD_chase_k12": hd12, "chase_k12_blind_margin_over_maj": round(mrg12, 4),
                "mean_perbit_bias": round(bias, 4)}
        out["rungs"].append(rung)
        print(json.dumps(rung))

    d2qs = np.array([folds[fm]["d2q"] for fm in sorted(folds)], float)
    lam = float(-np.polyfit(d2qs, np.log(np.array(biases)), 1)[0])
    out["lambda_bit_per_slot"] = lam
    print(f"lambda_bit (independent fit) = {lam:.4f}  [card 0.0030]")
    path = os.path.join(RES, "exp_hss_infodecode_verify_ember.json")
    json.dump(out, open(path, "w"), indent=1)
    print("wrote", os.path.normpath(path))


def _z_from_log10p(log10p):
    # two-sided-ish z for a one-tailed log10 p; rough sigma-equivalent for reporting only
    from math import sqrt, log
    p = 10 ** log10p
    if p <= 0: return 99.9
    # invert normal tail via asymptotic approx
    import statistics
    try:
        from scipy.stats import norm
        return norm.isf(p)
    except Exception:
        # crude fallback: z ~ sqrt(2*ln(1/p)) - correction
        z = math.sqrt(max(0.0, 2 * math.log(1 / p)))
        return z


if __name__ == "__main__":
    main()
