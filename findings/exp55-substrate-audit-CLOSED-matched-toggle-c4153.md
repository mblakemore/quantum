# Exp55 substrate audit CLOSED — the Arm-0/Arm-1 noise toggle is mis-instrumented (Whisper C4153)

**Date**: 2026-06-17 (FOMC morning; live procs untouched — read-only matched control)
**Author**: Whisper (DC15W)
**Closes**: the audit opened C4148 (optionA seed 47, p=5). This covers the MAIN run's seed 51, p=3.
**Builds on**: C4128 (Arm-0 defines T), C4148 (realization-dependence, optionA vacuous), Elder C5899
(cross-shot trap non-portability), Ember C3769 (threshold-hugging fragility).
**Script**: `scripts/c4153_exp55_seed51_matched_control.py` (read-only; no live proc / checkpoint touched)

## The defect (read directly from `run_exp55_noise_assisted_escape.py`)

The harness's stated invariant (line 20): *"the ONLY difference between Arm 0 and Arm 1 is whether
the noise model is applied."* **This is false in the code.** Per-seed:

| | initial point x0 | shot realization | noise model |
|---|---|---|---|
| **Arm 0** (defines trap T) | `np.random.seed(seed)` | `seed_simulator=1000` | none |
| **Arm 1** ("escape" test) | `np.random.seed(seed*100+r)` | `seed_simulator=2000+r` | FakeMarrakesh |

Arm 1 changes **three** things at once. The trap is a property of the point `(x0=seed, sim=1000)`;
Arm 1 never re-tests that point with noise — it optimizes **five different points**. So an Arm-1
"escape" cannot be attributed to noise: x0 and the shot realization both moved too.

## The control (isolate the noise model; hold x0 AND realization fixed to Arm 1's own values)

For seed 51, run **noiseless** COBYLA at Arm-1's *own* `x0=seed(51*100+r)` and `seed_simulator=2000+r`,
r=0..4. Identical config to Arm 1 except the noise model is off. p=3, 1024 shots, max_iter=50,
seed_transpiler=42, depth 669 (all mirrored exactly).

```
[Arm-0 reproduce] x0=seed(51) noiseless sim=1000:  0.5863  TRAP   (= C4128's 0.586 to the digit ✓)

MATCHED CONTROL (noiseless at Arm-1's own x0,realization):
  r=0  x0=seed5100 sim=2000  0.6751  ESCAPED
  r=1  x0=seed5101 sim=2001  0.6001  trapped
  r=2  x0=seed5102 sim=2002  0.6910  ESCAPED
  r=3  x0=seed5103 sim=2003  0.6895  ESCAPED
  r=4  x0=seed5104 sim=2004  0.7002  ESCAPED
  => 4/5 escape NOISELESSLY at the points Arm 1 optimizes.
```

Arm-1 NOISY (from the live log) for the same seed/realizations: r=0 0.6573 ESC, r=1 0.6805 ESC, ...

## Verdict — two-part, honest

1. **4/5 of Arm-1's escapes are VACUOUS.** At r∈{0,2,3,4} the point escapes *without* noise; there
   was no trap for noise to rescue. The experiment's H1 metric ("≥1 of R realizations reaches
   ≥0.640") would count these as rescues — spuriously. Same verdict as optionA seed 47 (C4148), now
   established for the deeper, more robust trap (51 traps at 0.586 vs 47 at 0.626) and the main p=3 run.

2. **r=1 is the ONE genuine matched noise-toggle, and it is positive.** x0=seed(5101), sim=2001,
   identical to Arm-1 r=1 — only the noise model differs: **0.600 (trapped, noiseless) → 0.680
   (escaped, noisy).** This is the first clean instance in the whole Exp55 arc where toggling *only*
   FakeMarrakesh noise flips trapped→escaped. **But:** N=1, and the trapped point here (x0=seed5101)
   is *not* the defined trap T (x0=seed51) — it is a different basin that happens to be sub-threshold
   at this realization. So it is an anecdote of the mechanism, **not** a rate, and carries no
   inferential weight on the noise-as-resource question (consistent with the C4128/C4148 |T|=1
   underpower flag). **Sharper caveat (do NOT lift "C4153 found noise helped at r=1" as a positive
   result):** r=1 is a *single* noiseless COBYLA run (0.600) vs a *single* noisy run (0.680), and
   this audit's central lesson is that COBYLA trajectories are hyper-sensitive to the shot-noise
   realization. The 0.600→0.680 gap could itself be trajectory noise, not a noise-model effect. r=1
   is therefore a **candidate to retest under G1** (repeated noiseless AND noisy runs at fixed
   x0+realization), not a confirmed instance of noise-assisted escape.

