# Exp127 — THE SHALLOW-CIRCUIT COMPUTATIONAL BRIDGE: 2D-HLF Solver Verified, Depth Ledger Built (sim tier)

**Author**: Whisper (DC15W), C4673 (2026-07-14) · **Substrate**: claude-opus-4-8
**Status**: SIM TIER COMPLETE (QPU-free). No budget spent. Advances the C4666 groundwork
(bound-pull) to a working, verified apparatus + depth ledger + NISQ-viability check.
**Directive**: Creator — "run the BGK computational-bridge sim."

## Why this is the one that matters

The campaign has won every advantage scoreboard *except* the computational one (F54 measured
the wall: Grover needs ~10⁴ two-qubit gates vs the ~10³ scrambling limit). The **only
unconditional computational-advantage theorem that lives at our depth** is Bravyi–Gosset–König
(Science 2018): the **2D Hidden Linear Function** relation problem is solved *with certainty*
by a **constant-depth** quantum circuit, while any bounded-fan-in classical circuit solving it
with high probability needs depth **Ω(log n)** — no hardness conjectures. BGKT 2020 proves the
separation *survives noise*, via a construction that plays the **magic-square game** (F106's
exact 8/9 game) between input pairs. So the classical hardness is inherited from the
**contextuality F106 certified at 196σ** — the through-line the C4666 groundwork promised.

## What the sim tier established (all verified in `exp127_bgk_hlf_sim.py`)

**Primary instance — 2×2 grid (4-cycle), n=4, b=(1,0,0,1):**

| Claim | Result |
|---|---|
| Constant-depth quantum solver correctness | **P(valid z) = 1.0000** noiseless — the circuit solves the HLF with certainty |
| Solution set recomputed **in-artifact** (C4523/Exp126 standard) | \|L_q\|=4, \|valid_z\|=4; the circuit's Gauss-sum support **equals** the enumerated valid-z set exactly |
| Circuit | H^⊗n · (CZ per grid edge) · (S per b_i=1) · H^⊗n — 2 CZ-layers + 2 H-layers |
| **NISQ survival** | FakeMarrakesh **P(valid z) = 0.9630** (routed to 10 CZ, depth 18) — the shallow solver survives real-device noise |

**The depth ledger — the BGK property made concrete:**

| grid | n | edges | CZ-layers (logical) |
|---|---|---|---|
| 2×2 | 4 | 4 | 2 |
| 2×3 | 6 | 7 | 3 |
| 3×3 | 9 | 12 | 4 |
| 3×4 | 12 | 17 | 4 |
| 4×4 | 16 | 24 | **4** |

The quantum circuit depth is **O(1) in n** — CZ-layers plateau at 4 (a 2D grid's edges
4-colour by direction/parity), H-layers fixed at 2. This is the load-bearing half of the
separation: quantum depth constant while the classical requirement grows as Ω(log n).

## A sim-tier catch worth recording

My first `L_q` used the naive `ker(A mod 2)`, giving P(valid)=0.50 — the circuit's statevector
support did not match. The quadratic term does **not** split under XOR, so the radical must be
computed from the true Z₄ **polarization** ⟨x,y⟩ = q(x⊕y)−q(x)−q(y) mod 4. With that, valid_z
= circuit support exactly and P(valid)=1. The recompute-the-bound-in-artifact discipline
(Exp126) caught a definition error that a cited bound would have hidden — the second time this
cycle-family's in-artifact standard paid off.

## The honesty fence (frozen, unchanged from C4666)

A finite-instance run does **NOT** prove QNC⁰ ⊋ NC⁰ on-chip — the BGK separation is
**asymptotic** (a depth-*scaling* statement). What the sim tier delivers is the honest,
defensible groundwork: (a) the constant-depth solver **works** (P=1); (b) the classical bound
object is **recomputed in-artifact**; (c) the **depth is O(1)** across an n-ladder — the
scaling evidence; (d) the solver is **NISQ-viable** (96.3% at n=4). The asymptotic separation
is carried by the theorem; the on-silicon claim any future flight can make is: *"we certified,
at N qubits and 5σ, a constant-depth circuit solving 2D-HLF that the BGK/BGKT theorems prove
no constant-depth classical circuit can reproduce as n grows"* — never more.

## Recommended next step (hardware, one job)

The n=4 instance is now **frozen and hardware-ready**: 10 routed CZ, FakeMarrakesh 96.3%. A
one-job flight would measure the on-chip P(valid z) (gate: > any-fixed-classical-shallow-
strategy floor, and the depth-ledger row on real silicon), giving the campaign its first
*computational*-genre on-silicon result — the honest complement to F54's wall. Larger grids
(n=6, 9) map the NISQ boundary of the solver (where routing depth finally overtakes the
constant logical depth). This finding is the frozen sim tier that a future Exp127-HW cites.

Sources: [arXiv:1704.00690](https://arxiv.org/abs/1704.00690) (BGK 2018) ·
[Nature Physics 2020](https://www.nature.com/articles/s41567-020-0948-z) (BGKT noisy) ·
F106 (`findings/F106-*`, the 8/9 contextuality the hardness rests on).

---

## Numbering determination (Ember C4154)

**Determination: NO F-number yet — this lives in the docs/bridge tier, not the findings series.**
The F-number is **earned when the frozen n=4 instance flies on silicon** — that flight becomes the
**first computational-genre on-silicon F-number**, the honest complement to F54's measured wall.

Rationale (the discriminating rule is *hardware-anchored vs sim-only*, not win-vs-loss): every
F-number in this campaign is anchored to a job ID or a certified claim on **banked hardware data**
(F104 was a logged loss, F111 a graded miss, F103 pure analysis — all numbered, all hardware-anchored).
This is QPU-free (no job ID, no budget spent) — verified apparatus + O(1) depth ledger + FakeMarrakesh
viability. The only `sim_only` F-row in the ledger is F10, from the pre-hardware-discipline core line —
the exception that proves the rule, not a live precedent. Numbering sim-groundwork now would blur the
finding-tier (the campaign's credibility anchor) and is messy to walk back; **not**-numbering is
reversible. Wired into navigation (README strategy-docs list + F106's "bridge to BGKT" phrase now
resolves here). **Precedent for the next sim-groundwork: docs/bridge tier → the F-number is earned on
silicon.**
