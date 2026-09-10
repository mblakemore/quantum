# P1 dual-probe — what measuring it would COST. Planning note, $0.

**Not a result and not a revision.** The 2026-09-10 P1 grade stands: **NOT MEASURED at 1.470σ**.
This prices a re-fly from numbers already published, so the next planner has a cost rather than a
power figure. Nothing here licenses flying; it says what flying would have to buy.

## The framework, recovered from the published table rather than assumed

The §5 MDE table implies a **3σ detection bar**: MDE₅₀/σ = 2.9991 ≈ 3, and MDE_p = (3 + z_p)·σ
reproduces all three published MDEs and the published power to 4 decimals. Verified before use.

## The cost

σ ran **2.025× the planning value**, and shot cost scales as the **square** of that.

| target power | σ needed | shot multiplier | rows per leg |
|---|---|---|---|
| 50% | 0.014667 | **1.97×** | 7,049 |
| 80% | 0.011453 | **3.24×** | 11,558 |
| 90% | 0.010277 | **4.02×** | 14,357 |

Recovering the **planning σ alone** — i.e. buying back the ~90.7% power the plan assumed — costs
**4.10×** the shots. The plan was not optimistic about the effect; it was optimistic about σ, and
that error is paid quadratically.

**As flown: 3,571 rows/leg, power 0.194 against the registered effect 0.044.**

## ⚠ These are a FLOOR on cost, not an estimate

- **σ ∝ 1/√shots is an ASSUMPTION.** It is licensed here by today's block bootstrap
  (`p1-block-bootstrap-drift-RESULT-ember-c4384.md`), which found **no detectable serial structure**
  in either leg. But that result's own scope limit applies: *no detectable* drift is not *no* drift.
- **Any systematic component does not shrink with shots.** If part of the measured σ is device-level
  rather than shot noise, these multipliers understate the cost — possibly without bound, since a
  systematic floor makes some target powers **unreachable at any n**.
- **0.044 is the REGISTERED effect.** If the true effect is smaller, every multiplier rises.
- **Do not convert to QPU-seconds by scaling wall time.** FULL ran 82 s and FIXED 438 s at identical
  stamp, layout and row count — a 5.34× asymmetry that is still **unexplained**. Scaling an
  unexplained runtime is how a cost estimate acquires false precision.

## What this is for

A null at 19% power is nearly uninformative — it was the likely outcome whether or not the effect is
real. The decision it feeds is not "was P1 wrong" but **"is 3.24× the shots worth spending to find
out"**, and that is a question for whoever holds the QPU budget, not for this note.

Source numbers: `p1-dual-probe-RESULT-ember-c4384.md` §5. Framework verified against its own table.
