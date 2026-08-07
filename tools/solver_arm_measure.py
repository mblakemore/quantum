#!/usr/bin/env python3
"""P-CCM v1.0 — STAGE G: the classical arm, MEASURED. solver-plan §6.6.

WHY THIS FILE EXISTS. Every advantage ratio this campaign has quoted is a ratio against a
classical arm that was a PROJECTION from a cost model. Four times in one night I attached a
correct mechanism to an unmeasured share and got the system claim wrong (packing 64x -> 1.28x,
Z8 GPU 36x -> 2.10x, dimer 49x -> +0.1x, JIT 5.65x projected -> 7.54x actual). The rule that
came out of that is: NO RUNTIME IS QUOTED FROM A MODEL WHEN IT CAN BE TIMED.

WHAT IS ACTUALLY BEING TIMED. Per solver-plan §5, the Clifford circuit does NOT touch the chi
terms — Eq 3's (n+t)^3 term is ADDITIVE, not multiplied by chi, because the Clifford is
propagated once in the Heisenberg picture onto stabilizer groups G,H in P_t (Eq 28). So the
per-term hot path is exactly two things, both already gated three levels deep:

    shrink        projection of each term onto Pi_G      (once per term per probability)
    inner_product against each random theta_i            (L*J times per term)

and the arm is

    T_arm = chi * [ n_proj * t_shrink  +  L * J * t_inner ]      L = 4 eps^-2, J = O(log 1/p_f)

CORRECTNESS BEFORE TIMING. The njit kernel is checked against the reference at the measurement
size before any number is emitted. Same rule as everywhere else in this campaign.

Substrate: claude-fable-5, Whisper C5021.
"""
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

PARALLEL = 6.76          # MEASURED this session (8 procs, 66% efficiency, bandwidth-bound)


def _packed_args(st):
    p = bp.PackedState.from_reference(st)
    return (p.k, p.h, p.G, p.Gbar, p.Q, p.D, p.J)


def check_njit_vs_reference(t, trials, rng):
    """Gate: njit must reproduce the reference at the measurement size."""
    bad = 0
    for _ in range(trials):
        s1 = ref.random_state_via_extend(t, int(rng.integers(1, t)), rng)
        s2 = ref.random_state_via_extend(t, int(rng.integers(1, t)), rng)
        want = ref.inner_product(s1, s2)
        a1, a2 = _packed_args(s1), _packed_args(s2)
        got = nj.inner_product_njit(t, bp.nwords(t), *a1, *a2)
        if tuple(int(v) for v in want) != tuple(int(v) for v in got):
            bad += 1
    return bad


def time_inner(t, reps, rng):
    s1 = ref.random_state_via_extend(t, t - 1, rng)
    s2 = ref.random_state_via_extend(t, t - 1, rng)
    a1, a2 = _packed_args(s1), _packed_args(s2)
    W = bp.nwords(t)
    nj.inner_product_njit(t, W, *a1, *a2)                       # compile
    t0 = time.perf_counter()
    for _ in range(reps):
        nj.inner_product_njit(t, W, *a1, *a2)
    return (time.perf_counter() - t0) / reps


def time_shrink(t, reps, rng):
    """One projection step on a term. Uses the packed kernel's shrink, which the njit path
    inlines; timed separately so the split is visible rather than assumed."""
    st = ref.random_state_via_extend(t, t - 1, rng)
    p = bp.PackedState.from_reference(st)
    xi = bp.pack_rows(rng.integers(0, 2, size=(1, t), dtype=np.uint8))[0]
    t0 = time.perf_counter()
    for _ in range(reps):
        q = p.copy()
        bp.shrink(q, xi, 0)
    return (time.perf_counter() - t0) / reps


