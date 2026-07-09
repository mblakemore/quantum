# Causal discrimination game — exact SDP bound pulled from literature (pre-reg groundwork)

**Author**: Whisper (DC15W), C4523 (2026-07-09) — Creator-directed follow-up to
`docs/bridges-to-compute-advantage-whisper-c4522.md` Bridge 3a
**Source**: Araújo, Branciard, Costa, Feix, Giarmatzi, Brukner, *Witnessing causal nonseparability*,
New J. Phys. **17**, 102001 (2015), arXiv:1506.03776 — extracted from the paper full text
(pdf-extraction skill), quotes verbatim below. This is the "Araújo et al. SDP" the ICO review
(arXiv:2506.04607) cites for the commute/anticommute causal bound.

## The task (their §"Chiribella's witness", Eqs. 79–84 + Appendix H)

Alice applies unitary U_A once, Bob applies U_B once; the pair is promised to either commute or
anticommute, **prior 1/2 each**. Charlie measures one qubit in the |±⟩ basis and guesses which.
Success probability p_succ = tr[G·W] for strategy/process W. **The quantum switch achieves
p_succ = 1** ("the probability of success is 1 when W = W_switch"; "the probability of success for
the quantum switch is always equal to one").

## The bounds — THREE regimes, and the choice of unitary measure is everything

| Unitary measure over pairs | Max causally-separable success p_sep | Where |
|---|---|---|
| **Pauli pairs only** | **= 1 (NO advantage possible)** | footnote 8 |
| Haar-based continuous measures | **≈ 0.9288** (SDP, YALMIP+MOSEK); worst-case noise tolerance 0.0766 | Eq. (84) |
| **Finite 10-unitary set 𝒢, SDP-optimized input distribution** | **≈ 0.8690** | Eq. (H3) |

Verbatim on the Pauli pitfall:
> "If we were to choose, for example, measures that only produce pairs of Pauli matrices, then there
> is a causally separable circuit that can decide the commutativity or anticommutativity with
> probability 1." (The circuit — from Chiribella's own paper — applies the Paulis to half of a
> maximally entangled state and measures in the Bell basis.)

Verbatim on the continuous bound:
> "Solving it with YALMIP and MOSEK, we obtain p_sep_succ ≈ 0.9288."

The finite, hardware-implementable game (Appendix H): unitaries drawn from
**𝒢 = {1, X, Y, Z, (X+Y)/√2, (X−Y)/√2, (X+Z)/√2, (X−Z)/√2, (Y+Z)/√2, (Y−Z)/√2}**,
input distributions q_ij over commuting / anticommuting pairs **optimized by SDP** (support
constrained to genuinely commuting / anticommuting pairs), giving
> "Solving this problem numerically, we found p_sep_succ ≈ 0.8690."

## Consequences for our pre-registration (the catch and the design)

1. **⚠️ Our F75/F77 apparatus runs Pauli pairs (X,X / X,Z) — in that regime the causal bound is 1
   and there is NO game to win.** Re-running F77 shots and comparing to 0.869 would be invalid.
   The witness result (F75/F77) stands on its own terms — causal *nonseparability* was certified via
   the witness operator, which is a different (device-characterized) certification than winning the
   game above the causal bound. The GAME version requires the 10-unitary set, including the four
   non-Pauli members (X±Y)/√2 etc.
2. **The graded bound for the game we can actually run is p_sep ≈ 0.8690** — with the paper's exact
   optimized input distribution. The bound is **distribution-dependent**: if our pre-reg uses any
   other distribution (e.g., uniform over valid pairs, or a subset forced by transpilation quality),
   the SDP must be RE-SOLVED for that distribution before grading. Do not grade against 0.869 unless
   the game is exactly theirs (the optimal q_ij are omitted "for brevity" in the paper — so in
   practice we must re-solve the SDP regardless, both to recover the optimal distribution and to
   verify 0.8690 reproduces).
3. **Hardware feasibility read**: F77's DISC_switch = +1.900 ⇒ per-shot discrimination success
   ≈ 0.95 on Pauli pairs. The margin over 0.869 is ~8pp — real but not huge, and the non-Pauli
   unitaries [(X±Y)/√2 rotations] may transpile deeper / dirtier than the Paulis we've run. Sentinel
   window-gating + placement (Bridges 1–2) are not optional here; they are what buys the margin.
4. **Adversary strength note (good news)**: "causally separable" includes classical mixtures of
   definite orders AND dynamical (outcome-dependent) order — a strictly stronger adversary class
   than F73/F77's fixed-order-mixture control. Beating 0.869 rules out ALL of it in one number.
5. **Honest-scope carryover** (from C4522 doc): a photonic device-independent certification exists
   (Nature Comms 2023). Ours = gate-model, pre-registered, superconducting, game-form. Say so.

## Concrete next steps (proposed owners)

- **SDP reproduction** (Ember or me, sim-tier, zero QPU): implement the W_sep cone (paper Thm 3
  characterization, 3-party switch scenario: d_AI=d_AO=d_BI=d_BO=2, d_CI=2) in cvxpy/MOSEK-or-SCS;
  reproduce 0.9288 (Eq. 84) and 0.8690 (Eq. H3); extract the optimal q_ij. Gate: match to ±0.001.
- **Game pre-registration** (Ember, per C4522 role split): 10-unitary set, sampled pairs per the
  recovered optimal q_ij, one query each per shot, Charlie's |±⟩ readout = the existing F77 control
  qubit readout; grade single-shot success vs the re-solved bound; sentinel-gated window +
  quiet-qubit placement; pre-register the sim-tier switch success under FakeMarrakesh noise as the
  feasibility check before any QPU spend.
- **Transpilation audit** (whoever pre-registers): per-pair 2q-gate counts for all pairs in the
  support of q_ij — the (X±Y)/√2 controlled versions are the depth risk.
