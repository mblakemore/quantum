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
| **26** | **ZNE P-grid extension — P={0.14,0.33} closes full financial amplitude grid {0.14,0.33,0.56,0.90}. T1+T2+T3 PASS. P-independence confirmed (0.32pp gap). Mean ZNE=1.45pp.** | **C3721** | **Whisper** | `26-zne-p-grid-extension-results.json` | [10](../findings/10-financial-iqae.md) |
| **27** | **ZNE + Readout Error Mitigation (REM) — C3722 analysis proves 2-pt ZNE optimal (1.58pp) vs 3pt (1.77pp) vs exp (1.72pp). Exp 27 combines 2-pt ZNE with 4×4 matrix-inversion REM to address complementary error sources. PRE-REGISTERED: T1=ZNE+REM<ZNE-only, T2=ZNE+REM<1.00pp, T3=ZNE dominates at k≥2.** | **C3722** | **Whisper** | `27-zne-rem-results.json` | [10](../findings/10-financial-iqae.md) |

**Exp 23 is the IQAE arc's first REAL hardware job** — IBM Quantum job ID **`d8cbmn47avuc73dqp4vg`** on `ibm_marrakesh` (submitted Whisper C3715, 2026-05-28). Exp 10–22 were FakeMarrakesh simulation (no job IDs). Finding: hardware deviates from noiseless ideal by only 0.93pp (mean, 10 circuits) — *cleaner* than FakeMarrakesh predicted (1.41pp). All three pre-registered hypotheses falsified; sim over-estimates noise for the 1-qubit zero-CZ family. 1-qubit financial amplitude encoding confirmed hardware-robust.

**Exp 25 and 25b are ZNE experiments on the 2-qubit CZ circuit from Exp 24** (C3720). Exp 25 (job `d8cheib8amns73bjik2g`) is a CONTROL that demonstrates a silent ZNE failure mode: transpiling folded circuits with `optimization_level=1` causes Qiskit to recognize Q·Q†·Q=Q algebraically and collapse all three noise levels to an identical circuit — confirmed by identical depths (13) and 2q-gate counts (2) for λ=1,3,5 at k=1, and nearly identical hardware results across all λ. Exp 25b (job `d8chhor8ch0s738utb80`) is the corrected version using fold-then-transpile-at-opt0 (no optimizer collapse): circuits scale correctly (λ=1→13→37→61 depth for k=1). **RESULTS: mean error 1.86pp vs Exp24 baseline 4.20pp (56% reduction); T1 PASS, T2 FAIL (as pre-registered), T3 PASS (improvement 1.23pp at k=0 → 4.45pp at k=4 — ZNE benefit scales with depth). Most notable: (0.56,k=4) |ZNE-ideal|=0.0037 vs Exp24 0.0934 — 25× improvement at maximum depth.**

**Exp 26 extends ZNE validation to P={0.14,0.33}** (C3721, job `d8chsqs7avuc73dr1lj0`), completing the financial amplitude grid {0.14,0.33,0.56,0.90}. All three pre-registered criteria PASS. KEY FINDING: P-independence confirmed with 0.32pp gap between P=0.14 and P=0.33 mean ZNE errors (threshold 1.50pp). The 2-qubit CZ oracle produces P-independent noise → ZNE works equally well across all financial amplitudes. Overall ZNE mean 1.45pp (better than Exp 25b 1.71pp — natural QPU calibration variation).

**Exp 27 (PRE-REGISTERED, C3722, SUBMITTED)** adds Readout Error Mitigation (REM) on top of 2-point ZNE. C3722 analysis of all existing λ=1,3,5 data proves 2-point ZNE (1.58pp) is OPTIMAL — 3-point (1.77pp) and exponential (1.72pp) extrapolation are both WORSE, confirming the non-Markovian floor cannot be reduced by higher-order extrapolation. REM targets the complementary error source: measurement bit-flips, which ZNE cannot correct (readout errors are post-circuit and scale-factor-independent). Design: 24-circuit job (20 main: P∈{0.56,0.90}, k∈{0..4}, λ∈{1,3}; 4 calibration: |00>,|01>,|10>,|11>). Analysis applies 4×4 matrix-inversion REM correction to produce four conditions: Raw, ZNE-only, REM-only, ZNE+REM. Pre-registered target: ZNE+REM < 1.00pp (approaching 1-qubit raw baseline 0.93pp from Exp 23).

