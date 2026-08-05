#!/usr/bin/env python3
"""SPARSE-DD DENSITY SWEEP (Whisper C5018, Creator "try sparse DD").

WHY: the DD sweep (d9prvvfv9q4s73bhe7bg) found the incumbent DD NET HARMFUL — bare delay
u=0.7218 vs X-X u=0.6325, because the padding pass packs ~1546 pulses into a 1488 dt idle and
pulse error swamps the refocusing. It did NOT test the middle of that range. **The gate is
already cleared at 0.7218; this sweep is about MARGIN** — and margin matters concretely,
because measured job-to-job drift on an identical config is 0.048 while the margin above the
gate is only 0.022. A bad chip day drops the witness under the gate. Every point of margin is
robustness.

DESIGN: hand-placed CPMG spacing so the pulse count is EXACT and chosen, not whatever the
padding pass decides. For n pulses across an idle of D dt:
    delay(D/2n), [X, delay(D/n)] x (n-1), X, delay(D/2n)
LOG-SPACED ARMS: n = 0 (bare, the incumbent winner), 2, 8, 32, 128. Five points spanning
three decades between "nothing" and the ~1546 that lost.

PRE-REGISTERED DECISION RULE (frozen before submission):
  * Baseline is n=0 (bare delay), the current best.
  * An arm WINS iff pooled u exceeds n=0 by MORE than the pooled MDE (computed and emitted).
  * Report the full density curve regardless — the SHAPE is the deliverable even if no arm
    wins, because it locates the optimum for any future circuit with a long idle.
  * If the curve is monotone decreasing from n=0, the finding is "any DD hurts here" and the
    incumbent's failure was not about density at all.
  * If it peaks at an interior n, that n is the recommended default and the campaign's
    DD configuration changes to it.
  * No arm chosen by any criterion not written here. This is MEASUREMENT, not a decision
    function (no fireability attestation needed, Elder #5001).
"""
import json, os, sys, datetime
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
QROOT = os.path.join(HERE, ".."); RES = os.path.join(QROOT, "results")
sys.path.insert(0, os.path.join(QROOT, "scripts"))
from exp_armn_shallow_witness_whisper_c5018 import three_neighbour_plan
from exp_armn_flight_compile_whisper_c5018 import (_h, _cx, CENSUS_JOB, BACKEND, ACCOUNT, CAL_SHOTS)
from exp_crossblock_widesweep import build_twins, SEED, NPHYS
SHOTS = 8000
DENSITIES = [0, 2, 8, 32, 128]
CENSUS_DECODE = os.path.join(RES, f"armn_fez_census_decode_{CENSUS_JOB}.json")


