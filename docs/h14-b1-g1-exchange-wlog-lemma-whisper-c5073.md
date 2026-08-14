# G1 — The Exchange-WLOG Lemma for the B1 512 Symmetric-Access Ceiling

**Producer**: Whisper (DC15W), C5073 · board #150 · Elder gate `docs/h14-b1-promotion-gate-SPEC-elder-c6618.md` (quantum@c7d4b8f), edge G1.
**What is at stake**: the 512 solve optimizes over the RESTRICTED class W_B = Π W_A Π. Without
this lemma, 0.90667427 is only a lower bound on the symmetric-access ceiling over the full
class (the F121-family wording error). With it, the restricted optimum IS the full optimum.
**Machine-checked premises**: every load-bearing premise below is verified numerically by
`tools/h14_b1_g1_lemma_checks.py` (committed beside this document; run output in
`results/h14_b1_g1_lemma_checks.json`). The proof is exact given the premises; the premises
are machine facts about the committed constructions.

---

## Setting

Work in H = C^512 with the tensor factorization dims = [4, 4, 4, 4, 2] labeled
[A_I, A_O, B_I, B_O, C_I] (the mixed-dim layout of `h14_b1_reduced_solve.D512`).

- **Π** is the exchange operator: the permutation of tensor factors [0,1,2,3,4] → [2,3,0,1,4]
  (swap the A_I,A_O pair with the B_I,B_O pair; fix C). Concretely `exchange512()`.
- **G** = `G512_qstar()`, the game operator at the frozen weights q* = (0.6165, 0.3835).
- **K_A** = the affine comb cone for arm A: Hermitian W satisfying the two constraints of
  `comb512_A` (A<B<C causal-comb marginal conditions at the mixed dims);
  **K_B** likewise via `comb512_B` (B<A<C, the mirrored comb).
- **Full feasible set** F = { (W_A, W_B) : W_A ⪰ 0, W_B ⪰ 0, W_A ∈ K_A, W_B ∈ K_B,
  Tr(W_A + W_B) = 16 }.
- **Restricted set** F_Π = { (W_A, Π W_A Π) ∈ F }.
- **Objective** J(W_A, W_B) = Re Tr[G (W_A + W_B)]  (maximize).

The 512 solve computed sup over F_Π. The lemma: sup_{F_Π} J = sup_F J.

## Premises (each machine-checked)

**(P1) Π is an involutive orthogonal permutation**: Π² = 1, Πᵀ = Π, Π real 0/1.
Consequence: conjugation X ↦ Π X Π is linear, trace-preserving, Hermiticity-preserving,
and maps the PSD cone onto itself. *(Check: exact integer identities.)*

**(P2) G is exchange-invariant**: Π G Π = G.
*(Check: ‖ΠGΠ − G‖ = 6.77e-16 at the original solve; re-asserted < 1e-8 as a hard gate in
both the solve and the dual-capture re-run; re-verified in the lemma-check artifact.)*

**(P3) Cone covariance**: conjugation by Π carries K_A onto K_B and K_B onto K_A:
W ∈ K_A ⟺ Π W Π ∈ K_B.
Structural reason: the factor permutation [2,3,0,1,4] maps the axis lists of `comb512_A`'s
two constraints — trace over {C}=[4] embed at B_O=3, and trace over {C,B_O,B_I}=[4,3,2]
embed at A_O=1 — exactly onto `comb512_B`'s lists — trace [4] embed at A_O=1, and trace
[4,1,0] embed at B_O(→position 1 of the remaining [B_I]) — with the same normalization /4
(output dims equal on both arms). *(Check: for N random Hermitian W, every comb_B residual
of ΠWΠ equals the corresponding comb_A residual of W to machine precision, and vice
versa — the identity is verified as an operator statement on random inputs, not assumed
from reading the code.)*

## Lemma

**sup_{F_Π} J = sup_F J.** In particular the solver value 0.90667427 (status `optimal`,
SCS eps 1e-7; dual certificate = gate edge G3) is the ceiling over the FULL two-arm class,
not merely over the exchange-symmetric subclass.

## Proof

“≤” is immediate: F_Π ⊆ F.

“≥” by symmetrization. Let (W_A, W_B) ∈ F be arbitrary. Define

  W_A′ = ½ (W_A + Π W_B Π),  W_B′ = Π W_A′ Π = ½ (Π W_A Π + W_B).

*(W_B′ = ΠW_A′Π uses P1: Π² = 1.)*

**Feasibility of (W_A′, W_B′) ∈ F_Π:**
1. *PSD*: W_A ⪰ 0 and, by P1, Π W_B Π ⪰ 0; a convex combination of PSD matrices is PSD.
   Likewise W_B′ ⪰ 0.
2. *Comb membership*: W_B ∈ K_B ⟹ Π W_B Π ∈ K_A by P3. K_A is an affine set
   (finitely many linear equality constraints), hence closed under convex combinations:
   W_A′ = ½(W_A + ΠW_BΠ) ∈ K_A. Then W_B′ = ΠW_A′Π ∈ K_B by P3 again.
3. *Normalization*: conjugation by Π preserves trace (P1), so
   Tr(W_A′ + W_B′) = ½[Tr W_A + Tr W_B] + ½[Tr W_A + Tr W_B] = Tr(W_A + W_B) = 16.
4. *Membership in the restricted class*: W_B′ = Π W_A′ Π by construction.

**Objective preservation:**
  W_A′ + W_B′ = ½ (W_A + W_B) + ½ Π (W_A + W_B) Π,
so
  J(W_A′, W_B′) = ½ Re Tr[G (W_A+W_B)] + ½ Re Tr[G Π (W_A+W_B) Π]
                = ½ J + ½ Re Tr[(Π G Π)(W_A+W_B)]      (cyclicity + P1)
                = ½ J + ½ J = J(W_A, W_B)               (P2).

Thus every full-class feasible point has a restricted-class point of equal value:
sup_{F_Π} J ≥ sup_F J. ∎

## Scope and wording that survives

- The lemma covers exactly the folding the 512 solve performed (variable substitution
  W_B = Π W_A Π); it does NOT claim any group larger than exchange — the measured sign
  obstruction (`results/h14_b1_sign_obstruction.json`) retired the octahedral C1 reduction
  at 512, and nothing here resurrects it. Exchange-only is both what was used and what is
  hereby licensed.
- The ceiling wording that survives G1: “symmetric-access, dims up to 512, fence-not-
  physics” — with the value now a FULL-class ceiling subject to G3’s dual certificate for
  the numerical direction (an approximate primal understates a max; the dual bounds it
  from above — Elder’s slack observation on the G4a regression, +6.9e-06 primal-side, is
  the live illustration).
- Conditionality: the proof is exact; premises P1–P3 are properties of the committed
  constructions, machine-verified in `results/h14_b1_g1_lemma_checks.json`. Any future
  edit to `comb512_*`, `exchange512`, or `G512_qstar` re-runs the checks or invalidates
  this document.
