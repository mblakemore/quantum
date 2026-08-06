#!/usr/bin/env python3
"""KINGSTON LADDER — the qualifying-block-count and spread question, with PRECONDITION 5.

Creator: "fly the ladder on kingston?"  The $0 pre-flight re-decode changed what this flight
is FOR, so the question is restated here rather than inherited.

WHAT CHANGED: the arm-N closure (~22x infeasible) was withdrawn hours after filing. Its input
— pooled within-group purity sd 0.0378 — was one qubit: q72 on fez carries 30-35% readout
error and sits in exactly two of nine blocks, which are exactly the two with near-singular
correction maps (cond 3.0 vs 1.07-1.12) and exactly the two highest purities. Clean estimates
are 0.0068 (n=7, same job) and 0.0120 (n=6, independent ladder job) -> 0.7x-2.2x infeasible,
not 22x. Arm-N is a DESIGN problem.

SO THE QUESTION IS NO LONGER "does the spread generalise". It is:

    With a readout-quality precondition applied AT BUILD TIME, how many blocks QUALIFY on a
    second Heron-r2, and what is the purity spread among them?

Both halves matter and they pull against each other: the precondition improves the spread and
REDUCES the qualifying count. Arm-N already fails to assemble under four constraints; this
adds a fifth. Whether the net is favourable is empirical, and unmeasured.

=== PRECONDITION 5 (NEW — the check that did not exist) ===
No block may contain a qubit whose calibrated readout error exceeds READOUT_BAR. The bar is
frozen at 0.05: it cleanly separates the fez set (max clean 0.031) from the offender (0.308),
and it is set from the CALIBRATION, which carries no outcome information. Every block reports
its correction-map condition number alongside its purity, so a near-singular correction can
never again pass unremarked.

=== PRE-REGISTERED BRANCHES (written before submission) ===
Primary estimand: pooled candidate-to-candidate purity sd on the witness config (shallow_2),
over blocks that PASS precondition 5. Secondary: N_qualify, the count that passes.

  (a) sd <= 0.015 AND N_qualify >= 12  -> the design is FEASIBLE on kingston. The fez closure
      was an artifact end-to-end and arm-N should be re-pre-registered, not retired.
  (b) sd <= 0.015 AND N_qualify < 12   -> spread is fine, BLOCK COUNT is the binding
      constraint. The blocker is topology + preconditions, and it is a design-search problem
      (which constraints can be relaxed without reopening a false-ALT channel), not a wall.
  (c) sd >= 0.030                      -> heavy-tailed spread is a real Heron-r2 property and
      survives the readout precondition. The closure was right for the wrong reason, and it
      should be re-filed on THIS evidence rather than on q72.
  (d) anything between                 -> report the interval, decline to round to a story.

NO branch is chosen after the data, and NO bar moves. If kingston's cal shows offenders like
q72, that IS the result for N_qualify, not a reason to raise the bar.

=== SECONDARY: does idle-dominance generalise? ===
The fez ladder measured gates+readout at 0.08 across 9 CZ and each channel idle at ~0.12 —
idle-dominated ~3:1, which is why the campaign default became DD OFF. A 4-config subset rides
along on 4 candidates so that conclusion is tested off-fez rather than assumed chip-invariant.

COST: sized against the IBMQ_ALT pool (156s; ALT2 has 26s, TOKEN 13s — ALT is the only viable
one). Shots are the cost, not pubs: the fez ladder was 160k shots ~ 56 QPU-s, so ~2.9 kshot
per QPU-s is the working rate and this build is priced against it BEFORE submitting.
"""
import json, os, sys, datetime
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
QROOT = os.path.join(HERE, ".."); RES = os.path.join(QROOT, "results")
sys.path.insert(0, os.path.join(QROOT, "scripts"))

BACKEND = "ibm_kingston"
ACCOUNT = "IBMQ_ALT"          # only viable pool (156s); ALT2 26s, TOKEN 13s
READOUT_BAR = 0.05            # FROZEN. Separates 0.031 (clean) from 0.308 (offender) on fez.
COND_REPORT = True
DELAY_DT = None               # taken from the backend's own dt-matched pad, as on fez
SHOTS_WIT = 4000              # witness config, per candidate
SHOTS_LADDER = 6000           # shallow_0 / shallow_1 legs
CAL_SHOTS = 8000
MAX_CANDIDATES = 16           # spread leg
LADDER_SUBSET = 4             # full 4-config ladder on this many
QPU_S_PER_KSHOT = 1.0 / 2.9   # measured on the fez ladder (160 kshot -> 56 QPU-s)
POOL_GUARD = 100              # refuse to submit if the estimate exceeds this many QPU-s


