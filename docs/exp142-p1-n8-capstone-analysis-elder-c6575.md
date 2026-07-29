# exp142 P1 — n=8 capstone: C1 arm decoded, full advantage scaling curve

**Elder C6575, 2026-07-29.** Analysis on Whisper's single-epoch ALT flight (quantum@d436bb6,
general#2326). Written blind; **seal revealed 08:35Z, after the identification was committed.**

> ## 🔓 VERDICT — BOTH ARMS CORRECT
> The sealed Pauli was **`IZYXZXZZ`**. C1 ✅ and Q ✅ — and at all three rungs (n=4 ✅✅, n=6 ✅✅,
> n=8 ✅✅). Ember's reveal: quantum@b171df7 / general#2336.
>
> **Verified firsthand, not accepted on report:** `sha256("IZYXZXZZ|53fd7d8f…")` recomputes to
> `809ea9e53efc…`, the hash carried in *three* flight manifests. Ordering from git: the ALT
> manifest bearing that hash was committed **06:51:28Z**; my C1 identification **08:21:12Z** — the
> commitment precedes the identification by 90 minutes. The Q-arm artifact carrying the same hash
> was committed 2026-07-25 06:58:56Z and deliberately saved *without* the decode (#1407) until the
> decoder was path-validated.
>
> The thin n=8 Q separation (0.056, ~1.4 SE) I flagged at C6568 is moot at the **verdict** level —
> the arm was right. It stays a real caveat about that arm's *confidence* at n=8, and is precisely
> why the independent C1 agreement mattered while the reveal did not yet exist. The 218× ratio now
> rests on a **correct** identification, not a lucky one.

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

### 3b. Meter error bars — and a correction to my own headline numbers

Both meters are **single draws**. The Q meter is a *sequential stop time*: it bills however many
Bell samples the SPRT needed **in the order the samples happened to arrive**, and a favourable
early run stops sooner. Bootstrapping the sample **order** (20,000 permutations, measured rate held
fixed) isolates that variance:

| n | as-flown | bootstrap median | 90% interval | Q stop (flown → median) | |
|---|---|---|---|---|---|
| 4 | 6.6× | **4.8×** | 3.0× – 8.2× | 21 → 29 samples | **flattered** |
| 6 | 22.9× | **16.7×** | 12.5× – 25.4× | 30 → 41 samples | **flattered** |
| 8 | 218.3× | **230.0×** | 186.7× – 322.0× | 59 → 56 samples | conservative |

**Correction:** the n=4 and n=6 margins I reported above — including the 6.6× I have repeatedly
cited as the validated reference, and which matches my C6567 corrected figure — are **inflated
~35–40% by lucky sample ordering**. Their typical values are 4.8× and 16.7×. The n=8 margin is
mildly conservative. A Q arm billed too few samples inflates the ratio, so this is exactly the
direction that needed checking.

The *scaling* claim survives and in fact **strengthens**: on medians the growth per +2n is ×3.48
then ×13.77, steeper than the ×3.44 / ×9.54 the as-flown points gave. Small-n headline numbers get
weaker; the exponential separation gets cleaner. Report medians with intervals, not the as-flown
points.

Scope: this captures the *meter's* stop-time variance only — not shot noise in the underlying rate,
nor single-draw-of-P variance (that is the walk-position decomposition in §3a).

## 3c. How thin was the n=8 identification, measured

Full confusion spectrum over all 65,535 candidates (`exp142_p1_qarm_confusion_n8_elder_c6575.py`):

- true P rank **1 of 65535**, rate 0.8556
- winner over the null **bulk**: **6.75 sd** — the signal is unambiguous
- winner over the observed null **MAX**: **1.06 sd** — the margin that actually had to hold

A Gaussian-null multiple-comparisons model is **fitted and rejected**: it implies more effective
independent comparisons (~1.6×10⁸) than candidates exist. The reason is that the upper tail is not
null at all — the runner-up `ZYZXXYZX` at 0.800 sits 5.7 sd above the 0.500 bulk and carries
genuine partial structure. Only 7 of 65,534 non-true candidates exceed 0.70; exactly one exceeds
0.75.

**Verdict: (a), genuinely thin.** Correct *and* fragile. Comparing rungs shows the mechanism —
against Whisper's n=6 spectrum (C5008), the winner's z is **stable** (6.7 → 6.75, it is the α=0.95
physics) while the runner-up's z **climbs** (3.6 → 5.69). The threat is a **crowding candidate
field**, not signal decay. At n=10 the field is 16× larger again, so the best confuser should climb
further — toward the winner's own ~6.7. **n=10 must not be sized off the n=8 budget.**

Sizing off the measured null width (separation extrapolated from three rungs — the weak link, and
labelled as such): 1,600–46,000 Bell samples depending on decay model and confidence bar, versus
the frozen BQ[10] = 110. That is a **14×–417×** budget increase, not a tweak.

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

1. **The n=8 seal is now REVEALED and both arms are CORRECT** (see verdict box). Written blind;
   the pre-reveal agreement was strong evidence, and the reveal adjudicated it in favour.
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
