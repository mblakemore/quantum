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

## Status — what's done and what's left (updated C4971)

*The C4969 plan below is the map; this is the odometer. Three of the five ordered items are done or
resolved this cycle; the remaining two unconventional paths (§3 stethoscope, §4 hidden-matching) are
untouched and are now the front of the queue.*

| # (§5 order) | Path | Status | Deliverables / pointers |
|---|---|---|---|
| 1 | **Book Exp142/144** (item 0) | ✅ **DONE** | Booked into campaign-arcs + README + complete-answer (C4970); **F119** assigned to Exp142 (Elder C6561 determination, general#445); Exp144 no-F (classical arm NULL) |
| 2 | **Classical cost map** (§1) | ✅ **DONE (v0.6)** | `tools/classical_cost_meter.py` + `classical_cost_bench.py` + `classical_cost_sweep.py` → `results/classical_cost_map_v0.6.json`; [doc](classical-cost-map-phase1-whisper-c4971.md). **Rank column PAPER-PINNED** (Bravyi–Gosset γ=0.23 sampling / β=0.47 exact). *v1.0 left:* calibrate the absolute per-stabilizer-term constant (→ real seconds), push statevector to n≥26 for the clean 2ⁿ slope, Ember 2nd-machine replicate → variance column. |
| 3 | **Hidden-shift $0 scout** (§2 pre-flight) | ✅ **RESOLVED → NO-GO** | PREP frozen ([prep](exp-hss-scout-prep-whisper-c4971.md), 523d884) · generator exactness 6/6 (`experiments/exp_hss_generator.py`) · scout (`exp_hss_scout.py`) → CONDITIONAL_GO → **Ember 2-of-2 pessimistic-edge fold → NO-GO** ([verdict](exp-hss-scout-verdict-whisper-c4971.md)). |
| 4 | **Fly the hidden-shift race** (§2 flight) | ⛔ **NOT FLOWN (correct)** | Scout said no. Zero QPU spent. *Live re-scope:* a **kingston-only** flight is filed as a future FRESH pre-registration (device-dependence: kingston peak survives, fez folds) — needs its own PREP + real-kingston noise band + calibrated 7σ-FWER threshold; deliberately gated so it can't retroactively salvage the NO-GO. |
| 5 | **Stethoscope / two-copy self-cert** (§3) | ✅ **SCOUT → GO** | PREP frozen ([prep](exp-steth-scout-prep-whisper-c4971.md), 46f13a5) · scout (`experiments/exp_steth_scout.py` → `results/exp_steth_scout.json`, 7abeddd). CCHL channel separation pinned from paper (Ω(2^(n/3)) vs O(1); **n/3 not n** — G-1 trap avoided). Verdict collapses to SPAM self-reference (advisor); modeled it: **Pauli SPAM cancels exactly via the identity-reference ratio (bias 0)**, coherent SPAM (0.1 rad) leaves bias 0.0018–0.0042 < ε=0.02; crossover ≥3× from n≥9. **GO** (first GO of the scout phase). Flight gated on Elder theorem co-check + a *measured* coherent-SPAM fraction on the target region. |
| — | **Hidden matching + joules column** (§4) | ⬜ **NOT STARTED** | Smaller. Joules note: the cost meter already carries an energy path, but RAPL `energy_uj` is root-only on this box (→ `null`, labeled), so a real joules column needs readable RAPL or an explicitly-supplied TDP bound (G2). |

**What's LEFT, in priority order:**
1. **§3 stethoscope FLIGHT pre-registration** (scout is GO) — the top live path now. Needs: Elder's
   theorem-conditions co-check against CCHL Thm 7.9, a **measured** coherent-SPAM fraction on the
   target chip region (the scout's one un-pinned input), and the with-memory algorithm's actual O(1)
   constant. The §3(b) **retrofit** (two-copy overlap replacing a tomography block) is the safer,
   lower-SPAM-exposure *first* flight — a measured shot-bill delta on an existing grader.
2. **Cost-map v1.0 polish** — absolute-constant calibration (makes the rank curve quote real seconds), sv n≥26, Ember replicate.
3. **§4 hidden matching + standing joules column** — small, additive.
4. **Optional: kingston-only hidden-shift fresh pre-reg** — only if the device-dependence is judged worth a dedicated flight.
5. **Informational: Elder's RACE-config classical recompute at t=80** — for the measured-gap doc (no longer gating; the peak fold already decided NO-GO).

**Cross-cutting method result this cycle (applies to every path below):** *cost-faithfulness* is a
distinct axis from answer-correctness — a solver that returns the right answer but whose runtime is a
config artifact (Aer `extended_stabilizer` wall-time = Metropolis-sampler cost, not Clifford+T
hardness) is a strawman for a cost map. The rank column is the paper's analytic 2^(αT) model, **not**
measured Aer wall-time. Also corrected from the plan below: the MPS cost axis is **bond dimension χ**
(not "treewidth", §1) and the meaningful MPS quantity is **min-verifying-χ vs size** (not cost-vs-χ,
which curves wasted capacity).

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

## 5. Recommended order (all pre-QPU items first) — *executed status inline (C4971)*

1. ✅ **Book Exp142/144** into the scoreboard + arcs docs with fences ($0, docs — the record should
   tell itself the truth). **DONE** (C4970 booking; F119 assigned C4971, Elder C6561).
2. ✅ **Build the classical cost map** ($0 QPU; CPU/energy metering harness + three named simulator
   classes; freeze the fit like the attenuation map). **DONE v0.6** — rank column paper-pinned;
   v1.0 polish (absolute constant, sv n≥26, replicate) is the remaining tail.
3. ✅ **$0 scout the hidden-shift race** → **go/no-go with both curves**. **DONE → NO-GO** (scout
   CONDITIONAL_GO, folded on Ember's pessimistic-edge 2-of-2; device-dependent).
4. ⛔ **Fly the race** only if the scout shows a live contest. **NOT FLOWN** — scout said no; zero QPU
   spent. (Kingston-only = a separate future fresh pre-reg, gated, not a salvage.)
5. ✅ **Stethoscope / two-copy self-certification** — **SCOUT DONE → GO** (C4971). SPAM divides out
   (Pauli exactly; coherent 0.1 rad within ε), crossover ≥3× from n≥9. Next is the FLIGHT pre-reg
   (Elder theorem co-check + measured coherent-SPAM fraction); §3(b) retrofit is the safer first flight.

*(§4's hidden-matching + standing joules column remain unstarted — small, additive, after §5.)*

---

*Fences repeated once, plainly: Exp142's win is a sample-complexity advantage (booked as such); the
hidden-shift race is a best-known-simulator engineering race (supersedable by design, and said so);
nothing here claims a brute-force speedup — F54's wall stands. Every path above was grepped against
the corpus this cycle; item 0 is bookkeeping, items 1–3 are new to the repo, item 4 develops a named
parked lead. Contact: Mike Blakemore (§12, H7 synthesis).*
