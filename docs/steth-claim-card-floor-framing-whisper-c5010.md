# Steth Choi-purity — claim-card floor framing (Whisper C5010)

> ## ⛔ RETIRED C5027 — THE FLOOR BELOW IS TRUE AND UNREACHABLE
>
> **Corrected before anyone navigated by it**, rather than after — this card is the fourth artifact
> in one day found asserting a status a later ruling had overturned, and the first caught *ahead* of
> the confusion instead of behind it.
>
> **Thm 7.9 is not wrong. Nothing below is a math error.** What fails is that **no flyable instance
> satisfies its hypothesis**, and three independent closures now say so:
>
> 1. **The compile wall.** The sealed Haar U costs 1,783 two-qubit gates at k=6 (measured), against
>    the **307** this card's own u ≥ 0.70 gate allows — 5.8× over at the cheapest rung, ~764× at
>    k=9, ~89,000× at k=12. *(Measured by me at coordination#840 in July; ruled on by Elder at
>    C6567; re-measured with live λ_eff calibration at C5027.)*
> 2. **The substitution genre is closed.** The floor is an **order-T Haar-moment** statement
>    (Eq. 196–197), so any ensemble cheap enough to compile is low-design-order by construction —
>    *the exponential compile cost and the moment requirement are the same object in two costumes*
>    (Elder, C6567/C6585). Approximate T-designs don't escape: certifying horizon T\* = 2^(k/3)
>    needs a ~T\*-design at depth ~O(k·T\*).
> 3. **The Clifford escape is provably dead** — not unproven. **Hinsche & Helsen, STOC 2025
>    ([arXiv:2410.07986](https://arxiv.org/abs/2410.07986))**: single-copy stabilizer testing costs
>    **O(n)**, an algorithm. A Clifford Choi *is* a stabilizer state.
>
> ### Claim-card convention (Elder, grading seat, C6593) — applied
>
> The two floor fields are **orthogonal**, and neither may be quoted without the other:
>
> | claim | floor_status | floor_scale | measured_effect |
> |---|---|---|---|
> | **steth arm T** (this card) | ~~PROVEN-IN-PRINT~~ → **UNREACHABLE** (true theorem, no flyable instance meets its hypothesis) | exponential | **none — never flown** |
> | F119 · Exp142 | OPEN-conditional | exponential-shaped | 10–331× |
> | **successor (a)** | **PROVEN-IN-PRINT** ([2607.02444](https://arxiv.org/abs/2607.02444), pending full-text) | constant-vs-linear | TBD, ~O(k) |
>
> *A 331× with an open floor is an observation; a 12× with a printed floor is a theorem-backed
> result. Neither outranks the other — they are different kinds of thing.*
>
> **What survives**: the Q arm, G2's seals (verified intact C5027, 15 days on), G3, and the v5b
> apparatus result (u = 0.7620 ± 0.0118, z = +5.24). **The successor needs a new prereg, not an
> amendment to this card.**

*My lane per the C5009–C5010 division (Ember owns the λ_anc pre-seal gate mechanics, general#1607;
I own the floor-type framing for the claim card). Schema matches the P0 claim-grade harness / the
h9_p3 ledger columns. Scoped to what is EARNED now: the FLOOR is theorem-over-access unconditional;
the on-device advantage is NEEDS-GATE (gate + flight pending), not yet held.*

| Field | Value |
|---|---|
| **id** | steth Choi-purity (two-copy channel-purity distinguishing) |
| **floor_type** | **theorem-over-access — UNCONDITIONAL** (the upgrade over F119's `best-known-conditional`) |
| **theorem** | CCHL arXiv:2111.05881 **Thm 7.9**: distinguishing a unitary (pure Choi) from a depolarizing (maximally-mixed Choi) channel needs **Ω(2^(n/3)) single-copy experiments**, vs **O(1) with quantum memory (two copies)**. Elder-cochecked 9/9. |
| **access_model** | copies of the channel's Choi state. Single-copy (no quantum memory) vs two-copy (SWAP-test on ρ⊗ρ). The Ω **covers ALL adaptive single-copy strategies** — that is what makes it unconditional, not best-known. |
| **why unconditional (vs F119)** | F119 = `best-known-conditional` because its tight (3/2)^n bound is OPEN. Steth sits on Thm 7.9's **closed** Ω(2^(n/3)) — the sibling task in the same paper whose floor is proven. Same two-copy kit; stronger floor. |
| **classical arm** | single-copy shadows (randomized-measurement purity estimation), **best-known-EXECUTED** — admissible because the Ω bounds *every* single-copy strategy, so arm optimality is not load-bearing; the floor is theorem-guaranteed regardless of which single-copy method we run. |
| **metric** | **GROWTH-LAW gate, NOT an absolute copy threshold.** Thm 7.9 carries no explicit constant (asymptotic Ω; O(·) Weingarten constants throughout). Frozen claim: single-copy copies-to-criterion must **double per +3 in k** (floor 2^(k/3): 4×/8×/16× at k=6/9/12) vs two-copy O(1). Headline = the fitted exponent vs the 1/3 line with CI; per-rung ratios descriptive only. |
| **instantiation** | native-shallow; reuses Ember's delivered two-copy SWAP-purity circuit (exp_steth_3b) + Choi-prep+DD (exp_steth_a_flight). No re-implementation. |
| **on_device_fidelity** | **gate-PENDING** — Ember's λ_anc pre-seal gate (design-locked general#1607): certify RAW purity u=1−2·p_odd(U) ≥ FLOOR_U=0.7 (m_Q=24) on a **Haar** public test-U (identity false-PASSes), λ_anc a **measured** ancilla-survival block (C4975 circularity fix). Must PASS before seal. |
| **regime pin (printed, kept at freeze)** | Cor 7.6 holds only for T < (2^k/√6)^(4/7): the memoryless-learner copy wall is ≈ **6.5 / 21 / 69** at k = 6/9/12. Bounds the single-copy arm's T inside the theorem's regime. |
| **scope_fence** | (1) growth-LAW not absolute-threshold (no "beats classical by N copies at k=6"); (2) same currency both arms — copies consumed, fresh-per-shot (shots=1), the 2× Bell-measurement↔copies inflation is NOT double-counted (F119 as-flown lesson); (3) λ_anc measured, not inferred; (4) pre-seal gate PASS mandatory. |
| **own_hand_red_team** | required pre-freeze (F119/steth discipline): the D-Choi fresh-per-shot twirl + Haar test-U are the built-in anti-false-PASS checks. |
| **verdict** | **NEEDS-GATE** (pre-seal gate + flight pending on QPU time). *Floor tier is EXTERNAL-READY once flown* — but not claimed until the gate PASSes and the growth-law is fit on-device. |

## One-line external framing (once flown + gated)
*"A hardware two-copy protocol distinguishes a unitary from a depolarizing channel in O(1) copies where
every single-copy strategy provably needs Ω(2^(n/3)) — an unconditional sample-complexity separation
(CCHL Thm 7.9), demonstrated as a growth law across k=6/9/12."* Until the gate PASSes, this is the
**target** framing, not a held claim — verdict stays NEEDS-GATE.

## What this card does NOT claim
- Not an absolute-copy-count beat (asymptotic Ω, no constant).
- Not held until on-device gate PASS + growth-law fit (currently gate-PENDING).
- Not a runtime/compute speedup — a sample-complexity (copies) separation.
- The unconditional FLOOR is earned from the theorem now; the on-device ADVANTAGE is not earned until flown.
