# Exp143 — Kingston's Pauli error channel, read by two-copy Bell sampling
**Whisper C4764, 2026-07-17 | job d9clt2cjeosc73fgf07g | 20 Bell pairs (40 qubits), 4 arms × 4,096 shots | Creator directive: "fly it"**

Each shot returns the Pauli syndrome (I/X/Y/Z) of every pair simultaneously — 16,384
direct draws from the chip's joint error distribution. Fingerprint = marginals +
pairwise correlations from the same shots.

## Headline numbers (mean error rate per pair)

| arm | window | mean err | Pauli composition (X / Z / Y) | process-attributed |
|-----|--------|----------|-------------------------------|--------------------|
| R   | none (SPAM floor) | 3.38% | 1.4% / 1.6% / 0.4% | — |
| D1  | 1 µs idle | 6.85% | 1.6% / 4.4% / 0.9% | **+3.5%** |
| D5  | 5 µs idle | 23.18% | 2.6% / 18.4% / 2.2% | **+19.8%** |
| G   | X·X gates | 3.72% | 1.4% / 2.0% / 0.4% | **+0.35%** |

- **Idle noise is dephasing**: the D5 excess is 87% Z-type — textbook phase noise.
  Roughly linear in time (~4%/µs raw idle, no dynamical decoupling).
- **1Q gates are clean**: two X gates add 0.35% total (~0.17%/gate incl. scheduling).

## The real finding: calibration-invisible dephasing outliers

Per-pair D5 error rates span **7% to 96%** — a 13× spread the arm means hide:

| pair (physical) | D5 err | R floor | IBM calibration T2 |
|---|---|---|---|
| **q2–q3** | **95.8%** | 1.6% | 110 / 237 µs — *healthy* |
| **q148–q149** | **65.5%** | 2.5% | 151 / 284 µs — *healthy* |
| q87–q88 | 27.6% | 4.0% | — |
| best pairs (q94-95, q140-141, q49-50) | 7–9% | 2-5% | 208–307 µs |

Published T2 (echo-based) predicts 2–5% dephasing at 5 µs for **every** one of these
qubits. Measured raw-idle error on q2–q3 is **96%** — the phase is fully randomized.
Echo T2 cancels quasi-static noise; raw idle decoheres with T2* (not published) or
suffers coherent Z-drift (frequency offset/Stark). Either way: **these qubits are
idle-hostile while looking calibration-perfect**, and our calibration-gated layout
picker (gate + readout errors) selected them for exactly that reason.

Cross-reference: **q148–q149 flew in Exp142** (n=4 bell_pairs manifest). Idle-window
dephasing of this magnitude on chosen edges is a plausible contributor to the
elevated q_hat we measured there.

## Crosstalk (pairwise correlation excess, D5 arm)

Largest: pairs (79,93)×(94,95) at +1.1pp excess, +4.8σ — physically adjacent lattice
region (93/94/95 contiguous), a genuine neighbor-crosstalk signal. All other
correlations ≤ +1.1pp: joint errors are dominated by independent per-qubit dephasing,
not collective events, at this scale and window.

## Actionable output (the "useful every flight thereafter" part)

1. **Layout pickers must test raw idle, not just gates+readout.** Proposed: this
   4-arm fingerprint (≈16k shots, ~5 QPU-s) as a pre-campaign step; exclude pairs with
   D5-style idle error > 2× cohort median. Would have excluded q2-3 and q148-149.
2. Circuits with unavoidable idle windows on these devices want **dynamical
   decoupling** — the D5-vs-calibration gap is the quantitative case.
3. Re-fly cadence: one fingerprint per calibration cycle turns this from snapshot
   into a stability track (explicitly NOT claimed from this single flight).

## Fences

Single calibration window, one flight — a snapshot, not stability. Process attribution
is arm-minus-reference (linear small-rate regime; fine at these levels except the two
outliers, where the R floor is negligible anyway). Pairwise crosstalk is classically
obtainable at poly cost — the two-copy edge is high-weight joint structure; here the
value is all-statistics-from-one-experiment plus direct error sampling. Coherent-drift
vs stochastic-dephasing on the outliers is not distinguished (needs a phase-sweep arm;
named as the natural follow-up, not flown).

## Provenance

Script `experiments/exp143_noise_fingerprint.py` (selftest 4/4 incl known-truth
injection, which caught an X/Z syndrome transposition pre-flight — untested-path
surface #7, zero shots spent). Raw fingerprint: `results/exp143_fingerprint.json`.
Manifest: `results/exp143_manifest.json`.
