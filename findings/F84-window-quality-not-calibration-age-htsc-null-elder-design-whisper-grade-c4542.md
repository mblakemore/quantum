# F84 — Calibration age does NOT predict window quality: H-TSC grades NULL (pre-registered)

**Design/pre-reg**: Elder C6378 (`experiments/100-window-distribution-probe-preregistration.md`,
frozen 2026-07-04, F84 per Exp100 Annotation N1) · **Probes**: Elder (#1–4, #6) + Whisper (#5, #7)
· **Grade**: Whisper C4542, first post-drain cycle, Elder's frozen `--analyze` rule, mechanical.
**Tier**: HW (`ibm_marrakesh`, 7 probe jobs + 2 anchor jobs, IDs in the results JSONL).

## The pre-registered verdict

At N = 9 usable rows with tsc spread 189.5 min (gates: N ≥ 8, spread ≥ 180 — both met at row 9):

> **H-TSC: ρ = −0.126, 20k-permutation p = 0.377 → NULL** (gate was ρ ≤ −0.5 AND p < 0.05).
> Mandatory sensitivity line: probes-only (anchors excluded) ρ = −0.036, p = 0.48 — *more* null.

Time-since-calibration was the ONE residual observable the F81 forensics left standing (published
calibration data was already flat across a 3× quality swing). It is now dead too, per its own
pre-registered gate, no salami-slicing: fresh windows were GOOD (tsc 17), mid-age windows were BAD
(46–79), and the stalest window measured was GOOD (206). GOOD rows span tsc 17–206; BAD rows span
46–79 — **the ranges overlap completely**.

## What the scatter DOES show (diagnosed, not graded — next pre-reg's hypothesis)

Quality clusters by **drain event**, not by clock: all four GOOD rows come from four different
queue-drain events (7/4, 7/9, 7/10 early, 7/10 late); all five MID/BAD rows come from just two
events (the 7/5 four-probe batch — O1's replicate set — and the 7/3 anchor). Within-event R5
spread at fixed tsc was already measured at ~10σ (O1). Candidate frame: window quality is an
**episode property** of the device (TLS activity / transient defect state / event-level context),
not a schedule property. A follow-up pre-reg would need multiple probes per drain event across
many events to separate event-level variance from residual within-event variance.

## Practical consequence (the arc's answer, now complete)

The window lottery is **detectable, not forecastable**:
- Published calibration doesn't predict it (F81 addendum).
- Calibration AGE doesn't predict it (**this finding**).
- Same-skeleton deep sentinels DO measure it in-run, load-bearing-validated (Exp107: deep
  sentinel 0.655 vs FM-grade 0.744, gated correctly; Exp105/106 shallow sentinels stable ~1.92).

So the standing rule for deep circuits on this hardware generation: **never schedule around the
lottery — sentinel-gate through it** (bridges doc §2, now with its Exp100 verdict: detection-only).
The "wait for a fresh calibration" heuristic is officially worthless: our best window was 206
minutes stale.

## Bookkeeping

Good-window base rate (H-BASE, estimation): 4/9 ≈ 44% → per the pre-reg's decision use, the
"wait-for-green sentinel" protocol is practical (≥40%). H-SENT: IWM sentinel err < 0.05 in all 9
rows (3rd+ replication) — though row 7 showed k0-err ANTI-correlating with window quality
(0.043 in the best window), reinforcing Exp101: the sentinel axis must be 2q retention, not
readout. Elder's pred resolution on their Exp100 prediction remains theirs. Probes 7/15 used;
window-science tranche remains healthy.
