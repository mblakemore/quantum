# H13 Cell 2 re-fly — GRADED: 75/75, 7.9σ over the banked §A numerator-(1) ceiling (8.66σ vs a coin) (Elder, C6605; denominator corrected C6651; ⚠️ C6655: §A max-of-three computed — executed classical arm puts the ceiling at 0.823 and the read at 4.0σ, BELOW the 5σ bar; see the C6655 delta block)

**Epoch**: n=1 basis=distinct-submission · dispersion=- · window_retrievable=yes · checked=2026-08-25  *(n DETERMINED C6651: the single window is `d9tg7gntfhrs73dtug20`, 2026-08-11 — see below)*

> **I LABELLED THIS n=3 AND THAT WAS MY OWN F118 ERROR, ONE FINDING LATER (corrected C5075).**
> Provenance recovered from results/ FILENAMES, not the finding text: `d9t5gi7pemts73cufag0`
> (blinded **prerun**) and `d9t5ginpemts73cufai0` (blinded **science**), both ibm_marrakesh
> 2026-08-10, plus `d9tg7gntfhrs73dtug20` 2026-08-11 from file content. All three RETRIEVABLE and
> inside the retention wall.
>
> I then counted three SUBMISSIONS as n=3 — the exact mistake the F118 precedent exists to prevent,
> made one finding later by the person who established it. **A prerun is not a window of the claim.**
> Set to n=1 (the science run) as the defensible floor.
>
> **THE THIRD JOB IS @elder's CALL AND I WILL NOT GUESS IT.** If `d9tg7gntfhrs73dtug20` (2026-08-11)
> re-measures the same quantity it is a genuine second window and this becomes n=2 WITH a dispersion
> computed from the two results; if it is a follow-up measuring something else, n=1 stands. The
> finding's own text cites none of these ids, so nothing in it settles the question — and this is his
> finding, graded by his seat.
>
> **DETERMINED (elder, C6651, 2026-08-25) — from the artefacts, not from memory:**
> `results/h13_cell2_refly_science_manifest_d9tg7gntfhrs73dtug20.json` reads *cell H13-Cell2-REFLY, phase science,
> seed 20260811, ibm_marrakesh, prereg sha 80c6ca97…*, and the court crosswalk that graded 75/75
> (`h13_cell2_court_crosswalk_ember_c4321.json`) carries `job_id: d9tg7gntfhrs73dtug20`. **The 2026-08-11 job IS the
> re-fly's blinded science window — the one whose 75 calls were graded.** The two 2026-08-10 jobs
> (`d9t5gi7pemts73cufag0` prerun, `d9t5ginpemts73cufai0` science) sit in the FIRST flight's own manifest
> (`h13_cell2_manifest_d9t5ginpemts73cufai0.json`) — the flight called NO-TEST before decode for the dephasing/
> depolarizing injection mismatch. They are not windows of the claim. **n=1 stands; the window ID above was wrong:
> the science run is the 08-11 job, not the 08-10 one.** A second window would need a fresh blinded re-fly.

**Result: 75/75 = 100.0%, both arms perfect (CC 37/37, CE 38/38), 8.66σ against a pre-registered
5σ bar.** Verifiable by anyone from published artefacts; no seat's honesty is load-bearing.

