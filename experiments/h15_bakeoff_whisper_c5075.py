#!/usr/bin/env python3
"""H15 BAKE-OFF (Whisper C5075) — three arms in ONE job, epoch common-mode.

WHY ONE JOB: the ALT rate moved 25pp between two jobs nine minutes apart, and that confound has
now overturned TWO of this campaign's comparisons (die selection, then the N2v2 premise). Putting
the arms in a single job makes the epoch common-mode, so the differences are design differences.

THE 2-FACTOR DESIGN:
  A  toffoli_simple   the FLOWN N1 loop, as control
  B  realtime_simple  A -> B isolates the IMPLEMENTATION change (Toffoli chain -> real-time logic)
  C  realtime_optimal B -> C isolates the RULE change (parity-only -> support-exact)
Plus the 8/8 ablation contract so the job carries its own instrument check.

PRE-REGISTERED PREDICTIONS (stated before the flight, so the result can disagree with me):
  * B > A on ALT accept, from the kingston probe's same-job sensor-vs-Toffoli reading (0.9375 vs
    0.875). The representative depolarizing model predicts the OPPOSITE (B slightly worse, eight
    readouts costing more than four Toffolis). Model and hardware disagree; this arm adjudicates.
  * C accuracy > B accuracy, because the rule change removes 15 zero-ALT-probability cells from
    the accept set. This is arithmetic, not physics, and should hold in any epoch.
  * C ALT accept slightly BELOW B (noisy ALT outcomes landing in the excluded cells are now
    rejected) - the gain is on the NULL side and must be read on ACCURACY, not on ALT alone.
DECISION RULE: adopt the arm with the highest measured accuracy; if B and C are within 1 SE of A
on accuracy, keep the flown design (do not churn a design on noise).
Unsealed, claim-free, known-A: same authorisation class as the R1 probes.
"""
import sys
import numpy as np
sys.path.insert(0, "/droid/repos/quantum/experiments")
from h15_n1_synapse_incircuit_whisper_c5074 import build as build_n1, classical_rule
from h15_n4_classical_decision_whisper_c5075 import build_n4, read as read_n4

SEED = 5075111
PER_ARM = 64          # ALT rows per arm
NULL_PER_ARM = 32     # NULL rows per arm (accuracy needs both sides)
N = 4

def draw_A(rng):
    A=[[0]*N for _ in range(N)]
    for i in range(N):
        for j in range(i,N): A[i][j]=int(rng.integers(2))
    return A

def rows():
    rng = np.random.default_rng(SEED)
    out=[]
    for arm in ("A_toffoli_simple","B_realtime_simple","C_realtime_optimal"):
        for _ in range(PER_ARM):     out.append((arm,"ALT", draw_A(rng)))
        for _ in range(NULL_PER_ARM): out.append((arm,"NULL",(int(rng.integers(16)),int(rng.integers(16)))))
    for _ in range(8): out.append(("ABL_never","ALT",draw_A(rng)))
    for _ in range(8): out.append(("ABL_always","ALT",draw_A(rng)))
    return out

def build_all():
    circs=[]
    for arm,kind,payload in rows():
        if arm.startswith("A_"):
            circs.append(build_n1(A=payload,arm="auto") if kind=="ALT" else build_n1(xu=payload,arm="auto"))
        elif arm.startswith("B_"):
            circs.append(build_n4(A=payload,arm="auto",rule="simple") if kind=="ALT" else build_n4(xu=payload,arm="auto",rule="simple"))
        elif arm.startswith("C_"):
            circs.append(build_n4(A=payload,arm="auto",rule="optimal") if kind=="ALT" else build_n4(xu=payload,arm="auto",rule="optimal"))
        elif arm=="ABL_never":
            circs.append(build_n1(A=payload,arm="never"))
        else:
            circs.append(build_n1(A=payload,arm="always"))
    return circs

def decode(mems):
    """A-arm memories are 'act dec bell'; B/C are 'act aa bb'. Response is field 0 either way."""
    out={}
    for (arm,kind,_),mem in zip(rows(),mems):
        resp = int(mem.split()[0])
        d=out.setdefault(arm,{}).setdefault(kind,[0,0])
        d[0]+=resp; d[1]+=1
    return out

def accuracy(d):
    a=d.get("ALT",[0,1]); n=d.get("NULL",[0,1])
    if n[1]==0: return None
    return 0.5*(a[0]/a[1]) + 0.5*(1-n[0]/n[1])

if __name__=="__main__":
    import json
    from h15_n1_synapse_incircuit_whisper_c5074 import SIM
    circs=build_all()
    r=SIM.run(circs,shots=1,memory=True).result()
    mems=[r.get_memory(i)[0] for i in range(len(circs))]
    d=decode(mems)
    print(f"rows={len(circs)}  est ~{len(circs)*0.021:.1f} QPU-s")
    for arm in sorted(d):
        acc=accuracy(d[arm]); s=d[arm]
        print(f"  {arm:20s} ALT {s.get('ALT',[0,0])}  NULL {s.get('NULL',[0,0])}  acc={acc if acc is None else round(acc,4)}")
    ok = (d["ABL_never"]["ALT"][0]==0 and d["ABL_always"]["ALT"][0]==8
          and all(d[a]["ALT"][0]==PER_ARM for a in ("A_toffoli_simple","B_realtime_simple","C_realtime_optimal")))
    print(f"SIM GATE ok={ok} (noiseless: all ALT arms must be perfect, never 0/8, always 8/8)")
    assert ok, "BAKE-OFF SELFTEST FAILED"
