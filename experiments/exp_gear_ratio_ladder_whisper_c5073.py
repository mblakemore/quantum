#!/usr/bin/env python3
"""THE GEAR-RATIO LADDER — tuning the automatic transmission's shift stroke (Whisper C5073,
Creator GO in-terminal "run the gear-ratio ladder"; successor to the transmission flight
d9v7f7v2sl0c73blhb0g whose first candidate R=Z(2) trended +2.81 sigma, under the bar).

DESIGN: the transmission circuit unchanged (sensor -> herald -> feedforward shift + witness),
with the shift's recovery operation swept across candidates on the shared qubit q2:
  Rz(theta), theta in {pi/4, pi/2, 3pi/4, pi, 5pi/4, 3pi/2, 7pi/4}   (7 ratios; pi = the flown R)
  Rx(pi)                                                             (1 cross-axis probe)
plus a same-job NEVER anchor (no shift; the c=1 stratum baseline). 9 pubs x 8000 shots.

PRE-REGISTERED:
  METRIC: per candidate, task X-parity on the c=1 (grind) stratum vs the same-job NEVER
    c=1 stratum; z from binomial-propagated se.
  P-L1 (a ratio engages): best candidate clears z >= 3.2 (one-sided, Bonferroni-8 at
    family alpha ~0.01) -> GEAR-RATIO-FOUND, the winner named with its curve position.
  P-L2 (the curve is physics): the 7 Rz points fit A*sin(theta+phi)+B with r^2 >= 0.8
    (a partial-phase coherent error predicts a sinusoidal tuning curve; the flown pi point
    should sit ON the curve, replicating its +2.8-sigma-class trend). The CURVE is a
    deliverable even if no single point clears P-L1 - it is the transmission's gear-ratio
    profile, and its peak phase phi estimates the actual error angle.
  GATES (carried from the transmission flight): witness/herald consistency >= 0.99 on every
    shifted pub; herald rate in [0.15, 0.55] all pubs; neutral (c=0) strata match NEVER's
    within 3 sigma per pub (no grinding in neutral at any ratio).
  SELFTEST: ideal -> silent (herald ~0, witness never); forced-grind -> witness exact.
Fences: same chain, one epoch, exploratory-tuning genre (no efficacy claim beyond the
pre-stated bars); device-characterized. Account IBMQ_ALT4.
"""
import argparse, json, os, sys, math
import numpy as np
from qiskit import QuantumCircuit, transpile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

BACKEND = "ibm_marrakesh"
SHOTS = 8000
THETAS = [math.pi/4, math.pi/2, 3*math.pi/4, math.pi, 5*math.pi/4, 3*math.pi/2, 7*math.pi/4]
OUT = os.path.join(HERE, "..", "results", "exp_gear_ratio_ladder_c5073_manifest.json")


def ladder_circuit(recovery, forced_grind=False):
    """recovery: ('rz', theta) | ('rx', pi) | None (NEVER anchor)."""
    qc = QuantumCircuit(5, 5)
    qc.h(0); qc.h(1); qc.h(2); qc.h(3)
    U = lambda: qc.ccz(0, 1, 2)
    V = (lambda: qc.cx(0, 2)) if forced_grind else (lambda: qc.ccz(0, 2, 3))
    U(); V()
    qc.x(0); V(); U(); qc.x(0)
    qc.h(0)
    qc.measure(0, 0)
    if recovery is not None:
        kind, ang = recovery
        with qc.if_test((qc.clbits[0], 1)):
            if kind == "rz":
                qc.rz(ang, 2)
            else:
                qc.rx(ang, 2)
            qc.x(4)
    qc.h(1); qc.h(2); qc.h(3)
    qc.measure(1, 1); qc.measure(2, 2); qc.measure(3, 3)
    qc.measure(4, 4)
    return qc


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 20000
    c = sim.run(ladder_circuit(("rz", math.pi)), shots=shots).result().get_counts()
    herald = sum(n for s, n in c.items() if s.replace(" ", "")[-1] == "1") / shots
    assert herald < 0.01, "ideal not silent"
    c = sim.run(ladder_circuit(("rz", math.pi/2), forced_grind=True), shots=shots).result().get_counts()
    bad = sum(n for s, n in c.items()
              if s.replace(" ", "")[-1] != s.replace(" ", "")[-5])
    assert bad == 0, "witness/herald mismatch under forced grind"
    print("selftest PASS: silent when meshed; witness exact under forced grind (rz and path checked)")
    return True


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--submit", action="store_true")
    a = ap.parse_args()
    assert selftest()
    from qiskit_ibm_runtime import SamplerV2
    from ibm_multi_account import service_for_submission
    svc = service_for_submission("IBMQ_ALT4")
    backend = svc.backend(BACKEND)
    props = backend.properties()
    print(f"marrakesh cal epoch: {props.last_update_date}")
    pubs, meta = [], []
    variants = [("never", None)] + [(f"rz_{i}", ("rz", t)) for i, t in enumerate(THETAS)] + [("rx_pi", ("rx", math.pi))]
    for name, rec in variants:
        qc = ladder_circuit(rec)
        tqc = transpile(qc, backend, optimization_level=1, seed_transpiler=5)
        pubs.append((tqc, None, SHOTS))
        meta.append({"block": name, "recovery": None if rec is None else [rec[0], rec[1]],
                     "shots": SHOTS, "depth": tqc.depth()})
        print(f"  [$0-validate] {name}: depth {tqc.depth()}")
    man = {"card": "exp_gear_ratio_ladder", "cycle": "C5073", "substrate": "claude-fable-5",
           "backend": BACKEND, "cal_epoch": str(props.last_update_date), "shots": SHOTS,
           "account": "IBMQ_ALT4", "thetas": THETAS,
           "purpose": "Gear-ratio ladder: sweep the transmission's shift stroke (Rz angle on shared qubit + Rx cross-probe) vs same-job NEVER anchor on the grind stratum",
           "lineage": "transmission d9v7f7v2sl0c73blhb0g (R=Z(2) trend +2.81 sigma)",
           "prereg": "P-L1 (Bonferroni-8 z>=3.2), P-L2 (sinusoidal tuning curve r^2>=0.8), gates + selftest in docstring",
           "pubs_meta": meta}
    if a.submit:
        man["pending_jobs_at_submit"] = backend.status().pending_jobs
        job = SamplerV2(mode=backend).run(pubs)
        man["job_id"] = job.job_id()
        print(f"SUBMITTED {man['job_id']} to {BACKEND} (pending at submit: {man['pending_jobs_at_submit']})")
    else:
        print("[dry] not submitted")
    json.dump(man, open(OUT, "w"), indent=1)
    print(f"manifest -> {OUT}")


if __name__ == "__main__":
    main()
