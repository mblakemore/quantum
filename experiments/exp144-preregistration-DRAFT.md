# Exp144 Pre-Registration v2 — Hidden-Hamiltonian Coefficient Learning Race
## (two-copy Bell sampling of e^{−iHt} recovers a sparse Pauli-coefficient VECTOR)

**Status: DRAFT v2 (pre-freeze). DYNAMICS design.** The v1 Gibbs-surrogate design was
voided by chair review (Whisper C4767: blockers R1 no-peaks / R2 poly-baseline) — both
independently CONFIRMED by exact computation (Elder C6506, `exp144_blocker_verification_elder_c6506.md`,
scripts committed). v2 is redesign direction (i), itself VERIFIED before adoption
(exact sim: Bell distribution is exactly 2^m-sparse with the subset sin²/cos² law).
Constants marked `⟨GATE-2⟩` are filled from the Gate-2 sim at freeze. Flow unchanged:
DRAFT → Gate-1 (theorem pin) → **Gate-2 (POWER CALC + kill-gate, respecified §G2)** →
FREEZE (hashes) → SEAL (Ember) → FLY (Ember) → blind decode 2-of-2 (Elder+Whisper) →
REVEAL → GRADE → email.
Roles as Exp142: Whisper chair, Ember sealed-committer/sole-submitter, Elder decoder+grader+sole-email.

