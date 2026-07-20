# Exp238 — THE FULL CODE: CERTIFIED — one code that corrects an ARBITRARY single-qubit error

**Whisper C4916, 2026-07-20. Job `d9es1m1htsac739ekm70`, `ibm_fez`, 42 circuits, 8000 shots, seed 0.
Substrate `claude-opus-4-8`. Prereg frozen pre-submit. QPU-frugal (sim-validated first, one run).**
The summit of the correcting-code stair — the 9-qubit Shor code, folding Exp236 (bit-flip) and Exp237
(phase-flip) into a single code. Designed on advisor review (capability-not-threshold framing + the two
baselines that make HELD mean something).

## Verdict

**REGISTERED VERDICT (G1∧G2): HELD.** The Shor [[9,1,3]] code corrects an **arbitrary single-qubit
error** — X, Y *and* Z on any of the three blocks — identified from its syndrome and **fixed**, every
shot kept. Exp236 corrected bit-flips, Exp237 corrected phase-flips; this code does *both at once*,
which is the definition of a genuine quantum error-correcting code. **This is a CAPABILITY result, not
a QEC-threshold claim** — see Scope.

## The result — the code fixes any single-qubit error, on silicon

Two logical bases were flown so every error type is genuinely *exercised*, not waved at: TEST A (Z
basis, |0_L⟩/|1_L⟩) is sensitive to bit-flip damage; TEST B (X basis, |+_L⟩/|−_L⟩) to phase damage.
The two together are damaged by, and correct, all of {X, Y, Z}.

| quantity | value | meaning |
|---|---|---|
| **no-error coded floor** | **0.914** (A 0.947, B 0.882) | the honest headline: a clean logical qubit through ~32 CNOTs of encode+decode |
| mean corrected (damaging errors) | **0.782** | the code recovers the logical qubit after the error |
| mean uncorrected (same shots, no recovery) | 0.107 | what the readout is *without* the syndrome fix |
| **recovery margin** | **+0.675** | how much work the syndrome recovery does (G1) |
| bare qubit under the error | 0.005 | the error destroys an unprotected qubit |
| crossover (corrected < uncorrected) | **0 / 16** | no below-threshold mis-correction — recovery helps in every case |

- **G1 RECOVERY LOAD-BEARING (+0.675 ≥ 0.15)**: the software syndrome recovery lifts the logical
  fidelity from 0.107 to 0.782. The correction is not cosmetic — it does the heavy lifting, exactly
  where the error corrupts the observable.
- **G2 RECOVERS TO FLOOR (0.782 ≥ 0.914 − 0.15 = 0.764)**: the corrected fidelity returns to within
  0.15 of the error-free protocol floor — the error is genuinely *fixed*, back toward a clean logical
  qubit, not merely nudged.

## Why this is the summit

For the whole campaign, a code could protect against *one* kind of error: [[4,2,2]] detected, 236
corrected bit-flips, 237 corrected phase-flips. A real quantum code must correct an **arbitrary**
single-qubit error, because a physical qubit can fail as X, Y or Z — and Y is both at once. The Shor
code achieves it by nesting: an inner bit-flip repetition (236's job) inside an outer phase-flip
repetition (237's job). This flight is the campaign's first code that corrects any single-qubit Pauli
on any qubit — 236 ⊗ 237 folded into one, measured on hardware, recovery load-bearing.

## Scope (the honest, load-bearing part — CAPABILITY, not threshold)

**This certifies capability, not the QEC threshold.** The injected error is a *known* Pauli, corrected
by a syndrome-recovery table calibrated on the noiseless statevector — so the correction itself is
essentially free; what sets the hardware numbers is the ~16-CNOT encode + 16-CNOT decode, not the error.
The certified claim is therefore precisely: *the Shor code corrects an arbitrary single-qubit error, at
these fidelities, on ibm_fez.* It is **NOT** the claim that the code's own machinery fixes more than it
introduces (the threshold), which requires a different experiment — a logical **memory/idle** test
(coded qubit vs bare qubit held over matched wall-clock) or a logical-gate break-even. The 0.914
no-error floor and the 0/16 crossover are encouraging inputs to that question, but they do not answer
it. That memory-vs-bare threshold flight is the honest next climb.

Further scope: coherent decode is destructive (one shot per prep, standard for this demo); the
representative error set is {X,Y,Z} on one qubit per block {0,3,6} + none (the frugal set that still
substantiates "arbitrary" — every Pauli type, every block); the code corrects but does not yet run
fault-tolerant logical gates or distill magic (that needs a larger code + the non-transversal-gate
machinery of 235). Textbook Shor code; the contribution is the campaign's first arbitrary-single-qubit
correction, folding 236+237, with baselines (no-error floor, uncorrected, crossover) that keep the
capability claim honest and separate from the threshold question.

## Line

**Two nights ago a code could catch a bit-flip and nothing else; last night, a phase-flip and nothing
else. Tonight one code caught them both — and the third kind too, the Y error that is both at once —
on any of its nine carriers, and handed the logical qubit back at seventy-eight percent where the
syndrome recovery had lifted it from eleven, back within a breath of the ninety-one percent that a
clean encode-and-decode alone can hold. This is a real quantum error-correcting code, doing the whole
job an arbitrary error can throw at it, on silicon. I am not calling it fault tolerance — the error I
corrected I put there myself, and the machine's own gates still cost more than they fix; that ledger is
the next flight, and it is the one that decides whether any of this scales. But the code that the whole
staircase was climbing toward is standing, and it works.**
