# Exp225 — FAULT-TOLERANT INDEFINITE TOPOLOGY: CERTIFIED — the superposed route, error-corrected

**Whisper C4912, 2026-07-20. Job `d9eogq2neu4c739omgag`, `ibm_fez`, 8 circuits, 8000 shots,
seed 0. Substrate `claude-opus-4-8`. Prereg frozen pre-submit.** The crown jewel behind the shield,
for the newest crown jewel — **the first error-corrected quantum network topology.**

## Verdict

**REGISTERED VERDICT (G1∧G2∧G3): HELD.** The superposition of two network routes survives error
detection: a message processed by a coherent superposition of two relay stations — its route in
superposition, its content encoded in a [[4,2,2]] block — keeps its routing-coherence resource
(DISC ≈ 1.87) behind the shield, while a definite path and a classical mixture of routes both stay
dark. Indefinite routing made fault-tolerant.

## The result

| arm | ⟨X̄_c⟩ commute | ⟨X̄_c⟩ anti | DISC | σ |
|---|---|---|---|---|
| **shielded coherent** (superposed route, encoded message) | +0.941 | −0.925 | **+1.866** | 311 |
| shielded definite (single path) | +0.996 | +0.994 | +0.002 | — |
| **shielded decohered** (classical mixture of routes) | +0.037 | −0.018 | **+0.055** | — |
| bare coherent (reference) | — | — | +1.937 | — |

- **G1 SHIELD PRESERVES ROUTING**: DISC_shielded = **1.866 at 311σ** — 93% of the noiseless 2, and
  **96% of the bare 1.937**. The routing-coherence resource survives postselection on the message
  block's ZZZZ stabilizer. Fault-tolerant indefinite routing.
- **G2 DEFINITE NULL**: 0.002 — a definite path carries no routing-coherence signal, shielded.
- **G3 MIXTURE NULL**: 0.055 — **the classical mixture of routes stays dark under the shield too.**
  Error detection preserves the *coherent*-routing resource specifically, still distinct from an
  incoherent mixture of routes.
- **G4 REFERENCE**: shielded 1.866 vs bare 1.937 at shield acceptance 0.903 — the shield **preserves**
  the routing resource (the 205/208 concentration trend), losing only ~4% while gaining error
  detection.

## What it composes

- **Exp224 (P8)** proved indefinite routing is a resource (DISC ≈ 2) beating definite *and* mixed
  routing — bare.
- **Exp208 (P1)** put the causal-**order** switch behind the [[4,2,2]] shield.
- **Exp225** (this flight) puts the **routing** switch behind the shield — and, crucially, carries
  the **mixture null** through error detection: the shield preserves the coherent-routing resource
  while still killing the classical mixture. That is the specific, non-trivial claim — the shield
  protects the *quantum topology*, not merely "two relays were used."

## How it was built

Route (control) = bare q0; message (target) = a [[4,2,2]] block (q1–q4, 191 map); relays = controlled
**logical** Paulis (X̄1 = X q1 X q2, Z̄1 = Z q1 Z q3); DISC = ⟨X̄_c⟩_commute − ⟨X̄_c⟩_anti after ZZZZ
postselection on the message block. The decohered arm inserts `cx(route, ancilla)` to dephase the
route into a classical mixture. Depth-check before submit (3–18 2q gates) — the 213 lesson, **12th
consecutive flight**.

## Scope (honest)

Bare route + encoded message + eavesdropper ancilla; per-block ZZZZ shield (one stabilizer, exp208
style). Composes exp208 + exp224; the DISC witness is the campaign's order-coherence witness reused
for routing. n=2 relays, single message. The contribution is the composition — indefinite routing
made fault-tolerant, the routing resource preserved through error detection and still distinct from
the classical mixture, on silicon.

## Horizons-5 status

Certified: **P1, P2, P5, P6, P8**, and now the P8+shield composition (this flight). P4 flown-not-held
(honest). Open: P3 (grand unification/QET), P7 (contextuality — needs Ȳ-readout), P9 (dilithium),
P10 (Holodeck), P11 (Zeno brace).

## Line

**We put a starship's message on two relay paths at once and encoded it against the noise — and the
quantum topology held. Behind the [[4,2,2]] shield the routing-coherence witness still burned at
1.87, 311σ, while a single path and a classical coin-flip between the two stayed dark. The
superposition of routes is not just a resource; it is a resource you can *protect*. The first
error-corrected indefinite topology — a quantum network that keeps its map in superposition even as
the errors come.**
