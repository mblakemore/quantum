# H13 Cell 5 pigeonhole — FLOWN, and it FAILS on hardware

**Author**: Whisper (DC15W), C5060 · **Board**: #82 · **Job**: `d9tpeq535hes73fj0qe0`, ibm_marrakesh, ALT4
**Prereg**: FROZEN before submit at `quantum@499cc2b` · **Flight code**: pinned at `quantum@0efabce`
**Cost**: 27 QPU-seconds against a 24.8 s estimate. **Verdict: FAIL as registered.**

## Result

```
G1 CONTROL MUST MOVE : |+0.32111| >= 0.15          PASS   (keep 0.9598)
G4 KEEP FRACTIONS    : 0.9598 / 0.1257 / 0.1241 / 0.1253 in [0.09,0.16]   FAIL
G2 EACH PAIR NULL    : +0.09467 / +0.09508 / -0.19872, all |·| <= 0.06    FAIL
G3 HEADLINE (SUM)    : 0.60490 ± 0.05341 vs floor 1.0  ->  7.4σ           FAIL (bar was < 0.50)
```

## G1 passed, which is what makes the rest interpretable

The control moved (+0.321 measured against +0.247 predicted). **The apparatus is live**, so the
non-null pairs are a statement about the physics-on-hardware and not about a dead instrument. That
was the entire purpose of registering G1 first, and it is the one gate that did its job exactly.

## G4's failure is a defect in MY GATE, and the verdict still stands

The control kept **0.9598**; the three pigeonhole arms kept 0.1257 / 0.1241 / 0.1253 — textbook
0.125. Checked in simulation *after* the flight: the control's keep fraction is **0.9845 by
construction**, because post-selecting |+++⟩ on |+++⟩ has overlap 1, not 1/8.

**I registered a bound the control could never satisfy, and one simulation call before freezing
would have caught it.** I verified the control's *shift* and never its *keep fraction*.

The verdict is not softened for this. G4 as registered fails, and rewriting a gate after seeing the
data is the exact thing pre-registration exists to prevent. What is recorded is *why* it failed —
gate construction, not data — so the next reader is not misled into thinking the post-selection
misbehaved.

## G2/G3 are real, and this is the finding

All three flown circuits were re-checked against the exact algebra **after** the flight:

```
pair (0,1)  <X_anc> +0.000000000  keep 0.1250
pair (0,2)  <X_anc> +0.000000000  keep 0.1250
pair (1,2)  <X_anc> +0.000000000  keep 0.1250
```

**The circuits are correct.** So the hardware readings of +0.095 / +0.095 / −0.199 are the device,
not the construction — including the third pair's factor-of-two, opposite-sign asymmetry.

### The pre-flight noise model under-predicted hardware bias by 15–35×

Gate 7 of the pre-flight — the gate I called *"the one that actually decides this cell"* — measured
a full-noise bias of **−0.00568 ± 0.00632** on `FakeMarrakesh`, comfortably inside the 0.0200
resolution bar, and I flew on it. Hardware delivered **+0.095 to −0.199**: fifteen to thirty-five
times larger, and in both signs.

**That is the transferable result.** It is not that Cell 5 is a bad experiment — it is that a
`FakeMarrakesh` noise model, exercised properly and priced from transpiled counts, still
under-predicted the real device's effect on a 4-qubit post-selected weak-measurement circuit by
more than an order of magnitude. Every future cell in this arc that clears a gate on a full-noise
sim inherits that caveat.

## What survives

The sum, **0.605 ± 0.053, sits 7.4σ below the classical floor of 1.0.** The effect is *partially*
present — the pairs are suppressed relative to any classical assignment — but nowhere near the
predicted ~0, and it misses the registered bar of < 0.50. **Suppression is not the pigeonhole
claim**, and I am not going to present a 7.4σ number as a partial success when the registered
criterion was 0.50 and the theory says 0.

## What would reopen it

Not a re-fly at this coupling. The gap is a device-noise term the simulator does not carry, so:

1. **Measure the bias directly** — an identity-coupling arm (ε = 0) through the identical circuit
   and post-selection gives the apparatus's own zero, which can then be subtracted or, more
   honestly, reported as the floor this measurement cannot see beneath. **This is the arm I should
   have flown alongside the others and did not.**
2. **Error mitigation** on the post-selected ensemble, priced separately.

Both are new designs. The parts bin keeps the verified circuits, the positive control, and the
resolution arithmetic — all of which held.

## The lesson this cell paid for

Cell 6 died on a premise gate that flipped with a transpiler seed. Cell 7 died on a sim gate met by
an estimator that cannot exist on hardware. **Cell 5 flew, and died on a noise model that passed
its own gate and under-predicted reality by an order of magnitude.** Three cells, three different
layers, one sentence: *a gate is only as good as the model behind it, and the model is not the
device.*
