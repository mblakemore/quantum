#!/usr/bin/env python3
"""
Exp72: Tegmark Quantum Phi N-Scaling Extension to N=13..14
Tests pred_c4012_001 and extends size law phi = -0.0236*log2(M) + 0.7531

Ember (DC15E) C4014 2026-06-27
Methodology identical to Exp71 for direct comparability.
"""
import numpy as np
import json
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, partial_trace, entropy
from itertools import combinations
import time

RNG = np.random.default_rng(seed=72)
N_SIZES = [13, 14]
K_SAMPLES = 100

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

def divisor_note(n):
    def is_prime(x):
        if x < 2: return False
        for i in range(2, int(x**0.5)+1):
            if x % i == 0: return False
        return True
    if is_prime(n):
        return "prime"
    if (n & (n-1)) == 0:
        return f"2^{int(np.log2(n))} — nilpotent"
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

# Size law parameters from Exp71 fit
SIZE_LAW_SLOPE = -0.0236
SIZE_LAW_INTERCEPT = 0.7531

def size_law_prediction(n_bipartitions):
    return SIZE_LAW_SLOPE * np.log2(n_bipartitions) + SIZE_LAW_INTERCEPT

print("=" * 65)
print("Exp72: Tegmark Quantum Phi N-Scaling Extension (N=13..14)")
print("Ember DC15E C4014 | 2026-06-27")
print("=" * 65)
print(f"Size law: phi_min = {SIZE_LAW_SLOPE} * log2(M) + {SIZE_LAW_INTERCEPT}")
print(f"Testing pred_c4012_001: N=13 prediction = 0.470 bits")
print()

# Carry forward Exp71 results for context
exp71_results = {
    3: 0.700, 4: 0.699, 5: 0.651, 6: 0.633, 7: 0.609,
    8: 0.579, 9: 0.562, 10: 0.534, 11: 0.543, 12: 0.464
}

results = {
    "experiment": "exp72",
    "author": "Ember (DC15E)",
    "cycle": "C4014",
    "date": "2026-06-27",
    "validates": "pred_c4012_001",
    "size_law_slope": SIZE_LAW_SLOPE,
    "size_law_intercept": SIZE_LAW_INTERCEPT,
    "n_sizes": N_SIZES,
    "n_samples": K_SAMPLES,
    "exp71_reference": exp71_results,
    "per_n": {}
}

total_start = time.time()

for N in N_SIZES:
    print(f"\n--- N={N} ({divisor_note(N)}) ---")
    t0 = time.time()

    circuit = build_cnot_ring(N)
    bipartitions = all_bipartitions(N)
    n_bipartitions = len(bipartitions)
    predicted = size_law_prediction(n_bipartitions)

    print(f"  Bipartitions: {n_bipartitions:,} | State dim: {2**N:,}")
    print(f"  Size law prediction: {predicted:.4f} bits")

    phi_mins = []
    phi_means_all = []

    for k in range(K_SAMPLES):
        init_state = random_product_state(N, RNG)
        sv = Statevector(init_state)
        sv = sv.evolve(circuit)
        sv_array = sv.data
        phi_min, phi_mean = tegmark_phi_for_state(sv_array, N, bipartitions)
        phi_mins.append(phi_min)
        phi_means_all.append(phi_mean)

        if (k + 1) % 20 == 0:
            elapsed = time.time() - t0
            eta = elapsed / (k+1) * (K_SAMPLES - k - 1)
            print(f"  k={k+1:3d}/{K_SAMPLES} | phi_min_so_far={np.mean(phi_mins):.4f} | "
                  f"elapsed={elapsed:.0f}s | ETA={eta:.0f}s")

    t1 = time.time()

    mean_phi_min = float(np.mean(phi_mins))
    std_phi_min = float(np.std(phi_mins))
    min_phi_min = float(np.min(phi_mins))
    max_phi_min = float(np.max(phi_mins))
    mean_phi_mean = float(np.mean(phi_means_all))

    residual = mean_phi_min - predicted
    within_pred_c4012 = (0.43 <= mean_phi_min <= 0.51) if N == 13 else None
    within_p2 = (0.40 <= mean_phi_min <= 0.48) if N == 14 else None

    per_n = {
        "n": N,
        "divisor_note": divisor_note(N),
        "n_bipartitions": n_bipartitions,
        "size_law_prediction": round(predicted, 4),
        "mean_phi_min": mean_phi_min,
        "std_phi_min": std_phi_min,
        "min_phi_min": min_phi_min,
        "max_phi_min": max_phi_min,
        "mean_phi_mean_allpartitions": mean_phi_mean,
        "residual_from_size_law": round(residual, 4),
        "runtime_seconds": round(t1 - t0, 2)
    }
    if within_pred_c4012 is not None:
        per_n["pred_c4012_001_confirmed"] = within_pred_c4012
    if within_p2 is not None:
        per_n["p2_confirmed"] = within_p2

    results["per_n"][str(N)] = per_n

    print(f"  RESULT: mean_phi_min={mean_phi_min:.4f} ± {std_phi_min:.4f}")
    print(f"  Prediction: {predicted:.4f} | Residual: {residual:+.4f}")
    if N == 13:
        status = "CONFIRMED" if within_pred_c4012 else "FALSIFIED"
        print(f"  pred_c4012_001: {status} (range 0.43-0.51)")
    print(f"  Runtime: {t1-t0:.1f}s")

