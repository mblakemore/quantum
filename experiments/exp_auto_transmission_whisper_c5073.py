#!/usr/bin/env python3
"""THE AUTOMATIC TRANSMISSION — Gear 3 senses, Gear 4 shifts (Whisper C5073, Creator GO
general#11504 "go on building the automatic transmission").

ONE circuit that senses whether its own gears mesh and shifts itself accordingly:
  SENSOR (Gear 3): the compiled-switch COMMUTE block on the science pair (U=CZ(1,2),
    V=CZ(2,3), shared qubit 2) with the control measured MID-CIRCUIT -> herald bit c.
    GEAR 3 measured this exact sensor: science visibility +0.307 -> herald rate
    P(c=1) ~ (1-0.307)/2 ~ 0.35 expected (vs floor-class ~0.08).
  SHIFT (Gear 4): feedforward on c. If c=1 ("grind" heralded): apply the frozen recovery
    candidate R = Z(2) (Finding 04: Z-type coherent errors dominate this fabric) AND flip a
    WITNESS ancilla (q4) - the witness proves in-hardware that the shift path executed.
  TASK: X-basis parity of the 3-qubit target register (parity of X1 X2 X3 - sensitive to
    coherent Z-type errors; ideal value +1 for the prepared |+++> register when U,V mesh).

ARMS (8000 shots each): AUTO (sense+shift as above) · NEVER (sensor runs, herald recorded,
no shift - the c=1 stratum shows the uncorrected grind) · ALWAYS (R applied unconditionally).

PRE-REGISTERED:
  PRIMARY P-M (the MECHANISM - this is the claim): the machine shifts in-hardware:
    (a) witness/herald consistency in AUTO >= 0.99 (witness=1 exactly on c=1 shots);
    (b) herald rate in [0.15, 0.55] on all arms (the GEAR-3 deficit class reproduces;
        band wide because it is a fresh epoch - the sensor re-measures its own input).
  SECONDARY P-R (EXPLORATORY, R frozen, efficacy not promised): task parity on the c=1
    stratum, AUTO vs NEVER. R right -> AUTO improves at 3 sigma; R wrong -> AUTO ~ NEVER
    and the result reads "transmission demonstrated, first gear-ratio candidate misses" -
    the linkage is the deliverable, the correction is tuning.
  GATES: mid-circuit measurement + if_test must compile (else NO-TEST named); AUTO's c=0
    stratum parity must match NEVER's c=0 stratum within 3 sigma (the shift must not
    disturb the meshed path - a transmission that grinds in neutral fails its own point).
  SELFTEST (pre-submit, statevector/Aer): ideal science pair -> c=1 rate ~0 and witness
    never fires; FORCED-GRIND check (V replaced by X(2), exact anticommute) -> c=1 rate
    0.5, witness fires on exactly the c=1 shots, R path executes.
Fences: device-characterized, one epoch, one chain; no autonomy/agency language beyond the
mechanical analogy; efficacy of R explicitly exploratory. Account IBMQ_ALT4.
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

BACKEND = "ibm_marrakesh"
SHOTS = 8000
OUT = os.path.join(HERE, "..", "results", "exp_auto_transmission_c5073_manifest.json")
# q0=switch control, q1..q3=target register, q4=witness ancilla
# clbits: 0=herald c, 1..3=task register, 4=witness


def transmission_circuit(arm, forced_grind=False):
    qc = QuantumCircuit(5, 5)
    qc.h(0); qc.h(1); qc.h(2); qc.h(3)
    U = lambda: qc.ccz(0, 1, 2)
    V = (lambda: qc.cx(0, 2)) if forced_grind else (lambda: qc.ccz(0, 2, 3))
    U(); V()
    qc.x(0); V(); U(); qc.x(0)
    qc.h(0)
    qc.measure(0, 0)                      # HERALD (mid-circuit)
    if arm == "auto":
        with qc.if_test((qc.clbits[0], 1)):
            qc.z(2)                        # frozen recovery candidate R
            qc.x(4)                        # witness: the shift path executed in-hardware
    elif arm == "always":
        qc.z(2); qc.x(4)
    # task readout: X-basis parity of target register
    qc.h(1); qc.h(2); qc.h(3)
    qc.measure(1, 1); qc.measure(2, 2); qc.measure(3, 3)
    qc.measure(4, 4)
    return qc


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 20000
    # ideal science pair: no grind, witness silent
    c = sim.run(transmission_circuit("auto"), shots=shots).result().get_counts()
    herald = sum(n for s, n in c.items() if s.replace(" ", "")[-1] == "1") / shots
    wit_on_c0 = sum(n for s, n in c.items() if s.replace(" ", "")[-1] == "0"
                    and s.replace(" ", "")[-5] == "1")
    print(f"  selftest ideal: herald rate {herald:.4f} (want ~0), witness-on-meshed {wit_on_c0} (want 0)")
    assert herald < 0.01 and wit_on_c0 == 0
    # forced grind: exact anticommute -> herald 0.5, witness fires exactly on c=1
    c = sim.run(transmission_circuit("auto", forced_grind=True), shots=shots).result().get_counts()
    n1 = w1 = bad = 0
    for s, n in c.items():
        b = s.replace(" ", "")
        cbit, wbit = b[-1], b[-5]
        if cbit == "1":
            n1 += n
            if wbit == "1": w1 += n
            else: bad += n
        elif wbit == "1": bad += n
    print(f"  selftest forced-grind: herald {n1/shots:.3f} (want ~0.5), witness consistency {w1}/{n1}, violations {bad}")
    assert abs(n1/shots - 0.5) < 0.02 and bad == 0 and w1 == n1
    print("selftest PASS: senses nothing when meshed, shifts exactly when ground")
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
    for arm in ("auto", "never", "always"):
        qc = transmission_circuit(arm)
        tqc = transpile(qc, backend, optimization_level=1, seed_transpiler=4)
        pubs.append((tqc, None, SHOTS))
        meta.append({"block": arm, "shots": SHOTS, "depth": tqc.depth(),
                     "cz_count": sum(1 for i in tqc.data if i.operation.num_qubits == 2)})
        print(f"  [$0-validate] {arm}: depth {tqc.depth()}, 2q {meta[-1]['cz_count']}")
    man = {"card": "exp_auto_transmission", "cycle": "C5073", "substrate": "claude-fable-5",
           "backend": BACKEND, "cal_epoch": str(props.last_update_date), "shots": SHOTS,
           "account": "IBMQ_ALT4", "arms": ["auto", "never", "always"],
           "purpose": "The automatic transmission: Gear-3 sensor (mid-circuit COMMUTE herald) driving Gear-4 feedforward (shift + witness) in one circuit",
           "prereg": "P-M primary (mechanism: witness/herald consistency >=0.99, herald in class band, neutral-path non-disturbance), P-R secondary exploratory (R=Z(2) frozen), gates + selftest in docstring",
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
