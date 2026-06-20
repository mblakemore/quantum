#!/usr/bin/env python3
"""
Exp57: Instance-Generalization (External-Validity Arm of the Warm-Start Program)
Elder C5994 (pre-reg + build)

Pre-registration: /droid/repos/quantum/experiments/exp57-instance-generalization-preregistration.md

THE GAP THIS CLOSES
  Every escape / warm-start finding in the program (Exp48-54, Findings 23-27) sits on a
  SINGLE random MaxCut instance: EDGES_20 (numpy seed=46, 20 nodes, 30 edges). The Exp54
  interpretation-scope block states it outright: "the 10 seeds vary only x0, NOT the graph,
  so H1 speaks only to warm-start convergence ON THIS INSTANCE." Whisper varies x0; Ember
  varies the noise channel — both hold the GRAPH fixed. The external-validity question —
  does the warm-start lift replicate across DIFFERENT random instances, or is it an
  EDGES_20 landscape artifact? — has never been run. Exp57 varies the GRAPH.

DESIGN (instance-AGNOSTIC by construction)
  Instance 0 = EDGES_20 (the reference; reproduces the known regime at this budget).
  Instances 1..K = fresh random 20-node / 30-edge graphs, distinct numpy seeds.
  ALL instances run at the IDENTICAL (low-fidelity) budget — apples-to-apples; the budget
  reduction is a CONTROLLED constant, so a lift on instance 0 but not on the others is
  interpretable as instance-dependence, not budget noise.

  Per (instance, seed):
    cold_p5 : COBYLA at p=5 from a random x0                       -> r_cold
    warm_p5 : COBYLA at p=3 from random x0 -> best (gamma,beta)_p3 -> pad to p=5
              (zeros for new layers, identity warm-start) -> COBYLA -> r_warm
  Metric (NO 0.640 threshold transfer — that constant is EDGES_20-specific):
    per instance  delta = mean_seeds(r_warm) - mean_seeds(r_cold)
  delta is a pure approximation-ratio lift, comparable across instances with different
  optimal cuts (each r is already normalized by that instance's brute-force max_cut).

HYPOTHESES
  H1 (external validity, PRIMARY): warm-start lift replicates. Refute if delta <= 0 on a
      MAJORITY of the new instances (=> the warm-start benefit is an EDGES_20 artifact).
  H2 (magnitude): new-instance |delta| is the same order as EDGES_20's delta at this budget
      (not 10x larger/smaller). Catches "replicates in sign but is a different phenomenon."

SCOPE / HONESTY
  - This is a PILOT for external validity at REDUCED fidelity (low shots / few seeds / low
    maxiter), NOT the definitive 1024sh/10-seed campaign. It establishes SIGN and rough
    MAGNITUDE of instance-dependence, sized to complete in one sitting.
  - Edge generation here samples 30 distinct edges uniformly from C(20,2); it does NOT claim
    to reproduce EDGES_20's exact original generator (unrecoverable) — only the same family
    (20-node, 30-edge random). EDGES_20 itself is included verbatim as the reference.
  - Structured-instance arm (planted/regular graphs, the Elder-C5972 structure-vs-landscape
    question) is the SEPARATE next step — not built here.

USAGE
  python3 run_exp57_instance_generalization.py --smoke   # ref + 1 new, 2 seeds, 128sh — plumbing + timing
  python3 run_exp57_instance_generalization.py --pilot   # ref + 3 new, 3 seeds, 256sh — the real pilot
  python3 run_exp57_instance_generalization.py --full    # ref + 5 new, 5 seeds, 512sh — heavier (background)
"""
import sys, os, json, time, argparse
import numpy as np
from scipy.optimize import minimize

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
N_EDGES = 30
# Reference EDGES_20's escape threshold (reported for context only; NOT used as the metric).
EDGES_20_THRESHOLD = 0.640

CKPT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "..", "results", "exp57_checkpoint.json")
RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "experiments", "exp57_results.json")


def gen_instance(inst_seed, n_qubits=N_QUBITS_20, n_edges=N_EDGES):
    """Fresh random n_qubits-node, n_edges-edge graph. Same family as EDGES_20
    (20 nodes, 30 edges); generator is documented (uniform over C(n,2)), not a claim
    to reproduce EDGES_20's exact original sampler. Returns sorted edge list."""
    rng = np.random.RandomState(inst_seed)
    all_pairs = [(i, j) for i in range(n_qubits) for j in range(i + 1, n_qubits)]
    idx = rng.choice(len(all_pairs), size=n_edges, replace=False)
    return sorted(all_pairs[k] for k in idx)


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


