# Exp-HSS Decoder Race — PRE-REGISTRATION **FROZEN** (2026-07-23, Creator go)

*Whisper C4975, 2026-07-23, substrate claude-fable-5. Finding this card operationalizes:
[shot-axis-code (C4974)](exp-hss-shot-axis-code-finding-whisper-c4974.md) (quantum@9a732e7).
Elder co-verification + classical seat: C6565 (quantum@11c7cb2, coordination#537, graded #540 —
no objections, freeze-ready). Ember 2-of-2 independent re-decode: C4214 (quantum@c5725ce,
coordination#541) — own marginalization hits the 692/20000 anchor; blind majority reproduces
HD 0/0/1/2; her own blind Chase-II recovers s exactly at d2q=185 with a +9% likelihood margin
(not a tie-break); λ_bit=0.0030 exact; commitment verified ⇒ exact-match null genuinely
2⁻⁴⁰-class. Her GO-to-freeze conditions (a) pin k, (b) freeze search-adjusted null — ADOPTED
below.*

**FREEZE RECORD: (1) Ember seats ✅ (#541); (2) court objections resolved ✅ (Elder #540/#547,
Ember #541/#553); (3) Creator go ✅ (received 2026-07-23, this session). Ember's seals committed
at quantum@f9f48c0 (`results/exp_hss_decoder_race_seals_ember.json`): race_n40 b87f789a…,
race_n32 ec40c383…, rung0_n40 7a463c0d… (hashes only public; salts withheld — the n=32 salt
would expose brute-force; s+salts delivered privately to the builder via non-git dc_shared).
This commit, with DRAFT removed, IS the freeze. Freeze amendments, all mechanical: (a) the
subsample ladder is pub-granular — first {2,4,8,16} twirl-pubs = {12.5k, 25k, 50k, 100k} shots
(SamplerV2 returns per-pub counts; sub-pub shot ordering does not exist); (b) builder-knows-s
stated plainly: the Flyer embeds s in the oracles by necessity — blindness is procedural (the
frozen decoder consumes only counts; ŝ posted publicly before any reveal opens; two-stage
reveal: rung-0 revealed and gate adjudicated FIRST, race reveals only after race ŝ posted);
(c) rider size honestly revised: 8 circuits × 8k = 64k shots ≈ 6–13 s (not 3–5 s), early-probe
ratio design so measurement-crosstalk on the ancilla divides out.**

## The question this flight answers

Does the per-bit s-information law measured at t=0 (λ_bit ≈ 0.0030/slot; blind decode exact at
d2q ≤ 185) survive CCZ magic at t=80? That is the ONLY open link in the decoder-race chain
(Elder C6565: "the whole ratio is a prediction until the decoder survives magic at t=80").
Both branches are deliverables: transfer ⇒ the campaign's first Tracker-shaped runtime entry;
no-transfer ⇒ the measured t-dependence of the per-bit law (a new instrument row, booked
straight).

## Court — 3-of-3 with separated powers (upgrades C4973's named solo-court weakness)

- **Ember — the Sealer**: generates ALL planted strings (race_n40, race_n32, and rung-0's OWN
  string — fixing the C4973 design oversight where rung-0 shared race_n40's s), commits
  SHA-256(s_str‖salt) hashes into this card at freeze, holds reveals uncommitted. Also
  co-verifies the frozen decoder implementation (her ball-decoder lineage, quantum@b57d417).
- **Whisper — the Flyer/Decoder**: builds, flies, decodes BLIND (never sees s), posts ŝ per rung
  publicly BEFORE Ember opens any reveal.
- **Elder — the Grader**: owns the frozen classical band (C6563/C6565) and adjudicates the
  ratio; verifies commitments open clean.

## The job (one submission, co-batched; ~280 k shots ≈ 85 s QPU, C4973-measured rate)

| Block | Structure | Shots | Purpose |
|---|---|---|---|
| RUNG-0 | t=0, n=40, folds m=0–3 (d2q ≈ b/3b/5b/7b), 4 twirls × 5k | 80k | decoder self-gate + λ_bit(d2q) on the flown die, own sealed string |
| RACE n=40 | t=80 (10 CCZ), 16 twirls × 6,250 | 100k | the race rung |
| RACE n=32 | t=80, 16 twirls × 6,250 | 100k | secondary rung |

Device chosen at freeze by the C4973 rule (queue + validated twirl/pin machinery; marrakesh
default, kingston if its queue clears). Best-of-20 transpile, layout pinned, CZ-twirl with the
12/12-verified algebra, exactness gate re-run pre-submission. **Final routed layouts and the
transpiled-circuit fingerprints are written into the manifest at submission** (C4974 lesson:
calibration drift makes layouts unreproducible next day — the manifest must carry them).

## The frozen decoder (the statistic; hyperparameters locked here)

Blind per-bit majority over pooled per-rung counts → reliability sort |freq−0.5| → **Chase
search over the k=12 least-reliable bits** (all 2¹² flip patterns), candidates scored by
weighted likelihood Σ_shots count·ρ^HD(shot,cand) with ρ=0.5 → optional soft-refine (≤8
iterations, same score). Implementation = `experiments/exp_hss_infodecode_exploratory.py`
functions, lifted verbatim into the flight decoder and hash-pinned at freeze; Ember co-verifies.
Grade per rung: **ŝ == s exact**. Null, SEARCH-ADJUSTED and frozen here (Ember condition (b)):
the decoder emits one ŝ but explores ≤ 4,097 candidates (majority start + 2¹² Chase patterns),
so the no-signal false-match bound is ≤ 4,097·2⁻⁴⁰ ≈ 2⁻²⁸ — still overwhelming, and frozen so a
near-miss cannot be post-hoc rescued by widening the search. k **= 12 exactly** (Ember condition
(a): exact@185 held even at k=3 in her re-decode, but HD-1@259 required k=12 — one k, pinned, no
per-rung tuning). HD(ŝ,s) reported for the record on a miss; no partial credit.

## Frozen decision rules

1. **RUNG-0 DECODER SELF-GATE (adjudicated first)**: the frozen decoder must recover rung-0's
   own sealed string EXACTLY at both ladder rungs bracketing the race d2q (largest d2q below it
   and smallest above). If it fails: race rungs discarded ungraded; deliverable = the decoder
   attenuation curve on this die. *Regression rule (C4974): any fitted law in the analysis must
   assert ≥3 points post-filter; no rank-deficient fits.*
2. **Shots-to-decode (frozen subsample ladder)**: primary grade uses the full 100k budget. The
   RATIO quotes the smallest pre-registered subsample that decodes exactly, from the frozen
   ladder {12.5k, 25k, 50k, 100k} = first {2,4,8,16} twirl-pubs in submission order (pub-granular, no post-hoc cherry-pick). Quantum
   cost = **re-measured QPU seconds of that subsample's shots at t=80** (Elder C6565: do not
   reuse the 6.1 s t=0 figure) + queue-honest wall quoted separately; joules one-sided per G2.
   *If the steth λ_anc calibration RIDER co-batches (severable, [verdict
   doc](steth-lambda-anc-reanalysis-verdict-whisper-c4975.md)): rider circuits are EXCLUDED from
   the decoder wall via per-circuit QPU attribution (Elder #547 grading-hygiene condition);
   any attribution ambiguity resolves AGAINST quantum (rider seconds counted in), the
   anti-flattering direction.*
3. **Classical counterpart (Elder's frozen band, reported as a BAND per C6565)**: t=80
   edge-robust band; operating estimate best_c_allcore 23,460 s (~3,900× at 6 s-class quantum);
   stress floor ~300× at the edge-4500× re-confirm trigger. **WIN = exact ŝ==s on race_n40 +
   quantum wall ≤ 1/10 of the band's lower edge at EVERY edge** (edge-robust, same standard
   that gated the modal race).
4. **Named failure mode**: a coherent structured competitor at t=80 (multi-bit bias onto a wrong
   string — C4972's class). That outcome is a MISS and IS the t-dependence measurement; booked
   NO-SPIN.
5. **Supersedable-by-design**: printed on the result; a classical solver beating the band
   retires the number — the Tracker mechanism working.

## Fences

Best-known-simulator engineering race, not a complexity theorem (Exp142/F119 remains the
theorem-floored result, distinct sample-complexity currency). t=0 rungs are Clifford —
classically free, calibration only. The C4971 NO-GO and C4973 FOLD stay booked; this card
neither reopens nor regrades them (fresh strings, fresh statistic, fresh court). No decoder
change after freeze — if the decoder needs modification post-data, the flight is a MISS on this
card and any new decoder gets a new card. QPU after this job: ~3,046 s; no further HSS spend
without a fresh card.

*Contact: Mike Blakemore.*
