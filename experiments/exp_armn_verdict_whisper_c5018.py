#!/usr/bin/env python3
"""ARM-N VERDICT FLIGHT (Whisper C5018, Creator "fly the verdict function").

THE THING THE AFTERNOON COULD NOT DO. The frozen arm-N rule was "ALT iff ZERO odd parities
over 24 x k pair-readings" — with a hardware odd-rate of 0.58-0.75 that fires with probability
~1e-17 for EITHER block: a constant function, a NON-TEST. This flight rebuilds the verdict so
it can fire, under every condition the court imposed.

WHAT CHANGED, each traceable to a measurement made today:
  * DD OFF. Bare delay. (DD sweep + density sweep: no pulse density beats bare; the incumbent
    X-X was COSTING 0.089 of purity.)
  * PURITY REFERENCE CO-BATCHED per candidate — a channel-free witness pub. It serves TWO
    roles: the in-job u >= 0.7 gate (job-to-job drift 0.048 EXCEEDS the 0.020 margin, so a
    purity certified elsewhere does not transfer), and the calibration input to tau.
  * TAU DERIVED FROM CALIBRATION + THEORY, never from witness outcomes (Elder's binding
    condition; threshold-after-data is the forbidden move). The FORMULA is frozen here:
        p_ALT  = (1 - u_app) / 2                      u_app = in-job purity reference
        p_NULL = (1 - u_app * NULL_ATTEN) / 2         NULL_ATTEN = 0.74, THEORY constant from
                                                      the C4998 G3 sims (matched-stochastic
                                                      Choi purity), frozen before this flight
        tau    = the sd-weighted midpoint of the two binomial means
    The only free input is u_app, which comes from a calibration pub, not from ALT/NULL data.

FIREABILITY ATTESTATION (Elder's three numbers, computed pre-flight at u_app = 0.7202):
    k=2 m_Q=120: P(fire|ALT) 0.979  P(fire|NULL) 0.039  separation 3.75 sd  range 22.5 counts
    k=3 m_Q= 90: P(fire|ALT) 0.980  P(fire|NULL) 0.026  separation 3.98 sd  range 25.3 counts
  BOTH branches fire with probability > 0 at every rung. Recomputed at decode from the
  ACTUAL in-job u_app and emitted with the verdict.

PRECONDITIONS carried unchanged: partner-role exclusion (derived from the census artifact),
per-block duration match, pairing reproduction from the frozen rule + delivered cal, and
Ember's both-ends interval check. Builder EMITS every field the decode needs; the decoder
REFUSES rather than borrowing from a sibling artifact.
"""
import json, os, sys, datetime
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
QROOT = os.path.join(HERE, ".."); RES = os.path.join(QROOT, "results")
sys.path.insert(0, os.path.join(QROOT, "scripts"))
from exp_armn_shallow_witness_whisper_c5018 import three_neighbour_plan
from exp_armn_flight_compile_whisper_c5018 import _h, _cx, CENSUS_JOB, BACKEND, ACCOUNT, CAL_SHOTS
from exp_armn_refly_whisper_c5018 import frozen_pairing, SELECT_BAR
from exp_crossblock_widesweep import build_twins, SEED, NPHYS

NULL_ATTEN = 0.74          # THEORY constant (C4998 G3): matched-stochastic Choi purity. FROZEN.
M, MQ = 40, {2: 120, 3: 90}
WITNESS_SHOTS = 4800       # >= M * max(MQ)
REF_SHOTS = 4000
U_GATE = 0.700
CENSUS_DECODE = os.path.join(RES, f"armn_fez_census_decode_{CENSUS_JOB}.json")


def tau_from_calibration(u_app, k, m_q):
    """FROZEN FORMULA. Only free input is u_app (a calibration pub), never witness data."""
    N = m_q * k
    pA = (1 - u_app) / 2
    pN = (1 - u_app * NULL_ATTEN) / 2
    mA, mN = N * pA, N * pN
    sA, sN = np.sqrt(N * pA * (1 - pA)), np.sqrt(N * pN * (1 - pN))
    tau = int(round((mA * sN + mN * sA) / (sA + sN)))
    from math import erf
    PfA = 0.5 * (1 + erf((tau + 0.5 - mA) / (sA * np.sqrt(2))))
    PfN = 0.5 * (1 + erf((tau + 0.5 - mN) / (sN * np.sqrt(2))))
    sep = (mN - mA) / np.sqrt((sA ** 2 + sN ** 2) / 2)
    return {"tau": tau, "N": N, "p_ALT": round(pA, 4), "p_NULL": round(pN, 4),
            "P_fire_given_ALT": round(PfA, 4), "P_fire_given_NULL": round(PfN, 4),
            "separation_sd": round(sep, 3), "dynamic_range_counts": round(mN - mA, 1)}


def witness(backend, q, pl, D, with_channel):
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(NPHYS)
    a1, a2, s1 = pl["anc1"], pl["anc2"], pl["s1"]
    _h(qc, a1); _cx(qc, a1, q); qc.barrier()
    if with_channel: qc.delay(D, q, unit="dt")          # DD OFF — bare delay (measured best)
    qc.barrier(); _cx(qc, q, s1); _cx(qc, s1, q); qc.barrier()
    _h(qc, a2); _cx(qc, a2, q); qc.barrier()
    if with_channel: qc.delay(D, q, unit="dt")
    qc.barrier(); _cx(qc, a1, a2); _h(qc, a1); _cx(qc, s1, q); _h(qc, s1)
    qc.measure_all(); return qc


