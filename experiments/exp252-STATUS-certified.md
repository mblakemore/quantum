# Exp252 — THE SHIELDED TRICORDER: PASS-HEISENBERG — GHZ phase super-resolution certified

**Whisper C4964, 2026-07-21. Job `d9fhjrqneu4c739pjtkg`, `ibm_fez`, 36 pubs × 4,000 shots, 40 s QPU
(quota 3,949 s). Substrate claude-opus-4-8. Pre-reg frozen pre-submit (quantum@7496cd8). Eighth and
final H7 flight. Graded by frozen DFT rule.**

## Verdict — the Heisenberg scaling law, measured

| GHZ size N | DFT peak freq | expected | visibility |
|---|---|---|---|
| N=1 (SQL reference) | 1 | 1 | 0.989 |
| N=2 | 2 | 2 | 0.949 |
| N=3 | 3 | 3 | 0.917 |
| N=4 | 4 | 4 | 0.933 |

**PASS-HEISENBERG.** Every GHZ_N sensor's phase parity oscillates at exactly frequency N — the N=4
entangled sensor resolves phase **four times finer** than a single qubit, the Heisenberg super-resolution
signature. Visibility stayed high (0.92–0.99) across all sizes: on this die a 4-qubit GHZ retains 93% of
its ideal metrological contrast.

## Prediction grading (pre-filed conf 0.8): verdict **HIT**, far better than feared
Peak == N for all N ✓. Predicted N=4 visibility 0.35–0.5; measured **0.933** — the named failure mode
(N=4 sinking into the shot-noise floor) did not come close to firing. fez GHZ fidelity was excellent.

## Scope
Physical GHZ metrology (the robust deliverable). The error-detected (shielded) logical-GHZ version
(Exp219, 16 qubits) is named as the next-hardware step, not flown — signal attenuation at that depth.

## H7 scoreboard — ARC COMPLETE
P6 ✅ · P7.0 ✅ · P2/248 ✅ · P7/247 ✅ · P1/249 ✅ · P5/250 ✅ · P3/251 NO-ADVANTAGE (root-caused) ·
**P4/252 ✅ PASS-HEISENBERG**. Eight programs flown: seven certified/positive + one honest negative,
on ~135 s of total QPU. Exp251b (in-circuit P3 redo) in progress.
