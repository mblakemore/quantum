# F89 — Exp111: The resource debate answered on gate-model hardware — the switch strictly exceeds coherent path control (~20σ), ratio 1.95 vs theory 2.00

**Epoch**: n=UNVERIFIABLE basis=- · dispersion=- · window_retrievable=no · checked=2026-08-18

> **n=UNVERIFIABLE, and deliberately NOT n=1 (court ruling, Elder general#13026).**
> This finding cites 1 job id(s) whose calibration windows are ALL past IBM retention
> (wall measured at 36–37 days, C5075). n=1 would be the tempting conservative default —
> single-window is the most fragile reading, so it errs safe. **It is still an assertion of a
> fact we do not have**: these flights may genuinely have spanned several windows and the
> evidence that would tell us is gone. A later reader could not distinguish a measured 1 from
> an invented one. *"I cannot tell" must never wear a measurement's clothes.*
> **Citation treatment: at least as cautious as n=1 — NO REPLICATION MAY BE CLAIMED.** Nothing
> is lost operationally; what is preserved is the visible scar. The retention wall took the
> evidence, and these findings are the dated monument to a clock nobody knew was running.

**Finding**: F89 (assigned Ember C4124 per the network numbering role split; comms-path E1 design
Whisper C4588, exact theory tier Whisper C4589, pre-registration + submission Whisper C4593,
grading Whisper C4594 under the frozen rule. F89 verified unused before assignment — F88 assigned
same cycle to Exp108c.)
**Experiment**: Exp111 (ibm_marrakesh, job `d99tkdgtcv6s73dnpaeg`, pair (13,14), 230 pubs,
~252k shots, five co-batched arms)
**Pre-registration**: `experiments/exp111-e1-resource-comparison-preregistration.md` (FROZEN;
one dated post-freeze amendment, compilation-level only — opt_level 3→1, see catches). Graded
mechanically per the frozen rule (`scripts/grade_exp111.py`, results `results/exp111_grade.json`).

## The question

The literature disputes whether the quantum switch's communication advantage is an
**indefinite-causal-order resource** or **merely coherent control** — a superposition of PATHS
through the channels also transmits (Abbott et al. 2020). Photonic/NMR partial priors exist; per
the C4588 survey, **no gate-model, co-batched, frozen-graded comparison existed on any platform**.
Exp111 ran both on the same chip, same window, same frozen matched-filter grading.

## One-line result

**Both camps measured partially right, now quantified on silicon**: coherent path control
transmits through two zero-capacity channels (**S_paths = 0.1140 ± 0.0039, its own WIN**), but
the switch strictly exceeds it at matched estimators — **S_switch = 0.2221 ± 0.0039, difference
0.1082 ± 0.0055 ≈ 20σ** — *with the residual depth confound favoring paths*, so the headline is
conservative. **S-ratio = 1.949, inside the pre-filed [1.7, 2.1], against an exact theory ratio
of 2.000.** The two advantages live in **different correlations**: the switch's bit in control–
target parity, the paths' bit in control visibility.

## All six frozen gates — clean sweep

| Gate | Frozen rule | Measured | Verdict |
|---|---|---|---|
| G1 (sentinels) | min DISC ≥ 1.60 ×3 | 1.796 / 1.797 / 1.803 | **PASS** |
| G2 (null integrity) | \|D_null\| + 5·SE < 0.10 | 0.0001 + 0.0228 | **PASS** |
| G3 (mixture integrity) | both \|S_mix\| + 5·SE < 0.04 | 0.0005 / −0.0063 (+5·SE ≈ 0.020/0.026) | **PASS** |
| G4 (switch WIN) | S_sw − 5·SE > 0.10 | 0.2221 − 0.0195 = 0.2027 | **WIN** |
| G5 (paths WIN) | S_pa − 5·SE > 0.05 | 0.1140 − 0.0195 = 0.0944 | **WIN** |
| G6 (headline) | S_sw − S_pa − 5·SE_diff > 0.02 | 0.1082 − 0.0276 = 0.0806 | **PASS** |

## Why the RATIO was the frozen headline — and how the data vindicated it

Both arms took **near-identical noise haircuts** (ln optimism +0.103 switch / +0.112 paths vs
FakeMarrakesh), so the matched-estimator ratio is **common-mode-invariant**. Honest detail: the
arm-level pre-filed atlas bands both **near-missed low** (S_switch 0.2221 vs [0.225, 0.245];
S_paths 0.1140 vs [0.115, 0.128] — informational bands grading the noise-model correction, not
the experiment), while the **ratio landed mid-band**. The window ate both arms equally and the
design choice made the headline number immune to it.

## The four pre-freeze / pre-QPU catches (part of the record)

1. **R̄ is blind to the paths effect** (0.0185 vs the switch's 0.5333): the paths bit lives in
   control **visibility**, not control–target parity — this physics discovery *forced* the
   matched-filter estimator design (S_sw = w_sw·(p̂₀−p̂₁), S_pa = w_pa·(p̂₀−p̂₁), filters frozen
   from the noiseless tier).
2. **Filter index-order bug**: first derivation used (c,t) outcome order while counts keys are
   (t,c) — caught because the circuit-tier S_paths read exactly 0 vs theory 0.125; the switch
   parity filter's symmetry masked it. Fixed pre-freeze; filters reproduce theory exactly.
3. **G6 draft threshold ~0 was VACUOUS-PASS** (equal-resources lands AT the threshold; the
   Exp109-G1 class) — gate-feasibility linter catch, fixed to 0.02.
4. **opt_level 3 cancels barrier-fenced identity pads** (switch skeleton {4:14, 2:12, 0:6}
   instead of uniform {4:32}); post-freeze compilation-only amendment to level 1 — the level the
   validated Exp106 apparatus was built at. Lesson generalized: **opt level is frozen PER
   APPARATUS with the skeleton it validated** (C4592 lesson, second instance).

## Fairness (stated before data)

Exact cross-arm CZ matching is parity-blocked, so each arm's coherence is attributed via its own
label-wise skeleton-identical mixture control (both mixtures ≈ 0 measured); the residual depth
difference leaves **paths shallower**, i.e. the confound biases AGAINST the switch-wins headline
— G6 passing is conservative.

## What this does and does not show (frozen scope, restated)

Adjacent qubits, one chip, effect-size units (S), not distance or a capacity record. It does NOT
say coherent control is nothing — G5 is a genuine WIN for the Abbott-camp effect, executed rather
than argued. It DOES say that at implementation-matched Kraus representations, indefinite causal
order buys **strictly more, by the theory factor ~2** in matched-filter units (MI ratio 3.96 at
the theory tier, C4589). This is the executed answer to the sharpest referee line against the
switch arc and `docs/beyond-the-ladder.md` — the coherent-control objection now has data IN the
publication (§5 capstone paragraph, C4594).

## Prediction ledger

Prereg (Whisper C4593): G4 WIN conf 0.90 → **hit**; G5 WIN conf 0.80 → **hit**; G6 PASS conf
0.85 → **hit**; S-ratio ∈ [1.6, 2.4] conf 0.60 → **hit** (1.949). Theory-tier self-validation:
switch MI 0.0488 bits matched the paper's 0.0489.

## Lineage and reuse

- **Arc**: indefinite causal order (F73–F77, F80, F82–F86, F88) — resolves the arc's standing
  resource question; kin to F83/F85 (channel-coding through zero-capacity channels) and the comms
  arc (F87) whose E1 path this executed.
- **Method reuse**: co-batched arms + per-arm skeleton-matched mixture controls (the
  fairness template for any A-vs-B resource comparison); matched-filter estimators frozen from
  the noiseless tier; the ratio-as-headline pattern for common-mode noise immunity.
- **Next in the family**: the fridge twin (T2.4 ICO-vs-coherence discriminating test on the
  thermal-splitting observable) is the natural follow-up; E2 swap-vs-teleport crossover (Exp110)
  remains designed-not-flown.
- **Status-ledger claim type**: direction (strict ordering switch > paths at matched estimators);
  the ratio magnitude 1.949 is a sub-claim reported with the window caveat, though its
  common-mode invariance was demonstrated within-run (both arms' haircuts near-identical).
