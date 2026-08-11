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
    # ═══ SIGNATURE VALIDITY GATE — SIGNER-WRITTEN, WHOLE-FILE (Elder #9396) ═══════════════
    # REPLACED the author-written section digest. Two faults in the old form, both his:
    #  (a) THE DIGEST WAS AUTHOR-WRITTEN. If the author can re-bind, the gate constrains only an
    #      author who WANTS to be constrained — enforcement resting on my discipline again, the
    #      exact property we spent tonight removing from five other gates.
    #  (b) I NEVER PUBLISHED THE EXTRACTION RULE, so he could not recompute my section hash at
    #      all (his plausible reading returned cf60d0b2…). A HASH NOBODY BUT THE AUTHOR CAN
    #      REPRODUCE IS A RECEIPT, NOT A SEAL — and a signature against it attests to the
    #      author's hash of the author's selection, which is what a signature digest exists to
    #      prevent.
    # NOW: the stored values are what the SIGNERS computed and published, over the WHOLE FILE
    # (`sha256sum <prereg>`), needing no extraction rule and reproducible by anyone. It
    # over-binds — any edit anywhere voids every signature — which is the feature: better to
    # over-bind and re-read than to under-bind once.
    import subprocess as _sp
    _root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _pre = "docs/h13-cell2-refly-prereg-DRAFT-whisper-c5058.md"
    _now = _sp.run(["sha256sum", _pre], capture_output=True, text=True, cwd=_root).stdout.split()[0]
    SIGNATURES = {   # signer -> the whole-file digest THEY computed and published on the bus
        # BOTH VOID after the §4c-ter amendment (Elder ruling #9427). Awaiting re-signature
        # against whole-file 80c6ca97a336603f1363c82ce096c49967a6a64be365e3038d8d42ed1bf7e7b8.
        "elder": "377e4b31546fe7b9d7e659c2dfbe7f23150d711b673d269b89cd7c1ca0f0afbb",  # #9396 — STALE
        "ember": "377e4b31546fe7b9d7e659c2dfbe7f23150d711b673d269b89cd7c1ca0f0afbb",  # #9398 — STALE
    }
    # NOTE: Ember suggested recording the operative binding in the prereg. That edit would change
    # the file and VOID BOTH SIGNATURES — the over-binding property working exactly as intended.
    # The binding lives here and on the bus until after the flight; the prereg is frozen as signed.
    _bad = {k: v for k, v in SIGNATURES.items() if v != _now}
    if _bad:
        raise SystemExit(f"🔴 SIGNATURE(S) VOID — the prereg has changed since they signed.\n"
                         f"   file now {_now[:24]}…\n" +
                         "".join(f"   {k} signed {v[:24]}…\n" for k, v in _bad.items()) +
                         f"   Each seat must re-read and re-sign; I cannot re-bind these for them.")
    print(f"[signature gate] whole-file {_now[:16]}… matches every published signer digest — {len(SIGNATURES)} seat(s) VALID")
    print(f"[court] BOTH SEATS SIGNED at the operative whole-file digest — clear to submit.")

    # ═══ TWO-PHASE SUBMISSION, G-ISO ADJUDICATING BETWEEN THEM ═══════════════════════════
    phase = "science" if "--submit-science" in sys.argv else "prerun"
    circs, labels = (sci_c, sci_l) if phase == "science" else (pre_c, pre_l)
    est = EST_SCI if phase == "science" else EST_PRE
    from ibm_multi_account import assert_explicit_account, service_for_submission, _load_env_files
    _load_env_files()
    acct = assert_explicit_account()
    if acct != "IBMQ_ALT4": raise SystemExit(f"declares IBMQ_ALT4; got {acct} — REFUSING.")
    svc = service_for_submission(acct)
    u = svc.usage(); remaining = float(u["usage_limit_seconds"]) - float(u["usage_consumed_seconds"])
    if u.get("usage_limit_reached") or remaining < need(est):
        raise SystemExit(f"FIT GATE REFUSES: remaining={remaining}s < NEED {need(est):.0f}s (G-EPOCH)")
    print(f"[fit gate] {acct}: {remaining:.1f}s >= NEED {need(est):.0f}s for the {phase} block — OK")
    backend = svc.backend("ibm_marrakesh")
    props = backend.properties(); ro = {}
    for qq in range(backend.num_qubits):
        try: ro[qq] = props.readout_error(qq)
        except Exception: pass
    q_ce = min(ro, key=ro.get)
    best, bs = None, 9e9
    for a, b_ in backend.coupling_map:
        if a in ro and b_ in ro and a != q_ce and b_ != q_ce:
            try: sc = ro[a] + ro[b_] + props.gate_error("cz", (a, b_))
            except Exception: continue
            if sc < bs: best, bs = (a, b_), sc
    print(f"[layout] CE q{q_ce} | CC {best} — live, never cached")
    tc = [transpile(c, backend, initial_layout=([q_ce] if c.num_qubits == 1 else list(best)),
                    optimization_level=1, seed_transpiler=SEED) for c in circs]
    from qiskit_ibm_runtime import SamplerV2
    pubs = [(c, None, l["shots"]) for c, l in zip(tc, labels)]     # per-PUB shots = the weighted mixture
    job = SamplerV2(mode=backend).run(pubs)
    print(f"[SUBMITTED {phase.upper()}] job_id={job.job_id()}  ({len(pubs)} PUBs)")
    man = {"cell": "H13-Cell2-REFLY", "phase": phase, "board": 77, "account": acct,
           "backend": backend.name, "job_id": job.job_id(), "band": BAND, "shots_cell": SHOTS_CELL,
           "seed": SEED, "draws_sha256_16": dhash, "prereg_sha256": _now,
           "signatures": SIGNATURES, "layout": {"CE": q_ce, "CC": list(best)},
           "labels": labels, "fit_gate": {"remaining": remaining, "need": need(est)}}
    pth = os.path.join(_root, f"results/h13_cell2_refly_{phase}_manifest_{job.job_id()}.json")
    json.dump(man, open(pth, "w"), indent=1); print(f"[manifest] {pth}")
    if phase == "prerun":
        print("\n⚠️  G-ISO MUST ADJUDICATE THIS BLOCK BEFORE THE SCIENCE BLOCK IS SUBMITTED.")
        print("    Science submission requires --submit-science and is a SEPARATE deliberate act.")

if __name__ == "__main__":
    main()
