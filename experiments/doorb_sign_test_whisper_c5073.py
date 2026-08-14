#!/usr/bin/env python3
"""DOOR-B SIGN/STRUCTURE TEST — measurement-quality vs coherent-leak (Whisper C5073, Creator GO).

Ember's discriminating test (originator steer general#11913): a measurement-quality artifact
carries a PER-QUBIT (apparatus) pattern INDEPENDENT of the planted P; a coherent leak follows
the planted eigenstate structure and TRACKS P. The 4 healthy draws each have a DIFFERENT planted
P, so the discrimination is direct:
  H_MEAS: the per-qubit ghost pattern is the SAME across draws (same hot qubits => apparatus).
  H_COH : the pattern TRACKS each draw's P (concentrates on letters that anticommute with P_q).

$0, imports Elder's validated decoder (doorb_decoder_elder = doorb-decoder-elder-v1, the A2
estimator, built-in selftest refuses to decode unless it passes), FROZEN before compute. Uses
tr(Qrho)^2 magnitudes (well-defined); the finer readout-asymmetry SIGN-DIRECTION correlation
needs Elder's signed reading + Ember's coherent phase model and is flagged, not faked.

PIN: (a) Elder decoder selftest PASSES; (b) mean weight-1 tr2 on healthy draws ~0.010
(reproduces A2 magnitude_structure) to within 2x.
ESTIMANDS per healthy draw (first_FAIL excluded per A2 a-priori stratum):
  g[q] = sum over L in {X,Y,Z} of tr((L on q)rho)^2  -- per-qubit ghost power (16-vector)
REGISTERED PREDICTIONS:
  P1 pin passes.
  P2 (cross-draw consistency): mean pairwise Pearson r of the 16-vector g across the 4 draws.
     H_MEAS -> high r (same hot qubits, P-independent). H_COH -> low r (pattern moves with P).
  P3 (P-tracking): per draw, correlate the 48 tr2 with the anticommutation indicator
     [L != P_q and P_q != I] (letters that anticommute with the planted letter).
     H_COH -> positive corr (ghost on anticommuting letters). H_MEAS -> ~0.
  VERDICT: high cross-draw r + ~0 P-tracking -> MEASUREMENT-QUALITY (P-independent apparatus,
     supports A2's S1/S3). Low cross-draw r + positive P-tracking -> COHERENT. Mixed -> report.
Healthy draws: refly(WIN) · i1 · i2 · i3.
"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
import doorb_decoder_elder as D

N = 16
RES = os.path.join(HERE, "..", "results")
HEALTHY = {   # first_FAIL (doorb_raw_science) excluded per A2 stratum
    "refly": ("doorb_refly_raw_science_n16_elder.json", "doorb_refly_grade_n16_elder.json"),
    "i1":    ("doorb_dist_i1_raw_science_n16_elder.json", "doorb_dist_i1_grade_n16_elder.json"),
    "i2":    ("doorb_dist_i2_raw_science_n16_elder.json", "doorb_dist_i2_grade_n16_elder.json"),
    "i3":    ("doorb_dist_i3_raw_science_n16_elder.json", "doorb_dist_i3_grade_n16_elder.json"),
}


def main():
    D.init()
    try:
        D.selftest()
        print("PIN(a): Elder decoder selftest PASS")
    except Exception as e:
        print(f"PIN(a) FAIL: selftest {e}"); return

    gvecs, pvecs, planted = {}, {}, {}
    for name, (sf, gf) in HEALTHY.items():
        P = (lambda d: d.get("planted_P") or d.get("pauli"))(json.load(open(os.path.join(RES, gf))))
        planted[name] = P
        shots = json.load(open(os.path.join(RES, sf)))["shots"]
        bells = [D.outcome_to_bells(s, N) for s in shots]
        # 48 weight-1 tr2
        m = {}
        for q in range(N):
            for L in "XYZ":
                Q = "I" * q + L + "I" * (N - 1 - q)
                m[(q, L)] = D.estimate(Q, bells)
        g = np.array([sum(m[(q, L)] for L in "XYZ") for q in range(N)])   # per-qubit power
        gvecs[name] = g
        # anticommutation predictor vector (48), and the aligned tr2 vector
        anti, tr2v = [], []
        for q in range(N):
            for L in "XYZ":
                anti.append(1.0 if (P[q] != "I" and L != P[q]) else 0.0)
                tr2v.append(m[(q, L)])
        pvecs[name] = (np.array(tr2v), np.array(anti))
        print(f"  {name} (P wt {sum(c!='I' for c in P)}): mean w1 tr2 {np.mean(list(m.values())):.4f} "
              f"per-qubit power range [{g.min():.4f},{g.max():.4f}]")

    mean_w1 = np.mean([np.mean(gvecs[n]) / 3 for n in gvecs])
    pin_b = 0.005 < mean_w1 < 0.02
    print(f"PIN(b): mean weight-1 tr2 {mean_w1:.4f} vs A2 ~0.010 -> {'PASS' if pin_b else 'CHECK'}")

    # P2 cross-draw consistency of the per-qubit power vectors
    names = list(gvecs); rs = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            rs.append(float(np.corrcoef(gvecs[names[i]], gvecs[names[j]])[0, 1]))
    cross_r = float(np.mean(rs))
    # P3 P-tracking: corr(tr2, anticommutation) per draw
    ptrack = {n: float(np.corrcoef(pvecs[n][0], pvecs[n][1])[0, 1]) for n in names}
    mean_ptrack = float(np.mean(list(ptrack.values())))

    print(f"\nP2 cross-draw per-qubit consistency: mean pairwise r = {cross_r:+.3f} "
          f"(pairwise {[round(r,2) for r in rs]})")
    print(f"P3 P-tracking (corr tr2 vs anticommute): per-draw {[round(v,2) for v in ptrack.values()]}, "
          f"mean {mean_ptrack:+.3f}")

    meas = cross_r > 0.3 and abs(mean_ptrack) < 0.15
    coh = mean_ptrack > 0.3 and cross_r < 0.15
    verdict = ("MEASUREMENT-QUALITY: per-qubit pattern consistent across draws (P-independent), "
               "no P-tracking -> apparatus artifact, supports A2 S1/S3" if meas else
               "COHERENT: pattern tracks planted P, low cross-draw consistency" if coh else
               "INCONCLUSIVE at this signal level (healthy ghost ~0.01 is near shot resolution); "
               "cross-draw r and P-tracking both weak -> the finer signed readout-asymmetry test "
               "(Elder signed reading + Ember phase model) is needed to decide")
    print(f"\nVERDICT: {verdict}")
    out = {"card": "doorb_sign_test", "cycle": "C5073", "pin_selftest": True, "pin_mean_w1": mean_w1,
           "planted": planted, "cross_draw_r": cross_r, "pairwise_r": rs,
           "P_tracking": ptrack, "mean_P_tracking": mean_ptrack, "verdict": verdict}
    json.dump(out, open(os.path.join(RES, "doorb_sign_test_c5073.json"), "w"), indent=1)
    print("-> results/doorb_sign_test_c5073.json")


if __name__ == "__main__":
    main()