# === ANALYSIS ===
print("\n" + "=" * 65)
print("FULL SERIES (N=3..14) with size law predictions")
print("=" * 65)
print(f"{'N':>3} {'M_parts':>8} {'SizeLaw':>8} {'Actual':>8} {'Residual':>9} {'Divisor'}")
print("-" * 65)

all_n = sorted(list(exp71_results.keys()) + N_SIZES)
for N in all_n:
    from math import comb
    M = sum(comb(N, k) for k in range(1, N//2+1))
    pred = size_law_prediction(M)
    if N in N_SIZES:
        actual = results["per_n"][str(N)]["mean_phi_min"]
        residual = actual - pred
        print(f"{N:>3} {M:>8,} {pred:>8.4f} {actual:>8.4f} {residual:>+9.4f} {divisor_note(N)[:20]} ← NEW")
    else:
        actual = exp71_results[N]
        residual = actual - pred
        print(f"{N:>3} {M:>8,} {pred:>8.4f} {actual:>8.4f} {residual:>+9.4f} {divisor_note(N)[:20]}")

# Hypothesis evaluation
print("\n=== PREDICTION OUTCOMES ===")
phi13 = results["per_n"]["13"]["mean_phi_min"]
phi14 = results["per_n"]["14"]["mean_phi_min"] if "14" in results["per_n"] else None
phi12 = exp71_results[12]

# P1 (pred_c4012_001)
p1 = 0.43 <= phi13 <= 0.51
print(f"P1 pred_c4012_001 (N=13 ≈ 0.470): {'CONFIRMED' if p1 else 'FALSIFIED'} (actual {phi13:.4f}, range 0.43-0.51)")

# P3 (no plateau at N=13..14)
if phi14 is not None:
    p3 = phi14 < phi12
    print(f"P3 (decline continues, phi14 < phi12={phi12:.4f}): {'CONFIRMED' if p3 else 'FALSIFIED'} (N=14={phi14:.4f})")

# P4 (no prime residue at N=13)
if phi14 is not None:
    p4 = abs(phi13 - min(phi12, phi14)) < 0.05
    print(f"P4 (N=13 prime not systematically higher): {'CONFIRMED' if p4 else 'FALSIFIED'}")

# Size law quality check
residuals_14 = []
for N in N_SIZES:
    from math import comb
    M = sum(comb(N, k) for k in range(1, N//2+1))
    actual = results["per_n"][str(N)]["mean_phi_min"]
    pred = size_law_prediction(M)
    residuals_14.append(abs(actual - pred))
print(f"\nSize law fit quality (N=13..14): max |residual| = {max(residuals_14):.4f} bits")

total_elapsed = time.time() - total_start

# Hypotheses dict
hypotheses = {
    "P1_pred_c4012_001_confirmed": p1,
    "P3_decline_continues": phi14 < phi12 if phi14 else None,
}

results["hypotheses"] = hypotheses
results["total_runtime_seconds"] = round(total_elapsed, 1)

out_path = "/droid/repos/quantum/experiments/exp72_results.json"
with open(out_path, "w") as f:
    json.dump(results, f, indent=2)

print(f"\nTotal runtime: {total_elapsed:.1f}s")
print(f"Results saved to: {out_path}")
