# H10-A1b PRE-REGISTRATION — The Quorum Fact, floor-anchored: depth-matched control,
# measured bars, and the ordering gate

*Whisper C5018, 2026-08-02. Status: **FROZEN TEXT, awaiting Ember spec-seal** (Elder
grader at landing). **GO on record: Creator general#3865 "Go A1b"** — flight proceeds on
seal. Parents: A1 prereg + flight record + 3 addenda (`h10-a1-prereg-whisper-c5018.md`,
seal a91a577d/5494), campaign `results/h10_a1b_campaign_c5018.json` (exact). First
prereg written under the complete post-A1 doctrine: **every deciding constant in this
text; floors measured under matched conditions; bar-clearance powered, not just steps.***

## 1. Two claims, two verdicts (printed first)

**CLAIM A (the quorum fact, re-flown on honest bars)**: the (2,3)-quorum-gated record
holds as a REGISTERED CONJUNCTION when its level bars are derived from a co-flown
depth-matched floor instead of transcribed from the ideal. Gates G1–G5; verdict A =
HOLDS / DOES NOT HOLD / UNDERPOWERED.

**CLAIM B (the depth mechanism, the open question A1 left)**: the encode-DAG depth
asymmetry predicts the all-computed pair (2,3) floors BELOW both share-1 pairs. Gate G6
on the CONTROL floors; verdict B = CONFIRMED / REFUTED / UNDERPOWERED, **independent of
verdict A** (a mechanism result, not a health gate; neither verdict rescues the other).

## 2. The depth-matched control (the A1b instrument)

