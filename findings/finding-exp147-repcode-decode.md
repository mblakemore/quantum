# Finding — Exp147: the campaign GF(2) decoder extends to QEC syndrome decoding; fez is below the repetition-code threshold

**Cycle**: C4833 · **Date**: 2026-07-18 · **Backend**: ibm_fez · **Job**: `d9dctekinv1c73aot06g`
**Code**: distance-d bit-flip repetition code, R=d syndrome rounds, d=3/5/7 × logical{0,1}, 4000 shots/circuit (8000/distance).

## What this rung was for

The roadmap step the C4832 retrospective gated: point the campaign's GF(2) statistical decoder
(Simon 145, Even-Mansour 146) at its native fault-tolerance cousin. Decoding a stabilizer code
is solving H·e = σ over GF(2) — the same machine. This measures whether that machine does real
QEC syndrome decoding on hardware, and how it compares to the standard decoder.

## The one honest reframe (made before results, not after)

Originally posted as a "race vs MWPM." That framing is wrong: **a correct minimum-weight GF(2)
decoder on a repetition code IS MWPM** — min-weight H·e=σ on a 1D space-time chain equals
minimum-weight matching, by math. "Beat MWPM" is unwinnable and vacuous. Corrected to
**validation**: does our GF(2) engine *reproduce* the optimal decoder? That is the honest,
complete answer to "how does it hold up against the standard."

## Results

| d | shots | p_L (MWPM, decoded) | p_L (raw, no decode) | EC reduction | ours==MWPM |
|---|-------|---------------------|----------------------|--------------|------------|
| 3 | 8000  | 0.0121              | 0.1185               | 9.8×         | 0.9956     |
| 5 | 8000  | 0.0181              | 0.2515               | 13.9×        | n/a (intractable) |
| 7 | 8000  | 0.0112              | 0.2729               | 24.3×        | n/a        |

Two clean, honest reads — the load-bearing fact first (Elder framing catch, C4834):

1. **The decoded logical error rate is FLAT with distance — no suppression. fez is below the
   repetition-code threshold** for this circuit and idle configuration. p_L(MWPM) = 0.0121 /
   0.0181 / 0.0112 at d=3/5/7 — not falling with d (d=7 even marginally below d=5:
   non-monotonic, consistent with a per-shot floor plus qubit-set heterogeneity across
   distances). **This was the pre-registered honest outcome** — flat/rising p_L = below
   threshold. Adding distance does not help when the per-component physical error sits above
   the code's threshold.

2. **Error correction works at each fixed distance** — decoding cuts logical error ~10–24×
   below the undecoded observable (9.8×/13.9×/24.3× at d=3/5/7). **Fence, same breath:** that
   ratio *grows* with d only because the RAW baseline worsens (p_L,raw 0.119 → 0.252 → 0.273 —
   longer chain, more physical qubits, more bare error), NOT because the correction strengthens.
   The decoded rate is flat (read #1). "24× at d=7" must not be read as correction improving
   with distance — the load-bearing facts are the flat decoded rate and the absent suppression.

3. **Validation: our GF(2) engine reproduces the optimal decoder — on hardware.** At d=3
   (where exact min-weight-coset enumeration is tractable, 2^10 null space), our engine and
   MWPM agree on **99.56%** of shots; the 0.44% are exact-weight degenerate ties on
   uncorrectable shots (both optimal, arbitrary tie-break — same behavior seen 2000/2000 in
   the selftest weight invariant). The enumerate-and-score move that picked Simon's period
   is, verbatim, a maximum-likelihood syndrome decoder.

## Fences (headline-level)

- **NOT fault tolerance**: offline classical decode, no logical gates, no real-time feedback.
- **Repetition code protects one error type** (bit-flip). It is the standard first hardware
  rung, not a full code — a surface-code patch (both error types, real threshold) is the next step.
- The ~1–2% logical floor is near the measured readout error (E_RO≈1%); part of the residual
  is likely final-readout-dominated, which distance cannot suppress. Single default layout per
  distance — a fingerprint-gated layout (Exp143 idle-hostile-outlier avoidance) could move the
  absolute numbers and is the obvious next lever.

## Where this sits on the roadmap

The roadmap claim was "our GF(2) decoder is already speaking the language fault tolerance needs."
Measured: it decodes a real QEC experiment on hardware and reproduces the ML-optimal decoder.
The gap to fault tolerance is now concrete and physical, not conceptual: **fez is below the
repetition-code threshold** for this configuration. The next rung is to get above threshold
(fingerprint-gated layout, DD on idle data qubits, or a better device) and *then* watch p_L fall
with distance — the real prize, now a measurement with a known obstacle rather than a hope.

## Gates (all passed pre-flight)

Truth-gate selftest: weight-1 corrections 166/166 (MWPM) + 18/18 (ours, d=3); bare-logical
falsifiability (the test can produce a logical error); ours==MWPM 2000/2000 on the min-weight
invariant; textbook suppression in noiseless-model MC (0.011→0.0007→0.0003). Gate-2 under
measured fez noise predicted suppression feasible (idle-over-rounds model ran optimistic, as
flagged pre-flight per the Exp144 lesson — and hardware indeed came in flat, vindicating
measure-don't-trust-the-model once more). Transpile dry-run confirmed mid-circuit measure+reset
on fez, depths 33/75/133.
