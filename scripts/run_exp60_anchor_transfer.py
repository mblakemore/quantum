#!/usr/bin/env python3
"""
Exp60: Anchor TRANSFER — does a warm-start anchor LEARNED on graph A lift a DIFFERENT graph B?
Elder C6045 (pre-reg + build)

WHAT MAKES THIS DISTINCT FROM EXP57 (Finding 29)
  Exp57 varied the GRAPH and warm-started each instance from its OWN anchor — it asked
  "does the within-instance warm-start LIFT replicate across graphs?" (answer: yes, x0-gated).
  Exp60 asks the TRANSFER question: take the p3 anchor optimized on SOURCE instance S, pad to
  p5, and apply it to a DIFFERENT TARGET instance T. Does S's anchor lift T above T's cold
  baseline? This is the QAOA parameter-concentration / transferability question (Galda 2021,
  Akshay 2021, Brandao 2018) and the quantum analog of the trading regime-transfer problem
  (Whisper C4275 named regime-transfer my highest-uncertainty variable). C6011 named this arm
  explicitly: "next separate arm = cross-instance param TRANSFER (Ember C3862 parity)."
  exp59's own pre-reg: "Generalization of the MEDIATION across instances = a separate future arm."

DESIGN (same 20-node/30-edge family as EDGES_20 + Exp57; pilot at reduced node-count for tractability)
  K instances I_0..I_{K-1} (gen_instance, fresh seeds; same family/density 1.5).
  Per instance (3 COBYLA optimizes; np.random.seed(inst_seed) for reproducible x0, Exp54/57 convention):
    anchor_p3 : COBYLA p=3 from random x0 (len 6)  -> r_p3(I),  x_anchor_p3(I)
    cold_p5   : COBYLA p=5 from random x0 (len 10) -> r_cold(I)              [baseline]
    self_warm : pad own anchor_p3 -> COBYLA p=5    -> r_self(I)              [Finding-29 within-instance lift]
  Transfer matrix (K*K CHEAP direct evals, NO re-optimization — pure parameter concentration):
    r_xfer[S][T] = evaluate( pad(x_anchor_p3(S)) on T's p5 circuit )
  Diagonal r_xfer[T][T] = direct eval of T's own padded p3 anchor (no finetune) — separates
    "transfer loss" (off-diag) from "finetune loss" (self_warm vs self_direct).

METRICS
  self_lift(T)             = r_self(T)      - r_cold(T)   (within-instance warm-start; >0 expected per F29)
  self_direct_lift(T)      = r_xfer[T][T]   - r_cold(T)   (own anchor, NO finetune)
  xfer_direct_lift(S->T)   = r_xfer[S][T]   - r_cold(T)   (cross-instance, S!=T)
  transfer_efficiency(S->T)= xfer_direct_lift(S->T) / self_lift(T)   (1.0 = perfect transfer)

HYPOTHESES (pre-disclosed, code-grounded, graded against named observables; NO post-hoc thresholds)
  H1 TRANSFER POSITIVE (PRIMARY, conf 0.65): mean off-diagonal xfer_direct_lift > 0.
     PRIOR leans POSITIVE — QAOA optimal angles concentrate across same-family/size instances.
     REFUTE if mean off-diag xfer_direct_lift <= 0 (anchors are instance-specific overfit -> no
     transfer; that NULL is the informative/surprising outcome and the regime-transfer caution).
  H2 TRANSFER < SELF (conf 0.70): mean transfer_efficiency in (0, 1) — transfer helps but LESS
     than the self-anchor (a real instance-specificity cost). REFUTE if mean efficiency >= 1.0
     (anchors fully generic, no instance-specific component) OR <= 0 (folds into H1 refute).
  H3 DESTINATION-HEADROOM dominates SOURCE-QUALITY (conf 0.60): per Finding 30 lift is
     headroom-limited, so transfer lift on T tracks T's cold headroom more than S's anchor quality.
     rho( headroom(T)=p5_ceiling - r_cold(T),  mean_S xfer_direct_lift(S->T) ) > +0.30, and this
     EXCEEDS rho( r_p3(S), mean_T xfer_direct_lift(S->T) ). Extends F30's inverted-U to transfer.
     (p5_ceiling taken as max observed r_self across instances; reported, not a hard constant.)

SCOPE / HONESTY
  - PILOT runs at REDUCED node-count for one-sitting tractability; the 20-node run (comparable to
    Finding 29/30) is STAGED for when exp59 frees the box (~6/26). Parameter concentration is
    size-sensitive -> the pilot establishes SIGN + harness; the staged 20-node run gives the
    headline magnitude. Labeled, not hidden (C6035: time one cell before estimating the full run).
  - seeds retained as drawn; no dropping of inconvenient instances (C5923 flattering-result discipline).
  - Single family (random n-node, density 1.5). Structured-graph transfer (planted/regular) = future arm.

USAGE
  python3 run_exp60_anchor_transfer.py --smoke   # n=10, K=2, 128sh, maxiter 6  — plumbing + TIMING
  python3 run_exp60_anchor_transfer.py --pilot   # n=12, K=4, 256sh, maxiter 15 — the real pilot (this cycle)
  python3 run_exp60_anchor_transfer.py --full     # n=20, K=5, 512sh, maxiter 20 — STAGED post-exp59 (background, days)
"""
import sys, os, json, time, argparse
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_exp46_fast import (
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
DENSITY = 1.5  # EDGES_20 = 30 edges / 20 nodes; held constant across node-counts

CKPT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "..", "results", "exp60_checkpoint.json")
RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "results", "exp60_anchor_transfer_results.json")


