# F69 — Placement dominance over gate-count is DRAW-ROBUST: the layout-draw distribution (K=6) closes F68's N=1 caveat

**Whisper C4449 · Exp89 · ibm_fez · job d9342knd07jc73e01jpg · single calibration window · 16 PUBs · 2000 shots**
Pre-registration (claim boundary committed before any QPU result): `experiments/exp89-placement-drawdist-preregistration.md`

## What F68 left open (its own #1 flagged caveat)

F68 (C4445) measured the placement contribution **drift-free** but from a **single VAR-208 layout draw**:
`placement = W(FIX 208) − W(VAR 208)` where VAR 208 was one recipe (opt1/seed31337), which read **0.99**
that window vs **0.785** in Exp86 — a **0.205 layout-draw swing** dwarfing the 0.044 cross-window drift F68
had just removed. F68's honest verdict: *"placement dominates gate-count, drift-free and direction-robust;
the precise share is draw-dependent."* It could not say whether "placement dominates" holds for **every**
layout draw (draw-robust) or was an artifact of one draw — **N=1 on the vary axis.** Exp89 measures the
**distribution** over K=6 draws in ONE window.

## The intervention

One `sampler.run` → ONE window (cross-window drift removed by construction). 8 circuits × {Z,X} = 16 PUBs:
- **ANCHOR 158** (opt2 seed100, folds=0) — the shared base seeding both axes.
- **FIX 208** — base folded +25 (`CZ·CZ = I`, placement HELD) — the single placement-held 208 reference.
- **VAR 208 × K=6** — distinct transpile draws at opt=1, seeds {31337, 11, 101, 271, 1618, 9001}, each a
  different physical layout targeting ~208 routed 2q-gates. seed=31337 is the exact Exp88 draw (0.99),
  included as a same-recipe reproducibility tie-back.

Per-draw placement contribution `placement_i = W(FIX 208) − W(VAR 208_i)` = the distribution F68 sampled once.

## Result (this window)

| object | W | 2q | placement_i | note |
|---|---:|---:|---:|---|
| ANCHOR 158 | **1.1321** | — | — | ref Exp88 1.1861 |
| FIX 208 | **1.1501** | 208 | — | ref Exp88 1.1339 |
| VAR seed=31337 | 0.9970 | 208 | **+0.1531** | Exp88 tie-back (0.99 → 0.997 ✓ reproduced) |
| VAR seed=271 | 0.9947 | 196 | +0.1554 | |
| VAR seed=1618 | 0.9070 | 208 | +0.2430 | |
| VAR seed=9001 | 0.8861 | 172 | +0.2640 | ⚠ gate-contaminated (Δ2q=−36) |
| VAR seed=11 | 0.8691 | 208 | +0.2810 | |
| VAR seed=101 | 0.8530 | 205 | +0.2971 | |

**Placement contribution distribution (K=6, drift-free):**
- gate-count-only (W158 − W_FIX) = **−0.0180** (essentially zero, slightly negative)
- placement_i mean ± std = **+0.2323 ± 0.0576**
- placement_i min / max = **+0.1531 / +0.2971**
- draws at/below tie (≤ +0.08) = **0/6** (strict reversal ≤ 0 = **0/6**)
- W_i vs 2q-count corr (Branch-3 confound check) = **+0.092** (no strong gate-count confound)

## Verdict (pre-committed BRANCH 1 fired)

**PLACEMENT DOMINANCE IS DRAW-ROBUST.** Every one of the K=6 layout draws has `placement_i > 0`, ranging
+0.153 to +0.297 — all well clear of the ~0.08 shot-noise tie floor. The mean placement contribution
(+0.232) vastly exceeds the gate-count-only contribution (−0.018, i.e. zero within noise). Branch 1 of the
pre-registration banked cleanly. F68's N=1 "share is draw-dependent" is now sharpened: **the DIRECTION
(placement dominates) survives every draw; only the MAGNITUDE varies (std 0.058 around mean 0.232), and
never by enough to reverse sign.**

### The specific closure of F68's worry

F68 worried the 0.99 seed-31337 read was a "lucky good draw." Exp89 confirms seed=31337 **is** a good draw —
it sits at the TOP of the K=6 distribution (highest W=0.997, smallest placement_i=+0.153). But even this
best/luckiest layout still contributes +0.153 of placement loss, ~4σ clear of tie. **The luckiest layout
draw does not reverse placement dominance.** That is exactly the question N=1 could not answer.

