# The Advantage Annex — Unconventional Paths to a Computing Advantage With a Measurable Classical Counterpart

*Whisper C4969, 2026-07-21, substrate claude-fable-5. Creator directive: "Look over H8 and all of our
previous experiments for anything else that is staring right at us that we haven't noticed — reimagine
the blocks to look for unconventional paths to a quantum computing advantage with a measurable
classical counterpart."*

*Companion to [H8 "The Bridge"](star-trek-horizons-8-the-bridge-whisper-c4968.md). Prior art inside
this repo, re-read this cycle before writing: [bridges-to-compute-advantage (C4522)](bridges-to-compute-advantage-whisper-c4522.md) ·
[the complete answer (C4682)](quantum-advantage-the-complete-answer-whisper-c4682.md) ·
[Bridge B / HLF (C4744)](proposal-hlf-classically-verifiable-family-whisper-c4744.md) ·
[Bridge C / Exp142 proposal (C4745)](proposal-bridge-c-learning-advantage-whisper-c4745.md) ·
[Exp142 advantage qualification (C4762)](../experiments/exp142_advantage_qualification_whisper_c4762.md).
Nothing below repeats those; each item survived a corpus grep before being called new.*

---

## 0. Staring at us, item zero: the record is ahead of its own scoreboard

Before proposing anything new — the biggest unnoticed thing is **a computational advantage the campaign
already measured and never booked.**

**Exp142 WON.** Frozen-grader verdict OVERALL WIN (Elder C6502): the two-copy Bell-sampling learner
identified the sealed hidden Pauli at every rung — measured shot ratios **4.9× / 31.5× / 266.6× /
2417.5×** at n = 4/6/8/10 (quantum meters 8/15/22/34 shots; prefix ratios up to 7,821×) — against an
**unconditional information-theoretic floor** (CCHL + the co-checked (3/2)ⁿ appendix, Elder C6490), with
the classical arm *executed head-to-head on the same chip* and the answer adjudicated by sealed
commitments (3-of-3 reveal verification). Exp144, the m-term Hamiltonian generalization, is airborne.

Yet: the C4682 "complete answer" predates the win and still calls the computational scoreboard open;
`campaign-arcs.md` has no Exp142 row; no F-number was assigned. **The campaign answered the Creator's
question more completely than it has told itself.** First deliverable of this annex ($0): book the
Exp142/144 arc into the scoreboard docs with its fences (sample-complexity currency; tracker-shape
mismatch per C4762 — a *structural* mismatch, not a weakness).

What C4762 also established: the Quantum Advantage Tracker's shape — a **classically-attemptable task,
scored against known answers, supersedable by classical progress** — is the one shape the campaign
still lacks. Every path below is aimed at that shape or at making it computable.

---

## 1. The one-sided ledger — we never built the classical cost map (the missing twin instrument)

**The blind spot**: the campaign's signature move is *pricing before flying* — the attenuation map
gives λ_eff per device, and every pre-registration quotes a predicted signal. But every one of those
instruments points at the **quantum** side of the ledger. The classical side — what a verified solution
costs a named classical machine, in seconds and joules, as a function of instance parameters — has
**never been measured once** in ~200 findings. Without the classical curve, no crossover is computable,
and every advantage conversation is one-handed.

**The instrument ($0 QPU, pure classical metering)**: `classical_cost_map` — CPU-seconds and joules
per verified solution on **our own box** (named CPU, named RAM), for named solver classes:
statevector (cost ~2ⁿ), MPS (cost ~χ², i.e. entanglement-governed), and **stabilizer-rank /
extended-stabilizer (cost ~2^{αT}, i.e. magic-governed)** — swept over n, T-count, and treewidth.
Same fit-and-freeze discipline as the attenuation map. Standing use: every candidate race quotes
*both* predicted curves pre-flight, and the **measured crossover frontier** becomes a first-class,
falsifiable object — the computational twin of F54's wall number.

## 2. The magic we certified but never priced — the hidden-shift race (the tracker-shaped flight)

**The reimagined block**: H6's proudest deliverable is **magic injection** — the fault-tolerant T, the
gate that makes the coded computer universal. Reimagine what T *is* on the classical side of the
ledger: by Gottesman–Knill, Clifford circuits are classically free, and **every injected T multiplies
the best classical simulation bill** (stabilizer-rank ~2^{αT}). The campaign certified magic as a
quantum *resource* and never noticed it is simultaneously a **classical cost dial**. We hold the fuel
gauge; we never priced the fuel.

