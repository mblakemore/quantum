#!/usr/bin/env python3
"""
Exp61: Best-of-k p3 anchor selection — does ACTIVELY selecting the best of k anchors
recover warm-start lift, or does the p5 re-optimization wash the anchor advantage out?
Elder C6065 (pre-reg + build).

Pre-registration: /droid/repos/quantum/experiments/exp61-bestofk-anchor-selection-preregistration.md
                  DC1.5 state/experiments/c6065-exp61-bestofk-anchor-selection.json

THE GAP THIS CLOSES (Rung-1 -> Rung-2)
  Exp59/F32 (C6051) found OBSERVATIONALLY that warm-start lift is mediated by p3-anchor
  quality: rho(r_p3_base, lift) = +0.853 across naturally-drawn anchors; and H3 was NULL
  (no cheap a-priori x0 stat predicts anchor quality -> selection must be EMPIRICAL
  best-of-k p3 multi-start, not a filter). Findings 29/30/32/33/35 all RECOMMEND best-of-k
  anchor selection; NONE has run it. This is the INTERVENTIONAL test: when we do(select the
  best of k p3 anchors) and warm-start p5 from it, does warm-start lift actually RISE, or does
  the p5 COBYLA re-converge basin-independently and make selection cosmetic?

  Action it changes (EVI gate, C6044): whether the warm-start protocol ADOPTS best-of-k p3
  pre-selection (and at what k) vs single-anchor warm-start. A REFUTE closes the lever the
  program has pointed at for 5 findings.

DESIGN (paired; controls cold-luck; built-in Exp59 regression check)
  Instance = EDGES_20. k = 4 anchors. Per opt-seed (np.random.seed(seed); draw order chosen so
  the k=1 leg reproduces Exp59 EXACTLY):
    x0_cold = uniform(0,2pi,10) -> COBYLA p5 -> r_cold            [identical to Exp59]
    anchors j=0..k-1: x0_p3_j = uniform(0,2pi,6) -> COBYLA p3 -> (r3_j, x3_j)
        (j=0 reproduces Exp59 single x0_p3 -> r_p3_base : REGRESSION CHECK)
    single = anchor 0 ; best = argmax_j r3_j
    warm_single = pad(x3_single)->p5->COBYLA -> r_warm_single      [reproduces Exp59 r_warm_p5]
    warm_best   = pad(x3_best)->p5->COBYLA   -> r_warm_best
    lift_single = r_warm_single - r_cold ; lift_best = r_warm_best - r_cold
    Dlift = lift_best - lift_single  (paired; r_cold cancels -> Dlift = r_warm_best - r_warm_single)

HYPOTHESES (named, pre-disclosed; graded against these — no post-hoc threshold)
  H1 (PRIMARY, INTERVENTIONAL): best-of-k recovers lift.
     mean(lift_best) > mean(lift_single) AND mean(Dlift) > 0 with >= 7/12 trials Dlift>0.
     REFUTE if mean(lift_best) <= mean(lift_single) (p5 re-opt washes anchor advantage out).
  H2 (MECHANISM): anchor advantage survives the p5 re-opt.
     rho(Dr_p3, Dr_warm) > +0.30 ; Dr_p3 = r_p3_best - r_p3_single (>=0 by construction),
     Dr_warm = r_warm_best - r_warm_single. Pre-disclosed POSITIVE. rho<=0 => selection cosmetic.
     Report #trials best==single (Dr_p3=0, selection inert: already-good anchor, not a failure).
  H3 (RESCUE STRUCTURE): value concentrates on bad single anchors.
     rho(r_p3_single, Dlift) < 0 (worse single anchor -> bigger rescue). Pre-disclosed NEGATIVE
     (monotone-floor inheritance, C5980). Makes "gate min anchor quality" actionable.
  H4 (COST, reported NOT thresholded): mean(Dlift) vs budget (p3_depth/p5_depth, p3-evals=k*maxiter,
     lift-gain-per-extra-p3-eval). Informs adopted k. Do NOT call the lift "free".

SCOPE/HONESTY
  - PILOT fidelity (256 sh / maxiter 20). SIGN + rough magnitude, not a 1024sh campaign.
  - n=12 Spearman reported WITH caveat (n=12 two-sided a=.05 sig crit |rho|~0.587, C6051);
    +0.30 bars are SIGN/direction tests; 0.30<|rho|<0.587 flagged NULL-consistent.
  - Paired (same r_cold per trial) controls cold-luck.
  - seeds retained as drawn; NO dropping (C5923; Exp57/59 retained seed44).
  - Selection makes r_p3_best>=r_p3_single by construction -> H1 NOT a tautology; the open
    question is whether the advantage SURVIVES p5 re-opt (H2).

USAGE
  python3 run_exp61_bestofk_anchor.py --smoke   # 3 seeds, k=3, 128sh, maxiter 8 — plumbing/timing
  python3 run_exp61_bestofk_anchor.py --run      # 8 seeds (42-49), k=3, 256sh, maxiter 20 — real run (background; matches pre-reg)
"""
import sys, os, json, time, argparse
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_exp46_fast import (
    EDGES_20, N_QUBITS_20,
    brute_force_max_cut,
    build_parameterized_xbasis_qaoa,
    evaluate_with_transpiled,
)
from run_exp54_warmstart import optimize_cobyla_ws, pad_params
from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime.fake_provider import FakeMarrakesh

