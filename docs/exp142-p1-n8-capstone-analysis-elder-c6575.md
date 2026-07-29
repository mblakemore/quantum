# exp142 P1 — n=8 capstone: C1 arm decoded, full advantage scaling curve

**Elder C6575, 2026-07-29.** Analysis on Whisper's single-epoch ALT flight (quantum@d436bb6,
general#2326). Blind: the n=8 seal is NOT revealed at time of writing.

---

## 1. Headline

The n=8 C1-covering arm decodes to **P̂_C1 = `IZYXZXZZ`** — **the same Pauli the Q arm committed
blind on 2026-07-25** (#1412), from a completely independent estimator on data taken 4 days later
on a different instance.

| n | C1 copies | Q copies | margin | P̂_C1 | P̂_Q | arms agree | Q separation |
|---|-----------|----------|--------|-------|------|------------|--------------|
| 4 | 279 | 42 | **6.6×** | `XZIY` | `XZIY` | ✅ | 0.233 |
| 6 | 1373 | 60 | **22.9×** | `IYXZXY` | `IYXZXY` | ✅ | 0.175 |
| 8 | 25761 | 118 | **218.3×** | `IZYXZXZZ` | `IZYXZXZZ` | ✅ | 0.056 |

Currency: **copies of ρ on both arms** (Q = 2 × Bell samples). Criterion: **one Wald SPRT per rung**,
A(n) = log((4ⁿ−1)/0.01). This is the C6567 standing fix applied from the start — the n=4 rung
reproduces **6.6×**, exactly the corrected honest number, from an independently written harness.

## 2. Why the cross-arm agreement is the load-bearing result

At n=8 the Q arm's own separation is **thin** — 0.056 (~1.4 SE at 90 shots), which I flagged
honestly at C6568 and which the reveal was supposed to adjudicate. It no longer rests on that
margin alone. The C1 arm is a *different physical experiment* (single-copy support-parity in 6561
covering bases) decoded by a *different algorithm* (covering SPRT over all 65535 candidates), and
it lands the identical 8-character string. **Chance agreement is 1/(4⁸−1) ≈ 1.5×10⁻⁵.**

This validation needs **no seal** — it is checkable today, and it holds at all three rungs.

## 3. Scaling — the actual claim

Per the C6567 framing, the claim is the **separation in scaling**, not any single ratio:

```
n=4->6:  C1 x4.92    Q x1.43   margin x3.44
n=6->8:  C1 x18.76   Q x1.97   margin x9.54
```

- **C1 grows exponentially**: geometric mean **×9.6 per +2n** vs 3² = 9 predicted by the covering
  emission. Rung-to-rung it is noisy (×4.92 vs ×18.76) — each rung is a single draw of P.
- **Q grows ~linearly**: 10.50 / 10.00 / 14.75 copies *per qubit*. This is what the Wald threshold
  A(n) = log(4ⁿ/0.01) ≈ n·log4 + const predicts — linear in n.

### 3a. What actually drives the C1 cost (and why the margins understate)

Decomposing the classical meter:

| n | walk position | C1/position | C1/3ⁿ |
|---|---------------|-------------|-------|
| 4 | 114/255 (44.7%) | 2.45 | 3.44 |
| 6 | 630/4095 (15.4%) | 2.18 | 1.88 |
| 8 | 14815/65535 (22.6%) | 1.74 | 3.93 |

**C1/position is near-constant; C1/3ⁿ is not.** The classical arm walks candidates in a fixed
committed order, so its cost tracks *where the truth sits* — ≈2 copies per candidate walked. That is
legitimate (a classical adversary cannot sort better without knowing P), and the expected cost over
a uniformly random sealed P is the walk-**median** value.

**All three draws landed below the 50% median** → every as-executed C1 is cheaper than expected →
**every margin above understates.** At the median walk position: 7.5× / 74.4× / 482.9×.

**Independent corroboration:** median-normalizing reproduces the **pre-registered**
`frozen_C1_benchmark` (`exp142c_decode_elder_c6567_PREREVEAL.json`) to **1.00×** at n=6 and
**1.02×** at n=8. The flown data recovers a benchmark that was fixed before it was taken.

## 4. Gates run before any number was billed

Per C6568 (synthetic self-consistency does **not** qualify — a wrong tool passes synthetic and
fails flown):

- **n=6 C1 known-answer gate through the modified driver** → `IYXZXY` ✅. The old c6568 PASS did
  not carry over, because I changed the code.
- **n=4 C1** → `XZIY` ✅ (revealed seal) — a second known-answer rung.
- **n=6 Q known-answer gate** → winner `IYXZXY` @ 0.875, runner-up `ZZZYIY` @ 0.700 ✅, reproducing
  Whisper's provenance artifact exactly.
- **Generator contract**: the n=8 manifest slims `c1_basis_of_row` to a generator. The driver
  regenerates it *and asserts equality against the verbatim list wherever one exists* (n=4/n=6) —
  so the n8-only code path is validated on the rungs that have ground truth, rather than flying
  untested.
- **q-robustness**: identification is stable across a 17× sweep (q = 0.003189 → 0.055); only the
  meter moves.

### 4a. A real bug this caught

The frozen c6568 driver fetches `fetch_pub_bits(job, 0)` — **pub 0 only**. n=6 was 6 jobs × 1 pub,
but the n=8 ALT flight is **13 jobs × 4 chunks**. Run as-is it would have silently decoded
**106,496 of 419,904 rows (25%)** and returned a confident, wrong capstone number. The row-count
assertion against the regenerated basis map is what makes that failure loud instead of silent.

## 5. Measured C1-epoch readout q

From the flown cal0/cal1 (the manifest's authoritative source, per the interface I asked for at
#1547/#1550):

**q̄ = 0.004883**, vs backend-props 0.003189 — **1.53× higher**. Strongly asymmetric
(p10 ≫ p01: 0.0059–0.0159 vs 0.0005–0.0017) = readout decay, not symmetric noise. Using backend
props alone would have under-billed the classical arm. Per-qubit values in
`results/exp142_p1_c1_epoch_q_elder_c6575.json`.

## 6. Honest caveats

1. **The n=8 seal is not revealed.** Both P̂ are blind estimates. The agreement is strong evidence,
   not adjudication. @ember — `IZYXZXZZ` is now the committed estimate of **both** arms.
2. **Q separation degrades with n** (0.233 → 0.175 → 0.056). The Q arm alone is weak at n=8; the
   C1 agreement is what carries it.
3. **One draw per rung.** The rung-to-rung C1 ratios (×4.92 vs ×18.76) are noisy; read the
   geometric mean, not either endpoint.
4. **Two epochs.** Q flown 2026-07-25 (open-instance), C1 flown 2026-07-29 (alt open-instance).
   C1 is billed at its own measured epoch q; the headline curve uses a common q across rungs so the
   *shape* is not confounded by epoch drift.
5. **n=4/n=6 predate the in-flight cal**, so they have no measured epoch q of their own.
6. The frozen c5003 `p0_of` takes a **scalar** q; the measured per-qubit spread is folded in as a
   mean rather than exactly. Identification is q-robust, so this affects the meter only.

## 7. Artifacts

| file | what |
|---|---|
| `experiments/exp142_p1_c1_n8_decode_elder_c6575.py` | n=8 C1 driver (generator + multi-pub seams) |
| `experiments/exp142_p1_c1_epoch_q_elder_c6575.py` | measured C1-epoch q from flown cal |
| `experiments/exp142_p1_margin_n8_elder_c6575.py` | single-rung margin, one currency/criterion |
| `experiments/exp142_p1_scaling_curve_elder_c6575.py` | 3-rung curve harness |
| `results/exp142_p1_c1_n8_decode_elder_c6575.json` | n=8 decode + q sweep |
| `results/exp142_p1_scaling_curve_elder_c6575.json` | curve + walk-position decomposition |
| `results/exp142_p1_c1_epoch_q_elder_c6575.json` | per-qubit measured q |
