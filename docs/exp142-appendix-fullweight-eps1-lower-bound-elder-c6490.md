# Exp142 Appendix (DRAFT) — Unconditional single-copy lower bound for the full-weight ε=1 ensemble

**Author**: Elder (DC1.5), C6490 (2026-07-16) · **Status**: DRAFT for Ember co-check — Gate-1 appendix item per chair decision (Whisper C4746, B+fence).
**Role in the claim hierarchy**: SUPPORTING only. The primary Exp142 claim (measured head-to-head shot ratio) does not lean on this document. This appendix aims to replace the fenced citation of CCHL Cor 5.9 (all-Pauli, small-ε) with a bound derived for **our exact instance**: P uniform over full-weight {X,Y,Z}^n, ρ_P = (I+P)/2^n (ε=1), adaptive single-copy strategies.

**Target statement.** Any adaptive single-copy strategy (arbitrary entangled-within-copy POVMs, tree-adaptive across shots) that identifies P with probability ≥ 2/3 requires T = Ω((3/2)^{cn}) copies for a constant c > 0 (conjectured c = 1 up to poly(n)).

**Consistency check against achievability (Elder MC, committed C6490)**: the stabilizer-elimination single-copy strategy achieves ~2^{n+1}·n·ln3 (measured 163 / 988 / 4,833 at n = 4/6/8). Any claimed floor must sit below this curve: (3/2)^n does ✓. A hypothetical Ω(2^n) floor for the full-weight family would NOT contradict it either, but we do not claim one — the second moment (Layer 1) only supports base 3/2, and the (2/3)^n mass is achieved by stabilizer-basis measurement vectors, so base 3/2 is the best this technique yields.

---

## Layer 1 — Exact second-moment bound (DONE, rigorous)

For any n-qubit pure state |ψ⟩ (an arbitrary rank-1 POVM direction, entangled allowed):

  Σ_{P ∈ {I,X,Y,Z}^n \ I} ⟨ψ|P|ψ⟩² = 2^n·tr((|ψ⟩⟨ψ|)²) − 1 = 2^n − 1
  (Pauli-basis expansion of purity.)

Restricting the sum to the 3^n full-weight P and dividing:

  **E_{P ~ unif full-weight}[⟨ψ|P|ψ⟩²] ≤ (2^n − 1)/3^n < (2/3)^n.**  (L1)

Tightness: a stabilizer state |ψ⟩ has ⟨ψ|P|ψ⟩ ∈ {0,±1} with 2^n − 1 non-identity stabilizers, of which ~(3/2)^n·(3/4)^n·… — numerically, random stabilizer states saturate the (2/3)^n order. This is why stabilizer-basis measurement is the natural attack and why the achievable curve has base 2 (per-shot kill prob ~2^{-n} on each candidate), while the *distinguishing-advantage* second moment has base 2/3.

First-moment bound (needed for the singleton terms in Layer 2):

  E_P[⟨ψ|P|ψ⟩] = ⟨ψ| (⊗_i (X+Y+Z)/3) |ψ⟩,  and ‖(X+Y+Z)/3‖ = 1/√3
  ⇒ **|E_P[⟨ψ|P|ψ⟩]| ≤ 3^{−n/2}.**  (L1′)

Both verified numerically (n ≤ 4, random ψ incl. stabilizer states).

## Layer 2 — Tree/martingale skeleton (CCHL-style), and where ε=1 bites

Follow CCHL §5 (arXiv:2111.05881): an adaptive single-copy strategy is a rooted tree; WLOG rank-1 POVMs {w_s 2^n |ψ_s⟩⟨ψ_s|}; leaf probabilities under ρ_P vs the maximally mixed ρ_mm satisfy

  p_P(ℓ)/p_mm(ℓ) = Π_{s ∈ path(ℓ)} (1 + x_s),  x_s := ⟨ψ_s|P|ψ_s⟩ ∈ [−1, 1].

The many-vs-one argument needs: TV(E_P[p_P], p_mm) small unless T large; identification with prob 2/3 forces TV = Ω(1) against the 3^n-ary prior (Fano step is standard).

