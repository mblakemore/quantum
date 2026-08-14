# Perturbations on our own collision data — what the corpus can still yield at $0 (Whisper C5073)

*Creator prompt (2026-08-14): "can we throw perturbations at existing data to extract info from
our own particle-accelerator collisions?" Answer: yes, and we have already done it once (F103).
This is the inventory scan for what the now-5×-larger corpus supports that we have NOT mined.
No QPU. Every claim below traces to banked data on disk.*

## The metaphor is exact, and the precedent is real
Each SHOT is a collision event; the 238-job custody-rescued corpus (791 MB, this session) is the
event log — 5× larger than a week ago. **F103 is the proof of concept**: it certified
entanglement via NEGATIVE conditional entropy from already-flown data at ZERO shots — new physics
from old collisions, exactly the ask. The question is what other analyses the enlarged log admits.

## The headline seam: the two-copy data is MEASURE-ONCE-ASK-MANY, and we asked once
The F122 / door-b two-copy Bell-sampling data (`doorb_dist_i{1,2,3}_raw_science_n16` +
refly/original: ~72,759 shots × 32 bits EACH, five sealed draws) has a property F122 used for
one number and left otherwise untouched: **two-copy Bell sampling of ρ⊗ρ gives E[∏ⱼ v_{Qⱼ}] =
tr(Qρ)² for ANY Pauli Q from the SAME shots.** F122 read exactly one Q (the sealed weight-12
Pauli's amplitude). The identical events also answer, at $0:

1. **Prepared-state PURITY** tr(ρ²) — a single robust number (the two-copy overlap / (−1)^#singlet
   estimator) quantifying how mixed the sealed state actually got. Never reported. A direct
   prep-quality readout of what the hardware delivered, from data already paid for.
2. **The Pauli WEIGHT-SPECTRUM** — Σ_{|Q|=w} tr(Qρ)² per weight w, Monte-Carlo-sampled (4ⁿ is
   un-enumerable at n=16 but the per-weight mean is estimable). Reveals whether the state's
   magnitude concentrates at the planted weight or carries a **leakage tail** at other weights —
   i.e. WHAT WAS ACTUALLY PREPARED vs the single-Pauli grade's one point.
3. **The ghost's spectral home** — the A2/S4 ghost (cross-copy correlations, measurement-quality-
   linked) was mapped only on the 48 weight-1 probes. The weight-spectrum places it in the full
   picture: is the ghost a weight-1 phenomenon or does it live across weights? Same shots.

## The perturbations proper (HEP-style cuts on the event log)
- **Post-selection cuts**: condition the event set on subsets (herald on a pair's outcome, or on
  sentinel state) and recompute — reveals conditional structure the pooled estimate averages out.
- **Jackknife across the five sealed draws** (i1/i2/i3 + refly + original): leave-one-draw-out
  resampling gives a **systematic-vs-statistical error decomposition** F122's per-draw σ never
  did — the "detector systematics" budget a reviewer asks for on any collision result.
- **Bootstrap the shot log** per draw for the true achieved-precision distribution (vs the
  formula SE), the same way F120's shot-axis re-read the fold's own discarded shots.

## Discipline (the cost of doing it right, stated up front)
Every observable above needs the exact Bell-decode convention. It is NOT re-derived — it is
IMPORTED from the flown-matched A2/F122 decoder that already correctly decoded THESE shots (the
B1-G3 lesson: import the validated path, self-certify, never re-transcribe a convention). The
observables + estimators freeze BEFORE any number is computed (F103/F122 lineage), and a number
on a new observable is not quoted until its estimator passes a known-answer pin. No rushed
session-end estimate — that is the accuracy-two-sided trap (a wrong number on a fresh observable
reads as a real finding).

## Recommendation
This is a frozen $0 extraction worth a dedicated block — the natural F103-successor. Highest-value
first cut: **prepared-state purity across the five sealed draws** (one number each, robust,
convention-pinned by import) — it prices what the hardware actually delivered under the F122 claim
and feeds the ghost picture. Priority: below the live F119 flight and the B1 packet, above new
QPU work, because it is free and the data cannot rot (already banked, retention-safe).
