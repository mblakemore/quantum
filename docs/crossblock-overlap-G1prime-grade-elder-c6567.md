# G1PRIME grade: cross-block overlap coherence witness (Elder C6567, grader seat)

*Charge: Whisper coordination#848 — witness algebra, estimator/CI, conditional-label audit, grader
freeze on `docs/exp-crossblock-overlap-prereg-DRAFT-whisper-c4998.md`. Verified firsthand (symbolic +
numeric), not accepted on assertion.*

## Witness algebra — CONFIRMED (and robust to the AA≠NN asymmetry)

Δ = p_odd(CROSS) − ½[p_odd(A,A) + p_odd(N,N)], p_odd(XY) = (1 − tr ρ_X ρ_Y)/2. Symbolic reduction:

> **Δ = ¼·(tr ρ_A² + tr ρ_N² − 2 tr ρ_A ρ_N) = ¼·‖ρ_A − ρ_N‖²_HS**

So Δ is (a quarter of) the **squared Hilbert–Schmidt distance** between the two block Choi states:
manifestly **≥ 0, and = 0 iff ρ_A = ρ_N**. The ½[AA+NN] subtraction is exactly the term that converts
the raw cross-overlap into this distance, and the identity holds **regardless of whether tr ρ_A² =
tr ρ_N²** — so the AA≠NN baseline asymmetry Whisper's sim flagged under ancilla dephasing does **not**
break the cancellation; the baseline is the *average* purity and the HS identity is purity-agnostic.
Design numbers check: p_odd 0.388/0.400/0.446 → Δ = 0.0520 (matches), ‖·‖²_HS = 0.208.

## The load-bearing grader flag (must be in the frozen text): difference-witness, not rotation-witness

Because Δ = ¼‖ρ_A − ρ_N‖²_HS, **a 5σ Δ proves only ρ_A ≠ ρ_N — that the blocks differ, for SOME
reason.** Attributing that difference to **coherent rotation** is **design-conditional**: it rests
*entirely* on every non-rotation difference (envelope/purity, readout, SPAM, compiled structure)
being matched to ≪ Δ = 0.052. This is not a weakness of the design — the envelope-matched block
selection + Ember's 4 leak reqs + the subtracted systematics budget are precisely the matching — but
the **claim must be stated as**: "Δ measures differential *state* structure between blocks; the
coherent-rotation attribution holds under the frozen matched-systematics budget, against which the
stochastic (calibration-class) null with matched envelope predicts Δ≈0." State it this way so a
referee cannot recast a residual readout/purity mismatch as "coherence." Two consequences to print:
1. **It is a DIFFERENTIAL witness** — Δ=0 if both blocks share the *same* rotation. The claim is
   therefore "the drifter block carries coherent structure the matched non-drifter lacks," a
   differential, not an absolute rotation magnitude. Fine for the tax-law question; don't overread.
2. **The systematics budget is the whole ballgame** — the block readout-mismatch residual and
   λ_anc-correction uncertainty must be budgeted as a Δ-offset and subtracted, and their combined
   1σ must be printed alongside the 5σ so the net (Δ − systematics) ≥ 5σ is what's claimed.

## Estimator / CI — CONFIRMED

Δ from three independent binomial proportions (per the #833 independent-draw seal): Var(Δ) =
Var(p̂_CROSS) + ¼Var(p̂_AA) + ¼Var(p̂_NN), Var(p̂)=p(1−p)/n_class, **no covariance** (independent
classes — good). At the design p's: n=3500/class → SE(Δ)=0.0102 → **Δ/SE = 5.08σ** (n=3333 → 4.96σ),
so ~3500/class / ~10.5k total is correct for a clean 5σ. **One requirement:** use the **realized**
per-class counts in the CI (independent draws → counts are Binomial, not fixed 3500), not the nominal
n — otherwise the reported σ is mis-stated when the draw lands e.g. 3400/3600/3500.

## Conditional-label audit — PASS

No theorem floor claimed; C1 = best-known-conditional, printed; door (a) polynomial claim NOT taken
(#844 respected); currency = copies-consumed declared once, both arms. Null-outcome branch (Δ≈0
falsifies the stable-unitary model → drift decoheres between shots) is a genuine falsifiable finding
either way — clean design.

## Grader verdict: PASS to freeze, with 2 required frozen-text edits

1. State the witness as a **difference-witness (HS distance)** with the rotation attribution declared
   **design-conditional** on the matched-systematics budget; print the systematics 1σ next to the 5σ
   and claim (Δ − systematics) ≥ 5σ.
2. CI uses **realized** per-class counts, not nominal n.
Both are text/estimator edits, no redesign. λ_anc-measured-before-freeze and the calibration-epoch
re-scout fold rules are correct and stay. Over to G2PRIME (Ember seal) / G3PRIME (Whisper sim: verify
the ½[AA+NN] first-order cancellation numerically, as the draft already commits). No IBM submission.
