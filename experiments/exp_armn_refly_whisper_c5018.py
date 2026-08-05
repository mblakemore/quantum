#!/usr/bin/env python3
"""ARM-N RE-FLY — single-job, select-on-start / verify-on-end (Whisper C5018).

WHY THIS DESIGN: the first arm-N flight (d9piq6bbvhrs73a2mhh0) was ruled
INCONCLUSIVE-BY-APPARATUS — a readout profile matched at census time had drifted ~0.009
against a 0.005 bar by flight time, in the adverse (false-ALT) direction. Ember's re-fly rule
sized against that ~5-hour gap turned out UNSATISFIABLE (required stability was negative).
This design removes the gap instead of tolerating it:

  ONE JOB.  cal_start -> [candidate-superset witness circuits] -> cal_end
  SELECT the graded pairs from cal_START, using a rule FROZEN before submission.
  VERIFY the match on cal_END — data genuinely independent of the selection data.

The census->flight interval becomes ZERO BY CONSTRUCTION; the verification interval becomes
the job duration (minutes), where today's bracket measured within-job movement at
~0.002-0.003 worst-case.

FROZEN PAIRING RULE (committed before submission; Elder recomputes it from rule + delivered
cal and any divergence is fail-closed, general#4844):
  For each candidate drifter d (census >=3 sigma), among candidate nulls n not already used:
    pair with the n minimizing |profile(d) - profile(n)| on the START cal,
    subject to that difference <= SELECT_BAR (0.002).
  A drifter with no qualifying partner is NOT GRADED (never force-paired).
  Ties broken by lower physical index. profile = (e0 + e1)/2, the selection metric of record.

RECEIPT (general#4852/#4857): the bundle emits `hazard_removed_dt` — the measured
census->start drift per candidate, i.e. the hazard this design removes rather than detects.
It gates nothing. It converts "the gap is zero because I built it that way" into a number.

PRECONDITIONS the court verifies from artifacts (all mechanical, none resting on care):
  1. no census drifter in any partner role (anc1/s1/anc2)  [derived from the census artifact]
  2. per-block total scheduled duration match              [equalizer, disclosed]
  3. pairing reproduction from (frozen rule + delivered cal)  [Elder recompute]
  4. Ember's both-ends interval check                      [her tool, upstream of decode]
"""
import json, os, sys, datetime
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
QROOT = os.path.join(HERE, "..")
RES = os.path.join(QROOT, "results")
sys.path.insert(0, os.path.join(QROOT, "scripts"))

# reuse the flown compile's verified machinery verbatim (zero re-transcription)
from exp_armn_flight_compile_whisper_c5018 import (
    neighbors, _h, _cx, _swap, _relay_cx, build_q_circuit, build_c1_circuit,
    build_lanc_circuit, transpile_with_dd, struct_fingerprint,
    CENSUS_JOB, BACKEND, ACCOUNT, M, MQ, C1_COPIES, Q_SHOTS, C1_SHOTS, CAL_SHOTS,
    TRIAL_ORDER_SEED,
)
from exp_crossblock_widesweep import build_twins, SEED, NPHYS

SELECT_BAR = 0.002          # frozen: selection tightness, leaves slack under Ember's 0.005
K_RUNGS = (2, 3)
CENSUS_DECODE = os.path.join(RES, f"armn_fez_census_decode_{CENSUS_JOB}.json")


def census():
    d = json.load(open(CENSUS_DECODE))
    drifters = [r["q"] for r in d["drifter_ranking"] if r.get("margin") and r["margin"] >= 3]
    quiet = [r["q"] for r in d["drifter_ranking"]
             if abs(r["excess"]) < 0.05 and (not r.get("margin") or r["margin"] < 3)]
    prof = {int(q): (v["e0"] + v["e1"]) / 2 for q, v in d["readout"].items()}
    return drifters, quiet, prof


