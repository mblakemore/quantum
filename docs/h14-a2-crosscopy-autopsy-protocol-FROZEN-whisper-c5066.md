# H14 cell A2 — THE GHOST IN THE CARGO BAY: analysis protocol (FROZEN before decode)

**Author**: Whisper (DC15W), C5066 (2026-08-13) · **Substrate**: claude-fable-5
**Arc**: H14 Deck A (charter `docs/h14-the-alien-ship-whisper-c5064.md`), committed-before-decode per the temporal-steering precedent. **This freeze is written from structure and summaries only** — grade-file probe *summaries* (max_abs, mean_abs, max_sigma) have been seen; **no per-probe signed vector has been decoded by this seat**. Custody state, corrected in-draft before this freeze was committed (the first draft called `raw_science` files "metadata" — wrong: their `shots` key holds the full shot-level record, ~2.6 MB / 72,759 entries for i1): **shot-level science data IS banked for the distribution instances** (`results/doorb_dist_i{1,2,3}_raw_science_n16_elder.json` + refly/original `doorb_*raw_science*` variants where present); grades carry summaries only. The protocol freezes the discrimination method before the vectors are ever assembled.
**Genre fence**: mechanism attribution for the F122 residual physics. No advantage claim; F122's claim card is untouched (its footnote gains a measured basis either way).

## The target

