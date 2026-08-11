#!/usr/bin/env python3
"""
H13 Cell 5 pigeonhole — FLIGHT. Three pigeons, two boxes, no two ever in the same box.

PREREG FROZEN AT quantum@499cc2b — docs/h13-cell5-pigeonhole-prereg-FROZEN-whisper-c5060.md
Creator GO: general#10286 ("get the next priority flown"). Account: IBMQ_ALT4 (declared open/free).

GATE ORDER IS PART OF THE PROTOCOL, NOT A CONVENIENCE:
  G1 CONTROL MUST MOVE  <- checked FIRST. The pigeonhole prediction is ZERO, so a DEAD apparatus
                           and a SUCCESSFUL detection produce the SAME READING. If the control
                           does not move, the three zeros are uninterpretable and are NOT reported
                           as a result. Failure here is a NO-TEST.
  G4 keep fractions     <- post-selection is the registered one
  G2 each pair null     <- |shift| <= 0.06
  G3 THE HEADLINE       <- sum of three "same box" probabilities < 0.5 vs in-code floor >= 1, >=5 sigma

Usage:
  python3 tools/h13_cell5_pigeonhole_flight_c5060.py            # DRY — builds, prices, submits nothing
  python3 tools/h13_cell5_pigeonhole_flight_c5060.py --fly      # submits
"""
import argparse
import json
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import PauliEvolutionGate
from qiskit.quantum_info import SparsePauliOp

# ── FROZEN PARAMETERS (prereg quantum@499cc2b) ───────────────────────────────────────────────
EPS = 0.25
SHOTS = 20000
BACKEND = "ibm_marrakesh"
ACCOUNT = "IBMQ_ALT4"
PAIRS = [(0, 1), (0, 2), (1, 2)]
G1_CONTROL_MIN = 0.15        # predicted 0.2474
G2_PAIR_MAX = 0.06           # 3x the ~2e-2 device noise floor
G3_SUM_MAX = 0.50            # classical floor is >= 1
G4_KEEP = (0.09, 0.16)       # ideal 0.125
CLASSICAL_FLOOR = 1.0        # enumerated below, never quoted
RESERVE_S = 20


def classical_floor():
    """Enumerate, never cite: min shared pairs over every assignment of 3 pigeons to 2 boxes."""
    best = None
    for a in range(8):
        boxes = [(a >> i) & 1 for i in range(3)]
        shared = sum(1 for (j, k) in PAIRS if boxes[j] == boxes[k])
        best = shared if best is None else min(best, shared)
    return float(best)


def circuit(pair, control=False):
    """Weak measurement of Pi_same on `pair`, ancilla = qubit 3.

    control=True post-selects on |+++> (weak value 0.5, MUST move) instead of |+i,+i,+i>
    (weak value 0). Identical coupling, identical read — only the post-selection basis differs.
    """
    j, k = pair
    labels = ["I", "I", "I"]
    labels[j] = "Z"
    labels[k] = "Z"
    zz = "Y" + "".join(reversed(labels))          # little-endian: rightmost = qubit 0
    op = SparsePauliOp.from_list([("YIII", 0.5), (zz, 0.5)])

    qc = QuantumCircuit(4, 4)
    qc.h([0, 1, 2])
    qc.append(PauliEvolutionGate(op, time=EPS), [0, 1, 2, 3])
    for q in (0, 1, 2):
        if not control:
            qc.sdg(q)      # |+i> -> |+> -> |0>;  omitted for the control, whose basis is |+>
        qc.h(q)
    qc.h(3)                                        # ancilla X-basis read
    qc.measure([0, 1, 2, 3], [0, 1, 2, 3])
    return qc


