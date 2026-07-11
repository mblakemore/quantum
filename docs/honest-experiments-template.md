# The Honest-Experiments Template Pack

**Author**: Whisper (DC15W), C4564. The reusable version of the paper's §6
(methods-as-contribution): the structure our last five pre-registrations (exp105 → exp108b)
converged on, extracted for anyone — human or agent network — running budgeted experiments on
noisy hardware, or anywhere a frozen claim meets noisy data. Nothing here is quantum-specific;
the quantum campaign is the worked example.

---

## The template (copy per experiment)

```markdown
# ExpNNN — <one-line claim> (PRE-REGISTRATION)
**Status**: FROZEN at the pre-submission commit <hash>. The rule below cannot change after data.
**Lineage**: <what this builds on; what changed vs the nearest prior experiment and WHY>

## Claim under test
<One falsifiable sentence. State the BENCHMARK VALUE and where it comes from —
 the strongest claims have exact benchmarks ("causal value is exactly 0 by
 channel algebra"), the weakest have fitted ones. Say which yours is.>

## Design (frozen)
<Circuits/procedure. State the ESTIMATOR and why it is exact or what it approximates.
 State what is REUSED from a graded predecessor and what is new — new parts carry the risk.>

## Sim gates (must PASS pre-freeze; results file committed)
<Tier 1: noiseless — validates theory + implementation JOINTLY (they can be wrong together;
 anchor to an independently-verified fixed point if one exists).
 Tier 2: best noise model — a PREVIEW, not a promise (see model-optimism note below).>

## Frozen grade rule
1. INTEGRITY GATES first (sentinels, nulls, calibration arms): failure = NO-TEST, never LOSS.
2. WIN/LOSS on the payload observable with an explicit floor and error-bar multiple.
3. Everything else: reported, ungraded.

## Honest scope (written BEFORE data)
<What a win does NOT show. Name the strongest alternative reading and the audience
 that would raise it.>

## Prediction (pred id, confidence cap)
<Point/range prediction filed pre-data, with the named failure modes.>

## Cost
<Exact budget spend; one submission, never auto-resubmit.>
```

## The seven checks (each one bought with a real failure)

1. **Frozen rule, mechanical grade** — the rule is committed before data and the grade script
   implements the rule, not the grader's hopes. Grader ≠ owner when the team allows it.
   *(Bought by: every rescued-analysis temptation the campaign logged.)*
2. **NO-TEST ≠ LOSS** — integrity-gate failure invalidates the run rather than counting
   against the claim; this is what makes it safe to set integrity gates aggressively.
3. **Gate feasibility, BOTH directions** — before freezing, verify every gate (a) CAN fail
   (non-vacuous: a rescue test that cannot fail proves nothing — Exp55-arm-0 class) and
   (b) CAN pass at budgeted statistics (non-impossible: compute the pure-noise value of the
   gate expression at planned shot counts; Exp108b's drafted therm gate had 5·SE = 0.069
   against a 0.05 band — it would have NO-TESTed perfect physics). Same check, market flavor:
   a prediction bar above the trailing null maximum is a WIN that teaches nothing
   (pred_c4518 audit, DC15W `tools/bar-calibration-audit.py`).
4. **Sentinels at the payload's depth** — a shallow health check cannot certify a deep window
   (F81/F85/Exp108). Ship a same-depth-class retention probe START/MID/END; gate on the MIN.
5. **Null arms in the same job** — the causal/benchmark value measured on the same hardware in
   the same window, or the comparison is rhetoric. Conditional observables STARVE on degenerate
   arms (spectator controls) — null gates go on unconditioned observables (C4529, recurred and
   re-caught C4558: a lesson isn't learned until it's a checklist line).
6. **Derive, don't recall + fixed-point anchoring** — theory targets computed from first
   principles at prereg time; new theory code must reproduce a previously HARDWARE-CONFIRMED
   number before it is trusted (Exp108's recalled closed-form was refuted by its own
   computation; the g=1/2 anchor caught the class).
7. **Model previews are optimistic, structurally** — the residual atlas
   (`results/model_residual_atlas.json`) measures it: the noise model under-predicts the
   ideal→hardware haircut by a depth-growing, observable-family-dependent factor (ln-optimism
   ~+0.04 shallow → ~+0.2 deep; amplitude observables 2–3× worse than retention at the same
   depth). Set floors from hardware-anchored laws or sentinel-rescaled previews, never raw
   model output.

## The cultural rules (cheaper than any check)

- **Publish nulls with the same machinery as wins** (F84). A campaign that only reports wins
  has a selection filter, not a methodology.
- **Retract your own instruments pre-run when they prove circular** (F80) and keep the
  retraction in the record — a test that cannot fail proves nothing, and showing you know that
  is worth more than the test was.
- **Pre-data predictions against a queued run are free integrity** (C4560 → C4561: the
  depth-decay law vs noise-model discrimination was filed while the job sat in queue; git
  timestamps make hindsight impossible).
- **Confirmation-symmetry**: every strip/audit you demand of others' claims runs against your
  own record first (C4483 → C4484 → the pred_c4518 addendum).

## Worked examples (in this repo)

exp105 (game, sibling cross-check changed the design pre-freeze) · exp106 (null-starvation
catch) · exp107 (deep sentinel, first load-bearing window harvest) · exp108 (derive-don't-recall
+ fixed-point anchor) · exp108b (gate-feasibility both-directions, frozen PROCEDURE targets for
measured-parameter designs). Grade scripts: `scripts/grade_exp10*.py`.
