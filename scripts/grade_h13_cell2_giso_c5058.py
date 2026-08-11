#!/usr/bin/env python3
"""G-ISO adjudication on the Cell 2 re-fly PRE-RUN. Gates the science block.
Clauses: isotropy spread · resolved signs · 3-of-3 signal floor · arm-p agreement · band spread."""
import json, math, os, sys, warnings, statistics; warnings.filterwarnings("ignore")
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,os.path.join(ROOT,"scripts"))
from ibm_multi_account import service_for_job
import importlib.util
spec=importlib.util.spec_from_file_location("gb",os.path.join(ROOT,"tools/g_band_gate.py")); GB=importlib.util.module_from_spec(spec); spec.loader.exec_module(GB)
# the isotropy / sign / signal-floor clauses live in the flown gate script (single source of truth
# — re-implementing them here would be a second copy that can silently diverge from what flew)
_i=importlib.util.spec_from_file_location("ig",os.path.join(ROOT,"scripts/h13_cell2_isotropy_gate_c5058.py")); IG=importlib.util.module_from_spec(_i); _i.loader.exec_module(IG)
JOB=sys.argv[1] if len(sys.argv)>1 else "d9tb3tgpdb6s73e7082g"
man=json.load(open(os.path.join(ROOT,f"results/h13_cell2_refly_prerun_manifest_{JOB}.json")))
o=service_for_job(JOB); svc=o[0] if isinstance(o,tuple) else o
res=svc.job(JOB).result()
cells={}
for lab,pub in zip(man["labels"],res):
    a=pub.data.c.to_bool_array().astype(int); n=a.shape[0]
    e=float(((-1.0)**(a[:,0]+a[:,1])).mean())
    k=(lab["unit"],lab["arm"],lab["basis"])
    cells.setdefault(k,[]).append((e,n))
corr={k: sum(e*w for e,w in v)/sum(w for _,w in v) for k,v in cells.items()}
N={k: sum(w for _,w in v) for k,v in cells.items()}
units=sorted({k[0] for k in corr})
print(f"=== G-ISO ADJUDICATION — Cell 2 re-fly PRE-RUN {JOB} ({len(units)} units) ===\n")
iso_fail=sign_fail=res_fail=armp_fail=0
phat_all=[]
for u in units:
    corrs={arm:{b:corr[(u,arm,b)] for b in ("X","Y","Z")} for arm in ("CE","CC")}
    ns={arm:N[(u,arm,"X")] for arm in ("CE","CC")}
    G=IG.grade(corrs, ns)                      # both arms together — the flown gate's own signature
    for arm in ("CE","CC"):
        g=G[arm]
        if not g["gate_pass_isotropy"]: iso_fail+=1
        if not g["gate_pass_signs"]: sign_fail+=1
        if g.get("gate_no_test"): res_fail+=1
    ag=GB.g_band_arm_agreement([corr[(u,"CE",b)] for b in ("X","Y","Z")],[corr[(u,"CC",b)] for b in ("X","Y","Z")])
    if ag["verdict"].startswith("REFUSE"): armp_fail+=1
    phat_all.append((ag["p_CE"]+ag["p_CC"])/2)
sp=GB.g_band_spread(phat_all)
print(f"  isotropy      : {len(units)*2-iso_fail}/{len(units)*2} arm-units PASS")
print(f"  resolved signs: {len(units)*2-sign_fail}/{len(units)*2} PASS")
print(f"  signal floor  : {len(units)*2-res_fail}/{len(units)*2} met 3-of-3")
print(f"  arm-p agree   : {len(units)-armp_fail}/{len(units)} units PASS")
print(f"  band spread   : realized sd {sp['realized_sd']} vs expected {sp['expected_sd']} -> {sp['verdict']}")
print(f"  realized p̂ mean {statistics.mean(phat_all):.4f} (declared band [0.30,0.70], mean 0.500)")
ok = (iso_fail==0 and sign_fail==0 and res_fail==0 and armp_fail==0 and not sp["verdict"].startswith("REFUSE"))
print(f"\n  G-ISO VERDICT: {'PASS — the science block is CLEARED for submission' if ok else 'FAIL — ABORT, the science block must NOT be submitted'}")
json.dump({"job":JOB,"units":len(units),"iso_fail":iso_fail,"sign_fail":sign_fail,"res_fail":res_fail,
           "armp_fail":armp_fail,"spread":sp,"phat_mean":statistics.mean(phat_all),
           "verdict":"PASS" if ok else "FAIL"},
          open(os.path.join(ROOT,f"results/h13_cell2_giso_{JOB}.json"),"w"),indent=1)
sys.exit(0 if ok else 1)
