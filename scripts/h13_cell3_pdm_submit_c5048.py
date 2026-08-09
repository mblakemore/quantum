#!/usr/bin/env python3
"""H13 Cell 3 — Temporal Negativity Meter — SUBMIT (prereg FROZEN at e7ca10d).

Usage: QPU_ACCOUNT_VAR=IBMQ_ALT2 python3 scripts/h13_cell3_pdm_submit_c5048.py
Declared venue: ibm_fez. 27 circuits x 2000 shots. Estimated ~3-5 QPU-s.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# An inherited instance pin from another account would misroute this token's submission.
os.environ.pop("QISKIT_IBM_INSTANCE", None)

from ibm_multi_account import assert_explicit_account, service_for_submission

DECLARED_BACKEND = "ibm_fez"
SHOTS = 2000
EST_COST_S = 5.0
PREREG = "docs/h13-cell3-pdm-prereg-FROZEN-whisper-c5048.md"

acct = assert_explicit_account()
if acct != "IBMQ_ALT2":
    raise SystemExit(f"prereg declares account IBMQ_ALT2; got {acct} — REFUSING.")
svc = service_for_submission(acct)

# --- fit gate (re-read at submit; the triage number is not trusted) ---
u = svc.usage()
remaining = float(u["usage_limit_seconds"]) - float(u["usage_consumed_seconds"])
if u.get("usage_limit_reached") or remaining < EST_COST_S:
    raise SystemExit(f"FIT GATE REFUSES: remaining={remaining}s < est {EST_COST_S}s "
                     f"or limit_reached={u.get('usage_limit_reached')}")
print(f"[fit gate] {acct}: {remaining:.1f} QPU-s remaining >= est {EST_COST_S}s — OK")

backend = svc.backend(DECLARED_BACKEND)
if backend.name != DECLARED_BACKEND:
    raise SystemExit(f"backend assert failed: {backend.name} != {DECLARED_BACKEND}")

# --- live layout pick (never cached) ---
props = backend.properties()
nq = backend.num_qubits
ro = {}
for q in range(nq):
    try:
        ro[q] = props.readout_error(q)
    except Exception:
        pass
t_qubit = min(ro, key=ro.get)

best_pair, best_score = None, 1e9
for a, b in backend.coupling_map:
    try:
        e2 = props.gate_error("cz", (a, b))
    except Exception:
        continue
    if a in ro and b in ro:
        s = ro[a] + ro[b] + e2
        if s < best_score:
            best_pair, best_score = (a, b), s
print(f"[layout] temporal qubit {t_qubit} (ro {ro[t_qubit]:.4f}); "
      f"spatial pair {best_pair} (score {best_score:.4f})")

# --- circuits ---
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, transpile

def pre_rotate(qc, q, basis):
    if basis == "X":
        qc.h(q)
    elif basis == "Y":
        qc.sdg(q); qc.h(q)

def un_rotate(qc, q, basis):
    if basis == "X":
        qc.h(q)
    elif basis == "Y":
        qc.h(q); qc.s(q)

BASES = ["X", "Y", "Z"]
circs, labels = [], []
# temporal arm: 2 preps x 9 basis pairs
for prep in (0, 1):
    for bi in BASES:
        for bj in BASES:
            qr = QuantumRegister(1, "q"); cr = ClassicalRegister(2, "c")
            qc = QuantumCircuit(qr, cr, name=f"T_p{prep}_{bi}{bj}")
            if prep:
                qc.x(0)
            pre_rotate(qc, 0, bi)
            qc.measure(0, 0)
            un_rotate(qc, 0, bi)
            pre_rotate(qc, 0, bj)
            qc.measure(0, 1)
            circs.append(qc); labels.append({"arm": "temporal", "prep": prep, "i": bi, "j": bj})
# spatial control: Phi+ x 9 basis pairs
for bi in BASES:
    for bj in BASES:
        qr = QuantumRegister(2, "q"); cr = ClassicalRegister(2, "c")
        qc = QuantumCircuit(qr, cr, name=f"S_{bi}{bj}")
        qc.h(0); qc.cx(0, 1)
        pre_rotate(qc, 0, bi)
        qc.measure(0, 0)          # wing A, mid-circuit (mirrors temporal pipeline)
        pre_rotate(qc, 1, bj)
        qc.measure(1, 1)          # wing B, end
        circs.append(qc); labels.append({"arm": "spatial", "i": bi, "j": bj})

tcircs = []
for qc, lab in zip(circs, labels):
    layout = [t_qubit] if lab["arm"] == "temporal" else list(best_pair)
    tqc = transpile(qc, backend=backend, initial_layout=layout, optimization_level=1)
    tcircs.append(tqc)

# gate-feasibility lint: temporal arm must be zero-2q; spatial exactly 1
for tqc, lab in zip(tcircs, labels):
    n2q = sum(1 for inst in tqc.data if inst.operation.num_qubits == 2)
    if lab["arm"] == "temporal" and n2q != 0:
        raise SystemExit(f"LINT: temporal circuit {tqc.name} has {n2q} 2q gates — REFUSING.")
    if lab["arm"] == "spatial" and n2q > 2:
        raise SystemExit(f"LINT: spatial circuit {tqc.name} has {n2q} 2q gates — REFUSING.")
print(f"[lint] {len(tcircs)} circuits pass (temporal zero-2q, spatial <=2)")

from qiskit_ibm_runtime import SamplerV2 as Sampler
sampler = Sampler(mode=backend)
job = sampler.run(tcircs, shots=SHOTS)
jid = job.job_id()
manifest = {
    "cell": "H13-Cell3-PDM", "prereg": PREREG, "prereg_commit": "e7ca10d",
    "account": acct, "backend": DECLARED_BACKEND, "job_id": jid,
    "shots": SHOTS, "n_circuits": len(tcircs), "labels": labels,
    "layout": {"temporal_qubit": t_qubit, "spatial_pair": list(best_pair)},
    "fit_gate": {"remaining_before": remaining, "est_cost": EST_COST_S},
}
out = f"/droid/repos/quantum/results/h13_cell3_manifest_{jid}.json"
with open(out, "w") as f:
    json.dump(manifest, f, indent=2)
print(f"SUBMITTED job {jid} -> {out}")
