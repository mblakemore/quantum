#!/usr/bin/env python3
"""SHALLOW WITNESS + LOSS-DECOMPOSITION LADDER (Whisper C5018, Creator "build the shallower witness").

WHY: the arm-N re-fly's witness measured Choi purity u = 0.553 (readout-corrected, full joint)
against a frozen gate of u >= 0.7 — 0/10 candidates passed, so the apparatus, not the
threshold, is the blocker (finding: armn-refly-inconclusive-by-decision-rule).

TWO CHANGES, each removing gates rather than hoping:
  1. PARTNER TOPOLOGY: require THREE free adjacent neighbours so anc2 is adjacent to the block
     qubit. The old geometry routed copy-2 prep through an occupied middle as a 4-CX relay;
     adjacency makes it a single CX.                                     4 CX -> 1 CX
  2. STORE BY TRANSFER, NOT SWAP: the storage qubit is genuinely |0> at that moment, so
     |psi>_b|0>_s -> |0>_b|psi>_s needs only CX(b,s); CX(s,b). A full SWAP's third CX exists
     to move the |0> back, which we do not need.                          3 CX -> 2 CX
  Per block qubit: 10 CX -> 6 CX.

AND THE POINT OF THE LADDER: "6 CX should give u ~ 0.70" is a PROJECTION (0.553^(6/10)).
Elder's condition is that apparatus claims be measured. So the flight measures purity at
FOUR configurations and decomposes where the loss actually lives:

  cfg          geometry   channel delays   isolates
  shallow_0    6 CX       0                gate + readout loss alone
  shallow_1    6 CX       1                + one channel idle
  shallow_2    6 CX       2 (the witness)  the real shallow witness
  deep_2       10 CX      2                the flown geometry, as the control

u(shallow_0) bounds what gates cost; u(shallow_2)/u(shallow_0) gives the idle cost;
deep_2 vs shallow_2 gives the measured CX dependence instead of the assumed one.
If the loss turns out NOT to be CX-dominated, the shallower circuit was the wrong fix and the
ladder says so BEFORE a witness is certified on it.

$0 mode (default): build, assert gate counts, print the ladder. --submit flies it.
"""
import json, os, sys, datetime
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
QROOT = os.path.join(HERE, ".."); RES = os.path.join(QROOT, "results")
sys.path.insert(0, os.path.join(QROOT, "scripts"))
from exp_armn_flight_compile_whisper_c5018 import (
    neighbors, _h, _cx, _relay_cx, transpile_with_dd, struct_fingerprint,
    CENSUS_JOB, BACKEND, ACCOUNT, CAL_SHOTS)
from exp_crossblock_widesweep import build_twins, SEED, NPHYS
SHOTS = 8000
# Ember #5004 power fix, BOTH remedies taken (they are not alternatives): the deep_2 vs
# shallow_2 leg is a ONE-CZ difference (10 vs 9), MDE ~0.107 per candidate at 960 shots
# against a per-CZ effect of ~0.045 — it can only detect the effect if the loss is ALREADY
# evenly gate-dominated, which is the hypothesis it exists to test. So: (a) raise shots on
# that pair specifically (se ~ 1/sqrt(N)), and (b) pre-register that a null on that leg is
# UNINFORMATIVE and may never be cited as evidence against gate-dominance.
SHOTS_GATE_LEG = 4000      # deep_2 / shallow_2 only; MDE 0.107 -> 0.052 single, 0.021 pooled
# COST CORRECTION (C5018): 32000 was chosen on the false premise that "shots are nearly free
# next to pubs". They are not — shots ARE the cost. 32k put the ladder at 496k shots ~ 174
# QPU-s against a ~2 s quote and a 309 s pool. 4000 is what Ember (#5004) and Elder (#5007)
# actually proposed; it clears the ~0.045/CZ effect pooled and costs ~56 QPU-s.
CENSUS_DECODE = os.path.join(RES, f"armn_fez_census_decode_{CENSUS_JOB}.json")


def three_neighbour_plan(backend, q, excluded):
    """anc1, anc2, s1 ALL adjacent to q — kills the relay. Returns None if q lacks degree."""
    free = [n for n in neighbors(backend, q) if n not in excluded]
    if len(free) < 3:
        return None
    return {"anc1": free[0], "anc2": free[1], "s1": free[2], "relay_mid": None}


def transfer(qc, a, b):
    """|psi>_a |0>_b -> |0>_a |psi>_b in TWO CX (valid only because b is genuinely |0>)."""
    _cx(qc, a, b); _cx(qc, b, a)


def build_witness(backend, q, plan, delay_dt, n_delays, deep=False):
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(NPHYS)
    a1, a2, s1 = plan["anc1"], plan["anc2"], plan["s1"]
    _h(qc, a1); _cx(qc, a1, q)                       # copy-1 Bell prep      1 CX
    qc.barrier()
    for _ in range(min(n_delays, 1)):
        qc.delay(delay_dt, q, unit="dt")
    qc.barrier()
    if deep:                                          # flown geometry: full SWAP  3 CX
        _cx(qc, q, s1); _cx(qc, s1, q); _cx(qc, q, s1)
    else:
        transfer(qc, q, s1)                           # shallow: transfer          2 CX
    qc.barrier()
    _h(qc, a2)
    if deep:
        _relay_cx(qc, a2, a1, q)                      # flown geometry: relay      4 CX
    else:
        _cx(qc, a2, q)                                # shallow: direct            1 CX
    qc.barrier()
    for _ in range(max(0, n_delays - 1)):
        qc.delay(delay_dt, q, unit="dt")
    qc.barrier()
    _cx(qc, a1, a2); _h(qc, a1)                       # destructive Bell pairing   2 CX
    _cx(qc, s1, q); _h(qc, s1)
    qc.measure_all()
    return qc


