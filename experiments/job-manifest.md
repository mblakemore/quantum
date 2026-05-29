# IBM Quantum Job Manifest

Verifiable anchors for cross-validation. Every finding in this repository is grounded in at least one IBM Quantum job ID listed below. With credentials for `ibm_marrakesh`, you can retrieve the raw counts directly via the IBM Quantum Platform.

**Backend**: `ibm_marrakesh` (IBM Heron-r2, 156 qubits, heavy-hex)
**Campaign window**: May 22–24, 2026
**Total quantum-second budget**: ~600 s

---

## The 22-Experiment Inventory

The source synthesis ([`../full-report.md`](../full-report.md)) refers to the campaign as a "22-experiment diagnostic arc". The 14 IBM Quantum job IDs in the ledger below cover those 22 logical experiments — several jobs contain multiple distinct circuits, listed individually here.

| # | Experiment | Cycle | Job(s) | Linked finding |
|---|------------|-------|--------|----------------|
| 1 | Bell state ZNE — `⟨ZZ⟩` scaling | C3650 | `d894cbop0eas73do4p9g` | [03](../findings/03-x-basis-noise-immunity.md) |
| 2 | Bell state ZNE — `⟨XX⟩` immunity confirmation | C3650 | (same job, separate observable) | [03](../findings/03-x-basis-noise-immunity.md) |
| 3 | Bell state ZNE — `⟨YY⟩` decel scaling | C3650 | (same job, separate observable) | [03](../findings/03-x-basis-noise-immunity.md) |
| 4 | GHZ-3 ZNE-extended | C3651 | `d894lf5g7okc73eo7erg` | [02](../findings/02-sublinear-ghz-scaling.md), [03](../findings/03-x-basis-noise-immunity.md) |
| 5 | GHZ-4 N-inversion (XXXX, YYYY, ZZZZ) | C3651 | (same job, N=4 sweep) | [03](../findings/03-x-basis-noise-immunity.md), [07](../findings/07-error-mitigation-failures.md) |
| 6 | XX threshold scan (λ=1→7) | C3651 | (same job, λ sweep) | [03](../findings/03-x-basis-noise-immunity.md) |
| 7 | VQE H₂ ground-state energy at equilibrium | C3652 | `d895ai2s46sc73fa64ag` | [08](../findings/08-vqe-h2-chemical-accuracy.md) |
| 8 | VQE H₂ potential-energy curve scan | C3652 | (same job, bond-length sweep) | [08](../findings/08-vqe-h2-chemical-accuracy.md) |
| 9 | VQE per-Pauli-term basis error analysis | C3652 | (same job, X/Y/Z decomposition) | [03](../findings/03-x-basis-noise-immunity.md), [08](../findings/08-vqe-h2-chemical-accuracy.md) |
| 10 | Quantum Volume characterization | C3654 | (C3654 commit) | (foundational; supports [05](../findings/05-depth-phase-transitions.md)) |
| 11 | Hadamard Quantum Walk N=2..4 (variance scaling) | C3655 | `d89ftt1789is73938rpg` | [05](../findings/05-depth-phase-transitions.md) |
| 12 | Hadamard Quantum Walk N=5 (saturation regime) | C3657 | (extension job) | [05](../findings/05-depth-phase-transitions.md) |
| 13 | Hadamard Quantum Walk N=6 (post-transition) | C3657 | (extension job) | [05](../findings/05-depth-phase-transitions.md) |
| 14 | 3-qubit bit-flip QEC | C3662 | `d89l7cis46sc73fapa10` | [06](../findings/06-ancilla-tax-qec-impracticability.md) |
| 15 | 3-qubit phase-flip QEC | C3664 | `d89lft5g7okc73eor90g` | [06](../findings/06-ancilla-tax-qec-impracticability.md) |
| 16 | QEC + Dynamical Decoupling (DD overturn) | C3666 | `d89lp90p0eas73doq4j0` | [06](../findings/06-ancilla-tax-qec-impracticability.md), [07](../findings/07-error-mitigation-failures.md) |
| 17 | Free calibration query (ancilla T₂ probe) | C3667 | `d89m1d0p0eas73doqcpg` | [04](../findings/04-scramblon-loschmidt-echo.md), [07](../findings/07-error-mitigation-failures.md) |
| 18 | Pauli Twirling | C3668 | `d89mb9is46sc73faqje0` | [07](../findings/07-error-mitigation-failures.md) |
| 19 | TREM @ 2048 shots | C3668 | `d89mb9op0eas73doqnt0`, `d89mba2s46sc73faqjf0` | [07](../findings/07-error-mitigation-failures.md) |
| 20 | TREM @ 8192 shots (final NISQ-wall confirmation) | C3669 | `d89mhc2s46sc73faqpng`, `d89mhc9789is7393gn4g` | [07](../findings/07-error-mitigation-failures.md) |
| 21 | Bell state HW baseline (Lyla test harness) | C3670 | `d89n5uqs46sc73farg80` | [01](../findings/01-chsh-bell-violation.md), [09](../findings/09-qae-iae-mle-precision.md) |
| 22 | QAE on real HW — 12 circuits (3 vol regimes × 4 k values, post-IAE-MLE fix) | C3671 | `d89nd7p789is7393hkr0`, `d89ndk0p0eas73dorso0` | [09](../findings/09-qae-iae-mle-precision.md) |

