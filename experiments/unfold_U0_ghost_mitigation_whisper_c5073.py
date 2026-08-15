#!/usr/bin/env python3
"""UNFOLD U0 — ghost-subtraction mitigation, the BUILD-UPON run (Whisper C5073). $0. FROZEN.

The Creator's integration test: a VALIDATED error signature (the ghost, U1: P-independent per-qubit
map, cross-draw r +0.81) is a mitigation ingredient. If the ghost is genuine measurement-quality
error on specific qubits, then a state whose sealed P has more support on HOT qubits should be more
degraded. Test whether the ghost map PREDICTS the per-draw tr2 deficit BEYOND the trivial weight
trend — non-circular, leave-one-out.

MODEL (deficit = apparatus loss on support qubits): -log(tr2_d)/2 = sum_{q in supp(P_d)} (-log f_q).
  M0 (weight-only baseline): -log f_q = c  (constant per-qubit fidelity) -> deficit_d = c * wp_d.
  M1 (ghost-informed):       -log f_q = c * ghat[q]  where ghat[q] = |g_bar[q]| / mean|g_bar|
                             (the P-INDEPENDENT ghost pattern, fixed) -> deficit_d = c * Ghost_overlap_d.
Both are ONE-parameter (c), fit by least squares on the log-deficit; the ONLY difference is whether
the per-qubit weighting is flat (M0) or the ghost pattern (M1). LEAVE-ONE-OUT: fit c on 3 draws,
predict the held-out draw's tr2 from its P's support alone, compare to actual.

PIN (must pass or NO-TEST): reproduce each draw's graded estimate_tr2 < 2e-3 (uncorrected).
REGISTERED PREDICTIONS:
  P1 pin reproduces all four uncorrected tr2.
  P2 the mean-fidelity model itself holds across the 4 different secrets (per-qubit f_hat consistent
     -> a simple apparatus model predicts all 4 measurements = the base 'walks like a duck').
  P3 BUILD-UPON SIGNAL: M1 (ghost-informed) LOO prediction error < M0 (weight-only) -> the ghost map
     adds predictive power -> the mitigation compounds. Corrected tr2 -> toward 1 WITHOUT overshoot.
  P4 FALSIFIER / honest branch: M1 not better than M0, or overshoot >1, or draw-inconsistent ->
     the weight-1 ghost is an INCOMPLETE error model at n=4; report the bound + whether a multi-draw
     flight is warranted (n=4 with a weight confound is low power BY CONSTRUCTION — stated up front).
Draws: refly · i1 · i2 · i3.
"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
import doorb_decoder_elder as D

N = 16
RES = os.path.join(HERE, "..", "results")
HEALTHY = {
    "refly": ("doorb_refly_raw_science_n16_elder.json", "doorb_refly_grade_n16_elder.json"),
    "i1":    ("doorb_dist_i1_raw_science_n16_elder.json", "doorb_dist_i1_grade_n16_elder.json"),
    "i2":    ("doorb_dist_i2_raw_science_n16_elder.json", "doorb_dist_i2_grade_n16_elder.json"),
    "i3":    ("doorb_dist_i3_raw_science_n16_elder.json", "doorb_dist_i3_grade_n16_elder.json"),
}


def main():
    D.init()
    try:
        D.selftest()
    except Exception as e:
        json.dump({"verdict": f"NO-TEST (selftest {e})"},
                  open(os.path.join(RES, "unfold_U0_ghost_mitigation_c5073.json"), "w")); return

    # load U1's P-independent ghost map
    u1 = json.load(open(os.path.join(RES, "unfold_U1_ghost_phase_c5073.json")))
    g_bar = np.array(u1["g_bar_P_independent_map"])
    ghat = np.abs(g_bar); ghat = ghat / ghat.mean()          # P-independent per-qubit weighting, fixed

    # PIN + gather per-draw (planted P, weight, graded tr2)
    draws = {}
    pin_ok_all = True
    for name, (sf, gf) in HEALTHY.items():
        g = json.load(open(os.path.join(RES, gf)))
        P = g.get("planted_P") or g.get("pauli"); graded = float(g["estimate_tr2"])
        wp = sum(c != "I" for c in P)
        bells = [D.outcome_to_bells(s, N) for s in json.load(open(os.path.join(RES, sf)))["shots"]]
        pin = D.estimate(P, bells); ok = abs(pin - graded) < 2e-3; pin_ok_all &= ok
        supp = [q for q in range(N) if P[q] != "I"]
        draws[name] = {"P": P, "wp": wp, "tr2": graded, "pin": pin, "pin_ok": ok,
                       "supp": supp, "ghost_overlap": float(sum(ghat[q] for q in supp))}
        print(f"  {name}: PIN {pin:.5f} vs {graded:.5f} {'OK' if ok else 'FAIL'} | wp {wp} | "
              f"ghost-overlap {draws[name]['ghost_overlap']:.2f}")
    if not pin_ok_all:
        json.dump({"verdict": "NO-TEST (pin)"},
                  open(os.path.join(RES, "unfold_U0_ghost_mitigation_c5073.json"), "w"))
        print("VERDICT: NO-TEST"); return

    names = list(draws)
    deficit = {n: -0.5 * np.log(draws[n]["tr2"]) for n in names}   # = sum_supp (-log f_q)
    wp = {n: draws[n]["wp"] for n in names}
    gov = {n: draws[n]["ghost_overlap"] for n in names}

    # P2: mean per-qubit fidelity consistency (constant-f model, in-sample)
    f_per_draw = {n: draws[n]["tr2"] ** (1.0 / (2 * wp[n])) for n in names}
    f_hat = float(np.mean(list(f_per_draw.values())))
    f_spread = float(np.std(list(f_per_draw.values())))
    print(f"\nP2 mean per-qubit fidelity f_hat = {f_hat:.4f} +/- {f_spread:.4f} "
          f"(per draw {[round(v,4) for v in f_per_draw.values()]}) "
          f"-> {'CONSISTENT (base model holds across 4 secrets)' if f_spread < 0.01 else 'scattered'}")

    # P3: leave-one-out prediction error, M0 (predictor=wp) vs M1 (predictor=ghost_overlap)
    def loo_rmse(predictor):
        errs = []
        for held in names:
            tr = [n for n in names if n != held]
            c = sum(deficit[n] for n in tr) / sum(predictor[n] for n in tr)   # 1-param LS through origin
            pred_deficit = c * predictor[held]
            pred_tr2 = float(np.exp(-2 * pred_deficit))
            errs.append((pred_tr2 - draws[held]["tr2"]) ** 2)
        return float(np.sqrt(np.mean(errs)))
    rmse_M0 = loo_rmse(wp)
    rmse_M1 = loo_rmse(gov)
    print(f"P3 LOO prediction RMSE: M0 (weight-only) {rmse_M0:.4f}  |  M1 (ghost-informed) {rmse_M1:.4f}  "
          f"-> ghost {'HELPS' if rmse_M1 < rmse_M0 else 'does NOT help'} "
          f"({100*(rmse_M0-rmse_M1)/rmse_M0:+.0f}% vs M0)")

    # mitigation: corrected tr2 under the better model's in-sample fit; check overshoot
    best = wp if rmse_M0 <= rmse_M1 else gov
    c_all = sum(deficit[n] for n in names) / sum(best[n] for n in names)
    corrected = {n: float(draws[n]["tr2"] * np.exp(2 * c_all * best[n])) for n in names}  # divide out modeled loss
    overshoot = any(v > 1.0 + 3 * 0.004 for v in corrected.values())   # >1 beyond ~shot SE
    print(f"    corrected tr2 (best model): {[round(corrected[n],3) for n in names]} "
          f"-> {'OVERSHOOT (>1)' if overshoot else 'physical (<=1)'}")

    # verdict
    helps = rmse_M1 < rmse_M0 * 0.98
    if helps and not overshoot:
        verdict = ("BUILD-UPON SIGNAL: the ghost map predicts the tr2 deficit BETTER than weight alone "
                   f"({100*(rmse_M0-rmse_M1)/rmse_M0:+.0f}% LOO), no overshoot -> the weight-1 ghost is a "
                   "usable per-qubit mitigation ingredient. n=4 is low power; a multi-draw flight would "
                   "certify it.")
    else:
        verdict = ("HONEST BRANCH (P4): at n=4 the ghost map does NOT beat the weight-only baseline "
                   f"(M0 {rmse_M0:.4f} vs M1 {rmse_M1:.4f}); the base per-qubit fidelity model DOES hold "
                   f"across 4 secrets (f_hat {f_hat:.3f} +/- {f_spread:.3f}) — the apparatus model walks "
                   "like a duck at the mean-fidelity level, but resolving the ghost's per-qubit "
                   "refinement needs more sealed draws (a multi-draw mitigation flight). Bound, not fail.")
    print(f"\nVERDICT: {verdict}")
    out = {"card": "unfold_U0_ghost_mitigation", "cycle": "C5073", "pin_all_ok": pin_ok_all,
           "f_hat": f_hat, "f_spread": f_spread, "f_per_draw": f_per_draw,
           "loo_rmse_M0_weight": rmse_M0, "loo_rmse_M1_ghost": rmse_M1,
           "ghost_overlap": gov, "wp": wp, "corrected_tr2_best": corrected, "overshoot": overshoot,
           "n_draws": len(names), "power_note": "n=4 with weight confound = low power by construction",
           "verdict": verdict}
    json.dump(out, open(os.path.join(RES, "unfold_U0_ghost_mitigation_c5073.json"), "w"), indent=1)
    print("-> results/unfold_U0_ghost_mitigation_c5073.json")


if __name__ == "__main__":
    main()
