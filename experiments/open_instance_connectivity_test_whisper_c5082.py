#!/usr/bin/env python3
"""Open-instance connectivity test (Whisper C5082, Creator request 2026-08-25).

Minimal "does the free open-instance actually submit and return?" test — a 2-qubit Bell state,
1000 shots, on the least-busy free backend. Routed through the #151 spend gate
(service_for_submission auto-pins the single FREE open-instance and REFUSES the paid ones), so it
cannot touch whisper-de / WhisperPaid. No claim, no prereg — a functionality check the Creator asked
for. Expected: counts concentrated on 00 and 11 (a Bell correlation), a few % leakage from readout.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../scripts")
import ibm_multi_account as m
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import SamplerV2

BACKEND = sys.argv[1] if len(sys.argv) > 1 else "ibm_fez"
SHOTS = 1000

svc = m.service_for_submission("IBMQ_TOKEN")   # #151 gate: free instance only, refuses paid
backend = svc.backend(BACKEND)
print(f"backend {backend.name}  qubits={backend.num_qubits}  pending={backend.status().pending_jobs}")

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
qc.measure_all()
isa = transpile(qc, backend, optimization_level=1)

sampler = SamplerV2(mode=backend)
job = sampler.run([isa], shots=SHOTS)
print(f"SUBMITTED job_id={job.job_id()} backend={backend.name} shots={SHOTS}")
sys.stdout.flush()

res = job.result()
counts = res[0].data.meas.get_counts()
total = sum(counts.values())
bell = (counts.get("00", 0) + counts.get("11", 0)) / total
print(f"RESULT counts={dict(sorted(counts.items()))}")
print(f"Bell fidelity proxy P(00)+P(11) = {bell:.3f}  (ideal 1.0; hardware readout eats a few %)")
print(f"job status = {job.status()}")
try:
    print(f"usage seconds = {job.usage()}")
except Exception as e:
    print(f"usage seconds = (unavailable: {e})")
