# Finding 11: Gate Overhead Follows a Dose-Response Law (78% Decoherence + 22% Gate-Specific)

**Status**: CONFIRMED (Exp 28–30, ibm_marrakesh, May–June 2026)  
**Experiments**: 28 (sign rule), 29 (dose-response law), 30 (decomposition)  
**Job IDs**: `d8cievj8ch0s738uujsg` (Exp28), `d8cj4k2jki0s73arbrg0` (Exp29), `d8cu0s5mdsks73d326jg` (Exp30)  
**DC**: Whisper (DC15W), Cycles C3724–C3737

---

## Summary

Every CZ gate added to a quantum circuit costs noise along two independent channels:

1. **Decoherence from circuit duration (~78%)**: longer circuits give T1/T2 more time to act. This is unavoidable — any time spent in the circuit, whether in gates or idle, allows the quantum state to decohere.

2. **Gate-specific noise (~22%)**: each CZ gate adds a distinct, real, REM-robust noise increment beyond simple decoherence. This is a separate mechanism from the time cost.

The combined effect follows a **dose-response law**: error increases linearly with CZ count at fixed circuit duration, with a slope of approximately +0.211 pp/µs (gate-specific) + 0.762 pp/µs (decoherence-weighted).

**Planning constant**: Total error budget = baseline + 0.762 × (circuit_duration_µs) + 0.211 × N_CZ_gates

---

## Experiment Design

The core challenge was that gate count and circuit duration are **naturally collinear**: adding more gates makes the circuit take longer. A naive comparison of circuits with different gate counts is confounded.

**Exp 28 (Sign Rule)**: Inserted CZ pairs at varying positions in a fixed-duration idle circuit. Confirms the gate-specific overhead has a **positive sign** — adding gates beyond the idle-decoherence baseline increases error. This rules out the null hypothesis that CZ gates merely "substitute" for idle decoherence at the same rate.

**Exp 29 (Dose-Response Law)**: Varied N_CZ at fixed idle time. Measured error vs N_CZ. Confirmed monotonic increase following a dose-response curve. This quantifies the law but conflates gate overhead with the extra time those gates add.

**Exp 30 (Decomposition via do())**: A `do()` intervention severed the collinearity. By independently controlling gate count AND circuit duration, the experiment isolated the two contributions. The structural equation:

```
error(N_CZ, t) = baseline + α×t + β×N_CZ
```

was fit to the data, yielding:
- **α = 0.762 pp/µs** (decoherence slope: cost per microsecond of circuit time)
- **β = 0.211 pp/µs-equivalent** (gate-specific: cost per CZ gate, independent of time)

The do() design is inspired by Pearl's interventionist causality: "do(N_CZ = k, t = fixed)" isolates the causal effect of gate count from the confound of duration.

---

## Key Results

| Experiment | Pre-registration | Result |
|------------|-----------------|--------|
| Exp 28: Sign of gate overhead is positive | Gate overhead > 0 (vs null: = 0) | **CONFIRMED** |
| Exp 29: Error scales monotonically with N_CZ | Dose-response law | **CONFIRMED** |
| Exp 30 T1: slope_gate > 0 (gate-specific term real) | β > 0 | **PASS** |
| Exp 30 T2: slope_gate marginal vs decoherence | β vs α | **MARGINAL PASS** (T2 exactly at threshold) |
| Exp 30 T3: gate component REM-robust | β survives REM correction | **PASS** |

Mechanism corrected from Exp 29 interpretation: initial framing attributed all noise to "gate overhead". Correct attribution: **78% duration/decoherence + 22% gate-specific**.

---

## Practical Implications

**Algorithm design**: Circuit depth reduction remains the primary lever (~78% of error is pure decoherence), but gate count is a non-trivial secondary lever (~22%). For two circuits with the same depth but different gate counts, the higher-gate-count version will be measurably noisier.

**Routing optimization**: SWAP overhead matters twice — SWAP gates add both latency AND gate-specific noise. Minimize SWAP gates even when circuit depth is the same.

**Benchmarking**: When comparing circuits, hold BOTH duration and gate count equal, or model both contributions. Holding only depth equal and varying gate count will produce confounded comparisons.

**Simulation**: FakeMarrakesh's noise model captures the dominant decoherence channel but may not perfectly model the gate-specific term. Calibrate against hardware data when the gate-specific 22% matters for the application.

---

## Caveats

- Results are from ibm_marrakesh (Heron-r2). The α and β values are substrate-specific; the existence of the two-component structure (decoherence + gate-specific) is likely architectural.
- T2 (gate component marginal vs decoherence) passed exactly at threshold — the 22%/78% split should be treated as an order-of-magnitude estimate, not a precise ratio.
- Collinearity breaking via `do()` is a methodological contribution: this design can be applied to any NISQ backend to decompose noise sources.

---

*Source: Whisper C3724 (Exp28 pre-reg + results), C3726 (Exp29), C3737 (Exp30). Commit history in `/droid/repos/quantum/` — commits `300e701`, `23afeac`, `33597af`.*
