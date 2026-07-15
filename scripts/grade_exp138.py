#!/usr/bin/env python3
"""Exp138 ICO heralded sub-bath reset — MECHANICAL GRADE (Whisper C4720).
Frozen rule: experiments/exp138-ico-reset-preregistration.md (committed a5a69b6 BEFORE
submission). Gates:
  INTEGRITY (any fail -> NO-TEST, not LOSS):
    - null band: |p1_D_null - 0.25| + 5*SE < 0.05 for BOTH definite orders
    - retention sentinel: min P(c=+, D=0) >= 0.90 (transfer integrity)
    - deco-null sentinel: P(c=+) in [0.40, 0.60]
  PRIMARY (WIN): min(null p1_D) - reset p1_D|+ - 5*hypot(se+, se_null) > 0.02
  SECONDARY (F95-style, LOSS-able, reported separately): reset p1_D|+ + 5*se+ < 0.25
  RESULT: WIN iff INTEGRITY pass AND PRIMARY pass.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'experiments'))
from run_exp66_qpu_partb import _get_ibm_service
from exp108_ico_refrigeration import pooled_stats, exact_targets, G

DEFAULT_MANIFEST = os.path.join(HERE, '..', 'results', 'exp138_jobids.json')


def main():
    manifest_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MANIFEST
    man = json.load(open(manifest_path))
    gates = man.get("gates", {})
    RET_MIN = gates.get("retention_min", 0.90)
    BEAT_FLOOR = gates.get("beat_floor", 0.02)
    THERM = gates.get("therm_band", 0.05)
    DECO_LO, DECO_HI = gates.get("deco_band", [0.40, 0.60])
    svc = _get_ibm_service()
    job = svc.job(man["job_id"])
    assert str(job.status()) in ("DONE", "JobStatus.DONE"), f"job not done: {job.status()}"
    res = job.result()
    metas = man["metas"]
    assert len(res) == len(metas), (len(res), len(metas))

    counts = {"reset": {}, "null_fwd": {}, "null_rev": {}}
    sentinels, deco = {}, None
    for pub, meta in zip(res, metas):
        c = pub.data.c.get_counts() if hasattr(pub.data, "c") else \
            list(pub.data.values())[0].get_counts()
        kind, label = meta["kind"], meta["label"]
        if kind in counts:
            counts[kind][tuple(meta["prep"])] = c
        elif "retention" in label:
            n = sum(c.values())
            sentinels[label] = c.get("00", 0) / n          # c0=0 (c=+), c1=0 (D=0)
        elif "deconull" in label:
            n = sum(c.values())
            deco = {k: v / n for k, v in c.items()}

    r = pooled_stats(counts["reset"], conditional=True)
    nf = pooled_stats(counts["null_fwd"], conditional=False)
    nr = pooled_stats(counts["null_rev"], conditional=False)
    th = exact_targets(G, np.diag([G, 1 - G]).astype(complex))

    print(f"=== {man.get('tag','exp138')} GRADE (job {man['job_id']}, chain {man['chain']}, "
          f"layout {man['layout']}, retention floor {RET_MIN}) ===")
    print(f"theory: reset p1_D|+={th['+']['p1']:.4f}  null 0.25 exactly  P(+)={th['+']['P']:.4f}")
    print(f"reset : p1_D|+={r['+']['p1']:.4f}(±{r['+']['se']:.4f})  "
          f"p1_D|-={r['-']['p1']:.4f}(±{r['-']['se']:.4f})  P(+)={r['+']['P']:.4f}")
    for name, n in [("null_fwd", nf), ("null_rev", nr)]:
        print(f"{name}: p1_D={n['p1']:.4f}(±{n['p1_se']:.4f}) [bath {1-G:.4f}]  P(c=+)={n['P+']:.4f}")
    print(f"retention replicates: " +
          " ".join(f"{k.split('_')[1]}={v:.4f}" for k, v in sorted(sentinels.items())))
    dec_pplus = sum(v for k, v in deco.items() if k[-1] == "0")
    print(f"deco-null P(c=+)={dec_pplus:.4f} (ideal 0.5)")

    # frozen gates (values from manifest, committed pre-data)
    null_ok = all(abs(n["p1"] - (1 - G)) + 5 * n["p1_se"] < THERM for n in (nf, nr))
    ret_ok = min(sentinels.values()) >= RET_MIN
    deco_ok = DECO_LO <= dec_pplus <= DECO_HI
    integrity = null_ok and ret_ok and deco_ok

    null_min, null_min_se = (nf["p1"], nf["p1_se"]) if nf["p1"] <= nr["p1"] else (nr["p1"], nr["p1_se"])
    beat_val = null_min - r["+"]["p1"]
    beat_margin = beat_val - 5 * np.hypot(r["+"]["se"], null_min_se)
    primary = beat_margin > BEAT_FLOOR
    subbath = r["+"]["p1"] + 5 * r["+"]["se"] < 0.25
    subbath_val = r["+"]["p1"] + 5 * r["+"]["se"]

    print(f"\nINTEGRITY: null-band {'ok' if null_ok else 'BAD'} | "
          f"retention {'ok' if ret_ok else 'BAD'} (min {min(sentinels.values()):.4f}/{RET_MIN}) | "
          f"deco {'ok' if deco_ok else 'BAD'} -> {'PASS' if integrity else 'NO-TEST'}")
    print(f"PRIMARY  beats-definite-order: beat={beat_val:.4f}, margin(−5SE)={beat_margin:.4f} vs 0.02 "
          f"-> {'PASS' if primary else 'FAIL'}")
    print(f"SECONDARY sub-bath: p1_D|+ +5SE={subbath_val:.4f} vs 0.25 -> {'PASS' if subbath else 'LOSS'}")

    if not integrity:
        verdict = "NO-TEST"
    elif primary:
        verdict = "WIN"
    else:
        verdict = "LOSS"
    beat_sigma = beat_val / np.hypot(r["+"]["se"], null_min_se)
    print(f"\nVERDICT: {verdict}"
          + (f"  (delivered D at p1={r['+']['p1']:.4f}, {beat_sigma:.1f}σ colder than definite-order "
             f"reset {null_min:.4f}; sub-bath leg {'cleared' if subbath else 'MISSED (honest)'})"
             if integrity else "  (integrity gate failed)"))

    out = {"verdict": verdict, "integrity": bool(integrity), "primary": bool(primary),
           "subbath": bool(subbath), "reset": r, "null_fwd": nf, "null_rev": nr,
           "sentinels": sentinels, "deco_pplus": dec_pplus,
           "beat_val": float(beat_val), "beat_margin": float(beat_margin),
           "beat_sigma": float(beat_sigma), "subbath_val": float(subbath_val),
           "theory": {"p1p": th["+"]["p1"], "p1m": th["-"]["p1"], "Pp": th["+"]["P"]}}
    outp = os.path.join(HERE, '..', 'results', f"{man.get('tag','exp138')}_grade.json")
    with open(outp, 'w') as f:
        json.dump(out, f, indent=1, default=float)
    print(f"\nwrote {os.path.abspath(outp)}")


if __name__ == "__main__":
    main()
