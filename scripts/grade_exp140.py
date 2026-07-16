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

arms = {"A": [], "B": [], "C": []}
for i, md in enumerate(meta["metas"]):
    c = res[i].data.o.get_counts()          # classical reg named 'o'
    f_z = md["sigma"] * parity(c)            # sigma_z-weighted, ideal +1
    arms.setdefault(md["arm"], []).append(f_z)

LABELS = {"A": "opt1 + baseline layout", "B": "opt3 + noise-aware layout (stack)",
          "C": "opt3 + baseline layout (opt-level control)"}
out = {"job": jid, "ideal": 1.0}
for arm in ("A", "B", "C"):
    if not arms.get(arm):
        continue
    vals = np.array(arms[arm]); f = vals.mean(); se = vals.std(ddof=1)/np.sqrt(len(vals))
    out[arm] = {"label": LABELS[arm], "f": float(f), "dev": float(abs(f-1)), "se": float(se), "n": len(vals)}
    print(f"Arm {arm} ({LABELS[arm]}): f={f:+.4f} ± {se:.4f}  |dev from 1.0|={abs(f-1):.4f}")

def contrast(x, y, name):
    if x not in out or y not in out:
        return
    d = out[x]["dev"] - out[y]["dev"]; sd = np.hypot(out[x]["se"], out[y]["se"])
    verdict = f"{y} closer to 1.0 ({d/sd:+.1f}σ)" if d > 2*sd else \
              (f"{x} closer ({d/sd:+.1f}σ)" if d < -2*sd else "null (<2σ)")
    out[f"delta_{x}{y}"] = {"delta_dev": float(d), "se": float(sd), "sigma": float(d/sd), "verdict": verdict}
    print(f"  Δ|dev| {x}−{y} = {d:+.4f} ± {sd:.4f}  ({d/sd:+.1f}σ) → {verdict}")

print("\nContrasts:")
contrast("A", "B", "combined (orig)")     # both variables (continuity with the first run)
contrast("C", "B", "PLACEMENT isolated")  # same opt3 → pure placement effect (the key one)
contrast("A", "C", "OPT-LEVEL isolated")  # same trivial layout → pure opt-level effect
json.dump(out, open(os.path.join(HERE, "..", "results", f"exp140_graded_{jid}.json"), "w"), indent=2)
print("graded ->", f"results/exp140_graded_{jid}.json")
