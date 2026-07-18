#!/usr/bin/env python3
"""Exp155 — Delayed-choice quantum eraser on IBM hardware ("the choice in the future
decides whether the past interfered"). Creator directive (2026-07-18): fly the most
frontier/star-trek self-verifying experiments until Quantinuum access; Elder's
intrinsic-falsifier bar. Advisor-hardened design. New quantum-network museum wing.

THE AHA. A system qubit S is put in superposition and its "which-path" information is
copied onto a marker qubit M (this destroys S's interference). Whether S's fringe REAPPEARS
depends on a later CHOICE about M: erase the which-path info (measure M in the conjugate
basis) and the fringe returns in coincidence; keep it (measure M in Z) and S stays flat.
In the DYNAMIC arm the choice is made by a quantum coin flipped AFTER S is already measured
— so a future random choice controls whether the already-recorded past shows a fringe.

THREE ARMS (all self-verifying — we hold the phase phi and predict the fringe exactly):
  A) STATIC ERASE     : H(M) before measuring M (which-path erased). Conditional P(S=0|M=0)
                        traces (1+cos phi)/2  -> full-visibility fringe.  [headline, reachable]
  B) STATIC WHICHPATH : measure M in Z (which-path kept). SAME coincidence post-selection as A.
                        Conditional P(S=0|M=0) is flat 1/2 -> NO fringe.   [MATCHED CONTROL]
  C) DYNAMIC DELAYED  : measure S; THEN H-ancilla -> quantum coin r (measured after S);
                        if r==1 apply H(M) (erase), else keep. Sort S by (r, M). r=1 branch
                        = fringe, r=0 branch = flat. The future coin toggles the past's fringe.
                        [the genuine Wheeler delayed choice; its own matched control is r=0]

THE NUMBER ON A CAPABILITY. Fringe visibility V = (Pmax-Pmin)/(Pmax+Pmin) of the coincidence
conditional P(S=0|M=0) vs phi. Erase should give large V, which-path V~0. Headline =
V_erase - V_whichpath (the erasure signal). The DYNAMIC arm crosses the same gap with the
choice provably in S's future.

MATCHED CONTROL (Ember C4196 discipline). The confound: does post-selection alone manufacture
a fringe? The which-path arm runs the IDENTICAL coincidence sort; H(M) is the ONLY independent
variable. If sorting made fringes, B would show one too. It must not.

NO-SIGNALING FENCE (the honesty guard, also a measured number). The UNCONDITIONED marginal
P(S=0) is flat for every arm at every phi -> V_marginal ~ 0. The fringe lives only in
coincidence; nothing about M's future choice is visible in S's marginal. No FTL, no
retrocausal signaling. That flatness is the fence AND a first-class result.

FENCE (headline): a hardware demonstration of the eraser primitive; "delayed choice" is the
temporal ORDER of the coin vs S's measurement (dynamic arm), not a claim about causation.
Finite visibility (SPAM + 1 CX + marker idle/feed-forward latency). Single system+marker.

Usage:
  python3 exp155_delayed_choice_eraser_ember.py --selftest   # noiseless truth-gate (can fail)
  python3 exp155_delayed_choice_eraser_ember.py --submit [--backend ibm_fez --shots 4000]
  python3 exp155_delayed_choice_eraser_ember.py --decode --manifest ../results/exp155_manifest.json
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

N_PHI = 8
PHASES = [2.0 * np.pi * k / N_PHI for k in range(N_PHI)]   # 0, pi/4, ... 7pi/4


def _bit(key, i):
    """clbit i, counting from the right (c0 = index 0). qiskit string is MSB-left."""
    b = key.replace(" ", "")
    return b[-1 - i]


# ---------- STATIC arms (A erase / B which-path): 2 qubits, 2 clbits ----------
def static_circuit(phi, erase):
    """q0=S, q1=M. Entangle which-path onto M, set fringe phase phi, read S in X basis.
    erase=True -> H(M) before measure (conjugate basis, which-path erased).
    erase=False -> measure M in Z (which-path kept = MATCHED CONTROL). Both measured at END
    (advisor: static measure-first buys no observable delayed choice, only marker idle)."""
    qc = QuantumCircuit(2, 2)
    qc.h(0); qc.cx(0, 1)          # S superposition, copy which-path to M -> (|00>+|11>)/rt2
    qc.rz(phi, 0)                 # fringe phase -> (|00>+e^{i phi}|11>)/rt2
    qc.h(0)                       # read S in X basis
    qc.barrier()
    if erase:
        qc.h(1)                   # erase which-path (conjugate basis)
    qc.measure(0, 0); qc.measure(1, 1)
    return qc


# ---------- DYNAMIC arm C: genuine delayed choice via a quantum coin AFTER S ----------
def dynamic_circuit(phi):
    """q0=S, q1=M, q2=coin. c0=S, c1=M, c2=r. Measure S FIRST, then flip a quantum coin r,
    then CONDITIONALLY erase (H(M)) iff r==1 -> the choice is causally after S's detection."""
    qc = QuantumCircuit(3, 3)
    qc.h(0); qc.cx(0, 1)
    qc.rz(phi, 0)
    qc.h(0)
    qc.measure(0, 0)              # S recorded -- "the past"
    qc.barrier()
    qc.h(2); qc.measure(2, 2)     # quantum coin r, generated AFTER S
    with qc.if_test((qc.clbits[2], 1)):
        qc.h(1)                   # r=1 -> erase which-path ; r=0 -> keep (matched control)
    qc.measure(1, 1)
    return qc


