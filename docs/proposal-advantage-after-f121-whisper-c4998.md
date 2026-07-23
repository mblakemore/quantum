# The Advantage After F121 — Point the Two-Copy Instrument at the Channel Calibration Cannot See

*Whisper C4998, 2026-07-23, substrate claude-fable-5. Creator directive: "look over our recent
experiment results, the H arcs, and the data for anything we've missed and see if you can find a
creative way to use our building blocks to achieve a measurable quantum computational advantage over
a classical counterpart." Written while Elder corrects the F121 surfaces (done, quantum@2cb7294,
spot-checked this cycle) and Ember audits F119 (coordination#791 — NOT touched here; this doc only
sequences behind her verdict). Successor to the post-F121 half of the
[advantage annex](advantage-annex-unconventional-paths-whisper-c4969.md); nothing below repeats it.*

---

## 1. What F121's death actually taught (the design rule, stated once)

The red-team (C4996) did not kill a number; it killed a *floor type*. The 1,818 s floor priced
**simulation of our circuit**; the problem's own algebra was poly-time. Generalized:

> **An advantage claim survives the F121 axis if and only if its classical floor is a theorem over
> an access model that the experiment physically enforces.**

Sort every advantage-flavored result we hold by floor type and the pattern is exact:

| Floor type | Enforced by | Our results | F121-axis status |
|---|---|---|---|
| Conjectured hardness of a *published* structure | nothing — adversary reads the structure | F121 (MM hidden-shift) | **DEAD** (41-query algebraic read) |
| Proven lower bound over a **physical access model** | physics: copies, probes, sent bits | F119 (single-copy sample floor)*, F107–F109 (SQL probe floor), superdense/QRAC (bit floor) | Survives — *if* the access model is genuinely closed AND the floor is actually a theorem AND the competitor arm is flown honestly (all three bit F119 — see the audit note below) |
| Proven asymptotic separation, apparatus flown | depth (BGK theorem) | F113/F114 | Survives as apparatus-of-theorem, never claimed as speedup |

*\*Ember's audit **landed** (general#810, `exp-hss-F119-redteam-audit-ember-c4215.md`):
**SUPERSEDED as-executed / QUALIFIED in principle.** The row-2 structure held where row 1
failed — seal PASS, honest-oracle PASS (the k-local marginals are maximally mixed; F121's
read-off attack has no target) — but two *implementation-level* lessons bind every future
row-2 flight, including §2: (a) the (3/2)ⁿ floor was **open, not proven** — cite only
published theorems as floors, and label appendix bounds *best-known / conditional*; (b) the
executed single-copy arm flew 12 shots per fixed basis, a **delivery artifact** that let a
36-copy determinism decoder beat the two-copy arm's 68 copies as-flown — the competitor arm
must draw **fresh randomness per copy (shots=1 per setting)** and both arms must be billed
in the same unit (copies consumed, not measurement events; the 2× Bell-measurement↔copies
inflation was part of the graded ratios).*

The verifiability–hardness tension named in C4996 lives entirely in row 1: a planted, self-verifying
structure is *published* structure, and published structure invites algebra. Row 2 has no such
tension: **nature does not publish its secrets**. The creative move is therefore not a new planted
problem — it is choosing a task whose secret is held by the *device*, not by us.

## 2. The proposal: the stethoscope advantage flight, aimed at the pad-drift

**Fuse the two arcs that closed this week.**

- **Building block 1 — the instrument (F119 genre, §3(a) of the annex):** two-copy / ancilla-assisted
  Choi channel spectroscopy. Floor already pinned from paper and co-checked by Elder 9/9 (CCHL
  arXiv:2111.05881 Thm 7.9): **Ω(2^(n/3)) single-copy experiments vs O(1) with quantum memory,
  unconditional, covering all adaptive single-copy strategies**. Scout says the measured sample
  ratio crosses 3× at n=9 (4×), 8× at n=12, 16× at n=15 — exponentially growing, hardware-reachable
  width (2n qubits). Three confounds already peeled by the C4971 flight arc with fixes in hand:
  non-Pauli T1 → twirl; placement → pin; ancilla survival → **calibrate λ_anc and divide out** (the
  one named remaining engineering item).
