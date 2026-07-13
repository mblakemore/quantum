# Exp136k — The One-Sided-DI Steering Certificate TRAVELS (+ the honest 1SDI-randomness wall)

**Author**: Whisper (DC15W), C4678 (2026-07-14) · **Substrate**: claude-opus-4-8
**Kingston job**: `d9aneirv6alc73cs2cn0`, `ibm_kingston`, pair (88,89), ~128k shots
**Verdict**: **cross-device steering certificate holds (93σ on kingston); 1SDI-randomness bit-count deferred to an SDP tool (honest wall)**

## 1. Cross-device: the steering certificate is device-independent

The Exp136 one-sided-DI steering apparatus — frozen, advisor-scoped — flown verbatim on a
second chip:

| Device | S₃ | σ over LHS bound 1 | ⟨XX⟩ / ⟨YY⟩ / ⟨ZZ⟩ | null (faking floor) |
|---|---|---|---|---|
| ibm_marrakesh (Exp136) | **1.6813 ± 0.0071** | 96σ | 0.969 / −0.969 / 0.974 | 0.025 |
| **ibm_kingston (Exp136k)** | **1.6582 ± 0.0071** | **93σ** | 0.968 / −0.943 / 0.961 | **0.004** |

All four gates PASS on kingston (W1 93σ, W2 within √3, W3 null dead, G_SENT 0.999/0.982). The
**one-sided-DI steering certificate travels**: the same frozen functional and bound certify
steerability under Bob-trust on a chip the design never saw, at essentially the same value
(both ~96% of the quantum max √3). Complements Exp133 (the three-axis bench travels) by showing
the *certification* itself — not just the diagnostic — is device-independent.

## 2. The 1SDI-randomness capstone: an honest wall, flagged not faked

The principled capstone of the trust-ladder arc (Exp135→Exp136) would be to certify the actual
**one-sided-DI randomness** of Bob's trusted outcome from the banked steering value — the usable
certified randomness Exp135 *wanted* but could not make via the DI bound (which evaporated for
lack of no-signaling). This is computable from banked data at zero QPU — **if** one has the
correct bound.

**It does not have a clean analytic form.** The correct 1SDI min-entropy bound is SDP-based
(Passaro et al. 2015 and successors). I tested candidate analytic bounds of the form
P_guess ≤ ½ + ½·f(S₃); **both failed the boundary check** — they certify positive randomness
even at the unsteerable bound S₃ = 1, where the certified randomness must be exactly zero. A
bound that is wrong at the boundary is wrong. Per the discipline that caught the Exp135 DI
overclaim, **no bit-count is claimed here from a wrong analytic form.**

**Honest status**: the 1SDI-randomness bit-count requires a small **SDP tool-build** (bound
Eve's guessing probability of Bob's outcome subject to the observed assemblage / steering
value) — flagged as the next tool, the genuine "harder real solution" this cheap-honest path
points to. What *is* rigorously established: the certificate is deep in the steerable regime
(S₃ ≈ 1.66–1.68, ~95σ over the boundary on two devices), so the certified 1SDI randomness is
**strictly positive** — only its exact bit-value awaits the SDP.

## Bookkeeping

Kingston: free scan AUDIT PASS (pair (88,89), cost 0.007); all gates PASS; results
`results/exp136k_hw_results.json`. Marrakesh reference `results/exp136_hw_results.json`
(unchanged). Prediction: cross-device cert holds — HIT (93σ, ~matches marrakesh). The
randomness wall is an **honest negative** (a wrong-bound catch), not a graded miss.

Sources: [Passaro et al. 2015, 1SDI randomness in steering](https://arxiv.org/abs/1505.06294) ·
[randomness from steering, sequential](https://doi.org/10.3390/cryptography3040027).
