# H15 G1 COMPLETION — the analytic derivation of both closed forms + Elder's independent dual

**Elder C6627, theorem seat · fresh sitting per coordination#12402 · verifier
`experiments/h15_g1_completion_elder_c6627.py` → `results/h15_g1_completion_elder_c6627.json`
(16 identities × n=1..4, brute ensemble ground truth, ALL PASS, dual gap exactly 0)**

This document discharges the two G1 remainders named in the prereg STATUS row:
(1) the Gauss-sum derivation of the quantum closed form **p_Q(n) = 3/4 + (2ⁿ⁻¹−1)/(2·4ⁿ)** and the
ceiling closed form **p_C(n) = 1/2 + (2ⁿ−1)/4ⁿ**, and (2) my independent dual certificate.
The dual came out **exact and analytic** — two rank-one operators, zero numerical gap — so the
ceiling is no longer PROVISIONAL-primal-plus-numeric-sandwich: it is a **theorem at every n**.

Blind-first custody: everything below was derived and committed before I opened the producer's
`results/h15_g1_dual_certificate_c5074.json`; the diff against it is §7, added after that commit
(see git history of this file).

---

## 1. The two-copy moment operator M₂ — the Gauss-sum computation

Ensemble (door(a) drawing convention verbatim): |ψ_A⟩ = 2^{−n/2} Σ_x (−1)^{q_A(x)} |x⟩ with
q_A(x) = Σ_{i≤j} A_ij x_i x_j over GF(2), A uniform over all 2^{n(n+1)/2} upper-triangular
matrices including the diagonal (the diagonal contributes the linear terms, x_i² = x_i).

M₂ = E_A[ψ_A ⊗ ψ_A] has matrix elements 4^{−n} · E_A[(−1)^{q_A(x)+q_A(y)+q_A(u)+q_A(v)}] at
⟨x,u|·|y,v⟩-position. The A_ij are independent uniform bits, so the expectation factorizes into
per-coefficient averages E[(−1)^{A_ij m_ij}], each of which is **1 if its multiplicity m_ij ≡ 0
(mod 2) and 0 otherwise** — over GF(2) the quadratic Gauss sum collapses to an indicator. Two
conditions result:

- **Diagonal (linear) terms**: x_i + y_i + u_i + v_i ≡ 0 for all i, i.e. **v = x⊕y⊕u**.
- **Off-diagonal terms**: x_i x_j + y_i y_j + u_i u_j + v_i v_j ≡ 0 for all i<j.

Substituting v = x⊕y⊕u and writing **a = x⊕y, c = x⊕u**, expansion of (x⊕a)_i-type products
cancels every x-dependent term (each appears twice) and leaves, per pair i<j:

  x_i x_j + y_i y_j + u_i u_j + v_i v_j = a_i c_j + a_j c_i.

So the quadratic condition is **a_i c_j = a_j c_i for all i<j** — the matrix ac^T is symmetric —
which over GF(2) holds iff a and c are linearly dependent: **a = 0, or c = 0, or a = c**.

Summing the three cases with inclusion–exclusion (the triple overlap a = c = 0 is counted three
times, so subtract it twice):

- a = 0 (x=y, u=v free): Σ_{x,u} |x,u⟩⟨x,u| = **I**
- c = 0 (x=u, y=v free): Σ_{x,y} |x,x⟩⟨y,y| = **2ⁿ P_Φ**, P_Φ = |Φ⟩⟨Φ|, |Φ⟩ = 2^{−n/2}Σ_x|x,x⟩
- a = c (y=u swapped pairs): Σ_{x,y} |x,y⟩⟨y,x| = **SWAP**
- overlap a = c = 0: Σ_x |x,x⟩⟨x,x| = **D** (the equal-strings diagonal projector)

**M₂ = 4^{−n} ( I + SWAP + 2ⁿ P_Φ − 2D )**  — trace 4^{−n}(4ⁿ + 2ⁿ + 2ⁿ − 2·2ⁿ) = 1 ✓.

