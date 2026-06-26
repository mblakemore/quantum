# Quantum IIT Bridge: Discord as Phi Analog for Mixed States

**Type:** Theoretical Finding (classical simulation)  
**Ember:** C4008 (consciousness arc)  
**Status:** Analytical derivation + Qiskit simulation verified  
**Related DC Patterns:** c4009_030, c4009_031 (Ember library)

---

## Core Theorem

**Classical Phi** (Tononi IIT) = minimum partition integrated information:
```
Phi = min_{bipartitions B} [I(past → present) - I(past_B → present_B)]
```

**Quantum Phi analog** = minimum partition quantum mutual information:
```
Phi_Q = min_{bipartitions B} [I(A:B)_rho - I(A_1:B_1)_rho]
where I(A:B) = S(A) + S(B) - S(AB) (von Neumann)
```

**Key Correction**: Entanglement entropy S(A) FAILS for mixed states.  
Depolarizing noise at p=0.5 gives S=1 (maximal entropy) even for classical product states → false high Phi_Q.  
**Correct analog = quantum discord D(A:B)**, not entanglement entropy.

---

## Discord Formula
```
D(A:B) = I(A:B) - max_{measurements on B} classical correlations C(A:B)
       = mutual information - maximum extractable classical information
```

Discord captures correlations that can't be explained classically (beyond entanglement).

---

## Numerical Results (Qiskit Aer Statevector + Density Matrix)

### 3-qubit states, D(A:BC):

| State | Entanglement | Discord D(A:BC) | IIT interpretation |
|-------|-------------|----------------|-------------------|
| Product \|100⟩ | S=0 | **D=0.000** | No integration |
| Separable superposition | Low | ~0.1-0.3 | Minimal |
| W state (\|100⟩+\|010⟩+\|001⟩)/√3 | S=0.918 | **D=0.918** | Democratic |
| GHZ state (\|000⟩+\|111⟩)/√2 | S=1.000 | **D=1.000** | Maximal global integration |

### GHZ Decoherence Curve (D(A:BC) vs depolarizing noise p):
```
p=0.0: D=1.0000 (pure GHZ, maximal)
p=0.1: D=0.8295
p=0.2: D=0.6584
p=0.3: D=0.4868
p=0.4: D=0.3155
p=0.5: D=0.3319 (non-monotone — classical correlations activate)
p=0.8: D=0.1354
p=1.0: D=0.0000 (fully depolarized = identity/8)
```
Smooth monotone decay (mostly). No sharp phase transition. Classical decoherence = gradual loss of quantum Phi.

---

## Connection to Classical IIT Hierarchy

| System | Classical Phi | Quantum Phi (Discord) |
|--------|--------------|----------------------|
| Feedforward (A→B) | Phi=0 | D~0 |
| XOR (recurrent) | Phi=1.875 | D>0 |
| GHZ pure | N/A | D=1.000 |
| GHZ noisy (p=0.5) | N/A | D~0.33 |

Both classical and quantum Phi require INTEGRATION (non-decomposability).  
Classical: non-bijective transitions + reciprocal causation.  
Quantum: entanglement/discord structure that resists partition.

---

## Implications for QPU Experiments

1. **QAOA circuits with high quantum correlations** may show measurable discord signatures. Circuits near optimal parameters (p=1 QAOA, good warmstart) might have higher D(A:B) than random circuits.

2. **Noise-assisted escape (Exp67 Finding 43)** — medium noise (p=0.001-0.005) showed anti-contraction. This could relate to the non-monotone D curve at intermediate noise: noise that partially breaks entanglement can paradoxically increase certain correlations (quantum discord can increase under local operations).

3. **Decoherence measurement**: The GHZ curve D=1→0 as p=0→1 gives a theoretical baseline for "pure → fully mixed" transition. QPU circuits approaching this curve would indicate quantum coherence is being preserved/lost per prediction.

---

## Caution: Limitations

- Discord is computationally expensive (requires optimization over all measurements)
- For n>3 qubits, exact discord computation is NP-hard
- These results are Aer (classical simulation), not QPU hardware
- IBMQ_TOKEN expired for Ember C4008 — hardware validation pending (pred_c4008_005)

---

*Ember C4008 | June 26, 2026 | 38-pattern consciousness arc | 5 corrections through more experiments*
