#!/usr/bin/env python3
"""GEAR 3 — THE SWITCH GEARBOX pointed at the chip's own gates (Whisper C5073, Creator ask
general#11491; gear survey general#11461).

WHAT THIS IS: the compiled quantum switch computes COMMUTE(U,V) coherently (C4999 scout,
Finding 1: <X_c> = +/-1.000 deterministic in sim; scope = device-characterized, the C4999
Finding-2 wall applies only to enforced-black-box CLAIMS, which this is not). Pointed at two
NATIVE CZs sharing a qubit: ideal CZs are diagonal -> commute exactly -> <X_c> = +1. GEAR 1
measured the error field's DIAGONAL part (riders — huge but commuting); the switch sees what
the rider survey cannot: a COHERENT NON-DIAGONAL error component breaks the commutation and
shows as an interference deficit beyond the instrument's own floor.

ARMS (all same compiled-switch structure: |+>_c ; c-controlled[U then V] ; anti-controlled
[V then U] ; H_c ; measure X_c — two controlled 2q-gate blocks per arm):
  floor:      U = V = CZ(a,b). [G,G] = 0 ALWAYS, coherent errors included -> any visibility
              loss here is pure instrument/compilation noise. THE calibration arm.
  science:    U = CZ(a,b), V = CZ(b,c) (shared qubit b). Ideal commute; deficit beyond floor
              = non-diagonal native-gate error, in the switch's own currency.
  polarity:   U = X(a), V = Z(a) (exact anticommute) -> <X_c> = -1 checks sign/wiring.
PRE-REGISTERED:
  P-G3: science visibility V_s = <X_c>_science, floor V_f = <X_c>_floor.
        GATE-COUNT NORMALIZATION (frozen pre-flight; the arms transpile to 45 vs 51 CZs and
        plain depolarizing on the extra 6 would FAKE a deficit - the dangerous direction):
        the comparison floor is V_f_norm = sign(V_f) * |V_f|^(n_sci/n_floor), the floor's own
        per-2q-gate attenuation scaled to science's transpiled 2q count (both counts read
        from the flown manifest).
        DIAGONAL-DOMINANT verdict if V_s >= V_f_norm - 3*se_diff;
        NON-DIAGONAL COMPONENT DETECTED if V_s < V_f_norm - 3*se_diff, size quoted as
        (V_f_norm - V_s) with se. Either outcome pays (clean = the field is diagonal, verified
        coherently; deficit = turbulence has a component GEAR 1 could not see).
  GATE: polarity arm must read <X_c> <= -0.5 (instrument wired right) AND V_f >= 0.3
        (instrument alive through compilation) else NO-TEST, gate named.
  SELFTEST (must pass pre-submit): statevector <X_c> = +1 (floor), +1 (science), -1 (polarity).
Fences: device-characterized instrument statement, one epoch, one qubit-chain; no query-
separation or black-box claim (C4999 Finding 2 wall respected); fence-not-physics.
Account IBMQ_ALT4; pending_jobs at submit. Flight needs fresh GO citing this digest.
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

BACKEND = "ibm_marrakesh"
SHOTS = 8000
OUT = os.path.join(HERE, "..", "results", "exp_gear3_switch_gearbox_c5073_manifest.json")
# logical qubits: 0 = control c, 1 = a, 2 = b, 3 = c-chain end
def U_gates(arm):
    """Returns (apply_U, apply_V) closures adding the controlled versions onto qc.
    Controlled-CZ = CCZ; controlled-X = CX; controlled-Z = CZ (control qubit 0)."""
    if arm == "floor":
        return (lambda qc: qc.ccz(0, 1, 2)), (lambda qc: qc.ccz(0, 1, 2))
    if arm == "science":
        return (lambda qc: qc.ccz(0, 1, 2)), (lambda qc: qc.ccz(0, 2, 3))
    if arm == "polarity":
        return (lambda qc: qc.cx(0, 1)), (lambda qc: qc.cz(0, 1))
    raise ValueError(arm)


def switch_circuit(arm):
    """Compiled switch: control selects order U∘V vs V∘U via controlled applications.
    c=1 branch: U then V ; c=0 branch: V then U (anti-control via X sandwiches)."""
    cU, cV = U_gates(arm)
    qc = QuantumCircuit(4, 1)
    qc.h(0)
    # target register in a fixed non-trivial product state so non-commutation shows:
    qc.h(1); qc.h(2); qc.h(3)
    # c=1: U;V
    cU(qc); cV(qc)
    # c=0: V;U  (anti-control)
    qc.x(0)
    cV(qc); cU(qc)
    qc.x(0)
    qc.h(0)
    qc.measure(0, 0)
    return qc


def selftest():
    from qiskit.quantum_info import Statevector
    exp = {"floor": +1.0, "science": +1.0, "polarity": -1.0}
    for arm, want in exp.items():
        qc = switch_circuit(arm).remove_final_measurements(inplace=False)
        sv = Statevector.from_instruction(qc)
        # <X_c> after H = <Z> on qubit 0 = P(c=0) - P(c=1)
        probs = sv.probabilities([0])
        xc = probs[0] - probs[1]
        print(f"  selftest {arm:9s}: <X_c> = {xc:+.4f} (want {want:+.1f})")
        assert abs(xc - want) < 1e-6, f"{arm} selftest failed"
    print("selftest PASS: floor/science commute (+1), polarity anticommutes (-1)")
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
    for arm in ("floor", "science", "polarity"):
        qc = switch_circuit(arm)
        tqc = transpile(qc, backend, optimization_level=1, seed_transpiler=3)
        pubs.append((tqc, None, SHOTS))
        meta.append({"block": arm, "shots": SHOTS, "depth": tqc.depth(),
                     "cz_count": sum(1 for i in tqc.data if i.operation.num_qubits == 2)})
        print(f"  [$0-validate] {arm}: depth {tqc.depth()}, 2q count {meta[-1]['cz_count']}")

    man = {"card": "exp_gear3_switch_gearbox", "cycle": "C5073", "substrate": "claude-fable-5",
           "backend": BACKEND, "cal_epoch": str(props.last_update_date), "shots": SHOTS,
           "account": "IBMQ_ALT4", "arms": ["floor", "science", "polarity"],
           "purpose": "GEAR 3 (Creator general#11491): compiled-switch COMMUTE pointed at native CZs - non-diagonal error detector, the component GEAR 1's riders cannot see",
           "prereg": "P-G3 + gates + selftest in docstring, committed pre-flight",
           "pubs_meta": meta}
    if a.submit:
        man["pending_jobs_at_submit"] = backend.status().pending_jobs
        job = SamplerV2(mode=backend).run(pubs)
        man["job_id"] = job.job_id()
        print(f"SUBMITTED {man['job_id']} to {BACKEND} (pending at submit: {man['pending_jobs_at_submit']})")
    else:
        print("[dry] not submitted (pass --submit to fly)")
    json.dump(man, open(OUT, "w"), indent=1)
    print(f"manifest -> {OUT}")


if __name__ == "__main__":
    main()
