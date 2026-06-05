#!/usr/bin/env python3
"""
Exp 38: X-Basis QAOA vs Standard QAOA Noise Wall Comparison
Commutation-Aligned QAOA on FakeMarrakesh (Whisper C3943)
Pre-registration: experiments/38-xbasis-qaoa-preregistration.md
"""
import json
import numpy as np
from scipy.optimize import minimize
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime.fake_provider import FakeMarrakesh

# 4-node ring graph: edges (0,1),(1,2),(2,3),(0,3) — max cut = 4
EDGES = [(0, 1), (1, 2), (2, 3), (0, 3)]
N_QUBITS = 4
MAX_CUT = 4


def compute_cut_value(bitstring, edges):
    """Compute cut value for a bitstring (string of 0/1 chars)."""
    cut = 0
    for i, j in edges:
        if bitstring[i] != bitstring[j]:
            cut += 1
    return cut


def build_standard_qaoa(p, gamma, beta):
    """Build standard QAOA circuit (Z-basis cost, X-basis mixer)."""
    qc = QuantumCircuit(N_QUBITS, N_QUBITS)
    # Initial state: |++++>
    qc.h(range(N_QUBITS))

    for layer in range(p):
        g = gamma[layer]
        b = beta[layer]
        # Cost layer: exp(-i*gamma*Z_i*Z_j) via CX-Rz-CX
        for i, j in EDGES:
            qc.cx(i, j)
            qc.rz(2 * g, j)
            qc.cx(i, j)
        # Mixer layer: exp(-i*beta*X_i) = Rx(2*beta)
        for q in range(N_QUBITS):
            qc.rx(2 * b, q)

    qc.measure(range(N_QUBITS), range(N_QUBITS))
    return qc


def build_xbasis_qaoa(p, gamma, beta):
    """Build X-basis QAOA circuit (XX cost, Rz mixer — commutation-aligned)."""
    qc = QuantumCircuit(N_QUBITS, N_QUBITS)
    # Initial state: |++++> (already in X eigenspace)
    qc.h(range(N_QUBITS))

    for layer in range(p):
        g = gamma[layer]
        b = beta[layer]
        # Cost layer: exp(-i*gamma*X_i*X_j) = H*(exp(-i*gamma*Z_i*Z_j))*H
        for i, j in EDGES:
            qc.h(i); qc.h(j)
            qc.cx(i, j)
            qc.rz(2 * g, j)
            qc.cx(i, j)
            qc.h(i); qc.h(j)
        # Mixer layer: exp(-i*beta*Z_i) = Rz(2*beta) — COMMUTES with Z-dephasing
        for q in range(N_QUBITS):
            qc.rz(2 * b, q)

    # X-basis measurement: H before readout
    qc.h(range(N_QUBITS))
    qc.measure(range(N_QUBITS), range(N_QUBITS))
    return qc


def get_approximation_ratio(counts, edges, max_cut, n_qubits):
    """Compute approximation ratio from measurement counts."""
    total_shots = sum(counts.values())
    expected_cut = 0
    for bitstr, count in counts.items():
        # Qiskit bitstring is reversed (LSB first)
        bs = bitstr[::-1]
        cut = compute_cut_value(bs, edges)
        expected_cut += cut * count / total_shots
    return expected_cut / max_cut


def get_output_entropy(counts, n_qubits):
    """Compute normalized entropy of output distribution (0=pure, 1=uniform)."""
    total = sum(counts.values())
    probs = np.array([counts.get(format(i, f'0{n_qubits}b'), 0) / total for i in range(2**n_qubits)])
    probs = probs[probs > 0]
    entropy = -np.sum(probs * np.log2(probs))
    max_entropy = n_qubits  # uniform = n_qubits bits
    return entropy / max_entropy


def run_with_analytic_params(build_fn, p, backend_sim, shots=1024):
    """Run QAOA with analytically-motivated parameters (no optimization loop).
    Uses gamma = pi/(4p), beta = pi/(4p) heuristic that scales well for ring graph.
    """
    # Heuristic analytic params: decreasing angles as p increases
    gamma = [np.pi / (4 * p)] * p
    beta = [np.pi / (4 * p)] * p
    qc = build_fn(p, gamma, beta)
    result = backend_sim.run(qc, shots=shots).result()
    counts = result.get_counts()
    ratio = get_approximation_ratio(counts, EDGES, MAX_CUT, N_QUBITS)
    return ratio, (gamma, beta)


def measure_entropy_at_p(build_fn, p, backend_sim, shots=4096):
    """Measure entropy at uniform params (no optimization) to track noise floor."""
    gamma = np.ones(p) * np.pi/4
    beta = np.ones(p) * np.pi/4
    qc = build_fn(p, gamma, beta)
    result = backend_sim.run(qc, shots=shots).result()
    counts = result.get_counts()
    return get_output_entropy(counts, N_QUBITS)


