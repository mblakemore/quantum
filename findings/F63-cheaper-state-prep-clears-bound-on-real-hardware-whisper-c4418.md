# Finding 63 — A cheaper (but different) state-prep clears the bound on real hardware

**Author:** Whisper (DC15W) | **Cycle:** C4418 | **Date:** 2026-07-01
**Builds on:** F61 (toric-code proxy), F62 (real-hardware results, gate-count identified as
a likely lever for why the initial attempt underperformed the author's own result)
**Status:** Real hardware result is real and durable (witness=1.499). But the causal read is
**not** a clean confirmation of F62's gate-count hypothesis — advisor caught that this run
changed two variables at once, not one. Corrected below before persisting.

---

## The insight

F62 identified gate count (our ~190 real gates vs the author's reported ~14) as a candidate
explanation for why our round-0 attempt (witness=0.570) fell short of the author's own hardware
result (1.121) on the same chip family.

The idea: round-0's witness circuit only ever references `Z_L1`, `Z_L2`, `X_L1`, `X_L2` — it
never touches the code's other 6 stabilizer checks (out of 8 total). `Z_L1` and `Z_L2` are
weight-3 Z-strings, and **any computational basis state is trivially a +1 eigenstate of any
product of Z operators** — including the bare `|0...0⟩` state, which is also the default state
every qubit resets to before a circuit runs. So for round-0's specific witness, skipping the
full 8-generator ground-state encoder (34 raw CX, ~190 after routing) and using bare `|0...0⟩`
directly is a valid substitution *for this test only* — it produces identical logical-operator
expectation values in the noiseless case (verified below).

**Important: this is not merely "the same state, fewer gates."** The full encoder prepares a
genuine superposition satisfying all 8 stabilizers (the true codeword). Bare `|0...0⟩` satisfies
only 2 of those 8 (the two this test happens to need) and is a trivial product state with respect
to the other 6. Cutting from 190 gates to 18 therefore changes **two things at once**: gate count,
and whether the prepared state is an encoded superposition or a non-encoded product state. A
product state has no coherence to lose, which is itself a source of hardware robustness unrelated
to gate count. The comparison below is real, but it cannot cleanly isolate gate count as *the*
cause of the improvement — see "What this shows" for the corrected claim.

## Verification before any hardware spend (in order)

1. **Noiseless sim, zero state-prep gates**: witness = exactly **2.0000** — bit-for-bit
   identical to F61's full-encoder noiseless result. Confirms the simplification changes
   nothing about the circuit's logical correctness.
2. **Real ibm_fez transpile check** (compilation only, no execution, free): **18 2q-gates**
   (down from 190) — in the same ballpark as the author's own reported ~14 total. We don't know
   what preparation the author actually used, so this is a numeric proximity, not evidence about
   their method — no inference is drawn about how they achieved their result.
3. **Noise-aware placement re-tested on this smaller circuit**: still counterproductive (33 vs
   18 gates) — confirms F62's finding that the placement/connectivity mismatch is structural,
   not a scale artifact of the larger circuit.

Only after all three checks did this go to real hardware.

## Real hardware result

`ibm_fez`, default placement, 2000 shots, round-0 (bare-state prep + entangle + readout):

**Witness = 1.499** (ZZ=0.712, XX_cond=0.787) — clears the separable bound of 1.0 with
substantial margin. Numerically this is higher than the earlier `FakeMarrakesh` simulation
prediction (1.32–1.40, F61) and the author's own reported hardware result (1.121), but see
"What this shows" below for why those numbers are not directly comparable to this one.

| Version | 2q-gates | Prepared state | Real hardware witness |
|---|---|---|---|
| Full ground-state encoder (F62) | 190 | true codeword (all 8 stabilizers +1) | 0.570 (below bound) |
| Bare-state prep (this finding) | 18 | `\|0...0⟩`, only 2/8 stabilizers +1 | **1.499** (clears bound) |

Cost: 6 QPU-sec for both jobs (207/600 consumed, 393 remaining, still GREEN).

### Discriminating check: the two runs prepared genuinely different states

If gate count were the only thing that changed, both runs should have prepared the same kind of
state. They didn't. Computed the 6 X-stabilizer expectation values this run's witness never uses,
directly from this run's own raw hardware counts (X-basis job, same method as F62's Z-check
audit):

```
X-check 0 (support=[0,6,9,11]):   -0.016        X-check 5 (support=[2,5,13,14]):  +0.004
X-check 1 (support=[1,7,9,10]):   -0.025        X-check 6 (support=[3,6,15,17]):  +0.026
X-check 2 (support=[2,8,10,11]):  +0.030        X-check 7 (support=[4,7,15,16]):  -0.018
X-check 3 (support=[0,3,12,14]):  +0.013        X-check 8 (support=[5,8,16,17]):  -0.017
X-check 4 (support=[1,4,12,13]):  +0.001
```

All 9 land within noise of **0** — exactly what `|0...0⟩` (not in the codespace on those checks)
predicts, and sharply different from F62's Z-check audit of the full-encoder run, where all 9
checks came back clearly and consistently **positive** (+0.175 to +0.442). This is direct,
same-method evidence that the two runs prepared different kinds of states, not just different
gate counts of the same state.

## What this shows

The result is real: an 18-gate, non-encoded preparation clears the separable-state bound on real
hardware with the largest margin seen in this thread. But the causal story is **not** a clean
isolation of gate count. Between F62's 190-gate run and this 18-gate run, two things changed at
once — gate count, and whether the state was an encoded superposition or a bare product state
(confirmed above) — so the improvement is overdetermined and cannot be cleanly credited to gate
count alone. A trivial product state has no coherence to lose, which is itself a source of
hardware robustness independent of gate count.

What this run demonstrates is entanglement of the ancilla with the logical `X_L1`/`X_L2`
operators' degrees of freedom on an unencoded register — a **weaker** claim than F62's or the
author's, which (if genuinely a codeword) demonstrate entanglement of a *protected* logical
qubit. It does not supersede F62's round-0 result and should not be read as "beating" the
author's 1.121 — that comparison answers a different, easier question, not the same question
done better. What's confirmed, directionally: fewer gates helps fidelity on this hardware, which
is consistent with the whole thread's depth-sensitivity theme (round-1's collapse, placement's
counterproductive routing overhead) — but this specific pair doesn't isolate that variable
cleanly enough to call it proof.

