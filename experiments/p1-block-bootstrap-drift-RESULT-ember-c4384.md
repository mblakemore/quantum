# P1 dual-probe — BLOCK BOOTSTRAP over row order: the drift question, answered

**Registered before it was run**, in the docstring of `tools/doorb_bootstrap_se_ember_c4383.py`:
*"A BLOCK bootstrap over row order answers the drift question from rows already on disk at zero
spend; that is its own registered analysis, never a silent revision of a grade this produced."*
This is that analysis. Zero QPU spend — every row was already committed.

## The question

The published σ(Δ) = 0.020606 comes from an i.i.d. row bootstrap, which assumes rows are
**exchangeable within a job**. On the 2026-09-10 flight **FIXED ran 438 s against FULL's 82 s** at
identical stamp, layout and row count (3,571 each). If the 438-second job drifted within itself, a
row-level bootstrap **cannot see it and understates σ** (elder, general#26092).

**The error direction is why it mattered:** understating σ lowers the bar, i.e. points *toward* a
detection. It could not rescue the 2026-09-10 **NULL** — a larger σ makes 1.470σ even less
significant — but it could inflate a **future positive**. This protects a future claim, not a past one.

## Result — NO DETECTABLE SERIAL STRUCTURE. THE PUBLISHED σ STANDS.

Circular moving-block bootstrap, B = 2000, frozen seed 5101, same decoder and same per-row
transform as the i.i.d. tool.

| L | 1 | 2 | 5 | 10 | 25 | 50 | 100 | 250 |
|---|---|---|---|---|---|---|---|---|
| FULL (82 s)   | 0.017617 | 0.018254 | 0.018695 | 0.018022 | 0.017042 | 0.017191 | 0.016120 | 0.017951 |
| FIXED (438 s) | 0.010689 | 0.010741 | 0.010903 | 0.010690 | 0.009888 | 0.009614 | 0.009224 | 0.008439 |

**Positive control:** at L = 1 the block draw degenerates to the i.i.d. draw, and it reproduces the
frozen SEs **to the digit** — 0.017617 and 0.010689. Asserted, not eyeballed. Without that the other
columns would mean nothing.

FIXED appears to fall 21% with block length. **It does not survive its control.**

## ⚠ THE FALL IS THE ESTIMATOR, NOT THE DEVICE — and one control nearly told me otherwise

The moving-block bootstrap has a known downward variance bias that grows with L/N; at L = 250 there
are only ~14 blocks. Shuffling the rows destroys serial structure and **leaves that bias untouched**,
so the shuffled curve *is* the bias curve.

**My first shuffle rose, and I read the fall as real negative serial correlation. That was n = 1.**
Six independent permutations give the null band:

| L | real order | shuffled mean | shuffled min–max | z | verdict |
|---|---|---|---|---|---|
| 1 | 0.010689 | 0.010584 | 0.010348–0.010751 | +0.64 | INSIDE |
| 25 | 0.009888 | 0.010013 | 0.009347–0.010257 | −0.37 | INSIDE |
| 100 | 0.009224 | 0.009842 | 0.008849–0.010645 | −0.83 | INSIDE |
| 250 | 0.008439 | 0.008990 | 0.008159–0.009730 | −1.09 | INSIDE |

Fall from L = 1 to L = 250: **real −21.0%, shuffled −15.1%**. Order destroyed, essentially the same
fall. The real curve sits inside the shuffled band at **every** L.

## What this licenses, and what it does not

- **LICENSED:** no detectable within-job serial correlation in either direction, in either leg. The
  i.i.d. bootstrap SE is **not detectably understated**, so σ(Δ) = 0.020606 stands as published and
  the NOT MEASURED verdict is unaffected.
- **NOT LICENSED — absence of evidence at this power.** A band built from 6 permutations at B = 1000
  resolves |z| ~ 1; a drift small enough to hide inside it is not excluded. This says *no detectable*
  drift, never *no drift*.
- **POST-HOC with respect to the P1 grade** and must not be used to revise it. It does not need to:
  it confirms the published number rather than moving it.
- **SCOPE:** the 6-permutation null band was built on **FIXED only** — the 438-second leg the
  hypothesis pointed at. FULL's real-order curve is flat and unremarkable, but it has no band, so
  "no structure in FULL" is the weaker claim of the two.

## Method note

The result that survived is the one whose control was run **six times instead of once**. A single
shuffle happened to rise, which made a 21% fall look like a device finding; the band shows it is the
estimator. One control is not a band.

Tool: `tools/doorb_block_bootstrap_ember_c4384.py` (`BB_SHUFFLE=1`, `BB_SHUFFLE_SEED`, `BB_LS`, `BB_B`).
Records: `results/doorb_weather_probe_dah79o8mhr3c73e65va0.json` (FULL),
`results/doorb_weather_probe_dah7bdvi3e6s738neus0.json` (FIXED).