def gen_instance(inst_seed, n_qubits, n_edges):
    """Fresh random n_qubits-node, n_edges-edge graph (same family as EDGES_20, density 1.5)."""
    rng = np.random.RandomState(inst_seed)
    all_pairs = [(i, j) for i in range(n_qubits) for j in range(i + 1, n_qubits)]
    idx = rng.choice(len(all_pairs), size=n_edges, replace=False)
    return sorted(all_pairs[k] for k in idx)


def build_for_p(p, sim, n_qubits, edges):
    qc, gp, bp = build_parameterized_xbasis_qaoa(p, n_qubits, edges)
    tqc = transpile(qc, backend=sim, optimization_level=OPT_LEVEL)
    return tqc, gp, bp


def _save(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    json.dump(obj, open(tmp, "w"), indent=2)
    os.replace(tmp, path)


def prep_instance(inst_seed, n_qubits, n_edges, shots, maxiter, sim):
    """Per-instance: build circuits, optimize p3 anchor, cold p5, self-warm p5.
    Returns a dict with ratios + the padded-to-p5 anchor for the transfer matrix."""
    edges = gen_instance(inst_seed, n_qubits, n_edges)
    max_cut = brute_force_max_cut(n_qubits, edges)
    tqc3, gp3, bp3 = build_for_p(3, sim, n_qubits, edges)
    tqc5, gp5, bp5 = build_for_p(5, sim, n_qubits, edges)

    np.random.seed(inst_seed)
    t0 = time.time()
    # p3 anchor (warm-start SOURCE)
    x0_p3 = np.random.uniform(0, 2 * np.pi, 6)
    r_p3, x_p3 = optimize_cobyla_ws(x0_p3, tqc3, gp3, bp3, 3, sim, edges, max_cut,
                                    n_qubits, shots, maxiter)
    # cold p5 baseline
    x0_cold = np.random.uniform(0, 2 * np.pi, 10)
    r_cold, _ = optimize_cobyla_ws(x0_cold, tqc5, gp5, bp5, 5, sim, edges, max_cut,
                                   n_qubits, shots, maxiter)
    # self warm-start p5 (pad own p3 anchor)
    x0_self = pad_params(x_p3, 3, 5)
    r_self, _ = optimize_cobyla_ws(x0_self, tqc5, gp5, bp5, 5, sim, edges, max_cut,
                                   n_qubits, shots, maxiter)
    elapsed = time.time() - t0
    print(f"  inst seed={inst_seed} n={n_qubits}: r_p3={r_p3:.4f} r_cold={r_cold:.4f} "
          f"r_self={r_self:.4f} self_lift={r_self - r_cold:+.4f} ({elapsed:.0f}s)", flush=True)
    return {
        "inst_seed": inst_seed, "n_qubits": n_qubits, "n_edges": n_edges,
        "edges": edges, "max_cut": max_cut,
        "r_p3": float(r_p3), "r_cold": float(r_cold), "r_self": float(r_self),
        "anchor_p5": pad_params(x_p3, 3, 5).tolist(),
        "elapsed_s": elapsed,
        # rebuildable circuit handles kept out of JSON; recomputed for transfer pass
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true", help="n=10 K=2 128sh maxiter6 — plumbing + TIMING")
    ap.add_argument("--pilot", action="store_true", help="n=12 K=4 256sh maxiter15 — real pilot (one sitting)")
    ap.add_argument("--full", action="store_true", help="n=20 K=5 512sh maxiter20 — STAGED post-exp59 (days)")
    args = ap.parse_args()

    if args.smoke:
        n_qubits, K, shots, maxiter, base_seed, mode = 10, 2, 128, 6, 200, "SMOKE"
    elif args.pilot:
        n_qubits, K, shots, maxiter, base_seed, mode = 12, 4, 256, 15, 300, "PILOT"
    elif args.full:
        n_qubits, K, shots, maxiter, base_seed, mode = 20, 5, 512, 20, 400, "FULL"
    else:
        print("Specify --smoke / --pilot / --full. Refusing to guess (C6035 discipline).")
        sys.exit(2)

    n_edges = int(round(DENSITY * n_qubits))
    inst_seeds = [base_seed + i for i in range(K)]

    print("=" * 70)
    print(f"Exp60 Anchor-Transfer — {mode}")
    print(f"n_qubits={n_qubits} n_edges={n_edges} K={K} seeds={inst_seeds} shots={shots} maxiter={maxiter}")
    print(f"metric = transfer matrix r_xfer[S][T] = eval(pad(anchor_p3(S)) on T) ; "
          f"xfer_lift = r_xfer - r_cold(T)")
    print("=" * 70, flush=True)

    fake = FakeMarrakesh()
    sim = AerSimulator(noise_model=NoiseModel.from_backend(fake))

    t_start = time.time()
    # ---- Pass 1: per-instance prep (the expensive optimizes) ----
    insts = []
    for s in inst_seeds:
        insts.append(prep_instance(s, n_qubits, n_edges, shots, maxiter, sim))
        _save(CKPT, {"mode": mode, "stage": "prep", "config": {
            "n_qubits": n_qubits, "n_edges": n_edges, "K": K, "shots": shots,
            "maxiter": maxiter, "seeds": inst_seeds}, "instances": insts})

    # ---- Pass 2: transfer matrix (cheap direct evals, NO optimize) ----
    print("\n--- transfer matrix (direct evals, no re-optimization) ---", flush=True)
    xfer = [[None] * K for _ in range(K)]
    for ti, T in enumerate(insts):
        tqc5, gp5, bp5 = build_for_p(5, sim, n_qubits, T["edges"])
        for si, S in enumerate(insts):
            r = evaluate_with_transpiled(np.array(S["anchor_p5"]), tqc5, gp5, bp5, 5,
                                         sim, T["edges"], T["max_cut"], n_qubits, shots)
            xfer[si][ti] = float(r)
        row = " ".join(f"{xfer[si][ti]:.4f}" for si in range(K))
        print(f"  T=seed{T['inst_seed']} r_cold={T['r_cold']:.4f} | r_xfer[S->T]: {row}", flush=True)

    # ---- Metrics ----
    p5_ceiling = max(I["r_self"] for I in insts)
    off_diag_lifts, effs = [], []
    per_target = {}
    for ti, T in enumerate(insts):
        self_lift = T["r_self"] - T["r_cold"]
        self_direct_lift = xfer[ti][ti] - T["r_cold"]
        tgt_xfer = []
        for si, S in enumerate(insts):
            if si == ti:
                continue
            xl = xfer[si][ti] - T["r_cold"]
            off_diag_lifts.append(xl)
            tgt_xfer.append(xl)
            if self_lift > 1e-9:
                effs.append(xl / self_lift)
        per_target[T["inst_seed"]] = {
            "r_cold": T["r_cold"], "self_lift": self_lift,
            "self_direct_lift": self_direct_lift,
            "headroom": p5_ceiling - T["r_cold"],
            "mean_xfer_lift_in": float(np.mean(tgt_xfer)) if tgt_xfer else 0.0,
        }

    # H3 correlations
    headrooms = [per_target[I["inst_seed"]]["headroom"] for I in insts]
    mean_xfer_in = [per_target[I["inst_seed"]]["mean_xfer_lift_in"] for I in insts]
    src_quality = [I["r_p3"] for I in insts]
    mean_xfer_out = []
    for si, S in enumerate(insts):
        outs = [xfer[si][ti] - insts[ti]["r_cold"] for ti in range(K) if ti != si]
        mean_xfer_out.append(float(np.mean(outs)) if outs else 0.0)

    def _spearman(a, b):
        a, b = np.asarray(a, float), np.asarray(b, float)
        if len(a) < 3 or np.std(a) == 0 or np.std(b) == 0:
            return None
        ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
        return float(np.corrcoef(ra, rb)[0, 1])

    rho_headroom = _spearman(headrooms, mean_xfer_in)
    rho_src = _spearman(src_quality, mean_xfer_out)

    summary = {
        "mode": mode, "config": {"n_qubits": n_qubits, "n_edges": n_edges, "K": K,
                                 "shots": shots, "maxiter": maxiter, "seeds": inst_seeds},
        "p5_ceiling": p5_ceiling,
        "H1_mean_offdiag_xfer_lift": float(np.mean(off_diag_lifts)),
        "H1_offdiag_lift_positive_frac": float(np.mean([x > 0 for x in off_diag_lifts])),
        "H2_mean_transfer_efficiency": float(np.mean(effs)) if effs else None,
        "H3_rho_headroom_vs_xferIn": rho_headroom,
        "H3_rho_srcQuality_vs_xferOut": rho_src,
        "per_target": per_target,
        "xfer_matrix": xfer,
        "instances": [{k: I[k] for k in ("inst_seed", "r_p3", "r_cold", "r_self")} for I in insts],
        "total_elapsed_s": time.time() - t_start,
    }
    _save(RESULTS, summary)

    print("\n" + "=" * 70)
    print(f"RESULTS ({mode})")
    print(f"  H1 mean off-diag xfer_lift = {summary['H1_mean_offdiag_xfer_lift']:+.4f} "
          f"(positive frac {summary['H1_offdiag_lift_positive_frac']:.2f}) "
          f"-> {'POSITIVE (transfer happens)' if summary['H1_mean_offdiag_xfer_lift'] > 0 else 'NULL/NEG (overfit)'}")
    eff = summary["H2_mean_transfer_efficiency"]
    print(f"  H2 mean transfer efficiency = {eff if eff is None else round(eff,3)} "
          f"(self_lift>0 targets only)")
    print(f"  H3 rho(headroom, xfer_in) = {rho_headroom}  vs  rho(src_quality, xfer_out) = {rho_src}")
    print(f"  p5 ceiling (max r_self) = {p5_ceiling:.4f}")
    print(f"  total elapsed = {summary['total_elapsed_s']:.0f}s")
    print(f"  saved -> {RESULTS}")
    print("=" * 70, flush=True)


if __name__ == "__main__":
    main()
