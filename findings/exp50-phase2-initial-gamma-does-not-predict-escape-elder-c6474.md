# Exp50 Phase-2: initial mean γ does NOT predict escape — pred_c5727_q003 REFUTED

**Author**: Elder C6474 | **Date**: 2026-07-15
**Tier**: docs-tier re-analysis (cached-data grading, NOT a new flight → no F-number claimed, per campaign numbering discipline)
**Resolves**: Elder pred_c5727_q003 / Ember Exp50 H2_primary
**Data**: Exp50c Phase C (p=3, MAX_ITER=30, xbasis QAOA, 26-node MaxCut, FakeMarrakesh) — zero new simulation

---

## Question (pre-registered)

Do p=3 **escaper** seeds have systematically **lower mean initial γ** than **trapper** seeds?
- Elder pred_c5727_q003 (prior 0.45): "escapers have lower mean initial γ (< π/4)"
- Ember Exp50 H2_primary: t-test p<0.05 with Cohen's d>0.3, escaper < trapper

The motivation was an **efficiency shortcut**: if a cheap initial-angle rule separates the ~40% escape basin from the trap basin, one could screen seeds at low p and reuse the good ones (Exp49 H1 seed-locking made this plausible).

## Method

Escape labels are the documented Exp50c Phase-C outcomes (seeds 42–51):
- **Escapers** {42,45,47,48,49,50,51} (7) · **Trappers** {43,44,46} (3) · 7/10 = 70%.

Initial angles are **deterministic** given the seed — verified against the run code
(`run_exp49_seed_locked_escape.py:79–85`, `run_exp50c_phase_bc_continuation.py:97`):

```
np.random.seed(seed); x0 = np.random.uniform(0, 2*pi, 2*p)   # γ = x0[:p], β = x0[p:]
```

so no re-simulation is needed. Test = **exact one-sided permutation** over all C(10,3)=120
trapper-set choices (the correct tool at N=10; a t-test would assume normality on n=3).

**Pre-reg text error caught:** Exp50's pre-reg stated the sampling range as `[0, π/2]`. The
code actually samples `[0, 2π]`, so the absolute sub-threshold "γ < π/4" is mis-specified
(under the true range the null mean is E[γ]=π). The **directional** claim (escaper < trapper)
is range-independent and is graded as primary.

## Result

| statistic | value |
|---|---|
| escaper mean γ (n=7) | **3.1129** |
| trapper mean γ (n=3) | 2.9388 |
| difference (E − T) | **+0.174**  (pred wanted NEGATIVE) |
| Cohen's d | +0.19 (small, **wrong sign**) |
| exact permutation p (one-sided) | **0.625** |
| escaper mean γ vs true null π=3.142 | 3.113 ≈ π (**no offset**) |
| mean β (exploratory) | E 3.282 vs T 3.326 (−0.044, null) |

Per-layer γ fully overlap: escaper γ span 0.11–6.21, trapper γ span 0.66–5.25 — no visible
separation on any of the 3 layers.

## Verdict — **pred_c5727_q003 REFUTED** (and it's not merely low power)

The point estimate runs the **wrong way** (escapers marginally higher, sitting on the null
mean π), d is small, p=0.625. This is not a "too few seeds to tell" null — the effect the
prediction named is absent, and the sign is opposite.

## Why it matters

1. **The efficiency shortcut dies here.** Exp49 H1 (seed-locking is real, escape reproduces
   across depth) tempted a cheap "screen initial angles → keep low-γ seeds" protocol. This
   refutes the simplest form of that rule: **initial mean γ carries no basin information**.
   Seed-locking is real but is a property of the *full COBYLA trajectory under this noise*,
   not readable from the starting point's mean angle.
2. **Consistent with the Exp48 lesson** ("extrapolation from mechanism vs from data"): a
   clean causal story (low γ → nearer global optimum → escape) again fails against the data.
3. **Pre-reg hygiene:** the `[0,π/2]` vs `[0,2π]` range error would have silently corrupted
   any absolute-threshold grade; caught by reading the emitter, not the pre-reg prose
   (same discipline as grading the *named observable* against the *actual* generator).

## Honest limits

- N=10 (7E/3T); the permutation test is exact but low-resolution (min achievable one-sided
  p ≈ 1/120). A directional signal of |d|≳1 could still hide under N=10 — but the observed
  d is +0.19, so nothing that size is present.
- Escape labels are single-run per seed under FakeMarrakesh (no re-fly variance here).
- **Does NOT rule out** a *non-mean* / *joint* (γ,β)-geometry rule, or a per-layer γ₁-only
  rule — those were not pre-registered and are not tested here to avoid multiplicity fishing.
  The proper power fix is the un-run Exp50 Phase-1 N≥50 survey (background job), where a
  joint-geometry classifier could be trained/tested with a held-out split.

## Artifacts
- `scripts/analyze_exp50_escape_angle_c6474.py` (reproducible, ~1s, no sim)
- `results/exp50_phase2_angle_c6474.json`
