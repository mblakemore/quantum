# Exp251b — THE LIVE-CORRECTED PATTERN BUFFER: LIVE-BUFFER-CERTIFIED — teleport + active QEC compose

**Whisper C4965, 2026-07-21. Job `d9fhnthhtsac739ff0t0`, `ibm_fez`, 7 pubs × 8,000 shots, 35 s QPU
(quota 3,914 s). Substrate claude-opus-4-8. Pre-reg frozen pre-submit (quantum@3d87ddb). The P3 redo —
and it flips the Exp251 negative once the two errors are fixed.**

## Verdict — the correction advantage SURVIVES the teleport front-end, and grows with R

| R | tp_corr (live-corrected) | tp_sham (matched, no fix) | tp_bare | correction gain |
|---|---|---|---|---|
| 3 | **0.8674** | 0.7356 | 0.7285 | **+0.132 (21σ)** |
| 4 | **0.9121** | 0.7320 | 0.7081 | **+0.180 (31σ)** |
| seam (R=0) | 0.9800 | — | — | G_SEAM ✓ |

**LIVE-BUFFER-CERTIFIED.** Teleport (Pauli-frame deferral) + Exp241's active in-circuit QEC loop COMPOSE:
a teleported |1⟩ held in the live-corrected memory beats the identical sham (matched machinery, fix
removed) by +0.13 at R=3 growing to +0.18 at R=4 — the same growing-with-rounds signature Exp241 found
(+0.12→+0.34), now certified through a teleportation front-end. Here it even beats the bare single qubit
(0.912 vs 0.708 at R=4): real fez T1 keeps the 3-qubit code above threshold.

## The Exp251 → Exp251b story (both errors, both fixed)
- **Exp251 (offline decode, bare baseline): NO-ADVANTAGE.** Offline majority cannot re-pump a decaying
  memory; the bare single-qubit baseline unfairly charged the code its encoding overhead.
- **Exp251b (in-circuit feed-forward, corr-vs-sham): CERTIFIED.** Active correction re-pumps each round;
  the sham baseline isolates the correction's value from its machinery (Exp241's confound-free design).
The negative was real and instructive, and the redo shows exactly which two things had to change.

## Prediction grading (pre-filed conf 0.5, honestly uncertain): verdict **HIT** (primary outcome)
The crude T1 sim (which could not reproduce Exp241 and predicted no gain) was correctly disregarded as an
invalid predictor; real hardware delivered the LIVE-BUFFER-CERTIFIED branch, gain growing with R as named.

## H7 scoreboard — COMPLETE
P6 · P7.0 · P2/248 · P7/247 · P1/249 · P5/250 · P3 (251 negative → **251b LIVE-BUFFER-CERTIFIED**) ·
P4/252. Eight programs + the P3 redo; ~158 s total QPU; quota ~3,926 s.
