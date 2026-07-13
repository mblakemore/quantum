# Exp124 — THE TRACTOR BEAM (ZENO PINNING): PREREGISTRATION (FROZEN)

**Author**: Whisper (DC15W), C4657. Creator: "Q6!" — the LAST open horizons-2 item.
One-cycle pipeline (Exp119/123-class: single qubit, huge margins, known physics).
Sim: `exp124_zeno_sim.py` → `results/exp124_feasibility.json` (law check PASS).

## Design correction owned first

The horizons-2 Q6 sketch ("pin against T1 decay") was **physically wrong** and is
corrected here at design time: Zeno protection requires quadratic short-time
dynamics; Markovian T1 decay is exponential and measurement-cadence-invariant.
The honest tractor beam: **hold |1⟩ against a coherent full π-rotation by
watching it.** Unwatched survival = cos²(π/2) = **0 exactly**; watched at cadence
N: P = [cos²(π/2N)]^N → 1. The claim class is "measurement holds a state against
coherent evolution at a certified strength," not "measurement beats
thermodynamics."

## Frozen apparatus (builders byte-identical: `exp124_zeno_sim.py::build`)

Single qubit. Arms: **pinned_N** (N ∈ {2,4,8,16}: Rx(π/N)+measure, ×N),
**unwatched_8** (same 8 Rx steps + barriers, no mid measurements —
structure-invariant per the C4650 anchor rule), **nodrive_N** (measurements only:
per-measurement QND survival q, the nuisance measured then corrected —
friction-02 practice). **9 pubs × 20k = 180k shots** — the cheapest flight of the
campaign. Site: frozen rule = argmin readout error (tiebreak index). Seeds 4657.
Audit: per-arm gate counts uniform; single-qubit (no 2q gates at all — a first).

## Frozen statistics and gates

P(pinned) = P(every projection = 1); unwatched = P(final = 1). Binomial SEs.

- **G0 (NO-TEST)**: nodrive_8 > 0.7 (fake 0.907) — mid-circuit measurement must be
  functional or pinning is untestable.
- **W_TRACTOR (headline)**: P(pinned_8) − P(unwatched_8) > 0.3 at 5σ →
  **ZENO-PINNING-CERTIFIED** (fake: 0.666 − 0.015 = 0.65; ~100σ above the bar).
- **W_CADENCE (support)**: P(pinned_8) − P(pinned_2) > 0 at 5σ — watch faster,
  hold tighter (fake diff 0.42).
- **Subclaims (reported)**: QND-corrected law residuals P/(q^N) vs [cos²(π/2N)]^N;
  q per cadence from nodrive arms (**the switch-bench v3 axis number**); the
  Zeno-vs-measurement-cost tradeoff (fake shows N=16 gains eaten by q^16 —
  hardware peak-cadence location reported).

## Predictions (registered at freeze)

**P1** W_TRACTOR: **0.92**. **P2** W_CADENCE: **0.90**. **P3** NO-TEST: **0.05**.

R2: `grade_exp124.py --selftest` 4/4 required pre-hardware
(`results/exp124_selftest.txt`). Lint: `experiments/exp124_gate_lint_spec.json`.
