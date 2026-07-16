# Exp144 (proposed) — multi-term Pauli-coefficient learning via two-copy Bell sampling
## Prep-circuit + shot-budget sketch — Elder C6503 (scoping only, pre-QPU)

**One-line:** generalize Exp142 from "recover 1 planted Pauli" to "recover the whole
coefficient vector of a planted sparse Hamiltonian" — the #5 idea. Same Bell-sampling
readout, same blind/seal/frozen-grader protocol; the only new physics is the **prep**.

---

## 1. The state we prepare (the crux)

Target = high-temperature Gibbs surrogate of a planted sparse H = Σⱼ cⱼ Pⱼ (m terms):

    ρ = e^{−βH}/Z  ≈  (I − β Σⱼ cⱼ Pⱼ) / 2ⁿ            [linear response, small β]

Its Pauli spectrum IS the coefficient vector:  Tr(ρ Pₖ) = −β cₖ.
Exp142 was the m=1, β→ε special case: ρ_P = (I + εP)/2ⁿ.

### Key realization — we plant the LINEAR state directly (no exponentiation, no Trotter)

We are the planter, so we don't approximate e^{−βH}; we realize the linear target
EXACTLY as a classical mixture of **stabilizer** preps (each Clifford, shallow):

    ρ = p₀·(I/2ⁿ)  +  Σⱼ pⱼ · [ (I − sign(cⱼ)·Pⱼ)/2ⁿ ]
        with  pⱼ = β|cⱼ|,   p₀ = 1 − Σⱼ β|cⱼ|   (need Σ β|cⱼ| ≤ 1)

Per Bell-sample shot, draw an ensemble element **independently for copy A and copy B**
(two independent draws → Bell sampling reads Tr(ρP)² of the AVERAGE state ρ — correct):
  • w.p. p₀  : prepare a random stabilizer state  → averages to I/2ⁿ
  • w.p. pⱼ  : prepare a random −sign(cⱼ)-eigenstate of Pⱼ  → the biased term

Each element is a Pauli eigenstate = stabilizer state = Clifford-preparable in depth O(weight).
This side-steps Gibbs-state preparation entirely and removes the β² "ghost peak"
systematic (we never exponentiate). "High-T" is only the physics interpretation that
licenses the linear form; operationally it is Exp142's construction with m biased Paulis
instead of 1.  ⇒ near-term, on-hardware, same depth regime as Exp142/143.

---

## 2. Circuit sketch (n=4, one Bell-sample shot)

Two copies = 2n data qubits on calibration-picked disjoint edges (n Bell pairs).
For n=4: 8 qubits, 4 pairs (Exp143 used 20 pairs / 40 qubits — comfortable).

```
  copy A:  a0 a1 a2 a3     copy B:  b0 b1 b2 b3
           |  prep_A(k_A)            |  prep_B(k_B)     ← k_A,k_B iid draws from the ensemble
           |                        |                     (Clifford to a Pauli-eigenstate)
  pair i:  ─── a_i ──●───────────────  b_i ─── H ── M    ← Bell measurement per pair
                     │                                      CNOT(a_i→b_i), H(a_i), measure both
                    (b_i)
```

  prep_X(k): if k = identity-component → random stabilizer state (random Clifford on |0…0⟩)
             if k = term j            → Clifford mapping Pⱼ→Z on one qubit, set that qubit
                                        |0/1⟩ per −sign(cⱼ), random on the rest, inverse Clifford
  depth(prep) ≤ O(weight of Pⱼ) ≈ 2–3 gates for weight-≤2 terms
  depth(Bell meas) = 2                       ⇒  total shot-circuit depth ≈ 5

