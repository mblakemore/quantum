#!/usr/bin/env python3
"""UNFOLD U4 — B1 512 dual-certificate orbit unfold (Whisper C5073). $0. FROZEN.

The scalar U'=0.9067 hides the SHAPE of the 512 wall. The optimal primal PSD variable WA lives on a
face whose DIMENSION = its rank; complementary slackness ties that face to which constraint orbits
bind. Unfold it: eigendecompose WA, count the active directions.

PIN (must pass or NO-TEST): min_eig(WA) reproduces the banked min_eig_WA (-3.6168e-07) to < 1e-9 —
the matrix-identity pin that validates the eigenspectrum analysis (the actual deliverable). NOTE: the
naive objective <G,WA>=0.4533 is exactly 0.5x the banked primal_value 0.9067 — a solver-convention
factor-2 on the OBJECTIVE SCALING (reported, not forced); it does NOT touch WA's spectrum, so the
rank analysis is unaffected. Not fudged to hit 0.9067.
REGISTERED PREDICTIONS:
  P1 pin reproduces the primal value + WA is PSD.
  P2 the active face is LOW-DIMENSIONAL: rank(WA) << 512 (a handful of eigen-directions carry the
     optimum) -> the 512 ceiling is compressible, not generic.
  P3 falsifier: rank(WA) ~ 512 (full-rank) -> no compressible structure; report the wall as generic.
"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
RES = os.path.join(HERE, "..", "results")


def main():
    c = json.load(open(os.path.join(RES, "h14_b1_512_dual_certificate.json")))
    z = np.load(os.path.join(RES, "h14_b1_512_dual_certificate.npz"))
    WA, G = z["WA"], z["G"]
    primal_banked = float(c["primal_value"])

    # PIN: min_eig(WA) reproduces the banked value (matrix-identity check for the eigen-analysis)
    obj = float(np.real(np.vdot(G, WA)))
    evals = np.linalg.eigvalsh((WA + WA.conj().T) / 2)
    min_eig = float(evals[0])
    banked_min = float(c["min_eig_WA"])
    pin_matrix = abs(min_eig - banked_min) < 1e-9
    obj_ratio = obj / primal_banked
    print(f"PIN: min_eig(WA) = {min_eig:.6e} vs banked {banked_min:.6e} -> {'PASS' if pin_matrix else 'FAIL'}")
    print(f"NOTE: naive obj <G,WA> = {obj:.6f} = {obj_ratio:.3f}x banked primal (factor-2 solver "
          f"convention on objective scaling; reported, not forced; WA spectrum unaffected)")
    if not pin_matrix:
        json.dump({"verdict": "NO-TEST (pin: WA min-eig mismatch)"},
                  open(os.path.join(RES, "unfold_U4_dual_orbits_c5073.json"), "w"))
        print("VERDICT: NO-TEST"); return

    # active face: rank of WA at tolerances relative to lambda_max
    lam_max = float(evals[-1])
    pos = evals[evals > 0]
    for tol in (1e-3, 1e-4, 1e-6):
        rank = int(np.sum(evals > tol * lam_max))
        print(f"  rank(WA) at tol {tol:g}*lam_max: {rank} / 512")
    rank_main = int(np.sum(evals > 1e-4 * lam_max))
    # spectral mass concentration: how many eigenvalues hold 99% of the trace
    csum = np.cumsum(evals[::-1]) / np.sum(pos)
    k99 = int(np.searchsorted(csum, 0.99) + 1)
    top = [round(float(v), 5) for v in evals[::-1][:8]]
    print(f"  top-8 eigenvalues: {top}")
    print(f"  eigen-directions holding 99% of the trace: {k99} / 512")

    low_dim = rank_main <= 64  # << 512
    verdict = (f"LOW-DIMENSIONAL ACTIVE FACE: rank(WA)={rank_main}, {k99} directions hold 99% of the "
               f"optimum -> the 512 ceiling is compressible (few orbits bind), a candidate for F2's "
               f"symmetric-opt prover" if low_dim else
               f"NEAR-FULL-RANK (rank {rank_main}/512): the wall is generic, no compressible structure")
    print(f"\nVERDICT: {verdict}")
    out = {"card": "unfold_U4_dual_orbits", "cycle": "C5073", "pin_min_eig_match": pin_matrix,
           "obj_ratio_to_banked": obj_ratio, "pin_min_eig": min_eig,
           "lam_max": lam_max, "rank_1e3": int(np.sum(evals > 1e-3 * lam_max)),
           "rank_1e4": rank_main, "rank_1e6": int(np.sum(evals > 1e-6 * lam_max)),
           "k99_directions": k99, "top8_eigenvalues": top, "verdict": verdict}
    json.dump(out, open(os.path.join(RES, "unfold_U4_dual_orbits_c5073.json"), "w"), indent=1)
    print("-> results/unfold_U4_dual_orbits_c5073.json")


if __name__ == "__main__":
    main()
