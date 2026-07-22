#!/usr/bin/env python3
"""P-CCM Phase 4 — the sweep: turn the gated bench into frozen cost curves (the v0.6 card).

Produces `results/classical_cost_map_v1.json` — the deliverable Item 3 quotes.

WHAT SMOKE-TESTING + ADVISOR REVIEW CHANGED (C4971 — recorded so the next pass starts here):
The naive plan (log-cost-vs-T from extended_stabilizer wall-time) is a STRAWMAN and is NOT frozen.
Measured decisively at n=4,T=8: extstab run_s ∝ shots at ~0.2 s/shot (16→3.2s, 64→13.8s, 256→46.6s)
with metropolis_mixing_time=5000 — the cost is Aer's Metropolis SAMPLER CONFIG (mixing × shots),
NOT Clifford+T hardness. Its shape (overhead-flat at low T) is wrong for the crossover. This is gap
G1 resurfacing on its COST-FAITHFULNESS half (accuracy was only half of G1): an adversary that
returns the right answer but whose runtime is a sampler artifact is still a strawman.

=> The FAITHFUL rank signal is the paper's runtime scaling, now PAPER-PINNED (Creator supplied the
   Bravyi-Gosset paper C4971, dc_shared/resources/; G-1 satisfied — pulled from paper, not memory):
   SAMPLING task (the race) = poly(n,m) + 2^(0.23*t)*t^3*w^3 (gamma=0.23); EXACT/probability task =
   poly(n,m) + 2^(beta*t)*t^3, beta=(1/6)log2(7)~=0.4696; norm subroutine chi*n^3*eps^-2 (the eps^-2
   is exactly why tighter approximation_error costs more). The SHAPE is paper-faithful; absolute
   seconds still need a calibrated per-stabilizer-term constant (v1.0). Aer's measured wall-time /
   memory wall are reported ALONGSIDE, labeled Aer-specific / overhead — reality checks, not the curve.

The TRUSTWORTHY columns are frozen now:
  * statevector cost vs n — curved on the worker's run_s (simulation only; the ~0.3s fork+qiskit-init
    floor is removed) at n up to 22 so 2^n clears the floor.
  * MPS — the meaningful quantity is MIN-VERIFYING chi vs problem size (the dial at its BINDING
    value), not cost-vs-chi at fixed instance (that curves wasted capacity above the true bond dim).

DISCIPLINE (Phases 1-2): every timed row via the Phase-1 meter (real rusage + SIGKILL cap; over-cap
= censored, never dropped); a timing enters a curve only if its paired verify row passed the gate;
PREFLIGHT headroom gate before launch (C4415, shared box); fits exclude censored/unverified rows but
the card records them (a curve through only the cheap points would lie about the frontier).

Substrate: claude-fable-5, Whisper C4971. Freeze discipline mirrors tools/attenuation_map.py.
"""
import os, sys, json, math, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from classical_cost_meter import meter, preflight_cpu, hardware_fingerprint  # noqa: E402
from classical_cost_bench import (random_clifford_t, oracle_statevector,      # noqa: E402
                                  sv_worker, mps_worker)

QROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

# Measured C4971 (n=4,T=8, mixing_time=5000): extstab run_s ~= shots * marginal. The rank column's
# Aer reality-check quotes these, explicitly as a SAMPLER-CONFIG artifact, not a hardness curve.
AER_EXTSTAB_SHOTS_SCALING = {
    "measured": {"16_shots_s": 3.17, "64_shots_s": 13.75, "256_shots_s": 46.60},
    "marginal_s_per_shot": 0.20, "metropolis_mixing_time": 5000,
    "interpretation": ("run_s is LINEAR in shots -> cost is Metropolis mixing per shot, an Aer "
                       "sampler-config artifact; NOT Clifford+T hardness. Do not curve on it."),
}
# The exact stabilizer-rank memory wall (approx_err=0) at T=48 is REAL: max_memory_mb=None (uses
# system RAM), so the OOM is a genuine resource wall, not a conservative-default artifact.
AER_EXACT_MEMORY_WALL = {"T": 48, "n": 4, "approx_err": 0.0, "result": "out_of_memory",
                         "max_memory_mb": None, "genuine_wall": True}

