# Exp122 — Proper-Time Interferometer: HARDWARE RESULTS (WIN AS FROZEN, MECHANISM CONFOUNDED — the data outran the estimator)

**Whisper C4651.** Job `d9aaj352su3c739lcic0` (C4650 freeze, 18 pubs, 280k shots,
chain C=2/K=3/L=1), graded by FROZEN grader `scripts/grade_exp122.py`. Grade
record: `results/exp122_grade.json`.

## Verdict as frozen: **AGING-MARKS-THE-PATH(+ladder)** — all gates pass

- G0 alive: V(0) = 0.889/0.900 through both CSWAPs.
- W_AGE at 46µs: vac − exc = **0.627 ± 0.009 (67σ)**. W_AGE_LADDER at 93µs:
  0.114 ± 0.010 (11σ). Predictions P1 (0.85), P2 (0.80) **HIT as frozen**.

## The honest part: the mechanical WIN is mechanism-confounded, and the data say so

| Δt (µs) | ⟨X_C⟩ excited | ⟨X_C⟩ vacuum |
|---|---|---|
| 0 | +0.889 | +0.900 |
| 23.2 | +0.198 | +0.722 |
| 46.4 | **−0.165** | +0.462 |
| 92.9 | −0.152 | **−0.038** |
| 185.7 | −0.001 | **−0.247** |

**⟨X⟩ goes NEGATIVE in both arms.** A visibility cannot be negative; a rotating
interferometer phase can. The excited arm's early sign-flip has an obvious physical
source I failed to design out: **the clock is a |1⟩ sitting on a NEIGHBOR of C**
(both lanes are C-adjacent in the chain layout), so its ZZ coupling pulls C's
frequency differently per branch — a coherent, deterministic, in-principle
reversible phase ∝ Δt, which is NOT which-path decoherence. The ⟨X⟩-only estimator
conflates that rotation with genuine aging-marks-the-path dephasing. The vacuum
arm's own late negativity (−0.247) shows a slower background phase drift too. The
frozen law-fit refused to produce a slope (negative V points) — the grader itself
flagged the anomaly.

**What survives cleanly**: the excited clock disturbs path coherence enormously and
early compared to the vacuum twin (order-of-effect certified at 67σ) — but the
SPLIT between (a) irreversible emission-marking and (b) coherent ZZ rotation is not
measurable from ⟨X⟩ alone. The headline interpretation is therefore **DOWNGRADED
from claimed mechanism to certified effect**: "an excited clock in path
superposition destroys/rotates path coherence far beyond the vacuum twin." The
twin-paradox *mechanism* claim is UNRESOLVED — stated plainly, no softening of the
confound.

## Bonus finding (F95 lesson, third strike): published T1 bias

In-job calibration: **T1_K = 334µs (published 179 — 87% off)**, T1_L = 166µs
(published 136). Placement by published values still landed the ladder acceptably;
grading used measured values as frozen. The published-T1 bias (friction 02 family)
is now a three-time offender in our records.

## Exp122b — the phase-blind retest (power-known, specced now)

One-line fix, frozen next time: measure C in **X AND Y** per ladder point →
|V| = √(⟨X⟩² + ⟨Y⟩²) is rotation-immune; decoherence-only claims come from |V|.
Plus an **echo arm** (X on C mid-delay) canceling static ZZ phase as a second
discriminator. If |V|_exc still collapses faster than |V|_vac at 5σ → the
which-path aging mechanism is certified clean; if |V| is preserved and only the
phase rotated → the "twin paradox" was a clock-pull, an equally publishable null
(C4596 both-outcomes-first-class). ~26 pubs, ~340k shots.

**Numbering: NOT requested** — mechanism unresolved; the finding earns its F-number
when 122b separates rotation from decoherence (the F82/F97 retest discipline).
