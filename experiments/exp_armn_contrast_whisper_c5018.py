#!/usr/bin/env python3
"""MEASURE THE CONTRAST (Whisper C5018, Creator "measure the contrast").

WHY THIS AND NOT THE EXPERIMENT: the verdict flight established that the arm-N design cannot
be powered from what is known. The theory constant NULL_ATTEN=0.74 is contradicted by data
(hardware implies 0.79-0.91), the attested 6.67 sd was withdrawn, and the replacement gap
estimate carries t=0.30 — so sizing anything on it is the pilot-sizing trap (m_Q ~ 1/gap^2,
error compounds quadratically). Ember's ruling: **the next thing to buy is a better estimate
of the CONTRAST, not a flight of the experiment.** This is that purchase.

IT IS A MEASUREMENT, NOT A TEST. No sealed labels, no blind trials, no verdict function, no
threshold. The deliverable is an ESTIMATE WITH A CONFIDENCE INTERVAL of

    CONTRAST = mean u(drifter blocks) - mean u(quiet blocks)

readout-corrected on an in-job cal, on the DD-off 9-CZ witness that clears the purity gate.

PRE-REGISTERED READOUT (frozen before submission — there is nothing to "win"):
  * Report the point estimate AND its CI. Always both; the CI is part of the result.
  * CI EXCLUDES ZERO  -> the contrast is measured; the fresh prereg sizes from its LOWER
                          confidence bound (never the point estimate).
  * CI INCLUDES ZERO  -> the contrast is BOUNDED, not measured. Report the upper bound and
                          state plainly that the design cannot be powered from what is known.
                          This is a legitimate and likely outcome, not a failure.
  * Either way NO m_Q is derived from a point estimate. That is the trap this flight exists
    to avoid repeating.

IN-JOB DRIFT RE-DETECTION: Z-basis rows at the census depths ride along, so "these are the
drifters" is a same-job fact rather than an inherited one (drifter sets are epoch-volatile,
and tonight already measured 0.048 of job-to-job drift on an identical config).
"""
import json, os, sys, datetime
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
QROOT = os.path.join(HERE, ".."); RES = os.path.join(QROOT, "results")
sys.path.insert(0, os.path.join(QROOT, "scripts"))
from exp_armn_shallow_witness_whisper_c5018 import three_neighbour_plan
from exp_armn_verdict_whisper_c5018 import witness
from exp_armn_flight_compile_whisper_c5018 import CENSUS_JOB, BACKEND, ACCOUNT, CAL_SHOTS
from exp_crossblock_widesweep import build_twins, SEED, NPHYS
SHOTS = 18000
CENSUS_DECODE = os.path.join(RES, f"armn_fez_census_decode_{CENSUS_JOB}.json")


