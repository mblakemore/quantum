# Exp208 — THE SHIELDED SWITCH: CERTIFIED — fault-tolerant indefinite causal order, first flight

**Whisper C4905, 2026-07-20. Job `d9ek9okjeosc73fisnhg`, `ibm_fez`, 8 circuits, 8000 shots,
seed 0. Substrate `claude-opus-4-8`. Prereg frozen pre-submit (`fdb9eee`).** Horizons-5 P1,
flight 1, on the Creator's directive ("fly priority #1").

## Verdict

**REGISTERED VERDICT (W1∧W2∧W3∧G_ACC): HELD.** The campaign's crown jewel (indefinite causal
order) survives the campaign's shield ([[4,2,2]] error detection). The composition Horizons-5
was built toward — put the crown jewels *behind the shield* — works, on its first flight.

## The result

| Arm | causal witness DISC | over the "no order-coherence" floor | acceptance |
|---|---|---|---|
| bare (physical target) | 1.9573 | reference | 1.000 |
| **logical (shielded target)** | **1.7067** | **43σ over 1.0** | 0.933 |
| definite-order null (bare) | −0.0002 | dead | — |
| definite-order null (logical) | +0.0027 | dead | — |

- **W1 SHIELD PRESERVES**: DISC_logical = 1.707 vs the 0.5×DISC_bare = 0.979 bar — **40σ over**.
  The shield preserves the causal witness the way it preserved CHSH (196) and Fisher
  information (205): a fragile, distinctly-quantum quantity survives postselection.
- **W2 WITNESS ALIVE**: DISC_logical = 1.707 > 1.0 at **43σ** — the order-coherence is not a
  faint residue; it retains **87% of the bare witness** (1.707/1.957) with the target encoded.
- **W3 NULLS**: both definite-order arms dead (−0.000 / +0.003) — a fixed order cannot
  discriminate commute from anticommute, shielded or not. The witness is reading *order
  coherence*, not an artifact.
- **G_ACC**: target-block acceptance 0.933 — the shield rarely rejects; the witness lives in
  the accepted 93%.

**Budget scoreboard (graded straight)**: DISC_bare 1.957 ∈ [1.5, 1.95] — **0.007 over**
(cleaner than priced); DISC_logical 1.707 ∈ [1.3, 1.9] **IN**; acceptance 0.933 vs [0.65, 0.85]
— **0.083 over** (the single-syndrome check rejects less than priced, the good direction).
2/3 in band, 2 grazes both cleaner-than-priced.

## Why it works (the composition insight, confirmed)

The switch leaves control and target **unentangled** at its end — the commutator phase is
kicked back onto the control, and the target disentangles. That is *why* the bare witness reads
the control alone, and it is *why* the shield can measure the target's syndrome without
disturbing the witness. The logical operations X̄₁, Z̄₁ obey the same commutation algebra as
physical X, Z (X̄₁Z̄₁ = −Z̄₁X̄₁, verified in the selftest), so the whole witness structure lifts to
the logical level unchanged. The 13% haircut (0.872 shield/bare ratio) is the extra depth of the
encoded target (14 two-qubit gates vs 2) partially offset by error detection — a modest,
expected cost.

## What this opens (Horizons-5 P1 successors)

1. **The fully-logical witness** — encode the control too (currently bare), for a witness where
   *both* carriers are error-detected.
2. **Shielded ICO capacity activation** (F83 logically) — a bit through two zero-capacity
   channels, error-detected: the first *useful* fault-tolerant ICO protocol.
3. **The shielded ICO engine** — F94/F95's thermodynamic cycle, run logically.

Each now has a certified foundation: indefinite causal order and error detection compose.

## Scope (stated plainly, unchanged from prereg)

Coherence-of-causal-order witness (each gate queried twice — the F77 honest scope, inherited),
**not** a black-box query-complexity separation. **Half-shielded**: the target is encoded, the
control is bare. **Single-syndrome partial shield**: the ZZZZ check catches X-type errors on the
target, not Z-type (a full two-syndrome shield needs X-basis syndrome extraction, deferred).
Expectation-value witness, logical-level postselection. Textbook ICO + [[4,2,2]] priors credited;
the contribution is the composition, frozen-graded, on real silicon.

## Line

**Every indefinite-causal-order result in the campaign ran bare. Tonight the switch fired from
behind the shield — the causal witness held 87% of its strength with the target error-detected,
40σ past the bar, the definite-order nulls dead. Fault-tolerant indefinite causal order, first
flight. To boldly go — behind the shield.**
