#!/usr/bin/env python3
"""DOOR-B PREPARED-STATE PURITY — a $0 perturbation on flown collision data (Whisper C5073).

Creator: "throw perturbations at existing data to extract info from our own collisions."
F103-lineage: a NEW observable from already-flown shots, zero QPU. FROZEN before compute
(commit precedes the run — the F103/F122 discipline).

THE OBSERVABLE (frozen): prepared-state purity tr(rho^2) of each sealed door-b draw, via the
two-copy destructive SWAP test. Two-copy Bell sampling of rho(x)rho: SWAP = prod_j SWAP_j,
SWAP_j = +1 on the symmetric Bell triplet {Phi+,Phi-,Psi+}, -1 on the antisymmetric SINGLET
Psi-. So tr(rho^2) = E[ (-1)^(#pairs in Psi-) ]. The singlet Psi- is the Y-labelled Bell state
= Weyl (x=1,z=1) under the flown-matched mapping. F122 read ONE Pauli's amplitude from these
shots; this reads the whole state's purity from the SAME events.

CONVENTION (imported, not re-derived — the B1-G3 lesson): g2 = exp142_robust_decoder_sim, the
flown-matched decoder validated on the revealed n6 rung and used for the F122/A2 grades.
g2.outcome_to_bits(s, n, mapping) -> per-pair Weyl (x|z); pair j is the singlet iff x_j & z_j.

PIN (must pass or NO-TEST): tr(rho^2) in [1/2^n, 1] for every draw (the physical bound for any
state). CONTROL: the FLIPPED reading (symmetric-as-singlet) must FAIL that bound on the same
data — proving the pin discriminates the convention, not just admits it.

REGISTERED PREDICTIONS (frozen):
  P1 (pin): all 5 draws land in [1/2^16, 1]. Fail -> NO-TEST (convention error), reported.
  P2 (cross-draw consistency): the 5 draws are one circuit family / one prep quality, so their
     purities should cluster; a wild outlier flags a bad draw (candidate: first-FAIL / i3-w13).
  P3 (soft, report-only): lower purity <-> more mixed <-> larger delivered eps (F122 eps_del
     ~0.16-0.18 class). Consistency check, not a gate.
Draws: doorb_raw_science (original WIN) · refly · dist_i1 · dist_i2 · dist_i3 (n=16 each).
"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import exp142_robust_decoder_sim as g2

N = 16
DRAWS = {
    "original(WIN)": "doorb_raw_science_n16_elder.json",
    "refly":         "doorb_refly_raw_science_n16_elder.json",
    "i1":            "doorb_dist_i1_raw_science_n16_elder.json",
    "i2":            "doorb_dist_i2_raw_science_n16_elder.json",
    "i3(w13)":       "doorb_dist_i3_raw_science_n16_elder.json",
}
RES = os.path.join(HERE, "..", "results")


def purity(bitstrings, mapping, flip=False):
    """tr(rho^2) = mean over shots of (-1)^(#singlet pairs). flip=True uses symmetric-as-singlet
    (the control that must fail the physical bound)."""
    acc = 0.0
    for s in bitstrings:
        q = g2.outcome_to_bits(s, N, mapping)          # (x_0..x_15 | z_0..z_15)
        y = int(np.sum((q[:N] == 1) & (q[N:] == 1)))   # # pairs in Psi- (Weyl Y)
        k = (N - y) if flip else y
        acc += (-1) ** k
    return acc / len(bitstrings)


def main():
    mapping = g2.calibrate_bell_mapping()
    lo = 1.0 / 2 ** N
    print(f"physical bound: purity in [{lo:.2e}, 1]")
    out = {"card": "doorb_purity_extraction", "cycle": "C5073", "n": N,
           "observable": "tr(rho^2) via two-copy SWAP, singlet=Psi-=Weyl(1,1)",
           "convention": "imported g2=exp142_robust_decoder_sim (flown-matched, F122/A2-validated)",
           "bound": [lo, 1.0], "draws": {}}
    vals = []
    for name, fn in DRAWS.items():
        p = os.path.join(RES, fn)
        if not os.path.exists(p):
            print(f"  {name}: MISSING {fn}"); continue
        bits = json.load(open(p))["shots"]
        pur = purity(bits, mapping, flip=False)
        ctrl = purity(bits, mapping, flip=True)
        in_bound = lo <= pur <= 1.0
        ctrl_fails = not (lo <= ctrl <= 1.0)
        vals.append(pur)
        out["draws"][name] = {"purity": pur, "n_shots": len(bits), "in_bound": in_bound,
                              "flipped_control": ctrl, "control_fails_bound": ctrl_fails}
        print(f"  {name:14s}: purity {pur:+.4f}  ({len(bits):,} shots)  "
              f"in-bound {in_bound}  | flipped-ctrl {ctrl:+.4f} fails-bound {ctrl_fails}")
    if not vals:
        print("NO-TEST: no draws"); return
    all_in = all(out["draws"][k]["in_bound"] for k in out["draws"])
    ctrl_ok = all(out["draws"][k]["control_fails_bound"] for k in out["draws"])
    spread = max(vals) - min(vals)
    out["P1_all_in_bound"] = all_in
    out["P1_control_discriminates"] = ctrl_ok
    out["P2_spread"] = spread
    out["P2_mean"] = float(np.mean(vals))
    verdict = ("PURITY-EXTRACTED" if all_in else "NO-TEST (pin: a draw left the physical bound)")
    out["verdict"] = verdict
    print(f"\nP1 pin: all draws in-bound {all_in} · flipped control fails-bound {ctrl_ok} "
          f"(pin {'DISCRIMINATES' if ctrl_ok else 'does NOT discriminate — weak'})")
    print(f"P2: mean purity {np.mean(vals):.4f}, spread {spread:.4f} across {len(vals)} draws")
    print(f"VERDICT: {verdict}")
    json.dump(out, open(os.path.join(RES, "doorb_purity_extraction_c5073.json"), "w"), indent=1)
    print("-> results/doorb_purity_extraction_c5073.json")


if __name__ == "__main__":
    main()
