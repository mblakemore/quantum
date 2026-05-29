# Finding 07 — Software Error Mitigation Is Largely Futile on Heron-r2

**Result**: Four canonical Error Mitigation strategies — Dynamical Decoupling, Pauli Twirling, Twirled Readout Error Mitigation (TREM), and Zero-Noise Extrapolation (ZNE) — were systematically applied to `ibm_marrakesh`. **All four degraded signal or were dwarfed by ±7pp daily substrate calibration drift.**

**Significance**: Software-level mitigation cannot rescue an algorithm from a thermodynamically volatile substrate. The path forward is **hardware-aware compilation** (locking seeds, choosing immune bases, minimizing depth), not algorithmic correction layers.

> **ELI5 — Plain English**: The quantum-computing community has a toolbox of clever software tricks that are supposed to *undo* the effects of chip noise after the fact — Dynamical Decoupling (DD), Pauli Twirling (PT), Twirled Readout Mitigation (TREM), and Zero-Noise Extrapolation (ZNE). We tried all four on this chip. **All four made things worse, not better.** Why? Each trick was invented for an older generation of chips with different dominant noise. On *this* chip, the trick adds more noise than it removes. Meanwhile, we discovered the chip's day-to-day variation is **±7 percentage points** (same circuit, same seed, 24 hours apart) — so any tiny "1–2pp improvement" from software tricks is **lost in the chip's natural wobble**. Bottom line: stop spending engineering effort on noise-cleanup software for this generation of hardware. Spend it on making your circuits *shorter* and on choosing the chip's "easy direction" (Finding 3) instead.

![All four mitigation strategies failed](../images/fig07_mitigation_failures.png)

*Figure 7. Δ fidelity (percentage points) and statistical significance for the four mitigation techniques attempted in cycles C3666–C3669. All four landed below zero — each technique was a net detractor at the measured shot counts.*

![Calibration drift: identical circuit, ±7pp in 24h](../images/fig10_calibration_drift.png)

*Figure 7b. The substrate "weather" — same circuit, same `seed_transpiler=42`, 24 hours apart, +7.3pp drift with no algorithmic explanation. Any 1–3pp improvement claim that does not control for this drift envelope is suspect.*

---

## The Four Failures

### 1. Dynamical Decoupling (DD) — Catastrophic

**Theory**: Insert rapid X-pulse sequences (Hahn echo, XY4) into idle qubit windows to average out low-frequency T₂ dephasing.

**Empirical result on `ibm_marrakesh`**:
- Initial application: silent failure. The `PadDynamicalDecoupling` transpiler pass requires an explicit `ALAPScheduleAnalysis` pass to be run first. **Without it, no pulses are inserted at all**, and the compiler will not warn you. (Critical software hazard for automated quantum pipelines.)
- After fixing the scheduling bug: XY4 sequence application produced a **catastrophic fidelity drop**.
- Causal analysis: 30–36 rapid microwave X-pulses inject **massive coherent calibration errors and microwave cross-talk** directly into the data payload.

**Why it failed**: T₁ and T₂ on Heron-r2 are routinely **> 200 μs**, with ancilla T₂ measured 270–340 μs during this campaign. A typical 500 ns idle window during syndrome extraction produces ~0.17% natural dephasing decay. **The threat DD was designed to suppress does not exist on this hardware.** Active CZ-gate errors (~0.4% each) dominate passive idling decoherence by ~20×.

DD is the right tool for older fixed-coupling architectures (Falcon, Eagle). It is the **wrong tool** for tunable-coupler Heron-class hardware. The XY4 pulse train is solving a problem that has already been solved by IBM's hardware-level coherence improvements.

**Evidence**: C3666 `do(DD)` → P(syndrome) decreased. Q0 fidelity 86.5% → 76.4%. Spread increased 3.8pp → 11pp. Pearl causal model overturned. Job `d89lp90p0eas73doq4j0`.

### 2. Pauli Twirling (PT) — Net Negative

**Theory**: Frame target gates with randomized Pauli operators to convert destructive *coherent* errors (quadratic accumulation) into *stochastic* errors (linear accumulation) that classical error budgets can absorb.

**Empirical result**:
- Error spread reduced from 3.8pp to ~1.3pp — **the coherent-to-stochastic conversion worked exactly as theoretically predicted**.
- BUT the mean fidelity dropped by ~2.3pp (6σ).

**Why it failed**: IBM's extensive hardware-level calibration on Heron-r2 already ensures the vast majority of residual gate noise is **stochastic depolarizing** noise, not coherent under-rotation. Pauli twirling applied to already-stochastic noise just incurs the thermodynamic cost of the additional framing gates **without yielding any conversion benefit**. The overhead is real; the upside is zero.

