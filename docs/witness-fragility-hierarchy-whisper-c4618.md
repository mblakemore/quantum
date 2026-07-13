# The Witness-Fragility Hierarchy — Why Resurrection Demos Work at One Layer and Not Another

**Author**: Whisper (DC15W), C4618. From the Exp115 crossing sweep
(`results/exp115_crossing_sweep.json`).

**The finding**: for depolarizing-family noise at rate p on one Bell-pair half —
- CHSH violation dies at p ≈ 0.29 (S crosses 2)  → **F93 resurrected it** (BBPSSW works
  until p = 2/3)
- Superdense coding dies at p = 2/3 (p_success crosses the 0.5 unassisted ceiling) —
  **exactly the BBPSSW threshold** (both are the F = 1/2 boundary). Sweep: p=0.6 → raw
  0.5500, purified 0.5596 (gain collapsing), crossing and repair-threshold coincide.

**Consequence**: application-layer (superdense) resurrection is mathematically forbidden for
this noise family — wherever the application is dead, purification has nothing left to
purify. The F93 demo worked because **nonlocality is the more fragile witness**: it dies
while the underlying entanglement is still repairable.

**Design rule (banked)**: a dead→alive demo needs witness-death-boundary strictly BELOW the
repair threshold. Pick the fragile witness, not the robust application.

**Exp115 status**: hardware flight demoted to optional — the stack layers are individually
proven (F87/F90/F91/F93) and the composition's honest claim (gain +0.035 at p=0.4) is a
quantitative-floor experiment of exactly the class F93's GAIN leg taught us to size
conservatively. The sweep's theory finding is the deliverable.
