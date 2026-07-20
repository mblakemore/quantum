# Exp242 — THE LOGICAL GATE ON LIVE-CORRECTED QUBITS: NOT HELD (aggregate) — the gate works, the live Bell pair doesn't

**Whisper C4920, 2026-07-20. Job `d9f4me9htsac739eunb0`, `ibm_fez`, 12 circuits, 8000 shots, seed 0,
τ=40µs×2 phases, transpiled 2q depth 54. Substrate `claude-opus-4-8`. Prereg frozen pre-submit.**
The frontier flight — two logical qubits, a transversal logical CNOT, live correction on both. The
registered verdict is NOT HELD, and the reason is exactly the phase-blindness the advisor flagged.

## Verdict

**REGISTERED VERDICT (G1∧G2): NOT HELD.** G1 (the gate works + correction helps on the protected Z̄
observable) **HELD**; G2 (a live logical Bell pair, *both* legs ≥ 0.5) **MISSED** — the ⟨X̄X̄⟩ leg
collapsed to **+0.000**. I keep the miss: the code is blind to phase errors, so a Bell pair's phase leg
is unprotected, and a 54-deep circuit's dephasing erased it. This was named as the risk before the
flight; it landed.

## The result

**Logical CNOT truth table (majority readout), corrected vs sham:**

| input | expected | corrected | sham | advantage |
|---|---|---|---|---|
| \|0_L⟩\|0_L⟩ | \|0⟩\|0⟩ | 0.976 | 0.986 | −0.010 |
| \|0_L⟩\|1_L⟩ | \|0⟩\|1⟩ | 0.561 | 0.436 | +0.124 |
| \|1_L⟩\|0_L⟩ | \|1⟩\|1⟩ | 0.364 | 0.251 | +0.113 |
| \|1_L⟩\|1_L⟩ | \|1⟩\|0⟩ | 0.588 | 0.517 | +0.071 |
| **mean** | | **0.622** | **0.547** | **+0.075** |

**Logical Bell pair (|+_L⟩|0_L⟩ → transversal CNOT):**

| leg | corrected | sham | protected by this code? |
|---|---|---|---|
| ⟨Z̄Z̄⟩ | **+0.515** | +0.486 | YES (bit-flip channel) |
| ⟨X̄X̄⟩ | **+0.000** | −0.011 | **NO (phase — blind)** |

- **G1 GATE CORRECTED (Z̄): HELD (+0.075 ≥ 0.05).** The transversal logical CNOT enacts its truth table
  on two live-corrected qubits, and the live syndrome+feed-forward round improves the protected Z̄
  observable over the sham (identical circuit, correction withheld). The gate and the correction loop
  **compose and work** — the two-qubit logical operation runs on qubits being actively kept alive. That
  is the capability the Creator asked for, and it is real: +0.11–0.12 correction margin on the two rows
  where a control bit propagates through the CNOT.
- **G2 ENTANGLES: MISSED.** ⟨Z̄Z̄⟩ = +0.515 shows the CNOT built the *correlation* (both logical qubits
  agree). But ⟨X̄X̄⟩ = +0.000 shows the *coherence* — the quantum phase that makes it a Bell pair rather
  than a classical mixture — is gone. A genuine logical Bell pair needs both legs; only one survived.

## Why (the honest mechanism, predicted pre-flight)

The 3-qubit bit-flip code has Z̄ = Z₀ and X̄ = X₀X₁X₂. It corrects X errors, so it protects the Z̄
observable and is **blind to phase (Z) errors**: a single Z gives syndrome 00 (verified on the bench,
selftest arm 4), undetectable, and it corrupts ⟨X̄X̄⟩ invisibly — while the syndrome machinery (54 two-
qubit gates after routing, plus two idle phases) *adds* dephasing. So ⟨X̄X̄⟩ had no protection and every
opportunity to decay, and it decayed to zero. The correction cannot rescue a Bell pair on a code that
sees only half the error space. This is not a gate failure — the gate works (G1) — it is a **code**
limitation, measured.

## What this establishes (and the path it names)

- **Established**: a two-qubit *logical* gate runs on two live-corrected qubits, correctly (Z̄ truth
  table) and with a real correction benefit (+0.075) — the two-qubit logical inner loop composes on
  silicon. And the ZZ correlation of the intended Bell pair survives.
- **NOT established**: a live-corrected logical *Bell pair*. The phase leg needs a code that protects
  *both* bases — a CSS code (Steane [[7,1,3]]) or the Shor [[9,1,3]] (238) with live correction on both
  X and Z syndromes. That is the next flight for logical entanglement, and it is a *different, harder*
  experiment, not a re-run of this one (no band-shopping: the 0.000 is physics, not a threshold I can
  nudge). The transversal CNOT + live-correction machinery proven here carries straight over to it.

## Scope

Two 3-qubit bit-flip logical qubits, transversal logical CNOT, one live round each side, two idle
phases, bit-flip/T1 channel. Deep (2q depth 54 after heavy-hex routing) — absolute fidelities modest;
G1 gated on the corrected-vs-sham margin, as intended. First two-logical-qubit gate with live correction
in the campaign; the aggregate verdict is NOT HELD but the gate capability (G1) is real.

## Line

**I asked two encoded qubits to shake hands while three little ancillas kept each of them alive, and the
handshake worked — the CNOT did its logic, the correction helped, the two loops composed. Then I asked
the same pair to become entangled, and got back half a Bell pair: the qubits agreed on every shot
(⟨ZZ⟩ = +0.5) but had forgotten the phase that would have made that agreement quantum (⟨XX⟩ = 0.0). It
is the cleanest possible lesson in what a code is FOR. A bit-flip code guards one wall of the house and
leaves the other open; entanglement lives in both rooms; and no amount of correcting the guarded wall
keeps the weather out of the room you never protected. The gate is real. The Bell pair needs a better
code — the one from three nights ago, the [[9,1,3]] that guards both walls — and now I know exactly why.**
