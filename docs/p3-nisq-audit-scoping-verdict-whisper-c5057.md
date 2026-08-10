# P3 NISQ Replication Audit — scoping verdict (board #64): broad audit RETIRED (superseded by the field); one narrow hardware leg priced and offered

**Author**: Whisper (DC15W), C5057 · **Substrate**: claude-fable-5 · **Board**: #64. $0 scoping pass; web-verified this cycle.

## The scoping finding: the audit we proposed in C4108 has been published by the field

**Hagar, "The NISQ Trap: Eight Years of Demonstrations the Hardware Was Built to Lose" (arXiv:2607.07530, submitted 2026-07-08)** audits **30+ advantage-class NISQ announcements** and finds every one (a contested exception aside) classically reproduced, shown to rest on classically tractable structure, or closed by a simulability theorem within ~18 months — synthesizing six 2024–2026 theoretical results into the mechanism: *the circuit regions NISQ hardware can run with fidelity coincide with the regions classical algorithms compress* (low effective depth, algebraic structure, geometric locality admit both). Ancillary file enumerates the flagship claims. Canonical worked example verified separately: IBM's 127-qubit kicked-Ising "utility" (Nature 618, 500 (2023)) vs the belief-propagation tensor-network reproduction (Tindall et al., PRX Quantum 5, 010308 (2024)).

**Verdict on P3-as-proposed: RETIRED — redundant.** A 3–5-claim audit by us in 2026 would be a strict subset of a published 30-claim audit with better theory coverage. Running it anyway would be exactly the rediscovery class our tooling exists to prevent, one level up (rediscovering a published meta-result).

## What survives (two narrow items, neither urgent)

1. **The convergence note (recommended, ~1 cycle, $0)**: Hagar's thesis is our own Side-B thesis derived independently from the inside — 122 findings in which every emulate-a-ledger attempt lost to the ledger and every certified survivor sold the absence of one (F106/F107/Hardy/negativity/steering/F101/F75/F122's access-model framing). Our corpus is an *independent, hardware-native, self-audited* confirmation of his pattern, including the one shape he flags as surviving: access-model/learning separations (our F122 family) rather than compute-the-ledger-faster claims. Worth a short repo doc + a possible beyond-the-ladder citation. This is a framing asset for every future claim we publish.
2. **The hardware leg (priced, NOT recommended now)**: the one thing no survey can do — one flagship-class circuit (scaled kicked-Ising, public circuits) flown on our silicon against our own classical arm under our five-class preflight and grading discipline: "the trap, reproduced end-to-end in one place." Museum-grade pedagogy (Dawn exhibit potential), scientifically incremental. Price: ~30–60 QPU-s + a classical-arm build. Sits behind every live physics cell in value; boarded only if the Creator wants the exhibit.

## Disposition
P3 removed from the standing open-questions queue (next-steps doc edit rides the next hygiene pass); board #64 closes with this verdict. The convergence note is offered as a follow-on, not started unbidden.
