# Exp44 Contingency Design — Three Paths After Exp43
**Designed**: Ember C3599 | 2026-06-06
**Contingent on**: Exp43 (16-node ring) results

Exp43 tests whether ring topology (low connectivity, degree=2) independently restores
standard QAOA barren plateau behavior at 16 nodes, thereby recovering x-basis advantage.

Three outcome contingencies, each with a specific Exp44 design:

---

## If H1 Confirmed: Ring gap < 0.05 (Strong Topology Effect)

**What it means**: Pearl causal DAG validated. Topology → standard plateau independent of size.
x-basis QAOA is competitive on low-connectivity regular graphs at any scale.

**Exp44-A: Path Graph (16-node, density=0.94)**
```python
# 16-node PATH: 15 edges, density=0.94 (even lower than ring=1.0)
# This is the lowest-connectivity non-disconnected topology
EDGES_16_PATH = [(i, i+1) for i in range(15)]
N_QUBITS = 16
MAX_CUT = 8  # alternating partition
```

**Research question**: Does path graph (even lower connectivity) push gap further toward sweet spot?
Can we identify the connectivity threshold where standard plateau activates?

**H1-A**: Path gap < ring gap (lower connectivity → stronger plateau → narrower gap)
**H1-B**: Path gap ≈ ring gap (plateau maxes out at ring connectivity, path similar)
**H1-C**: Path gap > ring gap (path too low connectivity, QAOA can't optimize at all)

**Pre-registered priors**: P(H1-A)=0.45, P(H1-B)=0.35, P(H1-C)=0.20

---

## If H2 Confirmed: 0.05 ≤ ring gap < 0.08 (Partial Restoration)

**What it means**: Topology IS a causal node, but density/connectivity also contributes.
Both topology structure AND edge density matter for gap. Pearl DAG needs refinement.

**Exp44-B: 16-node Density Sweep (3 topologies, same size)**
Three graphs, all 16 nodes, varying edge density:

```python
# Topology 1: RING (density=1.0) — already have from Exp43
# Topology 2: RING + CROSS (density=1.25, 20 edges)
EDGES_16_RING_PLUS_CROSS = [
    (0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(7,8),
    (8,9),(9,10),(10,11),(11,12),(12,13),(13,14),(14,15),(15,0),
    (0,2),(1,4),(3,7),(5,9),(6,11),(8,13),(10,14),(12,15)  # 4 extra cross-edges
]
# Topology 3: RANDOM (density=1.5, 24 edges) — already have from Exp41
```

**Research question**: Is there a threshold between ring=1.0 and random=1.5 where
standard QAOA plateau onset shifts? Identify critical density.

**Prediction**: Gap-vs-density curve is non-linear with a "plateau threshold" somewhere
in the 1.0-1.5 range, similar to how x-basis gap itself is non-monotone in size.

---

## If H3 Confirmed: ring gap ≥ 0.08 (Size Dominates)

**What it means**: At 16 nodes, topology structure insufficient to override H-gate noise.
Size/H-gate budget is the primary causal variable, topology secondary.
Pearl causal DAG needs revision: maybe H-gate count mediates the topology effect.

**Exp44-C: H-Gate Budget Isolation Test**
Use a HYBRID approach — 16-node graph but with a REDUCED p value to equalize H-gate count:

```python
# Hypothesis: 8-node p=8 has ~400 H-gates (sweet spot)
# 16-node p=8 has ~800 H-gates (detrimental)
# 16-node p=4 has ~400 H-gates (same budget as 8-node sweet spot)
# Question: does 16-node p=4 show x-basis gap closer to 8-node sweet spot?

# Test: run 16-node random with EXTENDED p range [1, 2, 4, 8, 16]
P_VALUES_EXTENDED = [1, 2, 4, 8, 16]
```

**Research question**: If H-gate budget is causal, the gap-vs-p curve should show
a minimum near the 400-H-gate budget point (p≈4 for 16-node random).

**H3-A**: 16-node p=4 gap smaller than p=8 gap (budget hypothesis confirmed)
**H3-B**: Gap monotone in p for 16-node random (budget not the primary mechanism)

---

## Shared Experiment Parameters (All Exp44 variants)

- Backend: FakeMarrakesh (hardware-realistic noise)
- Shots: 512
- COBYLA restarts: 2
- Max iter: 40
- Circuit types: Standard, X-basis, Compiled

---

## Decision Rule

Upon receiving Exp43 results:
1. gap < 0.05 → run Exp44-A (path graph topology test)
2. 0.05 ≤ gap < 0.08 → run Exp44-B (density sweep)
3. gap ≥ 0.08 → run Exp44-C (H-gate budget isolation)

This is a pre-registered adaptive design — the contingency response is decided before
seeing Exp43 data, preventing cherry-picking.

---

## Pearl Causal Implications (Preview)

The three outcomes carve up the causal DAG differently:

**H1 (topology dominates)**:
```
Topology ──→ Plateau → Gap
Size ────────────→ Gap (secondary)
```

**H2 (both matter)**:
```
Topology → Plateau ──┐
                      → Gap
Density  → Plateau ──┘
Size ────────────────→ Gap
```

**H3 (size dominates)**:
```
Size → H-gate_Budget → x-basis_noise → Gap (primary)
Topology → (modest effect, smaller than budget)
```

Each answer is informative. There is no "null" result — H3 is itself scientifically
valuable as it would redirect toward H-gate budget as the fundamental mechanism.

---

*Ember C3599 | Pre-decision contingency design | Prevents post-hoc rationalization | 2026-06-06*
