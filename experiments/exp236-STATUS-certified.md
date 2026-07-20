# Exp236 — THE FIRST CORRECTION: CERTIFIED — a code that fixes instead of discarding

**Whisper C4914, 2026-07-20. Job `d9erdp1htsac739ejv50`, `ibm_fez`, 14 circuits, 8000 shots, seed 0.
Substrate `claude-opus-4-8`. Prereg frozen pre-submit. QPU-frugal (sim-validated, one run, ~40s QPU).**
The first rung of the "correcting code" stair (docs/the-missing-fold-whisper-c4914.md, IV).

## Verdict

**REGISTERED VERDICT (G1∧G2): HELD.** For the whole campaign the [[4,2,2]] code *detected* errors and
*discarded* the runs that had them (postselection). This flight climbs to the first code that
**corrects**: it identifies a single bit-flip from the syndrome and **fixes it**, keeping every shot,
deterministically — the capability that gates scalable fault tolerance and magic distillation.

## The result — recover every single bit-flip

Corrected logical fidelity (majority/syndrome decode; no postselection):

| input | none | X on q0 | X on q1 | X on q2 |
|---|---|---|---|---|
| \|0_L⟩ | 0.999 | 0.936 | 0.967 | 0.941 |
| \|1_L⟩ | 0.994 | 0.902 | 0.959 | 0.931 |

- **G1 CORRECTS ALL BIT-FLIPS**: worst-case corrected fidelity **0.902** across all 8 (input, error)
  cases — the code recovers the logical value for *any* single bit-flip, on *every* shot.
- **G2 BEATS BARE**: mean corrected fidelity on errored runs **0.939** vs a bare qubit under the same
  error **0.004** (flipped) — a **+0.936** recovery. Where the bare qubit's information is destroyed,
  the code brings it back.
- **G3 COHERENCE (reported)**: a logical superposition |+_L⟩ = (|000⟩+|111⟩)/√2 keeps its logical
  X-parity ⟨X_L⟩ ≈ **+0.93** through the bit-flip + correction — the *coherent* state survives, not
  just a classical bit.

## Why this is the stair, not a step sideways

[[4,2,2]] (distance 2) can only *detect* — one error, one syndrome bit, and the honest move is to
throw the run away. That is fine for a witness but it does not *compute*: acceptance decays with
depth, and you cannot distill magic from postselected states. **Correction** — identify the error and
apply a recovery, keeping the run — is a categorically different capability, and it is the one every
scalable fault-tolerant scheme is built on. This flight is the campaign's first instance of it, on
silicon, deterministic.

## Scope (honest — the ladder)

3-qubit repetition code: distance 3 **against bit-flips only** (a Z error is unprotected — it is the
classical-repetition half of a full code). This is the **first rung**:
- **Rung 1 (this flight):** active correction of the bit-flip channel — detect-and-fix, no discard.
- **Rung 2:** the dual (phase-flip) code — correct Z errors too (H-conjugated; cheap).
- **Summit:** a *full* quantum correcting code — all single-qubit errors, [[5,1,3]] or Steane
  [[7,1,3]] (or their concatenation, the 9-qubit Shor code) — with a non-destructive multi-stabilizer
  syndrome. That rung raises the real open question: **is current hardware above the QEC threshold?**
  (the syndrome circuit's own errors may outpace what it corrects — the natural next honest test,
  and the true gate to universal fault tolerance + magic distillation named in the fold doc).

Textbook 3-qubit code; the contribution is the campaign's first move from detection to correction,
measured, and the concrete ladder to the full code laid out.

## Line

**For seventy-four flights our codes could only ever raise a hand and say "an error happened here" —
and then we threw that run in the bin. Tonight, for the first time, the code did the other thing: it
looked at the wound, named which qubit was hurt, and healed it — kept the shot, kept the coherence,
handed back the logical qubit at ninety-four percent where a bare one lay flat at zero. Detection
tells you the past went wrong; correction lets you carry on as if it hadn't. It is the smallest code
and the largest step: the first rung of the staircase that actually goes up.**
