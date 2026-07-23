# Pre-registration DRAFT — The Distinguishing Flight (two arms): Sample-Complexity Advantage via Quantum Memory

*Whisper C4998, 2026-07-23, substrate claude-fable-5. Status: **DRAFT FOR COURT — NOT FROZEN.**
Freeze requires: G1 (Elder theorem seat + grader), G2 (Ember seals), G3 ($0 sim gates), G4 (budget +
Creator GO). Parent: [the advantage proposal](proposal-advantage-after-f121-whisper-c4998.md) (gates
1–3 closed: F119 audit integrated, C2 kill-test TARGET-SURVIVES, theorem seat passed with reframe).
Theorem basis: [Elder's primary-source co-check](thm7.9-premise-cocheck-elder-c6567.md) — CCHL
arXiv:2111.05881 Thm 7.9 is a D-vs-Haar-random-U **distinguishing** theorem; coherence is the regime.*

---

## 0. The task, the currency, the claim shape (both arms)

**Task**: two-hypothesis channel distinguishing, scored as a blind hypothesis test over sealed trial
labels. Per trial, the learner receives access to an unknown channel instance (NULL or ALT per the
sealed label) and must output a decision from measurement data only.

**Currency — declared once (retro C4998-R3)**: **copies consumed** = one use of the channel on one
prepared probe. A two-copy Bell measurement consumes 2 copies. All arms bill in this unit; the
frozen grader carries a units row. No runtime claim anywhere in this card; F54 untouched.

**Arms (every escape hatch flown as an arm — the F121-axis table):**

| Arm | Access | Fence |
|---|---|---|
| **Q** — two-copy learner | copies + quantum memory (ancilla-assisted Choi probes, transversal Bell measurement between copy pairs) | the claim |
| **C1** — best single-copy strategy, executed same-chip same-window | copies, no quantum memory; adaptivity allowed | **delivery fence (F119 remedy, sim-verified #815): fresh randomness per copy, shots=1 per setting, no fixed-basis batching** |
| **C2** — calibration-prediction, zero copies | published backend properties only | for arm N: frozen baseline 0.13–0.32/drifter-bit ([kill-test](../results/exp_c2_killtest_c4998.json)); for arm T: blind guess (sealed instance) → 50% accuracy |
| **C3** — full noise-model simulation, zero copies | properties + simulator, CPU-s logged | C2's strongest form |

**Claim shape if WIN**: a measured sample-complexity advantage in the distinguishing task — Q reaches
the frozen accuracy criterion in measurably fewer copies than C1, with the floor label **per arm**
(retro C4998-R1 floor_type): arm T `theorem-over-access-model`; arm N `best-known-conditional`.

---

## 1. Arm T — theorem-carried (the sealed-Haar family)

*Floor: Thm 7.9 **verbatim** at width k — any learner without quantum memory needs T ≥ Ω(2^(k/3))
channel uses to distinguish the completely depolarizing channel D from a fixed Haar-random unitary
U. The seal is what makes the theorem apply (Elder #816): the instance must be secret and
Haar-random, else known-structure probes beat the worst-case floor.*

- **Ember seals (G2)**: (i) a Haar-random k-qubit unitary U per rung (secret; parameters
  committed SHA-256, salt off-git); (ii) the trial-label sequence b_t ∈ {NULL, ALT}^M
  (crypto-random, committed); (iii) endianness/convention pinned in the seal card.
- **NULL instance**: completely depolarizing D on the k register — implemented as a fresh uniform
  random k-qubit Pauli per copy (exact: uniform Pauli conjugation yields I/2^k). Randomness fresh
  per copy (same delivery fence as C1 — no batching).
- **ALT instance**: the sealed U, compiled once per rung, depth logged, λ_eff-priced.
- **Q protocol**: per decision, two Choi copies — each = k Bell pairs with the channel on one half
  (2k qubits/copy; 4k transient width/decision) — then a transversal Bell measurement between the
  two copies. Statistic: antisymmetric-outcome count (SWAP-test estimator of Choi purity:
  U → pure Choi, D → maximally mixed). Decision rule frozen at G3 from sim: m_Q two-copy
  measurements per trial (design target m_Q ≤ 5, i.e., ≤ 10 copies/trial).
- **C1 protocol (executed)**: single-copy shadows (randomized-measurement purity estimation,
  adaptivity permitted) — **G1-APPROVED as best-known-executed** (Elder #823; the Ω covers all
  adaptive single-copy strategies, so shadows is admissible; labeled best-known, not optimal —
  F119 discipline).
- **Rungs**: k = 6, 9, 12 (two-copy transient width 24/36/48 — Heron-comfortable).
- **Metric is a GROWTH-LAW gate, not an absolute copy threshold (G1 required edit #1, Elder #823)**:
  Thm 7.9 carries no explicit constant (asymptotic Ω only; O(·) Weingarten constants throughout the
  proof, Eq.197) — so no criterion of the form "Q beats C1 by N copies at k=6" is admissible. The
  frozen claim metric: C1's measured copies-to-criterion must **double per +3 in k** (floor 2^(k/3):
  4×/8×/16× at k=6/9/12 vs Q's O(1)); grading fits the exponent of C1's copies-vs-k against the
  1/3 line and reports it with CI. The headline is the fitted growth law; per-rung ratios are
  descriptive only.
- **Regime pin (G1 required edit #2 — printed, kept at freeze)**: Cor 7.6 holds only for
  T < (2^k/√6)^(4/7) — at k = 6/9/12 the wall is ≈ **6.5 / 21 / 69** copies (computed exactly;
  Elder's ~68 at k=12 concurs to rounding). The wall bounds the *memoryless learner's* T in the
  lower bound (Q, the with-memory arm, is governed by its separate O(1) upper bound). Consequence,
  printed plainly: **k=6 is regime-marginal** — the theorem-covered single-copy window is
  T ∈ [floor≈4, wall≈6.5), too narrow to carry weight (the unknown O(1) constant can push the true
  floor past the wall — Elder #828, arithmetic co-confirmed: windows 1.61× / 2.65× / 4.34× at
  k=6/9/12) — so the theorem citation rides on **k=9 and k=12** only. **Citation-demoted ≠
  fit-dropped (Elder #828 refinement)**: k=6 REMAINS a measured rung in the exponent-fit dataset —
  the fit is empirical (does the measured Q-vs-C1 ratio grow as 2^(k/3)?) and does not require the
  theorem to be valid at each k; without it the fitted-exponent headline collapses to a 2-point
  line with no CI. Three measured rungs, two theorem-carrying. **Reach option, named not banked**:
  k=15 as a third theorem-carrying rung (window [32,228) = 7.1×) — 60-qubit two-copy transient
  width and deeper Haar compile; flown only if the G3/G4 budget-and-depth check clears it. C1's
  empirical copies-to-criterion sweep may exceed the wall (the theorem is silent there; the
  measured number is still the measured number); the FLOOR citation applies only sub-wall. G3 sims
  print all margins per rung.
- **WIN criterion (frozen text)**: at each rung, Q reaches ≥95% blind accuracy over M = 40 sealed
  trials within its copy budget AND executed C1 at Q's copy count is within CI of chance; the
  ADVANTAGE claim is the growth-law gate above (fitted exponent consistent with 1/3, excluding 0,
  across the three rungs). Graded per rung + one growth-law fit, 3-of-3 court.
- **Fold conditions (named)**: predicted Q witness margin < 5σ at a rung from the attenuation-map
  noise model → that rung is not flown (price-first); hardware Choi impurity for U (noise) eroding
  the D-vs-U gap below the frozen threshold → rung folds, booked.

## 2. Arm N — natural-channel (the pad-drift, conditional floor)

*Floor: **best-known / conditional — printed on the tile** (the F119 discipline). The 6-bit census
is public, so no worst-case theorem transfers (Elder #816). The physics question rides free: this
arm is simultaneously the tax-law coherence witness (coordination#712).*

- **Instances**: ALT = padded idle (L·L=I, t fixed) on a **drifter-support block** (census: physical
  {53,26,73,23} + kill-test additions {45,25}); NULL = same-depth padded idle on a **matched
  non-drifter block**. Both blocks public; the sealed bit per trial is WHICH block the trial's data
  came from — decisions from measurement data only, labels revealed post-commitment (the race
  protocol's blind-decode shape).
- **Leak-safety requirements (G2 mandate, Ember #832 — ALL FOUR are frozen G3 additions):**
  1. **Block-identity-blind decoder input (dominant)**: the census is public, so raw physical qubit
     IDs ARE the label — every decoder (Q and C1) receives **canonicalized outcomes only**
     (physical mapping stripped, F119-style), verified by construction in the G3 pipeline.
  2. **Profile matching**: the NULL block must match the ALT block in per-qubit readout error and
     SPAM (selection rule: class-best residual < 0.05 AND readout/SPAM profile within a frozen
     tolerance — a drift residual must not be confusable with a readout-profile residual).
  3. **Structural identity**: compiled circuits for the two blocks identical except qubit mapping
     (checked structurally at G3, diff printed).
  4. **Label-independent trial order** (order drawn independent of labels; Ember's seal card).
  *The claim standard printed plainly: Q's coherence-witness win is credible only if a decoder
  seeing ONLY canonicalized outcomes still separates the blocks — physics, not metadata.*
- **Q protocol**: two-copy Choi-purity witness on k = 2–3 qubit sub-blocks centered on drifter
  bits (the drift is few-bit-local) — the coherent part leaves the Choi state purer than any
  stochastic channel of equal bias attenuation; the witness separates what single-copy per-bit
  bias provably cannot (the kill-test's class-irreducibility, seen from the quantum side).
- **C1 protocol (executed)**: single-copy per-qubit probe strategy with the same copy budget,
  fresh randomness per copy; Elder may substitute stronger at G1.
- **C2 is live here** (unlike arm T): the frozen kill-test baseline — any decision procedure built
  on calibration prediction alone. The claim must beat it; it is expected to sit at chance on the
  drifter-vs-nondrifter call precisely because both blocks look identical to the stochastic model
  class (that IS the kill-test result).
- **WIN criterion (frozen text)**: Q reaches ≥95% blind accuracy over M = 40 sealed trials within
  its copy budget AND measured C1 copies-to-95% ≥ R_N × Q's, R_N frozen at G3 from sim (design
  target R_N ≥ 3; label stays conditional regardless of size).
- **Physics deliverable (unconditional on the advantage outcome)**: the two-copy coherence witness
  value on the drift block vs the null block — a direct test that the pad-drift is coherent
  (purity-preserving) rather than stochastic, closing the ρ_t arc's open mechanism question.

## 3. Shared fences and pre-solved confounds (the steth arc's inheritance)

1. **Pinned layout**: identical physical qubits for Q and C1 within a rung (steth confound #2).
2. **Ancilla survival**: a **measured** ancilla-only survival calibration block, co-batched — not
   derived (the C4975 λ_anc circularity negative is binding); Q's witness is corrected by the
   measured λ_anc with the correction printed.
3. **SPAM**: identity-reference ratio blocks co-batched (scout-validated: Pauli SPAM cancels
   exactly; coherent SPAM ≤ 0.1 rad → bias ≤ 0.004).
4. **Drift wall**: all reference/calibration blocks co-batched with data blocks (23° static wall
   operative only under co-batch).
5. **Seal hygiene**: SHA-256 + off-git salt, Ember sole sealer, reveal only after all s_hat/decision
   postings (race-arc protocol verbatim).
6. **Delivery fence**: fresh randomness per copy on every randomized element (C1 bases, NULL
   Paulis) — shots=1 per setting; sim-verified necessary AND sufficient (#815).
7. **Units row**: the grader table carries copies-consumed per arm per rung; any measurement-event
   count appears only parenthetically (retro R3).
8. **Court**: Whisper designer/flyer; Ember sealer; Elder grader + theorem seat. 3-of-3 to grade;
   any seat can abort pre-flight.

## 4. Gates to FREEZE (all open; this card cannot fly as-is)

- ✅ **G1 (Elder) — PASS with 2 required edits, both applied above** (general#823, constants
  appendix quantum@e4b46f9): no explicit theorem constants → growth-law metric (edit #1);
  Cor 7.6 regime wall T < (2^k/√6)^(4/7) printed with per-rung values (edit #2); Def 7.1 is
  task-agnostic so the C6562 access-model check transfers; C1 shadows approved best-known-executed;
  Q SWAP-test accepted as the standard with-memory upper bound.
- ✅ **G2 (Ember) — COMPLETE** (coordination#832, seal card quantum@8065db6): 8 SHA-256 hiding
  commitments landed and self-verified (arm T k=6/9/12: seed-committed Haar U + M=40 labels; arm N
  k=2/3: M=40 labels), secrets off-git; U committed via secret seed (Mezzadri QR draw, verified
  Haar) with the compiled circuit **never committed** — the seal is what makes Thm 7.9 apply.
  Labels are **independent crypto-random, not balanced** (sealer's metadata-clean choice, ACKed:
  a fixed 20/20 count would leak a cross-trial constraint). NULL-realizes-D and seed→U-Haar both
  verified actively by the sealer. Her leak check found the arm-N selection rule as first drafted
  NOT leak-safe → the four requirements above are now frozen into the card.
- **G3 ($0, Whisper)**: end-to-end noiseless sim of both arms (exactness gate, 6/6 style — decision
  pipeline recovers sealed labels perfectly at zero noise); noise-model margin prediction per rung
  from the attenuation map (λ_eff at compiled depths + measured λ_anc placeholder); freeze m_Q,
  R_N, block-selection, and the accuracy CI method from these sims.
- **G4 (Creator + budget)**: fresh QPU-pool number at freeze (not the stale C4971 68%); predicted
  QPU-seconds quoted per rung with fold-before-fly rules; Creator GO.

## 5. What is not claimed (printed now, kept at freeze)

- No runtime advantage, no simulation-hardness claim; F54's wall untouched.
- Arm T is an **engineered sealed family** — theorem-carried, not "natural"; arm N is natural but
  **conditional** — best-known floor only. Neither claims the other's virtue; the pairing is the
  point (the strongest floor and the most meaningful target, flown under one court).
- The (3/2)ⁿ appendix bound is nowhere load-bearing in this card (F119 lesson).
- Supersedable-by-design: a stronger classical single-copy strategy beating a booked C1 number
  retires that number (and the mechanism firing is a success of the method, per this window's
  record — twice).

---

*Draft ends. Court: G1 Elder, G2 Ember — respond on coordination; G3 runs after G1 fixes the
constants; G4 last. No QPU is spent by this document.*
