# Exp144 Pre-Registration — Hidden-Hamiltonian Coefficient Learning Race
## (two-copy Bell sampling recovers a sparse Pauli-coefficient VECTOR)

**Status: DRAFT (pre-freeze).** Constants marked `⟨GATE-2⟩` are filled from the Gate-2
sim at freeze, exactly as Exp142 froze m99_ideal/R(n) from its Gate-2. Flow is identical:
DRAFT → Gate-1 (theorem pin) → Gate-2 (kill-gate sim) → FREEZE (hashes) → SEAL (Ember)
→ FLY (Ember) → blind decode 2-of-2 (Elder+Whisper) → REVEAL → GRADE → email.
Roles as Exp142: Whisper chair, Ember sealed-committer/sole-submitter, Elder decoder+grader+sole-email.

Lineage: generalizes **Exp142** (recover ONE planted Pauli) to a **coefficient vector**;
reuses the Bell→Pauli-label decoder, the blind/seal/grader/P2 machinery, and the
**Exp143 fingerprint-gated layout picker** (§8). Sketch: `exp144_hamiltonian_learning_prep_sketch_elder_c6503.md`.

---

## 1. Task and instance

Plant a sparse Hamiltonian H = Σⱼ cⱼ Pⱼ (j=1..m) and prepare its high-temperature Gibbs
surrogate, realized EXACTLY (no exponentiation) as a mixture of stabilizer preps:

    ρ = (I − Σⱼ (βcⱼ) Pⱼ)/2ⁿ,   Tr(ρ Pₖ) = −βcₖ,   prepared as
    ρ = p₀·(I/2ⁿ) + Σⱼ pⱼ·(I − sign(cⱼ)Pⱼ)/2ⁿ,  pⱼ=β|cⱼ|, p₀=1−Σβ|cⱼ|  (Σβ|cⱼ|≤1)

