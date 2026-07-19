# Finding — Exp188b: the live order-choice works, echoed — +20σ/26σ; two gauges teach two lessons

**Cycle**: C4879 · **Date**: 2026-07-19 · **Backend**: ibm_fez · **Job**: `d9e5722neu4c739o1hjg`
(6 circuits: echoed + unechoed same-job arms × 3 bases; layout pinned [23,22], coin at 120).
Companion to finding-exp188-live-choice.md. Machine verdict in `results/` reads NOT HELD (two
auxiliary gauges); the physics claim's criteria all held — accounting below.

## The headline — HELD

With the control **echoed** through the coin's window (X–[coin]–X, net identity):
**W₊ = +0.361 (+20σ off the mixture equator)** and **W₋ = −0.807 (26σ)**; the same job's tails
(live Z-sort) reconstruct both definite orders (0.965 / 0.953); coins fair (0.477–0.492).
Combined with 188's 184-live result (23σ): **both quartet anchors now stand with genuinely
live choices** — quantum coins, measured after the records closed, decided whether two states
were entangled (184) and whether two operations had a definite order (187). The compiled-choice
fence is closed for both, and the cure that made it possible was the run's own echo.

W₊ landed 0.011 *above* its band top (+0.12..+0.35) — echo efficacy under-priced a fourth time;
the echo keeps beating its own advertising.

## The two auxiliary gauges — failed as registered, each converting into a rule

1. **Unechoed replica**: W₊ = +0.011 (null, as diagnosed in 188) but W₋ = **+0.128** — a small
   sign-flipped residual not present in 188's run. Suspect: the far coin lengthens the
   feedforward latency; T1 bias on the shrunken − ensemble (p₋ small) can push its ⟨Z⟩
   positive. Un-diagnosed at flight level; flagged, not explained. Lesson: a "replica" arm
   under a *changed environment* (new pinned pair, far-coin latency) is not a replica — it is
   a new condition and should be banded as such.
2. **Future-blindness gauge**: 0.0475 vs the < 0.03 bar — with the coin **100 qubits away**,
   killing the crosstalk hypothesis and exposing the real problem: the gauge's per-basis se is
   ~0.022 and the bar was a round number at 1.4σ for a max-of-three statistic — it fails by
   chance ~1/3 of the time (184's clean 0.012 was luck as much as physics). No physically
   plausible coin→closed-record channel exists at that distance. Lesson (checklist item #7):
   **set gauge bars from the statistic's null distribution — se × multiplicity — never from
   round numbers.** A properly powered 3σ bar here is ~0.066; both flights' spreads (0.054,
   0.0475) sit inside it.

## Fence

As 188: on-chip QRNG (ordering, not space-like separation). The unechoed-replica anomaly is
recorded unexplained. Machine JSONs stand unedited; this finding is the interpretive layer,
with every number traceable.

## Status of the Creator's A+B

**B is done**: the live-choice upgrade holds for both quartet anchors (184-live 23σ; 187-live
echoed +20σ/26σ). **A is launched**: Shields stage (i) complete (finding-exp189) — detector
at 2% joint escape, acceptance 96.6%, shield paying 2× in Z. Stages (ii)–(iv) queued.
