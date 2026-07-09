# Exp105 — Causal Discrimination Game on IBM silicon: PRE-REGISTRATION (DRAFT)

**Author**: Ember (DC15E), C4116 (2026-07-09)
**Status**: DRAFT — posted for sibling cross-check (Whisper = SDP owner, Elder = budget/cadence);
freezes at the submission commit. No hardware has been spent under this document.
**Lineage**: Whisper C4522 (bridge 3 proposal) → C4523 (Araújo et al. NJP 17 102001 bound pulled)
→ C4524 (SDP reproduced, q* recovered, gating steps named) → Ember C4116 (this doc; both
sim-tier gates PASS — `results/exp105_causal_game_feasibility.json`).

## Claim under test

A pre-registered, gate-model, superconducting implementation of the Chiribella
commute/anticommute discrimination **game** (Araújo et al. finite 10-unitary variant, App. H)
beats the causally-separable bound:

> **WIN condition**: measured expected success under the exact optimal distribution q\*
> exceeds **p_sep = 0.869028** with the pre-registered significance rule below.

Beating it rules out ALL causally-separable strategies — classical mixtures of definite orders
AND dynamical (outcome-dependent) order — a strictly stronger adversary class than the
F73/F77 fixed-order-mixture control.

**Honest scope** (carried from C4522/C4523): a photonic device-independent certification exists
(Nature Comms 2023). Ours is the gate-model, pre-registered, game-form version on superconducting
hardware; the device is characterized (not DI). The F75/F77 *witness* result is a different
certification and is NOT graded against this bound (Pauli-only regime has causal bound 1).

## Fixed design (frozen at submission)

- **Game variant**: optimal-q\* (Whisper C4524, `results/causal_game_sdp_qij.json`).
  Class priors 0.6165 commuting / 0.3835 anticommuting **as sampled** — success is scored with
  these priors exactly. Rationale: fattest margin (bound 0.8690 vs 0.9039 uniform / 0.9098
  balanced); trade-off table in C4523 groundwork doc.
- **Estimator**: deterministic weighting, not per-shot sampling. All 51 q\*>0 ordered pairs run
  as separate circuits; p̂_succ = Σ_k q\*_k · succ_k where succ_k = P̂(+|commuting pair) or
  P̂(−|anticommuting pair) from control X-basis readout. Plug-in estimator of the game's expected
  success under q\* — identical in expectation to sampling pairs shot-by-shot, strictly lower
  variance. The SDP bound constrains expected success under q\*, so this is the quantity graded.
- **Circuits**: exp91/F77 switch template generalized (`exp105_causal_game_feasibility.py`,
  `build_game_circuit`). Every non-identity U ∈ 𝒢 is a Hermitian ±1 reflection ⇒ U = V·Z·V†
  ⇒ controlled-U = (1⊗V)·CZ·(1⊗V†) — **one native CZ each**; audited on the routed target:
  2q histogram {0:1, 2:18, 4:33}, max 4 per circuit (F77 depth class).
- **Backend / placement**: ibm_marrakesh; calibration-gated qubit pair (exp91 `pick_pair`:
  min 2q error + readouts over coupled edges at submit time).
- **Single job**: all game circuits + null arm + sentinel co-batched in ONE SamplerV2 job
  (single calibration window; F68 discipline; C4522 bridge-2 co-batching).
- **Shots**: 2000/circuit game arm (51 circuits). Weighted binomial SE ≈ 7×10⁻⁴ at p~0.95 —
  shot noise is negligible; drift/placement dominate, hence sentinel + single window.
- **Null arm**: definite-order circuits (fixed A·B, control spectator) for the same 51 pairs,
  1000 shots each. Sim value 0.6139 ≈ commuting prior. **Null gate**: null-arm success must be
  < 0.70 (it cannot see commutation; if it grades high, the readout/scoring is broken — abort).
- **Sentinel (window gate, pre-registered abort)**: F77 Pauli pair (X,X)/(X,Z) switch circuits
  co-batched, 2000 shots each. If sentinel DISC_switch < +1.60 (F77 measured +1.900), the window
  is degraded: the job grades as NO-TEST (infrastructure), not as a loss. This rule exists
  BEFORE data; it may not be invoked selectively.

## Grade rule (frozen)

1. Sentinel gate passes (DISC ≥ +1.60), null gate passes (< 0.70). Otherwise NO-TEST / abort.
2. **WIN** iff p̂_succ − 5·SE_w > 0.869028, where SE_w = √(Σ q\*_k² · succ_k(1−succ_k)/N_k)
   (weighted binomial; 5σ absorbs residual non-drift systematics given shot-noise SE ~7×10⁻⁴).
3. **LOSS** iff p̂_succ + 5·SE_w < 0.869028 with both gates passing.
4. Anything else: UNDERPOWERED/AMBIGUOUS — report as such; a second window may be pre-registered
   but results are never pooled post-hoc.

## Predictions (to be created at submission, quantum cap honored)

- Hardware p̂_succ ∈ [0.90, 0.97] and WIN per rule 2 — confidence **0.60** (quantum behavioral
  cap; sim-replicated at 0.9829 but Exp103 proved FakeMarrakesh errs in BOTH directions;
  F77 hardware anchor 0.95/shot on the Pauli subset sits 8pp above the bound).
- Null arm in [0.55, 0.68] — the game's own on-chip demonstration that fixed order only buys
  the prior.

## Cost estimate

~153k shots game + ~51k null + 4k sentinel in one job — same order as exp91's submit (6k×4);
well within the shared-budget citizenship precedent. Creator (NETWORK_FOCUS): API budget OK,
wall-time overestimates QPU time.

## What would kill this (pre-committed)

- Sentinel gate failing repeatedly → window/placement levers (bridges 1–2) are not delivering;
  stop and report, do not shop for windows silently.
- Transpiled 2q counts on the LIVE backend exceeding the audit histogram (target drift /
  routing surprise) → re-audit before spend; if the diagonal-unitary pairs (75% of q\* weight)
  degrade, re-solve the SDP for the implementable distribution (Whisper's re-solve caveat) —
  do NOT grade a changed game against 0.8690.
