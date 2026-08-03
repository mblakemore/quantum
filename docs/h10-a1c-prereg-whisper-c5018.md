# H10-A1c PRE-REGISTRATION — The Quorum Fact, context-priced: per-seed custody floors
# and the context-cost gate

*Whisper C5018, 2026-08-02. Status: **FROZEN TEXT, awaiting Ember spec-seal** (Elder
grader at landing). **GO on record: Creator direct message 2026-08-02 "run A1c"** —
flight proceeds on seal. Parents: A1b prereg + record + addenda (seal 41ef8972/7384),
campaign `results/h10_a1c_campaign_c5018.json`. Doctrine: every deciding constant in
this text; floors measured under matched conditions **including circuit context**;
bar-clearance powered.*

## 1. Two claims, two verdicts

**CLAIM A (the quorum fact, custody context-priced)**: the (2,3)-quorum-gated record
holds as a registered conjunction when EVERY level bar — including custody — derives
from a floor measured in the bar's own full circuit context. Gates G1a–G5; verdict A =
HOLDS / DOES NOT HOLD / UNDERPOWERED.

**CLAIM B (the context cost, the open number A1b measured once)**: an SU(4) scramble
block on share 3 costs the pair-(1,2) read a reproducible amount (~0.10–0.13 at A1b)
even though it never touches the pair. Statistic: **cost = floor_plain(RC) −
mean_seed(floor_ctx)**. Verdict B = CONFIRMED (≥ +2·se_diff) / REFUTED (≤ −2·se_diff)
/ UNDERPOWERED. Independent of verdict A; neither rescues the other. Ideal (noiseless)
cost = 0 → UNDERPOWERED, the correct null, sealed as the KA e2e target.

## 2. The context-matched custody control (the A1c instrument)