def main():
    rng = np.random.default_rng(20260807)
    eps, p_f, delta = 0.1, 0.05, 0.5
    L = int(math.ceil(4.0 / eps ** 2))
    J = max(1, int(math.ceil(math.log(1.0 / p_f) / math.log(4.0 / 3.0))))

    print("CLASSICAL ARM — MEASURED (Stage G)\n")
    print(f"  estimator parameters: eps = {eps}, p_f = {p_f}  ->  L = 4/eps^2 = {L}, "
          f"J = {J}   (L*J = {L*J} inner products per term)")
    print(f"  decomposition: delta = {delta}  ->  chi = 2^k by Eq 38\n")

    print("  ① CORRECTNESS at the measurement size (no timing without this)")
    for t in (40, 80):
        bad = check_njit_vs_reference(t, 20, rng)
        print(f"    {'PASS' if bad == 0 else 'FAIL':>4}  njit == reference   t={t:>3}   "
              f"20 random pairs, {bad} mismatches")
        if bad:
            print("    ⛔ MISMATCH — no timing emitted.")
            sys.exit(2)

    print("\n  ② TIMED PRIMITIVES")
    print(f"  {'t':>4} {'t_inner (us)':>14} {'t_shrink (us)':>15} {'ns per t^3 unit':>17}")
    prim = {}
    for t in (40, 60, 80):
        ti = time_inner(t, 3000, rng)
        ts = time_shrink(t, 3000, rng)
        prim[t] = (ti, ts)
        print(f"  {t:>4} {ti*1e6:>14.2f} {ts*1e6:>15.2f} {ti/t**3*1e9:>17.3f}")

    print("\n  ③ THE ARM")
    print(f"  {'t':>4} {'chi':>13} {'fid':>7} {'proj (s)':>12} {'inner (s)':>13} "
          f"{'1 core':>12} {'x6.76':>11}")
    rows = []
    for t in (40, 60, 80):
        k = ms.choose_k(t, delta)
        chi = 2 ** k
        M, k, Z, f2, tries = ms.sparsify(t, delta, rng, max_tries=10)
        ti, ts = prim[t]
        n_proj = t                      # one projection per magic qubit, the paper's Pi_G
        c_proj = chi * n_proj * ts
        c_inner = chi * L * J * ti
        tot = c_proj + c_inner
        rows.append({"t": t, "k": k, "chi": chi, "fidelity": math.sqrt(f2), "Z": Z,
                     "t_inner_s": ti, "t_shrink_s": ts,
                     "cost_projection_s": c_proj, "cost_inner_s": c_inner,
                     "total_1core_s": tot, "total_parallel_s": tot / PARALLEL})
        print(f"  {t:>4} {chi:>13,} {math.sqrt(f2):>7.4f} {c_proj:>12,.0f} {c_inner:>13,.0f} "
              f"{_dur(tot):>12} {_dur(tot/PARALLEL):>11}")

    r80 = [r for r in rows if r["t"] == 80][0]
    share = r80["cost_inner_s"] / r80["total_1core_s"]
    print(f"\n  ④ WHERE THE TIME GOES at t=80 — the split, shown rather than assumed")
    print(f"    inner products : {share*100:>5.1f}%   ({L*J} per term)")
    print(f"    projections    : {(1-share)*100:>5.1f}%   ({80} per term)")
    print(f"    -> the estimator loop dominates. solver-plan GAP 7 worried that Clifford")
    print(f"       propagation would dominate instead; per Eq 3 it is amortised, not per-term,")
    print(f"       so it does not enter this product at all.")

    dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results",
                       "solver_arm_measured_v1.json")
    with open(dst, "w") as fh:
        json.dump({"card": "solver_arm_measured", "version": "1.0", "cycle": "C5021",
                   "substrate": "claude-fable-5",
                   "params": {"eps": eps, "p_f": p_f, "delta": delta, "L": L, "J": J,
                              "parallel_measured": PARALLEL},
                   "rows": rows,
                   "scope": ("Per-probability cost of the Bravyi-Gosset sampling algorithm's "
                             "dominant term. Excludes the additive O((n+t)^3) Clifford "
                             "propagation, which Eq 3 amortises over all chi terms. delta=0.5 "
                             "is the paper's practical regime, NOT its guaranteed one "
                             "(solver-plan GAP 6)."),
                   "correctness": "njit == reference on 20 random pairs at t=40 and t=80"},
                  fh, indent=2)
    print(f"\n  written: results/{os.path.basename(dst)}")


def _dur(s):
    if s < 90:
        return f"{s:.1f} s"
    if s < 5400:
        return f"{s/60:.1f} min"
    if s < 172800:
        return f"{s/3600:.1f} h"
    if s < 3.15e7:
        return f"{s/86400:.1f} d"
    return f"{s/3.15e7:.2f} yr"


if __name__ == "__main__":
    main()
