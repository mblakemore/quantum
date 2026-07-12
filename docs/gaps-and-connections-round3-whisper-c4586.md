# What Are We Still Missing? — Round 3: The Corpus Itself, the Outside World, and the Thermodynamic Ledger

**Author**: Whisper (DC15W), C4586 (2026-07-12), Creator-directed (third full-repo review;
Exp108b `d998ch0tcv6s73dmvqr0` still queued at this commit).
**Relation to prior rounds**: Round 1 (`gaps-and-connections-synthesis-whisper-c4560.md`) hunted
BETWEEN ARCS — it produced the depth-decay law (since validated out-of-sample by Exp108) and
Exp108b (since built and submitted). Round 2 (`gaps-and-connections-round2-whisper-c4563.md`)
hunted UNEXPLOITED BANKED DATA and BETWEEN-REPO transfers — it produced the anisotropy null, and
C4564 executed its top items (FakeMarrakesh+ atlas v1, `design_optimum.py`, the experiments
template). This pass hunts at three levels neither round touched:

1. **The corpus as a dataset** — 115 finding files about the chip; zero findings about the
   findings.
2. **Exports to outside communities** — the causal-inference field, and the open-source tooling
   we depend on.
3. **Theory bookkeeping on already-measured data** — what F86's numbers imply that we haven't
   computed.

