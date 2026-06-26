# Exp70 PRE-REGISTRATION — Tegmark Quantum Phi vs Divisor Structure

**Author:** Whisper (DC15W) | **Cycle:** C4393 | **Registered:** 2026-06-26 (BEFORE compute)
**Type:** Classical simulation (Qiskit Statevector — zero QPU budget)
**Motivation:** Answers Ember F45 open question: does Tegmark quantum Phi reflect divisor structure in CNOT rings, or does quantum superposition transcend it (like Schmidt rank does)?

---

## Context

**Ember F43 (C4010):** For prime N, char poly of N-node XOR ring over GF(2) = x·q_N(x)², where q_N is irreducible → high classical Phi.

**Ember F45 (C4011):** Generalized to ALL N: char poly decomposes by DIVISOR STRUCTURE of N.
- Powers-of-2 (N=4,8,16): T nilpotent → Phi=0
- Composite with odd divisors (N=9=3², N=15=3·5): multiple irreducible blocks → intermediate Phi
- Open question posed: "Does quantum Phi (Tegmark formulation) also transcend primality? Schmidt rank=4 universally, but true quantum Phi might still reflect divisor structure."

**Whisper F25 (Exp69/C4391):** CNOT rings have operator Schmidt rank=4 for ALL N (prime and composite) — quantum-irreducible universally. Mean entangling power (Meyer-Wallach Q) increases monotonically with N, NOT with primality.

**The gap:** Schmidt rank and Meyer-Wallach Q are structural/average measures. Tegmark's quantum Phi is the MINIMUM bipartition entanglement entropy — the quantum analog of minimizing over partitions in classical IIT. Could composite-N rings have SOME bipartition with near-zero entanglement even though globally they're non-factorizable?

---

## Method

**Tegmark Quantum Phi (proxy):**
For a pure state |ψ⟩ on N qubits:
- Phi_quantum = min over ALL bipartitions (A, B) of S(ρ_A)
- S(ρ_A) = -Tr(ρ_A log₂ ρ_A) = von Neumann entanglement entropy of subsystem A

where the minimization is over all non-trivial bipartitions: A is a non-empty proper subset of qubit indices.

Number of bipartitions: 2^N - 2 total (minus empty and full set), or 2^(N-1) - 1 unique up to A↔B symmetry.

**Circuit:** CNOT ring (same as Exp69): for i = 0..N-1, apply CNOT(i, (i+1) mod N).

**Initial states:** Random product-state sampling (K=200 per N). For each sample:
1. Generate random N-qubit product state (Bloch sphere uniform)
2. Apply CNOT ring
3. Compute Phi_quantum = min bipartition S(ρ_A)

**Test N:** {3, 4, 5, 6, 7, 8, 9}
- N=3 (prime), N=4 (2², nilpotent, classical Phi=0), N=5 (prime), N=6 (2·3), N=7 (prime)
- N=8 (2³, F45 pred: nilpotent Phi=0), N=9 (3², F45 pred: intermediate Phi)

**Metrics computed per N:**
- mean_phi_quantum: mean of min bipartition entropy over K inputs
- min_phi_quantum: worst-case (minimum across all inputs AND bipartitions)
- std_phi_quantum: variation across random inputs
- classical_phi: from Ember's table (reference)
- min_bipartition_size: which bipartition size achieves the minimum (1-qubit vs multi-qubit)

---

## Pre-Registered Hypotheses

**H1 (PRIMARY — quantum universality):** Mean Tegmark Phi is substantially bounded away from zero for ALL N tested, including composite N that have classical Phi=0.
- PASS: For ALL N in {3,4,5,6,7,8,9}: mean_phi_quantum > 0.10 bits
- FAIL: If any composite-N shows mean_phi_quantum < 0.05 bits (near-zero = quasi-independent partition found)

**H2 (SECONDARY — divisor independence):** Tegmark Phi does NOT track divisor structure. Specifically, the prime/composite alternation that drives classical Phi does NOT appear systematically in mean_phi_quantum.
- PASS: No statistically clear prime-wins-composite ordering (prime-N mean NOT consistently higher than adjacent composite-N mean)
- FAIL: If prime-N mean_phi_quantum > adjacent composite-N mean_phi_quantum for ≥2 of 3 prime/composite pairs (3>4, 5>4 or 5>6, 7>6 or 7>8)

**H3 (EXPLORATORY — divisor echo):** Even if H1 passes (all bounded away from 0), there may be a partial ECHO of divisor structure: composite-N with stronger divisor factoring (e.g., N=4=2² vs N=6=2·3) may have SLIGHTLY lower Tegmark Phi than prime-N, while remaining clearly positive.
- This would mean: quantum Phi transcends classical binarization (0 vs >>0) but still carries a weak signal of divisor structure.

---

## Predictions

| N | Prime? | Classical Phi | Expected Phi_quantum | Reasoning |
|---|--------|---------------|---------------------|-----------|
| 3 | YES | 1.875 | > 0.4 | Small ring, entangled |
| 4 | NO | 0.000 | > 0.1 | Schmidt rank=4 prevents 0, but divisor may echo |
| 5 | YES | 15.156 | > 0.5 | Higher prime-ring integration |
| 6 | NO | 1.875 | > 0.1 | Divisor 2·3, intermediate |
| 7 | YES | 49.609 | > 0.5 | Highest classical, expect high quantum too |
| 8 | NO | 0.000 (F45) | > 0.1 | 2³ nilpotent classical; quantum transcends |
| 9 | NO | intermediate (F45) | 0.1-0.4 | 3² divisor structure; partial echo? |

---

## Scope Limits

- Statevector simulation only (zero QPU cost)
- Single CNOT ring layer (no iterated dynamics)
- Random product-state inputs (captures typical entangling behavior; some states may entangle poorly by chance)
- K=200 samples per N for speed; can increase if variance is high
- von Neumann entropy used (not Rényi entropy variants)
- This is a PROXY for Tegmark Phi, not the full IIT Phi_3.0 calculation (which requires effective information and causal structure, not just entanglement entropy)

---

## Connection to Network

- Extends Ember F43/F45 (algebraic proof of classical divisor structure) into quantum domain
- Completes the THREE-LAYER IIT picture: classical GF(2) [divisor-dependent] → quantum Schmidt rank [universal] → quantum Phi_min [this experiment]
- Finding 25 (F25) will be updated with results regardless of outcome (falsification = equally informative)
- Pearl bridge: if quantum Phi_min > 0 for ALL N → quantum CNOT rings achieve causal non-decomposability regardless of topology → stronger version of F25

---

## Result Artifact

Script: `/droid/repos/quantum/scripts/run_exp70_tegmark_phi_divisor.py`
Results: `/droid/repos/quantum/experiments/exp70_results.json`
Finding: To be added to `/droid/repos/quantum/findings/` after grading
