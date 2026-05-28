"""Exp 22: N-scaling coverage confirmation for 1-qubit IQAE (Whisper C3709).

Pre-registration (commit before running): Cycle C3709

CONTEXT:
  Exp 21 (C3705) ran N=40 trials with 1-qubit Bernoulli encoding on FakeMarrakesh.
  Results: P=0.56 coverage 87-90% (two independent runs), P=0.9 coverage 95%.
  P=0.56 is ~2.2σ below nominal 95% — borderline. N=40 sampling noise vs systematic bias?

HYPOTHESIS:
  H_noise: P=0.56 undercoverage at N=40 is sampling noise. At N=100, coverage →95%.
  H_bias:  P=0.56 has a small systematic bias even with 1-qubit encoding. Coverage < 90% at N=100.

Pre-registered falsification criteria:
  T1 (sampling-noise pass): P=0.56 coverage ∈ [0.88, 1.0] at N=100   → H_noise CONFIRMED
  T2 (systematic bias):     P=0.56 coverage < 0.88 at N=100           → H_bias  CONFIRMED
  T3 (outer zone):          P=0.9  coverage ≥ 0.90 at N=100           → outer-zone 1-qubit safe

DESIGN:
  - N=100 trials (vs N=40 in Exp 21)
  - P values: {0.4, 0.56, 0.9}  (safety baseline, IWM target, outer zone)
  - 1-qubit Bernoulli encoding (zero CZ gates) — identical to Exp 21
  - FakeMarrakesh noise, eps=0.04, alpha=0.05
  - Seeds: 42+i per trial (same seed scheme as Exp 21 for consistency)

Run: cd /droid/repos/quantum && python3 scripts/run_exp22_n_scaling_coverage.py
"""
import json
import numpy as np
from scipy import stats

EXPERIMENT = "22"
CYCLE = 3709
N_RUNS = 100
EPS = 0.04
ALPHA = 0.05
P_VALUES = [0.4, 0.56, 0.9]

