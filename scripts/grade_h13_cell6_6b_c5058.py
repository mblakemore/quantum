#!/usr/bin/env python3
"""H13 Cells 6+6b — GRADER. Bands frozen in docs/h13-cell6-6b-merged-prereg-DRAFT-v2-whisper-c5056.md."""
import json, os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
from ibm_multi_account import service_for_job

JOB = sys.argv[1] if len(sys.argv) > 1 else "d9t5esntfhrs73dtgtc0"
BAND = 0.06
CENTERS = {  # (tier,N) -> (eta_armed, f0call_transparent) from the freeze-time full-noise sim
 ("A",1):(0.005,0.93), ("A",2):(0.235,0.88), ("A",4):(0.450,0.79), ("A",8):(0.524,0.71),
 ("B",2):(0.227,0.85), ("B",4):(0.425,0.74), ("B",8):(0.461,0.63)}

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
man = json.load(open(os.path.join(root, f"results/h13_cell6_6b_manifest_{JOB}.json")))
o = service_for_job(JOB); svc = o[0] if isinstance(o, tuple) else o
res = svc.job(JOB).result()

rows, prem = {}, {}
for lab, pub in zip(man["labels"], res):
    d = pub.data
    tier, N, var = lab["tier"], lab["N"], lab["variant"]
    dd = d.d.to_bool_array().astype(int)
    rr = d.r.to_bool_array().astype(int).ravel()
    tot = dd.shape[0]
    fired = (dd.sum(axis=1) > 0)
    if var in ("marked", "unmarked"):
        pp = d.p.to_bool_array().astype(int).ravel()
        eta = float(((~fired) & (pp == 0)).mean())
        f0  = float(((~fired) & (pp == 1)).mean())
        rows[(tier, N, var)] = {"eta": eta, "f0call": f0, "fired": float(fired.mean()), "n": tot}
    else:
        prem[(tier, var)] = {"fire_rate": float(fired.mean()), "r_mean": float(rr.mean()), "n": tot}

print(f"=== H13 Cell 6+6b GRADE — job {JOB} on {man['backend']} ===\n")
print("PREMISE GATES")
gates = {}
p1a = prem[("A","P1_faithful")]["fire_rate"]; p1b = prem[("B","P1_faithful")]["fire_rate"]
p2a = prem[("A","P2_transparent")]["fire_rate"]; p2b = prem[("B","P2_transparent")]["fire_rate"]
p3  = prem[("A","P3_integrity")]["r_mean"]
for nm, val, rule, ok in (("P1_A armed-faithfulness", p1a, ">=0.95", p1a>=0.95),
                          ("P1_B armed-faithfulness", p1b, ">=0.95", p1b>=0.95),
                          ("P2_A transparency",       p2a, "<=0.03", p2a<=0.03),
                          ("P2_B transparency",       p2b, "<=0.03", p2b<=0.03),
                          ("P3_A subroutine integ.",  p3,  ">=0.98", p3>=0.98)):
    gates[nm] = ok
    print(f"  {nm:<26} {val:.4f}  rule {rule:<8} {'PASS' if ok else 'FAIL'}")

print("\nLADDERS (eta = correct call with EMPTY execution record)")
g1 = g2 = True
for tier, ladder in (("A",(1,2,4,8)), ("B",(2,4,8))):
    print(f"  Tier {tier}:")
    prev = -1
    for N in ladder:
        a = rows[(tier,N,"marked")]; t = rows[(tier,N,"unmarked")]
        ce, cf = CENTERS[(tier,N)]
        in_eta = abs(a["eta"]-ce) <= BAND; in_f0 = abs(t["f0call"]-cf) <= BAND
        g1 &= in_f0
        se = math.sqrt(max(a["eta"]*(1-a["eta"]),1e-9)/a["n"])
        print(f"    N={N:<2} eta={a['eta']:.4f}±{se:.4f} (band {ce:.3f}±{BAND}) {'IN' if in_eta else 'OUT':<3} | "
              f"f0call={t['f0call']:.4f} (band {cf:.2f}±{BAND}) {'IN' if in_f0 else 'OUT':<3} | fired={a['fired']:.3f}")
        if N > 1 and N <= (8 if tier=="A" else 8) and a["eta"] < prev - 0.02: g2 = False
        prev = a["eta"]
    peak = max(ladder, key=lambda N: rows[(tier,N,"marked")]["eta"])
    print(f"    peak at N={peak} (freeze predicted N={8})")
print(f"\nG1 f=0 call bands: {'PASS' if g1 else 'REVIEW'} | G2 monotone rise: {'PASS' if g2 else 'REVIEW'}")
n1 = rows[("A",1,"marked")]["eta"]
print(f"G4 N=1 EV-degenerate: eta={n1:.4f} {'PASS' if n1 < 0.05 else 'FAIL'}")
out = {"job": JOB, "backend": man["backend"], "bands": {f"{k[0]}_N{k[1]}": v for k,v in CENTERS.items()},
       "ladders": {f"{k[0]}_N{k[1]}_{k[2]}": v for k,v in rows.items()},
       "premise": {f"{k[0]}_{k[1]}": v for k,v in prem.items()},
       "gates": {**{k: bool(v) for k,v in gates.items()}, "G1_f0_bands": bool(g1), "G2_monotone": bool(g2),
                 "G4_N1_degenerate": bool(n1 < 0.05)}}
json.dump(out, open(os.path.join(root, f"results/h13_cell6_6b_grade_{JOB}.json"), "w"), indent=1)
print(f"\n[grade saved] results/h13_cell6_6b_grade_{JOB}.json")
