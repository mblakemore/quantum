#!/usr/bin/env python3
"""DOOR-B GHOST-POWER JACKKNIFE across the five sealed draws (Whisper C5073, Creator GO).

The systematic-vs-statistical budget F122 never did, on the quantity the weight-spectrum
surfaced: the ghost lives at weight 1 (and only there). Estimand W1 = sum over ALL 48 weight-1
Paulis of tr(Qrho)^2 = the ghost's integrated power per draw (EXACT, 48 terms, no sampling).
Jackknife across the 5 draws decomposes W1's cross-draw spread. $0, imports the validated F122
estimator, FROZEN before compute.

WHY IT MATTERS: A2/S4 ruled the ghost MEASUREMENT-QUALITY-LINKED (tracks per-pair cal deficit).
If true, W1 should VARY draw-to-draw with each draw's cal epoch -> a SYSTEMATIC component above
shot noise. If W1 is constant across draws to within shot noise -> statistical-only, which would
TENSION the apparatus-quality reading. The jackknife measures exactly this decomposition and is
the reviewer's 'detector systematics' number.

PIN (must pass): the estimator reproduces the banked graded tr2 for a draw's planted P (<2e-3).
REGISTERED PREDICTIONS:
  P1 pin reproduces.
  P2 W1 > 0 and resolvable (> its shot-noise SE) in all 5 draws (ghost present everywhere, per A2).
  P3 (the budget): cross-draw sample variance of W1 vs the mean within-draw shot-noise variance.
     A2-consistent prediction: cross-draw >> shot-noise (systematic epoch/cal variation dominates)
     -> the ghost power is a draw-dependent apparatus number, NOT a shot-noise artifact. The
     statistical-only outcome (cross-draw ~ shot-noise) would tension A2 and is equally reported.
Draws: original(WIN) · refly · i1 · i2 · i3 (n=16 each).
"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import exp142_robust_decoder_sim as g2

N = 16
RES = os.path.join(HERE, "..", "results")
SCIENCE = {
    "original": "doorb_raw_science_n16_elder.json",
    "refly":    "doorb_refly_raw_science_n16_elder.json",
    "i1":       "doorb_dist_i1_raw_science_n16_elder.json",
    "i2":       "doorb_dist_i2_raw_science_n16_elder.json",
    "i3":       "doorb_dist_i3_raw_science_n16_elder.json",
}
PIN_GRADE = ("i1", "doorb_dist_i1_grade_n16_elder.json")   # known-answer pin


def tr2(sb, P, csign):
    Pb = g2.pauli_to_bits(P)
    swapped = np.concatenate([Pb[N:], Pb[:N]])
    return 2 * float(np.mean((sb @ swapped) % 2 == csign[P.count("Y") % 2])) - 1


def weight1_paulis():
    out = []
    for i in range(N):
        for L in "XYZ":
            out.append("I" * i + L + "I" * (N - 1 - i))
    return out   # 48


def main():
    mapping = g2.calibrate_bell_mapping()
    csign = g2.calibrate_constraint_sign(mapping)
    w1 = weight1_paulis()

    # PIN
    g = json.load(open(os.path.join(RES, PIN_GRADE[1])))
    Pp = g.get("planted_P") or g.get("pauli"); graded = float(g["estimate_tr2"])
    sbp = np.array([g2.outcome_to_bits(s, N, mapping)
                    for s in json.load(open(os.path.join(RES, SCIENCE[PIN_GRADE[0]])))["shots"]])
    pin = tr2(sbp, Pp, csign); pin_ok = abs(pin - graded) < 2e-3
    print(f"PIN ({PIN_GRADE[0]}): tr2 {pin:.5f} vs graded {graded:.5f} -> {'PASS' if pin_ok else 'FAIL'}")
    if not pin_ok:
        json.dump({"verdict": "NO-TEST (pin)"}, open(os.path.join(RES, "doorb_ghost_jackknife_c5073.json"), "w"))
        return

    # W1 per draw (exact 48-term ghost power) + within-draw shot-noise variance on W1
    W, se2 = {}, {}
    for name, fn in SCIENCE.items():
        sb = sbp if name == PIN_GRADE[0] else np.array(
            [g2.outcome_to_bits(s, N, mapping) for s in json.load(open(os.path.join(RES, fn)))["shots"]])
        M = sb.shape[0]
        vals = np.array([tr2(sb, q, csign) for q in w1])       # 48 tr2 estimates
        W[name] = float(np.sum(vals))
        se2[name] = 48 * (1.0 / M)                              # Var(sum) ~ 48 * (1/M) per-term shot var
        print(f"  {name:9s}: W1 (ghost power) {W[name]:+.4f}  (M={M:,}, shot-SE {np.sqrt(se2[name]):.4f})")

    names = list(W); vals = np.array([W[n] for n in names]); K = len(vals)
    # jackknife across draws
    jk = np.array([np.mean(np.delete(vals, i)) for i in range(K)])
    jk_mean = float(np.mean(jk))
    jk_se = float(np.sqrt((K - 1) / K * np.sum((jk - jk_mean) ** 2)))
    # systematic vs statistical decomposition
    cross_var = float(np.var(vals, ddof=1))                    # observed cross-draw variance
    shot_var = float(np.mean([se2[n] for n in names]))         # mean within-draw shot variance
    excess = cross_var - shot_var                             # systematic variance (if > 0)
    sys_frac = max(0.0, excess) / cross_var if cross_var > 0 else 0.0
    verdict = ("SYSTEMATIC-DOMINATED: cross-draw spread exceeds shot noise -> W1 is a draw-dependent "
               "apparatus number (A2 measurement-quality reading supported)"
               if excess > shot_var else
               "STATISTICAL-CONSISTENT: cross-draw spread ~ shot noise -> W1 stable across draws "
               "within statistics (tensions the draw-dependent reading; report as-is)")
    out = {"card": "doorb_ghost_jackknife", "cycle": "C5073", "n": N,
           "pin": {"draw": PIN_GRADE[0], "tr2": pin, "graded": graded, "ok": pin_ok},
           "W1_per_draw": W, "W1_shot_var": se2,
           "jackknife_mean": jk_mean, "jackknife_SE": jk_se,
           "cross_draw_var": cross_var, "mean_shot_var": shot_var,
           "excess_systematic_var": excess, "systematic_fraction": sys_frac,
           "verdict": verdict}
    print(f"\nJACKKNIFE across {K} draws: W1 = {jk_mean:.4f} +/- {jk_se:.4f} (jackknife SE)")
    print(f"  cross-draw var {cross_var:.5f} · mean shot var {shot_var:.5f} · excess (systematic) {excess:+.5f}")
    print(f"  systematic fraction of variance: {sys_frac:.0%}")
    print(f"VERDICT: {verdict}")
    json.dump(out, open(os.path.join(RES, "doorb_ghost_jackknife_c5073.json"), "w"), indent=1)
    print("-> results/doorb_ghost_jackknife_c5073.json")


if __name__ == "__main__":
    main()
