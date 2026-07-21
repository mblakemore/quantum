# Exp211b (Braket) — IonQ definite-order NULL: closing the compiler-mapping loophole

**Pre-registration — frozen before submission. Substrate: claude-opus-4-8. Whisper, C4942.**

## Question
The Exp211 IonQ witness (W=1.894, WITNESS-FIRED) was witness-only — no downstream null-integrity arm.
An external review (Gemini eval, relayed by Creator) named the remaining loophole precisely: *a native
compilation could, remotely, map the gates so as to yield W>0 for the specific witness states for a
reason other than genuine indefinite order.* The semantic smoke validated the qubit mapping + bit
convention, but is NOT a definite-order control, so it does not close this. This flight closes it.

## Test
Run the **causal-mixture control**: the SAME two witness measurements (XX, XZ) on the **definite-order**
circuit (`build_circuit(..., definite=True)`) instead of the switch (`definite=False`). A faithful
compilation MUST give **W_definite ≈ 0** for a definite-order (causally-separable) process. If it does,
the switch's W=1.894 is genuinely from the order superposition, not a mapping artifact.

- Circuits: `wnull_c = build_circuit("X","X",0,definite=True)`, `wnull_a = build_circuit("X","Z",0,definite=True)`.
- Observable: W_definite = ⟨X_c⟩_comm − ⟨X_c⟩_anti (same formula as the witness).
- Shots: 100/circuit (seW = √(2/100) = 0.141). The null only needs to show W≈0, decisively below 1.894.
- Submission: `backend.run(native=True)` — identical IonQ native (GPI/GPI2/RZZ) + verbatim path as Exp211.
- Local-sim validation: **W_definite = 0.0000, NULL-CLOSED, 12.2σ below the switch value.**

## Criterion (frozen)
- **NULL-CLOSED** if **|W_definite| < 0.3** (collapses to ~0, decisively separated from the switch's 1.894).
- **NULL-FAIL** if |W_definite| ≥ 0.3 — would indicate the compilation produces W>0 as an artifact, and
  would retroactively qualify the Exp211 witness claim. Kept in the record either way.

## Device & cost
IonQ Forte-1 (`arn:aws:braket:us-east-1::device/qpu/ionq/Forte-1`).
2 circuits × 100 shots = 2×$0.30 + 200×$0.08 = **$16.60**. IonQ cumulative → **$194.40 < $200 ceiling**.

## Pre-filed prediction
- **Predict NULL-CLOSED, W_definite ≈ 0, confidence ~0.9.** The definite-order circuit is causally
  separable by construction; on ~99% ions it should read cleanly near 0. Local sim gives exactly 0.
- **Named failure mode**: W_definite far from 0 → a genuine compilation artifact (the loophole is real,
  not remote). This would be a significant negative and is kept in the record with full weight.

## Outcome handling
- CLOSED → the Exp211 witness upgrades from *witness-only* to *witness + definite-order null*; update the
  white paper (§6 limitation #1 and §4.3) to report the loophole closed, bringing IonQ's rigor near Rigetti's.
- The all-to-all topology confound (Gemini's 2nd point) is separate, inherent, and not closable by a null;
  it stays a stated caveat (already minimized: adjacent-pair 2-qubit witness, zero SWAPs on any platform).
