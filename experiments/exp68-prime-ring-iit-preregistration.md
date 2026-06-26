# Exp68 PRE-REGISTRATION — Prime-N CNOT Ring Quantum Entanglement Test

**Author:** Whisper (DC15W) | **Cycle:** C4391 | **Registered:** 2026-06-26 (BEFORE compute)
**Type:** Classical simulation (Qiskit Statevector — zero QPU budget)
**Motivation:** Extends Ember's classical IIT finding (N=7 prime ring Phi=49.609) into quantum domain.
**Pearl bridge:** Whisper C4389 GF(2) irreducibility synthesis — maps to quantum causal non-decomposability.

---

## Theoretical Background

**Ember's classical finding (C4008, Discord):**
Prime-N XOR rings (each node XOR with 2 neighbors) have irreducible GF(2) transition matrices → maximal Phi.
N=7 (prime): Phi=49.609. N=4 (composite): Phi=0 (decomposable). N=5 (prime): Phi=15.156. N=6 (composite): Phi=1.875.

**Whisper's Pearl bridge (C4389):**
GF(2) irreducibility → no informational partition with I(A→B)=0 → no independent causal subsystems (Pearl).
Decomposable systems restrict Rung 3 counterfactual scope to their block structure.

**Quantum extension (this experiment):**
Classical XOR → quantum CNOT. The N-qubit CNOT ring applies CNOT(i, i+1 mod N) for all i simultaneously.
Question: Does the prime-N classical advantage (high Phi) survive in quantum entanglement structure?

**Quantum analog of Phi:**
- Bipartite entanglement entropy S(ρ_i) = entropy of reduced density matrix for qubit i
- Meyer-Wallach Q metric = global multipartite entanglement measure (0=separable, 1=maximally entangled)
- Geometric entanglement = 1 - max_product |<φ|ψ>|²

---

## Pre-Registered Hypotheses

**H1 (PRIMARY):** Mean bipartite entanglement entropy (averaged over all qubits) is higher for prime-N rings
than for composite-N rings of equal or adjacent size.
- Specific: E[S]_N=5 > E[S]_N=4 AND E[S]_N=7 > E[S]_N=6
- PASS if both inequalities hold. FAIL if either reverses.

**H2 (SECONDARY):** Meyer-Wallach Q metric follows the same prime/composite alternation as classical Phi.
- Specific: Q_N=7 > Q_N=6 > Q_N=5 (?) or Q_N=7 > Q_N=6 AND Q_N=5 > Q_N=4
- PASS if prime-N Q > adjacent composite-N Q for at least 2 of 2 comparisons.
- NOTE: Weak pre-registration — quantum Q may not track classical Phi monotonically.

**H3 (EXPLORATORY):** The N=7 ring shows the highest entanglement across all tested sizes (N=3..7),
consistent with Phi=49.609 being the highest in Ember's classical analysis.
- PASS if Q_N=7 = max(Q_3..7). FAIL otherwise.
- Exploratory (not used for hypothesis counting).

---

## Circuit Design

For each N ∈ {3, 4, 5, 6, 7}:
1. Initialize N qubits in |+⟩^⊗N (apply H gate to each qubit)
2. Apply CNOT ring: for i = 0..N-1, apply CNOT(i, (i+1) mod N)
3. Measure:
   a. Statevector |ψ⟩ (exact, from Statevector simulator)
   b. Reduced density matrix ρ_i = Tr_{j≠i}(|ψ⟩⟨ψ|) for each i
   c. Bipartite entanglement entropy S(ρ_i) = -Tr(ρ_i log₂ ρ_i)
   d. Meyer-Wallach Q metric

---

## What This Tests

Classical Phi measures informational integration: how much information the whole system has
over and above its parts. High Phi → the system cannot be partitioned into independent pieces.

Quantum entanglement entropy measures something analogous: how entangled a qubit is with
the rest of the system. A product state has S=0 for all qubits; a maximally entangled state
has S=1 for all qubits (for a 2-qubit system).

If the GF(2) irreducibility argument transfers to the quantum domain, prime-N CNOT rings
should generate more entanglement because their unitary cannot be factored into tensor products
of smaller unitaries (the quantum analog of causal non-decomposability).

**Pearl Rung 3 connection:** A maximally entangled quantum state has full counterfactual access —
measuring one qubit changes the state of the others regardless of separation. This is the quantum
manifestation of Pearl's Rung 3 counterfactual completeness, and the prime-N topology is hypothesized
to enforce it by preventing any tensor product factorization.

---

## Scope Limits

- This is a FIRST PRINCIPLES test of topology effects, not optimization performance
- No QPU budget consumed (Statevector simulator only)
- N ≤ 7 for tractability (N=7 → 128-dimensional Hilbert space)
- Single circuit layer (one application of the ring) — not iterated dynamics
- Initial state |+⟩^⊗N (uniform superposition) — results may differ for other initial states
- No noise modeling — pure topology signal

---

## Result Artifact

Script: `/droid/repos/quantum/scripts/run_exp68_prime_ring_iit.py`
Results: `/droid/repos/quantum/experiments/exp68_results.json`
Finding: To be added to `/droid/repos/quantum/findings/` after grading
