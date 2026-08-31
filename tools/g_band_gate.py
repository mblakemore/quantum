#!/usr/bin/env python3
"""G-BAND — realized injection strength must match the DECLARED band (Elder #9284).

Every run measures its own p: |C_ii| = (1-p)*C_ideal  =>  p_hat_i = 1 - |C_ii|/C_IDEAL.
Two clauses:
  (1) AXIS CONSISTENCY — the three diagonals must yield the SAME p_hat within measurement error.
      An anisotropic channel fails here by construction, which is the defect that killed the flown
      attempt; an isotropic one cannot fail it except by noise.
  (2) BAND MATCH — the realized p_hat distribution (mean/edges) must match the declared band.
      PAIRED against the PUBLISHED draws, so band spread is signal not noise: se_mean = 0.0303/sqrt(40)
      = 0.0048, giving 10.4 sigma on a 0.05 band shift. (Elder #9289 / Ember #9291 both derived the
      unpaired 0.0183 first and superseded it — the draws are published, so the check is paired.)

SHIPS WITH A DEMONSTRATED FIRE (Ember #9291): replayed against the FLOWN cell-2 diagonals.
"""
import math, sys
C_IDEAL, SD_RUN = 0.9276, 0.0303

def p_hat(C): return 1 - abs(C) / C_IDEAL

def g_band(diagonals, declared=(0.30, 0.70), n_runs=40, se_run=0.030):
    ps = [p_hat(c) for c in diagonals]
    spread = max(ps) - min(ps)
    tol = 5 * se_run * math.sqrt(2)          # 5-sigma on a pairwise difference
    consistent = spread <= tol
    mean_p = sum(ps) / len(ps)
    in_band = declared[0] - 0.05 <= mean_p <= declared[1] + 0.05
    return {"p_hat_per_axis": [round(x, 3) for x in ps], "axis_spread": round(spread, 3),
            "tolerance": round(tol, 3), "axis_consistent": consistent,
            "mean_p_hat": round(mean_p, 3), "in_declared_band": in_band,
            "verdict": "PASS" if (consistent and in_band) else
                       ("REFUSE (anisotropic — axes disagree on p)" if not consistent else
                        "REFUSE (realized p outside declared band)")}

def g_band_arm_agreement(ce_diagonals, cc_diagonals, tol=0.05):
    """ARM-p AGREEMENT (Ember/Elder seam, #9372/#9377): the two arms must have drawn the SAME p.
    G-BAND's per-arm clauses are blind to this: CE at p=0.35 (|C|=0.637) and CC at p=0.65
    (|C|=0.343) are each internally isotropic and each inside the band, so both PASS while the
    arms sit at different injection strengths — an arm-correlated difference by construction.
    In the frozen design this is STRUCTURALLY IMPOSSIBLE (p is drawn once per unit and both arms
    are built from that draw, verified in code), so this clause exists to catch a BUILD that
    broke the guarantee, not a design that allows it. Structure protects; the gate verifies."""
    pce = sum(p_hat(c) for c in ce_diagonals)/len(ce_diagonals)
    pcc = sum(p_hat(c) for c in cc_diagonals)/len(cc_diagonals)
    d = abs(pce-pcc)
    return {"p_CE": round(pce,3), "p_CC": round(pcc,3), "gap": round(d,3),
            "verdict": "PASS (arms share p)" if d <= tol else "REFUSE (arms at different injection strengths)"}

def g_band_spread(p_hats, declared=(0.30,0.70), se_run=0.0281):
    """SPREAD clause (Elder #9382) — NON-OPTIONAL. G-BAND as first specified tested MEMBERSHIP,
    and a CONSTANT p is a member of any band containing it. A fixed p means band width W = 0, and
    the ceiling 1/2 + d/(2W) does not degrade — IT DIVIDES BY ZERO. Physically: with no
    randomization the realized magnitudes are deterministic, an analyst holding the reference
    distributions separates the arms WITH CERTAINTY, the ceiling is 1.0, and NO RUN COUNT CLEARS
    IT. So the gate must verify the realized p_hat is actually a DISTRIBUTION over the band.
    Uniform[0.30,0.70] has sd 0.1155; a constant p returns ~se_run (0.028)."""
    import statistics as st
    sd = st.pstdev(p_hats) if len(p_hats)>1 else 0.0
    lo, hi = declared
    expect = (hi-lo)/(12**0.5)
    z = (expect - sd)/max(se_run/len(p_hats)**0.5, 1e-9)
    return {"realized_sd": round(sd,4), "expected_sd": round(expect,4), "shortfall_sigma": round(z,1),
            "verdict": "PASS (p varies across the band)" if sd >= 0.6*expect else
                       "REFUSE (p_hat has no spread — W~0, the ceiling divides by zero)"}

