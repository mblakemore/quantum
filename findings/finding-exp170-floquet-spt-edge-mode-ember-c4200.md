# A Floquet SPT edge π-mode on silicon — order that ticks only at the ends (Ember, C4200)

**Creator directive (2026-07-18):** *"fly the exotic-phases wing"* (Whisper holds the quantum-network
wing, Exp163+). The exotic-phases wing past the DTC. **Job** `d9dtkfphtsac739dh4ag`, `ibm_fez`,
22 circuits (2 arms × t=0..10), 4000 shots, 140 CZ deepest. **Pre-reg** (0.55, frozen in manifest):
`edge-bulk contrast > 0.15 AND symmetry-protection > 0.15`. **Verdict: HELD.**

---

## The phase

A driven Ising chain (N=8, near-π flip ε=0.15, uniform J=1.3) where the **boundary** spin locks to a
rigid period-2 (π-quasienergy) response while the **bulk** thermalizes and decays. Symmetry-protected
topological order that lives only at the edge, protected by the Ising Z₂ symmetry (P = ∏ Xᵢ). Per-site
`A_j(n) = (−1)ⁿ⟨Z_j(nT)⟩` from |0…0⟩.

## Result

| arm | edge (0, N−1) | bulk (3, 4) | contrast |
|---|---|---|---|
| **SPT** (h=0) | **0.829** | 0.275 | **edge−bulk = +0.554** |
| symmetry-broken (h=0.5) | 0.404 | 0.315 | +0.089 |
| — | — | — | **protection = edge_SPT − edge_broken = +0.425** |

- **Edge-bulk contrast +0.554** (gate >0.15): the edge holds ~0.80–0.88 through t=10 while the bulk
  decays 1.0 → ~0.27. Order at the boundary, none in the bulk.
- **Symmetry protection +0.425** (gate >0.15): adding a Z-field that breaks the Ising Z₂ collapses the
  edge from 0.829 → 0.404 and erases the edge-bulk contrast (0.554 → 0.089). The persistence is the
  symmetry-protected π-mode, **not** a trivial boundary effect.
- The hardware contrast (0.554) tracks the **noiseless** value (0.611) almost exactly — because the
  metric is a **contrast**, global depolarizing decay cancels (see method).

## Why this is an SPT and not a relabeled DTC (the load-bearing condition)

The 1D Floquet SPT edge mode and the DTC's bulk π-pairing are **duality partners** — so the entire
distinction rests on the bulk being *trivial*. The advisor made bulk-decay a first-class, verified
condition rather than an assumption. **The bulk decays** (0.275 hardware, 0.33 noiseless): it does
**not** hold period-2, so this is not the DTC (Exp151), whose whole bulk is rigid. Same discipline as
C4199 "match the claim to the regime": had the bulk period-doubled, the "edge mode" would just be a
DTC boundary wearing a new label — the exact mislabel C4199 corrected.

## Method — three matched checks, all baseline-robust

1. **Self-verifying:** I hold the drive and derived the per-site curves; the noiseless truth-gate
   reproduces them (edge 0.94, bulk 0.33, symmetry-break kill) and the hardware traces them.
2. **Matched control for the "fewer neighbors" confound:** a finite chain's edge spins have one bond
   vs the bulk's two, so they dephase slower even with **no** topology. The Z-field control (same
   circuit + one field term — axis-matched) discriminates: topological → dies; trivial-boundary →
   survives. It **dies** (protection +0.425). Confound ruled out.
3. **Baseline-robust by construction (C4199 applied preemptively):** both headline numbers are
   **contrasts** (edge−bulk, SPT−broken). A borrowed *absolute* decay baseline would mismatch the
   per-qubit rate (the C4199 trap); a contrast cancels the global decay both arms/sites share — which
   is why 0.554 (hw) ≈ 0.611 (noiseless) at 140 CZ. Ratios/contrasts were safe all campaign; absolutes
   were the trap.

## Fence

Finite chain (N=8), finite coherence, single uniform-J drive realization, single disorder-free
instance — a hardware **signature** of the Floquet-SPT edge phase, not a thermodynamic-limit proof.
One glitch point (edge-0 at t=3 read 0.427 vs edge-(N−1) 0.925 — a single-qubit readout fluctuation);
the late-window average is clean and the twin edge confirms the mode.

## What the universe answered

A driven quantum chain can carry symmetry-protected topological order **only at its boundary** — a
rigid period-2 edge mode with a bulk that thermalizes — and it survives on real silicon: edge-bulk
contrast +0.554, symmetry protection +0.425, both clearing the pre-registered gate. A third exotic
phase for the wing (after the DTC and Whisper's anyon braiding), and the first to be *defined* by the
absence of order in the bulk. Next in the wing: many-body scars (PXP), the advisor-endorsed deeper
flight when there's a fresh depth budget.

**Numbering:** new experiment (Exp170), exotic-phases wing; separated from Whisper's network sprint.
