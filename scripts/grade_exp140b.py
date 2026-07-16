#!/usr/bin/env python3
"""grade_exp140b.py — grade the READOUT-CONTROLLED placement re-test (Whisper C4744).

Applies tensored-Z REM (from the 2 calibration circuits) to every arm, then contrasts the
REM-corrected echo recovery. c_q = 1 - e0_q - e1_q; corrected f = raw f / prod(c_q over the arm's
measured qubits). Reports raw AND REM-corrected so the readout contribution is explicit.
Usage: python3 scripts/grade_exp140b.py <jid>
"""
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
jid = sys.argv[1]
meta = json.load(open(os.path.join(HERE, "..", "results", f"exp140b_submit_{jid}.json")))

from qiskit_ibm_runtime import QiskitRuntimeService
svc = QiskitRuntimeService(); job = svc.job(jid)
print(f"job {jid} status: {job.status()}")
if str(job.status()) not in ("JobStatus.DONE", "DONE"):
    print("not done yet"); sys.exit(0)
res = job.result()

def counts_of(i, reg):
    return getattr(res[i].data, reg).get_counts()

def parity(counts):
    tot = sum(counts.values()); e = 0.0
    for bs, c in counts.items():
        e += (c / tot) * (1 if bs.replace(" ", "").count("1") % 2 == 0 else -1)
    return e

union = meta["union"]
# calibration -> per-union-qubit readout errors
idxCAL = {m["arm"]: i for i, m in enumerate(meta["metas"]) if m["arm"] in ("CAL0", "CAL1")}
def bitfrac(counts, i, want):
    tot = sum(counts.values()); s = 0
    for bs, c in counts.items():
        bits = bs.replace(" ", "")[::-1]  # bits[i] = c[i] = union[i]
        if i < len(bits) and bits[i] == want:
            s += c
    return s / tot
c0 = counts_of(idxCAL["CAL0"], "c"); c1 = counts_of(idxCAL["CAL1"], "c")
e0 = [bitfrac(c0, i, "1") for i in range(len(union))]   # prep0 -> read1
e1 = [bitfrac(c1, i, "0") for i in range(len(union))]   # prep1 -> read0
contrast = {union[i]: max(1e-6, 1 - e0[i] - e1[i]) for i in range(len(union))}
print("readout per union qubit (e0,e1 -> contrast):")
for i, q in enumerate(union):
    print(f"   q{q}: e0={e0[i]:.4f} e1={e1[i]:.4f} -> c={contrast[q]:.4f}")

arm_phys = meta["arm_phys"]
LAB = {"A": "opt1+baseline", "B": "opt3+noise-aware(stack)", "C": "opt3+baseline(control)"}
raw = {a: [] for a in ("A", "B", "C")}
for i, md in enumerate(meta["metas"]):
    if md["arm"] in raw:
        raw[md["arm"]].append(md["sigma"] * parity(counts_of(i, "o")))

out = {"job": jid, "backend": meta["backend"], "ideal": 1.0}
for a in ("A", "B", "C"):
    v = np.array(raw[a]); f_raw = v.mean(); se_raw = v.std(ddof=1) / np.sqrt(len(v))
    remfac = np.prod([contrast[p] for p in arm_phys[a]])
    f_rem = f_raw / remfac; se_rem = se_raw / remfac
    out[a] = {"label": LAB[a], "phys": arm_phys[a], "rem_factor": float(remfac),
              "f_raw": float(f_raw), "f_rem": float(f_rem), "se_rem": float(se_rem),
              "dev_rem": float(abs(f_rem - 1))}
    print(f"Arm {a} ({LAB[a]}) phys={arm_phys[a]}: f_raw={f_raw:+.4f} → REM(/{remfac:.3f}) "
          f"f={f_rem:+.4f} ± {se_rem:.4f}  |dev|={abs(f_rem-1):.4f}")

def contrast_arms(x, y, name):
    d = out[x]["dev_rem"] - out[y]["dev_rem"]; sd = np.hypot(out[x]["se_rem"], out[y]["se_rem"])
    verdict = f"{y} closer (+{d/sd:.1f}σ)" if d > 2*sd else (f"{x} closer ({d/sd:.1f}σ)" if d < -2*sd else "null (<2σ)")
    out[f"delta_{x}{y}"] = {"delta": float(d), "sigma": float(d/sd), "verdict": verdict}
    print(f"  REM Δ|dev| {x}−{y} ({name}) = {d:+.4f}  ({d/sd:+.1f}σ) → {verdict}")

print("\nREM-corrected contrasts (readout removed → residual = bulk placement):")
contrast_arms("C", "B", "PURE bulk placement")
contrast_arms("A", "C", "opt-level")
json.dump(out, open(os.path.join(HERE, "..", "results", f"exp140b_graded_{jid}.json"), "w"), indent=2)
print("graded ->", f"results/exp140b_graded_{jid}.json")
