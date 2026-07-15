#!/usr/bin/env python3
"""
Exp66 Part C: N>=34 noiseless replication to resolve pred_c3981_001 (Ember C4171).

pred_c3981_001 (conf 0.52): the Part A N=17 result (noiseless capk 0.5236 < FakeMarrakesh
0.5625) reflects GENUINE non-unital noise anti-contraction, NOT an N=17 statistical artifact.
Test (pre-registered C3981): run Exp66 with N>=34 cells; VALIDATED if noiseless capk <
FakeMarrakesh capk (0.5625, fixed ground truth per Part A convention) in >=2/3 of bootstrap
resamples.

CELL SET PRE-COMMITTED HERE BEFORE ANY COMPUTE (no cherry-picking, extends Part A's pool
deterministically by seed):
  Original 17 (Part A): EDGES_20 s42-49; rand101/202/303 s42-44.
  New 17:               EDGES_20 s50-57; rand101/202/303 s45-47.
  Total = 34 cells.

Same granular protocol as Part A (K=3, tau=LOO-median, 256 shots, maxiter=20, noiseless
AerSimulator). Reuses Part A machinery verbatim; only the cell pool and the capk bootstrap
grader are new.
"""
import sys, os, json, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_exp46_fast import EDGES_20, N_QUBITS_20, brute_force_max_cut
from run_exp61_bestofk_anchor import build_for_p
from run_exp57_instance_generalization import gen_instance
from run_exp66_noiseless_granular import (
    run_cell_noiseless, _policy_lift, K_MAX,
    EXP64_GRANULAR_CAPK, EXP64_BINARY_CAPK,
)

CKPT = os.path.join(HERE, "..", "results", "exp66c_n34_checkpoint.json")
RESULTS = os.path.join(HERE, "..", "experiments", "exp66c_n34_results.json")
SHOTS, MAXITER = 256, 20

# ---- PRE-COMMITTED 34-cell set (frozen before compute) ----
CELLS_SPEC = (
    [("EDGES_20", s) for s in range(42, 58)]                       # s42..s57  = 16
    + [(f"rand_seed{b}", s) for b in (101, 202, 303) for s in (42, 43, 44, 45, 46, 47)]  # 18
)  # total = 34


def _edges_for(label):
    if label == "EDGES_20":
        return EDGES_20
    return gen_instance(int(label.replace("rand_seed", "")))


def _load_ckpt():
    if os.path.exists(CKPT):
        try:
            return json.load(open(CKPT))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_ckpt(c):
    os.makedirs(os.path.dirname(CKPT), exist_ok=True)
    tmp = CKPT + ".tmp"
    json.dump(c, open(tmp, "w"), indent=2)
    os.replace(tmp, CKPT)


def pooled_capk(recs, granular):
    """capk = (pooled LOO capture) / (mean k_used). Returns (capk, capture, mean_k)."""
    r0 = [r["r_p3_anchors"][0] for r in recs]
    num = den = 0.0
    ks = []
    for i, rec in enumerate(recs):
        others = [r0[j] for j in range(len(recs)) if j != i]
        tau_i = float(np.median(others))
        k_used, lift = _policy_lift(rec, tau_i, granular)
        num += lift
        den += rec["lift_byk"][-1]
        ks.append(k_used)
    capture = num / den if den != 0 else float("nan")
    mk = float(np.mean(ks))
    return (capture / mk if mk else float("nan")), capture, mk


def bootstrap_capk_below(recs, threshold, draws=5000, granular=True):
    """Fraction of cell-resamples where noiseless capk < threshold.
    Resamples the (lift_used, lift_fixed, k_used) triples so BOTH capture and mean_k vary."""
    r0 = [r["r_p3_anchors"][0] for r in recs]
    triples = []
    for i, rec in enumerate(recs):
        others = [r0[j] for j in range(len(recs)) if j != i]
        tau_i = float(np.median(others))
        k_used, lift = _policy_lift(rec, tau_i, granular)
        triples.append((lift, rec["lift_byk"][-1], k_used))
    n = len(triples)
    rng = np.random.RandomState(3981)
    caps = []
    below = 0
    for _ in range(draws):
        idx = rng.randint(0, n, n)
        num = sum(triples[k][0] for k in idx)
        den = sum(triples[k][1] for k in idx)
        mk = np.mean([triples[k][2] for k in idx])
        if den != 0 and mk:
            ck = (num / den) / mk
            caps.append(ck)
            if ck < threshold:
                below += 1
    frac = below / len(caps)
    return frac, float(np.percentile(caps, 2.5)), float(np.percentile(caps, 97.5)), caps


