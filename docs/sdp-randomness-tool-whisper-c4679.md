# The 1SDI Randomness SDP Tool — the correct bound the analytic forms couldn't give

**Author**: Whisper (DC15W), C4679 (2026-07-14) · **Substrate**: claude-opus-4-8
**Tool**: `tools/sdp_randomness.py` · **Validation**: `results/sdp_randomness_validation.json`
**Directive**: Creator — "build the SDP randomness tool" (the wall Exp136k flagged).

## What it is

An **exact** semidefinite program for one-sided device-independent (1SDI) certified randomness
of the untrusted party's outcome, from a steering assemblage on a **trusted qubit**. It closes
the C4678 wall: my candidate *analytic* bounds certified randomness even at the unsteerable
boundary (where it must be zero), so they were wrong; the correct object is this SDP.

**Why it is exact here (no NPA hierarchy):** by the GHJW / Schrödinger–HJW theorem, a qubit
assemblage is quantum-realizable **iff** it is PSD and no-signaling — precisely the SDP
constraints. So for a trusted-qubit Bob the guessing-probability SDP is tight, not a relaxation.

```
maximize   P_guess = Σ_e Tr[ σ^e_{e|x*} ]          (Eve guesses Alice's outcome at x*)
over       σ^e_{a|x}  (2×2 Hermitian)
s.t.       Σ_e σ^e_{a|x} = σ_{a|x}   (reproduce the observed assemblage)
           σ^e_{a|x} ⪰ 0             (PSD)
           Σ_a σ^e_{a|x} indep. of x (no-signaling per Eve-branch)
H_min = −log₂ P_guess.
```
(Passaro–Acín et al., NJP 17 113010 (2015), adapted; cvxpy + SCS.)

## Validation — it passes the boundary the analytic bounds failed

Werner state ρ_v = v|Φ⁺⟩⟨Φ⁺| + (1−v)I/4, n=3 trusted MUB (X,Y,Z):

| v | S₃ | H_min (bits) |
|---|---|---|
| 1.00 | 1.732 (=√3) | **0.999 ≈ 1** |
| 0.95 | 1.645 | 0.554 |
| 0.90 | 1.559 | 0.381 |
| 0.80 | 1.386 | 0.152 |
| 0.70 | 1.212 | **0.000** |
| 0.577 (=1/√3) | 1.000 | **0.000** |

**BOUNDARY CHECK: PASS** — H_min = 0 at the unsteerable bound (S₃=1) and ≈1 at the pure Bell
state (S₃=√3). n=2 (X,Z) validated identically (threshold v=1/√2, S₂=1). The tool also
correctly reproduces the known Passaro feature that the **randomness threshold exceeds the
steering threshold**: states with S₃ ∈ [1, ~1.3] are steerable yet certify *zero* randomness —
a nuance no naive monotonic S→H_min bound (mine included) can capture, and the concrete reason
the SDP was necessary.

## Applied to the campaign's steering data (Werner-model estimate)

| Device | S₃ (measured) | Werner v | H_min (SDP) |
|---|---|---|---|
| marrakesh (Exp136) | 1.6813 | 0.971 | **0.656 bits/use** |
| kingston (Exp136k) | 1.6582 | 0.957 | **0.587 bits/use** |

**Scope, explicit**: these are **Werner-model estimates** — they map the measured steering
scalar to the isotropic-noise state with the same S₃, then run the SDP. The *rigorous*
per-device number requires **assemblage tomography** (Bob's X/Y/Z conditional states for each
of Alice's outcomes and settings), which Exp136 did not collect (it measured matched-basis
correlations only). The tool is **ready to consume** that richer data — a cheap one-job
follow-up flight (assemblage tomography on the Bell pair) would turn the ~0.6-bit estimate into
a rigorous 1SDI certificate.

## The arc this closes

Exp135 (on-chip CHSH — DI randomness *evaporated*, no-signaling unmet) → Exp136 (one-sided-DI
steering established, 96σ) → Exp136k (cert travels; analytic randomness bound *failed the
boundary check*) → **this tool** (the exact SDP bound, validated). The trust-ladder capstone now
has its correct instrument; the only remaining step to a rigorous on-silicon 1SDI randomness
*certificate* is feeding it assemblage-tomography data. The honest path reached the real tool.

**Reusable**: `from sdp_randomness import certify; certify(assemblage, x_star, dirs)` returns
{P_guess, H_min_bits, S_n} for any qubit steering assemblage — an operational capability for the
campaign's certification arc, not a one-off.
