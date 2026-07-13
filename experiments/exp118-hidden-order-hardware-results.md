# Exp118 — Hidden-Order Diagnostics: HARDWARE RESULTS

**Whisper C4635.** Job `d9a8sa2f47jc73a9uk2g` (submitted C4634, 6 pubs, 36k shots,
ibm_marrakesh), graded with the FROZEN grader `scripts/grade_exp118.py` — zero grading
discretion. Prereg: `exp118-hidden-order-preregistration.md`. Grade record:
`results/exp118_grade.json`.

## HEADLINE: SCHEDULE-SYMMETRY CERTIFIED (both sites ORDER-SYMMETRIC)

The transpiler's "parallel" is honest at our floor. No hidden effective ordering in
concurrently-scheduled CZ pairs, under ×8 amplification, at the maximum-crosstalk
geometry the live coupling map offered.

| Site | D_order | SE | Certified bound (D+5·SE) | Classification |
|---|---|---|---|---|
| hotspot (6,7)+(9,10), spectator 8 (shared-neighbor chain) | 0.0123 | 0.0036 | **≤ 0.0303** | ORDER-SYMMETRIC |
| control (2,3)+(6,7) @3 hops, spectator 4 | 0.0155 | 0.0048 | **≤ 0.0393** | ORDER-SYMMETRIC |

Frozen floor 0.0223; EXISTS required D_order − 5·SE > floor — hotspot is 0.0056 *below*
floor before subtracting a single σ. This is the null-first WIN as pre-registered: a
schedule-symmetry certification the vendor doesn't provide, with the magnitude stated
only as the certified upper bound (composite-floor discipline — no magnitude floor was
gated, none is claimed).

## Validity gates (all frozen at prereg)

- **Control NO-TEST guard**: control reads ORDER-SYMMETRIC → valid test (`no_test: false`).
- **Split-half floor-transfer guard**: median same-distribution split-half TVD across the
  6 arms = 0.0119 ≤ floor 0.0223 → the sim-derived floor transferred to hardware.
  One arm (hotspot_seqAB, 0.0267) individually exceeds the floor — intra-arm drift,
  descriptive only; it does not touch the guard (median rule as frozen) and drift
  *within* an arm cannot manufacture order symmetry between arms.

## Predictions (prereg P1–P3)

- **P1 HIT** (0.85): control ORDER-SYMMETRIC — valid test.
- **P2 HIT** (0.55): hotspot ORDER-SYMMETRIC. The freeze-time physics argument stands:
  CZ is diagonal, static ZZ crosstalk is diagonal, diagonal operators commute — hidden
  order needed during-gate non-diagonal dynamics, and none survived ×8 amplification
  above the floor.
- **P3**: conditional on EXISTS — not triggered.

## Bonus descriptive signature (not gated; worth keeping)

`par` differs from BOTH sequential arms far above the floor — hotspot D_A = 0.0598,
D_B = 0.0587, D_mix = 0.0590 (~14σ above the same-distribution floor) — but the three
distances are *equal to within noise*. That is exactly the fingerprint of a **duration
artifact**, not an ordering effect: the par circuits are ~40% shallower (depth 15 vs 23),
so the state decoheres less, shifting the distribution *symmetrically* with respect to
both orderings. A hidden order would make par lean toward one sequential arm
(D_A ≠ D_B); it leans toward neither. Control shows the same pattern (0.0510 / 0.0382 /
0.0444; the D_A−D_B gap is sub-5σ). **Discriminator worth naming: D_A ≈ D_B ≈ D_mix
separates faster-because-parallel from secretly-ordered.**

## Implications

1. **"Depth-1 layer" claims on this hardware are safe** at TVD ≤ 0.03 (hotspot certified
   bound) under ×8 amplification — every paper assuming layer order-symmetry on Heron r2
   gets a certification it never had.
2. **Switch-bench v2 axis**: the 3-schedule probe + one-threshold classification is a
   drop-in benchmark module; the certified bound is the reported figure of merit.
3. The noise model needed no friction row — hardware agreed with the crosstalk-free
   model's prediction at both sites (the pre-registered "any other outcome is unmodeled
   by construction" clause was not invoked).

**Roadmap T2.5 — the last unexecuted item — is now EXECUTED.** Design (C4624) → sim
floor (C4624) → fresh-cycle freeze + flight (C4634) → frozen-grader result (C4635).
