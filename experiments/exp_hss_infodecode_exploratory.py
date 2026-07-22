#!/usr/bin/env python3
"""EXPLORATORY (NO CLAIM) — s-INFORMATION retention vs modal-peak retention, banked C4973 job.

Whisper C4974, substrate claude-fable-5. $0 QPU (data re-fetch only, job d9g4oqsjeosc73fknnbg).

The C4973 rung-0 gate FOLDED under its frozen modal-R statistic; race rungs correctly DISCARDED
UNGRADED; that verdict STANDS. This is an instrument-class analysis of the CALIBRATION ladder
(rung-0, t=0 Clifford, classically free — no advantage claim can attach) asking: how fast does
the *decodable* s-information decay with depth, vs the modal peak the gate measured?

Motivating observation (C4974): the stage-1 d2q=111 modal string is HD-2 from s under the v3
convention (chance ~1.5e-5) — each shot at depth looks like s XOR sparse-errors, i.e. the shot
axis is a repetition code the width×depth law does not tax.

LAYOUT VERIFICATION (the convention court):
- rung-0 pubs all derive from t0 (fold/basis-translation preserve qubit indices), so ONE final
  layout applies to the whole ladder. Rebuilt deterministically (same transpiler seed, pinned
  initial layout from the manifest); fingerprints d2q=37 [manifest 37].
- SELF-CHECK (must pass or abort): marginalizing pooled m=0 with this layout, no reversal, must
  give modal == s with 692/20000 — the exact graded record of the flight's stage-1.
- race_n40's t40 could NOT be reproduced today (overnight calibration drift changed the
  best-of-20 outcome; manifest initial layout matched by 0/20 seeds) → race rungs are NOT
  analyzed here. The ladder brackets the race depth (37/111/185/259 vs 194), which is enough
  for the instrument question. A historical-target reconstruction is a possible follow-up.

Blind-first discipline: every decoder below uses ONLY the counts; s enters only as the final
score HD(decode, s).
"""
import json, math, os
from collections import Counter
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results")
MAN = json.load(open(os.path.join(RES, "exp_hss_race_flight_manifest.json")))
REV = json.load(open(os.path.join(RES, "exp_hss_race_reveal.json")))
FL = json.load(open(os.path.join(RES, "exp_hss_final_layouts_rebuilt.json")))

S40 = REV["race_n40"]["s_str"]
FINAL0 = FL["final0"]
NPHYS, N = 156, 40

from qiskit_ibm_runtime import QiskitRuntimeService


def get_counts(res_item):
    return res_item.data[list(res_item.data.keys())[0]].get_counts()


def marginalize(counts, layout):
    idx = [NPHYS - 1 - p for p in layout]
    out = Counter()
    for s, c in counts.items():
        out["".join(s[i] for i in idx)] += c
    return out


def hd(a, b):
    return sum(x != y for x, y in zip(a, b))


def ball_mass(counts, center, rmax=8):
    mass = [0] * (rmax + 1)
    for s, c in counts.items():
        d = hd(s, center)
        if d <= rmax:
            mass[d] += c
    return mass


def bit_fracs(counts, n=N):
    ones = np.zeros(n)
    tot = 0
    for s, c in counts.items():
        tot += c
        ones += c * (np.frombuffer(s.encode(), dtype=np.uint8).astype(np.int64) - 48)
    return ones / tot, tot


def majority(counts, n=N):
    frac, tot = bit_fracs(counts, n)
    mhat = "".join("1" if f > 0.5 else "0" for f in frac)
    z = np.abs(frac - 0.5) * 2 * math.sqrt(tot)
    return mhat, frac, z


def dup_majority(counts, n=N):
    """Majority over strings observed >=2x (junk shots at high entropy rarely repeat)."""
    dupc = Counter({s: c for s, c in counts.items() if c >= 2})
    if not dupc:
        return None, 0
    m, _, _ = majority(dupc, n)
    return m, sum(dupc.values())