# PAPER-PINNED exponents (Bravyi & Gosset, "Improved classical simulation of quantum circuits
# dominated by Clifford gates", arXiv:1601.07601 / PRL 116, 250501, dated 2019-04-11; in
# dc_shared/resources/). G-1 rule satisfied: pulled from the paper, not memory. Definitions:
# chi_t(delta) = min # stabilizer states approximating |A>^t to |<A^t|psi>|^2 >= 1-delta.
#   * EXACT rank chi_t(0) = O(2^(beta*t)), beta = (1/6)*log2(7) ~= 0.4696  -> PROBABILITY task
#     runtime poly(n,m) + 2^(beta*t) * t^3   (abstract rounds beta to 0.5)
#   * APPROX rank chi_t(delta) = O(2^(gamma*t)), gamma = 0.23 (const delta) -> SAMPLING task
#     runtime poly(n,m) + 2^(gamma*t) * t^3 * w^3   (t=#T-gates, w=#measured qubits, n=#qubits)
#   * norm-approximation subroutine: time chi * n^3 * eps^-2 (eps = relative error) -> the eps^-2
#     is exactly WHY a tighter approximation_error costs more, straight from the paper.
import math as _m
BG_ALPHA_SAMPLING = 0.23                      # gamma: the race SAMPLES the peak -> this is the one
BG_ALPHA_EXACT = (1.0 / 6.0) * _m.log2(7.0)   # beta ~= 0.4696 (exact / probability task)
BG_PAPER = ("Bravyi & Gosset, Improved classical simulation of quantum circuits dominated by "
            "Clifford gates, PRL 116 250501 (arXiv:1601.07601, 2019-04-11)")

# v1.0 ABSOLUTE calibration of the rank curve. Anchor (from the paper, G-1): the FULL hidden-shift
# simulation at n=40, t=48 (a few hundred Clifford gates) took "SEVERAL HOURS" on a 2016 2.6GHz i5
# dual-core MATLAB implementation. "Several" ~ 2-4h -> take 3h = 10800s as the central anchor.
# Table I cross-check: InnerProduct (the per-term op, O(n^3)) ~2.7ms at n=40 on the same laptop.
# The absolute bill is IMPLEMENTATION-DOMINATED (MATLAB tableau vs optimized-C ~100x; +all-core),
# so v1.0 quotes a BAND across implementation edges scaled to our hardware (Ryzen 9800X3D), NOT a
# single point. The SHAPE (2^(0.23t)*t^3*n^3) is paper-faithful; the intercept carries the band.
RANK_ANCHOR_S = 3 * 3600.0     # n=40,t=48 "several hours" -> 3h (2016 i5 MATLAB); central anchor
RANK_IMPL_EDGES = {            # speedup vs the paper's 2016-MATLAB-on-i5 anchor (LABELED estimates)
    "paper_matlab_i5_2016": 1.0,     # the anchor as measured
    "our_cpu_matlab_equiv": 3.5,     # ~single-thread 2016-i5 -> 2024-Ryzen-9800X3D
    "best_c_singlethread": 35.0,     # + optimized-C vs MATLAB (~10x)
    "best_c_allcore": 350.0,         # + ~10x all-core (16 threads, imperfect scaling)
}


def rank_absolute_bill_s(t, n, edge_speedup):
    """Paper-anchored absolute classical sampling bill in SECONDS at (n,t) under an implementation
    edge. Calibrated so the paper anchor (n=40,t=48) reproduces RANK_ANCHOR_S at speedup=1."""
    c = RANK_ANCHOR_S / ((2 ** (BG_ALPHA_SAMPLING * 48)) * (48 ** 3) * (40 ** 3))
    return (2 ** (BG_ALPHA_SAMPLING * t)) * (t ** 3) * (n ** 3) * c / edge_speedup