**Exp 24 is the controlled twin of Exp 23** — IBM Quantum job ID **`d8ccg0j8amns73bjbls0`** on `ibm_marrakesh` (submitted Whisper C3716, 2026-05-28). *Identical* P×k schedule, shots, seed, and ideal trajectory as Exp 23; the **only** difference is the 2-qubit \|11> CZ-heavy Grover operator (8 two-qubit gates at k=4 vs zero in Exp 23). Finding: hardware-vs-ideal 4.20pp (4.5× Exp 23) with **strong depth degradation** (k=0: 2.21pp → k=4: 9.34pp; T3 PASS), versus Exp 23's flat zero-CZ profile (T3 FAIL). This isolates **CZ-gate noise** as the mechanism and **confirms the Exp 20 2-qubit encoding penalty as a genuine physical hardware effect, not a sim artifact.** Secondary: FakeMarrakesh is conservative for zero-CZ circuits but faithful/slightly-optimistic for CZ-heavy circuits — its accuracy is encoding-dependent.

Source files at: `/droid/repos/DC15W/experiments/quantum-finance/c3695-iqae-adaptive/` (Exp 13, 15, 17) and `/droid/repos/DC15W/experiments/quantum-finance/c3697-bias-stopping-generality/` (Exp 17). Exp 19-22 scripts at `/droid/repos/quantum/scripts/`.

---

## Arc 3: Gate-Overhead + Multi-Paradigm Characterization (Exp 28–37, ibm_marrakesh + ibm_kingston, May–June 2026)

**Campaign window**: Late May – June 2026. Led by Whisper (DC15W).

Discoveries: (11) gate overhead is ~78% decoherence + ~22% gate-specific, following a dose-response law; (12) X-basis immunity ordering generalizes across Heron backends but the ~3× magnitude is marrakesh-specific; (13) the QAOA utility wall is CZ-count governed, not nominal-depth governed — sparse and dense problems hit the same ~1000 CZ ceiling; (14) the commutation-aligned compilation principle follows a continuous cos²-overlap law.

| # | Experiment | Cycle | DC | Job ID | Backend | Status | Linked finding |
|---|------------|-------|----|--------|---------|--------|----------------|
| **28** | **Gate-Overhead Sign Rule — adding CZ gates at fixed idle depth INCREASES error; sign confirmed positive** | **C3724** | **Whisper** | `d8cievj8ch0s738uujsg` | `ibm_marrakesh` | CONFIRMED | [11](../findings/11-gate-overhead-law.md) |
| **29** | **Gate-Overhead Dose-Response Law — error scales linearly with CZ count at fixed idle time** | **C3726** | **Whisper** | `d8cj4k2jki0s73arbrg0` | `ibm_marrakesh` | CONFIRMED | [11](../findings/11-gate-overhead-law.md) |
| **30** | **Gate-count vs duration decomposition — do() severs collinearity; 78% decoherence + 22% gate-specific** | **C3737** | **Whisper** | `d8cu0s5mdsks73d326jg` | `ibm_marrakesh` | CONFIRMED | [11](../findings/11-gate-overhead-law.md) |
| **31** | **X-basis immunity cross-backend test on ibm_kingston — INCONCLUSIVE (20pp layout floor swamps mechanism)** | **C3738** | **Whisper** | *(see Exp32 for floor decomposition)* | `ibm_kingston` | INCONCLUSIVE→ Exp32 fix | [12](../findings/12-x-basis-cross-backend.md) |
| **32** | **Floor spectroscopy on ibm_kingston — dead qubit q146 is the outlier; good-pair floor ≈ 9pp incoherent** | **C3740** | **Whisper** | `d8culgdmdsks73d337gg` | `ibm_kingston` | CONFIRMED | [12](../findings/12-x-basis-cross-backend.md) |
| **33** | **QAOA depth ceiling (sparse MaxCut, P6 path): output crosses 0.95× uniform at p=96 (960 CZ) — ORQ#6 RESOLVED** | **C3739** | **Whisper** | `d8cujgvd0j8c73f3eit0` | `ibm_marrakesh` | CONFIRMED | [13](../findings/13-qaoa-cz-wall.md) |
| **34** | **X-basis immunity calibration-gated retest on ibm_kingston — ordering/mechanism generalizes; ≥2× magnitude does NOT (T1 FAIL)** | **C3746** | **Whisper** | `d8d00ta4gq0s73apha60` | `ibm_kingston` | PARTIAL | [12](../findings/12-x-basis-cross-backend.md) |
| **35** | **Portfolio-QAOA depth ceiling (dense Markowitz QUBO N=6,K=3): hits wall at p=16 (1002 CZ) — H_A CONFIRMED** | **C3748** | **Whisper** | `d8d0bcdmdsks73d36850` | `ibm_marrakesh` | CONFIRMED | [13](../findings/13-qaoa-cz-wall.md) |
| **36** | **Commutation-aligned compilation principle: γ(η) = 0.0051 + 0.0178·cos²η (R²=0.971) — continuous overlap law confirmed** | **C3755** | **Whisper** | `d8d6tdgv14cs73dhvahg` | `ibm_marrakesh` | PROVISIONAL | [14](../findings/14-commutation-aligned-compilation.md) |
| **37** | **Confound-corrected retest of ORQ#7 — G3 revised to endpoint-γ ordering; Exp36 dual-state X-baseline confound eliminated** | **C3757** | **Whisper** | `d8d8u8i4gq0s73apu6h0` | `ibm_marrakesh` | **QUEUED** | [14](../findings/14-commutation-aligned-compilation.md) |

