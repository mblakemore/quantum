#!/usr/bin/env python3
"""
Experiment 10: Financial QAE — IAE-MLE on Market Amplitude
Ember C3401 execution of Whisper C3690 pre-registration

Pre-registration: /droid/repos/quantum/experiments/10-financial-qae-iae-mle-preregistration.md

Tests: Does IAE-MLE precision advantage (344x in Exp 9) survive NISQ noise
when applied to a financial amplitude oracle (P(IWM up) = 0.56)?

H1: MLE error < Naive error (precision advantage)
H2: MLE 95% CI width ≤ 70% of naive CI width
H3: |a_mle - a_true| ≤ 0.05
H4: k-value raw measurements within ±0.08 of expected (exploratory)
"""

import argparse
import json
import math
import sys
import time
from datetime import datetime, timezone

import numpy as np
from scipy import optimize

try:
    from qiskit import QuantumCircuit, transpile
    from qiskit_aer import AerSimulator
except ImportError as e:
    print(f"ERROR: {e}")
    sys.exit(1)

# ============================================================================
# Constants
# ============================================================================

A_TRUE = 0.56  # P(IWM direction "up"), Elder calibrated estimate
THETA = math.asin(math.sqrt(A_TRUE))  # arcsin(sqrt(0.56)) ≈ 0.8481 rad
K_VALUES = [0, 1, 2, 3, 4]
SHOTS = 2048
NISQ_TOLERANCE = 0.08  # H4 tolerance (±8pp from Finding 7 ±7pp drift)

# Expected P(|1>) for each k per pre-registration
EXPECTED_P = {k: math.sin((2*k + 1) * THETA)**2 for k in K_VALUES}


# ============================================================================
# Circuit Construction
# ============================================================================

def build_iae_circuit(k: int) -> QuantumCircuit:
    """Build k-th IAE circuit: Ry(2*(2k+1)*theta)|0>.

    Connection to Finding 3 (X-basis immunity): Ry rotation naturally
    places state in the X-basis measurement regime, leveraging structural
    noise immunity from the characterization campaign.
    """
    angle = 2 * (2*k + 1) * THETA
    qc = QuantumCircuit(1, 1)
    qc.ry(angle, 0)
    qc.measure(0, 0)
    return qc


# ============================================================================
# MLE Recovery
# ============================================================================

def mle_recovery(counts_data: list) -> float:
    """
    MLE estimate of amplitude a from IAE counts.

    Args:
        counts_data: list of (k, m_ones, n_total) tuples

    Returns:
        MLE estimate a_mle ∈ (0, 1)
    """
    def neg_log_likelihood(a):
        if a <= 1e-6 or a >= 1 - 1e-6:
            return 1e12
        ll = 0.0
        for k, m, n in counts_data:
            sin_arg = (2*k + 1) * math.asin(math.sqrt(a))
            p = math.sin(sin_arg)**2
            p = max(1e-10, min(1 - 1e-10, p))
            ll += m * math.log(p) + (n - m) * math.log(1 - p)
        return -ll

    result = optimize.minimize_scalar(neg_log_likelihood, bounds=(0.001, 0.999), method='bounded')
    return result.x


def bootstrap_ci(counts_data: list, n_bootstrap: int = 5000, alpha: float = 0.05) -> tuple:
    """Bootstrap 95% CI for MLE estimate."""
    estimates = []
    for _ in range(n_bootstrap):
        resampled = []
        for k, m, n in counts_data:
            m_boot = np.random.binomial(n, m / n)
            resampled.append((k, m_boot, n))
        try:
            est = mle_recovery(resampled)
            estimates.append(est)
        except Exception:
            pass
    estimates = sorted(estimates)
    lo = np.percentile(estimates, 100 * alpha / 2)
    hi = np.percentile(estimates, 100 * (1 - alpha / 2))
    return lo, hi, hi - lo


# ============================================================================
# Main Execution
# ============================================================================

def run_simulator():
    """Run IAE circuits on AerSimulator."""
    print("\n=== SIMULATOR RUN (AerSimulator) ===")
    backend = AerSimulator()
    results = {}

    for k in K_VALUES:
        qc = build_iae_circuit(k)
        transpiled = transpile(qc, backend, seed_transpiler=42)
        job = backend.run(transpiled, shots=SHOTS)
        counts = job.result().get_counts()
        m_ones = counts.get('1', 0)
        m_zeros = counts.get('0', 0)
        measured_p = m_ones / SHOTS
        expected = EXPECTED_P[k]
        results[k] = {'ones': m_ones, 'zeros': m_zeros, 'measured_p': measured_p,
                      'expected_p': expected, 'delta': measured_p - expected}
        print(f"  k={k}: measured={measured_p:.4f}  expected={expected:.4f}  delta={measured_p - expected:+.4f}")

    return results