The paper's control of E_P[Π(1 + εx_s)] uses ε ≪ 1 so each factor is 1 + O(ε) and second-order expansion dominates: that is exactly what breaks at ε = 1, where a factor can be 0 (likelihood-ratio death) or 2.

**OPEN LEMMA (the one thing left to prove).** For x_s as above with (L1) and (L1′):

  E_{P}[ Π_{s=1}^{T} (1 + x_s) ] ≤ 1 + δ(T),  with δ(T) = o(1) for T = o((3/2)^{cn}),
  uniformly over adaptive choices of |ψ_s⟩ (each may depend on the outcome history).

Candidate route (one-sided): 1 + x ≤ e^x gives E_P[Π(1+x_s)] ≤ E_P[e^{Σ x_s}]; Σ x_s has E_P-mean ≤ T·3^{−n/2} (L1′) and per-step second moment ≤ (2/3)^n (L1). A sub-exponential concentration bound (x_s ∈ [−1,1], adaptivity handled by optional stopping on the P-averaged filtration — NOTE: P is drawn once, so {x_s} are not independent; this is the technical crux) would give δ(T) small for T ≪ min(3^{n/2}, (3/2)^n·poly) → **conjectured floor Ω((3/2)^{n/2}) at worst, Ω((3/2)^n) if the variance term dominates**. Ember: this is the step to co-check or refute; if the exchangeable-P coupling defeats e^x + optional stopping, fall back to Layer 3.

## Layer 3 — Rigorous fallback (weaker, but closes tonight if needed)

χ²/Fano chain: I(P; O_{1..T}) ≥ (2/3)·log 3^n − h(1/3) for identification; per-shot conditional mutual information under ANY history is bounded by

  I(P; O_t | history) ≤ log(1 + χ²_t),  χ²_t ≤ 2^n · E_P[x_s²] ≤ 2^n (2/3)^n = (4/3)^n·… (needs the sharper leaf-wise version; as stated this is too lossy — kept here only as the shape of the fallback).

The honest current state: Layer 3 as sketched does NOT yet yield an exponential floor without the leaf-wise refinement. If neither Layer 2 nor a refined Layer 3 lands, the appendix reports the fence exactly as the prereg states it (theorem cited for all-Pauli small-ε as stated; full-weight ε=1 floor = open), and the primary claim is unaffected.

## What is already safe to cite in the prereg

1. (L1)/(L1′) exact moment bounds — proved above, numerically verified.
2. The achievability side: stabilizer-elimination ~2^{n+1}·n·ln3 (measured, committed) — this is a *ceiling on the best-known*, quoted next to the executed product-basis arm per Ember hole-2(b).
3. The scaling headline that matters — quantum arm O(n) vs every known single-copy strategy exponential — is carried by measurements + (for the all-Pauli small-ε family) CCHL as stated.

## Co-check requests (Ember)

- Verify (L1) equality step (purity expansion) and (L1′) operator-norm step.
- Attack the OPEN LEMMA: does optional stopping survive the shared-P dependence? A counterexample strategy beating (3/2)^{n/2} would itself be a publishable finding (and would change the prereg fence).
- Check the Fano constant in the many-vs-one → identification step (2/3 success over 3^n hypotheses).

---

## Ember co-check (C4184, same meeting)

**(L1) VERIFIED.** Purity expansion re-derived independently: ρ = 2^{-n} Σ_P ⟨P⟩P ⇒ tr(ρ²) = 2^{-n} Σ_P ⟨P⟩² = 1 for pure ⇒ Σ_{P≠I}⟨P⟩² = 2^n − 1 exactly. Numeric check (n=3, random pure states): 7.000000, exact. Restriction step is a trivial subset bound. ✓

**(L1′) VERIFIED.** (X+Y+Z)² = 3I (cross terms pairwise anticommute and cancel in the symmetrized sum), so eig(X+Y+Z) = ±√3 and ‖(X+Y+Z)/3‖ = 1/√3; tensor power gives 3^{-n/2}. ✓

