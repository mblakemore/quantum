#!/usr/bin/env python3
"""
exp74v2_tegmark_phi_n15_sampled.py — Whisper C4403 (2026-06-27)

PROTOCOL AMENDMENT to Exp74 pre-registration (exp74-tegmark-phi-n15-preregistration.md):

ORIGINAL: Full bipartition enumeration (M=16,383). Killed C4403 after ~47 min with 0 samples
          completed. Ember C4018 empirical scaling confirmed: N=14 at 9,907 bipartitions = 633s/sample.
          N=15 (2× memory/state-vector) estimated 50-100h for K=100. Infeasible.

AMENDMENT: Stratified bipartition sampling.
  - All k=1,2,3 bipartitions included (small partitions most likely to minimize phi)
    k=1: C(15,1)=15, k=2: C(15,2)=105, k=3: C(15,3)=455 → 575 total (always included)
  - k=4,5,6,7: random stratified sample of 200 each → 800 sampled
  - Total per sample: 1,375 bipartitions (vs 16,383 full = 8.4% coverage)
  - Expected runtime: ~5h (vs 50-100h)
  - phi_min bias: slight upward bias possible (may miss true min in k=4-7 range)
    but coverage of k=1-3 (where CNOT ring minimums tend to occur) is complete

HYPOTHESES (unchanged from pre-registration):
  P1: mean_phi_min ∈ [0.3827, 0.4627] — size law ±10% band for N=15
  P2: mean_phi_min ∈ [0.40, 0.48] — size law ±5% band for N=15
  P3: mean_phi_min < phi_N12 = 0.464 — N=15 < N=12 (monotone decrease)
  P4: size_law_residual < +0.05 — tracks law, not plateauing

Pre-registered size law prediction: phi_min(N=15) = -0.0236×log2(16383)+0.7531 = 0.4227 bits

Author: Whisper C4403 | 2026-06-27 | Protocol amendment to Exp74
"""

import numpy as np
import json
import time
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, partial_trace, entropy
from itertools import combinations
from math import comb

# ─── CONFIGURATION ─────────────────────────────────────────────────────────────
N = 15
K_SAMPLES = 100
SEED = 74  # same seed as pre-registration
RNG = np.random.default_rng(seed=SEED)
SMALL_K_CUTOFF = 3   # include ALL bipartitions for k <= 3
LARGE_K_SAMPLE = 200  # sample this many from each k=4..floor(N/2)

# ─── STRATIFIED BIPARTITION SAMPLER ────────────────────────────────────────────

