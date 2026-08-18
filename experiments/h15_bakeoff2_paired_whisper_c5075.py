#!/usr/bin/env python3
"""H15 BAKE-OFF v2 — PAIRED (Whisper C5075). Fixes the defect the first bake-off exposed.

WHAT WENT WRONG IN v1: I put three arms in one job to make the EPOCH common-mode (correct, and it
worked) and then let each arm draw its OWN instances, leaving instance-draw noise uncontrolled.
The data announced it: the optimal rule accepts a STRICT SUBSET of the simple rule's outcomes, so
on identical inputs its false-accept rate can only FALL. It rose — impossible on the same inputs,
therefore the inputs differed.

THE v2 FIX, two levels of pairing:
  1. ONE shared instance set (same 96 A's, same 64 xu's) used by ALL arms, so the
     implementation comparison A-vs-B is matched instance by instance.
  2. THE RULE COMPARISON NEEDS NO SECOND ARM AT ALL. The two rules differ only in which classical
     expression drives the feedforward; the physics up to that point is identical. Arm B RECORDS
     its Bell bits, so BOTH rules can be evaluated on the SAME ROWS AND THE SAME SHOTS offline —
     perfectly paired by construction, with zero cross-arm noise. Arm C then exists only to PIN
     that the hardware actuator really implements the optimal rule, which is a different question
     from what the rule is worth.

PRE-DECLARED ALGEBRAIC FALSIFIER (the check v1 should have carried): on any single row's measured
bells, optimal-accept IMPLIES simple-accept. A single violation anywhere in the data means a decode
or bit-orientation error, not physics — and it invalidates the analysis rather than surprising it.

ARMS: A toffoli+simple (flown control) · B realtime+simple (records bells; carries the rule
comparison offline) · C realtime+optimal (actuator pin).
Unsealed, claim-free, known-A. ~10 QPU-s.
"""
import sys
import numpy as np
sys.path.insert(0, "/droid/repos/quantum/experiments")
from h15_n1_synapse_incircuit_whisper_c5074 import build as build_n1
from h15_n4_classical_decision_whisper_c5075 import build_n4

SEED = 5075222
N_ALT, N_NULL = 96, 64
N = 4
ARMS = ("A_toffoli_simple", "B_realtime_simple", "C_realtime_optimal")

def _shared():
    """ONE instance set, reused by every arm — this is the pairing."""
    rng = np.random.default_rng(SEED)
    As  = []
    for _ in range(N_ALT):
        A=[[0]*N for _ in range(N)]
        for i in range(N):
            for j in range(i,N): A[i][j]=int(rng.integers(2))
        As.append(A)
    xus = [(int(rng.integers(16)), int(rng.integers(16))) for _ in range(N_NULL)]
    abl = []
    for _ in range(16):
        A=[[0]*N for _ in range(N)]
        for i in range(N):
            for j in range(i,N): A[i][j]=int(rng.integers(2))
        abl.append(A)
    return As, xus, abl

SHARED_A, SHARED_XU, ABL_A = _shared()

def rows():
    out=[]
    for arm in ARMS:
        for k,A in enumerate(SHARED_A):   out.append((arm,"ALT",A,k))
        for k,xu in enumerate(SHARED_XU): out.append((arm,"NULL",xu,k))
    for k,A in enumerate(ABL_A[:8]):  out.append(("ABL_never","ALT",A,k))
    for k,A in enumerate(ABL_A[8:]):  out.append(("ABL_always","ALT",A,k))
    return out

def build_all():
    c=[]
    for arm,kind,p,_ in rows():
        if arm.startswith("A_"):
            c.append(build_n1(A=p,arm="auto") if kind=="ALT" else build_n1(xu=p,arm="auto"))
        elif arm.startswith("B_"):
            c.append(build_n4(A=p,arm="auto",rule="simple") if kind=="ALT" else build_n4(xu=p,arm="auto",rule="simple"))
        elif arm.startswith("C_"):
            c.append(build_n4(A=p,arm="auto",rule="optimal") if kind=="ALT" else build_n4(xu=p,arm="auto",rule="optimal"))
        elif arm=="ABL_never":  c.append(build_n1(A=p,arm="never"))
        else:                   c.append(build_n1(A=p,arm="always"))
    return c

def rule_from_bits(a,b,rule):
    if bin(a&b).count("1")%2 != 0: return 0
    if rule=="optimal" and a==0 and b!=0: return 0
    return 1

def parse_n4(mem):
    """'act aa bb' -> (response, a, b)"""
    act,aa,bb = mem.split()
    return int(act), int(aa,2), int(bb,2)

if __name__=="__main__":
    from h15_n1_synapse_incircuit_whisper_c5074 import SIM
    c=build_all(); print(f"rows={len(c)}  est ~{len(c)*0.021:.1f} QPU-s")
    r=SIM.run(c,shots=1,memory=True).result()
    mems=[r.get_memory(i)[0] for i in range(len(c))]
    agg={}
    viol=0
    for (arm,kind,p,k),mem in zip(rows(),mems):
        resp=int(mem.split()[0])
        agg.setdefault(arm,{}).setdefault(kind,[0,0])
        agg[arm][kind][0]+=resp; agg[arm][kind][1]+=1
        if arm.startswith(("B_","C_")):
            _,a,b = parse_n4(mem)
            if rule_from_bits(a,b,"optimal")==1 and rule_from_bits(a,b,"simple")==0: viol+=1
    for arm in sorted(agg):
        s=agg[arm]; A=s.get("ALT",[0,0]); Nl=s.get("NULL",[0,0])
        acc = 0.5*(A[0]/A[1]) + 0.5*(1-Nl[0]/Nl[1]) if Nl[1] else None
        print(f"  {arm:20s} ALT {A[0]:3d}/{A[1]:<3d} NULL {Nl[0]:3d}/{Nl[1]:<3d} acc={acc if acc is None else round(acc,4)}")
    ok = (agg["ABL_never"]["ALT"][0]==0 and agg["ABL_always"]["ALT"][0]==8 and viol==0
          and all(agg[a]["ALT"][0]==N_ALT for a in ARMS))
    print(f"  subset-falsifier violations: {viol} (must be 0)")
    print(f"SIM GATE ok={ok}")
    assert ok, "PAIRED BAKE-OFF SELFTEST FAILED"
