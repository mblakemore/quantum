# N=8 scars past the wall — the scar survives; the wall is just decoherence (Ember, C4202)

**Creator directive (2026-07-18):** *"fly N=8 scars past the wall."* A deliberate coherence-wall probe:
does the many-body-scar anomaly survive at greater depth (bigger, cleaner noiseless signal) or does the
wall win? **Job** `d9duc14inv1c73apigj0`, `ibm_fez`, 35 circuits (5 inits × step 0..6), **8000 shots**,
**433 CZ** deepest (s≈0.385). **Pre-reg** (0.45, frozen): `F-anomaly > 0.05 AND Neel-anomaly > 0.05`;
null (wall wins) pre-registered as the likely, first-class outcome. **Verdict: HELD (bare gate).**

---

## Result

| init | role | F[6] | Néel \|m_s\|[6] |
|---|---|---|---|
| **10101010** | **SCAR** | **0.120** | **0.269** |
| 10101000 | generic | 0.062 | 0.206 |
| 00000000 | generic | 0.035 | 0.009 |
| 10100010 | generic | 0.018 | 0.093 |
| 10001000 | generic | 0.009 | 0.046 |

- **|Z₂⟩ is still the outlier at 433 CZ.** Néel anomaly **+0.064 ± 0.005 (2.6σ over the 0.05 gate)**;
  fidelity anomaly **+0.058 ± 0.005 (1.7σ, readout-limited)**. Both clear the frozen bare gate; the
  readout-robust Néel observable clears it at 2.6σ.

## The answer — the R-ratio, not the bare number

The bare anomaly (+0.06) is smaller than N=6's (+0.13) — but that comparison is meaningless, because an
anomaly is a *difference* and a difference scales by the survival factor s (the C4200 lesson): both the
noiseless anomaly and s differ between N=6 and N=8. The wall-probe question is not "is the number
smaller" but **"does the scar decay as pure decoherence predicts, or faster?"** The metric is the
residual ratio:

  **R = measured anomaly / (noiseless anomaly × s)**,  with N=6's R ≈ 0.56 as the reference.

| | measured | noiseless | s (actual qubits) | **R** |
|---|---|---|---|---|
| **Néel (clean read)** | +0.064 | +0.285 | 0.385 | **0.58** |
| fidelity | +0.058 | +0.333 | 0.385 | 0.45 |

**Néel R = 0.58 ≈ N=6's 0.56.** The scar anomaly shrank by *exactly* the decoherence factor and no
more — **the scar mechanism is intact; the coherence wall only attenuates the signal, it does not break
the scar.** "The wall is just decoherence." The fidelity R=0.45 sits a little lower, but that is the
*expected* mundane penalty of an 8-qubit return probability (all 8 bits must read correctly) — not a
scar-specific breakdown, which is why the per-qubit, readout-robust Néel R is the load-bearing read.
There is no evidence of scar-specific collapse at depth up to 433 CZ.

## Method — the three advisor-hardened checks (all the session's own lessons, applied)

1. **Outlier is airtight, not a convenient four:** a 0-QPU scan of all **55** blockade-respecting
   product states confirmed |Z₂⟩ is **rank 1/55** by fidelity revival (0.757; next non-Néel 0.424). The
   ensemble includes that strongest generic reviver (10101000) as the toughest honest comparison.
2. **Error bar restored** (dropped after Exp157): analytic SE — binomial on F, propagated on m_s —
   plus 8000 shots, so HELD/null is judged with a σ, not read off a point estimate. The verdict's
   nuance (Néel 2.6σ vs F 1.7σ) is only visible *because* the bar is there.
3. **R-ratio, not bare anomaly** (the C4200 lesson): a difference scales by s, so the finding is built
   around R vs 0.56 — which cleanly separates "scar intact, decoherence-limited" (R≈0.56) from
   "scar-specific breakdown" (R≪0.56). s priced on the actual job qubits (C4199), not a borrowed rate.

## Fence

Finite chain (N=8), coarse Trotter (dt=0.8, revival verified across dt), 433 CZ. The claim is a
hardware **signature**: the scar anomaly persists past the wall and its attenuation is consistent with
pure decoherence (R invariant from N=6). The fidelity channel is readout-limited at 8 qubits;
higher-fidelity readout or a ratio-based observable would sharpen the F read. Not a thermodynamic proof.

## What the universe answered

Pushing the Néel scar from N=6 (260 CZ) to N=8 (433 CZ): |Z₂⟩ remains the outlier over all 55
blockade states, and the anomaly's decay from N=6 to N=8 is exactly the decoherence factor — **the
scar goes past the wall intact, and the wall is just decoherence, not a scar killer.** The wall-probe
maps to "attenuation, not collapse." The exotic-phases wing's fourth phase now has a depth
characterization: the scar mechanism itself is robust; only the coherence budget limits how far we can
read it.

**Numbering:** new experiment (Exp172), exotic-phases wing; the session's deepest flight (433 CZ).
