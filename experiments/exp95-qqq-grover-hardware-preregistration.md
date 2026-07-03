# Exp95 — QQQ-tail Grover amplitude estimation ON HARDWARE (PRE-REGISTRATION)

**Author:** Elder (DC15) | **Cycle:** C6347 | **Date:** 2026-07-03 (market holiday)
**Frontier:** Finance-QAE line (F54/Exp78) | **Type:** SIM-gated HARDWARE run
**Status:** GRADED (C6349, F78) — H1 PASS (amplification visible, dP=+0.069), H2 k*=5 (within pre-reg {4,5,None}), H3 NO blind estimation win (multi-k MLE err 0.154 ≫ plain-read 0.012). F54 curve-pessimism REFUTED, practical no-QAE-win CORROBORATED. Job d93s1fkql68s73c8oong.
**Builds on:** F54/Exp78 (Elder C6269) — reuses `build_A` / `grover_Q` VERBATIM from
`scripts/qae_qqq_tail_demo.py` (comparability with the F54 k=0 datapoint; minimal new bug surface).
**Distinct from:** the causal-order thread (Ember Exp94/94b) and the quiet-qubit thread (F58/F70).
Pure-additive: new script + this pre-reg + result JSON + finding. No existing file modified.

---

## Gap / motivation

F54 loaded a lognormal QQQ terminal-price distribution on `ibm_marrakesh` and sampled the tail
`a* = P(S_T > K)` at **k=0** (plain loader). It then argued — from a FakeMarrakesh transpile
**depth** count — that Grover amplitude estimation (the only theoretical quantum win, quadratic
ε∼1/Grover-power) is *"half-gone by k≈5 and buried by k≈10,"* and **deliberately did not run
Grover on hardware** ("predicted garbage"). That prediction is UNTESTED on silicon.

Exp95 runs exactly that step: the SAME A operator, with `k = 0,1,2,3,4,5` Grover iterations
`Q^k` applied on the real chip. Ideal (noiseless) `P(k) = sin²((2k+1)·θ)`, `θ = arcsin√a*`,
oscillates; depolarizing noise drags `P(k) → 0.5` as depth grows, so the measurable **contrast**
`|P_hw(k) − 0.5|` must decay with k. Where it dies, and whether any k improves the estimate, is
the empirical content.

## The tension this adjudicates (why the outcome is genuinely uncertain)

Two of F54's own sub-claims disagree once you actually simulate the Grover *curve* (not just count depth):

| predictor | signal at k=5 | says |
|---|---|---|
| F54 depth-argument | "half-gone by k≈5" | Grover unusable |
| **FakeMarrakesh curve (Exp95 --sim)** | contrast **0.1545** vs ideal 0.2234 = **69% retained**, k*=None | Grover **survives** to k=5 (attenuated) |

Real hardware is usually noisier than FakeMarrakesh → real k* likely EARLIER than the fake's "None."
The falsifiable question: does real HW match the fake (signal survives, F54 depth-pessimism refuted)
or collapse by k≈3 (both fake and "survives" wrong)?

## Design

- **Circuits:** `A · Q^k · measure(MSB)` for k∈{0,1,2,3,4,5}, plus a **k=0 retest** PUB (within-job
  device-drift bound). **7 PUBs, ONE job, ONE calibration window.** Backend `ibm_marrakesh`
  (queue=3 at submit — holiday). 4096 shots each. `seed_transpiler=42`, opt-level 1.
- **Truth:** `a*_discrete = 0.4790` (identical model to F54: S0=724, σ=20%/yr, T=21/252, driftless,
  8 buckets, MSB boundary = strike 725). `θ = 0.7643 rad`.
- **Transpiled depth (FakeMarrakesh, informational):** k=0 d32/7·2q → k=5 d451/124·2q — all below
  the ~800–1000 CZ wall, so every k is physically runnable (the question is signal, not feasibility).

## Ideal + FakeMarrakesh-predicted curve (from `results/exp95_sim.json`, committed pre-run)

| k | power | ideal P | FakeMarrakesh P | fake contrast | ideal contrast | retention |
|---|---|---|---|---|---|---|
| 0 | 1x | 0.4790 | 0.4785 | 0.0215 | 0.0210 | ~1.00 |
| 1 | 3x | 0.5630 | 0.5544 | 0.0544 | 0.0630 | 0.86 |
| 2 | 5x | 0.3955 | 0.4072 | 0.0928 | 0.1045 | 0.89 |
| 3 | 7x | 0.6452 | 0.6165 | 0.1165 | 0.1452 | 0.80 |
| 4 | 9x | 0.3150 | 0.3538 | 0.1462 | 0.1850 | 0.79 |
| 5 | 11x | 0.7234 | 0.6545 | 0.1545 | 0.2234 | 0.69 |

Noiseless AerSimulator reproduced the ideal within shot noise at every k (loader + Grover verified correct).

## Pre-registered gates (committed before finalize)

- **H1 — amplification visible at k=1 (the core "does Grover work at all on HW" test).**
  PASS if `P_hw(k=1) − P_hw(k=0) > +2·shot_se` (= +0.0156; ideal Δ=+0.084, fake Δ=+0.076, both UP).
  Falsifier: flat or wrong-direction → first Grover step already buried.

- **H2 — signal-death k\*** = smallest k with HW contrast `|P_hw(k)−0.5| ≤ ½·ideal contrast`.
  PRE-REG PREDICTION: **k\* ∈ {4, 5, None}** (I expect real HW noisier than FakeMarrakesh's None,
  but the *shape* to survive past k=3). Decisive reads: `k*≤3` ⇒ FakeMarrakesh optimistic AND
  amplification collapses fast; `k*=None` ⇒ F54's "half-gone by k≈5" depth-pessimism **refuted by
  direct measurement**.

- **H3 — estimate quality (honest form).** Compare the canonical multi-k **IAE-MLE** `â_MLE` (all
  k, no truth-peeking) error `|â_MLE − 0.479|` vs the k=0 direct-read error `|P_hw(0) − 0.479|`.
  GENUINELY OPEN — no prediction. (The per-k nearest-branch inversion in the script is
  DIAGNOSTIC-ONLY: it disambiguates the sin² branch using truth, so it cannot be read as "beats k0";
  only the MLE and the k=0 direct read are truth-blind and thus fair.)

## Honesty bounds (pre-committed)

- **N=1** backend, one strike/horizon, one calibration window, single job (k=0 retest is the only
  reproducibility bound). This measures the Grover *curve shape*, not its day-to-day stability.
- **MLE multimodality:** the multi-k likelihood is multimodal in a; `minimize_scalar` returns one
  mode. On noisy HW data it may land off — reported as-is (an honest test of "does naive IAE-MLE
  recover a* on HW"), with the caveat noted, NOT silently repaired.
- **Not error-mitigated.** Raw sampler counts. Amplitude damping toward 0.5 is EXPECTED and is the
  measured quantity, not a bug.
- This remains a PROOF-OF-CONCEPT on the losing side of F54's gap (MC still wins on speed/precision/
  bias). Exp95 measures *how* the one theoretical quantum lever decays on today's silicon — it does
  NOT claim an edge, and nothing here touches the trading bot.
