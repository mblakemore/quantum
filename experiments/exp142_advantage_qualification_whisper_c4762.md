# Does Exp142 qualify as a submittable quantum advantage? — Whisper C4762 (2026-07-17)

Creator question after the graded WIN (frozen grader, 3-of-3 reveal verification, Elder
email sent). Assessment against three bars: the Quantum Advantage Tracker, the field's
bar for this result class, and our own venue rule.

## 1. Quantum Advantage Tracker: structurally OUT OF SCOPE — wrong shape, not too weak

Tracker criteria (re-fetched 2026-07-17, consistent with the C4743 review): scope is
**computational tasks** in three categories — observable estimation (expectation values
+ rigorous error bars), variational (ground-state energy upper bounds), classically
verifiable problems (scored against known answers/witnesses) — governed by a
**"superseded" mechanism**: candidates fall when classical algorithmic progress closes
the gap.

Exp142 is a **sample-complexity (learning) advantage**: the task is defined over
*physical sample access* to an unknown Pauli operation, not over a computational
instance. Two structural mismatches:

- A classical solver **cannot attempt our instance at all** — without quantum hardware
  access there is nothing to compute. The tracker's classical-vs-quantum leaderboard
  contest cannot be hosted on this task shape.
- The tracker's core mechanism (supersession) **does not apply**: within single-copy
  access, better classical strategies can improve constants (stabilizer is already
  ~2.3× better than our executed product-basis baseline, more at high noise) but the
  exponential floor is theorem-carried (CCHL, Gate-1-pinned conditions + the meeting's
  co-checked (3/2)^n floor). Scaling supersession is provably impossible in the model.

Same bottom line as C4743 for the F-series (provable-bound land vs contested-
computational land) — but for Exp142 the reason is *stronger*: the result is protected
by the very property that makes it ineligible.

## 2. The field's bar: genuine member of an ESTABLISHED class — a replication, not a first

The class exists and is published: **Huang, Broughton, Chen, et al., "Quantum advantage
in learning from experiments," Science 376:1182 (2022)** — Sycamore, up to 40 qubits,
~4 orders of magnitude fewer experiments (~10⁴× at n=20), same two-copy/Bell-sampling
paradigm, same CCHL theoretical foundation. A 2025-26 photonic follow-up (Science
adv2560) extends the class. Our n=10, 7,821× raw (≈240× vs best-known baseline) is
**smaller scale than the existing literature**.

Claiming novel science here would be an over-claim (C4713-16 taxonomy: framing-over-
reach). What Exp142 adds is **verification methodology**, not new physics:

- pre-registered frozen protocol (budgets, kill-gates, graded thresholds, hashes) BEFORE flight;
- cryptographically sealed ground truth committed before any shot flew;
- 2-of-2 blind independent decoding, every wave, answers committed before reading the sibling;
- BOTH arms executed on the same public hardware under the same noise (the conventional
  arm's 860k shots were real kingston shots, not simulated bounds);
- 6 protocol defects caught or prevented with zero reaching a graded artifact; full
  audit trail public in this repo.

Positioning that survives review: **"an adversarially-verified, pre-registered hardware
replication of the Huang et al. learning-advantage class on open-access IBM hardware,
with both arms executed on-chip."** Replications with stronger verification are real
scientific value — they are just not tracker material or a priority-claim paper.

## 3. Venue: the repo IS the venue (Creator directive C4594)

Per the standing rule (beyond-the-ladder precedent), venue-ready write-ups finish as
repo-native documents, not external submissions. Exp142's write-up already exists in
this repo: prereg + amendments + wave decodes + shot accounting + grader verdict +
reveal verification + results email. This assessment completes the record.


## Amendment A (C4763, chair-adopted from Ember): SINGLE INSTANCE PER RUNG

Verified against the commitment files: 4 commitments, 4 reveals, exactly ONE sealed P
per rung. The ratios 37x/168x/1,090x/7,821x are therefore **single-instance draws** —
meter medians average over shot/decode randomness at a FIXED P, not over the
fullweight_eps1 ensemble. No instance-level variance, no error bar across P; n=10
rests on one string. This does not weaken the WIN (ensemble and baseline were frozen
pre-flight; the seal precludes instance-shopping) but it bounds the claim: any write-up
printing 7,821x must carry "single instance, one P per rung" beside it, or it is the
framing-over-reach class (C4713-16). Honest next rung if effect SIZE is ever wanted:
seal k=5-10 P per rung and report the ratio distribution (~few hundred QPU-s).

## Verdict

- **Tracker submission: NO** — task shape is out of scope, and the supersession
  mechanism that defines the tracker cannot apply to a theorem-protected sample-
  complexity separation.
- **"Is it a quantum advantage?": YES, within its established class** — a correct,
  hardware-executed instance of the learning-from-experiments advantage, with a
  verification protocol that is (to our knowledge) unusually strong for the class — with the single-instance bound of Amendment A attached.
- **What it is NOT**: a first, a frontier-scale demonstration, or a computational-
  advantage claim of the random-circuit-sampling genre.
- **Action**: none external. The repo record is the deliverable. The genuine next step
  is the application, not the submission: point the Exp142 two-copy machinery at a
  string nature wrote — kingston's own Pauli error channel (noise-fingerprint readout),
  where the same math does useful work every flight thereafter.
