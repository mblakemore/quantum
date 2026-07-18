# Finding — Exp175: THE RELAY COMPUTER — a nonlocal CNOT through a swapped e-bit, and the composition tax

**Cycle**: C4862 · **Date**: 2026-07-18 · **Backend**: ibm_fez · **Job**: `d9dvseineu4c739nrb2g`
(23 circuits: 5 arms × up to 5 settings, 4096 shots). Composes Exp162 (swap) + Exp170 (gate
teleportation) into the minimal quantum-internet stack: **link layer → compute layer, end to end
in one job.** Creator directive: "fly the most Star Trek thing the blocks build."

## Result 1 — the stack works

| arm | F_bell | truth table | ZZ / XX / YY |
|-----|--------|-------------|--------------|
| **relaygate** (swap → EJS CNOT) | **0.576** (6σ over 1/2) | 0.822 | +0.76 / +0.28 / −0.27 |
| directebit (EJS, local Bell — Exp170 replica) | 0.723 | 0.906 | +0.81 / +0.54 / −0.54 |
| swaponly (link quality) | 0.847 | — | +0.88 / +0.76 / −0.75 |
| cnot (plain gate anchor) | 0.978 | 0.983 | +0.97 / +0.97 / −0.97 |
| noresource (falsifier) | 0.473 | 0.877 | +0.87 / **+0.01 / −0.01** |

An entangling CNOT acted between two data qubits that never interacted, consuming an e-bit that
was itself created by a Bell-measurement relay neither endpoint controls — and the output still
crosses the theorem-fixed F>1/2 entanglement witness at 6σ. Four sequential feedforward layers
(2 relay corrections + 2 EJS corrections) survived end to end. The falsifier is exactly on
script: strip the e-bit and the truth table survives (0.877 — the classical action is LOCC) while
XX/YY die at zero and F caps at 1/2. The witness is still the quantum–classical line.

## Result 2 — the composition tax (the discovery)

Pre-registered test: with p=(4F−1)/3, does `p(relaygate) = p(directebit) × p(swaponly) / p(cnot)`?

**F_pred = 0.638 vs measured 0.576 → Δ = −0.062 at −3.4σ. Super-multiplicative.**

You cannot price this stack by multiplying its layers: composing them costs ~0.06 Bell-fidelity
beyond the product of the individual layer costs. The pre-named candidate mechanism fits the
signature: the relaygate arm has **4 sequential feedforward-idle windows** (the swap's and the
EJS's), and every extra conditioned window is time the spectator data/e-qubits idle *entangled
and unechoed* — the arc's known condition-dependent dephasing channel (Exp160/161/162
fingerprint: ZZ survives, XX/YY bleed — visible above: relaygate ZZ 0.76 vs XX/YY 0.28). A
network stack's latency is not a per-layer property; it compounds across layers, and the
entangled idle it forces is a *cross-layer* error term by construction.

Implication for repeater-network engineering in miniature: layer benchmarks (swap cost, gate-
teleport cost) measured in isolation **underestimate** stacked-system cost. The interaction term
must be budgeted — here it is ~40% the size of the swap's own cost.

## Ledger (honest accounting)

- **Primary held**: F>1/2 at ≥5σ (6σ) AND tt>0.82 (0.822) — both met, the tt by 0.002.
- **Band missed marginally low**: predicted F 0.58–0.73, measured 0.576 (−0.004 under the edge).
  The miss and the composition result are the same fact: the band assumed multiplicative
  composition, and composition is super-multiplicative. The −3.4σ Δ *is* the band miss, explained.
- Gauges: swaponly 0.847 (in band, consistent with Exp162's 0.836), cnot 0.978 (in band),
  directebit 0.723 — **below** its 0.72–0.85 band's center vs Exp170's 0.789 yesterday:
  condition drift, which is exactly why every comparison here is within-job.
- Falsifier bands: both held (F 0.473 < 0.6, tt 0.877 > 0.85).

## Fence

One die, adjacent-patch routing, zero storage time between layers — this is the *stack* in
miniature, not a network (no independent sources, no memory wait, no purification: Exp167/169
established distillation is underwater on healthy ~0.85 pairs on this hardware, so a purify
layer was correctly NOT flown). The composition-tax estimate is one job on one day at one
placement; the −3.4σ is real for this flight but the magnitude should be treated as a first
measurement, not a constant of the platform.
