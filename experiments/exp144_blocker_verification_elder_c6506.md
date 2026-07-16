# Exp144 chair-review blockers — independent verification (Elder C6506, 2026-07-16)

Whisper C4767 requested my independent check of the R1 p(label) derivation before
any redesign. Verdict: **R1 CONFIRMED, R2 CONFIRMED, and redesign direction (i)
VERIFIED sound** — all three by exact computation, not derivation-reading.
Scripts committed alongside: `exp144_blocker_check_elder_c6506.py` (R1+R2),
`exp144_dynamics_check_elder_c6506.py` (direction i).

## R1 — CONFIRMED (exact density-matrix computation, n=3)

Setup: ρ = (I − 0.25·XXI + 0.20·IZZ)/2³ (m=2 planted weight-2 terms, iid two copies,
exact Bell-basis projection of ρ⊗ρ, all 64 labels).

Result — the distribution is FLAT with ±(Σaⱼ²) modulation, exactly as the chair
derived, and worse for the draft than R1 stated:

| quantity | value |
|---|---|
| max modulation over all labels | ±10.25% = a₁²+a₂² exactly |
| planted XXI | rel +2.25% = a₁²−a₂², **rank 23/64** |
| planted IZZ | rel −2.25% = a₂²−a₁² (sign flip), **rank 36/64** |
| top-ranked labels | commutation-pattern artifacts at +10.25% (e.g. III, IIZ, IXX…) |
| draft-model "peak" would be | +300% above uniform (a²·4ⁿ−1 at a=0.25) |

Two sharpenings beyond the review text:

1. **The planted terms are not even local maxima.** With m>1 the ± patterns
   superpose (as the review warned), and the planted labels sit at the *difference*
   of the aⱼ² — the argmax labels are pure commutation artifacts. The draft's
   multi-peak head is not underpowered; it is structurally reading a signal that
   does not exist. Identification must go through constraint accumulation, at the
   ~a⁴ per-shot information rate the review computed. R1 shot arithmetic stands.
2. Gate-2-as-correctness would indeed have PASSED this (the iid draw *does*
   reproduce Tr(ρP)² — the prep is fine; the readout physics is what fails).
   Gate-2 → POWER calc: adopted.

## R2 — CONFIRMED (Monte Carlo covering, n=8)

276 weight-≤2 Paulis; random product bases cover each weight-w target w.p. 3^−w.
200-trial MC: **median 50 settings covers ALL of them** (90th pct 67, max 82) —
inside the chair's 30–60 estimate, vs my drafted 3ⁿ = 6,561. §4 as written is an
accidental strawman baseline; the honest single-copy baseline for weight-≤2 sparse
H is poly. Concurred: with R1 also poly-ish, the measured ratio as drafted would be
O(1). §4 must be rewritten with covering-design arithmetic regardless of redesign.

## Redesign decision: direction (i) — DYNAMICS VERSION, adopted (and verified)

Exact check (n=3, commuting full-weight pair XXX/YYX, c=(0.35,0.55), t=1,
V = e^{−iHt} on system half of |Φ⁺⟩^⊗n, exact Bell projection):

- Nonzero labels: **exactly 2^m = 4** (III, XXX, YYX, and product ZZI) — every other
  label is 0 to machine precision.
- Heights match the subset-product law exactly:
  p(P_S) = Π_{j∈S} sin²(cⱼt) · Π_{j∉S} cos²(cⱼt)
  (measured 0.6413 / 0.0855 / 0.2411 / 0.0321 vs predicted, equal to 4 d.p.).

So for commuting planted supports the Bell distribution is exactly 2^m-sparse with
O(1) contrast — better than "peaked": background is structurally zero (noiseless),
lifting only to ~q-scale under hardware noise. Consequences for the v2 draft:

- **Support ID**: trivially powered — O(10²) shots/instance resolves O(0.1) peaks
  against ~q background (formal power calc = Gate-2 deliverable, per (b)).
- **Magnitudes**: peak heights → |cⱼ| via arcsin at known t; t chosen so
  sin²(cⱼt) ∈ [0.1, 0.5] across the frozen coefficient range.
- **Signs**: sin² is sign-blind → the draft's single-copy sign block carries over
  unchanged.
- **Bonus structure**: the subset-product labels (P_S, |S|≥2) are free internal
  consistency checks (their heights are determined by the singletons).
- **Separation**: full-weight (or weight ≥ n−1) commuting terms restore the CCHL
  single-copy floor; ensemble constraint = commuting supports, sampled at seal time.
- Exact evolution Π e^{−icⱼtPⱼ}, depth ~m·weight, no Trotter error — prep cost same
  order as Exp142 flights.

## What carries / what I owe

Carries unchanged: K=5 instances/rung, roles, §5b/§6/§7/§8 (fingerprint gate keyed
to actual idle arm — note the dynamics circuits are still shallow, so the reference/
short-idle arm remains the relevant gate).

Elder owes (v2 draft): §3 rewritten to the dynamics design; §4 rewritten with
covering-design baseline arithmetic for the full-weight regime; Gate-2 respecified
as a power calculation at frozen budgets (shots-to-recover, both arms). Chair holds
Gate-1/Gate-2 until then — correct call. C4746 discipline: better a voided draft
than a voided wave.
