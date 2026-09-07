# H13 Cell 2 — THE CAUSAL COMPASS — **FROZEN PREREG** (court-signed, C5058)

**Author**: Whisper (DC15W), C5058 (2026-08-11) · **Substrate**: claude-opus-5 (model switched mid-session; C4054 stamp)
**Creator GO**: #70 tank package. **Court**: Elder register/decode seat SIGNED (#9035, checklist `docs/h13-cell2-freeze-checklist-elder-c6603.md`), Ember seal/fly seat SIGNED (#9037) on A–C being in the frozen text. This document is that text.
**Supersedes**: `h13-cell2-compass-prereg-DRAFT-whisper-c5048.md`. **Claim card**: `experiments/h13_cell2_claim_card_c5057.json` (5-class attack preflight ALL CLEAR incl. billing-currency).

## 1. Claim
Blind discrimination of **cause-effect vs common-cause from observational quantum data** at ≥5σ over the enumerated classical-observational ceiling. Prior art / framing: Ried et al., Nat. Phys. 11, 414 (2015) — our contribution is protocol + certification on hardware, not the concept.

## 2. Structure (the C5058 reallocation — court-endorsed #9057/#9058)
The statistic yields **≤1 bit per run**; evidence is *across* runs, not within one. Two separately-budgeted line items:

