# Exp-HSS Race 3 — PRE-REGISTRATION **FROZEN** (2026-07-23)

**FREEZE RECORD**: Creator go ("fly race-3 with the split design", this session). Ember 4 fresh
seals quantum@282d228 (#585: rung0_n40 52b07619…, rung0_n32 91adde09…, race_n40 bf48b405…,
race_n32 c06cf711…; hardened format; twin endorsed as "exactly the right d-separator"). Elder
ACK #586: transcription matches #580 faithfully; both unspecified improvements endorsed (twin
unification, dose-matched padding); band standard reaffirmed (band is f(n,t), cap does not move
it; binding constraint = fastest classical edge, quantum wall ≤ 181.8 s); seat split at grade
time (Path A = device physics, Whisper/Ember; Path B = his band, fires only on twin-pass +
exact race decode). All prior race reveals (race-1 AND race-2) remain RETIRED unopened. This
commit, with DRAFT removed, is the freeze.**

*Whisper C4978, 2026-07-23, substrate claude-fable-5. Creator directive: "Fly race-3 with the
split design." Parent: [race-2 verdict](exp-hss-race2-verdict-whisper-c4977.md) + Elder grade
(#580, quantum@d38a309). Court: same 3-of-3 (Ember Sealer / Whisper Flyer-Decoder / Elder
Grader). Freeze = commit with DRAFT removed after Ember's seals + Elder's ACK.*

## The split (Elder #580, adopted): two questions, two graded paths, one new object

The race-2 gate conflated "can the decoder recover at this depth" (shots/hardware) with "does
t=80 behave like t=0" (the science). Race-3 splits them around **the depth-matched twin**: a
t=0 circuit padded to EXACTLY the race d2q, on the same routed layout, flown with the same
structure. The twin is simultaneously:
- **Path A (science, CANNOT fold)**: the differential control — HD and per-bit bias of the
  t=80 race rung vs the t=0 twin at matched depth. This d-separates the t-transfer question
  from the shot boundary and is graded as a MEASUREMENT (a number, not pass/fail).
- **Path B (advantage) gate**: the twin must decode EXACTLY — a gate AT race depth by
  construction, immune to the fold-granularity that ate race-2 (gate placement error = 0 slots).

## Twin construction (frozen)

t=0 transpiles over seeds SEED+0..29 at the race's pinned layout → depths b_s; choose (s, m, j)
with (2m+1)·b_s + 2j = d2q_race exactly, minimizing j (tie: smallest seed, then m). Padding =
j pairs of the folded circuit's OWN 2q layers (L·L = I, algebraically identity; inserted
adjacent; cycling through distinct layers so the added per-slot parallel-gate dose matches the
circuit's own density — a single-pair pad would under-dose the twin and bias the differential).
d2q recomputed after each insertion; build asserts final d2q == d2q_race. Same construction for
n=32 (its own twin at d2q_race32).

## The job (~104 pubs, 640k shots ≈ 165–195 s of ~2,907 s pool)

| Block | Structure | Shots |
|---|---|---|
| LADDER | t=0 base, m ∈ {0,1}, 4 twirls × 5k (curve + in-data convention anchor) | 40k |
| TWIN n=40 | t=0 padded to d2q_race40 exactly, 16 twirls × 6,250 | 100k |
| RACE n=40 | t=80, **32 twirls × 6,250** (2× shot boost per the 245 trend) | 200k |
| TWIN n=32 | t=0 padded to d2q_race32, 16 twirls × 6,250 | 100k |
| RACE n=32 | t=80, 16 twirls × 6,250 | 100k |

**Routing**: race_n40 = best-of-**100** transpile seeds (the 146-class routing is measured to
exist; race-2's 205 was a 20-seed draw); race_n32 = best-of-50. Layout pinned across all n=40
blocks. CZ-twirl (12/12 algebra); exactness gate + logical convention round-trip (race-2's
hardening, kept); manifest records final layouts + d2q per block.

## Frozen decision rules

1. **DEPTH CAP (Path B anti-cherry-pick, frozen BEFORE any transpile)**: race_n40 is
   advantage-eligible only if best-of-100 d2q_race40 ≤ **180** (proven-exact 190 minus margin).
   race_n32 same cap. Cap miss ⇒ Path B ungraded for that rung (stated now, so a deep routing
   day cannot be quietly re-rolled); Path A is measured regardless — the flight is never wasted.
2. **PATH B GATE**: the matched twin must decode EXACTLY (blind Chase-12, full 100k). Twin
   fold ⇒ that rung's advantage path ungraded (Path A still measured). No bracket, no
   granularity — the gate IS the race depth.
3. **PATH A (the t-transfer measurement, cannot fold)**: report, per subsample prefix
   ({2,4,8,16} twin / {2,4,8,16,32} race pubs): HD(ŝ, s) for twin (t=0) and race (t=80) at
   matched depth, and the per-bit bias ratio ρ_t = mean-bias(t80)/mean-bias(t0) with bootstrap
   CI (frozen: 1,000 resamples over pubs). Pre-registered reading: ρ_t ≈ 1 ⇒ magic-free
   per-bit law transfers; ρ_t < 1 ⇒ the magic tax, quantified. Both are wins for the science.
4. **PATH B WIN (unchanged lineage)**: exact ŝ==s on an advantage-eligible race rung +
   re-measured QPU wall (smallest exactly-decoding subsample) ≤ 1/10 of Elder's frozen t=80
   band lower edge at EVERY edge. Supersedable-by-design printed.
5. **Decoder**: frozen blind Chase-12 (ρ=0.5, soft ≤8, vectorized implementation of
   quantum@5dca04a lineage), ŝ in s_str display order, search-adjusted null ≤ 2⁻²⁸.
6. **Two-stage reveal**: (i) ŝ posted for ladder + twins → Ember reveals the two t=0 strings →
   Path-B gates adjudicated + convention anchor checked; (ii) ŝ posted for race rungs → Ember
   reveals race strings → Elder grades Path A differential + Path B (if eligible).
7. **Seals (Ember, 4 strings, upgraded format with s_bits_msb_last + convention line)**:
   rung0_n40 (ladder + twin40 share the t=0 n=40 logical circuit), rung0_n32 (twin32),
   race_n40, race_n32. Fresh crypto-random, fresh salts, hashes public, payload private.
8. **Named failure modes**: (a) ρ_t ≪ 1 (strong magic tax) ⇒ Path B likely misses exact — that
   IS the t-transfer answer, booked straight; (b) routing lottery lands d2q > 180 ⇒ Path B
   ungraded by rule 1, Path A proceeds; (c) twin padding parity unreachable for some (s,m)
   grid ⇒ build aborts pre-submission (no partial improvisation).

## Fences

t=0 blocks (ladder + twins) are Clifford — classically free, no advantage claim attaches. The
Path-A differential is device physics, not advantage. All prior verdicts stay booked
(C4971/C4973/C4976/C4977); reveals of prior race rungs remain retired. No decoder change after
freeze. QPU after this job ≈ 2,710–2,740 s; no further HSS spend without a fresh card.

*Contact: Mike Blakemore.*
