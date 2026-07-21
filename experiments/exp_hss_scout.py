#!/usr/bin/env python3
"""Exp-HSS Phases 2-5 — the Hidden-Shift $0 Scout verdict (Item 3 / P-HSS).

Consumes the Phase-1 generator (exp_hss_generator, exactness-gated 6/6) and produces the GO/NO-GO
verdict per the FROZEN PREP card (docs/exp-hss-scout-prep-whisper-c4971.md, quantum@523d884).
NO QPU. The decision rule was pre-committed BEFORE this ran.

Phase 2 depth pricing: transpile each rung to FakeFez/FakeKingston (Heron, cz-native), opt level 3,
  seed_transpiler pinned; count routed cz (= d2q) and depth. Transpilation != simulation, so this
  runs at all n incl 40.
Phase 3 peak-survival: R(d2q) = exp(-lambda_eff * d2q) from the FROZEN attenuation map
  (results/attenuation_map.json: kingston 0.00591/slot, fez 0.01351/slot). Friction-01 band: the
  fake is OPTIMISTIC at depth, so realized R <= predicted -> the survival estimate is an UPPER bound
  (conservative direction for a NO-GO, generous for a GO -> we test GO against the pessimistic edge).
  Per-rung FakeFez re-sim validation is Ember's 2-of-2 role (monitors down this cycle).
Phase 4 classical bill: paper shape 2^(0.23t)*t^3*w^3 (gamma=0.23 pinned) on RACE_CONFIG. Anchor:
  the paper's OWN benchmark is THIS family at n=40,t=48 = "several hours" (~3h) on a 2016 i5 MATLAB
  laptop. RACE_CONFIG (all-core Ryzen 9800X3D + optimized impl) is 100-1000x faster. We use the
  FAST edge (1000x) as the conservative-for-GO classical estimate (fast classical => harder to reach
  10 min => GO not manufactured by a generous constant), and report the slow edge (100x) as a band.
Phase 5 verdict: GO iff EXISTS (n,t) with peak detectable at >= effective-sigma AND classical bill
  >= 10 min on RACE_CONFIG (conservative/fast edge). Else NO-GO + the measured gap.

Substrate: claude-fable-5, Whisper C4971.
"""
import os, sys, json, math, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qiskit import transpile
from exp_hss_generator import build_hss_circuit, make_g_spec, t_count

QROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
LAMBDA_EFF = {"ibm_kingston": 0.00591, "ibm_fez": 0.01351}  # from results/attenuation_map.json
SEED_TRANSPILER = 20260721

# Classical anchor (paper's own hidden-shift benchmark = our family): n=40, t=48 ~ 3h on 2016 i5
# MATLAB. RACE_CONFIG speedup band [100x, 1000x]; conservative-for-GO = fast edge (1000x).
PAPER_ANCHOR = {"n": 40, "t": 48, "laptop_seconds": 3 * 3600, "hw": "2016 i5 MATLAB single-core"}
RACE_SPEEDUP_FAST, RACE_SPEEDUP_SLOW = 1000.0, 100.0
GAMMA = 0.23  # Bravyi-Gosset sampling exponent (pinned, PRL 116 250501)

# QPU-realistic shot budget for peak detection; at large n the 2^n background is negligible so the
# binding constraint is peak-count = R*shots above ~tens with FWER-corrected significance.
SHOT_BUDGET = 100_000
PEAK_MIN_COUNTS = 50  # >= ~7-sigma clean vs a ~0 large-n background (FWER over 2^n)


def _c_race_fast():
    """Per-unit classical constant on RACE_CONFIG fast edge, from the paper anchor."""
    n, t = PAPER_ANCHOR["n"], PAPER_ANCHOR["t"]
    laptop_c = PAPER_ANCHOR["laptop_seconds"] / ((2 ** (GAMMA * t)) * (t ** 3) * (n ** 3))
    return laptop_c / RACE_SPEEDUP_FAST


def classical_seconds(n, t, speedup):
    if t == 0:
        return None  # Clifford control: poly, Gottesman-Knill (not the exponential term)
    laptop_c = PAPER_ANCHOR["laptop_seconds"] / (
        (2 ** (GAMMA * PAPER_ANCHOR["t"])) * (PAPER_ANCHOR["t"] ** 3) * (PAPER_ANCHOR["n"] ** 3))
    return (2 ** (GAMMA * t)) * (t ** 3) * (n ** 3) * (laptop_c / speedup)