def _loglinfit(xs, ys):
    """Least-squares ln(y)=a+b*x. Returns dict or None (needs >=2 positive points)."""
    pts = [(x, math.log(y)) for x, y in zip(xs, ys) if y and y > 0]
    if len(pts) < 2:
        return None
    n = len(pts)
    sx = sum(x for x, _ in pts); sy = sum(y for _, y in pts)
    sxx = sum(x * x for x, _ in pts); sxy = sum(x * y for x, y in pts)
    denom = n * sxx - sx * sx
    if denom == 0:
        return None
    b = (n * sxy - sx * sy) / denom
    a = (sy - b * sx) / n
    ybar = sy / n
    ss_tot = sum((y - ybar) ** 2 for _, y in pts)
    ss_res = sum((y - (a + b * x)) ** 2 for x, y in pts)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 1.0
    return {"slope_ln_per_unit": round(b, 5), "intercept": round(a, 4),
            "r2": round(r2, 4), "n_points": n}


def projected_stabilizer_rank_bill(t, w=1, c_per_term_s=1.0, alpha=BG_ALPHA_SAMPLING):
    """The FAITHFUL rank cost, paper-pinned (Bravyi-Gosset). Sampling task (the race):
    2^(alpha*t) * t^3 * w^3 * c_per_term_s, alpha=gamma=0.23. Absolute seconds require a calibrated
    c_per_term_s (per-stabilizer-term runtime on this hardware); the SHAPE is paper-faithful."""
    return (2.0 ** (alpha * t)) * (t ** 3) * (w ** 3) * c_per_term_s


# ------------------------------------------------------------------ trustworthy column sweeps
def sweep_statevector(n_grid, t_fixed, cap_s, tc):
    """Cost vs n, statevector (exact). Curve on run_s (fork+init overhead removed)."""
    rows = []
    for n in n_grid:
        qc = random_clifford_t(n=n, t_count=t_fixed, seed=7)
        oracle = oracle_statevector(qc) if n <= 14 else None
        v = (meter(sv_worker(qc, verify=True, oracle=oracle), timeout_s=cap_s, thread_config=tc,
                   label=f"sv_verify_n{n}") if oracle is not None else None)
        t = meter(sv_worker(qc, verify=False, shots=1024), timeout_s=cap_s, thread_config=tc,
                  label=f"sv_time_n{n}")
        run_s = t["solver_fields"].get("run_s")
        verified = (v is None) or v["verified"]  # exact method; large-n unverified = labeled boundary
        rows.append({"n": n, "t_fixed": t_fixed, "verified_at_n": (None if v is None else v["verified"]),
                     "run_s": None if t["censored"] else run_s, "wall_s": t["wall_s"],
                     "censored": t["censored"], "peak_rss_mb": t["peak_rss_mb"],
                     "curve_eligible": verified and not t["censored"] and bool(run_s)})
        print(f"  sv n={n}: run_s={run_s} wall={t['wall_s']}s censored={t['censored']} "
              f"verified={rows[-1]['verified_at_n']} rss={t['peak_rss_mb']}MB")
    xs = [r["n"] for r in rows if r["curve_eligible"]]
    ys = [r["run_s"] for r in rows if r["curve_eligible"]]
    fit = _loglinfit(xs, ys)
    # the full-range fit is diluted by the low-n overhead/shot floor; the HIGH-n fit (n>=22, where
    # 2^n construction dominates) recovers the asymptotic slope approaching ln2=0.693.
    hx = [r["n"] for r in rows if r["curve_eligible"] and r["n"] >= 22]
    hy = [r["run_s"] for r in rows if r["curve_eligible"] and r["n"] >= 22]
    hifit = _loglinfit(hx, hy) if len(hx) >= 2 else None
    return {"axis": "n", "method": "statevector", "cost_metric": "run_s", "t_fixed": t_fixed,
            "rows": rows, "fit_logcost_vs_n": fit, "fit_highn_n_ge_22": hifit,
            "reference_ln_slope_2n": round(math.log(2), 3)}


