#!/usr/bin/env python3
"""H13 Cell 4 grader — bands frozen in docs/h13-cell4-hindsight-prereg-FROZEN-whisper-c5058.md."""
import json, math, os, sys, warnings; warnings.filterwarnings("ignore")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from ibm_multi_account import service_for_job
JOB = sys.argv[1] if len(sys.argv) > 1 else "d9t6qq1dsedc73aii7rg"
BAND = 0.06
man = json.load(open(os.path.join(ROOT, f"results/h13_cell4_manifest_{JOB}.json")))
o = service_for_job(JOB); svc = o[0] if isinstance(o, tuple) else o
res = svc.job(JOB).result()
ro = man["readout_err"]; h = (1 - 2 * ro) ** 2      # haircut: two measurements each ~(1-2*eps)
rows, ctrl = [], None
for lab, pub in zip(man["labels"], res):
    a = pub.data.c.to_bool_array().astype(int)
    # COLUMN ORDER: qiskit returns the classical register with c[1] (final) in column 0 and
    # c[0] (mid) in column 1. Established EMPIRICALLY from the no-mid control, which read
    # P=0.0000 in the column that must carry a physically-required 0.146 — an impossible value
    # that could only be an unwritten register. The control's ONLY job was to catch this class
    # and it did; an inverted mapping would have silently reported max-P(final) as "foresight"
    # and failed G3 for a reason that was not physics.
    a = a[:, ::-1]                                  # now col0 = mid, col1 = final
    n = a.shape[0]
    if not lab["mid"]:
        ctrl = {"final_p1": float(a[:, 1].mean()), "n": n, "expected_sin2": math.sin(math.radians(45)/2)**2}; continue
    joint = {}
    for m, f in a: joint[(int(m), int(f))] = joint.get((int(m), int(f)), 0) + 1
    fore = max(sum(v for (m, f), v in joint.items() if m == mm) for mm in (0, 1)) / n
    hind = sum(max(joint.get((0, f), 0), joint.get((1, f), 0)) for f in (0, 1)) / n
    gap = hind - 0.5
    se = math.sqrt(max(hind * (1 - hind), 1e-9) / n)
    pred = math.sin(math.radians(lab["theta_f"])) / 2 * h
    rows.append({"theta": lab["theta_f"], "foresight": fore, "hindsight": hind, "gap": gap,
                 "se": se, "predicted": pred, "dev": gap - pred, "in_band": abs(gap - pred) <= BAND})
print(f"=== H13 Cell 4 — HINDSIGHT METER — job {JOB} on {man['backend']} (q{man['layout'][0]}, ro={ro:.5f}, haircut={h:.4f}) ===\n")
print("  θ_f   foresight   hindsight     gap ± se        sin(θ)/2×h    dev     band")
for r in rows:
    print(f"  {r['theta']:>3}°   {r['foresight']:.4f}      {r['hindsight']:.4f}    {r['gap']:+.4f}±{r['se']:.4f}    "
          f"{r['predicted']:.4f}     {r['dev']:+.4f}   {'IN ' if r['in_band'] else 'OUT'}")
g1 = all(r["in_band"] for r in rows)
z0 = rows[0]["gap"] / rows[0]["se"]
g2 = abs(z0) <= 2
g3 = all(abs(r["foresight"] - 0.5) <= 0.02 for r in rows)
mid = [r for r in rows if 30 <= r["theta"] <= 60]
print(f"\n  G1 law-match, all 7 angles within ±{BAND}   : {'PASS' if g1 else 'FAIL'}")
print(f"  G2 null point θ=0 within 2σ of zero        : {'PASS' if g2 else 'FAIL'}  (z={z0:+.2f})")
print(f"  G3 foresight floor 0.500±0.02 everywhere   : {'PASS' if g3 else 'FAIL'}  "
      f"(range {min(r['foresight'] for r in rows):.4f}–{max(r['foresight'] for r in rows):.4f})")
print(f"  G4 θ=90° labelled CEILING (trivial copy)   : gap {rows[-1]['gap']:+.4f} — NOT the claim")
print(f"\n  THE CLAIM (mid-curve 30–60°): " + ", ".join(f"{r['theta']}°={r['gap']:+.4f}({r['gap']/r['se']:.0f}σ)" for r in mid))
if ctrl: print(f"  no-mid control: P(final=1)={ctrl['final_p1']:.4f}")
verdict = "PASS" if (g1 and g2 and g3) else "FAIL"
print(f"\n  VERDICT: {verdict}")
json.dump({"job": JOB, "haircut": h, "rows": rows, "control": ctrl,
           "gates": {"G1_law_match": g1, "G2_null": g2, "G3_foresight_floor": g3}, "verdict": verdict},
          open(os.path.join(ROOT, f"results/h13_cell4_grade_{JOB}.json"), "w"), indent=1)