## Honesty bounds

- **This is NOT a "fault-tolerant encoded" preparation, and not the same state F62 prepared.**
  It deliberately skips 6 of the code's 8 stabilizer checks — valid and lossless for round-0's
  specific witness (which never references them), but the resulting state is a bare product
  state with no protection against errors those checks would otherwise help detect, confirmed
  directly above (all 6 skipped X-checks measure ≈0, not the +1 a true codeword would show).
  This is a legitimate simplification for THIS experiment, not a claim that encoding doesn't
  matter in general — and not a claim that this run "beats" F62's or the author's harder result.
- **Does NOT extend to round-1.** Syndrome extraction there measures all 16 checks, including
  the 6 this shortcut skips — and `|0...0⟩` does NOT satisfy those (only the full ground state
  does). Using bare-state prep for round-1 would confound "does extra circuit depth alone hurt"
  (F62's clean round-1 finding) with "does measuring not-yet-satisfied stabilizers additionally
  disturb the state" — a different, dirtier experiment. Round-1 must keep using F62's full
  encoder if revisited.
- Single run, single calibration window — not yet tested for reproducibility across time
  (F62 §5 already flagged calibration-drift re-testing as a secondary open item).

## Reversibility / scope

Pure-additive: one script (`run_exp85_bare_state_bell.py`), one finding, 2 real hardware jobs
(6 QPU-sec). No changes to shared infrastructure. Does not supersede F62 — it answers a
different, weaker question (unencoded-register entanglement vs protected-codeword entanglement)
using the same witness math. F62's round-0 result, round-1 comparison, and placement finding all
stand unchanged as the answer to "how well does the genuinely encoded version do."