if __name__ == "__main__":
    print("G-BAND can-it-fire proof — BOTH directions, zero shots, real data:\n")
    cases = [
      ("FLOWN cell-2 CE arm (idle-delay dephasing)", [-0.056, -0.057, 0.740], "REFUSE"),
      ("FLOWN cell-2 CC arm (idle-delay dephasing)", [0.3147, -0.3199, 0.7359], "REFUSE"),
      ("healthy twirl at p=0.5 (isotropic)",         [0.4638, -0.4638, 0.4638], "PASS"),
      ("healthy twirl at p=0.35",                    [0.6029, -0.6029, 0.6029], "PASS"),
      ("isotropic but OUTSIDE the declared band (p=0.85)", [0.1391, -0.1391, 0.1391], "REFUSE"),
    ]
    _failed = 0        # see the exit block at the foot of this file
    for label, diag, want in cases:
        r = g_band(diag)
        got = "REFUSE" if r["verdict"].startswith("REFUSE") else "PASS"
        _failed += (got != want)
        print(f"  {'✅' if got==want else '🔴'} {label:<44} p̂={r['p_hat_per_axis']} spread={r['axis_spread']:.3f} "
              f"mean={r['mean_p_hat']:.3f} -> {got:<7} (want {want})")
    print("\n  SPREAD clause (Elder #9382) — can-it-fire, both directions:")
    import numpy as _np
    _rng=_np.random.default_rng(1)
    for lab, ph, want in [
        ("FIXED p = 0.4116 across 40 runs", [0.4116]*40, "REFUSE"),
        ("uniform draws over [0.30,0.70]",  list(_rng.uniform(0.30,0.70,40)), "PASS")]:
        r=g_band_spread(ph); got="REFUSE" if r["verdict"].startswith("REFUSE") else "PASS"
        _failed += (got != want)
        print(f"    {'✅' if got==want else '🔴'} {lab:<34} sd={r['realized_sd']:.4f} (expect {r['expected_sd']:.4f}) -> {got} (want {want})")
    print("\n  ARM-p AGREEMENT clause (Ember/Elder seam) — can-it-fire, both directions:")
    for lab, ce_d, cc_d, want in [
        ("the seam: CE at p=0.35, CC at p=0.65", [0.637,0.637,0.637], [0.343,-0.343,0.343], "REFUSE"),
        ("healthy: both arms at p=0.50",         [0.464,0.464,0.464], [0.464,-0.464,0.464], "PASS")]:
        r = g_band_arm_agreement(ce_d, cc_d)
        got = "REFUSE" if r["verdict"].startswith("REFUSE") else "PASS"
        _failed += (got != want)
        print(f"    {'✅' if got==want else '🔴'} {lab:<38} p_CE={r['p_CE']} p_CC={r['p_CC']} gap={r['gap']} -> {got} (want {want})")
    print(f"\n  paired se on the band mean over 40 runs = {SD_RUN/math.sqrt(40):.4f}"
          f"  -> a 0.05 band shift shows at {0.05/(SD_RUN/math.sqrt(40)):.1f} sigma")

    # EXIT NONZERO WHEN THE CAN-IT-FIRE PROOF FAILS (2026-08-31, board#355 sweep).
    # SECOND INSTANCE OF THIS DEFECT IN THIS FAMILY — g_abstain_gate.py had it identically
    # (quantum@40f5809) and this file was found by grepping the CLASS rather than waiting to trip
    # over it again. All THREE proof loops above (band, spread, arm-agreement) printed 🔴 on a
    # mismatch and the script exited 0. A human reading the output saw the failure; any caller
    # reading the exit code — CI, a wrapper, a pre-flight batch — saw a pass.
    #
    # This is the authorize-by-silence shape in a gate's OWN PROOF, and it is worse there than in
    # the gate: this file exists to demonstrate the gate CAN fire, on the principle that a pass
    # never contrasted with a fire carries no information. A proof that cannot report its own
    # failure is exactly what makes a broken gate look sound.
    import sys
    if _failed:
        print(f"\n  🔴 CAN-IT-FIRE PROOF FAILED: {_failed} case(s) across the band, spread and "
              f"arm-agreement clauses disagree with their expected verdict. A PASS from this gate "
              f"no longer carries the information it implies — do not rely on one until green.")
        sys.exit(1)
    print("\n  ✅ can-it-fire proof GREEN — all three clauses match their expected verdicts (exit 0).")
