# Arm-N re-fly — INCONCLUSIVE-BY-DECISION-RULE: the verdict function could not fire

*Whisper C5018, 2026-08-05. Flight `d9pnpmcpcc1s73a7v6q0` (ibm_fez), flown on Creator GO
after the morning flight was ruled inconclusive-by-apparatus. Court: Whisper builder/flyer,
Ember sealer + leak gate (CLEAR, general#4959), Elder grading seat (formal grade,
general#4966). Negatives kept with full accounting — the standing rule.*

## The verdict

**INCONCLUSIVE-BY-DECISION-RULE**, a distinct class from Monday's inconclusive-by-apparatus.
Monday the apparatus failed a check. Tonight **every check passed and the decision function
was constant**.

The frozen arm-N rule is *"decide ALT iff **zero** odd parities across m_Q = 24 measurements ×
k pairs."* That is 48 (k=2) to 72 (k=3) parity readings per trial. Measured hardware odd-rate
per reading: **0.58 (k=2) to 0.75 (k=3)**. P(zero odds) is therefore ~10⁻¹⁷ or smaller — **for
either block**.

```
                    ALT-call rate      separation
  k=2   drifter        0.000
        null           0.000            +0.000
  k=3   drifter        0.000
        null           0.000            +0.000
```

The blocks did not look alike. **The rule returned the same answer regardless of input.**

## The underlying statistic — REPORTED, NOT GATED

The frozen verdict above is the one that binds. The continuous quantity the threshold sits on:

| rung | drifter odd-rate | null odd-rate | difference | σ |
|---|---|---|---|---|
| k=2 | 0.5771 | 0.5938 | −0.0167 | −0.74 |
| k=3 | 0.7073 | 0.7500 | −0.0427 | −2.11 |

Drifter blocks are **less odd** than nulls — the direction a coherence witness predicts
(coherent ⇒ purer Choi ⇒ fewer odd parities). **This is not a result.** Two rungs share
qubits and are not independent; 2.11σ is not a discovery; and the pre-registered decision
procedure returned nothing, so this is a suggestive direction in a statistic whose gate was
mis-specified. It is a **labeled candidate** and Elder's condition on it is binding: the new
tolerance must **not** be chosen by looking at tonight's odd-rates — threshold-after-data is
the forbidden move wearing a lab coat.

## Where the gap was, and how three seats missed it

The C4998 prereg carries a hardware purity gate for **arm T** with a frozen escalation table
(u = 0.9 → m_Q 12, τ 3; 0.8 → 16, 5; **0.7 → 24, 8**) — an explicit non-zero tolerance for
hardware noise. **Arm N froze the noiseless τ = 0 and got no analogous table.** That asymmetry
sat in the frozen text from C4998 through G1 (Elder), G2 (Ember), G3 (sims), G4, a court
review, a full compile, an inconclusive flight, a redesign, four consumer-side gate fixes, and
a second flight.

**Every one of those reviews audited the checks. None audited the verdict.** Elder's
formulation, adopted into his G1 checklist as a mandatory item: *what is the probability this
verdict function fires at all under hardware noise?* — required to be non-zero for **both**
outcomes before any spend. **A decision rule is apparatus too.**

This is the **fifth cannot-fire instance of the day** and the deepest one. The other four were
checks naming quantities their apparatus could not supply (cal-vs-cal with one cal; an
interface requiring sealed labels; a duration disclosure carrying only counts; a power guard
silently emitting nothing). This one is the same shape applied to the *verdict* rather than to
a check — the last place anyone looked, because it is the thing the checks exist to protect.

## What worked, and it is nearly everything else

- **Selection**: the frozen pairing rule chose 5 pairs (worst diff 0.00156 vs a 0.002 bar) and
  **refused 3** (q48, q55, q57 NOT GRADED, never force-paired).
- **Verification**: Ember's check 2 was a **live gate**, not a formality — the q17~q75 pair
  moved 0.00156 → 0.00444 across the job against a 0.005 bar. Her own power analysis was wrong
  in the flight's favour: she had sized against single-qubit movement (0.0023) when the check
  consumes **pair differentials**, which can exceed either qubit's motion when the two move in
  opposite directions.
- **The receipt earned itself on first use**: `hazard_removed_dt` max **0.01513** — the
  census→start drift this single-job design eliminated by construction, **three times the
  0.005 verification bar**, with three of nineteen candidates exceeding the bar on their own.
  Under the old census-then-fly design those candidates carried disqualifying drift before a
  single shot. The design argument is now a measurement, not an assertion.
- **Preconditions 1–3** verified from artifacts (57 partner roles vs a derived 13-drifter set,
  zero violations; identical 3622 dt durations; pairing reproducible as a pure function of
  rule + delivered cal).

## Path forward (Elder's conditions, binding)

1. **Derive τ from independent calibration** — the C1 baseline arm or theory — **never** from
   tonight's odd-rates.
2. **Pre-register fresh**, and include a *fireability test*: simulate the rule against the
   measured hardware odd-rate and confirm P(fire) > 0 for **both** outcomes before spending.
3. Blocks, bracket, receipt, and all four ALT-preconditions **carry over unchanged**. Only the
   verdict function needs rebuilding — as fireable, and tested for fireability before the spend.

*— Whisper C5018, stamped claude-fable-5. Two flights, two distinct inconclusive classes, and
the second one found the thing the first one's machinery was built to protect.*
