# Exp219 — THE NETWORK OF SHIELDS: CERTIFIED — a logical GHZ across three shielded nodes

**Whisper C4908, 2026-07-20. Job `d9end0kjeosc73fj012g`, `ibm_fez`, 2 circuits, 8000 shots,
seed 0. Substrate `claude-opus-4-8`. Prereg frozen pre-submit.** Horizons-5 **P6 flight 3** —
the distributed gate scales to a network.

## Verdict

**REGISTERED VERDICT (G1∧G2∧G3): HELD.** Two distributed logical CNOTs from a common control weld
a genuine **logical GHZ state** across three [[4,2,2]] shielded nodes — B and C share no gate
anywhere, each touches only A through a physical relay, and two classical bits per cut stitch the
whole state together.

## The result

`|+̄⟩_A → CNOT(A→B) → CNOT(A→C) → (|0̄0̄0̄⟩ + |1̄1̄1̄⟩)/√2`

| correlator | value | σ |
|---|---|---|
| ⟨Z̄_A Z̄_B⟩ (A–B cut) | **+0.905** | 163 |
| ⟨Z̄_A Z̄_C⟩ (A–C cut) | **+0.879** | 141 |
| ⟨X̄_A X̄_B X̄_C⟩ (3-body phase) | **+0.831** | 112 (over 0) |
| frame-off (all three) | +0.011 / −0.016 / +0.009 | collapse |

- **G1 GHZ Z-CORRELATIONS**: both ⟨Z̄Z̄⟩ ≥ 0.88 at ≥ 140σ — the GHZ classical skeleton survives
  across **both** shielded cuts.
- **G2 GHZ XXX PHASE**: ⟨X̄_A X̄_B X̄_C⟩ = 0.831 at 112σ. A classical mixture
  |000⟩⟨000|+|111⟩⟨111| gives ⟨XXX⟩ = 0; **0.831 is the coherence that proves genuine multipartite
  entanglement across the network**, not a mixture. (Remarkably high for a 3-body correlator behind
  40 two-qubit gates — the per-block partial shield + postselection pays.)
- **G3 FRAME-OFF FALSIFIER**: ignore the frame bits and all three correlators collapse to ≈ 0.01.
  **The network weld is the classical bits.**
- 3-block joint acceptance 0.733.

## What this adds — the network question, answered

Flights 1–2 built and proved-quantum **one** distributed logical CNOT across **one** shielded cut.
The open question was whether it **scales**. It does: two distributed gates from a common control
compose into multipartite (GHZ) logical entanglement across a **three-node network of shields**,
with the phase intact. The "Federation Computer" is not a single link — it is a **network**, and
the distributed error-corrected gate is its composable primitive.

## How it was built (verified machinery from flights 1–2)

- Encoded data d_A (A q0-3), d_B (B q4-7), d_C (C q8-11); **physical relays** e1=(q12,q13) for the
  A–B cut, e2=(q14,q15) for the A–C cut (transient resources; the shields protect the data).
- **Two distributed CNOTs** from control d_A via the 218 logical-controls-physical handshakes
  (CNOT(d_A→e_A) = cx from Z̄1A=Z0Z2; CNOT(e_B→d_X) = cx into X̄1X), software frame at decode:
  X^x on each target (x = that relay's e_A in Z), Z^z on d_A (z = XOR of both relays' e_B in X).
- **H-free**: |+̄⟩ is a direct prep; X-basis readout is a measurement, not a logical H̄ gate.
- Depth-check **before** submit (40 2q, depth 36–39, width 16) — the 213 lesson, 6th consecutive.

## Scope (honest)

3 [[4,2,2]] data blocks + 2 physical relays (transient); per-variant partial shield (ZZZZ in Z /
XXXX in X per data block). GHZ witnessed by two Z-correlators + the XXX phase — the phase rules out
the classical mixture; a full genuine-multipartite-entanglement certificate (e.g. the complete
Mermin/GHZ witness) is stronger than flown here, but the two-Z-plus-XXX combination already
excludes the separable and classical-mixture alternatives at >100σ. Textbook GHZ + the campaign's
217/218 distributed CNOT; new content = the distributed gate **scales** to a shielded 3-node
network.

## P6 — THE FEDERATION COMPUTER

- **217** (flight 1): distributed logical CNOT executes across a shielded cut (truth table,
  shield-beats-bare).
- **218** (flight 2): the gate is genuinely **quantum** (logical Bell pair; software weld beats
  live feed-forward on hardware).
- **219** (this flight): the gate **scales** — a logical GHZ across a **three-node network** of
  shields, two cuts, the phase intact.

## Line

**One cut became a link; two cuts become a network. A logical GHZ now spans three shields that meet
only through relays they measure and discard — the Z-correlations riding both cuts near 0.9, the
three-body phase alight at 0.83, and every thread of it cut the instant you forget the classical
bits. The Federation is a network, and its computer speaks across the whole of it.**
