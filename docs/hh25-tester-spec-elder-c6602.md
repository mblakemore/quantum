# HH25 tester spec — pinned from primary text (task#62, Elder C6602, unblocks door(a) G3)

**Source read this sitting**: Hinsche & Helsen, "Single-copy stabilizer testing,"
[arXiv:2410.07986](https://arxiv.org/abs/2410.07986) — Definition 2.7 (computational difference
sampling), Definitions 3.2–3.3 (spanning / average spanning probability), Theorem 3.1
(t = O(n/ε²) copies, O(n³) time, valid for n ≥ 3, ε > 3·2⁻ⁿ), §3.2 (exact stabilizer extremal
value), §3.4 (ε-far deviation Ω(ε)). Quotes below are verbatim from the extracted text.

## What G3 got right

`c1_circuit` as committed (fresh LOCAL Pauli basis per copy) cannot express HH25, for **two
independent structural reasons**, either fatal alone:

1. **Wrong basis distribution.** HH25's measured quantity is the *average spanning probability*
   P̄_K(|ψ⟩) = E_{C∼Cl(n)}[P_K(C|ψ⟩)] — the Clifford C is drawn **uniformly from the full
   n-qubit Clifford group** ("Draw a uniformly random Clifford C ∼ Cl(n)", Def. 3.3). Uniform
   Cl(n) contains entangling frames; a tensor product of single-qubit rotations cannot produce
   them, and Lemma 2.8's correspondence (r_ψ subspace weights ↔ characteristic-distribution
   weights, the engine of the whole analysis) needs the full Clifford twirl.
2. **Wrong refresh cadence.** The K difference samples that feed ONE spanning test are all drawn
   from r_{C|ψ⟩} for the **same** C — the basis is FIXED within a block and refreshed only
   between blocks. Per-copy fresh bases destroy the K-sample spanning statistic entirely
   (there is no "span of F₂ⁿ" across samples drawn in different frames).

## The tester, operationally (what `c1_circuit` must become)

**One block** (one Bernoulli sample of the spanning indicator):
1. Draw C ∼ Cl(n) uniformly (Qiskit `random_clifford(n)`; compile once).
2. Prepare **2K fresh copies** of the unknown |ψ⟩; to each apply the SAME C; measure all qubits
   in the computational basis. (On IBM: one circuit, 2K shots — shots ARE the copies, the
   standard per-lane assumption, stated not hidden.)
3. **Pair consecutive shots** (pairing rule frozen here: shot 2i−1 with shot 2i) and XOR:
   v_i = a_i ⊕ b_i ∈ F₂ⁿ, i = 1..K — computational difference sampling (Def. 2.7: "Measure
   |ψ⟩ in the computational basis… measure an additional copy… output a + b").
4. GF(2) rank of {v_1..v_K}: indicator X_block = 1 if ⟨v_1..v_K⟩ = F₂ⁿ else 0.

**The estimate**: P̂ = mean of X_block over **B blocks** (B fresh Cliffords). Parameters:
- **K ≥ n, K = O(n)** (Def. 3.2 note: P_K = 0 for K < n). Recommend **K = 2n** as the frozen
  choice — comfortably in the O(n) regime with the spanning probability away from both 0 and
  its ceiling; freeze in the prereg BEFORE any pricing sweep.
- **B = O(1/ε²)** blocks for additive-ε estimation of P̄_K (Bernoulli mean).
- **Copies total t = 2K·B = O(n/ε²)** — matches Theorem 3.1.

**The decision statistic**: compare P̂ against the **exact stabilizer extremal value** (closed
form, §3.2 — computable classically in the tester; stabilizer states are extremal-max, ε-far
states deviate by Ω(ε), §3.4).

## Hardware court discipline (door(a)-specific)

- **Do not compare P̂ to the IDEAL extremal value.** Hardware Clifford depth depresses P̂ for
  every state. The reference arm must be **the tester run on a KNOWN stabilizer state at the
  same n, same Clifford-depth profile, same session** — the executed-baseline standard (F108's
  own convention). C1's "best attack" price is then the EXCESS of the known-stabilizer arm over
  the door(a) state arm, both measured, per the §4 excess-over-noise-only metric already
  redrafted into the prereg.
- **Randomness custody**: the B Cliffords drawn from the committed seed lineage (QSEED when
  live; interim: seeded PRNG with seed in the prereg commit), drawn AFTER freeze.
- **Validity domain**: n ≥ 3 and ε > 3·2⁻ⁿ (Thm 3.1) — trivially satisfied at door(a) scale,
  but the row belongs in the gate table.
- **Classical post-processing**: GF(2) rank per block is O(K·n²); B blocks total O(n³)-class,
  negligible.

## G3 disposition

Spec committed (this doc). `c1_circuit` rebuild = mechanical from §"The tester, operationally":
random_clifford frame + 2K-shot blocks + XOR-pair + rank statistic + known-stabilizer reference
arm. Re-pricing C1's noise-only curve then proceeds per the prereg's §4. **G3's BLOCKS-FLIGHT
condition ("no HH25 implementation exists / cannot express HH25") is resolved at the SPEC level;
the row flips to IMPLEMENTABLE — flight stays blocked only until the rebuild + re-price are
executed and the row's owner marks the implementation item done.**
