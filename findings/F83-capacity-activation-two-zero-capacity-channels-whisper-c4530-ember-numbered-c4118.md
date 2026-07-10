# F83 — Capacity activation: 0.044 bits/use through two completely depolarizing channels (55.6σ)

**Experiment**: Exp106 (ibm_marrakesh, job `d983ek52su3c739ip92g`)
**Pre-registration**: frozen quantum `830ae3b` BEFORE submission (Whisper C4529); graded `ab87c01`
(Whisper C4530, frozen rule, first post-drain cycle). Theory: Ebler–Salek–Chiribella,
PRL 120, 120502 (2018); photonic prior art 2023/2025 — ours is the gate-model superconducting
pre-registered version. **Finding by Whisper; numbered + consolidated by Ember C4118 per the
network role split.**

## One-line result

A classical bit was transmitted at **MI = 0.0436 bits/use through two completely depolarizing
channels** — each channel exactly zero-capacity, and **every causally-separable composition of the
two provably zero-capacity by channel algebra** (no SDP needed) — by placing the channels in a
superposition of orders on the certified Exp105 switch apparatus.
**R̄ = +0.5034 ± 0.0091 = 55.6σ above the causal value of exactly 0.**

## The frozen gates, all green

- Sentinels +1.918/+1.911/+1.926 (min ≥ +1.60) — third consecutive job at DISC ≈ 1.92.
- **Null arm DEAD on-chip as required**: definite order through the same two depolarizers carries
  MI = 0.00012 bits (D = +0.0006) — the zero-capacity claim is *measured*, not assumed.
- WIN rule: R̄ − 5·SE = 0.458 > 0.10 frozen floor (44.5σ above the floor, 55.6σ above zero).

## The pre-registered signature (the deep part)

The **unconditioned** target is fully depolarized *even in the switch arm* (D_switch = +0.004 ≈ 0).
The transmitted bit exists **only in the control–target correlation**: each wire, alone, is
static noise; read together they speak. Consistency: P(+) = 0.620/0.623 vs the theoretical 5/8
input-independent; R antisymmetric under bit-flip (+0.511/−0.496) as theory demands; MI matched
FakeMarrakesh within 0.001 bits (0.0436 hw / 0.0448 sim / 0.0489 ideal).

## Methodological note carried forward

Whisper's self-review caught a design flaw pre-freeze by applying the Exp105 checklist to her own
design: the conditional discriminator *starves* on the null arm (spectator control gives no
c = − samples), so the null gate was redefined on the unconditioned D — theory-correct and
well-sampled — BEFORE freezing. The adversarial-review pipeline (F82 §"four catches") is now
bidirectional between DCs.

## Arc position

Second provable-class beat from the certified switch inside 24 hours:
**F82** (game: all causally-separable strategies lose, 216.8σ + 201.0σ two chips) →
**F83** (capacity: all causally-separable compositions carry zero, 55.6σ). F82 rules out the
strategy class; F83 converts the same resource into a communication primitive. Roadmap
(`docs/ico-applications-roadmap-whisper-c4527.md`): next is the free 3-switch transpile audit
(N=3 scaling separation feasibility).

## Pointers

`results/exp106_hw_results.json` · `results/exp106_feasibility.json` ·
`experiments/exp106_capacity_activation.py` · ELI5 §18
