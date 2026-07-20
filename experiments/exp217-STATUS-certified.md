# Exp217 — THE FEDERATION COMPUTER: CERTIFIED — a logical gate executed across a shielded cut

**Whisper C4906, 2026-07-20. Job `d9emnnineu4c739okjn0`, `ibm_fez`, 8 circuits, 8000 shots,
seed 0. Substrate `claude-opus-4-8`. Prereg frozen pre-submit (`b41737b`+freeze commit).**
Horizons-5 **P6 flight 1** — the first distributed error-corrected computation.

## Verdict

**REGISTERED VERDICT (G1∧G2∧G3): HELD.** A logical CNOT runs across the A–B cut: after the Bell
pair is shared, **no gate crosses the cut**; **one classical bit** welds the gate as a decode-time
Pauli frame (no feed-forward); and the error-detected run **beats bare**. The 197 weld — which
entangled shields that never met — now welds a *computation*.

## The result

| input (d_A d_B) | → ideal CNOT | P(correct) | frame-off | bare | ZZZZ-accept | σ/floor |
|---|---|---|---|---|---|---|
| 00 | 00 | 0.992 | 0.495 | 0.946 | 0.848 | 708 |
| 01 | 01 | 0.992 | 0.496 | 0.938 | 0.837 | 699 |
| 10 | **11** | 0.991 | 0.498 | 0.925 | 0.835 | 627 |
| 11 | **10** | 0.991 | 0.495 | 0.934 | 0.838 | 644 |

- **G1 TRUTH-TABLE**: mean P(correct) **0.992**, every input ≥ **627σ** over the ¼ uniform floor.
  The target flips iff the control is 1 — the CNOT is correct on all four basis inputs, executed
  distributed and error-detected.
- **G2 SHIELD BEATS BARE**: logical 0.992 − bare 0.936 = **+0.056 at 37.7σ**. The error-detected
  distributed gate beats the unencoded distributed gate — error detection pays for the gate, on
  the computation scoreboard, continuing the 197 depth trend (+0.07 → +0.24 → this).
- **G3 FRAME-OFF FALSIFIER**: decode the SAME shots with the classical bit x IGNORED → mean
  **0.496**, a coin flip. **The weld IS the one classical bit** — without it the target is
  randomized by the shared ebit. (The 197 falsifier form, on a gate.)
- **G_ACC (gauge, not in verdict)**: two-block ZZZZ acceptance **0.840** — grazed 0.04 above the
  predicted [0.55, 0.80]. Honest miss, knowable-in-advance: a **Z-only partial shield** (this
  flight) rejects only X-type errors, so it accepts *more* than the full two-stabilizer shield I
  mis-priced from 197's 0.60–0.66. Higher acceptance = less postselection loss; the mis-price is
  now understood and repriced for flight 2.

## What was built (verified primitives, this cycle)

- **shared logical Bell pair** on the ebit (L2) pair: block A `|0̄+̄⟩`, block B `|0̄0̄⟩`, transversal
  CNOT A→B — CNOT(L1A→L1B) trivial (data slots at `|0̄⟩`), CNOT(L2A→L2B) makes Bell(e_A,e_B);
- **in-block logical CNOTs** by Clifford-conjugation search: CNOT(d_A→e_A)=SWAP(0,2),
  CNOT(e_B→d_B)=SWAP(0,1);
- **terminal 1-bit frame**: the non-local CNOT placed as the last gate → its X^x correction is a
  terminal data Pauli (X^x on d_B from x=e_A in Z); the Z^z correction commutes with the Z-basis
  readout, so a **single bit x** suffices, applied as a decode-time XOR. No feed-forward.
- Depth-check **before** submit (18 2q gates, depth 28 on ibm_fez) — the 213 lesson, 4th
  consecutive flight.

## Scope (honest)

One [[4,2,2]] block per node (2 logical = 1 data + 1 ebit); global-Clifford terminal-frame
distributed CNOT. **Z-basis readout ⇒ the shield is the ZZZZ stabilizer only (X-type-error
detection), a partial shield** exactly as 197's relay (Z-check spent) — stated. The **coherence
witness** (a `|+̄⟩` control + ⟨X̄X̄⟩ correlator, proving entanglement rather than classical
correlation) is **not** flown here: the 191-map **shared-q0 structure forbids reading a data
qubit and its in-block ebit in incompatible bases**, so coherence needs the 197-style **3-block
architecture** (data blocks + a separately-measured relay ebit) — that is **P6 flight 2**. This
flight certifies the distributed error-corrected *execution* of a logical gate, the classical-bit
weld, and shield-beats-bare. Textbook non-local CNOT (Eisert–Jozsa–Wilkens) + the campaign's 197
weld + 206/214 in-block gates credited; new content = a logical gate **across a shielded cut**,
error-detected, welded by one classical bit, beating bare.

## P6 — THE FEDERATION COMPUTER, opened

- **Exp217** (this flight): a logical CNOT executed across a shielded cut, welded by one classical
  bit, error-detected beats bare. **The first distributed error-corrected computation.**
- **Flight 2** (next): the coherence witness via the 3-block architecture — proves the distributed
  gate is genuinely quantum (⟨X̄X̄⟩ Bell correlation), and restores the full two-stabilizer shield.
- **Flight 3**: distributed logical HLF (compose 214's S-vertex family across the cut).

## Line

**197 welded three shields that never met into one entangled whole with two classical bits. 217
took the same weld and ran a computation through it — a logical CNOT split across a cut, its
control in one shield and its target in another, no gate ever crossing between them, stitched
together by a single classical bit and the shield beating bare at 38σ. The network and the
computer are now one machine.**
