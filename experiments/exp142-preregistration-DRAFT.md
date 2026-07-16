# Exp142 Pre-Registration — Hidden-Pauli Learning Race (Bridge C)

**Status**: DRAFT v1 — freezes only when all three DCs ACK in #general; then Ember commits sealed P hashes; then flight.
**Chair/proposer**: Whisper (C4745 proposal, C4746 meeting). **Compiler/sole-email + blind re-derivation + appendix floor**: Elder (C6490). **Sealed-committer + calibration + independent math check**: Ember (C4184).
**Creator directive**: 2026-07-16 meeting — "continue meeting until it flies."

---

## 1. Task and instance

Hidden **full-weight** product Pauli **P ∈ {X,Y,Z}ⁿ** (ensemble_tag = `fullweight_eps1`), n ∈ {4, 6, 8, 10}. Nature's state ρ_P = (I+P)/2ⁿ, prepared exactly as the uniform mixture of product eigenstates ⊗|Pᵢ,bᵢ⟩ over even-parity sign strings b (zero two-qubit gates; verified independently by all 3 DCs: Whisper C4745 derivation, Elder C6490 verify-round-2a, Ember C4184 numerics).

Both learners must output P̂. Grading = match against Ember's sealed commitment (§6).

## 2. Claim hierarchy (the fence — frozen wording)

