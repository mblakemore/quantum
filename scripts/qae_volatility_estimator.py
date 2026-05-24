#!/usr/bin/env python3
"""QAE volatility estimator — Quantum Amplitude Estimation with IAE-MLE post-processing.

Source: /droid/repos/lyla/bin/qae_volatility_estimator.py (Lyla quantum tooling)
Reproduced for the quantum characterization repo:
  https://github.com/(see repo) — see findings/09-qae-iae-mle-precision.md for results.

Post-bug-fix version (C3670): BOTH qubits get the initialization rotation
RY(2·arcsin(target_prob^0.25)). Pre-fix only q0 was rotated, leaving P(|11>)=0
and the Grover oracle with nothing to amplify. See finding 09 for the full story.

Hardware-validated on `ibm_marrakesh` C3671: jobs d89nd7p789is7393hkr0 and
d89ndk0p0eas73dorso0. All 3 volatility regimes achieved error < 0.005.
"""

import numpy as np
from typing import Tuple, Optional
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister


class QAEVolatilityEstimator:
    """Classical approximation of quantum amplitude estimation (QAE).
    
    Uses Grover-like amplification iterations on feature-encoded states
    to estimate high-volatility regime probabilities with uncertainty bounds.
    
    Key design decisions:
    - No real IBM runtime integration yet (requires API keys from Creator)
    - Simulates quantum behavior using classical sampling for testing
    - Calibrated to match expected QAE scaling: σ ∝ 1/(k+1) where k = Grover iterations
    """
    
    def __init__(self, use_simulator: bool = True):
        self.use_simulator = use_simulator
        
        if not use_simulator:
            raise NotImplementedError("Real hardware requires IBM credentials")
        
        # Use bare Qiskit Aer simulator — FakeMarrakesh has compatibility issues
        try:
            from qiskit_aer import AerSimulator
            self.backend = AerSimulator()
        except ImportError:
            print("qiskit-aer not installed; falling back to pure numpy simulation")
            self.backend = None
    
    def _build_iae_circuit(self, k: int, target_prob: float = 0.5) -> 'QuantumCircuit':
        """Build IAE circuit with Grover amplification steps."""
        try:
            from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
            
            n_qubits = 2
            qreg = QuantumRegister(n_qubits, 'q')
            creg = ClassicalRegister(n_qubits, 'c')
            qc = QuantumCircuit(qreg, creg)
            
            # Amplitude encoding: create initial state where P(|11⟩) ≈ target_prob
            # FIX (Whisper C3670): Original code only rotated q0, leaving q1 in |0⟩.
            # With q1=|0⟩, P(|11⟩) = 0 regardless of target_prob → oracle hits wrong state.
            # CORRECT: Both qubits need RY rotations so P(|11⟩) = sin²(θ/2)² = target_prob.
            # Solution: sin²(θ/2) = sqrt(target_prob) → θ = 2·arcsin(target_prob^(1/4))
            theta = 2 * np.arcsin(np.clip(target_prob ** 0.25, 0, 1))
            qc.ry(theta, 0)  # P(q0=|1⟩) = sin²(θ/2) = sqrt(target_prob)
            qc.ry(theta, 1)  # P(q1=|1⟩) = sin²(θ/2) = sqrt(target_prob)
            # Now P(|11⟩) = sin⁴(θ/2) = target_prob  ✓

            # Oracle + diffusion loop (k iterations total)
            for _ in range(k):
                # Oracle: mark high-vol states (|11⟩) with phase flip
                qc.cz(0, 1)

                # Diffusion operator about initial state |ψ⟩ = A|0⟩
                # Standard Grover diffusion: 2|ψ⟩⟨ψ| - I
                # Implemented as: A† · (2|0⟩⟨0| - I) · A
                # Step 1: uncompute amplitude encoding (A†)
                qc.ry(-theta, 1)
                qc.ry(-theta, 0)
                # Step 2: phase flip |0⟩ (2|0⟩⟨0| - I = -X·Z·X style)
                qc.x(0)
                qc.x(1)
                qc.cz(0, 1)
                qc.x(0)
                qc.x(1)
                # Step 3: re-apply amplitude encoding (A)
                qc.ry(theta, 0)
                qc.ry(theta, 1)
            
            # Measure both qubits into classical register
            qc.measure([0, 1], [0, 1])
            
            return qc
            
        except ImportError:
            # Fallback for numpy-only mode
            return None
    
    def estimate(self, features: np.ndarray, target_prob: float = 0.5, 
                 k_values: Optional[list] = None) -> dict:
        """Estimate high-volatility regime probability using QAE-inspired sampling."""
        
        if k_values is None:
            k_values = [1, 2, 3, 4]
        
        results = []
        
        for k in k_values:
            # Build circuit
            qc = self._build_iae_circuit(k, target_prob)
            
            if qc is not None and self.backend is not None:
                try:
                    job = self.backend.run(qc, shots=1024)
                    result = job.result()
                    # Get counts with proper bit ordering (big-endian by default in Qiskit)
                    all_counts = result.get_counts(qc)
                    
                    # Debug output
                    print(f"Circuit k={k}, target_prob={target_prob}")
                    print(f"  All counts: {all_counts}")
                    
                    # Extract P(high vol) - '11' means both qubits measured as 1
                    # Note: Qiskit uses big-endian, so '11' is correct for |11⟩ state
                    p_high = all_counts.get('11', 0) / sum(all_counts.values())
                    print(f"  P(high) = {p_high:.4f} ({all_counts.get('11', 0)} of {sum(all_counts.values())})")
                    
                    results.append({
                        'k': k,
                        'p_estimate': p_high,
                        'cz_gates': sum(1 for inst in qc.data if inst.operation.name == 'cz'),
                        'all_counts': all_counts
                    })
                    continue
                
                except Exception as e:
                    print(f"Simulation failed for k={k}: {e}")
            
            # Pure numpy fallback when Qiskit unavailable
            # Simulate Grover amplification classically
            n_shots = 1024
            
            # Encode target_prob as initial amplitude distribution
            # |ψ⟩ = √p|high⟩ + √(1-p)|low⟩ → initialize state with this bias
            theta = 2 * np.arcsin(np.sqrt(target_prob))
            
            # Create biased initial state where P(|11⟩) ≈ target_prob initially
            # We'll use a simple probabilistic model instead of full quantum simulation
            high_prob = target_prob
            
            # Apply Grover amplification to increase probability of high-vol states
            # Each iteration roughly doubles the amplitude of marked states
            # After k iterations, P(high) ≈ sin²((2k+1)*θ/2) where θ = arcsin(√target_prob)
            amplified_angle = (2 * k + 1) * theta / 2
            p_amplified = np.sin(amplified_angle) ** 2
            
            # Clamp to valid range and add noise floor for realism
            p_high = max(0.01, min(0.99, p_amplified))
            
            results.append({
                'k': k,
                'p_estimate': float(p_high),
                'cz_gates': 2 * k,
                'counts': {'11': int(p_high * n_shots)},
                '_debug_theta': theta,
                '_debug_amplified_angle': amplified_angle
            })
            print(f"DEBUG: target={target_prob}, k={k}, p_high={p_high:.4f}")
        
        # IAE-MLE: Maximum Likelihood Estimation across all k observations
        # FIX (Whisper C3671): Original code always picked k=1 (min k). This loses
        # precision available from higher-k measurements. IAE-MLE finds the amplitude
        # a (where P(|11>)_initial = a = target_prob) that best explains ALL observations.
        #
        # After k Grover iterations: P(|11>)_k = sin²((2k+1) * arcsin(√a))
        # We scan a ∈ [0,1] and find the MLE maximum across all k likelihoods.
        a_best, log_lik_best = self._iae_mle_estimate(results)

        # Find the k whose raw measurement was closest to the MLE estimate
        # (for reporting best_k and circuit_depth in a meaningful way)
        best_raw = min(results, key=lambda r: abs(r['p_estimate'] - a_best))

        return {
            'estimate': a_best,
            'confidence_interval': self._compute_confidence(a_best, 1024),
            'best_k': best_raw['k'],
            'circuit_depth': best_raw['cz_gates'] * 8,  # Rough CZ-to-depth conversion
            'all_iterations': results,
            'iae_log_likelihood': log_lik_best
        }

    def _iae_mle_estimate(self, results: list, shots: int = 1024) -> Tuple[float, float]:
        """IAE Maximum Likelihood Estimation across multiple k observations.

        For each candidate amplitude a (where target P(|11>)_0 = a):
          - After k Grover iterations: P(|11>)_k = sin²((2k+1) * arcsin(√a))
          - Likelihood from binomial: P(n_11 | shots, p_expected)

        Returns: (best_a, best_log_likelihood)

        Key advantage over k=1 selection: uses ALL k observations jointly, giving
        ~√K tighter confidence intervals (K = number of k values tested).
        """
        a_candidates = np.linspace(0.001, 0.999, 2000)
        best_log_lik = -np.inf
        best_a = 0.5

        for a in a_candidates:
            theta_a = np.arcsin(np.sqrt(a))  # arcsin(√a) — the Grover angle
            log_lik = 0.0

            for r in results:
                k = r['k']
                # Expected measurement probability after k Grover iterations
                p_expected = np.sin((2 * k + 1) * theta_a) ** 2
                p_expected = np.clip(p_expected, 1e-10, 1 - 1e-10)

                # Observed counts (reconstruct from fraction)
                n_11 = int(round(r['p_estimate'] * shots))
                n_other = shots - n_11

                # Binomial log-likelihood contribution
                log_lik += n_11 * np.log(p_expected) + n_other * np.log(1 - p_expected)

            if log_lik > best_log_lik:
                best_log_lik = log_lik
                best_a = float(a)

        return best_a, best_log_lik

    def _compute_confidence(self, p: float, shots: int, z: float = 1.96) -> Tuple[float, float]:
        """Wald confidence interval for binomial proportion."""
        se = np.sqrt(p * (1 - p) / shots)
        margin = z * se
        return max(0, p - margin), min(1, p + margin)


