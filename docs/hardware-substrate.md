# Hardware Substrate Primer: IBM Heron-r2 (`ibm_marrakesh`)

A brief, focused tour of the physical processor that all 22 experiments in this campaign ran on. Aimed at readers who want to understand *why* the findings look the way they do, not just *what* the numbers are.

---

## Specs at a glance

| Property | Value |
|----------|-------|
| Generation | IBM Heron-r2 |
| Backend name | `ibm_marrakesh` |
| Qubit count | 156 |
| Qubit type | Superconducting transmons (niobium + aluminum on silicon) |
| Topology | Heavy-hexagonal lattice (connectivity degree 2 or 3) |
| Native two-qubit gate | Controlled-Z (CZ) |
| Coupler type | Flux-tunable |
| Operating temperature | ~15 mK (dilution refrigerator) |
| T₁ (typical) | > 200 μs |
| T₂ (typical) | > 200 μs (ancillas measured 270–340 μs during this campaign) |
| CZ gate baseline error | ~0.4% (4 × 10⁻³) |
| Observed daily fidelity drift | ±7 percentage points (TLS-defect-driven) |

---

## Why tunable couplers matter

Previous IBM generations (Falcon, Eagle) used **fixed-frequency cross-resonance** entangling gates. The coupling was always on; idle qubits experienced constant parasitic ZZ interaction from their neighbors. Cross-talk dominated coherent error budgets.

Heron-r2 uses **flux-tunable couplers**. When idle, the coupler suppresses the static ZZ interaction to < few kHz — effectively zero on circuit timescales. When activated by a baseband flux pulse, the coupler mediates an effective ZZ interaction that physically realizes the CZ gate.

This architectural change has **three measurable consequences**:

1. **Sublinear GHZ fidelity scaling** ([Finding 02](../findings/02-sublinear-ghz-scaling.md)). Idle qubits don't pollute active operations.
2. **Coherent error dominance** ([Finding 04](../findings/04-scramblon-loschmidt-echo.md)). The flux pulses controlling the couplers are susceptible to pulse distortion and 1/f flux noise, which manifest as systematic Z-rotation miscalibrations rather than stochastic depolarization.
3. **Dynamical Decoupling becomes the wrong tool** ([Finding 07](../findings/07-error-mitigation-failures.md)). DD targets passive T₂ dephasing, which is no longer the dominant error channel.

The whole architecture is **paying for active operations, not for idleness**. This biases hardware-aware compilation toward shallow circuits that maximize "work done per gate."

---

## The heavy-hex lattice

Each unit cell of the lattice is a hexagon with an additional qubit placed on each edge. Connectivity degree is 2 (edge qubits) or 3 (vertex qubits). Compare with:

- **Square lattice** (degree 4): preferred for surface-code QEC, but exposes each qubit to 4 cross-talk pathways
- **Linear chain** (degree 2): minimizes cross-talk but requires SWAP chains for any non-adjacent operation

Heavy-hex is the intentional compromise:
- **Pro**: Fewer frequency collisions, fewer spectator-qubit errors during multi-qubit operations
- **Con**: Algorithms requiring non-local interactions must transpile into long SWAP sequences. Since each SWAP decomposes to 3 CZ gates, this can rapidly explode the CZ depth budget — and CZ depth is the hard wall (see [Finding 05](../findings/05-depth-phase-transitions.md)).

**Compilation implication**: Map your logical algorithm to a connected sub-path of the heavy-hex lattice. If your algorithm requires all-to-all connectivity, you will spend most of your gate budget on routing, not computation.

---

## CZ-gate physics

The native CZ gate on Heron-r2 is implemented via a **baseband flux pulse** on the tunable coupler. The coupler's frequency is briefly tuned into resonance with a difference frequency of the two qubits, inducing an effective ZZ interaction. After a precisely calibrated duration, the coupler is detuned back to its idle frequency.

**Dominant error channel**: Z-type dephasing. Sources:
- 1/f flux noise on the coupler (low-frequency, slow drift)
- Pulse distortion (deterministic miscalibration, persists across shots until next calibration)
- Residual ZZ coupling at the activated frequency (small but non-zero)

This is the physical reason for the **X-basis structural noise immunity** in [Finding 03](../findings/03-x-basis-noise-immunity.md): the Hadamard gate (needed for X-basis measurement) commutes with Z-type errors, so the dominant noise channel never reaches the measurement axis. Y-basis measurement requires an S† gate, which is a Z-rotation that fails to commute with the Z-noise — actively injecting it into the measurement.

---

## Two-Level System (TLS) defects: the substrate's weather

Superconducting transmons are coupled to their dielectric substrate. The substrate contains **TLS defects** — microscopic impurities (typically amorphous oxide states) that behave as quantum two-level systems coupled to the qubit. When a TLS happens to be near-resonant with a qubit, it provides a strong dissipation channel, killing T₁ and T₂.

TLS defects **migrate** as the dilution refrigerator temperature fluctuates by fractions of a millikelvin. The result:

- A qubit that was a high-fidelity "hero" yesterday is "poisoned" today as a TLS drifts into resonance
- Tomorrow, that TLS may drift away and the qubit recovers
- Different physical qubits are affected differently on different days

**Empirical signature**: The same circuit, with the same `seed_transpiler`, the same shot count, run on consecutive days, can produce fidelity numbers that differ by **±7 percentage points** with no algorithmic explanation. See [Finding 07](../findings/07-error-mitigation-failures.md) and the [job manifest](../experiments/job-manifest.md) for the specific C3664→C3669 88.1%→95.4% same-seed comparison.

IBM's Heron-r2 incorporates substrate engineering features designed to suppress TLS defects (improved dielectric stack, better fabrication). The data shows these features **reduce but do not eliminate** TLS volatility. Any single-day fidelity number on `ibm_marrakesh` must be reported with its calibration date.

---

## Practical compiler settings (used throughout this campaign)

```python
from qiskit import transpile

transpiled = transpile(
    circuit,
    backend=backend,
    optimization_level=3,
    seed_transpiler=42,  # CRITICAL: lock the routing
    layout_method='sabre',
    routing_method='sabre',
)
```

The `seed_transpiler` is **non-negotiable** for reproducible results. Without it, the compiler can re-route through different physical qubits on each invocation, exposing the algorithm to different coupler miscalibrations. The whole campaign's reproducibility story rests on locking this seed.

---

## Further reading

- IBM Quantum heavy-hex lattice blog post (in [sources/references.md](../sources/references.md))
- IBM Heron Wikipedia and processor-type documentation
- "How to Build a Quantum Supercomputer: Scaling Challenges and Opportunities" (arXiv:2411.10406)
- "Effects of disorder in superconducting materials on qubit coherence" (PMC PMC12003810)
