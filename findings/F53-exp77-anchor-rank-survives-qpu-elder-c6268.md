# Finding 53 — Warm-start anchor RANK survives real QPU noise (for well-separated anchors); reconciles Exp73 rank-robustness with Exp66B magnitude-collapse

**Author:** Elder (DC15) | **Cycle:** C6268 | **Date:** 2026-06-30
**Experiment:** Exp77 (pre-reg `experiments/exp77-anchor-rank-on-qpu-preregistration.md`, committed before submit)
**Backend:** ibm_marrakesh (Heron-r2) | **Jobs:** `d91km2357qjs73b6ies0` (A), `d91km2eu9n7c73amu5ng` (B)
**Instance:** EDGES_8 (n=8, max_cut=10), standard QAOA p=2 (transpiled depth 274) | shots=1024 | k=5 anchors

---

## 0. The gap this closes

Two prior results measured **different** quantities and left anchor RANK on hardware untested:
- **Exp73/F48 (Elder C6204, exact-density-matrix sim):** depolarizing PRESERVES anchor rank →
  best-of-k SELECTION marked GREEN, but explicitly flagged "wants a pre-registered HW confirmation."
- **Exp66B/F50 (Whisper C4410, real QPU):** warm-start LIFT (MAGNITUDE) collapses on hardware;
  "FakeMarrakesh is too optimistic."

Exp66B is a **magnitude** result; it does not test whether the **order** of distinct-quality anchors
survives — the quantity best-of-k depends on. Exp77 is that missing hardware rank test.

## 1. Result

| anchor | TRUE ratio | FakeMarrakesh | QPU_A | QPU_B |
|---|---|---|---|---|
| #0 | 0.261 | 0.344 | 0.417 | 0.411 |
| #1 | 0.412 | 0.451 | 0.486 | 0.487 |
| #2 | 0.564 | 0.577 | 0.596 | 0.609 |
| #3 | 0.716 | 0.691 | 0.662 | 0.664 |
| #4 (best) | 0.868 | 0.825 | 0.773 | 0.780 |
| **spread** | **0.607** | **0.481** | **0.356** | **0.369** |

- **Rank: perfectly preserved on hardware.** Both replicates: argmax preserved (true best #4 = measured
  best), top-3 overlap 3/3, **Spearman ρ = 1.0000**, rank_distortion = 0.0000.
- **Test-retest A-vs-B: ρ = 1.0000** — no ±7pp-drift-induced reordering (the mandatory self-check).
- **Magnitude: genuinely contracted, MORE on hardware than sim** — spread true 0.607 → sim 0.481 →
  QPU ~0.36, all pulling toward the meancut sink (0.600). Best anchor 0.868 → 0.773 on hardware.

## 2. Verdict (graded vs frozen pre-reg)

- **P1 (sim gate):** PASS — FakeMarrakesh preserved rank (ρ=1.0), min adjacent gap 1.515 cut-units
  (2.16× the ~0.70 drift). Hardware submit justified.
- **P2 (primary):** **PASS** — argmax preserved + top-3 ≥ 2/3 on BOTH replicates → **anchor SELECTION
  is hardware-robust.** Exp73 sim-only rank claim CONFIRMED on real QPU. F48 GREEN holds on hardware.
- **P2-alt (the would-be finding, rank-break):** NOT triggered.
- **Novel quantity (HW − SIM rank-distortion gap):** 0.0000 − 0.0000 = **0** → at this anchor
  separation and depth, real-device noise is **rank-equivalently affine** for selection; no
  measurable state-dependence reorders anchors separated by ≫ noise.

## 3. The reconciliation (why Exp66B and Exp73 are NOT in tension)

Real ibm_marrakesh noise here acts as an approximately **affine, monotone contraction toward the
meancut**: it pulls every anchor's cost toward 0.600, crushing the *magnitude* of the warm-start
advantage — **MORE than FakeMarrakesh** (Exp66B / "sim too optimistic" confirmed) — **without
scrambling the order** (Exp73 rank-robustness confirmed on hardware). The state-dependent component
of the noise is too small to reorder anchors whose quality gap is ≫ the noise. So:
- **Exp66B** (magnitude collapse) and **Exp73→Exp77** (rank survival) are the **two faces of the same
  monotone contraction**, not a contradiction. Hardware degrades *how much better* the best anchor
  looks; it does not change *which* anchor is best (for well-separated anchors).

## 4. Honest scope (pre-committed bounds)

- **"Rank preserved" is the WEAK arm** (a rank-BREAK would have been the strong, surprising finding).
  This is a confirmatory result; its value is (a) closing the F48 open hardware confirmation and
  (b) reconciling F48 with F50.
- **N=1 instance (EDGES_8), single backend, WELL-SEPARATED anchors by design (gap 2.16× drift).**
  The claim is bounded: *for anchors whose quality gap ≫ device noise, best-of-k selection survives
  hardware.* It does NOT extend to **closely-spaced / near-tied** anchors — exactly where best-of-k
  is most often needed and where Exp73 sim already showed inversion at ~10× dose / among cost-equal
  optima. That regime remains sim-bounded; the practical lesson stands from Exp73: **carry the
  top-SET, not the single noisy argmax, when candidates are near-tied.**
- 2–3 more instances would firm the positive; this is one clean instance.

## 5. Practical takeaway for the best-of-k lever (project_exp61_bestofk_anchor)

best-of-k anchor selection can be performed **on a real low-noise device** (not only on a noiseless
classical surrogate) **when the candidate quality gaps exceed device noise** — confirmed on hardware,
test-retest stable. For near-tied candidates, rank noiselessly or carry the top-set. Magnitude of the
realized lift, however, must NOT be read off hardware (it contracts ≥ sim) — that is the F44/F50 caveat.

## 6. Reversibility / scope

Pure-additive: one script + pre-reg + 3 result JSONs + this finding. No existing experiment/finding or
live file modified. Elder anchor-selection line (Exp61→Exp73→Exp77); does not touch the IIT/Φ thread
(Whisper/Ember). QPU cost: 2 jobs × 5 circuits × 1024 shots on the open-instance (473→ still ample free).
