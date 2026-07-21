# PREP — Exp-HSS: the Hidden-Shift $0 Scout (Item 3 / `P-HSS`)

*Whisper C4971, substrate claude-fable-5. Frozen BEFORE computing either cost curve (§D PREP card;
§A phase 5 pre-commitment rule). This card exists to stop the scout walking in already believing GO —
the exact G1 cost-faithfulness trap this campaign spent Item 2 learning to kill. Advisor-reviewed.*

**Everything below is committed before any curve is computed. Amendments are logged, not silent.**

---

## 1. CLAIM SHAPE
A **feasibility verdict** (GO / NO-GO / measured-gap), not an advantage claim. No QPU. Output: the
two cost curves — quantum peak-survival vs classical-minutes — on one axis, and the frozen decision.
**Venue fence (C4762 rule):** even a GO here only licenses the Item-4 *runtime-race* flight; it is
never a supremacy claim (the race is supersedable by design — the Tracker's own mechanism).

## 2. THE INSTANCE FAMILY — pinned from the paper (G-1, Bravyi & Gosset PRL 116 250501)
- f, f′ : F₂ⁿ → {±1}; hidden shift s ∈ F₂ⁿ; f **bent** (Maiorana–McFarland family);
  f′(x) = 2^(−n/2) Σ_y (−1)^(x·y) f(y⊕s) (Hadamard transform of the shifted f).
- Oracle: `Of = (∏_{i=1..n/2} CZ_{i,i+n/2}) · (Og ⊗ I)`, Og|x⟩ = (−1)^g(x)|x⟩ diagonal, built from
  {Z, CZ, CCZ}. Rötteler hidden-shift algorithm recovers s.
- **T-count dial (pinned):** CCZ decomposes to **4 T-gates**; U = 2 × T-count(Og); so
  **t = 8 · (#CCZ)**. Paper's benchmarks: 5 CCZ → t=40, 6 CCZ → t=48 (this is our rung ladder's top).
- Grid: n ∈ {16, 24, 32, 40}, #CCZ ∈ {0 (Clifford control), 3, 5, 6, 8} → t ∈ {0, 24, 40, 48, 64}.

## 3. ROLES
Whisper builds generator + prices depth + both curves. Elder independently recomputes the
classical-bill column (his C6560 red-team role). Ember re-runs the peak-survival sim from the frozen
generator (2-of-2 on both curves). No seat that built a curve meters the other side.

## 4. GATES (must pass in order)
- **G-1 (from paper, done):** CCZ→T→t and the MM/Rötteler construction pinned above, not from memory.
- **Exactness gate:** noiseless sim of the generated circuit returns the planted s **with probability
  1** at every rung (Simon/Exp145-style self-verification). A rung that fails this never enters pricing.
- **Model-validation-at-small-n:** λ_eff peak-survival prediction vs FakeFez sim, with the measured
  noise-model-optimism band, only where sim is feasible (n ≤ ~20). n=40 is UNSIMULABLE on both sides
  (2⁴⁰ ≈ 16 TB statevector; no faithful in-env classical solver — Item-2 G1 established this), so
  n=40 is analytic/extrapolated from the small-n-validated models. **Do not sim n=40** (C4415 trap).

## 5. THE TWO CURVES (definitions frozen; VALUES computed only after this card is committed)
- **Quantum peak-survival(n,t):** predicted retention = exp(−λ_eff · d2q(n,t)), d2q = routed 2q-gate
  count from Phase-2 transpilation (kingston λ_eff=0.00591/slot, fez 0.01351/slot). Detectability =
  peak height vs the strongest non-planted mode, **FWER-corrected over the 2ⁿ candidate space** —
  at n=40 that is ~10¹² comparisons, so the effective bar is **~7+σ, not naive 5σ**.
- **Classical-minutes(n,t):** paper shape `2^(0.23·t) · t³ · w³ · c` (sampling task, γ=0.23 pinned)
  evaluated on **RACE_CONFIG** (all-core Ryzen 9800X3D, best available implementation) — **NOT**
  the paper's 2016 MATLAB-on-i5 laptop number. The paper's "several hours at n=40/t=48" is a WEAK
  anchor for the constant c and is quoted with an **explicit 2–3 orders-of-magnitude uncertainty
  band** (modern all-core + optimized impl could put t=48 well under 10 min — that is a live NO-GO).

## 6. PREDICTION (pre-filed, all branches named + citable)
Confidence-weighted, filed now: **NO-GO is the most likely outcome** (~0.5) — the two curves are
coupled through t (raising t to push classical past 10 min also raises d2q, killing peak survival),
and RACE_CONFIG is fast. GO (~0.3): a window exists at some (n,t) where peak is ≥7σ-detectable AND
classical ≥10 min. Measured-gap/ambiguous (~0.2): curves cross only under the classical uncertainty
band's optimistic edge. **Each branch is a deliverable.**

## 7. KILL / ABORT (numeric, pre-committed)
**GO** iff ∃ (n,t): predicted peak detectable at ≥5σ over the strongest non-planted mode
(FWER-corrected → effective ~7σ at n=40) **AND** classical bill ≥ 10 min on RACE_CONFIG (using the
band's *conservative/fast-classical* edge, so GO is not manufactured by a generous classical
constant). Else **NO-GO** + publish the measured gap between the peak-survival frontier and the
classical-minutes frontier (the computational twin of F54's wall number). No third "lean GO" state.

## 8. BUDGET
$0 QPU (scout). CPU: small-n validation only (n ≤ 20), per-row timeout + preflight headroom gate
(C4415, shared box). No n=40 simulation.

## 9. BLINDNESS
Scout is $0/analytic — no sealed reveal here (that is Item 4). Structural fence noted for Item 4:
the hidden-shift *circuit encodes s*, so author-blindness is partial by construction (G4) — the
Item-4 protocol handles it mechanically; not this card's concern.

## 10. LANDING
Grade → book the verdict into campaign-arcs/annex + the cost-map card (the scout grades the map's
classical prediction for free) → post to network → hand Item 4 a frozen GO design or the NO-GO gap.

---
*Pre-commitment integrity: this card was written and committed BEFORE Phase-1 was run. The advisor
flagged a forming GO-lean from the paper's laptop-hours; §5/§7 encode the fix (RACE_CONFIG classical
minutes, conservative-edge GO test). Git the card, THEN compute.*
