#!/usr/bin/env python3
"""ARM-N FLIGHT COMPILE (Whisper C5018) — steps 3+4 of the GO chain (#4712).

Frozen inputs: prereg docs/exp-steth-advantage-prereg-DRAFT-whisper-c4998.md (G1-G4 closed;
arm-N rule: ALT iff ZERO odd parities, m_Q=24 -> 48 copies/trial, M=40 sealed trials/rung;
R_N=3); census decode armn_fez_census_decode_d9pelcrbvhrs73a2he50.json; blocks locked #4718
(k2 ALT {51,48}/NULL {32,50}; k3 ALT {51,48,39}/NULL {32,50,16}); copy structure = sequential
with storage on copy 1 only (asymmetry lands NULL-ward — Elder's soundness pass #4720);
channel = the register-wide d160 twin pad, EXACTLY the census's channel.

BATCHING (stated, in-manifest): arm-N Q and C1 circuits are DETERMINISTIC (no randomized
elements — the fence-6 fresh-randomness rule binds randomized elements only), so copies are
iid shots of one circuit per block. Trial assignment at decode: trial t (Ember's sealed label
b_t) consumes the next m_Q=24 (Q) / 48 (C1) shots of block b_t's pool in trial_order —
statistically identical to interleaved execution for deterministic circuits.

PER-BLOCK Q CIRCUIT (two-copy Choi purity, destructive Bell pairing):
  copy 1: H(anc1_i), CX(anc1_i->blk_i) ; PAD(d160, register-wide) ; SWAP blk_i->s1_i
  copy 2: H(anc2_i), CX(anc2_i->blk_i) ; PAD(d160) ;   (copy-2 system half = blk itself)
  pairing: CX(anc1_i->anc2_i)+H(anc1_i) ; CX(s1_i->blk_i)+H(s1_i) ; measure all
  statistic per shot: odd-parity count over pairs (frozen rule).
  Ancillas/storage OUTSIDE the 42q pad register, X-X DD during pads (fence 2's rider
  measures ancilla survival in-job).

C1 (honest |0>-probe, G3): prep |0> on block, PAD(d160), measure Z. Deterministic.

RIDERS co-batched (fence 2-4): cal0/cal1 (flight-cal for the bundle's readout lists — the
Ember #4716 independence upgrade), lambda_anc (Bell-prep, PAD, un-prep, measure ancillas),
SPAM identity-reference on each block.

REQ-3 ASSERT at build: ALT and NULL compiled circuits identical except qubit mapping —
op-name histograms, depth, 2q count must MATCH; diff printed; mismatch = no submit.

Modes: --build ($0: compile, asserts, bundle skeleton) | --submit (fez/ALT2, after
structural CLEAR) | --decode <jid> (frozen rule + bundle finalization from flight cal).
"""
import json, os, sys, datetime
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
QROOT = os.path.join(HERE, "..")
RES = os.path.join(QROOT, "results")
sys.path.insert(0, os.path.join(QROOT, "scripts"))

from exp_crossblock_widesweep import build_twins, SEED, NPHYS

CENSUS_JOB = "d9pelcrbvhrs73a2he50"
BACKEND = "ibm_fez"
ACCOUNT = "IBMQ_ALT2"
# RE-SELECTED under the JOINT constraint (#4739): req-2 profile match AND topological
# feasibility with ALL census drifters excluded from partner roles (the false-ALT
# partner-contamination channel found at compile). Originally-locked blocks {51,48}/{32,50}
# are INFEASIBLE under it. Top-by-drift-strength of 14 (k=2) / 16 (k=3) feasible pairs.
RUNGS = {2: {"alt": [48, 25], "null": [142, 75]},
         3: {"alt": [48, 25, 71], "null": [142, 75, 46]}}
M, MQ, C1_COPIES = 40, 24, 48
Q_SHOTS = M * MQ            # 960 per block per rung
C1_SHOTS = M * C1_COPIES    # 1920 per block per rung
CAL_SHOTS = 8000
TRIAL_ORDER_SEED = int(CENSUS_JOB[-6:], 36)  # public, fresh, derived — documented not chosen


def neighbors(backend, q):
    cm = backend.configuration().coupling_map
    ns = set()
    for a, b in cm:
        if a == q: ns.add(b)
        if b == q: ns.add(a)
    return sorted(ns)