# ---------- visibility from coincidence-sorted counts ----------
def _cond_fringe(counts_by_phi, select):
    """P(S=0 | M=0 [and select]) across phi. select(key)->bool filters the delayed-choice branch.
    Returns (conditional P(S=0) list, marginal P(S=0) list) over phi."""
    cond, marg = [], []
    for counts in counts_by_phi:
        s0_m0 = s_all_m0 = s0_all = tot = 0
        for key, c in counts.items():
            if select is not None and not select(key):
                continue
            s0 = _bit(key, 0) == "0"; m0 = _bit(key, 1) == "0"
            tot += c
            if s0: s0_all += c
            if m0:
                s_all_m0 += c
                if s0: s0_m0 += c
        cond.append(s0_m0 / s_all_m0 if s_all_m0 else 0.5)
        marg.append(s0_all / tot if tot else 0.5)
    return cond, marg


def _visibility(p):
    p = np.asarray(p, float)
    hi, lo = p.max(), p.min()
    return (hi - lo) / (hi + lo) if (hi + lo) > 1e-9 else 0.0


def _run_sim(circuits, shots=30000):
    from qiskit_aer import AerSimulator
    sim = AerSimulator()
    return [sim.run(qc, shots=shots).result().get_counts() for qc in circuits]


def selftest():
    """P3 TRUTH-GATE (noiseless Aer). ERASE fringe visibility ~1; WHICHPATH ~0 (matched
    control, same sort); MARGINAL ~0 for all (no-signaling). DYNAMIC r=1 ~1, r=0 ~0.
    Every assertion can fail -> falsifiability built in."""
    stat_e = _run_sim([static_circuit(p, True) for p in PHASES])
    stat_w = _run_sim([static_circuit(p, False) for p in PHASES])
    dyn = _run_sim([dynamic_circuit(p) for p in PHASES])

    ce, me = _cond_fringe(stat_e, None)
    cw, mw = _cond_fringe(stat_w, None)
    d1, dm1 = _cond_fringe(dyn, lambda k: _bit(k, 2) == "1")   # coin=1 -> erase
    d0, _ = _cond_fringe(dyn, lambda k: _bit(k, 2) == "0")     # coin=0 -> which-path

    Ve, Vw = _visibility(ce), _visibility(cw)
    Vd1, Vd0 = _visibility(d1), _visibility(d0)
    Vmarg = max(_visibility(me), _visibility(mw), _visibility(dm1))

    print("Exp155 selftest (noiseless Aer) | phi sweep:", [f"{p:.2f}" for p in PHASES])
    print(f"  STATIC  erase   V={Ve:.3f}   cond P(S=0|M=0)={[f'{x:.2f}' for x in ce]}")
    print(f"  STATIC  whichpt V={Vw:.3f}   cond P(S=0|M=0)={[f'{x:.2f}' for x in cw]}  (MATCHED CONTROL)")
    print(f"  DYNAMIC coin=1  V={Vd1:.3f}   (future coin erases)")
    print(f"  DYNAMIC coin=0  V={Vd0:.3f}   (future coin keeps which-path)")
    print(f"  NO-SIGNALING marginal visibility (max over arms) V_marg={Vmarg:.3f}  (must be ~0)")

    assert Ve > 0.98, "erase arm must show full-visibility fringe"
    assert Vw < 0.05, "which-path matched control must be flat (post-selection alone makes NO fringe)"
    assert Vd1 > 0.98, "dynamic future-erase branch must show the fringe"
    # coin split (~1/2) x M=0 condition (~1/2) -> ~1/4 the statistics of the static control,
    # so its zero-visibility sampling floor is ~2x higher; 0.08 reflects the shot count, not physics.
    assert Vd0 < 0.08, "dynamic future-keep branch must be flat"
    assert Vmarg < 0.05, "NO-SIGNALING: the unconditioned marginal must be flat for every arm"
    print("SELFTEST PASS: erase reveals the fringe, which-path (same sort) does not, the future "
          "coin toggles it, and no marginal ever moves (no signaling). Test can fail.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    circuits, order = [], []
    for i, p in enumerate(PHASES):
        circuits.append(transpile(static_circuit(p, True), backend=backend, optimization_level=3))
        order.append(["static_erase", i])
    for i, p in enumerate(PHASES):
        circuits.append(transpile(static_circuit(p, False), backend=backend, optimization_level=3))
        order.append(["static_whichpath", i])
    for i, p in enumerate(PHASES):
        circuits.append(transpile(dynamic_circuit(p), backend=backend, optimization_level=3))
        order.append(["dynamic", i])
    sampler = SamplerV2(mode=backend); job = sampler.run(circuits, shots=shots)
    manifest = {"exp": 155, "backend": backend_name, "shots": shots, "job_id": job.job_id(),
                "phases": PHASES, "order": order,
                "prereg": {"confidence": 0.60,
                           "gate": "V_erase - V_whichpath > 0.2 AND V_marginal < 0.1",
                           "dynamic_expected_residual": "marker-idle dephasing lowers V_dynamic below "
                                                        "V_static (Exp143/144/154 idle-error class)"},
                "note": "delayed-choice quantum eraser; static erase/whichpath matched control + "
                        "dynamic quantum-coin delayed choice; self-verifying (known phi); no-signaling fence"}
    out = os.path.join(HERE, "..", "results", "exp155_manifest.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(manifest, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits = 3 arms x {N_PHI} phi, {shots} shots) -> {out}")


def decode(mp):
    from run_exp66_qpu_partb import _get_ibm_service
    svc = _get_ibm_service(); man = json.load(open(mp)); res = svc.job(man["job_id"]).result()
    order = man["order"]
    by_arm = {"static_erase": [None] * N_PHI, "static_whichpath": [None] * N_PHI, "dynamic": [None] * N_PHI}
    for idx, (arm, i) in enumerate(order):
        r = res[idx]; reg = list(r.data.keys())[0]
        by_arm[arm][i] = getattr(r.data, reg).get_counts()

    ce, me = _cond_fringe(by_arm["static_erase"], None)
    cw, mw = _cond_fringe(by_arm["static_whichpath"], None)
    d1, dm1 = _cond_fringe(by_arm["dynamic"], lambda k: _bit(k, 2) == "1")
    d0, _ = _cond_fringe(by_arm["dynamic"], lambda k: _bit(k, 2) == "0")

    Ve, Vw = _visibility(ce), _visibility(cw)
    Vd1, Vd0 = _visibility(d1), _visibility(d0)
    Vmarg = max(_visibility(me), _visibility(mw), _visibility(dm1))
    signal = Ve - Vw

    print(f"Exp155 decode | job {man['job_id']} | backend {man['backend']}")
    print(f"  phi = {[f'{p:.2f}' for p in man['phases']]}")
    print(f"  STATIC  erase    V={Ve:.3f}  cond={[f'{x:.2f}' for x in ce]}")
    print(f"  STATIC  whichpath V={Vw:.3f}  cond={[f'{x:.2f}' for x in cw]}   (MATCHED CONTROL)")
    print(f"  DYNAMIC coin=1    V={Vd1:.3f}  (future coin erases)  cond={[f'{x:.2f}' for x in d1]}")
    print(f"  DYNAMIC coin=0    V={Vd0:.3f}  (future coin keeps)   cond={[f'{x:.2f}' for x in d0]}")
    print(f"  NO-SIGNALING marginal V_marg={Vmarg:.3f}")
    print(f"\n  ERASURE SIGNAL  V_erase - V_whichpath = {signal:+.3f}")
    gate = signal > 0.2 and Vmarg < 0.1
    print(f"  PRE-REG GATE (>0.2 AND V_marg<0.1): {'HELD' if gate else 'FALSIFIED'}")
    print(f"  DYNAMIC delayed-choice signal V(coin=1)-V(coin=0) = {Vd1 - Vd0:+.3f} "
          f"(future quantum coin toggles the past's fringe; idle-degraded vs static)")

    out = {"job_id": man["job_id"], "backend": man["backend"],
           "V_erase": Ve, "V_whichpath": Vw, "erasure_signal": signal,
           "V_dynamic_erase": Vd1, "V_dynamic_keep": Vd0, "dynamic_signal": Vd1 - Vd0,
           "V_marginal": Vmarg, "prereg_gate_held": bool(gate),
           "cond_erase": ce, "cond_whichpath": cw, "cond_dyn1": d1, "cond_dyn0": d0}
    fn = os.path.join(HERE, "..", "results", "exp155_decode.json")
    json.dump(out, open(fn, "w"), indent=1)
    print(f"-> {fn}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true"); ap.add_argument("--submit", action="store_true")
    ap.add_argument("--decode", action="store_true"); ap.add_argument("--manifest")
    ap.add_argument("--backend", default="ibm_fez"); ap.add_argument("--shots", type=int, default=4000)
    a = ap.parse_args()
    if a.selftest: selftest()
    elif a.submit: submit(a.backend, a.shots)
    elif a.decode: decode(a.manifest or os.path.join(HERE, "..", "results", "exp155_manifest.json"))
    else: ap.print_help()
