# Exp247 (H7-P7, redesigned) — PRE-REGISTRATION: THE ADAPTIVE HELM, static both-inputs form

**FROZEN before submission. Whisper C4954, substrate claude-fable-5. Creator go: "fly it" (2026-07-21).
Builder + frozen offline decoders + grader: `experiments/exp247_static_memory_decoder.py` (written and
selftested BEFORE any data). Redesign provenance: finding-exp241c (in-circuit rules killed offline;
T1-ML won 0.8125/0.8200 vs 0.5323/0.5252 on |1_L>-only data — the one-class caveat this flight closes).**

## Claim
A T1-aware, history-using ML decoder beats memoryless frame decoding at **balanced accuracy** (both
logical inputs, held-out shots) on live repeated-syndrome streams — i.e. the syndrome stream's memory
is decodable value, not just a diagnostic.

## Flight
`ibm_fez`, **8 pubs × 8,000 shots, fully static** (no feed-forward — no dynamic-circuit risk):
{|0_L⟩,|1_L⟩} × R∈{2,3,4} rounds (τ=30 µs/round, Exp241-matched; syndrome extraction + ancilla reset
only) + 2 readout cals. Transpiled 2q ≤ 22 (asserted). Est. 40–70 s of the 4,078 s remaining.

## Frozen decoders & rule
D0 majority; M frame-replayed memoryless (the Exp241 CORR map); ML_T1 asymmetric HMM — params
(p10,p01,q,rf) grid-fit on the TRAIN half (even shots, both classes, supervised calibration), ALL
decoders evaluated on the TEST half (odd shots) only.
**PASS = MEMORY-DECODER-CERTIFIED iff ΔBA(ML−M) > 0 AND pooled paired McNemar z > 5, at BOTH R=3 and
R=4 (test half).** Always reported: class-conditional accuracies (the bias check the offline study
could not do), R=2 row, fitted params incl. the **re-excitation rate p01** with the |0_L⟩ arm as its
isolator — a hardware number this campaign has never measured.

## Pre-filed prediction (before any data)
**MEMORY-DECODER-CERTIFIED, confidence 0.7.** Predicted: BA(M) ≈ 0.72–0.78 (e0 ~0.93–0.97, e1 ~0.50–0.56),
BA(ML) ≈ 0.83–0.90, ΔBA ≈ +0.10–0.15; p01 ≈ 0.003–0.03/round; p10 ≈ 0.14–0.22.
**Named failure modes**: (i) balanced ML ≤ M → the offline 0.82 was substantially one-class bias; P7
stands down and the bound is kept with full weight; (ii) ML wins on |1_L⟩ but degrades |0_L⟩ enough to
flatten ΔBA → reported as class asymmetry (partial); (iii) day-drift moves p10 off the fitted grid →
params re-fit is IN the frozen protocol (train-half fitting is per-flight by design), so this cannot be
invoked post-hoc — grid edges are reported if hit.

## PD gates (passed pre-freeze)
PD-1: noiseless aer end-to-end — registers/replay/HMM/balanced-metric wiring verified, all decoders
perfect on both classes at all R. PD-3: n/a (static). Depth assert in-code. Streams archived raw in the
result file (the 241b rule: every syndrome stream is a future instrument).
