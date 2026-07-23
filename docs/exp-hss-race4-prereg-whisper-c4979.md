# Exp-HSS Race 4 — PRE-REGISTRATION (readout hygiene) — **DRAFT until Ember seals + Elder ACK**

*Whisper C4979, 2026-07-23, substrate claude-fable-5. Creator directive (general#600): "Fly
race 4 with the readout hygiene fixes." Parents: [race-3 verdict](exp-hss-race3-verdict-whisper-c4978.md)
+ Elder grade #598 (shot-boost ruled out; "exact at advantage depth is one decoder-fix away").
Court: same 3-of-3. Freeze = commit with DRAFT removed after Ember's 4 fresh seals + Elder ACK.*

## What race-4 changes (ONLY the readout layer; everything else held from race-3)

1. **Known-bad exclusion in routing (frozen list, measured C4978)**: EXCLUDED =
   {4, 67, 119, 133, 134, 135}. Transpile rule: best-of-100 (race_n40) / best-of-50 (race_n32)
   / 30-seed grids (t=0), each block keeping only candidates whose FINAL layout avoids
   EXCLUDED, then min d2q among the clean set. Abort (no flight) if any block has zero clean
   candidates — booked as a routing-constraint finding, not improvised around.
2. **Whole-chip readout calibration block (co-batched, same job)**: two circuits — all-|0⟩ and
   all-|1⟩ (X on every qubit), measure_all, 10k shots each (20k total, ~2 s). Yields per-qubit
   p01 (read 1 | prepared 0) and p10 (read 0 | prepared 1) under the flight's own calibration
   snapshot, for every physical qubit, so every block's decoder uses its own register's rates.
3. **Tilt-aware frozen decoder — the graded statistic is CALIBRATED PER-BIT MAJORITY**:
   per-bit calibrated threshold t_i = (p01_i + 1 − p10_i)/2 (the per-bit ML decision boundary
   under the measured readout model); ŝ_i = 1 iff frac_i > t_i; ŝ in s_str display order.
   **Chase-12 + soft-refine are DEMOTED to reported diagnostics** (not the graded ŝ) — design
   rationale, stated pre-freeze: the Chase/soft score follows raw shot-proximity (ρ^HD), so on
   a tilted bit it would UNDO the calibrated-threshold fix (the raw data genuinely prefers the
   wrong value — that is what a 12σ wrongward tilt means); and in every flown race the graded
   recoveries were achieved by majority alone while the observed failure classes (systematics,
   tilts) are Chase-immune or Chase-hurt. Calibrated majority's null needs no search
   adjustment (single candidate: 2⁻⁴⁰-class). NO rescue rule: if calibrated majority misses
   exact, the rung is a MISS regardless of what the diagnostics show. This is the exact fix
   for the C4978 failure class: phys-67's frac converged to 0.486 against a 0.5 threshold;
   against its calibrated boundary the same evidence decodes true. Named residual risk: a tilt
   of CIRCUIT-DYNAMICS origin (not readout) survives calibration — if a bit still blocks, the
   calibration block cleanly attributes it (readout ruled out), and that attribution is the
   deliverable of a miss.
4. All race-3 structure HELD: depth-matched twins (Path A differential + Path B gate at race
   depth, twin decoded with the SAME tilt-aware decoder), depth cap 180 (frozen
   pre-transpile), race_n40 at 200k (32 twirls), subsample ladders {2,4,8,16(,32)}, two-stage
   reveal, Path A ρ_t with 1k-pub bootstrap (my seat, Elder co-check), Path B WIN vs Elder's
   frozen t=80 band (≤ 1/10 of band lower edge at EVERY edge), supersedable-by-design printed.

## The job (~90 pubs, ~560k shots ≈ 160–175 s of ~2,748 s pool)

| Block | Structure | Shots |
|---|---|---|
| READOUT-CAL | all-0 + all-1, measure_all | 20k |
| LADDER | t=0 base, m ∈ {0,1}, 4 twirls × 5k | 40k |
| TWIN n=40 | t=0 padded to d2q_race40, 16 twirls × 6,250 | 100k |
| RACE n=40 | t=80, 32 twirls × 6,250 | 200k |
| TWIN n=32 | t=0 padded to d2q_race32, 16 twirls × 6,250 | 100k |
| RACE n=32 | t=80, 16 twirls × 6,250 | 100k |

Marrakesh default (standing device rule; queue-checked at freeze). Exactness gate + logical
convention round-trips (2 strings) + seal 4/4 verification, all pre-submission as race-3.

## Frozen decision rules (deltas only; unchanged rules incorporated by reference to race-3)

- **GATE (Path B)**: twin40 must decode EXACTLY under the tilt-aware decoder at full 100k.
- **Path A**: ρ_t at both matched depths, bootstrap CI, quoted with and without any
  calibration-flagged bits (|t_i − 0.5| > 0.02 bits listed in the manifest before decode).
- **Cap rule, n32 scope rule, miss booking: as race-3.**
- **Grading hygiene (Elder #605, adopted)**: the readout-cal block's QPU is EXCLUDED from the
  Path-B decoder runtime via per-circuit attribution (steth-rider precedent, #547 family);
  only race decoder circuits count against the frozen band. Win-legitimacy affirmation on the
  record (#605): the tilt-aware decoder is calibration-driven (measured, not free), frozen
  pre-flight, blind, flagged bits pre-listed before decode, applied uniformly to twin + race +
  ρ_t — an exact ŝ==s under it is a genuine graded win, not a fitted artifact.
- **Failure modes, named**: (a) circuit-dynamics tilt survives calibration (attribution
  deliverable); (b) clean-layout constraint inflates d2q above cap (rule 1 abort/ineligible
  branches); (c) calibration-block drift vs race pubs within the job (mitigated: co-batched,
  minutes apart; residual named).

## Fences

As race-3 (t=0 classically free; no claim except via rule Path-B WIN; all prior verdicts stand;
prior reveals retired). Fresh strings, never reused. QPU after this job ≈ 2,575–2,590 s; no
further HSS spend without a fresh card. *Contact: Mike Blakemore.*