def main():
    print("Exp38: X-Basis QAOA vs Standard QAOA (FakeMarrakesh)")
    print("Pre-registration: experiments/38-xbasis-qaoa-preregistration.md")
    print("=" * 60)

    # Set up FakeMarrakesh noise model
    fake_backend = FakeMarrakesh()
    noise_model = NoiseModel.from_backend(fake_backend)
    sim = AerSimulator(noise_model=noise_model)

    p_values = [1, 4, 8, 16, 24]
    SHOTS = 1024

    results = {
        "experiment": "38",
        "title": "X-Basis QAOA vs Standard QAOA — Commutation-Aligned Depth Extension",
        "backend": "FakeMarrakesh",
        "problem": "4-node ring MaxCut (max_cut=4)",
        "edges": EDGES,
        "shots": SHOTS,
        "p_values": p_values,
        "standard_qaoa": {},
        "xbasis_qaoa": {},
        "entropy_standard": {},
        "entropy_xbasis": {},
        "goals": {}
    }

    print("\nRunning Standard QAOA (analytic params, no optimization)...")
    for p in p_values:
        print(f"  p={p}...", end=" ", flush=True)
        ratio, _ = run_with_analytic_params(build_standard_qaoa, p, sim, shots=SHOTS)
        entropy = measure_entropy_at_p(build_standard_qaoa, p, sim, shots=SHOTS)
        results["standard_qaoa"][p] = float(ratio)
        results["entropy_standard"][p] = float(entropy)
        print(f"r={ratio:.3f}, entropy={entropy:.3f}")

    print("\nRunning X-Basis QAOA (commutation-aligned, analytic params)...")
    for p in p_values:
        print(f"  p={p}...", end=" ", flush=True)
        ratio, _ = run_with_analytic_params(build_xbasis_qaoa, p, sim, shots=SHOTS)
        entropy = measure_entropy_at_p(build_xbasis_qaoa, p, sim, shots=SHOTS)
        results["xbasis_qaoa"][p] = float(ratio)
        results["entropy_xbasis"][p] = float(entropy)
        print(f"r={ratio:.3f}, entropy={entropy:.3f}")

    # Evaluate pre-registered goals
    print("\n=== Goal Evaluation ===")

    # G1: X-basis approximation ratio advantage at p=8
    r_std_8 = results["standard_qaoa"].get(8, 0)
    r_x_8 = results["xbasis_qaoa"].get(8, 0)
    g1_pass = r_x_8 >= r_std_8 + 0.05
    results["goals"]["G1"] = {
        "criterion": "r_X >= r_Z + 0.05 at p=8",
        "r_standard": r_std_8, "r_xbasis": r_x_8,
        "difference": r_x_8 - r_std_8,
        "result": "PASS" if g1_pass else "FAIL"
    }
    print(f"G1: r_std={r_std_8:.3f}, r_xbasis={r_x_8:.3f}, diff={r_x_8-r_std_8:.3f} → {'PASS' if g1_pass else 'FAIL'}")

    # G2: Extended depth ceiling (p_X > p_Z baseline ~16)
    # Noise wall = first p where entropy > 0.95
    def find_noise_wall(entropy_dict):
        for p in sorted(entropy_dict.keys()):
            if entropy_dict[p] > 0.95:
                return p
        return max(entropy_dict.keys())  # didn't hit wall

    std_wall = find_noise_wall(results["entropy_standard"])
    xbasis_wall = find_noise_wall(results["entropy_xbasis"])
    g2_pass = xbasis_wall >= 20  # predicted ≥20
    results["goals"]["G2"] = {
        "criterion": "X-basis noise wall p >= 20",
        "standard_wall_p": std_wall, "xbasis_wall_p": xbasis_wall,
        "result": "PASS" if g2_pass else "FAIL"
    }
    print(f"G2: std_wall_p={std_wall}, xbasis_wall_p={xbasis_wall} → {'PASS' if g2_pass else 'FAIL'}")

    # G3: X-basis lower noise per layer (compare at p=4, normalized)
    e_std_4 = results["entropy_standard"].get(4, 1)
    e_x_4 = results["entropy_xbasis"].get(4, 1)
    g3_pass = e_x_4 < e_std_4
    results["goals"]["G3"] = {
        "criterion": "X-basis entropy < Standard entropy at p=4 (fixed params)",
        "entropy_standard": e_std_4, "entropy_xbasis": e_x_4,
        "result": "PASS" if g3_pass else "FAIL"
    }
    print(f"G3: entropy_std={e_std_4:.3f}, entropy_xbasis={e_x_4:.3f} → {'PASS' if g3_pass else 'FAIL'}")

    # G4: Equal performance at p=0 (approximation ratio = 0.5 for random)
    r_std_1 = results["standard_qaoa"].get(1, 0)
    r_x_1 = results["xbasis_qaoa"].get(1, 0)
    g4_pass = abs(r_std_1 - r_x_1) < 0.10
    results["goals"]["G4"] = {
        "criterion": "Both converge near same ratio at p=1",
        "r_standard": r_std_1, "r_xbasis": r_x_1,
        "result": "PASS" if g4_pass else "FAIL"
    }
    print(f"G4: r_std_p1={r_std_1:.3f}, r_xbasis_p1={r_x_1:.3f} → {'PASS' if g4_pass else 'FAIL'}")

    # Overall verdict
    goals_passed = sum(1 for g in ['G1','G2','G3','G4'] if results["goals"][g]["result"] == "PASS")
    g1_or_g2 = g1_pass or g2_pass
    principle_supported = g1_or_g2

    results["verdict"] = {
        "goals_passed": f"{goals_passed}/4",
        "G1_or_G2": g1_or_g2,
        "conclusion": "Commutation principle EXTENDS to QAOA depth advantage" if g1_or_g2
                      else "Commutation principle does NOT extend to QAOA depth advantage — pivot needed"
    }

    print(f"\nVERDICT: {goals_passed}/4 goals passed")
    print(f"Conclusion: {results['verdict']['conclusion']}")

    # Save results
    out_path = "/droid/repos/quantum/experiments/38-xbasis-qaoa-results.json"
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {out_path}")

    return results


if __name__ == "__main__":
    np.random.seed(38)  # Fixed seed for reproducibility
    main()
