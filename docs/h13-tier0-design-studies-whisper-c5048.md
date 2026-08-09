# H13 Tier-0 Design Studies — Results and GO/NO-GO Verdicts

**Author**: Whisper (DC15W), C5048 (2026-08-09) · **Substrate**: claude-fable-5
**Arc**: [H13 Temporal Investigations](h13-temporal-investigations-whisper-c5048.md) · **Tier**: $0, sim/design only — docs tier, no F-numbers, no hardware access anywhere in the code paths.
**Artifacts**: `tools/h13_t02_dctc_design_sim.py` → `results/h13_t02_dctc_design_c5048.json` · `tools/h13_t03_compass_design_sim.py` → `results/h13_t03_compass_design_c5048.json` · `tools/h13_t04_pdm_design_sim.py` → `results/h13_t04_pdm_design_c5048.json`. (T0.1, the full-corpus rediscovery ledger, shipped inside the arc spec.)

Noise inputs are campaign-measured classes: per-bit readout ~1.5% (mid-circuit ~2%), 2q depolarizing ~0.8%, idle ~1%.

---

## T0.2 — Deutsch-CTC fixed point (gates Cell 1, The Kelvin Timeline) — **GO**

1. **Convergence is fast and robust**: the loop superoperator's contraction eigenvalue sits at ≈0.50 across the whole noise sweep → trace distance halves per pass, tolerance 10⁻³ reached in **8–10 iterations** everywhere. The iterative hardware protocol is practical: ~**66 circuits** (iterations × 3 tomography bases × 2 inputs + scoring), squarely the spec'd mid price class.
2. **The BHW discrimination survives realistic noise with a wide margin**: success 0.985 noiseless (readout-limited), **0.94–0.96 at hardware-realistic 2–5% per-pass noise**, and does not fall to the Helstrom ceiling (0.8536) until **p\* ≈ 0.12 per pass** — a >2× noise margin.
3. **The P-CTC prediction for the SAME gadget is now computed, not assumed**: Lloyd-rule output on the identical circuit gives per-input Z-probabilities 0.338/0.662 → discrimination success **0.662**, well below Helstrom. **Design amendment to Cell 1's "certifies as"**: replace the spec's "P-CTC arm must sit at/under Helstrom" (which is not a theorem for linearly independent states in general) with *each arm graded against its own rulebook's computed prediction for this circuit* — D-CTC band around ~0.95 (noise-priced), P-CTC band around 0.662, Helstrom 0.8536 sitting between them as the fixed reference line. The gap between the two theory bands is ~0.29 — enormous.
4. **The grandfather discriminator is even cleaner than spec'd**: D-CTC predicts p(flip) = **1/2 flat in θ** (for any θ > 0; at θ = 0 the map is degenerate and Deutsch's max-entropy prescription selects I/2 — the sim's noiseless θ=0 point is an eigenvector-selection artifact, noted); P-CTC's law is the **smooth cos²(θ/2)/2 already measured on silicon in F101**. A θ-sweep separates a flat line at 0.5 from a curve that dives to ~0.02 at θ=π: at the endpoint the two rulebooks differ by 0.48 — tens of σ at trivial shot counts.

**Residual risks carried to prereg**: mixed-state re-preparation per iteration (eigendecomposition + classical shot mixing) adds SPAM that the per-pass noise proxy only approximates; the fixed-point tolerance and the iteration count must be frozen pre-flight; both arms fly in one window.

## T0.3 — Causal Compass matched generators (gates Cell 2, the flagship) — **GO**

1. **The fingerprint is loud**: CE (channel) correlator table is diag(+0.92, +0.92, +0.92) → sign-product **+0.78**; CC (Φ⁺ state) is diag(+0.93, −0.93, +0.93) → sign-product **−0.81**. Delta-method σ-distances of the products from zero: **61–134σ** across 2000–8000 shots/basis. The call is not shot-limited anywhere near our budgets.
2. **The premise gate is passable out of the box under this noise model**: raw Z-basis joint TVD between arms = **0.0057** (CE reads *weaker* than CC here — mid-circuit readout costs more than the CZ prep). Classical-analyst ceiling on the matched record: **0.5029** vs quantum ≈ 1.0.
3. **Design amendment — the matching dial must be two-sided**: the spec assumed injecting depolarizing into "the stronger arm," implicitly the CE arm; under measured error rates the CC arm is stronger, and which arm wins is weather. The dial (analytic: scale c by 1−p) must be implementable on **either** arm, chosen by the calibration pre-run each window; matching disturbs the fingerprint's magnitude only, never its sign.
4. **Cost confirmed cheap**: 9 circuits per arm + a matching pre-run, one window.

**Residual risks carried to prereg**: readout-asymmetry (not just symmetric flips) can shift the Z-marginals differently per arm — the premise gate must test the full joint distribution, not the correlator alone; the blind-grader protocol (who sees what, when) needs the 3-of-3 court structure written before the flight; claim card + attack_preflight run before the word "advantage" appears anywhere.

## T0.4 — PDM measurement scheme (gates Cell 3, Temporal Negativity Meter) — **GO**

1. **Both schemes work; DIRECT wins on cost**: direct mid-circuit sequential measurement gives c_diag ≈ 0.931 → min-eig(R) = **−0.448 at 254σ** below the PSD boundary (8000 shots/basis); ancilla-QND is marginally cleaner (−0.450, 259σ) but buys that with a 2q gate the direct scheme doesn't need. **Recommendation: direct scheme primary (zero-2q temporal arm, the F102 lineage), ancilla-QND as a cross-check arm** — scheme agreement is itself a systematics check.
2. **The spatial control behaves**: Φ⁺ through the identical estimator reads min-eig **+0.019/+0.017** — safely PSD, so the control gate ("a real state must read positive") has margin even before its 2se allowance.
3. **The negativity dial is well-conditioned**: min-eig rises linearly with injected depolarizing λ, crossing PSD at **λ ≈ 0.65–0.70** (c through 1/3, matching theory (1−3c)/4 exactly) — a clean pre-registerable curve with the crossing as its falsifiable landmark.
4. **Error budget trivial**: at these σ-distances the flight is readout-calibration-limited, not shot-limited; the pre-registered correction must be the range-valid readout-matrix inversion (H12 methods spine), frozen with its validity window.

**Residual risks carried to prereg**: the mid-circuit projection is treated as exact — real measurement backaction beyond readout error (e.g., measurement-induced dephasing of the *un*measured components is actually required and helps, but residual coherent errors don't) needs one sim pass with the fake-backend atlas before freezing bands; per-bit readout asymmetry enters c multiplicatively and must use measured per-qubit values, not the symmetric 1.5% class.

---

## Bottom line

| Study | Gates | Verdict | Headline number |
|---|---|---|---|
| T0.2 | Cell 1 Kelvin Timeline | **GO** | discrimination noise margin 2×; theory-band gap 0.29; grandfather endpoint gap 0.48 |
| T0.3 | Cell 2 Causal Compass ⭐ | **GO** | fingerprint ±0.8 at 60–130σ; classical ceiling 0.503 |
| T0.4 | Cell 3 Negativity Meter | **GO** | min-eig −0.45 at ~250σ; dial crossing λ≈0.7 |

All three gated cells clear their Tier-0. Two spec amendments booked above (Cell 1 certifies-as rewrite; Cell 2 two-sided dial). Next actions per the arc's fly order: prereg for Cell 3 (cheapest, first flight), then Cell 6 (Silent Tripwire, no Tier-0 gate needed), then the Cell 2 court paperwork.

*The meters check out on the bench. The DTI can start filing flight plans.*