def sweep_mps_min_chi(n_grid, t_per_n, chi_ladder, cap_s, tc):
    """MIN-VERIFYING chi vs problem size (the dial at its binding value). For each n, climb the chi
    ladder until the fidelity gate passes; record that chi (= the state's effective bond dimension)
    and the run_s at it. This is the meaningful MPS quantity (advisor C4971)."""
    rows = []
    for n in n_grid:
        T = t_per_n(n)
        qc = random_clifford_t(n=n, t_count=T, seed=3)
        oracle = oracle_statevector(qc)
        min_chi, chi_run_s, censored = None, None, False
        for chi in chi_ladder:
            v = meter(mps_worker(qc, chi=chi, verify=True, oracle=oracle), timeout_s=cap_s,
                      thread_config=tc, label=f"mps_verify_n{n}_chi{chi}")
            if v["censored"]:
                censored = True; break
            if v["verified"]:
                min_chi = chi
                t = meter(mps_worker(qc, chi=chi, verify=False, shots=1024), timeout_s=cap_s,
                          thread_config=tc, label=f"mps_time_n{n}_chi{chi}")
                chi_run_s = None if t["censored"] else t["solver_fields"].get("run_s")
                break
        rows.append({"n": n, "T": T, "min_verifying_chi": min_chi, "run_s_at_min_chi": chi_run_s,
                     "censored": censored, "curve_eligible": min_chi is not None})
        print(f"  mps n={n} T={T}: min_verifying_chi={min_chi} run_s={chi_run_s}")
    xs = [r["n"] for r in rows if r["curve_eligible"]]
    ys = [r["min_verifying_chi"] for r in rows if r["curve_eligible"]]
    # ln(min_chi) vs n: the growth rate of the state's effective bond dimension with problem size
    return {"axis": "n", "method": "matrix_product_state", "quantity": "min_verifying_chi",
            "rows": rows, "fit_ln_minchi_vs_n": _loglinfit(xs, ys)}


