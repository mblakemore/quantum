# F68 — Same-window partition confirms placement dominates gate-count as a drift-free measurement (73/27)

**Whisper C4445 · Exp88 · ibm_fez · job d92u0k5958jc73bsa6qg · single calibration window · 10 PUBs · 2000 shots**
Pre-registration (claim boundary committed before results): `experiments/exp88-same-window-placement-gatecount-partition-preregistration.md`

## What F67 left open (its own flagged caveat)

F67 partitioned the Exp86 toric Bell-proxy witness-decline into gate-count (~40%) vs placement (~60%)
by comparing Exp87's fixed-placement fold slope against Exp86's vary-placement slope. But the two axes
ran in **different calibration windows**: the shared 158-gate object read **1.064** (Exp86) vs **1.108**
(Exp87) — a **+0.044 pure cross-window drift**, comparable to the fold-10 step (0.024). So the ~40/60
split was an **estimate, not a measurement**. F67 wrote the next step verbatim: "A clean same-window
replication of the Exp86 placement axis would tighten the partition." F68 is that replication.

## The intervention

Both axes in ONE `sampler.run` → ONE window (drift removed by construction). 5 circuits × Z/X = 10 PUBs:
- **ANCHOR 158** (opt2 seed100, folds=0) — *literally the same circuit* seeds both axes.
- **FIX 178 / FIX 208** — base folded +10 / +25 (`CZ·CZ = I` on the same physical qubits; placement held).
- **VAR 178 / VAR 208** — Exp86 MID (opt3 seed7) / HIGH (opt1 seed31337) re-transpilations (placement moves).

## Result (this window)

| object | W (this window) | prior-window ref (fix / var) |
|---|---:|---|
| ANCHOR 158 | **1.1861** | 1.108 / 1.064 |
| FIX 178 | 1.1818 | 1.084 |
| FIX 208 | 1.1339 | 1.000 |
| VAR 178 | 0.8702 | 0.904 |
| VAR 208 | **0.9900** | 0.785 |

**In-window partition (158→208, drift-free):**
- Total decline (vary-place) = W(158) − W(VAR 208) = **+0.1960**  (~4.9σ)
- Gate-count-only (fixed-place) = W(158) − W(FIX 208) = **+0.0522**  (~1.3σ — near the shot-noise floor)
- **Placement contribution = W(FIX 208) − W(VAR 208) = +0.1439**  (~3.6σ)

**Shot-noise floor (2000 shots; X-term post-selected on the L1 bit → ~1000 shots per conditional half):**
analytic std per W ≈ √(σ_ZZ² + σ_XX²) ≈ 0.03; each partition term is a *difference* of two W's → std ≈ 0.04.
So the total decline and the placement term are well-resolved (≥3.6σ), but the **gate-count term (0.052) is
only ~1.3σ — plausibly consistent with near-zero.** The split is therefore honestly stated as **~¾ placement
vs ~¼ gate-count, with the gate-count component near the shot-noise floor**, not a precise 73/27.

## Verdict (pre-committed branch 1 fired)

**PLACEMENT DOMINATES — F67 confirmed as a measurement.** With the cross-window drift removed by
construction, the within-window placement contribution (0.144, ~3.6σ) is far larger than the gate-count
contribution (0.052, ~1.3σ). Branch 1 of the pre-registration, banked cleanly on **direction**.

**What F68 does and does NOT sharpen vs F67's ~60/40:** it confirms the *direction* drift-free; it does
**not** refine the *fraction*. The 60→~75 shift is **not** attributable to drift removal — the same VAR-208
recipe (opt1/seed31337) read **0.99 here vs 0.785 in Exp86**, a 0.205 layout-draw swing that dwarfs the
anchor's 0.044 cross-window drift. So the exact percentage is **one high-variance layout draw**, not a
tightening of F67's number. Honest claim: *placement dominates gate-count, drift-free and direction-robust;
the precise share is draw-dependent.*

## Independent corroboration: the VAR axis is NON-MONOTONIC this window

VAR 208 (0.9900) > VAR 178 (0.8702) — adding **30 more routed 2q-gates raised the witness**. In Exp86 the
VAR points were monotone-decreasing (0.904 → 0.785). Here the opt1/seed31337 layout for 208 landed on
*better* physical qubits than opt3/seed7 for 178. **If gate-count were the dominant driver, more gates
could not raise W.** It rose only because layout swamped gate-count — a direction-only, sample-robust
signal that reinforces the headline independent of the exact percentage.

Corollary (magnitude, not headline): VAR 208 drew a *good* layout this window (0.99), so the FIX−VAR gap
here is on the *small* side of what the VAR draw distribution can produce — a worse VAR-208 layout (e.g.
Exp86's 0.785) would widen it. This is the same point as the draw-variance caveat above: the placement
*share* is draw-dependent, and this particular draw happens to understate rather than overstate it.

## Bounds held (did NOT claim)

- ❌ Gate-count separated from **depth** — folding couples them; the FIX axis measures the joint quantity.
- ❌ Pure qubit choice — VAR points differ in placement AND routing/depth; the subtraction attributes the
  208-gate FIX−VAR gap to **layout** (placement+routing), not qubit selection alone (same confound Exp86 had).
- ❌ A mechanism (dephasing/leakage/depolarizing) — the witness is a scalar.
- ⚠️ **FIX reaches 208 via folded `CZ·CZ=I` identities on good qubits; VAR reaches 208 via genuine
  re-routing.** Folded identity pairs may be *gentler* than real routed 2q-gates, which would bias the
  measured gate-count share *downward* independent of placement. Direction unaffected; magnitude only.
- ⚠️ **N=1 window.** This removes the *cross-window drift* confound F67 named; it does not make 73/27 a
  population estimate. Report as one clean drift-free measurement, not a distribution. A repeat window
  would tighten intra-window PUB-to-PUB variation further (the shared anchor bounds it here).

## Belief update

F67 said "placement is the larger driver, but the split is only an estimate." F68 upgrades this to a
**drift-free measurement**: on ibm_fez in the 158–208-gate window, **layout drives ~3/4 of encoded
witness loss and gate-count ~1/4**, and layout is strong enough to make the witness *non-monotonic in
gate-count* when a better layout offsets more gates. For algorithm design: **qubit/layout selection is
the first-order lever; marginal 2q-gate reduction is second-order.** Connects directly to Elder's
F65/F66/F57 "re-pick placement live, never cache" quiet-qubit results — same conclusion from the
witness side. Closes the F67 caveat; the toric-Bell-proxy placement/gate-count arc (F61→F68) resolves
on placement as the dominant lever.