**v1→v2 changelog:** §1 task now DYNAMICS (planted H applied as e^{−iHt} to Bell-pair
halves; full-weight COMMUTING terms), §3 decoder rewritten to the verified 2^m-sparse
peak law (v1's "peaks" on the Gibbs surrogate do not exist — R1), §4 baseline rewritten
with covering-design arithmetic in the full-weight regime (v1's weight-≤2 promise made
the baseline poly — R2), Gate-2 respecified as a POWER calculation (a correctness check
would have passed the broken v1). K=5, roles, §5b/§6/§7/§8 process sections carry from v1.

---

## 1. Task and instance

Plant a sparse commuting Hamiltonian H = Σⱼ cⱼ Pⱼ (j=1..m) and apply the EXACT evolution

    V = e^{−iHt} = Πⱼ e^{−i cⱼ t Pⱼ}      (terms commute → no Trotter error)

to the system half of n ideal Bell pairs. Each e^{−icⱼtPⱼ} is the standard Pauli-rotation
gadget (single-qubit basis change + CNOT ladder + Rz(2cⱼt) + unladder), depth ~2·weight+1
per term. Circuits are non-Clifford (arbitrary-angle Rz) — Gate-2 sims are statevector /
analytic-law, not stabilizer.

**Ensemble tag `dynamics_fullweight_m3` (frozen):**
- Rungs n ∈ {4, 6, 8} (3 rungs → scaling trend; no n=10).
- m = 3 planted terms per instance; each Pⱼ **FULL-WEIGHT** (no identity letters — this is
  what restores the exponential single-copy floor; R2 lesson), mutually COMMUTING, and
  **multiplicatively independent** (all 2³ subset products distinct; no subset product
  equals another planted term or identity). Sampled uniformly from full-weight strings
  subject to these constraints, at seal time.
- Coefficients: cⱼ from the frozen grid {0.15, 0.20, 0.25} (one each, m=3), signs uniform ±.
- Evolution time **t = 2.0 (FROZEN — Gate-2 t-sweep argmax, C6508)**: cⱼt ∈ {0.30, 0.40, 0.50}
  rad → sin²(cⱼt) ≈ {0.087, 0.152, 0.230}. **Singleton-dominance condition (frozen
  constraint, EXACT form — Gate-2 correction C6508):**
  min over singletons of p({j}) > max over |S|≥2 subsets of p(S), evaluated on the frozen
  grid×t via the subset law; equivalently tan²_min > max product of ≥2 tan² factors.
  At the frozen grid and t=2.0 the margin is **1.79×** (exact). *v2's original shorthand
  "sin²<0.5 ⟹ dominance" is NOT a valid implication — it only covers subsets CONTAINING
  the singleton; t=2.5 satisfies sin²<0.5 yet has margin 1.00× (Gate-2 B1). The exact
  inequality is what is frozen.* Decoder needs no structure search.
- **K = 5 independent instances per rung** (Ember C4189 caveat baked in at design time).
  15 sealed instances total.

**What "learn" means (frozen):** recover the SUPPORT (exactly the m planted Paulis, no
extra, none missing) AND each signed coefficient to |ĉⱼ − cⱼ| ≤ τ = 0.03. Both arms, same bar.

---

## 2. Claim hierarchy (the fence — frozen wording, inherited from Exp142 §2)

0. **Two-stage (unchanged fence).** Stage 1 races the two-copy learner against the executed
   single-copy **product-prep/product-measurement** baseline only. Any "beats best-known
   conventional" claim is DEFERRED; best-known single-copy strategies are quoted ALONGSIDE,
   never instead. Stage-2 robustness analysis carries by reference.
1. **PRIMARY (theorem-free, executed):** measured shot-count ratio to recover the full
   signed coefficient vector — two-copy Bell learner vs executed single-copy baseline,
   same chip, same calibration window, same success bar (§1).
2. **SUPPORTING (context only):** Gate-1 must pin, FROM PAPER TEXT, the correct
   memoryless-single-copy lower bound for the DYNAMICS setting (CCHL arXiv:2111.05881
   channel-learning theorems, and/or Huang et al. Science 2022 learning-from-experiments) —
   NOT the state-shadow bound v1 cited. Adaptation-gap count redone for the dynamics task
   (finite t, promised commuting m-sparse ensemble, identification-over-subclass, vector
   recovery). Theorem is context, never a lower bound on our executed conventional arm.
3. Reporting always quotes the triple (measured-vs-measured, measured-vs-analytic, theorem
   floor w/ fence) — alongside, never instead (Elder C6490).

---

## 3. Quantum arm — two-copy Bell sampling of the evolution (2n qubits, n Bell pairs)

Per shot: prepare n Bell pairs |Φ⁺⟩^⊗n (system half A, reference half B), apply V = e^{−iHt}
to A only, Bell-measure pairwise (CNOT(aᵢ→bᵢ), H(aᵢ), measure — the EXACT Exp142 label map,
reused unmodified). Label distribution (VERIFIED exactly, C6506 `exp144_dynamics_check_elder_c6506.py`):

    p(P_S) = Π_{j∈S} sin²(cⱼt) · Π_{j∉S} cos²(cⱼt)   for S ⊆ {1..m},  P_S = Πⱼ∈S Pⱼ
    p(anything else) = 0   (structurally — lifts only to ~hardware-noise scale)

Exactly 2^m = 8 nonzero labels: identity (S=∅, largest), the m planted terms, and their
products. **Contrast is O(1)** — this is what v1's mixed-state design lacked (R1).

**Decoder (Elder+Whisper, independent):**
- Histogram Bell labels over N_bell shots. **Support = the m largest non-identity peaks**
  (guaranteed by the frozen EXACT singleton-dominance inequality, §1 — margin 1.79× at the
  frozen grid×t), each also required to clear the frozen background threshold θ(n) ⟨GATE-2⟩
  (FW error α = 0.01/(4ⁿ−1), Bonferroni).
- **Magnitudes, self-normalized:** |ĉⱼ| = arctan(√(p̂ⱼ/p̂_∅))/t (ratio to the identity peak
  cancels common attenuation to first order; residual bias characterized at Gate-2).
- **Consistency checks (free, report-only):** multiplicativity p̂(P_{jk})·p̂_∅ ≈ p̂ⱼ·p̂ₖ for
  all pairs + the triple; total off-group mass (background monitor).
- **Sign block (single-copy, adaptive after support ID):** sin² is sign-blind. For each
  accepted Pⱼ, decoder solves (symplectic GF(2)) for a probe Qⱼ with {Qⱼ,Pⱼ}=0 and
  [Qⱼ,Pₖ]=0 (k≠j); prep a product eigenstate of the Pauli string iQⱼPⱼ, evolve V, measure
  Qⱼ in its letter basis: ⟨Qⱼ(t)⟩ = ∓sin(2cⱼt) — sign-sensitive, other terms pass through
  by construction. N_sign shots per term ⟨GATE-2⟩. Exact scheme + degeneracy handling in the
  Gate-2 sim.
- Quantum arm BUDGET (frozen conformity, §5): N_bell = 5·⟨GATE-2 m_bell⟩, N_sign ⟨GATE-2⟩.

---

## 4. Conventional arm — executed single-copy baseline (n qubits, same chip/windows)

Honest best single-copy product-prep/product-measure strategy, with the covering arithmetic
done CORRECTLY this time (R2 lesson):

- A product-basis setting (a length-n letter string) covers a FIXED full-weight Pauli with
  probability 3^−n; equivalently each setting measures exactly ONE full-weight string (plus
  its substrings). Covering all full-weight candidates needs ~3ⁿ settings (n=4: 81;
  n=6: 729; n=8: 6,561) — **the exponential wall is per-setting coverage, restored by the
  full-weight ensemble; it was destroyed by v1's weight-≤2 promise (median 50 settings —
  verified by MC, C6506).**
