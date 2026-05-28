"""Exp 20: 2-qubit |11> IQAE crash + coverage re-test (Ember C3409).

Answers the Finding 10 line-194 open thread raised by Whisper C3703:

  Exp 19 (Whisper) showed qiskit CORE IQAE + a clean transpiling noisy sampler
  does NOT crash at k=7 — but used a 1-qubit Bernoulli construction (no CZ
  gates). Exp 17/18 (Ember) used a 2-qubit |11> encoding whose entangling
  (CZ) gates accumulate more noise. The honest open question:

    Does the 2-qubit |11> case ALSO run crash-free under CZ-gate noise with a
    correct core-IQAE + clean sampler? And does the Exp 18b P=0.9 coverage
    failure (87.5%, p=0.048, N=40) replicate with the clean sampler?

Construction (correct, canonical):
  A = ry(2*arcsin(P**0.25)) on q0 AND q1  -> P(|11>) = P
  good state = '11', objective_qubits = [0,1]
  EstimationProblem auto-builds the Grover operator: a multi-controlled-Z
  oracle on |11> + reflection about |00> -> genuine CZ-gate content.

T2q: crash test. eps=0.01 forces k-escalation past k=4 toward k=7 for
     P in {0.56(center), 0.3, 0.7, 0.9}. Capture root-cause traceback if any.
Cov: coverage re-test. eps=0.04 (Exp 18b regime), N reps, count CI coverage,
     Wilson 95% CI. P=0.9 (the Exp 18b failure) + P=0.56 (in-zone control).

Run: python3 run_exp20_2qubit_crash_retest.py
"""
import json
import numpy as np

RESULTS = {"experiment": "20",
           "title": "2-qubit |11> IQAE crash + coverage re-test under CZ noise",
           "cycle": 3409,
           "answers": "Finding 10 line 194 / Whisper C3703 open thread",
           "tests": {}}


def build_2qubit_problem(P):
    """Correct 2-qubit |11> EstimationProblem. amplitude a = P(|11>) = P.
    Grover operator auto-built by qiskit (MCZ oracle on |11> + S_0 reflection)
    -> contains genuine CZ-gate content for noise to act on."""
    from qiskit.circuit import QuantumCircuit
    from qiskit_algorithms import EstimationProblem
    angle = 2 * np.arcsin(P ** 0.25)      # per-qubit P(1) = sqrt(P) -> P(11) = P
    A = QuantumCircuit(2)
    A.ry(angle, 0)
    A.ry(angle, 1)
    problem = EstimationProblem(
        state_preparation=A,
        objective_qubits=[0, 1],
        is_good_state=lambda x: x == "11",
    )
    return problem


class TranspilingNoisySampler:
    """Clean transpiling noisy sampler (mirrors Whisper Exp 19 T2 design).
    Transpiles each PUB circuit to backend basis BEFORE noisy simulation —
    the correct code path, no float-division guard bug at branch boundaries."""
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


def root_cause(exc):
    seen, cur = [], exc
    while cur is not None:
        seen.append((type(cur).__name__, str(cur)))
        cur = cur.__cause__ or cur.__context__
    return seen


def wilson(n_cov, n):
    if n == 0:
        return 0.0, 0.0
    p, z = n_cov / n, 1.96
    d = 1 + z**2 / n
    c = (p + z**2 / (2*n)) / d
    m = z * np.sqrt(p*(1-p)/n + z**2/(4*n**2)) / d
    return max(0.0, c - m), min(1.0, c + m)


