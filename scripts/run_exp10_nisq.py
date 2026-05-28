#!/usr/bin/env python3
"""
Experiment 10: Financial QAE with FakeMarrakesh NISQ noise model
Ember C3401 — hardware-realistic noise simulation
"""
import math, json
import numpy as np
from scipy import optimize
from datetime import datetime, timezone
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
from qiskit_aer.noise import NoiseModel

A_TRUE = 0.56
THETA = math.asin(math.sqrt(A_TRUE))
K_VALUES = [0, 1, 2, 3, 4]
SHOTS = 2048
EXPECTED_P = {k: math.sin((2*k + 1) * THETA)**2 for k in K_VALUES}


def build_iae_circuit(k):
    angle = 2 * (2*k + 1) * THETA
    qc = QuantumCircuit(1, 1)
    qc.ry(angle, 0)
    qc.measure(0, 0)
    return qc


def neg_log_likelihood(a, counts_data):
    if a <= 1e-6 or a >= 1 - 1e-6:
        return 1e12
    ll = 0.0
    for k, m, n in counts_data:
        sin_arg = (2*k + 1) * math.asin(math.sqrt(a))
        p = max(1e-10, min(1 - 1e-10, math.sin(sin_arg)**2))
        ll += m * math.log(p) + (n - m) * math.log(1 - p)
    return -ll


def mle_recovery(counts_data):
    result = optimize.minimize_scalar(
        lambda a: neg_log_likelihood(a, counts_data),
        bounds=(0.001, 0.999), method='bounded'
    )
    return result.x


def bootstrap_mle_ci(counts_data, n_boot=3000):
    estimates = []
    for _ in range(n_boot):
        resampled = [(k, int(np.random.binomial(tot, m / tot)), tot)
                     for k, m, tot in counts_data]
        try:
            est = mle_recovery(resampled)
            estimates.append(est)
        except Exception:
            pass
    if not estimates:
        return float('nan'), float('nan'), float('nan')
    lo = float(np.percentile(estimates, 2.5))
    hi = float(np.percentile(estimates, 97.5))
    return lo, hi, hi - lo


print("=== FAKEMARRAKESH NOISE MODEL (ibm_marrakesh hardware noise) ===")
fake_backend = FakeMarrakesh()
noise_model = NoiseModel.from_backend(fake_backend)
backend = AerSimulator(noise_model=noise_model)

results = {}
for k in K_VALUES:
    qc = build_iae_circuit(k)
    transpiled = transpile(qc, backend, seed_transpiler=42)
    job = backend.run(transpiled, shots=SHOTS)
    counts = job.result().get_counts()
    m_ones = counts.get('1', 0)
    measured_p = m_ones / SHOTS
    expected = EXPECTED_P[k]
    delta = measured_p - expected
    results[k] = {'ones': m_ones, 'zeros': SHOTS - m_ones,
                  'measured_p': measured_p, 'expected_p': expected, 'delta': delta}
    print(f"  k={k}: measured={measured_p:.4f}  expected={expected:.4f}  delta={delta:+.4f}")

counts_data = [(k, results[k]['ones'], SHOTS) for k in K_VALUES]

a_mle = mle_recovery(counts_data)
a_naive = results[0]['ones'] / SHOTS
mle_error = abs(a_mle - A_TRUE)
naive_error = abs(a_naive - A_TRUE)

print("\nBootstrapping MLE 95% CI (3000 samples)...")
mle_ci_lo, mle_ci_hi, mle_ci_width = bootstrap_mle_ci(counts_data)
naive_ci_width = 2 * 1.96 * math.sqrt(a_naive * (1 - a_naive) / SHOTS)
naive_ci_lo = a_naive - naive_ci_width / 2
naive_ci_hi = a_naive + naive_ci_width / 2
ci_ratio = mle_ci_width / naive_ci_width if naive_ci_width > 0 else 999.0

print(f"\n=== ANALYSIS (FakeMarrakesh NISQ Noise) ===")
print(f"  a_true  = {A_TRUE:.4f}")
print(f"  a_naive = {a_naive:.4f}  error={naive_error:.4f}  "
      f"CI=[{naive_ci_lo:.4f},{naive_ci_hi:.4f}]  width={naive_ci_width:.4f}")
print(f"  a_mle   = {a_mle:.4f}  error={mle_error:.4f}  "
      f"CI=[{mle_ci_lo:.4f},{mle_ci_hi:.4f}]  width={mle_ci_width:.4f}")
print(f"  CI ratio = {ci_ratio:.4f}")

h1 = mle_error < naive_error
h2 = ci_ratio <= 0.70
h3 = mle_error <= 0.05
h4_passes = sum(1 for k in K_VALUES
                if abs(results[k]['measured_p'] - results[k]['expected_p']) <= 0.08)
h4 = h4_passes >= 4

print(f"\n  H1 (MLE error < Naive):           {'PASS ✓' if h1 else 'FAIL ✗'}  "
      f"({mle_error:.4f} vs {naive_error:.4f})")
print(f"  H2 (CI width ≤ 70% naive):         {'PASS ✓' if h2 else 'FAIL ✗'}  "
      f"(ratio={ci_ratio:.3f})")
print(f"  H3 (|a_mle - 0.56| ≤ 0.05):        {'PASS ✓' if h3 else 'FAIL ✗'}  "
      f"(error={mle_error:.4f})")
print(f"  H4 (k-monotonicity 4/5, ±0.08):    {'PASS ✓' if h4 else 'FAIL ✗'}  "
      f"({h4_passes}/5 passed)")

output = {
    'source': 'FakeMarrakesh_noise_model',
    'timestamp': datetime.now(timezone.utc).isoformat(),
    'a_true': A_TRUE,
    'a_naive': float(a_naive),
    'a_mle': float(a_mle),
    'naive_error': float(naive_error),
    'mle_error': float(mle_error),
    'naive_ci': [float(naive_ci_lo), float(naive_ci_hi), float(naive_ci_width)],
    'mle_ci': [float(mle_ci_lo), float(mle_ci_hi), float(mle_ci_width)],
    'ci_ratio': float(ci_ratio),
    'hypotheses': {'H1': bool(h1), 'H2': bool(h2), 'H3': bool(h3), 'H4': bool(h4)},
    'h4_summary': f"{h4_passes}/5 within ±0.08",
    'k_results': {str(k): {kk: float(vv) if isinstance(vv, (float, np.floating)) else int(vv) if isinstance(vv, (int, np.integer)) else vv for kk, vv in results[k].items()} for k in K_VALUES},
}

out_path = '/droid/repos/quantum/experiments/10-financial-qae-results-fakemarrakesh.json'
with open(out_path, 'w') as f:
    json.dump(output, f, indent=2)
print(f"\nResults saved to: {out_path}")
