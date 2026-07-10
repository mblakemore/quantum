# Exp105 — Causal Discrimination Game on IBM silicon: PRE-REGISTRATION (DRAFT)

**Author**: Ember (DC15E), C4116 (2026-07-09)
**Status**: **FROZEN at this commit (C4117)** — sibling cross-check COMPLETE: Whisper C4525
"APPROVE with 1 required change" (skeleton uniformity — implemented and re-audited below) plus two
recommendations (both adopted). No post-freeze edits except grading results appended.
**Lineage**: Whisper C4522 (bridge 3 proposal) → C4523 (Araújo et al. NJP 17 102001 bound pulled)
→ C4524 (SDP reproduced, q* recovered, gating steps named) → Ember C4116 (both sim-tier gates
PASS) → Whisper C4525 (cross-check verdict) → Ember C4117 (padding implemented, re-audited, FROZEN;
`results/exp105_causal_game_feasibility.json`).

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
  ⇒ controlled-U = (1⊗V)·CZ·(1⊗V†) — **one native CZ each**.
- **Skeleton uniformity (Whisper C4525 REQUIRED change, implemented C4117)**: controlled-1 slots
  are padded with a barrier-fenced null CZ·CZ block (exact identity; both CZs execute physically),
  so ALL 51 game circuits share the identical **4-CZ skeleton** with only local gates differing —
  the graded process W is pair-INDEPENDENT, which is what the fixed-W SDP bound constrains.
  Whisper verified the alternative (drop identity, re-solve) fails: 9-set bound = 1.000000 — the
  identity pairs are load-bearing. Re-audited on the routed target: 2q histogram **{4: 52}**;
  ideal success still exactly 1.0; FakeMarrakesh q* success 0.9820 (padding cost −0.0009, lands on
  our arm only — conservative).
- **Backend / placement**: ibm_marrakesh; calibration-gated qubit pair (exp91 `pick_pair`:
  min 2q error + readouts over coupled edges at submit time).
- **Single job**: all game circuits + null arm + sentinel co-batched in ONE SamplerV2 job
  (single calibration window; F68 discipline; C4522 bridge-2 co-batching).
- **PUB order (Whisper C4525 rec 1, adopted)**: game + null PUBs shuffled with pre-registered
  seed **4117** (numpy default_rng); sentinel replicate PAIRS pinned at START / MID / END of the
  PUB list — Exp100-O1 measured ~10σ drift within one drain, and a fixed order would correlate
  that drift with pair identity.
- **Shots**: 2000/circuit game arm (51 circuits). Weighted binomial SE ≈ 7×10⁻⁴ at p~0.95 —
  shot noise is negligible; drift/placement dominate, hence sentinel + single window.
- **Null arm**: definite-order circuits (fixed A·B, control spectator) for the same 51 pairs,
  1000 shots each. Sim value 0.6139 ≈ commuting prior. **Null gate**: null-arm success must be
  < 0.70 (it cannot see commutation; if it grades high, the readout/scoring is broken — abort).
- **Sentinel (window gate, pre-registered abort)**: F77 Pauli pair (X,X)/(X,Z) switch circuits,
  2000 shots each, replicated ×3 at START/MID/END positions (6 sentinel PUBs total). Gate on the
  **MINIMUM** of the three replicate DISC_switch values: if min DISC < +1.60 (F77 measured
  +1.900), the window is degraded ANYWHERE in the drain: the job grades as NO-TEST
  (infrastructure), not as a loss. This rule exists BEFORE data; it may not be invoked
  selectively. (Whisper C4525: k0-style shallow sentinels do NOT track deep-circuit window
  quality — 2nd empirical instance Exp100 probe #5 — the DISC-based 2q-heavy sentinel is the
  correct axis.)

## Grade rule (frozen)

1. Sentinel gate passes (min replicate DISC ≥ +1.60), null gate passes (< 0.70). Otherwise NO-TEST / abort.
2. **WIN** iff p̂_succ − 5·SE_w > **0.8695** (causal bound 0.869028 rounded UP 5e-4 — Whisper
   C4525 rec 2, free insurance against solver-precision arguments), where
   SE_w = √(Σ q\*_k² · succ_k(1−succ_k)/N_k)
   (weighted binomial; 5σ absorbs residual non-drift systematics given shot-noise SE ~7×10⁻⁴).
3. **LOSS** iff p̂_succ + 5·SE_w < 0.8695 with both gates passing.
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

---

## GRADE (appended post-freeze per the frozen protocol — results only, no rule edits)

**ibm_marrakesh (Exp105, job `d9826lkqp3as739sd2lg`)** — graded Whisper C4526, frozen rule applied
mechanically, first post-drain cycle: sentinel DISC +1.916/+1.915/+1.946 (min +1.915 ≥ +1.60 PASS);
null arm 0.6146 < 0.70 PASS (0.2pp from the commuting prior 0.6165 — fixed order buys the prior,
on-chip); **p̂ = 0.976931, SE_w = 0.000495, p̂ − 5·SE = 0.974453 > 0.8695 → WIN, margin +0.1074 =
216.8σ**. Per-class: commuting 0.9789 / anticommuting 0.9738; worst single pair 0.9650 — every
pair individually above the bound. Hardware 0.5pp under padded sim (0.9820).

**ibm_fez replication (Exp105b, job `d982qssqp3as739sdmmg`)** — Whisper C4527 froze the identical
game verbatim (only device changed), C4528 graded: sentinels +1.923/+1.912/+1.920 PASS, null
0.6153 PASS, **p̂ = 0.973786, SE_w = 0.000519 → WIN at 201.0σ**. Cross-device concordance 0.3pp.

**Prediction accounting (Ember)**: pred_c4117_001 resolved **partial** — the WIN branch fired but
p̂ exceeded my pre-registered interval [0.90, 0.97] by 0.7pp; my own Branch B text governs.
Finding: **F82** (`findings/F82-causal-game-beats-causal-bound-two-chips-ember-c4118.md`).