The F122 grade measured, on the 48 weight-1 probes (n=16 qubits × 3 Paulis), a **signed cross-copy correlation ~0.04** (max 13.6σ across the family; i1's blind-probe summary shows the same class) while the 64 weight-heavy probes sit at true shot noise (0.0069). Sign structure already killed "polarization." Candidate mechanisms and their frozen signatures below.

## Stage 0 — custody verification + conditional repair ($0 QPU, read-path only)

Per flight, verify a shot-level science record exists on disk (`doorb_*raw_science*` with a populated `shots` list matching the manifest's shot count). For any flight missing one, re-pull raw counts by job ID via `ibm_multi_account.service_for_job` (read path; jobs flown 2026-08-05→12, within retention) and bank to `results/h14_a2_raw_<jobid>.json` **without decoding probe values** — the banking script writes counts verbatim and computes nothing. Distribution instances i1–i3 are already banked (verified); the first-FAIL and original-WIN flights are the candidates for repair.

## Stage 1 — assemble structure vectors (non-outcome metadata only)

From manifests + backend configuration (not from counts): probe index map (qubit q ∈ 0..15 × Pauli P ∈ {X,Y,Z} → physical qubit), the device coupling map for the flown layout, readout multiplexing groups, and per-flight physical layouts. Deliverable: the three **signature vectors** over probe index, computed by these frozen recipes:

- **S1 readout-line crosstalk**: indicator/weight vector from readout multiplexing group co-membership of the probe's physical qubit with other in-register qubits (group size − 1, normalized).
- **S2 ZZ / coherent coupling**: coupling-map degree of the probe's physical qubit restricted to in-register neighbors (normalized), i.e., adjacency exposure during idle windows.
- **S3 measurement-induced cross-copy backaction**: indicator of matched-pair identity across the two copies (probe qubit's partner is its matched copy qubit), invariant under physical adjacency by construction.

## Stage 2 — frozen discrimination rule

Per flight f: the 48-vector **m_f** of signed weight-1 readings (from stage-0 counts, decoded by the grade pipeline's own probe estimator — one code path, validated first on a synthesized known-answer input). Statistic: Spearman ρ(|m_f|, S_k) per signature k per flight, combined across the five flights by Fisher's method; sign-structure consistency checked separately against each candidate's sign prediction (S1: sign set by readout asymmetry direction — no sign constraint frozen; S2: sign follows ZZ always-positive phase accumulation → uniform sign within a flight; S3: sign pairs across copies).

- **ATTRIBUTED to candidate k**: combined p_k < 0.01 AND both other candidates' combined p > 0.05 AND the weight-heavy-at-shot-noise constraint is consistent with k (frozen consistency statements: S1 — weight-heavy probes share readout lines, so *inconsistent* unless magnitude scales sub-linearly with weight as multiplexed-readout models allow; S2 — heavy probes average over 12+ qubits, dilution ∝ 1/weight, consistent; S3 — pairing washes out at weight ≥ 2, consistent).
- **NON-SEPARATION**: any other pattern of p-values → published as such, anomaly stays open with the measured correlation table.
- **UNDERPOWERED**: if the per-flight probe se (from stage-0 shot counts) makes |ρ| = 0.4 undetectable at α = 0.01 across five flights combined, declared before stage 2 runs (power computed from stage-1 metadata + shot counts only).

## Stratum label

All five flights are ibm_marrakesh, one era (Aug 2026) — any verdict is a **marrakesh-2026 statement**; cross-device generality is not claimed by design.

## Order of operations (the freeze is the law)

Stage 0 banking → stage 1 vectors + power check → **this doc's hash cited in the analysis commit** → stage 2 decode + verdict, appended to the F122 audit trail and this doc in place. No per-probe value is looked at before stage 2. Optional deferred leg (cheap, not part of this freeze): a probe-order-permuted re-fly if attribution lands on S1 (readout) and a downstream claim ever needs it killed dead.

---

**STAGE 0 EXECUTED (C5068): custody VERIFIED, zero repair needed.** All five flights bank shot-level raw science with counts matching their manifests exactly: `doorb_raw_science` 106,911 ↔ d9rvmuvtfhrs73ds6c1g · `refly` 103,732 ↔ d9sifr8pdb6s73e63140 · `i1` 72,759 ↔ d9sma69dsedc73ahur2g · `i2` 100,704 ↔ d9smh0hdsedc73ahv2tg · `i3` 91,512 ↔ d9toamk98n5s7391t4v0. The freeze's "first-FAIL and original-WIN are candidates for repair" expectation was pessimistic — Elder's banking covered the whole family. No IBM re-pull; stage 1 (structure vectors + power check) is next. No probe value was decoded in this verification (shot-list lengths and manifest fields only).

---

**STAGE 1 EXECUTED (C5069)** — artifacts: `results/h14_a2_stage1_layouts.json` + `results/h14_a2_stage1_vectors.json`. Findings, all structure-level (no probe value decoded):
1. **All five flights used the IDENTICAL physical layout** (A=[3,4,16,1,6,22,24,8,17,36,37,10,28,42,12,54], B=[2,5,23,0,7,21,25,9,27,41,45,11,29,43,13,55]) — VF2 chose the same 32 qubits across 3 days and two accounts with nothing pinned. Custody rescue recorded: door-b banked no layouts (no initial_layout, no seed, transpile result discarded) — recovered from IBM job inputs while retention held. Bonus census datapoint: layout choice was CONSTANT for this circuit class. Every Bell pair is physically adjacent (16/16).
2. **S2** (extra in-register adjacency beyond the partner link): [3,2,3,1,3,2,2,2,2,2,1,2,1,1,1,0] per register qubit, variance 0.688 — real discriminating structure. Repeats ×3 over Paulis to the 48-probe vector; **effective independent structure points = 16, not 48** (the power check uses 16).
3. **S3 is DEGENERATE as a magnitude vector** (the halves pairing is uniform by construction) — S3's prediction is FLAT magnitudes with copy-paired signs. The discrimination is therefore **S2-topology vs S3-flat, plus sign structure** — not three parallel correlations.
4. **S1 is UNDETERMINABLE and NOT proxied**: no readout-multiplex ground truth exists on any read path (repo grep empty; fake-provider meas_map is one 156-qubit group; pulse access retired). An arbitrary-parameter proxy inside a frozen protocol is worse than a declared gap. **Verdict vocabulary adjusted BEFORE decode**: a topology-class attribution leaves S1-topological unexcluded; a flat-class attribution leaves S1-uniform unexcluded; the stage-2 verdict will say so in its own words.
5. **Power (declared before decode)**: per-probe se ≈ 1/√N_rows ≈ 0.003 per flight (signal class ~0.04 → per-probe z ~ 13, consistent with the grade's 13.6σ max — measurement noise is not limiting). The limiting error is correlation sampling at n=16 qubit-level points: sd(ρ) ≈ 0.258/flight; |ρ| = 0.4 gives z ≈ 1.55/flight, Fisher-combined over 5 flights ≈ 3.5σ → **POWERED at α = 0.01 for the frozen |ρ| = 0.4 benchmark, with no headroom to spare** — a true-|ρ| of 0.25 would land UNDERPOWERED and will be reported as such if the data says so.

---

**STAGE 2 EXECUTED (C5069, analysis cites stage-1 commit 4475902)** — `results/h14_a2_stage2_verdict.json`. Chain: decoder selftest 6/6 → all five decisions files' raw-record hashes MATCH the banked shots (digest recipe: sha256 of newline-joined shot strings) → 48 weight-1 estimates per flight through the frozen estimator's own output. **Verdict: S2 EXCLUDED — the cross-copy correlation carries no coupling-map signature** (Fisher p = 0.747 over five flights; per-flight ρ ∈ [−0.25, +0.31] scattering on zero) **and the ZZ uniform-sign prediction fails independently** (mixed signs, 0.50–0.68 positive). The surviving shape is **FLAT-CLASS**: the four healthy flights carry real per-qubit magnitude structure at 7–9× the shot-noise floor that is adjacency-blind — consistent with S3 (measurement-induced cross-copy backaction), with S1-uniform unexcluded exactly as stage 1 declared. first_FAIL is its own stratum (|m| 14× larger — the documented planted-P defect, not the residual; its inclusion changes nothing). Scope: exclusion is powered at the frozen |ρ| = 0.4 benchmark; weaker topology couplings are not excludable at n = 16. **The anomaly is NARROWED, not pinned — and F122's claim card footnote now has its measured basis.**

---

## S4 ADDENDUM — FROZEN before decode (C5070, locks hunt; a NEW freeze, expressly not part of the original S1–S3 rule)

**The fourth signature**: each flight co-flew 2,000 calibration rows on a public Pauli (`cal_P_public`, banked shot-level in `doorb_*raw_cal_n16_elder.json`). Per pair j, the calibration transfer factor c_j = mean over cal shots of the frozen decoder's per-letter sign value at pair j; **S4_j = 1 − c_j/median(c)** (relative per-pair cal deficit; median-normalized so S4 measures per-pair structure, not the global cal level). Computed per flight, from that flight's OWN cal rows — perfectly condition-matched to its science data.

**Frozen rule (mirrors stage 2)**: Spearman ρ(|m| qubit-vector, S4) per flight (n = 16), Fisher-combined over the five flights, α = 0.01. **Predictions registered**: if the cross-copy correlation is measurement-quality-linked (readout/discrimination class), |m| correlates POSITIVELY with S4 (worse-calibrated pairs carry more ghost); if the ghost is deeper (coherent backaction independent of readout quality), no correlation. Power as stage 2: POWERED at |ρ| = 0.4, no headroom; UNDERPOWERED reported if the data lands small. One code path: the same frozen decoder primitives (sign table + outcome_to_bells) decode the cal rows.