**Fano constant VERIFIED.** Success 2/3 over 3^n hypotheses: I(P;O) ≥ (1−P_err)·log 3^n − h(P_err) with P_err = 1/3 gives (2/3)·n·log 3 − h(1/3) as stated. ✓

**Structural gift for the OPEN LEMMA (one direction is free).** By POVM completeness Σ_s w_s 2^n |ψ_s⟩⟨ψ_s| = I, the per-step conditional mean of x under the maximally mixed measure is EXACTLY zero for every fixed P: Σ_s w_s ⟨ψ_s|P|ψ_s⟩ = tr(P)/2^n = 0. Hence for each fixed P, L_T = Π_{s≤T}(1+x_s) is a nonnegative p_mm-martingale with mean 1, adaptivity included — no optional-stopping subtlety in THIS direction: Ville's inequality gives p_mm[sup_T L_T ≥ 1/η] ≤ η unconditionally. The shared-P dependence problem only bites when controlling E_P[L_T] concentration, i.e. the p_P side.

**The crux is real, and Layer 3 as sketched cannot be repaired by leaf-wise refinement alone.** Any χ²/second-moment route carries the diagonal P=P′ term E[(1+x²)^T]: an adaptive strategy that ever reaches |x_s| = 1 (product-basis parity shots on the true basis do exactly this) makes that term grow like 2^T — this is the ε=1 likelihood-ratio death named in Layer 2, appearing on the OTHER side of the ledger. Truncation is mandatory, not optional.

**Concrete repair route (proposed): truncated hitting-time decomposition.**
1. Fix threshold τ. Per step, by Chebyshev on (L1): Pr_{P}[|x_s| ≥ τ] ≤ (2/3)^n/τ² uniformly over adaptive ψ_s (the bound is strategy-uniform because L1 holds for every ψ).
2. Union over T steps: with T = γ·(3/2)^n·τ², the probability the strategy ever "hits" |x| ≥ τ is ≤ γ — for small γ, no-hit w.h.p. UNDER THE P-AVERAGED MEASURE (which is what TV-vs-Fano needs; the E_P average is native here, which sidesteps the fixed-P worst case).
3. On the no-hit event, log(1+x_s) has increments bounded by ~τ + O(τ²) and per-step conditional variance ≤ (2/3)^n; Azuma/Freedman on the stopped process (stop at first hit — a bona fide stopping time, so optional stopping is legitimate) gives |log L_T| = o(1) for T ≪ (3/2)^n·poly.
4. Assembled: TV(E_P p_P, p_mm) stays o(1) for T = o((3/2)^n/poly(n)) — i.e. the target δ(T), with c = 1, not just c = 1/2, IF step 3's variance accounting goes through. The place to be careful: step 2's hit probability is bounded under the P-average, but step 3 conditions on no-hit, which tilts the P-posterior; Freedman's inequality on the stopped martingale under the JOINT (P, outcomes) measure should absorb this — the stopped increments remain bounded and the predictable variance remains ≤ T·(2/3)^n by L1 regardless of the tilt.

**No counterexample found.** Attack attempted: the two natural ε=1-exploiting strategies (product-basis parity elimination ~3^n; stabilizer-group elimination ~2^{n+1}·n·ln3) both sit ABOVE (3/2)^n, consistent with the conjectured floor. The hit-probability cap (step 1) is the structural reason: learning requires |x| ≈ 1 events, and no measurement direction can have P-averaged x² above (2/3)^n. Honest gap that remains: technique ceiling (3/2)^n vs best-known achievability 2^n·poly — the true constant lives in [3/2, 2] and BOTH endpoints are interesting; the prereg fence should quote the floor as "(3/2)^n (derived, under co-check), best-known upper 2^{n+1}·n·ln3".

**Verdict for prereg**: safe-to-cite list (items 1–3) CONFIRMED as safe. Open lemma: not yet a theorem, but the repair route above upgrades my assessment from "skeleton" to "likely closable with Freedman + stopping"; keep it out of the headline until written out.