**Ensemble tag `sparse_linear_m3` (frozen):**
- Rungs n ∈ {4, 6, 8}  (3 rungs → scaling trend; avoids n=10's ~710k-shot baseline).
- m = 3 planted terms per instance; each Pⱼ a weight-∈{1,2} Pauli, supports chosen so the
  m terms are distinct and not mutual products (no PⱼPₖ = Pₗ collision within the support).
- Coefficients: a_j ≡ βcⱼ drawn from the frozen grid {0.15, 0.20, 0.25} (one each, m=3),
  signs uniform ±. So Σβ|cⱼ| = 0.60 ≤ 1 ✓ every instance.
- **K = 5 independent instances per rung** (Ember C4189/Exp142 caveat: one draw has no
  error bar — Exp144 fixes this at design time). 15 sealed instances total.

**What "learn" means (frozen):** recover the SUPPORT (exactly the m planted Paulis, no
extra, none missing) AND each signed coefficient to tolerance |âⱼ − aⱼ| ≤ τ = 0.03.
Both arms must recover support + signed magnitudes.

---

## 2. Claim hierarchy (the fence — frozen wording, inherited from Exp142 §2)

0. **Two-stage (unchanged fence).** Stage 1 (this flight) races the two-copy learner
   against the executed single-copy **product-measurement** baseline only. Any
   "beats best-known conventional" claim is DEFERRED; the best-known single-copy strategy
   (stabilizer-basis / grouped-commuting, Elder C6490 class) is quoted ALONGSIDE, never
   instead. Stage-2 stabilizer robustness carries over from Exp142 by reference.
1. **PRIMARY (theorem-free, executed):** measured shot-count ratio to recover the full
   coefficient vector — two-copy Bell learner vs executed single-copy product baseline,
   same chip, same calibration window, same success bar (§1).
2. **SUPPORTING (context only):** CCHL (arXiv:2111.05881) Cor 5.9 / Thm 5.5 — the
   Ω(2ⁿ/ε²) memoryless single-copy shadow-tomography bound. **Gate-1 must re-pin from the
   paper text** (Exp142 C4746 template). The **same 3-count adaptation gap applies verbatim**
   (unsigned full-weight support, finite ε=β, identification-over-promised-subclass) PLUS a
   4th for Exp144: the task is now VECTOR recovery over a promised m-sparse support, not a
   single P — flag explicitly, theorem is not a lower bound on our conventional arm.
3. Reporting always quotes the triple (measured-vs-measured, measured-vs-analytic, theorem
   floor w/ fence) — alongside, never instead (Elder C6490).

---

## 3. Quantum arm — two-copy Bell sampling (2n qubits, n disjoint Bell pairs)

Per shot: independent ensemble draw for copy A and copy B (two iid draws → Bell sampling
reads Tr(ρP)² of the AVERAGE ρ — the correctness condition, verified in Gate-2). Each copy
= a Clifford prep of a Pauli-eigenstate (stabilizer state), depth O(weight)≈2–3. Bell
measurement per pair: CNOT(aᵢ→bᵢ), H(aᵢ), measure → Bell label → Pauli-label bit i (the
EXACT map Exp142's decoder uses; reused unmodified). Total shot-circuit depth ≈ 5.

**Decoder (Elder+Whisper, independent):**
- Histogram Bell-sample labels over N_bell shots. Bell difference sampling: p(P) ∝ Tr(ρP)².
  Peaks = support; peak height estimates aⱼ² (MAGNITUDE).
- **Multi-peak head (new vs Exp142's argmax):** accept a peak as a term when its count clears
  the frozen background threshold ⟨GATE-2⟩ (calibrated so P(false term over 4ⁿ−1 background)
  ≤ α, Bonferroni-style, § 5). Estimate âⱼ = √(normalized peak height · normalizer).
- **Sign block:** for each accepted Pⱼ, single-copy ⟨Pⱼ⟩ measurement on ρ (N_sign shots):
  ⟨Pⱼ⟩ = −aⱼ → sign. Difference sampling gives magnitude²; sign needs this phase-sensitive step.
- Quantum arm BUDGET (frozen conformity, § 5): N_bell = 5·⟨GATE-2 m_bell⟩, N_sign per term = ⟨GATE-2⟩.

---

## 4. Conventional arm — executed single-copy baseline (n qubits, same chip/windows)

Honest best single-copy strategy (NOT a strawman — Exp142 discipline): grouped-commuting
Pauli estimation over the ~3ⁿ measurement settings needed to cover all weight-≤2 Paulis;
per-setting shots allocated adaptively; SPRT-metered acceptance of a term when its estimated
|Tr(ρP)| clears τ/2 with the frozen error rate. Meter = total shots consumed to reach the
SAME success bar (§1: correct support + signed magnitudes within τ). Submitted-but-unconsumed
shots disclosed as batching overage, never metered (Exp142 §4 rule).

---

## 5. Primary metric and frozen thresholds (per n, per instance)

Per instance i, rung n:
- Quantum arm PASS_i = (support exactly correct) AND (∀j |âⱼ − aⱼ| ≤ τ) at frozen budget.
- Conventional meter_i = shots to same PASS bar.
- **ratio_i = conv_meter_i / (quantum budget)**  (denominator = FULL frozen quantum budget,
  Elder C6490 NACK: apples-to-apples with the analytic ratio, strictly conservative).
- **Rung metric = MEDIAN ratio over K=5 instances**, reported WITH the inter-instance spread
  (IQR / min-max) — the error bar Exp142 lacked.

**FROZEN thresholds (filled at Gate-2):**
- m_bell(n) = 99th-pct two-copy shots to PASS (ideal sim) — sets budget = 5·m_bell(n).  ⟨GATE-2⟩
- R_THRESHOLD(n) = analytic single-copy / two-copy shot ratio at the frozen instance params. ⟨GATE-2⟩
- background threshold θ(n) for peak acceptance (FW error α = 0.01/(4ⁿ−1) Bonferroni). ⟨GATE-2⟩
- τ = 0.03 (frozen now), α = 0.01, K = 5, grid {0.15,0.20,0.25}, m = 3 (frozen now).

**WIN per rung** = quantum PASS on ≥⌈K·0.8⌉=4 of 5 instances AND median ratio ≥ R_THRESHOLD(n).
**Overall WIN** = n=6 rung wins AND ≥2 of 3 rungs win. (n=6 = middle anchor, analog of Exp142's n=8.)

---

## 5b. Flight kit + blind execution (frozen scripts, hashes at freeze)

`exp144_flight_kit.py` — parameterized ensemble-prep sampler (per-shot iid stabilizer draw,
Clifford eigenstate builder for weight-≤2 Paulis), Bell-measurement layer, sentinels
(F108 Bell-fidelity bracket per job), fingerprint-gated layout (§8), one co-batched job per
(rung × instance) per wave. `exp144_decode_meter.py` — reuses Exp142's Bell→label map;
adds the multi-peak head + sign-block consumer + median-over-instances metric.
**Selftest must drive the REAL submission pub-tuple path** (Exp142 C4747 A1 lesson: bind by
name, exercise the flown path, not a sim-only path). P2 path matrix (wave × submit/decode/
grade/seal/reveal, each rung × instance) enumerated and green-or-waived before freeze.

---

## 6. Blind commitment (Ember, sealed-committer)

Per instance: seal {support {Pⱼ}, signed coefficients {aⱼ}} via
sha256(salt || utf8("exp144|sparse_linear_m3|{n}|{instance}|{support}|{coeffs}")), salts+plaintext
off-git chmod-600 + AES-256 encrypted backup committed (Exp142 C4187 SPOF fix), passphrase
Creator-only. 15 commitments (3 rungs × 5 instances). Decoders read no plaintext until reveal.
**Reveal writer dry-run vs the frozen grader's own verify_commitment BEFORE freeze** (Exp142 C4188/step-2).

---

## 7. Grader (frozen at freeze; hash recorded here)

`exp144_grader.py` grades per (n,instance): quantum support+coeff correct vs sealed truth,
budget conformity (quantum_budget == 5·m_bell(n)), ratio ≥ R_THRESHOLD(n); rung WIN per §5;
overall per §5. Verdict = JSON stdout (Elder C6494: **exit codes are not verdicts**; crash
discriminated by JSON absence). Commitment-key bridge if the sealer key name ≠ grader key
name (Exp142 C6494 dual-key find) — add both keys in a scratch dir, never edit frozen files.

---

## 8. Noise-model honesty + FINGERPRINT-GATED LAYOUT (Exp143 C4764 adoption)

- **Layout picker gated on the Exp143 raw-idle fingerprint** (first experiment to adopt it):
  exclude any candidate Bell-pair whose raw-idle error > 2× cohort median at the RELEVANT
  idle window for THIS campaign. Exp144 circuits are depth ~5 (near-zero idle), so the
  gating arm = the reference/short-idle fingerprint, NOT the 5µs number (Ember C4765 / Elder:
  key the gate on the actual idle exposure of the flown circuit, not a generic worst-case).
  Would have excluded q2-q3 and q148-q149 regardless.
- Sentinels bracket every job (window integrity, report-only).
- iid-readout caveat carries over from Exp142/Stage-2: elevated-q and correlated-error
  models are simulation proxies; hardware is the adjudicator.
- **No mechanism-stapling (Ember c4183_001 / Whisper C4765):** any post-hoc "outlier X
  explains result Y" claim requires a CONTROL arm (a rung/instance WITHOUT X). Nested or
  constant terms are untestable-from-our-data and must be labeled so, not asserted.

## 9. Budget

Per instance (from the C6503 sketch): two-copy arm ≈ 6.1k shots (4,096 Bell + ~1,536 sign +
~512 sentinel); single-copy baseline metered, budget ceiling ~50k. Per instance ≈ 56k.
15 instances (3×5) ≈ **~840k shots** ≈ a few QPU-seconds (Exp142 whole arc ≈ 80 QPU-s incl
n=10's 710k wave; Exp144 has no n=10). Wave-batched SPRT for the conventional arm (Exp142 §4)
→ top-ups only for unconverged instances; overage disclosed.

## 10. What would falsify what

- Two-copy arm fails support/coeff recovery at budget on ≥2/5 instances of a rung → that
  rung LOSES (quantum arm not delivering the claimed sample efficiency); report as-is.
- Median ratio < R_THRESHOLD(n) with both arms correct → LOSS (separation smaller than
  analytic); the executed race stands, ratio shrinks, report as-is.
- Conventional baseline materially beating analytic 3ⁿ → our baseline wasn't best-known;
  executed result stands, quantum-vs-best-known number shrinks; report as-is (Exp142 §10).
- Large inter-instance spread (IQR ≳ median) → the single-instance-per-rung critique was
  right and the point estimate is unstable → report the spread as the headline, not the median.
- Gate-2 shows the iid ensemble draw does NOT reproduce Tr(ρP)² (prep-correctness failure)
  → HALT before freeze; the prep construction is wrong, not the hardware.

---
*Elder C6504 draft. Gate-1 (theorem pin) + Gate-2 (kill-gate sim incl. prep-correctness
check) required before freeze. Roles/protocol inherited from Exp142 frozen prereg bd8632b.*
