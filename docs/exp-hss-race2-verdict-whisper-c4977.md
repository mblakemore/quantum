# Exp-HSS Race 2 — VERDICT: gate FOLDED by one bit at a rung 20% past race depth; exact blind recovery proven at d2q=190; the boundary is now bracketed

*Whisper C4977, 2026-07-23, substrate claude-fable-5. Frozen card:
[exp-hss-race2-prereg-FROZEN-whisper-c4977.md](exp-hss-race2-prereg-FROZEN-whisper-c4977.md)
(freeze quantum@adc334d). Job `d9go6ijsbqfc73eovb60`, ibm_marrakesh, 72 pubs, 440k shots,
**132 s QPU** (pool ≈ 2,907 s). Court: Ember sealed/revealed (#570/#578, commitment 94ee0e17
verifies), Elder ACK'd design with disclosure (#571), Whisper flew/decoded blind (ŝ posted
pre-reveal, #576). Adverse routing disclosed pre-decode (#573).*

## One-line verdict

**The frozen exact-at-both gate FOLDED — by exactly ONE bit, at a rung placed 20% past race
depth by fold granularity — race rungs discarded ungraded, no advantage claim. What the 132 s
measured: the blind frozen decoder recovers the sealed 40-bit s EXACTLY at d2q=190 under full
race structure (five-way blind consensus, identity convention, fresh silicon), the exact-recovery
boundary is now BRACKETED at [190, 245) with a shot-resolved interpretable miss, and both
race-1 fold causes are demonstrably fixed. The race depth (205) sits inside the bracket the
gate could not certify.**

## Measured table (blind Chase-12, ŝ vs revealed s, identity convention — held, no artifact)

| Block | d2q | shots | result |
|---|---|---|---|
| ladder m0 | 36 | 20k | **EXACT** |
| ladder m1 | 108 | 20k | **EXACT** |
| gate_below | 190 | 100k (race structure) | **EXACT** — also exact at 12.5k and 50k subsamples |
| gate_above | 245 | 100k | HD-1; subsamples 12.5k/25k/50k = HD-3/3/3 → **shots-limited convergence** |
| race n=40 | 205 | 100k | **UNGRADED** (gate folded; reveals retired unopened, as race-1) |
| race n=32 | 182 | 100k | UNGRADED (same; note 182 < gate_below 190 — would have been in-scope) |

## What this verdict establishes

1. **Both race-1 fold causes are fixed and verified on silicon.** The convention hardening
   held (identity HD-0, no endianness artifact — Ember #578); shot-matching + bracket placement
   moved the certified-exact frontier from 84 (race-1's ladder at 20k) to **190 at 100k** — a
   106-slot extension, exactly the shot-axis prediction Elder called "a real bet" (#571). The
   bet PAID at 190; it fell one bit short at 245.
2. **The fold is fully interpretable** (Elder's diagnostics did their job): HD falls 3→3→3→1
   with shots at fixed depth 245 — boundary shortfall, not placement systematic, not a
   structured competitor. Extrapolating the trend, ~2–3× more shots decode 245.
3. **The gate's failure mode this time was GRANULARITY, not placement philosophy**: the frozen
   rule correctly sought the smallest achievable rung ≥ 205, but fold arithmetic (odd multiples
   of available base depths) offered nothing between 205 and 245. The gate was forced to demand
   more than the race needs. Meanwhile race_n32 (182) sat BELOW the proven-exact 190 — in-scope
   by the n32 rule had the gate passed.
4. **The routing lottery is now a measured row**: d2q_race40 = 146 / 194 / 205 across three
   same-week best-of-20 transpiles of same-class circuits. Routing variance (±20%) is as large
   as a hardware generation's improvement — it belongs in the map.

## Race-3 prescription (needs a fresh Creator go; nothing flies on this card)

The boundary bracket [190, 245) contains the race depth — one granularity fix reaches it:
- **Dense gate grid**: 50–100 t=0 transpile seeds (denser base-depth set b_s) + folds m ≤ 8 →
  gate_above lands within ~2–5% of race depth instead of 20%.
- **Best-of-100 race transpile**: the 146-class routing exists (measured); more seeds pull
  d2q_race toward it — likely BELOW the proven-exact 190, converting the race question from
  "extend the boundary" to "inside certified territory."
- Everything else unchanged: same court, same frozen decoder, same two-stage reveal, same
  classical band (untouched, never invoked). Cost ≈ 130–150 s of 2,907 s.

## Fences

t=0 blocks are Clifford — classically free, no advantage claim attaches to any number above.
Race rungs stay ungraded forever on this card (reveals retired unopened, race-1 precedent).
The C4971 NO-GO and C4973/C4976 folds stay booked. Honest-negative lineage: F54 → steth gate →
C4973 (observable) → C4976 (placement + endianness) → **C4977 (granularity, by one bit)** —
five instruments, each built from the previous miss. The thesis stands un-refuted through all
of it: every blind decode at ≤190 slots has recovered the sealed answer exactly.

*Contact: Mike Blakemore.*
