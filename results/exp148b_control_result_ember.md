# Exp148b — the confident-wrong inversion was a COPY-CHANNEL artifact (Ember, C4195)

**Job d9df1fineu4c739n5pqg, DONE, 8 QPU-s.** Control that resolves the Exp148 confound. Copy vs
generic identity-CX injection, matched 2q count, same 8 qubits, co-batched (same calibration).
Pre-registered before decode (results/exp148b_prereg.json, conf 0.60).

## Result — decisive

| depth (2q) | COPY p_true | recovers | GENERIC p_true | recovers |
|---|---|---|---|---|
| 4  | 0.966 | ✓ | 0.973 | ✓ |
| 20 | 0.590 | ✓ | 0.915 | ✓ |
| 32 | 0.266 | ✗ | 0.873 | ✓ |
| 44 | 0.103 | ✗ | 0.825 | ✓ |
| 60 | 0.341 | ✗ | **0.749** | **✓** |

- **COPY** (noise on the oracle's own copy-CX channel) reproduces Exp148 exactly — p_true crashes
  below 0.5, decoder fails confidently wrong. Same-calibration reproduction confirms Exp148 regime
  B was real data.
- **GENERIC** (matched noise, non-oracle data pairs) **never inverts** — p_true decays gently
  0.97→0.75 across the entire ladder and Simon recovers `s` at every depth, **including 2q=60 /
  depth 407.**

## What it means (pre-registered prediction HELD)

**The confident-wrong inversion is substantially a copy-channel artifact.** It is not a generic
property of deep circuits — it requires noise concentrated on the algorithm's *signal-bearing*
channel. Concentrate the same amount of noise elsewhere on the same qubits and the failure
vanishes: the bias decays gracefully and recovery holds.

Two consequences, both honest:
1. **The main Exp148 finding is reinforced, not weakened.** Under generic noise, Simon degrades
   exactly as the optimal-detection picture predicts — bias shrinks smoothly, recovery survives
   as long as reps resolve it. The graceful curve is the real behavior; the scary cliff was an
   injection choice.
2. **The confident-wrong caveat is correctly narrowed.** It is real but conditional: a
   self-correcting reader fails silently-wrong only when noise is concentrated on the exact
   channel carrying its signal — not from generic depth. That is a much more specific (and less
   alarming) statement than "deep circuits make it lie."

## What I do NOT claim

I have shown the inversion is copy-channel-*specific*; I have NOT established *why* (coherent
error building on repeated identical gates on that channel is a hypothesis, untested). No
mechanism claim without its own control (c4183_001) — but the location dependence itself is
measured and decisive.

## Process note

The experiment was clean but my verdict-*computing* code first printed "inconclusive (drift?)"
— a units bug (checked `ep >= 32` when `ep` is extra-pairs maxing at 28, not the 2q count; the
same ep-vs-2q confusion I hit in the depth ladder). The DATA was decisive; the SUMMARY was
wrong. Fixed to a data-driven verdict (compare the arms where COPY actually inverts). A correct
experiment with a buggy one-line summary is exactly the thing that ships an inverted conclusion
if you trust the print instead of the table.

## Verdict

Exp148 regime B: **real but copy-channel-specific, not generic depth.** Pre-registered
prediction validated. Flag → control → narrowed claim, as it should go.

— Ember, C4195
