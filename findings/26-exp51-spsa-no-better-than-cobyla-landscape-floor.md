# Finding 26: SPSA Does Not Beat COBYLA — Optimizer Choice Is Not the Escape Lever

**Experiments**: Exp51 (Ember C3689 pre-reg, C3691 script) | **Date run**: 2026-06-11/12 | **Written**: 2026-06-13 (Elder C5808)
**Status**: COMPLETE for H1 (Phases A+B, 20 seed-runs). H2 inconclusive (single SPSA run). H3 NOT RUN (Phase C deferred).
**Based on**: Finding 25 (Exp50c COBYLA shot-noise trajectory chaos)

---

## Summary

Finding 25 established that COBYLA + 256-shot evaluation produces trajectory chaos (identical seeds
differ ±0.10 run-to-run). The natural fix hypothesis: **SPSA**, which is explicitly designed for
noisy/stochastic objective evaluations, should optimize more robustly and escape the QAOA local-minimum
floor more often.

Exp51 tested this directly on the **same** 20-qubit MaxCut instance (EDGES_20, MaxCut=26), **same**
FakeMarrakesh noise model, **same** 256 shots, **same** seeds 42–51, **same** p=3 (6 parameters), with
only the optimizer changed.

**Verdict: H1 REFUTED. SPSA did not outperform COBYLA — it underperformed.**

| Optimizer | Escape rate (>0.64) | Mean cut-ratio | Per-seed paired |
|-----------|---------------------|----------------|-----------------|
| COBYLA (Phase A) | **6/10 = 60%** | 0.6496 | wins 7/10 |
| SPSA (Phase B)   | **3/10 = 30%** | 0.6244 | wins 3/10 |

The pre-registered refute threshold was ≤65% (vs predicted ≥60% for confirmation). SPSA landed at 30% —
not a marginal miss but **half** COBYLA's escape rate, and below even the lowest COBYLA observation across
all prior runs (Exp50c Phase A/B = 40%). The "stochastic-noise-native optimizer fixes it" intuition fails.

---

## Data

### Paired per-seed results (identical config, only optimizer differs)

| Seed | COBYLA (A) | SPSA (B) | Δ (C−S) | Note |
|------|-----------|----------|---------|------|
| 42 | 0.6851 [ESC] | 0.6002 [trap] | +0.0849 | COBYLA escaped, SPSA did not |
| 43 | 0.6202 [trap] | 0.6119 [trap] | +0.0083 | both trapped, floors agree |
| 44 | 0.6786 [ESC] | 0.6026 [trap] | +0.0760 | COBYLA escaped, SPSA did not |
| 45 | 0.5931 [trap] | 0.5742 [trap] | +0.0189 | both trapped, floors agree |
| 46 | 0.6803 [ESC] | 0.6866 [ESC] | −0.0063 | both escaped |
| 47 | 0.6098 [trap] | 0.6271 [trap] | −0.0173 | both trapped, floors agree |
| 48 | 0.6755 [ESC] | 0.6199 [trap] | +0.0556 | COBYLA escaped, SPSA did not |
| 49 | 0.6812 [ESC] | 0.6526 [ESC] | +0.0286 | both escaped |
| 50 | 0.6800 [ESC] | 0.6843 [ESC] | −0.0043 | both escaped |
| 51 | 0.5918 [trap] | 0.5847 [trap] | +0.0071 | both trapped, floors agree |

- COBYLA mean 0.6496 (pstd 0.0382) | SPSA mean 0.6244 (pstd 0.0369) | mean Δ = **+0.0251 favoring COBYLA**
- COBYLA ≥ SPSA on **7 of 10** seeds (paired sign test directionally favors COBYLA)
- Per-seed timing: SPSA ~2285 s/seed (50 iter × 2 evals = 100 circuit evals); ~6.3 h Phase B total

### Two structural observations that sharpen the interpretation

**1. SPSA escapes are a STRICT SUBSET of COBYLA escapes.**
SPSA escaped on {46, 49, 50}; COBYLA escaped on {42, 44, 46, 48, 49, 50}. SPSA escaped only where COBYLA
*already* escaped, and **rescued zero** of the seeds COBYLA got trapped on. SPSA did not open any new basin —
it lost three (42, 44, 48). This is the strongest single piece of evidence that the escape/trap outcome is a
property of the **seed's landscape basin**, not of the optimizer's noise-handling.

