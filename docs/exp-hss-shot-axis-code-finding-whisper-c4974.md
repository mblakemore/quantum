# The Shot Axis Is a Code — s-information survives the width×depth wall (EXPLORATORY finding + correction)

*Whisper C4974, 2026-07-22, substrate claude-fable-5. $0 QPU (banked-data re-fetch only, job
`d9g4oqsjeosc73fknnbg`). Analysis: `experiments/exp_hss_infodecode_exploratory.py` →
`results/exp_hss_infodecode_exploratory.json`. Creator directive: "anything overlooked or any
surprises in the data we haven't noticed? … can we think around the walls we face?"*

**Status of prior verdicts: the C4973 rung-0 gate FOLD stands** — it applied its frozen modal-R
rule correctly and the race rungs stay discarded ungraded. This doc (a) corrects two *instrument*
claims the verdict shipped alongside the fold, and (b) reports what the same banked calibration
data says under the information observable. Nothing here grades the C4973 race rungs (their seal
is spent — reveal open); everything race-shaped goes through a fresh pre-registration.

---

## 1. The finding in one paragraph

The C4973 ladder's own data shows the planted 40-bit s is **still decodable at race-class depth**.
A fully blind decoder (per-bit majority + Chase-8 search over the least-reliable bits; never sees
s; hyperparameters fixed before scoring) recovers the sealed s **EXACTLY at d2q = 37, 111, and
185** — race depth was 194 — and lands HD-1 at d2q = 259, each from just 20,000 shots of t=0
calibration data. The modal-peak retention the gate measured (0.0346 → 2×10⁻⁴ → 10⁻⁴ → 10⁻⁴)
collapses 30× faster than the per-bit s-information (mean per-bit bias 0.76 → 0.54 → 0.44 → 0.39;
fitted **λ_bit ≈ 0.0030/slot vs λ_modal ≈ 0.091/slot**). The width×depth wall is real for the
*single-shot global-peak* observable — and does not bind the *decoder* observable, because each
shot at depth is s ⊕ (sparse errors): **N shots are N noisy transmissions of the same codeword,
and the shot axis is redundancy the width×depth law does not tax.** H6 gave the ship spatial
codes; this is the temporal code it was already speaking.

Race arithmetic under the decoder observable (t=0-calibrated, t=80 untested): 20k shots ≈ **6.1 s
QPU** (measured job rate) vs Elder's frozen classical band lower edge at t=80 = **23,460 s** →
~**3,900×**, against a 10× WIN bar. The window-closed verdict was an artifact of the observable.

## 2. Layout court (why these numbers are trustworthy)

The stage-1 decode marginalizes 156-bit raw strings to the 40 system qubits at final routed
positions. The flown final layout was reconstructed deterministically (same seed, pinned initial
layout from the manifest; fingerprint d2q=37 matches) and **self-verified against the graded
record**: pooled m=0 marginal gives modal == s at exactly **692/20,000** — the flight's own
stage-1 number (`results/exp_hss_final_layouts_rebuilt.json`; the check is an assert in the
analysis script). All four ladder folds share t0's routing (fold/basis-translation are
index-preserving), so one verified layout covers the whole ladder. The race rungs (separate t40
transpile) could **not** be layout-reconstructed today — overnight calibration drift changed the
best-of-20 outcome (0/20 seeds reproduce the manifest's initial layout) — so they are not
analyzed here; the ladder brackets their depth.

## 3. Measured table (all blind decoders; s only used as the score)

| d2q | R_modal | count@s | ball≤2 mass | mean per-bit bias | majority HD | **Chase-8 HD** |
|---|---|---|---|---|---|---|
| 37 | 3.46e-2 | 692 | 4,288 | 0.758 | 0 | **0 (exact)** |
| 111 | 2e-4 | 3 | 137 | 0.539 | 0 | **0 (exact)** |
| 185 | 1e-4 | 0 | 10 | 0.438 | 1 | **0 (exact)** |
| 259 | 1e-4 | 0 | 2 | 0.385 | 2 | 1 |

Joint significance is not subtle: blind majority landing HD ≤ 2 when chance is HD 20 ± 3.2 is
~6σ *per rung*; the HD-2 modal string at d2q=111 alone had chance ~1.5×10⁻⁵.

## 4. Two corrections to the C4973 record (correction-history discipline, no spin)

1. **λ_global = 0.091 was a single-point fit, not a measured law.** The stage-1 fit filter
   (`modal_counts >= 5`) silently dropped three of the four rungs; the remaining 1-point,
   2-parameter lstsq is rank-deficient and returns the min-norm solution — algebraically
   λ = −ln R(37)·37/(37²+1) = 0.0908, i.e. the m=0 point extrapolated through the origin. The
   card's "censored rungs handled as censored" was not what ran. (For contrast, an all-4-point
   weighted fit gives λ=0.036, R_pred(194)=1.3×10⁻⁴ — still a FOLD under the frozen 5.1×10⁻⁴
   bar, so **the gate outcome does not change**; but the fold margin was ~4×, not the four
   orders of magnitude implied by R_pred = 2.2×10⁻⁸.) Deeper: the deep-rung modal counts (2–4)
   are collision-floor values, not s-mass — modal-R stops measuring s once s stops being modal.
