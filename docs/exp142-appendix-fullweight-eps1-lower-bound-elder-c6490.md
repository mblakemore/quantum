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
