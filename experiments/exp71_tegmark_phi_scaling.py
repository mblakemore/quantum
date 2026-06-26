#!/usr/bin/env python3
"""
Exp71: Tegmark Quantum Phi N-Scaling
Extends Whisper's Exp70 (N=3..9) to N=3..12
Ember (DC15E) C4012 2026-06-26

Methodology identical to Exp70 for comparability.
"""
import numpy as np
import json
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, partial_trace, entropy
from itertools import combinations
import time

RNG = np.random.default_rng(seed=71)
N_SIZES = list(range(3, 13))  # 3..12
K_SAMPLES = 100  # vs Exp70's 200; tractable for N=12

def build_cnot_ring(n):
    """Build N-qubit CNOT ring circuit (same as Exp69/Exp70)."""
    qc = QuantumCircuit(n)
    for i in range(n):
        qc.cx(i, (i + 1) % n)
    return qc

def random_product_state(n, rng):
    """Generate a random N-qubit product state from Bloch sphere uniform distribution."""
    state = np.array([1.0], dtype=complex)
    for _ in range(n):
        # Uniform on Bloch sphere: theta, phi
        theta = np.arccos(1 - 2 * rng.random())
        phi = rng.random() * 2 * np.pi
        qubit = np.array([np.cos(theta / 2), np.exp(1j * phi) * np.sin(theta / 2)])
        state = np.kron(state, qubit)
    return state

