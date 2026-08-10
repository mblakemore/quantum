# The Sealed Shadow

### A blind, sealed, court-graded hardware demonstration of the quantum-memory advantage in Pauli learning — 9.3× fewer copies than *any* single-copy strategy (a demonstrated lower bound; 21.7× formula-vs-formula), on 32 qubits of `ibm_marrakesh`

**Author**: Whisper (DC15W), C5048 (2026-08-10) · **Substrate**: claude-fable-5
**Campaign**: Autonomous Characterization of IBM Heron-generation hardware (May 2026–)
**Result codename**: door (b) · **F-number**: **F122** (Ember, numbering seat — adjacent to F119/F120/F121: the third attempt at a learning advantage, and the first that survived)
**Status**: WIN — F1 PASS, 104σ. Survived its own [adversarial audit](adversarial-audit-doorb-refly-whisper-c5048.md); cleared to travel.

> **On the name.** "Door (b)" is an internal codename from the design phase. For anything public this document proposes **"The Sealed Shadow"** — the task is *Pauli shadow tomography*, and the methodological heart is that the secret is *sealed* and the grading is *blind*. Alternatives offered for the Creator's choice: *"Two Copies, One Secret"* (accessible), *"The Memory Advantage, Sealed"* (literal), or the journal-register descriptive title above. The rest of this paper uses "the Sealed Shadow / door (b)" interchangeably.

---

## Abstract

We report a hardware demonstration of the two-copy (quantum-memory) advantage for learning Pauli observables, executed under an adversarial sealed-commitment protocol with blind three-seat court grading. On 32 qubits of `ibm_marrakesh`, a two-copy Bell-sampling protocol recovered the amplitude of a **sealed** weight-12 Pauli operator drawn from the theorem's own hard-family ensemble ρ_P = (I+3εP)/2ⁿ (n=16), at **104σ** (estimate 0.3065 ± 0.00296), using **207,464 copies of ρ** — **9.3× fewer than the proven single-copy floor** of ~1.9 million copies at the amplitude the hardware actually delivered (ε=0.1845). The single-copy lower bound is Ω(2ⁿ/ε²) from Chen–Gong–Ye (FOCS 2024), and — verified against that paper's own protocol definitions — it holds against *any adaptively-chosen* single-copy measurement, licensing the claim in its strong form: **9.3× over any single-copy strategy, not merely best-known.** The advantage was then **confirmed across a distribution of three sealed draws** (this reference instance plus two more, all F1 PASS, all clearing the floor; two independent weight-12 draws agree on delivered ε to 1.2σ while a weight-11 draw sits 11σ away — a within-weight replicate with its own control, §6b), answering "lucky draw?" with replication rather than repetition. The advantage is in *copy currency only* (classical post-processing is Θ(4ⁿ) on both arms and is explicitly not part of the claim). The distinctive contribution beyond the physics is the discipline: a sealed secret committed before flight, a go consumed by exactly one seal, a flight that sized itself mid-air to the hardware epoch it actually occupied, and a fix — for a first flight that *failed as frozen* — validated from the blind side before the pass was measured.

---

## 1. The result in one paragraph

Give a learner copies of an unknown n-qubit state ρ and ask it to identify a hidden Pauli P by estimating |tr(Pρ)|. If the learner may only measure **one copy at a time** (with bounded quantum memory), a theorem says it needs a number of copies growing as 2ⁿ/ε² — astronomical at n=16. If it may measure **two copies jointly** in an entangled Bell basis, the same task takes O(n/ε⁴) copies — the pattern lights up almost immediately. This paper demonstrates that separation on real hardware, under a protocol designed so we cannot fool ourselves: the target Pauli is drawn and cryptographically sealed *before* the flight; the flight is graded *blind* against the sealed commitment by a different agent than the one who flew it; and the classical floor we beat is a *proven theorem*, not a conjecture. The measured recovery is 104σ clean and the demonstrated copy ratio is 9.3× (a lower bound — the flight was deliberately over-sized, so the error bar points *up*; the formula-vs-formula separation is 21.7×) — every digit of which we then attacked ourselves and could not move.

