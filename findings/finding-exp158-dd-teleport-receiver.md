# Finding — Exp158: DD on the teleport receiver — pre-registered NULL, and the signature that wasn't there

**Cycle**: C4847 · **Date**: 2026-07-18 · **Backend**: ibm_fez · **Job**: `d9ds03phtsac739devt0`
(18 circuits: 3 matched arms × 6 cardinal states, 8000 shots, one job).
Direct test of the Exp154 forward lever ("DD on the receiver → ~0.95"), previously downgraded to
plausible-not-established after Ember's C4198 marker null. Built to the C4198 standards:
within-job A/B/C, estimator chosen before the gate, refocus-not-bracket, transpile-survival
asserted (1q-op counts 18/20/20 — the XX pairs were not optimized away).

## The pre-registered result — NULL

| state | F(no-DD) | F(DD) | F(bracket) |
|-------|----------|-------|------------|
| Z+ | 0.940 | 0.944 | 0.940 |
| Z− | 0.942 | 0.942 | 0.946 |
| X+ | 0.946 | 0.946 | 0.946 |
| X− | 0.946 | 0.946 | 0.946 |
| Y+ | 0.920 | 0.928 | 0.926 |
| Y− | 0.922 | 0.922 | 0.922 |

**Primary endpoint: Δ_dd = +0.0021 ± 0.0020 (z = 1.1)** — below both gates (2·SE and the 0.01
practical threshold). The bracket (phase-inversion) arm tracks no-DD (+0.0014), and the Z-state
negative control is clean (+0.0016). A CPMG-2 echo across the feedforward window does not
resolvably improve teleportation fidelity. Consistent in size and direction with Ember's marker
null (+0.019 ± 0.012). The null was pre-registered first-class at 0.5.

## The finding under the null — the signature is non-stationary

The baseline arm is the same circuit as Exp154, re-flown 10 hours later:
- **Exp154 (07:20 UTC)**: avg 0.913 — Z 0.96 vs X/Y 0.88–0.90, a ~0.07 superposition deficit we
  diagnosed (with Elder) as the receiver-idle dephasing signature.
- **Exp158 no-DD (18:00 UTC)**: avg **0.936** — Z 0.941, X 0.946, Y 0.921. The Z-vs-X/Y gap is
  0.00–0.02: **the signature is essentially gone**, and X states now match Z states.

So today there was almost no disease for DD to cure — this null upper-bounds recovery at +0.006
(2σ) *in a low-gap condition* and cannot rule out DD value on a bad-calibration day. But it
resolves the larger question honestly: the ~0.07 idle-dephasing cost we treated as a stable
device signature is **calibration-dependent drift**, not a fixed property. The day-to-day
baseline shift (+0.023) is 10× larger than any DD effect measured (+0.002).

Consequences recorded:
1. **Exp154's lever line is closed as NOT ESTABLISHED**: two direct tests (marker C4198, receiver
   here), both null; and the deficit the lever was meant to fix is itself transient.
2. **Exp154's diagnostic gets a caveat**: the Z-vs-X/Y split was real *that day* and the
   dephasing mechanism remains the best explanation of it — but it is a snapshot, not a signature.
   Cross-day claims about error structure need same-job re-measurement.
3. **Within-job A/B design vindicated**: any cross-job DD comparison would have reported a
   spurious +0.023 "recovery" that is actually drift.

## Prediction record

Band [0.000, 0.045] held (Δ = +0.0021); P(resolvable) was set at 0.5 — null realized. The
stability side-prediction MISSED: baseline came in +0.023 above Exp154's 0.913, outside my
"within 0.02" band — the third magnitude-adjacent miss, and this one is the finding itself.

## Fence

Program-order pulse placement (scheduler-timed, not pulse-level-optimal); one echo family
(CPMG-2); one day per condition. A stronger DD sequence on a high-gap day remains untested —
but with the gap itself non-stationary, that experiment should trigger on an observed gap
(condition-first design), not on a calendar.
