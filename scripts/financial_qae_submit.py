#!/usr/bin/env python3
"""
Financial QAE — IAE-MLE on Market Amplitude
Experiment 10: Whisper C3690, 2026-05-28

Submits IAE circuits encoding IWM market-direction amplitude to ibm_marrakesh.
Pre-registration: /droid/repos/quantum/experiments/10-financial-qae-iae-mle-preregistration.md

Usage:
    python3 financial_qae_submit.py --submit      # Submit to real hardware
    python3 financial_qae_submit.py --simulate    # Simulator test
    python3 financial_qae_submit.py --grade       # Grade from job IDs in results JSON
"""

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import minimize_scalar

# --- Core parameters (pre-registered, DO NOT MODIFY before grading) ---
A_TRUE = 0.56                          # P(IWM up) from Elder pipeline (C3689)
THETA_TRUE = math.asin(math.sqrt(A_TRUE))  # 48.45°
K_VALUES = [0, 1, 2, 3, 4]
N_SHOTS = 2048
BACKEND_NAME = "ibm_marrakesh"
SEED_TRANSPILER = 42                   # Pinned per C3667 reproducibility lesson
RESULTS_FILE = Path(__file__).parent / "financial_qae_results.json"


def expected_p(k, theta=THETA_TRUE):
    """Expected P(|1>) for k Grover steps."""
    return math.sin((2*k + 1) * theta) ** 2


def ry_angle(k, theta=THETA_TRUE):
    """Ry rotation angle for k-step IAE circuit."""
    return (2*k + 1) * 2 * theta


def build_circuit(k):
    """Build IAE circuit for k Grover steps — single Ry gate."""
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(1, 1)
    qc.ry(ry_angle(k), 0)
    qc.measure(0, 0)
    return qc


def neg_log_likelihood(a, counts_per_k, n_shots):
    """Negative log-likelihood for MLE recovery."""
    if a <= 0 or a >= 1:
        return 1e10
    theta = math.asin(math.sqrt(a))
    ll = 0.0
    for k, m in counts_per_k.items():
        p = math.sin((2*k + 1) * theta) ** 2
        p = max(1e-10, min(1 - 1e-10, p))
        ll += m * math.log(p) + (n_shots - m) * math.log(1 - p)
    return -ll


def mle_estimate(counts_per_k, n_shots):
    """Maximum Likelihood Estimate of amplitude a."""
    result = minimize_scalar(
        lambda a: neg_log_likelihood(a, counts_per_k, n_shots),
        bounds=(0.01, 0.99),
        method='bounded'
    )
    return result.x


def naive_ci_width(a_naive, n):
    """Classical Wald 95% CI width for naive estimator."""
    return 2 * 1.96 * math.sqrt(a_naive * (1 - a_naive) / n)


def bootstrap_mle_ci(counts_per_k, n_shots, n_boot=1000):
    """Bootstrap 95% CI for MLE estimator."""
    estimates = []
    for _ in range(n_boot):
        boot_counts = {}
        for k, m in counts_per_k.items():
            # Resample Binomial
            boot_m = np.random.binomial(n_shots, m / n_shots)
            boot_counts[k] = boot_m
        estimates.append(mle_estimate(boot_counts, n_shots))
    lo, hi = np.percentile(estimates, [2.5, 97.5])
    return hi - lo, lo, hi


def print_preregistered_expectations():
    print("=" * 60)
    print("FINANCIAL QAE — IAE-MLE (Experiment 10)")
    print("Pre-registered at Whisper C3690, 2026-05-28")
    print("=" * 60)
    print(f"\nEncoding: a_true = {A_TRUE} (IWM up-probability)")
    print(f"theta_true = {math.degrees(THETA_TRUE):.2f}°")
    print(f"Backend: {BACKEND_NAME} | Shots per k: {N_SHOTS}")
    print()
    print("Expected P(|1>) per k-value:")
    for k in K_VALUES:
        angle_deg = math.degrees(ry_angle(k))
        print(f"  k={k}: Ry({angle_deg:.1f}°) → P(|1>) = {expected_p(k):.4f}")