def pick_partners(backend, block, register):
    """UNIFORM PATH GEOMETRY per block qubit: a 4-path anc2 - anc1 - blk - s1, disjoint
    across block qubits. Every role's gate sequence is then IDENTICAL by construction:
    prep-1 CX(anc1->blk) native; SWAP(blk,s1) native; prep-2 CX(anc2->blk) = the fixed
    4-CX relay through (occupied) anc1 — an operator identity independent of the middle
    state; pairing CX(anc1->anc2) and CX(s1->blk) both native. 10 CX per block qubit,
    every position, both blocks — req-3 exactness by construction."""
    # EXCLUSION SET: both blocks' qubits AND every census drifter (>=3sigma). A drifter
    # serving as a partner would feed coherent drift into the witness through the partner
    # role — coherent = pure = zero odd parities = reads ALT: the FALSE-ALT path the court
    # could not construct (#4720/#4722) EXISTS via partner contamination and is excluded
    # here by constraint. (Found at compile: q50's only free neighbor is census-drifter q48.)
    # DERIVED, never transcribed (C4872 lesson): the exclusion set is read from the census
    # decode artifact at build time, so a re-census automatically re-derives it and a
    # hand-copied list can never drift from the measurement it claims to represent.
    _cd = json.load(open(os.path.join(RES, f"armn_fez_census_decode_{CENSUS_JOB}.json")))
    CENSUS_DRIFTERS = {r["q"] for r in _cd["drifter_ranking"]
                       if r.get("margin") and r["margin"] >= 3}
    all_blocks = {q for r in RUNGS.values() for role in r.values() for q in role}
    excluded = set(block) | all_blocks | CENSUS_DRIFTERS

    def paths_for(q, used):
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
    def solve(i, used, acc):
        if i == len(order):
            return acc
        q = order[i]
        for cand in paths_for(q, used):
            vals = {cand["anc1"], cand["anc2"], cand["s1"]}
            r = solve(i + 1, used | vals, {**acc, q: cand})
            if r is not None:
                return r
        return None

    plan = solve(0, set(), {})
    assert plan, f"no joint disjoint assignment for block {block}"
    return plan


def _h(qc, q):
    qc.rz(np.pi / 2, q); qc.sx(q); qc.rz(np.pi / 2, q)


def _cx(qc, a, b):
    _h(qc, b); qc.cz(a, b); _h(qc, b)


def _swap(qc, a, b):
    _cx(qc, a, b); _cx(qc, b, a); _cx(qc, a, b)


def _relay_cx(qc, a, mid, b):
    """CX(a->b) through occupied mid: CX(a,mid)CX(mid,b)CX(a,mid)CX(mid,b) — restores mid."""
    _cx(qc, a, mid); _cx(qc, mid, b); _cx(qc, a, mid); _cx(qc, mid, b)


def pad_duration_dt(backend, twins):
    """Wall-clock duration (dt units) of the scheduled d160 twin pad on this backend —
    the block-local channel is a DELAY of exactly this duration (drift is time-accumulated:
    kingston clock census, constant deg/layer linear in depth; gate-driven components missed
    by delay land toward NULL = conservative, stated in manifest)."""
    from qiskit import transpile
    t = transpile(twins[160], backend, optimization_level=1,
                  seed_transpiler=SEED, scheduling_method="alap")
    return t.duration


def build_q_circuit(backend, twins, block, plan, delay_dt):
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(NPHYS)
    for q in block:                       # copy 1 prep (native, fixed decomposition)
        a1 = plan[q]["anc1"]
        _h(qc, a1); _cx(qc, a1, q)
    qc.barrier()
    for q in block:
        qc.delay(delay_dt, q, unit="dt")  # the channel, copy 1
    qc.barrier()
    for q in block:
        _swap(qc, q, plan[q]["s1"])       # store copy-1 system half
    qc.barrier()
    for q in block:                       # copy 2 prep: relay CX through an occupied middle
        p = plan[q]
        mid = p[p.get("relay_mid", "anc1")]
        _h(qc, p["anc2"]); _relay_cx(qc, p["anc2"], mid, q)
    qc.barrier()
    for q in block:
        qc.delay(delay_dt, q, unit="dt")  # the channel, copy 2
    qc.barrier()
    for q in block:                       # destructive transversal Bell pairing
        p = plan[q]
        _cx(qc, p["anc1"], p["anc2"]); _h(qc, p["anc1"])
        _cx(qc, p["s1"], q); _h(qc, p["s1"])
    qc.measure_all()
    return qc


def build_c1_circuit(backend, twins, block, delay_dt):
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(NPHYS)
    for q in block:
        qc.delay(delay_dt, q, unit="dt")
    qc.measure_all()
    return qc


