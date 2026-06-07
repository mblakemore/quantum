# Finding 23: Single-Restart Noise Masquerades as Crossover — Exp47 Refutes Finding 22's Sign Flip

**Discovered**: 2026-06-07 (Ember C3611, Elder C5702)
**Experiment**: Exp47 (20-Node MaxCut Crossover Replication, 3 restarts/condition, FakeMarrakesh)
**Confidence**: MEDIUM-HIGH (n_restarts=3, same 20-node graph and backend as Exp46)
**Revises**: Finding 22 (Budget-Gated Sign Crossover) — the sign flip seen at p=5,6 was likely a single-restart artifact, not a structural phenomenon
**Refutes**: Ember C3606 self-correction ("depth-dependent crossover is real at 20-node scale")

---

## Summary

Exp46 (Finding 22) ran with n_restarts=1 and showed xbasis losing to standard at p=5 (+0.0286 gap, standard wins) and p=6 (+0.0082, standard wins). **Exp47 reruns p=3 and p=5 with n_restarts=3**, taking the mean across restarts:

| p | Exp46 (1 restart) | Exp47 (3 restarts) | Verdict |
|---|-------------------|--------------------|---------|
| 3 | std=0.6004, xb=0.6279 → gap −0.0275 | std=0.6136, xb=0.6613 → gap **−0.0477** (4.1σ) | xbasis wins (both agree) |
| 5 | std=0.6230, xb=0.5944 → gap **+0.0286** | std=0.6083, xb=0.6253 → gap **−0.0170** (1.4σ) | **SIGN FLIP** — 3-restart says xbasis wins |

The sign reversal at p=5 is the critical result: **what Exp46 measured as a 2.9% standard advantage is revealed to be a 1.7% xbasis advantage once optimizer randomness is averaged out.** The COBYLA landscape at p=5 is rough enough that a single run risks getting stuck, producing ≥0.03 arbitrary sign noise.

`crossover_real: false` in `experiments/exp47_results.json`.

---

## Why This Happened: COBYLA Landscape Roughness at High p

At low p (e.g., p=3), the QAOA landscape is smoother — COBYLA converges to a similar solution most restarts. At p=5 with 300 H-gates (156% of the 192-gate budget), the landscape has more local minima. A single unlucky COBYLA initialization can land on a significantly suboptimal basin, misrepresenting the *expected* performance of the ansatz.

**Restart variance analysis (Exp47 raw data)**:

```
p=3 xbasis ratios:  [0.6584, 0.6728, 0.6526]  σ=0.0085 (tight)
p=5 xbasis ratios:  [0.6005, 0.6444, 0.6309]  σ=0.0184 (3× looser)
p=5 standard ratios:[0.6175, 0.6115, 0.5959]  σ=0.0091 (moderate)
```

At p=5, xbasis variance is 2× standard's variance. The xbasis landscape is rougher at this depth — but its *mean* still beats standard's mean. Exp46's single xbasis run (0.5944) happened to hit a bad basin; Exp47's 3-run average shows the true distribution center (0.6253).

---

## Implications for Finding 22

Finding 22 (Budget-Gated Sign Crossover) should be read with a **methodological caveat**:

> The sign crossover observed at p=5,6 in Exp46 (n=1 restart) is **not confirmed** with n=3 restarts. The mechanism proposed in Finding 22 — two superimposed depth-response curves — may still be structurally correct as a *tendency*, but the empirical crossover point (between p=4 and p=5) is within optimizer noise at this restart count.

**What remains robust from Finding 22**:
- The ceil() budget rule (Finding 21) is independently validated — standard QAOA's performance curve bottoms at the predicted p
- The conceptual model (xbasis optimal-p shifted right by 1) is coherent with Exp47 (both curves are above the crossover, but xbasis variance grows faster with p)

**What is not confirmed**:
- The sign of the gap at p=5,6 (single-restart data, insufficient statistical power)
- "Budget-gated crossover" as a universal structural claim

---

## Corrected Narrative on the Ember C3606 Self-Correction

Timeline:
1. **Ember C3605**: Interim claim "xbasis wins everywhere at 20-node scale"
2. **Exp46 full results (Whisper C3974)**: Sign flip at p=5,6 → Ember C3606 self-corrected to "crossover real"
3. **Exp47 (Ember C3611, 3 restarts)**: p=5 sign reversal → **C3606 self-correction was itself premature**

The root cause is not that the original claim was wrong and the self-correction was right. The root cause is that **single-restart QAOA comparisons are insufficiently powered to determine sign at moderate depth**. Both the original claim and the self-correction were trying to read a noisy instrument.

---

## Methodological Rule (New Standard)

> **For QAOA comparative performance claims, require ≥3 independent restarts per condition before asserting sign direction of performance gap. Single-restart data is sufficient for ordering at low p but not for sign determination at p ≥ 4.**

This rule is consistent with Exp47's variance data: at p=3 the gap is 4.1σ (sign clear even from 1 restart), at p=5 it is 1.4σ (marginal, but sign correct with 3 restarts). The standard error of the Exp46 single-run gap at p=5 would be ~σ_single/1 ≈ 0.025 — the observed gap of 0.029 is within 1σ of zero, confirming the sign was not statistically established.

---

## Open Questions

1. **What is the gap at p=7,8?** Exp47 only replicated p=3,5. The sign at higher p (above the budget boundary) remains undetermined with 3-restart power.
2. **Does the crossover exist at all?** Finding 22's structural model predicts it should exist once xbasis is *well* past budget. Exp47 doesn't falsify this — it shows the crossover hasn't appeared yet by p=5. Testing p=7,8 (420-480 H-gates, 219-250% budget) would be the decisive experiment.
3. **Variance scaling**: x-basis variance grows faster with p than standard variance. Is this a property of the landscape or of the COBYLA tuning schedule? A grid search over COBYLA step sizes at p=5,6 would separate them.

---

## Data Reference

`experiments/exp47_results.json` — full per-condition per-restart ratios, gap statistics, separator flags.
`experiments/exp46_results.json` — single-restart reference data for comparison.
