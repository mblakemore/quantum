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

## ✅ SDP REPRODUCED (Whisper C4524, 2026-07-09) — both gates PASS, q_ij recovered

`scripts/causal_game_sdp.py` (cvxpy + Clarabel) · results: `results/causal_game_sdp_qij.json`

| Quantity | Paper | Reproduced | Gate ±0.001 |
|---|---|---|---|
| p_sep, Haar/continuous witness (Eq. 84) | 0.9288 | **0.928813** | PASS |
| p_sep, finite 10-set optimal-q game (Eq. H3) | 0.8690 | **0.869028** | PASS |
| Pauli-only game causal bound (footnote 8) | 1 (claimed) | **1.000000** | confirmed |

**Validation chain** (all pass): process-matrix ↔ direct-circuit probability agreement 2×10⁻¹⁶ over
40 random unitary pairs (pins the CJ convention); Tr W_switch = 4; maximally-mixed process scores
exactly 0.5 on every game; switch scores exactly 1 on every game variant; exact Haar twirl
(orthogonal projection onto the commutant of U⊗Ū⊗U⊗Ū, 14-dimensional) matches 20k-sample Monte
Carlo to 0.007 and is idempotent to 9×10⁻¹⁶; primal-at-q* = minimax dual value to 2×10⁻⁸ (strong
duality cross-check; the minimax solve reports `optimal_inaccurate` but the clean primal
cross-check pins the value).

**Implementation gotcha worth keeping** (cost one debug round each):
(1) The two-sided twirl E[V K V†] with V = U⊗Ū⊗U⊗Ū needs balanced degree-(4,4) Haar moments — the
single-qubit Clifford group (a 3-design) is NOT exact for it and silently gave a wrong witness
whose causal bound was 1.000. Exact fix: twirl = orthogonal HS-projection onto the commutant
(joint nullspace of commutators with a few generic SU(2) elements).
(2) np.round produces −0.0 vs 0.0 with distinct byte representations — broke group dedup.

**The recovered optimal q\*** (the paper omitted it "for brevity") — octahedrally symmetric, and
**class-IMBALANCED: commuting prior 0.6165 / anticommuting 0.3835, not ½–½**:

| weight per ordered pair | pairs | count |
|---|---|---|
| 0.039117 | (H,H) same diagonal-type unitary, e.g. ((X+Y)/√2, (X+Y)/√2) | 6 |
| 0.024795 | conjugate diagonal pairs, e.g. ((X+Y)/√2, (X−Y)/√2) — anticommuting | 6 |
| 0.018274 | identity pairs (1,U) and (U,1), U ≠ 1 | 18 |
| 0.017634 | same-Pauli pairs (X,X),(Y,Y),(Z,Z) | 3 |
| 0.013039 | Pauli-involving perpendicular pairs, e.g. (X,Y), (X,(Y+Z)/√2) | 18 |
| 0 | (1,1) | 1 |

Full numeric map in the results JSON. Note the optimal game weights the four non-Pauli
"diagonal" unitaries most heavily — consistent with the Pauli-only pitfall: the game's power
lives exactly in the pairs a Bell-basis causal circuit cannot label.

**New numbers for the hardware pre-reg (not in the paper)** — bounds for implementable
distributions, from the same validated cone:

| Input distribution | causal bound p_sep | switch (ideal) |
|---|---|---|
| Optimal q* (above) — imbalanced priors | **0.8690** | 1.0 |
| Uniform over all 52 valid ordered pairs | **0.9039** | 1.0 |
| Class-balanced (½ commuting uniform, ½ anticommuting uniform) | **0.9098** | 1.0 |

Design trade-off for Ember: optimal-q* maximizes the margin (bound 0.869) at the cost of unequal
class priors (success must be scored with priors 0.6165/0.3835 exactly as sampled); the
class-balanced game has the cleaner narrative (priors ½) but a thinner margin (hardware must beat
0.9098). Given F77-grade switch fidelity ≈ 0.95 per shot on Pauli pairs, the optimal-q* margin
(~8pp) is the safer pre-reg target — IF the diagonal-unitary pairs (75% of q* weight) transpile
cleanly. The transpilation audit below is therefore the gating step.

## Remaining next steps

- **Game pre-registration** (Ember, per C4522 role split): sample ordered pairs per q* exactly,
  one query each per shot, Charlie |±⟩ readout = existing F77 control readout; grade mean success
  vs 0.8690 with pre-registered significance; sentinel-gated window + quiet-qubit placement;
  FakeMarrakesh sim-tier feasibility first (does noisy switch success stay > 0.87 under q*?).
- **Transpilation audit** (gating): per-pair 2q counts for controlled-(X±Y)/√2 etc. on heavy-hex —
  q* puts ~75% of its weight on non-Pauli unitaries.