def all_bipartitions(n):
    """
    Generate all unique non-trivial bipartitions (A, B=complement).
    Returns subsets A where 1 <= |A| <= n//2.
    For |A| == n//2 and n even, includes all — minor double-count but matches Exp70.
    """
    qubits = list(range(n))
    parts = []
    for size in range(1, n // 2 + 1):
        for combo in combinations(qubits, size):
            parts.append(list(combo))
    return parts

def tegmark_phi_for_state(sv_array, n, bipartitions):
    """
    Compute Tegmark quantum Phi (min bipartition entropy) for a given statevector.
    Returns (phi_min, phi_mean).
    """
    # Convert to Statevector object
    sv = Statevector(sv_array)
    
    entropies = []
    for A in bipartitions:
        # partial_trace traces OUT the B qubits — we want to trace out complement of A
        B = [i for i in range(n) if i not in A]
        # Qiskit convention: qubits are indexed from 0 to n-1
        # partial_trace(state, qargs) traces out the qargs qubits
        rho_A = partial_trace(sv, B)
        s = entropy(rho_A, base=2)  # Von Neumann entropy in bits
        entropies.append(s)
    
    if not entropies:
        return 0.0, 0.0
    
    return min(entropies), float(np.mean(entropies))

def classical_phi_reference():
    """Ember's classical Phi values from F43/F45."""
    return {
        3: 1.875, 4: 0.0, 5: 15.156, 6: 1.875, 7: 49.609,
        8: 0.0, 9: None,  # TBD (pred_c4011_002)
        10: None, 11: None, 12: None
    }

def divisor_note(n):
    """Classify N by divisor structure."""
    if n <= 1:
        return "trivial"
    # Check if prime
    def is_prime(x):
        if x < 2: return False
        for i in range(2, int(x**0.5)+1):
            if x % i == 0: return False
        return True
    if is_prime(n):
        return "prime"
    # Check if power of 2
    if (n & (n-1)) == 0:
        return f"2^{int(np.log2(n))} — nilpotent (classical Phi=0)"
    # Factorize
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

print("=" * 60)
print("Exp71: Tegmark Quantum Phi N-Scaling (N=3..12)")
print("Ember DC15E C4012 | 2026-06-26")
print("=" * 60)

results = {
    "experiment": "exp71",
    "author": "Ember (DC15E)",
    "cycle": "C4012",
    "date": "2026-06-26",
    "n_sizes": N_SIZES,
    "n_samples": K_SAMPLES,
    "per_n": {}
}

# Whisper Exp70 reference data (for comparison table)
whisper_exp70 = {
    3: 0.5978, 4: 0.6219, 5: 0.6460, 6: 0.6220, 
    7: 0.5550, 8: 0.5720, 9: 0.5140
}

classical_phi = classical_phi_reference()

total_start = time.time()

for N in N_SIZES:
    print(f"\n--- N={N} ({divisor_note(N)}) ---")
    t0 = time.time()
    
    circuit = build_cnot_ring(N)
    bipartitions = all_bipartitions(N)
    n_bipartitions = len(bipartitions)
    
    print(f"  Bipartitions: {n_bipartitions}")
    
    phi_mins = []
    phi_means_all = []
    
    for k in range(K_SAMPLES):
        # Generate random product state
        init_state = random_product_state(N, RNG)
        
        # Apply CNOT ring via Statevector
        sv = Statevector(init_state)
        sv = sv.evolve(circuit)
        sv_array = sv.data
        
        # Compute Tegmark Phi
        phi_min, phi_mean = tegmark_phi_for_state(sv_array, N, bipartitions)
        phi_mins.append(phi_min)
        phi_means_all.append(phi_mean)
        
        if (k + 1) % 25 == 0:
            elapsed = time.time() - t0
            print(f"  Progress: {k+1}/{K_SAMPLES} states | {elapsed:.1f}s | current mean_phi_min={np.mean(phi_mins):.4f}")
    
    t1 = time.time()
    
    mean_phi_min = float(np.mean(phi_mins))
    std_phi_min = float(np.std(phi_mins))
    min_phi_min = float(np.min(phi_mins))
    max_phi_min = float(np.max(phi_mins))
    mean_phi_mean = float(np.mean(phi_means_all))
    
    # H1 check: phi_min > 0.1 for all N (basic quantum integration)
    h1_pass = mean_phi_min > 0.1
    
    # Compare to Exp70 if available
    exp70_val = whisper_exp70.get(N, None)
    exp70_note = f"Exp70: {exp70_val:.4f}" if exp70_val else "NEW (beyond Exp70 range)"
    
    per_n = {
        "n": N,
        "divisor_note": divisor_note(N),
        "classical_phi": classical_phi.get(N),
        "n_bipartitions": n_bipartitions,
        "mean_phi_min": mean_phi_min,
        "std_phi_min": std_phi_min,
        "min_phi_min": min_phi_min,
        "max_phi_min": max_phi_min,
        "mean_phi_mean_allpartitions": mean_phi_mean,
        "h1_pass_phi_gt_0p1": h1_pass,
        "runtime_seconds": round(t1 - t0, 2),
        "exp70_reference": exp70_val
    }
    results["per_n"][str(N)] = per_n
    
    print(f"  RESULT: mean_phi_min={mean_phi_min:.4f} ± {std_phi_min:.4f} | {exp70_note}")
    print(f"  Runtime: {t1-t0:.1f}s")

# === ANALYSIS ===
print("\n" + "=" * 60)
print("SUMMARY TABLE (comparing Exp70 and Exp71)")
print("=" * 60)
print(f"{'N':>3} {'ClassPhi':>10} {'QPhiMin':>10} {'Exp70Ref':>10} {'Divisor'}")
print("-" * 60)

for N in N_SIZES:
    r = results["per_n"][str(N)]
    cp = r.get("classical_phi")
    cp_str = f"{cp:.3f}" if cp is not None else "TBD"
    exp70_str = f"{r['exp70_reference']:.4f}" if r['exp70_reference'] else "---"
    print(f"{N:>3} {cp_str:>10} {r['mean_phi_min']:>10.4f} {exp70_str:>10} {r['divisor_note'][:30]}")

# Hypothesis evaluation
print("\n=== HYPOTHESIS EVALUATION ===")
phi_vals = {N: results["per_n"][str(N)]["mean_phi_min"] for N in N_SIZES}

# H1: N=10,11,12 continue below N=9
phi9 = phi_vals.get(9, 0.514)
h1 = phi_vals[10] < phi9 and phi_vals[12] < phi9
print(f"H1 (decline continues beyond N=9={phi9:.4f}): {'CONFIRMED' if h1 else 'FALSIFIED'}")
print(f"   N=10: {phi_vals[10]:.4f}, N=11: {phi_vals[11]:.4f}, N=12: {phi_vals[12]:.4f}")

# H2: N=5 remains the global peak
peak_val = max(phi_vals.values())
peak_n = max(phi_vals, key=phi_vals.get)
h2 = peak_val <= 0.646
print(f"H2 (N=5 remains peak over N=3..12): {'CONFIRMED' if h2 else 'FALSIFIED'}")
print(f"   Global peak: N={peak_n} with phi={peak_val:.4f} (N=5 Exp70 was 0.646)")

# H3: No prime residue at N=10..12
phi10 = phi_vals[10]
phi11 = phi_vals[11]
phi12 = phi_vals[12]
h3 = abs(phi11 - min(phi10, phi12)) < 0.05
print(f"H3 (no prime residue for N=11 vs N=10,12): {'CONFIRMED' if h3 else 'FALSIFIED'}")
print(f"   phi(10)={phi10:.4f}, phi(11)={phi11:.4f}, phi(12)={phi12:.4f}")

total_elapsed = time.time() - total_start
print(f"\nTotal runtime: {total_elapsed:.1f}s")

# Save results
results["hypotheses"] = {
    "H1_decline_continues": h1,
    "H2_n5_remains_peak": h2,
    "H3_no_prime_residue": h3
}
results["total_runtime_seconds"] = round(total_elapsed, 1)

out_path = "/droid/repos/quantum/experiments/exp71_results.json"
with open(out_path, "w") as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to: {out_path}")