def build_lanc_circuit(backend, twins, block, plan, delay_dt):
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(NPHYS)
    for q in block:
        a1 = plan[q]["anc1"]
        _h(qc, a1); _cx(qc, a1, q)
    qc.barrier()
    for q in block:
        qc.delay(delay_dt, q, unit="dt")
    qc.barrier()
    for q in block:
        a1 = plan[q]["anc1"]
        _cx(qc, a1, q); _h(qc, a1)   # un-prep: ideal -> all zeros on (anc, blk)
    qc.measure_all()
    return qc


def transpile_with_dd(backend, qc):
    from qiskit import transpile
    from qiskit.transpiler import PassManager
    from qiskit.transpiler.passes import ALAPScheduleAnalysis, PadDynamicalDecoupling
    from qiskit.circuit.library import XGate
    tqc = transpile(qc, backend, optimization_level=1, seed_transpiler=SEED)
    durations = backend.target.durations()
    pm = PassManager([ALAPScheduleAnalysis(durations),
                      PadDynamicalDecoupling(durations, [XGate(), XGate()])])
    return pm.run(tqc)


def struct_fingerprint(tqc):
    ops = {}
    for i in tqc.data:
        ops[i.operation.name] = ops.get(i.operation.name, 0) + 1
    return {"depth": tqc.depth(), "d2q": sum(1 for i in tqc.data if i.operation.num_qubits == 2),
            "ops": dict(sorted(ops.items()))}


