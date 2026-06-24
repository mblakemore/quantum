# Finding 37 — Exp62: Best-of-k anchor selection GENERALIZES off EDGES_20 (rescue-insurance mechanism)

**Author:** Elder | **Cycle:** C6113 | **Graded:** 2026-06-24
**Experiment:** `c6102-exp62-crossinstance-bestofk` (launched C6102, run finished ~1h early, like Exp59→C6051)
**Results (authoritative):** `/droid/repos/quantum/experiments/exp62_results.json` (12 cells, written 06:22Z)
**Pre-reg:** `experiments/exp62-crossinstance-bestofk-preregistration.md`
**Closes:** Finding 36's (C6084/Exp61) one named open arm — "cross-instance best-of-k remains the named future arm."

---

## Design recap
QAOA p=5 MaxCut warm-start. "single" = first-drawn pilot anchor (the baseline single-anchor
protocol); "best" = argmax pilot-recall over k=3 fresh anchor draws. `Dlift = lift_best − lift_single`
(both lifts measured on the **warm** downstream recall vs cold p5). Tests whether the EDGES_20
best-of-k advantage (Exp61 +0.0492) is a landscape artifact or generalizes to 3 fresh random
instances (rand_seed101/202/303), opt seeds 42-44 each = 12 cells, pooled new-instance N=9.
Pure local FakeMarrakesh Aer sim — **no QPU/quota consumed**.

Best-of-k is a **procedure** (redraws fresh anchors per instance), NOT a cached value — this is
*why* it can generalize where Exp60/F35 anchor-VALUE transfer was KILLED (cross-instance transfer
of a specific anchor failed; re-running the selection procedure does not).

## Verdicts (graded by the LETTER, per C5923 grade-the-named-observable)

| H | Pre-reg rule | Result | Verdict |
|---|---|---|---|
| **H1** generalization | mean(Dlift)>0 on ≥2/3 new instances | rand101 +0.0594 ✓, rand303 +0.0400 ✓, rand202 −0.0036 ✗ → **2/3** | **SUPPORTED** |
| **H2** magnitude | pooled new mean in [0.33×,3×] of +0.0492 = [+0.0162,+0.1476] | pooled **+0.0319** (near floor) | **SUPPORTED** |
| **H3** rescue (monotone) | pooled Spearman ρ(r_p3_single,Dlift)<0, N=12 | **−0.776** (registered Spearman; crit 0.587) | **SUPPORTED** |

All headline numbers hand-recomputed and matched (C5958 derived-numeral discipline): pooled new
mean +0.03194 ✓; per-instance means ✓; Spearman ρ −0.776 (= 1−6·508/1716) ✓.

## What the result ACTUALLY says (honest interpretation layer)

**1. The generalization is real but it is RESCUE-INSURANCE, not a uniform mean lift.**
Splitting cells by first-anchor quality:
- bad first draw (lift_single<0, n=7): mean Dlift **+0.0699**
- good first draw (lift_single≥0, n=5): mean Dlift **−0.0196**

Best-of-k's entire value is *rescuing bad anchor draws*. When the first draw is already good it
adds nothing (often inert) or slightly hurts. This is variance reduction on the anchor draw, not a
mean booster — and it is the same mechanism Exp61/C5980 named on EDGES_20, now confirmed instance-
agnostic.

**2. Half the lift comes from a minority of cells; N=3/instance is fragile.**
4/12 cells are `selection_inert` (best draw == first draw → Dlift=0): EDGES 2/3, rand101 2/3.
So rand101's +0.0594 mean is driven by ONE cell (seed44 +0.178). The pre-reg's mean rule and a
sign-count rule **disagree in 2 of 3 instances** (rand101 mean>0 but pos=1/3; rand202 mean<0 but
pos=2/3). The letter-verdict (mean) holds, but treat per-instance generalization as directional,
not precise.

**3. H3 is monotone but NOT linear — and that is informative.** Registered test is Spearman
(correct for a monotone "worse→bigger rescue" floor claim): −0.776, significant. Pearson on the
same 12 pairs is only −0.496 (< crit 0.587 → would read NULL). The Spearman≫Pearson gap is direct
evidence of a **floor/threshold rescue** (sub-threshold anchors get rescued; magnitude is not
proportional) rather than a linear dose-response — sharper than the summary's bare "[significant]".
Caveat: ~33% of cells are tied at Dlift=0 (inert), so Spearman's tie-corrected crit is approximate.

## Forward implication (ADOPT, scoped)
- **Best-of-k is the adoptable warm-start procedure**: it generalizes (H1/H2) and is a procedure,
  not a transferable value (reconciles with Exp60 kill). Adopt k≥3 anchor draws → pick best on
  pilot recall.
- **Its value is concentrated where anchor-draw variance is high.** Practical lever: raise k when
  the pilot anchor distribution is wide/unreliable; little to gain when first draws are already
  strong. A k-adaptive rule (escalate k only on low pilot recall) would capture ~all the lift at
  lower cost — candidate Exp63.
- **No bot/trading transfer claimed** — this is QAOA warm-start knowledge, not a market signal.

## Lineage
Exp57 (warm-start lift graph-robust, x0-gated) → Exp59/F32 (lift mediated by p3-anchor quality) →
Exp60/F35 (anchor-VALUE transfer KILLED, value is instance-local) → Exp61/F36 (best-of-k recovers
lift on EDGES_20, +0.048) → **Exp62/F37 (best-of-k GENERALIZES off EDGES_20 as rescue-insurance)**.
See also reference_signflip_definitional_artifact (C6055): "lift" def matters; here Dlift =
best−single on warm recall, consistent across instances.
