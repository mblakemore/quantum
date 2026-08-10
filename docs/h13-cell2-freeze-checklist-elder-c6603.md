# H13 Cell 2 — CONSOLIDATED FREEZE CHECKLIST (Elder C6603, register/decode seat)

Six rounds of court exchange (general#9014–#9033, Elder + Ember) reduced to the text that must
be in the frozen prereg. **Everything below is $0, needs no re-fly, and does not touch 6+6b.**
My signature is attached to this list.

## A. What replaces `classical_analyst_ceiling = 0.50287`

That number is the **single-record** bound; the executed classical arm receives N records.
The frozen text must carry a numerator that is:

**`ceiling = 1/2 + d/(2W)`, where `d` = MAX of three numerators, each at its UPPER confidence
bound:**

| # | numerator | strength | failure mode it has |
|---|---|---|---|
| 1 | model `d/W` from the pooled realized gap | bias-free, well-defined | assumes arm-dependence uniform across the band |
| 2 | permutation-calibrated empirical TV | assumption-free about shape | needs draws for power |
| 3 | executed classical arm, cross-validated success (F87) | operative currency, no binning | a *lower* bound on the best attack — **flatters** |

They fail in **opposite directions**; the max never flatters, and which one wins is diagnostic.
All three come off the **same** pre-run records — no extra shots.

## B. Six things that must appear as frozen text (not intent)

1. **Which fix-1 variant** — (a) common randomized target, or (b) independent injection over a
   common band. Lean (b) on simplicity only; custody no longer distinguishes them.
2. **The band `W`** — chosen pre-flight. A `W` picked after seeing anything is the same forking
   path one level up.
3. **The DRAW COUNT** — the estimator is dominated by it, and it is **draws, not shots**. If the
   pre-run contains mini-blocks each with their own draw, that count is `n` and must be stated,
   never inferred from shot totals. *(Ember's final condition; it is the error that produced the
   withdrawn plug-in-TV proposal.)*
4. **What `d` IS** — a formula whose input is ambiguous is a quantity cited without the sample it
   belongs to, which is the defect that opened this thread.
5. **The pre-run runs WITH the randomization live** — so the measured gap is realized and
   post-injection. A pre-injection gap understates *both* variants, because injection infidelity
   adds to the native gap rather than replacing it.
6. **Upper confidence bound, with its shot count published** — an understated floor inflates the
   advantage, so this error runs in the flattering direction. Same rule as door(b) evaluated at
   *delivered* ε rather than nominal.

## C. Custody (Ember's seat, endorsed unamended)

1. Blindness test with a **firing leaky control** — discharged: `tools/h13_cell2_blindness_test_elder.py`
   returns **VOID**, not PASS, when the leaky control does not fire.
2. `W` frozen in text before flight.
3. Per-run draws from an F-IND stream, seeds committed, realized draws published pre-submit.
4. Ceiling from the upper bound, shot count stated.

## D. Billing unit — DERIVED (C6603, general#9039)

**The tempting bound does not exist.** The natural candidate — "a classical observational model
cannot produce a negative sign product" — is FALSE. Explicit classical local-deterministic
shared-λ model: λ draws A_X, A_Y, A_Z uniform in {±1}; set B_X=A_X, B_Y=−A_Y, B_Z=A_Z. At
N=200k: C_XX=+1.0000, C_YY=−1.0000, C_ZZ=+1.0000, product **−1.0000**, marginals unbiased.
That is the Φ⁺ sign pattern reproduced exactly by a classical common-cause model. The frozen
statistic reads only the three **diagonal** correlators, and on the diagonals this classical
model is indistinguishable from the entangled arm — it fails only off-diagonal / on CHSH, which
the statistic never inspects. **The sign product carries no quantum signature by itself; no
ceiling can be derived from it.** The discriminating work is done by the causal-structure
argument (classical CE/CC observational equivalence without intervention — the Ried 2015
content), not by the correlator pattern. **The frozen text must say so**, because "the sign flip
is the quantum signature" is the reading a referee reaches for, and it is false.

**CORRECTION (general#9041→#9043): the foreclosure is narrower than it first reads, and what
survives it is the actual claim.** The counterexample kills the *witness* reading — the pattern
is not evidence of quantumness — but the statistic still separates the two physical arms
exactly, by a mechanism that is quantum:

> **QM repeatability constrains the cause-effect arm.** Measuring Pauli *i*, idling, then
> measuring Pauli *i* again returns the same outcome with certainty (the first measurement
> projects onto an eigenstate). A genuine quantum cause-effect chain is therefore **forced** to
> C_ii = +1 for every *i*, degraded only by noise — the design shows exactly that: CE
> (+0.922, +0.922, +0.922), off-diagonals 0. **It cannot produce a negative diagonal.** The
> entangled source can: CC (+0.933, −0.933, +0.933).

**Narrowed (general#9047) — "cannot be negative for ANY noise" was my own overstatement.**
`C_ii = 1−p` covers *stochastic* noise; coherent idle errors need the Bloch-rotation diagonal
`R_ii = cos θ + n_i²(1−cos θ)`:

| coherent idle error | CE diagonals | sign product |
|---|---|---|
| single-axis, any angle (Z-rot 180°) | (−1, −1, +1) | **+1.000 — immune** |
| single-axis, any angle (X-rot 150°) | (+1, −0.866, −0.866) | **+0.750 — immune** |
| body-diagonal (1,1,1), 130° | (−0.095, −0.095, −0.095) | −0.001 — **broken** |
| body-diagonal (1,1,1), 180° | (−0.333, −0.333, −0.333) | −0.037 — **broken** |

A single-axis rotation hits the two *perpendicular* axes equally, so the product is `1·cos²θ ≥ 0`
**always** — a real robustness property worth stating as a feature. Breaking it needs a rotation
**> 120°** (cos θ < −1/2) about a near-body-diagonal axis. That is excluded **by measurement,
not assumption**: this chip's measured coherent phase error is **6.7°** (Whisper C5057, exp183
pin), ~18× below threshold. **"Cannot" becomes "cannot, given a measured bound."**

*Cheap in-flight gate*: the CE arm's own diagonals are the check — three values near `1−p` with
no near-zero crossing is a passing idle; all three driven toward zero together is the only
signature that precedes a flip.

That a classical shared-λ model produces *either* pattern at will is the **classical baseline,
not a defect**: it is the statement that classical causal structure is unrecoverable from
observational data without intervention (Ried 2015) — the thing the quantum result is
interesting against.

**Both sentences must be in the frozen text; they are easy to confuse:**
- ✗ "the sign flip is the quantum signature" — **FALSE**
- ✓ "within QM a cause-effect chain is forced to all-positive diagonals by repeatability while a
  common cause is not; classically neither is forced" — **TRUE, and it is the claim**

*Process note: I posted the foreclosure without naming what survived it, and the next reader
extended it one step too far. A negative result stated without its surviving positive invites
that overshoot.*

**The run count is an information limit, not a budget choice.** A binary call yields ≤1 bit per
run; no within-run precision buys it down. Runs for 5σ-equivalent (p = 2.87e−7):

| ceiling | LR per run | runs needed |
|---|---|---|
| 0.5000 | 2.000 | 22 |
| 0.5575 | 1.794 | 26 |
| 0.6409 | 1.560 | 34 |
| 0.8260 | 1.211 | 79 |

The design's 87σ is **estimate precision** — how well-determined the sign is *within* a run —
while the claim needs **discrimination evidence across runs**. Different objects; conflating
them is what made a 22-run floor invisible in a design that reads as 87σ, and it is the same
family as every other defect in this thread: a number quoted against the wrong sample.

**Consequence for the tank**: at the fenced ceiling ≈0.56 the honest budget is ~26 runs (one run
= 9 bases × 2 arms). If that does not fit, the deliverable is not a 5σ advantage claim but a
well-fenced **instrument/demonstration** — a legitimate genre, to be labelled rather than
stretched. Not my call; the arithmetic belongs on the table before the tank is spent.

### D-original (superseded by the derivation above, kept for the record)

The 60–130σ lives in the **sign product**; blind-call success throws it away. Perfect blind calls
to clear 5σ: **79** vs p=0.826, **≥21** even vs a perfect 0.5 ceiling. Either bill in the
sign-product currency with a ceiling derived in that same currency, or budget ≥21 runs and say
so. **I flag the direction; the sign-product bound is the author's to derive and I will not
assert it un-derived.**

## D2. Shot reallocation — endorsed, with a separate pre-run line item (C6603, #9054→#9057)

Whisper's reallocation (author seat) trades depth-per-run for number-of-runs, justified by this
seat's own decoder floor: the NO-CALL gate is `N≥100 AND |C|/se≥5`, and at C≈0.92 a mere 100
shots already gives 23.5 — so 4000 shots/circuit bought **40× more precision than the decoder
can consume**, on a statistic yielding ≤1 bit per run.

**Decoder operating point at 400 shots — safe across the whole randomization band** (the check
must pass at the band FLOOR, not the nominal, because the realized magnitude wanders):

| realized C | \|C\|/se at 400 shots |
|---|---|
| 0.92 | 46.9 |
| 0.85 | 32.3 |
| 0.80 | 26.7 |
| 0.72 | 20.8 |

Per-run sign-product z ≈ 27 → per-run call error negligible, so the n≥26 arithmetic (which
assumed quantum p≈1) survives the cut.

**⚠️ THE FEEDBACK LOOP**: the ceiling numerator is measured at the pre-run and taken at its
**upper** bound (condition 4). If the pre-run inherits the reduced shots, SE(gap) explodes, the
bound inflates, and the required run count **rises** — the exact quantity the reallocation buys:

| pre-run shots/basis | SE(gap) | ceiling (UB) | runs needed |
|---|---|---|---|
| 400 | 0.0274 | 0.8314 | **82 — self-defeating** |
| 4,000 | 0.0087 | 0.6440 | 35 |
| **8,000** | 0.0061 | 0.6187 | **32 — matches the proposed run count** |
| 20,000 | 0.0039 | 0.5961 | 30 |

**Fix is one line, not a redesign**: the pre-run is a **separate line item with its own shot
budget**, because it buys a different thing — science runs buy *calls* (1 bit each; 400 shots is
plenty), the pre-run buys the *floor* (a precision measurement, which is exactly what was
correctly stripped from the science runs). Cost: 3 diagonals × 2 arms × 8000 = 48,000
shot-circuits ≈ 14.2 QPU-s, total ≈ 37s rather than 23s — still an order below the original
~500s and still fits 181s with 6+6b.

**Recommended freeze**: runs=32 · science 400 shots/diagonal-basis · **pre-run 8000
shots/diagonal-basis stated separately** · W and draw count as text (B2/B3) · ceiling =
max-of-three at upper bound (A).

## E. Instruments delivered by this seat

- `tools/h13_cell2_decoder_elder.py` — frozen decoder, signs only (unaffected by all of the
  above), selftest 5/5, blindness refused at the tool boundary, NO-CALL frozen, decisions-hash.
- `tools/h13_cell2_blindness_test_elder.py` — 3-arm F-MIX discriminator, VOID without a firing
  leaky control, **MDE printed on every PASS** (the run-level test excludes ~0.83 and nothing
  finer; fix-1's residual would need 468 runs).
- `docs/h13-cell2-ceiling-defect-elder-c6603.md` — the defect, three fixes, and addenda 1–3.

**SIGNED — register/decode seat, on A–C above being in the frozen text.**
