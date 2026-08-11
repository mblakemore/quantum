# H13 Cell 5 pigeonhole — PRE-REGISTRATION (FROZEN before submit)

**Author**: Whisper (DC15W), C5060 · **Board**: #82 · **Creator GO**: general#10286 "get the next priority flown"
**Design study this rests on**: `findings/h13-cell5-pigeonhole-FLYABLE-preflight-complete-whisper-c5060.md`
**Tools**: `tools/h13_cell5_pigeonhole_resolution_precheck.py`, `tools/h13_cell5_pigeonhole_transpile_price.py`
**Genre**: foundations. **NOT an advantage claim** — no claim card, nothing for attack_preflight.
**This file is frozen at commit before submit. Any edit after submit invalidates the flight.**

## The claim

Three particles, two boxes. Pre-select |+++⟩, post-select |+i,+i,+i⟩. **No two particles are ever
found in the same box** — every pair's weak value of Π_same is zero — while any classical
assignment of 3 pigeons to 2 boxes forces at least one shared pair.

**Classical floor, enumerated in-code over all 2³ assignments** (`resolution_precheck.py` Part 2),
never quoted from Aharonov et al.:

```
min shared pairs over all 8 assignments = 1
=> sum of the three classical pair-probabilities >= 1
```

## Frozen parameters

| | |
|---|---|
| Backend | `ibm_marrakesh` |
| Account | `IBMQ_ALT4` (declared open/free by the Creator, board#10133) |
| Coupling | **ε = 0.25**, identical in every arm |
| Shots | **20,000 per pair × 3 pairs + 20,000 control = 80,000** |
| Expected keep | 12.50% per arm (2,500 kept per pair) |
| Estimated cost | **≈25 QPU-s** (0.31 ms/shot, from Cell 3 = 16s/54k, Cell 4 = 11s/32k, Hardy = 15s/48k) |
| Ask under G-EPOCH margin | max(25×1.5, 25+20) = **45 s** |

**Why ε = 0.25 and not smaller.** The pigeonhole weak value is **exactly zero at every coupling**
(verified across ε ∈ {1.0, 0.5, 0.25, 0.1, 0.05, 0.02, 0.01}), so a larger ε cannot bias the null —
but it makes the *control* signal large. At ε = 0.25 the control shift is sin(0.25) = 0.2474,
**12× the ~2×10⁻² device noise floor**, at 1% departure from linearity.

## Gates — all frozen, numeric, and checked in this order

**G1 — CONTROL MUST MOVE (premise gate; failure = NO-TEST, not a result).**
Post-selecting on |+++⟩ instead of |+i,+i,+i⟩ gives a known weak value of 0.5. Measured control
shift must be **≥ 0.15** (predicted 0.2474; the bar is set well below prediction so ordinary
hardware attenuation does not fail a live apparatus).
*Rationale: the pigeonhole prediction is ZERO, so a dead apparatus and a successful detection
produce the same reading. Without G1 this experiment cannot distinguish them and is not a
measurement. G1 is checked FIRST and a failure stops the analysis.*

**G2 — ALL THREE PAIRS NULL.** Each pair's measured |shift| ≤ **0.06** (3× the noise floor).

**G3 — THE HEADLINE, and it is a SUM not a per-pair claim.** The three pair values converted to
"same box" probabilities must sum to **< 0.5**, against the enumerated classical floor of **≥ 1**,
at **≥ 5σ**. Predicted sum ≈ 0; se(sum) ≈ 0.035 from 2,500 kept per pair, so the floor sits ≈ 28σ away.

**G4 — KEEP FRACTIONS PRINTED** for every arm, and each within **[0.09, 0.16]** of the ideal 0.125.
A keep fraction far off 12.5% means the post-selection is not the registered one.

## What would falsify this

- **Control does not move** → NO-TEST. The apparatus is not demonstrated live; nothing is claimed.
- **Any pair reads |shift| > 0.06** → the effect does not reproduce on hardware; report as a failure
  of the effect, not of the instrument, *provided G1 passed*.
- **Sum ≥ 0.5** → the pigeonhole census fails and the classical floor is not beaten.
- **Keep fraction outside [0.09, 0.16]** → post-selection is wrong; NO-TEST.

## Honesty fences (standing, from the arc header)

1. Post-selection budgets printed for every arm — this effect lives entirely in a sifted ensemble.
2. The classical floor is enumerated in code, never cited.
3. Not an advantage claim; foundations genre, labelled in the finding's header.
4. **Weak-value scope**: this certifies the pigeonhole effect *under the frozen measurement model*
   (von Neumann coupling at ε = 0.25, ancilla pointer read in X). It is not a claim about where
   particles "are" absent that model.
5. Sim ≠ hardware: everything above is predicted from noiseless statevector plus a FakeMarrakesh
   noise model (bias −0.00568 ± 0.00632). The flight is the measurement.

## Pre-registered prediction

All three pairs read zero within the noise floor; the sum lands near 0 against a classical floor of
1; the control moves to ≈0.25. **If the control fails, I report a NO-TEST and no pigeonhole claim
is made, regardless of what the three pairs did** — the pairs' zeros would be uninterpretable and I
will not present them.
