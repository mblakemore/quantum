#!/usr/bin/env python3
"""
Exp73 (Elder C6204) — Does depolarizing noise preserve warm-start ANCHOR RANKING?

Bridges F44/Exp68 (the warm-start cost-GAP contracts under depol) to my best-of-k anchor
SELECTION lever (project_exp61_bestofk_anchor): best-of-k assumes you can RANK anchors by cost.
Under device noise, is that rank preserved?

  - GLOBAL depol: cost_noisy = (1-p)*cost_pure + p*meancut  -> affine-increasing -> rank PROVABLY preserved.
  - LOCAL per-gate depol: state-dependent contraction (F44: 0.62-0.87 spread) -> rank CAN invert.

Pre-reg: experiments/exp73-anchor-rank-preservation-under-noise-preregistration.md (committed before compute).
EDGES_8, QAOA p=2, exact density-matrix (NO shots). Reuses exp68 infra. No Ember/Whisper files touched.
"""
import sys, os, json, argparse
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_exp46_fast import build_parameterized_standard_qaoa, compute_cut_value, brute_force_max_cut
from run_exp68_landscape_gap_contraction import (
    EDGES_8, N, P_LAYERS, MEANCUT, _cut_table, exp_cost_from_probs,
    pure_probs, pure_cost, global_depol_cost, local_depol_cost,
)
from scipy.optimize import minimize


def spearman(a, b):
    """Spearman rank correlation between two equal-length sequences (no scipy.stats dep)."""
    a = np.asarray(a, float); b = np.asarray(b, float)
    ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
    ra = ra - ra.mean(); rb = rb - rb.mean()
    denom = np.sqrt((ra**2).sum() * (rb**2).sum())
    return float((ra * rb).sum() / denom) if denom > 0 else 1.0


