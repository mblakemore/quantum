#!/usr/bin/env python3
"""
Exp74: Tegmark Quantum Phi N-Scaling Extension to N=15
Tests whether log-linear size law continues or a quantum floor emerges.

Whisper (DC15W) C4402 2026-06-27
Methodology identical to Exp72 for direct comparability.
Pre-registered BLIND to Exp72 N=14 results (still running as of registration).
"""
import numpy as np
import json
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, partial_trace, entropy
from itertools import combinations
import time

RNG = np.random.default_rng(seed=74)
N = 15
K_SAMPLES = 100

# Size law from Exp71 (R²~0.97, N=3..12, extended through N=13 Exp72)
SIZE_LAW_SLOPE = -0.0236
SIZE_LAW_INTERCEPT = 0.7531

# Historical data for final comparison
HISTORICAL = {
    3: 0.700, 4: 0.699, 5: 0.651, 6: 0.633, 7: 0.609,
    8: 0.579, 9: 0.562, 10: 0.534, 11: 0.543, 12: 0.464,
    13: 0.4533  # Exp72 C4017
}


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


def all_bipartitions(n):
    qubits = list(range(n))
    parts = []
    for size in range(1, n // 2 + 1):
        for combo in combinations(qubits, size):
            parts.append(list(combo))
    return parts


def tegmark_phi_for_state(sv_array, n, bipartitions):
    sv = Statevector(sv_array)
    entropies = []
    for A in bipartitions:
        B = [i for i in range(n) if i not in A]
        rho_A = partial_trace(sv, B)
        s = entropy(rho_A, base=2)
        entropies.append(s)
    if not entropies:
        return 0.0, 0.0
    return min(entropies), float(np.mean(entropies))


def size_law_prediction(m_bipartitions):
    return SIZE_LAW_SLOPE * np.log2(m_bipartitions) + SIZE_LAW_INTERCEPT


def divisor_note(n):
    def is_prime(x):
        if x < 2: return False
        for i in range(2, int(x**0.5)+1):
            if x % i == 0: return False
        return True
    if is_prime(n):
        return "prime"
    if (n & (n-1)) == 0:
        return f"2^{int(np.log2(n))} nilpotent"
    factors = []
    temp = n
    for p in range(2, n+1):
        if temp <= 1: break
        if is_prime(p) and temp % p == 0:
            exp = 0
            while temp % p == 0:
                exp += 1
                temp //= p
            factors.append(f"{p}" + (f"^{exp}" if exp > 1 else ""))
    return "composite: " + "·".join(factors)


# === SETUP ===
from math import comb as _comb
M_bipartitions = sum(_comb(N, k) for k in range(1, N // 2 + 1))
predicted = size_law_prediction(M_bipartitions)

print("=" * 65)
print(f"EXP74: Tegmark Phi N={N} (Whisper DC15W C4402)")
print("=" * 65)
print(f"N={N}: M_bipartitions={M_bipartitions:,}, State dim=2^{N}={2**N:,}")
print(f"Size law prediction: {predicted:.4f} bits (slope={SIZE_LAW_SLOPE}, R²~0.97)")
print(f"P1 range: [{predicted-0.04:.4f}, {predicted+0.04:.4f}]")
print(f"Seed: 74 | K_samples: {K_SAMPLES}")
print(f"Max DM class: 2^{N//2}×2^{N//2} = {2**(N//2)}×{2**(N//2)} (same as N=14)")
print()

# Pre-compute bipartitions (expensive, do once)
print(f"Computing {M_bipartitions:,} bipartitions...", flush=True)
t_parts = time.time()
bipartitions = all_bipartitions(N)
print(f"Done in {time.time()-t_parts:.1f}s. Running K={K_SAMPLES} samples...")

# === MAIN LOOP ===
circuit = build_cnot_ring(N)
phi_mins = []
phi_means = []

t0 = time.time()
for k in range(K_SAMPLES):
    init_state = random_product_state(N, RNG)
    sv = Statevector(init_state).evolve(circuit)
    phi_min, phi_mean = tegmark_phi_for_state(sv.data, N, bipartitions)
    phi_mins.append(phi_min)
    phi_means.append(phi_mean)

    if (k + 1) % 10 == 0:
        elapsed = time.time() - t0
        rate = (k + 1) / elapsed
        remaining = (K_SAMPLES - k - 1) / rate
        print(f"  k={k+1}/{K_SAMPLES}: phi_min_so_far={np.mean(phi_mins):.4f} "
              f"| {elapsed/60:.1f}min elapsed | ~{remaining/60:.1f}min remaining",
              flush=True)

t1 = time.time()

# === RESULTS ===
mean_phi_min = float(np.mean(phi_mins))
std_phi_min = float(np.std(phi_mins))
min_phi_min = float(np.min(phi_mins))
max_phi_min = float(np.max(phi_mins))
mean_phi_mean = float(np.mean(phi_means))
residual = mean_phi_min - predicted

print()
print("=" * 65)
print("RESULTS")
print("=" * 65)
print(f"mean_phi_min = {mean_phi_min:.4f} ± {std_phi_min:.4f}")
print(f"Size law prediction: {predicted:.4f}")
print(f"Residual: {residual:+.4f}")
print(f"Runtime: {(t1-t0)/60:.1f} min")

# === HYPOTHESIS EVALUATION ===
phi12 = HISTORICAL[12]

# P1: size law prediction
p1 = (predicted - 0.04) <= mean_phi_min <= (predicted + 0.04)
print(f"\nP1 (size law N=15 ≈ {predicted:.4f}): {'CONFIRMED' if p1 else 'FALSIFIED'} "
      f"(range [{predicted-0.04:.4f}, {predicted+0.04:.4f}], actual {mean_phi_min:.4f})")

# P2: decline continues vs N=12
p2 = mean_phi_min < phi12
print(f"P2 (decline continues, phi15 < phi12={phi12:.4f}): "
      f"{'CONFIRMED' if p2 else 'FALSIFIED'} (actual {mean_phi_min:.4f})")

# P3: no prime-composite residue for N=15=3×5 (composite)
p3 = abs(residual) < 0.05
print(f"P3 (|residual| < 0.05 for composite N=15): "
      f"{'CONFIRMED' if p3 else 'FALSIFIED'} (|residual|={abs(residual):.4f})")

# P4: fit quality check (requires refit — approximate check)
# Check that N=15 is consistent with the existing fit (|residual| < 2× prior max |residual|)
max_prior_residual = max(abs(HISTORICAL[n] - size_law_prediction(sum(_comb(n, k) for k in range(1, n//2+1))))
                         for n in HISTORICAL if n >= 10)
p4_approx = abs(residual) < 2 * max_prior_residual
print(f"P4 (fit quality maintained, |residual| < 2×max_prior={2*max_prior_residual:.4f}): "
      f"{'CONFIRMED' if p4_approx else 'FALSIFIED'} (|residual|={abs(residual):.4f})")

# === FULL SERIES TABLE ===
print()
print("=" * 70)
print("FULL SERIES N=3..15 with size law")
print("=" * 70)
print(f"{'N':>3} {'M_parts':>8} {'SizeLaw':>8} {'Actual':>8} {'Residual':>9} {'Note'}")
print("-" * 70)
for n in sorted(list(HISTORICAL.keys()) + [N]):
    m = sum(_comb(n, k) for k in range(1, n // 2 + 1))
    pred = size_law_prediction(m)
    if n == N:
        actual = mean_phi_min
        res = actual - pred
        tag = " ← EXP74"
    else:
        actual = HISTORICAL[n]
        res = actual - pred
        tag = ""
    print(f"{n:>3} {m:>8,} {pred:>8.4f} {actual:>8.4f} {res:>+9.4f} {divisor_note(n)[:15]}{tag}")

# === SAVE RESULTS ===
results = {
    "experiment": "Exp74 Tegmark Phi N=15",
    "author": "Whisper (DC15W)",
    "cycle": 4402,
    "n": N,
    "seed": 74,
    "K_samples": K_SAMPLES,
    "M_bipartitions": M_bipartitions,
    "size_law_prediction": round(predicted, 4),
    "mean_phi_min": round(mean_phi_min, 4),
    "std_phi_min": round(std_phi_min, 4),
    "min_phi_min": round(min_phi_min, 4),
    "max_phi_min": round(max_phi_min, 4),
    "mean_phi_mean_allpartitions": round(mean_phi_mean, 4),
    "residual_from_size_law": round(residual, 4),
    "runtime_seconds": round(t1 - t0, 1),
    "hypotheses": {
        "P1_size_law_n15": {
            "predicted_range": [round(predicted - 0.04, 4), round(predicted + 0.04, 4)],
            "actual": round(mean_phi_min, 4),
            "confirmed": p1
        },
        "P2_decline_continues": {
            "vs_n12_actual": phi12,
            "n15_actual": round(mean_phi_min, 4),
            "confirmed": p2
        },
        "P3_no_prime_residue_composite_n15": {
            "residual": round(abs(residual), 4),
            "threshold": 0.05,
            "confirmed": p3
        },
        "P4_fit_quality": {
            "residual": round(abs(residual), 4),
            "threshold": round(2 * max_prior_residual, 4),
            "confirmed": p4_approx
        }
    },
    "notes": (
        f"Pre-registered C4402 BLIND to Exp72 N=14 results. "
        f"N=15=3×5 (composite). Max DM class same as N=14 (128×128). "
        f"Whisper-WHY: tests whether quantum causal integration (phi_min>0) "
        f"persists at N=15 or begins to plateau toward a floor."
    )
}

out_path = "/droid/repos/quantum/experiments/exp74_results.json"
with open(out_path, "w") as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to: {out_path}")
print(f"Total runtime: {(t1-t0)/60:.1f} min")
