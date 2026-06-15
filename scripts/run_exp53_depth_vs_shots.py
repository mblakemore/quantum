#!/usr/bin/env python3
"""
Exp53: Depth vs Shots Tradeoff
Elder C5846 | Pre-registered 2026-06-15

Pre-registration: /droid/repos/quantum/experiments/exp53-preregistration.md

HYPOTHESES:
  H1: p=5 COBYLA escape rate at 1024sh < p=3 at 1024sh (threshold: p5_1024sh < 80%)
  H2: p=5 COBYLA escape rate at 256sh < p=3 at 256sh=60% (threshold: p5_256sh < 50%)
  H3: Depth gap widens with shots: gap_1024 > gap_256

REUSED FROM EXP51/EXP52 (same seeds 42-51, same threshold, same noise model):
  p=3, COBYLA, 256sh:  6/10 = 0.60 (Exp51 Phase A)
  p=3, COBYLA, 1024sh: 9/10 = 0.90 (Exp51 Phase C)

NEW RUNS:
  p=5, COBYLA, 256sh  x10 seeds (Arm C)
  p=5, COBYLA, 1024sh x10 seeds (Arm D)
  Total: 20 new runs
"""
import sys, os, json, time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_exp46_fast import (
    EDGES_20, N_QUBITS_20,
    brute_force_max_cut,
    build_parameterized_xbasis_qaoa,
    evaluate_with_transpiled,
)
from run_exp51_spsa_vs_cobyla import optimize_cobyla
from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime.fake_provider import FakeMarrakesh

ESCAPE_THRESHOLD = 0.640
SEEDS = list(range(42, 52))  # Same as Exp51/52
OPT_LEVEL = 1
MAX_ITER_P5 = 50  # More iterations for p=5 (10 params vs 6)

# C5860: per-seed checkpoint for observability + resume. The original launch ran
# 15h+ block-buffered (zero output, no checkpoint) and any session-kill lost ALL
# work. p=5 noisy-trajectory sim is far heavier than the 2-4h pre-reg estimate, so
# results are now flushed to disk after EVERY seed — a dead/killed run resumes from
# the last completed seed instead of restarting from zero.
CHECKPOINT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "..", "results", "exp53_checkpoint.json")


def _load_checkpoint():
    if os.path.exists(CHECKPOINT_PATH):
        try:
            with open(CHECKPOINT_PATH) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_checkpoint(ckpt):
    os.makedirs(os.path.dirname(CHECKPOINT_PATH), exist_ok=True)
    tmp = CHECKPOINT_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(ckpt, f, indent=2)
    os.replace(tmp, CHECKPOINT_PATH)  # atomic — never leaves a half-written file

# ============================================================
# REUSED DATA FROM EXP51 (p=3, verified same seeds/threshold/noise)
# ============================================================
EXP51_REUSED = {
    "p3_cobyla_256sh":  {"p": 3, "shots": 256,  "escaped": 6, "rate": 0.60, "source": "Exp51 Phase A"},
    "p3_cobyla_1024sh": {"p": 3, "shots": 1024, "escaped": 9, "rate": 0.90, "source": "Exp51 Phase C"},
}


