# Exp183c — D1 POWER RE-FLY: pre-registration (FROZEN before flight)

**Author**: Whisper (DC15W), C5075 (2026-08-18). **Substrate**: claude-fable-5.
**Authorization**: Creator, this session, on the bus: *"exp183b D1 on ALT5"* — single-use, consumed by
this flight. Account `IBMQ_ALT5`, runtime-verified open plan; `service_for_submission`'s #151 gate
refuses any non-open route.
**Genre fence**: mechanism discrimination on a recorded anomaly. **No advantage claim, no new-physics
claim.** `attack_preflight` not applicable; account preflight mandatory and run.

## Why this flight exists, and the correction that produced it

exp183b's D1 returned **SYMMETRIC at χ² = 2.98 vs crit 9.210** — and Elder showed the reading is
**bounded, not conclusive**: the MDE was **0.0494** against a measured residual of **0.0248**, so the
test could only have detected an asymmetry twice the size of the thing it was measuring.

I then filed the re-fly precondition as *"wait until the residual returns above 0.0494"*. **That was
one-sided.** The MDE is `√(1.5·λ)/√shots` — the residual is one lever and **SHOTS ARE THE OTHER**:

| shots | MDE | vs residual 0.0248 |
|---|---|---|
| 8,000 (as flown) | 0.0494 | NON-TEST |
| 31,705 | 0.0248 | breakeven |
| **50,000** | **0.0197** | discriminates |
| 126,821 | 0.0124 | half the residual |

**D1 does not need the anomaly to return. It needs ~6× the shots.** Waiting was never the only route
and I should not have presented it as one.

## What flies

**8 circuits, arm A only, `SHOTS = 50000`** (vs 8,000), same pinned linear triple, same
`seed_transpiler=1837`, same decode path:

- **D1 (primary)**: base XXY, XYX, YXX — the three single-Y permutations
- **G1 (health)**: base XXX, XYY, YXY, YYX — the Mermin set
- **D2 (secondary)**: base YYY

Arm B (the −φ̂ intervention) is **NOT flown.** Its gate G2 requires the anomaly present at ≥0.05 and
it measured 0.0248 today; an intervention on an absent phase is untestable regardless of shots, and
flying it would be spending on a known NO-TEST.

## Frozen decision rules

- **G1 — health**: M_A ≥ 3.0 (se_M = 2/√50000 = 0.00894). Below → NO-TEST, publish anyway.
- **D1 — PRIMARY**: χ² = Σ((E₃_A,i − Ē)/se)², se = 1/√50000 = 0.004472, df = 2, **α = 0.01, crit
  9.210**. χ² ≤ crit → **SYMMETRIC**; χ² > crit → **QUBIT-SPECIFIC**, largest deviation named with
  its qubit.
- **MDE DECLARED IN ADVANCE**: **0.0197**. Any SYMMETRIC verdict is reported *with this number*, and
  is a statement that no asymmetry ≥0.0197 is present — never "the residual is symmetric".
- **RESIDUAL RECORDED AS A DATED POINT** regardless of verdict: mean(|E₃_A single-Y|) with
  `measurement_date`, appended to `results/exp183b_residual_census.json`. This is the third dated
  point in the oscillation-vs-walk-past series and accrues **whatever D1 returns**.
- **PRE-STATED NON-TEST BRANCH**: if the residual has fallen further such that MDE 0.0197 again
  exceeds it, D1 is **NON-TEST at this shot count** and the finding is the new residual value. Stated
  now so a second null cannot be narrated as confirmation.
- **D2 — sign structure**: reported PASS/FAIL, does not gate.

## What this flight CANNOT do

It cannot test the intervention (G2 absent). It cannot exclude the crosstalk class below 0.0197. It
cannot settle rolling-vs-fixed on the residual — that needs the third and fourth dated points.

## Cost

8 circuits × 50,000 shots = 400,000 shots, vs exp183b's 112,000. ALT5 reads 126 s. Runtime fit gate
at submit remains the wall.
