#!/usr/bin/env python3
"""DOOR-B CALIBRATED SPECTRUM — measure-once-ask-many, done right (Whisper C5073, Creator GO).

Retry of the purity extraction with the CALIBRATED F122 estimator (the NO-TEST diagnosis:
the signal lives in the P-selected cross-pair correlation, not a symmetric #singlet count).
$0, F103-lineage, FROZEN before compute.

THE ESTIMATOR (imported, F122/A2-validated): for a Pauli Q, tr(Qrho)^2 = 2*rate - 1, where
rate = fraction of shots whose calibrated constraint value <Q_Weyl, shot_Weyl> equals csign.
g2 = exp142_robust_decoder_sim (flown-matched, reproduced the revealed n6 rung + graded tr2).

WHY NOT SCALAR PURITY: tr(rho^2) = (1/2^n)(1 + sum_{Q != I} tr(Qrho)^2) needs 4^16 terms;
uniform Pauli sampling is hopelessly high-variance (a few large, ~all tiny). So the clean
extractable NEW observable is the LEAKAGE SPECTRUM AROUND THE PLANTED P: is the prepared state
a sharp sealed-P eigenstate, or is its magnitude spread (leaked) to nearby Paulis? That is
'what was actually prepared', from flown data.

FROZEN QUESTION SET per draw:
  - planted P                          (the PIN)
  - all 16 single-letter neighbors of P (flip one Weyl letter -> weight +-1): leakage ring
  - 48 random Paulis, 16 each at weight {4, 10, 16}: the background level
PIN (must pass or NO-TEST): tr2(planted P) reproduces the banked graded estimate_tr2 to < 2e-3.
REGISTERED PREDICTIONS:
  P1 pin reproduces (validates the estimator on THIS data).
  P2 single-letter neighbors near 0 (mean |tr2| < 0.05): sharp seal, clean prep, no leakage ring.
     If neighbors carry magnitude -> coherent leakage detected (equally a result).
  P3 random background near 0: the high-weight state has no accidental low-weight structure.
Draws: i1 (w11, graded 0.37019) · i2 (w12, 0.30084) · i3 (w13, 0.28106).
"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import exp142_robust_decoder_sim as g2

N = 16
RES = os.path.join(HERE, "..", "results")
DRAWS = {
    "i1": ("doorb_dist_i1_raw_science_n16_elder.json", "doorb_dist_i1_grade_n16_elder.json"),
    "i2": ("doorb_dist_i2_raw_science_n16_elder.json", "doorb_dist_i2_grade_n16_elder.json"),
    "i3": ("doorb_dist_i3_raw_science_n16_elder.json", "doorb_dist_i3_grade_n16_elder.json"),
}
RNG = np.random.default_rng(5073)


def tr2(shots_bits, P, csign):
    Pb = g2.pauli_to_bits(P)
    swapped = np.concatenate([Pb[N:], Pb[:N]])
    vals = (shots_bits @ swapped) % 2
    ypar = P.count("Y") % 2
    rate = float(np.mean(vals == csign[ypar]))
    return 2 * rate - 1


def neighbors(P):
    out = []
    for i in range(N):
        for L in "IXYZ":
            if L != P[i]:
                out.append(P[:i] + L + P[i+1:])
    return out  # 16 * 3 = 48 single-letter neighbors; sample 16


def rand_pauli(weight):
    pos = RNG.choice(N, size=weight, replace=False)
    s = ["I"] * N
    for p in pos:
        s[p] = RNG.choice(list("XYZ"))
    return "".join(s)


def main():
    mapping = g2.calibrate_bell_mapping()
    csign = g2.calibrate_constraint_sign(mapping)
    out = {"card": "doorb_calibrated_spectrum", "cycle": "C5073", "n": N,
           "estimator": "2*rate-1, calibrated F122 (g2 flown-matched)", "draws": {}}
    all_pin = True
    for name, (sf, gf) in DRAWS.items():
        grade = json.load(open(os.path.join(RES, gf)))
        P = grade.get("planted_P") or grade.get("pauli")
        graded = float(grade["estimate_tr2"])
        shots = json.load(open(os.path.join(RES, sf)))["shots"]
        sb = np.array([g2.outcome_to_bits(s, N, mapping) for s in shots])

        pin_val = tr2(sb, P, csign)
        pin_ok = abs(pin_val - graded) < 2e-3
        all_pin &= pin_ok

        nb = RNG.choice(neighbors(P), size=16, replace=False)
        nb_vals = [tr2(sb, q, csign) for q in nb]
        bg = {w: [tr2(sb, rand_pauli(w), csign) for _ in range(16)] for w in (4, 10, 16)}

        out["draws"][name] = {
            "planted_P": P, "graded_tr2": graded, "my_tr2": pin_val,
            "pin_dev": abs(pin_val - graded), "pin_ok": pin_ok,
            "neighbor_mean_abs": float(np.mean(np.abs(nb_vals))),
            "neighbor_max_abs": float(np.max(np.abs(nb_vals))),
            "background_mean_abs": {str(w): float(np.mean(np.abs(v))) for w, v in bg.items()},
        }
        print(f"{name}: PIN tr2 {pin_val:+.5f} vs graded {graded:.5f} dev {abs(pin_val-graded):.2e} "
              f"{'PASS' if pin_ok else 'FAIL'}")
        print(f"    leakage ring |tr2|: mean {np.mean(np.abs(nb_vals)):.4f} max {np.max(np.abs(nb_vals)):.4f}"
              f"  | background |tr2| w4/10/16: "
              f"{np.mean(np.abs(bg[4])):.4f}/{np.mean(np.abs(bg[10])):.4f}/{np.mean(np.abs(bg[16])):.4f}")
    if not all_pin:
        out["verdict"] = "NO-TEST (pin: estimator did not reproduce a graded tr2)"
    else:
        # interpret the leakage ring
        rings = [out["draws"][k]["neighbor_mean_abs"] for k in out["draws"]]
        sharp = all(r < 0.05 for r in rings)
        out["verdict"] = ("SPECTRUM-EXTRACTED: sharp seal (clean prep, no leakage ring)" if sharp
                          else "SPECTRUM-EXTRACTED: leakage ring present (coherent spread to neighbors)")
    print(f"\nVERDICT: {out['verdict']}")
    json.dump(out, open(os.path.join(RES, "doorb_calibrated_spectrum_c5073.json"), "w"), indent=1)
    print("-> results/doorb_calibrated_spectrum_c5073.json")


if __name__ == "__main__":
    main()
