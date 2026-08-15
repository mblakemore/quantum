#!/usr/bin/env python3
"""UNFOLD U2a — boundary purity / purity-in-weight profile (Whisper C5073). $0. FROZEN.

Full purity tr(rho^2)=(1/2^n)(1+sum_{Q!=I} tr(Qrho)^2) needs all 4^n terms (hopeless). But the
SHELL POWER S_w = sum_{weight(Q)=w} tr(Qrho)^2 is a real, computable slice: it says WHERE the state's
purity lives in weight. Enumerable exactly for w in {0,1,2}; sampled with stated variance above.
This unfolds the state as a purity-in-weight profile and measures the 3^w-boundary structure directly.

PIN (must pass or NO-TEST): D.estimate reproduces each draw's graded tr2 < 2e-3.
REGISTERED PREDICTIONS:
  P1 pin reproduces.
  P2 the BOUNDARY shells (w=1,2) are near the shot floor (carry only the ghost + noise), while the
     PLANTED-weight shell carries the mass -> the state's purity lives at its planted weight, the
     boundary is clean (matches sharp-seal F122 + weight-spectrum).
  P3 falsifier: a boundary or mid shell carries resolvable mass -> hidden low/mid-weight structure.
RESOLUTION: per-Pauli SE ~ 1/sqrt(M) ~ 0.004 (M~72-106k); shell sums of K terms have SE ~ 0.004*sqrt(K)
so the w=2 shell (K=1080) floor is ~0.13 — stated as an UPPER BOUND, not exact zero.
Draws: i1 (wp11) · i2 (wp12) · i3 (wp13).
"""
import json, os, sys, itertools
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
import doorb_decoder_elder as D

N = 16
RES = os.path.join(HERE, "..", "results")
DRAWS = {
    "i1": ("doorb_dist_i1_raw_science_n16_elder.json", "doorb_dist_i1_grade_n16_elder.json"),
    "i2": ("doorb_dist_i2_raw_science_n16_elder.json", "doorb_dist_i2_grade_n16_elder.json"),
    "i3": ("doorb_dist_i3_raw_science_n16_elder.json", "doorb_dist_i3_grade_n16_elder.json"),
}
RNG = np.random.default_rng(20731)


def shell_paulis_exact(w):
    for pos in itertools.combinations(range(N), w):
        for letters in itertools.product("XYZ", repeat=w):
            s = ["I"] * N
            for p, L in zip(pos, letters):
                s[p] = L
            yield "".join(s)


def rand_pauli(w):
    pos = RNG.choice(N, size=w, replace=False)
    s = ["I"] * N
    for p in pos:
        s[p] = RNG.choice(list("XYZ"))
    return "".join(s)


def main():
    D.init()
    try:
        D.selftest()
    except Exception as e:
        json.dump({"verdict": f"NO-TEST ({e})"}, open(os.path.join(RES, "unfold_U2a_boundary_purity_c5073.json"), "w")); return

    out = {"card": "unfold_U2a_boundary_purity", "cycle": "C5073", "draws": {}}
    all_pin = True
    for name, (sf, gf) in DRAWS.items():
        g = json.load(open(os.path.join(RES, gf)))
        P = g.get("planted_P") or g.get("pauli"); graded = float(g["estimate_tr2"])
        wp = sum(c != "I" for c in P)
        bells = [D.outcome_to_bells(s, N) for s in json.load(open(os.path.join(RES, sf)))["shots"]]
        M = len(bells); sigma0 = 1.0 / np.sqrt(M)
        pin = D.estimate(P, bells); pin_ok = abs(pin - graded) < 2e-3; all_pin &= pin_ok

        shells = {}
        # exact shells w=0,1,2
        for w in (0, 1, 2):
            terms = list(shell_paulis_exact(w)) if w > 0 else ["I" * N]
            vals = [D.estimate(q, bells) for q in terms]
            K = len(terms)
            shells[w] = {"power": float(np.sum(vals)), "K": K, "exact": True,
                         "floor_SE": float(sigma0 * np.sqrt(K))}
        # sampled shells (mean-scaled to full shell size) for w=4,8,wp,16
        from math import comb
        for w in sorted(set([4, 8, wp, 16])):
            Kfull = comb(N, w) * (3 ** w)
            samp = [D.estimate(rand_pauli(w), bells) for _ in range(48)]
            shells[w] = {"power_est": float(np.mean(samp) * Kfull), "mean_abs": float(np.mean(np.abs(samp))),
                         "K_full": Kfull, "exact": False, "sampled": 48}
        out["draws"][name] = {"planted_P": P, "planted_weight": wp, "graded_tr2": graded,
                              "pin_ok": pin_ok, "sigma0": sigma0, "shells": shells}
        print(f"{name} (wp={wp}, graded {graded:.4f}, pin {'OK' if pin_ok else 'FAIL'}, sig0 {sigma0:.4f}):")
        for w in (0, 1, 2):
            print(f"    w={w}: shell power {shells[w]['power']:+.4f} (K={shells[w]['K']}, floor SE {shells[w]['floor_SE']:.3f})")
        print(f"    w={wp} [PLANTED]: est power {shells[wp]['power_est']:.2f}, mean|tr2| {shells[wp]['mean_abs']:.4f}")

    if not all_pin:
        out["verdict"] = "NO-TEST (pin failed on a draw)"
    else:
        # boundary clean iff w=1,2 shells within a few sigma of their floor
        clean = all(abs(out["draws"][k]["shells"][1]["power"]) < 3 * out["draws"][k]["shells"][1]["floor_SE"] and
                    abs(out["draws"][k]["shells"][2]["power"]) < 3 * out["draws"][k]["shells"][2]["floor_SE"]
                    for k in out["draws"])
        out["verdict"] = ("BOUNDARY-CLEAN: w=1,2 shells at floor (only ghost+noise); purity mass lives "
                          "at the planted weight -> purity-in-weight profile confirms sharp seal from the "
                          "purity angle" if clean else
                          "BOUNDARY-STRUCTURE: a low-weight shell carries resolvable mass above floor")
    print(f"\nVERDICT: {out['verdict']}")
    json.dump(out, open(os.path.join(RES, "unfold_U2a_boundary_purity_c5073.json"), "w"), indent=1)
    print("-> results/unfold_U2a_boundary_purity_c5073.json")


if __name__ == "__main__":
    main()
