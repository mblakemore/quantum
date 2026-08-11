#!/usr/bin/env python3
"""Grade the Cell 2 re-fly isotropy pre-flight gate (board #77). All four clauses:
   isotropy (Elder #9099 magnitude spread + MDE) · |C| not signed C (Whisper) ·
   sign check (Ember #9200) · resolution precondition (Elder #9204)."""
import json, math, os, sys, warnings; warnings.filterwarnings("ignore")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from ibm_multi_account import service_for_job
import importlib.util
spec = importlib.util.spec_from_file_location("g", os.path.join(ROOT, "scripts/h13_cell2_isotropy_gate_c5058.py"))
G = importlib.util.module_from_spec(spec); spec.loader.exec_module(G)
JOB = sys.argv[1] if len(sys.argv) > 1 else "d9t730npemts73cuh45g"
man = json.load(open(os.path.join(ROOT, f"results/h13_cell2_isotropy_manifest_{JOB}.json")))
o = service_for_job(JOB); svc = o[0] if isinstance(o, tuple) else o
res = svc.job(JOB).result()
acc = {"CE": {b: [] for b in G.BASES}, "CC": {b: [] for b in G.BASES}}
for lab, pub in zip(man["labels"], res):
    a = pub.data.c.to_bool_array().astype(int); n = a.shape[0]
    e = float(((-1.0) ** (a[:, 0] + a[:, 1])).mean())
    acc[lab["arm"]][lab["basis"]].append((e, n, lab["twirl"]))
corrs, ns = {}, {}
for arm, d in acc.items():
    corrs[arm] = {}
    tot_n = 0
    for b, v in d.items():
        w = sum(n for _, n, _ in v)
        corrs[arm][b] = sum(e * n for e, n, _ in v) / w
        tot_n = w
    ns[arm] = tot_n
g = G.grade(corrs, ns)
print(f"=== H13 Cell 2 RE-FLY — ISOTROPY PRE-FLIGHT GATE — job {JOB} on {man['backend']} ===")
print(f"    p_depol={man['p_depol']} frozen · shots/cell={ns} · arm gap {man['arm_gap']} · MDE 0.0098\n")
for arm in ("CE", "CC"):
    x = g[arm]
    print(f"  {arm}:  C = {x['C']}")
    print(f"       |C| = {x['abs_C']}   max pairwise spread = {x['max_pairwise_spread_abs']}  "
          f"(threshold {round(man['arm_gap']+0.0098,5)})")
    print(f"       signs {x['signs']} vs ideal {x['signs_expected']}   z = {x['sign_z']}")
    print(f"       ISOTROPY {'PASS' if x['gate_pass_isotropy'] else 'FAIL'} · "
          f"SIGNS {'PASS' if x['gate_pass_signs'] else 'FAIL'}"
          + (f" (UNRESOLVED {x['unresolved_axes']} — not counted as mismatch)" if x['unresolved_axes'] else "")
          + (f" (MISMATCH {x['sign_mismatch_axes']})" if x['sign_mismatch_axes'] else ""))
    print()
overall = all(g[a]["gate_pass"] for a in ("CE", "CC"))
no_test = any(g[a].get("gate_no_test") for a in ("CE", "CC"))
# THREE-STATE, not two. FAIL would mean "the design does not work"; NO-TEST means "the design
# was never flown". Conflating them would blame the physics for a harness bug.
if overall: v = "PASS — the twirl produces an isotropic channel on silicon; the re-fly design is ALIVE"
elif no_test: v = ("NO-TEST — signal floor not met (fewer than 3 of 3 axes resolved). The correlators are dead, so "
                   "isotropy passes trivially and signs pass vacuously. This says NOTHING about the twirl design.")
else: v = "FAIL — resolved correlators, but anisotropic or sign-flipped; the re-fly design needs rework"
print(f"  VERDICT: {v}")
json.dump({"job": JOB, "p_depol": man["p_depol"], "shots_per_cell": ns, "corrs": corrs,
           "grade": g, "verdict": "PASS" if overall else "FAIL"},
          open(os.path.join(ROOT, f"results/h13_cell2_isotropy_grade_{JOB}.json"), "w"), indent=1, default=str)