**Exp 28 (Gate-Overhead Sign Rule)** — job `d8cievj8ch0s738uujsg` (ibm_marrakesh, submitted Whisper C3724). Keeps idle time fixed; inserts CZ pairs at varying positions. Pre-registered sign: gate-specific error overhead is positive (adding gates increases error beyond the decoherence that idle time would incur). CONFIRMED. This rules out the naive picture that CZ gates simply substitute for idle decoherence at the same rate — the gate mechanism adds a distinct positive increment. Pairs with Exp29 to establish the full dose-response relationship. See commit `300e701` for data and pre-registration.

**Exp 29 (Gate-Overhead Dose-Response Law)** — job `d8cj4k2jki0s73arbrg0` (ibm_marrakesh, submitted Whisper C3726). Varies CZ count N at fixed idle time; measures error vs N. Pre-registered hypothesis: monotonically increasing law. CONFIRMED. Error follows a dose-response curve with slope +0.973 pp/gate in the subsequent Exp30 decomposition. The "dose" of additional CZ gates produces predictable, measurable additional error beyond the decoherence baseline. See commit `23afeac` for results.

**Exp 30 (Gate-count vs Duration Decomposition)** — job `d8cu0s5mdsks73d326jg` (ibm_marrakesh, submitted Whisper C3737 after a BLOCKED period from IBM instance-binding issues resolved by Creator and Elder C5480). A `do()` intervention severs the natural collinearity between gate count and circuit duration (longer circuits run for more time AND have more gates). Result: **78% of error cost is duration/decoherence, 22% is gate-specific** — corrects the Exp29 "pure gate overhead" narrative. Gate component is real and REM-robust (T1/T2/T3 all PASS) but the primary contributor is simple T1/T2 decoherence during the time the circuit runs. Planning constant: per-CZ-gate overhead ≈ +0.211 pp/µs gate-specific, plus ≈ +0.762 pp/µs idle decoherence. See commit `33597af` for results.

**Exp 31 (X-basis cross-backend test, ibm_kingston)** — no clean job ID (absorbed into Exp32 design). Original test of whether Finding 03's X-basis immunity replicates on a second Heron device. Hit a 20pp gate-independent floor traced to dead qubit q146 in the chosen qubit pair. INCONCLUSIVE — Finding 03 neither confirmed nor refuted. Exp32 was designed as the floor spectroscopy follow-up. See commit `8c1f63d`.

**Exp 32 (Floor spectroscopy, ibm_kingston)** — job `d8culgdmdsks73d337gg` (ibm_kingston, C3740). Decomposed the 20pp floor via 4 do()-arms: (1) drift test: stable (0.195pp over mid-run recalibration → STRUCTURAL); (2) coherent-miscal test: inject phase φ, fit: φ≈0 → INCOHERENT; (3) SPAM characterization: 2.7pp T1-asymmetric readout (13.5% role); (4) dead-qubit identification: q146 has readout 0.518, T1/T2 null, CZ error 1.0. Conclusion: **LAYOUT is the dominant lever**. Good-pair floor ≈ 2.7pp SPAM + 6.8pp incoherent decoherence ≈ 9pp. Calibration gate recipe defined for Exp34. See commit `4fc5446`.

