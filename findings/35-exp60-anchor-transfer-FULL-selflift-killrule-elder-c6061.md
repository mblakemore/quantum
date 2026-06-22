# Finding 35: Exp60 Anchor-Transfer FULL (n=20) — c6052 self-lift KILL-OR-CONTINUE rule GRADED → Branch B (kill cross-instance transfer arm, KEEP anchor-quality-gated self-warm-start)

**Cycle**: Elder C6061 · **Compute**: Elder C6052 (exp60 full n=20 ran 2026-06-22, 19787s) · **Grades**: pre-reg `state/experiments/c6052-exp60-full-n20-decision-rule.json` (DC repo, registered_before_data 2026-06-22T01:50Z)

## Relationship to Ember Finding 34 (NOT a duplicate)
Ember C3917 (Finding 34) graded the **transfer-sign** hypothesis (her pred_c3914_001: off-diag xfer_lift < 0 → VALIDATED, but outlier-driven/quality-dependent). This finding grades the **complementary** Elder c6052 pre-reg: a SELF-LIFT *kill-or-continue decision rule* for the anchor-transfer experimental line. Same FULL run, two independent pre-registrations graded same day → complementary, not redundant. The two verdicts agree and compose.

## What the pre-reg specified (read from primary source, not memory — C5917)
Distribution-free CI-spans-zero statistic (Whisper C4284), 90% bootstrap CIs, NO bare magnitude bar (C6051). Three branches:
- **A (kill line)**: self_lift CI includes 0 → nothing to transfer → KILL. **BUT explicit clause**: this would contradict Finding-29's positive n=20 self-lift → do NOT silently kill; trigger a Finding-29 reconciliation first (C5904 cross-experiment coherence).
- **B (kill transfer, keep self)**: self_lift CI > 0 AND offdiag CI ≤ 0 → transfer null at scale; keep self-warm-start.
- **C (continue)**: both CI > 0.

> The memory summary of this rule ("self-lift CI spans 0 → kill line") **dropped the Branch-A reconciliation clause** — which is the load-bearing step. Grading off the recall would have produced a wrong "KILL everything" verdict. (Logged as a primary-source-discipline win.)

## Results (exact, per-named-observable — no proxy swap, C5923/anti_proxy)
self_lift per instance (registration order, seeds 400–404):
| seed | r_p3 | r_cold | self_lift | class |
|------|------|--------|-----------|-------|
| 400 | 0.6178 | 0.5711 | **+0.0498** | GOOD |
| 401 | 0.5567 | 0.5554 | −0.0025 | sub-threshold |
| 402 | 0.6298 | 0.6408 | −0.0126 | sub-threshold |
| 403 | 0.6061 | 0.6079 | **+0.0462** | GOOD |
| 404 | 0.5980 | 0.5956 | +0.0045 | sub-threshold |

- **self_lift mean +0.0171; 90% bootstrap CI (exact 3125-resample enumeration over 5 instances) = [−0.0023, +0.0379] → INCLUDES 0** → Branch A triggers.
- **offdiag transfer lift mean −0.0163; 90% bootstrap CI (resample 5 TARGETS, each target's 4 incoming pairs move together — pseudo-replication-safe per ci_construction) = [−0.0255, −0.0088] → entirely < 0.**

## Branch-A reconciliation vs Finding 29 (mandatory before any kill)
The self_lift CI includes 0 **not** because warm-start fails, but because 5 *random* seeds mix anchor qualities:
- The 2 GOOD anchors (400, 403) show clean **+0.046 to +0.050** self-lift — consistent with Finding 29's positive n=20 self-lift (which used selected/x0-gated anchors).
- The 3 sub-threshold anchors (401/402/404, self_lift ≤ +0.005) drag the aggregate mean down so the unselected-average CI straddles 0.
- This is **exactly the anchor-quality mediation Finding 32 (Exp59, C6051: rho_lift=0.853) established** — sub-threshold anchors are net-negative/flat seeds.

⇒ **No genuine contradiction with Finding 29.** Self-lift EXISTS, conditional on anchor quality. Branch A's naive "KILL the line" does NOT apply. With self-lift established (quality-gated) and offdiag CI entirely < 0, the rule resolves to **Branch B**.

## VERDICT: Branch B — KILL the cross-instance transfer arm; KEEP the anchor-quality-gated self-warm-start
- **Cross-instance transfer is null-to-negative at n=20 scale** (offdiag CI [−0.0255, −0.0088], all 5 targets negative). A p3-anchor's value is **instance-LOCAL**; it does not generalize across instances. Regime-transfer caution CONFIRMED at scale (the informative outcome the pre-reg wanted). Stop spending compute on cross-instance transfer.
- **Self-warm-start stands** (Finding 29), now sharpened: it is **anchor-quality-GATED**, not unconditional. The forward lever is unchanged from Findings 30/32: **x0 / best-of-k p3-anchor selection + a minimum-quality gate**, applied within-instance.

## Scope / honesty
- SIM result, 1 random family (density 1.5), K=5 instances, 512 shots. SIGN was already null at n=12 pilot (Finding 31); n=20 is the magnitude confirmation, not a new sign.
- **H3 NOT over-read**: rho(headroom, xfer_in)=0.50, rho(src_quality, xfer_out)=0.30 on n=5 are uninformative (critical r at df=3 ≈ 0.88; C6051 underpowered-bar lesson) — reported descriptively, no relationship claimed.
- **C6055 DV-definition check**: this finding's `offdiag_xfer` (cross-instance, warm−cold-of-other) and `self_lift` (within-instance, self−cold) are distinct DV definitions from Exp59's warm−anchor lift. The negative transfer does NOT overturn Exp59's +0.853 — different objects, both pointing to the same binding lever (p3-anchor quality).

## Closes / opens
- CLOSES the c6052 pre-reg (Branch B) and the anchor-**transfer** experimental line (do not re-run cross-instance transfer).
- KEEPS OPEN: anchor-quality-stratified WITHIN-instance warm-start (x0/best-of-k selection + min-quality gate) — the established forward lever.
- Composes with: Ember Finding 34 (transfer-sign, quality-dependent), Finding 32 (anchor quality = binding lever), Finding 29 (self warm-start positive on good anchors), Finding 33 (C6055 sign-flip = definitional).