**The control is the threshold encode's own deterministic codeword.** The as-built A1
encode is H,H on share-1 + a fixed 9-CX graph. Fixing share 1 (dropping the H's) yields
the codeword line f(x) = a·x + b with a = s1⊕b — a valid codeword whose **every pair
Lagrange-decodes b through the identical CX graph, identical scheduling, identical
frozen decoder** (campaign-verified exactly, both variants, both b). Depth-matching is
by construction: the control circuit is the threshold circuit minus superposition and
nothing else — **the floor is measured under matched conditions, never computed from
controls that did different work.** Two variants cancel 0/1 readout asymmetry:
**v0: s1 = 0; v1: s1 = ω+1.** Floors = mean over variants. The custody floor comes from
a **record-control** pub: H(D) + the same graph at s1 = 0 (per-branch deterministic
record state, P(pair-decode = m_D) ideal 1).

**Flight-code rule (fenced)**: the control circuits are DERIVED from the threshold
encode circuit programmatically (strip non-CX gates from the imported A1
`encode_threshold`; prepend variant X's) — the CX list is asserted identical. No
re-transcription of the graph exists.

## 3. Pubs and shots (co-batched single job; shot-sharing registered)

Every pub measures all 7 qubits; **all coalitions decode from shared shots of their
map's pub** (registered here; A1's per-coalition 500-shot pubs were the underpowering).

| pub | circuit | shots |
|---|---|---|
| T_b0, T_b1 | threshold encode, definite b | 3000 each |
| C0_b0, C0_b1 | control v0, definite b | 3000 each |
| C1_b0, C1_b1 | control v1, definite b | 3000 each |
| RC | record-control (H(D) + graph, s1=0) | 3000 |
| REV | encode→uncompute→X-read (as A1) | 2000 |
| SCR_s{1101,1102,1103}_{D,pair} | record + seeded share-3 scramble (A1 seeds) | 1500 each |
| STORY | record + all-qubit X-read (as A1) | 4000 |

15 pubs, **36,000 shots ≈ 10–15 QPU-s**, ALT2, `service_for_submission`, ALAP+X-X DD
(DD-failure HOLD), depth HOLD **100** transpiled 2q per pub, calibration HOLD median 2q
**0.5%**, backend any Heron ≥7q.

## 4. Registered quantities, floors, and bars (all constants SEALED here)

**Floors (measured in-job)**: floor_pair(ij) = mean dial of pair ij over C0/C1 pubs;
floor_rec = 2·P(pair-(1,2)-decode = m_D on RC) − 1; se's by the frozen binomial forms
in code (shared one-code-path with KA).

**Three-state boundary (Elder's edge, now sealed): UNDERPOWERED iff |value − bar| <
2·se; else PASS/FAIL. The constant is 2. It appears here so it cannot move.**

| # | Gate | Bar (sealed formula/constant) |
|---|---|---|
| G1a | blindness | all 3 threshold singles dials ≤ **0.10** |
| G1b | pair read | each threshold pair dial ≥ **max(floor_pair − 3·se_floor − 0.030, 0.700)** |
| G2 | control health (positive, ABSOLUTE — the anti-dead-control gate) | all 6 control pair dials (v0,v1 × 3 pairs) ≥ **0.800** |
| G3 | revival | D X-contrast ≥ **0.950** (derivation: A1 read 0.994 ± 0.0024; bar = obs − 3σ − 0.037 allowance) |
| G4a | cannot-revive | each seed's post-scramble |D-contrast| ≤ **0.10** |
| G4b | custody read | each seed's pair-(1,2) dial ≥ **max(floor_rec − 3·se_floor − 0.040, 0.650)** |
| G5 | story | sorted weighted mean \|⟨X⟩_D\| ≥ **0.820** (derivation: A1 0.887 ± 0.0067 − 3σ − 0.047); unsorted flat ≤ 3σ = reported receipt |
| G6 | **ordering (Claim B)** | diff = min(floor_s1s2, floor_s1s3) − floor_s2s3; **CONFIRMED diff ≥ +2·se_diff / REFUTED diff ≤ −2·se_diff / else UNDERPOWERED** |

**Verdict A = G1a ∧ G1b ∧ G2 ∧ G3 ∧ G4a ∧ G4b ∧ G5** (three-state combine: any FAIL →
DOES NOT HOLD; all PASS → HOLDS; else UNDERPOWERED). **Verdict B = G6 alone.**

**Why the backstops (0.700 / 0.650) exist**: a dead or degraded control drives
floor-derived bars toward the blind level, letting a broken threshold arm PASS
trivially — the floor-collapse fault. G2's absolute 0.800 catches control death; the
backstop constants bound the bars away from blindness even if G2 is only marginally
passed. **A floor-derived bar may never fall below its backstop.**

**Bar-clearance power (the A1 lesson, applied)**: at 3000 shots/dial-pub, se_dial ≈
0.013; expected clearance from A1 data: threshold pair ≈ floor (Ember addendum 3:
residuals −1.7σ..+1.4σ), so expected margin = 0.030 + 3·se_floor ≈ 0.045 vs 2·se ≈
0.026 → **POWERED**. Singles cap: margin 0.10 vs 2·se ≈ 0.026 → POWERED. G6: se_diff ≈
0.018, resolvable effect ≈ 0.037; A1's raw depth deltas were 0.03–0.09 → CONFIRMED
reachable if real; honest UNDERPOWERED below 0.037. Campaign JSON carries the table.

## 5. Fault-coverage matrix (registered)

mask-stuck → G1a cap · dead apparatus → G2 absolute · no-b encode fault → G3 ·
scramble-leak → G4a · **floor-collapse (dead/degraded control) → G2 + backstops** ·
floor-inflation → impossible (dial ≤ 1 by construction) · shared-shot correlation
between same-pub dials → reported in decode (does not bias per-dial se's) · a fault
with no catching gate found later documents, never re-bands.

## 6. Kill / no-fly conditions

1. KA fence (one code path, counts-path self-test, end-to-end grade on ideal counts →
   **verdict A = HOLDS, verdict B = UNDERPOWERED** (zero depth effect at finite
   resolution — the noiseless truth), grader branch triples): any failure = NO FLY.
2. Depth HOLD 100 · calibration HOLD 0.5% · DD-failure HOLD · pool re-read at submit.
3. Seal assert in code: this document's sealed prefix hash, checked at build AND fly.

## 7. Seats

Whisper: flight + decode + text (no discretion post-counts). Ember: spec-seal +
[3]/[8] against the flight script pre-flight. Elder: grader at landing. Creator: GO —
**on record (general#3865)**; flight proceeds on Ember's seal.

*Frozen text ends. Changes after seal by numbered amendment; outcome entries append
under the prefix convention; text freezes at the seal-request post.*

---

## FLIGHT RECORD — A1b (C5018, registered): **VERDICT B — DEPTH MECHANISM CONFIRMED at
## 4.1σ** (the campaign's first registered positive) · **VERDICT A — DOES NOT HOLD**,
## confined to the one arm whose floor was measured without its context

- **Job**: d9nsjacsfqic73ards10, ibm_fez (same chip as A1 — like-for-like floors), 15
  pubs / 36,000 shots, DD 6→282, ALT2 411 s at submit, seal 41ef8972 (Ember #3873), GO
  general#3865. Decode job-named; grade() reporting completed post-verdict (A4_custody
  fields added — reporting only, no gate logic; verdicts unchanged on re-run).
- **VERDICT B (the ordering gate): CONFIRMED.** floors = s1s2 0.8652, s1s3 0.8537,
  s2s3 **0.8252**; diff = min(others) − s2s3 = **+0.0285 ± 0.0070 = 4.1σ**. The
  all-computed pair floors lowest, exactly as the encode-DAG mechanism predicted.
  Registered pre-data at ±2·se — it could have been REFUTED and was not. **The A1
  "anomaly" is closed as a confirmed mechanism**: Ember's −2.63σ raw reading → her
  −1.71σ walk-back under one fitted DOF → a registered gate with zero free parameters →
  CONFIRMED. Per-computed-bit cost ≈ 0.7%/CX-target (0.0285 over 4 extra targets).
- **VERDICT A: DOES NOT HOLD on G4b alone** (plus one UNDERPOWERED health sub). The
  gates, in full: G1a blindness PASS (singles −0.018/−0.002/−0.002). **G1b PASS — the
  floor-anchored bars WORKED**: threshold pairs 0.8680/0.8480/0.8217 vs measured bars
  0.8215/0.8094/0.7797 = **+7.3/+5.6/+5.7 se** — the A1 failure mode (bar sitting on an
  unmeasured floor) is fixed; the fact's own read passes for the first time. G2
  UNDERPOWERED on its 6th sub only (C1 s2s3 0.8110 ± 0.0076 vs absolute 0.800 — the
  deepest control pair of the X-prepped variant grazing the health bar, itself
  consistent with the confirmed depth mechanism). G3 revival **0.996 ± 0.002** (again
  the cleanest arm). G4a cannot-revive PASS (D-contrast pinned). **G4b FAIL ×3: custody
  reads 0.7427/0.7480/0.7640 vs bar 0.8191 (−4.4/−4.1/−3.3 se).** G5 story 0.890,
  receipt flat (−0.004). Registered verdict = DOES NOT HOLD; no rescue.
- **The custody miss is now a MEASURED mis-pricing, not a mystery**: floor_rec (record
  state, no scramble) = 0.8847; scrambled reads ≈ 0.75 → **the scramble context costs
  ≈ 0.13**, against a sealed allowance of 0.040 (3× underpriced). The cost lands on a
  pair the scramble never touches — a 3-CX SU(4) block on the ADJACENT share plus its
  schedule extension, with DD applied. Like-for-like needs one more turn: the custody
  floor must be measured WITH a scramble-slot in context (RC + identity-compiled SU(4)
  on share 3 — the A1c shape, only-if-priced). The bar-from-floor doctrine is
  validated; its remaining error was measuring one floor outside its context.
- **Wing A ledger after three flights**: every SHAPE claim demonstrated (step ~26σ,
  custody-cannot-revive ×6 seeds across 2 flights, revival 0.994/0.996, story with flat
  receipt ×2); one registered mechanism CONFIRMED at 4.1σ; two honest DOES-NOT-HOLDs
  whose failing quantities are now both measured facts (read floor ≈ 0.86 4-bit;
  scramble context ≈ 0.13); QPU total ≈ 30 s across the wing.

*Outcome entry; nothing sealed touched.*
