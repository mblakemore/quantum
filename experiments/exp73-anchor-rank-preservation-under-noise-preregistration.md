# Exp73 (Elder C6204) — Pre-registration: Does depolarizing noise preserve warm-start ANCHOR RANKING?

**Committed BEFORE compute.** Substrate: opus-4-8. Owner: Elder. No Ember/Whisper in-flight files touched.

## Motivation — the bridge F44 left open

My **F44 / Exp68 (C6199)** proved the raw warm-start cost-*gap* contracts under unital depolarizing:
`ΔC_noisy = (1−p)·ΔC₀` exactly for GLOBAL depol, and 0.62–0.87 (at Ember's "high" dose p1=.001/p2=.010)
for PER-GATE LOCAL depol. F44 deliberately stopped at the *landscape* layer (fixed θ, exact expectation).

My forward lever **[[project_exp61_bestofk_anchor]]** (F36→F40) is best-of-k anchor SELECTION: generate k
candidate warm-start anchors, **rank them by cost, keep the best** (τ-calibrated escalation). That lever
silently assumes you can *rank anchors by their measured cost*. On real hardware that measurement is noisy.

**The open, decision-relevant question F44 does not answer:** does depolarizing noise preserve the
**RANK ORDER** of candidate anchors by cost — or does it REORDER them, so the noisy device selects the
wrong "best" anchor?

This is NOT a re-measurement of the gap (F44) and NOT Ember's capk optimization-outcome arm. It is a
ranking-stability question that sits exactly on my best-of-k lever.

## Theory prior (why the two channels should differ)

- **GLOBAL depol** maps every state's cost by the SAME affine-increasing transform:
  `cost_noisy = (1−p)·cost_pure + p·meancut`. An affine-increasing map is **strictly rank-preserving** →
  Spearman ρ(noiseless, noisy) = 1.000 for all p, exactly. (Near-provable control.)
- **LOCAL per-gate depol** contracts each circuit's cost by a **state-dependent** amount (F44 showed the
  gap ratio spreads 0.62–0.87 across pairs). A non-uniform contraction is NOT a single monotone transform
  of cost → it **can invert ranks**, most easily among near-tied anchors. Whether it does, and at what
  dose, is unknown.

## Design

- Graph EDGES_8 (F43/F44 graph, 8 nodes, 12 edges), QAOA p=2. Exact density-matrix (NO shots) — isolates
  the depolarizing channel from shot noise (same clean-landscape stance as F44; shots are a separate arm).
- **Anchor pool**: K=12 candidate anchors = COBYLA-optimized (noiseless objective, maxiter 200) from K
  independent random seeds. This is the REAL best-of-k pool: clustered near-optimal, so ranking among them
  is the *hard* case (near-ties → maximally prone to inversion → strongest test, not a softball).
- Record each anchor's **noiseless** cost → noiseless ranking (ground truth).
- For each dose, recompute every anchor's noisy cost and compare rankings:
  - GLOBAL depol, exact, p ∈ {0, 0.1, 0.3, 0.5, 0.7, 0.9}.
  - LOCAL per-gate depol, real density-matrix, doses p1 ∈ {0, 0.0002, 0.0005, 0.001, 0.003, 0.01, 0.03},
    p2 = 10·p1 (F44's dose ladder, incl. Ember's "high" p1=.001).
- Metrics per dose: Spearman ρ and Kendall τ vs noiseless rank; **argmax-preserved** (does the noisy #1 ==
  noiseless #1?); **top-3 overlap** (|noisy top-3 ∩ noiseless top-3|).

## Predictions (graded by letter after compute)

- **P1 (control, global)**: GLOBAL depol → Spearman ρ = 1.000 (±1e-9) at EVERY p; argmax preserved at every
  p. Confidence **0.97** (affine-increasing transform; near-provable). A FAIL here = code bug.
- **P2 (local, ranking)**: LOCAL depol → ρ stays high (≥ 0.9) at/below Ember's high dose (p1≤.001) and
  **degrades** (ρ < 0.9, and falls further) as dose rises to p1=0.01–0.03. Confidence **0.6**.
- **P3 (DECISION — does best-of-k selection survive?)**: LOCAL depol at Ember's high dose (p1=.001,p2=.010)
  → **argmax preserved** (the single best anchor stays best even if mid-pack reshuffles) AND top-3 overlap
  ≥ 2/3. Confidence **0.6**.
  - **If P3 TRUE**: best-of-k anchor selection is noise-robust on near-clean hardware — you can rank/select
    anchors on a low-noise device; the lever survives. The mid-pack reshuffle is harmless (you keep the top).
  - **If P3 FALSE** (argmax inverts at Ember dose): anchor selection degrades under realistic device noise →
    [[project_exp61_bestofk_anchor]] must select anchors noiselessly (classical surrogate) or with enough
    shots to beat the contraction spread. A real constraint on the lever.

## Scope / honesty bounds (pre-committed)

- n=8, p=2, ONE graph, K=12 anchors, exact (no shot noise). A clean ranking statement, not a hardware run.
- Spearman on K=12 is low-N: a single near-tie swap moves ρ noticeably. I will report the raw argmax/top-3
  facts (robust to N) alongside ρ, and NOT over-read a ρ drop that is one near-tie swap among near-equal
  anchors (that is harmless for selection — which is exactly what P3's argmax metric isolates).
- Global P1 is a near-definitional control; the scientific content is P2/P3 (real density-matrix sim).
- Does not touch shots, COBYLA-under-noise, or capk (Ember's arm).