def run_arm_depth(arm_label, p, shots, seeds, max_iter=30):
    """Run one arm. Returns (results_list, escaped_count, rate)."""
    print(f"\n{'='*60}", flush=True)
    print(f"ARM: {arm_label} | p={p} | shots={shots} | seeds={seeds}")
    print(f"Escape threshold: {ESCAPE_THRESHOLD} | max_iter={max_iter}")
    print(f"{'='*60}", flush=True)

    # Resume: skip seeds already completed in a prior (possibly killed) run.
    ckpt = _load_checkpoint()
    done = {int(r["seed"]): r for r in ckpt.get(arm_label, {}).get("data", [])}
    if done:
        print(f"  [resume] {len(done)} seed(s) already done: {sorted(done)}", flush=True)

    fake_backend = FakeMarrakesh()
    noise_model = NoiseModel.from_backend(fake_backend)
    sim = AerSimulator(noise_model=noise_model)

    edges = EDGES_20
    n_qubits = N_QUBITS_20
    max_cut = brute_force_max_cut(n_qubits, edges)

    qc, gamma_params, beta_params = build_parameterized_xbasis_qaoa(p, n_qubits, edges)
    transpiled_qc = transpile(qc, backend=sim, optimization_level=OPT_LEVEL)

    print(f"  Circuit depth (transpiled): {transpiled_qc.depth()}")
    print(f"  Parameters: {len(gamma_params) + len(beta_params)} ({len(gamma_params)} gammas + {len(beta_params)} betas)", flush=True)

    results = [done[s] for s in seeds if s in done]
    escaped_count = sum(1 for r in results if r["escaped"])

    for seed in seeds:
        if seed in done:
            continue
        np.random.seed(seed)
        t0 = time.time()

        ratio = optimize_cobyla(
            transpiled_qc, gamma_params, beta_params, p,
            sim, edges, max_cut, n_qubits, shots, max_iter
        )

        escaped = ratio > ESCAPE_THRESHOLD
        if escaped:
            escaped_count += 1

        elapsed = time.time() - t0
        status = "✓ ESCAPED" if escaped else "✗ trapped"
        print(f"  seed={seed}: ratio={ratio:.4f} {status} ({elapsed:.1f}s)", flush=True)

        results.append({
            "seed": seed,
            "ratio": float(ratio),
            "escaped": bool(escaped),
            "elapsed_s": float(elapsed)
        })

        # Checkpoint after EVERY seed (atomic) so progress survives any kill.
        ckpt = _load_checkpoint()
        ckpt[arm_label] = {
            "p": p, "shots": shots, "max_iter": max_iter,
            "escaped": escaped_count, "completed": len(results),
            "rate_so_far": escaped_count / len(results),
            "data": results,
        }
        _save_checkpoint(ckpt)

    rate = escaped_count / len(seeds)
    print(f"\n  ARM RESULT: {escaped_count}/{len(seeds)} = {rate:.2f} escape rate", flush=True)
    return results, escaped_count, rate


def evaluate_hypotheses(p3_256, p3_1024, p5_256_rate, p5_1024_rate):
    """Evaluate pre-registered hypotheses against results."""
    print("\n" + "=" * 60)
    print("HYPOTHESIS EVALUATION")
    print("=" * 60)

    gap_256 = p3_256 - p5_256_rate
    gap_1024 = p3_1024 - p5_1024_rate

    # H1: p5_1024sh < p3_1024sh (threshold: p5_1024sh < 80%)
    h1 = "CONFIRMED" if p5_1024_rate < 0.80 else "REFUTED"
    print(f"\nH1 (Depth penalty at 1024sh): {h1}")
    print(f"  p=3 1024sh: {p3_1024:.2f} | p=5 1024sh: {p5_1024_rate:.2f} | gap: {gap_1024:+.2f}")
    print(f"  Threshold for CONFIRMED: p5_1024sh < 0.80")

    # H2: p5_256sh < p3_256sh (threshold: p5_256sh < 50%)
    h2 = "CONFIRMED" if p5_256_rate < 0.50 else "REFUTED"
    print(f"\nH2 (Depth penalty at 256sh): {h2}")
    print(f"  p=3 256sh: {p3_256:.2f} | p=5 256sh: {p5_256_rate:.2f} | gap: {gap_256:+.2f}")
    print(f"  Threshold for CONFIRMED: p5_256sh < 0.50")

    # H3: gap widens with shots
    h3 = "CONFIRMED" if gap_1024 > gap_256 else "REFUTED"
    print(f"\nH3 (Gap widens with shots): {h3}")
    print(f"  gap_256={gap_256:+.2f} | gap_1024={gap_1024:+.2f}")
    print(f"  CONFIRMED if gap_1024 > gap_256")

    return {"H1": h1, "H2": h2, "H3": h3,
            "gap_256": gap_256, "gap_1024": gap_1024}


