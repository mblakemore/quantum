# Autonomous Characterization of the IBM Heron-r2 Quantum Processor

**A 22-experiment empirical diagnostic campaign on `ibm_marrakesh` (156-qubit heavy-hex), May 2026.**

This repository documents an autonomous, multi-agent network's exhaustive characterization of IBM's Heron-r2 processor. Operating directly on the physical Quantum Processing Unit (QPU) — no simulators, no extrapolations — the network extracted raw performance metrics under a strict 600-quantum-second execution budget, executing circuits ranging from foundational CHSH Bell tests to Variational Quantum Eigensolvers (VQE), Quantum Amplitude Estimation (QAE), 3-qubit dynamic circuits, and Hadamard quantum walks.

The findings constitute novel discoveries about the operational behavior of modern superconducting NISQ hardware: structural noise immunity tied to commutation relations, sub-noise-floor coherent error excursions driven by scramblon dynamics, qualitative phase transitions in algorithmic scaling, and the mathematical impossibility of break-even error correction on current substrates.

---

## TL;DR — Headline Findings

| # | Finding | Why It Matters |
|---|---------|----------------|
| 1 | **CHSH violation of ~2.74** at the Tsirelson-bound limit | 96.8% of maximum quantum fidelity — establishes the floor "decoherence tax" of the substrate |
| 2 | **Sublinear GHZ fidelity decay** (N=2→5) | Heavy-hex topology + tunable couplers limit per-qubit error overhead — favors large, shallow entanglement |
| 3 | **Structural X-basis noise immunity** (3× independent confirmation) | Hadamard commutes with the dominant CZ Z-dephasing channel — measurement-basis choice is a first-class compilation concern |
| 4 | **Sub-noise-floor Loschmidt echo excursions** | Coherent error oscillations confirm non-Markovian scramblon dynamics at mid-circuit depth |
| 5 | **Phase transition at ~800–1000 CZ gates** | Past this depth, output is statistically uniform noise — a hard event horizon for algorithmic utility |
| 6 | **Ancilla tax kills NISQ QEC** | 8 extra CZ gates per syndrome injects ~3 orders of magnitude more noise than the code corrects |
| 7 | **Error mitigation is largely futile** | DD, Pauli twirling, TREM all degraded signal; ±7pp daily calibration drift dwarfs any mitigation gain |
| 8 | **VQE H₂ at chemical accuracy** | 0.001 Ha error vs FCI — hardware is genuinely useful when algorithms are hardware-aware |
| 9 | **IAE-MLE QAE precision: 344× over naive** | Maximum-likelihood best-k selector across Grover oscillations recovers amplitude estimation on real HW |

---

## Repository Map

```
.
├── README.md                    ← you are here
├── full-report.md               ← complete synthesis (the Gemini deep-research source doc)
├── findings/                    ← one-per-discovery deep dives
│   ├── 01-chsh-bell-violation.md
│   ├── 02-sublinear-ghz-scaling.md
│   ├── 03-x-basis-noise-immunity.md
│   ├── 04-scramblon-loschmidt-echo.md
│   ├── 05-depth-phase-transitions.md
│   ├── 06-ancilla-tax-qec-impracticability.md
│   ├── 07-error-mitigation-failures.md
│   ├── 08-vqe-h2-chemical-accuracy.md
│   └── 09-qae-iae-mle-precision.md
├── experiments/
│   └── job-manifest.md          ← IBM Quantum job IDs + dates + circuits (for cross-validation)
├── scripts/                     ← Python source: circuits, submission tools, analysis
│   └── README.md
├── docs/
│   └── hardware-substrate.md    ← Heron-r2 physical architecture primer
└── sources/
    └── references.md            ← 60+ peer-reviewed and primary sources
```

---

## Hardware Under Test

- **Processor**: IBM Heron-r2 (`ibm_marrakesh`)
- **Qubit count**: 156 superconducting transmons
- **Topology**: heavy-hexagonal lattice (connectivity degree 2 or 3)
- **Native two-qubit gate**: controlled-Z (CZ) via flux-tunable couplers
- **Environment**: dilution refrigerator @ ~15 mK
- **T₁, T₂**: routinely > 200 μs (ancilla T₂ measured 270–340 μs during this campaign)
- **CZ gate error**: ~0.4% baseline
- **Daily calibration drift observed**: ±7 percentage points (same circuit, same seed, 24h apart)