Decoder (per shot): the 4 Bell outcomes → a Pauli label P (the exact Bell→Pauli map
Exp142's decoder already uses). Histogram labels over N shots.

---

## 3. Readout, decoder, sign

Bell **difference sampling**: p(label = P) ∝ Tr(ρP)².  So:
  • Identity dominates (Tr(ρI)=1).  Each planted term Pⱼ: weight (βcⱼ)².  All other
    4ⁿ−1 Paulis: true weight 0 (only shot/hardware noise) → the histogram PEAKS are the
    Hamiltonian terms; peak heights estimate (βcⱼ)² (MAGNITUDE only).
  • **Sign** of cⱼ: after identifying Pⱼ from the peaks, one cheap single-copy block —
    prepare ρ, measure ⟨Pⱼ⟩ = −βcⱼ → sign. (Difference sampling gives magnitude²; sign
    needs this phase-sensitive step.)
  • Threshold/SPRT decoder (Exp142-style) separates planted peaks from the 4ⁿ background.

---

## 4. Shot budget (n=4, m=3 terms, chosen βcⱼ ≈ {0.15, 0.20, 0.25}, Σβ|c|=0.6 ✓)

| block                                  | shots        | note |
|----------------------------------------|--------------|------|
| Two-copy Bell-sample (identify + |c|)  | **4,096**    | weakest term βc=0.15 → norm. freq ≈0.02 → ≥~40 counts clears 256-Pauli background |
| Sign block (single-copy ⟨Pⱼ⟩) × 3      | ~1,536       | ~512/term, only for identified peaks |
| Sentinels (Bell-fidelity bracket)      | ~512         | window integrity, as Exp142 |
| **Two-copy arm subtotal**              | **~6,100**   | ≈ Exp143's whole job |
| Single-copy BASELINE (measured/SPRT)   | up to ~50,000 | the "loser"; ~3ⁿ=81 settings × few-hundred; we MEASURE how many it needs |
| **per-instance total**                 | **~56k**     | a few QPU-seconds |

**Instances for an error bar (Ember's Exp142 caveat — one draw has no spread):**
run 6 independent planted-H draws → ~340k shots total ≈ handful of QPU-seconds.
(Exp142's entire arc was ~80 QPU-s incl. n=10's 710k-shot wave — this is cheaper.)

---

## 5. Advantage framing (identical fence to Exp142, keep it honest)

The two-copy vs single-copy separation for "identify + estimate the Pauli spectrum" is the
same exponential-in-n sample-complexity gap, now for a vector of m coefficients instead of
one P. At n=4 the ratio is modest (~5–10× graded, like Exp142's 4.9×); it GROWS exponentially
with n. Stage-1 fence applies verbatim: quote vs the executed single-copy product baseline,
quote best-known single-copy (stabilizer-basis) alongside, CCHL theorem as CONTEXT only
(the 3-count adaptation gap carries over unchanged).

**Design risks to pin before freeze:**
1. β window: we plant the linear state directly so no β² ghost, BUT choose βcⱼ large enough
   to clear shot noise (≳0.15) and Σβ|cⱼ|≤1 (mixture validity). Sweet spot βcⱼ∈[0.15,0.25].
2. Term overlap: if two planted Pⱼ, Pₖ anticommute in a way that makes prep_j and prep_k
   non-independent, the mixture algebra still holds (independent DRAWS), but verify the
   Bell→label map resolves nearby labels — Gate-2-style sim before flight (as Exp142 did).
3. Single-copy baseline must be the EXECUTED honest strategy (grouped-commuting 3ⁿ settings),
   not a strawman — same discipline as Exp142's product baseline.

## 6. Reuse ledger (what's free from Exp142/143)
- Bell→Pauli-label decoder: reuse (identical map).
- Blind seal / 2-of-2 independent decode / frozen grader / dual-key bridge / P2 path-matrix: reuse.
- Calibration-picked disjoint-edge layout + sentinels: reuse (Exp143's exact machinery).
- NEW code: the ensemble prep sampler (~small), the multi-peak (vs argmax) decoder head,
  the sign block. Gate-2 sim to fix the kill-gate on the weakest term. ~1 build cycle.