**Evidence**: C3668 PT job `d89mb9is46sc73faqje0`. Spread compression confirmed; mean fidelity loss confirmed. Conclusion: **Heron-r2 errors are already stochastic — twirling them is gilding the lily**.

### 3. Twirled Readout Error Mitigation (TREM) — Statistically Significant Degradation

**Theory**: Apply random X-gates immediately before readout to symmetrize asymmetric readout errors.

**Empirical result**:
- TREM @ 2048 shots: approximately flat (within shot noise floor)
- TREM @ 8192 shots: **-0.7pp degradation, 2.7σ negative** on the target observable

**Why it failed**: The X-gates applied immediately prior to the readout resonators **inject more stochastic gate error than the readout asymmetry they cancel**. On modern hardware where readout calibration is already pretty good, the net effect of "fixing" readout via additional gates is negative.

**Evidence**: C3669 TREM@8192 job `d89mhc9789is7393gn4g`. -0.7pp delta, 2.7σ.

### 4. Zero-Noise Extrapolation (ZNE) — Linear Models Fail at Scale

**Theory**: Amplify noise (1×, 2×, 3×) via identity insertions / unitary folding, regress observable error back to zero-noise intercept.

**Empirical result at N=2 (Bell state)**: Works as predicted. ZNE recovers a meaningful zero-noise estimate. Provides clean evidence of `⟨XX⟩` immunity (see [Finding 03](03-x-basis-noise-immunity.md)).

**Empirical result at N=4 (GHZ-4)**: **N-Inversion** — the noise scaling patterns *qualitatively inverted* from N=2:

| Observable | N=2 scaling | N=4 scaling |
|------------|-------------|-------------|
| `⟨XX...X⟩` | IMMUNE | γ=0.779 **decelerating** |
| `⟨YY...Y⟩` | γ≈0.7 decelerating | γ=1.439 **accelerating** |
| `⟨ZZ...Z⟩` | γ≈1.6 accelerating | γ=1.963 still accelerating, more steeply |

**Why it failed**: As the register size grows, the topological weight of multi-qubit Pauli operators shifts and their commutation relations with global cross-talk and readout channels change fundamentally. **The linear scaling models calibrated on 2-qubit benchmarks do not extrapolate to N-qubit algorithmic structures.**

This is a deep limitation: ZNE assumes a known scaling form. On Heron-r2, the scaling form **changes with N**. Any production deployment of ZNE on multi-qubit observables requires per-N calibration — which obviates much of the point.

**Evidence**: C3651 ZNE-extended job `d894lf5g7okc73eo7erg`. 7/8 pre-reg PASS, with the N-inversion being the most novel finding (γ-spread = 1.184).

## The Dominating Effect: Daily Calibration Drift

Across these iterative mitigation experiments, the campaign discovered a confound that overwhelms all four mitigation strategies:

**Same circuit. Same transpiler seed. Same shot count. Different day. ±7 percentage point fidelity drift.**

Specifically: a reference circuit on C3664 measured **88.1%** fidelity. The *identical* circuit (seed=42, no changes) on C3669 measured **95.4%** fidelity. Δ = 7.3 percentage points, no algorithmic explanation.

**Cause**: Two-Level System (TLS) defects in the dielectric substrate couple to qubits as the dilution refrigerator's millikelvin temperatures fluctuate. A high-fidelity "hero" qubit one day becomes a poisoned qubit the next as a TLS migrates within the substrate.

**Implication**: Any error mitigation strategy that claims a 1–3pp improvement is **inside the substrate noise envelope**. You cannot honestly report a 2pp ZNE improvement without specifying which calibration day you measured on, and a re-measurement the next day might show the "improvement" inverted entirely.

This is the most operationally important finding in the entire campaign for anyone deploying quantum algorithms in production: **the substrate is the noise floor, and the substrate moves**. Real-time hardware characterization must precede any high-stakes algorithmic execution.

## Refinement (C3725–C3726): the "futile" verdict was confounded — here is the law underneath it

Finding 7's own caveat (cross-day, cross-circuit; ±7pp drift) means its blanket "mitigation
is futile" verdict was confounded by its own standard. Two co-submitted, deconfounded
experiments (matched-pairs, one calibration snapshot — the C3723 design) resolved it.

**Exp 28 — the Gate-Overhead Sign Rule (CONFIRMED, job `d8cievj8ch0s738uujsg`).**
Holding the *target* fixed (readout error) and varying *only* the mechanism, on the same
circuits under one calibration snapshot: REM (M⁻¹ post-processing, **0** added gates)
*helped* (−0.68pp), while TREM (X-twirl, **injects** gates, same readout target) was *null*
(−0.19pp). The **sign** of a technique's effect is set by its residual payload-gate
overhead, **not** the error channel it targets. Finding 7 is **refined, not overturned**:
gate-*injecting* mitigation is futile on Heron-r2; *zero-gate-overhead* mitigation
(post-processing REM, extrapolate-away ZNE) extracts genuine value.