def run_hardware():
    """Submit IAE circuits to ibm_marrakesh."""
    try:
        from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
    except ImportError:
        from qiskit_ibm_runtime import QiskitRuntimeService, Sampler

    print("\n=== HARDWARE SUBMISSION (ibm_marrakesh) ===")
    svc = QiskitRuntimeService(channel='ibm_quantum_platform')
    backend = svc.backend('ibm_marrakesh')
    print(f"Backend: {backend.name}")
    print(f"Status: {backend.status()}")

    job_ids = {}
    results = {}

    print(f"\nSubmitting {len(K_VALUES)} circuits (2048 shots each)...")
    for k in K_VALUES:
        qc = build_iae_circuit(k)
        transpiled = transpile(qc, backend, seed_transpiler=42)

        try:
            with Sampler(mode=backend) as sampler:
                job = sampler.run([transpiled], shots=SHOTS)
                job_ids[k] = job.job_id()
                print(f"  k={k}: submitted job_id={job.job_id()}")
        except Exception as e:
            print(f"  k={k}: SamplerV2 failed ({e}), trying legacy Sampler...")
            try:
                from qiskit_ibm_runtime import Sampler as LegacySampler
                with LegacySampler(session=None, backend=backend) as sampler:
                    job = sampler.run([transpiled], shots=SHOTS)
                    job_ids[k] = job.job_id()
                    print(f"  k={k}: submitted (legacy) job_id={job.job_id()}")
            except Exception as e2:
                print(f"  k={k}: FAILED: {e2}")
                job_ids[k] = None

    print("\nWaiting for jobs to complete...")
    for k in K_VALUES:
        jid = job_ids.get(k)
        if jid is None:
            continue
        job = svc.job(jid)
        print(f"  Polling k={k} (job {jid})...", end='', flush=True)
        while True:
            status = job.status()
            if status.name in ('DONE', 'ERROR', 'CANCELLED'):
                print(f" {status.name}")
                break
            print('.', end='', flush=True)
            time.sleep(5)

        if status.name == 'DONE':
            result = job.result()
            try:
                # SamplerV2 result format
                pub_result = result[0]
                counts_array = pub_result.data.c.get_counts()
            except Exception:
                # Legacy format
                counts_array = result.get_counts()

            m_ones = counts_array.get('1', 0)
            m_zeros = counts_array.get('0', 0)
            measured_p = m_ones / SHOTS
            expected = EXPECTED_P[k]
            results[k] = {
                'ones': m_ones, 'zeros': m_zeros,
                'measured_p': measured_p, 'expected_p': expected,
                'delta': measured_p - expected, 'job_id': jid
            }
            print(f"    k={k}: measured={measured_p:.4f}  expected={expected:.4f}  delta={measured_p - expected:+.4f}")

    return results, job_ids


