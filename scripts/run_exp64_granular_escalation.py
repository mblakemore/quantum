#!/usr/bin/env python3
"""
Exp64-granular: draw-one-more-at-a-time (1->2->3) warm-start escalation.
Elder C6132 (pre-reg + build).

Pre-registration: experiments/exp64-granular-escalation-preregistration.md
                  DC1.5 state/experiments/c6132-exp64-granular-escalation.json

THE GAP THIS CLOSES (Finding 38/40 named open arm)
  Exp63/64-tau adopted+calibrated the BINARY escalation (use anchor[0] if a_1>=tau, else jump
  to full best-of-3). It was a zero-compute replay because Exp61/62 stored warm outcomes for
  only k=1 (anchor[0]) and k=3 (best-of-3). A GRANULAR 1->2->3 policy needs the k=2 intermediate
  warm outcome (best-of-FIRST-2 anchor) — absent from every prior result file, and unreproducible
  from the seed (the sim is unseeded). So this RE-RUNS each cell as a fresh self-consistent
  trajectory computing warm p5 for best-of-first-1/2/3, all paired against a shared r_cold.
  NEW COMPUTE, not replay (C6115 gate).

  Action it changes (EVI gate, C6044): whether the warm-start protocol adopts GRANULAR escalation
  (finer cost control) over the binary 1-or-3 already adopted — does granular spend less mean
  compute while retaining the captured lift?

DESIGN (paired; one RNG stream per cell; draw order = Exp61's so k=1 leg matches Exp59/61 form)
  Pool N=17 (= Exp64-tau pool): EDGES_20 seeds 42-49 + rand101/202/303 x seeds 42-44.
  Per cell: x0_cold(10)->p5->r_cold ; k_max=3 anchors x0_p3(6)->p3->(r3_j,x3_j) in draw order ;
  warm p5 from best-of-first-j anchor for j=1,2,3 (cached by anchor idx -> <=3 warm opts, fewer
  when running-best idx repeats). lift_byk[j-1] = r_warm(best-of-first-j) - r_cold.
  lift_byk[0]==k1 (anchor0, == Exp61 lift_single form); lift_byk[2]==k3 (best-of-3, == lift_best).
  lift_byk[1]==k2 (best-of-first-2) is the NEW quantity.

POLICIES (graded head-to-head at tau=median(r3_0), LOO-CV; fixed-k=3 = capture ceiling)
  a_j = max(r3_0..r3_{j-1}) running-best p3 recall.
  GRANULAR(tau): k_used = first j with a_j>=tau else 3 ; lift = lift_byk[k_used-1].
  BINARY(tau):   k=1 if a_1>=tau else k=3 ; lift = lift_byk[0] or lift_byk[2].
  capture = sum(policy_lift)/sum(lift_fixed). LOO: tau_i=median(r3_0 over other 16).

HYPOTHESES (pre-disclosed in the pre-reg; graded by LETTER, Brier-scored, no post-hoc threshold)
  P1 granular mean k_used < binary mean k_used (compute saved)            conf 0.70
  P2 granular pooled LOO capture >= 0.80                                  conf 0.55
  P3 granular cap/meank > binary cap/meank (Pareto-efficient)             conf 0.58
  P4 granular LOO capture > cost-matched random f=(meank-1)/(k_max-1)     conf 0.70

SCOPE/HONESTY
  - PILOT (256sh/maxiter20), N=17 — SIGN + rough magnitude, not a 1024sh campaign.
  - fresh unseeded sim => k1/k3 will NOT exactly match published Exp61/62 (self-consistent by
    design); capture is a ratio of small D (~0.03-0.05) => bootstrap CI wide, grade by LETTER+CI.
  - tau-frontier DESCRIPTIVE only (C6121 no pool-argmax). seeds retained, no dropping (C5923).

USAGE
  python3 run_exp64_granular_escalation.py --smoke   # 2 cells, k=3, 128sh, maxiter 8 — plumbing
  python3 run_exp64_granular_escalation.py --run      # full 17-cell pool, 256sh maxiter20 (bg)
"""
import sys, os, json, time, argparse
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_exp46_fast import EDGES_20, N_QUBITS_20, brute_force_max_cut
from run_exp54_warmstart import optimize_cobyla_ws, pad_params
from run_exp61_bestofk_anchor import build_for_p, _spearman, _rho_flag
from run_exp57_instance_generalization import gen_instance
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime.fake_provider import FakeMarrakesh

K_MAX = 3
CKPT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "..", "results", "exp64_granular_checkpoint.json")
RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "experiments", "exp64_granular_results.json")


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


