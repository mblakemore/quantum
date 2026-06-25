#!/usr/bin/env python3
"""
Exp66 Part A: Noiseless vs FakeMarrakesh granular escalation comparison.
Ember C3981 (pre-reg: experiments/exp66-noiseless-vs-noisy-granular-preregistration.md).

PURPOSE: Test nc-ch8-9 contractivity theory (Elder C6142).
  Does FakeMarrakesh noise contract the granular Pareto-efficiency?
  Same 17-cell pool as Exp64, same granular protocol, but AerSimulator() with NO noise model.

  Compare: noiseless capture-per-k vs Exp64 FakeMarrakesh 0.5625.
  H1: noiseless > 0.5625 (noise WAS contracting)
  H2: ratio noiseless/0.5625 > 1.20 (>=20% contraction)
  H3: Pareto-efficiency holds in both noise conditions

USAGE:
  python3 run_exp66_noiseless_granular.py --smoke   # 2 cells, fast plumbing check
  python3 run_exp66_noiseless_granular.py --run      # full 17-cell pool
"""
import sys, os, json, time, argparse
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_exp46_fast import EDGES_20, N_QUBITS_20, brute_force_max_cut
from run_exp54_warmstart import optimize_cobyla_ws, pad_params
from run_exp61_bestofk_anchor import build_for_p
from run_exp57_instance_generalization import gen_instance

# Exp64 FakeMarrakesh ground-truth (fixed, from finding41)
EXP64_GRANULAR_CAPK = 0.5625
EXP64_BINARY_CAPK   = 0.5025
EXP64_LOO_CAPTURE_G = 0.960
EXP64_MEAN_K_G      = 1.706

K_MAX = 3
CKPT    = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "results", "exp66_noiseless_checkpoint.json")
RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "experiments", "exp66_results.json")


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


def run_cell_noiseless(seed, k_max, edges, max_cut, shots, maxiter, sim, n_qubits, circuits):
    """Identical protocol to Exp64's run_cell_granular but on noiseless sim."""
    np.random.seed(seed)
    t0 = time.time()
    tqc5, gp5, bp5 = circuits[5]
    tqc3, gp3, bp3 = circuits[3]

    x0_cold = np.random.uniform(0, 2 * np.pi, 10)
    r_cold, _ = optimize_cobyla_ws(x0_cold, tqc5, gp5, bp5, 5, sim, edges, max_cut,
                                   n_qubits, shots, maxiter)

    anchors = []
    for j in range(k_max):
        x0_p3 = np.random.uniform(0, 2 * np.pi, 6)
        r3, x3 = optimize_cobyla_ws(x0_p3, tqc3, gp3, bp3, 3, sim, edges, max_cut,
                                    n_qubits, shots, maxiter)
        anchors.append((float(r3), np.asarray(x3, dtype=float)))

    bestfirst_idx = []
    cur = 0
    for j in range(k_max):
        if anchors[j][0] > anchors[cur][0]:
            cur = j
        bestfirst_idx.append(cur)

    warm_cache = {}
    r_warm_byk = []
    for j in range(k_max):
        idx = bestfirst_idx[j]
        if idx not in warm_cache:
            x0w = pad_params(anchors[idx][1], 3, 5)
            rw, _ = optimize_cobyla_ws(x0w, tqc5, gp5, bp5, 5, sim, edges, max_cut,
                                       n_qubits, shots, maxiter)
            warm_cache[idx] = float(rw)
        r_warm_byk.append(warm_cache[idx])

    lift_byk = [rw - r_cold for rw in r_warm_byk]
    rec = {"seed": seed, "k_max": k_max,
           "r_cold_p5": r_cold,
           "r_p3_anchors": [a[0] for a in anchors],
           "bestfirst_idx": bestfirst_idx,
           "r_warm_byk": r_warm_byk,
           "lift_byk": lift_byk,
           "n_warm_opts": len(warm_cache),
           "elapsed_s": time.time() - t0}
    print(f"  seed={seed} cold={r_cold:.4f} p3[{','.join(f'{a[0]:.3f}' for a in anchors)}]"
          f" bestfirst{bestfirst_idx} warm[{','.join(f'{w:.3f}' for w in r_warm_byk)}]"
          f" lift[{','.join(f'{l:+.3f}' for l in lift_byk)}]"
          f" ({rec['elapsed_s']:.0f}s)", flush=True)
    return rec


def _policy_lift(rec, tau, granular):
    r3 = rec["r_p3_anchors"]
    lift = rec["lift_byk"]
    k_max = len(r3)
    if granular:
        a = -1e18
        for j in range(k_max):
            a = max(a, r3[j])
            if a >= tau:
                return j + 1, lift[j]
        return k_max, lift[k_max - 1]
    else:
        if r3[0] >= tau:
            return 1, lift[0]
        return k_max, lift[k_max - 1]