Nothing here requires QPU. One item was seeded this cycle (§1's reversal ledger).

---

## §1. The self-replication audit — P3 pointed at ourselves

The ORQ list has carried "P3: replication audit of 3–5 high-citation NISQ claims" for weeks,
aimed at the FIELD. The confirmation-symmetry rule (C4483: audit your own record before anyone
else's) says the first target should be this repo. We now have 115 finding files — and **no
machine-readable answer to "how many of our own findings survived contact with a retest?"**
I tried to compute the corpus's survival rate this cycle by grep; it cannot be done, because
findings carry no status field. That is the gap.

**The seed data exists** — documented reversals/softenings, enumerable by hand:

| Event | What happened | Claim type that failed |
|---|---|---|
| F80 | retracted before running (rescaling, not independent signal) | independence claim |
| Finding 22 → 23 | sign crossover refuted; single-restart artifact | single-run rate |
| Finding 24 (C6347) | seed-locking softened to leaning-stochastic on leave-one-out | correlation magnitude |
| Finding 25 | Exp49's 100% escape non-replicates (±0.10 same-seed spread) | single-run rate |
| Finding 14 (ORQ#7, C4328) | cos² law collapsed on protocol-matched retest (R² 0.971→0.131) | smooth-law universality |
| Finding 12 | X-basis 3× magnitude is marrakesh-specific; ordering generalizes | magnitude (direction survived) |
| F81 | loader depth boundary not stable 11h apart, same circuits/qubits | boundary stability |

**The visible pattern, even in seed data**: what dies is *magnitudes, single-run rates, and
universality claims*; what survives is *directions, orderings, and mechanisms*. Finding 12 states
this within one finding ("take the technique, don't bank on the 3×") — nobody has checked whether
it is a law of the whole corpus.

**Buildable** (v1, zero QPU): a `findings/status-ledger.json` — one row per finding: status
(CONFIRMED-ON-RETEST / UNTESTED / SOFTENED / REFUTED / REGIME-CONTINGENT), claim-type features
(direction vs magnitude vs law; single-run?; sim-only?; hardware-replicated?; restarts≥3?),
retest pointer. Then one afternoon of classification and one regression: **which claim features
predict refutation**. Products: (a) a claim-risk prior that future preregs consult when setting
confidence (the quantitative version of the Finding-23 restart rule), (b) a meta-science exhibit
— "an agent network measured its own replication rate" — which no NISQ group publishes, and
(c) the honest preamble P3 needs before we audit anyone else.

## §2. A causal-discovery stress-test dataset — the Pearl lane's missing *executable* export

The paper argues in theory that the switch sits outside the model class W_sep that classical
causal discovery assumes. The unmade artifact is the **executable demonstration**: take the
banked measured distributions (Exp105 game data, Exp106/107 capacity conditionals, Exp108
thermal conditionals) and feed them to the standard discovery algorithms (PC, FCI, GES —
`causal-learn` implementations). Ground truth: *no definite causal order exists* — the one label
no existing benchmark dataset has. Every published causal-discovery benchmark assumes a true DAG;
ours provably (and now measurably, 216.8σ) lacks one.

Either output is a result: a confidently wrong DAG (the interesting case — WHICH wrong DAG, and
is it stable across our datasets?) or an inconsistency verdict (FCI can emit one; PC cannot).
Package as a public dataset + notebook next to the demos: **a stress test for causal-discovery
software where the right answer is "your premise is false."** Complements the paper with the
thing referees can run; aimed at exactly the community (causal inference) the paper targets, in
their own toolchain. Zero QPU — all data banked.

## §3. The Maxwell-demon ledger — F86's unfinished bookkeeping

F86 measured the refrigeration effect (Δ = 0.1796 ± 0.0085) and the spec states the no-free-lunch
qualitatively (the control qubit's coherence is consumed; measuring it in X is the demon's
erasure cost). **Nobody has closed the ledger with our numbers**: from the measured conditional
populations and control-outcome distribution, compute (in the Felce–Vedral accounting — follow
the paper's definitions, do not invent) the heat moved out of the target per run vs the
Landauer-bounded cost of the control measurement/reset at the same temperatures. One number
falls out: **the measured efficiency of a gate-model ICO refrigerator relative to the demon
bound** — a number that exists for no other platform's implementation (the NMR/IBM-cloud priors
report the effect, not the ledger). It also connects the switch arc to the repo's own
thermodynamic-necessity framing (Landauer) — currently a rhetorical link, made quantitative.
Zero QPU; closed-form plus banked Exp108/108b data (108b's native-T1 version makes the ledger
*more* interesting: the working fluid is free, the demon cost is not).

## §4. Upstream exports — turn incidents into citable contributions

**4.1 The FakeMarrakesh depth-optimism issue.** The atlas (C4564) now documents ln-optimism
growing +0.04 (shallow) → +0.21–0.31 (deep, observable-dependent) across three independently
flagged incidents. That is a data-backed bug report for the `qiskit-ibm-runtime` fake-provider
maintainers — the atlas table IS the issue body. Cost: an afternoon. Payoff: the finding becomes
citable infrastructure feedback instead of a private grievance, and every future user of the
noise model benefits. (Frame per the atlas: model optimism grows with depth and is
observable-family-dependent; corrections must be sentinel-anchored.)

**4.2 The vacuous-gate linter as a standalone.** The feasibility checker (compute the pure-noise
value of every gate expression at budgeted shots; verify each gate CAN pass and CAN fail) is
buried in the experiments template. Extracted as a small library with the Exp108b defect as its
test case, it is useful to any preregistering experimenter — quantum or not (round 2's §3.1
bar-calibration audit is the same linter pointed at trading thresholds; build it once).

## §5. The Ladder tour — one narrative the repo has never told

Every public surface (README, ELI5, front door) is *result-ordered*. The repo also supports a
*concept-ordered* tour that no page tells: **Pearl's Ladder of Causation, climbed on real
silicon** — Rung 1 (association): the characterization corpus (F1–F27, noise maps, sentinels);
Rung 2 (intervention): the repo's genuine do() experiments (Finding 11's dose-response
gate-count/duration severing; Finding 18's H-gate surgical removal); Rung 3 (counterfactuals):
the prereg discipline itself (frozen predictions are counterfactual commitments); and then the
ending no textbook has — **off the ladder**: the switch, where the causal arrow itself is in
superposition and the ladder's premise fails, measured at 216.8σ. An interactive page in the
existing demo style. Educational export for causal-inference students (the paper's audience,
younger); reuses banked data and existing page infrastructure; my specialist lane end-to-end.
This is the only proposal that re-frames the ENTIRE repo — not just the switch arc — under one
idea.

## §6. Wild cards (named, parked)

- **Policy-commutator note** (macro lane): the switch machinery is a physical study of
  ‖[A,B]‖ ≠ 0 consequences; macro intervention *sequencing* (hike-then-QT vs QT-then-hike) is an
  order-dependence question with the same algebra. Historical macro data is too thin to estimate
  commutators credibly — parked as an essay-grade idea unless Creator wants it.
- **Games as instruments**: the public demos could log anonymized human-vs-causal-bound
  performance (humans playing the discrimination game against the real hardware distributions).
  Static-page infrastructure makes telemetry a real cost; privacy questions are Creator's call.
  Parked.
- **Hidden-order diagnostics (roadmap T2.5) — re-flagged as the most underrated UNEXECUTED
  hardware item**: witness-certifying whether nominally-parallel gates are secretly sequenced is
  pure characterization (zero foundations risk), entirely our apparatus, and feeds the weather
  service. It has sat unexecuted since C4527 while cheaper items kept winning; noted so it stops
  being silently deprioritized.

## §7. Standing queue + recommended order

Items ABOVE this doc in priority (existing commitments, not new gaps): **(0) pearl-bridge v0.3
blockers from Elder's C6443 hinge review** — two blockers (single operative ceiling; σ provenance
/ stat+syst disclosure) — venue-ready after one pass; and **Exp108b grade on return** (frozen
rule). Backlog from prior rounds still open: switch-bench packaging, weather page, memory
sentinel, unified ledger, Φ×ICO (Ember), deep-canary (Elder), sentinel-ledger regime pass.

| # | Item | Cost | Why this order |
|---|---|---|---|
| 0 | Paper blockers + Exp108b grade | zero QPU | pre-existing commitments outrank new ideas |
| 1 | §1 status-ledger + audit v1 | zero QPU | changes how every FUTURE finding sets confidence |
| 2 | §4.1 upstream FakeMarrakesh issue | zero QPU | atlas is ready; cheapest external value |
| 3 | §2 causal-discovery stress dataset | zero QPU | paper companion; do alongside blocker pass |
| 4 | §3 demon ledger | zero QPU | strongest after Exp108b lands (native-fluid row) |
| 5 | §5 Ladder tour page | zero QPU | biggest build; slot into a demos arc |

*Three rounds in, the pattern of the gap-hunt itself: Round 1 found physics (the law), Round 2
found data (the atlas), Round 3 finds epistemics (the corpus's own survival statistics) and
exports (giving the methodology away). That progression is probably the sign the repo's internal
frontier is genuinely well-covered — the remaining value increasingly lives in what we hand to
others.*
