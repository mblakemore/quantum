# Finding — Exp157: ANYON BRAIDING — Z2 mutual statistics on ibm_fez

**Cycle**: C4846 · **Date**: 2026-07-18 · **Backend**: ibm_fez · **Job**: `d9drgc9htsac739dedu0`
(8 circuits: 6 Wilson-loop arms + 2 stabilizer receipts, 4096 shots; 2q-depths 12–27 after routing).
Creator directive: fly anyon braiding (Ember has the DD-on-receiver upgrade). Companion to the
exotic-phases wing.

## What it is

Particles confined to two dimensions need be neither bosons nor fermions. On a 7-qubit planar
toric-code patch (2 plaquettes, 6 stars, open boundaries) we prepare the loop-gas ground state
(CSS encoder from the GF(2) row-reduced star matrix — 5 H + CX layers), create m-anyons with
X-strings, and read the phase an e-anyon acquires circling an m as an **ancilla-controlled Wilson
loop**: ancilla in |+⟩, CZ along the loop, measure ⟨X⟩ = the loop's eigenvalue. One enclosed m
must give exactly −1 — the π mutual phase that defines anyonic statistics.

## The result — the phase counts enclosed topological charge, and nothing else

| arm | ⟨X_anc⟩ | expected | σ |
|-----|---------|----------|---|
| empty loop | +0.800 | +1 | 51 |
| **braid: m inside** | **−0.781** | **−1** | **50** |
| m outside the loop | +0.833 | +1 | 53 |
| deformed loop, same m | −0.796 | −1 | 51 |
| pair enclosed (fusion) | +0.779 | +1 | 50 |
| pair straddling the loop | −0.823 | −1 | 53 |

Six arms, six correct signs at ~50σ each, contrast 0.78–0.83 essentially flat across loop sizes.
Together they close every classical loophole on each other:
- −1 appears **only** when the enclosed m-charge is odd (arms 1,2,5,6) — Z2 fusion: two anyons
  inside give (−1)² = +1; a pair straddling the loop counts only its enclosed member.
- Charge **outside** the loop does nothing (arm 3) — locality.
- Deforming the loop around the same charge changes nothing (arm 4) — the phase is topological,
  a property of the enclosed charge, not of the path's shape or length.

## The receipts — order in loops, not in locals

Same ground state, no ancilla: plaquettes B_p = +0.856/+0.818 and stars A_v = 0.866–0.949, while
**every single edge measures as a fair coin** (⟨Z_i⟩ = 0.00–0.06). The loops are certain while
their parts are random — that coexistence is the signature of topological order; no product state
can show it, and it is what makes the Wilson-loop values topology rather than parity bookkeeping
on a classical bit-string.

## Prediction record (logged)

Pre-registered: all signs >5σ (held) with contrast 0.3–0.6 — **actual 0.78–0.83, above the
band**. Second consecutive magnitude miss in opposite directions (Exp156 too optimistic on the
offset, Exp157 too pessimistic on contrast — I over-weighted the Exp147 routing-cost lesson;
level-3 routing on 8 qubits was cheap). Signs and mechanisms right both times; magnitude priors
carry ~2× error either way. Future pre-registrations: bands 2× wider, sign claims stay hard.

## Fence

Abelian Z2 (toric-code) **e–m mutual statistics** read by single-shot Wilson-loop interferometry
— not non-abelian braiding (no computation by braiding), not adiabatic anyon transport, not fault
tolerance. One small patch, open boundaries, raw hardware. The ~0.2 contrast loss is circuit
noise; the six signs are the physics.
