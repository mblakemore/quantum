# P1 n-ladder — TWO WEATHER-GATE AMENDMENTS (DRAFT, for a FUTURE freeze)

**Register seat: Whisper · C5097 · 2026-09-06 · NOT FROZEN, NOT FLYABLE**

This is a **draft for sign-off**, queued on the frozen registration
(`p1-ladder-fix-proposal-whisper-c5093.md`, line 392). It changes the flight gate, so it needs
**both seats' sign and a fresh digest**, and any flight under it needs a **new Creator GO** —
GO #2 was consumed by the same-weight repeat. Nothing here authorizes anything.

The campaign as flown is **not** waiting on this: four rungs DELIVER, the temporal control is
ungradeable as flown, and that summary line stands. These amendments are about what the *next*
freeze should require.

---

## The two candidates, as queued

1. **Matched-weight weather probe.** The G-WEATHER probe is the full-weight XYZ pattern at every
   n, so its weight equals n, while the science calibration this registration added is matched to
   the sealed w. The gate therefore gets harder with width by construction — at n=20 it is a
   20-weight probe against a floor calibrated at n=16.
2. **A margin above ε_min.** The gate admits ε_eff 0.1282 exactly as it admits 0.23. A flight can
   be admitted on the weakest state the gate allows, with no record that it was marginal beyond
   the logged number.

---

## §1 EVIDENCE FOR (1): the accepted-probe gradient

Every accepted weather probe of the campaign, by rung, from the registration's per-rung table:

| rung | n | sealed w | accepted ε_eff | halts/probes before it |
|---|---|---|---|---|
| 1 | 20 | 12 | 0.1287 | 2 |
| 2 | 16 | 13 | 0.1390 | 0 |
| 3 | 12 | 9  | 0.1783 | 0 |
| 4 | 8  | 6  | 0.2317 | 0 |
| repeat | 20 | 14 | 0.1350 | 0 |
| repeat1 | 20 | 12 | 0.1282 | 4 |

Accepted ε_eff falls monotonically with n across the four ladder rungs, and **every halt in the
campaign occurred at n=20** — the widest probe. That is the predicted signature of a probe whose
difficulty scales with width, measured rather than argued.

**It is not proof.** n and the sealed w are correlated by the draw law (E[w]=3n/4; the
registration records median corr 0.96 across these rungs), and epoch quality is not held fixed
across days. A four-point monotone gradient with a known confound is **consistent with** width
scaling, not a measurement of it. The amendment is justified by the *structural* argument — the
probe's weight is n by construction while the thing being gated is at w — and the gradient is
corroboration, not the case.

## §2 EVIDENCE FOR (2): two of six accepted probes were at the floor

Margins of the accepted probe above the 0.128 floor: rung 1 **+0.0007**, repeat1 **+0.0002**,
against 0.0110 (n=16), 0.0503 (n=12), 0.1037 (n=8), 0.0070 (repeat).

Two of six accepted flights cleared by under 0.001, i.e. under 1% of the floor. **The rate is
2/6 = 33% [10%, 70%] (95% Wilson, width 60pp) — the interval is too wide to quote a point
estimate**, and it is stated here only to fix that the sample cannot support one. The finding is
the two *instances*, not a frequency: a gate with no margin admitted two flights on states it
would have refused had the fourth decimal fallen the other way.

## §3 THE TENSION THE TWO AMENDMENTS CREATE — and why they should be decided together

They push **opposite ways on the epoch-selection effect** that grade rule (c) already tracks:

- **(2) makes the gate stricter** → more halts → rungs fly only in better epochs → *more*
  selection, and rule (c) fires more often (it already fires on the repeat: 4 halts vs 0 at rungs
  2–4, so the width residual is flagged EPOCH-CONFOUNDED).
- **(1) makes the gate easier at large n** (probe weight w instead of n) → fewer halts at the wide
  rungs, where every halt in this campaign occurred → *less* selection.

Adopting (2) alone would tighten the bar on the exact rungs that already halt most, and could
push a wide rung into unflyability. Adopting (1) alone removes the width scaling but leaves the
no-margin admission. **Recommendation: adopt both or neither**, and register the *combined*
expected halt rate rather than each amendment's separately.

## §4 COST, PRICED BEFORE REGISTERING (not after)

A weather probe is 2,000 rows in its own leading job; measured cost of a halt is **~4 s** of tank
(registration, rung-1 halt). The repeat rung absorbed 4 halts/probes ≈ 16 s against a 266 s tank.
A margin of δ above the floor raises the halt count; at the observed spread of accepted ε_eff a
δ = 0.005 margin would have refused 2 of the 6 accepted probes, costing on the order of another
probe or two per wide rung — **tens of seconds, not a rung.** This is affordable on a free-tier
tank. Stated because a method change that fixes correctness usually costs more, and pricing it
belongs *before* the freeze, not after.

## §5 WHAT IS NOT DECIDED HERE

- **The value of δ.** Not proposed. Choosing it from these six probes would be fitting a
  threshold to the sample that motivated it. It should be set from the *physics* of what ε_eff
  the decode needs, or pre-registered as a fixed fraction of ε_min with the reasoning stated.
- **Whether a refused-in-band probe is a HALT or a distinct REFUSE state.** A band refusal is not
  the same event as being below the floor and probably should not share its label in the record.
- **Retro-application.** These do not re-grade any flown rung. Four rungs delivered under the
  gate as registered; changing the gate afterwards and re-reading old rungs through it would be
  exactly the post-hoc move the blind protocol exists to prevent.

## §6 SIGN-OFF REQUIRED

- [ ] **Ember** (runner/sealer owner) — implementability of a matched-weight probe at the sealed
      w without leaking w before unseal. *This is the open technical question:* the probe is
      public and pre-seal, so a probe **at the sealed weight** may disclose w. If it does, (1)
      must instead use a **fixed weight declared in the registration** (e.g. 3n/4, the draw-law
      mean), which removes the width scaling without touching the seal. **Flagged as the likely
      blocker on (1) as literally worded.**
- [ ] **Elder** (grader) — how (1) and (2) change grade rule (c) and the width residual.
- [ ] **Creator** — a fresh GO, bound to a new digest, before any flight under an amended gate.

---

*Draft only. Not frozen, no digest, no flight. The current ladder flies as registered or not at
all.*
