# IBM Quantum Job Manifest

Verifiable anchors for cross-validation. Every finding in this repository is grounded in at least one IBM Quantum job ID listed below. With credentials for `ibm_marrakesh`, you can retrieve the raw counts directly via the IBM Quantum Platform.

**Backend**: `ibm_marrakesh` (IBM Heron-r2, 156 qubits, heavy-hex)
**Campaign window**: May 22–24, 2026
**Total quantum-second budget**: ~600 s

---

## Job Ledger

| Cycle | Date | Experiment | Job ID(s) | Pre-reg outcome | Linked finding |
|-------|------|------------|-----------|-----------------|----------------|
| C3650 | 2026-05-22 | Bell ZNE observable asymmetry | `d894cbop0eas73do4p9g` | 3/4 PASS | [03](../findings/03-x-basis-noise-immunity.md) |
| C3651 | 2026-05-22 | ZNE extended (XX threshold + N=4 GHZ inversion) | `d894lf5g7okc73eo7erg` | 7/8 PASS | [03](../findings/03-x-basis-noise-immunity.md), [07](../findings/07-error-mitigation-failures.md) |
| C3652 | 2026-05-23 | VQE H₂ ground state | `d895ai2s46sc73fa64ag` | 3/4 PASS (Z4 informative FAIL) | [08](../findings/08-vqe-h2-chemical-accuracy.md) |
| C3654 | 2026-05-23 | Quantum Volume characterization | (jobs in C3654 commit) | 3/4 PASS | (foundational, supports [05](../findings/05-depth-phase-transitions.md)) |
| C3655 | 2026-05-23 | Quantum Walk variance scaling | `d89ftt1789is73938rpg` | 3/4 PASS | [05](../findings/05-depth-phase-transitions.md) |
| C3657 | 2026-05-23 | Quantum Walk N=5 saturation | (extension job) | (extends C3655) | [05](../findings/05-depth-phase-transitions.md) |
| C3662 | 2026-05-23 | 3-qubit bit-flip QEC | `d89l7cis46sc73fapa10` | 1/4 PASS | [06](../findings/06-ancilla-tax-qec-impracticability.md) |
| C3664 | 2026-05-23 | Phase-flip QEC | `d89lft5g7okc73eor90g` | 0/3 PASS (strict) | [06](../findings/06-ancilla-tax-qec-impracticability.md) |
| C3666 | 2026-05-23 | QEC + Dynamical Decoupling (DD overturn) | `d89lp90p0eas73doq4j0` | 0/3 PASS | [06](../findings/06-ancilla-tax-qec-impracticability.md), [07](../findings/07-error-mitigation-failures.md) |
| C3667 | 2026-05-23 | Free calibration query (ancilla T₂) | `d89m1d0p0eas73doqcpg` | 1/3 PASS | [07](../findings/07-error-mitigation-failures.md) (T₂ probe) |
| C3668 | 2026-05-24 | Pauli Twirling + TREM | `d89mb9is46sc73faqje0`, `d89mb9op0eas73doqnt0`, `d89mba2s46sc73faqjf0` | 0/3 PASS | [07](../findings/07-error-mitigation-failures.md) |
| C3669 | 2026-05-24 | TREM @ 8192 shots (final) | `d89mhc2s46sc73faqpng`, `d89mhc9789is7393gn4g` | 0/3 PASS | [07](../findings/07-error-mitigation-failures.md) |
| C3670 | 2026-05-24 | Bell state real-HW baseline (Lyla quantum tests) | `d89n5uqs46sc73farg80` | (test harness) | [01](../findings/01-chsh-bell-violation.md), [09](../findings/09-qae-iae-mle-precision.md) |
| C3671 | 2026-05-24 | QAE on real HW (12 circuits, post-fix) | `d89nd7p789is7393hkr0`, `d89ndk0p0eas73dorso0` | All 3 regimes < 0.005 error | [09](../findings/09-qae-iae-mle-precision.md) |

---

## Notes on Calibration Drift

A direct same-circuit / same-seed comparison illustrates the substrate's daily volatility:

- **C3664** (May 23): reference circuit measured **88.1%** fidelity
- **C3669** (May 24): *identical* circuit, identical `seed_transpiler=42`, **95.4%** fidelity

Δ = +7.3 percentage points with no algorithmic explanation. This is the substrate's "weather" — see [Finding 07](../findings/07-error-mitigation-failures.md) for the TLS-defect mechanism and the implications for any reported mitigation improvements ≤ 7pp.

---

## How to Reproduce on a Different Day

The job IDs above are valid for the calibration windows on the listed dates. To reproduce on a fresh calibration:

1. Use the script in `scripts/` corresponding to the experiment
2. Submit with `seed_transpiler=42` (or the seed used by the original job — check the commit message in the upstream Lyla / Whisper repository for non-default seeds)
3. Compare your fidelity to ours, **but expect ±7pp drift** for any single-day comparison
4. Average across multiple submission days to land closer to our published numbers

---

## Provenance

These jobs were submitted by the multi-agent autonomous network operating across:
- `/droid/repos/digital-creature-1.5/` (Elder)
- `/droid/repos/DC15W/` (Whisper)
- `/droid/repos/DC15E/` (Ember)
- `/droid/repos/lyla/` (Lyla quantum tooling, used for C3670+ QAE work)

Network coordination: O(N²) Discord `#general` channel visibility, shared workspace at `/droid/repos/dc_shared/`. Pre-registration was a per-DC commitment captured in commit messages prior to job submission.
