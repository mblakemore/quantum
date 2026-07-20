# Exp218 — THE COHERENT FEDERATION: CERTIFIED — the distributed logical CNOT is genuinely quantum

**Whisper C4907, 2026-07-20. Job `d9en584jeosc73fivo80`, `ibm_fez`, 12 circuits, 8000 shots,
seed 0. Substrate `claude-opus-4-8`. Prereg frozen pre-submit.** Horizons-5 **P6 flight 2** —
closes flight 1's coherence gap.

## Verdict

**REGISTERED VERDICT (G1∧G2∧G3): HELD.** On `|+̄⟩_A|0̄⟩_B` the distributed CNOT makes a **logical
Bell pair** across the shielded cut — **both** ⟨Z̄_AZ̄_B⟩ and ⟨X̄_AX̄_B⟩ ≈ +1. Exp217's
software-welded distributed gate is therefore a genuine **quantum** gate, not a classical
permutation.

## The result

| arm (weld) | ⟨Z̄Z̄⟩ | ⟨X̄X̄⟩ | frame-off (Z, X) | truth table |
|---|---|---|---|---|
| **SW** (software frame — 217's method) | **+0.873** | **+0.890** | −0.016, −0.003 | 0.928 (210σ) |
| FF (live feed-forward, dynamic) | +0.787 | +0.339 | (live) | 0.910 (162σ) |

- **G1 COHERENCE (SW)**: ⟨Z̄Z̄⟩ = 0.873 **and** ⟨X̄X̄⟩ = 0.890, each ≫ 5σ over 0. Both Bell
  correlators positive = genuine entanglement. A classical correlation gives ⟨X̄X̄⟩ ≈ 0; **the
  distributed CNOT is quantum.**
- **G2 TRUTH (SW)**: mean P(correct) 0.928 over the 4 basis inputs, min **210σ** over the ¼ floor.
- **G3 FRAME-OFF FALSIFIER**: ignore the frame bits → ⟨Z̄Z̄⟩ = −0.016, ⟨X̄X̄⟩ = −0.003, both
  collapse to zero. **The weld is the classical bits** (the 217/197 falsifier form, on the
  coherence).

## The bonus finding (G4) — the software weld beats live feed-forward

The two welds were flown side by side. In theory both are coherent (deferred Pauli corrections =
feed-forward when no Clifford follows). **On silicon they are not equal: SW ⟨X̄X̄⟩ = 0.890 vs FF
⟨X̄X̄⟩ = 0.339.** The live feed-forward's mid-circuit measurement + real-time conditional gate
adds latency during which the data qubits idle and decohere — and it is the **conjugate basis**
that pays (⟨X̄X̄⟩ falls from 0.89 to 0.34 while ⟨Z̄Z̄⟩ only 0.87→0.79). **Post-hoc software
bookkeeping is both cheaper and more coherent than a live classical channel on today's hardware.**
A practical result for distributed quantum computation: don't pay for feed-forward when a terminal
Pauli frame suffices.

## Why flight 1 couldn't see this, and flight 2 can

Flight 1 (2-block) put the ebit inside the data block; the 191-map **shared-q0** structure forbids
reading a data qubit and its in-block ebit in incompatible bases, so ⟨X̄X̄⟩ was unreachable — 217
could only certify the computational truth table. This flight puts the ebits in a **physical relay**
(q8, q9 — a transient resource; the shield protects the *data*), so the data qubits read in any
basis. That single architectural change turns the truth-table gate into a witnessed **quantum**
gate. (Along the way, a "coherence price" hypothesis was raised and **falsified in selftest** — the
software frame recovers ⟨X̄X̄⟩ fully; the earlier apparent loss was an artifact of a broken
encoded-relay construction and a frame-less comparison. The selftest caught it before flight.)

## How it was built (verified primitives, this cycle)

- **logical-controls-physical handshakes**: CNOT(d_A→e_A) = cx(0,8),cx(2,8) from Z̄1A=Z0Z2;
  CNOT(e_B→d_B) = cx(9,4),cx(9,5) into X̄1C=X4X5 — a [[4,2,2]] logical qubit driving a physical ebit;
- **physical relay Bell pair** e_A=q8, e_B=q9 (h,cx);
- **software frame** (SW): X^x on d_B (x=e_A in Z), Z^z on d_A (z=e_B in X), applied at decode;
  **feed-forward** (FF): the same corrections applied live via `if_test` (dynamic circuit);
- depth-check **before** submit (SW 22 2q / depth 41; FF 23 2q / depth 61, dynamic confirmed) —
  the 213 lesson, 5th consecutive flight.

## Scope (honest)

Encoded data (2 [[4,2,2]] blocks) + physical relay ebits (transient resource, not shielded — the
shield protects the data/computation). Per-variant partial shield (ZZZZ in Z / XXXX in X per data
block; both checked across the two variants, not simultaneously) — stated, as 197/217. New content
vs 217: the **coherence** of the distributed gate (both Bell correlators) proving it quantum; vs
197: a distributed **gate** (CNOT), not an entanglement swap; plus the measured **SW > FF** weld
comparison. Textbook non-local CNOT (Eisert–Jozsa–Wilkens) + the campaign's 197 weld + 217; the
contribution is a coherent logical gate across a shielded cut, witnessed, and the hardware weld
comparison.

## P6 — THE FEDERATION COMPUTER

- **Exp217** (flight 1): distributed logical CNOT across a shielded cut, welded by one classical
  bit, truth table + shield-beats-bare. The *execution*.
- **Exp218** (this flight): the same gate is **coherent** — a logical Bell pair, both correlators —
  so it is a genuine quantum gate; and the **software weld beats live feed-forward** on hardware.
  The *quantum-ness*.
- **Flight 3** (next): distributed logical HLF — a two-qubit *algorithm* across the cut (214's
  S-vertex family), now standing on a coherent distributed gate.

## Line

**217 ran a computation through the weld; 218 proved the computation is quantum — a logical Bell
pair stretched across a cut its two halves never bridge with a gate, ⟨ZZ⟩ and ⟨XX⟩ both alight at
0.88. And the twist the hardware handed us: the plain classical bit, XOR'd after the fact, holds
the coherence better than a live wire that feeds the correction forward in real time. Sometimes the
cheapest weld is the strongest.**