See [`docs/hardware-substrate.md`](docs/hardware-substrate.md) for the full physical architecture primer.

---

## Methodology

**Autonomous network**: A multi-agent system designed all circuits, transpiled them with explicit `seed_transpiler` pinning (to control for topological routing artifacts), submitted to `ibm_marrakesh` via the Qiskit Runtime SamplerV2, and post-processed results — with no human in the experimental loop.

**Pre-registration discipline**: Every experiment defined falsifiable hypotheses *before* job submission (typically 3–4 binary pre-reg gates per experiment). Pass/fail was machine-evaluated after the job returned. Failed pre-regs are reported as informatively as successes — the campaign treats "the data refuted the hypothesis" as a first-class result.

**Pearl causal framing**: Where mechanism mattered (not just correlation), error pathways were modeled as directed acyclic graphs and tested via interventional comparisons (`do(X)`) rather than observational regressions. The X-basis immunity finding (`findings/03`) and the Dynamical Decoupling overturn (`findings/07`) are the clearest examples.

**Budget**: Total ~600 quantum-seconds across the 22 experiments. Real hardware time, not simulator time. Job IDs are listed in [`experiments/job-manifest.md`](experiments/job-manifest.md) for independent verification.

---

## Cross-Validation

Every finding in this repository is anchored to:

1. **A specific IBM Quantum job ID** (verifiable on IBM Quantum Platform if you have credentials for the same backend)
2. **A specific date** (calibration snapshot for `ibm_marrakesh`)
3. **A Python script** in `scripts/` that reproduces the circuit (with the transpiler seed)
4. **Pre-registration criteria** stated in the linked finding document
5. **Primary sources** in `sources/references.md`

If you can repeat the same circuit on the same backend within the same calibration window, you should land within shot noise of our numbers. If you can't, the most likely cause is calibration drift (see Finding 7) — re-check on a fresh calibration day.

---

## Limitations & Honest Caveats

- **Single substrate**: All 22 experiments ran on `ibm_marrakesh` specifically. Findings claimed as "Heron-r2 architecture" properties are strongest where independently confirmed across multiple jobs/days; "X-basis immunity" has three independent confirmations (Bell, GHZ-3, VQE-H₂), so we promote it from "observation" to "discovery." Single-job observations are flagged as such in the individual finding docs.
- **Calibration drift is the elephant**: A ±7pp daily fidelity drift means absolute numbers shift between runs. We report the numbers we measured on the dates listed; reproductions should land within the drift envelope.
- **NISQ-era characterization**: These findings describe the operational behavior of 2026-era superconducting hardware. They are not claims about the long-term limits of quantum computing — they are claims about *this generation* of substrate.
- **Source synthesis**: The narrative framing in [`full-report.md`](full-report.md) is a Gemini deep-research synthesis of the underlying experimental data. The findings documents in `findings/` are written directly from the experimental record (cycle commits, job IDs, raw measurements) and are the primary source of truth.

---

## License & Attribution

Public for cross-validation, replication, and peer review. If you reproduce or build on this work, citing the IBM Quantum job IDs in `experiments/job-manifest.md` is the most useful form of attribution — it gives downstream readers a verifiable anchor.

The Python scripts in `scripts/` are released for educational and research use. Lyla quantum tooling (`qae_volatility_estimator.py`, `ibm_quantum_submit.py`) is sourced from the upstream Lyla project and reproduced here with attribution headers.

---

*"The hardware remains strictly bounded by fundamental thermodynamic ceilings. To extract maximum computational utility from modern heavy-hex processors, algorithm designers must abandon reliance on software error mitigation and future-proof error correction codes. Instead, the focus must shift entirely to hardware-aware compilation: prioritizing absolutely minimal circuit depth, rigidly locking compiler routing seeds to prevent destructive topological optimization artifacts, and relentlessly mapping algorithmic observables to the hardware's native, noise-resistant X and Z measurement axes."*

— from the synthesis conclusion ([`full-report.md`](full-report.md))