- **Building block 2 — the target (the ρ_t arcs, C4982–C4985):** the magic-tax decomposition found a
  **depth-growing coherent few-bit drift that resists randomized compiling** — context-dependent
  CZ-pulse coherence, circuit-structure-tied (twin drifter positions {23,26,53,73} disjoint from t80
  drifters {46,57,70}), refuting the C4984 twirl-the-pads design rule on flown data. It is measured,
  reproducible physics that **does not appear in, and cannot be predicted from, the published
  calibration model** — that is precisely what "RC-resistant + structure-tied" means operationally.

**Why the fusion is the point.** The F121-analog attack on any *channel-learning* advantage claim is
the **zero-sample classical arm**: predict the channel from published backend properties (T1/T2,
gate errors) plus a noise model, spend nothing, match the answer. An idle-T1 channel — the C4971
steth target — dies to it. The pad-drift channel is, by measurement, the component of our hardware's
behavior that this arm *gets wrong*. Choosing it as the target is what closes the escape hatch: the
secret is held by the device, the access model (samples of the channel) is physically enforced for
every arm, and the single-copy floor is a theorem.

### The pre-registered arms (all escape hatches flown as arms, not footnotes)

| Arm | Access | Cost currency | Role |
|---|---|---|---|
| **Q** — two-copy Bell-probe learner | samples of the channel, quantum memory | samples to reach accuracy ε | the claim |
| **C1** — best single-copy strategy, executed same-chip same-window | samples of the channel, no quantum memory | samples to reach ε | the theorem-floored competitor (Ω(2^(n/3))). **F119-audit fence: fresh randomness per copy (shots=1 per setting), no fixed-basis batching; both arms billed in copies consumed** — sim-verified by Ember's remedy check (general#815, quantum@b8a29fe): batching's determinism attack dies at shots=1 AND the separation survives (37×/348×/1105× at n=4/6/8) |
| **C2** — calibration-prediction, zero samples | published backend properties only | 0 samples | the F121-analog. The claim must show the target carries structure C2 gets wrong by ≫ ε |
| **C3** — full noise-model simulation from calibration | published properties + simulator | 0 samples, CPU-seconds logged | C2's strongest form; same role |

Verdict shape: **advantage = Q reaches ε with measurably fewer samples than C1 (factor ≥4× at n≥9,
pre-registered) AND the target channel is demonstrated outside C2/C3's reach.** If C2/C3 predict the
channel within ε, the target dies and the flight is not flown — that is the fence doing its job
pre-spend, the same mechanism that would have caught F121 before submission.

### The named open design question (for Elder's theorem seat — not resolved here)

Thm 7.9's premise is a **Pauli channel**; the drift's calibration-invisibility *is* non-Pauli
coherence. The tension is real and must be settled before any prereg freeze. Three candidate
resolutions, in order of preference:
1. **Reframe the task as channel identification/distinguishing within a family** — CCHL and the
   learning-from-experiments line prove exponential single-copy separations for general (non-Pauli)
   dynamics; pin the exact theorem + constants from the paper (G-1 discipline — not from memory).
2. **Twirl and bound**: twirl the target, book the Pauli-projected channel as the learned object,
   and bound the residual coherent part as a systematic (it is measured: few-bit, position-stable).
3. **Fall back to the T-slot stochastic core** (flat, Pauli-like) — only if a $0 check shows the
   calibration model *also* fails to predict its magnitude; otherwise the C2 arm eats it.

### Gates, in order (nothing flies until all pass)

1. ✅ **Ember's F119 audit verdict lands and is integrated** — **DONE** (general#810, integrated
   above): verdict SUPERSEDED-as-executed / QUALIFIED-in-principle. Consequences adopted here:
   the §2 floor citation stands (CCHL Thm 7.9 is a *published theorem*, distinct from the open
   (3/2)ⁿ appendix bound that bit F119); the C1 arm carries the delivery-artifact fence; both
   arms are billed in copies. F119's own fix (re-fly conv arm at shots=1/row) is Ember's remedy
   lane, separate from this proposal.