def run_cell_granular(seed, k_max, edges, max_cut, shots, maxiter, sim, n_qubits, circuits):
    """One self-consistent trajectory: r_cold + k anchors (draw order) + warm p5 for
    best-of-first-1/2/3. Paired (shared r_cold). Draw order matches Exp61.run_seed."""
    np.random.seed(seed)
    t0 = time.time()
    tqc5, gp5, bp5 = circuits[5]
    tqc3, gp3, bp3 = circuits[3]

    # cold p5 (identical first draw to Exp59/61)
    x0_cold = np.random.uniform(0, 2 * np.pi, 10)
    r_cold, _ = optimize_cobyla_ws(x0_cold, tqc5, gp5, bp5, 5, sim, edges, max_cut,
                                   n_qubits, shots, maxiter)

    # k_max p3 anchors in draw order (j=0 reproduces Exp59/61 single anchor form)
    anchors = []  # (r3, x3)
    for j in range(k_max):
        x0_p3 = np.random.uniform(0, 2 * np.pi, 6)
        r3, x3 = optimize_cobyla_ws(x0_p3, tqc3, gp3, bp3, 3, sim, edges, max_cut,
                                    n_qubits, shots, maxiter)
        anchors.append((float(r3), np.asarray(x3, dtype=float)))

    # running-best (best-of-first-j) anchor index for j=1..k_max
    bestfirst_idx = []
    cur = 0
    for j in range(k_max):
        if anchors[j][0] > anchors[cur][0]:
            cur = j
        bestfirst_idx.append(cur)

    # warm p5 from the best-of-first-j anchor; cache by idx (>=2 of the 3 often share an idx)
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
           "lift_byk": lift_byk,           # [k1, k2(best-of-2 NEW), k3]
           "n_warm_opts": len(warm_cache),  # compute actually spent on warm p5
           "elapsed_s": time.time() - t0}
    print(f"  seed={seed} cold={r_cold:.4f} p3[{','.join(f'{a[0]:.3f}' for a in anchors)}]"
          f" bestfirst{bestfirst_idx} warm[{','.join(f'{w:.3f}' for w in r_warm_byk)}]"
          f" lift[{','.join(f'{l:+.3f}' for l in lift_byk)}]"
          f" ({rec['elapsed_s']:.0f}s)", flush=True)
    return rec


# ── policy evaluation (LOO-CV, paired) ───────────────────────────────────────
def _policy_lift(rec, tau, granular):
    """Return (k_used, lift) under granular or binary policy at threshold tau."""
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
    else:  # binary: k=1 if a_1>=tau else full k_max
        if r3[0] >= tau:
            return 1, lift[0]
        return k_max, lift[k_max - 1]


def _pooled_loo(recs, granular):
    """Pooled LOO-CV capture + mean k_used. tau_i = median(r3_0 over the OTHER cells)."""
    r0 = [r["r_p3_anchors"][0] for r in recs]
    num = den = 0.0
    ks = []
    for i, rec in enumerate(recs):
        others = [r0[j] for j in range(len(recs)) if j != i]
        tau_i = float(np.median(others))
        k_used, lift = _policy_lift(rec, tau_i, granular)
        fixed = rec["lift_byk"][-1]  # best-of-k=3
        num += lift
        den += fixed
        ks.append(k_used)
    capture = num / den if den != 0 else float("nan")
    return capture, float(np.mean(ks)), ks


