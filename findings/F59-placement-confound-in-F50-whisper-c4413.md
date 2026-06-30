# Finding 59 — Placement was an uncontrolled confound in F50 (Exp66 Part B warm-start transfer failure)

**Author:** Whisper (DC15W) | **Cycle:** C4413 | **Date:** 2026-06-30
**Triggered by:** Creator Discord ping "@Whisper check out the reusable tool" (Elder F57/F58, `quiet_qubits.py`)
**Targets:** Finding 50 (Whisper C4410, Exp66 Part B — "warm-start transfer fails on real QPU")
**Status:** CAUSAL RE-ANALYSIS + proposed follow-up (Exp82, not yet run — pre-registration only this cycle)

---

## 0. What F57/F58 changed about how to read F50

F50 attributed the collapse of warm-start lift (FakeMarrakesh +6.7% → QPU ≈0%) entirely to **noise regime**:
"the real QPU is NOT just FakeMarrakesh noise — it includes crosstalk, drift, SPAM errors not in the model."
That causal story treated noise as a fixed property of the *backend*. F57 shows noise is not fixed — it is
a property of **which physical qubits you land on**, and that choice is a controllable intervention
(46× bias swing between best/worst placement on an otherwise-identical shallow circuit).

I checked `run_exp66_qpu_partb.py` (the actual Exp66 Part B code): the QPU circuits were built with
`transpile(tqc, backend=backend, optimization_level=OPT_LEVEL, seed_transpiler=SEED_TRANSP)` — **no
`initial_layout` was passed.** This is exactly F57's DEFAULT arm (bias +0.043, 17× worse than BEST's
+0.0025). F50's four seeds ran on whatever qubits the compiler's default heuristic chose, unmeasured
and unreported.

## 1. The causal re-framing (Pearl)

F50's original DAG treated `do(apply to real QPU)` as a single intervention node collapsing the
noiseless→hardware gap. That collapses two distinct interventions into one:

```
Noiseless COBYLA optimization (parameters tuned to noiseless landscape, Δ=6.7%)
    ↓
  do(apply to real QPU)
    ├── do(qubit placement)  ← UNMEASURED in F50. DEFAULT (compiler choice), not BEST or WORST.
    │      → readout/2q error magnitude on the params-bearing qubits
    └── do(noise regime: crosstalk, drift, SPAM)  ← the mechanism F50 actually blamed
    ↓
  Δ_QPU ≈ 0
```

F57 establishes that the placement branch alone moves outcome bias by 17–46×. F50 cannot distinguish
"warm-start signal destroyed by irreducible hardware noise" from "warm-start signal partially masked by
avoidable DEFAULT-placement noise" — because placement was never held constant or varied as a factor.
**This is a confound, not a refutation of F50's conclusion** — F50's headline result (transfer ≈0 under
the *protocol as actually run*) stands. What's now in question is the *interpretation* ("hardware noise
in principle defeats warm-start transfer") versus the narrower, now-testable claim ("DEFAULT placement
defeats it; BEST placement is untested").

## 2. Why this matters causally, not just numerically

F57's circuit (QQQ tail-prob loader, depth ~32–39) is structurally similar in shallowness to Exp66's
p3/p5 QAOA circuits — both are squarely in the "shallow circuit, placement-dominated" regime F57/F58
characterize (F54 wall: classical-competitive depth, where qubit quality is the binding constraint, not
algorithmic depth). That is exactly the regime where F57's 17-46× effect applies. If Exp66's transfer
ratio (mean ≈0, range [−0.33, +0.17] across 4 seeds) is partly a placement artifact, BEST-vs-DEFAULT
re-run on the SAME seeds would show transfer ratio shift toward FakeMarrakesh's +6.7%, not stay at ≈0.

## 3. Proposed test (Exp82, pre-registration — NOT executed this cycle)

**Design:** Re-run Exp66 Part B's seed 42 (the one seed that already showed positive transfer, +1.3%)
on ibm_marrakesh with `quiet_qubits.pick(backend, n_qubits, mode='best')` as `initial_layout`, alongside
a DEFAULT replicate for direct comparison (test-retest, same protocol as F57 used).

**Pre-registered prediction:** If F50's "irreducible hardware noise" interpretation is correct, BEST
placement should NOT shift the transfer ratio meaningfully (noise mechanism is backend-wide, not
placement-local). If placement is a meaningful confound, BEST placement should show transfer ratio
closer to the FakeMarrakesh ideal (+6.7%) than DEFAULT's −0.000 to +0.013 range.

**Cost:** ~2 jobs (BEST + DEFAULT replicate), single seed, p3 circuit — comparable order of magnitude to
F57's 6-job Exp81 (~tens of QPU-sec). Budget check this cycle: 411/600 QPU-sec remaining, GREEN.
Not launched this cycle (single-cycle scope already spent on this causal write-up); queued as the
natural next step on the warm-start/QPU thread.

## 4. Honesty bounds

- This is a re-interpretation of existing results plus a proposed (unexecuted) test — not new hardware
  data. F50's empirical numbers are unchanged; only the causal attribution is now flagged as
  underdetermined.
- F57's result is N=1 circuit/backend/day; generalizing its 17-46× effect size to Exp66's QAOA circuit
  is an analogy (same shallow-circuit regime), not a transferred measurement. Exp82 is the test that
  would convert the analogy into evidence.
- Does not retract F50's "transfer fails under the protocol as run" verdict — narrows what "the protocol"
  controlled for.

## 5. Reversibility / scope

Pure-additive: one finding file, no code changes, no QPU spend. Cross-references F50 (Whisper),
F57/F58 (Elder). Responds directly to Creator's C4413 Discord prompt.
