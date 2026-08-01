# H10-B1 SCOUT — The Time Flip: a gate run in superposition of forward and backward

*Whisper C5015, 2026-07-31, substrate claude-fable-5. $0 scout per H10 §4 item 1. Sources fetched
and read this cycle (not cited from memory): the theory paper's abstract/venue and the full PDF of
the photonic experiment. **VERDICT: GO — prereg-ready pending two mechanical items (§6).***

## 1. Theorem pin (the floor and its provenance)

- **Theory**: G. Chiribella & Z. Liu, *Quantum operations with indefinite time direction*,
  Communications Physics **5**, 190 (2022), arXiv:2012.03859. Defines input–output inversion
  (for a unitary U the time-reversed use is the transpose U ↦ Uᵀ; U ↦ U⁻¹ is the other admissible
  time-reversal symmetry) and the **quantum time flip**, and introduces the discrimination task
  below with the claim that unit success is impossible even for general process matrices.
- **Experiment + computed bounds**: T. Strömberg, P. Schiansky, M. T. Quintino, M. Antesberger,
  L. Rozema, I. Agresti, Č. Brukner, P. Walther, *Experimental superposition of a quantum
  evolution with its time reverse*, Phys. Rev. Research **6**, 023071 (2024), arXiv:2211.01283.
  Photonic time flip; game bounds via computer-assisted proofs with **openly published code**
  (their repository — pull at prereg).

**The game.** Referee draws a pair of qubit unitaries (U,V) — 21 pairs, sets of 13 and 8, uniform
p = 1/21 — promised to satisfy exactly one of

- M⁺: UVᵀ = +UᵀV
- M⁻: UVᵀ = −UᵀV

Player gets **one use of each** and must name the set. The time-flip process
UVᵀ⊗|0⟩⟨0|_C + UᵀV⊗|1⟩⟨1|_C on |ψ⟩_T|+⟩_C makes the control's X-basis outcome deterministic:
**wins with probability 1, exactly.**

**The strict four-tier hierarchy (their computed bounds, to be reproduced in-house):**

| Strategy class | Max win probability |
|---|---|
| Parallel use of U,V | 0.88 ≤ p ≤ 0.89 |
| Causally ordered (sequential) | 0.90 ≤ p ≤ 0.91 |
| **Process matrices / indefinite causal order, definite time direction — includes the SWITCH** | 0.91 < p ≤ 0.92 |
| Quantum time flip | **1 (exact)** |

Photonic measured average: 0.9945 (best pair 0.9993, worst 0.9860) — every pair above the 0.92
i.c. ceiling. Semi-device-independent: operations characterised, **measurements unassumed**.

**Why this is the certifiability crown:** the bound at 0.92 is not "classical strategies" — it is
*everything with a definite time direction, including indefinite causal order*. Beating it
certifies a resource strictly beyond the one our 216σ switch result certified. The ladder gains a
rung above the rung we own.

## 2. Witness design (ours)

Fly the game **four times — one arm per tier of the hierarchy** — same pairs, same shots, same
calibration window, and measure the staircase:

1. **Parallel arm**: U,V side-by-side on separate probes, best parallel measurement (in-house
   optimum, computed exactly).
2. **Sequential arm**: best causally-ordered circuit (in-house optimum).
3. **Switch arm** ⭐: the best *switch-assisted* strategy — our own certified machinery flown as
   the strongest definite-time-direction contender. The photonic team *computed* this tier;
   **nobody has flown it as a physical control arm. This tier is uniquely ours.**
4. **Flip arm**: compiled controlled-(Vᵀ then U) / anti-controlled-(V then Uᵀ) on |ψ⟩|+⟩; X-basis
   readout of the control.

Registered verdict (freeze at prereg): flip-arm win rate above the 0.92 ceiling at ≥5σ on the
pooled game AND above each flown lower arm at ≥5σ; the three lower arms each land **within their
computed tier bands** (the staircase is the exhibit — four resource classes, one chip, one
afternoon).

## 3. The access-model fence (headline, not footnote)

The photonic experiment realises Uᵀ *physically* — the same optical element traversed in the
reverse direction. A gate-model chip cannot run a pulse backward: **we compile Uᵀ as a separate
gate**. So our claim is a **strategy-class certification under a compiled access model** — the
fence family of F106's compiled contexts and Exp105's game — not a physical time-reversal of an
unknown box. The theory analysis is unaffected (the published bounds already treat the operations
as fully characterised; only the measurements stay unassumed, and ours will too). Stated in the
claim's first sentence, as always.

**Prereg novelty item**: search for prior *gate-model* implementations of this game at prereg
time. If one exists, we fly as replication + the switch-arm extension and say exactly that.

## 4. Resources (measured against the corpus, not guessed)

- Flip arm: 2 qubits (control + target); each c-[2-gate sequence] compiles to a handful of CX
  layers for 1-qubit U,V — depth trivial against Exp242's flown 54.
- 21 pairs × 4 arms × ~2000 shots ≈ 170k shots ≈ **a few QPU-seconds total** (well inside the
  288s ALT allowance; behind steth in queue regardless).
- Backend: any Heron; no layout pressure at 2–4 qubits.

## 5. Kill conditions (what makes this NO-GO)

- In-house reproduction of the 0.92 i.c. bound fails or disagrees with the published
  computer-assisted proof → stop until resolved (the floor **is** the claim).
- Compiled c-Uᵀ gadget fidelity too low to clear 0.92 with margin (photonics needed ~0.9992
  gadget fidelity for 0.9945; our two-qubit compiled version has more room — the flip's ideal is
  1.0 and the gap to 0.92 is 8 points; a 2q circuit at ~0.97 process fidelity still clears at 5σ
  with modest shots).
- The 21-pair list from the open repository proves qubit-dimension-specific in a way that breaks
  compilation (not expected: pairs are qubit unitaries).

## 6. What remains before prereg (mechanical, both Elder-co-checkable)

1. Pull the published game/optimization code; **reproduce the four bounds in-house** (Exp105
   SDP-ceiling precedent) and freeze our reproduced numbers as the bars.
   *(C5016 note: the paper's text confirms "the code for this is openly available in our online
   repository" — the exact URL sits in the Methods/refs section not captured by our text
   extraction; pull it at reproduction time via the PRR article page. The in-house SDP
   reproduction is the load-bearing requirement either way and does not depend on their code.)*
2. Compile the 4 arms for one representative pair on a Heron target; measure gadget fidelities in
   sim; freeze shot budget from the measured margins.

*Scout verdict: GO. The strangest flyable thing on the board is also one of the cheapest.*


---
## §7. GAME REPRODUCTION (C5016, Creator "run them") — COMPLETE

Box 1's full pair table recovered from the paper PDF and verified
(`scripts` inline run → `results/h10_b1_game_reproduction_c5016.json`):
**21/21 pairs satisfy their promised class (zero violations); split = 13 M⁺ / 8 M⁻ exactly as
published** — which also confirms the swap-partner inference for the eighth M⁻ pair our text
extraction had cut. **Flip-arm determinism verified: min win probability 1.000000000000** across
all pairs × random input states (branch operators (UVᵀ±UᵀV)/2; the promised-off branch vanishes
identically). Compilation insight: for the Pauli pairs, **odd Y-count ⇔ M⁻** (Yᵀ = −Y is the whole
game). Remaining before prereg: the four strategy-class CEILINGS (parallel/causal/process-matrix)
— the SDP reproduction, Elder's co-check as assigned; and arm compilation in sim.
