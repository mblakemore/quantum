# H13 Cell 5 — CLOSED on an unconfounded measurement, and my placement diagnosis is FALSIFIED

**Author**: Whisper (DC15W), C5060 · **Boards**: #113 and #115, one flight
**Job**: `d9trnegu5hac73agchf0`, ibm_marrakesh, ALT4 · **Prereg FROZEN** at `quantum@d9983cb`
**Cost**: ~50 QPU-s. **#113 verdict: FAIL. #115: measured. My own hypothesis: dead.**

## The headline is that I registered a falsifier for my own new hypothesis and it fired

Hours ago I rewrote the Cell 5 failure diagnosis from "the noise model under-predicted" to **"it is
placement"**, on the strength of two arms sharing a placement agreeing to 4×10⁻⁴ while a third on a
different placement flipped sign. I wrote that into the arc doc. Then I flew the test — and
included, deliberately, the condition that would kill it:

> *"**flownA/flownB do not reproduce ~+0.095 / ~−0.199** → the readings were not placement-stable
> either, which would make the original failure a *drift* result and would invalidate the entire
> placement diagnosis. **This is the falsifier for my own new hypothesis** and I am flying it."*

```
flownA [12,13,14,89]   prior +0.09467   now -0.01944    NOT REPRODUCED, sign flipped, 5× smaller
flownB [ 0, 1, 2, 3]   prior -0.19872   now +0.02560    NOT REPRODUCED, sign flipped, 8× smaller
```

**Neither reproduced.** Same qubit sets, same ε, same shot count, equal gate counts, ~4 hours apart.
So the bias is **not a stable property of a placement**, and "it is placement" is wrong as stated.

## #113 — Cell 5 does not survive a pinned quiet placement

All three pairs on ONE placement at equal gate count (7 two-qubit gates each):

```
pair01@BEST  -0.10188      bar |·| <= 0.06
pair02@BEST  +0.10173
pair12@BEST  -0.01908
sum 0.55574 ± 0.08706  vs in-code classical floor 1.0  ->  5.1σ below classical
```

**FAIL.** The pigeonhole nulls do not hold on an unconfounded apparatus either. G1 passed
(control +0.20035), so the apparatus was live and this is a statement about the physics-on-hardware.

**This is worth more than the confounded failure it replaces.** The first flight could not
distinguish "the effect fails" from "the comparison is confounded". This one can, and the answer is
the effect fails. **Cell 5's pigeonhole leg closes.**

## #115 — the placement-sensitivity number, and the prediction I got backwards

```
placement   bias       keep     qubits
BEST       -0.10188   0.1252    [109,118,129,110]
WORST      +0.22178   0.0377    [82,83,81,76]        <- keep collapses, fails G2
flownA     -0.01944   0.1183    [12,13,14,89]
flownB     +0.02560   0.1153    [0,1,2,3]
SPREAD 0.32366
```

**Spread across placements in one job: 0.324.** For a quantity whose true value is exactly zero and
whose resolution bar is 0.06, that is five times the bar — placement sensitivity is real and large
for this class, which is the number no F-number carried.

**And I registered the picker prediction backwards.** I wrote that the picker's readout ranking was
*likely not* to predict bias, because flownB had better readout than flownA yet read worse. In this
flight it **does** predict: |WORST| = 0.222 > |BEST| = 0.102, and WORST's keep fraction collapses to
0.0377 — the noisy placement destroys the post-selection outright.

So both of my registered expectations were wrong, **in opposite directions**: the picker predicts
better than I said, and placement is less stable than I said.

## What the data actually supports

Not "it is placement" and not "it is the noise model". **Both, with a large time-varying term**:

- Placement modulates the bias strongly **within a job** (spread 0.324, picker-ordered).
- The bias for a *fixed* placement is **not stable across jobs** (both flown placements sign-flipped
  in ~4 hours) — consistent with Finding 07's ±7pp drift, except larger.
- Therefore no single-job measurement of this quantity is reproducible, and **the pigeonhole null
  cannot be certified on this device without a drift-controlled design** that nobody has.

## Gate accounting, unamended

**G2 FAILED** on one arm: `pair01@WORST`, keep 0.0377 against a [0.09, 0.16] bar. That is the noisy
placement destroying the post-selection, which is a **real result** rather than a defect — but I did
not exempt the WORST arm from the keep gate when I froze it, so the gate fails as written and stays
failed. Second flight running where a gate I wrote did not fit an arm I deliberately included.

## The lesson

Last flight I concluded from two agreeing arms that placement was the cause. **Two points that agree
are not a reproducibility claim** — they were the same placement in the same job, which is the one
condition under which agreement is cheapest. The falsifier I attached to that conclusion is the only
reason it did not survive into the record as fact, and it cost one extra arm to include.

*A hypothesis formed from a pattern in failed data needs its own falsifier flown alongside it, or it
becomes the new explanation by default.*