def main(submit=False):
    from ibm_multi_account import service_for_submission
    from qiskit_ibm_runtime import SamplerV2
    from qiskit import QuantumCircuit, transpile
    from exp_armn_shallow_witness_whisper_c5018 import three_neighbour_plan
    from exp_armn_verdict_whisper_c5018 import witness
    from exp_armn_flight_compile_whisper_c5018 import pad_duration_dt
    from exp_crossblock_widesweep import build_twins

    svc = service_for_submission(ACCOUNT)
    svc = svc[0] if isinstance(svc, tuple) else svc
    pool = svc.usage()["usage_remaining_seconds"]
    print(f"POOL ({ACCOUNT}): {pool}s")
    backend = svc.backend(BACKEND)
    props = backend.properties()
    cal = str(props.last_update_date)
    print(f"backend {BACKEND}  cal {cal}")

    # ---- PRECONDITION 5 INPUT: per-qubit readout error straight from the calibration ----
    nq = backend.num_qubits
    rerr = {}
    for q in range(nq):
        try:
            rerr[q] = float(props.readout_error(q))
        except Exception:
            rerr[q] = 1.0        # unknown = disqualified, never silently admitted
    bad = sorted([q for q in range(nq) if rerr[q] > READOUT_BAR])
    print(f"[precond 5] readout bar {READOUT_BAR}: {len(bad)}/{nq} qubits FAIL "
          f"(worst {max(rerr.values()):.3f}, median {np.median(list(rerr.values())):.4f})")
    print(f"[precond 5] failing qubits: {bad[:30]}{' ...' if len(bad) > 30 else ''}")

    twins, _ = build_twins(backend)
    D = pad_duration_dt(backend, twins)
    print(f"channel idle D = {D} dt")

    # ---- candidate selection: FROZEN RULE, applied before any outcome exists ----
    # A candidate qualifies iff (1) it has three free adjacent neighbours, and
    # (2) EVERY qubit in the resulting block passes the readout bar.
    excluded = set(bad)
    cands, rejected_readout = [], []
    for q in range(nq):
        if q in excluded:
            continue
        pl = three_neighbour_plan(backend, q, excluded | {q})
        if not pl:
            continue
        block = [pl["anc1"], pl["anc2"], pl["s1"], q]
        worst = max(rerr[b] for b in block)
        if worst > READOUT_BAR:
            rejected_readout.append((q, round(worst, 4)))
            continue
        cands.append({"q": q, "plan": pl, "worst_readout": round(worst, 4)})

    n_qualify = len(cands)
    print(f"\n[N_qualify] {n_qualify} blocks pass three-neighbour AND readout bar")
    print(f"[rejected on readout alone] {len(rejected_readout)}")

    # deterministic pick: lowest worst-readout first, tie-break by qubit index
    cands.sort(key=lambda c: (c["worst_readout"], c["q"]))
    sel = cands[:MAX_CANDIDATES]
    ladder_sel = sel[:LADDER_SUBSET]
    print(f"[selected] {[c['q'] for c in sel]}")

    # ---- cost, priced BEFORE submitting ----
    kshot = (2 * CAL_SHOTS
             + len(sel) * SHOTS_WIT                       # shallow_2 (witness) leg
             + len(ladder_sel) * (2 * SHOTS_LADDER + SHOTS_WIT)) / 1000.0
    est = kshot * QPU_S_PER_KSHOT
    print(f"\n[cost] {kshot:.0f} kshot -> ~{est:.0f} QPU-s estimated (pool {pool}s)")
    if est > POOL_GUARD or est > pool * 0.75:
        print(f"REFUSING: estimate {est:.0f}s exceeds guard {POOL_GUARD}s or 75% of pool")
        return None

    if not submit:
        print("\n[dry run] pass --submit to fly")
        return {"n_qualify": n_qualify, "selected": [c["q"] for c in sel], "est_qpu_s": est}

    # ---- build pubs ----
    pubs, meta = [], []
    for tag, st in (("cal0", 0), ("cal1", 1)):
        qc = QuantumCircuit(nq)
        if st:
            for i in range(nq):
                qc.x(i)
        qc.measure_all()
        pubs.append(transpile(qc, backend, optimization_level=1))
        meta.append({"block": tag, "shots": CAL_SHOTS})

    def add(q, pl, cfg, ch, deep, shots):
        qc = witness(backend, q, pl, D if ch else 0, ch)
        t = transpile(qc, backend, optimization_level=1)
        pubs.append(t)
        n2 = sum(1 for i in t.data if i.operation.num_qubits == 2)
        meta.append({"block": f"{cfg}_q{q}", "q": q, "config": cfg, "plan": pl,
                     "n2q": n2, "shots": shots,
                     "worst_readout": max(rerr[b] for b in [pl["anc1"], pl["anc2"], pl["s1"], q])})

    for c in sel:
        add(c["q"], c["plan"], "shallow_2", True, False, SHOTS_WIT)
    for c in ladder_sel:
        add(c["q"], c["plan"], "shallow_0", False, False, SHOTS_LADDER)
        add(c["q"], c["plan"], "shallow_1", True, False, SHOTS_LADDER)

    n2s = sorted({m["n2q"] for m in meta if "n2q" in m and m["config"] == "shallow_2"})
    print(f"[precond 2] shallow_2 2q counts: {n2s} (identical={len(n2s) == 1})")

    sampler = SamplerV2(mode=backend)
    for p, m in zip(pubs, meta):
        pass
    job = sampler.run([(p,) for p in pubs], shots=max(m["shots"] for m in meta))
    jid = job.job_id()
    print(f"\nSUBMITTED {jid}")

    man = {"card": "armn_kingston_ladder", "cycle": "C5018", "substrate": "claude-fable-5",
           "backend": BACKEND, "account": ACCOUNT, "cal_epoch_at_build": cal,
           "delay_dt": D, "readout_bar": READOUT_BAR,
           "precondition_5": ("no block may contain a qubit with calibrated readout error "
                              "> READOUT_BAR; bar frozen before build from the CALIBRATION, "
                              "which carries no outcome information"),
           "n_qualify": n_qualify, "n_rejected_readout": len(rejected_readout),
           "n_qualify_caveat": ("NOT apples-to-apples with fez's 9. That 9 was AFTER drifter "
                                "exclusion; this count has no drifter exclusion (no kingston "
                                "census exists). It is an UPPER bound on the arm-N qualifying "
                                "count, and a census would reduce it. Reported as such."),
           "n_rejected_readout_caveat": ("0 by construction, not by luck: failing qubits are "
                                         "put in `excluded` BEFORE three_neighbour_plan runs, "
                                         "so they are never chosen as partners. This counter "
                                         "is uninformative and is kept only for transparency."),
           "branch_a_note": ("N_qualify resolved AT BUILD TIME (36 >= 12) — a build-time "
                             "quantity, not data. So (a) vs (b) now hinges on sd alone. "
                             "Stated before submission so it cannot be read as a post-hoc win."),
           "rejected_readout": rejected_readout[:50],
           "readout_err_selected": {c["q"]: c["worst_readout"] for c in sel},
           "branches": {
               "a": "sd<=0.015 and N_qualify>=12 -> FEASIBLE, re-pre-register arm-N",
               "b": "sd<=0.015 and N_qualify<12  -> block count binds, design-search problem",
               "c": "sd>=0.030                   -> heavy tail is real, re-file closure on THIS",
               "d": "otherwise                    -> report the interval, no story"},
           "estimand": ("pooled candidate-to-candidate purity sd on shallow_2 over blocks "
                        "passing precondition 5; secondary N_qualify"),
           "cost_est_qpu_s": round(est, 1), "pool_at_build": pool,
           "pubs_meta": meta, "job_id": jid,
           "submit_iso": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    out = os.path.join(RES, f"armn_kingston_manifest_{jid}.json")
    json.dump(man, open(out, "w"), indent=1)
    print(f"wrote {out}")
    return man


if __name__ == "__main__":
    main(submit="--submit" in sys.argv)
