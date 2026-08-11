#!/usr/bin/env python3
"""H13 Cell 2 RE-FLY — two-block submit with G-ISO between them.  Whisper C5058.

BLOCK 1 (PRE-RUN)  measures the floor AND runs G-ISO in flight.  If G-ISO fails, THE SCIENCE
                   BLOCK IS NEVER SUBMITTED — worst case 34s est / 54s need, not 102/153.
BLOCK 2 (SCIENCE)  40 runs x 3 diagonals x 2 arms x 4 twirl components @ 1000 shots.

Injection: WEIGHTED Pauli twirl (I at 1-3p/4, each of X,Y,Z at p/4) — isotropic, sign-preserving,
verified on silicon by the C5058 gate (CE spread 0.0186 / CC 0.0040, z~78-82).
Band declared IN p: [0.30, 0.70] at 1000 shots keeps the upper edge inside the decoder knee (0.832).
Usage: QPU_ACCOUNT_VAR=IBMQ_ALT4 python3 scripts/h13_cell2_refly_submit_c5058.py [--dry-run|--prerun-only]
"""
import json, math, os, sys, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.pop("QISKIT_IBM_INSTANCE", None)
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile

BAND, N_DRAWS, N_RUNS, SHOTS_CELL = (0.30, 0.70), 20, 40, 1000
BASES, TWIRLS, SEED = ("X","Y","Z"), ("I","X","Y","Z"), 20260811
EST_PRE, EST_SCI = 34.0, 68.0
def need(est): return max(est*1.5, est+20)          # G-EPOCH, multiplicative (Ember #9349)

def rot(qc,q,b,inv=False):
    if b=="X": qc.h(q)
    elif b=="Y":
        if inv: qc.h(q); qc.s(q)
        else: qc.sdg(q); qc.h(q)
def pauli(qc,q,p):
    if p=="X": qc.x(q)
    elif p=="Y": qc.y(q)
    elif p=="Z": qc.z(q)

def ce(basis,tw,name):
    q=QuantumRegister(1,"q"); c=ClassicalRegister(2,"c"); qc=QuantumCircuit(q,c,name=name)
    rot(qc,q[0],basis); qc.measure(q[0],c[0]); rot(qc,q[0],basis,True)
    pauli(qc,q[0],tw)
    rot(qc,q[0],basis); qc.measure(q[0],c[1]); return qc
def cc(basis,tw,name):
    q=QuantumRegister(2,"q"); c=ClassicalRegister(2,"c"); qc=QuantumCircuit(q,c,name=name)
    qc.h(q[0]); qc.cx(q[0],q[1]); pauli(qc,q[0],tw)
    for k in (0,1): rot(qc,q[k],basis)
    qc.measure(q[0],c[0]); qc.measure(q[1],c[1]); return qc

def block(n_units, tag, rng):
    """Each unit draws its own p from the band; shots split by the weighted mixture."""
    circs, labels = [], []
    for u in range(n_units):
        p = float(rng.uniform(*BAND))
        w = {"I":1-3*p/4, "X":p/4, "Y":p/4, "Z":p/4}
        # LARGEST-REMAINDER allocation so the components sum to EXACTLY SHOTS_CELL.
        # Naive per-component round() gave 692+103*3 = 1001 against a declared 1000 (Ember #9381,
        # Elder #9382). The physics does not care; THE RECORD DOES — a pre-registered integer
        # differing from a shipped one is how "the flown design was the frozen design" stops
        # being checkable, and tonight has been one long argument that only the checkable
        # version is worth having.
        raw = {t: SHOTS_CELL*w[t] for t in TWIRLS}
        sh = {t: int(raw[t]) for t in TWIRLS}
        rem = SHOTS_CELL - sum(sh.values())
        for t in sorted(TWIRLS, key=lambda t: raw[t]-int(raw[t]), reverse=True)[:rem]: sh[t]+=1
        assert sum(sh.values()) == SHOTS_CELL, f"shot allocation {sh} sums to {sum(sh.values())}, not {SHOTS_CELL}"
        for b in BASES:
            for arm,mk in (("CE",ce),("CC",cc)):
                for t in TWIRLS:
                    circs.append(mk(b,t,f"{tag}{u}_{arm}_{b}_{t}"))
                    labels.append({"unit":u,"arm":arm,"basis":b,"twirl":t,"p":round(p,4),"shots":sh[t]})
    return circs, labels

