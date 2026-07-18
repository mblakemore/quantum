#!/usr/bin/env python3
"""Exp154 — Quantum teleportation with verified fidelity on IBM hardware ("beam me up").
Creator directive C4844: fly the most frontier/star-trek self-verifying experiment; Elder's
intrinsic-falsifier bar. New quantum-network museum wing.

THE AHA. Destroy a qubit's state here, reconstruct it there — using a shared Bell pair and two
classical bits, with the original provably gone (no-cloning). We teleport each of the six
cardinal states (|0>,|1>,|+>,|->,|+i>,|-i>) across a real feed-forward circuit (mid-circuit
Bell measurement -> conditional X/Z correction on the receiver, fez dynamic circuits) and verify
the output fidelity against the KNOWN input. Intrinsic falsifier: we hold the inputs, so the
fidelity is directly checkable, no seals.

THE NUMBER ON A CAPABILITY. Average teleportation fidelity F over the six states vs the classical
measure-and-prepare bound of **2/3**: any strategy without shared entanglement cannot exceed 2/3.
Cross it = genuine quantum teleportation on silicon. Control: run the identical circuit with the
Bell pair NOT entangled -> F collapses to chance (falsifiability; the entanglement is load-bearing).

FENCE (headline): finite fidelity (SPAM + 1 CX + feed-forward latency); single-hop, post-corrected
in real time. A hardware demonstration of the teleportation primitive, not a deployed network.

Usage:
  python3 exp154_teleportation.py --selftest    # P3 truth-gate: noiseless F=1 all six, control<=2/3, test can fail
  python3 exp154_teleportation.py --submit [--backend ibm_fez --shots 4000]
  python3 exp154_teleportation.py --decode --manifest ../results/exp154_manifest.json
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

# six cardinal states: prep gates (from |0>) and verify gates (U_prep^dagger, so measuring 0 = fidelity)
STATES = {
    "Z+": {"prep": [],            "verify": []},
    "Z-": {"prep": ["x"],         "verify": ["x"]},
    "X+": {"prep": ["h"],         "verify": ["h"]},
    "X-": {"prep": ["x", "h"],    "verify": ["h", "x"]},
    "Y+": {"prep": ["h", "s"],    "verify": ["sdg", "h"]},
    "Y-": {"prep": ["h", "sdg"],  "verify": ["s", "h"]},
}
CLASSICAL_BOUND = 2.0 / 3.0


def _apply(qc, gates, q):
    for g in gates:
        getattr(qc, g)(q)


def teleport_circuit(prep, verify, entangled=True, correct=True):
    """q0 = source |psi>, q1+q2 = Bell pair; Bell-measure q0q1, feed-forward correct q2, verify q2.
    entangled=False -> no Bell resource (entanglement falsifier). correct=False -> skip the
    conditional X/Z (classical-feedforward falsifier, Elder C4844)."""
    qc = QuantumCircuit(3, 3)
    _apply(qc, prep, 0)                       # prepare |psi> on the source
    if entangled:
        qc.h(1); qc.cx(1, 2)                  # shared Bell pair (the resource)
    qc.barrier()
    qc.cx(0, 1); qc.h(0)                      # Bell measurement basis
    qc.measure(0, 0); qc.measure(1, 1)
    if correct:
        with qc.if_test((qc.clbits[1], 1)):   # X correction if m1=1
            qc.x(2)
        with qc.if_test((qc.clbits[0], 1)):   # Z correction if m0=1
            qc.z(2)
    qc.barrier()
    _apply(qc, verify, 2)                     # U_psi^dagger: measuring 0 == fidelity to |psi>
    qc.measure(2, 2)
    return qc


def _fidelity_from_counts(counts, shots):
    """F = P(q2 measured 0). Classical bits little-endian 'c2 c1 c0'; c2 is leftmost char."""
    good = 0
    for bit, c in counts.items():
        b = bit.replace(" ", "")
        # qiskit string is c2c1c0 (creg index 2 is most significant / leftmost)
        c2 = b[0]
        if c2 == "0":
            good += c
    return good / shots


def _run_sim(entangled):
    from qiskit_aer import AerSimulator
    sim = AerSimulator()
    fids = {}
    for name, s in STATES.items():
        qc = teleport_circuit(s["prep"], s["verify"], entangled)
        res = sim.run(qc, shots=4000).result()
        fids[name] = _fidelity_from_counts(res.get_counts(), 4000)
    return fids


def selftest():
    """P3 TRUTH-GATE (noiseless Aer). Entangled: F=1 for all six states (perfect teleportation).
    Control (Bell pair NOT entangled): F must NOT beat the 2/3 classical bound -> the entanglement
    is load-bearing (the test can fail). Falsifiability built in."""
    ent = _run_sim(True)
    ctl = _run_sim(False)
    print(f"Exp154 selftest (noiseless Aer) | classical bound = {CLASSICAL_BOUND:.3f}")
    print(f"{'state':>5} {'F(teleport)':>12} {'F(no-ent ctl)':>14}")
    for name in STATES:
        print(f"{name:>5} {ent[name]:>12.3f} {ctl[name]:>14.3f}")
    avg_e = np.mean(list(ent.values())); avg_c = np.mean(list(ctl.values()))
    print(f"\naverage: teleport {avg_e:.3f} vs classical bound {CLASSICAL_BOUND:.3f}")
    # Falsifiability lives on the SUPERPOSITION states: without the Bell pair the circuit cannot
    # carry X/Y states (F->1/2). The Z states are a degenerate case (any |0>-defaulting circuit
    # gets Z+ right), so the control AVERAGE is not the 2/3 bound — the bound is a theorem, a
    # constant we compare the quantum fidelity against.
    superpos = [ctl[k] for k in ("X+", "X-", "Y+", "Y-")]
    print(f"no-entanglement control on superposition states X±/Y±: {[f'{f:.2f}' for f in superpos]} "
          f"(→ chance; entanglement is load-bearing for superpositions)")
    assert all(f > 0.99 for f in ent.values()), "noiseless teleportation must give F=1 for every state"
    assert all(f < 0.6 for f in superpos), "no-entanglement control must fail (~1/2) on superposition states"
    print("SELFTEST PASS: perfect teleportation F=1 all six; without entanglement the superposition "
          "states collapse to chance (test can fail). Quantum F is compared to the 2/3 theorem, not the control avg.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    circuits, order = [], []
    for entangled in (True, False):
        for name, s in STATES.items():
            qc = teleport_circuit(s["prep"], s["verify"], entangled)
            circuits.append(transpile(qc, backend=backend, optimization_level=3))
            order.append((name, entangled))
    sampler = SamplerV2(mode=backend); job = sampler.run(circuits, shots=shots)
    manifest = {"exp": 154, "backend": backend_name, "shots": shots, "job_id": job.job_id(),
                "order": [[n, e] for (n, e) in order], "classical_bound": CLASSICAL_BOUND,
                "note": "teleportation fidelity vs 2/3 bound; entangled arm + no-entanglement control; "
                        "real feed-forward; self-verifying (known input states)"}
    out = os.path.join(HERE, "..", "results", "exp154_manifest.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(manifest, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits: 6 states x {{teleport,control}}, {shots} shots) -> {out}")


def decode(mp):
    from run_exp66_qpu_partb import _get_ibm_service
    svc = _get_ibm_service(); man = json.load(open(mp)); res = svc.job(man["job_id"]).result()
    shots = man["shots"]; ent, ctl = {}, {}
    for idx, (name, entangled) in enumerate(man["order"]):
        r = res[idx]; reg = list(r.data.keys())[0]
        F = _fidelity_from_counts(getattr(r.data, reg).get_counts(), shots)
        (ent if entangled else ctl)[name] = F
    print(f"Exp154 decode | job {man['job_id']} | backend {man['backend']} | bound {CLASSICAL_BOUND:.3f}")
    print(f"{'state':>5} {'F(teleport)':>12} {'F(no-ent ctl)':>14}")
    for name in STATES:
        print(f"{name:>5} {ent[name]:>12.3f} {ctl[name]:>14.3f}")
    avg_e = float(np.mean(list(ent.values()))); avg_c = float(np.mean(list(ctl.values())))
    beats = avg_e > CLASSICAL_BOUND
    print(f"\nAVERAGE TELEPORTATION FIDELITY: {avg_e:.3f}  vs classical bound {CLASSICAL_BOUND:.3f}")
    print(f"no-entanglement control: {avg_c:.3f}")
    print(f"VERDICT: {'BEATS the classical bound -> genuine quantum teleportation on silicon' if beats else 'below bound (noise-limited; honest null)'}"
          f" | margin {avg_e - CLASSICAL_BOUND:+.3f}")
    out = {"job_id": man["job_id"], "backend": man["backend"], "avg_fidelity": avg_e,
           "avg_control": avg_c, "classical_bound": CLASSICAL_BOUND, "beats_bound": beats,
           "per_state_teleport": ent, "per_state_control": ctl}
    fn = os.path.join(HERE, "..", "results", "exp154_decode.json")
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
    elif a.decode: decode(a.manifest or os.path.join(HERE, "..", "results", "exp154_manifest.json"))
    else: ap.print_help()