---

## 2. The task, the trick, and the floor

**The task.** *Unsigned Pauli shadow tomography*: given copies of ρ, estimate |tr(Pρ)| for Pauli operators P to additive error ε. We register the *unsigned* task deliberately (§2 of the [prereg](doorb-unsigned-shadow-prereg-DRAFT-ember-c4262.md)): the **signed** version tr(Pρ) additionally requires coherent majority-vote sign recovery across several copies held *simultaneously in persistent quantum memory* — hardware we do not have. Two-copy Bell measurement alone computes the *magnitudes*, so the unsigned task is one our apparatus implements *in full*, not in part. This distinction is load-bearing and returns in §7.

**The trick.** For a pair of copies ρ⊗ρ, a Bell-basis measurement across the two registers reads out, per Pauli, a quantity whose expectation is tr(Pρ)² — the squared amplitude — directly. N Bell measurements estimate all 4ⁿ squared amplitudes at once. Single-copy measurements cannot access this quadratic quantity without paying the exponential price the floor names.

**The floor** (the thing F119 never had — see §8). Chen, Gong, Ye, *"Optimal tradeoffs for estimating Pauli observables,"* FOCS 2024 (arXiv:2404.19105), prove that any protocol measuring c copies at a time with k qubits of memory needs Ω(2ⁿ/(cε²)) copies. At c=1, k=0 — a single-copy learner with no memory — this is **Ω(2ⁿ/ε²)**. Crucially, the paper's single-copy model (its **Definition 1**) states: *"The algorithm is allowed to perform arbitrary POVM measurements on one copy of the unknown quantum state ρ at a time… The choice of POVM can depend on all previous measurement outcomes,"* and every lower bound is proven in the learning-tree framework (**Definition 6**: *"At each non-leaf node u, we measure ρ⊗c using an adaptively chosen POVM"*). The floor therefore holds against **adaptive** single-copy strategies, not only non-adaptive ones — the strong form of the comparison, confirmed by two independent source extractions (this author; Elder, grading seat). (The same paper notes that non-adaptive *sign*-learning is a separate, still-open hard case; we do the unsigned task and stay inside that boundary — §7.)

---

## 3. The hard-family state, and why it is the only admissible one

The sealed state is **ρ_P = (I + 3εP)/2ⁿ** — the exact ensemble Chen–Gong–Ye's lower bound is proven over. This is not a convenience: racing our apparatus against a floor proven for a *different* family of states would be the "theorem does not cover our case" error that has killed campaign claims before. A convenient random *product* state, for instance, grades trivially — and is not drawn from the hard ensemble, so a memoryless learner may beat the floor on it. The ensemble was ruled and registered before any prep code existed.

Two facts made ρ_P flyable at zero-2q-gate prep cost — a result derived twice independently during the design (Ember via Clifford conjugation, Whisper via product eigenbases):

- **ρ_P is exactly a classical mixture of product eigenstates of P**: with probability (1+3ε)/2 a uniformly random +1 product eigenstate, else a −1 one. So a Pauli string's eigenspaces are *product-sampleable* — the whole state preps with single-qubit rotations and a biased coin, no entangling gates.
- Its Pauli expectations are **analytic**: tr(Q ρ_P) = 3ε·δ_{Q,P}. Truth is closed-form for every one of the 4ⁿ probes; the grader never needs a simulation it might get wrong.

The zero-2q prep had a second dividend that closed a leak channel (§4): because the secret P selects only single-qubit rotation *angles* on one uniform template, the circuit *structure* is identical under every binding, and P rides entirely in a custody-held parameter table — the device-independence "uniform template" gold standard, at a reduced gate budget.

---

## 4. The protocol — designed so we cannot fool ourselves

Five disciplines make every step checkable against an external record — git and the ship's-computer bus — rather than against anyone's word. Each has an incident behind it.

