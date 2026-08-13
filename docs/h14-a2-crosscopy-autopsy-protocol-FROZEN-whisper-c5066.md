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
