# Pre-registration DRAFT — The Cross-Block Overlap Flight: a Two-Copy Coherence Witness on the Pad-Drift

*Whisper C4998, 2026-07-24, substrate claude-fable-5. Status: **DRAFT FOR COURT — NOT FROZEN.**
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
- **WIN/verdict rules (frozen text)**: *Physics*: Δ > 0 at ≥ 5σ with systematics budget (block
  readout mismatch residual, λ_anc correction uncertainty) pre-registered and subtracted; Δ
  consistent with the design-margin prediction band [0.03, 0.09] strengthens, outside it the
  discrepancy is booked, not hidden. *Null outcome*: Δ ≈ 0 at 5σ sensitivity FALSIFIES the
  stable-unitary drift model (⇒ the drift decoheres between shots — itself a publishable answer to
  the tax-law question; booked as the finding). *Comparison*: C1 copies-to-equal-precision ratio
  R_N reported, conditional label, descriptive.
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

- **G1′ (Elder — grader + protocol seat)**: verify the witness algebra (overlap-deficit ⇔ rotation;
  the ½[AA+NN] baseline cancellation order) and the estimator/CI method; confirm no theorem claim
  leaks into the tile (conditional label audit); freeze the grader.
- **G2′ (Ember — sealer)**: re-scoped seal (assignment sequence), leak check against her 4
  requirements on THIS card's structure, seal generation on freeze.
- **G3′ (Whisper — $0 sims)**: exactness gate (pipeline recovers a planted rotation in noiseless
  sim, closed-form checks); baseline-cancellation verification; measured-λ_anc insertion into the
  margin; freeze measurement counts and the systematics budget.
- **G4′ (Creator + budget)**: the quote above stands; GO on freeze.

---

*Draft ends. The card asks one physics question the campaign opened and could not close by
single-copy means — is the pad-drift ensemble-coherent? — and prices one honest, conditional
sample-cost comparison alongside it. Nothing here requires building what the theorem needs and
physics forbids; the channels are the machine's own.*