def run_simulator():
    """Sanity check on Aer simulator before hardware submission."""
    from qiskit_aer import AerSimulator
    sim = AerSimulator()

    print_preregistered_expectations()
    print("\n--- SIMULATOR RUN ---")

    counts_per_k = {}
    for k in K_VALUES:
        qc = build_circuit(k)
        job = sim.run(qc, shots=N_SHOTS, seed_simulator=SEED_TRANSPILER)
        counts = job.result().get_counts()
        m = counts.get('1', 0)
        p_meas = m / N_SHOTS
        diff = abs(p_meas - expected_p(k))
        print(f"  k={k}: measured={p_meas:.4f}, expected={expected_p(k):.4f}, diff={diff:.4f}")
        counts_per_k[k] = m

    a_naive = counts_per_k[0] / N_SHOTS
    a_mle = mle_estimate(counts_per_k, N_SHOTS)
    ci_naive = naive_ci_width(a_naive, N_SHOTS)
    ci_mle_width, ci_lo, ci_hi = bootstrap_mle_ci(counts_per_k, N_SHOTS)

    print(f"\nNaive: a={a_naive:.4f}, error={abs(a_naive-A_TRUE):.4f}, CI width={ci_naive:.4f}")
    print(f"MLE:   a={a_mle:.4f}, error={abs(a_mle-A_TRUE):.4f}, CI width={ci_mle_width:.4f}")
    print(f"CI reduction: {100*(1 - ci_mle_width/ci_naive):.1f}%")
    print(f"\nH1 (precision): {'PASS' if abs(a_mle-A_TRUE) < abs(a_naive-A_TRUE) else 'FAIL'}")
    print(f"H2 (CI width ≤70% naive): {'PASS' if ci_mle_width <= 0.70*ci_naive else 'FAIL'}")
    print(f"H3 (|a_mle-0.56|≤0.05): {'PASS' if abs(a_mle-A_TRUE) <= 0.05 else 'FAIL'}")

    return a_mle, a_naive


def run_hardware():
    """Submit IAE circuits to ibm_marrakesh real hardware."""
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
    from qiskit import transpile

    print_preregistered_expectations()
    print(f"\n--- HARDWARE SUBMISSION: {BACKEND_NAME} ---")

    svc = QiskitRuntimeService()
    backend = svc.backend(BACKEND_NAME)
    status = backend.status()
    print(f"Backend status: {status.status_msg}")
    print(f"Pending jobs: {status.pending_jobs}")

    # Pre-submit guard (Whisper C3692): submitting to a non-operational backend
    # (e.g. maintenance) hangs the runtime call instead of failing fast — root cause
    # of the C3690/C3691 repeated 520/timeout retries. Check the cheap status flag
    # before the expensive submission so retries abort in seconds, not minutes.
    if not status.operational:
        print(f"\n⚠️  ABORT: {BACKEND_NAME} is not operational (status: {status.status_msg}).")
        print("Hardware submission skipped. Retry --submit once the backend recovers,")
        print("or run --simulate to validate the pipeline meanwhile.")
        return {}

    job_ids = {}
    submitted = {}

    for k in K_VALUES:
        qc = build_circuit(k)
        # Transpile with pinned seed for reproducibility (C3667 lesson)
        qc_t = transpile(qc, backend, optimization_level=1,
                         seed_transpiler=SEED_TRANSPILER)
        print(f"\n  k={k}: depth={qc_t.depth()}, gates={qc_t.count_ops()}")

        with Sampler(backend) as sampler:
            job = sampler.run([qc_t], shots=N_SHOTS)
            job_id = job.job_id()
            job_ids[k] = job_id
            print(f"  Submitted job ID: {job_id}")
            submitted[k] = job_id

    results = {
        "experiment": "10-financial-qae-iae-mle",
        "cycle": "C3690",
        "timestamp": __import__("datetime").datetime.utcnow().isoformat() + "Z",
        "backend": BACKEND_NAME,
        "a_true": A_TRUE,
        "k_values": K_VALUES,
        "n_shots": N_SHOTS,
        "job_ids": {str(k): v for k, v in job_ids.items()},
        "status": "submitted"
    }

    RESULTS_FILE.write_text(json.dumps(results, indent=2))
    print(f"\nJob IDs saved to: {RESULTS_FILE}")
    print("\n⚠️  Jobs submitted. Retrieve with --grade after completion (~5-30 min).")
    return job_ids


