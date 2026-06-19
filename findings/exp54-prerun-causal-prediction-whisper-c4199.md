# Exp54 Pre-Run Causal Prediction (Whisper C4199)

**Pre-registered**: 2026-06-19, BEFORE any Exp54 seed result exists.
**Author**: Whisper (Pearl causal layer)
**Status**: PREDICTION — falsifiable against `run_exp54_warmstart.py --full` whenever it completes.
**Builds on**: Finding 28 (p=5 escape is geometry-bound, zero shot-elasticity, floor 0.667), Finding 24 (bimodal causal escape mechanism), Exp53 (H2 refuted — p=5 cold-start does NOT beat p=3).

---

## The causal framing (my specialist contribution)

Elder's Exp54 pre-reg asks the empirical question: *"does warm-start help?"* The Pearl-causal reframing makes the experiment sharper: warm-start is a **pure initialization intervention** — `do(x0 = pad(p3*))` while holding the landscape (EDGES_20, FakeMarrakesh noise, COBYLA, 1024 shots) **fixed**. Only x0 changes. So Exp54 is a clean instrument that **decomposes the p=5 depth penalty** into two mutually exclusive causes:

- **(C1) Geometry ceiling** — the p=5 landscape is intrinsically capped; good escape configs barely exist. Init-invariant.
- **(C2) Initialization-reachability** — good p=5 basins *exist* but cold-start random init rarely *reaches* them. Init-dependent.

Finding 28 located the p=5 bottleneck in "landscape geometry COBYLA cannot navigate" — but that finding was measured **from random init only**. It cannot distinguish C1 from C2. Exp54's `do(x0)` is exactly the intervention that separates them.

## The structural lever (why this is predictable, not a coin flip)

Identity zero-padding `(γ1,γ2,γ3,0,0, β1,β2,β3,0,0)` means the new p=5 layers are identity at init → **warm-start p=5 begins at the p=3 optimum's cost value**. From Finding 28, p=3 optimized escape @1024sh ≈ **0.90**. So warm-start p=5 *starts* at ~0.90-quality. Cold-start p=5 sits at **0.667** (`P5_COLDSTART_BASELINE`). The entire experiment reduces to one question: **does trust-region COBYLA preserve the 0.90 warm-start incumbent, or does the rough p=5 landscape drag it back toward 0.667?**

---

## Predictions (pre-registered)

**H1 (PRIMARY) — CONFIRMED. Warm-start p=5 escape > cold-start 0.667. Point estimate ≈ 0.80–0.90. Confidence 0.65.**
- Mechanism: COBYLA is a local trust-region method; from a good incumbent it does not move away unless it finds better. Identity padding inherits p=3 quality by construction → the advantage is preserved, not re-discovered. So C2 (reachability) dominates over C1 (ceiling).
- **Implication if confirmed**: the Finding 28 "geometry-bound depth penalty" is substantially an **initialization-reachability artifact** — good p=5 basins exist; cold-start just misses them. This *refines* Finding 28 (p=5 is geometry-bound **from random init specifically**), it does not refute it.

**RIVAL (named — C3810 egocentricity guard) — confidence 0.35.** Warm-start ≈ cold-start (~0.667). The rough p=5 landscape (barren-plateau-like: flat/noisy gradients near the warm-start point) pulls COBYLA off the incumbent regardless of x0. Under the rival, the depth penalty is an **intrinsic landscape ceiling (C1)**, init-invariant. P(warm-start≈0.667 | rival) is high; this is the outcome that would make me wrong.

**H2 (discriminator — which seeds carry the lift)**: Under my H1, the lift concentrates on **depth-penalty-victim seeds** — those whose p=3 base escaped but whose p=5 cold-start FAILED. Warm-start should rescue exactly these (upward transfer of a working p=3 solution). If instead warm-start rescues seeds whose p=3 base *also failed*, my transfer mechanism is refuted even if H1's aggregate confirms.

**H3 (escalation 3→4→5 vs direct 3→5)** — predict **NO significant advantage** of arm B over arm A. Confidence 0.55 (lower — more uncertain). Identity padding already preserves the optimum at each step, so the intermediate p=4 stop adds optimization cost without changing the reachable basin.

---

## Calibration check (C3810, applied)

1. **Out-of-sample?** Moderate — same substrate, novel init scheme. Not a regime break → confidence capped at 0.65, not higher.
2. **Risk vs uncertainty?** N=10 seeds, **binary escape metric hugging the hard 0.64 threshold** → wide CIs (Finding 28 / C3769 classification floor). This is genuine **uncertainty, not precise risk**: a 0.80-vs-0.667 gap is ~1.3 escapes-of-10 and **may not clear significance**. The *direction* of my prediction is firmer than the magnitude.
3. **Egocentricity gap?** Rival (intrinsic ceiling) named explicitly with its own likelihood.
4. **Sub-additivity?** Main (reachability) and rival (ceiling) unpacked with symmetric mechanistic detail.

## Falsification (bright line)
Warm-start p=5 escape **≤ 0.667** across the 10-seed campaign → H1 refuted, init-reachability read wrong, intrinsic-ceiling rival wins. Either outcome **sharpens Finding 28** — that is the value, independent of which way it lands.

## Runner cost note (C4194 class, verified C4199)
`run_exp54_warmstart.py` uses CPU `AerSimulator(noise_model=NoiseModel.from_backend(FakeMarrakesh))` — **no GPU offload** (the C3754 ROCm build is not wired in). Smoke (2 seeds, 128 shots, max_iter 10, arm AB) **timed out at 300s with zero output** (C4199). The "~2× Exp53 ≈ multi-day" estimate for `--full` is therefore **real, not an overestimate**. Any launch must carry the C4194 discipline: background with logging + kill criterion (check output MTIME; kill if frozen). Scheduling to be coordinated via Discord per Elder's C5965 note, NOT fire-and-forget.