def frozen_pairing(prof_start, drifters, nulls):
    """THE FROZEN RULE. Pure function of (profiles, candidate lists). Elder recomputes this."""
    used, pairs, ungraded = set(), [], []
    for d in sorted(drifters, key=lambda q: q):          # deterministic order
        best, bestdiff = None, None
        for n in sorted(nulls):
            if n in used:
                continue
            diff = abs(prof_start[d] - prof_start[n])
            if diff <= SELECT_BAR and (bestdiff is None or diff < bestdiff
                                       or (diff == bestdiff and n < best)):
                best, bestdiff = n, diff
        if best is None:
            ungraded.append(d)
        else:
            used.add(best)
            pairs.append({"drifter": d, "null": best, "diff": round(bestdiff, 6)})
    return pairs, ungraded


def partner_plan(backend, block, excluded):
    """Uniform 4-path geometry, drifters excluded from partner roles (precondition 1)."""
    used = set(block)

    def cands(q, used):
        out = []
        for a1 in neighbors(backend, q):
            if a1 in used or a1 in excluded: continue
            for a2 in neighbors(backend, a1):
                if a2 in used or a2 in excluded or a2 == q: continue
                for s1 in neighbors(backend, q):
                    if s1 in used or s1 in excluded or s1 in (a1, a2): continue
                    out.append({"anc1": a1, "anc2": a2, "s1": s1, "relay_mid": "anc1"})
        for s1 in neighbors(backend, q):
            if s1 in used or s1 in excluded: continue
            for a2 in neighbors(backend, s1):
                if a2 in used or a2 in excluded or a2 == q: continue
                for a1 in neighbors(backend, q):
                    if a1 in used or a1 in excluded or a1 in (s1, a2): continue
                    out.append({"anc1": a1, "anc2": a2, "s1": s1, "relay_mid": "s1"})
        return out

    order = sorted(block, key=lambda q: len([n for n in neighbors(backend, q)
                                             if n not in excluded]))

    def solve(i, u, acc):
        if i == len(order):
            return acc
        for c in cands(order[i], u):
            r = solve(i + 1, u | {c["anc1"], c["anc2"], c["s1"]}, {**acc, order[i]: c})
            if r:
                return r
        return None

    return solve(0, set(), {})