**The task family (new to this repo — zero grep hits)**: **Roetteler's hidden-shift problem** for bent
functions. Structure: H-layer · phase oracle · H-layer · phase oracle · H-layer → the output is the
hidden shift string **s, deterministically** — a *peak of ideal weight 1*, self-verifying by
construction (grade = does the modal output equal the planted s), no classical simulation needed to
check. Quadratic bent functions give pure-Clifford oracles (classically free); **cubic terms inject
CCZ/T** — the hardness dial is literally the number of magic gates, and the classical bill is the
map's 2^{αT} curve. This is the deterministic-peak cousin of the "peaked-RCS moonshot" Bridge C ranked
and parked (conjectural hardness, ~8% peak visibility): the hidden shift keeps the verifiability and
fixes the visibility (ideal peak 1.0 vs. planted-peak's marginal residue).

**Why it fits this hardware**: width-cheap (n = 24–40 within a 156-qubit Heron), shallow (three H
layers + two diagonal layers; 2q count ~100–200 pre-routing at T ≈ 50), and the peak degrades
gracefully — a peak retaining even a few percent over 2ⁿ outcomes is detected in ~100 shots. Bravyi–
Gosset used *exactly this family* as their classical-simulator benchmark (40 qubits, 48 T gates,
~hours) — meaning at our reachable scale the classical side is **attemptable but expensive: a genuine
two-sided contest whose outcome is not known in advance**, the best possible shape for a
pre-registered race. Credit stated: the task and the simulators are the literature's; the contribution
is the metered, pre-registered, both-arms-executed, energy-audited race under one court.

**The race, and its fences**:
- Both arms metered on named hardware: QPU seconds (+ queue-honest wall time) vs. CPU seconds, **and
  joules per verified solution on both sides** (energy is the second axis, and in some regimes the
  crossover arrives earlier in joules than in seconds — the harness measures both for free).
- Hardness is **best-known-simulator, supersedable** — stated as a *feature*: unlike Exp142's
  theorem-carried floor, this race is exactly the live-leaderboard shape the tracker hosts. A classical
  algorithmic advance beating our booked point is the mechanism working as designed.
- **No supremacy promise.** The deliverable is the measured two-curve crossover map — including the
  honest outcome where the curves don't cross in reach, which would be the classical twin of F54's
  wall measurement and just as citable.
- **Gate**: P0-priced first — λ_eff (+ the H8 λ_ff term if dynamic peak-boosting is used) must predict
  peak survival at the T-count where the classical bill is ≥ minutes; if the map says the peak dies
  first, the measured gap between frontiers is the finding, and no QPU is spent flying a foregone loss.

## 3. The two-copy instrument pointed at ourselves — advantage as infrastructure

Exp142's deeper lesson is being under-used: **the campaign now owns a certified measurement primitive
(transversal Bell sampling) that provably beats every single-copy strategy at learning tasks** — and
the campaign's own daily workload IS a learning task. Every certification we fly estimates
fidelities/observables with single-copy shots. Reimagined: point the advantage at our own bill.

- **The doctor's quantum stethoscope** (Bridge C §5 rung C2, still unflown): entangled-probe Pauli
  channel spectroscopy of the chip itself — device characterization (our home turf, the H8-P7
  "Physical") with a provably-quantum instrument; the classical counterpart is the standard
  probe-and-measure QCVV workflow *we ourselves run*, executed same-chip same-window.
- **Two-copy purity/overlap certification**: destructive Bell measurement gives overlap/purity
  estimates that replace whole tomography blocks in our graders — a measured shot-bill reduction on
  the campaign's own certifications, compounding every future flight.

This is the unconventional inversion: not "find a customer for the advantage" but **be the customer** —
the first program whose quantum advantage pays its own QPU bill in saved shots.

## 4. Two smaller paths, named honestly

- **Hidden matching (one-way communication race)**: unconditional Ω(√n)-bit classical vs O(log n)-qubit
  quantum, executed both-arms as a resource-counting demo (F107's QRAC is the n=2 rung; flagged in
  Bridge C alternatives, never developed). Width-cheap, shallow, modest measured factors (~4–8× at
  n=64). Fence: same-chip "communication" is resource-counting, not spatially-separated comms (F115
  no-signaling lesson applies to the framing).
- **Joules-per-solution as a standing column**: add energy metering to *every* future race harness
  (near-zero cost, one more logged number both sides). The field argues about it; we can just measure it.

## 5. Recommended order (all pre-QPU items first)

1. **Book Exp142/144** into the scoreboard + arcs docs with fences ($0, docs — the record should tell
   itself the truth).
2. **Build the classical cost map** ($0 QPU; CPU/energy metering harness + three named simulator
   classes; freeze the fit like the attenuation map).
3. **$0 scout the hidden-shift race**: bent-function circuit generator, T-count dial, noiseless +
   FakeFez peak-survival vs λ_eff prediction, classical bill from item 2 → **go/no-go with both curves
   on one plot** before any spend.
4. **Fly the race** only if the scout shows a live contest (either verdict citable).
5. **Stethoscope / two-copy self-certification** after Exp144 lands (its theorem-conditions check is
   the gate, per Bridge C §5).

---

*Fences repeated once, plainly: Exp142's win is a sample-complexity advantage (booked as such); the
hidden-shift race is a best-known-simulator engineering race (supersedable by design, and said so);
nothing here claims a brute-force speedup — F54's wall stands. Every path above was grepped against
the corpus this cycle; item 0 is bookkeeping, items 1–3 are new to the repo, item 4 develops a named
parked lead. Contact: Mike Blakemore (§12, H7 synthesis).*
