# Finding — Exp185: THE UNIVERSE WHERE TIME IS OPTIONAL — two legs held; leg 2 failed by the letter, by 0.008, teaching a rule I already owned

**Cycle**: C4875 · **Date**: 2026-07-19 · **Backend**: ibm_fez · **Job**: `d9e46v4inv1c73appu20`
(7 circuits, 8000 shots). Page–Wootters emergent time, circuit form (Moreva-style). Creator go:
ship-computer general#86. **Verdict by the pre-registered letter: NOT HELD (2 of 3 legs).**
The record stands; the re-flight (185b) carries a principled, pre-committed criterion fix.

## Result

**Leg 1 — the inhabitants have time: HELD.** Conditioned on their clock, the system is caught
mid-evolution, sweeping the equator 90°/tick exactly as the law U = S dictates:

| tick | (X, Y) measured | predicted | F |
|------|------------------|-----------|---|
| 0 | (+0.961, +0.068) | (+1, 0) | 0.980 |
| 1 | (−0.012, +0.956) | (0, +1) | 0.978 |
| 2 | (−0.944, +0.062) | (−1, 0) | 0.972 |
| 3 | (−0.025, −0.950) | (0, −1) | 0.975 |

Mean F = 0.976, sign pattern 4/4 (band 0.92–0.98 ✓).

**Leg 3 — time has an off-switch: HELD**, near-perfectly. Remove the two entangling gates and
every tick shows the identical |+⟩ at F = 0.997/0.998/0.998/0.996. **The inhabitants' time is
the entanglement; without it their universe is frozen at every clock reading.**

**Leg 2 — the outside is frozen: NOT HELD by the letter.** echo_id (prep ceiling) = 0.889;
echo_T (prep → correct-law translation → unprep) = **0.792 vs the pre-registered ≥ 0.80 —
missed by 0.008** (~1.8σ below the bar); the sharp form (within 0.06 of the ceiling) also
missed (gap 0.097). The *separation conjunct held*: correct-law 0.792 vs wrong-law 0.414, a
0.378 gap (≥ 0.25 required) — and the wrong-law translation landed at its theoretical ½ in
**ratio** terms (0.414/0.889 = 0.466 ≈ 0.5).

## Why leg 2's bar was wrong (and whose fault that is)

The physics prediction is not an absolute echo value — it is that the correct-law translation
costs *nothing beyond its own gates* while the wrong-law translation costs a factor ½ **relative
to the prep ceiling**. In ratio form (post-hoc here, labeled as such): echo_T/echo_id = 0.891
(the translation's compiled circuit — a routed CX between clock qubits + 1q gates — costs ~11%,
all of it gate error), against echo_Tclock/echo_id = 0.466 ≈ the theoretical 0.5. The structure
is exactly Page–Wootters. My absolute 0.80 bar silently assumed a near-free translation circuit.
**Exp182 (C4870) had already established the rule — pre-register baseline-normalized ratios,
never absolutes that confound the effect with same-job overheads — and I failed to apply it to
leg 2.** The miss is mine, the rule was on the books, and the letter-verdict stands unamended.

## Disposition

Exp185's record: leg 1 and leg 3 held with their bands; leg 2 fails by the letter. **Exp185b**
(pre-registered before its flight, criterion derived from the standing C4870 rule, not from
this data's location): leg 2 in normalized form — echo_T/echo_id ≥ 0.80 AND
(echo_T − echo_Tclock)/echo_id ≥ 0.30 AND echo_Tclock/echo_id ∈ 0.40–0.60 — same circuits,
same everything else. Legs 1 and 3 carry over unchanged.

## Fence

A 4-tick cyclic toy universe on 3 transmons; "external time" is circuit depth — the claim is
the state's invariance under its own internal translation (the Page–Wootters statement), not
about laboratory clocks; U = S is Clifford by design; the off-switch removes entanglement at
preparation. Conditional tomography uses X, Y (equatorial law); n per tick ≈ 4000.
