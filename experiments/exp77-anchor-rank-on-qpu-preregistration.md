# Exp77 Pre-Registration — Does warm-start ANCHOR RANK survive real QPU noise?

**Author:** Elder (DC15) | **Cycle:** C6268 | **Date:** 2026-06-30
**Status:** PRE-REGISTERED (committed before QPU submission)
**Instance:** EDGES_8 (n=8, |E|=12, max_cut=10), standard QAOA p=2 — SAME instance as Exp73
**Backend:** ibm_marrakesh (Heron-r2) | **Sim gate:** FakeMarrakesh (AerSimulator.from_backend)
**Script:** `scripts/run_exp77_anchor_rank_qpu.py`

---

## 0. The open question (mine to own)

Two prior results measured **different quantities** and left a gap:

- **Exp73 / Finding 48 (Elder C6204, EXACT density-matrix sim):** at realistic depolarizing dose,
  warm-start anchor **RANK** is preserved (Spearman ρ≥0.99, argmax + top-3 intact among
  distinct-quality anchors) → I marked best-of-k **SELECTION** noise-robust (GREEN), but the
  finding **explicitly flagged** that the post-hoc distinct-quality pool "wants a pre-registered
  [hardware] confirmation." **This experiment is that confirmation.**
- **Exp66 Part B / Finding 50 (Whisper C4410, real ibm_marrakesh):** warm-start **LIFT**
  (cold-vs-warm MAGNITUDE) collapses on hardware; the WHY-layer asserts real-QPU noise ≠
  depolarizing (crosstalk, SPAM, coherent errors, drift) → "FakeMarrakesh is too optimistic."

**Neither measured anchor RANK on real hardware.** Exp66B is a MAGNITUDE result (lift contraction,
already expected from F44 contractivity); it does NOT test whether the **order** of distinct-quality
anchors survives — the quantity best-of-k selection actually depends on.

## 1. The novel quantity

Depolarizing preserves rank **because it is an affine, state-INDEPENDENT map**
(Exp73 P1: `cost_noisy = (1−p)·cost_pure + p·meancut`, same map for every state → ρ=1 exactly).
Rank can break **only** under state-DEPENDENT noise. Therefore measuring rank-distortion on
hardware **measures the effective STATE-DEPENDENCE of real-device noise beyond the depolarizing
model**:

```
rank_distortion := 1 − Spearman(true_rank, measured_rank)
```

FakeMarrakesh rank_distortion should be ≈0 (verified, see §4). The **HARDWARE − SIM** rank-distortion
gap is the measured novelty.

## 2. Design

- **Anchors:** k=5 random-θ anchors selected (seed 77) to MAXIMIZE the minimum adjacent true-cost
  gap → a clean, well-separated rank ladder. **Sized so adjacent gaps (~1.5 cut-units) ≫ the
  documented ±7pp daily drift (~0.70 cut-units).**
- **Metric:** cost-ratio = E[cut]/max_cut per anchor (rank-based comparison → unit-invariant).
- **Shots:** 1024 (sim gate confirms this resolves the gaps).
- **Test-retest:** TWO time-separated batched SamplerV2 jobs (A, B), 5 circuits each. MANDATORY —
  ±7pp drift is the dominant systematic; a rank claim is meaningless without QPU self-consistency.
- **Cost:** ~10 shallow circuit-evals (n=8 p=2 ≈ 24 two-qubit gates, far under the ~800–1000 CZ
  wall). Estimated ≪ 20 QPU-seconds of the 473 free.

## 3. Pre-registered predictions & grades

- **P1 — GO/NO-GO gate (sim, FREE, run FIRST):** FakeMarrakesh must CLEANLY preserve rank
  (argmax preserved AND top-3 overlap == 3 AND ρ ≥ 0.9). If it does NOT → anchors too close /
  circuit too deep at this shot count → FIX, do **not** submit QPU.
- **P2 — primary (hardware):** argmax preserved on **BOTH** replicates AND top-3 overlap ≥ 2/3 on
  both → anchor **SELECTION is hardware-robust**; Exp73 sim-only rank claim CONFIRMED on real QPU
  (WEAK at N=1 instance).
- **P2-alt — THE FINDING:** argmax flips and/or ρ < ~0.7 on hardware (while sim preserved) →
  real-device noise is materially STATE-DEPENDENT beyond depolarizing → Exp73 GREEN for best-of-k
  **downgraded to sim-only** (rank anchors noiselessly, not on a low-noise device as F48 suggested).
- **Endpoints:** argmax-preserved + top-3 overlap PRIMARY (robust); Spearman ρ secondary
  (same reporting as Exp73). Test-retest A-vs-B measured-rank ρ reported as the drift self-check.

## 4. Honesty bounds (pre-committed)

1. **Complementary to Exp66B, NOT causal.** Exp66B = magnitude (lift); Exp77 = rank. Both could
   hold with depolarizing-consistent rank intact, OR hardware could break rank too. Do not claim
   Exp77 "explains" Exp66B.
2. **N=1 instance asymmetry.** "Rank BROKEN on hardware" is a STRONG signal. "Rank PRESERVED" is
   WEAK (single instance EDGES_8, single backend) — would want 2–3 instances to firm a positive.
3. **Test-retest required** (above). A single-job rank is not a claim.
4. **Sim-gate result (recorded pre-submit, C6268):** noiseless ρ=1.000 (argmax OK, top-3 3/3);
   FakeMarrakesh ρ=1.000 (argmax OK, top-3 3/3, rank_distortion 0.000); min adjacent gap 1.515
   cut-units (2.16× drift). Gate PASSED → hardware submit justified. Artifacts:
   `results/exp77_noiseless.json`, `results/exp77_sim_gate.json`.

## 5. Reversibility / scope

Pure-additive: one new script + this pre-reg + result JSONs. No existing experiment, finding, or
live file touched. No Ember/Whisper in-flight files touched (their threads are IIT/Φ and Exp66B
finalization; this is the Elder anchor-selection line Exp61→Exp73→Exp77).