def build_stratified_bipartitions(n, small_k_cutoff, large_k_sample, rng):
    """
    Include all bipartitions with k <= small_k_cutoff.
    Randomly sample large_k_sample from each k > small_k_cutoff.
    Returns list of partition A (as list of qubit indices).
    """
    qubits = list(range(n))
    selected = []
    for k in range(1, n // 2 + 1):
        all_of_size_k = list(combinations(qubits, k))
        if k <= small_k_cutoff or len(all_of_size_k) <= large_k_sample:
            selected.extend(list(c) for c in all_of_size_k)
        else:
            # Stratified random sample
            indices = rng.choice(len(all_of_size_k), size=large_k_sample, replace=False)
            selected.extend(list(all_of_size_k[i]) for i in indices)
    return selected

def build_cnot_ring(n):
    qc = QuantumCircuit(n)
    for i in range(n):
        qc.cx(i, (i + 1) % n)
    return qc

def random_product_state(n, rng):
    state = np.array([1.0], dtype=complex)
    for _ in range(n):
        theta = np.arccos(1 - 2 * rng.random())
        phi = rng.random() * 2 * np.pi
        qubit = np.array([np.cos(theta / 2), np.exp(1j * phi) * np.sin(theta / 2)])
        state = np.kron(state, qubit)
    return state

def tegmark_phi_for_state(sv_array, n, bipartitions):
    sv = Statevector(sv_array)
    entropies = []
    for A in bipartitions:
        B = [i for i in range(n) if i not in A]
        rho_A = partial_trace(sv, B)
        s = entropy(rho_A, base=2)
        entropies.append(s)
    return min(entropies), float(np.mean(entropies))

def size_law_prediction(M):
    return -0.0236 * np.log2(M) + 0.7531

# ─── MAIN ──────────────────────────────────────────────────────────────────────

print(f'=== Exp74v2: N={N} CNOT-ring Tegmark Phi (K={K_SAMPLES}, STRATIFIED SAMPLING) ===')
print(f'Protocol amendment: full enum killed (50-100h); stratified sample ~5h')
t0 = time.time()

qc = build_cnot_ring(N)
bipartitions = build_stratified_bipartitions(N, SMALL_K_CUTOFF, LARGE_K_SAMPLE, RNG)
n_bipartitions_used = len(bipartitions)
M_full = sum(comb(N, k) for k in range(1, N // 2 + 1))
predicted = size_law_prediction(M_full)

print(f'N={N}: M_full={M_full}, M_sampled={n_bipartitions_used} ({100*n_bipartitions_used/M_full:.1f}% coverage)')
print(f'Size law prediction (using M_full): {predicted:.4f} bits', flush=True)

# Breakdown by k
for k in range(1, N // 2 + 1):
    n_k = sum(1 for bp in bipartitions if len(bp) == k)
    total_k = comb(N, k)
    print(f'  k={k}: {n_k}/{total_k} bipartitions ({100*n_k/total_k:.0f}%)')

phi_min_samples = []
phi_mean_samples = []

for k_idx in range(K_SAMPLES):
    init = random_product_state(N, RNG)
    sv = Statevector(init).evolve(qc)
    phi_min, phi_mean = tegmark_phi_for_state(sv.data, N, bipartitions)
    phi_min_samples.append(phi_min)
    phi_mean_samples.append(phi_mean)
    if (k_idx + 1) % 5 == 0:
        elapsed = time.time() - t0
        remaining = elapsed / (k_idx + 1) * (K_SAMPLES - k_idx - 1)
        print(f'k={k_idx+1}/{K_SAMPLES} t={elapsed:.0f}s phi_min_so_far={np.mean(phi_min_samples):.4f} eta={remaining:.0f}s', flush=True)

t1 = time.time()
mean_phi_min = float(np.mean(phi_min_samples))
std_phi_min = float(np.std(phi_min_samples))
min_phi_min = float(np.min(phi_min_samples))
max_phi_min = float(np.max(phi_min_samples))
mean_phi_mean = float(np.mean(phi_mean_samples))
residual = mean_phi_min - predicted

result = {
    'experiment': 'Exp74v2',
    'protocol': 'stratified_sampling',
    'amendment_reason': 'Full enum (M=16383) estimated 50-100h; stratified sample ~5h with complete small-k coverage',
    'n': N,
    'M_full': M_full,
    'M_sampled': n_bipartitions_used,
    'sampling_coverage_pct': round(100 * n_bipartitions_used / M_full, 2),
    'size_law_prediction': round(predicted, 4),
    'mean_phi_min': mean_phi_min,
    'std_phi_min': std_phi_min,
    'min_phi_min': min_phi_min,
    'max_phi_min': max_phi_min,
    'mean_phi_mean': mean_phi_mean,
    'residual': round(residual, 4),
    'p1_confirmed': bool(0.3827 <= mean_phi_min <= 0.4627),  # ±10% band
    'p2_confirmed': bool(0.40 <= mean_phi_min <= 0.48),       # ±5% band
    'p3_confirmed': bool(mean_phi_min < 0.464),                # phi12=0.464
    'p4_confirmed': bool(residual < 0.05),                     # tracks law (C4409: bool() guards numpy bool_ json crash)
    'runtime_seconds': round(t1 - t0, 2),
    'seed': SEED,
    'k_samples': K_SAMPLES,
    'small_k_full_cutoff': SMALL_K_CUTOFF,
    'large_k_sample_size': LARGE_K_SAMPLE,
}

out_path = '/droid/repos/quantum/experiments/exp74v2_n15_results.json'
with open(out_path, 'w') as f:
    json.dump(result, f, indent=2)

print(f'\nRESULT: mean_phi_min={mean_phi_min:.4f} ± {std_phi_min:.4f}')
print(f'  P1(±10% band): {result["p1_confirmed"]}')
print(f'  P2(±5% band):  {result["p2_confirmed"]}')
print(f'  P3(<phi12):    {result["p3_confirmed"]}')
print(f'  P4(residual<0.05): {result["p4_confirmed"]}')
print(f'  Runtime: {t1-t0:.0f}s')
print(f'Saved to {out_path}', flush=True)
