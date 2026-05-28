"""Exp 21: 1-qubit IQAE coverage sweep — encoding vs intrinsic undercoverage (Whisper C3705).

Co-run with Ember C3409 Exp 20 (2-qubit |11> re-test).

Ember Exp 20 found at eps=0.04, N=40, FakeMarrakesh:
  - P=0.9  coverage: 42.5% (Wilson [28.5, 57.8]) — FAR below 95% nominal
  - P=0.56 coverage: 62.5% (Wilson [47.0, 75.8]) — also well below 95%
  - Mechanism: noise biases estimate; CIs come out tight (width 0.004-0.011)
    → overconfident, mis-centered intervals
  - KEY CAVEAT: Ember's 2-qubit |11> construction amplifies CZ gate count.
    Is the coverage failure encoding-driven (CZ noise) or intrinsic IQAE?

This experiment:
  - Same params: eps=0.04, alpha=0.05, N=40, FakeMarrakesh noise
  - 1-qubit Bernoulli (ZERO CZ gates — controls for encoding noise)
  - P sweep: {0.1, 0.3, 0.4, 0.56, 0.7, 0.9}
  - Measure: CI coverage rate + interval width + estimate bias

Hypothesis:
  - If P=0.56 shows GOOD coverage (>=90%) in 1-qubit: undercoverage is encoding-driven
  - If P=0.56 shows BAD coverage also in 1-qubit: undercoverage is intrinsic to IQAE/noise

Run: cd /droid/repos/quantum && python3 scripts/run_exp21_1qubit_coverage_sweep.py
"""
import json
import numpy as np
from scipy import stats

EXPERIMENT = "21"
CYCLE = 3705
N_RUNS = 40
EPS = 0.04
ALPHA = 0.05
P_VALUES = [0.1, 0.3, 0.4, 0.56, 0.7, 0.9]

# Ember Exp 20 results for comparison
EMBER_EXP20 = {
    "0.56": {"coverage": 0.625, "wilson_lo": 0.470, "wilson_hi": 0.758, "n": 40},
    "0.9":  {"coverage": 0.425, "wilson_lo": 0.285, "wilson_hi": 0.578, "n": 40},
}


def wilson_ci(k, n, alpha=0.05):
    """Wilson score interval for binomial proportion k/n."""
    if n == 0:
        return (0.0, 1.0)
    z = stats.norm.ppf(1 - alpha / 2)
    p_hat = k / n
    denom = 1 + z**2 / n
    centre = (p_hat + z**2 / (2 * n)) / denom
    half = z * np.sqrt(p_hat * (1 - p_hat) / n + z**2 / (4 * n**2)) / denom
    return (max(0, centre - half), min(1, centre + half))


class TranspilingNoisySampler:
    """Minimal transpiling noisy sampler — identical to Exp 19 T2."""
    def __init__(self, backend, shots=1024, seed=42):
        from qiskit_aer.primitives import SamplerV2 as AerSampler
        from qiskit_aer.noise import NoiseModel
        self._backend = backend
        self._nm = NoiseModel.from_backend(backend)
        self._inner = AerSampler(options={
            "backend_options": {"noise_model": self._nm},
            "run_options": {"shots": shots, "seed": seed}})

    def run(self, pubs):
        from qiskit import transpile
        new_pubs = []
        for pub in pubs:
            circ = pub[0]
            tcirc = transpile(circ, backend=self._backend, optimization_level=1)
            new_pubs.append((tcirc,) + tuple(pub[1:]))
        return self._inner.run(new_pubs)


def build_bernoulli_1qubit(P):
    """Standard 1-qubit Bernoulli EstimationProblem (zero CZ gates)."""
    from qiskit.circuit import QuantumCircuit
    from qiskit_algorithms import EstimationProblem
    theta = 2 * np.arcsin(np.sqrt(P))
    A = QuantumCircuit(1)
    A.ry(theta, 0)
    Q = QuantumCircuit(1)
    Q.ry(2 * theta, 0)
    return EstimationProblem(state_preparation=A, grover_operator=Q, objective_qubits=[0])


def make_iqae(backend, seed):
    """Create a fresh IQAE instance with a unique seed for each run."""
    from qiskit_algorithms import IterativeAmplitudeEstimation
    sampler = TranspilingNoisySampler(backend, shots=1024, seed=seed)
    return IterativeAmplitudeEstimation(epsilon_target=EPS, alpha=ALPHA, sampler=sampler)


