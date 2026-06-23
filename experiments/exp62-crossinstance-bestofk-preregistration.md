# Exp62 — Cross-instance best-of-k p3 anchor selection generalization

**Pre-registered:** C6102 (2026-06-23) | **Author:** Elder | **Runner:** `scripts/run_exp62_crossinstance_bestofk.py`
**Rung:** Pearl Rung-2 interventional (`do(select best of k anchors)`) replicated across instances.
**DC mirror:** DC1.5 `state/experiments/c6102-exp62-crossinstance-bestofk.json`

## The gap this closes
Finding 36 (C6084, Exp61) validated best-of-k p3 anchor selection ON EDGES_20: it RECOVERS
warm-start lift (H1 interventional SUPPORTED, paired t≈3.43, mean Dlift = **+0.049**). Its
forward section names exactly ONE open arm: *"cross-instance best-of-k remains the named future
arm."* This experiment runs it.

**Distinct from Exp60/F35 (C6061)**, which KILLED cross-instance anchor-VALUE TRANSFER (an
instance's tuned p3 anchor is instance-LOCAL — you cannot cache it and reuse it elsewhere).
Best-of-k is NOT a transfer: it draws k FRESH anchors FOR EACH instance and selects the best
EMPIRICALLY, so it *should* be instance-agnostic (a procedure, not a cached value). H1 tests
whether that prediction holds or whether the +0.049 lift is an EDGES_20 landscape artifact.

**Action it changes (EVI, C6044):** whether Finding 36's "ADOPT best-of-k p3 pre-selection"
decision is a GENERAL warm-start protocol rule or an EDGES_20-specific result.

## Design (instance-agnostic; paired; reuses Exp61 `run_seed` verbatim)
- **Instances:** `EDGES_20_ref` + 3 fresh random graphs `gen_instance(101/202/303)` (Exp57's
  generator — same family: 20 nodes / 30 edges, uniform over C(20,2)). Verified distinct:
  max_cut 26 / 26 / 25 / 26.
- **Budget (identical across all instances):** k=3, 256 shots, COBYLA maxiter 20, FakeMarrakesh
  Aer noise model. Apples-to-apples → a lift on EDGES_20 but not the new instances is
  interpretable as instance-dependence, not budget noise.
- **Per (instance, seed)** call `Exp61.run_seed` VERBATIM (no re-derivation). Paired:
  `Dlift = lift_best − lift_single = r_warm_best − r_warm_single` (r_cold cancels).
- **Seeds 42–44** per instance (3 each → 12 cells; pooled new-instance N=9). EDGES_20 42–44
  REPRODUCE the first 3 Exp61 RUN cells = regression check.

## Hypotheses (named, pre-disclosed; graded against these — no post-hoc threshold)
- **H1 (PRIMARY, generalization):** best-of-k Dlift>0 replicates OFF EDGES_20. `mean(Dlift) > 0`
  on a strict MAJORITY of the 3 new instances (≥2/3). **REFUTE** if `mean(Dlift) ≤ 0` on the
  majority of new instances ⇒ best-of-k lift is an EDGES_20 artifact, Finding 36 adoption scoped
  to EDGES_20. (Mirrors Exp57 H1 framing.)
- **H2 (magnitude):** pooled new-instance `mean(Dlift)` is the SAME ORDER as EDGES_20's Exp61
  +0.049, i.e. within [0.33×, 3×] → **[+0.016, +0.148]**. Outside band = different regime.
- **H3 (rescue structure replicates):** pooled `rho(r_p3_single, Dlift) < 0` across all 12 cells
  (worse single anchor → bigger best-of-k rescue), the H3 found on EDGES_20 (C5980 monotone-
  floor). Tests whether the rescue MECHANISM is instance-agnostic.

H2/H3 are direction/order tests at this n; |rho| bars flagged NULL-consistent per C6051
(n=9 pooled two-sided α=.05 Spearman sig crit ≈ 0.666; n=3 per-instance is direction-only).

## Scope / honesty
- PILOT fidelity (256 sh / maxiter 20), per-instance N=3 (mirrors Exp57 pilot grid). SIGN +
  rough magnitude, NOT a 1024-shot campaign.
- Same instance FAMILY (uniform random 20n/30e). Does NOT test STRUCTURED graphs
  (planted/regular) — a separate named arm (Elder C5972 structure-vs-landscape).
- Seeds retained as drawn; NO dropping (C5923; Exp57/59/61 retained seed44).
- Reuses `Exp61.run_seed` ⇒ per-cell numbers come from the SAME validated code path.

## Grading
Grade the named per-instance observable (`per_instance[*].mean_d_lift`, `d_lift_pos`) and the
three pre-disclosed verdicts H1/H2/H3 in `exp62_results.json["summary"]`. Track BOTH error
directions on H1 (generalizes vs EDGES_20-specific). Estimated completion ~11.6h from launch
(2026-06-23 19:39 UTC) ⇒ grade ~2026-06-24; grade off the checkpoint once all 3 new instances
have ≥2/3 seeds (H1 majority cannot then flip). Finding → `findings/37-*.md`, committed to quantum repo.
