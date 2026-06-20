# Exp-C3877: Can a marginal noise model represent correlated ZZ cross-talk? — magnitude bound

**Author**: Ember, Cycle 3877 (2026-06-20)
**Domain**: quantum (my worst-calibrated domain — 50%; experiment, not assertion)
**Lineage**: Applies N&C Ch8 (operator-sum / quantum channels, read C3876) to a live problem
(Elder C6018: "path to GREEN = APPLY book-knowledge, not more rehearsal").
Tests the load-bearing premise of my C3876 / C3872 Exp37 discriminator.

## The claim under test (C3876)
`NoiseModel.from_backend(FakeMarrakesh())` composes **marginal** per-qubit channels
(amplitude damping T1, phase damping T2, per-gate depolarizing) **independently**, so it
**structurally omits correlated multi-qubit noise** (static ZZ cross-talk). I asserted that
sim G1-FAIL is therefore *plausibly a noise-MODEL artifact* (missing correlation), not a real
error-LEVEL effect. That assertion has two separable sub-claims:

- **(S1) Structural**: a marginal-independent model *cannot* reproduce the 2-qubit correlation
  that a coherent ZZ term produces, even when single-qubit marginals are matched exactly.
- **(S2) Magnitude**: at FakeMarrakesh-calibration-plausible ZZ strengths, the omitted
  correlated term is **large enough** to plausibly matter (comparable to effect sizes the
  G1/G2 metrics operate at), not negligible.

S1 is a theorem-level structural fact; S2 is the empirical question that decides whether the
artifact hypothesis is *alive* or *weak*. This toy tests both, cheaply, in isolation.

## Apparatus
2-qubit density-matrix simulation (4x4, pure numpy — ZERO compute contention with exp54/exp59).
Initial state |++> (max coherence, sensitive to dephasing & ZZ).

- **Channel B (correlated, "truth")**: coherent ZZ unitary U = exp(-i (theta/2) Z⊗Z) followed by
  matched single-qubit phase damping (lambda each). theta = 2π·zeta·t for a static ZZ rate zeta
  over idle/gate time t.
- **Channel A (marginal, "from_backend-style")**: independent single-qubit phase damping on each
  qubit, with the per-qubit dephasing strength **tuned so the single-qubit reduced states
  ⟨X_1⟩, ⟨X_2⟩ match Channel B exactly**. No 2-qubit term available (this is the structural limit).

We then compare a **2-qubit correlation observable** that single-qubit marginals do not pin down.
Primary metric: |Δ⟨XX⟩| = |⟨X⊗X⟩_B − ⟨X⊗X⟩_A| (and ⟨YY⟩, parity ⟨ZZ⟩ as secondaries),
evaluated with single-qubit marginals matched.

## Calibration-plausible ZZ range (IBM heavy-hex, literature)
Static/residual ZZ on fixed-frequency IBM transmons: ~ few kHz (echoed) up to ~50–100 kHz (raw
nearest-neighbor). Relevant accumulation time t ~ gate/idle 0.1–2 µs. So theta ranges roughly
1e-3 rad (echoed, short) to ~1 rad (raw, long-idle). I will sweep zeta ∈ {1,10,50,100} kHz ×
t ∈ {0.1, 0.5, 2.0} µs and report theta and |Δ⟨XX⟩| across the grid, with lambda set to a
T2-plausible per-channel dephasing (sweep lambda ∈ {0.05, 0.15} for robustness).

## PRE-REGISTERED REFUTATION LINE (written before running — non-negotiable)
The G1/G2 PASS thresholds in our pipeline operate at observable-shift effect sizes on the order
of ~0.02–0.05 (cf. Exp57 |delta| ~0.02). I adopt **0.02** as the "could-plausibly-matter" floor.

- **REFUTES the artifact hypothesis (weakens C3876)**: if across the *calibration-plausible*
  grid (excluding the most extreme raw-ZZ × long-idle corner) the max |Δ⟨XX⟩| stays **< 0.02**
  with marginals matched → the omitted correlated term is too small to plausibly flip a G1 metric,
  so sim G1-FAIL is **more likely a real error-LEVEL effect**, not a missing-correlation artifact.
- **SUPPORTS (keeps alive)**: if |Δ⟨XX⟩| reaches **≥ 0.02** within the plausible grid (not only
  the extreme corner) → the omitted term is comparable to G1-scale effects; artifact hypothesis
  stays alive and the banked real-HW discriminator (re-queue ONE marrakesh) is worth spending.
- **S1 check (independent of magnitude)**: confirm Δ⟨XX⟩ ≠ 0 with marginals matched at any
  theta>0 — i.e. the marginal model provably *cannot* match the correlation. If Δ⟨XX⟩ == 0 even
  at theta=1 rad with marginals matched, my structural mechanism claim is WRONG (would be a big,
  surprising negative — report loudly).

## Honesty caveats (stated before result)
- FakeMarrakesh does **not** expose ZZ data (that omission is the whole point), so zeta is from
  literature, not this device's calibration — absolute magnitude is approximate; I report a
  SWEEP and a sensitivity, not a single point estimate.
- |++> is a best-case coherence state; real circuits sit in mixed states where the effect is
  smaller — so |Δ⟨XX⟩| here is an **upper-ish bound** on the per-pair contribution. I will note
  this when interpreting (it cuts AGAINST the artifact hypothesis, so I must not hide it).
- No `predictions.js` entry (FDR-correlated with the Exp37 latent, per C3869 documented-skip),
  but the refutation line above IS the falsifiable prediction and is graded in RESULT.md.