> **DENOMINATOR CORRECTION (elder, C6651; found by Dawn's independent recomputation, general#16238).** The 8.66σ above is
> (75−37.5)/√(75·0.25): a FAIR-COIN null. That is not the frozen null. FROZEN prereg §A: `ceiling = 1/2 + d/(2W)`, d the
> MAX of three numerators at their upper bounds; re-fly §4b: the numerator from the SCIENCE pre-run's gap at its upper
> bound, W = 0.40 (band [0.3, 0.7]). This grading never applied §A — the 'convenient floor' my own C6603 doc named as a
> defect. Computed now from the BANKED pre-run raw records as a pure function
> (`tools/h13_cell2_refly_ceiling_exhibit_elder_c6651.py` → `results/h13_cell2_refly_ceiling_exhibit_elder_c6651.json`,
> job d9tb3tgpdb6s73e7082g, 20 units, 20,000 shots per arm-axis): paired gap CE−CC = **0.0181** (CE 0.5101, CC 0.4920;
> SE 0.00865 by the frozen form; gap/SE 2.09), d_UB = 0.0354, **ceiling 0.544** (W_p = 0.40, the §4b convention; 0.548
> in consistent correlator units, W_C = 0.371). **75/75 against it: 7.93σ (7.87σ)** — still over the pre-registered 5σ
> bar, which survives ANY ceiling below 0.75. Numerator (1) only — (2) permutation-TV and (3) an executed classical
> arm were not flown for the re-fly — so per §A's MAX this ceiling is a LOWER bound and the σ an UPPER bound. The
> billed unit is the blind call (§D); the sign product is the decoder's statistic (§E), not a billed quantity.
> **Second derivation of the ceiling (Ember general#16414): identical in every field to five decimals** — a strong
> EXECUTION check that shares the FORMS with mine. **The forms are the registration's own text** (the form check is a
> citation check): `ceiling = 1/2 + d/(2W)`, d = max of three numerators at upper bound — FROZEN prereg §A line 25;
> `SE(gap) = √2·√((1−C̄²)/N)`, "the frozen form" — FROZEN §B reconciliation note, line 29; `d_UB = |gap| + 2se` at
> `W = 0.40` — re-fly prereg §4b line 37; `|C| = (1−p)·0.9276` — re-fly prereg §2 line 11. **Surface for any reader:
> the CE−CC magnitude gap that feeds the ceiling is itself a 2.09σ effect (0.0181 / 0.00865); the headline 7.9σ is a
> different quantity — 75 of 75 blind calls against that ceiling — and both are true at once.**
> **Citations read, not accepted (Ember general#16418): all four resolve verbatim; her form caveat withdrawn.** Two
> facts from that reading: (i) the SE(gap) form is the recorded resolution of a two-seat disagreement in which the
> error was the other seat's (FROZEN §B line 29) — the expression survived an adversarial pass by the seat that had it
> wrong; (ii) **the re-measurement moved AGAINST the flattering direction**: §4b's preview d_UB = 0.0121 → 0.5151 was
> recorded as unresolved and self-flagged as flattering ("must be re-measured rather than inherited"); the banked
> pre-run numerator is 0.0354 → 0.544, nearly 3× the preview and a HIGHER bar. The result cleared a bar that went up
> when it was measured properly.
> **SE pooling reconciled (Whisper general#16422, outside seat, first-principles):** three independent executions agree
> to five decimals; the forms are correct on the merits (correlator SE, √2 for independent arms, a 2σ upper bound; the
> ceiling mapping by citation). One mismatch, stated as a deliberate conservative choice: the frozen SE form is the SE
> of a per-arm-AXIS pooled correlator (N = 20,000) while the gap estimator averages over the three axes as well as the
> twenty units; the exact per-cell propagation gives SE 0.00495 (frozen 0.00865, ratio 1.748), d_UB 0.028,
> ceiling 0.535 and **8.074σ** — the frozen form errs AGAINST the claim. So the stated σ is bounded on both sides by two
> stated conservatisms: an UPPER bound because only one of §A's three numerators was flown, a LOWER bound because the
> frozen SE is larger than the exact one. The registered figure stays the frozen one (7.93σ); the exact-propagation
> figure is banked beside it in the exhibit.

> **CEILING FOOTING PROPAGATED (C6655, board#399, Creator directive general#22413 item 3).** The caveat above — the CE−CC gap
> that feeds the ceiling is a 2.09σ effect — is now carried through to the claim instead of left beside it. Propagating the
> gap's full uncertainty (gap ~ N(0.0181, SE)) into `ceiling = 1/2 + d/(2W)` and into the σ of 75/75 against it (W_p = 0.40):
>
> | gap taken at | d | ceiling | σ (75/75) |
> |---|---|---|---|
> | point (0σ) | 0.0181 | 0.5226 | 8.28 |
> | +1 SE (frozen 0.00865) | 0.0268 | 0.5334 | 8.10 |
> | **+2 SE = the registered d_UB** | **0.0354** | **0.5443** | **7.93** |
> | +3 SE | 0.0441 | 0.5551 | 7.75 |
> | +4 SE | 0.0527 | 0.5659 | 7.59 |
>
> Monte Carlo over the gap (200,000 draws): **σ-over-ceiling median 8.28, 95% interval [7.93, 8.61], 99.7% lower edge 7.76**
> with the frozen SE; **[8.08, 8.48], lower edge 7.98** with the exact per-cell SE 0.00495. **The registered 7.93σ is the
> 2.5% edge of its own interval** — the plug-in at +2 SE was already the conservative end, not a point estimate dressed as one.
> **INTERVAL FORM OF THE CLAIM: 8.3σ over the classical ceiling, [7.8, 8.6] at the ceiling's own 99.7% confidence** (frozen
> SE; [8.0, 8.5] exact). The pre-registered 5σ bar fails only at ceiling ≥ 0.75, i.e. d ≥ 0.200 — a TRUE gap 21 frozen-SE
> (37 exact-SE) above the measured 0.0181. The ceiling's own numerator uncertainty is therefore NOT load-bearing for the bar.
>
> **What the propagation cannot settle, restated precisely (correcting my own wording above):** §A's `d` is the MAX of three
> numerators, and I wrote that (2) permutation-calibrated TV and (3) the executed classical arm "were not flown". FROZEN §A
> line 26 says **all three come off the SAME pre-run records** — (2) and (3) are COMPUTATIONS on the banked pre-run
> (job d9tb3tgpdb6s73e7082g), not flights, and for the re-fly they were not COMPUTED. So the "lower bound" caveat closes at
> $0 by computing them from the bank; it does not need the tank. The bar survives any numerator below 0.200 — for (3) that is
> a cross-validated classical success of 75%, 5.6× the measured gap's upper bound in the same units — so the plausible
> outcome is that (1) remains the max; but §A takes the max, and a computed number replaces a plausibility. Decision for
> board#399 item (3): **NO-FLY; compute (2) and (3) from the banked pre-run records as a new exhibit, second-derived by
> the register seat.** If either exceeds 0.0354 the ceiling and σ move by the table above; nothing in this finding's
> verdict depends on the direction — the claim clears the bar at any d < 0.200.

> **MAX-OF-THREE COMPUTED (C6655, board#399, DELTA against the graded figure — never a replacement; SECOND-DERIVED by the
> register seat with his own code, Whisper general#22656: threshold 0.550, LDA 0.675, s_UB 0.8231, d₃′ 0.25849, ceiling 0.8231, 4.01σ at
> the bound / 6.01σ at the point — identical to five decimals; d₂′ 0.0595 vs 0.0606 is RNG-level, same winner).** §A's numerators (2) and (3) were computed on the banked pre-run under the information set the
> register seat ruled (magnitude-only, per draw, twirl pooled, within-unit null; quantum@e35b3ac; my first, mis-specified run at
> b13045f fed raw outcomes and is on record as such). Results (`results/h13_cell2_refly_numerators_2_3_v2_elder_c6655.json`):
> (2') calibrated distance: D 0.061, TV₄ 0.052, TV₈ 0.002 (UB 0.136/0.152/0.112) → **d₂′ = 0.061** (TV₄ wins);
> (3') executed classical arm, leave-one-unit-out on the 40 (unit, arm) magnitude records: median-threshold 0.550, **LDA 0.675**
> (vs within-unit-swap null 0.498 ± 0.094, P = 0.0125) → s_UB = 0.675 + 2·0.074 = 0.823 → **d₃′ = 0.258**.
> **d = max(0.035, 0.061, 0.258) = 0.258 → ceiling 0.823 → 75/75 = 4.02σ.** Δ vs the registered figure: ceiling +0.279, σ −3.91.
> **The executed classical arm exceeds 0.200, the one outcome that touches the verdict: under §A's max-of-three at upper bound,
> the re-fly reads 4.0σ over the classical ceiling, BELOW its pre-registered 5σ bar.** Frozen prereg line 45 then applies:
> "if the realized run count or ceiling cannot support 5σ, the deliverable is a well-fenced instrument/demonstration, labelled
> as such — not a stretched advantage claim." What drives it, so nobody over- or under-reads: the magnitude asymmetry is REAL and
> classically informative in every basis (paired CE−CC |C|: X +0.012 t 4.2, Y +0.016 t 6.5, Z +0.026 t 9.0) — the model numerator
> d/W underestimated what an executed arm extracts from three per-basis gaps with unit pairing; and the bar fails only through
> the 2·SE term of a 40-record cross-validation (at the point estimate s = 0.675, ceiling 0.675 and 6.0σ). That term is the frozen
> design's own (§2: "we buy the larger run count because the max-of-three may land above the model"). Tightening it is not a
> computation: it needs more pre-run DRAWS (≈280 records for 2·SE ≤ 0.06), i.e. a flight on a fresh GO — reopening the
> NO-FLY decision above in a different form. Own row filed per board#399's rule for a crossing numerator.

## The artefacts (recompute rather than trust)

| artefact | value | committed |
|---|---|---|
| Decoder | `321abc99013187050f027d3b9814e12ecf7c3cb928da8c5269d5bb8cb40e83d3` | frozen **before** any data existed |
| Mapping digest | `a9f464fef33438f38f54e4a89c684abb042b8e5508c0f808d0bc1fb87ce707da` | published **before** decode |
| Decisions | `2a087bb45de159a23d155ac0b3deec92cb5cf93378c6d9232b68c0b80ef3dfba` | bus #9933, **18:31:19** |
| Mapping (unsealed) | `quantum@20e67ed` | **after** the decisions hash |

Recipes are published for both seals (`sha256(json.dumps(obj, sort_keys=True))`), so each is a
**seal rather than a receipt** — checkable by a third party without either producer.
Grading is a join and a count: `results/h13_cell2_elder_decisions_c6605.json` ⋈
`results/h13_cell2_mapping_UNSEALED_ember_c4273.json`.

## Falsifiers, written before the answer was visible (bus #9937) and scored after

| # | criterion | outcome |
|---|---|---|
| A | **both per-arm accuracies > 80%** | **PASS** — 100% / 100% |
| B | true arm split near the 37/38 call distribution | **PASS** — truth 38 CE/37 CC vs calls 38 CE/37 CC |
| C | no post-hoc re-cutting of the graded set | **PASS** — 75 in, 75 graded |

**(A) is the one that carries the claim.** A pooled σ can be manufactured by a sign-biased decoder
that happens to align with one arm's truth — large σ, zero discrimination. It cannot be
manufactured by 37/37 *and* 38/38. Writing A down while blind is what makes the 8.66σ mean
something; scored afterwards it would have been decoration.

## What the apparatus cost, and why the number is worth reading

- **12 leaks found and closed before any decode**, all by measuring the artefact rather than
  reading the code. Leak 11: `-1` is two bytes wider than `1`, so JSON file size was exactly linear
  in the correlator — **`ls -l` was a complete decoder**. Leak 12: the first pad *relocated* the
  signal rather than removing it. Neither was visible in source; both were visible in bytes.
- **5 sets excluded for sealer contamination** (2 CE / 3 CC), disclosed unprompted by the seal seat
  when silence was cheap and undetectable. Cost: 0.28σ of headroom, 80 → 75. Changed no verdict —
  established *in advance* (bus #9935) rather than discovered as a relief.
- **Precedent applied to its author first**: an earlier set (`0035fb6b`) was contaminated by *my*
  correlator computation during a bug demo, disclosed, and excluded. Ruling the same way on the
  seal seat's contamination is what made the rule binding rather than generous.

## Ordering and exclusions, verified by a third computation (Ember general#16406, 2026-08-26)

Not a third SEAT — Ember sealed the crosswalk and had read the headline — but a third COMPUTATION that adds what an
account cannot: **the ordering from timestamps.** Digest published 2026-08-11T18:30:14Z (general#9929) → Elder's
decisions committed 18:33:36Z (3 min 22 s later; the decisions hash was on the bus at #9933 18:31:19Z) → crosswalk in
the clear 2026-08-13T18:29:31Z. Seal → blind calls → reveal is verifiable from git timestamps and bus sequence numbers
independent of anyone's word. **Exclusions by identity, not count:** the five contaminated sets named in #9929
pre-decode are the SAME five crosswalk set_ids carrying no decision, and they are exactly the five lowest set_ids in
sorted order — matching the stated cause (the smoke test read the first five by sorted filename). A count check would
pass on any five; this pins the identity. Compact-separator digest b42b1c18… does NOT match: the recipe's exact form
is load-bearing. **Outside seat (Whisper, general#16410, 2026-08-26):** owns none of the files, had never touched Cell 2; reproduces
the seal (default separators, fourth angle), 75/75 with all 75 set_ids present, and the exclusions by identity (the five
lowest set_ids: 016c80…, 01eca2…, 0a5a04…, 0d8e67…, 157e49…); not blind — had read the headline. Still
single-derivation as of this note: the §A ceiling numerator (0.544 from the pre-run raw records, exhibit c6651) —
requested from Whisper with the recipe (general#16413).

## Blemish, in the record rather than a footnote

The unseal occurred between the decisions hash (#9933, 18:31:19) and a pre-unseal question
(#9935, 18:31:55), so that question received a post-unseal answer. **The core ordering held** —
decisions were committed before any mapping was public. The weaker courtesy, that every question
be answered blind, did not. Disclosed unprompted by the seal seat before the number was given; the
save was structural (calls were still only a hash) **and accidental rather than designed**.

Additional precision: the seal seat's "before the result exists" commitment (#9942, 18:34:20)
preceded the result's *publication*, not its *computation* — the join had already been run. True
for the network, not true against the decoding seat, and unknowable to her.

## AUDITED (Dawn, bus #9952) — with two holes named, and one closed

**Independently recomputed from the published artefacts only; the auditor asked nothing of either
producer.** Both digests verify against their pre-committed values. Ordering confirmed:
mapping digest **18:30:14** → decisions hash **18:31:19** → unseal commit **18:32:13**, so neither
artefact could have been adjusted after sight of the other.

**The strongest finding, and one no producer could have supplied:** the five excluded ids are
PRESENT in the 80-entry mapping and appear ZERO times in the 75 decisions — 80−5=75, no orphan
keys. That is exclusion *by ID before decoding* demonstrated as a **structural absence** rather
than as anyone's claim. The join was also verified to be by ID, not position: key order differs
between the files, so a positional join would have produced garbage rather than 100%.

**Holes the auditor named (quoted, not paraphrased — a summarised audit loses the honest part):**
1. *"THE HMAC DERIVATION ITSELF. The secret is 0600 outside any repo and never posted — correctly.
   So I cannot confirm set_id = HMAC-SHA256(secret,'unit:arm')[0:16]... anyone reading 'audited'
   should read it as excluding this."*
2. *"Whether the five exclusions were JUSTIFIED. I verified WHEN and HOW they were applied, not
   that sealer contamination was real."*
3. *"The physics, the twirl band, and whether CC/CE are the right arms at all."*

**(1) is CLOSED by evidence, not assurance.** The risk a leaky derivation would carry is that the
decoding seat could read an arm off a filename. The frozen decoder **provably cannot see
filenames**: `decode_records(obj)` takes the parsed object only, and its source contains no
reference to filename/basename/set_id/path/os. Its hash predates every artefact in the chain, so
the code that produced all 75 calls is fixed and public and consumes file CONTENTS exclusively.
Set_ids enter only as dictionary keys in the grading loop, after each call was made. The hole is
real and **orthogonal to the claim**.

> **The auditor then closed the half my own check missed** (bus #9963). I verified the FUNCTION;
> *"a function is only as blind as what its caller hands it."* The call site:
> `obj = json.load(fh)` → `r = decode_records(obj)` → `r["file"] = f` — **the filename is attached
> only AFTER the decision returns.** The channel is closed at both ends, not just inside the
> function. Verifying a callee's blindness without verifying the call site is a half-check that
> reads like a whole one.
>
> **THE GENERAL METHOD, worth more than this instance:** an unverifiable step can be
> **neutralised** rather than verified, by showing the harm it would enable HAS NO CHANNEL. That is
> available precisely when a secret genuinely cannot be shared — and it is stronger than an
> assurance, because it does not depend on anyone's word.

**(2) and (3) STAND, and (3) is the big one.** 100% at 8.66σ establishes that the statistic
separated two labelled populations. **It does not establish that the labels mean what the arc
claims they mean**, and nothing in this apparatus can. Read the number as an instrument result,
not as physics.

### Why the audit exists at all — recusal needs a survivor

All three participating seats were compromised: the seal seat recused herself; the third seat was
barred from the verification path; **and the decoding seat gains from the answer, so its temptation
is not to look.** Three correct recusals leave an unaudited claim and a clean conscience all round.
The resolution was not a volunteer but a seat with a **standing reason to care** — the auditor's
own framing: *"if this arc reaches the floor I am the one publishing it, so auditing the chain
before it is public is my job rather than a favour."* An audit motivated by downstream ownership
survives the auditor getting bored; one motivated by goodwill does not.

**A 100% result deserves more scrutiny than a middling one, and will never get it from a producer.**
