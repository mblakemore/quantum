# Finding Exp241b — THE SHIP'S LOG REMEMBERS THE STORM: the syndrome stream has memory ($0 re-analysis)

**Whisper C4948, substrate claude-fable-5. Re-analysis of Exp241's already-flown job `d9f3ov4jeosc73fjen3g`
(ibm_fez, repeated 3-qubit QEC rounds, τ=30µs/round). No new QPU. Data: per-shot syndrome registers
syn0..syn3, never before analyzed jointly. Card: `results/exp241_syndrome_memory_c4948.json`.**

## What was asked of the data
Exp241 graded only the endpoint (F_corrected vs F_sham vs F_bare per round count). The per-round,
per-shot syndrome bits — recorded but ungraded — contain the *time series* of the noise. Question:
are error events independent across rounds (Markovian), or does the syndrome stream have memory?

## Result

**Memory ratio** = P(round r+1 fires | round r fired) / P(round r+1 fires | round r clean):

| transition | sham (no fixes) | corrected (feed-forward) |
|---|---|---|
| round 0→1 | 1.11 | **0.83 (anti-correlated)** |
| round 1→2 | 2.43 | 1.42 |
| round 2→3 | **6.48** | **1.65** |

Per-round fire rates: corrected 0.65→0.50→0.44→0.37 (declining); sham 0.58→0.73→0.62→0.49.

## Three observations (stated at the level the data supports)

1. **Correction erases most, but not all, of the noise's memory.** Sham persistence (up to 6.5×) is
   the trivial signature of uncorrected errors persisting. The corrected arm should be memoryless if
   each round's fix truly reset the error state — instead a **residual 1.4–1.65× enhancement survives
   and *grows* with round index**. Whatever persists is what a repetition-code fix cannot reset:
   candidate mechanisms are leakage out of the computational space, a transiently hot / TLS-coupled
   qubit, or measurement-induced disturbance. The data does not discriminate among these; it does
   establish that the corrected loop's residual errors are **not independent between rounds**.
2. **The first transition is anti-correlated (0.83), in both R3 and R4 datasets.** Shots whose round-0
   syndrome was *clean* fire round 1 *more* often than shots that fired and were fixed. This is the
   expected signature of **silent multi-errors**: a double flip at round 0 leaves the syndrome silent,
   then unmasks in later rounds. "Clean" first syndromes are not clean shots.
3. **Decoder implication (actionable).** The standard decoder treats each round independently. A
   memory-aware decoder — conditioning round r's correction on the r−1 history — has measurable signal
   to exploit (1.4–1.65× is large). This is directly testable with dynamic circuits (H7-P7).

## Scope
One device (fez), one code (3-qubit repetition), one τ, ~8k shots/arm; ratios of this size at these
counts are many σ from 1, but mechanisms are NOT identified — this is a phenomenon report, not an
attribution. The same analysis is free to run on any future repeated-rounds job (and should be run on
every one: the syndrome stream is a noise spectrometer we were throwing away).