def main(submit=False):
    from ibm_multi_account import service_for_submission
    from qiskit_ibm_runtime import SamplerV2
    from qiskit import QuantumCircuit, transpile
    from qiskit.transpiler import PassManager
    from qiskit.transpiler.passes import ALAPScheduleAnalysis
    svc = service_for_submission(ACCOUNT)
    pool = svc.usage()["usage_remaining_seconds"]; print(f"POOL ({ACCOUNT}): {pool}s")
    backend = svc.backend(BACKEND); cal = str(backend.properties().last_update_date)
    twins, _ = build_twins(backend)
    from exp_armn_flight_compile_whisper_c5018 import pad_duration_dt
    D = pad_duration_dt(backend, twins)
    cen = json.load(open(CENSUS_DECODE)); drifters = set(cen["drifter_set"])
    cands = []
    for q in sorted(int(x) for x in cen["readout"]):
        pl = three_neighbour_plan(backend, q, drifters | {q})
        if pl: cands.append((q, pl, q in drifters))
    dr = [c for c in cands if c[2]][:3]; nu = [c for c in cands if not c[2]][:3]
    print(f"[candidates] drifters {[c[0] for c in dr]} | quiet {[c[0] for c in nu]}")
    pubs, meta = [], []
    for tag, st in (("cal0_start", 0), ("cal1_start", 1)):
        qc = QuantumCircuit(NPHYS)
        if st: qc.x(range(NPHYS))
        qc.measure_all()
        pubs.append((transpile(qc, backend, optimization_level=0), None, CAL_SHOTS))
        meta.append({"block": tag, "shots": CAL_SHOTS})
    sched = PassManager([ALAPScheduleAnalysis(backend.target.durations())])
    viol = []
    for q, pl, isd in dr + nu:
        for r in ("anc1", "s1", "anc2"):
            if pl[r] in drifters: viol.append((q, r, pl[r]))
        for kind, ch, sh in (("WIT", True, WITNESS_SHOTS), ("REF", False, REF_SHOTS)):
            t = sched.run(transpile(witness(backend, q, pl, D, ch), backend,
                                    optimization_level=1, seed_transpiler=SEED))
            n2 = sum(1 for i in t.data if i.operation.num_qubits == 2)
            pubs.append((t, None, sh))
            meta.append({"block": f"{kind}_q{q}", "kind": kind, "q": q, "plan": pl,
                         "role": "drifter" if isd else "quiet", "shots": sh, "n2q": n2})
    for tag, st in (("cal0_end", 0), ("cal1_end", 1)):
        qc = QuantumCircuit(NPHYS)
        if st: qc.x(range(NPHYS))
        qc.measure_all()
        pubs.append((transpile(qc, backend, optimization_level=0), None, CAL_SHOTS))
        meta.append({"block": tag, "shots": CAL_SHOTS})
    print(f"[precond 1] drifter-in-partner-role violations: {viol if viol else 'NONE'}")
    assert not viol
    n2s = sorted({m["n2q"] for m in meta if m.get("kind") == "WIT"})
    print(f"[precond 2] witness 2q counts: {n2s} (identical={len(n2s)==1})")
    att = {f"k{k}": tau_from_calibration(0.7202, k, MQ[k]) for k in (2, 3)}
    for k, a in att.items():
        print(f"[fireability {k}] tau={a['tau']} P(fire|ALT)={a['P_fire_given_ALT']} "
              f"P(fire|NULL)={a['P_fire_given_NULL']} sep={a['separation_sd']}sd "
              f"range={a['dynamic_range_counts']}")
    tot = sum(m["shots"] for m in meta)
    print(f"[cost] {len(pubs)} pubs / {tot} shots ~ {tot/100000*35:.0f} QPU-s (pool {pool}s)")
    man = {"card": "armn_verdict_flight", "cycle": "C5018", "substrate": "claude-fable-5",
           "backend": BACKEND, "account": ACCOUNT, "cal_epoch_at_build": cal, "delay_dt": D,
           "dd": "OFF — bare delay (measured best: no density beats it)",
           "NULL_ATTEN_theory": NULL_ATTEN, "M": M, "m_Q": MQ, "u_gate": U_GATE,
           "tau_source": ("FROZEN FORMULA in tau_from_calibration(); only free input is u_app "
                          "from the co-batched channel-free REF pub. NEVER from witness data."),
           "fireability_attestation_at_build": att,
           "select_bar": SELECT_BAR, "candidates": {"drifter": [c[0] for c in dr],
                                                    "quiet": [c[0] for c in nu]},
           "preconditions": {"1_partner_exclusion": {"drifter_set": sorted(drifters),
                                                     "violations": viol},
                             "2_duration_2q": n2s,
                             "3_pairing": "frozen_pairing() + cal_start marginals in bundle",
                             "4_interval": "Ember both-ends check"},
           "cost": {"pubs": len(pubs), "shots": tot}, "pubs_meta": meta}
    if submit:
        job = SamplerV2(mode=backend).run(pubs)
        man["job_id"] = job.job_id(); man["submit_iso"] = datetime.datetime.now(datetime.UTC).isoformat()
        p = os.path.join(RES, f"armn_verdict_manifest_{job.job_id()}.json")
        json.dump(man, open(p, "w"), indent=1); print(f"SUBMITTED {job.job_id()} -> {p}")
    else:
        p = os.path.join(RES, "armn_verdict_build_c5018.json")
        json.dump(man, open(p, "w"), indent=1); print(f"[build] $0 -> {p}")


if __name__ == "__main__":
    main(submit="--submit" in sys.argv)
