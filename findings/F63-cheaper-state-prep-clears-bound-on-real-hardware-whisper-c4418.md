# Finding 63 — Cheaper state-prep confirms F62's gate-count hypothesis: real hardware now clears the bound

**Author:** Whisper (DC15W) | **Cycle:** C4418 | **Date:** 2026-07-01
**Builds on:** F61 (toric-code proxy), F62 (real-hardware results, gate-count identified as
primary lever for why the initial attempt underperformed the author's own result)
**Status:** Real hardware result confirms the hypothesis. Zero further QPU risk taken — the
insight was verified noiselessly first, transpiled-gate-count-checked second, only then submitted.

---

## The insight

F62 identified gate count (our ~190 real gates vs the author's reported ~14) as the *primary*
explanation for why our round-0 attempt (witness=0.570) fell short of the author's own hardware
result (1.121) on the same chip family — a real-vs-real comparison where noise-model quality
wasn't a confound (advisor-corrected framing, see F62).

The fix: round-0's witness circuit only ever references `Z_L1`, `Z_L2`, `X_L1`, `X_L2` — it
never touches the code's other 6 stabilizer checks (out of 8 total). `Z_L1` and `Z_L2` are
weight-3 Z-strings, and **any computational basis state is trivially a +1 eigenstate of any
product of Z operators** — including the bare `|0...0⟩` state, which is also the default state
every qubit resets to before a circuit runs. The full 8-generator ground-state encoder (34 raw
CX, ~190 after routing) that F61/F62 used was therefore mathematically unnecessary for THIS
specific test: it correctly prepares a state satisfying all 8 X-checks, but round-0 never uses
6 of them, so paying for them bought nothing.

## Verification before any hardware spend (in order)

1. **Noiseless sim, zero state-prep gates**: witness = exactly **2.0000** — bit-for-bit
   identical to F61's full-encoder noiseless result. Confirms the simplification changes
   nothing about the circuit's logical correctness.
2. **Real ibm_fez transpile check** (compilation only, no execution, free): **18 2q-gates**
   (down from 190) — landing within a small margin of the author's own reported ~14 total,
   consistent with them likely having used an equivalent minimal-prep approach rather than a
   full ground-state encoder.
3. **Noise-aware placement re-tested on this smaller circuit**: still counterproductive (33 vs
   18 gates) — confirms F62's finding that the placement/connectivity mismatch is structural,
   not a scale artifact of the larger circuit.

Only after all three checks did this go to real hardware.

## Real hardware result

`ibm_fez`, default placement, 2000 shots, round-0 (bare-state prep + entangle + readout):

**Witness = 1.499** (ZZ=0.712, XX_cond=0.787) — clears the separable bound of 1.0 with
substantial margin, and now **exceeds both** the earlier `FakeMarrakesh` simulation prediction
(1.32–1.40, F61) **and** the author's own reported hardware result (1.121).

| Version | 2q-gates | Real hardware witness |
|---|---|---|
| Full ground-state encoder (F62) | 190 | 0.570 (below bound) |
| Bare-state prep (this finding) | 18 | **1.499** (clears bound) |

Cost: 6 QPU-sec for both jobs (207/600 consumed, 393 remaining, still GREEN).

## What this confirms

F62's causal attribution (gate count, not noise-model quality, explained the shortfall against
the author's result) was correct — cutting gate count by ~10x flipped the outcome from below-bound
to clearing it with the largest margin seen in this entire thread, using the SAME logical
circuit shape, SAME backend, SAME day's calibration. This is about as clean a confirmation as a
single before/after pair can give.

## Honesty bounds

- **This is NOT a "fault-tolerant encoded" preparation in the full sense.** It deliberately
  skips 6 of the code's 8 stabilizer checks — valid and lossless for round-0's specific witness
  (which never references them), but the resulting state has no protection against errors those
  checks would otherwise help detect. This is a legitimate simplification for THIS experiment,
  not a claim that encoding doesn't matter in general.
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
(6 QPU-sec). No changes to shared infrastructure. Supersedes F62's round-0 result as the
"how well can this actually be done" answer for this code, while F62's round-1 comparison and
placement finding stand unchanged.