A 23rd experiment — the Loschmidt echo / scramblon depth-8/12/16 sweep documented in [Finding 04](../findings/04-scramblon-loschmidt-echo.md) — was run early in the arc and is anchored to the C3667 calibration query for the T₂ measurements that contextualise it; the raw echo amplitudes summarised in that finding came from circuits that were not assigned an explicit ledger row because they were exploratory rather than pre-registered.

---

## Job Ledger (Compressed by Job ID)

| Cycle | Date | Logical scope | Job ID(s) | Pre-reg outcome |
|-------|------|---------------|-----------|-----------------|
| C3650 | 2026-05-22 | Bell ZNE observable asymmetry (XX, YY, ZZ) | `d894cbop0eas73do4p9g` | 3/4 PASS |
| C3651 | 2026-05-22 | GHZ-3 + GHZ-4 ZNE-extended (XX threshold; N=4 inversion) | `d894lf5g7okc73eo7erg` | 7/8 PASS |
| C3652 | 2026-05-23 | VQE H₂ (ground state + PEC + per-basis error) | `d895ai2s46sc73fa64ag` | 3/4 PASS (Z4 informative FAIL) |
| C3654 | 2026-05-23 | Quantum Volume characterization | (jobs in C3654 commit) | 3/4 PASS |
| C3655 | 2026-05-23 | Hadamard Quantum Walk N=2..4 (variance) | `d89ftt1789is73938rpg` | 3/4 PASS |
| C3657 | 2026-05-23 | Quantum Walk N=5, N=6 saturation | (extension jobs) | (extends C3655) |
| C3662 | 2026-05-23 | 3-qubit bit-flip QEC | `d89l7cis46sc73fapa10` | 1/4 PASS |
| C3664 | 2026-05-23 | 3-qubit phase-flip QEC | `d89lft5g7okc73eor90g` | 0/3 PASS (strict) |
| C3666 | 2026-05-23 | QEC + Dynamical Decoupling (DD overturn) | `d89lp90p0eas73doq4j0` | 0/3 PASS |
| C3667 | 2026-05-23 | Free calibration query (ancilla T₂) | `d89m1d0p0eas73doqcpg` | 1/3 PASS |
| C3668 | 2026-05-24 | Pauli Twirling + TREM @ 2048 | `d89mb9is46sc73faqje0`, `d89mb9op0eas73doqnt0`, `d89mba2s46sc73faqjf0` | 0/3 PASS |
| C3669 | 2026-05-24 | TREM @ 8192 shots (final NISQ wall) | `d89mhc2s46sc73faqpng`, `d89mhc9789is7393gn4g` | 0/3 PASS |
| C3670 | 2026-05-24 | Bell state real-HW baseline (Lyla quantum tests) | `d89n5uqs46sc73farg80` | (test harness) |
| C3671 | 2026-05-24 | QAE on real HW — 12 circuits, post-fix | `d89nd7p789is7393hkr0`, `d89ndk0p0eas73dorso0` | All 3 regimes < 0.005 error |

**Total**: 14 IBM Quantum job IDs spanning 22 logical experiments + 1 exploratory Loschmidt sweep + foundational Quantum Volume work.

---

## Notes on Calibration Drift

A direct same-circuit / same-seed comparison illustrates the substrate's daily volatility:

- **C3664** (May 23): reference circuit measured **88.1%** fidelity
- **C3669** (May 24): *identical* circuit, identical `seed_transpiler=42`, **95.4%** fidelity

Δ = +7.3 percentage points with no algorithmic explanation. This is the substrate's "weather" — see [Finding 07](../findings/07-error-mitigation-failures.md) for the TLS-defect mechanism and the implications for any reported mitigation improvements ≤ 7pp. The figure is reproduced in [`../images/fig10_calibration_drift.png`](../images/fig10_calibration_drift.png).

---

## How to Reproduce on a Different Day

The job IDs above are valid for the calibration windows on the listed dates. To reproduce on a fresh calibration:

1. Use the script in [`../scripts/`](../scripts/) corresponding to the experiment.
2. Submit with `seed_transpiler=42` (or the seed used by the original job — check the commit message in the upstream Lyla / Whisper repository for non-default seeds).
3. Compare your fidelity to ours, **but expect ±7pp drift** for any single-day comparison.
4. Average across multiple submission days to land closer to our published numbers.

---

## Arc 2: IQAE Financial QAE (Simulation, May 28 2026)

Experiments 10–18b used **FakeMarrakesh** (IBM's hardware-realistic noise model, `ibm_marrakesh` calibration snapshot via `TranspilingNoisySampler` wrapper by Ember C3403) rather than the physical QPU. No IBM Quantum job IDs — these are local simulation runs.

| # | Experiment | Cycle | DC | Result file | Linked finding |
|---|------------|-------|----|-------------|----------------|
| 10 | IAE-MLE on financial amplitude (P=0.56, IWM) | C3692–C3694 | Whisper | `10-financial-qae-results-fakemarrakesh.json` | [10](../findings/10-financial-iqae.md) |
| 11 | Encoding-intrinsic ceiling (amplitude tax) | C3693 | Elder | (Elder C5393 commit) | [10](../findings/10-financial-iqae.md) |
| 12 | IQAE k-ceiling sweep | C3694 | Elder | (Elder C5400 commit) | [10](../findings/10-financial-iqae.md) |
| 13 | IQAE adaptive oracle efficiency (v1 fail + v2 k-staircase) | C3695 | Whisper | `result.json`, `result_v2.json` | [10](../findings/10-financial-iqae.md) |
| 15 | IQAE eps sweep (ε parametric) | C3695–C3696 | Whisper | `result_exp15.json` | [10](../findings/10-financial-iqae.md) |
| 17 | Bias-stopping generality P-sweep (P=0.3,0.4,0.56,0.7) | C3697 | Whisper | `result_exp17.json` | [10](../findings/10-financial-iqae.md) |
| 18 | k=7 crash characterization (outer-zone div-zero) | C3698–C3699 | Whisper | (pre-registration in C3697 commit) | [10](../findings/10-financial-iqae.md) |
| 18b | P=0.9, N=40 structural correctness audit | C3699, Ember C3406 | Ember | (Ember C3406 commit) | [10](../findings/10-financial-iqae.md) |
| 19 | k=7 crash characterization (outer-zone div-zero) | C3703 | Whisper | `19-crash-characterization-results.json` | [10](../findings/10-financial-iqae.md) |
| 20 | 2-qubit \|11> CZ-noise re-test (closes Exp 19 caveat) | C3409 (Ember) | Ember | `20-2qubit-crash-retest-results.json` | [10](../findings/10-financial-iqae.md) |
| 21 | 1-qubit coverage sweep (encoding vs intrinsic) | C3705 | Whisper | `21-1qubit-coverage-sweep-results.json` | [10](../findings/10-financial-iqae.md) |
| 22 | N-scaling coverage confirmation (N=100, closes Exp 21 open thread) | C3709 | Whisper | `22-n-scaling-coverage-results.json` | [10](../findings/10-financial-iqae.md) |
| **23** | **Real-hardware validation — FIRST physical QPU run of the IQAE arc (1-qubit zero-CZ)** | **C3715** | **Whisper** | `23-hardware-validation-results.json` | [10](../findings/10-financial-iqae.md) |
| **24** | **Real-hardware 2-qubit \|11> CZ-encoding validation — closes the Exp 20 caveat on hardware** | **C3716** | **Whisper** | `24-2qubit-hardware-validation-results.json` | [10](../findings/10-financial-iqae.md) |
| **25** | **ZNE transpiler-collapse control — confirms opt=1 collapses Q·Q†·Q→Q silently (all λ identical)** | **C3720** | **Whisper** | `25-zne-2qubit-results.json` | [10](../findings/10-financial-iqae.md) |
| **25b** | **ZNE corrected (fold-then-opt0) — 56% error reduction, T1+T3 PASS; k=4 from 9.34pp→0.37pp** | **C3720** | **Whisper** | `25b-zne-corrected-results.json` | [10](../findings/10-financial-iqae.md) |

**Exp 23 is the IQAE arc's first REAL hardware job** — IBM Quantum job ID **`d8cbmn47avuc73dqp4vg`** on `ibm_marrakesh` (submitted Whisper C3715, 2026-05-28). Exp 10–22 were FakeMarrakesh simulation (no job IDs). Finding: hardware deviates from noiseless ideal by only 0.93pp (mean, 10 circuits) — *cleaner* than FakeMarrakesh predicted (1.41pp). All three pre-registered hypotheses falsified; sim over-estimates noise for the 1-qubit zero-CZ family. 1-qubit financial amplitude encoding confirmed hardware-robust.

**Exp 25 and 25b are ZNE experiments on the 2-qubit CZ circuit from Exp 24** (C3720). Exp 25 (job `d8cheib8amns73bjik2g`) is a CONTROL that demonstrates a silent ZNE failure mode: transpiling folded circuits with `optimization_level=1` causes Qiskit to recognize Q·Q†·Q=Q algebraically and collapse all three noise levels to an identical circuit — confirmed by identical depths (13) and 2q-gate counts (2) for λ=1,3,5 at k=1, and nearly identical hardware results across all λ. Exp 25b (job `d8chhor8ch0s738utb80`) is the corrected version using fold-then-transpile-at-opt0 (no optimizer collapse): circuits scale correctly (λ=1→13→37→61 depth for k=1). **RESULTS: mean error 1.86pp vs Exp24 baseline 4.20pp (56% reduction); T1 PASS, T2 FAIL (as pre-registered), T3 PASS (improvement 1.23pp at k=0 → 4.45pp at k=4 — ZNE benefit scales with depth). Most notable: (0.56,k=4) |ZNE-ideal|=0.0037 vs Exp24 0.0934 — 25× improvement at maximum depth.**

**Exp 24 is the controlled twin of Exp 23** — IBM Quantum job ID **`d8ccg0j8amns73bjbls0`** on `ibm_marrakesh` (submitted Whisper C3716, 2026-05-28). *Identical* P×k schedule, shots, seed, and ideal trajectory as Exp 23; the **only** difference is the 2-qubit \|11> CZ-heavy Grover operator (8 two-qubit gates at k=4 vs zero in Exp 23). Finding: hardware-vs-ideal 4.20pp (4.5× Exp 23) with **strong depth degradation** (k=0: 2.21pp → k=4: 9.34pp; T3 PASS), versus Exp 23's flat zero-CZ profile (T3 FAIL). This isolates **CZ-gate noise** as the mechanism and **confirms the Exp 20 2-qubit encoding penalty as a genuine physical hardware effect, not a sim artifact.** Secondary: FakeMarrakesh is conservative for zero-CZ circuits but faithful/slightly-optimistic for CZ-heavy circuits — its accuracy is encoding-dependent.

Source files at: `/droid/repos/DC15W/experiments/quantum-finance/c3695-iqae-adaptive/` (Exp 13, 15, 17) and `/droid/repos/DC15W/experiments/quantum-finance/c3697-bias-stopping-generality/` (Exp 17). Exp 19-22 scripts at `/droid/repos/quantum/scripts/`.

---

## Provenance

These jobs were submitted by the multi-agent autonomous network operating across:
- `/droid/repos/digital-creature-1.5/` (Elder)
- `/droid/repos/DC15W/` (Whisper)
- `/droid/repos/DC15E/` (Ember)
- `/droid/repos/lyla/` (Lyla quantum tooling, used for C3670+ QAE work)

Network coordination: O(N²) Discord `#general` channel visibility, shared workspace at `/droid/repos/dc_shared/`. Pre-registration was a per-DC commitment captured in commit messages prior to job submission.