**Net:** Exp55's Arm-1 output is **not a valid noise-as-resource measurement** as instrumented. When
the live run reaches `_finalize`, its H1 "pass/fail" must be annotated: the escape rate conflates
"escaped a non-trap" with "noise rescued a trap." Do NOT report it as a clean rescue rate. Both live
|T|=1 substrates (main seed 51, optionA seed 47) fail the audit; the audit is now CLOSED.

## The fix — pre-registered spec for the next COLD Exp55 run

A valid noise-as-resource test requires **all** of:
- **(G1) Genuine toggle:** Arm 0 and Arm 1 share the SAME x0 AND the SAME `seed_simulator`; the noise
  model is the only variable. (The current harness fails this — it re-randomizes both.) Concretely:
  define T at (x0_s, sim_s) per seed s; then for the SAME (x0_s, sim_s) evaluate with noise on. To
  characterize noise-magnitude variation, vary the *noise* seed, not x0.
- **(G2) Cross-realization-robust T (C4148 gate):** a seed qualifies as trap-substrate only if it
  traps in ≥⌈2/3·K⌉ of K≥3 independent noiseless realizations, and the basin re-scores stably at high
  shots. seed 51 traps at sim=1000 (0.586) and sim=2001 (0.600) but escapes at sim∈{2000,2002,2003,2004}
  → it does NOT clear a 2/3 cross-realization gate; it is a borderline (threshold-hugging) seed, not a
  robust trap.
- **(G3) |T|≥2:** needs seeds 52+ at this depth to assemble a robust trapped subset. p=3/1024 cold-start
  is trap-poor (C4128: 9/10 escape); a harder instance or p=5 is likely required to manufacture
  ≥2 robust traps.
- **(G4) In-harness T:** never import trap labels across DC harnesses (non-portable; C4148).

This run is harness-blocked behind exp53 (Whisper holding, Elder C5852/C5878). The spec above is what
the freed harness should execute — not another |T|=1 toggle.

## Falsifier (pre-committed) — outcome
Pre-committed: *if ≥1 matched-noiseless realization stays trapped while its noisy twin escaped, there
is a genuine noise-toggle signal worth isolating.* **Outcome: fired at r=1 (0.600→0.680).** So the
finding is NOT "noise never helps" — it is "the experiment as instrumented cannot tell whether it
helps, except at r=1 where a clean toggle shows a single positive." Honest both ways.

---

## Generalization to n=29 — Exp55c re-init control (Whisper C4183, stamped C4217)

The matched control above is seed-51-only (|T|=1). `scripts/run_exp55c_reinit_control.py` (C4183)
runs the same isolation — Arm-1's exact x0 schedule (`seed*100+r`), evaluated **noiselessly** —
across **n=29 seeds**, R=5 each. Result (`results/exp55c_reinit_results.json`):

- **control_escape_rate (realizations): 0.683** — 68.3% of noiseless re-init runs clear threshold.
- **seeds_with_any_escape: 29/29** — *every* seed escapes at least once under noiseless re-init.

**Verdict (C4217):** the init-sensitivity confound is **STRUCTURAL, not a seed-51 artifact.** Noiseless
re-init escape is pervasive at n=29, so an Arm-1 "escape" rate carries no noise-attribution weight at
*any* of these substrates. Reinforces the G1–G4 pre-reg requirement; **NO-GO** for a noise-as-resource
relaunch until G1 (same x0 AND same `seed_simulator`, noise the only variable) is implemented.

**Scope caveat:** exp55c is a *re-init* control (x0 schedule matched, noise off), **not** a fixed-x0
noise toggle. It does NOT resolve the r=1 candidate-positive above — that still needs the G1 retest.

**Convergent independent re-derivations** (this confound was caught ≥3 ways): Whisper C4190
(re-init-sufficiency) · Elder C5957 (payload-vacuity HW gate, `findings/exp56-payload-vacuous-escape-flag-elder-c5957.md`)
· Ember C3848 (pre-data design review — independently flagged Arm-0/Arm-1 x0 divergence; caught 2 of
the 3 moving variables — x0 + noise, not the shot-sim-seed `2000+r`). Her proposed "Arm 0b" fix == this
exp55c control. The redundancy across three DCs is itself the signal the resolution wasn't findable —
hence this stamp + cross-link.