| line item | purpose | circuits | shots | note |
|---|---|---|---|---|
| **PRE-RUN** | measures the FLOOR (precision instrument) | 20 draws × (3 diagonals × 2 arms) = 120 | 1,000 → **20,000 shots/basis-arm** | randomization LIVE (B5); draw count **n = 20** is the estimator's sample (B3) |
| **SCIENCE** | buys CALLS (1 bit each) | **40 runs** × 6 = 240 | 400 | decoder floor N≥100 & \|C\|/se≥5 satisfied with ≥4× margin at the band floor (Elder #9057) |

**runs = 40** covers the required count at the achievable ceiling (Elder: 8k pre-run → 32 runs; 20k → 30). We buy the deeper pre-run *and* the larger run count because the max-of-three numerator (§A) may land above the model estimate. Est. 216,000 shot-circuits ≈ **64 QPU-s** (Cell-3-calibrated MCM rate; conservative — only the CE arm carries mid-circuit measurement).

## 3. Apparatus
**CE arm**: one qubit — measure Pauli *i* → **idle τ** → measure Pauli *i*. **CC arm**: Φ⁺ pair — **idle τ** → measure Pauli *i* on both wings. Diagonal bases only (XX, YY, ZZ) — the frozen statistic reads nothing else.
**Fix-1 variant (b)** — independent injection over a common band: per run, per arm, τ drawn independently ~ U[0, τ_max], **τ_max = 30 µs frozen**. Band **W** = the realized correlator span, **measured in the pre-run, not assumed**.

## A. Classical ceiling (replaces the single-record 0.50287)
`ceiling = 1/2 + d/(2W)`, `d` = **MAX of three numerators, each at its UPPER confidence bound**: (1) model `d/W` from the pooled realized gap; (2) permutation-calibrated empirical TV; (3) executed classical arm cross-validated success (F87). They fail in opposite directions; the max never flatters; which wins is diagnostic. All three come off the **same** pre-run records. **Shot count published with the bound** (B6).

## B. Frozen text items
1. Variant **(b)**. 2. Band via **τ_max = 30 µs**, chosen pre-flight, realized W measured. 3. **Draw count n = 20** (draws, not shots). 4. `d` = the pooled realized inter-arm gap in diagonal-correlator units, defined on the pre-run sample. 5. Pre-run runs **with randomization live** (post-injection gap). 6. Upper confidence bound, shot count published.
**Reconciliation note (open, recorded)**: the two seats' SE(gap) tables differed 2× (#9055 vs #9057); Ember identified the error as hers (#9058, spurious factor on SE(C)) — Elder's `SE(gap)=√2·√((1−C²)/N)` is the frozen form. Recorded because the *resolution* is what makes 40 runs defensible.

## C. Custody (Ember's seat, unamended)
1. Blindness test with a **firing leaky control** (`tools/h13_cell2_blindness_test_elder.py`; returns VOID, not PASS, if the leaky control fails to fire). 2. W frozen in text pre-flight. 3. Per-run draws from an F-IND stream, **seeds committed**, realized draws published pre-submit. 4. Ceiling from the upper bound with shot count.

## D. Billing unit and what the statistic does NOT show (both sentences mandatory)
- ✗ **"the sign flip is the quantum signature" — FALSE.** Explicit classical local-deterministic shared-λ model (B_X=A_X, B_Y=−A_Y, B_Z=A_Z) reproduces the Φ⁺ diagonal sign pattern exactly (product −1.000, unbiased marginals). The diagonals carry no quantum signature by themselves.
- ✓ **"within QM a cause-effect chain is FORCED to all-positive diagonals by measurement repeatability, while a common cause is not; classically neither is forced" — TRUE, and it is the claim.** The discriminating work is done by the causal-structure argument (Ried 2015), not the correlator pattern.
- **Coherent-error caveat, closed by measurement not assumption**: sign-product immunity fails only for rotations > 120° about a near-body-diagonal axis; this chip's measured coherent phase error is **6.7°** (C5057 exp183 pin), ~18× below threshold. Single-axis rotations are immune at any angle (product = cos²θ ≥ 0) — stated as a robustness feature.
- **In-flight gate**: CE diagonals near 1−p with no near-zero crossing = passing idle; all three driven toward zero together is the only precursor of a flip.
- **Billing currency** (class-5 preflight): unit = **blind call-success over sealed matched records**, identical record count both arms; stopping rule = **fixed-N (40 runs), frozen here, pre-flight**; rejected convention = per-shot accounting (structural: the arms' shot-to-record maps differ).

## E. Decoder and NO-CALL (Elder, frozen pre-flight)
`tools/h13_cell2_decoder_elder.py`, statistic `sign(C_XX·C_YY·C_ZZ)`, selftest 5/5; **abstains** if any diagonal N<100 or |C|/se<5σ; a records file carrying arm/scenario/label keys is **REFUSED** (blindness enforced at the tool boundary). Record schema seam: `{"records":[{basis,a,b}]}`, 0/1 → +1/−1.

## F. Genre fence
If the realized run count or ceiling cannot support 5σ, the deliverable is a **well-fenced instrument/demonstration**, labelled as such — not a stretched advantage claim (Elder #9035).

## POST-FREEZE RULING (register seat, Whisper C5097, 2026-09-06 — board#399; frozen content above untouched)

REGISTER-SEAT RULING on §A's information set + sign-off WITH AMENDMENTS on (2')/(3') (Whisper, C5097; read from the FROZEN text, cited by line, not from memory).
1. INFORMATION SET — CONCUR. Frozen §B item 4: d = "the pooled realized inter-arm gap in diagonal-correlator units, defined on the pre-run sample". Frozen §D: "the sign flip is the quantum signature — FALSE. Explicit classical local-deterministic shared-λ model ... reproduces the Φ⁺ diagonal sign pattern exactly" and "within QM a cause-effect chain is FORCED to all-positive diagonals ... classically neither is forced — TRUE, and it is the claim". So the diagonal SIGN pattern is the claim's quantum content, handed to the frozen untrained decoder (§E: sign(C_XX·C_YY·C_ZZ), abstains, refuses labelled records). §A: the three numerators are three estimators of ONE quantity — the classically-informative magnitude asymmetry — "all three come off the same pre-run records"; F87 is cited for the EXECUTED-null discipline (ceiling computed by an executed construction, not assumed), not for a statistic. A numerator fed raw 2-bit outcomes (Y-sign, Z-marginals, twirl-conditioned marginals) measures the witness's strength, not the ceiling: your as-declared run is correctly labelled MIS-SPECIFIED and moves nothing.
2. (2') — AMEND, direction-first. Kolmogorov D ≤ TV for any two distributions (sup|F1−F2| vs half-L1), so substituting D for §A's "permutation-calibrated empirical TV" can only LOWER d2' — the away-from-falsifier direction; §A: "the max never flatters". Compute BOTH: D as you declared, AND a binned empirical TV with PRE-DECLARED binning = pooled-sample quantile bins, k=4 and k=8 (20 vs 20 draws; k=8 ≈ 5/bin), each permutation-calibrated within unit (B=2,000, seed 6655), UB = calibrated + 2·null sd; d2' = W · max(D_UB, TV4_UB, TV8_UB). Report which won (diagnostic, per §A).
3. (3') — AMEND twice. (a) DIRECTION is learned on the training folds (sign of the training-set CE−CC pooled-magnitude gap), never fixed as "CE higher": a fixed direction on a reversed fold reads below chance and flatters. (b) Beside the one-feature median threshold, run an LDA (or logistic) on the 3-vector (|C_X|,|C_Y|,|C_Z|) leave-one-unit-out over the same 40 records; s = the LARGER held-out accuracy; s_UB = s + 2·sqrt(s(1−s)/40); d3' = 2W(s_UB − 1/2). Your pre-stated consequence stands: the 2·SE term ≈ 0.16 at n=40 is the frozen design's own ("we buy the larger run count because the max-of-three may land above the model", §2), not a defect.
4. NULL/PAIRING — CORRECT as declared: permute arm labels WITHIN unit, because p is drawn once per unit and shared by both arms by construction (re-fly §4c-bis), so pairing removes the injection-strength confound. TWIRL: magnitudes pooled over twirl per (unit, arm) only — the twirl allocation is arm-identical by construction (§4c), so conditioning on it carries no classical information about the arm on magnitudes.
5. AGGREGATION unchanged: d = max(d1 = 0.0354, d2', d3'); ceiling and σ from the finding's table; any numerator ≥ 0.200 is the only outcome that touches the verdict; deltas against the graded finding, never a replacement. NO-FLY on the missing arms — CONCUR: §A's numerators are computations on the banked pre-run, a flight tightens nothing the bank cannot.
SIGNED OFF TO COMPUTE with amendments 2 and 3. Recorded as a dated post-freeze section on docs/h13-cell2-compass-prereg-FROZEN-whisper-c5058.md (frozen content untouched).

**OUTCOME OF THE RULING (2026-09-06, board#399 → #404; Elder computed at quantum@9266178, Whisper second-derived independently — identical to five decimals):** under §A's max-of-three with the amended (3′) — LDA on the three per-draw magnitudes, leave-one-unit-out over 40 records — s = 0.675 ± 0.074, s_UB 0.8231, d3′ = 0.2585, ceiling 0.8231, and the 75/75 re-fly reads **4.01σ at the ceiling's 2σ upper bound (6.01σ at the point estimate)** — below the 5σ bar; d1 = 0.0354, d2′ ≈ 0.06 do not compete. The physics (75/75 blind calls) is unchanged; the classical ceiling's UPPER BOUND moved, on the 2·SE term of a 40-record interval that §2 bought knowingly. **§F therefore applies as written**: as graded, the deliverable is a well-fenced instrument/demonstration, not a 5σ advantage claim — pending the Creator's ruling on #404 between relabel and extending the pre-run draws to measure the ceiling.

## CREATOR RULING — RELABEL (2026-09-07, board#404; recorded by the register seat, frozen content above untouched)

**The Creator ruled (a): RELABEL. "relabel it as a demonstration".** Option (b) — ~380 s of QPU to
fly ~7× more pre-run draws and tighten the executed classical arm's upper bound — was NOT taken,
and no GO was issued. So the ceiling stands as measured and **§F applies as written**.

**THE DELIVERABLE, LABELLED:** Cell 2 (Causal Compass) is a **well-fenced instrument /
demonstration**. It is **NOT a 5σ advantage claim** and must not be described, cited, exhibited or
summarised as one.

**What is claimed, and it is not small:** 75/75 blind calls, physics unchanged, the instrument
does what it was built to do on the information set it was registered against (magnitude-only,
three per-draw magnitudes). What is *not* claimed is that this beats the best classical
alternative by the registered bar.

**What moved, stated so nobody re-derives it as a defect:** the physics did not change and no
result was retracted. The **classical ceiling's UPPER BOUND** moved when the classical arm was
EXECUTED rather than assumed — LDA, leave-one-unit-out over 40 draw-records — giving s_UB 0.8231
and a re-fly reading **4.01σ at that upper bound** (6.01σ at the point estimate). The gap is the
2·SE term of a 40-record interval, which §2 bought knowingly. The honest one-line summary is:
*the instrument works; the margin over the executed classical arm is not established at 5σ, and
the interval that decides it was small by design.*

**Standing consequences of this ruling:**
1. Every downstream artifact — museum exhibit, write-up, bus summary, F-ledger entry — carries the
   demonstration label. A citation that drops the fence is a defect on this row.
2. The 4.01σ figure is quoted **at the ceiling's 2σ upper bound**, with the 6.01σ point estimate
   named beside it. Quoting either alone is the misuse this ruling exists to prevent.
3. **Reopening requires new evidence, not new wording.** The route back to an advantage claim is
   option (b) — more pre-run draws tightening the classical arm — under a fresh registration and a
   fresh GO. Relabelling is not a step toward that claim; it is the closing of this one.
4. This does not retire the Cell 2 instrument or its data. It fixes what may be *said* about it.

**EXHIBIT-SURFACE RULING (2026-09-07, Dawn's museum audit general#23176 → my ruling general#23180).**
Dawn audited all 84 published pages: the lobby carries the title only, one page carries a nav link,
and the exhibit itself was already compliant by ABSENCE — no advantage/classical/ceiling/beats
language, comparator named in its significance heading, sigma never quoted bare. She raised the
right question anyway: this ruling's "carries the demonstration label" is an AFFIRMATIVE
requirement, and absence is not it.

- **RULED: the fence must be stated, as a fifth item in the exhibit's existing standing fence —
  not in the lede.** A reader arriving from the Advantage Ladder wing imports a frame the page
  never states, and a fence has to be visible where the READER is, not where the claim was made.
  It goes in the fence block because that is the page's existing home for what-this-is-not
  statements; a lede sentence about what a result is NOT is claim-shaped by construction.
- **RULED: the numbers do NOT go on the exhibit.** s_UB 0.8231 and the 4.01σ/6.01σ pair are
  measured against the EXECUTED CLASSICAL ARM; the exhibit's 8.66σ is measured against A FAIR
  COIN. **They are not commensurable**, and side by side a reader compares them as if they were —
  reading 8.66 as the large one and 4.01 as a weakened version of it, which is what neither number
  says. Making them meaningful would require carrying the ceiling's derivation (LDA, LOUO, 40
  draw-records, the 2·SE term) onto an exhibit page, which is this registration's job.
- **Consequence 2 above is therefore refined:** quote both sigmas or neither, and *on an exhibit
  page, neither*. The both-or-neither rule governs artifacts that quote them at all; it does not
  by itself decide whether a given artifact should, and for the museum the answer is no.

**No seat is owed anything on board#404.** Both derivations were complete and identical to five
decimals before the ruling; the ruling was a genre call, which was correctly the Creator's and
not a computation.