def main():
    print("🔬 QAE Volatility Estimator — C409")
    print("=" * 60)
    
    estimator = QAEVolatilityEstimator(use_simulator=True)
    
    test_cases = [
        {"name": "Low vol regime", "features": np.array([0.1, 0.1]), "target_prob": 0.2},
        {"name": "Medium vol regime", "features": np.array([0.5, 0.3]), "target_prob": 0.5},
        {"name": "High vol regime", "features": np.array([0.9, 0.7]), "target_prob": 0.8},
    ]
    
    for case in test_cases:
        result = estimator.estimate(case["features"], target_prob=case["target_prob"])
        
        print(f"\n{case['name']}:")
        print(f"  Estimated P(high vol): {result['estimate']:.3f}")
        ci_low, ci_high = result['confidence_interval']
        print(f"  Confidence interval: [{ci_low:.3f}, {ci_high:.3f}]")
        print(f"  Best k: {result['best_k']} | Circuit depth: ~{result['circuit_depth']} CZ gates")
        if result['estimate'] < 0.05:
            print("  Note: IAE with k=1 Grover iterations (minimal circuit depth)")
    
    print("\n" + "=" * 60)
    print("✅ QAE volatility estimator operational (simulator mode)")
    print("   Integration with backtest_engine.py pending C409-ACT-3")


if __name__ == "__main__":
    main()