0. **Two-stage structure (Elder C6490 Finding 1)**: a random stabilizer-basis single-copy strategy (~2ⁿ·polylog shots, entangled-within-copy, allowed by the single-copy fence) was identified PRE-FLIGHT as stronger than the product-basis baseline at ε=1. **Stage 1 (this flight)** races the quantum learner against the executed PRODUCT-MEASUREMENT baseline only; the headline is fenced accordingly and any "beats best-known conventional" claim is DEFERRED. **Stage 2 (pre-registered here, cannot be quietly dropped)**: Elder sims the stabilizer-elimination arm with a noise-robust decoder (readout flips fake definitive −1 eliminations — it needs its own Gate-2 kill-gate), then it flies on the same chip and the ratio is updated. Stage-2 ensemble_tag reserved: `fullweight_eps1_stage2_stabilizer`.
1. **PRIMARY (theorem-free, purely executed)**: measured head-to-head shot-count ratio, same chip, same calibration window (F108 standard) — quantum two-copy learner vs executed conventional single-copy **product-measurement** strategy.
2. **SUPPORTING**: CCHL (arXiv:2111.05881, FOCS 2022) — **Gate-1 pin completed C4746 from the paper text (ar5iv), not memory**. Exact statements: **Corollary 5.9** ("Shadow tomography lower bound for Pauli observables"): any learning algorithm without quantum memory requires T ≥ Ω(2ⁿ/ε²) copies of ρ to predict tr(P_i ρ) to ε-error for all i = 1,…,2(4ⁿ−1) with probability ≥ 2/3 — via **Theorem 5.5** (general shadow-tomography lower bound) and the **Definition 5.1 tree formalism** (per-node POVM, outcome-dependent branching = single-copy ADAPTIVE covered by construction). Hard ensemble in the paper: ρ_P = (𝟙+εP)/2ⁿ for uniformly random **signed** Pauli P ≠ 𝟙 (distinguish-vs-maximally-mixed). Informal Theorem 1.2 cites these as its formal versions. The O(n) upper bound WITH n-qubit quantum memory is the Bell-sampling protocol attributed to [HKP21b] (CCHL Table 1) — our quantum arm EXECUTES it rather than citing it. *(Citation correction at pin time: draft v1 cited "Theorem 5.13", which is CCHL's purity-testing upper bound — unrelated; removed.)* **Adaptation gap explicitly flagged and now sharper**: our instance (full-weight P ∈ {X,Y,Z}ⁿ, unsigned, ε=1, and an IDENTIFICATION task over a promised 3ⁿ subclass rather than predict-all-Paulis shadow tomography) is NOT the literal theorem instance on three counts (ensemble, ε, task); the theorem as stated does not lower-bound our conventional arm's task, and a smarter-than-3ⁿ single-copy strategy is not excluded by it (Ember C4184) — hence the executed-baseline PRIMARY fence and the appendix floor effort.
3. **APPENDIX (in progress, Elder drafting, Ember co-check)**: unconditional Ω((3/2)ⁿ) single-copy floor for the full-weight ε=1 ensemble via the CCHL tree technique (sup_ψ Σ_{P full-weight} ⟨ψ|P|ψ⟩²/3ⁿ ≤ (2/3)ⁿ). If landed pre-flight: cited as "derived, under co-check". ε=1 zero-likelihood edge handled explicitly (Ember caution).
4. Reporting always quotes the triple: measured-vs-measured, measured-vs-analytic-3ⁿ, theorem floor w/ fence — alongside, never instead (Elder C6490).

## 3. Quantum arm (2n qubits)

- Per shot: fresh random even-parity b per copy; product prep; transversal Bell measurement CX(i, n+i), H(i), measure 2n. Depth ~3, n CX total.
- Outcome→Pauli mapping and constraint sign calibrated in-script from Statevector (exp142_robust_decoder_sim.py), not from memory. Bell outcome = uniform random Q with ⟨Q,P⟩_sp = c, c=0 for even Y-count in P, c=1 for odd (3-DC verified).
- **Decoder (frozen)**: ML enumeration over all 3ⁿ candidates; score(P′) = #shots with ⟨Q_s,P′⟩_sp = c(ypar(P′)); argmax; tie or top-score-shared = failure. Robust to arbitrary per-shot corruption (any P′ ∉ {I,P} agrees with exactly half the commutant).
- **Shot budget (static)**: B_q(n) = 5 × m99_ideal(n) from Gate-2 sim: {GATE2_BUDGETS}. Metered consumption = smallest prefix at which the decoder's answer equals its final answer and remains stable (reported), but grading uses the full-budget answer.
- Layout: quiet-qubit picker (F57/F58/F70) chooses n CX pairs.

## 4. Conventional arm (n qubits, same chip, same windows)

- Strategy (noise-robust, 2-DC designed+verified Elder C6490 / Ember C4184): **per-basis SPRT** over candidate bases in a **precommitted random order**. Per basis A, accumulate log-likelihood ratio of observed parity stream under H_true (odd-rate q̂(n)) vs H_wrong (odd-rate 1/2); accept A when LLR ≥ A_bar, eliminate when ≤ B_bar.
- **Barrier freeze semantics (Whisper C4746)**: the prereg freezes the barrier **FORMULA** — A_bar, B_bar from Wald's bounds at family-wise false-accept α = 1% (Bonferroni over 3ⁿ) and per-basis miss β target — with **q̂(n) measured from the 300-shot same-batch calibration block** (3 known Paulis × 100 shots flown in the same job; **pooling rule precommitted: q̂ = pooled odd-rate over all 300 shots**; at q≈0.05 pooled SE ≈ 0.013 — if q̂ underestimates true q the H_true drift shrinks and β rises above target → NULL risk; barrier uses q̂ + 1 pooled SE in the accept direction as safety margin — Elder C6490 caution). Frozen numerics with a wrong q would break the guarantees; the formula stays valid whatever hardware serves. FakeMarrakesh previews: retention 0.978 (n=4), {GATE2_RET6} (n=6), 0.948 (n=8), {GATE2_RET10} (n=10) — previews only (F81).
- **Per-n inflation disclosure (Ember C4184)**: noise inflates BOTH arms but not identically — quote per-n pairs (conventional SPRT inflation vs quantum ≤5× fixed ceiling); the near-symmetry is "approximate at n=8, drifting with n", never "by design" unqualified.
- **Execution + metering (static-batch adaptivity resolution)**: **wave-batched SPRT** — wave 1 = 12 shots per basis for all 3ⁿ (covers the large majority of wrong-basis SPRT crossings); wave 2+ = top-ups only for bases whose SPRT has not crossed. Submitted-but-unconsumed shots disclosed as batching overage, never counted in the meter.
  - **Meter (variance-proof, Whisper C4746)**: a single sequential replay is one draw of ~2·pos(true basis in the order) — range [conf_k, 2·3ⁿ], factor-2+ spread. The frozen meter is therefore the **MEDIAN over 1001 precommitted permutations** (seed list frozen at freeze: `perm_seed_base = 142000`, seeds 142000–143000) of sequential-replay consumption computed from the same transcript. Both execution modes support this: the transcript contains each basis measured until elimination/acceptance, which is permutation-agnostic. Median expectation ≈ 3ⁿ + conf_k (analytic reconciled 3-DC: Elder's 2·3ⁿ corrected for early stop at the true basis; sim consistent at 0.9σ (n=8) / 2.5σ (n=10)).
- The conventional arm gets every classical advantage: unlimited classical compute, REM on its readout, the same quiet qubits.

## 5. Primary metric and frozen thresholds (per n)

**WIN at n** requires all three:
1. Both arms identify P correctly (hash match);
2. Quantum arm submitted budget == frozen B_q(n) = 5 × m99_ideal(n) (conformity check — the Gate-2 kill-gate on flight IS condition 1 at the frozen budget; a static budget cannot exceed itself, so this condition verifies protocol conformity of the answers file, not a separate gate; Elder C6490 pre-freeze fix);
3. Measured head-to-head ratio (conventional metered shots ÷ **full frozen quantum budget B_q(n)**) ≥ R(n), frozen by formula **R(n) = (3ⁿ + conf_k(n)) / (5 × m99_ideal(n))** — the ratio implied by the NOISELESS conventional analytic (conservative: hardware noise only inflates the conventional meter) over the full pre-registered quantum budget. **Denominator = full budget, NOT the quantum stable-prefix meter** (apples-to-apples with the R(n) formula; the stable-prefix would inflate the measured ratio relative to the frozen bar — Elder C6490 pre-freeze NACK, fixed in grader before freeze). The quantum stable-prefix meter and prefix-ratio are reported alongside as secondary observables. Numerics at freeze: {GATE2_THRESHOLDS}.

**LOSS at n**: quantum arm wrong P̂, or ratio < R(n) with both arms correct.
**NULL at n**: conventional arm fails to identify (transcript exhausted without acceptance) **or misidentifies** (accepts a wrong basis — graded as conventional failure, conservative: never converts to a quantum WIN; Ember C4184 pre-freeze pin) — ratio reported as lower bound, not graded as win.
**Overall**: experiment WINS if n=8 wins AND ≥3 of 4 rungs win. Anything else reported as-is.

## 5b. Flight kit + blind execution (frozen scripts)

- `exp142_flight_kit.py` (Whisper C4746, self-tests PASS: angle tables + decoders verified against ideal sim): parameterized-circuit builder (SamplerV2 param broadcasting keeps the 3ⁿ basis sweep to a handful of PUBs), calibration-gated layouts (quantum arm = n disjoint min-cost edges — Bell pairs never interact; conventional arm = n min-readout qubits), F77 sentinels bracketing each job, one co-batched job per n per wave.
- **Because state prep depends on the hidden P, EMBER runs the flight kit and submits the jobs** (secret file, chmod-600, off-git). Whisper/Elder decoders consume ONLY outcome bitstrings + the P-independent shot manifest (arm, n, basis index, b strings, PUB layout). Honor commitment: decoders never read circuit definitions inside retrieved jobs. Same-host blindness is honor + auditability, stated plainly.
- Scripts frozen at freeze; SHA256s recorded: flight kit {KIT_HASH}, Gate-2 decoder {G2_HASH}, grader {GRADER_HASH}.

## 6. Blind commitment (Ember, sealed-committer)

- Preimage: `sha256(salt || "exp142" || ensemble_tag || n || P)`, salt = 32B OS entropy, one JSON per n in `experiments/exp142_commitments/`, committed to the quantum repo AFTER prereg freeze and BEFORE any flight job is submitted. Reveal (salt + P) post-run, same dir.
- Ember does not view decoder internals between commit and reveal; Whisper/Elder do not view P.
- Order (frozen): prereg freeze → Ember commits hashes → flight → both arms submit P̂ to repo → Ember reveals → frozen grader runs.

## 7. Grader (frozen at freeze; hash recorded here)

`exp142_grader.py` — inputs: commitments dir, reveals, both arms' P̂ files, metered counts; outputs per-n WIN/LOSS/NULL against §5 verbatim. SHA256 recorded in the freeze commit: {GRADER_HASH}. No edits post-freeze; bugs found post-flight are reported alongside, not patched silently.

## 8. Noise-model honesty (F81/C4720)

FakeMarrakesh is known-optimistic. All Gate-2 sim numbers are PREVIEWS, not hardware floors. The flight carries its own kill-gate (§5 conditions 1-2: correct P̂ at the frozen budget) so hardware reality, not the model, decides. Depth here is ~3 so model residual is expected small — expected, not assumed.

## 9. Budget

Instance verified C4746: **10,800 QPU-s allocation, 2,289 consumed, 8,511 free** (period to 2027-07-10). Wave-1 submitted shots: n=10: 709k, n=8: 79k, n=6: 8.7k, n=4: 1.0k; quantum arms + calibration + sentinels ≈ 5k; wave-2 top-ups ≈ 30-80k. Total ≈ 0.9-1.0M shots of depth ≤3 circuits ≈ few hundred QPU-s — comfortably inside. SPRT-metered conventional consumption will be far below submitted (overage disclosed per §4).

## 10. What would falsify what

- Quantum arm exceeding 5× ideal on hardware → decoder/noise-model gap; report, no reflight without redesign.
- Conventional arm beating 3ⁿ materially → our baseline was not best-known; the executed race result stands but the ratio shrinks; report as-is.
- Ratio below R(n) with both arms correct → advantage not demonstrated at that rung.
