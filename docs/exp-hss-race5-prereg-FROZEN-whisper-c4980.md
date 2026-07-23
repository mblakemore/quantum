# Exp-HSS Race 5 — PRE-REGISTRATION **FROZEN** (2026-07-23) — the graded attempt

**FREEZE RECORD**: Creator go (general#637, "Go 5"). Ember 2 fresh seals quantum@b26e0d8
(#640: rung0_n40 08009946…, race_n40 aab3c1bd…; GREEN on both changes; stuck-vs-tilted failure
mode (d) adopted). Elder ACK #641 (both changes match his shape exactly; win-legitimacy
affirmed: exclusion-dropped safe because the validated cal block absorbs tilts at zero quantum
cost, graded on the atomic 2⁻⁴⁰ null, cap frozen pre-transpile; min-d2q routing = the honest
WIN-maximizer). This commit is the freeze.**

*Whisper C4980, 2026-07-23, substrate claude-fable-5. Creator directive (general#637): "Go 5."
Shape agreed by full court in the race-4 record (Elder #626/#634, Ember #625): drop exclusion,
decoder-side hygiene only, shallow routing, cap raised toward the demonstrated boundary. Court:
same 3-of-3. Freeze = commit with DRAFT removed after Ember's 2 fresh seals + Elder ACK.*

## Changes vs race-4 (exactly two; everything else held)

1. **Routing exclusion DROPPED.** Plain best-of-100 transpile (min d2q, no layout filter).
   Rationale, measured: exclusion cost +92 depth slots and killed n32 outright, while the
   race-4 cal block absorbed three fresh tilted qubits at zero quantum cost — decoder-side
   calibration is the scalable, die-agnostic hygiene (pattern: mitigate in the estimator, not
   the resource).
2. **Depth cap RAISED 180 → 200.** The race-4 clean-register boundary is demonstrated exact at
   ≥217 (t=0) with the same calibrated decoder; 200 keeps a 17-slot margin below the
   demonstrated boundary while clearing the expected shallow routing class (125–160 measured
   this week). Anti-cherry-pick unchanged: cap frozen NOW, pre-transpile; cap-miss ⇒ Path B
   ungraded, Path A still measured.

## Held from race-4 (by reference): the validated machinery

Whole-chip readout-cal block (all-0/all-1, 20k) · graded statistic = CALIBRATED PER-BIT
MAJORITY (t_i = (p01_i+1−p10_i)/2; atomic 2⁻⁴⁰ null; Chase/soft diagnostics only; NO rescue) ·
depth-matched twin (Path-A differential + Path-B gate at race depth, twin must decode EXACTLY) ·
n=40 only · exactness gate + logical convention round-trip · two-stage reveal (ŝ before
reveals; rung-0 first) · flagged-bits list emitted pre-reveal · cal-block QPU excluded from the
decoder wall via per-circuit attribution (Elder #605) · ρ_t at the matched depth with 1k-pub
bootstrap (my seat, Elder co-check; quoted as the SECOND clean-register point — the race-5
depth plus race-4's 217 begin the clean multi-depth set Elder's #630 caveat requires).

## The job (~58 pubs, 360k shots ≈ 105–120 s of ~2,639 s pool)

| Block | Structure | Shots |
|---|---|---|
| READOUT-CAL | all-0 + all-1, measure_all | 20k |
| LADDER | t=0 base, m ∈ {0,1}, 4 twirls × 5k | 40k |
| TWIN n=40 | t=0 padded to d2q_race40 exactly, 16 twirls × 6,250 | 100k |
| RACE n=40 | t=80, 32 twirls × 6,250 | 200k |

Marrakesh default (standing rule, queue-checked at freeze). Seals: Ember, 2 fresh strings
(rung0_n40 shared by ladder+twin; race_n40), hardened 0-indexed format.

## Frozen decision rules

1. **CAP**: race_n40 advantage-eligible iff best-of-100 d2q ≤ **200**.
2. **GATE**: twin40 decodes EXACTLY (calibrated majority, full 100k).
3. **WIN (Path B — the graded attempt)**: exact ŝ==s on race_n40 (calibrated majority) AND
   re-measured quantum wall (smallest exactly-decoding pre-registered subsample of
   {2,4,8,16,32} pubs; per-circuit attribution excludes the cal block) ≤ **1/10 of Elder's
   frozen t=80 band lower edge at EVERY edge** (binding: fastest-classical edge_4500× floor
   1,818 s ⇒ quantum wall ≤ 181.8 s). Supersedable-by-design printed on the result.
4. **Path A**: ρ_t(d2q_race) with bootstrap CI — second clean-register point.
5. **Named failure modes**: (a) fresh wrongward tilt of circuit-dynamics origin on a race bit
   (cal block attributes it; MISS booked); (b) routing lottery lands > 200 (cap branch, Path A
   only); (c) twin fold (gate branch); (d) *Ember #640, adopted*: a FULLY-STUCK qubit (frac
   pinned ~0/1 regardless of input) landing in the unexcluded routing — threshold-UNcorrectable
   by construction (no t_i recovers a bit the qubit never encodes; race-4 validated the decoder
   on a clean register, tilt-rescue ≠ stuck-rescue). Expected signature: clean 1-bit MISS,
   immediately localized by the emitted per-bit frac + cal rates. Every branch a deliverable;
   no rescue anywhere.

## Fences

Best-known-simulator engineering race, not a complexity theorem (Exp142/F119 distinct
currency). t=0 blocks classically free. All prior verdicts stand; all prior reveals resolved
or retired. A WIN, if graded, is stated with its fences: one instance family, one die, named
classical solver band (Elder C6563 edge-robust, anti-flattering), joules one-sided per G2.
QPU after this job ≈ 2,520–2,535 s; no further HSS spend without a fresh card.
*Contact: Mike Blakemore.*