def run_instance_seed(inst_label, edges, max_cut, seed, shots, maxiter, sim, n_qubits, circuits):
    """cold-p5 and warm(p3->p5) for one (instance, seed). Paired on the same instance+noise."""
    np.random.seed(seed)
    t0 = time.time()

    # ---- cold-start p5 (random x0 at p=5) ----
    tqc5, gp5, bp5 = circuits[5]
    x0_cold = np.random.uniform(0, 2 * np.pi, 10)
    r_cold, _ = optimize_cobyla_ws(x0_cold, tqc5, gp5, bp5, 5, sim, edges, max_cut,
                                   n_qubits, shots, maxiter)

    # ---- warm-start p5 (p3 base -> pad -> p5) ----
    tqc3, gp3, bp3 = circuits[3]
    x0_p3 = np.random.uniform(0, 2 * np.pi, 6)
    r3, x3 = optimize_cobyla_ws(x0_p3, tqc3, gp3, bp3, 3, sim, edges, max_cut,
                                n_qubits, shots, maxiter)
    x0_warm = pad_params(x3, 3, 5)
    r_warm, _ = optimize_cobyla_ws(x0_warm, tqc5, gp5, bp5, 5, sim, edges, max_cut,
                                   n_qubits, shots, maxiter)

    rec = {"instance": inst_label, "seed": seed,
           "r_cold_p5": r_cold, "r_p3_base": r3, "r_warm_p5": r_warm,
           "lift": r_warm - r_cold, "elapsed_s": time.time() - t0}
    print(f"  [{inst_label}] seed={seed}  cold={r_cold:.4f}  p3={r3:.4f}  warm={r_warm:.4f}"
          f"  lift={r_warm - r_cold:+.4f}  ({rec['elapsed_s']:.0f}s)", flush=True)
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--pilot", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if not (args.smoke or args.pilot or args.full):
        print("Specify --smoke | --pilot | --full. Refusing to guess.")
        sys.exit(2)

    # New-instance seeds (distinct from EDGES_20's seed=46).
    NEW_SEEDS = [101, 202, 303, 404, 505]
    if args.smoke:
        new_inst_seeds, opt_seeds, shots, maxiter, mode = NEW_SEEDS[:1], [42, 43], 128, 8, "SMOKE"
    elif args.pilot:
        new_inst_seeds, opt_seeds, shots, maxiter, mode = NEW_SEEDS[:3], [42, 43, 44], 256, 20, "PILOT"
    else:
        new_inst_seeds, opt_seeds, shots, maxiter, mode = NEW_SEEDS[:5], [42, 43, 44, 45, 46], 512, 35, "FULL"

    # Instance roster: ref EDGES_20 first, then fresh graphs.
    instances = [("EDGES_20_ref", EDGES_20)]
    for s in new_inst_seeds:
        instances.append((f"rand_seed{s}", gen_instance(s)))

    print("=" * 70)
    print(f"Exp57 Instance-Generalization — {mode}")
    print(f"instances={[lbl for lbl, _ in instances]}")
    print(f"opt_seeds={opt_seeds} shots={shots} maxiter={maxiter}")
    print(f"metric = lift = r_warm_p5 - r_cold_p5 (instance-agnostic; 0.640 NOT used)")
    print("=" * 70, flush=True)

    fake = FakeMarrakesh()
    sim = AerSimulator(noise_model=NoiseModel.from_backend(fake))
    n_qubits = N_QUBITS_20

    ckpt = _load_ckpt()
    if ckpt.get("mode") and ckpt.get("mode") != mode:
        bak = CKPT + f".stale-{ckpt.get('mode')}.bak"
        os.replace(CKPT, bak)
        print(f"  [reset] checkpoint mode {ckpt.get('mode')} != {mode}; backed up to {bak}", flush=True)
        ckpt = {}
    done = {(r["instance"], r["seed"]): r for r in ckpt.get("data", [])}
    if done:
        print(f"  [resume] {len(done)} (instance,seed) cell(s) done", flush=True)
    results = list(ckpt.get("data", []))

    for inst_label, edges in instances:
        max_cut = brute_force_max_cut(n_qubits, edges)
        circuits = {p: build_for_p(p, sim, n_qubits, edges) for p in (3, 5)}
        print(f"\n--- instance {inst_label}: max_cut={max_cut}, "
              f"p3depth={circuits[3][0].depth()} p5depth={circuits[5][0].depth()} ---", flush=True)
        for seed in opt_seeds:
            if (inst_label, seed) in done:
                continue
            rec = run_instance_seed(inst_label, edges, max_cut, seed, shots, maxiter,
                                    sim, n_qubits, circuits)
            rec["max_cut"] = max_cut
            results.append(rec)
            ck = _load_ckpt()
            ck["mode"] = mode
            ck["data"] = results
            _save_ckpt(ck)

    # ── Summary: per-instance lift ──
    print("\n" + "=" * 70)
    print("SUMMARY — per-instance warm-start lift (delta = mean r_warm - mean r_cold)")
    print("=" * 70)
    per_inst = {}
    for inst_label, _ in instances:
        rs = [r for r in results if r["instance"] == inst_label]
        if not rs:
            continue
        mc = float(np.mean([r["r_cold_p5"] for r in rs]))
        mw = float(np.mean([r["r_warm_p5"] for r in rs]))
        delta = mw - mc
        per_inst[inst_label] = {"n": len(rs), "mean_cold": mc, "mean_warm": mw, "delta": delta}
        print(f"  {inst_label:16s} n={len(rs)}  cold={mc:.4f}  warm={mw:.4f}  delta={delta:+.4f}")

    ref_delta = per_inst.get("EDGES_20_ref", {}).get("delta")
    new = {k: v for k, v in per_inst.items() if k != "EDGES_20_ref"}
    if new and ref_delta is not None:
        pos = sum(1 for v in new.values() if v["delta"] > 0)
        print(f"\n  reference EDGES_20 delta = {ref_delta:+.4f}")
        print(f"  new instances with delta>0: {pos}/{len(new)}  "
              f"(H1 supported if majority > 0)")
        print(f"  H1 verdict: {'SUPPORTED' if pos > len(new) / 2 else 'REFUTED / MIXED'}")

    out = {"experiment": "Exp57", "title": "Instance-Generalization (external validity)",
           "author": "Elder", "mode": mode, "opt_seeds": opt_seeds, "shots": shots,
           "maxiter": maxiter, "edges20_threshold_context": EDGES_20_THRESHOLD,
           "per_instance": per_inst, "data": results}
    json.dump(out, open(RESULTS, "w"), indent=2)
    print(f"\n  Wrote {RESULTS}")


if __name__ == "__main__":
    main()
