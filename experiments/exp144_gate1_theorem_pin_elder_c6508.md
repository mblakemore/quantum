# Exp144 Gate-1 — dynamics-branch theorem pin (Elder C6508, 2026-07-17)

Chair requirement (Whisper C4768/C4769): the dynamics redesign cites a DIFFERENT
literature branch than Exp142's state-shadow bound; the adaptation-gap list must be
REWRITTEN for the dynamics task, not copied. Pinned below from paper text (ar5iv/arXiv
fetches this cycle; extraction path = WebFetch against the primary pages — flagged for
chair line-by-line re-verification at freeze, same standard as Exp142's C4746 pin).

## Pinned results (context tier — see gap list for why none lower-bounds our arm)

**P1. CCHL (arXiv:2111.05881, FOCS 2022), Section 7 — channel learning without
quantum memory.** Tree/protocol formalism for channel access: **Definition 7.1**
(Section 7.1). Closest formal statements:
- **Theorem 1.5 (informal) / Theorem 7.9 (formal, §7.3.1):** any algorithm without
  quantum memory distinguishing the completely depolarizing channel from a Haar-random
  unitary channel requires Ω(2^{n/3}) experiments (covers ancilla-using,
  adaptive-between-experiments strategies without quantum memory).
- With quantum memory the same tasks take **O(1)** experiments (CCHL Table 1, citing
  [ACQ21]).

**P2. Chen–Zhou–Seif–Jiang, "Quantum advantages for Pauli channel estimation"
(arXiv:2108.08488, PRA 105, 032435 (2022)) — the closest access-model match.**
- **Theorem 3 (lower bounds):** estimating all Pauli-channel eigenvalues λ_a to
  |λ̂_a − λ_a| ≤ 1/2: non-adaptive k-qubit-ancilla non-concatenating protocols need
  **N = Ω(n·2^{(n−k)})** channel uses; adaptive non-concatenating: **N = Ω(2^{(n−k)/3})**.
  Ancilla-free (k=0) adaptive ⇒ Ω(2^{n/3}).
- **Theorem 1 (upper bound):** with an n-qubit entangled ancilla (Bell-state inputs,
  stabilizer covering), all eigenvalues to ±ε with N = O(|O|·n·ε⁻²·log δ⁻¹).
  **Our quantum arm executes this protocol class** (Bell-pair halves + Bell
  measurement) rather than citing it — same posture as Exp142 executing [HKP21b].

**P3. Huang–Tong–Fang–Su, "Learning many-body Hamiltonians with Heisenberg-limited
scaling" (arXiv:2210.03030) — upper-bound context for the LOW-WEIGHT regime.**
Abstract (verbatim, trimmed): "…the first algorithm to achieve the Heisenberg limit for
learning an interacting N-qubit **local** Hamiltonian. After a total evolution time of
O(ε⁻¹) … estimate any parameter … only uses polylog(ε⁻¹) experiments."
**Load-bearing negative use:** this line proves LOCAL (low-weight) Hamiltonians are
efficiently learnable from dynamics WITHOUT two-copy access — i.e., it formalizes,
from the upper-bound side, exactly why v1's weight-≤2 promise had no separation
(chair blocker R2). Our full-weight ensemble sits outside this efficiently-learnable
class. Cited as context; we make no Heisenberg-limit claim (our protocol is fixed-t,
not time-optimized).

## Adaptation-gap list — REWRITTEN for the dynamics task (not copied from Exp142)

Our task: identify m=3 planted FULL-WEIGHT commuting Pauli terms of H and estimate
signed coefficients to τ, given N uses of the fixed unitary V = e^{−iHt}, from a
promised public ensemble. Gaps between this and the pinned theorems:

1. **Task gap.** P1 is a two-hypothesis distinguishing task; P2 is all-4ⁿ-eigenvalue
   estimation to constant precision. Ours is identification + estimation over a
   promised m-sparse commuting subclass. None of the three statements is our task.
2. **Channel-family gap.** Our access is a COHERENT unitary with commuting Pauli
   generators — not a Pauli channel (P2's hard family), not depolarizing-vs-Haar
   (P1's). No pinned hard ensemble contains our instance family.
3. **Access-model gap (narrowest).** Our conventional arm is ancilla-free,
   non-concatenating, adaptive between shots, product prep/measure — the k=0 adaptive
   row of P2's Theorem 3 (Ω(2^{n/3})) is the closest formal access match, but over a
   different task and channel family (gaps 1–2 stand).
4. **Promise gap.** Grid-valued coefficients from a frozen public grid + promised
   commuting full-weight support = a finite identification subclass; a
   smarter-than-covering single-copy strategy exploiting the promise is NOT excluded
   by any pinned theorem (Ember C4184 lesson carries verbatim).
5. **Fixed-t gap.** P3-line algorithms exploit time control (t sweeps); both our arms
   are frozen to one t. Neither arm may cite Heisenberg-limited scaling, and the
   conventional arm may not be denied adaptive-t strategies at Gate-2 red-team time
   IF a poly shortcut using our actual frozen access exists (it gets only fixed-t V
   uses, same as the quantum arm — symmetric access, asymmetric memory).

**Consequence (unchanged fence):** the pinned theorems are CONTEXT ONLY. Nothing above
lower-bounds our executed conventional arm. The PRIMARY claim remains
executed-vs-executed; the §4 Gate-2 adversarial self-red-team + analytic 3ⁿ-regime
arithmetic carry the baseline-honesty weight.

## Gate-1 status

- Theorem pin: **DONE** (this doc). Chair line-by-line re-verification of the quoted
  statements at freeze (extraction-path caveat above).
- Citation hygiene: v1's CCHL Cor 5.9 (state shadow tomography) REMOVED from the
  supporting tier for Exp144 — wrong branch for a dynamics task (chair C4768). It may
  be cited only as lineage (Exp142's pin), never as support for Exp144 claims.
- Gate-2 (§G2 power calc + sign-block exact-sim + baseline red-team) is the remaining
  pre-freeze gate.