def _pooled_loo(recs, granular):
    r0 = [r["r_p3_anchors"][0] for r in recs]
    num = den = 0.0
    ks = []
    for i, rec in enumerate(recs):
        others = [r0[j] for j in range(len(recs)) if j != i]
        tau_i = float(np.median(others))
        k_used, lift = _policy_lift(rec, tau_i, granular)
        fixed = rec["lift_byk"][-1]
        num += lift
        den += fixed
        ks.append(k_used)
    capture = num / den if den != 0 else float("nan")
    return capture, float(np.mean(ks)), ks


def _bootstrap_capture_ci(recs, granular, draws=2000):
    r0 = [r["r_p3_anchors"][0] for r in recs]
    pair = []
    for i, rec in enumerate(recs):
        others = [r0[j] for j in range(len(recs)) if j != i]
        tau_i = float(np.median(others))
        _, lift = _policy_lift(rec, tau_i, granular)
        pair.append((lift, rec["lift_byk"][-1]))
    n = len(pair)
    rng = np.random.RandomState(66)
    caps = []
    for _ in range(draws):
        idx = rng.randint(0, n, n)
        num = sum(pair[k][0] for k in idx)
        den = sum(pair[k][1] for k in idx)
        if den != 0:
            caps.append(num / den)
    if not caps:
        return None, None
    return float(np.percentile(caps, 2.5)), float(np.percentile(caps, 97.5))


