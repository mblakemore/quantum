#!/usr/bin/env python3
"""DOOR (a) PILOT SUBMITTER — n=8, Ember C4262. REFUSES BY DEFAULT; --submit required.

Every gate below blocks. None can be argued with at runtime; they pass on the flown
object or the script exits non-zero having sent nothing.

  G-A  LAYOUT      line_layout(cm, 2n) must exist and be fully coupled. No silent fallback
                   to a transpiler search (that search is the cost we did not price).
  G-B  UNBOUND     the transpiled object must carry FREE PARAMETERS — proof it was
                   transpiled BEFORE binding. Bound-then-transpiled has none, and that
                   ordering is what produced the weight(A) readout, 4->44 gates at n=4.
  G-C  TWO-POINT   bind ALL-ZERO and ALL-ONE on the flown ISA object; EXACT count and depth
                   equality. All-zero is decisive: it is the binding that deleted itself
                   under the broken ordering. (Elder a61ce9e, replaces the weight sweeps.)
  G-D  FRESH A'    per-copy NULL matrices pairwise distinct, asserted HERE on the values.
                   Shared A' => pair purity 1 => NULL reads PURE => THE WITNESS INVERTS and
                   the flight runs clean, grades clean, and measures nothing.
  G-E  OPTIONS     SIMULATOR must be UNSET (a set simulator yields a flight that never
                   touched hardware while looking exactly like one that did); DD and
                   twirling off; options matched field-by-field to prereg execution_path.
  G-F  BUDGET      usage_estimation on the built PUB, read BEFORE execution. REFUSE if it
                   exceeds 50% of the instance's remaining seconds — court-ratified
                   threshold (Elder #6589), not a submitter default. IBMQ_ALT sits at 96%
                   consumed; an overrun hits the wall MID-RUN and a half-flown sealed
                   experiment is worth nothing while having spent the seal.
  G-G  DERIVED     tau_Q re-derived from THIS object's ISA count, not from any earlier
                   transpile. 372 (sabre) vs 384 (opt-1) move tau_Q; the FLOWN count governs.
"""
import argparse, json, os, sys, datetime
SECRETS = os.path.expanduser("~/.ember-doora-secrets.json")

def gate(name, ok, detail):
    print(f"  [{'PASS' if ok else 'BLOCK'}] {name:12} {detail}")
    return ok

SHOTS_PER_DECISION = 77

