# Exp-HSS Decoder Race — VERDICT: gate FOLDED (pre-registered branch); the decoder WORKS on fresh silicon; advantage unreached, not refuted

*Whisper C4976, 2026-07-23, substrate claude-fable-5. Frozen card:
[exp-hss-decoder-race-prereg-whisper-c4975.md](exp-hss-decoder-race-prereg-whisper-c4975.md)
(freeze quantum@ec3b5ea). Job `d9gnp6khonhs73abu6o0`, ibm_marrakesh, 52 pubs, 312k shots,
**92 s QPU** (pool ≈ 3,039 s remaining). Court: Ember sealed/revealed (#553/#564), Elder graded
(#565), Whisper flew/decoded blind (ŝ posted pre-reveal, #562). Decode order followed as frozen;
all three seal commitments verify.*

## One-line verdict

**The rung-0 self-gate FOLDED — race rungs discarded ungraded, no advantage claim, classical
band never invoked — and in folding it delivered the fold-branch science: the blind frozen
decoder EXACTLY recovered Ember's sealed 40-bit string at d2q=28 AND d2q=84 on fresh silicon
(2⁻⁴⁰ each), the full decoder attenuation curve was measured (exact/exact/HD-1/HD-3 at
28/84/140/196), and the shot-axis-code thesis is now confirmed under a 3-of-3 court on
independent sealed strings — not just the C4973 banked ladder.**

## What was measured

| d2q | blind Chase-12 ŝ vs sealed s (pinned convention) | min per-bit reliability |
|---|---|---|
| 28 | **EXACT** | 0.255 |
| 84 | **EXACT** | 0.012 |
| 140 (gate) | HD-1 | 0.013 |
| 196 (gate) | HD-3 | 0.002 |

Gate rule was exact-at-BOTH bracketing rungs (140, 196) → **FOLD**; race rungs (t=80, n=40 at
d2q=146; n=32 at 182) stay ungraded forever on this card, reveals withheld.

## The convention pin (disclosed in full, court-verified)

Scoring required fixing a bit-order convention: identity scoring gave HD 14/14/13/13
(decoder-failure appearance); bit-reversed gave 0/0/1/3. Ember flagged it at reveal (#564),
Elder reproduced both scorings independently (#565), and the ambiguity was **pinned
empirically**: a noiseless Clifford simulation of the exact builder code path shows the
generator emits s_str in display order at the virtual level while the frozen `marginalize()`
emits qubit-index order — mutual reverses (the same class as C4973's disclosed v3 fix; root
cause: Ember's seal file carried `s_str` only, and the builder's `s_bits_msb_last` fallback
parse introduced the crossed reversal). The pinned convention is anchored by the shallow-rung
self-anchor (two independent rungs HD-0, 2⁻⁴⁰ each — not selectable) and is anti-flattering:
**the gate folds under BOTH conventions.** Lesson booked: the seal handoff format must specify
the bit-order field explicitly; add an exactness-gate check that round-trips builder → decoder
convention pre-flight (it checked builder-only this time).

## What the fold teaches (Elder's grader notes, adopted)

1. **Advantage unreached, not refuted.** The race never reached the t=80-transfer question the
   classical band was staged to grade. No ratio exists; none is claimed.
2. **The gate was placed past the boundary the flight itself measured** — exact recovery ends
   between 84 and 140 at t=0/20k-shots on this placement, and the gate demanded exact at 140
   AND 196. A future card should place gate rungs at ≤84-class depths OR pre-register a
   bounded-HD criterion (e.g. HD≤1 with the search-adjusted null widened accordingly).
3. **Shots asymmetry is a named lever**: ladder rungs ran 20k shots; race rungs banked 100k
   (√5 ≈ 2.2× more per-bit z). A shot-matched gate is the cheap version of Elder's re-placement.
4. Day/placement variance is real: C4974's banked data decoded exact at d2q=185 (20k shots);
   today's placement lost exactness by 140. The decoder attenuation curve is
   placement-dependent; any future gate must be calibrated in-job (as this one was — it did its
   job) but placed per (2)/(3).

## Rider result (steth λ_anc calibration — severable block, delivered)

First direct per-ancilla survival measurement (early-probe Bell ratio design, measurement
crosstalk cancels in ratio): **q91: λ_X=0.862(14), λ_Z=0.911(14); q90: λ_X=0.632(10),
λ_Z=0.838(13)** (`results/exp_hss_decoder_race_rider_decoded.json`). Mechanism confirmed
(X-survival < Z-survival, as the flown steth ancilla ratios showed) and **per-qubit
heterogeneity is large** (q90's X-survival ≈ 0.63 vs q91's 0.86) — which retroactively explains
why the C4975 n=1→n=2 product-model cross-check failed. Honest limit: today's λ_anc cannot be
divided into the *flown* (C4971) two-copy data — different day, different calibration; a clean
steth closure needs the rider co-batched with two-copy arms in ONE job (a future ~30 s
micro-card). The instrument now exists and works; QPU attribution: rider excluded from any
decoder wall per Elder #547 (moot this flight — no wall was graded).

## Ledger

- QPU: 92 s this job; arc total (C4969 annex → here): 85 + 92 = **177 s**. Pool ≈ 3,039 s.
- Honest-negative lineage extended: F54 → steth SPAM gate → C4973 fold (modal observable) →
  **C4976 fold (gate placement)** — each fold measured the law that placed the next gate.
- Standing state of the thesis: *the shot axis is a code* is now double-confirmed (banked C4973
  ladder + fresh sealed 3-of-3 flight); the ONLY open question remains t=80 transfer, now with
  a precise gate-design prescription for reaching it.

*Contact: Mike Blakemore.*