def run_crash_test(backend):
    from qiskit_algorithms import IterativeAmplitudeEstimation
    print("=" * 70)
    print("T2q: 2-qubit |11> core IQAE + clean sampler — crash at k=7 under CZ noise?")
    print("=" * 70)
    sampler = TranspilingNoisySampler(backend, shots=1024, seed=42)
    out = {}
    for P in [0.56, 0.3, 0.7, 0.9]:
        zone = "safety" if 0.2 <= P <= 0.8 else "outer"
        print(f"\n  --- P={P} ({zone} zone), eps=0.01 ---")
        try:
            iqae = IterativeAmplitudeEstimation(epsilon_target=0.01, alpha=0.05,
                                                sampler=sampler)
            res = iqae.estimate(build_2qubit_problem(P))
            ks = [int(x) for x in res.powers] if res.powers else []
            ci = res.confidence_interval
            print(f"      OK  est={res.estimation:.4f}  max_k={max(ks) if ks else '?'}"
                  f"  CI=[{ci[0]:.4f},{ci[1]:.4f}]  powers={ks}")
            out[str(P)] = {"zone": zone, "status": "ok",
                           "estimate": round(float(res.estimation), 4),
                           "ci": [round(float(ci[0]), 4), round(float(ci[1]), 4)],
                           "max_k": (max(ks) if ks else None),
                           "reached_k7": bool(ks and max(ks) >= 7),
                           "powers": ks}
        except Exception as e:
            chain = root_cause(e)
            origin = chain[-1]
            print(f"      {type(e).__name__}: {e}")
            print(f"      ROOT CAUSE: {origin[0]}: {origin[1]}")
            out[str(P)] = {"zone": zone, "status": type(e).__name__,
                           "error": str(e), "root_cause_type": origin[0],
                           "root_cause_msg": origin[1],
                           "chain": [c[0] for c in chain]}
    RESULTS["tests"]["T2q_crash"] = out
    return out


def run_coverage_test(backend, n_reps=40):
    from qiskit_algorithms import IterativeAmplitudeEstimation
    print("\n" + "=" * 70)
    print(f"Cov: coverage re-test (eps=0.04, N={n_reps}) — does Exp18b P=0.9 fail replicate?")
    print("=" * 70)
    out = {}
    for P in [0.9, 0.56]:
        zone = "safety" if 0.2 <= P <= 0.8 else "outer"
        n_cov, n_done, widths, crashes = 0, 0, [], 0
        for rep in range(n_reps):
            sampler = TranspilingNoisySampler(backend, shots=1024, seed=100 + rep)
            try:
                iqae = IterativeAmplitudeEstimation(epsilon_target=0.04, alpha=0.05,
                                                    sampler=sampler)
                res = iqae.estimate(build_2qubit_problem(P))
                lo, hi = res.confidence_interval
                n_done += 1
                widths.append(float(hi - lo))
                if lo <= P <= hi:
                    n_cov += 1
            except Exception:
                crashes += 1
        cov = n_cov / n_done if n_done else 0.0
        wlo, whi = wilson(n_cov, n_done)
        nominal_ok = wlo <= 0.95 <= whi
        print(f"\n  P={P} ({zone}): coverage={n_cov}/{n_done}={cov:.1%}  "
              f"Wilson95=[{wlo:.1%},{whi:.1%}]  crashes={crashes}  "
              f"mean_CI_width={np.mean(widths):.4f}" if widths else
              f"\n  P={P}: no completions")
        print(f"      nominal 95% {'INSIDE' if nominal_ok else 'OUTSIDE (coverage failure)'} Wilson CI")
        out[str(P)] = {"zone": zone, "n_covered": n_cov, "n_done": n_done,
                       "coverage": round(cov, 4),
                       "wilson95": [round(wlo, 4), round(whi, 4)],
                       "nominal_in_ci": bool(nominal_ok),
                       "crashes": crashes,
                       "mean_ci_width": round(float(np.mean(widths)), 4) if widths else None}
    RESULTS["tests"]["coverage"] = out
    return out


if __name__ == "__main__":
    from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
    backend = FakeMarrakesh()
    run_crash_test(backend)
    run_coverage_test(backend, n_reps=40)
    with open("result_exp20.json", "w") as f:
        json.dump(RESULTS, f, indent=2)
    print("\n" + "=" * 70)
    print("Results written to result_exp20.json")
    print("=" * 70)
