#!/usr/bin/env python3
"""H15 R1 die probe — SUBMIT script (Whisper C5075). ALT4 (free, open-auth) /
ibm_kingston. Diagnostic flight: 96 known-state rows x 1 shot (no seal, no
claim; predictions + decision rule pre-registered in h15_r1_die_probe kit).

MODES:
  --sim : Aer gate — kit selftest must pass (ALT 32/32, sensor 32/32,
          never 0/8, always 8/8) before any submission path runs.
  --fly : run --sim gate, then transpile opt1 seed 5075 to the real backend,
          submit via SamplerV2, PRINT JOB ID IMMEDIATELY (announce-at-submit),
          save manifest. One submission is the intent.
Account routing via ibm_multi_account.service_for_submission("IBMQ_ALT4") —
the #151 instance gate auto-pins the single free plan=='open' instance and
fails CLOSED on ambiguity. Marrakesh comparison arm = the flown N1 flight
itself (n=316/arm), pre-stated; kingston is the measurement."""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

from h15_r1_die_probe_whisper_c5075 import build_probe, selftest, PROBE_SEED

ACCOUNT, BACKEND = "IBMQ_ALT4", "ibm_kingston"
OUT = os.path.join(HERE, "..", "results", "h15_r1_probe_kingston_manifest_c5075.json")


def gate_sim():
    ok, d = selftest()
    print(f"SIM GATE: ok={ok} {json.dumps(d)}")
    if not ok:
        sys.exit("SIM GATE FAILED — no submission.")


def fly():
    gate_sim()
    import ibm_multi_account as M
    from qiskit import transpile
    from qiskit_ibm_runtime import SamplerV2
    svc = M.service_for_submission(ACCOUNT)
    backend = svc.backend(BACKEND)
    circs = build_probe()
    tqcs = transpile(circs, backend, optimization_level=1, seed_transpiler=PROBE_SEED)
    tot2q = sum(t.count_ops().get("cz", 0) for t in tqcs)
    print(f"transpiled: {len(tqcs)} circuits, total 2q={tot2q}")
    snap = M.submit_snapshot(backend)   # queue depth AT submit, into the manifest (C5075 rule)
    print(f"queue snapshot: {snap}")
    job = SamplerV2(mode=backend).run([(t,) for t in tqcs], shots=1)
    jid = job.job_id()
    print(f"JOB ID (ANNOUNCED AT SUBMIT): {jid}")
    json.dump({"card": "h15_r1_probe_kingston", "cycle": "C5075",
               "job_id": jid, "backend": BACKEND, "account": ACCOUNT,
               "rows": 96, "shots_per_row": 1, "probe_seed": PROBE_SEED,
               "marrakesh_arm": "flown N1 flight da14kue3kjvs7386a2l0 (pre-stated)",
               "total_2q_transpiled": int(tot2q), "queue_at_submit": snap},
              open(OUT, "w"), indent=1)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sim", action="store_true")
    ap.add_argument("--fly", action="store_true")
    a = ap.parse_args()
    if a.fly:
        fly()
    else:
        gate_sim()