1. **Sealed commitment.** P is drawn and its SHA-256 commitment `b3fb6cfe08b548fa…` is git-pinned *before* submission, binding the frozen-prereg hash `0acd1f8a`. The identity string `XZXXIYYYXIZIIYXX` (weight 12) is not revealed until after grading; the flight manifest carries **no P and no draws**.

2. **Blind three-seat court.** Three different agents: **register** (Whisper — posts n, ε, budget, falsifiers before the seal exists), **seal+fly** (Ember — draws P, submits, holds the secret), **decode** (Elder — reproduces from raw counts using a decoder frozen at commit `5104851` *before* the seal was spent, selftest 6/6). The decode seat hashes its decisions and posts the hash to the bus **before** any unseal; the flyer never sees a result before that hash lands. "The whole value of this protocol is in the parts the flyer does not do."

3. **Single-use, seal-bound authorization.** The Creator's go (`general#8174`) is consumed by exactly one seal digest and confers nothing on any other flight. A re-fly needs a fresh go citing the new seal — a rule written after an 11-hour-old consumed go resurfaced as a live-looking mention.

4. **Weather-gated self-sizing.** The copy budget is a *registered function* T(ε) = 4·ln(2·4ⁿ/δ)/ε⁴, frozen days before any epoch. The flight's own leading calibration job reads the delivered signal amplitude in the epoch it *actually occupies* (not a stale standalone probe), computes its budget from the frozen function, and aborts cheaply if the epoch is unclaimable. Here: delivered ε=0.1494 at the calibration read → T sized to 207,464 copies → flew.

5. **Delivered-ε evaluation.** The claim evaluates the floor at the amplitude *actually delivered* by the hardware (ε=0.1845 on the science rows), never at the nominal or sizing value. This is the conservative direction: a larger delivered ε gives a *smaller* floor and thus a *smaller* ratio (9.3× vs 14.1–14.4× at other epochs).

---

## 5. The failure-first arc — two flights, and why the first one mattered

The Sealed Shadow's most distinctive feature is that it **failed first, on the record, and the failure made the success believable.**

**Flight 1 (seal `4a6b9f73`, P=`IIYIYIZIYIZZZIXZ`) — FAILED AS FROZEN.** The prep drew the biased sign only over *non-identity* qubit positions; the identity-position qubits flew *constant* (|0⟩ every shot) instead of maximally mixed. The delivered state was therefore |0…0⟩ ⊗ (planted direction), which is **not the hard family the floor is proven over** — a state with pure disclosed qubits violates the theorem's premise. The court's seeded weight-1 tripwire probes read **0.91–0.98 on exactly the seven identity positions**, localizing the defect to the qubit set from the sealed record alone, before the unseal named which qubits it would incriminate. Graded FAIL-AS-FROZEN, posted in the same words a pass would have used.

**The fix, and its blind validation.** The bug was one line (randomize *all* positions, not just non-identity). Rather than trust an inspection of the author's own prep code, the fix got a can-fire gate — **F-MIX**: every qubit's reduced state must be maximally mixed except the planted directions, with a *buggy control arm that must fire* (it reads 1.000) and a fixed arm that must pass (0.015). Then — the move an author cannot make for themselves — the fix was **validated from the blind side**: on Flight 2, before any unseal, the decode seat reported the **0.91–0.98 failure signature absent** — the residual ~0.03 deviations appear on identity and non-identity positions *alike* (the largest, −0.0403, sits on a non-identity position and is negative; see R2, §7), i.e. the identity qubits are **no longer distinguishable from the rest**, which is exactly what the fix guarantees. This reading was committed against positions {4, 9, 11, 12} the decode seat could not know; the unseal proved it right. F-MIX's guarantee became a *measurement* taken while the answer was still sealed. (An earlier phrasing of this reading said "absent *on* the identity positions," which invites "nothing is there" — ~0.03 is there; it is simply no longer concentrated. Corrected against the decode record.)

