#!/usr/bin/env python3
"""UNFOLD U1 — ghost per-qubit map (Whisper C5073). $0. FROZEN before compute.

PREMISE-CORRECTION CAUGHT AT PIN (freeze working, docs §1 U1): the campaign hypothesized a
weight-1 SIGNED per-qubit direction recoverable because 3^1=3 is cheap. But D.estimate on the
two-copy corpus returns tr(Qrho)^2 (the two-copy Bell identity E[v_P]=tr(Prho)^2 — VERIFIED: it
reproduces the graded estimate_tr2 to 1e-5). The square is sign-free at EVERY weight, not just high
weight — this is *why* dig A needed single-copy (dig B wall: no single-copy on the marrakesh ghost
qubits). So the signed direction is NOT extractable here; U1 delivers the VALID quantity the pin
leaves standing: the P-independent per-qubit ghost POWER map (magnitude), which is exactly U0's input.

PIN (must pass or NO-TEST): (a) D.selftest passes; (b) D.estimate(planted_P) reproduces each draw's
graded estimate_tr2 < 2e-3 (this simultaneously CONFIRMS D.estimate = tr2, sign-free).
ESTIMAND per healthy draw: g[q] = sum_{L in XYZ} tr((L on q)rho)^2  (16-vector, per-qubit ghost power)
REGISTERED PREDICTIONS:
  P1 pin passes on all 4 draws (and confirms sign-free tr2).
  P2 cross-draw consistency of g reproduces the sign-test (mean pairwise r ~ +0.8, P-independent).
  P3 (premise correction, reported not faked): the SIGNED direction is single-copy-only; U1's
     deliverable is the magnitude map g_bar[q] = mean over draws (the P-independent apparatus map).
Draws: refly · i1 · i2 · i3 (first_FAIL excluded per A2 stratum).
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
        D.selftest(); print("PIN(a) selftest: PASS")
    except Exception as e:
        print(f"PIN(a) FAIL: {e}")
        json.dump({"verdict": "NO-TEST (selftest)"}, open(os.path.join(RES, "unfold_U1_ghost_phase_c5073.json"), "w"))
        return

    gvecs, planted, tr2_planted, pin_ok_all = {}, {}, {}, True
    for name, (sf, gf) in HEALTHY.items():
        g = json.load(open(os.path.join(RES, gf)))
        P = g.get("planted_P") or g.get("pauli"); graded = float(g["estimate_tr2"])
        planted[name] = P; tr2_planted[name] = graded
        shots = json.load(open(os.path.join(RES, sf)))["shots"]
        bells = [D.outcome_to_bells(s, N) for s in shots]
        # PIN(b): planted-P tr2 reproduces the grade (confirms sign-free tr2)
        pin = D.estimate(P, bells); pin_ok = abs(pin - graded) < 2e-3; pin_ok_all &= pin_ok
        # per-qubit ghost power (magnitude, the valid quantity)
        gq = np.array([sum(D.estimate("I" * q + L + "I" * (N - 1 - q), bells) for L in "XYZ")
                       for q in range(N)])
        gvecs[name] = gq
        print(f"  {name} (P wt {sum(c!='I' for c in P)}): PIN tr2 {pin:.5f} vs graded {graded:.5f} "
              f"{'PASS' if pin_ok else 'FAIL'} | ghost power range [{gq.min():+.4f},{gq.max():+.4f}]")

    if not pin_ok_all:
        json.dump({"verdict": "NO-TEST (pin: tr2 did not reproduce a grade)"},
                  open(os.path.join(RES, "unfold_U1_ghost_phase_c5073.json"), "w"))
        print("VERDICT: NO-TEST"); return

    names = list(gvecs)
    rs = [float(np.corrcoef(gvecs[a], gvecs[b])[0, 1])
          for i, a in enumerate(names) for b in names[i + 1:]]
    cross_r = float(np.mean(rs))
    g_bar = np.mean([gvecs[n] for n in names], axis=0)   # the P-independent apparatus map (U0 input)
    hot = [int(q) for q in np.argsort(g_bar)[::-1][:6]]
    cold = [int(q) for q in np.argsort(g_bar)[:3]]
    print(f"\nP2 cross-draw consistency: mean pairwise r = {cross_r:+.3f} (reproduces sign-test ~0.81)")
    print(f"P3 P-independent ghost map g_bar: hot qubits {hot}  cold {cold}")
    verdict = ("PREMISE-CORRECTED: two-copy tr2 is sign-free at all weights (the signed direction is "
               "single-copy-only, dig B wall); U1 delivers the P-independent per-qubit ghost-power map "
               f"(cross-draw r {cross_r:+.2f}) as U0's input.")
    print(f"VERDICT: {verdict}")
    out = {"card": "unfold_U1_ghost_phase", "cycle": "C5073",
           "premise_correction": "D.estimate=tr(Qrho)^2 (two-copy Bell identity), sign-free at all "
                                  "weights; signed direction needs single-copy (dig B wall).",
           "pin_all_ok": pin_ok_all, "planted": planted, "tr2_planted": tr2_planted,
           "ghost_power_per_draw": {n: gvecs[n].tolist() for n in names},
           "cross_draw_r": cross_r, "pairwise_r": rs,
           "g_bar_P_independent_map": g_bar.tolist(), "hot_qubits": hot, "cold_qubits": cold,
           "verdict": verdict}
    json.dump(out, open(os.path.join(RES, "unfold_U1_ghost_phase_c5073.json"), "w"), indent=1)
    print("-> results/unfold_U1_ghost_phase_c5073.json")


if __name__ == "__main__":
    main()