**floor_ctx(seed) is measured on the deterministic codeword (v0, s1 = 0, definite b)
WITH that seed's actual scramble on share 3.** Shares 1 and 2 are computational-basis
definite and the scramble's support {q5,q6} is disjoint from the pair-read's support
{q1..q4}: the pair-(1,2) Lagrange decode returns b EXACTLY under ANY share-3 unitary —
ideal dial 1, an integer KA target, proved in the fence by statevector with the real
seeded unitaries. Same seed, same gates, same schedule shape as the gated custody arm:
**the floor prices readout + encode depth + scramble context, per seed,
like-for-like.** The only unpriced delta is the D-superposition (record vs definite-b),
measured ≈0.008 at A1b (RC 0.8847 vs C0_s1s2 0.8927) — covered by the sealed 0.030
allowance. The ordering result (A1b's G6 CONFIRMED) is **re-measured and REPORTED as
replication data, not re-gated** — honest replication without verdict inflation.

## 3. Pubs and shots (co-batched single job; shot-sharing registered as A1b)

| pub | circuit | shots |
|---|---|---|
| T_b0, T_b1 | threshold encode, definite b | 3000 each |
| C0_b0, C0_b1, C1_b0, C1_b1 | depth-matched controls (as A1b) | 3000 each |
| RC | record-control, no scramble (floor_plain) | 3000 |
| SCTX{1101,1102,1103}_b{0,1} | codeword v0 + that seed's scramble (floor_ctx) | 1500 each |
| REV | encode→uncompute→X-read | 2000 |
| SCR{seed}_{D,pair} | record + seeded scramble (the gated custody arm) | 1500 each |
| STORY | record + all-qubit X-read | 4000 |

21 pubs, **45,000 shots ≈ 12–16 QPU-s**, ALT2 via `service_for_submission`, ALAP+X-X
DD (DD-failure HOLD), depth HOLD **100**, calibration HOLD median 2q **0.5%**, Heron
≥7q. Scramble seeds frozen as A1/A1b: 1101, 1102, 1103.

## 4. Registered bars (all constants SEALED here)

**Three-state boundary: UNDERPOWERED iff |value − bar| < 2·se; else PASS/FAIL. The
constant is 2. It appears here so it cannot move.**

| # | Gate | Bar (sealed formula/constant) |
|---|---|---|
| G1a | blindness | all 3 threshold singles dials ≤ **0.10** |
| G1b | pair read | each threshold pair dial ≥ **max(floor_pair − 3·se_floor − 0.030, 0.700)** (floors from C0/C1, as A1b — VALIDATED there at +5.6–7.3 se) |
| G2 | control health (positive, ABSOLUTE) | all 6 control pair dials ≥ **0.780** (re-derived pre-data per Elder #3883: A1b deepest pair 0.8110 − 3·0.0076 ≈ 0.788, rounded down; ≫ dead ≈ 0; clearance 0.031 vs 2·se 0.015 → POWERED) |
| G3 | revival | D X-contrast ≥ **0.950** |
| G4a | cannot-revive | each seed's post-scramble \|D-contrast\| ≤ **0.10** |
| G4b | custody read, context-priced | each seed's pair-(1,2) dial ≥ **max(floor_ctx(seed) − 3·se_floor(seed) − 0.030, 0.650)** — per-seed bars from per-seed floors; allowance 0.040→0.030 because the context is now in the floor |
| G5 | story | sorted weighted mean \|⟨X⟩_D\| ≥ **0.820**; unsorted flat ≤ 3σ = reported receipt |
| B | context cost | cost = floor_plain − mean_seed(floor_ctx); **CONFIRMED ≥ +2·se_diff / REFUTED ≤ −2·se_diff / else UNDERPOWERED** |

**Verdict A = G1a ∧ G1b ∧ G2 ∧ G3 ∧ G4a ∧ G4b ∧ G5** (any FAIL → DOES NOT HOLD; all
PASS → HOLDS; else UNDERPOWERED). **Verdict B = the context-cost gate alone.**
Backstops 0.700/0.650 as A1b (floor-collapse fault: G2 absolute + backstops; a
floor-derived bar may never fall below its backstop).

**Power (campaign JSON)**: G4b — expected floor_ctx ≈ 0.76, bar ≈ 0.694, expected read
≈ 0.75 → clearance ≈ 0.056 vs 2·se ≈ 0.034 → POWERED. B — se_diff ≈ 0.011 vs expected
cost 0.10–0.13 → >8σ if real. G1b/G1a/G3/G5 carried with A1b-demonstrated margins.

## 5. Fault-coverage matrix

As A1b (mask-stuck → G1a · dead apparatus → G2 · no-b → G3 · scramble-leak → G4a ·
floor-collapse → G2 + backstops) **plus: scramble-slot miscompiled (SCTX pub silently
missing its scramble) → caught by B**: floor_ctx would read ≈ floor_plain, cost ≈ 0 →
B returns UNDERPOWERED/REFUTED instead of CONFIRMED — the fault surfaces in a
registered verdict, not silently. A fault with no catching gate found later documents,
never re-bands.

## 6. Kill / no-fly conditions

1. KA fence: one code path; counts-path self-test; e2e grade on ideal counts →
   **A = HOLDS, B = UNDERPOWERED**; boundary-2 discriminating grader triples. Any
   failure = NO FLY.
2. Depth HOLD 100 · calibration HOLD 0.5% · DD-failure HOLD · pool re-read at submit.
3. Frozen-text hash asserted in code at build AND fly.

## 7. Seats

Whisper: flight + decode + text (no discretion post-counts). Ember: spec-seal + [3]/[8]
pre-flight. Elder: grader at landing. Creator: GO — **on record (direct, "run A1c")**;
flight proceeds on Ember's seal.

*Frozen text ends. Changes after seal by numbered amendment; outcome entries append
under the prefix convention; text freezes at the seal-request post.*

---

## FLIGHT RECORD — A1c (C5018, registered): **VERDICT A — UNDERPOWERED with ZERO FAILS**
## (the wing's first no-fail flight; two seed-margins short of HOLDS) · **VERDICT B —
## CONFIRMED at 2.1σ, and the magnitude rewrites the context-cost story**

- **Job**: d9ntia460llc73cagnfg, ibm_fez (third flight, same chip), 21 pubs / 45,000
  shots, DD 6→414, ALT2 399 s at submit, seal 1fe4b5eb (Ember #3915), GO general#3911.
  Decode job-named: `results/h10_a1c_decode_d9ntia460llc73cagnfg.json`.
- **VERDICT A: UNDERPOWERED — no gate failed anywhere.** G1a PASS · **G1b PASS
  (+8.9/+8.8/+7.4 se — floor-anchored bars validated a THIRD time)** · **G2 PASS 6/6 at
  the re-derived 0.780 (Elder's TODO fix worked: no sub grazing)** · G3 PASS (revival
  contrast 1.0000 this run — the arm's third consecutive ≥0.994) · G4a PASS ×3 ·
  **G4b: [UNDERPOWERED, UNDERPOWERED, PASS]** — custody reads 0.8120/0.8160/0.8440 vs
  per-seed bars 0.8021/0.8130/0.8123 = margins **+0.66/+0.20/+2.29 se: all three
  POSITIVE, two unresolved at the sealed 2·se boundary** · G5 PASS (0.880, receipt flat).
  The conjunction sat two seed-margins from the wing's first HOLDS, and the registered
  rule correctly refused to claim what 1500-shot pubs could not resolve. **The bars were
  almost perfectly placed** (reads − bars = +0.010/+0.003/+0.032): the context-matched
  floor minus the 0.030 allowance landed ON the true operating point.
- **VERDICT B: CONFIRMED — cost = +0.0209 ± 0.0099 (2.11σ, clearing its sealed 2·se bar
  by 0.11σ — a hair, stated as such).** The context cost is REAL on the codeword and
  SMALL — and that rewrites the A1b story in a way only this instrument could:
  **the scramble's damage decomposes into three measured pieces**:
  (i) codeword context cost (B, same job): **0.021**;
  (ii) record-state interaction (floor_ctx − record reads, per seed): **+0.048/+0.054/
  +0.025** — the D-superposition pays roughly DOUBLE the codeword's cost again;
  (iii) job-state dependence: scramble-on-record cost was **0.13 in A1b's job, 0.063 in
  this one** — same seeds, same chip, ~2.5 h apart (DD pulse counts 282 vs 414). **The
  "context cost" is not a physical constant of the gadget; it is dominated by
  scheduling/calibration state and roughly halved overnight.** A1b's 0.040 allowance
  wasn't merely 3× under-priced — it was pricing a moving target. A1c's per-seed
  same-job floors are the only reason the bars landed on the operating point.
- **Ordering replication (reported, not gated, exactly as sealed)**: diff = +0.0222 ±
  0.0071 = **3.1σ, same direction** — the A1b CONFIRMED mechanism replicates out of
  registration. Floors s1s2 0.8550 / s1s3 0.8438 / s2s3 0.8217.
- **Wing A final ledger (four flights, ~44 QPU-s)**: A1 DNH (bar artifact — proven by
  A1b) → A1b DNH on one arm + mechanism CONFIRMED 4.1σ → **A1c zero fails,
  UNDERPOWERED by two thin true margins + context-cost CONFIRMED + ordering
  replicated 3.1σ**. Each flight failed exactly one layer deeper than the last; the
  final state is a conjunction whose every gate is either passing or unresolved-thin,
  with three registered positives (mechanism, replication, context-cost) inside the
  campaign. **Paths, only-if-priced**: A1d = same instrument, custody pubs at 4–6×
  shots (~+20k) to resolve the two thin margins — with the honest statement that the
  true margins are ~+0.003–0.010 and resolution could land EITHER side; or rest here,
  where the record already says everything the hardware said.

*Outcome entry; nothing sealed touched.*
