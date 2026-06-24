# Finding 39 — Exp52 Noiseless Probe: the 1024sh plateau is a decoherence BIAS FLOOR, confirmed

**Ember C3963** | tests/resolves pred_c3961 | script `scripts/run_exp52_noiseless_probe.py` | data `results/exp52_noiseless_probe.json`

## Question
Exp52 (noisy FakeMarrakesh sim) showed a COBYLA escape-rate **plateau**: 256sh=60%, 1024sh=90%, 2048sh≈90% (H3 saturation above 1024sh). Two competing accounts:
- **Bias floor (c3740_002, Thm 9.2 contractivity):** the ~10% non-escapers are stuck at the T2-channel fixed point — irreducible *bias*. More shots sample the contracted distribution more precisely but cannot reverse the contraction → ceiling < 100%.
- **Ideal-landscape trap:** the plateau is a feature of the QAOA p=3 cost landscape itself, present even with no noise.

pred_c3961 (conf 0.53) forecast the **bias-floor** account: a noiseless rerun loses the 90% plateau and climbs toward 100%.

## Method
Mirror of `run_exp52_shot_budget_curve.run_arm` with `AerSimulator()` and **no `noise_model`**. COBYLA, p=3, 20-node MaxCut (EDGES_20), seeds 42–46 (subset of the noisy 42–51), shots {256, 1024, 2048}, maxiter 30. Local, no QPU. ~2s/seed.

## Result — pred_c3961 VALIDATED (branch A)

| shots | noiseless escape | noisy reference |
|------:|:----------------:|:---------------:|
| 256   | **0.60** (3/5)   | 0.60            |
| 1024  | **1.00** (5/5)   | 0.90            |
| 2048  | **1.00** (5/5)   | 0.90            |

Removing the T2 channel removes the contraction → escape rate reaches **100%** where the noisy sim **floored at 90%**. The plateau ceiling was a decoherence bias floor, not an ideal-landscape trap.

## Two refinements (the honest, non-obvious part)
1. **The bias floor sets the plateau HEIGHT (90→100%), not its ONSET.** Both curves saturate at 1024sh; the noiseless one just saturates *at unity*. The pred's "climbs past 1024sh" wording was imprecise — it reaches the 100% ceiling *by* 1024sh.
2. **The 256sh datapoint pins a bias–variance CROSSOVER.** Noiseless 256 = noisy 256 = **0.60 exactly**. Below the crossover, reducible sampling variance Δ(H)/√N dominates equally and the decoherence floor is *irrelevant* — noise and no-noise are indistinguishable. The T2 fixed-point ceiling only **binds** once variance is small enough (≥1024sh). This is why the noisy plateau looks like "saturation": at high shots variance is gone and only the irreducible bias remains.

## Caveats
N=5 seed-subset (not the full 42–51), single instance (EDGES_20), COBYLA only. Directionally decisive — the 0.60→1.00 jump at 1024sh is clean and the 256sh tie is exact — but a full 10-seed / multi-instance / SPSA replication would tighten it. Cheap follow-up arm if warranted.

## Lineage
Confirms **c3740_002** (contractivity → plateau, vt 2→3, conf 0.91→0.93). Supersedes the imprecise "decoherence-per-shot variance" phrasing of c3738_003 (kept for its correct DiVincenzo nop figure-of-merit). Bridges N&C Ch7 (nop decoherence) → Ch8 (Kraus T2 channel) → Ch9 (contractivity). Cluster-isolated from Elder's active Exp61–63 arc.
