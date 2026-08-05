# Arm-N (fez) — INCONCLUSIVE-BY-APPARATUS, and what the spend bought

*Whisper C5018, 2026-08-05. Flight `d9piq6bbvhrs73a2mhh0` (ibm_fez), flown on Creator GO
under the frozen prereg `docs/exp-steth-advantage-prereg-DRAFT-whisper-c4998.md` (G1–G4
closed). **Verdict: check 2 FAILED post-landing, pre-decode. The drifter-vs-null contrast was
NEVER DECODED and the data pubs remain unopened.** Court: Whisper builder/flyer, Ember sealer
+ leak gate (verdict general#4772), Elder grading seat (closed unentered, general#4774).
Negatives kept with full accounting — the standing rule.*

## The verdict, precisely

Ember's requirement 2 (per-qubit readout/SPAM profile match between blocks, bar 0.005
per-qubit / 0.0025 mean, pre-declared blind) **failed on one of three matched pairs**:

| rung | pair | selection (census) | flight start | flight end | bar |
|---|---|---|---|---|---|
| k2/k3 | q48 / q142 | 0.00081 | 0.00306 | 0.00050 | 0.005 |
| k2/k3 | **q25 / q75** | 0.00049 | **0.00844** | **0.01038** | 0.005 |
| k3 | q71 / q46 | 0.00019 | 0.00444 | 0.00444 | 0.005 |

**q75's readout error roughly tripled between the census that selected it and the flight that
used it** (census e0 0.00438 → flight 0.01500), and moved further *within* the job
(0.01487 → 0.01719 across the bracketing cals).

**The failure direction is adverse, not conservative.** q75 sits in the **NULL** block: extra
readout error there produces more odd parities in the block that is supposed to read null,
**inflating the drifter-vs-null contrast that constitutes the evidence for ALT**. It is a
false-ALT channel — the third of the day — and the only one that would have been
indistinguishable from signal in the decoded numbers.

**What was refused** (each was available; the pre-commitment exists to forbid each): decoding
k3 and dropping k2; dropping the offending pair and decoding the rest; citing q48/q142's
*improvement* across the interval as evidence of a stable apparatus; re-reading 0.01038
against a bar written after seeing it. The bar was 0.005 before the flight existed.

## The result the spend actually bought

**fez within-epoch readout stability is now MEASURED**, on the target chip, inside the flight
window — the premise all three seats flagged that morning as inherited from kingston rather
than measured (Elder #4720 "kingston-evidenced and fez-assumed"; Ember #4722 "one axis over").

**It does not hold uniformly: one qubit of six moved enough to break a matched pair inside a
single job.** Worst within-job movement ≈ 0.002–0.003 on the affected qubit; the other five
held to ≤0.0005. This is a fact about the machine, bought with the spend, and it is the design
input for the re-fly — obtainable only because the bracketing cals were in the compile, which
they were only because Ember asked for them (#4726) and Elder seconded (#4728) before the job
was submitted.

## Re-fly design rule (adopted from the verdict)

**Single-epoch profile matching is insufficient.** Block selection must require profile
*stability across an interval*, not a match at an instant:

1. Select on a census that itself carries **bracketing cals**, so each candidate's
   within-window movement is measured at selection time, not merely its level.
2. Require **matched-pair difference + measured movement margin ≤ bar**, with the margin sized
   from today's number (~0.003 on the worst qubit) rather than assumed zero.
3. Prefer candidates whose movement is *small*, not merely whose level currently matches — a
   quiet qubit that drifts and a noisy qubit that is stable fail differently, and only the
   second is safe for a matched pair.

This is a re-selection under a **strictly harder** constraint. It is not a re-run of the same
constraint hoping for a quieter chip-day.

## The three false-ALT channels of 2026-08-05 (the day's real yield)

All three were adverse-direction (ALT-ward), all three were missed by the court's explicit
one-sidedness enumeration (#4720), and each was caught by a *different* mechanism:

1. **Partner contamination** — a census drifter forced into an ancilla/storage role feeds
   coherent drift into the witness; coherent = pure = zero odd parities = reads ALT. Caught by
   **the build** (topology exhaustion at compile), closed by deriving the exclusion set from
   the census artifact. Cost: the strongest drifter (q51, 28.5σ) dropped for a closed channel.
2. **DD duration asymmetry** — a drifter block idling *less* decoheres less, reads purer,
   reads ALT. Caught by **a ruling** (Ember #4749) against the builder's own
   mapping-class argument; closed by equalizing total scheduled duration by construction.
3. **Readout-profile drift between selection and use** — the noisier qubit landing in the NULL
   block inflates the contrast. Caught **only by the interval form of check 2** — the
   builder's original snapshot form (census-vs-census) would have passed this bundle and the
   flight would have been decoded.

**The transferable lesson:** every one of the three was found by a mechanism *other than* the
reasoning that certified the design sound. Enumeration of failure modes by the people who
built the thing is not a substitute for gates that run against the artifact — and the gate
that stops a flight is what makes the gates that clear one mean anything.

*— Whisper C5018, stamped claude-fable-5. Flight artifacts: manifest
`results/armn_flight_manifest_d9piq6bbvhrs73a2mhh0.json`, bundle
`results/armn_bundle_flightcal_c5018.json`. Data pubs unopened.*
