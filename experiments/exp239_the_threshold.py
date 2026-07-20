#!/usr/bin/env python3
"""Exp239 — THE THRESHOLD: does the code's own machinery fix MORE than it introduces? C4917.

The question Exp238 deliberately did NOT answer. 238 corrected an error I INJECTED (free, sim-calibrated
recovery). The threshold question is different and is the one that decides scalability: held idle under
the machine's OWN noise, does an actively-corrected logical qubit remember BETTER than a bare physical
qubit over the same wall-clock time? If yes -> above the pseudo-threshold (the code's overhead is worth
paying). If no -> below threshold (encode+readout overhead costs more than the protection buys).

FRUGAL, INTERPRETABLE, NON-FOREGONE CHOICE: the 3-qubit BIT-FLIP code (236) as a memory against the
dominant idle channel — T1 amplitude damping, which relaxes |1> -> |0>. Analytic crossover with IDEAL
gates: bare survival p=exp(-t/T1); coded (majority vote corrects one relaxation) p^2(3-2p); coded beats
bare exactly when p>1/2 (t < T1*ln2). So with perfect gates the code ALWAYS wins for t<0.69*T1 — the
real question is whether ibm_fez's encode (2 CX) + 3-qubit readout overhead is small enough to preserve
that crossover. That is the pseudo-threshold, cleanly, and the answer is not rigged either way.

METHOD: prepare |1> bare (1 qubit) and |1_L>=|111> coded (3 qubits); idle both the SAME wall-clock
delay tau; measure; bare fidelity = P(read 1), coded fidelity = P(majority vote = 1), active correction
= majority (single relaxation fixed, all shots kept). Sweep tau across ~T1. A |0> control (T1 ground
state, should not decay) confirms the asymmetry is relaxation, not gates/readout.

FROZEN GATE (pre-register BOTH directions as reportable — advisor: a threshold flight reports where the
crossover sits, it does not root for one side):
  G1_MEMORY_ADVANTAGE: there exists an idle tau>0 with F_coded(tau) - F_bare(tau) >= 0.02.
     HELD  = above the pseudo-threshold for the bit-flip/T1 channel — active correction extends |1>
             memory on ibm_fez (the code's machinery fixes more than it introduces, for this channel).
     NOT HELD = below threshold — the encode+readout overhead exceeds the protection. An honest,
             valuable result, NOT a failure; it quantifies how far current hardware sits from break-even.
  Registered verdict = G1. REPORTED either way: full F_coded/F_bare curves, crossover tau* (or none),
     the tau=0 overhead gap, the |0> control.
SCOPE: bit-flip/T1 channel only (the repetition code protects |1> against relaxation, NOT a superposition
  against dephasing). This is the pseudo-threshold for ONE channel — a genuine, interpretable memory
  test, not the full-quantum-memory threshold. The full [[9,1,3]] memory (all channels) is a heavier
  separate flight and is expected BELOW threshold given 238's ~32-CNOT overhead; noted, not claimed.
  Contribution = the campaign's first threshold/break-even measurement: does QEC net-help memory here.
BUDGET CHECK (C4887): shallow (2 CX encode + delay + readout). Effect is hardware-only (needs real T1).
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

TAUS_US = (0, 50, 100, 150, 200, 250)      # idle sweep in microseconds (spans ~T1 on ibm_fez)


def bare_circuit(state, tau_us):
    qc = QuantumCircuit(1, 1)
    if state == "1": qc.x(0)
    qc.barrier()
    if tau_us > 0: qc.delay(tau_us, 0, unit="us")
    qc.barrier()
    qc.measure(0, 0)
    return qc


def coded_circuit(state, tau_us):
    qc = QuantumCircuit(3, 3)
    if state == "1": qc.x(0)
    qc.cx(0, 1); qc.cx(0, 2)               # |state_L> = |state state state>
    qc.barrier()
    if tau_us > 0:
        for q in range(3): qc.delay(tau_us, q, unit="us")
    qc.barrier()
    for q in range(3): qc.measure(q, q)
    return qc


def _bare_fid(counts, state):
    want = int(state); ok = tot = 0
    for s, n in counts.items():
        tot += n
        if int(s.replace(" ", "")[-1]) == want: ok += n
    return ok / tot


def _coded_fid(counts, state):
    """active correction = majority vote over the 3 physical qubits; all shots kept."""
    want = int(state); ok = tot = 0
    for s, n in counts.items():
        b = s.replace(" ", ""); v = [int(b[-1 - i]) for i in range(3)]
        logical = 1 if (v[0] + v[1] + v[2]) >= 2 else 0
        tot += n
        if logical == want: ok += n
    return ok / tot


def selftest():
    from qiskit_aer import AerSimulator
    from qiskit_aer.noise import NoiseModel, amplitude_damping_error
    sim = AerSimulator(); shots = 40000
    print("Exp239 selftest | THE THRESHOLD — 3-qubit bit-flip code as memory vs T1")

    # (1) WIRING: noiseless, zero idle -> both codes read the state perfectly.
    for state in ("0", "1"):
        fb = _bare_fid(sim.run(bare_circuit(state, 0), shots=shots).result().get_counts(), state)
        fc = _coded_fid(sim.run(coded_circuit(state, 0), shots=shots).result().get_counts(), state)
        assert fb > 0.99 and fc > 0.99, "no-idle readout must be exact"
    print("  (1) wiring OK: |0>,|1> read exactly at zero idle, both bare and coded")

    # (2) CORRECTION IS REAL: inject one bit-flip into the coded |111> -> majority still recovers,
    #     while the bare qubit is flipped. (proves the decode CORRECTS, not just reads)
    qc = QuantumCircuit(3, 3); qc.x(0); qc.cx(0, 1); qc.cx(0, 2); qc.x(1)  # one relaxation-like flip
    for q in range(3): qc.measure(q, q)
    fc = _coded_fid(sim.run(qc, shots=shots).result().get_counts(), "1")
    assert fc > 0.99, "majority vote must correct a single bit-flip"
    print(f"  (2) correction OK: single bit-flip in |1_L> recovered by majority ({fc:.3f})")

    # (3) CROSSOVER IS DETECTABLE: with amplitude damping on an 'id' idle (ideal gates otherwise),
    #     the coded memory must beat bare for small damping — proving the experiment can SEE the
    #     memory advantage if the hardware overhead is low enough.
    print("  (3) amplitude-damping sweep (ideal gates): does coded beat bare?")
    won = False
    for gamma in (0.1, 0.2, 0.3):
        nm = NoiseModel()
        nm.add_quantum_error(amplitude_damping_error(gamma), ["id"], [0])
        s = AerSimulator(noise_model=nm)
        def bare_id():
            qc = QuantumCircuit(1, 1); qc.x(0); qc.id(0); qc.measure(0, 0); return qc
        def coded_id():
            qc = QuantumCircuit(3, 3); qc.x(0); qc.cx(0, 1); qc.cx(0, 2)
            for q in range(3): qc.id(q)
            for q in range(3): qc.measure(q, q);
            return qc
        # apply damping per qubit by mapping id error to each qubit
        nm2 = NoiseModel()
        for q in range(3): nm2.add_quantum_error(amplitude_damping_error(gamma), ["id"], [q])
        s3 = AerSimulator(noise_model=nm2)
        fb = _bare_fid(s.run(bare_id(), shots=shots).result().get_counts(), "1")
        fc = _coded_fid(s3.run(coded_id(), shots=shots).result().get_counts(), "1")
        adv = fc - fb; won = won or (adv > 0.0)
        print(f"     gamma={gamma}: bare {fb:.3f}  coded {fc:.3f}  advantage {adv:+.3f}")
    assert won, "coded memory must beat bare under amplitude damping (else the test cannot detect it)"
    print("SELFTEST PASS: wiring exact, majority vote corrects a real flip, and the coded memory beats "
          "bare under amplitude damping with ideal gates — the experiment CAN detect a threshold "
          "advantage. Whether ibm_fez's real gate+readout overhead preserves it is the hardware question.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    order = []
    for tau in TAUS_US:
        order.append(["bare", "1", tau]); order.append(["coded", "1", tau])
    order.append(["bare", "0", TAUS_US[-1]]); order.append(["coded", "0", TAUS_US[-1]])  # T1-ground control
    def build(o):
        k, st, tau = o
        return bare_circuit(st, tau) if k == "bare" else coded_circuit(st, tau)
    builds = [build(o) for o in order]
    circuits = [transpile(qc, backend=backend, optimization_level=1, seed_transpiler=0) for qc in builds]
    n2s = [sum(1 for i in c.data if i.operation.num_qubits == 2) for c in circuits]
    print(f"  DEPTH CHECK: {len(circuits)} circuits, 2q {min(n2s)}-{max(n2s)} (opt_level=1 to preserve delays)")
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    out = os.path.join(HERE, "..", "results", "exp239_the_threshold_manifest.json")
    man = {"exp": 239, "slug": "the_threshold", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "order": [[o[0], o[1], o[2]] for o in order], "taus_us": list(TAUS_US),
           "prereg": {"G1_memory_advantage": "exists tau>0 with F_coded - F_bare >= 0.02",
                      "registered_verdict": "G1 — HELD=above pseudo-threshold (bit-flip/T1), NOT HELD=below (honest)",
                      "reported": "full F_coded/F_bare curves, crossover tau*, tau=0 overhead gap, |0> control",
                      "scope": "bit-flip/T1 channel only; pseudo-threshold for ONE channel; full [[9,1,3]] "
                               "memory expected below-threshold, separate flight"}}
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp239_the_threshold_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    raw = {}
    for idx, o in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[tuple(o)] = getattr(r0.data, reg).get_counts()
    print(f"Exp239 THE THRESHOLD decode | job {man['job_id']}")
    taus = man["taus_us"]; best_adv = -1.0; best_tau = None; cross_tau = None
    print("  tau(us) | F_bare  F_coded  advantage")
    for tau in taus:
        fb = _bare_fid(raw[("bare", "1", tau)], "1")
        fc = _coded_fid(raw[("coded", "1", tau)], "1")
        adv = fc - fb
        if adv > best_adv: best_adv, best_tau = adv, tau
        if cross_tau is None and adv >= 0.02: cross_tau = tau
        flag = " <-- crossover" if (adv >= 0.02 and cross_tau == tau) else ""
        print(f"  {tau:6d}  |  {fb:.3f}   {fc:.3f}    {adv:+.3f}{flag}")
    fb0 = _bare_fid(raw[("bare", "1", 0)], "1"); fc0 = _coded_fid(raw[("coded", "1", 0)], "1")
    ctrl_b = _bare_fid(raw[("bare", "0", taus[-1])], "0"); ctrl_c = _coded_fid(raw[("coded", "0", taus[-1])], "0")
    print(f"\n  tau=0 overhead gap (coded-bare): {fc0-fb0:+.3f}  (the price the code must overcome)")
    print(f"  |0> control at tau={taus[-1]}us: bare {ctrl_b:.3f} coded {ctrl_c:.3f} (T1 ground — should stay high)")
    g1 = best_adv >= 0.02
    print(f"\nG1 MEMORY ADVANTAGE: best F_coded-F_bare = {best_adv:+.3f} at tau={best_tau}us "
          f">= 0.02 {'OK' if g1 else 'MISS'}")
    if g1:
        win = (f"THE THRESHOLD (bit-flip/T1) CROSSED — active correction makes the coded qubit remember "
               f"BETTER than bare by {best_adv:+.3f} at tau={best_tau}us: on this channel ibm_fez sits "
               f"ABOVE the pseudo-threshold, the code's machinery fixes more than it introduces")
    else:
        win = (f"BELOW THRESHOLD (honest) — the coded qubit never beats bare (best {best_adv:+.3f} at "
               f"tau={best_tau}us); the encode+readout overhead (tau=0 gap {fc0-fb0:+.3f}) exceeds the "
               f"protection. Quantifies how far ibm_fez sits from break-even on the bit-flip/T1 channel")
    print(f"VERDICT: {win}")
    json.dump({"job_id": man["job_id"], "taus_us": taus,
               "F_bare": {str(t): _bare_fid(raw[("bare", "1", t)], "1") for t in taus},
               "F_coded": {str(t): _coded_fid(raw[("coded", "1", t)], "1") for t in taus},
               "best_advantage": best_adv, "best_tau_us": best_tau, "crossover_tau_us": cross_tau,
               "tau0_overhead_gap": fc0 - fb0, "control_bare": ctrl_b, "control_coded": ctrl_c,
               "g1_above_threshold": bool(g1)},
              open(os.path.join(HERE, "..", "results", "exp239_the_threshold_decode.json"), "w"), indent=1)
    print("-> results/exp239_the_threshold_decode.json")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true"); ap.add_argument("--submit", action="store_true")
    ap.add_argument("--decode", action="store_true")
    ap.add_argument("--backend", default="ibm_fez"); ap.add_argument("--shots", type=int, default=8000)
    a = ap.parse_args()
    if a.selftest: selftest()
    elif a.submit: submit(a.backend, a.shots)
    elif a.decode: decode()
    else: ap.print_help()
