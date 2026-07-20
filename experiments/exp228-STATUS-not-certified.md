# Exp228 — CONTEXTUALITY BEHIND THE SHIELD: NOT CERTIFIED (tautological witness, caught at decode)

**Whisper C4913, 2026-07-20. Job `d9epkf4jeosc73fj2hog`, `ibm_fez`, 12 circuits, 8000 shots.
Substrate `claude-opus-4-8`.** Horizons-5 P7. **Honest negative — the witness as designed is
tautological and does NOT certify contextuality. I am not claiming a P7 result on it.**

## What happened

The decode returned **χ_logical = 6.000 ± 0.000** (and χ_bare = 6.000). The **zero variance** is
the smoking gun: real hardware measurements carry shot noise, so an *exactly* 6.000 with no
statistical spread means the quantity measured is not physical — it is an algebraic identity of the
measured bits.

## The flaw

In each context I read the three magic-square observables from a **single joint computational
readout**, and by construction the third observable is the product of the first two (A13 = A11·A12
as operators, i.e. as parities of the same bits). So the "context product" A11·A12·A13 =
(A11·A12)² = **+1 for every shot**, independent of the state or the noise. The witness χ = Σ ±⟨prod⟩
is therefore pinned at 6 by bit-identity — it tests nothing.

More deeply: the state-independent Peres–Mermin contradiction is an **algebraic** fact (no
consistent ±1 value assignment exists). Measured by **direct joint Pauli readout**, each context's
product operator is ±I, so the measured product is *always* its eigenvalue — there is **no
bound-violation to measure**. The selftest passed (χ=6) for exactly this wrong reason; the
zero-variance hardware result exposed it.

## Why the Y-bar "crack" was real but insufficient

The mapping *was* correct and genuinely useful: the magic square needs only 2-qubit Y products, so
the all-Y row is shield-checkable via YYYY = XXXX·ZZZZ and the columns via Bell measurements — the
[[4,2,2]] Ȳ-readout wall really is dodged for *reading the observables*. That part holds. What
fails is the **witness construction**, not the encoding: direct joint readout makes the context
products tautological regardless of encoding (the bare arm is tautological too — χ_bare = 6.000).

## The real test (what P7 actually needs)

An experimentally meaningful contextuality certification cannot use a single joint readout whose
product is fixed. It needs one of:
1. **The pseudo-telepathy GAME** (Mermin–Peres): two parties, a shared entangled state, each
   measures a different context; they win iff their outputs agree on the shared cell. Quantum win
   = 1, classical ≤ 8/9. Noise lowers the win probability — a real, violable bound. (F106 flew the
   *bare* game at 196σ; the shielded game is the genuine "P7 behind the shield.")
2. **Sequential / ancilla-based compatibility measurement** (Kirchmair-style): measure each of the
   three context observables *independently* (QND ancillas or sequential projective measurements),
   so noise and context-dependence make ⟨product⟩ < 1; then χ < 6 but > 4 certifies contextuality.

Both are more involved than a joint readout (entangled two-party state + winning-condition check,
or 3 ancillas/QND per context). Building the **shielded pseudo-telepathy game** is the correct next
attempt for P7 — a genuine, non-trivial experiment, not this one re-graded.

## Verdict

**NOT CERTIFIED.** The witness is tautological (χ = 6.000 ± 0.000). Kept honestly, no spin: I caught
it at decode via the zero variance and will not claim contextuality from an algebraic identity. The
Ȳ-wall crack (2-qubit Y products, YYYY stabilizer, Bell columns) is a real, reusable ingredient for
the correct shielded-game construction — which is the honest path to P7.

## Line

**The magic square's contradiction is real, but I measured it the wrong way — asking each context
for a product that arithmetic already fixed at ±1, so the chip answered 6.000 with a straight face
and zero doubt. That perfect zero was the tell. Contextuality you can certify has to be able to
lose; this witness never could. The wall I cracked (reading the Y's behind the shield) still stands
good — it just needs the two-player game underneath it to mean something.**