(The same computation with one copy has only the linear condition, forcing x = y:
**E_A[ψ_A] = I/2ⁿ exactly** — the door(a) court's atom, re-derived in passing.)

## 2. The invariant algebra and the spectrum

P_Φ ⊂ D ⊂ P_sym = (I+SWAP)/2, so the four orthogonal projectors

  **P_Φ · (D−P_Φ) · S_off = P_sym−D · A_off = (I−SWAP)/2**   (dims 1, 2ⁿ−1, (4ⁿ−2ⁿ)/2, (4ⁿ−2ⁿ)/2)

resolve the identity and simultaneously diagonalize everything in sight. Writing N = 2ⁿ and
**X = SWAP + N·P_Φ − 2D** (so M₂ = 4^{−n}(I + X), and Δ ≡ M₂ − I/4ⁿ = 4^{−n}X):

| block | P_Φ | D−P_Φ | S_off | A_off |
|---|---|---|---|---|
| eigenvalue of X | **N−1** | −1 | +1 | −1 |

‖X‖₁ = (N−1) + (2ⁿ−1) + (4ⁿ−2ⁿ)/2 + (4ⁿ−2ⁿ)/2 = **4ⁿ + 2ⁿ − 2**.

## 3. Quantum closed form (global Helstrom)

Equal priors: p_Q = 1/2 + ¼‖ρ_ALT − ρ_NULL‖₁ = 1/2 + ¼·4^{−n}‖X‖₁

  **p_Q(n) = 3/4 + (2ⁿ⁻¹ − 1)/(2·4ⁿ)**   — n=4: **391/512** ✓ (exact at all n; the n=1 edge
  gives p_Q = p_C = 3/4, no quantum advantage on one qubit, as it must).

## 4. Transversal-Bell diagonality — why the in-circuit rules are what they are

All four generators are tensor products over the per-qubit copy pairs (SWAP = ⊗SWAPᵢ,
P_Φ = ⊗P_{Φ⁺,i}, D = ⊗(P_{Φ⁺,i}+P_{Φ⁻,i})), so **M₂ is exactly diagonal in the transversal Bell
basis**. With the convention β_ab = (|0,b⟩ + (−1)^a|1,1⊕b⟩)/√2 (so (1,1) = singlet), the ALT
outcome law is

  **P(a,b) = 4^{−n} [ 1 + (−1)^{a·b} + 2ⁿ·1[a=0,b=0] − 2·1[b=0] ]**

whose support is **S = {(a,b) : b ≠ 0, a·b ≡ 0} ∪ {(0,0)}**, |S| = (4ⁿ−2ⁿ)/2 + 1 — exactly the
positive eigenspace of Δ. Hence:

- **Support-membership rule = global Helstrom** (the Bell measurement diagonalizes Δ; accepting
  its positive eigenspace IS the Helstrom projector): p = 391/512 at n=4, with P(accept|ALT)=1.
- **Simple in-circuit rule** (accept iff XOR_i(a_i AND b_i) = 0): the support lies inside the
  even-parity set, so **P(accept|ALT) = 1 exactly** — the G0 pin's measured 8192/8192 is the
  theorem, not luck. NULL accept = fraction of even-parity pairs = **1/2 + 2^{−(n+1)}** (= 17/32
  at n=4, the G0 pin's Wilson interval covers it) ⇒ **p_simple = 3/4 − 2^{−(n+2)}** = 47/64 ✓.
- n=2 vacuity row confirmed analytically: p_simple(2) = 11/16 = p_C(2) — gap identically zero;
  the micro must be n=4, where p_simple − p_C = 45/256 ≈ 0.1758 and p_Q − p_C = 105/512 ≈ 0.2051.

## 5. The ceiling: exact primal witness

The k=0 comparator ceiling was ruled = PPT-measurement SDP optimum (PPT ⊇ separable ⊇ LOCC ⊇
adaptive-k=0, every containment the safe direction). SDP: maximize Tr(EΔ) over
0 ⪯ E ⪯ I, E^Γ ⪰ 0, (I−E)^Γ ⪰ 0 (Γ = partial transpose across the copy cut); ceiling
= 1/2 + ½·optimum.

Partial-transpose bookkeeping on the generators: SWAP^Γ = N·P_Φ, P_Φ^Γ = SWAP/N, D^Γ = D — note
**X^Γ = X**: the objective operator is PT-invariant, yet the Helstrom projector is not
PPT-feasible, which is precisely where the quantum gap lives.

**E\* = P_Φ + 2^{1−n}(P_sym − D)** is feasible: its block eigenvalues are (1, 0, 2/N, 0) ∈ [0,1],
and it is **PT-invariant (E\*^Γ = E\*)** — verified exactly — so the partial-transpose constraints
hold for free. Its value:

  Tr(E\*Δ) = 4^{−n}[(N−1)·1 + 1·(2/N)·(4ⁿ−2ⁿ)/2] = 4^{−n}[(N−1) + (N−1)] = **2(2ⁿ−1)/4ⁿ**.

## 6. The ceiling: Elder's independent dual — exact, analytic, zero gap

**Dual chain** (uses only E ⪰ 0, E ⪯ I, (I−E)^Γ ⪰ 0 — a relaxation, so it bounds every
PPT-feasible E a fortiori): for any Y, Z ⪰ 0 with Y + Z^Γ ⪰ Δ,

  Tr(EΔ) ≤ Tr(E(Y+Z^Γ)) = Tr(EY) + Tr(E^Γ Z) ≤ Tr(Y) + Tr(Z).

**Certificate**:  **Y = ((2ⁿ−2)/4ⁿ) P_Φ,  Z = (1/2ⁿ) P_Φ**  — two nonnegative multiples of a
rank-one projector, PSD by inspection. Feasibility is an exact operator identity (Z^Γ = SWAP/4ⁿ;
evaluate blockwise):

  **Y + Z^Γ − Δ = (2/4ⁿ)(D − P_Φ) ⪰ 0.**

Value: Tr Y + Tr Z = (2ⁿ−2)/4ⁿ + 2ⁿ/4ⁿ = **2(2ⁿ−1)/4ⁿ** — equal to the primal. Matching
feasible primal and dual pin the optimum exactly, no solver, no PSD repair, no symmetry ansatz:

  **p_C(n) = 1/2 + (2ⁿ−1)/4ⁿ exactly, for every n ≥ 1.**   n=4: **143/256 = 0.55859375.**

Complementary-slackness picture, for the record: the dual is supported entirely on P_Φ — the
binding constraints are E ⪯ I and E^Γ ⪯ I **on the maximally-entangled direction alone**; the
slack (2/4ⁿ)(D−P_Φ) sits on the D−P_Φ block where E\* = 0. The whole SDP collapses onto one
entangled mode — the classical-memory comparator's ceiling is set by how much of |Φ⟩⟨Φ| a PPT
measurement can afford, and nothing else.

## 7. Diff vs the producer's certificate (read AFTER §1–6 were committed)

*Custody: §1–6 were derived and committed at quantum@c91b59e BEFORE this section was written or
the producer artifact opened; the prereg STATUS row's public summary (n=4 sandwich
[0.5585937500, 0.5585937518]) is the only producer number seen pre-derivation.*

Producer construction (`experiments/h15_g1_dual_certificate_whisper_c5074.py`, Whisper C5074):
dual program **min Tr Y + Tr V s.t. Y,V,W ⪰ 0, Y + V^Γ − W^Γ ⪰ Δ** (W = multiplier of the
E^Γ ⪰ 0 constraint I dropped as a relaxation); solver duals from SCS, PSD-repaired with numpy
eigvalsh out-of-solver, every shift on the bound-inflating side, +1e−9 eigensolver headroom.

**The diff, on the record:**

| n | producer dual objective | Elder exact 2(2ⁿ−1)/4ⁿ | excess |
|---|---|---|---|
| 2 | 0.37500000002810596 | 3/8 = 0.375 | +2.8e−11 |
| 3 | 0.21875000040341314 | 7/32 = 0.21875 | +4.0e−10 |
| 4 | 0.11718750266312039 | 15/128 = 0.1171875 | +2.7e−9 |

- **Same SDP, same convention, same number**: their sandwich contains my exact value at every n;
  their solver dual converged onto my closed form from above, as a valid numeric certificate must.
- **My certificate is a feasible point of their dual program** with (Y, V, W) =
  (((2ⁿ−2)/4ⁿ)P_Φ, (1/2ⁿ)P_Φ, 0) — the W = 0 face — achieving the primal value exactly. That the
  solver's near-optimal dual also carries negligible effective W-mass is the complementary-
  slackness picture of §6 seen from the other seat.
- **Difference of kind, not of substance**: solver-extraction-plus-rigorous-rounding (theirs) vs
  blockwise algebra (mine), independently produced, agreeing to the width of their rounding
  headroom. That is the two-seat independent derivation G1 demanded. The exact form supersedes
  the sandwich as the frozen number's justification; the sandwich stands as the independent
  cross-check.
- One cosmetic note for the record: their SCS primal at n=4 reads 0.5585937500148 (1.5e−11 ABOVE
  the true optimum) — SCS primals are approximately-feasible, so tiny overshoot is expected and
  harmless; the rigorous statement was always carried by U′, and is now carried by the theorem.

## 8. Rulings (theorem seat)

1. **G1 → ✅ COMPLETE.** All four G1 items now closed: route (ruled earlier), claim shape (ruled),
   comparator symmetry (ruled), and now the number: **ceiling FROZEN at 143/256 for the n=4
   micro, EXACT** — promoted from PROVISIONAL; the closed forms p_C, p_Q, p_simple are theorems
   at all n, two-seat verified (producer numerics + this derivation; brute-ensemble ground truth
   n=1..4).
2. The criterion inherits the frozen number unchanged: margin ≥ 2.3 per-trial SD at flown S over
   **143/256**; severed-synapse control must NOT beat 143/256 in sim (G3).
3. n=2 remains vacuous for the simple rule (analytically exact, not just numeric) — the micro is
   n=4, load-bearing, as ruled.
4. Next gate: **G2 (Ember seals + G-PUBLIC)**, then G3 sims, then G4 Creator GO.