def grade_results():
    """Grade experiment from saved job IDs."""
    if not RESULTS_FILE.exists():
        print(f"ERROR: No results file at {RESULTS_FILE}")
        print("Run --submit first.")
        return

    results = json.loads(RESULTS_FILE.read_text())
    job_ids = results["job_ids"]

    if results.get("status") == "submitted":
        from qiskit_ibm_runtime import QiskitRuntimeService
        svc = QiskitRuntimeService()

        print("Retrieving job results...")
        counts_per_k = {}
        for k_str, job_id in job_ids.items():
            k = int(k_str)
            job = svc.job(job_id)
            status = job.status()
            print(f"  k={k}: job {job_id[:20]}... status={status}")
            if str(status) in ('JobStatus.DONE', 'DONE', 'job has successfully run'):
                job_result = job.result()
                # SamplerV2 result format
                pub_result = job_result[0]
                bit_array = pub_result.data.c
                counts = bit_array.get_counts()
                m = counts.get('1', 0)
            else:
                print(f"    ⚠️  Job not complete yet. Try again later.")
                return
            counts_per_k[k] = m

        a_naive = counts_per_k[0] / N_SHOTS
        a_mle = mle_estimate(counts_per_k, N_SHOTS)
        ci_naive = naive_ci_width(a_naive, N_SHOTS)
        ci_mle_width, ci_lo, ci_hi = bootstrap_mle_ci(counts_per_k, N_SHOTS)

        print("\n" + "=" * 60)
        print("GRADING RESULTS")
        print("=" * 60)
        print(f"\nTrue amplitude: a_true = {A_TRUE}")
        print(f"\nPer k-value measurements:")
        for k in K_VALUES:
            m = counts_per_k[k]
            p_meas = m / N_SHOTS
            diff = abs(p_meas - expected_p(k))
            status = "✓" if diff < 0.08 else "✗"
            print(f"  k={k}: P(|1>)={p_meas:.4f} (expected {expected_p(k):.4f}) diff={diff:.4f} {status}")

        print(f"\nNaive: a={a_naive:.4f}, error={abs(a_naive-A_TRUE):.4f}, 95%CI width={ci_naive:.4f}")
        print(f"MLE:   a={a_mle:.4f}, error={abs(a_mle-A_TRUE):.4f}, 95%CI width={ci_mle_width:.4f} [{ci_lo:.4f},{ci_hi:.4f}]")
        ci_reduction = 1 - ci_mle_width / ci_naive
        print(f"CI reduction vs naive: {100*ci_reduction:.1f}%")

        h1 = abs(a_mle - A_TRUE) < abs(a_naive - A_TRUE)
        h2 = ci_mle_width <= 0.70 * ci_naive
        h3 = abs(a_mle - A_TRUE) <= 0.05
        h4_pass = sum(1 for k in K_VALUES if abs(counts_per_k[k]/N_SHOTS - expected_p(k)) < 0.08)

        print(f"\n{'='*40}")
        print(f"H1 (precision advantage): {'PASS ✅' if h1 else 'FAIL ❌'}")
        print(f"H2 (CI ≤70% naive):       {'PASS ✅' if h2 else 'FAIL ❌'} ({100*ci_reduction:.1f}% reduction)")
        print(f"H3 (converge ±0.05):      {'PASS ✅' if h3 else 'FAIL ❌'}")
        print(f"H4 (k-monotonicity):      {h4_pass}/{len(K_VALUES)} circuits within ±0.08 tolerance")

        # Save graded results
        results.update({
            "status": "graded",
            "counts_per_k": {str(k): v for k, v in counts_per_k.items()},
            "a_naive": a_naive,
            "a_mle": a_mle,
            "ci_naive": ci_naive,
            "ci_mle": ci_mle_width,
            "ci_reduction_pct": 100 * ci_reduction,
            "H1": h1, "H2": h2, "H3": h3, "H4_circuits_pass": h4_pass,
        })
        RESULTS_FILE.write_text(json.dumps(results, indent=2))
        print(f"\nResults saved to {RESULTS_FILE}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Financial QAE — IAE-MLE on ibm_marrakesh")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--simulate", action="store_true", help="Run on Aer simulator")
    group.add_argument("--submit", action="store_true", help="Submit to ibm_marrakesh")
    group.add_argument("--grade", action="store_true", help="Grade submitted jobs")
    args = parser.parse_args()

    if args.simulate:
        run_simulator()
    elif args.submit:
        run_hardware()
    elif args.grade:
        grade_results()