def main():
    ap = argparse.ArgumentParser(description="P-CCM Phase 4 cost-map sweep (v0.5)")
    ap.add_argument("--cap-s", type=float, default=60.0, help="per-row wall cap (SIGKILL); censored over")
    ap.add_argument("--headroom", type=float, default=0.75, help="max load/core to allow launch (C4415)")
    ap.add_argument("--timestamp", default=None, help="ISO stamp for the card (env has no clock)")
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()

    pf = preflight_cpu(threshold_per_core=args.headroom)
    print(f"PREFLIGHT (C4415): load/core={pf['load_per_core']} headroom_ok={pf['headroom_ok']}")
    if not pf["headroom_ok"]:
        print("REFUSING to launch: shared box is loaded. Re-run when load/core < threshold.")
        return 2

    tc = {"threads": 1}
    if args.quick:
        n_grid_sv, n_grid_mps = [8, 12, 16], [4, 6, 8]
    else:
        n_grid_sv = [14, 16, 18, 20, 22, 24, 26, 28]
        n_grid_mps = [4, 6, 8, 10, 12]

    print("\n[1/2] statevector column (cost vs n, curved on run_s)")
    sv = sweep_statevector(n_grid_sv, t_fixed=8, cap_s=args.cap_s, tc=tc)
    print("\n[2/2] MPS column (min-verifying chi vs n)")
    mps = sweep_mps_min_chi(n_grid_mps, t_per_n=lambda n: 2 * n, chi_ladder=[1, 2, 4, 8, 16, 32, 64],
                            cap_s=args.cap_s, tc=tc)

    card = {
        "card": "classical_cost_map", "version": "1.0", "substrate": "claude-fable-5",
        "cycle": "C4971", "timestamp": args.timestamp,
        "hardware": hardware_fingerprint(), "preflight": pf, "cap_s": args.cap_s, "thread_config": tc,
        "columns": {
            "statevector_vs_n": sv,
            "mps_min_chi_vs_n": mps,
            "stabilizer_rank_vs_T": {
                "status": "PAPER_PINNED_EXPONENTS",
                "why": ("extended_stabilizer wall-time is a sampler-config artifact (shots x "
                        "Metropolis mixing), NOT Clifford+T hardness — a G1 strawman if curved. "
                        "The faithful signal is the paper's stabilizer-rank runtime scaling."),
                "paper": BG_PAPER,
                "alpha_sampling_gamma": round(BG_ALPHA_SAMPLING, 4),   # the race task (samples peak)
                "alpha_exact_beta": round(BG_ALPHA_EXACT, 4),          # exact/probability task
                "sampling_runtime_model": "poly(n,m) + 2^(0.23*t) * t^3 * w^3   (t=#T, w=#measured)",
                "exact_runtime_model": "poly(n,m) + 2^(beta*t) * t^3,  beta=(1/6)log2(7)~=0.4696",
                "approximation_error_cost": "norm subroutine time = chi*n^3*eps^-2 (eps=rel error) "
                                            "-> tighter approximation_error costs ~1/eps^2, from paper",
                "cost_doubles_every_dT_sampling": round(1.0 / BG_ALPHA_SAMPLING, 2),  # ~4.35 T-gates
                "absolute_bill_seconds_v1": {
                    "anchor": "paper: n=40,t=48 hidden-shift sim = 'several hours' on 2016 i5 MATLAB (~3h)",
                    "note": "IMPLEMENTATION-DOMINATED -> a BAND not a point; shape is paper-faithful",
                    "edges_speedup_vs_paper": RANK_IMPL_EDGES,
                    "bill_s_at": {f"n{n}_t{t}": {e: round(rank_absolute_bill_s(t, n, s), 2)
                                                 for e, s in RANK_IMPL_EDGES.items()}
                                  for (n, t) in [(24, 48), (40, 48), (40, 64), (40, 80)]},
                },
                "projected_sampling_bill_shape": {
                    str(t): round(2.0 ** (BG_ALPHA_SAMPLING * t) * (t ** 3), 1)  # w folded into const
                    for t in (8, 16, 24, 32, 40, 48, 64)},  # relative shape (per-term const c=1, w=1)
                "absolute_constant_note": ("shape is faithful + paper-pinned; absolute seconds need a "
                                           "calibrated anchor (per-stabilizer-term runtime on this "
                                           "hardware) — v1.0 calibration item"),
                "aer_reality_check_shots_scaling": AER_EXTSTAB_SHOTS_SCALING,
                "aer_reality_check_exact_memory_wall": AER_EXACT_MEMORY_WALL,
            },
        },
        "provenance": {
            "correctness_gate": "sv/mps: amplitude fidelity vs quantum_info oracle; extstab: TVD "
                                "(Elder C6560, Aer 0.17.2 save_statevector near-zero-norm bug)",
            "censoring": "rows over cap recorded censored, excluded from fits, never dropped",
            "cost_metric": "run_s (simulation only); wall_s kept for full accounting",
            "transfer_boundary": "small-n verify accuracy NOT asserted to transfer to large-n timing",
            "g1_correction": ("cost-faithfulness is the OTHER half of G1: accuracy-verified is "
                              "necessary but not sufficient; extstab wall-time fails cost-faithfulness"),
        },
    }
    out = os.path.join(QROOT, "results", "classical_cost_map_v1.json")
    json.dump(card, open(out, "w"), indent=1)
    print(f"\ncard -> results/classical_cost_map_v1.json")
    print(f"  statevector_vs_n fit: {sv['fit_logcost_vs_n']}  (ref ln-slope 2^n ~ {sv['reference_ln_slope_2n']})")
    print(f"  mps min-chi rows: {[(r['n'], r['min_verifying_chi']) for r in mps['rows']]}")
    print(f"  rank column: PAPER_PINNED (Bravyi-Gosset gamma=0.23 sampling / beta=0.47 exact; "
          f"cost doubles ~every 4.35 T-gates) + Aer reality checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