2. ✅ **$0 pre-flight C2 test on existing data — RUN, TARGET SURVIVES** (Creator GO, C4998;
   `experiments/exp_c2_killtest_calibration_arm.py` → `results/exp_c2_killtest_c4998.json`).
   Three variants, strictly ordered by generosity: calibration-pure, calibration-anchored, and
   **class-best** — the per-bit least-squares supremum of the *entire* stochastic model class
   (bias = A·s^d, A≥0, s∈[0,1]), which is calibration-snapshot-independent. Results: non-drifter
   bits are ordinary stochastic decay (class-best median residual 0.016, 31/36 within ε=0.05) —
   but the pre-identified drifters are **class-irreducible: 0/4 within ε=0.05, median residual
   0.28, worst 0.32** (the sign-flips are unreachable by any stochastic/calibration model; the
   fit rails at zero while the data goes to −0.28/−0.32). The measured C2 gap (0.13–0.32 per
   drifter bit) is now the frozen baseline the advantage claim must exceed. **Secondary finding**:
   the class-best residual is itself a cleaner coherent-bit detector — it found **two drifters
   the arc's census missed** (pos18 phys45, a sign-flip; pos33 phys25, an *inverted* drifter
   starting negative), census 4→6. Caveats logged in the artifact: proxy observable (per-bit
   bias through the decode pipeline, not Choi eigenvalues — the flight's own C2 arm still runs
   at flight time); calibration snapshot from the 16:47Z cycle vs the 05:44Z flight window
   (class-best is immune); calibration-only variants under-predict decay broadly, consistent
   with the attenuation map's λ_eff > calibration.
3. **Elder theorem seat** on the Pauli-premise question above; **Ember sealer** design (the channel
   instance/region sealed the way she sealed the race strings).
4. **QPU budget check at flight time** (fresh number, not the C4971 68% figure; Creator says budget
   OK — still a chosen spend, priced first per the standing policy).

### What the claim would be, said plainly

A **sample-complexity computational advantage on a natural task**: characterizing a real, unplanted,
calibration-invisible physical process of our own device, where the quantum-memory learner measurably
beats (a) the best executed single-copy strategy backed by an unconditional information-theoretic
floor, and (b) the zero-cost classical predictor that kills naive versions of the claim. No runtime
claim; F54's wall untouched; currency printed on the tin. This is the Google/CCHL
"learning-from-experiments" shape, but with the target channel *scientifically motivated by our own
open physics question* (the tax-law redesign named in coordination#712) — the flight would answer a
real question about the drift **and** bank the advantage measurement in one spend.

## 3. Ranked alternatives considered (kept, not developed)

- **Forrelation query race** — the *proven maximal* query separation (1 quantum vs Ω(√N/log N)
  classical, unconditional in the black-box model). New genre-entry beyond Exp145's Simon flight;
  cheap, shallow. Fence: query currency only, black-box only — white-box classical computes the
  forrelation in O(N log N) trivially at reachable n, and post-C4996 that fence must be printed in
  the headline. Ranked below the steth flight because it re-enters row-1 territory the moment anyone
  reads it as runtime; queue as a $0 scout if the steth path stalls.
- **New hidden-shift instance family (non-MM bent functions)** — **rejected**. The MM family is
  algebraically broken (C4996); non-MM families offer only "no known attack," which after our own
  41-query lesson is exactly the floor type we no longer fly. The supersession clause would hang
  over it from day one.
- **Hidden-matching Scoreboard-2 flight** — unchanged from the C4971 scout (GO-able, cheap,
  communication currency, not computational). Still parked behind the computational path.

## 4. Missed-thread flags from this cycle's sweep ($0 bookings, graders' lanes)

1. **F120's instrument record is stale-low**: README says "blind exact recovery demonstrated to
   d2q=217," but the organic ρ_t-law flight decoded ladder rung `lad_d_hi m2` **blind-exact at
   d2q=310** (s_hat posted pre-reveal in coordination#726, graded CLEAN [0,0,0] against Ember's
   revealed rung0, #728). The campaign's deepest blind exact decode is 310, not 217 — the record is
   ahead of its own scoreboard again (the annex item-0 pattern, second occurrence). → **Elder
   (grader)** to confirm and book; touches README line 17 and the F120 finding doc.
2. **The ρ_t tax-law redesign (coordination#712) and this proposal are the same spend**: the drift
   physics question and the advantage flight share a target, a region, and a seal design. Whoever
   scopes the redesign should read §2 first so we don't design two flights for one measurement.

---

*Fences repeated once, plainly: nothing here is flown, priced, or claimed — this is a scoping
proposal gated behind Ember's F119 audit and a $0 calibration-prediction test that can kill it.
The floor-type table in §1 is the load-bearing contribution; the flight design in §2 is its first
application. Exact theorem statements and constants get pinned from papers at prereg time, not
quoted from memory.*
