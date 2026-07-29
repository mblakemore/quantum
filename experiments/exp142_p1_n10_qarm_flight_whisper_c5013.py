#!/usr/bin/env python3
"""Exp142 P1 n=10 HYBRID RUNG — Q-ARM FLIGHT (Whisper C5013). Prereg §4.4, FROZEN @ 7bde06ba.

528 Bell samples (the gate-derived CONSERVATIVE-CORNER budget, results/exp142_p1_n10_qgate_
whisper_c5013.json) on the ALT open-instance. Seal: quantum@e145d02 (Ember), hash-only.

BLINDNESS (per §6 + the C5012 precedent): this script reads the sealed P from Ember's
off-git secret store AT RUNTIME to build the prep angles — Whisper the agent never prints,
logs, or inspects it. Before building anything, the script VERIFIES the secret against the
PUBLIC commitment (sha256(utf8(P+'|'+salt)) == committed hash) and aborts loudly on mismatch.
The manifest records only public objects (bases, layout, job ids, hashes) — delivery-integrity
of the scaffold (manifest P-independence, shots=1, fresh-per-row) was verified at C5003 and
the scaffold is imported UNCHANGED.

Order-of-operations at flight time (all in the git DAG, Elder ancestry-verified #2577):
freeze 7bde06b -> gate 8577c56 -> benchmark 9fa4eee -> seal e145d02 -> THIS FLIGHT.
"""
import hashlib, json, os, sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import exp142_flight_kit as K
from exp142_p1_flight_scaffold_whisper_c5003 import q_arm_rows

FREEZE = "7bde06ba3a1344cdeb95fe277b8fad91944cc43c"
N = 10
BUDGET = 528                        # frozen gate output: conservative corner, NOT K.BQ[10]
SECRET = os.path.expanduser("~/.ember-p1-secrets.json")
COMMITMENT = os.path.join(HERE, "exp142_commitments", "commitment_p1_allpaulis_n10.json")
ALT_CRN = ("crn:v1:bluemix:public:quantum-computing:us-east:"
           "a/1e9b7ff09baf49ef875846a9eb696283:44cfd6bd-c143-4ed4-8bc0-9d560992006f::")


def sealed_P_verified():
    """Load the sealed P and VERIFY it against the public commitment before use.
    Returns P without ever printing it. Aborts loudly on any mismatch."""
    sec = json.load(open(SECRET))[f"p1_allpaulis:{N}"]
    com = json.load(open(COMMITMENT))
    recomputed = hashlib.sha256((sec["P"] + "|" + sec["salt"]).encode()).hexdigest()
    if recomputed != com["hash_sha256"]:
        sys.exit("SEAL MISMATCH: secret store does not match the public commitment. ABORT.")
    if len(sec["P"]) != N or any(c not in "IXYZ" for c in sec["P"]) or set(sec["P"]) == {"I"}:
        sys.exit("SEAL MALFORMED: P fails the ensemble shape check. ABORT.")
    print(f"  seal verified: sha256(P|salt) == {com['hash_sha256'][:16]}… (public commitment)")
    return sec["P"]


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="ibm_fez")     # same device family as executed rungs
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    P = sealed_P_verified()

    token = None
    for line in open("/mnt/droid/repos/DC15W/.env"):
        if line.startswith("IBMQ_ALT"):
            token = line.strip().split("=", 1)[1]
    if not token:
        sys.exit("IBMQ_ALT token not found. ABORT.")

    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    from qiskit import transpile as _t
    svc = QiskitRuntimeService(channel="ibm_quantum_platform", token=token, instance=ALT_CRN)
    backend = svc.backend(args.backend)
    q_layout, conv_layout, bell_pairs = K.pick_layouts(backend, N)

    # --- build: Q arm ONLY, at the FROZEN budget, fresh OS-entropy prep draws ---
    rng = np.random.default_rng()                        # OS entropy — fresh per flight
    qqc, qparams = K.quantum_template(N)
    qrows = q_arm_rows(N, P, rng, BUDGET)
    tq = _t(qqc, backend, initial_layout=q_layout, optimization_level=1, seed_transpiler=142)
    tsent = _t(K.sentinel_circuit(), backend, optimization_level=1, seed_transpiler=142)

    pubs = [(tsent, None, K.SENT_SHOTS),
            (tq, K.named_rows(qparams, qrows), 1),
            (tsent, None, K.SENT_SHOTS)]
    print(f"  built: sentinel + quantum({BUDGET} rows, shots=1) + sentinel on {args.backend}, "
          f"q_layout={q_layout}")

    if args.dry_run:
        print("  DRY-RUN: no submission.")
        return 0

    sampler = SamplerV2(mode=backend)
    job = sampler.run(pubs)
    manifest = {
        "experiment": "exp142_p1_n10_qarm_flight", "cycle": "C5013", "n": N,
        "prereg_freeze_commit": FREEZE,
        "seal_commit": "e145d027fc727a53aa906dbf6c16cb1f24854bc3",
        "commit_hash": json.load(open(COMMITMENT))["hash_sha256"],
        "gate_result_commit": "8577c56", "benchmark_commit": "9fa4eee",
        "bell_samples": BUDGET,
        "budget_rule": "conservative corner of the frozen parametric box (gate VERDICT: FLY)",
        "backend": args.backend, "instance": "ALT open-instance",
        "q_layout": q_layout, "bell_pairs": bell_pairs,
        "job_id": job.job_id(), "shots_per_row": 1,
        "pubs": [{"kind": "sentinel_start", "shots": K.SENT_SHOTS},
                 {"kind": "quantum", "rows": BUDGET, "shots": 1},
                 {"kind": "sentinel_end", "shots": K.SENT_SHOTS}],
        "committer": "Whisper (DC15W) — P read at runtime for prep only, verified vs public "
                     "commitment, never printed/logged",
    }
    outp = os.path.join(HERE, "..", "results", "exp142_p1_n10_qarm_flight_manifest.json")
    json.dump(manifest, open(outp, "w"), indent=1)
    print(f"  SUBMITTED: job {job.job_id()} -> {outp}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
