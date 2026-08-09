#!/usr/bin/env python3
"""H13 Cell 5 — Hardy's Paradox — SUBMIT (prereg FROZEN at e7ca10d).

Usage: QPU_ACCOUNT_VAR=IBMQ_ALT python3 scripts/h13_cell5_hardy_submit_c5048.py
Declared venue: ibm_fez. 8 circuits (4 Hardy x 8000 + 4 null x 4000). Estimated ~2-3 QPU-s.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.pop("QISKIT_IBM_INSTANCE", None)

from ibm_multi_account import assert_explicit_account, service_for_submission, _load_env_files

_load_env_files()  # tokens live in .env; the assert checks os.environ before the guard would load them

DECLARED_BACKEND = "ibm_fez"
SHOTS_HARDY, SHOTS_NULL = 8000, 4000
EST_COST_S = 3.0
PREREG = "docs/h13-cell5-hardy-prereg-FROZEN-whisper-c5048.md"

STATE = [-0.204057, -0.615875, 0.412407, -0.639515]
TH = {"A1": 1.210571, "A2": 6.158402, "B1": 4.198403, "B2": 5.533757}
SETTINGS = [("A1", "B1"), ("A2", "B1"), ("A1", "B2"), ("A2", "B2")]

acct = assert_explicit_account()
if acct != "IBMQ_ALT":
    raise SystemExit(f"prereg declares account IBMQ_ALT; got {acct} — REFUSING.")
svc = service_for_submission(acct)

u = svc.usage()
remaining = float(u["usage_limit_seconds"]) - float(u["usage_consumed_seconds"])
if u.get("usage_limit_reached") or remaining < EST_COST_S:
    raise SystemExit(f"FIT GATE REFUSES: remaining={remaining}s, "
                     f"limit_reached={u.get('usage_limit_reached')}")
print(f"[fit gate] {acct}: {remaining:.1f} QPU-s remaining >= est {EST_COST_S}s — OK")

backend = svc.backend(DECLARED_BACKEND)
if backend.name != DECLARED_BACKEND:
    raise SystemExit("backend assert failed")

props = backend.properties()
ro = {}
for q in range(backend.num_qubits):
    try:
        ro[q] = props.readout_error(q)
    except Exception:
        pass
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
print(f"[layout] pair {best_pair} (score {best_score:.4f})")

import numpy as np
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, transpile
from qiskit.circuit.library import StatePreparation

circs, labels, pubs_shots = [], [], []
for arm, shots in (("hardy", SHOTS_HARDY), ("null", SHOTS_NULL)):
    for sa, sb in SETTINGS:
        qr = QuantumRegister(2, "q"); cr = ClassicalRegister(2, "c")
        qc = QuantumCircuit(qr, cr, name=f"{arm}_{sa}{sb}")
        if arm == "hardy":
            vec = np.array(STATE, dtype=float)
            qc.append(StatePreparation(vec / np.linalg.norm(vec)), [0, 1])
        # measurement setting: Ry(-theta) then Z (freeze-numeric convention).
        # Bit order: freeze indexes amplitudes as (a b) with A the MSB; qiskit's
        # StatePreparation on [0,1] makes q1 the MSB — so A lives on q1, B on q0.
        qc.ry(-TH[sa], 1)
        qc.ry(-TH[sb], 0)
        qc.measure(1, 1)   # c1 = a
        qc.measure(0, 0)   # c0 = b
        circs.append(qc); labels.append({"arm": arm, "A": sa, "B": sb})
        pubs_shots.append(shots)

tcircs = [transpile(qc, backend=backend, initial_layout=list(best_pair),
                    optimization_level=1) for qc in circs]

for tqc, lab in zip(tcircs, labels):
    n2q = sum(1 for inst in tqc.data if inst.operation.num_qubits == 2)
    if lab["arm"] == "hardy" and n2q > 3:
        raise SystemExit(f"LINT: {tqc.name} has {n2q} 2q gates > 3 — REFUSING.")
    if lab["arm"] == "null" and n2q != 0:
        raise SystemExit(f"LINT: null {tqc.name} has {n2q} 2q gates — REFUSING.")
print("[lint] pass")

from qiskit_ibm_runtime import SamplerV2 as Sampler
sampler = Sampler(mode=backend)
job = sampler.run([(tqc, None, s) for tqc, s in zip(tcircs, pubs_shots)])
jid = job.job_id()
manifest = {
    "cell": "H13-Cell5-Hardy", "prereg": PREREG, "prereg_commit": "e7ca10d",
    "account": acct, "backend": DECLARED_BACKEND, "job_id": jid,
    "labels": labels, "shots": pubs_shots, "layout": {"pair": list(best_pair)},
    "state": STATE, "thetas": TH,
    "fit_gate": {"remaining_before": remaining, "est_cost": EST_COST_S},
}
out = f"/droid/repos/quantum/results/h13_cell5_manifest_{jid}.json"
with open(out, "w") as f:
    json.dump(manifest, f, indent=2)
print(f"SUBMITTED job {jid} -> {out}")
