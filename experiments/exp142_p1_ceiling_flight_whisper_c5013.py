#!/usr/bin/env python3
"""CEILING HUNT — per-rung Q-arm flight (Whisper C5013). FROZEN prereg @ 2adf197f.

Generalization of the verified n=10 flight (exp142_p1_n10_qarm_flight_whisper_c5013.py,
job d9l38b8i, graded CORRECT) to arbitrary rung n: same seal-verify-before-build, same
runtime-only P handling, same sentinel structure. Budget comes from the rung's committed
GATE RESULT — never typed by hand.

Usage: python3 exp142_p1_ceiling_flight_whisper_c5013.py --n 12 [--backend ibm_fez] [--dry-run]
"""
import argparse, hashlib, json, os, sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import exp142_flight_kit as K
from exp142_p1_flight_scaffold_whisper_c5003 import q_arm_rows

FREEZE = "2adf197ff7e472683e7aefd60ea46b307fa1a4e4"
SECRET = os.path.expanduser("~/.ember-p1-secrets.json")
ALT_CRN = ("crn:v1:bluemix:public:quantum-computing:us-east:"
           "a/1e9b7ff09baf49ef875846a9eb696283:44cfd6bd-c143-4ed4-8bc0-9d560992006f::")


def sealed_P_verified(n):
    sec = json.load(open(SECRET))[f"p1_allpaulis:{n}"]
    com = json.load(open(os.path.join(HERE, "exp142_commitments",
                                      f"commitment_p1_allpaulis_n{n}.json")))
    salt = sec.get("salt_hex", sec.get("salt"))
    if hashlib.sha256((sec["P"] + "|" + salt).encode()).hexdigest() != com["hash_sha256"]:
        sys.exit("SEAL MISMATCH vs public commitment. ABORT.")
    if len(sec["P"]) != n or any(c not in "IXYZ" for c in sec["P"]) or set(sec["P"]) == {"I"}:
        sys.exit("SEAL MALFORMED. ABORT.")
    print(f"  seal verified: sha256(P|salt) == {com['hash_sha256'][:16]}…")
    return sec["P"], com["hash_sha256"]


def gate_budget(n):
    g = json.load(open(os.path.join(HERE, "..", "results", f"exp142_p1_ceiling_gate_n{n}.json")))
    if g["VERDICT"] != "FLY":
        sys.exit(f"GATE VERDICT for n={n} is {g['VERDICT']!r} — no flight. ABORT.")
    if g["freeze_commit"] != FREEZE:
        sys.exit("GATE artifact freeze hash mismatch. ABORT.")
    return int(g["FLIGHT_BUDGET_bell_samples"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--backend", default="ibm_fez")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    n = a.n
    budget = gate_budget(n)
    P, seal_hash = sealed_P_verified(n)

    token = None
    for line in open("/mnt/droid/repos/DC15W/.env"):
        if line.startswith("IBMQ_ALT"):
            token = line.strip().split("=", 1)[1]
    if not token:
        sys.exit("IBMQ_ALT token not found. ABORT.")

    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    from qiskit import transpile as _t
    svc = QiskitRuntimeService(channel="ibm_quantum_platform", token=token, instance=ALT_CRN)
    backend = svc.backend(a.backend)
    q_layout, _conv, bell_pairs = K.pick_layouts(backend, n)

    rng = np.random.default_rng()
    qqc, qparams = K.quantum_template(n)
    qrows = q_arm_rows(n, P, rng, budget)
    tq = _t(qqc, backend, initial_layout=q_layout, optimization_level=1, seed_transpiler=142)
    tsent = _t(K.sentinel_circuit(), backend, optimization_level=1, seed_transpiler=142)
    pubs = [(tsent, None, K.SENT_SHOTS),
            (tq, K.named_rows(qparams, qrows), 1),
            (tsent, None, K.SENT_SHOTS)]
    print(f"  built: sentinel + quantum({budget} rows, shots=1) + sentinel on {a.backend}, "
          f"{2*n} qubits")
    if a.dry_run:
        print("  DRY-RUN: no submission.")
        return 0

    job = SamplerV2(mode=backend).run(pubs)
    manifest = {"experiment": f"exp142_p1_ceiling_rung_n{n}", "cycle": "C5013",
                "prereg_freeze_commit": FREEZE, "commit_hash": seal_hash,
                "gate_artifact": f"results/exp142_p1_ceiling_gate_n{n}.json",
                "bell_samples": budget, "backend": a.backend, "instance": "ALT open-instance",
                "q_layout": q_layout, "bell_pairs": bell_pairs, "job_id": job.job_id(),
                "shots_per_row": 1,
                "committer": "Whisper (DC15W) — P runtime-only, verified vs public commitment"}
    outp = os.path.join(HERE, "..", "results", f"exp142_p1_ceiling_flight_n{n}_manifest.json")
    json.dump(manifest, open(outp, "w"), indent=1)
    print(f"  SUBMITTED: job {job.job_id()} -> {outp}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