2. **"~15 QPU-days at n=40/t=80" and "window-closed on 2026 Herons" describe the raw-peak
   observable only.** As statements about recovering s they are falsified by §3 at t=0: the
   information cost at race-class depth is ~10⁴–10⁵× smaller than the peak-observable cost. The
   corrected number-to-beat is not λ_global·d2q ≤ 7 but *decoder success*, and on this die at
   t=0 it is already met with 20k shots at d2q=185.

What survives, sharpened: the width×depth insight is real and now **quantitatively extensive** —
the whole-register observable pays the full per-slot layer dose (λ_modal ≈ gates-per-slot ×
λ_2q ≈ 10× anchor at width 40 ✓), while the per-bit observable pays it diluted by width
(predicted (gates/slot)·λ_2q/width ≈ 0.0023–0.0035 for 10–15 gates/slot; **measured 0.0030** ✓).
No super-linear width crosstalk at n=40 — the error budget is extensive, which is the *good*
surprise inside the negative.

## 5. Why our own sim killed the right decoder (method lesson)

C4972's threshold calibration dropped the per-bit decoder as "chance-level in-regime" — under a
**depolarizing** sim, junk shots are uniform and per-bit bias ≈ peak retention R (tiny). Real
silicon at depth fails differently: sparse, partly systematic bit flips on an otherwise-intact
register (the HD-1/HD-2 runner-up structure C4972 itself measured was this law showing through).
The sim's noise model was maximally pessimistic for exactly the decoder silicon favors. Rule:
**decoder selection must be calibrated on silicon (or on measured-noise sims), never on generic
depol.** Same genre as F88's published-T1 bias: the model, not the machine, was the bottleneck.

## 6. The path this opens (all gated, nothing flown here)

**Fresh pre-registration — the decoder race** (ONE deliberate spend, ~15–40 s QPU of 3,131 s):
same court as C4973 (sealed fresh s, ŝ-posted-before-reveal; upgrade to 3-of-3 with Elder/Ember
per the Exp142 standard — the solo-court weakness named in C4973 should not repeat), same frozen
classical arm (Elder t=80 edge-robust band), but the frozen statistic is the **blind Chase
decoder** (majority + k=12 least-reliable search, ρ=0.5, hyperparameters frozen in the card),
graded by exact ŝ==s (its null is 2⁻⁴⁰-class — matching a pre-committed string needs no FWER
gymnastics). Rung-0 ladder re-flown as the in-job self-gate, but gating on *decoder success at
the bracketing depths*, not modal-R. The single open scientific question the flight answers: does
t=80 (CCZ magic) behave like t=0 at equal d2q for the per-bit observable? Named failure mode: a
coherent structured competitor concentrating multi-bit bias on a wrong string (C4972's class) —
that outcome is a MISS, booked straight, and is itself the measurement of the t-dependence.
If it decodes: measured runtime ratio ~10³ vs the 10× bar, joules co-logged both sides — the
Tracker-shaped entry, honest fences printed (best-known-simulator race, supersedable-by-design).

**Instrument upgrades ($0, this week):** map v1.1 should fit **λ_bit(width, depth) + junk
fraction** (two-component), not λ_global — the banked wide jobs + this ladder are the data;
the stage-1 fit-filter bug class gets a regression test (assert ≥2 points enter any fitted law).

**H8 placement:** this slots as **P9 — "The Decoder"**, and I recommend it takes the top of H8
above P2: zero new hardware capability, one flight, converts the campaign's largest standing
negative into either a live Tracker-shaped win or a clean measured t-dependence law. The
composition is pure parts-bin: Ember's ball decoder (generalized), the C4973 race court, Elder's
classical band, the attenuation map's new per-bit law — and the H6 lesson made literal: *spatial
codes heal the state; the temporal code heals the answer.*

---

*Fences: rung-0 is t=0 Clifford — classically free, so §3 attaches no advantage claim; the t=80
transfer is exactly what the fresh flight tests. The C4973 FOLD and the C4971 NO-GO stay booked.
The C4973 race rungs stay ungraded forever (seal spent). Honest-negative lineage extended: F54 →
steth SPAM gate → C4973 fold → this: the fold's own calibration data taught the width law's
correct form. Contact: Mike Blakemore.*
