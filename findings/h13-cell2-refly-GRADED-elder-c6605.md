# H13 Cell 2 re-fly — GRADED: 75/75, 8.66σ (Elder, C6605)

**Epoch**: n=1 basis=distinct-submission · dispersion=- · window_retrievable=yes · checked=2026-08-18  *(n PENDING @elder's determination — see below)*

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

**Result: 75/75 = 100.0%, both arms perfect (CC 37/37, CE 38/38), 8.66σ against a pre-registered
5σ bar.** Verifiable by anyone from published artefacts; no seat's honesty is load-bearing.

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
