# Finding Exp241c (P7.0) — the offline decoder study: naive memory rules FAIL, the flag INVERTS, and Exp247 as designed is dead ($0)

**Whisper C4951, substrate claude-fable-5. All from Exp241's already-flown job `d9f3ov4jeosc73fjen3g`.
Cards: `results/exp241c_offline_decoders.json`, `exp241c_flag_purification.json`,
`exp241c_corrected_arm_purification.json`. Method: Pauli-frame replay of in-circuit decoders on the
sham arm's recorded streams (faithful for X-corrections on a bit-flip code: syn(e^f)=syn(e)^syn(f)).**

## Method validation (the replay is real)
Replayed-memoryless on sham data reproduces the actual corrected arm: 0.619 vs 0.616 (R2), 0.542 vs
0.523 (R3). At R4 it does NOT: replay 0.521 vs real 0.442 — **the physical fix machinery costs ~0.08
fidelity by round 4** relative to idealized instant corrections (finding 3).

## Finding 1 — both planned memory rules LOSE (Exp247's premise refuted pre-flight)
Test-half success rates (R2/R3/R4): memoryless M = 0.614/0.532/0.525; **debounce A = 0.419/0.264/0.202
(catastrophic)**; revert-B = identical to M (never diverges); HMM-ML (symmetric-flip model) = below M
(model misspecified for T1-asymmetric noise — noted, not load-bearing). Root cause of A's failure: the
fitted stream parameters are flip-rate p≈0.14/round vs ancilla-readout q≈0.08 — **the stream is
signal-dominated, not readout-noise-dominated. The plan's pre-filed intuition was WRONG (graded miss).**
Debouncing delays true fixes in a p≫q regime = malpractice.

## Finding 2 — the memory signal cashes as PURIFICATION, and its meaning depends on the machinery
- **Idealized replay**: repeat-fire flagged shots are doomed (F 0.05–0.08); discarding 13–23% of shots
  lifts F by +0.09/+0.13/+0.13 — the flag detects unhealable trajectories at ~93% precision.
- **Real corrected arm (its own recorded syndromes)**: the flag INVERTS — flagged shots are BETTER
  (0.64/0.61/0.53) than kept (0.61/0.51/0.41). Interpretation: with physical fixes, a phantom
  (readout-error-triggered) fix flips a good qubit, re-fires the SAME syndrome next round, and is
  self-healed — real-arm repeat-fires are dominated by benign phantom-repair events, not stuck errors.
- The two regimes bracket the truth: **what a syndrome repeat MEANS depends on whether the fix that
  preceded it was real** — no 2-round history rule can be interpreted without a model of the fix
  machinery itself.

## Finding 3 — the machinery cost curve
Real corrected arm underperforms idealized replay by 0.00/0.02/0.08 at R2/R3/R4: feed-forward's own
noise grows superlinearly in rounds at this scale. A number the plan's P3 (pattern buffer) must respect.

## Verdict for Exp247
**DO NOT FLY as designed** — the pre-registered primary claim (rule A or B beats memoryless) is
refuted on real streams; the flight would have been a predictable NOT-HELD. The PD-4 gate did its job
for $0. Redesign options (Creator decision): (a) T1-aware asymmetric ML offline decoder study first
($0) — if a correct-model decoder beats M offline, Exp247 becomes a STATIC flight (record streams, no
in-circuit adaptation, offline decode = how real QEC decoders work anyway); (b) stand P7 down, promote
P2 (cloak) to first H7 flight; (c) fly a purification-focused variant only if a rule survives (a).

---
## ADDENDUM (C4952) — option (a) executed: the T1-aware ML decoder WINS, Exp247 redesign proceeds
Asymmetric HMM (decay p10, re-excitation p01, fitted on train half: p10=0.22/round [grid edge, noted],
p01=0.005, q=0.05, rf=0.02), evaluated on the held-out test half: **F_ML_T1 = 0.8125 (R3) / 0.8200 (R4)
vs memoryless M = 0.5323 / 0.5252 — McNemar z = +32.8 / +34.2** (`results/exp241c_t1_ml.json`).
The syndrome HISTORY discriminates "started |111⟩ and decayed stepwise" from "was |000⟩ all along" —
information the final readout alone cannot carry. The pre-stated decision rule (>3σ at both R3 and R4)
is met by an order of magnitude.

**Honesty caveat (identified before any celebration)**: Exp241 encoded ONLY |1_L⟩ — this is single-class
performance on the hard (decaying) input; a decoder biased toward "1" gains unfairly on such data (ML
answers "0" on 18% of shots, so it is not degenerate, but balanced accuracy is unmeasured). **The
redesigned Exp247 therefore REQUIRES both |0_L⟩ and |1_L⟩ arms**, decoded offline, graded on balanced
accuracy — which the static-flight design provides naturally.

**Exp247 REDESIGN (to be frozen at its own pre-reg)**: STATIC flight (no in-circuit adaptation, no
dynamic-logic risk): encode |0_L⟩ AND |1_L⟩, R ∈ {3,4} rounds of syndrome extraction with NO feed-forward
(the sham structure), 8k shots/pub ≈ 8-10 pubs; decode offline with (i) majority baseline, (ii) frame-replayed
memoryless, (iii) T1-aware ML (params fit on a train split of the SAME flight, both classes); primary:
balanced accuracy ML vs memoryless, >5σ paired. Bonus: the |0_L⟩ arm measures the re-excitation rate —
a hardware number we have never isolated.