def iterative_soft_majority(counts, n=N, rho=0.5, iters=8):
    """EM-flavored blind decoder: weight each shot by rho^HD(shot, current estimate),
    re-vote, repeat. Starts from plain majority. Never sees s."""
    est, _, _ = majority(counts, n)
    strings = list(counts.items())
    arrs = [(np.frombuffer(s.encode(), dtype=np.uint8).astype(np.int64) - 48, c) for s, c in strings]
    for _ in range(iters):
        e = np.frombuffer(est.encode(), dtype=np.uint8) - 48
        num = np.zeros(n)
        den = 0.0
        for a, c in arrs:
            w = c * (rho ** int((a != e).sum()))
            num += w * a
            den += w
        new = "".join("1" if f > 0.5 else "0" for f in (num / den))
        if new == est:
            break
        est = new
    return est


def analyze_rung(tag, counts):
    shots = sum(counts.values())
    modal, mc = counts.most_common(1)[0]
    mhat, frac, z = majority(counts)
    mdup, dupshots = dup_majority(counts)
    msoft = iterative_soft_majority(counts)
    agree = np.array([abs((1 - frac[i]) if S40[i] == "0" else frac[i]) for i in range(N)])
    return {
        "tag": tag, "shots": shots, "distinct": len(counts),
        "modal_counts": mc, "R_modal": mc / shots, "HD_modal_s": hd(modal, S40),
        "count_at_s": counts.get(S40, 0),
        "ball_mass_around_s_r0to8": ball_mass(counts, S40),
        "HD_majority_s": hd(mhat, S40),
        "HD_dupmajority_s": (hd(mdup, S40) if mdup else None), "dup_shots": dupshots,
        "HD_softmajority_s": hd(msoft, S40),
        "mean_perbit_agreement_with_s": float(agree.mean()),
        "min_perbit_agreement_with_s": float(agree.min()),
        "blind_z_min_med_max": [float(z.min()), float(np.median(z)), float(z.max())],
    }


def main():
    svc = QiskitRuntimeService()
    job = svc.job(MAN["job_id"])
    res = job.result()
    meta = MAN["pubs_meta"]

    folds = {}
    for i, m in enumerate(meta):
        if m["block"] != "rung0":
            continue
        c = marginalize(get_counts(res[i]), FINAL0)
        fd = folds.setdefault(m["fold_m"], {"d2q": m["d2q"], "counts": Counter()})
        fd["counts"].update(c)

    out = {"card": "exp_hss_infodecode_EXPLORATORY_no_claim", "cycle": "C4974",
           "substrate": "claude-fable-5", "job_id": MAN["job_id"],
           "scope": "rung-0 t=0 Clifford CALIBRATION ladder only (layout-verified); race rungs "
                    "NOT analyzed (t40 layout unreproducible after calibration drift)",
           "fences": "C4973 fold verdict STANDS; blind-first decoders; s used only as score",
           "rungs": []}

    # convention self-check FIRST (abort if the anchor fails)
    m0 = folds[0]["counts"]
    modal0, mc0 = m0.most_common(1)[0]
    assert modal0 == S40 and mc0 == 692, f"SELF-CHECK FAIL: HD={hd(modal0,S40)} counts={mc0}"
    out["convention_self_check"] = "PASS — pooled m=0 modal == s at 692/20000 (graded record)"

    for fm in sorted(folds):
        r = analyze_rung(f"rung0_m{fm}_d2q{folds[fm]['d2q']}", folds[fm]["counts"])
        out["rungs"].append(r)
        print(json.dumps(r))

    # lambda_info vs lambda_modal: decay of mean per-bit BIAS (2*agreement-1) vs d2q,
    # and the modal fit for contrast (all 4 points, weighted)
    d2qs = np.array([folds[fm]["d2q"] for fm in sorted(folds)], float)
    bias = np.array([2 * r["mean_perbit_agreement_with_s"] - 1 for r in out["rungs"]])
    lam_bit = np.polyfit(d2qs, np.log(bias), 1)
    out["perbit_bias_vs_d2q"] = {"d2q": d2qs.tolist(), "mean_bias": bias.tolist(),
                                 "lambda_bit_per_slot": float(-lam_bit[0]),
                                 "note": "per-bit bias decay constant — the s-INFORMATION scale; "
                                         "compare stage-1 lambda_modal=0.091 (single-point min-norm)"}
    path = os.path.join(RES, "exp_hss_infodecode_exploratory.json")
    json.dump(out, open(path, "w"), indent=1)
    print("wrote", os.path.normpath(path))
    print(json.dumps(out["perbit_bias_vs_d2q"]))


if __name__ == "__main__":
    main()
