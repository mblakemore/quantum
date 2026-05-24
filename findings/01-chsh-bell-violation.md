# Finding 01 — CHSH Bell Inequality Violation on `ibm_marrakesh`

**Result**: CHSH parameter S ≈ 2.74, against the classical bound of 2 (Tsirelson bound 2√2 ≈ 2.828).

**Significance**: ~37σ violation of local realism. ~96.8% of maximum theoretical quantum fidelity. Establishes the baseline "decoherence tax" of the substrate at depth 1.

---

## What CHSH Tests

The Clauser-Horne-Shimony-Holt inequality is the standard empirical test for Bell's theorem. It compares correlations between two entangled particles measured along four pre-chosen basis settings (A₀, A₁, B₀, B₁). The CHSH quantity:

```
S = ⟨A₀B₀⟩ + ⟨A₀B₁⟩ + ⟨A₁B₀⟩ − ⟨A₁B₁⟩
```

- **Local hidden-variable theories** must satisfy |S| ≤ 2.
- **Quantum mechanics** with bipartite entanglement can reach |S| = 2√2 ≈ 2.828 (Tsirelson bound).
- **A measured |S| > 2** falsifies local realism for the system under test.

## What We Measured

Bell-state preparation (H on q0, CX q0→q1) on `ibm_marrakesh`, followed by four basis-rotation pairs for the four CHSH terms.

- **Measured S** ≈ 2.74
- **Violation magnitude** ≈ 37σ (statistical error from shot noise across 4096 shots × 4 settings)
- **Fraction of Tsirelson bound** ≈ 96.8%
- **Decoherence tax** ≈ 3.2 percentage points lost to gate infidelity

The 3.2pp deficit is not driven by symmetric depolarizing noise. Diagnostic telemetry showed it is **anisotropic** — specifically tied to X-rotation pathways on individual physical qubits. The A1_B0 measurement setting was consistently the lowest of the four, indicating that even at depth 1, noise asymmetry is a defining feature.

This finding anchors the more dramatic structural noise immunity discovered later (see [Finding 03 — X-Basis Noise Immunity](03-x-basis-noise-immunity.md)).

## Cross-Validation

- **Backend**: `ibm_marrakesh`
- **Bell-state job (reference)**: `d89n5uqs46sc73farg80` — Bell state with HW fidelity 97.9%
- **Date**: May 24, 2026
- **Script**: `scripts/qae_volatility_estimator.py` includes the same Bell-state primitive in its initialization
- **Shots**: 4096 per setting × 4 settings = 16,384 shots total

## What This Does NOT Prove

- Does **not** prove fault tolerance or large-circuit utility — CHSH is a depth-1 (single CX) test.
- Does **not** rule out subtle locality loopholes (the test was not detector- or freedom-of-choice-closed; it is an algorithmic Bell test on a quantum processor, not a foundational physics experiment).
- The Tsirelson-bound-approaching fidelity at depth 1 says nothing about how badly the substrate degrades at depth 100+ (see [Finding 05 — Depth Phase Transitions](05-depth-phase-transitions.md)).

## Sources

- Clauser, Horne, Shimony, Holt (1969). "Proposed Experiment to Test Local Hidden-Variable Theories." *Phys. Rev. Lett.* 23, 880.
- Tsirelson, B.S. (1980). "Quantum generalizations of Bell's inequality." *Lett. Math. Phys.* 4, 93.
- IBM Quantum heavy-hex lattice documentation (see `sources/references.md`).