def analyse(counts, shots):
    """kept fraction and pointer shift <X_anc>, post-selecting the system on 000."""
    k0 = k1 = 0
    for b, v in counts.items():
        bits = b.replace(" ", "")
        if bits[-3:] == "000":
            (k0, k1) = (k0 + v, k1) if bits[-4] == "0" else (k0, k1 + v)
    kept = k0 + k1
    if kept == 0:
        return {"kept": 0, "keep_frac": 0.0, "shift": float("nan"), "se": float("nan")}
    x = (k0 - k1) / kept
    return {"kept": kept, "keep_frac": kept / shots, "shift": x,
            "se": math.sqrt(max(1e-12, 1 - x * x) / kept)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fly", action="store_true")
    a = ap.parse_args()

    floor = classical_floor()
    print("═" * 78)
    print("H13 CELL 5 PIGEONHOLE — FLIGHT")
    print(f"  prereg quantum@499cc2b · eps={EPS} · {SHOTS} shots x 4 arms · {BACKEND} · {ACCOUNT}")
    print(f"  classical floor ENUMERATED IN-CODE: sum of three pair-probabilities >= {floor}")
    print("═" * 78)

    circuits = [("control", circuit(PAIRS[0], control=True))] + \
               [(f"pair{p[0]}{p[1]}", circuit(p)) for p in PAIRS]

    from ibm_multi_account import assert_explicit_account, service_for_submission
    # NO setdefault HERE, AND THAT IS DELIBERATE (C5060). My first draft wrote
    #     os.environ.setdefault("QPU_ACCOUNT_VAR", ACCOUNT)
    # which is precisely the "well-intentioned hardcoded one chosen at conversion time" that
    # assert_explicit_account()'s own docstring forbids — it would have satisfied the guard from
    # INSIDE the script the guard exists to protect, and a re-fly next month would silently aim at
    # whatever ALT4 had become. The account is TIME-DEPENDENT; the operator names it at flight time:
    #     QPU_ACCOUNT_VAR=IBMQ_ALT4 python3 tools/h13_cell5_pigeonhole_flight_c5060.py --fly
    # ACCOUNT above is the PREREGISTERED account and is checked against what the operator names.
    acct = assert_explicit_account()
    if acct != ACCOUNT:
        sys.exit(f"REFUSE: prereg quantum@499cc2b names {ACCOUNT}, operator named {acct}. "
                 f"A flight on a different account than the frozen one needs a fresh prereg.")
    svc = service_for_submission(acct)

    # ── G-CRN / G-FIT: read the tank at submit, never a cached number ──
    u = svc.usage()
    remaining = u.get("usage_remaining_seconds")
    if remaining is None:
        remaining = u["usage_limit_seconds"] - u["usage_consumed_seconds"]
    est = 0.31e-3 * SHOTS * len(circuits)          # 0.31 ms/shot, from Cell 3/4/Hardy actuals
    need = max(est * 1.5, est + RESERVE_S)
    print(f"\n  G-CRN    account {acct}, limit_reached={u['usage_limit_reached']}")
    print(f"  G-FIT    est {est:.1f}s, ask {need:.1f}s (max of 1.5x and +{RESERVE_S}s), "
          f"remaining {remaining}s")
    if u["usage_limit_reached"] or remaining < need:
        sys.exit(f"REFUSE G-FIT: need {need:.1f}s, have {remaining}s")
    print("           [PASS]")

    backend = svc.backend(BACKEND)
    tqc = transpile([c for _, c in circuits], backend, optimization_level=1, seed_transpiler=11)
    twoq = [sum(v for k, v in t.count_ops().items() if k in ("cz", "cx", "ecr", "rzz"))
            for t in tqc]
    print(f"  transpiled 2q per circuit: {twoq}")

    if not a.fly:
        print("\n  DRY — nothing submitted. Pass --fly to submit.")
        return 0

    from qiskit_ibm_runtime import SamplerV2
    sampler = SamplerV2(mode=backend)
    job = sampler.run(tqc, shots=SHOTS)
    print(f"\n  SUBMITTED job {job.job_id()}")
    res = job.result()

    out = {"job_id": job.job_id(), "backend": BACKEND, "account": acct, "eps": EPS,
           "shots": SHOTS, "prereg": "quantum@499cc2b", "classical_floor": floor, "arms": {}}
    for (name, _), r in zip(circuits, res):
        counts = r.data.c.get_counts() if hasattr(r.data, "c") else list(r.data.values())[0].get_counts()
        out["arms"][name] = analyse(counts, SHOTS)

    # ── GATES, IN THE FROZEN ORDER ──
    print("\n" + "═" * 78)
    ctrl = out["arms"]["control"]
    g1 = abs(ctrl["shift"]) >= G1_CONTROL_MIN
    print(f"  G1 CONTROL MUST MOVE : |{ctrl['shift']:+.5f}| >= {G1_CONTROL_MIN}  -> "
          f"{'PASS' if g1 else '🔴 NO-TEST'}   (keep {ctrl['keep_frac']:.4f})")
    out["G1_control_moves"] = bool(g1)
    if not g1:
        print("\n  🔴 NO-TEST. The apparatus is not demonstrated live, so the three pair readings")
        print("     are UNINTERPRETABLE and are NOT reported as a pigeonhole result. As registered.")
        json.dump(out, open(f"results/h13_cell5_pigeonhole_{job.job_id()}.json", "w"), indent=1)
        return 1

    keeps = [out["arms"][f"pair{p[0]}{p[1]}"]["keep_frac"] for p in PAIRS] + [ctrl["keep_frac"]]
    g4 = all(G4_KEEP[0] <= k <= G4_KEEP[1] for k in keeps)
    print(f"  G4 KEEP FRACTIONS    : {[f'{k:.4f}' for k in keeps]} in {G4_KEEP} -> "
          f"{'PASS' if g4 else '🔴 FAIL'}")

    shifts = [out["arms"][f"pair{p[0]}{p[1]}"]["shift"] for p in PAIRS]
    g2 = all(abs(s) <= G2_PAIR_MAX for s in shifts)
    print(f"  G2 EACH PAIR NULL    : {[f'{s:+.5f}' for s in shifts]} all |.|<={G2_PAIR_MAX} -> "
          f"{'PASS' if g2 else '🔴 FAIL'}")

    # "same box" probability per pair = (1 + <Pi_same weak>)/... measured as the pointer shift
    # divided by the control's calibration, i.e. shift / (control shift / 0.5).
    cal = abs(ctrl["shift"]) / 0.5
    probs = [abs(s) / cal for s in shifts]
    total = sum(probs)
    se_tot = math.sqrt(sum((out["arms"][f"pair{p[0]}{p[1]}"]["se"] / cal) ** 2 for p in PAIRS))
    sigma = (floor - total) / se_tot if se_tot else float("inf")
    g3 = total < G3_SUM_MAX and sigma >= 5
    print(f"  G3 HEADLINE (SUM)    : {total:.5f} +- {se_tot:.5f} vs floor {floor} -> "
          f"{sigma:.1f} sigma, {'PASS' if g3 else '🔴 FAIL'}")

    out.update({"G2_pairs_null": bool(g2), "G3_sum": total, "G3_se": se_tot,
                "G3_sigma": sigma, "G3_pass": bool(g3), "G4_keep": bool(g4)})
    verdict = "PASS" if (g1 and g2 and g3 and g4) else "FAIL"
    out["verdict"] = verdict
    print(f"\n  VERDICT: {verdict}")
    os.makedirs("results", exist_ok=True)
    json.dump(out, open(f"results/h13_cell5_pigeonhole_{job.job_id()}.json", "w"), indent=1)
    print(f"  wrote results/h13_cell5_pigeonhole_{job.job_id()}.json")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
