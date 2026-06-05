#!/usr/bin/env python3
"""
Exp 39: X-Basis QAOA Advantage Under Optimization Budget Constraints
COBYLA budget sweep to test whether commutation advantage manifests at low iterations.
Pre-registration: experiments/39-low-budget-cobyla-preregistration.md
Whisper C3946 | 2026-06-05
"""
import json
import sys
import numpy as np
from scipy.optimize import minimize
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime.fake_provider import FakeMarrakesh

# 4-node ring graph (same as Exp38 for direct comparison)
EDGES_4 = [(0, 1), (1, 2), (2, 3), (0, 3)]
N_QUBITS_4 = 4
MAX_CUT_4 = 4

# 8-node random MaxCut (for size generalizability check)
# Graph: 8 nodes, random connected graph with expected max-cut ~8
EDGES_8 = [(0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(7,0),(0,3),(1,5),(2,6),(4,7)]
N_QUBITS_8 = 8
MAX_CUT_8 = 8  # approximate upper bound


def compute_cut_value(bitstring, edges):
    """Compute cut value for a bitstring (string of 0/1 chars)."""
    return sum(1 for i, j in edges if bitstring[i] != bitstring[j])


def build_standard_qaoa(p, gamma, beta, n_qubits, edges):
    """Standard QAOA (Z-basis cost, Rx mixer)."""
    qc = QuantumCircuit(n_qubits, n_qubits)
    qc.h(range(n_qubits))
    for layer in range(p):
        g, b = gamma[layer], beta[layer]
        for i, j in edges:
            qc.cx(i, j)
            qc.rz(2 * g, j)
            qc.cx(i, j)
        for q in range(n_qubits):
            qc.rx(2 * b, q)
    qc.measure(range(n_qubits), range(n_qubits))
    return qc


def build_xbasis_qaoa(p, gamma, beta, n_qubits, edges):
    """X-basis QAOA (XX cost, Rz mixer — commutes with Z-dephasing)."""
    qc = QuantumCircuit(n_qubits, n_qubits)
    qc.h(range(n_qubits))
    for layer in range(p):
        g, b = gamma[layer], beta[layer]
        for i, j in edges:
            qc.h(i); qc.h(j)
            qc.cx(i, j)
            qc.rz(2 * g, j)
            qc.cx(i, j)
            qc.h(i); qc.h(j)
        for q in range(n_qubits):
            qc.rz(2 * b, q)
    qc.h(range(n_qubits))
    qc.measure(range(n_qubits), range(n_qubits))
    return qc


def get_approximation_ratio(counts, edges, max_cut, n_qubits):
    """Approximation ratio from measurement counts."""
    total = sum(counts.values())
    expected_cut = sum(
        compute_cut_value(bs[::-1], edges) * cnt / total
        for bs, cnt in counts.items()
    )
    return expected_cut / max_cut


def get_output_entropy(counts, n_qubits):
    """Normalized entropy of output distribution."""
    total = sum(counts.values())
    probs = np.array([counts.get(format(i, f'0{n_qubits}b'), 0) / total for i in range(2**n_qubits)])
    probs = probs[probs > 0]
    return -np.sum(probs * np.log2(probs)) / n_qubits


def optimize_qaoa(build_fn, p, sim, edges, max_cut, n_qubits, budget, shots=1024, n_restarts=3):
    """
    Optimize QAOA with COBYLA budget constraint.
    Returns (best_ratio, best_params) across n_restarts random initializations.
    budget = max COBYLA iterations per restart.
    """
    best_ratio = 0.0
    best_params = None

    for restart in range(n_restarts):
        params0 = np.random.uniform(0, 2*np.pi, 2*p)

        def neg_ratio(params):
            gamma = params[:p]
            beta = params[p:]
            qc = build_fn(p, gamma, beta, n_qubits, edges)
            result = sim.run(qc, shots=shots).result()
            counts = result.get_counts()
            return -get_approximation_ratio(counts, edges, max_cut, n_qubits)

        opt = minimize(
            neg_ratio, params0,
            method='COBYLA',
            options={'maxiter': budget, 'rhobeg': 0.5, 'catol': 1e-4}
        )
        ratio = -opt.fun
        if ratio > best_ratio:
            best_ratio = ratio
            best_params = opt.x

    return best_ratio, best_params


def run_entropy_check(build_fn, p, sim, edges, n_qubits, shots=4096):
    """Measure entropy at heuristic params (no optimization) — budget-independent coherence check."""
    gamma = [np.pi / (4 * p)] * p
    beta = [np.pi / (4 * p)] * p
    qc = build_fn(p, gamma, beta, n_qubits, edges)
    result = sim.run(qc, shots=shots).result()
    counts = result.get_counts()
    return get_output_entropy(counts, n_qubits)


def main(problem="4node", run_hardware=False):
    import sys
    print(f"Exp39: X-Basis QAOA Budget Sweep ({'4-node ring' if problem=='4node' else '8-node random'})", flush=True)
    print("Pre-registration: experiments/39-low-budget-cobyla-preregistration.md", flush=True)
    print("=" * 65, flush=True)

    # Problem selection
    if problem == "4node":
        edges = EDGES_4
        n_qubits = N_QUBITS_4
        max_cut = MAX_CUT_4
        p_values = [1, 4]  # skip p=8: too slow for FakeMarrakesh budget sweep
    else:
        edges = EDGES_8
        n_qubits = N_QUBITS_8
        max_cut = MAX_CUT_8
        p_values = [1, 4]

    # Budget sweep
    # NOTE Protocol Deviation PD1: COBYLA requires min maxiter = num_vars+2.
    # For p=1 (2 params): min=4. For p=4 (8 params): min=10.
    # Budgets below these minimums are silently raised by scipy.
    # Therefore effective low-budget range is: p=1 → [4,6,8], p=4 → [10,15,20]
    BUDGET_LEVELS = [4, 6, 8, 12, 16, 20, 30, 50]  # effective minimums as floor
    N_RESTARTS = 2
    SHOTS = 256  # reduced for speed (FakeMarrakesh local sim)

    # FakeMarrakesh noise model
    fake_backend = FakeMarrakesh()
    noise_model = NoiseModel.from_backend(fake_backend)
    sim = AerSimulator(noise_model=noise_model)

    results = {
        "experiment": "39",
        "title": "X-Basis QAOA Budget Sweep — Commutation Advantage Under COBYLA Constraints",
        "backend": "FakeMarrakesh",
        "problem": f"{n_qubits}-qubit MaxCut",
        "edges": edges,
        "n_qubits": n_qubits,
        "max_cut": max_cut,
        "shots": SHOTS,
        "n_restarts": N_RESTARTS,
        "p_values": p_values,
        "budget_levels": BUDGET_LEVELS,
        "standard_qaoa": {},  # [budget][p] = ratio
        "xbasis_qaoa": {},
        "entropy_standard": {},  # [p] = entropy (budget-independent)
        "entropy_xbasis": {},
        "goals": {}
    }

    # Entropy check (budget-independent, run once per p)
    print("\n[Entropy check — budget-independent coherence]")
    for p in p_values:
        e_std = run_entropy_check(build_standard_qaoa, p, sim, edges, n_qubits)
        e_xb = run_entropy_check(build_xbasis_qaoa, p, sim, edges, n_qubits)
        results["entropy_standard"][p] = float(e_std)
        results["entropy_xbasis"][p] = float(e_xb)
        print(f"  p={p}: entropy_std={e_std:.3f}, entropy_xbasis={e_xb:.3f}")

    # Budget sweep
    print(f"\n[Budget sweep: p={p_values}, budgets={BUDGET_LEVELS}, {N_RESTARTS} restarts each]")
    for p in p_values:
        results["standard_qaoa"][p] = {}
        results["xbasis_qaoa"][p] = {}
        print(f"\n  p={p}:")
        for budget in BUDGET_LEVELS:
            r_std, _ = optimize_qaoa(build_standard_qaoa, p, sim, edges, max_cut, n_qubits, budget, SHOTS, N_RESTARTS)
            r_xb, _ = optimize_qaoa(build_xbasis_qaoa, p, sim, edges, max_cut, n_qubits, budget, SHOTS, N_RESTARTS)
            results["standard_qaoa"][p][budget] = float(r_std)
            results["xbasis_qaoa"][p][budget] = float(r_xb)
            diff = r_xb - r_std
            marker = " <-- X-basis WINS" if diff >= 0.05 else (" <-- STD WINS" if diff <= -0.05 else "")
            print(f"    budget={budget:3d}: std={r_std:.3f}, xbasis={r_xb:.3f}, diff={diff:+.3f}{marker}")

    # Pre-registered goal evaluation
    print("\n=== Pre-Registered Goal Evaluation ===")

    # G1: At 1-2 COBYLA iterations: r_xbasis > r_standard by ≥0.05
    g1_pass = False
    g1_data = {}
    for p in p_values:
        for budget in [1, 2]:
            r_std = results["standard_qaoa"][p].get(budget, 0)
            r_xb = results["xbasis_qaoa"][p].get(budget, 0)
            diff = r_xb - r_std
            g1_data[f"p{p}_b{budget}"] = {"r_std": r_std, "r_xb": r_xb, "diff": diff}
            if diff >= 0.05:
                g1_pass = True

    results["goals"]["G1"] = {
        "criterion": "r_xbasis > r_standard by ≥0.05 at budget=1 or budget=2 (any p)",
        "data": g1_data,
        "result": "PASS" if g1_pass else "FAIL"
    }
    print(f"G1 (low-budget X-basis advantage): {'PASS' if g1_pass else 'FAIL'}")
    for k, v in g1_data.items():
        print(f"  {k}: std={v['r_std']:.3f}, xbasis={v['r_xb']:.3f}, diff={v['diff']:+.3f}")

    # G2: Crossover exists — budget N* where standard overtakes X-basis
    g2_pass = False
    crossover_data = {}
    for p in p_values:
        found_crossover = None
        for budget in BUDGET_LEVELS:
            r_std = results["standard_qaoa"][p].get(budget, 0)
            r_xb = results["xbasis_qaoa"][p].get(budget, 0)
            if r_std > r_xb + 0.05 and budget >= 10:
                found_crossover = budget
                g2_pass = True
                break
        crossover_data[f"p{p}"] = found_crossover
    results["goals"]["G2"] = {
        "criterion": "Standard QAOA overtakes X-basis at some budget N* ≥ 10 (confirming compensation exists)",
        "crossover_budgets": crossover_data,
        "result": "PASS" if g2_pass else "FAIL"
    }
    print(f"G2 (crossover exists): {'PASS' if g2_pass else 'FAIL'} | crossovers: {crossover_data}")

    # G3: Entropy advantage survives across all budget levels (budget-independent)
    g3_results = {}
    g3_pass = True
    for p in p_values:
        e_std = results["entropy_standard"].get(p, 1)
        e_xb = results["entropy_xbasis"].get(p, 1)
        g3_results[f"p{p}"] = {"e_std": e_std, "e_xb": e_xb, "xbasis_lower": e_xb < e_std}
        if e_xb >= e_std:
            g3_pass = False
    results["goals"]["G3"] = {
        "criterion": "X-basis entropy < Standard entropy at all p-levels (replication of Exp38 G3)",
        "data": g3_results,
        "result": "PASS" if g3_pass else "FAIL"
    }
    print(f"G3 (entropy advantage survives): {'PASS' if g3_pass else 'FAIL'}")
    for k, v in g3_results.items():
        print(f"  {k}: std_entropy={v['e_std']:.3f}, xbasis_entropy={v['e_xb']:.3f}")

    # G4: Performance gap narrows monotonically as budget increases (for at least one p)
    g4_pass = False
    g4_data = {}
    for p in p_values:
        diffs = [results["xbasis_qaoa"][p].get(b, 0) - results["standard_qaoa"][p].get(b, 0)
                 for b in BUDGET_LEVELS]
        # Check if generally decreasing (allow 1 non-monotone step)
        violations = sum(1 for i in range(len(diffs)-1) if diffs[i+1] > diffs[i] + 0.02)
        monotone = violations <= 1
        g4_data[f"p{p}"] = {"diffs": [round(d,3) for d in diffs], "monotone": monotone}
        if monotone:
            g4_pass = True
    results["goals"]["G4"] = {
        "criterion": "X-basis advantage (xbasis-standard diff) narrows monotonically as budget increases (≤1 violation)",
        "data": g4_data,
        "result": "PASS" if g4_pass else "FAIL"
    }
    print(f"G4 (monotone gap narrowing): {'PASS' if g4_pass else 'FAIL'}")
    for k, v in g4_data.items():
        print(f"  {k}: diffs={v['diffs']}, monotone={v['monotone']}")

    # Verdict
    goals_passed = sum(1 for g in ["G1","G2","G3","G4"] if results["goals"][g]["result"] == "PASS")
    hypothesis_supported = g1_pass
    results["verdict"] = {
        "goals_passed": f"{goals_passed}/4",
        "primary_hypothesis_G1": "SUPPORTED" if hypothesis_supported else "NOT SUPPORTED",
        "conclusion": (
            "X-basis QAOA advantage manifests at low optimization budget — "
            "commutation smooths parameter landscape, fewer iterations needed"
            if hypothesis_supported else
            "X-basis structural advantage does NOT translate to low-budget performance — "
            "commutation and optimization landscape are decoupled"
        )
    }

    print(f"\nVERDICT: {goals_passed}/4 goals passed")
    print(f"Primary hypothesis (G1): {results['verdict']['primary_hypothesis_G1']}")
    print(f"Conclusion: {results['verdict']['conclusion']}")

    # Save results
    suffix = "4node" if problem == "4node" else "8node"
    out_path = f"/droid/repos/quantum/experiments/39-budget-sweep-results-{suffix}.json"
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {out_path}")

    return results


if __name__ == "__main__":
    np.random.seed(39)
    problem = sys.argv[1] if len(sys.argv) > 1 else "4node"
    main(problem=problem)
