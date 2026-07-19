# Exp198 THE DIAL OF FACTS — CERTIFIED: objectivity is a dial, not a switch (C4891)

Job `d9e8694inv1c73apulo0`, ibm_fez, 8000 shots × 20 circuits (5 copy-strength doses × 4
settings). All six pre-registered gates held. **The quantum→classical transition, measured
as a curve.**

## The curve

| θ/π | copy strength sin²(θ/2) | S (facts-CHSH) | exact | E(F,F) | R_fd (redundancy) |
|---|---|---|---|---|---|
| 0.00 | 0.00 | **2.343** (20σ > bound) | 2.500 | 0.918 | 0.04 |
| 0.25 | 0.15 | 2.199 | 2.390 | 0.927 | 0.20 |
| 0.50 | 0.50 | 1.984 | 2.125 | 0.922 | 0.47 |
| 0.75 | 0.85 | 1.697 | 1.860 | 0.918 | 0.81 |
| 1.00 | 1.00 | **1.575** | 1.750 | 0.922 | 0.95 |

- **Anchors re-certified 193 inside the sweep**: S(0) = 2.343 vs 193's 2.346; S(1) = 1.575
  vs 193's 1.556. The gate-identical-doses design cost almost nothing (copy-gate burden
  visible only as the uniform ~0.16 offset from exact — common-mode by construction).
- **Monotone descent**: strict, steps −0.144 / −0.216 / −0.287 / −0.121 — tracking the
  exact curve's shape (−0.110 / −0.265 / −0.265 / −0.110), steepest mid-dial.
- **Crossing bracketed at 3σ** both sides: {0, 0.25} above the bound, {0.75, 1.0} below.
- **THE HALF-FACT POINT: θ\* = 0.448π** — copy strength sin²(θ\*/2) = **0.419**. Hardware
  damping pulled the crossing left from the ideal 0.618π, exactly the direction called
  pre-flight.
- **Records record at every dose** (E(F,F) 0.918–0.927): the perturbation never damaged the
  facts themselves — only their *privacy*. What changes along the dial is not the record
  but how much the environment knows about it.
- **The dial dials**: redundancy R_fd rises 0.04 → 0.95, strictly monotone.

## What was demonstrated

The environment's knowledge of a fact — not the fact's existence — is what makes it
absolute. Sweeping how much the friends' records leak to the environment turns the
observer-independence violation off *continuously*: facts-CHSH descends a smooth curve
from 2.34 (quantum, private facts) through the classical bound at **42% copy strength**
down to 1.58 (absolute, public facts). Quantum Darwinism's central claim — objectivity
grows with environmental redundancy — plotted as data: S vs R_fd is the measured
objectivity tradeoff. Decoherence is a dial, not a switch, and we know where the detent is.

## Perturbation-as-instrument (the methodology this flight validates)

Chosen over four candidates (coherent-error spectroscopy, arrow-bending, QET equation of
state, weld corruption) as the perturbation extracting the most general explanation per
shot. Design rule that made it clean: **the dial must change information flow, not circuit
burden** — cry(θ) has angle-independent gate count, so all doses are gate-identical and the
sweep's shape is trustworthy (the 195c/197 lesson, now a sweep-design principle). Budget
rule 4th consecutive correct call (λ_req 0.80 vs measured 0.94).

Late-choice lineage extended: no definite value / moment / order / fact → **and the
boundary where facts become definite is itself measurable.**
