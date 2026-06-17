# Exp55 H3 Spot-Check (Arm 1, r=0): The First Noise-Escape Is *Genuine*, Not a Lucky Shot

**Author**: Whisper C4147 | **Date**: 2026-06-17
**Pre-reg**: experiments/exp55-noise-assisted-escape-preregistration.md (C4108)
**Prior**: findings/exp55-arm0-finding-c4128.md (Arm 0 → T={51})
**Script**: scripts/exp55_h3_spotcheck_c4147.py (one-off, read-only) | **Data**: results/exp55_h3_spotcheck_c4147.json

## Context
Arm 1 (structured FakeMarrakesh noise on the trapped subset T) is mid-flight: **r=0 of R=5**
done on the sole trapped seed 51. The script's built-in H3 pass (`_finalize`) only fires after
*all* realizations complete, so it has not run. This spot-checks the pre-registered **H3
anti-artifact control** on the one escape we have, replicating `_finalize`'s noiseless re-eval
byte-for-byte (lines 212–229).

## The question H3 exists to answer
Arm 1 r=0 reported seed 51 escaping under noise: noisy ratio **0.6573 ≥ 0.640**. But 0.6573 sat
only +0.017 above threshold. The most likely confound (pre-reg §Falsification): the "escape" is a
**lucky high-variance shot** under noisy sampling, not a real move to a better optimization basin.
H3 isolates this — re-score the **noise-found parameters noiselessly**. Artifact → noiseless
re-check falls back below 0.640. Genuine → it holds.

## Result (results/exp55_h3_spotcheck_c4147.json)

| quantity | value |
|---|---|
| x0 cold-start (trapped) — noiseless, Arm 0 | 0.5863 |
| x0 noiseless band (8 sim-seeds) | 0.5784 ± 0.0041 |
| x1 noise-found — **noisy**, Arm 1 r=0 | 0.6573 (escaped) |
| **x1 noise-found — noiseless re-check (canonical H3)** | **0.6914** |
| x1 noiseless band (8 sim-seeds) | 0.6912 ± 0.0004, **8/8 ≥ 0.640** |
| ‖x1 − x0‖ (6-D, range 0–2π) | 7.25 |

**H3 passes decisively for this realization.** The noise-found params re-score **0.691 noiselessly**
— not marginally above threshold but *higher than the 0.657 the noisy measurement showed*, with a
tight band (σ=0.0004) and 100% of re-evals above threshold. The large param distance (7.25) confirms
COBYLA landed in a genuinely different region, not a local jitter of the cold-start point.

## Interpretation
The structured FakeMarrakesh noise knocked COBYLA out of a **real 0.578 trap** into a **real 0.691
basin**. Noise lowered the *measurement* ceiling (true basin 0.691 read as 0.657 under noise) while
raising the *escape floor* — exactly the conditional floor-vs-ceiling effect H1 predicts and the
pre-reg's stochastic-resonance / noise-assisted-transport framing anticipates. For this data point,
the artifact hypothesis is **ruled out**.

## Scope honesty (C3810 / C4128 carry-forward)
- **N=1.** |T|=1 and r=0 of R=5. This is a high-quality *anecdote*, **not** statistical resolution.
- **Does NOT resolve H1** — that needs the escape *rate* over R=5 (is it 1/5? 5/5?). Only r=0 is in.
- **Does NOT resolve H2** — Arm 2 (depolarizing, matched-strength control) not run; "structure is the
  resource" is untested. Any kick might do this on N=1.
- **What it DOES establish, cleanly:** the single escape we have is a genuine basin move, not
  measurement variance. The pre-reg's primary confound is closed for this realization.
- The C4128 re-scope (re-target T to Exp53's p=5 trapped seeds — seed 43 is trapped at p=5/1024,
  0.5996) remains the path to a *powered* test. Exp53's live p=5 arm is now producing that subset.

## Why recorded now (not deferred to `_finalize`)
Creator directive: "keep /droid/repos/quantum repo updated." The first Arm-1 realization carrying a
clean H3 pass is a substantive interim datum on the repo's Priority-1 (Noise-as-Resource) frontier,
worth committing rather than sitting unanalyzed in a log for the ~20h the remaining r=1–4 take
(~4.9h/realization). `_finalize` will recompute H3 canonically over all R=5 at completion; this
spot-check is read-only and does not touch the running process (C4038).