**Exp 29 — the Gate-Overhead Dose-Response Law (CONFIRMED, job `d8cj4k2jki0s73arbrg0`).**
The strongest form of the test: inject `D` logically-**identity** CZ-pairs (`CZ·CZ = I`,
barrier-fenced) into the payload and vary only `D ∈ {0,2,4,6}` pairs → `{0,4,8,12}` added
2q-gates. Identity injection targets *nothing*, so any degradation is **pure gate
overhead** — the confound-free limit of Exp 28 (which still *targeted* readout). Result on
live `ibm_marrakesh`, perfectly monotone:

| Injected identity CZ-pairs | Added 2q-gates | Raw mean error | REM mean error |
|---|---|---|---|
| 0 | 0 | 2.83pp | 2.01pp |
| 2 | 4 | 3.60pp | 2.84pp |
| 4 | 8 | 4.72pp | 3.90pp |
| 6 | 12 | 5.98pp | 5.19pp |

Spearman `ρ(D, error) = +1.000`; OLS slope **+0.264pp of estimator error per added
2q-gate**. The REM-corrected slope (+0.265pp/gate) is *identical* to the raw slope —
readout is a constant offset; the per-gate cost is the **gates themselves**, not readout.

**The law underneath the Sign Rule:** residual payload-gate count is a *continuous* cause
of degradation, costing ≈0.26pp per added 2-qubit gate on this substrate. This is *why*
every gate-injecting technique (TREM, DD pulse trains, PT framing) lands net-negative — each
added gate costs more than the passive error it was designed to remove. Mitigation is not
"futile"; it is **governed by a gate-overhead budget**, and only techniques that spend zero
residual payload gates can come out ahead.

## The Working Strategy: Hardware-Aware Compilation

Given that DD, PT, TREM, and ZNE all under-perform, the productive replacements are:

1. **Lock transpiler seeds.** The compiler's freedom to re-route is, in expectation, a destructive freedom on Heron-r2. Pin the seed.
2. **Choose noise-immune bases.** Map observables to `⟨X⟩` and `⟨Z⟩` where the algorithm permits. Avoid `S†` gates.
3. **Minimize CZ depth.** This is the single largest lever (see [Finding 05](05-depth-phase-transitions.md)).
4. **Use IAE-MLE-style maximum-likelihood estimators** for amplitude problems instead of relying on raw shot statistics (see [Finding 09](09-qae-iae-mle-precision.md)). This is a **genuine** mitigation that works.
5. **Measure twice, deploy once.** Run a screening job on the day of your real run to confirm baseline fidelity. If you're outside your expected envelope, defer.

## Cross-Validation

- **C3666 DD overturn**: Job `d89lp90p0eas73doq4j0`
- **C3668 PT + TREM**: Jobs `d89mb9is46sc73faqje0`, `d89mb9op0eas73doqnt0`, `d89mba2s46sc73faqjf0`
- **C3669 TREM@8192**: Jobs `d89mhc2s46sc73faqpng`, `d89mhc9789is7393gn4g`
- **C3651 ZNE N-inversion**: Job `d894lf5g7okc73eo7erg`
- **C3667 calibration query (free)**: Job `d89m1d0p0eas73doqcpg`. Ancilla T₂ = 270–340 μs documented.

## Sources

- ZNE theory and folding-free approaches — see [`sources/references.md`](../sources/references.md) entries [21], [51], [45], [54], [55].
- IBM Quantum dynamical-decoupling pass manager — see [`sources/references.md`](../sources/references.md) entries [46], [47], [48], [49] (Qiskit docs + source).
- TLS / dielectric-defect literature — see [`sources/references.md`](../sources/references.md) entry [11] (PMC12003810), entry [16] (IBM TLS mitigation).
- Calibration-drift datasets — see [`sources/references.md`](../sources/references.md) entries [52] (Hugging Face qiskit-calibration-drift), [53] (few-shot cross-device transfer).
- Approximate compilation and proton-transfer kinetics — see [`sources/references.md`](../sources/references.md) entry [50].
- Pauli-twirling symmetrization — Wallman, J.J.; Emerson, J. (2016). "Noise tailoring for scalable quantum computation via randomized compiling." *Phys. Rev. A* 94, 052325.
- Readout error mitigation (M3) — see [`sources/references.md`](../sources/references.md) entry [44].
