# Exp-HSS Decoder Race 2 — PRE-REGISTRATION (fixed gate placement) — **DRAFT until Ember seals**

*Whisper C4977, 2026-07-23, substrate claude-fable-5. Creator directive: "Fly the re-fly with the
fixed gate placement." Parent verdict: [C4976](exp-hss-decoder-race-verdict-whisper-c4976.md)
(gate folded on placement past the measured exact-recovery boundary + 20k/100k shot asymmetry).
This card implements Elder's grader prescription (#565) verbatim. Court: same 3-of-3 separated
powers (Ember Sealer / Whisper Flyer-Decoder / Elder Grader). Freeze = this card committed with
DRAFT removed after Ember's fresh seals land.*

## What changed vs C4975 (the two fold causes, fixed; nothing else moved)

1. **Gate placement — rungs BRACKET race depth tightly, chosen by frozen deterministic rule.**
   After the race transpile fixes d2q_race (n=40) and the t=0 base transpile fixes b:
   - gate_below = largest (2m+1)·b_s ≤ d2q_race, gate_above = smallest (2m+1)·b_s ≥ d2q_race,
     searching m ∈ 0..6 over the t=0 transpile depths b_s from seeds SEED+0..19 (all with the
     race's pinned layout). No more demanding exactness 34% past race depth.
2. **Shot-matching — gate rungs fly the RACE structure exactly**: 16 twirls × 6,250 = 100k
   shots each, identical to the race rung they predict (C4976 left √5 of per-bit z on the
   table by gating at 20k).
3. **Convention round-trip (C4976 endianness lesson)**: (a) Ember's seal file must carry
   `s_str` AND `s_bits_msb_last` AND a one-line convention statement; (b) the pre-flight
   exactness gate now round-trips builder → transpile → marginalize → compare-to-s_str (the
   C4976 gate checked builder-only); (c) the frozen decoder reports ŝ in **s_str display
   order** (reverse of qubit-index marginal — pinned by the C4976 sim).

## The job (one submission, ~72 pubs, 440k shots ≈ 130–145 s of ~3,039 s pool)

| Block | Structure | Shots |
|---|---|---|
| LADDER (curve+anchor) | t=0, m ∈ {0,1} of base b, 4 twirls × 5k | 40k |
| GATE_BELOW | t=0 at largest (2m+1)b_s ≤ d2q_race, 16 twirls × 6,250 | 100k |
| GATE_ABOVE | t=0 at smallest (2m+1)b_s ≥ d2q_race, 16 twirls × 6,250 | 100k |
| RACE n=40 | t=80 (10 CCZ), 16 twirls × 6,250 | 100k |
| RACE n=32 | t=80, 16 twirls × 6,250 | 100k |

Device by the standing rule (queue + validated machinery; marrakesh default). Best-of-20 race
transpile; layout pinned across all n=40 blocks; CZ-twirl (12/12 algebra); manifest records
FINAL routed layouts + d2q for every block. All t=0 blocks embed ONE sealed rung-0 string
(same logical circuit; folds/stretches are transpile-level).

## Frozen decision rules

1. **GATE (adjudicated first, two-stage reveal as C4976)**: frozen decoder must recover the
   rung-0 sealed string **EXACTLY at BOTH gate rungs at their full 100k shots**. Now fair by
   construction: same depth class, same shots, same twirl structure as the race rung it
   predicts. FOLD ⇒ race rungs discarded ungraded; deliverable = the shot-matched decoder
   attenuation points + curve. No bounded-HD softening: with placement and shots matched, exact
   is the honest bar (Elder's option (a)+(3), not (b)).
2. **Race grading (unchanged from C4975)**: frozen blind Chase-12 (ρ=0.5, soft ≤8, k=12,
   search-adjusted null ≤ 4,097·2⁻⁴⁰ ≈ 2⁻²⁸); pub-granular subsample ladder {2,4,8,16} pubs;
   primary grade at 16; ratio quotes the smallest exactly-decoding subsample with QPU
   re-measured at t=80. ŝ posted publicly before reveals; rung-0 revealed and gate adjudicated
   before race decode.
3. **n=32 scope rule (new, honest)**: race_n32 is graded ONLY IF d2q_race32 ≤ gate_above's
   d2q; otherwise informational-ungraded (its depth was outside the gate's certified region —
   C4976's n32 at 182 vs n40 gate would have had exactly this gap).
4. **WIN (unchanged)**: exact ŝ==s on race_n40 + quantum wall ≤ 1/10 of Elder's frozen t=80
   band lower edge at EVERY edge (band ~300× stress / ~3,900× operating). Supersedable-by-design
   printed. Every other outcome booked as measured, no spin.
5. **Named failure modes**: (a) coherent structured competitor at t=80 (the open t-transfer
   question — a MISS here IS the t-dependence measurement); (b) day/placement variance pushing
   even shot-matched gate rungs past exactness — that outcome quantifies the placement lottery
   and folds honestly.

## Fences

Best-known-simulator engineering race, not a complexity theorem; Exp142/F119 distinct currency.
t=0 blocks classically free (calibration, no advantage claim). C4971 NO-GO, C4973 FOLD, C4976
FOLD all stay booked; fresh strings (never reused), fresh salts. No rider this flight (Creator
scoped the re-fly; steth co-batch remains its own future micro-card). No decoder change after
freeze. QPU after this job ≈ 2,900 s; no further HSS spend without a fresh card.

*Contact: Mike Blakemore.*
