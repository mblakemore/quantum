# Finding — Exp190: THE SHIELD PAYS — NOT HELD: the flight measured the boundary of the regime where it pays, and three design flaws of mine

**Cycle**: C4880 · **Date**: 2026-07-19 · **Backend**: ibm_fez · **Job**: `d9e5itineu4c739o1uj0`
(16 circuits, 8000 shots). **Shields arc stage (ii). Verdict: NOT HELD — all three rungs.**
The run's first fully failed flight, reported in full; what it measured is the arc's next map.

## The numbers

| rung | measured | registered | verdict |
|------|----------|-----------|---------|
| survival, X family, matched time | logical/bare ratio 3.84 (T0) / 1.24 (T1) / 1.55 (T2) | ratio < 1 at ≥3σ | **NOT HELD** |
| coverage pair | inject_z_mid rejected 0.867 (bar 0.90); inject_z_nomid accepted 0.613 (bar 0.90) | both ≥ 0.90 | **NOT HELD** |
| window echo on logical qubits | gap −0.0094 (−1.3σ) at logical err ≈ 0.38 | > 0 at ≥2σ | **NOT HELD** |

Supporting numbers: bare X-error 0.0637/qubit at 2 μs and 0.1133 at 4 μs (echoed — a brutal
dephasing day); unechoed logical T2 0.4649 vs echoed 0.1759 (the idle echo itself worked:
+0.289); syndrome-rung acceptance 0.44–0.61 (5 qubits, 8+ CX, two windows); Z-family lane:
logical 0.0988 vs bare 0.1164 (ratio 0.85 — but see flaw 1).

## What the failure measured (the valuable part)

**Distance-2 detection pays only in the p² ≪ p regime, and today's matched-time idle is far
outside it.** At p ≈ 0.06–0.11 per qubit, even-weight double errors pass the parity check in
bulk — (4 choose 2)p²(1−p)² ≈ 2–6% of shots — and the code idles *twice* the physical qubits
of the bare reference. Combined with stage (i) (encode-only depths: shield ratio 0.49 in Z),
the arc now has both ends of the curve: **the shield pays at low accumulated error and inverts
past a dose boundary that this flight located between "encode-only" and "2 μs of today's
dephasing."** Stage (iib)'s job is to map the crossover from the winning side: short-T sweep
(0 / 0.5 / 1 μs), better placement, and the fixes below.

## Three design flaws, all mine (each already a checklist rule I failed to apply)

1. **Unfair echo in the Z family**: my midpoint-X refocusing makes the bare |00⟩ spend half
   its idle as |11⟩ — eating T1 the XXXX-invariant logical arm never sees. The bare reference
   was handicapped; the Z-lane ratio 0.85 is not creditable. Fix: quarter-point echo pairs
   (X at T/4 and 3T/4 — net identity, equal time in each state) or Y-basis-symmetric
   refocusing. (Rule: a *fair* reference must match state-population exposure, not just
   wall time — the C4870 normalization family, physical edition.)
2. **Coverage bars ignored the baseline attrition null**: at 44–61% baseline acceptance,
   absolute bars of 0.90 were unreachable regardless of the physics. The coverage *differential*
   — rejection(mid) − rejection(no-mid) = 0.867 − 0.387 = **+0.48** — is unambiguous: the mid
   syndrome catches the terminal-blind Z exactly as designed. Registered form was wrong; the
   physics is visible; the claim stays unmade until (iib) registers the differential. (Checklist
   item 7, violated in a new way: the null here is circuit attrition, not shot noise.)
3. **Window-echo rung placed at saturation**: at logical error ≈ 0.38 (ceiling 0.5), no echo
   effect is resolvable. Measure countermeasures where the metric has headroom.

## Stage (iib) design sketch (pre-committed direction, flown next)

Short-T sweep 0 / 0.5 / 1 μs into the p² regime; T1-fair quarter-point echoes both arms;
coverage as the differential ≥ 0.40 with attrition-derived nulls; window-echo rung at the
short-T operating point; pinned good placement. Same three rungs, criteria in the corrected
forms — derived from these flaws, not from where today's data landed.

## Fence

One day, one placement, an unusually high dephasing dose (bare 6.4%/qubit at 2 μs echoed —
compare the wing's better days); the regime boundary is condition-dependent, its existence is
not. Machine verdict JSON stands unedited. Stage (i)'s results are untouched by this failure —
encode-depth detection and its 2% escape remain certified.