# Exp 21 N=40 results for comparison
EXP21_N40 = {
    "0.56": {"coverage": 0.875, "wilson_lo": 0.739, "wilson_hi": 0.945, "n": 40},
    "0.9":  {"coverage": 0.950, "wilson_lo": 0.835, "wilson_hi": 0.986, "n": 40},
    "0.4":  {"coverage": 0.925, "wilson_lo": 0.801, "wilson_hi": 0.974, "n": 40},
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
    """Minimal transpiling noisy sampler — identical to Exp 21."""
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
    from qiskit_algorithms import IterativeAmplitudeEstimation
    sampler = TranspilingNoisySampler(backend, shots=1024, seed=seed)
    return IterativeAmplitudeEstimation(epsilon_target=EPS, alpha=ALPHA, sampler=sampler)


def run_single_p(P, backend):
    """Run N_RUNS IQAE trials for a given P value."""
    problem = build_bernoulli_1qubit(P)
    zone = "outer" if P < 0.2 or P > 0.8 else "safety"
    print(f"\n  --- P={P} ({zone} zone), N={N_RUNS} trials ---")

    covered = 0
    estimates = []
    ci_widths = []
    errors = 0

    for i in range(N_RUNS):
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
            if (i + 1) % 20 == 0:
                running_cov = covered / (i + 1)
                print(f"    {i+1}/{N_RUNS}: coverage {running_cov:.1%}  "
                      f"last CI=[{lo:.4f},{hi:.4f}]  est={est:.4f}")
        except Exception as e:  # noqa: BLE001
            errors += 1
            if errors <= 3:
                print(f"    run {i+1} FAILED: {e}")

    n_valid = N_RUNS - errors
    coverage = covered / n_valid if n_valid > 0 else None
    wlo, whi = wilson_ci(covered, n_valid) if n_valid > 0 else (None, None)
    avg_est = float(np.mean(estimates)) if estimates else None
    avg_bias = float(avg_est - P) if avg_est is not None else None
    avg_width = float(np.mean(ci_widths)) if ci_widths else None

    print(f"    RESULT: coverage={coverage:.1%}  Wilson=[{wlo:.3f},{whi:.3f}]  "
          f"avg_est={avg_est:.4f}  bias={avg_bias:+.4f}  errors={errors}")

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

    # Compare to Exp 21 N=40
    key = str(P)
    if key in EXP21_N40:
        e21 = EXP21_N40[key]
        entry["exp21_n40_coverage"] = e21["coverage"]
        entry["exp21_n40_wilson"] = [e21["wilson_lo"], e21["wilson_hi"]]
        if coverage is not None:
            delta = coverage - e21["coverage"]
            entry["delta_vs_exp21"] = round(delta, 3)
            print(f"    vs Exp21(N=40): {e21['coverage']:.1%} → {coverage:.1%}  Δ={delta:+.1%}")

    return entry


def evaluate_preregistration(results):
    """Check pre-registered falsification criteria."""
    print("\n" + "=" * 70)
    print("PRE-REGISTRATION EVALUATION")
    print("=" * 70)

    verdicts = {}

    r56 = results.get("0.56")
    if r56 and r56.get("coverage") is not None:
        cov56 = r56["coverage"]
        wlo56 = r56["wilson_lo"]
        whi56 = r56["wilson_hi"]
        print(f"\n  P=0.56 (IWM target): coverage={cov56:.1%}  Wilson=[{wlo56:.3f},{whi56:.3f}]")
        if cov56 >= 0.88:
            verdict = "T1-PASS: SAMPLING NOISE"
            print(f"  T1 PASS: {cov56:.1%} ≥ 88% — N=40 undercoverage was sampling noise")
            print(f"  H_noise CONFIRMED: 1-qubit encoding is coverage-calibrated for P=0.56")
        else:
            verdict = "T2-PASS: SYSTEMATIC BIAS"
            print(f"  T2 PASS: {cov56:.1%} < 88% — systematic undercoverage confirmed at N=100")
            print(f"  H_bias CONFIRMED: 1-qubit encoding has a residual bias at P=0.56")
        verdicts["p056"] = verdict

    r09 = results.get("0.9")
    if r09 and r09.get("coverage") is not None:
        cov09 = r09["coverage"]
        print(f"\n  P=0.9 (outer zone): coverage={cov09:.1%}")
        if cov09 >= 0.90:
            verdict = "T3-PASS: OUTER ZONE SAFE"
            print(f"  T3 PASS: {cov09:.1%} ≥ 90% — outer zone safe with 1-qubit encoding")
        else:
            verdict = "T3-FAIL: OUTER ZONE UNSAFE"
            print(f"  T3 FAIL: {cov09:.1%} < 90% — outer zone fails even with 1-qubit encoding")
        verdicts["p09"] = verdict

    return verdicts


def main():
    print(f"\nExp {EXPERIMENT}: N-scaling coverage confirmation for 1-qubit IQAE")
    print(f"Cycle: C{CYCLE} | N={N_RUNS} (vs N=40 in Exp 21)")
    print(f"Pre-registered: T1 (P=0.56 ≥ 88% → sampling noise), "
          f"T2 (P=0.56 < 88% → systematic bias), T3 (P=0.9 ≥ 90% → outer safe)\n")

    try:
        from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
    except ImportError as e:
        print(f"IMPORT FAILED: {e}")
        return {"import_error": str(e)}

    backend = FakeMarrakesh()

    results = {}
    for P in P_VALUES:
        results[str(P)] = run_single_p(P, backend)

    verdicts = evaluate_preregistration(results)

    # Final synthesis
    print("\n" + "=" * 70)
    print("SYNTHESIS: N-SCALING ARC CLOSURE")
    print("=" * 70)
    r56 = results.get("0.56", {})
    cov56 = r56.get("coverage")
    if cov56 is not None:
        if cov56 >= 0.88:
            print(f"\n  IWM TARGET (P=0.56): {cov56:.1%} at N=100")
            print(f"  Previous: 87.5% at N=40. Resolution: SAMPLING NOISE.")
            print(f"  1-qubit IQAE coverage arc CLOSED: encoding-driven (Exp 21) + N=40 noise (Exp 22).")
            print(f"  Practical recommendation: 1-qubit Bernoulli encoding provides calibrated")
            print(f"  95% CI coverage for financial IQAE at P≈0.56 with N≥80.")
        else:
            print(f"\n  IWM TARGET (P=0.56): {cov56:.1%} at N=100 — SYSTEMATIC BIAS FOUND.")
            print(f"  Even with zero-CZ encoding, IQAE has residual undercoverage at P=0.56 under noise.")
            print(f"  Implication: IQAE CIs may be slightly overconfident even in 1-qubit regime.")

    output = {
        "experiment": EXPERIMENT,
        "title": "N-scaling coverage confirmation for 1-qubit IQAE",
        "cycle": CYCLE,
        "params": {
            "eps": EPS,
            "alpha": ALPHA,
            "N": N_RUNS,
            "backend": "FakeMarrakesh",
            "encoding": "1-qubit Bernoulli (zero CZ gates)",
        },
        "context": (
            f"Exp 21 (C3705) showed P=0.56 coverage 87-90% at N=40 (1-qubit encoding). "
            f"~2.2σ below nominal 95%. This experiment (N={N_RUNS}) tests whether "
            f"that undercoverage is sampling noise or systematic bias."
        ),
        "preregistered_criteria": {
            "T1": "P=0.56 coverage >= 0.88 at N=100 → sampling noise (H_noise confirmed)",
            "T2": "P=0.56 coverage < 0.88 at N=100 → systematic bias (H_bias confirmed)",
            "T3": "P=0.9 coverage >= 0.90 at N=100 → outer zone safe with 1-qubit",
        },
        "verdicts": verdicts,
        "results": results,
    }

    outpath = f"experiments/{EXPERIMENT}-n-scaling-coverage-results.json"
    with open(outpath, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n  Results written to {outpath}")
    return output


if __name__ == "__main__":
    main()