- Executed scheme: SPRT-metered candidate sweep over the promised (public) ensemble class —
  for candidate P, conjugation readout as in §3's sign block (prep product eigenstate of
  iQP, evolve, measure Q): planted → ⟨Q(t)⟩ = ∓sin(2ct) ≠ 0; non-planted → 0.
  **Conserved-candidate subtlety (flagged, Gate-2 resolves):** a non-planted candidate
  COMMUTING with all planted terms is conserved by V — the naive ⟨P⟩-conservation test
  cannot reject it; the conjugation readout CAN (it reads the coefficient, which is 0).
  Probe-choice interaction with unknown planted terms is randomized + majority-voted;
  scheme frozen at Gate-2.
- **Gate-2 adversarial self-red-team (R2 prevention, mandatory):** before freeze, actively
  attempt to construct a poly single-copy shortcut for THIS promised ensemble (commuting,
  full-weight, m=3, grid coefficients, public class). If one is found, IT becomes the
  baseline and all thresholds are recomputed from it. An accidental-strawman §4 must be
  caught by us, pre-freeze, not by a reviewer.
- Meter = total shots consumed to the SAME success bar (§1). Submitted-but-unconsumed
  shots disclosed as batching overage, never metered (Exp142 §4 rule).

---

## 5. Primary metric and frozen thresholds (per n, per instance)

Per instance i, rung n:
- Quantum arm PASS_i = (support exactly correct) AND (∀j: sign correct AND |ĉⱼ−cⱼ| ≤ τ)
  at frozen budget.
- Conventional meter_i = shots to same PASS bar.
- **ratio_i = conv_meter_i / (quantum budget)** (denominator = FULL frozen quantum budget,
  Elder C6490: strictly conservative, apples-to-apples with the analytic ratio).
- **Rung metric = MEDIAN ratio over K=5 instances**, reported WITH inter-instance spread
  (IQR / min-max) — the error bar Exp142 lacked.

**FROZEN thresholds (filled at Gate-2):**
- m_bell(n) = 99th-pct two-copy shots to PASS (noise-modeled sim, §G2) → budget = 5·m_bell(n). ⟨GATE-2⟩
- R_THRESHOLD(n) = analytic single-copy / two-copy shot ratio at frozen instance params. ⟨GATE-2⟩
- background threshold θ(n) (α = 0.01/(4ⁿ−1) Bonferroni). ⟨GATE-2⟩
- N_sign per term. ⟨GATE-2⟩
- τ = 0.03, α = 0.01, K = 5, grid {0.15,0.20,0.25}, m = 3, t = 2.0 (provisional): frozen now.

**WIN per rung** = quantum PASS on ≥4/5 instances AND median ratio ≥ R_THRESHOLD(n).
**Overall WIN** = n=6 rung wins AND ≥2 of 3 rungs win.

---

## 5b. Flight kit + blind execution (frozen scripts, hashes at freeze)

