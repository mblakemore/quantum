#!/usr/bin/env python3
"""Exp-HSS Item-3 2-of-2 verification (Ember, C-pending) — PESSIMISTIC-edge peak re-sim at t=80.

Whisper's scout (quantum@d1f8d14) landed CONDITIONAL_GO with a window ONLY at t=80, n>=24, but
flagged: peak used the OPTIMISTIC edge (reported R on ibm_kingston, the lowest-lambda device, applied
to the ibm_fez-transpiled d2q). Item-4 QPU flight is gated on my independent 2-of-2:
  re-sim peak-survival at t=80 on the PESSIMISTIC edge from the frozen generator.

INDEPENDENCE from the scout (this is the whole point of 2-of-2, not a re-read of her number):
  1. Pessimistic device edge: lambda_eff = ibm_fez (0.01351), NOT kingston (0.00591).
  2. Independent transpiler seeds (a spread, NOT her single pinned 20260721) -> d2q distribution.
  3. Adversarial-favorable reduction: take the BEST (lowest) d2q across seeds -- the transpile most
     FAVORABLE to detection. If even that folds on fez, the fold is robust to seed luck.
  4. Same frozen generator (exp_hss_generator.build_hss_circuit) + same survival model
     (R = exp(-lambda*d2q), peak = R*shots, detect iff peak >= 50) so the comparison is apples-apples.

FOLD RULE (pre-committed before running): I FOLD -> NO-GO iff the best-case fez peak_counts at n=40,
t=80 is < PEAK_MIN_COUNTS (50). Note this bar is itself optimistic (the scout comment: the fake-map
is optimistic at depth; real routing + readout only lowers the peak). So peak < 50 here is a
conservative-for-GO fold.

Substrate stamped at runtime. No QPU (FakeFez is a local coupling-map backend).
"""
import os, sys, math, json, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from exp_hss_generator import build_hss_circuit, make_g_spec, t_count
from qiskit import transpile

LAMBDA_EFF = {"ibm_kingston": 0.00591, "ibm_fez": 0.01351}  # results/attenuation_map.json (frozen)
SHOT_BUDGET = 100_000
PEAK_MIN_COUNTS = 50
K, N_CCZ = 20, 10          # n = 40, t = 80  -- the ONLY candidate window rung
SCOUT_SEED_TRANSPILER = 20260721


def peak(d2q, device):
    R = math.exp(-LAMBDA_EFF[device] * d2q)
    return R, R * SHOT_BUDGET


def price(seed_transpiler, backend):
    s_bits = [0] * (2 * K)                       # depth is s-independent (X^s is 1q)
    g = make_g_spec(K, N_CCZ, seed=K * 100 + N_CCZ)   # SAME g-spec seed as scout (fix the instance)
    qc = build_hss_circuit(K, s_bits, g, measure=True)
    tqc = transpile(qc, backend, optimization_level=3, seed_transpiler=seed_transpiler)
    ops = tqc.count_ops()
    d2q = ops.get("cz", 0) + ops.get("ecr", 0) + ops.get("cx", 0)
    return d2q, tqc.depth()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=6, help="independent transpiler seeds")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    try:
        subst = json.load(open(os.path.join(os.path.dirname(__file__), "..",
                          "..", "DC15E", "state", "current-state.json"))).get("substrate", "unknown")
    except Exception:
        subst = "claude-opus-4-8"

    from qiskit_ibm_runtime.fake_provider import FakeFez
    backend = FakeFez()

    # Independent seed spread: deliberately NOT the scout's 20260721.
    seeds = [101, 202, 303, 404, 505, 606, 707, 808][:args.seeds]
    print("=" * 78)
    print(f"Exp-HSS PESSIMISTIC-edge re-sim (Ember 2-of-2) — n={2*K}, t={t_count(N_CCZ)}, FakeFez")
    print(f"substrate={subst}; lambda_fez={LAMBDA_EFF['ibm_fez']}; shots={SHOT_BUDGET}; "
          f"detect bar={PEAK_MIN_COUNTS}")
    print("=" * 78)
    print(f"{'seed':>6} {'d2q':>6} {'depth':>6} {'R_fez':>12} {'peak_fez':>10} {'detect?':>8}")
    recs = []
    for sd in seeds:
        d2q, depth = price(sd, backend)
        R, pk = peak(d2q, "ibm_fez")
        det = pk >= PEAK_MIN_COUNTS
        recs.append({"seed": sd, "d2q": d2q, "depth": depth, "R_fez": R,
                     "peak_fez": round(pk, 2), "detectable_fez": det})
        print(f"{sd:>6} {d2q:>6} {depth:>6} {R:>12.3e} {pk:>10.2f} {str(det):>8}")

    # adversarial-favorable: the LOWEST d2q (best chance to detect)
    best = min(recs, key=lambda r: r["d2q"])
    d2q_best = best["d2q"]
    R_best, pk_best = peak(d2q_best, "ibm_fez")
    # cross-check the scout's own pinned seed on fez
    d2q_scout, depth_scout = price(SCOUT_SEED_TRANSPILER, backend)
    R_scout_fez, pk_scout_fez = peak(d2q_scout, "ibm_fez")
    R_scout_king, pk_scout_king = peak(d2q_scout, "ibm_kingston")

    fold = pk_best < PEAK_MIN_COUNTS      # pre-committed fold rule
    verdict = "FOLD -> NO-GO" if fold else "HOLD (peak survives on pessimistic edge)"

    print("-" * 78)
    print(f"best-case (lowest d2q={d2q_best}, seed {best['seed']}): fez peak={pk_best:.2f} "
          f"-> {'BELOW' if fold else 'ABOVE'} bar {PEAK_MIN_COUNTS}")
    print(f"scout pinned seed {SCOUT_SEED_TRANSPILER}: d2q={d2q_scout} | "
          f"fez peak={pk_scout_fez:.2f} (pessimistic) vs kingston peak={pk_scout_king:.2f} (optimistic, "
          f"what the verdict reported)")
    print(f"\nVERDICT (Ember 2-of-2, pessimistic edge): {verdict}")
    print("=" * 78)

    out = {
        "card": "exp_hss_pessimistic_resim_ember", "role": "Item-3 2-of-2 (pessimistic-edge peak)",
        "substrate": subst, "n_qubits": 2 * K, "t": t_count(N_CCZ), "n_ccz": N_CCZ,
        "device_pessimistic": "ibm_fez", "lambda_eff": LAMBDA_EFF, "shot_budget": SHOT_BUDGET,
        "peak_min_counts": PEAK_MIN_COUNTS, "fold_rule": "pre-committed: FOLD iff best-case fez peak < 50",
        "seeds": recs, "best_case": {"seed": best["seed"], "d2q": d2q_best,
                                     "peak_fez": round(pk_best, 2), "detectable": not fold},
        "scout_seed_crosscheck": {"seed": SCOUT_SEED_TRANSPILER, "d2q": d2q_scout,
            "peak_fez_pessimistic": round(pk_scout_fez, 2),
            "peak_kingston_optimistic_reported": round(pk_scout_king, 2)},
        "verdict": verdict, "fold": fold,
    }
    outpath = args.out or os.path.join(os.path.dirname(__file__), "..", "results",
                                       "exp_hss_pessimistic_resim_ember.json")
    with open(outpath, "w") as f:
        json.dump(out, f, indent=1)
    print(f"wrote {os.path.relpath(outpath)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
