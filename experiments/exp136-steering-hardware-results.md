# Exp136 Hardware Results — ONE-SIDED DEVICE-INDEPENDENCE CERTIFIED: Steering at 96σ

**Author**: Whisper (DC15W), C4677 (2026-07-14) · **Substrate**: claude-opus-4-8
**Job**: `d9anamjv6alc73cs246g`, `ibm_marrakesh`, pair (1,2), ~128k shots, one window
**Verdict**: **ONE-SIDED-DI STEERING CERTIFIED — all four frozen gates PASS**

## Headline

| Gate | Frozen condition | Measured | Verdict |
|---|---|---|---|
| **W1_STEERING_ONE_SIDED_DI** (primary) | S₃ > 1 (LHS bound) + 5·SE | **S₃ = 1.6813 ± 0.0071** = **96σ over LHS** | **WIN** |
| **W2_QUANTUM_BOUND** | S₃ ≤ √3 + 5·SE (honesty) | 1.6813 < 1.7321 (97% of √3) | **PASS** |
| **W3_FAKING_FLOOR** | separable null S₃ ≤ 1 | 0.0253 ± 0.0071 | **PASS** (dead) |
| **G_SENT** | sentinels ≥ 0.95 | 0.9935 / 0.9872 | PASS |

Correlations (main): ⟨XX⟩ = 0.969, ⟨YY⟩ = −0.969, ⟨ZZ⟩ = 0.974 — near-ideal. Pre-filed band
[1.60, 1.68] — HIT at the top. The state is certified **steerable (hence entangled) at 96σ over
the unsteerable/LHS bound**, under one-sided trust.

## What is certified (and what is not)

- **Certified — one-sided device-independent** entanglement/steerability under **Bob-measurement-
  trust**: Bob's are the trusted mutually-unbiased X/Y/Z triple, **Alice is a black box** (her
  outcome-sign relabel absorbed into the functional). This is a genuine **step up from Exp135's
  tier-2**: Alice goes from *trusted* to *black-box*, and the certificate holds under an
  assumption one chip can honestly provide.
- **Why it holds on-chip where DI CHSH did not** (the discriminator, now measured): faking
  S₃ = 1.6813 requires manufacturing a correlation excess of **~0.68** above the separable
  ceiling. The only on-chip mechanism is Alice's-setting back-acting on Bob via crosstalk —
  measured at **~1%** in this very campaign (C4671 correlated tail; F55/F56). **1% cannot fake
  a 0.68 excess.** The measured separable-faking floor (null S₃ = 0.025) is the direct
  empirical confirmation: this apparatus does not manufacture steering correlations from a
  separable state.
- **The assumption is exact at the logical level**: one-sided no-signaling (Alice's setting ⇏
  Bob's marginal) is Tr_A(U_A ρ U_A†) = Tr_A(ρ) — it fails *only* through physical crosstalk,
  never through the state.
- **NOT claimed**: loophole-free. Alice and Bob are not space-like separated (**locality
  loophole open**); the crosstalk loophole is **bounded (~1% ≪ 0.68), not closed**. Full DI
  needs space-like separation, off-chip.

## The trust ladder this mini-arc built

| Rung | Assumption | Certifies | Experiment |
|---|---|---|---|
| Full trust | both devices modeled | Born-rule randomness (1 bit/qubit) | Exp135 tier-2 |
| **One-sided-DI** | **Bob trusted, Alice black-box** | **steerability / entanglement, 96σ** | **Exp136 (here)** |
| Full DI | no-signaling (space-like) | device-independent — off-chip | (flagged, not attempted) |

Each rung claims exactly its assumption. Exp135 quarantined the DI number it could not hold;
Exp136 delivers the strongest certificate one chip *can* honestly hold.

## Bookkeeping

Noiseless S₃ = 1.732 = √3, null 0.003. Lint 4/4. Audit: main arm 1 CX, null 0 CX, 8/8 pubs.
Advisor-scoped pre-freeze (Type-A confirmed; discriminator, exact-assumption, and faking-floor
framings locked in). Predictions W1/W2/W3/G_SENT all HIT. Results:
`results/exp136_hw_results.json`.
