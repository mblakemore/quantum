#!/usr/bin/env python3
"""grade_exp140.py — grade the Exp140 OLE-echo trust-calibration flight (Whisper C4744).

Reads results/exp140_submit_<jid>.json (metas) + the completed job. For each arm computes
  f_arm = (1/N_init) Σ_z σ_z · <O>_z      (ideal = +1.0 exactly, α=0 echo)
then dev_arm = |f_arm − 1|. Bridge-A gate: |dev_B(noise-aware placement)| < |dev_A(baseline)|.
RAW (pre-rescaling) reported = mechanism signal. A null delta = underpowered/ambiguous (mirror
refocus + rescaling can collapse it), NOT 'the stack fails' — per the frozen pre-reg.
Usage: python3 scripts/grade_exp140.py <jid>
"""
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
jid = sys.argv[1] if len(sys.argv) > 1 else None
meta_path = os.path.join(HERE, "..", "results", f"exp140_submit_{jid}.json")
meta = json.load(open(meta_path))

from qiskit_ibm_runtime import QiskitRuntimeService
svc = QiskitRuntimeService()
job = svc.job(jid)
print(f"job {jid} status: {job.status()}")
if str(job.status()) not in ("JobStatus.DONE", "DONE"):
    print("not done yet — re-run when complete."); sys.exit(0)

res = job.result()
def parity(counts):
    tot = sum(counts.values()); e = 0.0
    for bs, c in counts.items():
        ones = bs.replace(" ", "").count("1")
        e += (c/tot) * (1 if ones % 2 == 0 else -1)
    return e

arms = {"A": [], "B": []}
for i, md in enumerate(meta["metas"]):
    c = res[i].data.o.get_counts()          # classical reg named 'o'
    f_z = md["sigma"] * parity(c)            # sigma_z-weighted, ideal +1
    arms[md["arm"]].append(f_z)

out = {"job": jid, "ideal": 1.0}
for arm, label in [("A", "baseline placement"), ("B", "noise-aware placement (stack)")]:
    vals = np.array(arms[arm]); f = vals.mean(); se = vals.std(ddof=1)/np.sqrt(len(vals))
    out[arm] = {"label": label, "f": float(f), "dev": float(abs(f-1)), "se": float(se), "n": len(vals)}
    print(f"Arm {arm} ({label}): f={f:+.4f} ± {se:.4f}  |dev from 1.0|={abs(f-1):.4f}")

dA, dB = out["A"]["dev"], out["B"]["dev"]
delta = dA - dB
se_delta = np.hypot(out["A"]["se"], out["B"]["se"])
out["delta_dev"] = float(delta); out["se_delta"] = float(se_delta)
gate = "PASS (stack recovers closer to 1.0)" if delta > 2*se_delta else \
       ("NULL/underpowered (ambiguous — NOT 'stack fails')" if abs(delta) <= 2*se_delta else
        "INVERTED (baseline closer — stack did not help this window)")
print(f"\nRAW delta |dev_A|-|dev_B| = {delta:+.4f} ± {se_delta:.4f} (2·SE={2*se_delta:.4f})")
print(f"Bridge-A gate: {gate}")
json.dump(out, open(os.path.join(HERE, "..", "results", f"exp140_graded_{jid}.json"), "w"), indent=2)
print("graded ->", f"results/exp140_graded_{jid}.json")