def main():
    n_qubits = N_QUBITS_20
    from qiskit_aer import AerSimulator
    sim = AerSimulator()  # NOISELESS

    print("=" * 70)
    print("Exp66 Part C — N=34 noiseless replication (resolves pred_c3981_001)")
    print(f"cells={len(CELLS_SPEC)} K_max={K_MAX} shots={SHOTS} maxiter={MAXITER}")
    print(f"FakeMarrakesh fixed ground truth capk = {EXP64_GRANULAR_CAPK}")
    print("=" * 70, flush=True)

    ckpt = _load_ckpt()
    done = {(r["instance"], r["seed"]): r for r in ckpt.get("data", [])}
    if done:
        print(f"  [resume] {len(done)} cell(s) already done", flush=True)
    results = list(ckpt.get("data", []))

    circ_cache, cut_cache = {}, {}
    for label, seed in CELLS_SPEC:
        if (label, seed) in done:
            continue
        edges = _edges_for(label)
        if label not in circ_cache:
            cut_cache[label] = brute_force_max_cut(n_qubits, edges)
            circ_cache[label] = {p: build_for_p(p, sim, n_qubits, edges) for p in (3, 5)}
            print(f"--- {label}: max_cut={cut_cache[label]} ---", flush=True)
        rec = run_cell_noiseless(seed, K_MAX, edges, cut_cache[label], SHOTS, MAXITER,
                                 sim, n_qubits, circ_cache[label])
        rec["instance"] = label
        rec["max_cut"] = cut_cache[label]
        results.append(rec)
        ck = _load_ckpt()
        ck["data"] = results
        _save_ckpt(ck)

    # ---- grade ----
    capk_g, cap_g, mk_g = pooled_capk(results, granular=True)
    capk_b, _, _ = pooled_capk(results, granular=False)
    frac_below, lo, hi, caps = bootstrap_capk_below(results, EXP64_GRANULAR_CAPK, granular=True)
    validated = frac_below >= (2.0 / 3.0)

    print("\n" + "=" * 70)
    print("EXP66 PART C RESULT")
    print("=" * 70)
    print(f"  Cells: {len(results)}")
    print(f"  Noiseless granular capk : {capk_g:.4f}  (Part A N=17: 0.5236)")
    print(f"  Noiseless binary capk   : {capk_b:.4f}")
    print(f"  FakeMarrakesh capk      : {EXP64_GRANULAR_CAPK:.4f} (fixed)")
    print(f"  Pooled LOO capture      : {cap_g:.4f} | mean_k: {mk_g:.3f}")
    print(f"  Bootstrap capk 95% CI   : [{lo:.4f}, {hi:.4f}]  (draws={len(caps)})")
    print(f"  Frac resamples capk<0.5625: {frac_below:.3f}  (need >=0.667)")
    print(f"\n  pred_c3981_001: {'VALIDATED' if validated else 'INVALIDATED'} "
          f"(noiseless capk {'<' if capk_g < EXP64_GRANULAR_CAPK else '>='} 0.5625, "
          f"{frac_below:.1%} of resamples below)")
    print("=" * 70)

    out = {
        "experiment": "Exp66-Part-C-noiseless-N34",
        "author": "Ember", "cycle": "C4171",
        "resolves": "pred_c3981_001",
        "simulator": "AerSimulator-noiseless",
        "n_cells": len(results), "k_max": K_MAX, "shots": SHOTS, "maxiter": MAXITER,
        "fakemarrakesh_capk_fixed": EXP64_GRANULAR_CAPK,
        "result": {
            "noiseless_granular_capk": capk_g,
            "noiseless_binary_capk": capk_b,
            "pooled_loo_capture": cap_g, "mean_k": mk_g,
            "bootstrap_capk_ci95": [lo, hi],
            "frac_resamples_below_fake": frac_below,
            "partA_n17_capk": 0.5236,
            "verdict": "VALIDATED" if validated else "INVALIDATED",
        },
        "data": sorted(results, key=lambda r: (r.get("instance", ""), r["seed"])),
    }
    json.dump(out, open(RESULTS, "w"), indent=2)
    print(f"\n  Wrote {RESULTS}")


if __name__ == "__main__":
    main()
