#!/usr/bin/env python3
"""FIX THE WITNESS — matched delay sweep on kingston AND fez. Step (1) of the forced ordering.

Creator: "fix the witness / anything else we can do at the same time?"

THE ORDERING (Ember #5165, agreed and not reorderable):
    (1) fix the witness so it clears u >= 0.7 SOMEWHERE   <-- THIS JOB
    (2) THEN replicate at N >= 30 qualifying blocks
    (3) THEN test mechanisms
Step (2) depends on this job's outcome, so it deliberately does NOT ride along. Conflating a
step with the step that gates it is the error class this cycle has been about.

=== WHY A SWEEP IS THE FIX ===
The witness fails on kingston at u = 0.2236 vs a frozen gate of 0.700, and the loss is
idle-specific (gates+readout are fine: shallow_0 = 0.9115 vs fez 0.9207). The idle is the only
lever, so sweeping it BOTH finds the D that clears the gate AND measures the functional form
of the loss — the same circuits, no extra cost for the second payload.

=== THE RIDER, AND WHAT IT BUYS (the "anything else" answer) ===
A MATCHED fez arm at the SAME D values. The current anomaly claim ("kingston loses 3x per
idle") compares kingston at D=1647 against fez at D=1488 — an 11% D mismatch that can explain
at most ~11% of a 3x effect, but which is nonetheless UNMATCHED. Both chips have dt = 4.0 ns,
so equal D is equal physical time and the comparison becomes clean. It also yields fez's own
u(D) curve, which is what the eventual arm-N redesign has to choose D from.

=== A FUNCTIONAL-FORM QUESTION THE LADDER ALREADY RAISED ===
Both chips lose a CONSTANT ABSOLUTE purity per idle, not a constant fraction:
    kingston  0.9115 -> 0.5670 -> 0.2236   drops 0.3445, 0.3434
    fez       0.9207 -> 0.8040 -> 0.6804   drops 0.1167, 0.1236
Multiplicative (depolarizing) decay predicts equal RATIOS, which would put kingston's
two-idle point at ~0.353; it measures 0.2236 — worse than exponential. Three points cannot
distinguish forms; five can. This is free and rides on the same pubs.

=== PRE-REGISTERED BRANCHES — EVERY ONE CARRIES THE APPARATUS GATE ===
(the correction from this cycle: a branch that can fire on a failed instrument is a formula,
 not a pre-registration)

  PRIMARY (step 1): the largest D whose two-idle witness clears u >= 0.700, per chip.
    (a) some D >= 824 clears on kingston  -> witness FIXED with useful drift exposure; step 2
        is unblocked on kingston at that D.
    (b) only D <= 412 clears on kingston  -> FIXED but at 4x-less drift exposure; step 2 is
        unblocked, and the arm-N signal cost of the short D must be priced before step 3.
    (c) NO D clears on kingston, including D=0 -> the failure is NOT the idle after all, and
        shallow_0 = 0.9115 becomes the thing to explain. Kingston is out as a host.
  SECONDARY (the anomaly, D now matched): ratio of kingston to fez absolute loss per idle at
    equal D, reported with its spread. NO claim is carried from any D where the chip's own
    witness fails the gate.
  TERTIARY (the coincidence, logged in advance as a coincidence): q21 and q47 are included
    deliberately. If they stay HIGH at every D it is a block property; if the split appears
    only at long D it is a D-dependent effect; if they track the others everywhere the
    original split was noise. Any of the three is informative and none is a mechanism.

NOTHING here sizes step (2). N >= 30 comes from Ember's f^k arithmetic and is not touched by
this job's outcome.
"""
import json, os, sys, datetime
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
QROOT = os.path.join(HERE, ".."); RES = os.path.join(QROOT, "results")
sys.path.insert(0, os.path.join(QROOT, "scripts"))

ACCOUNT = "IBMQ_ALT"            # 106s remaining; ALT2 26s, TOKEN 13s
READOUT_BAR = 0.05              # precondition 5, frozen, unchanged
GATE = 0.700                    # frozen all campaign — now a BRANCH PRECONDITION, not context
CAL_SHOTS = 8000