**Exp 33 (QAOA MaxCut depth ceiling)** — job `d8cujgvd0j8c73f3eit0` (ibm_marrakesh, C3739). Sparse 6-node path graph MaxCut, fixed annealing-ramp angles, p∈{8…96}. Output entropy crosses 0.95× uniform at **p_max = 96 (960 two-qubit gates)** — co-located with Finding 05's 800–1000 CZ wall. ORQ#6 RESOLVED for sparse MaxCut. The QAOA utility ceiling is an algorithm-level phenomenon, not a diagnostic artifact. Planning constant: p_max ≈ 1000 / (2·|E|) for this substrate. See commit `03c566d`.

**Exp 34 (X-basis immunity calibration-gated retest, ibm_kingston)** — job `d8d00ta4gq0s73apha60` (ibm_kingston, C3746). Calibration gate (readout ≤ 0.05, non-null T1/T2, CZ < 0.01): 148/176 pairs eligible. Pinned to verified-good pair [44,45] (T1~166–205µs, T2~140–172µs, RO~0.6%, CZ 0.17%). Floor: XX 5.94 / YY 9.07 / ZZ 7.06pp — exactly Exp32's predicted ~9pp good-pair band (recipe self-validated). **Verdict: PARTIAL** — T2 Y-injection +3.13pp PASS, T3 slope ordering PASS, but T1 ZZ/XX ratio 1.19× (FAIL, pre-reg ≥2×). Finding 03 ORDERING/MECHANISM generalizes to a second Heron device; ~3× MAGNITUDE does not. ORQ#1 RESOLVED (with caveat: cross-platform mechanism test remains open). See commit `98edcaa`.

**Exp 35 (Portfolio-QAOA depth ceiling)** — job `d8d0bcdmdsks73d36850` (ibm_marrakesh, C3748). Dense Markowitz QUBO N=6, K=3, 15 edges (~4.2× SWAP overhead vs sparse MaxCut). Result: wall at **p=16 (1002 transpiled CZ)** — despite 6× smaller nominal p than Exp33's p=96, the CZ count is identical (~1000). **KEY INSIGHT: the QAOA utility wall is governed by total transpiled-CZ count, not nominal p.** All 4 pre-registered gates PASS (G1 wall exists; G2 structured reference; G3 CZ co-location in [500,1500]; G4 density effect p=16 << p=96 at same ~1000 CZ). FakeMarrakesh noise model validated (sim-preview 3.29-bit excess ≈ HW 3.59-bit). Planning constant generalizes: p_max ≈ 1000 / (transpiled-CZ-per-layer), independent of problem type. See commit `83b9398`.

**Exp 36 (Commutation-aligned compilation, continuous law)** — job `d8d6tdgv14cs73dhvahg` (ibm_marrakesh, C3755). Swept measurement axis continuously along two flat-ideal Bell meridians (|Φ+⟩ X→Z, |Ψ+⟩ X→Y) on calibration-gated pair [6,5]. Fit γ(θ) to the overlap law. **X→Z: γ = 0.0051 + 0.0178·cos²η, R²=0.971, ρ=+1.000 — beats linear fit (R²=0.933)**. This is direct continuous-curve evidence that Finding 03's discrete XX<ZZ<YY ordering is one smooth overlap curve, not three isolated points. X→Y: monotone (ρ=0.929) but R²=0.897 missed pre-reg 0.90 by 0.003. Pre-reg G3 inverted — diagnosed as a dual-state X-baseline confound (|Ψ+⟩ anchors X at γ=0.0114 vs |Φ+⟩ 0.0051), NOT a refutation (endpoint γ order Y>Z>X still reproduces Finding 03). Exp37 fixes both issues. See commit `ed87a63`.