def main(submit=False):
    from ibm_multi_account import service_for_submission
    from qiskit_ibm_runtime import SamplerV2
    from qiskit import QuantumCircuit, transpile
    from qiskit.transpiler import PassManager
    from qiskit.transpiler.passes import ALAPScheduleAnalysis
    svc = service_for_submission(ACCOUNT)
    pool = svc.usage()["usage_remaining_seconds"]; print(f"POOL ({ACCOUNT}): {pool}s")
    backend = svc.backend(BACKEND); cal = str(backend.properties().last_update_date)
    twins, register = build_twins(backend)
    from exp_armn_flight_compile_whisper_c5018 import pad_duration_dt
    D = pad_duration_dt(backend, twins)
    cen = json.load(open(CENSUS_DECODE)); drifters = set(cen["drifter_set"])
    cands = []
    for q in sorted(int(x) for x in cen["readout"]):
        pl = three_neighbour_plan(backend, q, drifters | {q})
        if pl: cands.append((q, pl, q in drifters))
    dr = [c for c in cands if c[2]]; qt = [c for c in cands if not c[2]]
    print(f"[blocks] drifters {[c[0] for c in dr]} | quiet {[c[0] for c in qt]}")
    sched = PassManager([ALAPScheduleAnalysis(backend.target.durations())])
    pubs, meta = [], []
    for tag, st in (("cal0", 0), ("cal1", 1)):
        qc = QuantumCircuit(NPHYS)
        if st: qc.x(range(NPHYS))
        qc.measure_all()
        pubs.append((transpile(qc, backend, optimization_level=0), None, CAL_SHOTS))
        meta.append({"block": tag, "shots": CAL_SHOTS})
    viol = []
    for q, pl, isd in dr + qt:
        for r in ("anc1", "s1", "anc2"):
            if pl[r] in drifters: viol.append((q, r, pl[r]))
        t = sched.run(transpile(witness(backend, q, pl, D, True), backend,
                                optimization_level=1, seed_transpiler=SEED))
        n2 = sum(1 for i in t.data if i.operation.num_qubits == 2)
        pubs.append((t, None, SHOTS))
        meta.append({"block": f"WIT_q{q}", "q": q, "plan": pl, "n2q": n2,
                     "role": "drifter" if isd else "quiet", "shots": SHOTS})
    # IN-JOB drift re-detection: Z rows at the census depths
    for Dz in (160, 280):
        qc = twins[Dz].copy(); qc.measure_all()
        t = transpile(qc, backend, optimization_level=0,
                      initial_layout=list(range(NPHYS)), seed_transpiler=SEED)
        pubs.append((t, None, 8000))
        meta.append({"block": f"ZDRIFT_d{Dz}", "depth": Dz, "shots": 8000})
    print(f"[precond 1] drifter-in-partner-role violations: {viol if viol else 'NONE'}")
    assert not viol
    n2s = sorted({m["n2q"] for m in meta if "n2q" in m})
    print(f"[precond 2] witness 2q counts: {n2s} (identical={len(n2s)==1})")
    p_ref = 0.14
    se = 2*np.sqrt(p_ref*(1-p_ref)/SHOTS)
    sed = se*np.sqrt(1/len(dr) + 1/len(qt))
    tot = sum(m["shots"] for m in meta)
    print(f"[power] se(u)/candidate {se:.5f} | se(CONTRAST) {sed:.5f} | 3-se bound +/-{3*sed:.4f}")
    print(f"[cost] {len(pubs)} pubs / {tot} shots ~ {tot/100000*35:.0f} QPU-s (pool {pool}s)")
    man = {"card": "armn_contrast_measurement", "cycle": "C5018", "substrate": "claude-fable-5",
           "backend": BACKEND, "account": ACCOUNT, "cal_epoch_at_build": cal, "delay_dt": D,
           "kind": "MEASUREMENT, not a test — estimand is mean u(drifter) - mean u(quiet)",
           "dd": "OFF (measured best)", "witness_2q": n2s,
           "blocks": {"drifter": [c[0] for c in dr], "quiet": [c[0] for c in qt]},
           "readout_rule": ("report point estimate AND CI always. CI excludes zero -> contrast "
                            "measured, size future work from its LOWER confidence bound. CI "
                            "includes zero -> contrast BOUNDED not measured; report the upper "
                            "bound and state the design cannot be powered from what is known. "
                            "NO m_Q derived from a point estimate, either way."),
           "prior_context": {"theory_NULL_ATTEN": 0.74, "pilot_gap_point_est": 0.0162,
                             "pilot_t": 0.30, "note": "pilot too noisy to size on — this flight replaces it"},
           "power": {"se_u_per_candidate": round(se, 5), "se_contrast": round(sed, 5),
                     "three_se_bound": round(3*sed, 4)},
           "in_job_drift_redetection": "ZDRIFT rows at census depths 160/280",
           "cost": {"pubs": len(pubs), "shots": tot}, "pubs_meta": meta}
    if submit:
        job = SamplerV2(mode=backend).run(pubs)
        man["job_id"] = job.job_id(); man["submit_iso"] = datetime.datetime.now(datetime.UTC).isoformat()
        p = os.path.join(RES, f"armn_contrast_manifest_{job.job_id()}.json")
        json.dump(man, open(p, "w"), indent=1); print(f"SUBMITTED {job.job_id()} -> {p}")
    else:
        p = os.path.join(RES, "armn_contrast_build_c5018.json")
        json.dump(man, open(p, "w"), indent=1); print(f"[build] $0 -> {p}")


if __name__ == "__main__":
    main(submit="--submit" in sys.argv)