def kendall_tau(a, b):
    """Kendall tau-a (concordant - discordant) / total pairs."""
    a = np.asarray(a, float); b = np.asarray(b, float)
    n = len(a); c = d = 0
    for i in range(n):
        for j in range(i + 1, n):
            s = np.sign(a[i] - a[j]) * np.sign(b[i] - b[j])
            if s > 0: c += 1
            elif s < 0: d += 1
    tot = n * (n - 1) / 2
    return float((c - d) / tot) if tot > 0 else 1.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--k', type=int, default=12, help='anchor pool size')
    ap.add_argument('--pool', choices=['cobyla', 'random'], default='cobyla',
                    help="cobyla = COBYLA-optimized (degenerate near-optimal); "
                         "random = raw random theta (genuine cost SPREAD — the real ranking test)")
    ap.add_argument('--out', default=None)
    args = ap.parse_args()
    rng = np.random.default_rng(args.seed)
    K = args.k
    if args.out is None:
        args.out = os.path.join(os.path.dirname(__file__), '..', 'results',
                                f'exp73_anchor_rank_preservation_{args.pool}.json')

    max_cut = brute_force_max_cut(N, EDGES_8)
    qc, gamma, beta = build_parameterized_standard_qaoa(P_LAYERS, N, EDGES_8)
    n_params = 2 * P_LAYERS
    print(f"Exp73 | EDGES_8 n={N} |E|={len(EDGES_8)} max_cut={max_cut} meancut={MEANCUT} | QAOA p={P_LAYERS} | K={K} anchors", flush=True)

    # --- build the anchor pool ---
    def neg_cost(theta):
        return -pure_cost(qc, gamma, beta, theta)
    anchors = []
    if args.pool == 'cobyla':
        # K COBYLA-optimized anchors (clustered near-optimal; tends to DEGENERATE ties at the optimum)
        for s in range(K):
            x0 = rng.uniform(0, np.pi, n_params)
            r = minimize(neg_cost, x0, method='COBYLA', options={'maxiter': 200})
            anchors.append(r.x)
    else:
        # K raw random theta — genuine cost SPREAD; the real "rank distinct-quality candidates" test
        for s in range(K):
            anchors.append(rng.uniform(0, np.pi, n_params))
    print(f"pool mode: {args.pool}", flush=True)
    pure_costs = np.array([pure_cost(qc, gamma, beta, t) for t in anchors])
    noiseless_rank = np.argsort(np.argsort(-pure_costs))  # rank 0 = best (highest cost)
    best_noiseless = int(np.argmax(pure_costs))
    top3_noiseless = set(np.argsort(-pure_costs)[:3].tolist())
    print(f"anchor pool pure costs: min={pure_costs.min():.4f} max={pure_costs.max():.4f} "
          f"spread={pure_costs.max()-pure_costs.min():.4f} (cut/max best={pure_costs.max()/max_cut:.3f})", flush=True)
    print(f"  noiseless best anchor = #{best_noiseless} (cost {pure_costs.max():.4f}); top-3 = {sorted(top3_noiseless)}", flush=True)

    pa_list = [pure_probs(qc, gamma, beta, t) for t in anchors]

    # ===== P1: GLOBAL depol — affine transform, rank must be exactly preserved =====
    print("\n--- P1: GLOBAL depolarizing — Spearman rho(noiseless, noisy) vs p (expect 1.000) ---", flush=True)
    global_rows = []
    p1_pass = True
    for p in [0.0, 0.1, 0.3, 0.5, 0.7, 0.9]:
        nc = np.array([global_depol_cost(pa_list[i], p) for i in range(K)])
        rho = spearman(pure_costs, nc)
        argmax_ok = (int(np.argmax(nc)) == best_noiseless)
        top3_ov = len(set(np.argsort(-nc)[:3].tolist()) & top3_noiseless)
        p1_pass &= (abs(rho - 1.0) < 1e-9) and argmax_ok
        global_rows.append({"p": p, "spearman": rho, "argmax_preserved": bool(argmax_ok), "top3_overlap": top3_ov})
        print(f"  p={p:.1f}  rho={rho:.6f}  argmax_preserved={argmax_ok}  top3_overlap={top3_ov}/3", flush=True)

    # ===== P2/P3: LOCAL per-gate depol — does ranking degrade? does argmax survive? =====
    print("\n--- P2/P3: LOCAL per-gate depolarizing — rank stability vs dose (p2=10*p1) ---", flush=True)
    doses = [0.0, 0.0002, 0.0005, 0.001, 0.003, 0.01, 0.03]
    local_rows = []
    for p1 in doses:
        p2 = 10 * p1
        if p1 == 0.0:
            nc = pure_costs.copy()
        else:
            nc = np.array([local_depol_cost(qc, gamma, beta, anchors[i], p1, p2) for i in range(K)])
        rho = spearman(pure_costs, nc)
        tau = kendall_tau(pure_costs, nc)
        argmax_ok = (int(np.argmax(nc)) == best_noiseless)
        top3_ov = len(set(np.argsort(-nc)[:3].tolist()) & top3_noiseless)
        local_rows.append({"p1": p1, "p2": p2, "spearman": rho, "kendall_tau": tau,
                           "argmax_preserved": bool(argmax_ok), "top3_overlap": top3_ov,
                           "noisy_cost_spread": float(nc.max() - nc.min())})
        ember = " <-- Ember high dose" if abs(p1 - 0.001) < 1e-12 else ""
        print(f"  p1={p1:.4f} p2={p2:.4f}  rho={rho:.4f} tau={tau:.4f}  argmax={'OK' if argmax_ok else 'INVERTED'}  top3={top3_ov}/3{ember}", flush=True)

    # ---- grade predictions ----
    ember_row = next(r for r in local_rows if abs(r["p1"] - 0.001) < 1e-12)
    low_dose_rows = [r for r in local_rows if 0 < r["p1"] <= 0.001]
    high_dose_rows = [r for r in local_rows if r["p1"] >= 0.01]
    p2_low_ok = all(r["spearman"] >= 0.9 for r in low_dose_rows)
    p2_high_degrade = any(r["spearman"] < 0.9 for r in high_dose_rows)
    p2_pass = p2_low_ok and p2_high_degrade
    p3_argmax = ember_row["argmax_preserved"]
    p3_top3 = ember_row["top3_overlap"] >= 2
    p3_pass = p3_argmax and p3_top3

    print("\n================ VERDICTS ================", flush=True)
    print(f"P1 (global rank exactly preserved, all p): {'PASS' if p1_pass else 'FAIL (code bug)'}", flush=True)
    print(f"P2 (local: rho>=0.9 at/below Ember dose AND degrades at high dose): "
          f"{'PASS' if p2_pass else 'FAIL'} (low_ok={p2_low_ok}, high_degrades={p2_high_degrade})", flush=True)
    print(f"P3 (DECISION: argmax preserved + top3>=2/3 at Ember high dose): "
          f"{'PASS' if p3_pass else 'FAIL'} (argmax={p3_argmax}, top3={ember_row['top3_overlap']}/3)", flush=True)
    if p3_pass:
        print("  -> best-of-k anchor SELECTION is noise-robust on near-clean hardware: the single best", flush=True)
        print("     anchor stays best under Ember's high dose; mid-pack reshuffle is harmless for selection.", flush=True)
    else:
        print("  -> anchor SELECTION degrades under realistic device noise: best-of-k must rank anchors", flush=True)
        print("     noiselessly (classical surrogate) or with enough shots to beat the contraction spread.", flush=True)

    out = {
        "experiment": "exp73_anchor_rank_preservation", "cycle": 6204, "author": "elder",
        "n_qubits": N, "edges": EDGES_8, "max_cut": max_cut, "meancut": MEANCUT,
        "qaoa_p": P_LAYERS, "seed": args.seed, "K_anchors": K,
        "anchor_pure_costs": pure_costs.tolist(),
        "noiseless_best_anchor": best_noiseless, "noiseless_top3": sorted(top3_noiseless),
        "pure_cost_spread": float(pure_costs.max() - pure_costs.min()),
        "P1_global": {"pass": bool(p1_pass), "rows": global_rows},
        "P2_local": {"pass": bool(p2_pass), "low_dose_rho_ge_0.9": bool(p2_low_ok),
                     "high_dose_degrades": bool(p2_high_degrade), "rows": local_rows},
        "P3_decision": {"pass": bool(p3_pass), "argmax_preserved_at_ember_dose": bool(p3_argmax),
                        "top3_overlap_at_ember_dose": ember_row["top3_overlap"],
                        "ember_dose_spearman": ember_row["spearman"]},
        "verdict": {
            "P1_global_rank_exactly_preserved": bool(p1_pass),
            "P2_local_rank_degrades_with_dose": bool(p2_pass),
            "P3_bestofk_selection_noise_robust_at_ember_dose": bool(p3_pass),
        },
    }
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, 'w') as f:
        json.dump(out, f, indent=2)
    print(f"\nsaved -> {os.path.abspath(args.out)}", flush=True)


if __name__ == '__main__':
    main()