`exp144_flight_kit.py` — instance sampler (commuting full-weight multiplicatively-independent
triples), Pauli-rotation circuit builder (exact Π e^{−icⱼtPⱼ}), Bell-measurement layer,
sentinels (F108 Bell-fidelity bracket per job), fingerprint-gated layout (§8), one co-batched
job per (rung × instance) per wave. `exp144_decode_meter.py` — reuses Exp142's Bell→label map;
adds top-m peak head + multiplicativity checks + sign-block consumer + median-over-instances
metric. **Selftest must drive the REAL submission pub-tuple path** (Exp142 C4747 A1 lesson).
P2 path matrix (wave × submit/decode/grade/seal/reveal, each rung × instance) enumerated and
green-or-waived before freeze.

---

## 6. Blind commitment (Ember, sealed-committer) — SCHEMA PINNED PRE-FREEZE (Ember ask #1, C6509)

**Preimage (EXACT, frozen here — the vector serialization IS the commitment):**

    sha256( salt_bytes || utf8("exp144|dynamics_fullweight_m3|{n}|{k}|{terms_csv}|{coeffs_csv}") )

- `n` ∈ {4,6,8} decimal, `k` ∈ {1..5} decimal instance index (NEW vs Exp142 — 15 instances).
- `terms_csv`: the m=3 term labels, **canonical order = lexicographic ascending** of the
  label strings (uppercase IXYZ alphabet, length n, no internal separators), joined by ",".
  Ordering is normative: any other order is a different preimage.
- `coeffs_csv`: signed coefficients **in the SAME index order as terms_csv**, each
  formatted exactly `%+.2f` (grid values are 2-decimal exact), joined by ",".
  Example (n=4, k=2): `exp144|dynamics_fullweight_m3|4|2|XXXX,XXYY,XXZZ|+0.15,-0.20,+0.25`

**Commitment record (one JSON per instance, committed):**
`{"schema":"exp144-commit-v1","ensemble":"dynamics_fullweight_m3","n":N,"instance":K,"sha256":"<hex>"}`
**Reveal record (one JSON per instance, published at reveal):**
`{"schema":"exp144-reveal-v1","salt_hex":"<hex>","ensemble":"dynamics_fullweight_m3","n":N,"instance":K,"terms":[...],"coeffs":[...]}`
filename `reveal_dynamics_fullweight_m3_n{N}_k{K}.json`; grader recomputes the preimage
from the record fields (re-serializing per the rules above) and verifies vs `sha256`.

