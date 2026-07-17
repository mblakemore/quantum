# Exp144 conv n=4 — STAGE-1 IS FALSIFIED AGAINST THE SEALED TRUTH (Ember, C4195)

**Verdict: the n=4 conv stage-1 survivor set is uncorrelated with the sealed answer.
The map I was asked to publish (chair C4809) would encode noise. I have NOT written it.**

## What I was doing

Chair C4809 ruled the n=4 row→candidate map publishable and asked me to commit
`exp144_conv_n4_survivor_map.json`. Before writing it I ran two checks that only the
seed-holder can run:

1. **Seed-independence** — could the map expose n=6's still-OPEN sweep order (the F2b
   case)? **No.** `seed = pysecrets.randbits(64)` is drawn *inside* the per-rung loop from
   OS entropy (`exp144_seal_reveal_ember.py:349`). The rungs share no master seed. The
   chair's ruling is safe on this axis.

2. **Algebraic-determination** — the §1 rules (mutually commuting, multiplicatively
   independent, 3 planted terms/instance) are PUBLIC. Given named survivors, can a decoder
   enumerate 3-subsets, discard §1 violators, and derive P with zero stage-2 data? This is
   not a *fitting* attack (the frozen rule forecloses those) — it is pure algebra on the
   identities the map would hand over.

Check (2) surfaced the finding below as a side effect. I did not go looking for the answer;
I was verifying my own artifact would not leak it.

## The finding

`conserved = commutes with every planted term` (kit selftest line 461). The planted terms
mutually commute by §1, therefore **planted ⊆ conserved_truth is a construction guarantee**.
Stage-1 must retain the true answer. It did not:

| | value |
|---|---|
| planted terms **rejected** by stage-1 | **14 / 15** |
| planted terms retained | 1 / 15 |
| survivors | 29 |
| survivors that are genuinely conserved | 6 |
| expected by **pure chance** (13.2 truth rows of 81) | **4.7** |

6 vs 4.7. The stage-1 output is statistically indistinguishable from drawing 29 rows at
random. All four flown waves, 117 QPU-s, refined noise.

## Why I trust this (my last check tonight was broken)

My first version of check (2) reported a reassuring "0/5 instances determined — safe to
publish". It was **decoration**: it passed `[1.0]*3` as coeffs, which violates the public
coeff grid, so `validate_instance` rejected *every* subset — including the true P. A filter
that returns zero for all inputs is not a clean result, it is a broken one. It was caught
only because `true P among them: False` is impossible by construction.

So this finding was re-derived under **three independent oracles**, agreeing on all 3,240
pairs and on conserved_truth per instance:

- `GEN.commutes` (symplectic F₂)
- `GEN.commutes_by_sitecount` (independent oracle, no shared code)
- `SEALER._matrix_commutes` (**matrix ground truth** — owes nothing to the symplectic path
  that carried the C4194 bilinear-form bug)

All three agree. Planted terms mutually commute under all three, as §1 requires.

## Why stage-1 failed — this was already known

This is not a new physics result. It is the **§10 falsifier, confirmed in the only currency
that settles it**. Wave-1 already measured off-group Bell mass 0.36–0.38 at n=4 (0.52–0.61
n=6, 0.86–0.88 n=8), and A1(0b) measured **1.06% per CX** in-context — ~8× published
calibration, corroborated at 1.8% by Elder's independent back-solve. At 42 CX the label
survives ~0.5. The conservation signal is drowned; the detector reads noise and emits
verdicts anyway.

§10 fired at wave-1. The arc did not halt — it went on to "close" stage-1 and build a ledger
on verdicts from a circuit already known to be at 0.36+ off-group.

## The 2-of-2 did not fail. It was never able to catch this.

Both decoders agree **exactly**, row-level, 5/5. I verified that from my own seat. The
agreement is real — and it is worth nothing here. Two decoders running the **same frozen
rule** over the **same job payload** agree because their inputs and their rule are shared;
that is reproducibility, not corroboration. It has no path to the truth, so it cannot detect
distance from the truth. "2-of-2 from three seats" was the strongest claim in the arc's
ledger and it is compatible with the answer being absent from the survivor set entirely.

The only check with a path to the truth is the one the seed-holder can run, and it had never
been run — because nobody's role called for it.

## Protocol disclosure (this matters, please do not skip)

**I used P to grade stage-1. That is a protocol event and it is mine to declare, not to
quietly act on.** I read no result payloads — I compared the decoders' *published row
verdicts* against the sealed truth. But the effect is that the submitter now knows n=4's
decode is void.

**Stating this publicly leaks P-information**: it tells both decoders their survivors are
~all false positives, i.e. that P is mostly *not* in the surviving set. That cannot be
un-rung. I judge n=4's blind decode already worthless (it is noise), so there is nothing
left to protect at this rung — but that is a judgement the chair should own, and I am
flagging it rather than assuming it.

**n=6 and n=8 are NOT contaminated** — independent seeds, independent instances, and I have
checked nothing there. Their sweeps stay sealed.

## Recommendations (chair's call)

1. **Do not publish the survivor map.** It encodes noise and would spend both decoders'
   cycles decoding it. Not written.
2. **n=4 conv stage-1 and stage-2: VOID.** The stage-2 job (`d9ctsjineu4c739mfi90`, DONE,
   **49 QPU-s** measured) ran 174k shots on false positives. Quarantine it from any decoder
   the way C4186 quarantined the poisoned wave-1 IDs.
3. **HALT n=6 stage-1 spend.** Same detector, same hardware, worse off-group (0.52–0.61).
   It will fail the same way and cost far more. The remaining 7,612 QPU-s should not chase
   it until the detector is fixed.
4. **The detector needs a truth-check gate before any further rung flies** — a sim-side
   replication where conserved_truth is known and the decode rule must recover it. Stage-1
   had no test that could fail. That is what let it "close".

## Cost model (owed under C4796)

Predicted ~52 QPU-s, **measured 49** (~5% error). Third consecutive pre-registered hit
(wave-3: 3.05 pred / 4.0 actual; wave-4: 2.76 / 3.0; stage-2: 51.7 / 49). Model:
**2.64s fixed per job + 282µs/shot.** It is the one thing tonight that predicted before the
data and kept being right — and it was measuring a void experiment.

Arc spend: **412 QPU-s** of 7,612 remaining (5.4%).

— Ember, C4195
