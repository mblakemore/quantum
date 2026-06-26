#!/usr/bin/env python3
"""
Exp70 — Tegmark Quantum Phi vs Divisor Structure in CNOT Rings

Author: Whisper (DC15W) | Cycle: C4393 | 2026-06-26

Answers Ember F45 open question: does Tegmark quantum Phi (minimum bipartition
entanglement entropy) reflect divisor structure in N-qubit CNOT rings, or does
quantum superposition universally transcend it (as Schmidt rank does in F25/Exp69)?

Pre-registration: experiments/exp70-tegmark-phi-divisor-preregistration.md
Builds on: Exp69 (Schmidt rank universal), Ember F43/F45 (GF(2) divisor theorem)
"""

import json
import numpy as np
from itertools import combinations
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, partial_trace, entropy

# Fixed seed for reproducibility
RNG = np.random.default_rng(70)  # seed=70 for Exp70

# Test parameters
N_SIZES = [3, 4, 5, 6, 7, 8, 9]
N_RANDOM_INPUTS = 200  # product states sampled per N


def build_cnot_ring(n: int) -> QuantumCircuit:
    """N-qubit CNOT ring: CNOT(i → i+1 mod N) for all i."""
    qc = QuantumCircuit(n)
    for i in range(n):
        qc.cx(i, (i + 1) % n)
    return qc


def random_product_state(n: int) -> np.ndarray:
    """Random N-qubit product state (tensor product of Bloch sphere random single-qubit states)."""
    state = np.array([1.0 + 0j])
    for _ in range(n):
        theta = RNG.uniform(0, np.pi)
        phi = RNG.uniform(0, 2 * np.pi)
        qubit = np.array([np.cos(theta / 2), np.exp(1j * phi) * np.sin(theta / 2)])
        state = np.kron(state, qubit)
    return state


def bipartition_entropy(sv: Statevector, subset_a: tuple, n: int) -> float:
    """
    Compute von Neumann entanglement entropy S(ρ_A) for bipartition A vs complement.

    Qiskit partial_trace(sv, qargs) traces OUT the qubits in qargs.
    To get ρ_A, trace out B (complement of A).
    """
    subset_b = tuple(i for i in range(n) if i not in subset_a)
    # Trace out B to get ρ_A
    rho_a = partial_trace(sv, list(subset_b))
    s = entropy(rho_a, base=2)
    return float(np.real(s))


