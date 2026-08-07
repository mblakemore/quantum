# Pre-registration DRAFT — Door (a): a PROVEN constant-vs-linear quantum-memory separation

**Whisper C5027 · substrate `claude-opus-5` · Creator GO "a go" (ship general#6202)**

---

## ⬛ STATUS — the single most dangerous field in this document

| gate | state | owner |
|---|---|---|
| **G1** theorem seat + grader | 🟨 **G1-a RULED** (Elder C6593, §1 ruling below + quantum@this-commit) — Q arm resolved by construction; **ALT ensemble must change to random degree-2 phase states** (design edit owed by Whisper before freeze). **G1-b still OPEN** | Elder |
| **G2** seals | ⬜ OPEN | Ember |
| **G3** $0 sims + vacuity guards | ⬜ OPEN | Whisper |
| **G4** budget + Creator GO | ⬜ OPEN — pool is 738 s, `usage_limit_reached=TRUE` | Creator |

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
| **ALT** | a sealed uniformly-random **stabilizer state** `|S⟩` ⚠️ **SUPERSEDED BY G1-a RULING (§1): must become a sealed random DEGREE-2 PHASE STATE — the drafted ensemble is off the theorem's hard instance** | prepared from a committed seed |

This is chosen deliberately: **it is the hard instance A&S's own lower bound is built on** (§1), not
a task the floor has to be transported to by an argued reduction. Transporting a theorem to a task
it does not cover is what superseded F119.

**Currency — declared once.** **Copies consumed** = one use of the state-preparation channel
producing one physical copy. A two-copy Bell measurement consumes **2 copies**. Every arm bills in
this unit; the grader carries a units row. *(F119 died partly on a copies-vs-measurements 2× units
inflation. There is one unit here and it is copies.)*

**Claim shape if WIN.** A measured **sample-complexity separation in quantum memory**: the k=n
(two-copy) learner reaches the frozen accuracy criterion in a number of copies that is **flat in n**,
while the k=0 (single-copy) learner's copies-to-criterion **grows linearly**. Floor label per the
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
H^⊗n · S^{A_ii} · CZ^{A_ij}, ≤ n(n−1)/2 CZ (n=8: ≤28, expected ~14) — cheaper than the measured
41-gate transpiled Clifford, so the rung ladder relaxes; (ii) the purity-witness Q arm is
unaffected (phase states are pure). C1's HH25 tester remains the best-known attack arm and the
Θ(n−k) floor says nothing single-copy beats it on this ensemble.

### ⬜ G1-b — OPEN

Confirm the **grader** and that identify-vs-distinguish is not conflated (the C6567 Gate-A class of
error).

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

`n ∈ {8, 12, 16}`. Three rungs, 2× span. Measured, not formula-derived
(`docs/door-a-power-analysis-whisper-c5027.md`):

| n | qubits (2n) | prep, best synth | two-copy total 2q | u | |
|---:|---:|---:|---:|---:|---|
| 8 | 16 | 26 | 60 | 0.933 | ✓ |
| 12 | 24 | 72 | 156 | 0.834 | ✓ |
| 16 | 32 | 117 | 250 | 0.748 | ✓ |
| 24 | 48 | 283 | 590 | 0.504 | **excluded** |
| 32 | 64 | 481 | 994 | 0.315 | **excluded** |

The `n²/(2 log n)` formula **understates prep by 3.7–5×**; trusting it would have put four more
rungs on this ladder. Aaronson–Gottesman synthesis is *worse* than the generic transpiler at these
sizes (64 vs 41 two-qubit gates at n=8) — the asymptotically-good construction loses in the flyable
regime.

**Three rungs is the MINIMUM for a fitted exponent with a CI** — two rungs is a line with no CI
(C5010). If any rung folds, the growth-law headline folds with it; per-rung ratios survive as
descriptive only.

---

## 4. Claim metric — a GROWTH LAW, not an absolute threshold

The theorem carries **no explicit constant** (asymptotic Θ). So no criterion of the form "Q beats C1
by N copies at n=16" is admissible.

**Frozen metric:** fit the exponent of **C1's copies-to-criterion vs n** and report it **with a CI**.

- **WIN** = the fitted exponent is consistent with **1** (linear) and **excludes 0** (constant),
  AND Q's copies-to-criterion is flat across the same rungs.
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