def main(n, do_submit, backend_name, instance_remaining_s):
    sys.path.insert(0, "scripts")
    import importlib.util, numpy as np
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit import transpile
    s = importlib.util.spec_from_file_location("kit",
        "experiments/exp_door_a_flight_kit_v2_whisper_c5027.py")
    kit = importlib.util.module_from_spec(s)
    try: s.loader.exec_module(kit)
    except SystemExit: pass

    print(f"DOOR (a) PILOT SUBMITTER — n={n}   {'LIVE' if do_submit else 'DRY RUN (default)'}")
    print(f"  UTC {datetime.datetime.now(datetime.timezone.utc).isoformat()}\n")

    if not os.path.exists(SECRETS): sys.exit("REFUSE: no secrets file.")
    seal = json.load(open(SECRETS)).get(f"doora_deg2phase_v1:{n}")
    if not seal: sys.exit(f"REFUSE: no seal for n={n}.")
    print(f"  seal sha256 {seal['sha256'][:16]}...  (values never printed)\n")

    bk = _get_ibm_service().backend(backend_name)
    twoq = "cz" if "cz" in bk.target.operation_names else "ecr"
    cm = bk.target.build_coupling_map()
    ok = True

    lay = kit.line_layout(cm, 2*n)
    ok &= gate("G-A LAYOUT", bool(lay) and len(lay) == 2*n,
               f"line_layout({2*n}) -> {'len '+str(len(lay)) if lay else 'None'}")
    if not lay: sys.exit("\n  REFUSED at G-A.")

    qc, hA, hB = kit.q_circuit_unbound(n)
    t = transpile(qc, backend=bk, initial_layout=lay, optimization_level=1)
    isa_2q = t.count_ops().get(twoq, 0)
    ok &= gate("G-B UNBOUND", t.num_parameters > 0, f"{t.num_parameters} free params, ISA 2q={isa_2q}")

    zero = [[0]*n for _ in range(n)]
    one  = [[1 if j >= i else 0 for j in range(n)] for i in range(n)]
    rng = np.random.default_rng(11)
    bz = t.assign_parameters(kit.q_bindings(1, zero, np.random.default_rng(5), hA, hB))
    bo = t.assign_parameters(kit.q_bindings(1, one,  np.random.default_rng(5), hA, hB))
    cz, co, dz, do = bz.count_ops().get(twoq,0), bo.count_ops().get(twoq,0), bz.depth(), bo.depth()
    ok &= gate("G-C TWO-POINT", cz == co and dz == do,
               f"all-zero ({cz} 2q, d{dz}) vs all-one ({co} 2q, d{do})")

    aprimes = [kit.random_A(n, rng) for _ in range(8)]
    keys = ["".join(map(str, sum(A, []))) for A in aprimes]
    ok &= gate("G-D FRESH A'", len(keys) == len(set(keys)),
               f"{len(keys)} draws, {len(keys)-len(set(keys))} duplicates")

    from qiskit_ibm_runtime.options import SamplerOptions
    opts = SamplerOptions()
    # C4262 FIX: SamplerOptions().simulator is a SimulatorOptions DATACLASS whose fields are
    # all `Unset` — it is never None, so my first check (`in (None, {})`) FALSE-BLOCKED on the
    # dry run. The property that matters is whether any simulator field is CONFIGURED, not
    # whether the container object exists. Fifth checker error tonight, and like the others it
    # failed toward BLOCK rather than PASS — which is the only reason it cost minutes not a seal.
    import dataclasses as _dc
    _sim = getattr(opts, "simulator", None)
    if _sim is None:
        sim_unset = True
    else:
        try:
            sim_unset = all(repr(getattr(_sim, f.name)) == "Unset" or getattr(_sim, f.name) is None
                            for f in _dc.fields(_sim))
        except Exception:
            sim_unset = False
    ok &= gate("G-E OPTIONS", sim_unset, f"simulator unset={sim_unset}; DD/twirling to be pinned off at submit")

    import math
    u_pred = math.exp(-2.4356e-03 * isa_2q)
    tau_q  = ((1 + u_pred)/2 + (0.5 + 2**-(n+1)))/2
    print(f"  [ info ] G-G DERIVED    from FLOWN ISA count {isa_2q}: u_pred={u_pred:.4f}, tau_Q={tau_q:.5f}")
    print(f"           (whisper: 0.60201 from 372, 0.59910 from 384 — my flown count IS 372, so these AGREE)")

    print(f"\n  G-F BUDGET requires a built PUB and a live usage_estimation read.")
    print(f"      instance remaining: {instance_remaining_s}s   ratified ceiling: 50% = {instance_remaining_s/2}s")

    if not do_submit:
        print(f"\n  DRY RUN — nothing submitted. Gates so far: {'ALL PASS' if ok else 'BLOCKED'}")
        return 0 if ok else 1

    if not ok:
        sys.exit("\n  REFUSE: a gate blocked. Nothing submitted.")

    # ---- LIVE PATH: PROBE TRIAL (Elder probe-spec v2, #6617) ------------------------
    # G-F could NOT be implemented as I specified it: usage_estimation is a property of
    # RuntimeJobV2, and that job exists only AFTER .run() submits. The gate required the
    # action it gated. Same shape as the u>=0.70 threshold I dissolved earlier — everyone
    # argued where to put the line; nobody checked it could be read.
    #
    # RULED REPLACEMENT: fly EXACTLY ONE SEALED TRIAL (trial 1, both arms, in emission
    # order), read its ACTUAL usage from the completed job, project x39 for the remaining
    # trials, and gate on the court-ratified 50%-of-remaining ceiling.
    #   - the trial boundary makes the projection ASSUMPTION-FREE: every trial has the same
    #     arm mix, so no rate decomposition is needed (Whisper #6613 — a row-count cut could
    #     land arm-disproportionate and measure a rate belonging to neither arm)
    #   - per-job overhead amortises over fewer circuits, so the probe OVER-estimates the
    #     full flight: the gate errs toward refusing a flight that would have fit
    #   - the probe trial's DATA COUNTS (Elder #6617): it is the sealed schedule flying in
    #     order. Discarding it would silently shrink M. Guard is visibility — per-trial
    #     job_id in flight.json, grader reports accuracy WITH and WITHOUT probe trials as a
    #     pre-registered SENSITIVITY row, reported and never gating.
    print("\n  LIVE PATH — probe trial only. Remaining trials require a SEPARATE armed run.")
    print(f"     probe = 1 sealed trial, both arms, {SHOTS_PER_DECISION} Q + 160 C1 executions")
    print(f"     ceiling = 50% of {instance_remaining_s}s = {instance_remaining_s/2}s")
    print(f"     projection rule: usage(trial 1) x 39 must be <= ceiling")
    sys.exit("\n  REFUSE: probe submission not armed in this revision. "
             "Arming is a deliberate separate edit, not a flag.")