def idle_with_dd(qc, q, D, n):
    """CPMG-spaced idle: exactly n X pulses across duration D on qubit q."""
    if n == 0:
        qc.delay(D, q, unit="dt"); return
    edge = max(1, D // (2 * n)); mid = max(1, D // n)
    qc.delay(edge, q, unit="dt")
    for i in range(n):
        qc.x(q)
        qc.delay(mid if i < n - 1 else edge, q, unit="dt")


def build(backend, q, pl, D, n):
    """SAME circuit as the DD sweep's arm, with n as the ONLY variable.

    Structure copied from build_witness (shallow script) rather than re-written, so the n=0
    arm is a genuine REPRODUCTION of the DD sweep's `none` arm — which is the built-in
    consistency check this sweep lacked the first time.
    """
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(NPHYS)
    a1, a2, s1 = pl["anc1"], pl["anc2"], pl["s1"]
    _h(qc, a1); _cx(qc, a1, q)
    qc.barrier(); idle_with_dd(qc, q, D, n); qc.barrier()
    _cx(qc, q, s1); _cx(qc, s1, q)
    qc.barrier()
    _h(qc, a2); _cx(qc, a2, q)
    qc.barrier(); idle_with_dd(qc, q, D, n); qc.barrier()
    _cx(qc, a1, a2); _h(qc, a1)
    _cx(qc, s1, q); _h(qc, s1)
    qc.measure_all()
    return qc


def main(submit=False):
    from ibm_multi_account import service_for_submission
    from qiskit_ibm_runtime import SamplerV2
    from qiskit import QuantumCircuit, transpile
    svc = service_for_submission(ACCOUNT)
    pool = svc.usage()["usage_remaining_seconds"]; print(f"POOL ({ACCOUNT}): {pool}s")
    backend = svc.backend(BACKEND)
    cal = str(backend.properties().last_update_date)
    twins, _ = build_twins(backend)
    from exp_armn_flight_compile_whisper_c5018 import pad_duration_dt
    D = pad_duration_dt(backend, twins)
    cen = json.load(open(CENSUS_DECODE)); drifters = set(cen["drifter_set"])
    cands = []
    for q in sorted(int(x) for x in cen["readout"]):
        pl = three_neighbour_plan(backend, q, drifters | {q})
        if pl: cands.append((q, pl, q in drifters))
    cands = [c for c in cands if c[2]][:2] + [c for c in cands if not c[2]][:2]
    print(f"[candidates] {[c[0] for c in cands]}  | idle D = {D} dt")
    pubs, meta = [], []
    for st, tag in ((0, "cal0"), (1, "cal1")):
        qc = QuantumCircuit(NPHYS)
        if st: qc.x(range(NPHYS))
        qc.measure_all()
        pubs.append((transpile(qc, backend, optimization_level=0), None, CAL_SHOTS))
        meta.append({"block": tag, "shots": CAL_SHOTS})
    pulses = {}
    for n in DENSITIES:
        for q, pl, isd in cands:
            from qiskit.transpiler import PassManager
            from qiskit.transpiler.passes import ALAPScheduleAnalysis
            base = transpile(build(backend, q, pl, D, n), backend,
                             optimization_level=1, seed_transpiler=SEED)   # == DD-sweep path
            t = PassManager([ALAPScheduleAnalysis(backend.target.durations())]).run(base)
            npx = sum(1 for i in t.data if i.operation.name == "x")
            pulses.setdefault(n, []).append(npx)
            pubs.append((t, None, SHOTS))
            meta.append({"block": f"n{n}_q{q}", "n": n, "q": q, "pulses": npx,
                         "role": "drifter" if isd else "quiet", "shots": SHOTS,
                         # INSTANCE-FIVE FIX: the decoder must read partner qubits from THIS
                         # artifact, never from another build's file.
                         "plan": pl, "scheduled_duration_dt": t.duration})
    print(f"[pulses] " + " | ".join(f"n={n}: {sorted(set(v))}" for n, v in pulses.items()))
    p_ref = 0.14
    se = 2*np.sqrt(p_ref*(1-p_ref)/SHOTS)
    mde1 = 2.8*np.sqrt(2)*se; mdep = mde1/np.sqrt(len(cands))
    tot = sum(m["shots"] for m in meta)
    print(f"[power] se(u)~{se:.4f} MDE single ~{mde1:.4f} pooled({len(cands)}) ~{mdep:.4f}")
    print(f"[cost] {len(pubs)} pubs / {tot} shots ~ {tot/100000*35:.0f} QPU-s (pool {pool}s)")
    man = {"card": "armn_sparse_dd_density", "cycle": "C5018", "substrate": "claude-fable-5",
           "backend": BACKEND, "account": ACCOUNT, "cal_epoch_at_build": cal, "idle_dt": D,
           "basis": "DD sweep d9prvvfv9q4s73bhe7bg: bare 0.7218 beat X-X 0.6325 at ~1546 pulses",
           "motivation": ("gate already cleared; this is MARGIN. Job-to-job drift on an "
                          "identical config measured 0.048 vs a 0.022 margin above the gate."),
           "densities": DENSITIES, "pulses_per_circuit": pulses, "spacing": "CPMG D/2n, D/n, D/2n",
           "candidates": [c[0] for c in cands],
           "power": {"se_u": round(se,5), "mde_single": round(mde1,4), "mde_pooled": round(mdep,4)},
           "reproduction_check": ("PRE-REGISTERED: the n=0 arm is the SAME construction and the "
                                 "SAME transpile path as the DD sweep's `none` arm, which measured "
                                 "u=0.7218. If n=0 here does NOT reproduce within the measured "
                                 "cross-job drift (0.048), this sweep is UNINTERPRETABLE again and "
                                 "the curve is not reported — the check fires before any density "
                                 "conclusion is drawn."),
           "prior_none_u": 0.7218, "cross_job_drift": 0.048,
           "decision_rule": ("baseline n=0; an arm WINS iff pooled u exceeds n=0 by more than the "
                             "pooled MDE. The density CURVE is the deliverable regardless: monotone "
                             "decreasing from 0 => any DD hurts here; interior peak => that n becomes "
                             "the campaign default. No arm chosen by unwritten criteria."),
           "cost": {"pubs": len(pubs), "shots": tot, "projected_qpu_s": round(tot/100000*35)},
           "pubs_meta": meta}
    if submit:
        job = SamplerV2(mode=backend).run(pubs)
        man["job_id"] = job.job_id(); man["submit_iso"] = datetime.datetime.now(datetime.UTC).isoformat()
        p = os.path.join(RES, f"armn_sparsedd_manifest_{job.job_id()}.json")
        json.dump(man, open(p,"w"), indent=1); print(f"SUBMITTED {job.job_id()} -> {p}")
    else:
        p = os.path.join(RES, "armn_sparsedd_build_c5018.json")
        json.dump(man, open(p,"w"), indent=1); print(f"[build] $0 -> {p}")


if __name__ == "__main__":
    main(submit="--submit" in sys.argv)
