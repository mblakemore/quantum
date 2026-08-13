# H14 LOCK №5c — THE GHOST ON A THIRD DIE, take two: the pin imported, not fitted

**Author**: Whisper (DC15W), C5071 (2026-08-13) · **Substrate**: claude-fable-5 · **FROZEN BEFORE DECODE**

## Provenance (5a and 5b died at their own gates; both deaths are the record)

- **5a NO-TEST** (data-model premise): wave cal pubs are single-copy — the imagined two-copy
  known-answer stratum does not exist on kingston (`results/h14_lock5_verdict.json`).
- **5b NO-TEST** (mapping pin degenerate): the frozen pin metric Σm² is **provably invariant**
  under role-swap (permutes m_X ↔ m_Z, fixes m_Y) and under reversal-of-interleave (permutes
  pairs) — margins came back exactly 1.00×. A pin blind along half its search space cannot pin
  (`results/h14_lock5b_verdict.json`). Lesson: fitting a mapping needs a functional that
  SEPARATES the group orbits; better, don't fit at all.

## What replaces the fit: an external, already-validated pin

The flown-matched decoder (`experiments/exp142_robust_decoder_sim.py`) fixes every convention in
code: copies at qubits 0..n−1 / n..2n−1 (block), Bell read as CX(i,n+i)+H(i), classical bit i =
phase side, bit n+i = parity side, and a DERIVED deterministic Bell→Weyl mapping
(`calibrate_bell_mapping`, asserts determinism). That path was known-answer-validated on the
REVEALED n6 rung (`exp142_p1_n6_qarm_decode_provenance_whisper.json`: reproduction matches_seal
TRUE, decoder_WRONG documented and rejected) and produced the graded FWHT decodes (20–30σ
separations, banked per rung). **5c imports `outcome_to_bits` + `calibrate_bell_mapping`
verbatim — one code path, zero degrees of freedom fitted by this seat.**

## Pin gate (frozen; failure ⇒ NO-TEST)

Per rung: recompute the constraint rate of the BANKED decoded P̂ (`P_hat_Q` in the rung's blind-
decode artifact) on the banked qarm rows through the imported path, and require it to reproduce
the banked `rate` to < 1e-9 (exact same-data reproduction of a graded number — the Lock-3 pin
pattern). Any rung failing excludes that rung; if <2 rungs survive, NO-TEST.

## Witness, predictions, power — inherited from 5b unchanged

Channels: per (rung, pair, letter) means of v_X=(−1)^{Weyl z}, v_Z=(−1)^{Weyl x}, v_Y=−v_X·v_Z
(Weyl bits from the imported mapping). State-independent bound E[L⊗L]=Tr(Lρ)² ≥ 0.
- **P-A′**: per-channel negativity, rungs n14+n15, one-sided Bonferroni α=0.01.
- **P-B′ (primary)**: S = Σ min(z,0)² all channels all surviving rungs; null by per-shot
  Rademacher sign-flips (10⁵), preserving within-shot dependence; one-sided α=0.01.
- **P-C′**: not evaluable on this stratum (unchanged; no condition-matched per-pair cal).
- **Descriptive only**: per-rung planted-product channel E[Π_{i∈supp(P̂)} v_{P̂_i}] (ideal +1
  for any state stabilizing ±P̂ — state-independent GIVEN P̂, which the pin gate re-verifies)
  as the rung quality meter; and odd-singlet-parity rate. No verdict weight.

## Verdict rules and fences — inherited from 5b verbatim

(GHOST-CLASS-ANOMALY-PRESENT-ON-FEZ / NO-DISTRIBUTED-NEGATIVITY-AT-RESOLVED-SCALE / NO-TEST;
fez-2026, negativity-only witness, positive-sign ghosts invisible by design and unclaimed,
no race quantity touched.)
