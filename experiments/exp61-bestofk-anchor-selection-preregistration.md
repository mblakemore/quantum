# Exp61 — Best-of-k p3 anchor selection: does ACTIVELY selecting the best anchor recover warm-start lift?

**Author**: Elder · **Cycle**: C6065 · **Date**: 2026-06-22
**Program**: warm-start (Exp48–60, Findings 23–35)
**Runner**: `scripts/run_exp61_bestofk_anchor.py`
**Pre-reg mirror**: DC1.5 `state/experiments/c6065-exp61-bestofk-anchor-selection.json`

## The gap (why this is the next arm, not a re-measurement)
The whole warm-start program now converges on ONE un-tested rule. Findings 29/30/32/33/35:
- **F29 (Exp57, C6011)**: warm-start lift is x0-GATED (opt-seed ~69.7% of variance, graph 8.4%).
- **F32 (Exp59, C6051)**: that gating is **mediated by p3-anchor quality** — observationally,
  `ρ(r_p3_base, lift) = +0.853`; and H3 was NULL (no cheap a-priori x0 stat predicts anchor
  quality → selection must be **empirical best-of-k p3 multi-start**, not an a-priori filter).
- **F35 (Exp60, C6061)**: "Forward lever unchanged = x0/best-of-k anchor select."

Every finding *recommends* best-of-k anchor selection. **None has run it.** Exp59 is
**observational** (Pearl Rung-1): it watched lift vary with naturally-drawn anchor quality.
The actionable rule requires a **Rung-2 interventional** test: when we **do(select the best of k
p3 anchors)** and warm-start p5 from it, does the warm-start lift actually RISE — or does the
p5 COBYLA re-optimization re-converge to the same basin regardless of the anchor, washing out
the advantage and making selection cosmetic?

**The action this changes (stated up-front, EVI gate per C6044):** whether the warm-start
protocol ADOPTS best-of-k p3 pre-selection (and at what k), vs keeps single-anchor warm-start.
A REFUTE here closes the lever the program has pointed at for 5 findings → stop building it.

## Design (paired; controls cold-luck; built-in Exp59 regression check)
Instance = **EDGES_20** (every prior escape/warm-start finding lives here). k = **3** anchors,
N = **8** seeds (42–49). Right-sized vs Exp59's REAL ~10.9h/seed (C6035 lesson — Exp61 has more
opts/seed: 1 cold_p5 + k p3 + ≤2 warm_p5; k=3/N=8 keeps the campaign near Exp59's footprint).
Per opt-seed (`np.random.seed(seed)` — draw order chosen so k=1 reproduces Exp59 EXACTLY):
1. `x0_cold` = uniform(0,2π,10) → COBYLA p=5 → `r_cold`   *(identical draw to Exp59)*
2. anchors j=0..k-1: `x0_p3_j` = uniform(0,2π,6) → COBYLA p=3 → `(r3_j, x3_j)`
   *(j=0 reproduces Exp59's single x0_p3 → r_p3_base — REGRESSION CHECK)*
3. `single` = anchor 0 ; `best` = argmax_j r3_j
4. `warm_single` = pad(x3_single)→p5→COBYLA → `r_warm_single`  *(reproduces Exp59 r_warm_p5)*
5. `warm_best`   = pad(x3_best)→p5→COBYLA   → `r_warm_best`
6. `lift_single = r_warm_single − r_cold` ; `lift_best = r_warm_best − r_cold`
7. `Δlift = lift_best − lift_single` (paired; same r_cold cancels → Δlift = r_warm_best − r_warm_single)

Seeds 42–53 (N=12), so seeds 42/43/44 cross-check the Exp57 pilot AND seeds 42–53's k=1 leg
must match Exp59 within optimizer noise (regression assertion logged, not graded).
Fidelity = pilot (256 shots, maxiter 20, FakeMarrakesh) — matches Exp59 so results compose.

## Hypotheses (named observables, pre-disclosed — graded against these, no post-hoc threshold)
- **H1 (PRIMARY — best-of-k recovers lift; INTERVENTIONAL):**
  `mean(lift_best) > mean(lift_single)` **AND** `mean(Δlift) > 0` with **≥ 60% of trials Δlift > 0**
  (vote_need = ceil(0.6·N) = **5/8** at N=8).
  **REFUTE** if `mean(lift_best) ≤ mean(lift_single)` → p5 re-opt washes out the anchor advantage,
  selection is cosmetic, the lever is dead.
- **H2 (MECHANISM — anchor advantage survives the p5 re-opt):**
  `ρ(Δr_p3, Δr_warm) > +0.30` where `Δr_p3 = r_p3_best − r_p3_single ≥ 0` (by construction) and
  `Δr_warm = r_warm_best − r_warm_single`. Pre-disclosed POSITIVE. If `ρ ≤ 0`, the optimizer
  erases the anchor gain (better anchor ≠ better warm) → selection is cosmetic even if H1 squeaks.
  Report #trials where best==single (Δr_p3=0, selection inert — these are the "already-good-anchor"
  trials and must not be read as failures).
- **H3 (RESCUE STRUCTURE — value concentrates on bad single anchors; makes "gate min quality" real):**
  `ρ(r_p3_single, Δlift) < 0` — the WORSE the single anchor, the BIGGER the best-of-k rescue.
  Pre-disclosed NEGATIVE (monotone-floor inheritance, C5980). This is the actionable shape:
  if true, best-of-k earns its cost mainly when the first anchor is poor → conditional rule.
- **H4 (COST — reported, NOT thresholded; anti "free-lift" framing):**
  best-of-k costs `(k−1)` extra p3 optimizations/trial. Report `mean(Δlift)` against the budget:
  p3_depth vs p5_depth, p3-evals = k×maxiter, and **lift-gain-per-extra-p3-eval**. Informs the
  adopted k (a positive-but-tiny gain → "use k=2", not k=4). Honesty guard: do NOT call the lift
  "free"; it is bought with k× anchor compute.

## Scope / honesty
- PILOT fidelity (256 sh / maxiter 20). Establishes SIGN + rough magnitude of the intervention,
  not a definitive 1024-shot campaign. N=12 trials × k=4 is a real distribution but small;
  Spearman on N=12 reported WITH its caveat (n=12 sig crit |ρ|≈0.587 two-sided α=.05 per
  reference_prereg_magnitude_bar_underpowered C6051) — the +0.30 bars are SIGN/direction tests,
  not significance claims; a NULL-consistent ρ between 0.30 and 0.587 is flagged as such.
- Paired design (same r_cold per trial) controls the cold-luck path Exp59 had to decompose.
- Seeds retained as drawn; **no dropping inconvenient seeds** (C5923 flattering-result discipline;
  Exp57/Exp59 both retained seed44).
- Selection (best-of-k) mechanically makes r_p3_best ≥ r_p3_single → H1 is NOT a tautology: the
  open question is whether that anchor advantage SURVIVES the p5 re-optimization (H2). If p5
  re-converges basin-independently, H1 REFUTES despite better anchors.
- Single instance by design (graph share 8.4%, C6011-settled). Cross-instance best-of-k = future arm.

## Grading
Read `experiments/exp61_results.json` `summary`; grade H1/H2/H3 against the named observables;
report H4 cost; write Finding 36. Est completion: ~12 trials × (1 cold_p5 + 4 p3 + 2 warm_p5);
p3 cheaper than p5 so ≈ 1.6–1.9× the Exp59 ~13h → run in background, reniced.
