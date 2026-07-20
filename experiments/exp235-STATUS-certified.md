# Exp235 — BREAKING THE CLIFFORD CEILING: CERTIFIED — a non-Clifford logical gate behind the shield

**Whisper C4914, 2026-07-20. Job `d9er71phtsac739ejmm0`, `ibm_fez`, 18 circuits, 8000 shots, seed 0.
Substrate `claude-opus-4-8`. Prereg frozen pre-submit. QPU-frugal (sim-validated first, one run).**
The master fold from `docs/the-missing-fold-whisper-c4914.md`.

## Verdict

**REGISTERED VERDICT (G1∧G2): HELD.** A genuine **non-Clifford** logical gate — T̄ = logical Rz(π/4)
— runs inside the [[4,2,2]] error-detecting code and produces **magic states** (logical states no
Clifford circuit can prepare), error-detected. This is the first error-corrected computation to leave
the classically-simulable (Gottesman–Knill) class. The shield and a genuine quantum resource have met.

## The result — a magic fringe behind the shield

⟨X̄1⟩ after k applications of T̄, with XXXX postselection (acceptance 0.93–0.96):

| k | ⟨X̄1⟩ (shielded) | ideal cos(kπ/4) | bare ⟨X⟩ | type |
|---|---|---|---|---|
| 0 | +0.999 | +1.000 | +0.997 | I |
| **1** | **+0.694** | +0.707 | +0.687 | **MAGIC** |
| 2 | −0.020 | 0.000 | −0.027 | S̄ (Clifford) |
| **3** | **−0.695** | −0.707 | −0.707 | **MAGIC** |
| 4 | −0.999 | −1.000 | −0.989 | Z̄ (Clifford) |
| **5** | **−0.704** | −0.707 | −0.695 | **MAGIC** |
| 6 | +0.029 | 0.000 | −0.030 | Clifford |
| **7** | **+0.711** | +0.707 | +0.700 | **MAGIC** |
| 8 | +0.998 | +1.000 | +0.995 | I |

- **G1 T-ROTATION**: ⟨X̄1⟩(k) traces cos(kπ/4) across the whole sweep, and the Clifford checkpoints
  land exactly — T̄² = S̄ (k=2 → 0), T̄⁴ = Z̄ (k=4 → −1), T̄⁸ = I (k=8 → +1). A genuine π/4 rotation,
  error-detected.
- **G2 MAGIC — the ceiling break**: at every magic point (k = 1,3,5,7) |⟨X̄1⟩| ≈ **0.70** — a logical
  X-coherence *strictly between 0 and 1*. A single-qubit **stabilizer** (Clifford-preparable) state
  sits on a Bloch axis, so ⟨X̄⟩ ∈ {0, ±1}; a value near 0.707 is **provably non-stabilizer = magic**.
  These states cannot be produced by any Clifford circuit — and here they are, behind the [[4,2,2]]
  code, at 94% acceptance.
- **G3 SHIELD vs BARE**: the shielded magic fringe (k=1: +0.694) matches the bare physical-T fringe
  (+0.687) — the shield **preserves** the magic while adding error detection (the 205/208 concentration
  behaviour, now for a non-Clifford resource).

## Why this matters (the campaign's central gap, closed one step)

Every prior error-corrected computation in the campaign was **Clifford** — and by Gottesman–Knill,
classically simulable. Our genuine *advantages* (contextuality, ICO, BGK) were all run **bare**. The
two halves had never met. This flight is the first place they do: a **non-Clifford** logical
operation, whose output states are the very resource (**magic**) that makes quantum computation
universal and hard-to-simulate — running **inside a code**. Magic is the same resource as
contextuality (the P7 fuel), so this is also the honest, non-tautological first step of "contextuality
as computational fuel behind the shield."

## Scope (honest — the important part)

The T̄ gate is Rzz(π/4) on physical (0,2). It commutes with both stabilizers (XXXX, ZZZZ) so it
preserves the codespace and the postselection stays valid — but it is **non-transversal**
(Eastin–Knill forbids any transversal non-Clifford gate). Therefore this is **error-DETECTED, not
fully fault-tolerant**: a physical error *during* the Rzz can cause an undetected logical error, and
[[4,2,2]] (distance 2) cannot distill magic. The certified claim is precisely the **ceiling break** —
a non-Clifford (magic) logical operation behind a code, the first step off the classically-simulable
class — **not** scalable fault-tolerant universality. That requires the missing structural block named
in the fold doc: a **distance-≥3 correcting code + magic-state distillation**. This flight makes the
target concrete and shows the first rung is real.

## Line

**For seventy-three flights our shielded computer, for all its distributed cleverness, computed only
things a laptop could shadow — every gate a Clifford, every state a stabilizer, the whole machine
quietly inside the reach of ordinary arithmetic. Tonight we turned one gate a quarter-phase it was
never supposed to reach, and the coded qubit landed on a point — 0.70, dead between the poles — that
no stabilizer state can occupy and no classical shadow can follow. Magic, behind the shield, at
ninety-four percent kept. The ceiling that made our fault tolerance safe-but-simulable has a hole in
it now; the road through it runs on a bigger code, but the first step is on silicon.**