def build(submit=False):
    from ibm_multi_account import service_for_submission
    from qiskit_ibm_runtime import SamplerV2
    from qiskit import QuantumCircuit, transpile
    svc = service_for_submission(ACCOUNT)
    u = svc.usage()
    print(f"POOL ({ACCOUNT}): {u['usage_remaining_seconds']}s (re-read at submission)")
    backend = svc.backend(BACKEND)
    cal = str(backend.properties().last_update_date)
    twins, register = build_twins(backend)
    from exp_armn_flight_compile_whisper_c5018 import pad_duration_dt
    delay_dt = pad_duration_dt(backend, twins)
    drifters, quiet, prof_census = census()

    # CANDIDATE SUPERSET: every census drifter that admits a partner plan, plus every quiet
    # candidate that does. Selection happens AFTER landing from cal_start under the frozen
    # rule — so the flown set must cover every pair the rule could choose.
    excluded = set(drifters)
    cand_d = [q for q in drifters if partner_plan(backend, [q], excluded | {q}) is not None]
    cand_n = [q for q in quiet if partner_plan(backend, [q], excluded | {q}) is not None]
    print(f"[superset] drifter candidates {cand_d}")
    print(f"[superset] null candidates    {cand_n}")

    pubs, meta = [], []
    for state, tag in ((0, "cal0_start"), (1, "cal1_start")):
        qc = QuantumCircuit(NPHYS)
        if state:
            qc.x(range(NPHYS))
        qc.measure_all()
        pubs.append((transpile(qc, backend, optimization_level=0), None, CAL_SHOTS))
        meta.append({"block": tag, "shots": CAL_SHOTS})

    # Per-CANDIDATE single-qubit witness blocks (k=1 units). A graded k=2/k=3 rung is
    # assembled at decode from the pairs the frozen rule selects — so the flown circuits do
    # not encode the selection, which is what makes select-after-landing legitimate.
    durations, structures, plans = {}, {}, {}
    for role, cands_ in (("drifter", cand_d), ("null", cand_n)):
        for q in cands_:
            plan = partner_plan(backend, [q], excluded | {q})
            plans[f"{role}_q{q}"] = plan
            tq = transpile_with_dd(backend, build_q_circuit(backend, twins, [q], plan, delay_dt))
            tc = transpile_with_dd(backend, build_c1_circuit(backend, twins, [q], delay_dt))
            tl = transpile_with_dd(backend, build_lanc_circuit(backend, twins, [q], plan, delay_dt))
            for tag, c, sh in ((f"Q_{role}_q{q}", tq, Q_SHOTS),
                               (f"C1_{role}_q{q}", tc, C1_SHOTS),
                               (f"LANC_{role}_q{q}", tl, 2000)):
                pubs.append((c, None, sh))
                meta.append({"block": tag, "role": role, "q": q, "shots": sh,
                             "scheduled_duration_dt": c.duration})
            durations[f"q{q}"] = {"Q": tq.duration, "C1": tc.duration, "LANC": tl.duration}
            structures[f"q{q}"] = struct_fingerprint(tq)

    for state, tag in ((0, "cal0_end"), (1, "cal1_end")):
        qc = QuantumCircuit(NPHYS)
        if state:
            qc.x(range(NPHYS))
        qc.measure_all()
        pubs.append((transpile(qc, backend, optimization_level=0), None, CAL_SHOTS))
        meta.append({"block": tag, "shots": CAL_SHOTS})

    # PRECONDITION 1 assert: no census drifter in any partner role, anywhere
    viol = [(k, q, r, v) for k, pl in plans.items() for q, p in pl.items()
            for r, v in p.items() if r in ("anc1", "s1", "anc2") and v in excluded]
    print(f"[precond 1] census-drifter partner violations: {viol if viol else 'NONE'}")
    assert not viol, "precondition 1 violated"

    # PRECONDITION 2: all candidate blocks are single-qubit and structurally identical by
    # construction; report the duration spread so the equalization is verifiable, not asserted
    qd = {k: v["Q"] for k, v in durations.items()}
    print(f"[precond 2] Q-circuit durations: min {min(qd.values())} max {max(qd.values())} dt "
          f"(identical={len(set(qd.values())) == 1})")

    man = {"card": "armn_refly", "cycle": "C5018", "substrate": "claude-fable-5",
           "backend": BACKEND, "account": ACCOUNT, "cal_epoch_at_build": cal,
           "design": "single-job select-on-start / verify-on-end; gap eliminated by construction",
           "frozen_pairing_rule": {
               "metric": "(e0+e1)/2 per qubit from cal_start",
               "select_bar": SELECT_BAR,
               "rule": "for each drifter in ascending index order, pair with the unused null "
                       "minimizing |profile diff| subject to diff <= select_bar; ties to lower "
                       "index; no qualifying partner => NOT GRADED (never force-paired)",
               "reproducible_from": "this rule + cal_start marginals in the delivered bundle"},
           "candidates": {"drifter": cand_d, "null": cand_n},
           "partner_plans": {k: {str(q): p for q, p in pl.items()} for k, pl in plans.items()},
           "durations": durations, "structures": structures,
           "census_job": CENSUS_JOB, "census_profiles": {str(k): v for k, v in prof_census.items()},
           "rungs_assembled_at_decode": list(K_RUNGS),
           "M": M, "m_Q": MQ, "trial_order_seed": TRIAL_ORDER_SEED,
           "preconditions": {"1_partner_exclusion": "asserted at build (no violations)",
                             "2_duration": qd,
                             "3_pairing_reproduction": "frozen rule above + cal_start in bundle",
                             "4_interval_check": "Ember, both ends, upstream of decode"},
           "pubs_meta": meta}
    if submit:
        job = SamplerV2(mode=backend).run(pubs)
        man["job_id"] = job.job_id()
        man["submit_iso"] = datetime.datetime.now(datetime.UTC).isoformat()
        p = os.path.join(RES, f"armn_refly_manifest_{job.job_id()}.json")
        json.dump(man, open(p, "w"), indent=1)
        print(f"SUBMITTED {job.job_id()} -> {p}")
    else:
        p = os.path.join(RES, "armn_refly_build_c5018.json")
        json.dump(man, open(p, "w"), indent=1)
        print(f"[build] $0 — no submit ({len(pubs)} pubs). -> {p}")


if __name__ == "__main__":
    build(submit="--submit" in sys.argv)