def summarize(results, k_max):
    cap_g, mk_g, ks_g = _pooled_loo(results, granular=True)
    cap_b, mk_b, ks_b = _pooled_loo(results, granular=False)
    ci_g = _bootstrap_capture_ci(results, granular=True)
    eff_g = cap_g / mk_g if mk_g else float("nan")
    eff_b = cap_b / mk_b if mk_b else float("nan")
    f_g = (mk_g - 1.0) / (k_max - 1.0) if k_max > 1 else 0.0

    # H1: noiseless cap-per-k > Exp64 FakeMarrakesh 0.5625
    h1 = bool(eff_g > EXP64_GRANULAR_CAPK)
    # H2: ratio > 1.20
    ratio = eff_g / EXP64_GRANULAR_CAPK if EXP64_GRANULAR_CAPK else float("nan")
    h2 = bool(ratio > 1.20)
    # H3: Pareto-efficient in both conditions (noiseless: granular eff > binary eff)
    h3 = bool(eff_g > eff_b)

    print("\n" + "=" * 70)
    print("EXP66 PART A — NOISELESS vs FAKEMARRAKESH COMPARISON")
    print("=" * 70)
    print(f"  Cells: {len(results)} | K_max={k_max}")
    print(f"\n  NOISELESS RESULTS:")
    print(f"    Granular LOO capture : {cap_g:.4f} (Exp64 FakeMarrakesh: {EXP64_LOO_CAPTURE_G:.4f})")
    print(f"    Granular mean k_used : {mk_g:.3f} (Exp64: {EXP64_MEAN_K_G:.3f})")
    print(f"    Granular capture/k   : {eff_g:.4f} (Exp64: {EXP64_GRANULAR_CAPK:.4f})")
    print(f"    Binary capture/k     : {eff_b:.4f} (Exp64: {EXP64_BINARY_CAPK:.4f})")
    print(f"    Bootstrap 95% CI     : [{ci_g[0]:.3f}, {ci_g[1]:.3f}]")
    print(f"\n  NOISE EROSION:")
    print(f"    Ratio noiseless/FakeMarrakesh: {ratio:.3f}")
    print(f"    H1 (noiseless capk > 0.5625):  {'VALIDATE' if h1 else 'INVALIDATE'}")
    print(f"    H2 (ratio > 1.20):              {'VALIDATE' if h2 else 'INVALIDATE'}")
    print(f"    H3 (Pareto-efficient noiseless):{'VALIDATE' if h3 else 'INVALIDATE'}")
    print(f"\n  PRED_C3980_001 IMPLICATION (QPU test, Part B):")
    if ratio > 1.20:
        print(f"    Noise DID erode: noiseless {eff_g:.3f} vs noisy {EXP64_GRANULAR_CAPK:.3f}.")
        print(f"    QPU (higher noise than FakeMarrakesh) could erode further toward <0.40.")
    elif h1:
        print(f"    Mild noise erosion (ratio {ratio:.2f}x). QPU erosion to <0.40 less certain.")
    else:
        print(f"    No erosion in FakeMarrakesh direction. QPU <0.40 harder to justify mechanistically.")
    print("=" * 70)

    return {
        "granular": {"loo_capture": cap_g, "mean_k_used": mk_g,
                     "k_dist": {str(v): ks_g.count(v) for v in sorted(set(ks_g))},
                     "capture_per_k": eff_g, "bootstrap95_capture": list(ci_g)},
        "binary": {"loo_capture": cap_b, "mean_k_used": mk_b,
                   "k_dist": {str(v): ks_b.count(v) for v in sorted(set(ks_b))},
                   "capture_per_k": eff_b},
        "noise_erosion": {
            "noiseless_capk": eff_g,
            "fakemarrakesh_capk": EXP64_GRANULAR_CAPK,
            "ratio_noiseless_over_noisy": ratio,
        },
        "hypotheses": {"H1": bool(h1), "H2": bool(h2), "H3": bool(h3)},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--run", action="store_true")
    args = ap.parse_args()
    if not (args.smoke or args.run):
        print("Specify --smoke | --run. Refusing to guess.")
        sys.exit(2)

    if args.smoke:
        cells = [("EDGES_20", EDGES_20, 42), ("rand_seed101", gen_instance(101), 42)]
        shots, maxiter, mode = 128, 8, "SMOKE"
    else:
        cells = ([("EDGES_20", EDGES_20, s) for s in range(42, 50)]
                 + [("rand_seed101", gen_instance(101), s) for s in (42, 43, 44)]
                 + [("rand_seed202", gen_instance(202), s) for s in (42, 43, 44)]
                 + [("rand_seed303", gen_instance(303), s) for s in (42, 43, 44)])
        shots, maxiter, mode = 256, 20, "RUN"

    n_qubits = N_QUBITS_20

    from qiskit_aer import AerSimulator
    sim = AerSimulator()  # NOISELESS — no noise_model arg

    print("=" * 70)
    print(f"Exp66 Part A — Noiseless granular escalation — {mode}")
    print(f"cells={len(cells)} k_max={K_MAX} shots={shots} maxiter={maxiter}")
    print(f"Simulator: AerSimulator (NOISELESS — no noise model)")
    print(f"Baseline: Exp64 FakeMarrakesh granular cap_k={EXP64_GRANULAR_CAPK}")
    print(f"Pre-reg: experiments/exp66-noiseless-vs-noisy-granular-preregistration.md")
    print("=" * 70, flush=True)

    ckpt = _load_ckpt()
    if ckpt.get("mode") and ckpt.get("mode") != mode:
        bak = CKPT + f".stale-{ckpt.get('mode')}.bak"
        os.replace(CKPT, bak)
        print(f"  [reset] stale checkpoint mode {ckpt.get('mode')} → backed up", flush=True)
        ckpt = {}
    done = {(r["instance"], r["seed"]): r for r in ckpt.get("data", [])}
    if done:
        print(f"  [resume] {len(done)} cell(s) already done", flush=True)
    results = list(ckpt.get("data", []))

    circ_cache = {}
    cut_cache = {}
    for inst_label, edges, seed in cells:
        if (inst_label, seed) in done:
            continue
        if inst_label not in circ_cache:
            cut_cache[inst_label] = brute_force_max_cut(n_qubits, edges)
            circ_cache[inst_label] = {p: build_for_p(p, sim, n_qubits, edges) for p in (3, 5)}
            print(f"--- {inst_label}: max_cut={cut_cache[inst_label]} ---", flush=True)
        rec = run_cell_noiseless(seed, K_MAX, edges, cut_cache[inst_label], shots, maxiter,
                                 sim, n_qubits, circ_cache[inst_label])
        rec["instance"] = inst_label
        rec["max_cut"] = cut_cache[inst_label]
        results.append(rec)
        ck = _load_ckpt()
        ck["mode"] = mode
        ck["data"] = results
        _save_ckpt(ck)

    summary = summarize(results, K_MAX)
    out = {"experiment": "Exp66-noiseless-granular",
           "title": "Noiseless vs FakeMarrakesh granular escalation comparison (Part A)",
           "author": "Ember", "cycle": "C3981",
           "pre_registration": "experiments/exp66-noiseless-vs-noisy-granular-preregistration.md",
           "simulator": "AerSimulator-noiseless",
           "mode": mode,
           "k_max": K_MAX, "shots": shots, "maxiter": maxiter,
           "exp64_baseline": {"granular_capk": EXP64_GRANULAR_CAPK,
                              "binary_capk": EXP64_BINARY_CAPK,
                              "loo_capture": EXP64_LOO_CAPTURE_G,
                              "mean_k": EXP64_MEAN_K_G},
           "summary": summary,
           "data": sorted(results, key=lambda r: (r.get("instance", ""), r["seed"]))}
    json.dump(out, open(RESULTS, "w"), indent=2)
    print(f"\n  Wrote {RESULTS}")


if __name__ == "__main__":
    main()