def run_coverage_sweep():
    print("=" * 70)
    print(f"Exp {EXPERIMENT}: 1-qubit IQAE coverage sweep")
    print(f"  eps={EPS}, alpha={ALPHA}, N={N_RUNS}, FakeMarrakesh")
    print(f"  P values: {P_VALUES}")
    print("=" * 70)

    try:
        from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
    except ImportError as e:
        print(f"IMPORT FAILED: {e}")
        return {"import_error": str(e)}

    backend = FakeMarrakesh()

    results = {}
    for P in P_VALUES:
        problem = build_bernoulli_1qubit(P)
        zone = "outer" if P < 0.2 or P > 0.8 else "safety"
        print(f"\n  --- P={P} ({zone} zone), running {N_RUNS} trials ---")

        covered = 0
        estimates = []
        ci_widths = []
        errors = 0

        for i in range(N_RUNS):
            # Fresh sampler + IQAE per run ensures independent noise seeds
            iqae = make_iqae(backend, seed=42 + i)
            try:
                res = iqae.estimate(problem)
                lo, hi = res.confidence_interval[0], res.confidence_interval[1]
                est = float(res.estimation)
                width = hi - lo
                hit = (lo <= P <= hi)
                if hit:
                    covered += 1
                estimates.append(est)
                ci_widths.append(width)
                if (i + 1) % 10 == 0:
                    running_cov = covered / (i + 1)
                    print(f"    {i+1}/{N_RUNS}: coverage so far {running_cov:.1%}  "
                          f"last CI=[{lo:.4f},{hi:.4f}] est={est:.4f}")
            except Exception as e:  # noqa: BLE001
                errors += 1
                print(f"    run {i+1} FAILED: {e}")

        n_valid = N_RUNS - errors
        coverage = covered / n_valid if n_valid > 0 else None
        wlo, whi = wilson_ci(covered, n_valid) if n_valid > 0 else (None, None)
        avg_est = float(np.mean(estimates)) if estimates else None
        avg_bias = float(avg_est - P) if avg_est is not None else None
        avg_width = float(np.mean(ci_widths)) if ci_widths else None

        print(f"    RESULT: coverage={coverage:.1%} "
              f"Wilson=[{wlo:.3f},{whi:.3f}]  "
              f"avg_est={avg_est:.4f}  bias={avg_bias:+.4f}  "
              f"avg_width={avg_width:.4f}  errors={errors}")

        entry = {
            "P": P,
            "zone": zone,
            "n_valid": n_valid,
            "n_covered": covered,
            "coverage": round(coverage, 4) if coverage is not None else None,
            "wilson_lo": round(wlo, 3) if wlo is not None else None,
            "wilson_hi": round(whi, 3) if whi is not None else None,
            "avg_estimate": round(avg_est, 4) if avg_est is not None else None,
            "avg_bias": round(avg_bias, 4) if avg_bias is not None else None,
            "avg_ci_width": round(avg_width, 4) if avg_width is not None else None,
            "errors": errors,
        }

        # Compare to Ember Exp 20 if available
        key = str(P)
        if key in EMBER_EXP20:
            e20 = EMBER_EXP20[key]
            entry["ember_exp20_coverage"] = e20["coverage"]
            entry["ember_exp20_wilson"] = [e20["wilson_lo"], e20["wilson_hi"]]
            if coverage is not None:
                delta = coverage - e20["coverage"]
                entry["delta_vs_ember"] = round(delta, 3)
                verdict = ("ENCODING-DRIVEN" if coverage > e20["coverage"] + 0.15
                           else "INTRINSIC" if coverage < e20["coverage"] + 0.05
                           else "MIXED/UNCERTAIN")
                entry["encoding_vs_intrinsic"] = verdict
                print(f"    vs Ember Exp20: +{delta:+.1%}  verdict={verdict}")

        results[key] = entry

    return results


def main():
    print(f"\nExp {EXPERIMENT}: 1-qubit IQAE coverage sweep — encoding vs intrinsic")
    print(f"Cycle: C{CYCLE}  |  Co-run with Ember C3409 Exp 20\n")

    coverage_results = run_coverage_sweep()

    # Synthesize
    print("\n" + "=" * 70)
    print("SYNTHESIS")
    print("=" * 70)

    # Key question: is P=0.56 (IWM target) coverage good in 1-qubit?
    r56 = coverage_results.get("0.56", {})
    if r56 and r56.get("coverage") is not None:
        cov56 = r56["coverage"]
        verdict56 = r56.get("encoding_vs_intrinsic", "unknown")
        print(f"\n  IWM TARGET (P=0.56): {cov56:.1%} coverage (1-qubit)")
        print(f"  Ember Exp20 (2-qubit): {r56.get('ember_exp20_coverage', '?'):.1%}")
        print(f"  Verdict: {verdict56}")
        if cov56 >= 0.85:
            print("  => Coverage failure IS encoding-driven. 1-qubit is safe. "
                  "IWM 'immune' claim HOLDS for 1-qubit encoding.")
        elif cov56 >= 0.70:
            print("  => Mixed result. Partial encoding contribution. Further analysis needed.")
        else:
            print("  => Coverage failure is INTRINSIC to IQAE under noise. "
                  "IWM 'immune' claim requires qualification regardless of encoding.")

    output = {
        "experiment": EXPERIMENT,
        "title": "1-qubit IQAE coverage sweep — encoding vs intrinsic undercoverage",
        "cycle": CYCLE,
        "params": {"eps": EPS, "alpha": ALPHA, "N": N_RUNS,
                   "backend": "FakeMarrakesh", "encoding": "1-qubit Bernoulli (zero CZ gates)"},
        "context": ("Ember Exp 20 found 62.5% coverage at P=0.56 (2-qubit), "
                    "42.5% at P=0.9. This sweep isolates encoding vs intrinsic."),
        "results": coverage_results,
    }

    outpath = f"experiments/{EXPERIMENT}-1qubit-coverage-sweep-results.json"
    with open(outpath, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n  Results written to {outpath}")
    return output


if __name__ == "__main__":
    main()