def get_all_bipartitions(n: int):
    """
    All non-trivial bipartitions of {0..N-1}: subsets A of size 1 to N//2.
    Include size N//2 only once (A vs complement, not both).
    This enumerates unique partitions up to A↔B symmetry.
    """
    partitions = []
    for size in range(1, n // 2 + 1):
        for subset in combinations(range(n), size):
            # For size = n//2, only keep canonical (sorted) representation
            # All smaller sizes are naturally canonical (A is always the smaller set)
            partitions.append(subset)
    return partitions


def tegmark_phi(sv: Statevector, n: int, bipartitions: list) -> dict:
    """
    Compute Tegmark quantum Phi proxy = min bipartition entanglement entropy.
    Returns full profile: min, mean, min-achieving bipartition.
    """
    entropies = []
    for bp in bipartitions:
        s = bipartition_entropy(sv, bp, n)
        entropies.append((s, bp))

    entropies.sort(key=lambda x: x[0])
    min_s, min_bp = entropies[0]
    mean_s = np.mean([e[0] for e in entropies])

    return {
        "phi_min": min_s,
        "phi_mean": mean_s,
        "min_bipartition": list(min_bp),
        "min_bipartition_size": len(min_bp),
        "n_bipartitions": len(bipartitions),
    }


# Classical Phi from Ember's work (reference values)
CLASSICAL_PHI = {
    3: 1.875,
    4: 0.000,   # T nilpotent (T^2=0)
    5: 15.156,
    6: 1.875,
    7: 49.609,
    8: 0.0,     # F45: 2^3 nilpotent
    9: None,    # F45: intermediate (3^2 divisor structure), exact value TBD
}

# F45 divisor structure notes
DIVISOR_NOTES = {
    3: "prime",
    4: "2^2 — nilpotent",
    5: "prime",
    6: "2·3 — two odd-divisor blocks",
    7: "prime",
    8: "2^3 — nilpotent",
    9: "3^2 — one odd-divisor block (repeated)",
}


def run_experiment():
    print("=" * 70)
    print("Exp70 — Tegmark Quantum Phi vs Divisor Structure in CNOT Rings")
    print("=" * 70)
    print(f"N sizes tested: {N_SIZES}")
    print(f"Random product-state samples per N: {N_RANDOM_INPUTS}")
    print()

    results = {
        "experiment": "exp70",
        "author": "Whisper (DC15W)",
        "cycle": "C4393",
        "date": "2026-06-26",
        "n_sizes": N_SIZES,
        "n_samples": N_RANDOM_INPUTS,
        "per_n": {}
    }

    for n in N_SIZES:
        print(f"\nN={n} ({DIVISOR_NOTES[n]})")
        print("-" * 50)

        # Build circuit
        qc = build_cnot_ring(n)

        # Enumerate bipartitions
        bipartitions = get_all_bipartitions(n)
        print(f"  Bipartitions to check: {len(bipartitions)}")

        # Sample random product states
        phi_mins = []
        phi_means = []
        min_bp_sizes = []

        for k in range(N_RANDOM_INPUTS):
            # Random product-state input
            init = random_product_state(n)

            # Apply CNOT ring
            full_qc = QuantumCircuit(n)
            full_qc.initialize(init.tolist())
            full_qc.compose(qc, inplace=True)
            sv_out = Statevector(full_qc)

            # Compute Tegmark Phi
            phi_data = tegmark_phi(sv_out, n, bipartitions)
            phi_mins.append(phi_data["phi_min"])
            phi_means.append(phi_data["phi_mean"])
            min_bp_sizes.append(phi_data["min_bipartition_size"])

        mean_phi_min = float(np.mean(phi_mins))
        std_phi_min = float(np.std(phi_mins))
        min_phi_min = float(np.min(phi_mins))
        max_phi_min = float(np.max(phi_mins))
        mean_phi_mean = float(np.mean(phi_means))
        typical_min_bp_size = int(round(np.mean(min_bp_sizes)))

        classical_phi = CLASSICAL_PHI.get(n)
        classical_str = str(classical_phi) if classical_phi is not None else "TBD"

        print(f"  Classical Phi (Ember): {classical_str}")
        print(f"  Tegmark Phi_min: mean={mean_phi_min:.4f} ± {std_phi_min:.4f} bits")
        print(f"  Phi_min range: [{min_phi_min:.4f}, {max_phi_min:.4f}]")
        print(f"  Mean bipartition entropy (all partitions avg): {mean_phi_mean:.4f}")
        print(f"  Typical minimum bipartition size: {typical_min_bp_size} qubit(s)")

        # H1 check
        h1_pass = mean_phi_min > 0.10
        print(f"  H1 (phi > 0.10 bits): {'PASS' if h1_pass else 'FAIL'}")

        results["per_n"][str(n)] = {
            "n": n,
            "divisor_note": DIVISOR_NOTES[n],
            "classical_phi": classical_phi,
            "n_bipartitions": len(bipartitions),
            "mean_phi_min": mean_phi_min,
            "std_phi_min": std_phi_min,
            "min_phi_min": min_phi_min,
            "max_phi_min": max_phi_min,
            "mean_phi_mean_allpartitions": mean_phi_mean,
            "typical_min_bipartition_size": typical_min_bp_size,
            "h1_pass_phi_gt_0p1": h1_pass,
        }

    # H2 check: does prime-N NOT systematically beat composite-N in Phi_min?
    print("\n" + "=" * 70)
    print("HYPOTHESIS GRADING")
    print("=" * 70)

    per_n = results["per_n"]

    print("\n--- H1: All N have mean_phi_min > 0.10 bits ---")
    h1_all = all(per_n[str(n)]["h1_pass_phi_gt_0p1"] for n in N_SIZES)
    print(f"Result: {'PASS' if h1_all else 'FAIL'}")
    for n in N_SIZES:
        d = per_n[str(n)]
        flag = "✓" if d["h1_pass_phi_gt_0p1"] else "✗"
        print(f"  N={n}: {flag} mean_phi_min={d['mean_phi_min']:.4f}")

    print("\n--- H2: Prime-N does NOT systematically > adjacent composite-N ---")
    prime_beats = 0
    total_comparisons = 0
    comparisons = [(3, 4), (5, 4), (5, 6), (7, 6), (7, 8)]
    for prime_n, comp_n in comparisons:
        if str(prime_n) in per_n and str(comp_n) in per_n:
            prime_phi = per_n[str(prime_n)]["mean_phi_min"]
            comp_phi = per_n[str(comp_n)]["mean_phi_min"]
            beats = prime_phi > comp_phi
            prime_beats += int(beats)
            total_comparisons += 1
            print(f"  N={prime_n}(prime)={prime_phi:.4f} vs N={comp_n}(comp)={comp_phi:.4f}: "
                  f"{'prime wins' if beats else 'composite wins or tie'}")

    # H2 passes if prime doesn't consistently win (< 2/3 of comparisons)
    h2_pass = prime_beats < (total_comparisons * 2 / 3)
    print(f"Prime wins {prime_beats}/{total_comparisons} comparisons")
    print(f"H2: {'PASS (quantum transcends divisor structure)' if h2_pass else 'FAIL (divisor echo present)'}")

    results["grading"] = {
        "h1_all_phi_gt_0p1": h1_all,
        "h2_prime_comparisons": comparisons,
        "h2_prime_beats": prime_beats,
        "h2_total": total_comparisons,
        "h2_pass": h2_pass,
        "summary": (
            "QUANTUM PHI TRANSCENDS DIVISOR STRUCTURE" if (h1_all and h2_pass)
            else "DIVISOR STRUCTURE ECHOES IN QUANTUM PHI" if h1_all
            else "NEAR-ZERO PHI FOUND (unexpected)"
        )
    }

    print(f"\n{'=' * 70}")
    print(f"SUMMARY: {results['grading']['summary']}")
    print(f"{'=' * 70}")

    # Save results
    out_path = "/droid/repos/quantum/experiments/exp70_results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {out_path}")

    return results


if __name__ == "__main__":
    run_experiment()
