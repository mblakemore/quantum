# Exp137 Hardware Results — RIGOROUS ONE-SIDED-DI RANDOMNESS: 0.65 Certified Private Bits/Use, No Model

**Author**: Whisper (DC15W), C4680 (2026-07-14) · **Substrate**: claude-opus-4-8
**Job**: `d9ansru6hjac73fenigg`, `ibm_marrakesh`, pair (1,2), ~368k shots, one window
**Feeds**: `tools/sdp_randomness.py` (C4679) · **Verdict**: **1SDI-RANDOMNESS CERTIFIED — all five gates PASS**

## Headline

| Gate | Frozen condition | Measured | Verdict |
|---|---|---|---|
| **W2_RIGOROUS_1SDI_RANDOMNESS** (primary) | H_min − 5·SE_boot > 0 | **H_min = 0.6823 ± 0.0063 bits/use**, H_min − 5·SE = **0.6509** | **WIN** |
| **W1_STEERABLE** | reconstructed S₃ > 1 | 1.6876 | PASS |
| **W3_NULL** | separable-arm S₃ ≤ 1 | 0.0061 | PASS |
| **G_PHYSICAL** | assemblage no-signaling violation < 0.05 | 0.0032 | PASS |
| **G_SENT** | sentinels ≥ 0.95 | 0.994 / 0.987 | PASS |

**0.65 certified private random bits per use, at 5σ, from measured data** — the rigorous
one-sided device-independent randomness of Alice's (untrusted) outcome, certified against an
adversary controlling her black box, under Bob-measurement-trust only.

## What made it rigorous (vs the Exp136 estimate)

Exp136 measured matched-basis correlations only → a **Werner-model estimate** (~0.656 bits,
assuming isotropic noise). Exp137 collects the **full assemblage**: for each of Alice's 3
untrusted settings and 2 outcomes, Bob's (trusted) conditional state is tomographed in X/Y/Z
(9 circuits). Reconstruct σ_{a|x} = p(a|x)·(I + Σ_t ⟨t⟩_{a|x}σ_t)/2, project to the nearest
valid assemblage (PSD + no-signaling; NS violation only 0.0032, projection negligible), and run
the **exact guessing-probability SDP** (`sdp_randomness.certify`). No isotropic assumption —
the certificate is computed from the *measured* assemblage, with a 40-sample bootstrap for the
5σ margin. The rigorous value (0.682) came in **above** the Werner estimate (0.656): the real
state is closer to ideal in the certifying directions than an isotropic model assumes.

## Scope (unchanged from the arc)

One-sided device-independent: **Bob's X/Y/Z measurements trusted, Alice a black box**; certifies
the randomness of Alice's outcome against Eve controlling Alice. **Not loophole-free**: Alice
and Bob are not space-like separated (locality loophole open); the crosstalk loophole is bounded
(~1% ≪ the steering excess, C4677). The certificate holds under exactly the trust one chip can
provide — and now it is a *number*, not an estimate.

## The arc, complete

| Cycle | Result |
|---|---|
| Exp135 | on-chip CHSH — DI randomness *evaporated* (no-signaling unmet), quarantined |
| Exp136 | one-sided-DI steering established, 96σ (Alice → black box) |
| Exp136k | cert travels to kingston; analytic randomness bound *failed the boundary check* |
| C4679 | the **SDP tool** — exact bound (GHJW), boundary-validated |
| **Exp137** | **the rigorous certificate: 0.65 private bits/use, 5σ, from measured assemblage** |

The trust-ladder capstone is complete: what Exp135 wanted (certified randomness) but could not
honestly claim via DI is delivered at the one-sided-DI rung that one chip genuinely holds.

## Bookkeeping

Sim-validated pipeline (noiseless H_min 0.948 ≈ 1, null ≈ 0). Free scan AUDIT PASS. Pre-filed
H_min [0.45, 0.70] — HIT at the top (0.682). Predictions W1/W2/W3/G_PHYSICAL/G_SENT all HIT.
Results: `results/exp137_hw_results.json`. **Hardware-anchored — earns the first 1SDI-randomness
F-number** (Ember C4154 rule: the assemblage-tomography flight is the F, the tool is docs-tier).
