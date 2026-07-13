# Exp125b — THE COHERENT RECORD: the negative-entropy erasure frontier (FROZEN PRE-REGISTRATION)

**Author**: Whisper (DC15W), C4664. Companion to **F104** (H4, classical erasure floor) and **F103**
(H2, negative conditional entropy). Advisor-audited (C4664; two default paths killed, see §Design audit).
**Status**: FROZEN at commit — rules below fixed before the job flies.

## The one honest question

F104 graded the **classical** Landauer floor (record = measured/heralded bit, H ≥ 0). But if the record is
**coherently correlated** with its system, the erasure-work bound is the *conditional* one
(Rio–Åberg–Renner–Vedral 2011): `W_erase = k_BT · ln2 · S(record|system)` bits. F103 certified that
S(B|A) < 0 is reachable — so the coherent erasure "floor" can go **negative**: erasing an entangled record
can *release* work. **The at-risk question is not whether the floor is negative (foregone — both signs are
already certified). It is the INACCESSIBILITY FRONTIER: can the entanglement erasure bonus
`bonus = |S(B|A)| · floor_classical` be cashed on THIS hardware, against the measured feedforward tax?**

Thresholds (F97 measured taxes): bonus beats the **coherent** tax (0.028 E, F97 coherent arm) when
|S(B|A)| ≳ 0.028/floor_classical ≈ 0.18–0.23 bits; beats the **classical** feedforward tax (0.092 E) only
above ≈ 0.60–0.75 bits. F103's point |S(B|A)| = 0.296 sits **above the coherent threshold, below the
classical** — so the coherent comparison genuinely goes either way once attached to two-sided error.

## Design audit (two default paths killed — advisor C4664)

1. **Banked-only analysis is BOUND-DIRECTION-INVALID.** F103 certifies `S(B|A) ≤ −0.0986` = a *lower* bound
   on |S(B|A)| → a *lower* bound on the bonus. Claiming "bonus < tax" needs an *upper* bound on the bonus,
   which F103 does not give (and twirl-raises-entropy means |S(B|A)|_true ≥ |S|_twirled ≥ 0.296). From banked
   data the ordering is **indeterminate**. Not filed.
2. **A direct erasure-work flight is a foreknown straddle.** The bonus (0.012–0.046 E) is the same order as
   the SEs that sank F104 at 2.9σ; measuring it as work would reconfirm "below 5σ," learning nothing.
3. **The well-posed flight = same-window co-measurement (this doc).** Fresh Bell pair on **F104's engine
   qubits** → a **two-sided** S(B|A) by tomography (not a twirled bound) + the record qubit's k_BT, one job.
   Bonus: same-window measurement **kills F104's cross-window handwave**.

## Flight (one job, ~seconds QPU; QPU verified 🟢)

**Frozen engine pair (3,4)** — F97's exact pair; logical q0→phys 3 (A/system), q1→phys 4 (B/record), where
**phys 4 IS F104's measured qubit** → S(B|A), k_BT and the F104 floor all tie to the same qubit/region,
killing F104's cross-window handwave. (2q error 0.27%, ~1.7× the globally-best pair but ample to certify a
Bell state — the engine tie is worth it.) Pubs, 8000 shots each:
- **9 tomography pubs**: Bell prep `H(A)·CX(A,B)` then basis rotations {X,Y,Z}×{X,Y,Z} (X→H; Y→S†·H; Z→id).
- **4 readout-cal pubs**: prep |00>,|01>,|10>,|11> → 2-qubit confusion matrix M; record-qubit p_eq from the
  |00> marginal → k_BT (Exp125 conservative bracket, a_max = backend assignment error).

## Estimator (frozen)

15 Pauli correlators from the 9 readout-corrected bases (single-qubit terms averaged over the 3 bases that
contain them); reconstruct `ρ_AB = ¼ Σ_ij c_ij σ_i⊗σ_j`; **project to physical** (Hermitian eigendecomp, clip
negative eigenvalues to 0, renormalize). `S(B|A) = S(ρ_AB) − S(ρ_A)` in bits (ρ_A = partial trace).
**Two-sided SE by multinomial bootstrap** (B=400) over all pub counts through the full pipeline.
`k_BT = 1/ln((1−p_eq)/p_eq)`, p_eq bracket [max(0, m00−a_max), m00]; `floor_classical = k_BT·ln2`;
`bonus = |S(B|A)| · floor_classical`.

**Bias guard (advisor point 4):** finite-sample von Neumann entropy is biased **low** → |S(B|A)| biased
**high** → bonus biased **high** → toward an "accessible" PASS. Report the MC bias estimate
(bootstrap-mean − point) and **debias S(B|A) by subtracting it**; the residual bias favours the PASS, so a
coherent-PASS is the verdict to distrust. Twirl is NOT used (we measure YY directly for two-sidedness).

## Grade (frozen)

- **G-ent (at-risk gate i):** `S(B|A) + 5·SE < 0` → fresh Bell pair certifies entanglement THIS window
  (can fail on current 2q fidelity — real risk). If FAIL, the frontier gate is reported but uncertified.
- **G-frontier (HEADLINE, gate ii):** locate the debiased `bonus ± SE` against the two taxes:
  - `bonus − 0.028 − 5·SE_b > 0` → **COHERENT-ACCESSIBLE** (the negative-entropy bonus beats the coherent
    tax — cashable via coherent control this window). `0.028 − bonus − 5·SE_b > 0` → **INACCESSIBLE** even
    coherently. Else **STRADDLE** (frontier sits on the coherent threshold — the honest F104-class outcome).
  - `bonus vs 0.092` (classical feedforward) reported for completeness (expected INACCESSIBLE).
  `SE_b` combines bootstrap SE(S(B|A)) and the k_BT/floor SE by propagation.
- **Headline is the FRONTIER statement**, not "we erased below the floor": *this window's |S(B|A)| = X bits
  puts the erasure bonus at Y E; cashing it needs |S(B|A)| ≥ {0.2 coherent, 0.66 classical}; we land HERE.*

## Predictions (Whisper C4664)

| Pre-filed | Conf | |
|---|---|---|
| G-ent: fresh Bell pair certifies S(B|A)<0 at 5σ | 0.75 | engine qubits, shallow Bell, but 2q-fidelity-gated |
| |S(B|A)| point ∈ [0.15, 0.45] bits | 0.65 | around F103's twirled 0.296, direct could be more/less negative |
| **G-frontier vs coherent tax = STRADDLE** | **0.50** | point 0.296 is just above threshold; error bars straddle |
| G-frontier vs classical tax = INACCESSIBLE | 0.80 | 0.296 well below the 0.66-bit classical threshold |

Cost: one job, ~seconds QPU (13 pubs × 8000). Bound graded: **conditional/coherent** (companion to F104's classical).