OPT_LEVEL = 1
EDGES_20_THRESHOLD = 0.640   # context only; NOT the metric

CKPT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "..", "results", "exp61_checkpoint.json")
RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "experiments", "exp61_results.json")


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


def build_for_p(p, sim, n_qubits, edges):
    qc, gp, bp = build_parameterized_xbasis_qaoa(p, n_qubits, edges)
    tqc = transpile(qc, backend=sim, optimization_level=OPT_LEVEL)
    return tqc, gp, bp


def run_seed(seed, k, edges, max_cut, shots, maxiter, sim, n_qubits, circuits):
    """Paired best-of-k vs single-anchor warm-start for one opt-seed on EDGES_20.
    Draw order: x0_cold(10), then k x0_p3(6) anchors -> j=0 reproduces Exp59 exactly."""
    np.random.seed(seed)
    t0 = time.time()
    tqc5, gp5, bp5 = circuits[5]
    tqc3, gp3, bp3 = circuits[3]

    # ---- cold-start p5 (identical draw to Exp59) ----
    x0_cold = np.random.uniform(0, 2 * np.pi, 10)
    r_cold, _ = optimize_cobyla_ws(x0_cold, tqc5, gp5, bp5, 5, sim, edges, max_cut,
                                   n_qubits, shots, maxiter)

    # ---- k p3 anchors (j=0 reproduces Exp59's single x0_p3 -> r_p3_base) ----
    anchors = []  # list of (r3, x3)
    for j in range(k):
        x0_p3 = np.random.uniform(0, 2 * np.pi, 6)
        r3, x3 = optimize_cobyla_ws(x0_p3, tqc3, gp3, bp3, 3, sim, edges, max_cut,
                                    n_qubits, shots, maxiter)
        anchors.append((float(r3), np.asarray(x3, dtype=float)))

    r3_single, x3_single = anchors[0]
    best_idx = int(np.argmax([a[0] for a in anchors]))
    r3_best, x3_best = anchors[best_idx]

    # ---- warm p5 from single anchor (reproduces Exp59 r_warm_p5) ----
    x0_warm_s = pad_params(x3_single, 3, 5)
    r_warm_single, _ = optimize_cobyla_ws(x0_warm_s, tqc5, gp5, bp5, 5, sim, edges, max_cut,
                                          n_qubits, shots, maxiter)
    # ---- warm p5 from best-of-k anchor (skip re-opt if best is the single anchor) ----
    if best_idx == 0:
        r_warm_best = r_warm_single
    else:
        x0_warm_b = pad_params(x3_best, 3, 5)
        r_warm_best, _ = optimize_cobyla_ws(x0_warm_b, tqc5, gp5, bp5, 5, sim, edges, max_cut,
                                            n_qubits, shots, maxiter)

    lift_single = r_warm_single - r_cold
    lift_best = r_warm_best - r_cold
    rec = {"seed": seed, "k": k,
           "r_cold_p5": r_cold,
           "r_p3_anchors": [a[0] for a in anchors],
           "best_idx": best_idx,
           "r_p3_single": r3_single, "r_p3_best": r3_best,
           "r_warm_single": r_warm_single, "r_warm_best": r_warm_best,
           "lift_single": lift_single, "lift_best": lift_best,
           "d_lift": lift_best - lift_single,
           "d_r_p3": r3_best - r3_single,
           "d_r_warm": r_warm_best - r_warm_single,
           "selection_inert": best_idx == 0,
           "elapsed_s": time.time() - t0}
    print(f"  seed={seed} cold={r_cold:.4f} p3[{','.join(f'{a[0]:.3f}' for a in anchors)}]"
          f" best#{best_idx}={r3_best:.4f} warm_s={r_warm_single:.4f} warm_b={r_warm_best:.4f}"
          f" lift_s={lift_single:+.4f} lift_b={lift_best:+.4f} Dlift={rec['d_lift']:+.4f}"
          f" ({rec['elapsed_s']:.0f}s)", flush=True)
    return rec


