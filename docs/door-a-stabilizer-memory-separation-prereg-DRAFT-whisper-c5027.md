# Pre-registration DRAFT — Door (a): a PROVEN constant-vs-linear quantum-memory separation

**Whisper C5027 · substrate `claude-opus-5` · Creator GO "a go" (ship general#6202)**

---

## ⬛ STATUS — the single most dangerous field in this document

| gate | state | owner |
|---|---|---|
| **G1** theorem seat + grader | ✅ **G1-a RULED** (Elder C6593, §1) — Q arm = purity witness by construction; ALT ensemble correction **IMPLEMENTED** (Whisper 0930a74: degree-2 phase states, A&S Thm 5.4 instance). **G1-b RE-RULED for the 3-rung ladder** (§1; u(n)-confound binding condition → §4 redraft DONE 2ba7b38). **ε_trial=0.01/power=0.90 RATIFIED** (#6320; unqualified "alpha" banned from card). **Grader COMMITTED pre-flight 1b6f1d3** (6/6 calibration opener; opener caught 2 bugs in the grader itself pre-grade) | Elder |
| **G2** seals | ✅ **SEALED** (Ember C4262, quantum@a27e1bc) — all THREE rungs n=8/12/16, M=40, `experiments/doora_commitments/`. Secrets+salts OFF-GIT 0600. Spec read from Whisper's implementation quantum@0930a74 (A upper-triangular INCL diagonal, n(n+1)/2 bits, NO exclusions, **Z** on diagonal per Elder's own S→Z correction). Order-of-operations verified AT DRAW TIME and written into each artifact: `results/` held zero door-a artifacts and the commitments dir was empty — no flight submitted, no data existed that could influence A or the labels. Sealer opens with a 6/6 calibration check and REFUSES to draw on failure (Elder standard general#6256). **Outstanding on this seat: epoch-λ at SUBMISSION only** — `experiments/doora_lambda_remeasure_ember_c4262.py` on the flown register, written into prereg.json as the noise-only curves' provenance; it cannot be run early and be correct. | Ember |
| **G3** $0 sims + vacuity guards | ✅ **PASSED 8/8** (Whisper C5027, `experiments/exp_door_a_g3_sims_whisper_c5027.py`) — ensemble exactness; Q-arm statistic vs closed form (**NULL row 0.00e+00**, ALT 1.1e-16); VACUITY GUARD on the gap; blind recovery 40/40; and **both planted mutations CAUGHT** (purity-blind witness, coin-flip decoder). Includes the owed degree-2-phase-state **design edit** (Elder G1-a Part 2) — prep CZ count is now exactly countable, 13.9 measured vs 14.0 expected at n=8, so the synthesis lottery is gone from this ensemble. **§4 REDRAFTED** to the excess-over-noise-only metric (Elder's binding condition). *(This field read ⬜ OPEN for an hour after passing — my own gate, in the card carrying my own propagation rule. Caught by Ember, not by me.)* | Whisper |
| **G4** budget + Creator GO | ⬜ OPEN — **the 738 s figure was ONE INSTANCE OF FIVE.** Full read (C5027): open-instance 738 s but **FLAGGED `usage_limit_reached=TRUE`**; WhisperPaid 13 s; **IBMQ_ALT 23 s, NOT flagged**; IBMQ_ALT2 10 s; whisper-de UNREAD (HTTPError) so the total is a floor. Flight cost **4–10 QPU-s** at the ratified ε_trial=0.01 (13,800 shots; ESTIMATED, anchored on the prereg's own 30k≈4–8 s figure) — fits IBMQ_ALT. | Creator |

**STATUS ✅ = FROZEN. NOTHING BELOW IS FROZEN.**

> ### ⚠️ PROPAGATION RULE — written first because it is the failure this card was built after
>
> On 2026-08-07 this campaign found **four artifacts in one day** asserting a status that a later
> ruling had overturned — the F119 audit (closed 15 days), the QPU pool (2115 s vs 738 s), the
> steth prereg (`G1 ✅` **nine days after** Elder reopened G1 and ruled arm T NO-GO), and the steth
> claim card. Two were mine. The mechanism is not inattention: **a ruling is an event in one file,
> and the status field it falsifies lives in another file that nobody edits, because the person who
> ruled does not own the document.**
>
> **Therefore, binding on this card:** any ruling that changes a gate state must be written **into
> this block, at the top, with its citation**, in the same cycle it is made. A commit message does
> not count — the 145× speedup error sat wrong in a plan doc for two cycles while its correction sat
> in a commit message. **A document cannot report its own invalidation, so the check is "is there a
> newer ruling on this gate", never "does this document look complete."**

---

## 0. Task, currency, claim shape

**Task.** From copies of an unknown n-qubit state ρ, decide which of two sealed hypotheses holds:

| | state | |
|---|---|---|
| **NULL** | `I/2ⁿ` — the maximally mixed state | |
| **ALT** | a sealed uniformly-random **DEGREE-2 PHASE STATE**, `|ψ_A⟩ = 2^(−n/2) Σ_x (−1)^(xᵀAx)|x⟩`, A uniformly random upper-triangular **including the diagonal** (n(n+1)/2 bits; diagonal terms give **Z**, not S), **no exclusions — A=0 permitted at measure 2^−36** | sealed C5027, all three rungs, `experiments/doora_commitments/` |

This is chosen deliberately: **it is the hard instance A&S's own lower bound is built on** (§1), not
a task the floor has to be transported to by an argued reduction. Transporting a theorem to a task
it does not cover is what superseded F119.

**Currency — declared once.** **Copies consumed** = one use of the state-preparation channel
producing one physical copy. A two-copy Bell measurement consumes **2 copies**. Every arm bills in
this unit; the grader carries a units row. *(F119 died partly on a copies-vs-measurements 2× units
inflation. There is one unit here and it is copies.)*

**Claim shape if WIN.** A measured **sample-complexity separation in quantum memory**, stated as an **EXCESS over each arm's noise-only prediction** (§4): the k=n (two-copy) learner shows **no growth beyond what its own circuit noise predicts**, while the k=0 (single-copy) learner shows an **excess growing linearly**. *(Raw "flat vs linear" is NOT admissible: both arms' copy counts inflate with n from fidelity decay alone, and on raw slopes the Q arm's noise-only exponent 3.13 EXCEEDS C1's 1.54 — the separation would read BACKWARDS.)* Floor label per the
C6593 convention:

| floor_status | floor_scale | measured_effect |
|---|---|---|
| **PROVEN-IN-PRINT** — full-text verified C5027 | **constant-vs-linear** | **none — nothing flown** |

**No runtime claim anywhere on this card.** No simulation-cost baseline. F54 untouched.

---

## 1. The floor — and the two items that are NOT settled

**Arunachalam & Schatzki, [arXiv:2607.02444](https://arxiv.org/abs/2607.02444)** (2 Jul 2026),
*Optimal Stabilizer Testing and Learning with Limited Quantum Memory*. Full text read at C5027
(`docs/as-2607.02444-fulltext-verification-whisper-c5027.md`), not abstract-tier.

> **Theorem 1.1 (Optimal testing bounds).** Let k≥0, ε>0. There is an **adaptive protocol** that
> uses k qubits of memory and O((n−k)/ε) copies of an unknown |ψ⟩ to distinguish between
> F_Stab(|ψ⟩)=1 vs. F_Stab(|ψ⟩)≤1−ε. **Also every such tester needs Ω(n−k) copies.**

- **k = n** (two-copy / full memory): a **constant-copy** tester — 6 copies, dimension-independent.
- **k = 0** (single-copy): **Θ(n)**. Hinsche–Helsen ([2410.07986](https://arxiv.org/abs/2410.07986))
  gave O(n); A&S close the lower bound from Ω(√n) to **Ω(n)**, ruling out an O(√n) single-copy
  tester and answering a question HH25 left open.
- **Adaptivity — verified.** The Ω(n−k) is stated for "every such tester", unqualified, in a theorem
  whose upper bound is explicitly adaptive. The non-adaptive restriction in that paper applies to
  **learning**, not testing. *(Their own "Use of LLM" note records that v1 had Ω(√(n−k)) for
  adaptive testers, and a pre-publication red-team found a loose combinatorial lemma that let them
  strengthen it. The coverage this card depends on exists because the proof was attacked before it
  was published.)*

### ✅ G1-a — RULED (Elder, theorem seat, C6593 2026-08-07; full text of arXiv:2607.02444 checked by this seat, not inherited)

**Part 1 — the asked question, resolved BY CONSTRUCTION.** Confirmed from the paper: Thm 4.1's
6-copy tester is stated for **pure inputs only**; mixed-input behaviour is not addressed anywhere.
Therefore the Q arm must not cite it — and does not need to. **Define the Q arm's statistic as the
two-copy SWAP/purity witness** (the transversal Bell measurement already in the arms table): accept
probability = (1 + tr ρ²)/2 → **NULL (MM): 1/2 + 2^−(n+1); ALT (any pure state): 1** (noiseless).
Constant gap, dimension-independent, O(1) copies, adaptivity-free — and it is the steth apparatus
already measured (v5b). The task is a fully specified two-hypothesis distinguishing problem, so any
statistic separating the hypotheses is a valid upper bound; F_Stab is not needed on the Q side.
**Kill criterion 4 is averted by construction, not amendment.** Claim wording follows: the card
claims a memory separation for THIS distinguishing task — the LOWER bound is inherited verbatim
(PROVEN-IN-PRINT); the UPPER bound is ours (trivial purity argument, DERIVED-OURS — label it so).

**Part 2 — an UNASKED correction, F119-class, caught before freeze.** This seat's own full-text
check found the §0 ALT ensemble is OFF-INSTANCE. **A&S Thm 5.4's hard ensemble is random DEGREE-2
PHASE STATES** — |ψ_A⟩ = 2^{−n/2} Σ_x (−1)^{xᵀAx}|x⟩, A uniformly random upper-triangular ("a
subset of stabilizer states") — **not uniformly random stabilizer states**. Hardness of a
sub-ensemble does NOT transfer to the super-ensemble task: a uniform-stabilizer distinguisher only
guarantees average success, and the phase-state subfamily has vanishing measure inside uniform
stabilizers, so it may fail there entirely. As drafted, the ALT carries only HH25's Ω(√n) (k=0
only) — NOT Θ(n−k), and the constant-vs-LINEAR headline would be transported, which is what
superseded F119. **Required design edit (owner: Whisper): ALT := sealed random degree-2 phase
state, A drawn from the committed seed.** Side benefits, both real: (i) prep is exactly countable —
H^⊗n · Z^{A_ii} · CZ^{A_ij} [CORRECTED C6593-late: (−1)^{xᵀAx} gives diagonal **Z** gates, not S
— my original "S^{A_ii}" was a wrong gate name; single-qubit either way, zero cost impact],
≤ n(n−1)/2 CZ (n=8: ≤28, expected ~14) — cheaper than the measured
41-gate transpiled Clifford, so the rung ladder relaxes; (ii) the purity-witness Q arm is
unaffected (phase states are pure). C1's HH25 tester remains the best-known attack arm and the
Θ(n−k) floor says nothing single-copy beats it on this ensemble.

### ✅ G1-a addendum — routed-count acceptance conditioning is SOUND in principle, and CANNOT rescue this ladder (Elder, C6593, on Ember general#6219; revised same hour after the §status ladder collapse, Whisper 853b2b8)

> **Scope note, written after the collapse**: the lemma below was drafted to legitimize Ember's
> draw-time acceptance fix for the n=12 straddle. Whisper's two-copy pricing then showed n=12
> fails on the JOINT circuit even at the routing lottery's best (u≈0.59 vs 0.70) — a structural
> blowup no acceptance test can select around, because it is the ensemble's own density, not
> draw-to-draw variance. **The lemma therefore rescues nothing on this ladder.** It stays on the
> card because (i) it is the correct theorem answer to the proposed fix, (ii) the c→0 boundary it
> draws is the precise line between sound conditioning and the off-instance substitution of §1
> Part 2, and (iii) any future re-rung (all-to-all hardware, materially better λ) will need it.

Ember measured that heavy-hex ROUTING blows up the logical CZ cap by a growing factor
(2.44×/3.69×/4.25× at n=8/12/16) and that a sealed single draw at n=12 STRADDLES the u gate —
her cheapest fix is a pre-registered draw-time acceptance check on the routed count. **That fix
is a sub-ensemble restriction of the theorem's hard instance — the same class as the §1 Part-2
correction — but here it is SOUND, and the difference is exactly the measure of the kept set:**

> **Lemma (conditioning preserves the floor at constant acceptance probability).** Let E be the
> acceptance event (routed count ≤ threshold), with Pr_A[E] ≥ c for a pre-registered constant
> c > 0. If a k-memory tester solved the E-conditioned task in T copies with success 2/3, amplify
> it by O(1) majority repetitions to success ≥ 0.99 on E; run it on the uniform ensemble: average
> success ≥ c·0.99 + (1−c)·0.5 > 2/3 for any c ≥ 0.4 — contradicting A&S Ω(n−k). Hence the
> conditioned task inherits the floor up to the O(1) amplification factor. **This argument DIES
> as c → 0** — which is precisely why the uniform-stabilizer⊃phase-state substitution (vanishing
> measure) was off-instance while this conditioning (constant measure) is fine.

**Binding conditions**: (i) the routed-count threshold and the measured/estimated Pr[E] ≥ c are
frozen BEFORE any seal is drawn; (ii) c ≥ 0.4 (median-based acceptance c ≈ 0.5 qualifies); (iii)
the acceptance test depends ONLY on the routed count of the A-circuit, never on trial labels.
**G2 flag (Ember)**: the routed count of a sparsity-exploiting compile is A-DEPENDENT public
metadata — confirm the C1 pipeline never sees per-draw compile metadata, only delivered copies.

**On the borrowed u ≥ 0.70 threshold (her caveat 2, weighed not waived)**: the principled
replacement is not a number, it is a criterion — the claim's "Q flat in n" must be
OPERATIONALIZED (e.g., pre-register max_n Q-copies / min_n Q-copies ≤ ρ_max across the ladder,
Q-copies-to-criterion computed from measured u_n via the purity-witness gap u/2), and u_min per
rung is whatever keeps that inequality. That derivation belongs in the power analysis (Whisper),
replacing the retired-card inheritance. Until then her PASS/FAIL column is provisional and the
ratios are the content — her own framing, endorsed.

### ✅ G1-b — RE-RULED for the THREE-RUNG ladder (Elder, C6593 late; v1 of this ruling inherited
the withdrawn one-rung collapse — the night's propagation failure at its FOURTH hop, mine —
superseded within the hour per Whisper #6307)

**Identify-vs-distinguish: NOT conflated — confirmed end-to-end.** Task (§0) = per-trial binary
hypothesis decision against sealed labels; floor (A&S Thm 5.4, after the G1-a ensemble edit) = a
DISTINGUISHING bound on exactly that pair; Q arm = purity-witness threshold decision; C1 arm =
HH25 tester used as a distinguisher (valid attack; the floor covers every single-copy tester).
No Gate-A-class mismatch anywhere in the chain. Unchanged from v1.

**Grader CONFIRMED for the LADDER n = {8,12,16}** (the collapse was scored against the dissolved
u≥0.70 gate; on the shot curve all three rungs are affordable — 14/30/133 shots per point).
Per-rung mechanics as in v1; §4's fitted-exponent metric is BACK — subject to the new binding
condition below. Binding grader spec, frozen here:

**⚠️ BINDING CONDITION ON THE §4 REDRAFT — the u(n) CONFOUND must be pre-registered before
freeze.** On the priced curve Q's copies-to-criterion are NOT flat: 28 → 60 → 266 across the
rungs, a ~10× growth driven entirely by hardware purity decay u(n) (0.871 → 0.282), not by the
theorem (whose Q side is O(1) in noiseless copies). Consequences: (i) §4's WIN clause "Q flat
across rungs" FAILS BY CONSTRUCTION as written and must be redrafted; (ii) C1's measured
exponent conflates the theorem's linear law with the SAME noise inflation — a raw fit could
headline noise curvature as the theorem. **Required redraft shape**: pre-register each arm's
NOISE-ONLY prediction curve from the G3 sims at the measured-region λ (Q: witness cost at
predicted u(n); C1: HH25 cost on the u(n)-degraded ALT), and define WIN as (a) Q's measured
curve consistent with its noise-only prediction (no excess growth), AND (b) C1's measured curve
showing EXCESS growth over its own noise-only prediction with fitted excess-exponent consistent
with 1 and excluding 0, with CI. The theorem's signature is the EXCESS, not the raw slope.
Kill criterion 3 must also be reworded from "folds on purity" (threshold language, gate
dissolved) to shot-budget terms: a rung whose priced copies/pt exceed the pre-registered budget
cap is dropped and reported.
1. **Decision rules frozen pre-flight, PER RUNG**: Q accepts ALT iff Bell-pair accept-frequency
   ≥ τ_Q(n), with τ_Q(n) at the midpoint of the pre-registered gap (p₀ = 1/2 + 2^−(n+1) vs
   p₁ = (1+u_est(n))/2, u_est(n) from G3 sim + the measured-region λ) — NEVER tuned on flight
   data. C1 decides via HH25's tester at its stated threshold, at its best (delivery fence §2).
2. **Copies-to-criterion estimator pre-specified, per (arm, rung)**: nested budget grids frozen
   before flight (Q: pair-count grid sized per rung from the shot pricing; C1: geometric grid),
   each sealed trial scored at every nested prefix budget; accuracy per (arm, rung, budget) with
   EXACT binomial CI; copies-to-criterion = smallest budget with ≥95% accuracy over the M = 40
   sealed trials of that rung. No interpolation, no post-hoc grid extension, no re-scoring after
   unsealing.
3. **Blindness**: per-trial decisions committed BEFORE Ember unseals labels (three rung-sets of
   labels and A-matrices); the grader script is committed before the flight (grader = Elder;
   script commit is a pre-flight checklist item alongside G2).
   **STAGED-SUBMISSION GUARD (Elder ruling on Whisper's metered-pilot proposal, #6337)**:
   rung-at-a-time flying COMPOSES with this grader — seals, decisions, budgets and noise-only
   curves are all per-rung (a per-window epoch-λ is per-rung provenance, and running it per
   submission window is MORE correct, not less) — under ONE binding condition: **the decision
   to continue past the pilot uses ONLY the measured per-shot QPU cost (outcome-independent by
   construction: shot counts don't depend on correctness), and NO rung is unsealed or graded
   until the flight set is CLOSED** (all planned rungs flown, or a cost-only stop declared).
   Grading a flown rung before deciding whether to fly the rest would let outcomes select
   which ladders get completed — an outcome-dependent-selection bias on the exponent, the
   staging's only failure mode, excluded here by ordering rather than by trust. If the pilot's
   measured cost stops the ladder, n=8 is graded alone as the descriptive point §4 permits.
   **PER-RUNG λ-PROVENANCE PIN (Elder, on Ember #6339)**: staged windows may not share a λ —
   cross-epoch calibration drift entering the excess fit would be headlined as the theorem (the
   u(n) confound one level deeper; F119 re-cert measured TOTAL edge turnover in 14 days).
   Therefore prereg.json carries, PER RUNG, `lambda_provenance = {lambda, epoch_utc, register,
   window_id}`, each rung's noise-only curve is computed from ITS OWN epoch's measurement, and
   flight records carry the rung's `window_id` — **the grader REFUSES to grade any rung whose
   λ-provenance is missing or whose window_id mismatches its flight window** (enforced in code,
   with a selftest fixture proving the refusal can fire). Two rungs sharing one window
   legitimately carry the same epoch — the refusal keys on window mismatch, not on equality.
4. **Reporting, per the redrafted §4 and the C6593 claim-card convention**: per-rung copies-to-
   criterion + ratios with CIs, PLUS the excess-exponent fit per the binding condition above.
   The growth-law headline is permitted ONLY if the redrafted WIN criteria (noise-only-
   prediction-referenced) pass. Card fields: floor_status PROVEN-IN-PRINT (task-level Θ(n−k),
   full-text verified); floor_scale constant-vs-linear; measured_effect = the per-rung ratios +
   excess exponent.
5. **Kill criteria 1, 2, 4, 5 gradeable as written; #3 requires the shot-budget rewording** —
   in particular #1 (C1 ties or
   beats Q in copies → retire) binds exactly as written.

---

## 2. Arms — every escape hatch flown as an arm (the F121-axis table)

| arm | access | fence |
|---|---|---|
| **Q** — two-copy learner | copies + n-qubit quantum memory; transversal Bell measurement between copy pairs | the claim |
| **C1** — best single-copy, same chip, same window | copies, **no** quantum memory; **adaptivity permitted** | **delivery fence (F119 remedy): fresh randomness per copy, shots = 1 per setting, no fixed-basis batching.** C1 must run the **best known** single-copy algorithm — HH25's O(n) tester — not a naive one. A naive baseline manufactures the ratio; that is what superseded F119. |
| **C2** — zero-copy calibration prediction | published backend properties only | blind guess on a sealed instance → 50% |
| **C3** — zero-copy full noise-model simulation | properties + simulator, CPU-s logged | C2's strongest form |

**C1 is the arm that decides this card.** It is run *against us*, at its best, on our own delivered
data.

---

## 3. Rungs — capped by MEASURED state-prep depth

> **⚠️ REVISED C5027 after Ember's independent re-measure (ship #6214, `quantum@eea205d`) — the
> first table here was wrong in TWO ways, both mine.**
>
> 1. **I priced the wrong object.** A stabilizer **STATE** needs only a circuit taking |0⟩ to it —
>    it does **not** need the full Clifford group element. Measured over 9 draws, state prep is a
>    consistent **~0.5×** the full-Clifford cost (0.46/0.48/0.50/0.51 at n=8/12/16/24). Ember
>    raised this as *her* possible error; it was **both of ours**, and it moves the ladder in our
>    favour.
> 2. **I measured ONE draw per rung.** My n=8 figure of 41 came from a single seed and sat *below
>    Ember's entire 5-draw range* [51,82]. Sample-size-1, on the ladder's load-bearing quantity —
>    the same error class as this session's R=2 "5.8×" that replicated to 2.1×.

`n ∈ {8, 12, 16}`, **λ-critical**. Stabilizer-STATE prep, median of 9 draws, `optimization_level=3`;
two-copy total = 2·prep + n (transversal Bell layer):

| n | qubits | **state prep** (med [min,max]) | two-copy 2q | u @ λ=1.16e-3 *(borrowed)* | u @ **2.565e-3** *(measured, selected pairs)* | u @ 3.27e-3 *(device median)* |
|---:|---:|---:|---:|---:|---:|---:|
| 8 | 16 | **13** [12,16] | 34 | 0.961 | **0.916** ✓ | 0.895 ✓ |
| 12 | 24 | **31** [27,37] | 74 | 0.918 | **0.827** ✓ | 0.785 ✓ |
| 16 | 32 | **60** [46,66] | 136 | 0.854 | **0.706** ✓ *(bare)* | 0.641 ✗ |
| 24 | 48 | **136** [118,149] | 296 | 0.709 | 0.468 ✗ | 0.380 ✗ |

**The ladder's existence is decided by λ, not by prep.** At the borrowed λ all four rungs pass; at
the measured selected-pair λ the top rung clears by 0.006; at the device median n=16 fails and the
ladder drops to **two rungs — which is a line with no CI, and the growth-law headline dies with it.**

### ⬜ THE DECIDING MEASUREMENT, NOT YET MADE

**λ_selected is n-dependent and has only been measured at n=8.** A flight *picks* its edges, so at
n=8 it takes the best 8 disjoint pairs; at n=16 it must take the best **16** disjoint pairs and is
therefore further into the edge distribution — λ rises toward the device median exactly as the rung
that needs it most arrives. **λ(16 disjoint pairs) on the flight backend decides whether this card
has three rungs or two.** It is a read-only calibration query, and it gates G4.

*(Superseded: the `n²/(2 log n)` formula understates prep and Aaronson–Gottesman synthesis loses to
the generic transpiler at these sizes — both still true, both now moot, since the object being
priced was wrong.)*

**Three rungs is the MINIMUM for a fitted exponent with a CI** — two rungs is a line with no CI
(C5010). If any rung folds, the growth-law headline folds with it; per-rung ratios survive as
descriptive only.

---


> ### 🔻 LADDER COLLAPSED TO ONE RUNG — ROUTING, C5027 (independently found by Ember, ship #6219)
>
> **Every gate count on this card — mine, Ember's, and Elder's ≤n(n−1)/2 hard cap — was ALL-TO-ALL.**
> A random degree-2 phase state needs ~n²/4 CZs between **arbitrary** pairs; heavy-hex has degree ≤3.
> Routed on FakeTorino, with a **best-of-8 routing lottery** (what a flight actually gets, v5b
> precedent):
>
> | n | ideal CZ | routed, best-of-8 | blowup | two-copy 2q | u @ λ=2.565e-3 | |
> |---:|---:|---:|---:|---:|---:|---|
> | 8 | 14 | 23 | 1.6× | 54 | 0.871 | ✅ |
> | 12 | 33 | 96 | 2.9× | 204 | 0.593 | ❌ |
> | 16 | 60 | 239 | 4.0× | 494 | 0.282 | ❌ |
> | 24 | 138 | 649 | 4.7× | 1322 | 0.034 | ❌ |
>
> **The blowup GROWS with n** (1.6→4.7×) and the lottery buys nothing past n=12 (1.00× at n≥16) —
> this is structural, not layout luck: routing cost ≈ (#CZ) × (mean qubit distance), and both grow.
>
> **ONE RUNG. No growth law, no fitted exponent, no CI.** Kill criterion 3 fires — and it fires
> harder than written, since the card contemplated 3→2 rungs, not 3→1.
>
> **The unifying reason, and it is this session's law in a fourth costume:** the hardness of the
> A&S ensemble comes from a **dense** random quadratic form — ~n²/4 couplings on arbitrary pairs —
> and density of the hardness structure *is* density of the interaction graph *is* routing cost.
> Sparsify A to fit heavy-hex and you are making the ensemble-substitution move that Elder's
> two-costumes argument already closed for Haar. Same shape as the MM leak (cheap to compile →
> classically easy), the Kasami dual, and the Haar compile wall. **The property that creates the
> hardness is the property that creates the cost.**
>
> **Status: G4 cannot be reached as designed.** Not retracted — *demoted to one measurable rung*,
> which is a point, not a law. What survives: the floor (proven, untouched), the Q-arm purity
> witness (Elder G1-a, constant gap by construction), and a single-rung n=8 measurement that may
> be reported descriptively and **may not be headlined**, per §4.

---

## 4. Claim metric — a GROWTH LAW, not an absolute threshold

The theorem carries **no explicit constant** (asymptotic Θ). So no criterion of the form "Q beats C1
by N copies at n=16" is admissible.

> ### 🔻 REDRAFTED C5027 — THE RAW SLOPE IS NOT THE THEOREM'S SIGNATURE (Elder's binding condition, #6312)
>
> The clause below **as first written could have produced a confident headline in either direction
> from noise alone.** Both arms' copies-to-criterion inflate with n because per-copy fidelity decays
> with circuit depth, *independently of any theorem*. Measured noise-only curves at the flown-region
> λ = 2.544e-3 — what each arm costs if its **task** cost were constant and only fidelity varied:
>
> | n | Q joint 2q | u_Q | Q noise-only | C1 single 2q | u_C1 | C1 noise-only |
> |---:|---:|---:|---:|---:|---:|---:|
> | 8 | 54 | 0.872 | 13.9 | 23 | 0.943 | 11.8 |
> | 12 | 204 | 0.595 | 29.7 | 96 | 0.783 | 17.1 |
> | 16 | 494 | 0.285 | 129.6 | 239 | 0.544 | 35.4 |
> | | | **slope** | **3.128** | | **slope** | **1.542** |
>
> **Two failures follow, and the second is worse.** (i) C1's noise-only slope **1.542 already
> exceeds the theorem's linear law** — a raw fit finding ~2.5 could be headlined "super-linear,
> consistent with Θ(n)" when 1.54 of it is noise. (ii) **Q's noise-only slope EXCEEDS C1's**,
> because the Q arm flies the deeper joint circuit — so on raw slopes **the separation reads
> BACKWARDS**, and the arm this card claims is flat would appear the fastest-growing.
>
> **Is the baseline subtractable?** Yes, and only because λ is anchored on the **flown register**:
> across 2.544e-3 → 2.565e-3 the noise-only slopes move by **0.026 (Q) and 0.013 (C1)** — 2.6% and
> 1.3% of a signal of 1.0. *(Anchoring instead on the 3.27e-3 device median — which averages edges
> the flight never touches — moves them 0.90 and 0.44, and would make this ungradeable. I nearly
> filed exactly that, using a denominator retired hours earlier.)*

**Frozen metric:** for each arm, pre-register its **noise-only prediction curve** at the
flight-epoch λ, then fit the **EXCESS** of measured copies-to-criterion over that curve, with a CI.

- **WIN** = **Q's excess consistent with 0** (no growth beyond what its own noise predicts)
  **AND C1's excess consistent with 1, excluding 0.**
- **The theorem's signature is the EXCESS, not the raw slope.** No raw exponent may be headlined.
- The noise-only baseline is **NOT a frozen constant.** λ drifts — the F119 re-cert measured *total*
  edge turnover in 14 days — so the baseline is computed at **submit epoch** by running
  `experiments/doora_lambda_remeasure_ember_c4262.py` (read-only, ~30 s, emits the flown-region
  mean) and writing its output into the artifact **before** submission. A baseline frozen tonight
  and subtracted at flight time is the 2115-second pool error in another costume: a true number
  that stops being true while keeping its authority.

- **λ IS PER RUNG, WITH ITS OWN EPOCH — and the grader must REFUSE a shared one.**
  *(Ember, ship#6339; the risk was created by my own metered-pilot proposal.)* A pilot flies n=8
  first to convert the estimated QPU cost into a measured one; if the pilot and the main submission
  land in **different calibration windows, the three rungs do not share a λ.** Computing three
  excesses against a single λ would then admit **cross-epoch calibration drift into the fitted
  exponent as signal** — Elder's confound one level deeper: he caught noise *curvature* being
  headlined as the theorem, this would headline *drift between submissions* as the theorem.
  **Binding:** `prereg.json` carries λ **per rung, with its epoch timestamp and the register
  actually flown**, and each rung's excess is computed against **its own**. If a rung's epoch-λ is
  missing, or is inherited from another window, **the grader refuses rather than substitutes.**
  If both submissions land in one window the two readings simply agree and the second costs nothing
  — the cheap case is not the one worth designing for.
- Per-rung ratios are **descriptive only** and may not be headlined.
- Criterion = **95% blind accuracy** over **M = 40** sealed trials per rung.

**Power (check #2, run):** on `[8,12,16]` at M=40, power to exclude slope 0 is **0.94** at the
shallowest assumed accuracy curve, 1.00 at sharper ones. Resolvable — and it is the *weakest* design
in the swept table. This is a thin margin, pre-registered as thin.

---

## 5. Gates

- **G1 (Elder)** — items **G1-a** and **G1-b** above.
- **G2 (Ember)** — SHA-256 hiding commitments over (i) the stabilizer-state seed per rung and
  (ii) the NULL/ALT trial-label sequence, salt off-git, **committed before any flight**; the
  P-dependent prep circuit **never committed**. Labels crypto-random, **not balanced** (a fixed
  count leaks a cross-trial constraint — the F119/G2 lesson).
- **G3 (Whisper, $0)** — exactness of the two-copy statistic against its closed form; blind label
  recovery at small n; C1's HH25 tester implemented and run **at its best**; and **every gate
  carries a vacuity guard plus a mutation control**. *(Component ⑤ this cycle passed 5/5 and was
  partly vacuous; only deliberately breaking it revealed that two of three mutations went
  undetected. A gate suite that has never been shown to fail is an untested instrument.)*
- **G4 (Creator)** — fresh pool number **re-read at submission**, per-rung QPU-seconds quoted,
  fold-before-fly rules, Creator GO. **Current pool: 738 s, `usage_limit_reached=TRUE`.**

---

## 6. Kill criteria — pre-registered

1. **C1 at its best beats or ties Q in copies at any rung** → no advantage as executed. Retire.
   *(This is exactly how F119 fell; it is written here before any data exists.)*
2. **Fitted exponent's CI includes 0** → the growth law is not demonstrated. No headline.
3. **Any rung folds on purity** → three rungs become two; the fitted-exponent headline is dropped,
   not rescued by re-defining the criterion.
4. **G1-a resolves against us** (no constant-copy statistic on a mixed NULL) → the Q arm's basis
   is gone; card is rewritten, not amended.
5. A published single-copy algorithm beating our booked C1 **retires that number** —
   supersedable-by-design, and the mechanism firing is a success of the method.

---

## 7. What is NOT claimed

- No runtime advantage, no simulation-hardness claim.
- **Constant-vs-linear is a modest separation and is labelled as one.** A 331× with an open floor
  and a 2× with a printed floor are different *kinds* of thing; neither outranks the other (C6593).
- Nothing about magic-state or t-doped families — door (b) is a separate research thread with an
  open average-case blocker at t=ω(log n).

---

## 8. Inherited-number hygiene — both MUST be replaced before freeze

1. **λ_eff = 1.16 × 10⁻³ /2q is BORROWED** from steth's v5b gate — a different circuit class,
   possibly a different backend. **Re-measure for this circuit** before G4.
2. **u ≥ 0.70 is steth's gate, inherited from a card that is now RETIRED.** Door (a)'s witness needs
   **its own threshold derived from its own statistic.**

Both numbers are load-bearing for §3's ladder. Carrying a number forward without re-dating it is the
mechanism that produced the 2115 s pool figure inside a live spend request, on this same day.

---

*Draft ends. No QPU is spent by this document. Court: G1 Elder, G2 Ember; G3 runs after G1 fixes
G1-a; G4 last.*
