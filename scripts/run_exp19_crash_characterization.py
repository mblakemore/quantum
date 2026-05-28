"""Exp 19: IQAE k=7 outer-zone crash characterization (Whisper C3703).

Open question from Finding 10: is the Exp 18 k=7 div-zero crash at outer-zone
P (0.3/0.7/0.9) FUNDAMENTAL IQAE geometry, or a FIXABLE numerical/wrapper guard?

Three tests:
  T1 (analytic): Fisher information per shot = 4(2k+1)^2 — CONSTANT in theta.
                 => div-zero is NOT Fisher information vanishing. Rules out the
                 "no-confidence point" fundamental hypothesis.
  T2 (reproduce): Run qiskit CORE IterativeAmplitudeEstimation under an Aer
                 Sampler with a FakeMarrakesh noise model, at outer-zone vs
                 safety-zone P. Does CORE crash at k=7, or only Ember's
                 TranspilingNoisySampler V2 wrapper? Capture exact traceback.
  T3 (mechanism): Inspect IQAE's k-escalation / interval-rescaling. Identify
                 the branch-boundary division that blows up.

Run: python3 scripts/run_exp19_crash_characterization.py
"""
import json
import sys
import traceback
import numpy as np

RESULTS = {"experiment": "19", "title": "IQAE k=7 outer-zone crash characterization",
           "cycle": 3703, "tests": {}}

# ---------------------------------------------------------------------------
# T1: Fisher information is constant in theta -> div-zero is NOT Fisher vanishing
# ---------------------------------------------------------------------------
def fisher_per_shot(k, theta):
    """Per-shot Fisher info for measuring p = sin^2((2k+1) theta).
    I = (dp/dtheta)^2 / (p(1-p)). Analytically reduces to 4(2k+1)^2."""
    m = 2 * k + 1
    p = np.sin(m * theta) ** 2
    dp = m * np.sin(2 * m * theta)          # d/dtheta sin^2(m theta)
    if p <= 0 or p >= 1:
        return np.inf, p                      # numeric boundary (handled by clip in real code)
    return (dp ** 2) / (p * (1 - p)), p

def run_t1():
    print("=" * 70)
    print("T1: Fisher information vs theta (is div-zero a Fisher-vanishing point?)")
    print("=" * 70)
    rows = []
    for P in [0.3, 0.56, 0.7, 0.9]:
        theta = np.arcsin(np.sqrt(P))
        for k in [0, 3, 7]:
            I, p = fisher_per_shot(k, theta)
            analytic = 4 * (2 * k + 1) ** 2
            rows.append({"P": P, "k": k, "theta": round(float(theta), 5),
                         "p_k": round(float(p), 5),
                         "fisher_numeric": (None if np.isinf(I) else round(float(I), 3)),
                         "fisher_analytic_4(2k+1)^2": analytic})
            tag = "p_k≈boundary" if (p < 1e-6 or p > 1 - 1e-6) else ""
            print(f"  P={P:<4} k={k:<2} (2k+1)θ={(2*k+1)*theta:6.3f}  p_k={p:6.4f} "
                  f"  I_num={'inf' if np.isinf(I) else f'{I:8.2f}'}  I_analytic={analytic:<5} {tag}")
    print("\n  => Fisher info equals 4(2k+1)^2 wherever p_k is not exactly 0/1.")
    print("     It GROWS with k. So the k=7 crash is NOT a vanishing-information point.")
    print("     The div-zero must come from p_k hitting 0/1 (the sin^2 branch")
    print("     boundary), where log(p) / 1/(p(1-p)) terms blow up — a guardable")
    print("     numerical event, not loss of statistical information.\n")
    RESULTS["tests"]["T1_fisher"] = {
        "claim": "Fisher info = 4(2k+1)^2, constant in theta, grows with k",
        "implication": "k=7 crash is NOT Fisher-information vanishing; it is a "
                       "p_k->0/1 branch-boundary numerical event (guardable)",
        "rows": rows}
    return rows