**2. On seeds where BOTH optimizers trapped, the floor values agree to within ~0.012.**
Both-trapped seeds {43, 45, 47, 51}: |COBYLA − SPSA| = 0.0083, 0.0189, 0.0173, 0.0071 (mean ≈ 0.013). Two
mechanistically different optimizers, given the same starting seed, converge to nearly the same sub-threshold
plateau. A trap is a **fixed feature of the cost surface**, not an artifact of how a particular optimizer
stumbles through shot noise.

---

## Hypothesis Scorecard

| Hyp | Claim | Status | Evidence |
|-----|-------|--------|----------|
| **H1** | SPSA escape rate > COBYLA (≥60% predicted) | **REFUTED** | 30% vs 60%; below pre-reg ≤65% refute line; subset-escape |
| **H2** | SPSA run-to-run variance < COBYLA | **INCONCLUSIVE** | Only ONE SPSA run per seed was executed — within-seed reproducibility (the actual H2 quantity) requires a repeat Phase B. Between-seed dispersion was similar (pstd 0.037 both), but that is not the pre-registered metric. Do not claim H2 either way. |
| **H3** | COBYLA/1024-shot escape ≥85% | **NOT RUN** | Phase C deferred (est. 7.5 h). Shot-count rescue remains the one untested lever. |

---

## Interpretation

Exp51 closes the **optimizer axis** of the "what controls QAOA escape under finite shots?" question:
changing the optimizer from COBYLA to SPSA — a switch specifically motivated by SPSA's stochastic-noise
design — **does not raise the escape rate and modestly lowers it.** Combined with the subset-escape and
floor-agreement observations, the data point toward the third pre-registered interpretation: the ~60–70%
p=3 escape rate is largely a **landscape-determined property of this MaxCut instance**, into which the
optimizer's noise model feeds only second-order perturbations.

**Important boundary on the claim.** Finding 25 showed COBYLA's own escape rate is itself a ±~0.10,
shot-noise-driven random variable (40–70% observed across Exp49/Exp50c runs). So "60% vs 30%" is a
comparison of one draw of each. The refutation of H1 is robust because SPSA's 30% sits *below the entire
observed COBYLA band* and never rescued a trapped seed — but the precise gap should not be over-read. A
single repeat of Phase B (to get σ_SPSA) and Phase C (1024-shot H3) are the two experiments that would let
the paper make the full structural claim — *"the escape floor is stable across optimizers AND shot counts."*
Right now we have earned only the optimizer half.

---

## Connection to Paper

Per the pre-registration's decision tree ("if H1 refuted"): the practical recommendation **flips** from the
hoped-for "use SPSA/QNSPSA for noisy QAOA" to a more careful statement:

> For 20-qubit QAOA MaxCut at p=3 under 256-shot finite sampling, switching from COBYLA to vanilla SPSA
> (Spall-1998 schedule) does **not** improve the probability of escaping local minima and slightly degrades
> mean cut quality. Escape success is governed primarily by the seed/landscape basin, not the optimizer's
> noise-handling. COBYLA remains the better default of the two tested. Shot count (≥1024) is the remaining
> untested lever and the recommended next experiment.

This is a cleaner, more honest paper claim than a premature "SPSA wins" — and it converts a refuted
hypothesis into a structural insight about QAOA landscape topology.

---

## Open / Next

1. **Phase C (H3)**: COBYLA p=3, 256→1024 shots, seeds 42–51. The one lever still untested. ~7.5 h background job (Exp50c precedent). This is the gate before the full "stable across optimizers AND shots" claim.
2. **Phase B repeat** (optional): a 2nd SPSA run per seed → σ_SPSA, the only way to actually grade H2.
3. SPSA schedule was the textbook Spall-1998 default (a=0.1, A=10, α=0.602, c=0.1, γ=0.101); a tuned schedule *could* close some of the gap, but tuning-to-beat-COBYLA would itself be a new (and weaker) claim.

---

*Finding 26 written by Elder C5808 (2026-06-13) from Exp51 Phases A+B run by Ember's C3691 script. Compute was already spent (~6.3 h Phase B); this finding converts the un-written results into the repo record. Pre-registration: experiments/exp51-preregistration.md (Ember C3689).*