def do_build(submit=False):
    from ibm_multi_account import service_for_submission
    from qiskit_ibm_runtime import SamplerV2
    from qiskit import QuantumCircuit, transpile
    svc = service_for_submission(ACCOUNT)
    u = svc.usage()
    print(f"POOL ({ACCOUNT}): {u['usage_remaining_seconds']}s (re-read at submission)")
    backend = svc.backend(BACKEND)
    cal = str(backend.properties().last_update_date)
    print(f"{BACKEND} cal epoch: {cal}")
    twins, register = build_twins(backend)
    delay_dt = pad_duration_dt(backend, twins)
    print(f"[channel] block-local DELAY = {delay_dt} dt (scheduled d160 twin-pad duration)")

    pubs, meta = [], []
    for state, tag in ((0, "cal0"), (1, "cal1")):
        qc = QuantumCircuit(NPHYS)
        if state:
            qc.x(range(NPHYS))
        qc.measure_all()
        pubs.append((transpile(qc, backend, optimization_level=0), None, CAL_SHOTS))
        meta.append({"block": tag, "shots": CAL_SHOTS})

    structure = {}
    structure_sched = {}
    plans = {}
    for k, blocks in RUNGS.items():
        for role in ("alt", "null"):
            blk = blocks[role]
            plan = pick_partners(backend, blk, register)
            plans[f"k{k}_{role}"] = plan
            tq = transpile_with_dd(backend, build_q_circuit(backend, twins, blk, plan, delay_dt))
            tc = transpile_with_dd(backend, build_c1_circuit(backend, twins, blk, delay_dt))
            tl = transpile_with_dd(backend, build_lanc_circuit(backend, twins, blk, plan, delay_dt))
            for tag, tqc, shots in ((f"Q_k{k}_{role}", tq, Q_SHOTS),
                                    (f"C1_k{k}_{role}", tc, C1_SHOTS),
                                    (f"LANC_k{k}_{role}", tl, 2000)):
                pubs.append((tqc, None, shots))
                meta.append({"block": tag, "k": k, "role": role, "shots": shots})
            # req-3 compares the LOGICAL compiled shape (pre-DD): DD padding is per-qubit-
            # duration-consequent (mapping-class, excluded by the checker's design); the
            # scheduled deltas are DISCLOSED separately for the sealer's veto.
            from qiskit import transpile as _tp
            pre = _tp(build_q_circuit(backend, twins, blk, plan, delay_dt), backend,
                      optimization_level=0, seed_transpiler=SEED)
            structure[f"k{k}_{role}"] = struct_fingerprint(pre)
            structure_sched[f"k{k}_{role}"] = struct_fingerprint(tq)

    # BRACKETING CALS (court ask #4726/#4728): end-of-job cal blocks — cal-vs-cal drift
    # across the co-batch becomes measurable; Elder's NULL discharge condition + Ember's
    # interval check + fez within-epoch stability, one cheap block.
    for state, tag in ((0, "cal0_end"), (1, "cal1_end")):
        qc = QuantumCircuit(NPHYS)
        if state:
            qc.x(range(NPHYS))
        qc.measure_all()
        pubs.append((transpile(qc, backend, optimization_level=0), None, CAL_SHOTS))
        meta.append({"block": tag, "shots": CAL_SHOTS})

    # REQ-3 structural assert: ALT vs NULL fingerprints match per k (except mapping)
    req3 = {}
    for k in RUNGS:
        a, n = structure[f"k{k}_alt"], structure[f"k{k}_null"]
        match = (a["ops"] == n["ops"] and a["depth"] == n["depth"] and a["d2q"] == n["d2q"])
        req3[f"k{k}"] = {"match": match, "alt": a, "null": n}
        print(f"[req3] k={k}: ALT vs NULL structural match = {match} "
              f"(depth {a['depth']}/{n['depth']}, 2q {a['d2q']}/{n['d2q']})")
    if not all(v["match"] for v in req3.values()):
        print("[req3] MISMATCH — printing diffs; NO SUBMIT")
        for k, v in req3.items():
            if not v["match"]:
                print(k, "ALT", v["alt"], "NULL", v["null"])
        if submit:
            sys.exit("req3 failed")

    # trial_order: genuine shuffle, public derived seed (Ember #4228: never an interleave)
    rng = np.random.default_rng(TRIAL_ORDER_SEED)
    trial_order = {f"k{k}": [int(x) for x in rng.permutation(M)] for k in RUNGS}

    man = {"card": "armn_flight", "cycle": "C5018", "substrate": "claude-fable-5",
           "backend": BACKEND, "account": ACCOUNT, "cal_epoch_at_build": cal,
           "census_job": CENSUS_JOB, "rungs": {str(k): v for k, v in RUNGS.items()},
           "partner_plans": {kk: {str(q): p for q, p in pl.items()} for kk, pl in plans.items()},
           "frozen_rule": "ALT iff zero odd parities; m_Q=24; M=40; R_N=3; u-gate per G3 table",
           "batching": "deterministic circuits -> iid shots; trial t consumes next m_Q/48 shots of block b_t in trial_order",
           "channel": "BLOCK-LOCAL DELAY at the scheduled d160 twin-pad duration (census register topologically self-enclosed: zero free partners register-wide -> the prereg's own block-local padded-idle reading; time-accumulated drift per kingston clock census; gate-driven components missed land toward NULL = conservative)",
           "trial_order_seed": TRIAL_ORDER_SEED, "trial_order": trial_order,
           "structure": {kk: v for kk, v in structure.items()},
           "structure_scheduled_deltas": structure_sched,
           "bracketing_cals": "cal0/cal1 at job start AND cal0_end/cal1_end at job end (#4726)", "req3": {k: v["match"] for k, v in req3.items()},
           "go": "G4 Creator #4711; court soundness Elder #4720; blocks #4718",
           "pubs_meta": meta}
    if submit:
        job = SamplerV2(mode=backend).run(pubs)
        man["job_id"] = job.job_id()
        man["submit_iso"] = datetime.datetime.now(datetime.UTC).isoformat()
        path = os.path.join(RES, f"armn_flight_manifest_{job.job_id()}.json")
        json.dump(man, open(path, "w"), indent=1)
        print(f"SUBMITTED {job.job_id()} -> {path}")
    else:
        path = os.path.join(RES, "armn_flight_build_c5018.json")
        json.dump(man, open(path, "w"), indent=1)
        print(f"[build] $0 — no submit. -> {path}")
        # bundle skeleton for Ember's structural CLEAR (readout.* = PENDING flight cal)
        bundle = {"readout": {"drifter": "PENDING_FLIGHT_CAL", "null": "PENDING_FLIGHT_CAL"},
                  "structure": {"drifter": {f"k{k}": structure[f"k{k}_alt"] for k in RUNGS},
                                "null": {f"k{k}": structure[f"k{k}_null"] for k in RUNGS}},
                  "trial_order": trial_order, "trial_order_seed": TRIAL_ORDER_SEED,
                  "note": "structural-CLEAR stage; readout lists populate from the FLIGHT job's cal (Ember #4716 independence)"}
        bpath = os.path.join(RES, "armn_bundle_structural_c5018.json")
        json.dump(bundle, open(bpath, "w"), indent=1)
        print(f"[bundle] structural skeleton -> {bpath}")


if __name__ == "__main__":
    if "--submit" in sys.argv:
        do_build(submit=True)
    else:
        do_build(submit=False)
