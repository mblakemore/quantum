#!/usr/bin/env python3
"""H15 R1-EXT — SUBMIT (Whisper C5075). ALT4 (free/open) / ibm_kingston.
Unsealed, claim-free diagnostic — Elder ruling general#12730 §2: same authorisation class as the
kingston probe, needs no seal-bound GO. n=128 per his §3 recommendation (CI-low 0.807 vs the
0.7392 floor), ~3.0 QPU-s to protect a 14.5-s SEALED flight whose GO is single-use.
Carries the C5075 queue snapshot at submit."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
from h15_r1_ext_probe_whisper_c5075 import build_ext, selftest, EXT_SEED

ACCOUNT, BACKEND = "IBMQ_ALT4", "ibm_kingston"
OUT = os.path.join(HERE, "..", "results", "h15_r1_ext_manifest_c5075.json")

def gate():
    ok, d = selftest()
    print(f"SIM GATE: ok={ok} {json.dumps(d)}")
    if not ok: sys.exit("SIM GATE FAILED — no submission.")

def fly():
    gate()
    import ibm_multi_account as M
    from qiskit import transpile
    from qiskit_ibm_runtime import SamplerV2
    svc = M.service_for_submission(ACCOUNT)
    backend = svc.backend(BACKEND)
    tqcs = transpile(build_ext(), backend, optimization_level=1, seed_transpiler=EXT_SEED)
    snap = M.submit_snapshot(backend)
    print(f"queue snapshot: {snap}")
    job = SamplerV2(mode=backend).run([(t,) for t in tqcs], shots=1)
    jid = job.job_id()
    print(f"JOB ID (ANNOUNCED AT SUBMIT): {jid}")
    json.dump({"card": "h15_r1_ext", "cycle": "C5075", "job_id": jid, "backend": BACKEND,
               "account": ACCOUNT, "rows": len(tqcs), "shots_per_row": 1, "ext_seed": EXT_SEED,
               "authorisation": "Elder ruling general#12730 - unsealed claim-free diagnostic, no seal-bound GO required",
               "queue_at_submit": snap}, open(OUT, "w"), indent=1)
    print(f"wrote {OUT}")

if __name__ == "__main__":
    fly() if "--fly" in sys.argv else gate()