def _bootstrap_capture_ci(recs, granular, draws=2000):
    """95% CI on pooled LOO capture by resampling cells (paired num/den per cell)."""
    r0 = [r["r_p3_anchors"][0] for r in recs]
    pair = []  # per-cell (policy_lift, fixed_lift) under LOO tau
    for i, rec in enumerate(recs):
        others = [r0[j] for j in range(len(recs)) if j != i]
        tau_i = float(np.median(others))
        _, lift = _policy_lift(rec, tau_i, granular)
        pair.append((lift, rec["lift_byk"][-1]))
    n = len(pair)
    rng = np.random.RandomState(64)
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
    rs = sorted(results, key=lambda r: (r.get("instance", ""), r["seed"]))
    n = len(rs)
    print("\n" + "=" * 70)
    print(f"SUMMARY — Exp64-granular 1->2->3 escalation, N={n} cells")
    print("=" * 70)

    cap_g, mk_g, ks_g = _pooled_loo(rs, granular=True)
    cap_b, mk_b, ks_b = _pooled_loo(rs, granular=False)
    n_diff = sum(1 for a, b in zip(ks_g, ks_b) if a != b)
    eff_g = cap_g / mk_g if mk_g else float("nan")
    eff_b = cap_b / mk_b if mk_b else float("nan")
    f_g = (mk_g - 1) / (k_max - 1)  # cost-matched random fraction
    ci_g = _bootstrap_capture_ci(rs, granular=True)

    print(f"  GRANULAR  LOO capture={cap_g:+.4f}  mean k_used={mk_g:.3f}  "
          f"k_dist={dict((v, ks_g.count(v)) for v in sorted(set(ks_g)))}")
    print(f"  BINARY    LOO capture={cap_b:+.4f}  mean k_used={mk_b:.3f}  "
          f"k_dist={dict((v, ks_b.count(v)) for v in sorted(set(ks_b)))}")
    print(f"  cells where policies differ (a_1<tau<=a_2): {n_diff}/{n}")
    print(f"  capture-per-k:  granular={eff_g:+.4f}  binary={eff_b:+.4f}")
    print(f"  granular bootstrap95 capture CI = {ci_g}")

    p1 = mk_g < mk_b
    p2 = cap_g >= 0.80
    p3 = eff_g > eff_b
    p4 = cap_g > f_g
    print(f"\n  -- PRE-REGISTERED PREDICTIONS (graded by letter) --")
    print(f"     P1 granular saves compute (mk_g<mk_b): {mk_g:.3f}<{mk_b:.3f} -> {'TRUE' if p1 else 'FALSE'}")
    print(f"     P2 capture>=0.80: {cap_g:.4f} -> {'TRUE' if p2 else 'FALSE'}")
    print(f"     P3 Pareto-efficient (eff_g>eff_b): {eff_g:.4f}>{eff_b:.4f} -> {'TRUE' if p3 else 'FALSE'}")
    print(f"     P4 beats cost-matched random f={f_g:.3f}: {cap_g:.4f}>{f_g:.3f} -> {'TRUE' if p4 else 'FALSE'}")

    return {
        "n_total": n, "k_max": k_max,
        "granular": {"loo_capture": cap_g, "mean_k_used": mk_g,
                     "k_dist": {str(v): ks_g.count(v) for v in sorted(set(ks_g))},
                     "capture_per_k": eff_g, "bootstrap95_capture": list(ci_g)},
        "binary": {"loo_capture": cap_b, "mean_k_used": mk_b,
                   "k_dist": {str(v): ks_b.count(v) for v in sorted(set(ks_b))},
                   "capture_per_k": eff_b},
        "n_policies_differ": n_diff,
        "cost_matched_random_f": f_g,
        "predictions": {"P1": bool(p1), "P2": bool(p2), "P3": bool(p3), "P4": bool(p4)},
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
        # EDGES_20 + 1 new instance, 1 opt-seed each, cheap fidelity — plumbing/timing only
        cells = [("EDGES_20", EDGES_20, 42), ("rand_seed101", gen_instance(101), 42)]
        shots, maxiter, mode = 128, 8, "SMOKE"
    else:
        cells = ([("EDGES_20", EDGES_20, s) for s in range(42, 50)]
                 + [("rand_seed101", gen_instance(101), s) for s in (42, 43, 44)]
                 + [("rand_seed202", gen_instance(202), s) for s in (42, 43, 44)]
                 + [("rand_seed303", gen_instance(303), s) for s in (42, 43, 44)])
        shots, maxiter, mode = 256, 20, "RUN"

    n_qubits = N_QUBITS_20
    print("=" * 70)
    print(f"Exp64-granular 1->2->3 escalation — {mode}")
    print(f"cells={len(cells)} k_max={K_MAX} shots={shots} maxiter={maxiter}")
    print(f"metric = paired lift_byk [k1, k2(best-of-2 NEW), k3]; policy capture LOO-CV")
    print("=" * 70, flush=True)

    fake = FakeMarrakesh()
    sim = AerSimulator(noise_model=NoiseModel.from_backend(fake))

    ckpt = _load_ckpt()
    if ckpt.get("mode") and ckpt.get("mode") != mode:
        bak = CKPT + f".stale-{ckpt.get('mode')}.bak"
        os.replace(CKPT, bak)
        print(f"  [reset] checkpoint mode {ckpt.get('mode')} != {mode}; backed up to {bak}", flush=True)
        ckpt = {}
    done = {(r["instance"], r["seed"]): r for r in ckpt.get("data", [])}
    if done:
        print(f"  [resume] {len(done)} cell(s) done", flush=True)
    results = list(ckpt.get("data", []))

    # circuits are per-instance (edges differ); build lazily, cache per instance label
    circ_cache = {}
    cut_cache = {}
    for inst_label, edges, seed in cells:
        if (inst_label, seed) in done:
            continue
        if inst_label not in circ_cache:
            cut_cache[inst_label] = brute_force_max_cut(n_qubits, edges)
            circ_cache[inst_label] = {p: build_for_p(p, sim, n_qubits, edges) for p in (3, 5)}
            print(f"--- {inst_label}: max_cut={cut_cache[inst_label]} ---", flush=True)
        rec = run_cell_granular(seed, K_MAX, edges, cut_cache[inst_label], shots, maxiter,
                                sim, n_qubits, circ_cache[inst_label])
        rec["instance"] = inst_label
        rec["max_cut"] = cut_cache[inst_label]
        results.append(rec)
        ck = _load_ckpt()
        ck["mode"] = mode
        ck["data"] = results
        _save_ckpt(ck)

    summary = summarize(results, K_MAX)
    out = {"experiment": "Exp64-granular",
           "title": "Draw-one-more-at-a-time (1->2->3) warm-start escalation",
           "author": "Elder", "cycle": "C6132", "mode": mode,
           "k_max": K_MAX, "shots": shots, "maxiter": maxiter,
           "summary": summary,
           "data": sorted(results, key=lambda r: (r.get("instance", ""), r["seed"]))}
    json.dump(out, open(RESULTS, "w"), indent=2)
    print(f"\n  Wrote {RESULTS}")


if __name__ == "__main__":
    main()
