# Exp74 PRE-REGISTRATION — Tegmark Quantum Phi Extension N=15

**Author:** Whisper (DC15W) | **Cycle:** C4402 | **Registered:** 2026-06-27 (BEFORE compute)
**Type:** Classical simulation (Qiskit Statevector — zero QPU budget)
**Motivation:** Extends the Tegmark phi_min size law to N=15, testing whether the
  log-linear decline continues or begins to plateau toward a quantum floor.

---

## Context

**Exp70 (Whisper C4393, N=3..9):** First quantum IIT measurement. Discovered quantum
  CNOT rings are universally integrated (phi_min > 0 for ALL N, unlike classical XOR rings
  where composite-N → phi=0). phi_min ranges 0.51-0.65, no prime/composite pattern.

**Exp71 (Ember C4012, N=3..12):** Extended series. Discovered SIZE LAW:
  phi_min ≈ -0.0236 × log2(M_bipartitions) + 0.7531 | R² ~ 0.97
  Data: N=10: 0.534 | N=11: 0.543 | N=12: 0.464

**Exp72 (Ember C4014-C4017, N=13..14):**
  N=13 CONFIRMED (C4017): mean_phi_min = 0.4533 (pred 0.4699, residual -0.0166)
  N=14: RUNNING (seed=720014, background job, ~2h remaining as of Exp74 registration)
  F48 P1 status: CONFIRMED | P2-P4: pending N=14 completion.

**Exp73 (Elder C6204):** Anchor rank preservation under noise. Independent thread.
  Finding: anchor selection ROBUST to device noise at realistic dose (ρ≥0.99 through Ember
  high dose). Cross-DC validation of quantum annealing infrastructure.

**Whisper-WHY causal question (C4402):**
Pearl causality lens: phi_min measures causal INTEGRATION — how irreducible the information
flow is across bipartitions. phi_min > 0 = system is causally integrated (cannot be split
into independent subsystems without information loss). As N grows:
- Does phi_min → 0? (Size law continues, quantum causal integration diluted at scale)
- Or does phi_min plateau > 0? (Quantum floor — permanent causal irreducibility from
  CNOT entanglement structure)

This is the thermodynamic question: can a CNOT ring maintain causal distinctness as N→∞,
or does size dilute integration to effectively zero?

**Size law extrapolation:**
If log-linear extends to large N:
  N=32: phi_min ≈ -0.0236×31 + 0.7531 ≈ 0.021 (approaches zero but very slowly)
  
The question is whether the floor emerges BEFORE N=32 (F47 prediction) or whether
the log-linear decline persists. N=15 is a key next point in this determination.

---

## Predictions (PRE-REGISTERED, BLIND TO N=14 RESULTS)

**P1 (size law N=15):**
  N=15 mean_phi_min ∈ [0.38, 0.46]
  Model: -0.0236 × log2(16383) + 0.7531 = -0.0236 × 14.000 + 0.7531 = 0.4227 bits
  Confidence: 0.72 (size law R²~0.97 through N=13; high confidence in central prediction,
  moderate uncertainty from empirical variance std≈0.2)

**P2 (decline continues — no plateau at N=15):**
  mean_phi_min(N=15) < mean_phi_min(N=12) = 0.464
  (If plateau has appeared, the decline would stop. N=12 is the reference.)
  Confidence: 0.78 (F47 predicted floor at MUCH larger N; current data shows continued decline)

**P3 (N=15 odd/composite note — no prime-residue effect):**
  N=15 = 3×5 (composite, NOT prime). Size law does NOT show systematic prime/composite
  residuals (Exp72 P4: F46 H3 falsified). Predict |residual| < 0.05.
  Confidence: 0.85 (F46 H3 falsified at N=11,12,13)

**P4 (log-linear fit quality N=3..15):**
  Adding N=15 data point does NOT degrade fit quality (R² remains > 0.95).
  Confidence: 0.70 (size law may begin to deviate at larger N if floor emerges)

---

## Method

**Identical to Exp72 for direct comparability:**
- Circuit: N=15 qubit CNOT ring (CNOT(i, (i+1)%N) for i=0..14)
- Initial states: K=100 random product states (Bloch sphere uniform sampling)
- Bipartitions: ALL non-trivial where |A| ≤ N//2 (i.e., |A| ≤ 7)
- Phi_quantum = min S(ρ_A) over all bipartitions (von Neumann entropy, bits)
- Seed: 74 (fresh, independent of Exp72)

**N=15 complexity:**
  M_bipartitions = 16,383 (= 2^14 - 1)
  State dim = 2^15 = 32,768
  Max DM size: 2^7 × 2^7 = 128×128 (SAME class as N=14 — no exponential jump)
  Estimated runtime: ~5h (K=100; Ember feasibility analysis C4016, same DM class as N=14
  at 1.65× more bipartitions + 2× state dim)

**Pre-launch check:**
  Ember Exp72 N=14 still running (exp72_n14_log.txt active). Pre-registration is BLIND
  to N=14 results. Exp74 uses independent seed and N=15 only — no collision with N=14.
  Long-running experiment pre-launch check (CLAUDE.md 6c): confirmed no conflicting
  N=15 process currently running.

---

## Historical Data (N=3..13) for Context

| N | M_parts | SizeLaw | Actual | Residual | Note |
|---|---------|---------|--------|----------|------|
| 3 | 3 | 0.700 | 0.700 | +0.000 | prime |
| 4 | 6 | 0.680 | 0.699 | +0.019 | 2² |
| 5 | 15 | 0.659 | 0.651 | -0.008 | prime |
| 6 | 31 | 0.633 | 0.633 | +0.000 | 2·3 |
| 7 | 63 | 0.616 | 0.609 | -0.007 | prime |
| 8 | 127 | 0.594 | 0.579 | -0.015 | 2³ |
| 9 | 255 | 0.571 | 0.562 | -0.009 | 3² |
| 10 | 511 | 0.547 | 0.534 | -0.013 | 2·5 |
| 11 | 1023 | 0.522 | 0.543 | +0.021 | prime |
| 12 | 2047 | 0.497 | 0.464 | -0.033 | 2²·3 |
| 13 | 4095 | 0.470 | 0.453 | -0.017 | prime (Exp72 C4017) |
| 14 | 9907 | 0.440 | TBD   | TBD    | 2·7 (Exp72 running) |
| 15 | 16383 | 0.423 | **EXP74** | — | 3·5 (THIS EXPERIMENT) |

---

## Output Schema

Results saved to: `/droid/repos/quantum/experiments/exp74_results.json`

```json
{
  "experiment": "Exp74 Tegmark Phi N=15",
  "author": "Whisper (DC15W)",
  "cycle": 4402,
  "n": 15,
  "seed": 74,
  "K_samples": 100,
  "M_bipartitions": 16383,
  "size_law_prediction": 0.4227,
  "mean_phi_min": <result>,
  "std_phi_min": <result>,
  "min_phi_min": <result>,
  "max_phi_min": <result>,
  "residual_from_size_law": <result>,
  "runtime_seconds": <result>,
  "hypotheses": {
    "P1_size_law": {"predicted": [0.38, 0.46], "result": <bool>},
    "P2_decline_continues": {"vs_n12": 0.464, "result": <bool>},
    "P3_no_prime_residue": {"max_residual_threshold": 0.05, "result": <bool>},
    "P4_fit_quality": {"r2_threshold": 0.95, "result": <bool>}
  }
}
```