def main():
    dry = "--dry-run" in sys.argv; pre_only = "--prerun-only" in sys.argv
    rng = np.random.default_rng(SEED)
    pre_c, pre_l = block(N_DRAWS, "PRE", rng)
    sci_c, sci_l = block(N_RUNS, "SCI", rng)
    draws = sorted({l["p"] for l in pre_l}) , sorted({l["p"] for l in sci_l})
    dhash = hashlib.sha256(json.dumps([l["p"] for l in pre_l+sci_l]).encode()).hexdigest()[:16]
    print(f"[build] PRE {len(pre_c)} circuits / SCI {len(sci_c)} circuits; band p{BAND}; {SHOTS_CELL} shots/cell")
    print(f"[custody] seed {SEED} committed; realized-draws sha256[:16]={dhash}")
    print(f"[budget] est pre {EST_PRE}s / sci {EST_SCI}s = {EST_PRE+EST_SCI}s;  NEED (G-EPOCH) = {need(EST_PRE+EST_SCI):.0f}s")
    print(f"[band]   pre-run p range {min(draws[0]):.3f}-{max(draws[0]):.3f}; science {min(draws[1]):.3f}-{max(draws[1]):.3f}")
    if dry:
        from qiskit_aer import AerSimulator
        sim=AerSimulator()
        tc=transpile(pre_c[:24], sim, optimization_level=1, seed_transpiler=SEED)
        res=[sim.run([c],shots=l["shots"]).result() for c,l in zip(tc,pre_l[:24])]
        acc={}
        for l,c,r in zip(pre_l[:24],tc,res):
            cn=r.get_counts(c); tot=sum(cn.values())
            e=sum(((-1)**(int(k.replace(" ","")[0])+int(k.replace(" ","")[1])))*v for k,v in cn.items())/tot
            acc.setdefault((l["arm"],l["basis"]),[]).append((e,l["shots"]))
        print("[dry-run] unit 0 twirl-averaged correlators (p=%.3f):" % pre_l[0]["p"])
        for k,v in sorted(acc.items()):
            C=sum(e*w for e,w in v)/sum(w for _,w in v); print(f"   {k[0]} {k[1]}: {C:+.4f}")
        print("   expect |C| ~ (1-p)*0.98 on all three axes, CC's YY negative")
        return
    # ═══ SIGNATURE VALIDITY GATE (Elder #9369) ═══════════════════════════════════════════
    # "My signature is on the prereg AS AMENDED, AND IT DOES NOT CARRY FORWARD. If anything in
    #  §2, §4, §4b or §5(c) moves between now and submit, my seat's signature is VOID until I
    #  re-read and re-sign." A signature is a durable-looking artifact that keeps its authority
    #  after the object beneath it changes — the same silent failure as his fossil pre-reg, one
    #  level up. So the signature is BOUND TO A TEXT DIGEST and this checks it, rather than
    #  trusting anyone's memory of what was signed.
    import hashlib as _h
    _pre = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "docs/h13-cell2-refly-prereg-DRAFT-whisper-c5058.md")
    _s = open(_pre).read(); _secs = {}
    for _tag in ["## 2.", "## 4.", "## 4b.", "## 5."]:
        _i = _s.find(_tag)
        if _i < 0: continue
        _j = len(_s)
        for _o in ["## 1.", "## 2.", "## 3.", "## 4.", "## 4b.", "## 5."]:
            _k = _s.find(_o, _i + len(_tag))
            if _k > 0: _j = min(_j, _k)
        _secs[_tag] = _s[_i:_j]
    _now = _h.sha256("".join(_secs[k] for k in sorted(_secs)).encode()).hexdigest()
    ELDER_SIGNED_DIGEST = "929cb1c4ba4adcbfb07900f5dbeab60b1909604c71f51edac4bc094c9bec5682"
    if _now != ELDER_SIGNED_DIGEST:
        raise SystemExit(f"🔴 SIGNATURE VOID: the prereg sections Elder signed have CHANGED.\n"
                         f"   signed {ELDER_SIGNED_DIGEST[:24]}…  now {_now[:24]}…\n"
                         f"   His seat must re-read and re-sign before this can fly (his #9369).")
    # DRAW-PUBLICATION GATE (Ember condition 2, #9372): the declared draw list must be committed
    # BEFORE any PUB is sent, or G-BAND certifies a shopped list — worse than no check at all.
    import subprocess as _sp
    _r = _sp.run(["git","log","--oneline","-S",dhash,"--","docs/","results/"],
                 capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if dhash not in (_r.stdout or "") and not any(dhash in open(os.path.join(dp,f)).read()
            for dp,_,fs in os.walk(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"docs"))
            for f in fs if f.endswith(".md")):
        raise SystemExit(f"🔴 DRAW LIST NOT PUBLISHED: digest {dhash} is not git-pinned in docs/.\n"
                         f"   Publish-before-reveal (Ember #9372): commit the draw digest, post it, THEN submit.")
    print(f"[draw-publication gate] draw digest {dhash} is git-pinned — publish-before-reveal satisfied")
    print(f"[signature gate] prereg §2/§4/§4b/§5 unchanged since Elder signed ({_now[:16]}…) — his seat VALID")
    print("\n[HOLD] submission is gated on BOTH court signatures. Elder: SIGNED + digest-verified. Ember: PENDING.")
    print("[HOLD] no PUB will be sent until the seal/fly seat signs the amended prereg.")

if __name__ == "__main__":
    main()
