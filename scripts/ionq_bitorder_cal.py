#!/usr/bin/env python3
"""Deterministic bit-order calibration for the IonQ native/verbatim path — resolves Exp211b.

Prepares a KNOWN asymmetric state: X on q0 (the control) only -> control=1, target=0.
In qiskit convention (clbit1 clbit0), this is the bitstring '01'. Independent ground truth:
  - IonQ native returns '01' -> convention PRESERVED. The Exp211b null failure is REAL and the
    Exp211 witness is SUSPECT (it may have read the wrong qubit).
  - IonQ native returns '10' -> get_counts flips bits (endianness) for verbatim circuits. The
    witness read the control correctly under the reversed convention; Exp211 RESTORED, null closes.
This is a calibration (a known input), NOT a re-read of the failed data — no band-shopping.
  python3 ionq_bitorder_cal.py            # FREE local-sim sanity (expect '01')
  python3 ionq_bitorder_cal.py --submit   # ~$4.30 on IonQ Forte-1 (50 shots)
"""
import sys, os, json, argparse
HERE = os.path.dirname(os.path.abspath(__file__)); QROOT = os.path.join(HERE, "..")
for p in ("experiments", "scripts", "tools"):
    sys.path.insert(0, os.path.join(QROOT, p))
from qiskit import QuantumCircuit
from braket_switch_causal import get_backend


def cal_circuit():
    # deterministic |q0=1, q1=0>, with BOTH qubits carrying gates so native compilation cannot
    # drop the idle one (the v1 failure: idle q1 was dropped -> 1-bit result).
    qc = QuantumCircuit(2, 2)
    qc.x(0); qc.x(1); qc.cx(0, 1)   # q0=1 ; q1 = 1 XOR 1 = 0
    qc.measure(0, 0); qc.measure(1, 1)
    return qc


def cal_circuit_gatefree():
    # C4943 diagnostic: SAME known asymmetric outcome as the CX cal ('01' in qiskit tc order),
    # but ZERO entangling gates — probes the ENTANGLER-FREE compilation class, the class the
    # Exp211b null lived in. (The CX cal only certified the entangled class.) Both qubits carry
    # 1q gates (x·x = I on q1) so neither is idle-droppable (the v1 failure).
    #   '01' -> gate-free class ALSO preserved: 211b permutation hypothesis REFUTED, anomaly open.
    #   '10' -> gate-free class SWAPPED: 211b NULL-FAIL fully explained as server-side
    #           bit-permutation bookkeeping, not physics.
    qc = QuantumCircuit(2, 2)
    qc.x(0)
    qc.x(1); qc.x(1)
    qc.measure(0, 0); qc.measure(1, 1)
    return qc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--gate-free", action="store_true",
                    help="entangler-free variant (C4943): probes the 211b null's compilation class")
    ap.add_argument("--shots", type=int, default=50)
    args = ap.parse_args()
    qc = cal_circuit_gatefree() if args.gate_free else cal_circuit()
    which = "ionq" if args.submit else "local"
    bk = get_backend(which)
    print(f"backend {bk.name} ({'QPU — SPEND' if args.submit else 'LOCAL — FREE'})")
    if args.submit:
        print(f"COST: 1 task x $0.30 + {args.shots} shots x $0.08 = ${0.30 + args.shots*0.08:.2f}")
        job = bk.run([qc], shots=args.shots, native=True)
        man = {"job_id": str(job.job_id())}
        stem = "braket_ionq_bitorder_cal_gatefree" if args.gate_free else "braket_ionq_bitorder_cal"
        json.dump(man, open(os.path.join(QROOT, "results", f"{stem}_manifest.json"), "w"))
        print("handle persisted:", man["job_id"])
        counts = job.result().get_counts()
    else:
        stem = "braket_ionq_bitorder_cal_gatefree" if args.gate_free else "braket_ionq_bitorder_cal"
        counts = bk.run([qc], shots=args.shots).result().get_counts()
    top = max(counts, key=counts.get)
    print("counts:", counts)
    print("ideal qiskit (control q0=1, target q1=0) = '01'")
    print(f"top bitstring: {top}")
    if args.gate_free:
        if top == "01":
            verdict = "GATEFREE-PRESERVED -> 211b permutation hypothesis REFUTED; anomaly unexplained"
        elif top == "10":
            verdict = ("GATEFREE-SWAPPED -> 211b NULL-FAIL explained: server-side bit permutation "
                       "on entangler-free programs (bookkeeping, not physics)")
        else:
            verdict = f"UNEXPECTED ({top})"
    elif top == "01":
        verdict = "CONVENTION-PRESERVED -> Exp211b null-fail is REAL, Exp211 witness SUSPECT"
    elif top == "10":
        verdict = "CONVENTION-REVERSED (endianness) -> Exp211 witness RESTORED, null closes under correction"
    else:
        verdict = f"UNEXPECTED ({top})"
    print("VERDICT:", verdict)
    json.dump({"counts": counts, "top": top, "verdict": verdict},
              open(os.path.join(QROOT, "results", f"{stem}.json"), "w"), default=float)
    return 0


if __name__ == "__main__":
    sys.exit(main())