def analyze(results: dict, source: str = "simulator") -> dict:
    """Run H1-H4 hypothesis tests."""
    if not results:
        print("No results to analyze.")
        return {}

    counts_data = [(k, results[k]['ones'], SHOTS) for k in sorted(results.keys())]

    # Naive estimate: k=0 only
    k0 = results[0]
    a_naive = k0['ones'] / SHOTS
    naive_error = abs(a_naive - A_TRUE)
    naive_ci_lo = a_naive - 1.96 * math.sqrt(a_naive * (1 - a_naive) / SHOTS)
    naive_ci_hi = a_naive + 1.96 * math.sqrt(a_naive * (1 - a_naive) / SHOTS)
    naive_ci_width = naive_ci_hi - naive_ci_lo

    # MLE estimate
    a_mle = mle_recovery(counts_data)
    mle_error = abs(a_mle - A_TRUE)

    # Bootstrap CI for MLE
    print("\nBootstrapping MLE 95% CI (5000 samples)...")
    mle_ci_lo, mle_ci_hi, mle_ci_width = bootstrap_ci(counts_data)

    print(f"\n=== ANALYSIS ({source.upper()}) ===")
    print(f"  True amplitude (a_true): {A_TRUE:.4f}")
    print(f"  Naive estimate  (k=0):   {a_naive:.4f}  (error={naive_error:.4f}, 95%CI=[{naive_ci_lo:.4f},{naive_ci_hi:.4f}] width={naive_ci_width:.4f})")
    print(f"  MLE estimate    (k=0..4): {a_mle:.4f}  (error={mle_error:.4f}, 95%CI=[{mle_ci_lo:.4f},{mle_ci_hi:.4f}] width={mle_ci_width:.4f})")

    h1 = mle_error < naive_error
    ci_ratio = mle_ci_width / naive_ci_width
    h2 = ci_ratio <= 0.70
    h3 = mle_error <= 0.05
    h4_details = {}
    h4_pass_count = 0
    for k in sorted(results.keys()):
        delta = abs(results[k]['delta'])
        passed = delta <= NISQ_TOLERANCE
        h4_details[k] = {'delta': results[k]['delta'], 'passed': passed}
        if passed:
            h4_pass_count += 1
    h4 = h4_pass_count >= 4  # Allow 1 failure

    print(f"\n  H1 (MLE error < Naive error):     {'PASS ✓' if h1 else 'FAIL ✗'}  ({mle_error:.4f} vs {naive_error:.4f})")
    print(f"  H2 (CI width ≤ 70% of naive):     {'PASS ✓' if h2 else 'FAIL ✗'}  (ratio={ci_ratio:.3f})")
    print(f"  H3 (|a_mle - 0.56| ≤ 0.05):       {'PASS ✓' if h3 else 'FAIL ✗'}  (error={mle_error:.4f})")
    print(f"  H4 (k-monotonicity, ±0.08, 4/5):  {'PASS ✓' if h4 else 'FAIL ✗'}  ({h4_pass_count}/5 within tolerance)")

    return {
        'source': source,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'a_true': A_TRUE,
        'a_naive': float(a_naive),
        'a_mle': float(a_mle),
        'naive_error': float(naive_error),
        'mle_error': float(mle_error),
        'naive_ci': [float(naive_ci_lo), float(naive_ci_hi), float(naive_ci_width)],
        'mle_ci': [float(mle_ci_lo), float(mle_ci_hi), float(mle_ci_width)],
        'ci_ratio': float(ci_ratio),
        'hypotheses': {'H1': h1, 'H2': h2, 'H3': h3, 'H4': h4},
        'h4_details': {str(k): v for k, v in h4_details.items()},
        'k_results': {str(k): results[k] for k in sorted(results.keys())},
    }


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Financial QAE Experiment 10')
    parser.add_argument('--test', action='store_true', help='Run on simulator only')
    parser.add_argument('--hardware', action='store_true', help='Submit to ibm_marrakesh')
    parser.add_argument('--output', default=None, help='JSON output file')
    args = parser.parse_args()

    print("=" * 70)
    print("EXPERIMENT 10: Financial QAE — IAE-MLE on Market Amplitude")
    print(f"Ember C3401 | Whisper C3690 pre-registration")
    print(f"a_true = {A_TRUE}, theta = {THETA:.6f} rad ({math.degrees(THETA):.4f}°)")
    print("=" * 70)

    print("\nExpected P(|1>) per k-value:")
    for k in K_VALUES:
        print(f"  k={k}: {EXPECTED_P[k]:.4f}  (Ry angle = {math.degrees(2*(2*k+1)*THETA):.2f}°)")

    all_results = {}

    if args.test or not args.hardware:
        sim_results = run_simulator()
        analysis = analyze(sim_results, source='simulator')
        all_results['simulator'] = analysis

    if args.hardware:
        hw_results, job_ids = run_hardware()
        if hw_results:
            analysis = analyze(hw_results, source='hardware')
            analysis['job_ids'] = {str(k): v for k, v in job_ids.items()}
            all_results['hardware'] = analysis

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(all_results, f, indent=2, default=str)
        print(f"\nResults saved to: {args.output}")

    # Summary
    print("\n" + "=" * 70)
    print("EXPERIMENT 10 SUMMARY")
    for src, data in all_results.items():
        h = data.get('hypotheses', {})
        passed = sum(1 for v in h.values() if v)
        print(f"  {src.upper()}: {passed}/4 hypotheses passed")
        print(f"    a_naive={data.get('a_naive', 'N/A'):.4f}  a_mle={data.get('a_mle', 'N/A'):.4f}  a_true={A_TRUE}")
    print("=" * 70)
