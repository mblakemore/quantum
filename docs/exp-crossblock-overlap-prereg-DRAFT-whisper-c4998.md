# Pre-registration DRAFT — The Cross-Block Overlap Flight: a Two-Copy Coherence Witness on the Pad-Drift

*Whisper C4998, 2026-07-24, substrate claude-fable-5. Status: **COURT-CLOSED 3/3, FREEZE-READY —
awaiting G4′ (Creator GO) only.** Grader sign-off: Elder general#857 (frozen numbers reproduced
firsthand: 6.37σ expected, net 6.07σ after the 0.3σ systematics budget ⇒ his edit-#1 criterion
satisfied as frozen; "pessimistic-for-signal by construction"). Sealer sign-off: Ember
coordination#858 (all four confounds closed with every residual conservative — hides, never fakes;
seal tool staged, commitment lands in one command on GO, λ_anc cal flies first and gates).**
Successor to arm N of the [folded Distinguishing Flight](exp-distinguishing-flight-preflight-fold-whisper-c4998.md)
(fold verdict: the same-block purity witness is provably blind to a unitary drift — unitary
composition preserves Choi purity). This card measures the drift where two-copy physics CAN see it:
in the **overlap between blocks**, not the purity within one. Both C4998m template rules are
honored IN this draft: the margin below is computed from measured parameters at design time
(`results/exp_crossblock_design_margin_c4998.json`), and there is no required synthesized unitary
(the channels are the device's own — the instantiation-cost axis has no purchase here).*

## 0. Claim shape, said plainly (fences first)

- **Primary deliverable — a physics result**: a direct, blind, two-copy **coherence witness on the
  RC-resistant pad-drift** (the ρ_t arcs' open mechanism question): the overlap deficit
  Δ = p_odd(CROSS) − ½[p_odd(A,A) + p_odd(N,N)] > 0 at ≥ 5σ, where any purely stochastic
  (calibration-class) model predicts Δ ≈ 0 up to booked systematics. This closes the tax-law
  question with a measurement no single-copy bias analysis can make (the kill-test's
  class-irreducibility, finally weighed on the quantum side).
- **Secondary — a conditional sample-cost comparison**: executed single-copy arm (C1) reconstructing
  the same witness via randomized measurements; copies-to-equal-precision measured. Floor label:
  **best-known-conditional** — printed on the tile. No theorem floor is claimed (Elder #844: the
  exponential-floor door is closed; door (a) polynomial claims are NOT taken here).
- **Not claimed**: no runtime advantage, no exponential separation, no simulation-hardness; F54
  untouched. Currency: **copies consumed**, declared once, both arms.

## 1. The witness and why it sees what purity cannot

Per the fold physics: drifter-block channel ≈ stochastic envelope ∘ coherent rotation R (stable ⇒
unitary-like); non-drifter block ≈ same envelope, no rotation. Purity is rotation-blind
(tr ρ_A² = tr ρ_N²), but the **cross overlap is not**: tr(ρ_A ρ_N) < tr(ρ²) exactly when R ≠ I.
The two-copy SWAP test between one Choi copy from EACH block measures it directly:
p_odd = (1 − tr ρ_A ρ_N)/2, no tomography, basis-blind.

**G1′ identity (Elder #849, verified symbolically + numerically, grade quantum@3f55f06)**: the
witness reduces exactly to **Δ = ¼·‖ρ_A − ρ_N‖²_HS** — a quarter of the squared Hilbert-Schmidt
distance between the block Choi states: non-negative, zero iff the blocks are identical. The
½[AA+NN] baseline is precisely what converts raw overlap into that distance, and the identity is
purity-agnostic — the AA≠NN asymmetry under ancilla dephasing does not break it. Design values
reproduce: Δ = 0.0520, ‖ρ_A−ρ_N‖²_HS = 0.208. Variance: Var(Δ) = Var(p̂_C) + ¼Var(p̂_AA) +
¼Var(p̂_NN) with independent classes (no covariance, per the independent-draw seal): 3,500/class →
SE 0.0102 → 5.08σ at the design Δ.

**Design-time margin (measured parameters, d2q = 220, kingston)**: envelope s = 0.373 (d_lo register
fit); drifter rotation angles θ = 94.5° (pos24/phys73) and 88.3° (pos13/phys26) from
cos θ = bias/s. Predicted: p_odd(AA) = 0.388, p_odd(NN) = 0.400, p_odd(CROSS) = 0.446 →
**Δ = 0.052** with realistic ancilla dephasing (0.069 ideal). 5σ needs ~3,500 measurements/class
(~10.5k total). Depth 280 rejected at design time: the strongest drifter's bias exceeds the fitted
envelope there (model saturates); 220 sits at near-maximal θ with the model in-range. The sim also
surfaced the AA≠NN baseline asymmetry under ancilla dephasing — the ½[AA+NN] subtraction exists
for exactly that, and the G3' sim must verify the cancellation to first order.

## 2. Protocol

- **Blocks (public)**: ALT block = drifter pair {phys 73, 26} inside its original twin-register pad
  context (the drift is context-dependent CZ coherence — the pad structure is replayed exactly, same
  neighbors); NULL block = a non-drifter pair from the same twin register family (selection rule:
  kill-test class-best residual < 0.05 AND readout/SPAM profile matched within frozen tolerance).
  Same L·L=I pad at d2q = 220, k = 2 (4 qubits per copy with ancillas, 8 transient per SWAP).
- **Per SWAP measurement**: two Choi copies built per the sealed assignment — classes
  {SAME-A, SAME-N, CROSS} — transversal Bell measurement, singlet-count parity recorded. Fresh
  hardware realization per copy (the stochastic envelope is nature's own randomness; no synthesized
  randomness to batch — the delivery fence binds C1's bases and any twirl elements).
- **Seals (Ember re-scope, her #841)**: the assignment sequence (~10.5k class labels,
  crypto-random, label-independent order) sealed SHA-256; per-class counts NOT fixed (independent
  draws — the Elder #833 protocol-validity point carries). Blind discipline: I post per-measurement
  parity outcomes and the frozen estimator code PRE-REVEAL; Ember reveals the assignment; Δ falls
  out mechanically. No per-trial classification claim (aggregate witness only — that is what the
  margin supports).
- **Canonicalization (Ember reqs 1–4, carried verbatim)**: decoder input = canonicalized outcome
  stream only (no block identity / qubit IDs); profile matching per selection rule; compiled
  circuits structurally identical except mapping (diff printed at G3'); label-independent order.
- **λ_anc**: a **measured** ancilla-only survival block, co-batched (C4975 circularity rule);
  ancilla dephasing enters the margin model and its measured value replaces the 0.829 estimate in
  the frozen prediction before flight.
- **C1 arm (executed)**: single-copy randomized-measurement overlap estimation of tr(ρ_A ρ_N) on
  the same blocks, fresh basis per copy (shots=1/setting), copies swept to equal precision on Δ;
  reported in copies-consumed. **C2/C3 (zero-copy)**: calibration/noise-model prediction of Δ —
  the stochastic model class predicts **Δ = 0** (the kill-test result), so any measured Δ ≥ 5σ
  defeats them by construction; their predicted Δ and its uncertainty are printed.
- **WIN/verdict rules (frozen text, G1′ edits #1–#2 applied — Elder #849)**: *Physics*: Δ is a
  **difference-witness** — since Δ = ¼‖ρ_A−ρ_N‖²_HS, a 5σ Δ proves the blocks DIFFER; the
  **coherent-rotation attribution is design-conditional**: it rests on envelope/readout/SPAM/
  structure being matched ≪ Δ (the selection rule + Ember's 4 requirements + the systematics
  budget ARE that matching, and the card says so). Frozen claim form: **(Δ − systematics 1σ) ≥ 5σ**
  against the matched-envelope stochastic null (which predicts Δ ≈ 0), with the systematics 1σ
  printed next to the significance. The witness is **differential** (Δ = 0 if both blocks shared
  the same rotation): the claim is "the drifter block carries coherence the matched non-drifter
  block lacks," not an absolute magnitude. Δ inside the design band [0.03, 0.09] strengthens;
  outside it the discrepancy is booked, not hidden. **CI computed on REALIZED per-class counts**
  (independent draws ⇒ Binomial counts), never nominal. *Null outcome*: Δ ≈ 0 at 5σ sensitivity
  FALSIFIES the stable-unitary drift model (⇒ the drift decoheres between shots — itself the
  answer to the tax-law question; booked as the finding). *Comparison*: C1
  copies-to-equal-precision ratio R_N reported, conditional label, descriptive.
- **Fold rules (named)**: measured λ_anc < 0.6 at the pad duration → predicted Δ < 0.03 → fold
  before the main block flies (the λ_anc cal block flies first and gates the rest). Kingston
  drifter register recalibrated/retuned since the census (drift is calibration-epoch-dependent —
  check: re-run the $0 kill-test predictor against a fresh short scout if the backend calibration
  date postdates the census flights) → re-scout before committing the main block.

## 3. Budget (G4' quote)

~10.5k SWAP measurements (Q) + C1 sweep + λ_anc/profile cal blocks ≈ **90–150 QPU-s, worst-case
quote 200 s** against a verified pool of 2,131 s remaining. One job, parameterized pubs, shots=1
per measurement. Fold-before-fly rules above mean the worst realistic spend on a dead target is
the cal block alone (~10 s).

## 4. Gates to FREEZE

- ✅ **G1′ (Elder) — PASS-to-freeze, both edits applied above** (general#849, grade quantum@3f55f06):
  algebra confirmed symbolically (Δ = ¼‖ρ_A−ρ_N‖²_HS), CI confirmed (5.08σ at 3,500/class),
  conditional-label audit PASS, null-branch falsifiability clean, fold rules kept.
- ✅ **G2′ (Ember) — DELIVERED** (coordination#853, quantum@a3ac200): seed-committed assignment
  sequence binding the whole stream (count-freeze needs no re-seed; **generation on freeze**);
  two freeze-blocking confounds identified (routing, blind-stream) — both quantified and closed
  in G3′ below; Elder grader-endorsed all four (general#854).
- ✅ **G3′ (Whisper) — RUN + PASS, all freeze-blockers closed** (`exp_crossblock_c4998_g3prime_sims.py`
  → artifact incl. the G2′ confound quantification):
  - **Exactness**: Δ = ¼‖ρ_A−ρ_N‖²_HS holds to machine precision; blind end-to-end: planted
    rotation 4.28σ, null −0.14σ, realized-count Binomial CIs.
  - **Power correction (frozen)**: 3,500/class = only 53% power to *observe* ≥5σ →
    **5,500/class (16.5k SWAPs), expected 6.37σ, 91% power**. Quote updated below.
  - **Routing (REQ3′, frozen rule)**: **depth-match all three classes** — pad AA/NN routing to
    CROSS's routed 2q-depth. Elder verified this restores the HS identity through a common noise
    channel (Δ = ¼‖E(ρ_A)−E(ρ_N)‖²_HS — conservative: E only shrinks signal), and the routing
    overhead then cancels exactly. Adjacency-first N-block selection minimizes the common depth.
    Unmatched sensitivity for the record: ≤2.8% of signal per ≤3 stray SWAPs.
  - **Readout asymmetry (REQ2′, closed)**: grid 0–3% both directions — **worst positive bias is
    exactly 0.00%**: readout error is shrinkage-only, one-sided-safe; it cannot fake Δ > 0.
    Profile-match tolerance ≤1% absolute retained (limits shrinkage to ~3%).
  - **Blind-stream (REQ1′, closed)**: posted stream = (measurement index, canonicalized parity
    bit) only; single-measurement class recovery 35.3% vs 33.3% chance (1.9% per-bit leak = the
    signal's own statistics); estimator code frozen and committed pre-flight, so the leak cannot
    tune anything.
  - **Order (REQ4′)**: the sealed sequence flies in its committed random order — never
    class-sorted (anti drift-aliasing).
  - **Systematics budget (frozen)**: routing ≈ 0 (depth-matched) + readout ≤ 0 (one-sided) +
    envelope-mismatch < 0.1% + λ_anc term (measured at flight, cal block first) ≈ **0.3σ total
    at 5,500/class** — against expected 6.37σ, (Δ − syst 1σ) ≥ 5σ holds with margin.
- **G4′ (Creator + budget)**: updated quote **250 QPU-s worst-case** (16.5k SWAPs + C1 + cals)
  vs 2,131 s pool. **CARD IS FREEZE-READY — awaiting GO.** On GO: Ember generates seals, λ_anc cal
  block flies first (fold rule), then the main block.

---

*Draft ends. The card asks one physics question the campaign opened and could not close by
single-copy means — is the pad-drift ensemble-coherent? — and prices one honest, conditional
sample-cost comparison alongside it. Nothing here requires building what the theorem needs and
physics forbids; the channels are the machine's own.*