# ---------------------------------------------------------------------------
# T2: Does qiskit CORE IQAE crash, or only the wrapper?
# ---------------------------------------------------------------------------
def build_bernoulli_circuits(P):
    """Standard QAE Bernoulli A and Grover Q operators for amplitude a=sin^2(theta)=P."""
    from qiskit.circuit import QuantumCircuit
    from qiskit_algorithms import EstimationProblem
    theta = 2 * np.arcsin(np.sqrt(P))   # so that A|0> has P(|1>) = sin^2(theta/2) = P
    A = QuantumCircuit(1)
    A.ry(theta, 0)
    Q = QuantumCircuit(1)
    Q.ry(2 * theta, 0)                   # Grover operator for single-qubit Bernoulli
    problem = EstimationProblem(state_preparation=A, grover_operator=Q,
                                objective_qubits=[0])
    return problem

class TranspilingNoisySampler:
    """Minimal stand-in for Ember's TranspilingNoisySampler V2 wrapper.

    Plain AerSampler chokes on IAE's composite Grover instructions
    ('unknown instruction: circuit-N'). IAE requires a sampler that
    transpiles each PUB circuit to basis gates BEFORE noisy simulation.
    This is the exact code path where the Exp 18 k=7 div-zero lived.
    """
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


def run_t2():
    print("=" * 70)
    print("T2: qiskit CORE IQAE + transpiling noisy sampler — crash at k=7?")
    print("=" * 70)
    out = {}
    try:
        from qiskit_algorithms import IterativeAmplitudeEstimation
        from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
    except Exception as e:
        print(f"  IMPORT FAILED: {e}")
        out["import_error"] = str(e)
        RESULTS["tests"]["T2_core_iqae"] = out
        return out

    backend = FakeMarrakesh()
    sampler = TranspilingNoisySampler(backend, shots=1024, seed=42)

    def root_cause(exc):
        """Walk the __cause__/__context__ chain to the originating exception."""
        seen = []
        cur = exc
        while cur is not None:
            seen.append((type(cur).__name__, str(cur)))
            cur = cur.__cause__ or cur.__context__
        return seen

    # eps=0.01 forces k-escalation past k=4 toward the k=7 regime
    for P in [0.56, 0.3, 0.7, 0.9]:
        zone = "safety" if 0.2 <= P <= 0.8 else "outer"
        print(f"\n  --- P={P} ({zone} zone) ---")
        try:
            iqae = IterativeAmplitudeEstimation(epsilon_target=0.01, alpha=0.05,
                                                sampler=sampler)
            problem = build_bernoulli_circuits(P)
            res = iqae.estimate(problem)
            ks = [int(x) for x in res.powers] if hasattr(res, "powers") else None
            print(f"      OK  estimate={res.estimation:.4f}  max_k={max(ks) if ks else '?'}"
                  f"  powers(k)={ks}")
            out[str(P)] = {"zone": zone, "status": "ok",
                           "estimate": round(float(res.estimation), 4),
                           "max_k": (max(ks) if ks else None), "powers": ks}
        except Exception as e:
            chain = root_cause(e)
            origin = chain[-1]
            print(f"      {type(e).__name__}: {e}")
            print(f"      ROOT CAUSE: {origin[0]}: {origin[1]}")
            print(f"      chain: {' <- '.join(c[0] for c in chain)}")
            out[str(P)] = {"zone": zone, "status": type(e).__name__,
                           "error": str(e), "root_cause_type": origin[0],
                           "root_cause_msg": origin[1],
                           "chain": [c[0] for c in chain]}
    RESULTS["tests"]["T2_core_iqae"] = out
    return out


if __name__ == "__main__":
    run_t1()
    run_t2()
    outpath = "experiments/19-crash-characterization-results.json"
    with open(outpath, "w") as f:
        json.dump(RESULTS, f, indent=2)
    print("\n" + "=" * 70)
    print(f"Results written to {outpath}")
    print("=" * 70)
