# Exp142b F1: threshold-confirm decoder rule (Elder C6567, grader seat)

*K7 STOP (Whisper #908): my censoring proviso (#903, >1/20 flag) fired pre-emptively — the all-pass
confirm rule censors 72/89/97% at 2% readout. This is a decoder-RULE bug, not a task problem. Fix is
my grader seat (F1). Diagnosis + design verified firsthand.*

## Diagnosis CONFIRMED (all-pass collapses under readout)

parity flip prob per copy p_flip = (1−(1−2e)ⁿ)/2 = 0.075/0.109/0.139 at e=2% (n=4/6/8). The old
ALL-PASS rule accepts the true basis iff all conf checks pass → P = (1−p_flip)^conf =
**0.334 / 0.142 / 0.050** → the TRUE P is REJECTED most of the time on hardware. The 74/696/4421
medians + 100%-correct were **noiseless-only** (readout_err=0). Retired.

## F1 — ADOPT the threshold-confirm rule

Replace all-pass with: **accept basis A iff ≥ τ of conf′ parity checks pass.** (conf′, τ) sized from
the cal block's **MEASURED per-qubit readout q_n** (NOT assumed 2%) as a Binomial hypothesis test:
- true-accept: P(Bin(conf′, 1−p_flip(q_n,n)) ≥ τ) > **99%**
- family-wise false-accept over 3ⁿ candidates: 3ⁿ · P(Bin(conf′, ½) ≥ τ) < **1%**

Representative design at e=2% (frozen values recomputed from measured q_n at grade):
| n | p_flip | conf′ | τ (τ/conf′) | true-accept | family-wise FA | old conf |
|---|---|---|---|---|---|---|
| 4 | 0.075 | 37 | 30 (0.81) | 0.9945 | 0.0077 | 14 |
| 6 | 0.109 | 56 | 44 (0.79) | 0.9939 | 0.0076 | 17 |
| 8 | 0.139 | 78 | 60 (0.77) | 0.9904 | 0.0065 | 20 |

**conf′ is a modest CONSTANT-FACTOR bump** (≈2.6–3.9×) over old conf — readout robustness costs a
constant, the exponential cost stays the 3ⁿ candidate cardinality. **The separation SURVIVES** (Q
stays O(1)); this only fixes the decoder rule. Whisper #908 confirmed.

## F2 — ADOPT worst-case sizing L(n) = 2·3ⁿ + conf′

= full-elimination guarantee (~176/1475/13.2k rows/rep) → kills the position-tail censoring (the e=0
16.5%/6.5% residual: P shuffled late costs up to 2·3ⁿ+conf copies). With F1 (readout-robust,
true-accept>99%) + F2 (position-robust), total censoring <1% ≪ the 1/20 flag.

## Consequences for the card (my earlier pins, corrected)

1. **C1 benchmark RE-SIMMED under the threshold rule at measured readout** = the new benchmark
   numbers. My G1 §1 (74/696/4421) is **superseded** (noiseless). Ember's lane; I grade the re-sim.
2. **Q meter also evaluated under measured readout** (apples-to-apples; O(1) so robust, but confirm).
3. **Growth-trend** uses the new readout-robust medians; ratio = median(new-C1)/median(Q),
   best-known-conditional, fitted exponent w/ CI. Separation intact.
4. **Attack gate UNAFFECTED** — the determinism decoder is a separate decoder on the shots=1 data;
   F1 changes only the honest single-copy confirm rule.
5. **Budget F2 ~296k shots ~35–55s exceeds the 40s quote → Creator-visible re-quote** (standing GO
   was on 40s). Flag for Creator ack before flight.

## Verdict

ADOPT F1 (threshold ≥τ of conf′, sized from measured q_n for true-accept>99% + family-wise<1%) + F2
(L=2·3ⁿ+conf′). Re-sim achievability under the new rule = new benchmark. Court: Ember lands F1 in the
kit + re-sim; Whisper re-runs K7 (censoring<1/20 must now pass); Creator re-quote on the budget; then
emission. My proviso did its job — $0, pre-flight. No IBM submission.
