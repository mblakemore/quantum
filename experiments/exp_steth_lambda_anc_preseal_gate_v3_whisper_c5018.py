#!/usr/bin/env python3
"""λ_anc PRE-SEAL GATE v3 (Whisper C5018) — Ember's locked v2 design + DD hardening.

GO on record: Creator general#3967 "Universal Translator, fly it, go". The main
distinguishing flight stays HELD until this gate passes: v2 measured λ_anc = 0.483 ±
0.063 (ancilla keeps half its signal) and u = 0.5625 ± 0.1033 vs floor 0.70 →
UNDERPOWERED. v2 flew WITHOUT dynamical decoupling; the mechanism (ancilla idle
decoherence) is exactly what ALAP + X-X DD addresses — the same machinery that
hardened every H10 flight since B1b, with the same DD-failure HOLD.

ZERO RE-TRANSCRIPTION: circuits, estimators, constants, grading, and manifest
conventions are IMPORTED from Ember's v2 module (c4227) — this wrapper changes exactly
two things: (1) transpiled circuits get ALAP + X-X DD (verified pulse insertion, HOLD
if none); (2) optimization_level 1→3. Everything else — shots, seeds, pubs, decode —
is v2's own code path, so v2-vs-v3 is a clean DD-intervention comparison.
"""
import importlib.util, json, os, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "..", "results")
_spec = importlib.util.spec_from_file_location(
    "v2", os.path.join(HERE, "exp_steth_lambda_anc_preseal_gate_v2_ember_c4227.py"))
v2 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(v2)

def submit_v3(k=2):
    sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
    from ibm_multi_account import service_for_submission
    from qiskit import transpile
    from qiskit_ibm_runtime import SamplerV2
    from qiskit.transpiler import PassManager
    from qiskit.transpiler.passes import ALAPScheduleAnalysis, PadDynamicalDecoupling
    from qiskit.circuit.library import XGate
    svc = service_for_submission("IBMQ_ALT2")
    u = svc.usage()
    print(f"POOL RE-READ (ALT2): {u['usage_remaining_seconds']}s of {u['usage_limit_seconds']}")
    best = None
    for b in svc.backends():
        st = b.status()
        if st.operational and b.configuration().n_qubits >= 4 * k:
            if best is None or st.pending_jobs < best[0]: best = (st.pending_jobs, b)
    backend = best[1]
    circs, shots, labels = v2.build_v2_circuits(k)
    tqc = transpile(circs, backend=backend, optimization_level=3, seed_transpiler=4227)
    durations = backend.target.durations()
    pm = PassManager([ALAPScheduleAnalysis(durations),
                      PadDynamicalDecoupling(durations, [XGate(), XGate()])])
    out = pm.run(tqc)
    xb = sum(sum(1 for i in t.data if i.operation.name == "x") for t in tqc)
    xa = sum(sum(1 for i in t.data if i.operation.name == "x") for t in out)
    if xa <= xb: sys.exit(f"DD HOLD: no pulses inserted (x {xb} -> {xa})")
    print(f"DD applied: X pulses {xb} -> {xa}")
    tqc = out
    job = SamplerV2(mode=backend).run([(t, None, s) for t, s in zip(tqc, shots)])
    man = {"experiment": "steth_lambda_anc_preseal_gate_v3_DD", "cycle": "C5018",
           "parent_design": "ember c4215 locked / c4227 v2 (imported, unmodified)",
           "delta": "ALAP + X-X DD (B1b machinery) + opt3; nothing else changed",
           "go": "Creator general#3967 'Universal Translator, fly it, go'",
           "account": "ALT2", "pool_remaining_at_submit_s": u["usage_remaining_seconds"],
           "backend": backend.name, "dd_x_pulses": [xb, xa], "k": k,
           "labels": labels, "shots": shots, "job_id": job.job_id(),
           "submit_iso": datetime.datetime.utcnow().isoformat() + "Z",
           "committer": "Whisper (DC15W)"}
    path = os.path.join(RESULTS, f"steth_lambda_anc_preseal_v3_manifest_{job.job_id()}.json")
    json.dump(man, open(path, "w"), indent=1)
    # v2.decode_v2 reads the newest v2-named manifest; write a v2-compatible copy so the
    # imported decode path (unchanged code) finds this job.
    compat = os.path.join(RESULTS, "steth_lambda_anc_preseal_v2_manifest_c4227.json")
    json.dump(man, open(compat, "w"), indent=1)
    print(f"SUBMITTED: {job.job_id()} -> {path}")

if __name__ == "__main__":
    if "--decode" in sys.argv:
        v2.decode_v2(sys.argv[sys.argv.index("--decode") + 1])
    else:
        submit_v3()