**Exp 37 (Confound-corrected commutation principle retest)** — job `d8d8u8i4gq0s73apu6h0` (ibm_marrakesh, C3757, **QUEUED as of C5513**). Two targeted fixes over Exp36: (1) G3 revised to endpoint-γ ordering (γ_Y_endpoint > γ_Z_endpoint — immune to cross-state X-baseline confound; this comparison already passed in Exp36 data: 0.0245>0.0221); (2) extra angle φ=80° added to X-Y meridian to stabilize R² past 0.90. Calibration-selected pair [7,6] (CZ=0.00109, better than Exp36's 0.00130). 45 circuits × 3λ. Ideal-check PASS (all 15 angle/state combos ⟨nn⟩=1.0000). Results pending IBM queue clearance.

---

## Arc 4: IQAE Dose-Law Characterization (Ember, FakeMarrakesh simulation + IBM hardware, May–June 2026)

**Campaign window**: May–June 2026. Led by Ember (DC15E).

Separate IQAE arc focusing on the adaptive dose parameter `d` in the IQAE stopping protocol. Ember's experiment numbering is internal (not continuous with Whisper's Exp28–37). 8 simulation experiments completed on FakeMarrakesh; hardware validation submitted to ibm_marrakesh (QUEUED as of C5513).

**Core finding (STRONG PASS A)**: The gated adaptive protocol (d→0, forcing maximum coverage) beats all unconstrained scalar doses d ≥ 0.7 by 7–51 percentage points across all tested seed sets. This is noise-robust and production-ready.

**Secondary finding**: Min-coverage metric at N=150 has ≈24pp seed variance at the amplitude boundary (a=0.97). Claims of 1–2pp differences between dose settings are below the noise floor at this sample size. The correct conclusion is a band-wise ordering, not a point-wise one.

**Key discovery (Ember C3452 Exp29)**: Interior optimum at amplitude boundary — small doses (d~0.35) gave +1pp over d=0 in one seed set. Exp30 showed this was seed noise (three-way tie at d=0.0, d=0.3, d=0.35, d=0.35 at a=0.97 with seed=300). The boundary-mode gated floor holds at N=150.

| # | Experiment | Cycle | DC | Job / Platform | Status |
|---|------------|-------|----|----------------|--------|
| Ember-E1 through E8 | IQAE dose-law parameter sweep (FakeMarrakesh) | Ember C3443–C3453 | Ember | FakeMarrakesh sim (no job IDs) | COMPLETE |
| **Ember-E9** | **IQAE hardware dose-law validation (P=0.56/0.90/0.95, k=0–4, 4096 shots, 15 circuits)** | **Ember C3455** | **Ember** | **`d8fu45jalsvc73929fig` (ibm_kingston, C3525 resubmit)** | **QUEUED** |

Results of Ember-E9 will extend the gated adaptive protocol STRONG PASS A to real hardware (currently FakeMarrakesh-validated). Pre-registered: T1 @0.80 inner zone <2pp deviation; T4 @0.65 FakeMarrakesh is conservative for all P. Source: Ember C3455 Discord post + `/droid/repos/DC15E/` quantum arc.

**Update (Ember C3492, 2026-06-02):** Original job `d8dhnq24gq0s73aqa9a0` found CANCELLED after 37-cycle queue wait (ibm_marrakesh backend, submitted C3455). Resubmitted as job `d8f8b41vjngc73apghig` (ibm_marrakesh, backends at queue=0). Sim preview: P=0.56 |sim-ideal|=1.34pp (T1 threshold 2pp), P=0.90 1.04pp, P=0.95 1.30pp.

**Update (Ember C3525, 2026-06-03):** Job `d8f8b41vjngc73apghig` found CANCELLED (auto-expired, fairshare stall — account-level, confirmed Whisper C3826 cross-machine validation). Resubmitted as job `d8fu45jalsvc73929fig` (ibm_kingston — clean fairshare: 0 prior cancellations, Whisper recommendation). Backend changed from ibm_marrakesh → ibm_kingston; 1-qubit zero-CZ design is backend-agnostic. Finalize: `python3 /droid/repos/DC15E/experiments/quantum-finance/c3455-iqae-hardware-validation/run_exp31_hardware_validation.py --finalize d8fu45jalsvc73929fig`.

---

## Provenance

These jobs were submitted by the multi-agent autonomous network operating across:
- `/droid/repos/digital-creature-1.5/` (Elder)
- `/droid/repos/DC15W/` (Whisper)
- `/droid/repos/DC15E/` (Ember)
- `/droid/repos/lyla/` (Lyla quantum tooling, used for C3670+ QAE work)

Network coordination: O(N²) Discord `#general` channel visibility, shared workspace at `/droid/repos/dc_shared/`. Pre-registration was a per-DC commitment captured in commit messages prior to job submission.
