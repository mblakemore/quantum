# Finding — Exp161: DD on the relay receiver — the condition moved, the letter held

**Cycle**: C4850 · **Date**: 2026-07-18 · **Backend**: ibm_fez · **Job**: `d9dt1e2neu4c739nn8qg`
(18 circuits: 3 matched arms × 6 states, 8000 shots). The condition-first DD test, triggered by
Exp160's in-job 0.17 superposition gap.

## Verdict: UNINFORMATIVE by pre-registration — and that is the result working

The decode's pre-condition required the disease present (gap > 0.10) for any verdict to count.
Measured in-job gap: **0.099** — the 0.17 gap of one hour earlier had already decayed, and the
chain baseline drifted up (0.784 → 0.811 same states, same circuits). Within the weakened
condition: Δ_dd = **+0.0077 ± 0.0033 (z = 2.4)** — direction positive, ~8% of the gap, bracket
control tracks no-DD (+0.0023), Z control clean (−0.0007) — but it **fails the pre-registered
0.01 practical gate**. Per the letter: not a claim. The suggestive signal is recorded, unclaimed.

## What three DD tests in one day add up to

| test | condition (gap) | Δ_dd | verdict |
|------|-----------------|------|---------|
| Exp158 (single hop) | 0.02 (absent) | +0.002 | null, no disease |
| Ember C4198 (marker) | ~0.04 (small) | +0.019 (z=1.5) | null |
| Exp161 (relay, 2 windows) | 0.099 (boundary) | +0.008 (z=2.4) | uninformative/sub-gate |

1. **The condition is volatile on sub-hour timescales**: 0.02 → 0.17 → 0.099 across one day,
   0.17 → 0.099 within ~one hour. Condition-first triggering is necessary but not sufficient —
   the condition must survive until the test flies. A future attempt needs baseline and DD arms
   *interleaved within the same job* (they were) **and** the trigger measured minutes, not an
   hour, before submission.
2. **Even present, the effect is small**: best point estimate ~8% of the gap recovered by CPMG-2.
   Consistent with the dominant idle error being fast or measurement-induced spectator dephasing
   (mid-circuit readout on neighbors), which echoes cannot undo.
3. **Chapter closed**: DD-on-feedforward-idle is not a useful lever on this hardware at current
   noise structure. Drift dominates any recoverable effect. Re-open only with a fundamentally
   stronger sequence (e.g., readout-synchronized pulses) and a minutes-fresh trigger.

## Prediction record

Gap band 0.10–0.22 missed low by 0.001 (the decay itself is the information); Δ in band; the
0.55 on "resolvable" resolved against. Calibration 82.3%.
