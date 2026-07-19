# Exp185 Pre-registration — THE UNIVERSE WHERE TIME IS OPTIONAL: Page-Wootters emergent time

**Cycle**: C4875 · **Date**: 2026-07-19 · **Backend**: ibm_fez · **Shots**: 8000 × 7 circuits
**Class**: foundations (Page & Wootters 1983; Moreva et al. 2014, circuit form). Creator go:
ship-computer general#86.

## The universe

Three qubits: a 2-qubit **clock** C (ticks t = 0..3) and a 1-qubit **system** S, prepared in
the Feynman **history state** |Ψ⟩ = ½ Σ_t |t⟩_C ⊗ S^t|+⟩_S (law of physics U = S, chosen so
U⁴ = I exactly — the 4-tick clock wraps cleanly). Preparation is 3 H's + controlled-S (from the
1s tick bit) + CZ (= controlled-S², from the 2s bit). Three claims, one universe:

1. **The inhabitants have time**: conditioned on the clock reading t, the system is caught
   mid-evolution — Bloch vector sweeping the equator 90°/tick: (X,Y) = (+1,0) → (0,+1) →
   (−1,0) → (0,−1). Read out by conditional tomography (system X and Y bases × clock Z).
2. **The outside has none**: the internal time-translation T = (clock increment mod 4) ⊗ S
   leaves |Ψ⟩ exactly invariant. Certified by Loschmidt echo: prep → T → prep⁻¹ → P(000).
   Control within the claim: the **wrong-law** translation T′ = increment ⊗ 𝟙 (tick the clock
   without evolving the system) has |⟨Ψ|T′|Ψ⟩|² = 1/2 exactly — a translation is invisible
   only if it carries the law of physics with it.
3. **Time has an off-switch**: cut the clock–system entanglement (same preparation minus the
   two controlled gates) and the inhabitants' time VANISHES — every conditional state is the
   same |+⟩, the sweep collapses to zero. Time in this universe *is* the entanglement.

## Arms / circuits (7 total)

| circuit | what |
|---------|------|
| history × {X, Y} | conditional tomography of the evolving universe |
| echo_id | prep → prep⁻¹ (preparation-quality baseline) |
| echo_T | prep → (increment ⊗ S) → prep⁻¹ — the frozen-outside certificate |
| echo_Tclock | prep → (increment ⊗ 𝟙) → prep⁻¹ — the wrong-law control (ideal ½) |
| notime × {X, Y} | product universe (no entanglement) — the off-switch |

## Pre-registered predictions (three-legged primary, all must hold)

1. **Internal time**: history-arm mean per-tick fidelity to S^t|+⟩ ≥ 0.90 (band 0.92–0.98),
   with the (X,Y) sign pattern correct at all four ticks.
2. **External frozen**: echo_T ≥ 0.80 (band 0.82–0.95) AND echo_T − echo_Tclock ≥ 0.25
   (bands: echo_Tclock 0.40–0.55, ideal 0.50; echo_id 0.88–0.98 as the prep ceiling —
   echo_T within 0.06 of echo_id is the sharp form: the correct-law translation costs nothing).
3. **Off-switch**: notime-arm mean per-tick fidelity to the STATIC |+⟩ ≥ 0.90 (band
   0.93–0.99), i.e. the sweep collapses (fidelity to the *evolving* prediction necessarily
   fails at t=2 where |+⟩ vs |−⟩ are orthogonal).

## Fences, stated up front

A 4-tick cyclic toy universe on 3 transmons: "external time" is circuit depth (the physical
chip of course sits in lab time — the claim is about the STATE's invariance under its own
internal translation, the Page-Wootters statement, not about stopping lab clocks); U = S is
Clifford (deliberate: exact wrap, cheap prep — a non-Clifford law is a follow-up); conditional
tomography uses X,Y only (the evolution lives on the equator; Z ≈ 0 throughout is a free gauge,
reported). The "off-switch" removes entanglement at preparation — a mid-flight disentangling
operation is a (named) follow-up, not claimed.

## Discipline

ps aux: clean. Claim: exp185 (whisper C4875). Ledger prediction pre-submit. Prereg committed
before decode. Selftest gates: per-tick F > 0.99 with correct sign pattern; echo_id & echo_T
> 0.99; echo_Tclock = 0.50 ± 0.02; notime static-F > 0.99.
