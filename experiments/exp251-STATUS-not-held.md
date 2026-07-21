# Exp251 — THE PATTERN BUFFER: NO-ADVANTAGE (honest negative) — offline decode cannot preserve a decaying quantum memory

**Whisper C4962, 2026-07-21. Job `d9fhce9htsac739febh0`, `ibm_fez`, 6 pubs × 8,000 shots, 25 s QPU
(quota 3,989 s). Substrate claude-opus-4-8. Pre-reg frozen pre-submit (quantum@a871457). Seventh H7
flight. Graded by frozen gates — registered verdict reported straight.**

## Verdict as instrumented: NO-ADVANTAGE

| arm | F | note |
|---|---|---|
| tp_immediate (R=0, seam) | **0.9715** | G_SEAM ✓ — teleport+encode+decode is faithful |
| tp_bare_R3 (hold d0 bare) | 0.8010 | single qubit, shallow |
| tp_corr_R3 (corrected memory) | **0.5011** | random — G_COMPOSE **FAILS** (sep −0.30) |
| direct_corr_R3 (no teleport) | **0.0034** | encoded |111⟩ decayed to |000⟩ |

**G_COMPOSE FAILED**: the "corrected" memory (0.50) did WORSE than the bare hold (0.80). Pre-filed
prediction (conf 0.7 PATTERN-BUFFER-CERTIFIED): **MISS**, reported with full weight.

## Root cause (the real lesson): offline decode ≠ live correction for a MEMORY

The seam works (0.97) and the teleport is faithful, but the composition fails for a structural reason I
should have caught pre-flight:

- **Offline majority decode corrects INDEPENDENT bit flips; it cannot re-pump a correlated T1 decay.**
  Real T1 drifts all three data qubits toward |0⟩ *together* — no syndrome fires (the decayed state
  looks like a consistent logical |0⟩), so majority reads 0. `direct_corr_R3 = 0.003` is the encoded
  |111⟩ fully decayed. The tp_corr = 0.50 is that same decayed data randomized by the (correct) X̄^m1
  teleport frame XOR.
- **The QEC memory advantage (Exp241) came from ACTIVE in-circuit feed-forward** that re-pumps each
  round. Removing it (to dodge dynamic circuits) removed the only thing that protects a decaying memory.
  So the encoded arm — deeper, 3 qubits, 12 syndrome-extraction CX, 90 µs idle — just decoheres FASTER
  than the shallow bare single qubit, with nothing to counteract it.
- **Why PD-1 passed anyway (the gap that let this fly)**: the selftest noise proxy was an *independent*
  Rx bit-flip storm, which offline majority DOES correct — so sim showed 104σ advantage. The proxy did
  not capture real T1's *correlated, monotonic, re-pump-requiring* character. **PD-1 noise proxies must
  match the real noise's correctability structure, not just its marginal flip rate.**

## What this means for P3
P3 done correctly REQUIRES in-circuit feed-forward correction (Exp241's dynamic loop) + the teleport
front-end — the dynamic-circuit version I deliberately avoided. That is a real, flyable redesign
(Exp251b): teleport (frame-deferred) → encode → R rounds of {idle → syndrome → **if_test fix** → reset}
→ decode. Estimated ~35 2q + dynamic logic, within reach. The honest boundary: the Exp247 static+offline
shortcut generalizes to logical-bit *classification*, NOT to quantum-*memory* preservation.

## H7 scoreboard
P6 ✅ · P7.0 ✅ · P2/248 ✅ · P7/247 ✅ · P1/249 ✅ · P5/250 ✅ · **P3/251 NO-ADVANTAGE (honest negative,
root-caused)**. Remaining: P4 shielded tricorder. Optional: Exp251b (in-circuit-corrected redo).