# D grid: ABSOLUTE dt values, IDENTICAL on both chips. dt = 4.0 ns on each, so equal dt is
# equal physical time and the cross-chip comparison is genuinely matched.
#
# CAUGHT IN DRY RUN: the first version used fractions of each chip's OWN D0 (1647 vs 1488),
# which produced grids of [0,0.82,1.65,3.3,6.59]us and [0,0.74,1.49,2.98,5.95]us — i.e. it
# REPRODUCED the very D mismatch this rider exists to remove. A control that inherits the
# confound it controls for is not a control.
#
# fez's historical D0 = 1488 dt is not on the grid; it sits between 824 and 1647 and is
# interpolable from the measured curve, which is strictly better than a second unmatched point.
D_GRID_DT = [0, 206, 412, 824, 1647]

PLAN = {
    # backend        blocks  shots   must_include (kingston: the HIGH pair, deliberately)
    "ibm_kingston": (8, 4000, [21, 47]),
    "ibm_fez":      (4, 3000, []),
}
QPU_S_PER_KSHOT = 1.0 / 2.9     # measured on the fez ladder (160 kshot -> 56 QPU-s)
POOL_GUARD_FRAC = 0.90          # refuse if the total estimate exceeds this share of the pool


def build(svc, bname, nblocks, shots, must, pool_left):
    from qiskit import QuantumCircuit, transpile
    from exp_armn_shallow_witness_whisper_c5018 import three_neighbour_plan
    from exp_armn_verdict_whisper_c5018 import witness
    from exp_armn_flight_compile_whisper_c5018 import pad_duration_dt
    from exp_crossblock_widesweep import build_twins

    backend = svc.backend(bname); props = backend.properties()
    nq = backend.num_qubits
    rerr = {}
    for q in range(nq):
        try:
            rerr[q] = float(props.readout_error(q))
        except Exception:
            rerr[q] = 1.0
    bad = {q for q in range(nq) if rerr[q] > READOUT_BAR}
    twins, _ = build_twins(backend)
    D0 = pad_duration_dt(backend, twins)      # this chip's incumbent, recorded not used for the grid
    Ds = list(D_GRID_DT)                       # IDENTICAL on both chips — matched physical time
    print(f"\n=== {bname} ===  dt={backend.dt*1e9:.2f}ns  D0={D0}dt  grid={Ds} dt "
          f"= {[round(d*backend.dt*1e6,2) for d in Ds]} us")
    print(f"  [precond 5] {len(bad)}/{nq} qubits fail readout bar {READOUT_BAR}")

    cands = []
    for q in range(nq):
        if q in bad:
            continue
        pl = three_neighbour_plan(backend, q, bad | {q})
        if not pl:
            continue
        blk = [pl["anc1"], pl["anc2"], pl["s1"], q]
        cands.append({"q": q, "plan": pl, "worst_readout": round(max(rerr[b] for b in blk), 4)})
    cands.sort(key=lambda c: (c["worst_readout"], c["q"]))
    forced = [c for c in cands if c["q"] in must]
    rest = [c for c in cands if c["q"] not in must]
    sel = forced + rest[: max(0, nblocks - len(forced))]
    print(f"  N_qualify={len(cands)}  selected={[c['q'] for c in sel]}"
          f"{' (must-include honoured: ' + str([c['q'] for c in forced]) + ')' if forced else ''}")
    missing = [m for m in must if m not in [c["q"] for c in sel]]
    if missing:
        print(f"  !! must-include {missing} did NOT qualify — recorded, not forced in")

    pubs, meta = [], []
    for tag, st in (("cal0", 0), ("cal1", 1)):
        qc = QuantumCircuit(nq)
        if st:
            for i in range(nq):
                qc.x(i)
        qc.measure_all()
        pubs.append(transpile(qc, backend, optimization_level=1))
        meta.append({"block": tag, "shots": CAL_SHOTS})

    for c in sel:
        for D in Ds:
            qc = witness(backend, c["q"], c["plan"], D, D > 0)
            t = transpile(qc, backend, optimization_level=1)
            n2 = sum(1 for i in t.data if i.operation.num_qubits == 2)
            tot_delay = sum(i.operation.duration or 0 for i in t.data
                            if i.operation.name == "delay")
            pubs.append(t)
            meta.append({"block": f"D{D}_q{c['q']}", "q": c["q"], "D": D,
                         "D_frac": round(D / D0, 3) if D0 else 0,
                         "D_us": round(D * backend.dt * 1e6, 4),
                         "plan": c["plan"], "n2q": n2, "total_delay_dt": tot_delay,
                         "worst_readout": c["worst_readout"], "shots": shots})

    n2s = sorted({m["n2q"] for m in meta if "n2q" in m})
    print(f"  [precond 2] 2q counts across ALL D: {n2s} (identical={len(n2s)==1})")
    kshot = sum(m["shots"] for m in meta) / 1000.0
    est = kshot * QPU_S_PER_KSHOT
    print(f"  [cost] {len(pubs)} pubs / {kshot:.0f} kshot -> ~{est:.0f} QPU-s")
    return backend, pubs, meta, est, {"D0": D0, "Ds": Ds, "n_qualify": len(cands),
                                      "n_bad_readout": len(bad), "missing_must": missing}


