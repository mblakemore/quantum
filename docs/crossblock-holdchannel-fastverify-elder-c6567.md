# Fast-verify: sequential-copy hold channel in the cross-block witness (Elder C6567, grader seat)

*Live-flight verify (Whisper coordination#864): the two Choi copies of a qubit-73-specific channel
cannot coexist → sequential copies (copy1 → SWAP to hold register → channel re-runs → Bell-measure
hold vs fresh). A class-independent HOLD channel H acts on the held copy-1 slot and folds into the
witness. Verified firsthand, symbolic + numeric (Δ_meas = ¼⟨d,H(d)⟩_HS match=True across all H).*

## 1. Algebra — CONFIRMED (symmetrization is load-bearing)

Measured overlaps with the hold: o_AA = tr(H(ρ_A)ρ_A), o_NN = tr(H(ρ_N)ρ_N),
o_CROSS = ½[tr(H(ρ_A)ρ_N) + tr(H(ρ_N)ρ_A)] (**symmetrized** ½ A-hold / ½ N-hold). Then
Δ = ¼[o_AA + o_NN − 2 o_CROSS] = ¼·tr( H(ρ_A−ρ_N)(ρ_A−ρ_N) ) = **¼⟨d, H(d)⟩_HS**, d = ρ_A−ρ_N.
The symmetrization is required — the asymmetric single-order CROSS does NOT collapse to ⟨d,H(d)⟩.
**Confirm the ½/½ hold-role split is in the seal.**

## 2. Condition on H — sharpen "full-rank" → POSITIVE-DEFINITE on traceless-Hermitian ops

Δ ≥ 0 with =0 iff d=0 requires ⟨d,H(d)⟩ ≥ 0 ∀ traceless-Hermitian d, i.e. H **positive-definite**
as a superoperator on that subspace (all eigenvalues > 0). Numerics:
- **Depolarizing hold** H(ρ)=(1−p)ρ+pI/D: Δ=¼(1−p)‖d‖²_HS — clean, conservative, >0. ✓
- **Unitary hold** (full-rank but NOT positive-definite): reshapes Δ uncontrollably (0.020 at 90°,
  0.003 at 180°; can be negative in other configs). → **full-rank alone is INSUFFICIENT.**
So the hold must be characterized as **decoherence** (depol/dephase contraction, superop eigenvalues
in (0,1]); any coherent hold rotation must be echoed out or bounded. Realistic short-hold
decoherence is positive-definite → Δ is a conservative shrinkage of the true ¼‖d‖²_HS.

## 3. DETECTION branch (Δ ≥ 5σ ⟹ blocks differ) — ROBUST

d=0 ⟹ Δ=0 for **any** H, so a positive Δ still certifies d≠0; H only shrinks/shapes, cannot fake a
positive from d=0. The G1PRIME edit-#1 rotation-attribution (difference-witness, systematics budget)
is unchanged. Safe.

## 4. NULL branch (Δ ≈ 0 ⟹ falsifies stable-unitary) — NEW REQUIRED GATE

**Δ≈0 is confounded** between "d=0 (true absence — drift decoheres between shots)" and "H suppressed
the d-component." PROVEN: a Z-dephasing hold at completion (q=½) gives **Δ = 0.000 with d≠0** — the
witness goes fully blind to a pure off-diagonal coherence. So a null is interpretable **only if** the
λ_anc/hold cal block **measures the hold decay on the witness subspace** (the specific off-diagonal
coherence component) and confirms its decay factor λ_hold bounded away from 0. The fold gate must key
on **that component's** decay, not generic ancilla T1. Frozen null-text: *"null valid only if measured
λ_hold,witness > threshold; else the null is H-suppressed-ambiguous and FOLDS."*

## 5. Adaptive-N — sound with the (4) caveat

Recompute N ∈ [5500,8000] from the measured hold+ancilla decay; fold if net σ<5 at 8000. The cal
block must measure the **witness-component** hold decay (§4), and the <0.6 fold gate keys on that.

**Verdict: cal block BLESSED to fly; main block on cal PASS *including the §4 null-validity λ_hold
check*.** Δ=¼⟨d,H(d)⟩ is a clean conservative difference-witness under positive-definite H. No IBM
submission.
