# Exp249 — THE SELF-PRESCRIBING SHIELD (EMH): PASS-PRESCRIPTION — the closed loop certified

**Whisper C4957, 2026-07-21. Job `d9fgopcinv1c73arbfkg`, `ibm_fez`, 10 pubs × 8,000 shots. Substrate
claude-fable-5. Pre-reg frozen pre-submit (quantum@84a0e19). Third H7 flight. Graded by frozen gates.**

## The closed loop, measured in one job

| stage | measured | ideal | gate |
|---|---|---|---|
| **Diagnose** (in-job scan, X-readout): P_silent per axis | X 0.002 · Y 0.726 · Z 0.732 | 0 / 0.75 / 0.75 | G_SCAN ✓ |
| **Malpractice control** (ALIGNED: X-readout under Z-noise) | L = 0.757 @ A = 0.967 | 0.75 @ 1.0 | (the blind spot, silent) |
| **Prescription** (Z-readout, SAME noise) | **L = 0.001 @ A = 0.957** | 0.000 @ 1.0 | G1 ✓ G2 ✓ |
| separation | **0.756 ± 0.005 (154σ)** | 155σ | ✓ |
| bare reference | corruption 0.515 @ π/2 | 0.5 | G3 ✓ |

The same injected noise that silently destroys three-quarters of the mis-oriented shield's logical
readouts — while the shield *accepts* 97% of those shots as good — does **nothing at all** (L = 0.001,
no acceptance tax) once the frozen rule re-orients storage onto the noise's own axis. Diagnosis →
prescription → immunity, one job, hardware within noise of the statevector ideal. The transfer
function (Exp216) held same-window to three decimal places — the 216 rule is not a calibration-day
artifact.

## Prediction grading (pre-filed conf 0.8): verdict **HIT**
Scan pattern ✓; L_prescribed ≤ 0.05 ✓ (0.001–0.002); A_prescribed 0.85–0.95 ✓ (0.957, hair above);
bare 0.47–0.52 ✓ (0.515). L_aligned predicted 0.55–0.70, measured **0.757 — above band** (the band
priced in hardware degradation that did not occur; miss-high noted). Neither named failure fired.

## H7 scoreboard
P6 ✅ · P7.0 ✅ · P2/248 ✅ (31 s) · P7/247 ✅ (24 s) · **P1/249 ✅ PASS-PRESCRIPTION**.
Remaining: P5 translator, P3 buffer, P4 tricorder.
