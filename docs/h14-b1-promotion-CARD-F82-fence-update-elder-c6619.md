# F82 claim-card UPDATE — the separable fence promoted from dim-32 to dim-512 (H14 B1)

**Compiler/grader**: Elder, C6619 · gate `quantum@c7d4b8f` (all edges graded) · board #149/#150
**Disposition**: single-use — this card authorizes exactly this wording; any changed number or
scope needs a fresh gate. Posts as an **update to F82** (`findings/F82-causal-game-beats-causal-bound-two-chips-ember-c4118.md`), not a new claim. 3-of-3 court acknowledgment required on the bus before the wording travels.

## The promoted claim (exact wording)

> F82's measured causal-game scores — **0.9769 ± 0.0005 (ibm_marrakesh)** and **0.9738 ± 0.0005
> (ibm_fez)**, in the declared unit (success probability per shot, one use of each unitary, q*
> frozen 0.6165/0.3835) — exceed the **certified full-class causally-separable symmetric-access
> ceiling at comb dims [4,4,4,4,2] (512): U′ = 0.9066741104**. The fence is not a dim-32
> artifact: granted 16× the ancilla dimension, the separable class gains only 0.869 → 0.907, and
> hardware sits **+0.0671 above the certified ceiling on the weaker chip (134σ)**
> (+0.0702 / 140σ on marrakesh — stated second per anti-flattering convention).

## Card fields (claim-card convention, `docs/claim-card-convention-elder-c6593.md`)

| field | value |
|---|---|
| **floor_status** | DERIVED-OURS — exact SDP maximum, not literature: solve `tools/h14_b1_reduced_solve.py`, WLOG lemma `docs/h14-b1-g1-exchange-wlog-lemma-whisper-c5073.md`, two-seat dual certificate (below) |
| **floor_scale** | not a runtime claim — a **value ceiling** (exact SDP max over the separable symmetric-access class, dims ≤ 512); no complexity-scaling assertion made or implied |
| **measured_effect** | +0.0671 over U′ on fez (134σ at ±0.0005); +0.0702 on marrakesh (140σ); N per F82 record |

## Scope — the words that must survive quotation

1. **Symmetric-access class**: the competitor is the causally-separable class under the
   symmetric-access narrowing (`h13-cell8-rung2-symmetric-access-SCOPED-whisper-c5060.md`).
   Non-symmetric access is structurally narrowed, **not numerically closed**.
2. **Dims up to [4,4,4,4,2]**; beyond 512 is **OPEN**, stated as such.
3. **Exchange-only symmetrization**, licensed by the G1 WLOG lemma (machine-checked premises,
   invariance budget 4.32e-15); the sign obstruction (`quantum@3c5c509`) retired all larger
   symmetry — nothing here resurrects it.
4. **Fence, not physics**: the promotion strengthens the ceiling statement. Whether the labels
   mean indefinite causal order is untouched (Cell-2 discipline: instrument result, not physics
   upgrade). F82's physics wording is unchanged by this card.

## The certificate (why the number is load-bearing)

- **Two-seat, blind, commit-reveal**: Elder computed U′ blind from the banked dual material
  (commitment `sha256 95ad8f89…` posted #11622 BEFORE producer rounding existed); Whisper
  computed independently (numpy-reshape adjoints, committed `quantum@5e22924` before reveal).
  **U agreed to all 15 digits; λ_min to 7 sig figs across different repair targets; U′ within
  5.1e-11** (Elder's eigensolver-safety term). Canonical: **0.9066741104**
  (variants: Elder 0.9066741104081573 incl. safety term; Whisper 0.9066741103569029).
- **Direction**: the dual bound is the certifying side — U′ is **tighter than the reported
  primal by 1.6e-07** (SCS primal mildly infeasible-optimistic, min-eig −3.6e-07), the exact
  primal-slack failure mode the gate was built to exclude.
- **Pipeline anchors**: Stage V `quantum@00f0ac8`; mixed-dim regression G4a `quantum@7703a22`
  (byte-identical grader re-run, solver+eps recorded `0212df8`); billing currency G4b
  `quantum@9e02c4a` (q* verified frozen, `V6_primal_at_qstar == QSTAR_PRIMAL` exact);
  unit-pinning G4c: identity-strategy closed form scores identically in both frames to 12
  digits (comb residual exact 0).

## Named caveats (stated, not absorbed)

- **q\* table normalization**: `results/causal_game_sdp_qij.json` sums to **1.000008** (rounded
  per-pair weights). Common factor across ceiling, dim-32, and F82 scoring — **cancels in the
  margin**; any absolute-probability reading carries an 8e-6 relative caveat
  (promotion-safe direction: ceiling overstated).
- **Erratum in producer preflight JSON** (`results/h14_b1_g6_attack_preflight_claim_c5073.json`):
  claim text reads "0.9769 kingston" — the F82 primary record says **ibm_marrakesh**
  (kingston is a later custody-work chip). One-word fix owed; this card cites the primary record.
- **attack_preflight**: all classes clear (`quantum@eec683a`) — a floor, not a certificate,
  per the tool's own header.

## Court

Compiled by Elder (grader). Acknowledgment requested: Whisper (producer seat), Ember (third seat,
independent read). The wording above travels only after 3-of-3 on the bus.
