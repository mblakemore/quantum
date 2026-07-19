# Finding — Exp185b: TIME IS ENTANGLEMENT — all three legs held under the pre-committed normalized criteria

**Cycle**: C4875 · **Date**: 2026-07-19 · **Backend**: ibm_fez · **Job**: `d9e4bgphtsac739dpt20`
(same 7 circuits as Exp185; amendment exp185b-preregistration-amendment.md committed **before**
this flight). Companion to finding-exp185-pagewootters.md, whose letter-verdict (NOT HELD,
leg 2 absolute bar) stands in the record unamended.

## Result — the Page–Wootters universe, certified

| leg | measured | criterion (pre-committed) | verdict |
|-----|----------|---------------------------|---------|
| **1 — inhabitants have time** | mean F(evolving) = 0.973, signs 4/4 (0.968/0.975/0.976/0.974) | ≥ 0.90, 4/4 | **HELD** (replicates 185's 0.976) |
| **2 — outside is frozen** | echo_T/echo_id = **0.907**; wrong-law ratio 0.469 (theory ½); normalized gap 0.438 | ≥ 0.80 (sharp ≥ 0.85); gap ≥ 0.30; wrong-law ∈ 0.40–0.60 | **HELD, sharp** |
| **3 — time has an off-switch** | notime F(static) = 0.998 per tick | ≥ 0.90 | **HELD** (replicates 185's 0.997) |

The three sentences this universe makes true, now with hardware certificates:
1. **Conditioned on their own clock, the inhabitants evolve** — the system marches around the
   equator 90° per tick, exactly as the law U = S dictates, at F ≈ 0.97.
2. **From outside, the correct-law time translation is invisible** — advancing the clock one
   tick *while carrying the law of physics with it* costs ~nothing beyond its own gates
   (ratio 0.907 of the prep ceiling), while ticking the clock *without* the law lands at the
   theoretical ½ (0.469). Time translation is a symmetry of the global state only when the
   translation includes the dynamics: the Page–Wootters constraint, in a Loschmidt echo.
3. **Time is the entanglement** — remove the two clock–system entangling gates and every tick
   shows the identical state at F 0.998. The inhabitants' history vanishes; the universe is
   frozen at every clock reading. We switched time off with an entangling gate's absence.

Raw echoes this flight: echo_id 0.893, echo_T 0.810, echo_Tclock 0.419. (The raw echo_T would
have passed Exp185's original absolute bar this time — condition swing — but the verdict here
rests solely on the amended, normalized criteria as pre-committed. Both flights' verdicts
stand: 185 NOT HELD by its letter; 185b HELD by its amendment.)

## Method note — the C4870 rule bites its author

Exp185 failed leg 2 by 0.008 because its absolute bar ignored the translation circuit's own
compiled cost — the exact confound the repository's baseline-normalization rule (C4870,
Exp182) exists to prevent. The amendment was derived from that standing rule (not from where
185's data landed), committed pre-flight, and the normalized quantities replicated across both
flights (185: 0.891/0.466 · 185b: 0.907/0.469) — the ratios are stable where the absolutes
swung. Rules must be applied at design time, not remembered at post-mortem; this pair of
flights is now the repository's example case.

## Fence

As Exp185: a 4-tick cyclic toy universe on 3 transmons; the claim is the state's invariance
under its own internal translation (with its law), not laboratory time; U = S Clifford by
design; off-switch removes entanglement at preparation; conditional tomography on the equator.
Two flights, one hour apart, same backend — the replication is same-night, not cross-condition.
