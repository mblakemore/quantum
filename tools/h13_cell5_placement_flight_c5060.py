#!/usr/bin/env python3
"""
H13 Cell 5 — PINNED-PLACEMENT re-fly + PLACEMENT-SENSITIVITY sweep. Boards #113 and #115, one job.

PREREG FROZEN AT quantum@d9983cb — docs/h13-cell5-placement-prereg-FROZEN-whisper-c5060.md
Creator GO: "create board tasks for the 3 (both/and!) and run them".

WHAT THE PRIOR FLIGHT GOT WRONG: no pinned initial_layout, so the transpiler chose per circuit.
Pairs (0,1) and (0,2) landed on [12,13,14,89] and agreed to 4e-4; pair (1,2) landed on [0,1,2,3]
and read the opposite sign. THE PAIR-TO-PAIR COMPARISON *IS* THE CLAIM AND IT WAS CONFOUNDED WITH
QUBIT CHOICE. Every arm here pins its layout explicitly.

SUBMITS AND EXITS — never waits (C5060). A submission is irreversible and an analysis is free;
binding them gave the analysis the submission's failure modes and a queue delay read as a failed
experiment. Grade with h13_cell5_placement_grade_c5060.py whenever it lands.

Usage:
  QPU_ACCOUNT_VAR=IBMQ_ALT4 python3 tools/h13_cell5_placement_flight_c5060.py        # DRY
  QPU_ACCOUNT_VAR=IBMQ_ALT4 python3 tools/h13_cell5_placement_flight_c5060.py --fly
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from qiskit import transpile

# ── FROZEN (prereg quantum@d9983cb) ──────────────────────────────────────────────────────────
EPS = 0.25
SHOTS = 20000
BACKEND = "ibm_marrakesh"
ACCOUNT = "IBMQ_ALT4"
RESERVE_S = 20
FLOWN_A = [12, 13, 14, 89]      # gave +0.09467 / +0.09508
FLOWN_B = [0, 1, 2, 3]          # gave -0.19872


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fly", action="store_true")
    a = ap.parse_args()

    from ibm_multi_account import assert_explicit_account, service_for_submission
    acct = assert_explicit_account()          # operator names it; no setdefault (C5060)
    if acct != ACCOUNT:
        sys.exit(f"REFUSE: prereg names {ACCOUNT}, operator named {acct} — needs a fresh prereg.")
    svc = service_for_submission(acct)

    import quiet_qubits as QQ
    from h13_cell5_pigeonhole_flight_c5060 import circuit, PAIRS, classical_floor
    backend = svc.backend(BACKEND)

    # PICK LIVE, NEVER CACHED (F58/F70) — a cached pick is a stale claim about a drifting device.
    best = QQ.pick(backend, 4, mode="best")
    worst = QQ.pick(backend, 4, mode="worst")

    # ══ ORDERING IS NOT THE SAME AS THE QUBIT SET, AND THE DRY RUN CAUGHT ME (C5060) ═══════════
    # initial_layout pins LOGICAL->PHYSICAL ORDER. My first draft passed the qubit sets in index
    # order; forcing the ancilla onto physical 89 made it non-adjacent to its partners and the
    # router inserted SWAP chains across 18 qubits — 49 two-qubit gates against 7 everywhere else.
    # A comparison between a 49-gate arm and a 7-gate arm measures GATE COUNT, NOT PLACEMENT,
    # which is the same confound one level down from the one this whole flight exists to remove.
    # Orderings below are searched per placement so every arm inside a comparison group is
    # gate-count-EQUAL, and equality is ENFORCED below rather than trusted.
    def order_for(qubits, circs):
        """Ordering minimising (spread, max) of 2q counts over `circs` — equal cost or nothing."""
        import itertools
        bestp = None
        for perm in itertools.permutations(qubits):
            cs = [sum(v for k, v in transpile(c, backend, initial_layout=list(perm),
                                              optimization_level=1, seed_transpiler=11)
                      .count_ops().items() if k in ("cz", "cx", "ecr", "rzz")) for c in circs]
            key = (max(cs) - min(cs), max(cs))
            if bestp is None or key < bestp[0]:
                bestp = (key, list(perm), cs)
        return bestp[1], bestp[2]

    pair_circs = [circuit(p) for p in PAIRS]
    ord_best, cnt_best = order_for(best["qubits"], pair_circs)          # hosts all three pairs
    ord_sweep = {k: order_for(v, [circuit(PAIRS[0])])[0]                # hosts pair01 only
                 for k, v in (("BEST", best["qubits"]), ("WORST", worst["qubits"]),
                              ("flownA", FLOWN_A), ("flownB", FLOWN_B))}
    P = {"BEST": best["qubits"], "WORST": worst["qubits"], "flownA": FLOWN_A, "flownB": FLOWN_B}
    print("═" * 78)
    print("H13 CELL 5 — PINNED PLACEMENT + SENSITIVITY SWEEP")
    print(f"  prereg quantum@d9983cb · eps={EPS} · {SHOTS} shots × 8 arms · {BACKEND} · {ACCOUNT}")
    print(f"  classical floor (in-code): sum of pair probabilities >= {classical_floor()}")
    for k, v in P.items():
        print(f"  {k:7} {v}")
    print(f"  picker scores: best {best['score']:.4f}  worst {worst['score']:.4f}")
    print("═" * 78)

    # ARMS: 4 on BEST (the #113 pinned test), plus pair01 on three more placements (#115 sweep)
    # GROUP A (#113 pinned test): control + all three pairs on ONE placement, ONE ordering.
    # GROUP B (#115 sweep): pair01 across four placements, each at its own pair01-optimal ordering.
    arms  = [("control@BEST", circuit(PAIRS[0], control=True), ord_best, "A")]
    arms += [(f"pair{p[0]}{p[1]}@BEST", circuit(p), ord_best, "A") for p in PAIRS]
    arms += [(f"pair01@{k}", circuit(PAIRS[0]), ord_sweep[k], "B")
             for k in ("BEST", "WORST", "flownA", "flownB")]
    print(f"  ordering for group A (3 pairs equal-cost): {ord_best} -> 2q {cnt_best}")

    # EACH ARM TRANSPILED TO ITS OWN PINNED LAYOUT — the entire point of this flight.
    tqc = [transpile(c, backend, initial_layout=lay, optimization_level=1, seed_transpiler=11)
           for _, c, lay, _ in arms]
    groups = {}
    for (name, _, lay, grp), t in zip(arms, tqc):
        used = sorted({t.find_bit(q).index for inst in t.data for q in inst.qubits})
        n2q = sum(v for k, v in t.count_ops().items() if k in ("cz", "cx", "ecr", "rzz"))
        ok = "OK" if set(used) <= set(lay) else "🔴 LAYOUT NOT HONOURED"
        groups.setdefault(grp, []).append((name, n2q))
        print(f"  [{grp}] {name:16} layout {str(lay):22} 2q {n2q:3d}  {ok}")
        if set(used) > set(lay):
            sys.exit(f"REFUSE: {name} escaped its pinned layout — routing added qubits {used}")

    # ══ ENFORCED, NOT TRUSTED: every arm inside a comparison group must be gate-count EQUAL ══
    for grp, items in groups.items():
        ns = [n for _, n in items]
        if max(ns) != min(ns):
            sys.exit(f"REFUSE: group {grp} arms differ in 2q count {items} — a comparison across "
                     f"unequal circuits measures GATE COUNT, not the variable under test.")
        print(f"  group {grp}: all {len(ns)} arms at {ns[0]} two-qubit gates ✅ comparable")

    u = svc.usage()
    remaining = u.get("usage_remaining_seconds")
    if remaining is None:
        remaining = u["usage_limit_seconds"] - u["usage_consumed_seconds"]
    est = 0.31e-3 * SHOTS * len(arms)
    need = max(est * 1.5, est + RESERVE_S)
    print(f"\n  G-CRN  {acct}, limit_reached={u['usage_limit_reached']}")
    print(f"  G-FIT  est {est:.1f}s, ask {need:.1f}s, remaining {remaining}s")
    if u["usage_limit_reached"] or remaining < need:
        sys.exit(f"REFUSE G-FIT: need {need:.1f}s, have {remaining}s")
    print("         [PASS]")

    if not a.fly:
        print("\n  DRY — nothing submitted. Pass --fly to submit.")
        return 0

    from qiskit_ibm_runtime import SamplerV2
    job = SamplerV2(mode=backend).run(tqc, shots=SHOTS)
    jid = job.job_id()
    print(f"\n  SUBMITTED job {jid}")
    os.makedirs("results", exist_ok=True)
    man = {"job_id": jid, "backend": BACKEND, "account": acct, "eps": EPS, "shots": SHOTS,
           "prereg": "quantum@d9983cb", "arms": [n for n, _, _, _ in arms],
           "ordering_groupA": ord_best, "ordering_sweep": ord_sweep,
           "placements": P, "picker_best_score": best["score"], "picker_worst_score": worst["score"],
           "classical_floor": classical_floor(), "est_qpu_s": round(est, 1)}
    path = f"results/h13_cell5_placement_manifest_{jid}.json"
    json.dump(man, open(path, "w"), indent=1)
    print(f"  wrote {path}")
    print(f"\n  NOT WAITING. Grade when it lands:")
    print(f"    QPU_ACCOUNT_VAR={acct} python3 tools/h13_cell5_placement_grade_c5060.py {jid}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
