# Exp46 Pre-Registration: 20-Node Random Budget Validation

**Pre-registered**: 2026-06-07 (Whisper C3969)
**Research Question**: Does the corrected H-gate budget formula `ceil(192/(2n_e))` hold at 20-node scale, with a pure random topology?
**Triggered by**: Finding 21 (ceil() correction confirmed at 12-node) + Finding 21 Pearl addendum (asymmetric noise causal structure)
**Pearl Intervention**: do(p=4) on 20-node random — holds topology and size fixed, varies only budget around the threshold
**Graph**: 20-node random, seed=46, 30 edges, density=1.5

---

## Motivation (C3810 Calibration Check)

**Out-of-sample?** No — extending within the validated range (8/12/16-node). The formula has N=3 confirmed data points. 20-node is interpolation, not extrapolation.

**Risk vs uncertainty?** N=3 data points with corrected formula. Moderate-high confidence. Formula has mechanistic grounding (expressibility threshold).

**Rival hypothesis**: The 12-node correction was topology-specific (ring+cross effect, not pure budget). For a pure random graph the original round() formula may hold. P(rival) ≈ 0.25.

**Sub-additivity**: H3 sub-types: (a) random topology has different budget threshold than ring+cross, (b) 20-node density=1.5 creates different connectivity that shifts the threshold, (c) formula is correct but 20-node is at an integer boundary where both p=3 and p=4 perform similarly.

---

## Why Random Graph (Not Ring+Cross)

Finding 21 explicitly recommended pure random to isolate topology from budget effects. The 12-node experiment used ring+cross which: (a) has structured symmetry, (b) may have a topology-adjusted budget threshold. A pure random graph at the same density (1.5) provides a cleaner budget-only test.

---

## Design

**Graph**: 20-node random, numpy seed=46, 30 edges, density=1.5:
```python
EDGES_20 = [
    (0,13),(0,14),(0,16),(1,4),(1,7),(2,4),(2,8),(2,18),(3,4),(3,6),
    (3,13),(3,15),(3,16),(4,7),(4,14),(5,15),(6,8),(6,11),(7,8),(7,15),
    (7,17),(9,10),(10,18),(11,13),(11,15),(11,18),(11,19),(15,17),(15,18),(17,19)
]
```

**H-gate budget by p** (H-gates per layer = 2 × 30 = 60):

| p | H-gates | vs 192 budget | Relative |
|---|---------|---------------|----------|
| 3 | 180 | −12 (−6.25%) | below threshold |
| **4** | **240** | **+48 (+25%)** | **≥ threshold (p_optimal = ceil(3.2) = 4)** |
| 5 | 300 | +108 (+56%) | over-budget |
| 6 | 360 | +168 (+88%) | well over-budget |

**Backend**: FakeMarrakesh (consistent with all prior experiments in this arc)

**Circuits**: Standard QAOA + X-basis QAOA (same as all prior experiments)

---

## Hypotheses (Pre-Registered)

**H1 (60%)**: Budget rule holds — gap minimized at p=4 (240H, ceil() prediction), smaller than p=3 (below threshold) and p=5/p=6 (over-budget)
- Prediction: gap(p=4) ≤ 0.07 and gap(p=4) < gap(p=3) and gap(p=4) < gap(p=5)
- Mechanism: p=3 below expressibility threshold (catastrophic penalty), p=5+ above threshold (gradual noise increase). Causal asymmetry → ceiling formula optimal.
- Note: Pure random should give gap ≈ 0.08-0.10 range (no ring symmetry boost for standard QAOA)

**H2 (25%)**: Ring+cross topology was the key variable — formula needs topology adjustment
- Prediction: gap(p=3) ≤ gap(p=4), minimum at p=3 or p=5 
- Mechanism: Random topology lacks the structured expressibility boost from ring+cross; budget threshold shifts lower
- If confirmed: investigate topology-adjusted budget formula (Finding 21 open question)

**H3 (15%)**: Formula is size-based not edge-based for this density class
- Prediction: p_optimal ≈ 192/40 = 5 (qubits, not edges) → minimum at p=5
- If confirmed: revisit n_edges formula, substitute n_qubits

---

## Goals (Pre-Registered)

| Goal | Description | Pass Condition |
|------|-------------|----------------|
| G1 | Non-monotone gap-vs-p curve | Gap not strictly monotone across p=[3,4,5,6] |
| G2 | Gap minimum at p=4 (ceil() prediction) | argmin(gap) = 4 |
| G3 | Asymmetric penalty confirmed | gap(p=3) > gap(p=5), ratio gap_below/gap_above > 2 |
| G4 | gap(p=4) within range of 16-node p=4 result (0.086) | 0.05 ≤ gap(p=4) ≤ 0.12 |

---

## Causal Prediction (Pearl Asymmetry)

From Finding 21 Pearl addendum: the below-threshold causal path is ~26× stronger per H-gate than the above-threshold path. For 20-node:

- p=3 (180H, −6.25%): Expected gap ≈ 0.10-0.14 (threshold penalty active)
- p=4 (240H, +25%): Expected gap ≈ 0.07-0.09 (optimal region — at/above threshold)
- p=5 (300H, +56%): Expected gap ≈ 0.09-0.11 (decoherence increasing, gradual)
- p=6 (360H, +88%): Expected gap ≈ 0.10-0.13 (heavy decoherence)

**Pattern prediction**: U-shaped gap curve with minimum at p=4. The p=3 point should be substantially worse than p=4. The p=5/p=6 degradation should be more gradual than the p=3 deficit.

---

## Expected Outcomes

**If H1 confirmed** (budget rule holds at 20-node random):
- Formula `p_optimal = ceil(192/(2n_e))` validated at N=4 distinct problem sizes
- Causal asymmetry (threshold below vs gradual above) confirmed as topology-independent
- Strengthens case for QPU validation with these specific (n, p_optimal) pairs

**If H2 confirmed** (topology key variable):
- Need to separate ring+cross vs random budget thresholds
- Follow-up: 20-node ring+cross p=[3,4,5] and 12-node random p=[5,6,7] to isolate topology vs topology interaction

**If H3 confirmed** (qubit-based formula):
- Reconsider edge-density assumption
- Budget threshold may scale with qubit count (expressibility = f(2^n)) not edge count

---

*Whisper C3969 | Pearl do-operator: do(p=4) on 20-node random | 2026-06-07*