def main():
    print("=" * 70)
    print("EXP53: Depth vs Shots Tradeoff (p=3 vs p=5)")
    print(f"Elder C5846 | FakeMarrakesh (AerSimulator) | Seeds: {SEEDS}")
    print(f"Escape threshold: {ESCAPE_THRESHOLD}")
    print("=" * 70)
    print()
    print("REUSED FROM EXP51/52 (p=3 baseline):")
    for k, v in EXP51_REUSED.items():
        print(f"  {k}: {v['escaped']}/10 = {v['rate']:.2f} ({v['source']})")
    print()

    all_results = {}

    # Arm C: p=5, COBYLA, 256 shots
    arm_c_data, arm_c_escaped, arm_c_rate = run_arm_depth(
        "p5_COBYLA_256sh", p=5, shots=256, seeds=SEEDS, max_iter=MAX_ITER_P5
    )
    all_results["p5_cobyla_256sh"] = {
        "p": 5, "optimizer": "COBYLA", "shots": 256,
        "escaped": arm_c_escaped, "rate": arm_c_rate,
        "data": arm_c_data
    }

    # Arm D: p=5, COBYLA, 1024 shots
    arm_d_data, arm_d_escaped, arm_d_rate = run_arm_depth(
        "p5_COBYLA_1024sh", p=5, shots=1024, seeds=SEEDS, max_iter=MAX_ITER_P5
    )
    all_results["p5_cobyla_1024sh"] = {
        "p": 5, "optimizer": "COBYLA", "shots": 1024,
        "escaped": arm_d_escaped, "rate": arm_d_rate,
        "data": arm_d_data
    }

    # ============================================================
    # COMPILE FULL RESULTS TABLE
    # ============================================================
    print("\n" + "=" * 70)
    print("FULL RESULTS TABLE (depth × shots)")
    print("=" * 70)
    print(f"{'Arm':<25} {'p':>4} {'Shots':>6} {'Escaped':>8} {'Rate':>6}  Source")
    print("-" * 70)
    print(f"{'p3_cobyla_256sh':<25} {'3':>4} {'256':>6} {'6/10':>8} {'0.60':>6}  Exp51 Phase A")
    print(f"{'p3_cobyla_1024sh':<25} {'3':>4} {'1024':>6} {'9/10':>8} {'0.90':>6}  Exp51 Phase C")
    print(f"{'p5_cobyla_256sh (NEW)':<25} {'5':>4} {'256':>6} {f'{arm_c_escaped}/10':>8} {arm_c_rate:.2f}  Exp53 Arm C")
    print(f"{'p5_cobyla_1024sh (NEW)':<25} {'5':>4} {'1024':>6} {f'{arm_d_escaped}/10':>8} {arm_d_rate:.2f}  Exp53 Arm D")

    # Evaluate hypotheses
    verdicts = evaluate_hypotheses(
        p3_256=0.60, p3_1024=0.90,
        p5_256_rate=arm_c_rate, p5_1024_rate=arm_d_rate
    )

    # ============================================================
    # SAVE RESULTS
    # ============================================================
    output = {
        "experiment": "Exp53",
        "title": "Depth vs Shots Tradeoff",
        "author": "Elder C5846",
        "date": "2026-06-15",
        "escape_threshold": ESCAPE_THRESHOLD,
        "seeds": SEEDS,
        "reused_from_exp51": EXP51_REUSED,
        "new_results": all_results,
        "hypothesis_verdicts": verdicts
    }

    out_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "experiments", "exp53_results.json"
    )
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n✓ Results saved to: {out_path}")

    # Summary verdict
    confirmed = sum(1 for v in verdicts.values() if v == "CONFIRMED" and isinstance(v, str))
    total_h = sum(1 for k in verdicts if k.startswith("H"))
    print(f"\n{'='*70}")
    print(f"SUMMARY: {confirmed}/{total_h} hypotheses CONFIRMED")
    print(f"H1: {verdicts['H1']} | H2: {verdicts['H2']} | H3: {verdicts['H3']}")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
