#!/usr/bin/env python3
"""P-CCM v1.0 — THE ESTIMATOR ROUTE: past the O(chi^2) wall.

WHY SWITCH. The exact norm is O(chi^2), which is what capped the C5024 ladder at t=46 (8 min);
t=56 would be 1.1e9 inner products, about 16 hours. Component ④ replaces it with O(chi*L*J).

THE SPEEDUP I QUOTED WAS WRONG AND IS CORRECTED HERE. I posted "145x" for that swap. It used
L*J = 225, i.e. eps = 0.3 = 30% relative error per norm — too loose to compare against an oracle —
AND it compared ONE norm's estimator cost against TWO norms' exact cost. The real figures:

    eps = 0.3   L*J =  225   ->  72.8x     (but 30% error: not usable for an oracle check)
    eps = 0.2   L*J =  500   ->  32.8x
    eps = 0.1   L*J = 2000   ->   8.2x     <- at a precision that can actually be checked

and the estimator only wins at all once chi > 2*L*J. Quoting a speedup at a precision I would not
use is the same shape as a weak baseline.

TWO THINGS THAT MAKE THE RATIO CHEAP AND SCALE-FREE:

  * COMMON RANDOM NUMBERS. P = 2^-u ||Pi_G psi||^2 / 2^-v ||Pi_H psi||^2. Estimating numerator and
    denominator with the SAME random theta_i correlates their fluctuations, and since Pi_G is a
    sub-projector of Pi_H the two overlaps move together, so the RATIO is far better determined
    than either norm. The benefit is MEASURED below against the exact answer, not assumed.
  * The 2^t prefactor of Eq 15 CANCELS in the ratio, so nothing here forms a number that scales
    with t. That is the structural version of the C5024 lesson: the previous harness produced nan
    twice because every magnitude in the expression decayed like 2^-t. Here none of them do.

ERROR BARS ARE MEASURED, NOT ASSERTED: L samples in J batches, the reported value is the median of
the batch ratios and the reported uncertainty is their spread.

A PRE-LAUNCH CHECK THAT PAID: component ④a's dim_distribution overflowed float64 at n = 44
(|S_n^n| = 8*2^(n+n(n+1)/2), and n+n(n+1)/2 crosses 1024 at n = 43), so every t >= 44 run would
have raised OverflowError immediately. Predicted from the formula, checked, and fixed in log space
BEFORE launching a multi-hour job — rather than discovered inside one.

Substrate: claude-fable-5, Whisper C5025. Creator directive: "switch to the estimator route and
push past t=56".
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stabilizer_rank_kernel as ref                                        # noqa: E402
import stabilizer_rank_bitpacked as bp                                      # noqa: E402
import stabilizer_njit as nj                                                # noqa: E402
import magic_sparsify as ms                                                 # noqa: E402
import gadgetize as gd                                                      # noqa: E402
import stabilizer_estimator as se                                           # noqa: E402
import large_run as lr                                                      # noqa: E402


def _amp(packed_terms, theta_packed, t, W):
    """<theta|Pi psi> = SUM_a c_a <theta|phi_a>, through the njit kernel."""
    acc = 0j
    for c, s in packed_terms:
        acc += c * ref.triple_to_complex(nj.inner_product_njit(t, W, *s, *theta_packed))
    return acc


def estimate_ratio(pn, pd, t, u, v, L, J, rng, progress=None):
    """P = 2^(v-u) * ||Pi_G psi||^2 / ||Pi_H psi||^2 by common-random-number sampling.

    Returns (P_hat, spread, per_batch, n_inner). The 2^t prefactor of Eq 15 cancels in the ratio,
    so no quantity here scales with t."""
    W = bp.nwords(t)
    batch = []
    n_inner = 0
    for j in range(J):
        sg = sh = 0.0
        for i in range(L):
            th = se.random_stabilizer_state(t, rng)
            tp = lr._pack(th)
            ag = _amp(pn, tp, t, W)
            ah = _amp(pd, tp, t, W)
            n_inner += len(pn) + len(pd)
            sg += abs(ag) ** 2
            sh += abs(ah) ** 2
        batch.append((2.0 ** (v - u)) * (sg / sh) if sh > 0 else float("nan"))
        if progress:
            progress(j + 1, J, batch[-1])
    good = [b for b in batch if math.isfinite(b)]
    if not good:
        return float("nan"), float("nan"), batch, n_inner
    return float(np.median(good)), float(np.std(good)), batch, n_inner


def prepare(n, nt, delta, seed, rng_seed=None):
    """Build a T-sensitive instance and project its terms onto Pi_G and Pi_H."""
    rng = np.random.default_rng(seed)
    gates = lr.build_instance(n, nt, rng)
    build, t = gd.gadgetize(gates, n)
    Qout, x = [0], (0,)
    want = gd.brute_force_pout(gates, n, Qout, x)
    if abs(want - 0.5) < 0.05 or want < 1e-9 or want > 1 - 1e-9:
        return None
    y = tuple(int(vv) for vv in rng.integers(0, 2, size=t))
    pre = [g for j in range(t) for g in (("SDG", n + j), ("H", n + j))]
    V = pre + build(y)
    ng = [gd.pauli_Z(n + t, q, x[i]) for i, q in enumerate(Qout)] + \
         [gd.pauli_Z(n + t, n + j, y[j]) for j in range(t)]
    dg = [gd.pauli_Z(n + t, n + j, y[j]) for j in range(t)]
    G, u = gd.heisenberg_reduce(V, n, t, ng)
    H, v = gd.heisenberg_reduce(V, n, t, dg)
    M, k, Z, fid2, _ = ms.sparsify(t, delta, rng, max_tries=10)
    bits = ms.term_bitstrings(M, k)
    coeff = ms.coefficient(k, Z)
    t0 = time.perf_counter()
    pn = lr.projected_terms(bits, coeff, [(P.k, P.a, P.b) for P in G])
    pd = lr.projected_terms(bits, coeff, [(P.k, P.a, P.b) for P in H])
    return {"t": t, "k": k, "chi": 2 ** k, "fid2": fid2, "u": u, "v": v, "pn": pn, "pd": pd,
            "want": want, "t_project": time.perf_counter() - t0, "rng": rng}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=5)
    ap.add_argument("--nt", type=int, default=56)
    ap.add_argument("--delta", type=float, default=0.5)
    ap.add_argument("--L", type=int, default=64)
    ap.add_argument("--J", type=int, default=9)
    ap.add_argument("--seed", type=int, default=20260807)
    ap.add_argument("--calibrate", action="store_true",
                    help="also compute the EXACT O(chi^2) answer and compare (small t only)")
    a = ap.parse_args()

    print("ESTIMATOR ROUTE — past the O(chi^2) wall\n")
    print(f"  L = {a.L} samples x J = {a.J} batches = {a.L*a.J} random stabilizer states per norm")
    print("  common random theta across numerator and denominator; the 2^t prefactor cancels")
    print("  in the ratio, so nothing here scales with t.\n")

    inst = None
    for att in range(24):
        inst = prepare(a.n, a.nt, a.delta, a.seed + 977 * att)
        if inst is not None:
            break
    if inst is None:
        print("  no T-sensitive instance found"); sys.exit(2)

    t, chi = inst["t"], inst["chi"]
    print(f"  instance: n = {a.n}, t = {t}, k = {inst['k']}, chi = {chi:,}, "
          f"fid^2 = {inst['fid2']:.4f}")
    print(f"  survivors: Pi_G {len(inst['pn']):,}  Pi_H {len(inst['pd']):,}   "
          f"(projection took {inst['t_project']:.1f}s)")
    print(f"  P_oracle = {inst['want']:.6f}   (brute force costs 2^n, independent of t)\n")

    exact = None
    if a.calibrate:
        t0 = time.perf_counter()
        nG = lr.norm2_exact(inst["pn"], t)
        nH = lr.norm2_exact(inst["pd"], t)
        exact = (2.0 ** (inst["v"] - inst["u"])) * (nG / nH)
        print(f"  CALIBRATION: exact O(chi^2) = {exact:.6f} "
              f"({len(inst['pn'])*(len(inst['pn'])+1)//2 + len(inst['pd'])*(len(inst['pd'])+1)//2:,}"
              f" inner products, {time.perf_counter()-t0:.1f}s)\n")

    def prog(j, J, val):
        print(f"    batch {j:>2}/{J}: ratio = {val:.6f}", flush=True)

    t0 = time.perf_counter()
    P, sd, batches, n_inner = estimate_ratio(inst["pn"], inst["pd"], t, inst["u"], inst["v"],
                                             a.L, a.J, inst["rng"], progress=prog)
    el = time.perf_counter() - t0
    sem = sd / math.sqrt(len([b for b in batches if math.isfinite(b)]))

    print(f"\n  ESTIMATE   P = {P:.6f}  +/- {sem:.6f} (sem over batches; batch sd {sd:.6f})")
    print(f"  ORACLE     P = {inst['want']:.6f}")
    print(f"  |err|        = {abs(P - inst['want']):.6f}")
    if exact is not None:
        print(f"  vs EXACT O(chi^2) = {exact:.6f}   |estimator - exact| = {abs(P-exact):.6f}")
    print(f"\n  {n_inner:,} inner products in {el:.1f}s "
          f"({el/max(1,n_inner)*1e6:.2f} us each)")
    exact_cost = len(inst['pn']) * (len(inst['pn']) + 1) // 2 + \
        len(inst['pd']) * (len(inst['pd']) + 1) // 2
    print(f"  the exact O(chi^2) route would need {exact_cost:,} "
          f"({exact_cost/max(1,n_inner):.1f}x more, ~{exact_cost*el/max(1,n_inner)/3600:.1f} h)")

    out = {"card": "estimator_run", "version": "1.0", "cycle": "C5025",
           "substrate": "claude-fable-5", "n": a.n, "t": t, "k": inst["k"], "chi": chi,
           "fidelity2": inst["fid2"], "L": a.L, "J": a.J,
           "P_estimate": P, "sem": sem, "batch_sd": sd, "batches": batches,
           "P_oracle": inst["want"], "abs_err": abs(P - inst["want"]),
           "P_exact_chi2": exact, "inner_products": n_inner, "wall_s": el,
           "exact_route_inner_products": exact_cost}
    dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results",
                       f"estimator_run_t{t}_v1.json")
    with open(dst, "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"  written: results/{os.path.basename(dst)}")


if __name__ == "__main__":
    main()