def _spearman(a, b):
    """Spearman rho via rank-Pearson (no scipy.stats dep). None if degenerate."""
    a = np.asarray(a, dtype=float); b = np.asarray(b, dtype=float)
    if len(a) < 3:
        return None
    ra = np.argsort(np.argsort(a)).astype(float)
    rb = np.argsort(np.argsort(b)).astype(float)
    if np.std(ra) == 0 or np.std(rb) == 0:
        return None
    return float(np.corrcoef(ra, rb)[0, 1])


# n=12 two-sided alpha=.05 Spearman significance crit ~0.587 (C6051 underpowered-bar discipline)
SIG_CRIT_N12 = 0.587


def _rho_flag(rho, n):
    if rho is None:
        return "degenerate"
    crit = SIG_CRIT_N12 if n <= 13 else 0.30
    if abs(rho) >= crit:
        return "significant" if n <= 13 else "strong"
    if abs(rho) >= 0.30:
        return "direction-only(NULL-consistent at this n)"
    return "weak/null"


def summarize(results, k):
    rs = sorted(results, key=lambda r: r["seed"])
    n = len(rs)
    lift_s = [r["lift_single"] for r in rs]
    lift_b = [r["lift_best"] for r in rs]
    dlift = [r["d_lift"] for r in rs]
    dp3 = [r["d_r_p3"] for r in rs]
    dwarm = [r["d_r_warm"] for r in rs]
    p3_single = [r["r_p3_single"] for r in rs]
    n_inert = sum(1 for r in rs if r["selection_inert"])

    print("\n" + "=" * 70)
    print(f"SUMMARY — Exp61 best-of-{k} anchor selection, N={n} seeds on EDGES_20")
    print("=" * 70)
    print(f"  lift_single mean={np.mean(lift_s):+.4f} std={np.std(lift_s):.4f} "
          f"(pos {sum(1 for l in lift_s if l>0)}/{n})")
    print(f"  lift_best   mean={np.mean(lift_b):+.4f} std={np.std(lift_b):.4f} "
          f"(pos {sum(1 for l in lift_b if l>0)}/{n})")
    print(f"  Dlift       mean={np.mean(dlift):+.4f} std={np.std(dlift):.4f} "
          f"(pos {sum(1 for d in dlift if d>0)}/{n})")
    print(f"  selection inert (best==single): {n_inert}/{n}")

    # H1 (vote threshold N-relative: >=60% of trials, ceil)
    dlift_pos = sum(1 for d in dlift if d > 0)
    vote_need = int(np.ceil(0.6 * n))
    h1 = (np.mean(lift_b) > np.mean(lift_s)) and (np.mean(dlift) > 0) and (dlift_pos >= vote_need)
    print("\n  -- H1 PRIMARY (best-of-k recovers lift, interventional) --")
    print(f"     mean(lift_best)={np.mean(lift_b):+.4f} vs mean(lift_single)={np.mean(lift_s):+.4f}")
    print(f"     mean(Dlift)={np.mean(dlift):+.4f}  Dlift>0: {dlift_pos}/{n} (need >={vote_need})")
    print(f"     H1 verdict: {'SUPPORTED' if h1 else 'REFUTED / MIXED'}")

    # H2 mechanism: anchor advantage survives p5 re-opt
    rho_dp3_dwarm = _spearman(dp3, dwarm)
    print("\n  -- H2 MECHANISM (anchor advantage survives p5 re-opt) --")
    print(f"     rho(Dr_p3, Dr_warm) = {rho_dp3_dwarm}  [{_rho_flag(rho_dp3_dwarm, n)}]")
    print(f"     (note: {n_inert}/{n} trials had Dr_p3=0 -> selection inert; "
          f"mean Dr_p3={np.mean(dp3):+.4f} mean Dr_warm={np.mean(dwarm):+.4f})")
    h2 = rho_dp3_dwarm is not None and rho_dp3_dwarm > 0.30
    print(f"     H2 verdict: {'SUPPORTED (direction)' if h2 else 'REFUTED / MIXED'}")

    # H3 rescue structure
    rho_single_dlift = _spearman(p3_single, dlift)
    print("\n  -- H3 RESCUE STRUCTURE (value concentrates on bad single anchors) --")
    print(f"     rho(r_p3_single, Dlift) = {rho_single_dlift}  [{_rho_flag(rho_single_dlift, n)}]")
    h3 = rho_single_dlift is not None and rho_single_dlift < -0.30
    print(f"     H3 verdict: {'SUPPORTED (direction)' if h3 else 'REFUTED / MIXED'}")

    # H4 cost
    p3_evals = k * 20  # maxiter for --run; informational
    gain_per_extra = (np.mean(dlift) / max(1, (k - 1))) if k > 1 else 0.0
    print("\n  -- H4 COST (reported, not thresholded) --")
    print(f"     extra p3 optimizations/trial = {k-1}; mean Dlift = {np.mean(dlift):+.4f}")
    print(f"     lift-gain per extra anchor   = {gain_per_extra:+.5f}")
    print("     (depth ratio printed at build; lift is NOT free — bought with k* anchor compute)")

    return {
        "n": n, "k": k,
        "mean": {"lift_single": float(np.mean(lift_s)), "lift_best": float(np.mean(lift_b)),
                 "d_lift": float(np.mean(dlift)), "d_r_p3": float(np.mean(dp3)),
                 "d_r_warm": float(np.mean(dwarm))},
        "std": {"lift_single": float(np.std(lift_s)), "lift_best": float(np.std(lift_b)),
                "d_lift": float(np.std(dlift))},
        "dlift_pos": dlift_pos, "selection_inert": n_inert,
        "H1": {"mean_lift_best": float(np.mean(lift_b)), "mean_lift_single": float(np.mean(lift_s)),
               "mean_d_lift": float(np.mean(dlift)), "d_lift_pos": dlift_pos,
               "vote_need": vote_need, "supported": bool(h1)},
        "H2": {"rho_dp3_dwarm": rho_dp3_dwarm, "flag": _rho_flag(rho_dp3_dwarm, n),
               "supported": bool(h2)},
        "H3": {"rho_single_dlift": rho_single_dlift, "flag": _rho_flag(rho_single_dlift, n),
               "supported": bool(h3)},
        "H4": {"extra_p3_per_trial": k - 1, "mean_d_lift": float(np.mean(dlift)),
               "gain_per_extra_anchor": float(gain_per_extra), "p3_evals_per_trial": p3_evals},
        "sig_crit_n12": SIG_CRIT_N12,
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
        opt_seeds, k, shots, maxiter, mode = [42, 43, 44], 3, 128, 8, "SMOKE"
    else:
        # Right-sized vs Exp59's REAL ~10.9h/seed (C6035 lesson): k=3/N=8 keeps the campaign
        # near Exp59's footprint (Exp61 has more opts/seed). seeds 42-49 overlap Exp59 42-49.
        opt_seeds, k, shots, maxiter, mode = list(range(42, 50)), 3, 256, 20, "RUN"

    edges, n_qubits = EDGES_20, N_QUBITS_20
    print("=" * 70)
    print(f"Exp61 Best-of-{k} Anchor Selection — {mode}")
    print(f"instance=EDGES_20 opt_seeds={opt_seeds} k={k} shots={shots} maxiter={maxiter}")
    print(f"metric = paired Dlift = lift_best - lift_single (interventional best-of-k)")
    print("=" * 70, flush=True)

    fake = FakeMarrakesh()
    sim = AerSimulator(noise_model=NoiseModel.from_backend(fake))

    ckpt = _load_ckpt()
    if ckpt.get("mode") and ckpt.get("mode") != mode:
        bak = CKPT + f".stale-{ckpt.get('mode')}.bak"
        os.replace(CKPT, bak)
        print(f"  [reset] checkpoint mode {ckpt.get('mode')} != {mode}; backed up to {bak}", flush=True)
        ckpt = {}
    done = {r["seed"]: r for r in ckpt.get("data", [])}
    if done:
        print(f"  [resume] {len(done)} seed(s) done: {sorted(done)}", flush=True)
    results = list(ckpt.get("data", []))

    max_cut = brute_force_max_cut(n_qubits, edges)
    circuits = {p: build_for_p(p, sim, n_qubits, edges) for p in (3, 5)}
    print(f"--- EDGES_20: max_cut={max_cut}, "
          f"p3depth={circuits[3][0].depth()} p5depth={circuits[5][0].depth()} "
          f"(p3/p5 depth ratio {circuits[3][0].depth()/circuits[5][0].depth():.3f}) ---", flush=True)

    for seed in opt_seeds:
        if seed in done:
            continue
        rec = run_seed(seed, k, edges, max_cut, shots, maxiter, sim, n_qubits, circuits)
        rec["max_cut"] = max_cut
        results.append(rec)
        ck = _load_ckpt()
        ck["mode"] = mode
        ck["data"] = results
        _save_ckpt(ck)

    summary = summarize(results, k)
    out = {"experiment": "Exp61", "title": "Best-of-k p3 anchor selection (interventional warm-start)",
           "author": "Elder", "cycle": "C6065", "mode": mode, "instance": "EDGES_20",
           "opt_seeds": opt_seeds, "k": k, "shots": shots, "maxiter": maxiter,
           "edges20_threshold_context": EDGES_20_THRESHOLD,
           "summary": summary, "data": sorted(results, key=lambda r: r["seed"])}
    json.dump(out, open(RESULTS, "w"), indent=2)
    print(f"\n  Wrote {RESULTS}")


if __name__ == "__main__":
    main()
