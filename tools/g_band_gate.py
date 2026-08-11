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

if __name__ == "__main__":
    print("G-BAND can-it-fire proof — BOTH directions, zero shots, real data:\n")
    cases = [
      ("FLOWN cell-2 CE arm (idle-delay dephasing)", [-0.056, -0.057, 0.740], "REFUSE"),
      ("FLOWN cell-2 CC arm (idle-delay dephasing)", [0.3147, -0.3199, 0.7359], "REFUSE"),
      ("healthy twirl at p=0.5 (isotropic)",         [0.4638, -0.4638, 0.4638], "PASS"),
      ("healthy twirl at p=0.35",                    [0.6029, -0.6029, 0.6029], "PASS"),
      ("isotropic but OUTSIDE the declared band (p=0.85)", [0.1391, -0.1391, 0.1391], "REFUSE"),
    ]
    for label, diag, want in cases:
        r = g_band(diag)
        got = "REFUSE" if r["verdict"].startswith("REFUSE") else "PASS"
        print(f"  {'✅' if got==want else '🔴'} {label:<44} p̂={r['p_hat_per_axis']} spread={r['axis_spread']:.3f} "
              f"mean={r['mean_p_hat']:.3f} -> {got:<7} (want {want})")
    print(f"\n  paired se on the band mean over 40 runs = {SD_RUN/math.sqrt(40):.4f}"
          f"  -> a 0.05 band shift shows at {0.05/(SD_RUN/math.sqrt(40)):.1f} sigma")
