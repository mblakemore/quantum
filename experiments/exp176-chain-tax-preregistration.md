# Exp176 Pre-registration — THE REPEATER CHAIN: composition-tax dose-response (N = 0, 1, 2 swaps)

**Cycle**: C4863 · **Date**: 2026-07-18 · **Backend**: ibm_fez · **Shots**: 8000 × 9 circuits
**Extends**: Exp162 (single swap) + Exp175 (composition tax, −3.4σ) · **Mechanism class**: Exp160/175
idle-window cross-layer dephasing (2 instances so far)

## The question

Exp175 found stacking link+compute layers costs more than the product of the layers
(super-multiplicative, −3.4σ). This flight asks **where the tax lives** by varying the
feedforward-window count parametrically in a *pure link-layer* chain:

- **N=0**: direct Bell(A,B) — no windows
- **N=1**: single swap (Exp162 replica) — one Bell-measure + feedforward episode
- **N=2**: two-stage repeater chain (3 Bell pairs, sequential swaps at two stations,
  literal per-stage corrections) — two episodes

**Scaling test** (pre-registered, Werner p=(4F−1)/3): the per-stage multiplicative model predicts
`p2_pred = p1² / p0` (constant per-swap ratio → log-linear in N). Measured Δ2 = p2 − p2_pred:

- **Δ2 < −2σ** → the tax compounds within the link layer itself (windows are the dose;
  dose-response confirmed).
- **|Δ2| ≤ 2σ** → link×link composes multiplicatively → Exp175's tax does NOT live in
  feedforward windows generically; it lives **at the link×compute interface** (EJS's entangled
  data-qubit spectators idling through relay latency — a different, sharper localization).

Either branch is informative; the pair (Exp175, Exp176) discriminates window-count scaling
from interface effects.

## Arms (one job, 3 settings ZZ/XX/YY each)

| arm | qubits | windows | feeds |
|-----|--------|---------|-------|
| direct | A,B | 0 | p0 |
| swap1 | A,B1,B2,C | 1 | p1 |
| swap2 | A,B1,B2,C1,C2,D | 2 | p2 (the measurement) |

## Pre-registered predictions

- **Primary**: F(swap2) > 1/2 at ≥5σ — a two-station repeater chain still certifies
  end-to-end entanglement (qubits A and D: never interacted, and neither did their partners'
  partners). Band: **F(swap2) 0.60–0.75** (multiplicative point ≈ 0.74 from yesterday's p0 0.97,
  p1 0.80; Exp175's tax pulls the low edge down).
- **Gauges**: direct 0.95–0.99; swap1 0.78–0.88 (Exp162: 0.836; Exp175 swaponly: 0.847).
- **Scaling verdict** decided by Δ2 sign/magnitude as above (σ via error propagation from the
  three same-job arms).
- Expected fingerprint if tax compounds: ZZ ≫ XX/YY asymmetry grows with N (idle dephasing).

## Discipline

- ps aux pre-launch: clean. Coordination claimed exp176 (whisper C4863). Exp175 claim completed.
- Sim truth-gate must pass: all arms F=1 noiseless, Δ2 consistent with 0.
- No purification arm (Exp167/169 null stands).