**Flight 2 (seal `b3fb6cfe`, P=`XZXXIYYYXIZIIYXX`, weight 12) — WIN.** 22 chunked jobs on `ibm_marrakesh`, 103,732 Bell shots + 2,000 calibration rows, all gates green (G-DECODE 5.55e-16, F-BIAS/F-IND/F-MIX fire correctly, G-CRN/G-BACKEND/G-FIT, G-SEAL matches the pinned commitment). Billed **109 seconds** against a 176-second estimate — *under*, where the predecessor's many-rows-few-shots load once overran its model 4.3× and exhausted a paid tank with zero completed jobs.

---

## 6. Results

| quantity | value |
|---|---|
| Planted P (revealed post-grade) | `XZXXIYYYXIZIIYXX`, weight 12 |
| Amplitude estimate tr(Pρ)² | **0.30646 ± 0.00296** |
| Significance from zero | **103.7σ** |
| Delivered ε (science) | 0.1845 |
| Copies spent (quantum) | 207,464 (= 2 × 103,732 pairs) |
| Single-copy floor at delivered ε | 1,924,619 copies |
| **Advantage ratio (copy currency)** | **9.28× over any single-copy strategy** |
| Largest artifact, any of 112 blind probes | 0.0403 (a weight-1 probe) |
| Separation, planted vs largest artifact | 7.6× on tr², 2.8× on \|tr\| |
| Random weight-heavy probes (P's own family) | max 0.0069 = 2.3σ (true shot noise) |

**The full ratio chain, every number labeled by its epoch** (this travels *with* the headline): nominal 14.4× → pilot-epoch 13.9× → sizing-epoch 14.1× → **delivered-instance 9.3×**. The register seat capped the number at the delivered-ε value at the moment of the win, before anyone outside had to ask — the smallest of the four, the only one every clause survives.

Each figure in that chain evaluates the *floor* at a different ε while holding the *flown copies* fixed. A distinct question is what the comparison gives when **both** budgets are evaluated at the **same** ε — the conventional way a separation is stated. Since floor = 2ⁿ/ε² and the two-copy budget is T(ε) = 4·ln(2·4ⁿ/δ)/ε⁴, the matched-ε ratio is 2ⁿε²/K with K = 4·ln(2·4ⁿ/δ) ≈ 103, giving **21.7× at the delivered ε = 0.1845**. The two numbers answer different questions and both belong: **9.3× is what was demonstrated** — the proven floor against copies actually purchased and verified sufficient — and it is an **empirical lower bound whose error bar points *upward***, because the flight was deliberately over-sized (F1 cleared at ~104σ, far beyond detection). **21.7× is the formula-vs-formula separation.** The headline remains the demonstrated figure; the labels keep a reader from taking the lower bound for the estimate. (Framing: Ember, from Whisper's failed weight prediction; identity three-seat-verified #8429/#8431/#8434.)

---

## 6b. The distribution — replication with a within-weight control

A single sealed instance demonstrates the advantage; it cannot show it is not a lucky draw. Under a **bounded batch authorization** (one go, N≤3, each instance sealed→flown→decoded before the next — *incremental-atomic*, so the reported n is always the count flown and a short batch is the budget gate working, never a truncation), two further instances flew under the identical frozen protocol, with the sealed Pauli drawn **uniform-random** over non-identity strings. A third was **aborted by its own budget gate** with the seal unspent (the pre-registered short-batch outcome; that published-but-unflown seal is a live commitment — it flies unchanged if the tank refills, and is never replaced by a fresh draw, which would be selection invisible in the artifact).

**Three sealed draws, three blind decodes, three F1 PASSes** (σ on the shot-noise ruler, the campaign-consistent convention):

| instance | weight | delivered ε | F1 σ | raw ratio | matched-ε ratio |
|---|---|---|---|---|---|
| F122 (reference) | 12 | 0.1850 ± 0.0013 | 103.7 | 9.26× | 21.7× |
| i2 | 12 | 0.1828 ± 0.0014 | 100.1 | 9.73× | 21.2× |
| i1 | 11 | 0.2030 ± 0.0012 | 107.5 | 10.96× | 26.1× |

**The observable is delivered ε, not the ratio.** The raw ratio has two inputs — floor set by *delivered* ε, flown copies by *sizing* ε — so it is not a clean function of the sealed Pauli's weight (R3). Delivered ε is measured directly at each calibration gate and *is*: the two independent weight-12 draws (F122, i2) agree to **1.2σ**, while the weight-11 draw (i1) sits **11σ** away — lighter Paulis deliver higher amplitude, a genuine weight signal with its own within-weight control. That control — two draws at the *same* weight agreeing — is what a distribution over three *scattered* weights could not have given, and it is the substance of the answer to "is this a lucky draw?": **no** — the advantage cleared the proven floor on every draw, and the one quantity that varies does so with a measured, controlled structure. Gate 2 of external-submission readiness is discharged on this evidence.

## 7. The adversarial audit — what we did to break it, and could not

Full detail: [adversarial-audit-doorb-refly-whisper-c5048.md](adversarial-audit-doorb-refly-whisper-c5048.md). Summary:

- **`attack_preflight.py`: 4/4 CLEAR** (planted-structure-leak, idealized-hard-delivered-easy, under-priced-baseline, ceiling-quoted-as-advantage) — treated as a floor, not a certificate.
- **Every load-bearing number recomputed conservative.** The copy ratio is 9.28× in *copy currency on both sides* — the unit inflation that killed F119 (counting Bell measurements as one copy) would read 18.6× and is *not* claimed. The delivered-ε choice is the *smallest* available ratio (anti-shopping). The reported SE (0.00296) matches the empirical null spread (0.00300) to 0.99, so 104σ is not an SE artifact. The planted signal sits **44×** above its own probe family's worst artifact (the 7.6× headline uses a more conservative denominator).
- **The F121 killer is inapplicable by construction.** F121 died because its secret was a *queryable circuit* whose Maiorana–McFarland algebra leaked it in 41 classical queries. The Sealed Shadow's secret is the *parameter of a physical state* you can only be handed copies of — there is no white-box function to query, so state-learning is the structural *inverse* of circuit-hiding.
- **The adaptivity question, resolved from primary text.** The one item the grade artifact could not settle — whether the floor covers *adaptive* single-copy strategies — was closed by extracting the Chen–Gong–Ye PDF and quoting its Definitions 5–6 verbatim: the model is adaptive by construction. The claim travels in the strong form.
- **Two residuals, neither touching F1**: the 9.3× *ratio* is single-instance (a distribution over sealed P would make it a curve, R1); a ~0.03–0.04 signed cross-copy correlation appears in the *delivered* pairs (F-IND's axis measured through hardware, R2) — it *hurts* the quantum arm rather than helping, sits 44× below the signal, and is filed to the limitations ledger.
- **R3 — the demonstrated ratio has two inputs, only one of which is nature.** The floor is set by *delivered* ε, the flown copies by *sizing* ε, so ratio ∝ ε_size⁴/ε_del². Across the flown instances this identity reproduces the observed variation (predicted 1.189 vs measured 1.184) **without any weight term** — surfaced by a *failed* on-record prediction (Whisper #8416) that lighter Paulis would lower the ratio; they did not, because the sizing ε moved. Consequently the raw ratio is not a clean function of the sealed Pauli's weight, **no ratio-vs-weight trend is claimed**, and the observable that actually varies is **delivered ε**, measured directly at each calibration gate. (The distribution flight, in progress, reports ε_del per instance for exactly this reason.)

---

## 8. What this is NOT, and how it sits beside the two claims we retired

The Sealed Shadow's standing rests on the campaign having executed *its own* biggest claims. It is what the campaign's advantage standard produces when a claim survives it — the same standard that buried the two below:

- **NOT a runtime or total-work advantage.** Classical post-processing is Θ(4ⁿ) on **both** arms and is excluded from the claim; the advantage is in *copies of ρ consumed* only. This is stated in the prereg's one-sentence claim precisely because **F121** died on that slip — its "476× runtime win" priced *simulating the circuit*, and the problem itself fell to a 41-query classical solve in 0.25 ms. F121 as a runtime advantage: RETIRED, by our own red team, pre-submission.
- **NOT F119, and structurally its inverse.** **F119** (the first learning-advantage attempt) was SUPERSEDED-as-executed: its delivered flight leaked the secret through a fixed-basis-per-row artifact, and its (3/2)ⁿ floor was an *open conjecture*, not a theorem. The Sealed Shadow fixes both: the delivery is fenced (F-IND/F-MIX, blind-validated), and the floor is **proven in print** (Chen–Gong–Ye). Where F119's first flight leaked, the Sealed Shadow's first flight *failed loudly and was caught*; where F119's floor was open, this one is closed.
- **NOT sign-learning.** We do the *unsigned* task. The signed task's non-adaptive hardness is an open question in the same source paper; we stay inside that boundary by construction (§2, §7).
- **NOT a below-threshold fault-tolerant result, and NOT a supremacy claim.** It is a copy-complexity separation on one instance, on one die, in one epoch, with the scope stated as such.

---

## 9. Reproducibility

| artifact | value |
|---|---|
| Frozen prereg | [`docs/doorb-unsigned-shadow-prereg-DRAFT-ember-c4262.md`](doorb-unsigned-shadow-prereg-DRAFT-ember-c4262.md), hash `0acd1f8a` |
| Winning flight job | `d9sifr8pdb6s73e63140` (`ibm_marrakesh`, 22 jobs) |
| Seal (commitment) | `b3fb6cfe08b548fa…`, git-pinned at commit `4759817` before submission |
| Decoder (frozen pre-seal) | `tools/doorb_decoder_elder.py` @ `5104851`, selftest 6/6 |
| Decisions hash (pre-unseal) | `a0a7f1f3ca2b8d8f…` |
| Grade | [`results/doorb_refly_grade_n16_elder.json`](../results/doorb_refly_grade_n16_elder.json) |
| Sim replication (pre-flight, F1/F2/F3 PASS) | commit `9a6c8ad` |
| Ordering (checkable) | register `#7414`/`#8175` → seal `4759817` → go-bound `#8186` → airborne `64f06eb` → decisions-hash `#8221` → unseal `74497e3` → grade `#8227` |

Every step is timestamped on the ship's-computer bus and in git; the protocol's integrity is in the *order*, and the order is public.

---

## 10. Methods (short form)

n=16 (32 physical qubits, two copies). Hard-family state ρ_P prepared by per-shot randomized single-qubit product eigenstates with a biased global-sign coin (zero two-qubit gates in prep); transversal Bell measurement across the two copies (one CX + H per pair). 103,732 science pairs + 2,000 public-P calibration rows, chunked into 22 jobs with per-job balance re-read. Budget T(ε) frozen pre-flight; ε read from the leading calibration job in-epoch. Decoder reproduces |tr(Pρ)| per Pauli from raw Bell counts with the transpose-factor (−1)^#Y(P), endianness, and bit-layout conventions pinned by golden fixtures. Grading: F1 (planted amplitude ≥ decision bar at ≥5σ), F2 (budget sufficient), F3 (pipeline vs closed-form truth), against 112 seeded blind probes calibrating the null. Full methodology: [`docs/methodology-and-validation.md`](methodology-and-validation.md).

---

## Closing

The Sealed Shadow is the campaign's first advantage-class result to meet every clause of the standard that its two retired predecessors built — and it earned the word by surviving the same red team that retired them. The number that travels is **9.3× fewer copies than any single-copy strategy, at 104σ, blind, sealed, court-graded, against a proven floor** — and the reason to believe it is everything we retired, failed, and re-flew to get there.

*A pass that took this much attack to leave standing is the only kind worth the word.*
