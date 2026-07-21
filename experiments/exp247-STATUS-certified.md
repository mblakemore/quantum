# Exp247 — THE ADAPTIVE HELM (static): MEMORY-DECODER-CERTIFIED

**Whisper C4955, 2026-07-21. Job `d9fglbsjeosc73fju9r0`, `ibm_fez`, 8 pubs × 8,000 shots, 24 s QPU
(quota 4,054 s remains). Substrate claude-fable-5. Pre-reg frozen pre-submit (quantum@b9b8de8;
pre-data amendment 4565496). Graded by the frozen decoder suite. Second H7 flight.**

## Verdict — the syndrome stream's memory is decodable value, balanced

| R | decoder | acc \|0_L⟩ | acc \|1_L⟩ | balanced | ΔBA(ML−M) | McNemar z |
|---|---|---|---|---|---|---|
| 3 | majority | 0.997 | 0.278 | 0.637 | | |
| 3 | memoryless | 0.994 | 0.603 | 0.798 | | |
| 3 | **ML_T1** | **0.969** | **0.885** | **0.927** | **+0.129** | **+29.3** |
| 4 | majority | 1.000 | 0.163 | 0.581 | | |
| 4 | memoryless | 0.996 | 0.580 | 0.788 | | |
| 4 | **ML_T1** | **0.967** | **0.881** | **0.924** | **+0.136** | **+29.9** |

(R=2 row consistent: ΔBA +0.082, z +21.8.) Frozen rule (ΔBA > 0 AND z > 5 at both R=3,4, held-out
shots): **met by ~6× on z.**

**The bias check the offline study couldn't do**: the T1-aware decoder's gain is NOT class bias — it
buys +0.28/+0.30 on the decaying |1_L⟩ class at a cost of only ~0.03 on |0_L⟩. At four rounds of
τ=30 µs, history-aware offline decoding recovers a logical bit at 92% balanced where memoryless
correction gets 79% and the final readout alone gets 58%. **The ship's log is worth a third of the
cargo.**

## The bonus number: re-excitation
Fitted p01 = 0.003/round — at the grid MINIMUM (edge hit, disclosed per pre-reg (iii)): the honest
statement is **p01 ≲ 0.003/round**, ~70× below the decay rate p10 (0.22/round, also grid edge, high
side). First isolation of the up-rate in this campaign; a finer grid refit on the archived raw streams
is free future work (params feed only the decoder, so edges do not touch the verdict).

## Prediction grading (pre-filed conf 0.7): verdict **HIT**
ΔBA predicted +0.10–0.15 → measured +0.129/+0.136 ✓ IN BAND. Absolute BAs ran ABOVE both predicted
bands (ML 0.92–0.94 vs predicted 0.83–0.90; M 0.79–0.80 vs 0.72–0.78) — a better hardware day than
Exp241's; miss-high noted honestly. Named failure modes (i)/(ii) did not fire — the offline win
generalized. First-submission depth-assert catch ($0) documented in the amendment.

## H7 scoreboard
P6 ✅ ($0) · P7.0 ✅ ($0) · P2/Exp248 ✅ CERTIFIED (31 s) · **P7/Exp247 ✅ CERTIFIED (24 s)**.
H7 hardware total: 55 s. Next in plan order: P1/Exp249 (EMH shield), Creator-gated.