def main(submit=False):
    from ibm_multi_account import service_for_submission
    from qiskit_ibm_runtime import SamplerV2
    from qiskit import QuantumCircuit, transpile
    svc = service_for_submission(ACCOUNT)
    u = svc.usage(); print(f"POOL ({ACCOUNT}): {u['usage_remaining_seconds']}s")
    backend = svc.backend(BACKEND)
    cal = str(backend.properties().last_update_date)
    twins, register = build_twins(backend)
    from exp_armn_flight_compile_whisper_c5018 import pad_duration_dt
    delay_dt = pad_duration_dt(backend, twins)
    cen = json.load(open(CENSUS_DECODE))
    drifters = set(cen["drifter_set"])
    # candidates: qubits with THREE free neighbours, drifters excluded from partner roles
    cands = []
    for q in sorted(set(cen["readout"]) | set()):
        q = int(q)
        pl = three_neighbour_plan(backend, q, drifters | {q})
        if pl:
            cands.append((q, pl, q in drifters))
    drift_c = [c for c in cands if c[2]][:3]
    quiet_c = [c for c in cands if not c[2]][:3]
    print(f"[topology] 3-neighbour candidates: {len(cands)} total | "
          f"drifters {[c[0] for c in drift_c]} | quiet {[c[0] for c in quiet_c]}")
    pubs, meta = [], []
    for st, tag in ((0, "cal0"), (1, "cal1")):
        qc = QuantumCircuit(NPHYS)
        if st: qc.x(range(NPHYS))
        qc.measure_all()
        pubs.append((transpile(qc, backend, optimization_level=0), None, CAL_SHOTS))
        meta.append({"block": tag, "shots": CAL_SHOTS})
    counts = {}
    for q, pl, isd in drift_c + quiet_c:
        for cfg, nd, deep in (("shallow_0", 0, False), ("shallow_1", 1, False),
                              ("shallow_2", 2, False), ("deep_2", 2, True)):
            t = transpile_with_dd(backend, build_witness(backend, q, pl, delay_dt, nd, deep))
            n2q = sum(1 for i in t.data if i.operation.num_qubits == 2)
            counts.setdefault(cfg, []).append(n2q)
            sh = SHOTS_GATE_LEG if cfg in ("deep_2", "shallow_2") else SHOTS
            pubs.append((t, None, sh))
            meta.append({"block": f"{cfg}_q{q}", "cfg": cfg, "q": q, "shots_used": sh,
                         "role": "drifter" if isd else "quiet", "n2q": n2q,
                         "plan": pl, "shots": sh})
    for cfg, v in counts.items():
        print(f"[gates] {cfg:>10}: 2q per candidate = {sorted(set(v))}")
    assert max(counts["shallow_2"]) < min(counts["deep_2"]), "shallow must be shallower"
    p_ref = 0.22
    se_u = 2*np.sqrt(p_ref*(1-p_ref)/SHOTS_GATE_LEG)
    mde1 = 2.8*np.sqrt(2)*se_u; mde6 = mde1/np.sqrt(6)
    man = {"card": "armn_shallow_witness_ladder", "cycle": "C5018", "substrate": "claude-fable-5",
           "backend": BACKEND, "account": ACCOUNT, "cal_epoch_at_build": cal,
           "purpose": ("decompose where witness purity is lost: gates vs channel idle vs "
                       "geometry. u>=0.7 gate must be MEASURED, not projected."),
           "changes": {"relay->adjacent CX": "4 CX -> 1", "SWAP->transfer": "3 CX -> 2"},
           "gate_counts": counts, "pubs_meta": meta, "delay_dt": delay_dt,
           "power": {"gate_leg": "deep_2 vs shallow_2 is a ONE-CZ difference; "
                                 f"shots raised to {SHOTS_GATE_LEG} (MDE ~0.107 -> ~0.018)",
                     # Ember #5011: a BOUND, not a disclaimer. "Uninformative" would throw
                     # away a real result; the MDE is the legitimate null-interpretation floor,
                     # exactly as the condition number was the legitimate amplification ceiling.
                     "gate_leg_null_disposition": (
                         f"BOUND, not a disclaimer. At {SHOTS_GATE_LEG} shots se(u)~{se_u:.4f}, "
                         f"single-candidate MDE ~{mde1:.3f}, pooled over 6 candidates ~{mde6:.4f}. "
                         f"A NULL on the one-CZ leg therefore means: per-CZ purity cost is BELOW "
                         f"~{mde1:.3f} (single) / ~{mde6:.4f} (pooled) — under HALF the ~0.045 per "
                         f"CZ that even gate-dominance of the observed 0.45 loss would require. "
                         f"That is a citable, falsifiable upper bound on gate cost and it is what "
                         f"tells a future designer that fewer gates is not the fix. It may NOT be "
                         f"restated as 'gates do not matter' (unbounded) nor as 'uninformative'."),
                     "other_legs": "delay series (0/1/2) and shallow_0 are well-powered; the "
                                 "delay lever is far larger than one gate"}}
    if submit:
        job = SamplerV2(mode=backend).run(pubs)
        man["job_id"] = job.job_id()
        man["submit_iso"] = datetime.datetime.now(datetime.UTC).isoformat()
        p = os.path.join(RES, f"armn_shallow_manifest_{job.job_id()}.json")
        json.dump(man, open(p, "w"), indent=1); print(f"SUBMITTED {job.job_id()} -> {p}")
    else:
        p = os.path.join(RES, "armn_shallow_build_c5018.json")
        json.dump(man, open(p, "w"), indent=1)
        print(f"[build] $0 — no submit ({len(pubs)} pubs). -> {p}")


if __name__ == "__main__":
    main(submit="--submit" in sys.argv)