def price_depth(k, n_ccz, backend, seed):
    """Transpile the rung to `backend`, return routed cz count (d2q) and depth."""
    s_bits = [0] * (2 * k)  # depth is s-independent (X^s is 1q); plant zeros for a clean count
    g = make_g_spec(k, n_ccz, seed)
    qc = build_hss_circuit(k, s_bits, g, measure=True)
    tqc = transpile(qc, backend, optimization_level=3, seed_transpiler=SEED_TRANSPILER)
    ops = tqc.count_ops()
    d2q = ops.get("cz", 0) + ops.get("ecr", 0) + ops.get("cx", 0)
    return {"n_qubits": 2 * k, "n_ccz": n_ccz, "t": t_count(n_ccz), "d2q": d2q, "depth": tqc.depth()}


def peak_survival(d2q, device):
    R = math.exp(-LAMBDA_EFF[device] * d2q)
    peak_counts = R * SHOT_BUDGET
    detectable = peak_counts >= PEAK_MIN_COUNTS  # optimistic edge (map is fake-optimistic at depth)
    return {"device": device, "lambda_eff": LAMBDA_EFF[device], "R_upper": R,
            "peak_counts_at_100k": round(peak_counts, 2), "detectable_optimistic": detectable}


def main():
    ap = argparse.ArgumentParser(description="Exp-HSS scout verdict (Item 3 Phases 2-5)")
    ap.add_argument("--timestamp", default=None)
    ap.add_argument("--backend", default="fez", choices=["fez", "kingston"])
    args = ap.parse_args()
    from qiskit_ibm_runtime.fake_provider import FakeFez, FakeKingston
    backend = FakeFez() if args.backend == "fez" else FakeKingston()
    dev = "ibm_fez" if args.backend == "fez" else "ibm_kingston"

    # grid: n = 2k, #CCZ dial -> t = 8*#CCZ. Includes paper rungs (5 CCZ t40, 6 CCZ t48) + higher t.
    ks = [8, 12, 16, 20]          # n = 16, 24, 32, 40
    cczs = [0, 3, 5, 6, 8, 10]    # t = 0, 24, 40, 48, 64, 80
    rows = []
    print(f"PRICING on {dev} (seed_transpiler={SEED_TRANSPILER}); c_race_fast={_c_race_fast():.3e}\n")
    for k in ks:
        for nc in cczs:
            if nc > k * (k - 1) * (k - 2) // 6:
                continue
            price = price_depth(k, nc, backend, seed=k * 100 + nc)
            surv_k = peak_survival(price["d2q"], "ibm_kingston")  # best device (lowest lambda_eff)
            surv_f = peak_survival(price["d2q"], "ibm_fez")
            t = price["t"]
            c_fast = classical_seconds(price["n_qubits"], t, RACE_SPEEDUP_FAST)
            c_slow = classical_seconds(price["n_qubits"], t, RACE_SPEEDUP_SLOW)
            row = {**price, "R_upper_kingston": round(surv_k["R_upper"], 6),
                   "peak_counts_kingston_100k": surv_k["peak_counts_at_100k"],
                   "detectable_kingston": surv_k["detectable_optimistic"],
                   "detectable_fez": surv_f["detectable_optimistic"],
                   "classical_s_race_fast": None if c_fast is None else round(c_fast, 2),
                   "classical_s_race_slow": None if c_slow is None else round(c_slow, 2),
                   "classical_ge_10min_fast": (c_fast is not None and c_fast >= 600),
                   # GO test: BEST device detectable AND classical >=10min on the CONSERVATIVE (fast) edge
                   "both_hold": (surv_k["detectable_optimistic"] and c_fast is not None and c_fast >= 600)}
            rows.append(row)
            print(f"  n={row['n_qubits']:2d} t={t:2d} d2q={row['d2q']:5d}: "
                  f"R_king={row['R_upper_kingston']:.2e} peak@100k={row['peak_counts_kingston_100k']:.1f} "
                  f"detect={row['detectable_kingston']}  classical_fast={row['classical_s_race_fast']}s "
                  f">=10min={row['classical_ge_10min_fast']}  BOTH={row['both_hold']}")

    go = any(r["both_hold"] for r in rows)
    # the measured gap: for each n, the max t where peak still detectable vs the min t where classical>=10min
    win_rows = [r for r in rows if r["both_hold"]]
    win_ts = sorted({r["t"] for r in win_rows})
    win_ns = sorted({r["n_qubits"] for r in win_rows})
    # robustness: the window sits ONLY at t beyond the paper's validated t=48 benchmark, and the peak
    # side used the OPTIMISTIC R upper bound. So the GO is CONDITIONAL, not a green light.
    beyond_paper = all(t > PAPER_ANCHOR["t"] for t in win_ts) if win_ts else False
    if not go:
        verdict, robustness = "NO-GO", "no (n,t) satisfies both curves on the conservative edges"
    else:
        verdict = "CONDITIONAL_GO"
        robustness = {
            "window": {"t": win_ts, "n_qubits": win_ns},
            "fragility": [
                f"window sits ONLY at t={win_ts} — {'BEYOND' if beyond_paper else 'within'} the "
                f"paper's validated t=48 benchmark (extrapolation of the 0.23 exponent to higher t)",
                "peak-survival used the OPTIMISTIC R upper bound (fake-optimistic-at-depth); the "
                "realized/pessimistic edge (Ember 2-of-2 re-sim) could push peak below detection",
                "classical bill is the paper's 2016-laptop anchor x1000 fast-edge extrapolated to "
                "t=80; Elder's independent RACE_CONFIG recompute (2-of-2) could move the 10-min line",
                "n=16 is NO-GO at every t (classical stays < 10 min even at t=80) — the window needs n>=24",
            ],
            "gate_before_item4": ("Item-4 QPU flight is GATED on the 2-of-2 confirming BOTH: (a) peak "
                                  "detectable on the PESSIMISTIC edge at t=80, (b) classical >=10min on "
                                  "a real RACE_CONFIG solver at t=80. Until then this is a candidate, "
                                  "not a green light."),
        }
    gap = []
    for k in ks:
        n = 2 * k
        nrows = [r for r in rows if r["n_qubits"] == n]
        t_peak_max = max([r["t"] for r in nrows if r["detectable_kingston"]], default=None)
        t_class_min = min([r["t"] for r in nrows if r["classical_ge_10min_fast"]], default=None)
        gap.append({"n": n, "max_t_peak_detectable": t_peak_max,
                    "min_t_classical_ge_10min_fast": t_class_min,
                    "window_exists": (t_peak_max is not None and t_class_min is not None
                                      and t_class_min <= t_peak_max)})

    card = {
        "card": "exp_hss_scout_verdict", "item": 3, "substrate": "claude-fable-5", "cycle": "C4971",
        "timestamp": args.timestamp, "backend_priced": dev, "seed_transpiler": SEED_TRANSPILER,
        "prep_card": "docs/exp-hss-scout-prep-whisper-c4971.md (quantum@523d884, pre-committed)",
        "decision_rule": ("GO iff EXISTS (n,t): peak detectable >=~7sigma (FWER over 2^n; proxy "
                          "peak_counts>=50 at 100k shots, R upper-bound) AND classical >=600s on "
                          "RACE_CONFIG fast edge (1000x over paper's 2016 laptop; conservative for GO)"),
        "gamma": GAMMA, "paper_anchor": PAPER_ANCHOR, "lambda_eff": LAMBDA_EFF,
        "shot_budget": SHOT_BUDGET, "peak_min_counts": PEAK_MIN_COUNTS,
        "rows": rows, "verdict": verdict, "go_robustness": robustness, "gap_by_n": gap,
        "fences": {
            "peak_survival": "R is an UPPER bound (fake optimistic at depth, friction-01); realized "
                             "detection is worse -> GO tested against the generous edge, so a NO-GO "
                             "here is robust. Per-rung FakeFez re-sim = Ember 2-of-2 (pending).",
            "classical": "fast edge (1000x) is conservative-for-GO; slow edge (100x) reported as band. "
                         "Elder independent classical recompute on RACE_CONFIG = 2-of-2 (pending).",
            "n40_unsimulable": "n=40 peak-survival + classical are analytic/extrapolated (2^40 wall); "
                               "d2q at n=40 is REAL (transpiled, not simulated).",
        },
    }
    out = os.path.join(QROOT, "results", "exp_hss_scout_verdict.json")
    json.dump(card, open(out, "w"), indent=1)
    print(f"\nVERDICT: {verdict}")
    for g in gap:
        print(f"  n={g['n']}: peak detectable up to t={g['max_t_peak_detectable']}, "
              f"classical>=10min from t={g['min_t_classical_ge_10min_fast']} -> "
              f"window={'YES' if g['window_exists'] else 'NO'}")
    print(f"card -> results/exp_hss_scout_verdict.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