def main(submit=False):
    from ibm_multi_account import service_for_submission
    from qiskit_ibm_runtime import SamplerV2
    svc = service_for_submission(ACCOUNT)
    svc = svc[0] if isinstance(svc, tuple) else svc
    pool = svc.usage()["usage_remaining_seconds"]
    print(f"POOL ({ACCOUNT}): {pool}s")

    built, total = [], 0.0
    for bname, (nb, sh, must) in PLAN.items():
        b, pubs, meta, est, info = build(svc, bname, nb, sh, must, pool)
        built.append((bname, b, pubs, meta, est, info)); total += est

    print(f"\n[TOTAL] ~{total:.0f} QPU-s of {pool}s pool ({100*total/pool:.0f}%)")
    if total > pool * POOL_GUARD_FRAC:
        print(f"REFUSING: {total:.0f}s exceeds {POOL_GUARD_FRAC:.0%} of pool")
        return None
    if not submit:
        print("\n[dry run] pass --submit to fly")
        return None

    out = []
    for bname, backend, pubs, meta, est, info in built:
        job = SamplerV2(mode=backend).run(
            [(p, None, m["shots"]) for p, m in zip(pubs, meta)])
        jid = job.job_id()
        print(f"SUBMITTED {bname}: {jid}")
        man = {"card": "armn_delay_sweep", "cycle": "C5018", "substrate": "claude-fable-5",
               "backend": bname, "account": ACCOUNT, "job_id": jid,
               "cal_epoch_at_build": str(backend.properties().last_update_date),
               "gate": GATE, "readout_bar": READOUT_BAR, "D_grid_dt": D_GRID_DT, "chip_incumbent_D0": info["D0"],
               "purpose": "STEP 1 of the forced ordering: fix the witness so it clears the gate",
               "branch_precondition": ("EVERY branch is conditioned on the chip's own witness "
                                       "clearing u>=0.700 in-job at the D in question. A branch "
                                       "that can fire on a failed instrument is a formula, not "
                                       "a pre-registration (C5018 kingston lesson)."),
               "branches": {
                   "a": "some D>=824 clears on kingston -> FIXED with useful drift exposure",
                   "b": "only D<=412 clears -> FIXED at 4x-less exposure; price the signal cost",
                   "c": "no D clears incl. D=0 -> not the idle; shallow_0 is what needs explaining"},
               "secondary": ("kingston:fez absolute loss per idle at EQUAL D. The D grid is "
                             "ABSOLUTE and identical on both chips (dt=4.0ns on each), which "
                             "removes the 1647-vs-1488 mismatch the current 3x claim carries. "
                             "A first version of this script used per-chip fractions and "
                             "reproduced that mismatch; caught in dry run before submission."),
               "tertiary": ("q21/q47 included deliberately: HIGH at every D = block property; "
                            "split only at long D = D-dependent; tracking others = original "
                            "split was noise. Logged as a coincidence IN ADVANCE."),
               "does_not_size_step2": ("N>=30 comes from Ember's f^k arithmetic and is NOT "
                                       "touched by this job's outcome"),
               "cost_est_qpu_s": round(est, 1), "pool_at_build": pool,
               "info": info, "pubs_meta": meta,
               "submit_iso": datetime.datetime.now(datetime.timezone.utc).isoformat()}
        path = os.path.join(RES, f"armn_sweep_manifest_{jid}.json")
        json.dump(man, open(path, "w"), indent=1)
        print(f"  wrote {path}")
        out.append(jid)
    return out


if __name__ == "__main__":
    main(submit="--submit" in sys.argv)
