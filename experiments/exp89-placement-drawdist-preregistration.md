# Exp89 — Layout-draw DISTRIBUTION of the placement contribution at 208 gates (pre-registration)

**Whisper C4448 · ibm_fez · single calibration window · pre-registered before any QPU result.**
Provenance reuse (no re-derivation): fold + FIX reference from Exp87; vary-place recipe + codeword
verification from Exp86; code/circuit/grading from Exp84; same-window co-submission harness from Exp88.

## The open caveat this closes (F68's own #1 flag)

F68 (C4445) measured the placement contribution drift-free **but from a single VAR-208 layout draw**:
`placement = W(FIX 208) − W(VAR 208)` where VAR 208 = one recipe (opt1/seed31337), which read **0.99**
this window vs **0.785** in Exp86 — a **0.205 layout-draw swing** that F68 flagged as dwarfing the
0.044 cross-window drift it had just removed. F68's honest verdict: *"placement dominates gate-count,
drift-free and direction-robust; the precise share is **draw-dependent**."* It could not say whether
"placement dominates" is **draw-robust** (holds for every layout draw) or an artifact of one draw,
because **N=1** on the vary axis. This experiment measures the **distribution** over K draws.

## The intervention

One `sampler.run` → ONE window (drift removed by construction). Objects:
- **ANCHOR 158** — opt=2 seed=100 folds=0 (the shared base; identical circuit that seeds both axes).
- **FIX 208** — base folded +25 (`CZ·CZ=I`, placement HELD) — the single placement-held 208 reference.
- **VAR 208 × K=6** — K distinct transpile draws at opt=1, seeds {31337, 11, 101, 271, 1618, 9001},
  each a **different physical layout** targeting ~208 routed 2q-gates. seed=31337 is the exact Exp88
  VAR-208 draw (0.99) — included as a same-recipe reproducibility tie-back.

8 objects × {Z, X} = **16 PUBs**, 2000 shots each, one job. Per-draw **2q-gate count recorded** so
gate-count variation across VAR draws is visible and can be separated from pure layout effect.

Per-draw placement contribution: `placement_i = W(FIX 208) − W(VAR 208_i)`. The set {placement_i}
is the distribution F68 could only sample once.

## PRE-COMMITTED CLAIM BOUNDARY (both directions bank a clean result)

Let the K VAR-208 witnesses be W_i and the placement-held reference be W_FIX. Decided BEFORE results:

- **BRANCH 1 — DRAW-ROBUST DOMINANCE:** every draw has `W_i < W_FIX` (all placement_i > 0) AND the
  distribution mean placement contribution exceeds the gate-count-only contribution
  `(W(158) − W_FIX)`. → "Placement dominates gate-count is draw-ROBUST, not a lucky single draw."
  Report mean ± std of placement_i and the min/max draw.

- **BRANCH 2 — DRAW-DEPENDENT SIGN:** at least one draw has `W_i ≥ W_FIX` (placement_i ≤ 0), i.e. a
  good layout draw matches or beats the placement-held fold. → F68 qualified: "placement dominance is
  draw-dependent in SIGN for the best layouts, not merely in magnitude." Report the fraction of draws
  that reverse and the draw distribution honestly. This does NOT overturn the mean direction if the
  mean placement_i still > 0; it bounds the tail.

- **BRANCH 3 — GATE-COUNT CONFOUND EXPOSED:** if the spread in W_i is explained by the recorded 2q-count
  spread across draws (high-W draws systematically have fewer gates), then the "layout-draw variance" is
  partly gate-count variance in disguise. → Report the W_i-vs-2qcount association; attribute honestly.
  A draw landing far from 208 (e.g. |Δ2q| > 15) is reported but flagged as gate-count-contaminated for
  the matched-208 placement comparison.

## Bounds I will NOT claim (stated before results)

- ❌ Pure qubit choice — VAR draws differ in placement AND routing/depth (same confound as Exp86/88);
  the subtraction attributes the gap to **layout** (placement+routing), not qubit selection alone.
- ❌ A mechanism — the witness is a scalar; no dephasing/leakage/depolarizing attribution.
- ⚠️ FIX reaches 208 via folded `CZ·CZ=I` (may be gentler than genuine routed 2q-gates), biasing the
  measured placement share; direction unaffected, magnitude only. Same caveat as F67/F68.
- ⚠️ Shot-noise floor: 2000 shots, X-term post-selected on L1 → ~1000 eff/half; per-W std ≈ 0.03,
  each placement_i is a difference of two W's → std ≈ 0.04. A |placement_i| < ~0.08 is within ~2σ of
  zero and reported as "consistent with a tie," not a reversal.
- ⚠️ K=6 draws characterizes the distribution coarsely (std estimate ~±30%); it answers the
  **draw-robust vs single-lucky-draw** question, not a precise population variance.

## Success = a banked result on EITHER branch

The value is turning F68's N=1 "share is draw-dependent" into a measured distribution: whether
placement dominance survives every layout draw (Branch 1) or reverses for the best draws (Branch 2),
either is a genuine sharpening. Pre-committed so the grade cannot be motivated after the fact.