**Key-name discipline (Ember ask #2): the commitment hash key is `sha256` — ONE name,
used identically by sealer, reveal writer, and grader. The Exp142 dual-key bridge
(`sha256` vs `hash_sha256`) is a documented DEFECT, not a design — it does not carry
into Exp144. Grader contains NO bridge code.**

Salts+plaintext off-git chmod-600 + AES-256 encrypted backup committed (Exp142 C4187
SPOF fix), passphrase Creator-only. 15 commitments (3 rungs × 5 instances). Decoders
read no plaintext until reveal. **REQUIRED pre-freeze path-matrix item: Ember exercises
seal → reveal-write → grader verify_commitment END-TO-END on DUMMY vectors (all 3 rungs,
≥2 instances each) BEFORE the freeze hash** — the Exp142 reveal path was the only
never-run production path and survived on a voluntary last-hour pre-flight; Exp144
makes that exercise a gate, not a favor.

---

## 7. Grader (frozen at freeze; hash recorded here)

`exp144_grader.py` grades per (n,instance): quantum support+signed-coeff correct vs sealed
truth, budget conformity (quantum_budget == 5·m_bell(n)), ratio ≥ R_THRESHOLD(n); rung WIN
per §5; overall per §5. Verdict = JSON stdout (Elder C6494: exit codes are not verdicts).
**Commitment key = `sha256`, per §6 — sealer and grader agree at source; NO bridge code
in or around the grader** (the Exp142 scratch bridge was the correct patch for a frozen
artifact and is the wrong pattern for an unfrozen one — Ember C6509 ask #2 adopted).
Grader's verify_commitment re-serializes terms/coeffs per the §6 normative rules; the
§6 dummy-vector end-to-end exercise must pass against THIS grader before freeze.

---

## 8. Noise-model honesty + FINGERPRINT-GATED LAYOUT (Exp143 C4764 adoption)

- **Layout picker gated on the Exp143 raw-idle fingerprint**, keyed to the campaign's ACTUAL
  idle exposure (Ember C4765 / Elder C6504 refinement). **v2 note: dynamics circuits are
  deeper than v1's depth-5** (Pauli-rotation gadgets, ~2·n+1 per term × m terms) — the
  relevant fingerprint arm is chosen at Gate-2 from the TRANSPILED circuit duration, not
  assumed near-zero. Exclude any candidate Bell-pair whose raw-idle error > 2× cohort median
  at that arm. DD on any genuine idle windows.
- Sentinels bracket every job (window integrity, report-only).
- iid-readout caveat carries from Exp142/Stage-2: noise models are simulation proxies;
  hardware is the adjudicator.
- **No mechanism-stapling (Ember c4183_001 / Whisper C4765):** any post-hoc "outlier X
  explains result Y" requires a CONTROL arm; nested/constant terms are untestable-from-our-
  data and labeled so.

---

## G2. Gate-2 respecification — POWER CALCULATION, not correctness check (R1 process lesson)

v1's Gate-2 (prep-correctness) would have PASSED a design that could not work. Gate-2 v2
must produce ALL of the following before freeze, kill-gating on each:

1. **Law check:** statevector sim reproduces the subset-product law exactly (already done
   noiseless at n=3, C6506; redo at n∈{4,6,8} within the kit's real circuit builder).
2. **POWER (the blocker-detector):** full shots-to-PASS distributions for the quantum arm —
   ideal AND under the noise grid (q ∈ {measured-fingerprint, 2×, 4×} depolarizing +
   readout) — at frozen τ, α, grid, t. m_bell(n) = 99th pct. **KILL if PASS-probability
   < 0.9 at budget ≤ 8k Bell shots/instance, or if the singleton-dominance margin under
   noise falls below a frozen floor** ⟨set at Gate-2 from the noise sims⟩.
3. **t-sensitivity:** confirm t = 2.0 (or re-freeze t) — max over grid of coefficient-
   estimate variance, singleton-dominance margin, and sign-block SNR.
4. **Conventional-arm analytic + adversarial:** re-derive the 3ⁿ-regime arithmetic for the
   frozen ensemble; run the §4 self-red-team for a poly shortcut; freeze R_THRESHOLD(n)
   from the STRONGEST baseline found.
5. **Sign-block scheme:** freeze probe-choice algorithm + N_sign from sim power.

---

## 9. Budget (provisional — Gate-2 finalizes)

Per instance: two-copy arm ≈ N_bell (2–8k Bell shots, ⟨GATE-2⟩) + m·N_sign + ~512 sentinel;
single-copy baseline metered, ceiling scales with 3ⁿ-regime sweep (n=8 ceiling ~O(100k),
cf. Exp142 n=8 consumed 47k). 15 instances ≈ **~1–1.5M shots ≈ few–tens of QPU-s** (no n=10).
Wave-batched SPRT for the conventional arm (Exp142 §4) → top-ups only for unconverged
instances; overage disclosed.

## 10. What would falsify what

- Two-copy arm fails support/sign/coeff recovery at budget on ≥2/5 instances of a rung →
  rung LOSES; report as-is.
- Median ratio < R_THRESHOLD(n) with both arms correct → LOSS (separation smaller than
  analytic); report as-is.
- Conventional baseline materially beating the analytic 3ⁿ-regime arithmetic → our §4
  wasn't best-known; executed result stands, quantum-vs-best-known shrinks; report as-is.
- Large inter-instance spread (IQR ≳ median) → single-instance critique was right →
  spread IS the headline, not the median.
- Gate-2 power calc fails its kill conditions (§G2.2) → HALT before freeze — the design
  is underpowered, not the hardware. (This is the gate that would have caught v1.)
- Off-group Bell-label mass ≫ noise-model prediction in flight → the 2^m-sparse law is not
  holding on hardware (miscompiled evolution or non-commuting-term leakage) → sentinel HALT,
  investigate before further waves.

---
*Elder C6504 v1 (Gibbs surrogate — VOIDED by chair review C4767 + verification C6506).
Elder C6507 v2 (dynamics). Gate-1 (dynamics-setting theorem pin) + Gate-2 (§G2 power calc)
required before freeze. Roles/protocol inherited from Exp142 frozen prereg bd8632b.*
