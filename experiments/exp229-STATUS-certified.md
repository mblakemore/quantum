# Exp229 — THE PAST IS NOT WRITTEN: CERTIFIED — the Leggett-Garg temporal-Bell inequality

**Whisper C4913, 2026-07-20. Job `d9epva4jeosc73fj2v4g`, `ibm_fez`, 3 circuits, 8000 shots,
seed 0. Substrate `claude-opus-4-8`. Prereg frozen pre-submit.** A new wild one, chosen on Creator
review of the H5 results ("anything new? wild stuff?").

## Verdict

**REGISTERED VERDICT (G1∧G2): HELD.** The Leggett-Garg inequality — the *temporal* Bell inequality —
is violated: K3 = 1.429 beats the macrorealist bound of 1 (reaching 95% of the quantum maximum 1.5).
A qubit has no definite, non-invasively-knowable value between measurements: **reality is indefinite
in TIME**, just as Bell/CHSH showed it indefinite in space.

## The result

| correlator | measured | ideal cos |
|---|---|---|
| C12 = ⟨Q(t1)Q(t2)⟩ | +0.479 | +0.500 |
| C23 = ⟨Q(t2)Q(t3)⟩ | +0.474 | +0.500 |
| C13 = ⟨Q(t1)Q(t3)⟩ | −0.476 | −0.500 |

**K3 = C12 + C23 − C13 = 1.429 ± 0.017** (macrorealist bound 1, quantum max 1.5).

- **G1 MACROREALISM VIOLATION**: K3 = 1.429 > 1 at **25σ**. Any theory in which the qubit has a
  definite value at all times *and* can be measured non-invasively is excluded.
- **G2 QUANTUM VALUE**: K3 = 1.429, 95% of the ideal 1.5 — a small readout/measurement haircut only.

## What it is (and the P7 lesson applied)

A single qubit precesses under Rx(π/3) per step; Q = σ_z ∈ {+1,−1}; the two-time correlators are
measured by a projective mid-circuit measurement at the earlier time, evolution, then a second
measurement. K3 > 1 is impossible for a macrorealist (definite-value + non-invasive) description.

**Validity was checked explicitly** (the Exp228/P7 tautology lesson): the initial state is |+⟩, so
every first measurement is genuinely uncertain (~50/50), and the correlators carry real shot-noise
variance — K3 is a *physical* quantity that *can* fall below 1.5 (and did, to 1.429). This is a real
measurement of a violable bound, not an algebraic identity.

## Why it matters here

This is the **temporal complement** to the campaign's spatial-nonlocality results (CHSH at 72σ, the
magic-square game at 196σ) and the time-domain sibling of P3 (the arrow of time on the κ dial): the
same indefiniteness that Bell found across space, Leggett-Garg finds across time. The past between
measurements is not written.

## Scope (honest)

Single qubit, projective mid-circuit measurement (dynamic circuit). The macrorealist bound assumes
**non-invasive measurability**; testing it with projective measurement leaves the standard LG
"clumsiness/invasiveness" loophole (a genuine measurement disturbs the state) — stated, as in all
LG hardware tests; loophole-free LG needs ideal-negative-result or weak measurement. Textbook
Leggett-Garg (1985); new to the campaign. Depth-check before submit (0 two-qubit gates, the cheapest
flight of the campaign) — the 213 lesson, 16th consecutive.

## Line

**Bell taught us a pair of particles need not carry, between them across space, the answers to
questions no one has yet asked. Tonight a single qubit taught us the same across time: measured at
three moments, its correlations summed to 1.43, past the wall of 1 that any definite, quietly-knowable
history could not cross, at 25 sigma. The past, between glances, is not written — it is still a
superposition of what it might have been.**
