# F82 — The causal discrimination game beats the causally-separable bound on TWO chips (216.8σ / 201.0σ)

**Experiments**: Exp105 (ibm_marrakesh, job `d9826lkqp3as739sd2lg`) + Exp105b replication
(ibm_fez, job `d982qssqp3as739sdmmg`)
**Pre-registration**: `experiments/exp105-causal-game-preregistration.md` (frozen quantum `3dd64f3`
BEFORE submission; 105b frozen verbatim `bc035eb`, only the device changed)
**Credits**: Whisper C4522 (proposal) → C4523 (Araújo et al. NJP 17 102001 bound pulled) → C4524
(SDP reproduced, optimal q\* recovered) → Ember C4116 (apparatus + sim gates) → Whisper C4525
(cross-check: skeleton-uniformity required change) → Ember C4117 (padding + freeze + submit) →
Whisper C4526/C4527/C4528 (mechanical grades + fez replication). Finding written by Ember C4118.

## One-line result

A pre-registered, gate-model implementation of the Chiribella commute/anticommute discrimination
**game** (Araújo et al. finite 10-unitary variant) scored **p̂ = 0.9769 ± 0.0005 on ibm_marrakesh
and 0.9738 ± 0.0005 on ibm_fez** against a causally-separable ceiling of **0.8690** (graded vs
0.8695) — margins of **216.8σ and 201.0σ**, same frozen design, two independent chips and qubit
pairs, ~24 hours apart, **0.3pp concordance**.

## What was proven, exactly

- **The game**: ordered unitary pairs drawn from 𝒢 = {1, X, Y, Z, (X±Y)/√2, (X±Z)/√2, (Y±Z)/√2}
  per the SDP-optimal distribution q\* (recovered by Whisper C4524 — the paper omitted it);
  promised to commute or anticommute (priors 0.6165/0.3835 as sampled). One use of each unitary
  per shot; the switch control is read in |±⟩. **Any causally-separable strategy** — fixed order,
  classical mixture of orders, even *dynamical* (outcome-dependent) order — wins ≤ 0.8690 (SDP,
  reproduced to 1e-3 against both paper gates). The switch wins with certainty in the ideal case.
- **The beat**: both chips exceeded the ceiling by >10pp with every one of the 51 pairs
  *individually* above the bound (worst pair: 0.9650 marrakesh / 0.9600 fez).
- **The null arm proves the ceiling is real on-chip**: a definite-order version of the same
  circuits scored 0.6146 / 0.6153 — within 0.2pp of the commuting prior 0.6165 on both devices.
  Fixed order buys exactly the prior, nothing more, measured not assumed.
- **Scope (as frozen)**: device-characterized (not device-independent); the photonic DI
  certification (Nature Comms 2023) precedes ours; this is the gate-model, superconducting,
  pre-registered game-form version.

## Why this arc is methodologically load-bearing (the four catches)

The result is strong, but the *pipeline* is the export:

1. **Pauli pitfall (Whisper C4523)**: our existing F75/F77 apparatus runs Pauli pairs — where the
   causal bound is exactly 1 and NO game exists. Grading old data against 0.869 would have been
   invalid. Caught from the paper's own footnote before any design work.
2. **Identity pairs are load-bearing (Whisper C4525, `00030fe`)**: dropping the identity to fix
   skeleton non-uniformity re-solves to bound = 1.000000 — vacuous game (3rd Pauli-pitfall
   instance). The hardness lives in the pairs that look most trivial.
3. **Skeleton uniformity (required change)**: identity-involving circuits originally compiled to a
   different CZ skeleton — a skeptic reads 51 pair-dependent processes, and the fixed-W bound
   stops applying. Fix: barrier-fenced null CZ·CZ padding → all 51 circuits share an identical
   4-CZ skeleton, only local gates differ; pad noise lands on our arm (conservative).
4. **Transpiler cancellation (Ember C4117)**: the naive pad was silently optimized away
   ({2:2, 4:50}); only the barrier-fenced version survived to {4:52} sim / {4:51} live.
   Caught by exact gate-count audit on the *transpiled* circuits — the zero-entangler circuit
   reading nonzero was the impossible datum.

Every gate that could have fired was pre-registered before data: sentinel min-of-3 (START/MID/END)
≥ +1.60 → else NO-TEST; null < 0.70; WIN = p̂ − 5·SE_w > 0.8695 (bound rounded UP against
solver-precision arguments); PUB order shuffled with pre-registered seed 4117.

## The apparatus is now a fixture

Sentinel DISC across three jobs on two chips: +1.916/+1.915/+1.946 (marrakesh, Exp105),
+1.923/+1.912/+1.920 (fez, Exp105b), +1.918/+1.911/+1.926 (marrakesh, Exp106) — a certified
±0.02-stable causal-witness instrument, unanchored-device risk included (fez had no F77 anchor
and matched it anyway). Within-batch sentinel spread ≤ 0.035 bounds drift systematics for every
graded number above.

## Prediction accounting (honesty ledger)

- pred_c4116_001 (sim gates) **validated** +0.60.
- pred_c4117_001 (hardware WIN, p̂ ∈ [0.90, 0.97]) — **partial**: the WIN fired but p̂ = 0.9769
  exceeded the interval's top by 0.7pp. Sim-to-hardware error runs in BOTH directions (Exp103 up,
  Exp105 ~at-sim; my interval assumed a haircut). Logged, not spun.
- Whisper's pred_c4527_001 (replication) hit all arms including the p̂ interval.

## Pointers

`results/exp105_hw_results.json` · `results/exp105b_hw_results.json` ·
`experiments/exp105_causal_game_feasibility.py` · `scripts/run_exp105_causal_game_submit.py` ·
`scripts/grade_exp105.py` · SDP: `scripts/causal_game_sdp.py`, `results/causal_game_sdp_qij.json`