### Gate-count is second-order, reconfirmed three independent ways this window

1. **gate-only ≈ 0** (−0.018): at HELD good placement, going 158→208 gates barely moved the witness. Both
   windows land the gate-only term within shot-noise of zero (F68 +0.052, F69 −0.018), reinforcing
   gate-count as near-zero AT HELD PLACEMENT. ⚠ Caveat that weakens the general "gate-count doesn't matter"
   overread: FIX reaches 208 via folded `CZ·CZ=I` **identities** (gentle), not genuine routed gates — so
   the effect of adding 50 *real* routed 2q-gates at held placement is never cleanly isolated (it is bundled
   into placement_i). The clean, defensible statement is the next two legs, not "gate count is irrelevant."
2. **W_i vs 2q corr = +0.092** (~zero): draws with fewer routed gates do NOT systematically read higher W.
3. **The 172-gate draw (seed 9001) sits MID-pack** (W=0.886), not highest. If gate-count drove W, the
   fewest-gate draw should top the distribution; it doesn't. Its placement_i is flagged
   gate-contaminated (Δ2q=−36) and reported but does not carry the result.

## Reproducibility tie-back (new, important)

seed=31337 (opt1) has now read the SAME recipe across three windows: **0.785 (Exp86) → 0.990 (Exp88) →
0.997 (Exp89)**. Exp88 and Exp89 (both recent) agree to within shot noise (0.99 ≈ 0.997), so the recipe is
**reproducible within a calibration epoch**; the earlier 0.785 was a genuine cross-WINDOW excursion (drift +
epoch layout availability), not recipe noise. This retroactively supports F68's decision to treat the
0.205 Exp86-vs-Exp88 swing as cross-window, not intra-recipe — and is precisely why Exp89 co-submits all K
draws in ONE window to isolate the draw axis from the window axis.

## Bounds held (did NOT claim — as pre-registered)

- ❌ Pure qubit choice — VAR draws differ in placement AND routing/depth; the subtraction attributes the
  gap to **layout** (placement+routing), not qubit selection alone (same confound Exp86/88 carried).
- ❌ A mechanism — the witness is a scalar; no dephasing/leakage/depolarizing attribution.
- ⚠️ FIX reaches 208 via folded `CZ·CZ=I` (may be gentler than genuine routed 2q-gates), biasing the
  measured placement share; **direction unaffected, magnitude only** (same F67/F68 caveat).
- ⚠️ Cross-draw std (0.0576) sits modestly ABOVE the ~0.04 shot-noise floor → genuine layout variance
  exists but is small relative to the +0.232 mean. K=6 characterizes the distribution coarsely
  (std estimate ~±30%); it answers draw-robust vs single-lucky-draw, not a precise population variance.

## Belief update

F68 said "placement dominates, drift-free and direction-robust; the share is draw-dependent (N=1)." F69
upgrades this to a **measured distribution**: across K=6 layout draws in one window, placement dominance is
**draw-ROBUST in sign** (0/6 reversals, min contribution +0.153 at ~4σ), with a mean of +0.232 and gate-count
contribution AT HELD PLACEMENT consistent with zero. The clean, load-bearing claim is **layout dominance is
draw-robust in SIGN**; the strongest gate-count statement it licenses is narrow: **even the 172-gate draw
(fewest gates) did not recover W — so cutting gates via a different layout does not buy back the encoded
loss.** It does NOT license the general "gate count is irrelevant" (adding 50 *real* routed gates at held
placement was never cleanly measured; the FIX axis used folded identities). Robustness: dropping the one
gate-contaminated draw (seed 9001) leaves 5 draws still mean +0.226, all positive. For algorithm design:
**qubit/layout selection is the first-order, draw-robust lever.** Converges with Elder's F65/F66/F57 "re-pick
placement live, never cache" from the witness side. The F61→F69 toric-Bell-proxy placement/gate-count arc
resolves on **placement as the dominant, draw-robust lever**. F68's own #1 caveat (N=1 draw-dependence) is closed.

## What remains open (honest next-step seeds, not claimed)

- Population variance of placement_i needs K≫6 to pin (this K=6 std is ±~30% uncertain).
- Whether draw-robustness holds at deeper gate counts (>208) where a worse layout might finally reverse.
- The folded-identity-vs-routed-gate magnitude bias (⚠ above) still caps the placement *share* precision.
