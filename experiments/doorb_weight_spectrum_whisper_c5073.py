#!/usr/bin/env python3
"""DOOR-B WEIGHT SPECTRUM — the broad structure search (Whisper C5073, Creator GO).

Next mine after the calibrated spectrum (sharp seal: no leakage in the planted-weight+-1 ring).
The weight-spectrum widens the search to ALL Pauli weights - a coherent prep-error component at
a FAR weight (low-weight stabilizer leak, a specific correlated-error signature) would be
invisible to the neighbor ring but visible here. $0, F103-lineage, imports the validated F122
estimator, FROZEN before compute.

OBSERVABLE (frozen): per weight w, the mean and max |tr(Qrho)^2| over K random Paulis of weight
w (sampled, since 4^16 is un-enumerable). tr(Qrho)^2 = 2*rate-1, g2 flown-matched estimator.

RESOLUTION (stated up front, honestly): the per-Pauli shot-noise floor is
sigma0 = 2*sqrt(0.25/M) ~ 1/sqrt(M) ~ 0.003 for M~100k. So this measures each weight's magnitude
DOWN TO ~0.003 and RESOLVES only structure ABOVE it. A flat-at-floor spectrum is an UPPER BOUND
(no resolvable off-planted structure), not a proof of exact zero - the honest reading.

PIN (must pass or NO-TEST): re-reproduce the banked graded tr2 for the planted P (< 2e-3).
REGISTERED PREDICTIONS:
  P1 pin reproduces.
  P2 (from sharp-seal): every sampled weight sits at the floor - max |tr2| over the whole
     sample < 5*sigma0 (~0.016), no weight shows resolvable excess. The planted spike is the
     ONLY structure, isolated at its weight; loss is incoherent (spread below resolution across
     the exponential background), confirmed spectrum-wide.
  P3 (the alternative that pays): if some weight's max |tr2| exceeds 5*sigma0, a coherent
     structure component lives there - localizes the prep-error kind. Either outcome is a result.
Weights probed: {0,1,2,4,8, wp-1, wp, wp+1, 12,14,16} per draw (wp = planted weight).
Draws: i1 (wp=11) · i2 (wp=12) · i3 (wp=13).
"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import exp142_robust_decoder_sim as g2

N = 16
K = 32                       # random Paulis per weight
RES = os.path.join(HERE, "..", "results")
DRAWS = {
    "i1": ("doorb_dist_i1_raw_science_n16_elder.json", "doorb_dist_i1_grade_n16_elder.json"),
    "i2": ("doorb_dist_i2_raw_science_n16_elder.json", "doorb_dist_i2_grade_n16_elder.json"),
    "i3": ("doorb_dist_i3_raw_science_n16_elder.json", "doorb_dist_i3_grade_n16_elder.json"),
}
RNG = np.random.default_rng(50731)


def tr2(sb, P, csign):
    Pb = g2.pauli_to_bits(P)
    swapped = np.concatenate([Pb[N:], Pb[:N]])
    vals = (sb @ swapped) % 2
    return 2 * float(np.mean(vals == csign[P.count("Y") % 2])) - 1


def rand_pauli(weight):
    pos = RNG.choice(N, size=weight, replace=False) if weight else []
    s = ["I"] * N
    for p in pos:
        s[p] = RNG.choice(list("XYZ"))
    return "".join(s)


def main():
    mapping = g2.calibrate_bell_mapping()
    csign = g2.calibrate_constraint_sign(mapping)
    out = {"card": "doorb_weight_spectrum", "cycle": "C5073", "n": N, "K": K, "draws": {}}
    all_pin, any_structure = True, False
    for name, (sf, gf) in DRAWS.items():
        grade = json.load(open(os.path.join(RES, gf)))
        P = grade.get("planted_P") or grade.get("pauli")
        graded = float(grade["estimate_tr2"]); wp = P.count("X") + P.count("Y") + P.count("Z")
        shots = json.load(open(os.path.join(RES, sf)))["shots"]
        M = len(shots)
        sb = np.array([g2.outcome_to_bits(s, N, mapping) for s in shots])
        sigma0 = 1.0 / np.sqrt(M)

        pin = tr2(sb, P, csign); pin_ok = abs(pin - graded) < 2e-3; all_pin &= pin_ok
        weights = sorted(set([0, 1, 2, 4, 8, wp - 1, wp, wp + 1, 12, 14, 16]) & set(range(0, N + 1)))
        spec = {}
        for w in weights:
            v = [abs(tr2(sb, rand_pauli(w), csign)) for _ in range(K)]
            spec[w] = {"mean_abs": float(np.mean(v)), "max_abs": float(np.max(v))}
        thr = 5 * sigma0
        structured = [w for w in weights if spec[w]["max_abs"] > thr]
        any_structure |= bool(structured)
        out["draws"][name] = {"planted_P": P, "planted_weight": wp, "graded_tr2": graded,
                              "pin_tr2": pin, "pin_ok": pin_ok, "sigma0": sigma0,
                              "threshold_5sigma": thr, "spectrum": spec,
                              "weights_with_structure": structured}
        print(f"{name} (wp={wp}, planted tr2 {graded:.4f}, pin {'OK' if pin_ok else 'FAIL'}, "
              f"sigma0 {sigma0:.4f}, 5sig {thr:.4f}):")
        for w in weights:
            flag = "  <-- STRUCTURE" if spec[w]["max_abs"] > thr else ""
            tag = " [planted wt]" if w == wp else ""
            print(f"    w={w:2d}: mean|tr2| {spec[w]['mean_abs']:.4f}  max {spec[w]['max_abs']:.4f}{tag}{flag}")

    if not all_pin:
        out["verdict"] = "NO-TEST (pin failed on some draw)"
    elif any_structure:
        out["verdict"] = "STRUCTURE-FOUND: a weight exceeds the shot-noise floor (coherent component localized)"
    else:
        out["verdict"] = ("FLAT-AT-FLOOR: no resolvable off-planted structure at any probed weight; "
                          "the planted spike is isolated, loss is incoherent spectrum-wide (upper bound = 5*sigma0/weight)")
    print(f"\nVERDICT: {out['verdict']}")
    json.dump(out, open(os.path.join(RES, "doorb_weight_spectrum_c5073.json"), "w"), indent=1)
    print("-> results/doorb_weight_spectrum_c5073.json")


if __name__ == "__main__":
    main()
