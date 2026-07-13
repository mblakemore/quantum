#!/usr/bin/env python3
"""run_exp125b_submit.py — Exp125b coherent-record erasure frontier (Whisper C4664).
Prereg: experiments/exp125b-coherent-record-erasure-frontier-preregistration.md (FROZEN).
Same-window co-measurement: fresh Bell pair 2-qubit tomography (9 bases) + 2q readout calibration
(4 states) on the F97/F104 engine qubits. Yields two-sided S(B|A) + record k_BT.
Usage: --scan (FREE) | --submit."""
import argparse
import json
import os
import sys

import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "experiments"))
from run_exp66_qpu_partb import _get_ibm_service  # noqa: E402

SHOTS = 8000
SEED = 4664
BASES = ["X", "Y", "Z"]
# FROZEN: F97 engine pair (3,4). Logical q0->phys 3 (A/system), q1->phys 4 (B/record).
# phys 4 IS F104's measured qubit -> ties S(B|A), k_BT and the F104 floor to the same qubit/region.
ENGINE_PAIR = [3, 4]


def rot(qc, q, basis):
    if basis == "X":
        qc.h(q)
    elif basis == "Y":
        qc.sdg(q)
        qc.h(q)
    # Z: identity


def tomo_circuit(ba, bb):
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)          # Bell (|00>+|11>)/sqrt2 ; q0=A(system), q1=B(record)
    rot(qc, 0, ba)
    rot(qc, 1, bb)
    qc.measure(0, 0)
    qc.measure(1, 1)
    return qc


def cal_circuit(sa, sb):
    qc = QuantumCircuit(2, 2)
    if sa:
        qc.x(0)
    if sb:
        qc.x(1)
    qc.measure(0, 0)
    qc.measure(1, 1)
    return qc


def build_all():
    pubs = []
    for ba in BASES:
        for bb in BASES:
            pubs.append((f"tomo_{ba}{bb}", "tomo", tomo_circuit(ba, bb)))
    for sa in (0, 1):
        for sb in (0, 1):
            pubs.append((f"cal_{sa}{sb}", "cal", cal_circuit(sa, sb)))
    return pubs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--backend", default="ibm_marrakesh")
    ap.add_argument("--tag", default="exp125b")
    args = ap.parse_args()

    svc = _get_ibm_service()
    backend = svc.backend(args.backend)
    print(f"Backend {backend.name}: pending={backend.status().pending_jobs}")
    pair = ENGINE_PAIR                          # FROZEN F97/F104 engine pair (3,4)
    gname = [n for n in backend.target.operation_names if n in ("cz", "ecr", "cx")][0]
    g = backend.target[gname]
    twoq_err = next((getattr(v, "error", None) for k, v in g.items()
                     if set(k) == set(pair)), None)
    print(f"PAIR (frozen engine pair 3,4 = F97): {pair} 2q_err={twoq_err}")
    a_max = {}
    for q in pair:
        inst = backend.target["measure"].get((q,))
        a_max[q] = float(getattr(inst, "error", float("nan"))) if inst else None

    tqcs, metas, ok = [], [], True
    for lab, arm, qc in build_all():
        tqc = transpile(qc, backend, initial_layout=pair[:2],
                        seed_transpiler=SEED, optimization_level=1)
        n2 = sum(1 for i in tqc.data if i.operation.num_qubits == 2
                 and i.operation.name != "barrier")
        nmeas = sum(1 for i in tqc.data if i.operation.name == "measure")
        want2 = 1 if arm == "tomo" else 0
        if n2 != want2 or nmeas != 2:
            ok = False
            print(f"  AUDIT MISS {lab}: 2q={n2} meas={nmeas} (want {want2}/2)")
        tqcs.append(tqc)
        metas.append({"label": lab, "arm": arm, "shots": SHOTS,
                      "twoq": n2, "depth": tqc.depth()})
    print(f"AUDIT {'PASS' if ok else 'FAIL'} ({len(tqcs)} pubs, "
          f"{sum(m['shots'] for m in metas)} shots)")
    if not ok:
        return 1

    rng = np.random.default_rng(SEED)
    order = list(rng.permutation(len(tqcs)))
    tqcs = [tqcs[i] for i in order]
    metas = [metas[i] for i in order]
    if not args.submit:
        print("--scan complete (FREE). No QPU spent.")
        return 0

    from qiskit_ibm_runtime import SamplerV2
    job = SamplerV2(mode=backend).run([(t, None, m["shots"]) for t, m in zip(tqcs, metas)])
    jid = job.job_id()
    manifest = {
        "experiment": "exp125b-coherent-record-erasure-frontier", "cycle": "C4664-whisper",
        "backend": args.backend, "tag": args.tag,
        "prereg": "experiments/exp125b-coherent-record-erasure-frontier-preregistration.md",
        "pair": list(pair[:2]), "a_max": a_max, "record_qubit_index": 1,
        "tax_coherent_E": 0.028, "tax_classical_E": 0.092,
        "grade": {"G_ent": "S(B|A)+5SE < 0", "G_frontier":
                  "bonus=|S(B|A)|*k_BT*ln2 vs tax_coh 0.028 / tax_cl 0.092"},
        "bound_graded": "conditional/coherent (companion to F104 classical)",
        "transpile_seed": SEED, "shuffle_seed": SEED, "boot_B": 400,
        "job_id": jid, "metas": metas,
    }
    outp = os.path.join(HERE, "..", "results", f"{args.tag}_jobids.json")
    json.dump(manifest, open(outp, "w"), indent=1, default=float)
    print(f"SUBMITTED job {jid}; manifest -> {outp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
