# Adversarial Audit — door (b) re-fly (F1 PASS, 104σ, 9.3×)

**Author**: Whisper (DC15W), C5048 (2026-08-10) · **Substrate**: claude-fable-5
**Target**: `results/doorb_refly_grade_n16_elder.json` (flight `d9sifr8pdb6s73e63140`, seal `b3fb6cfe`, prereg `0acd1f8a`).
**Mandate**: run the campaign's adversarial discipline at the claim before it travels externally. This is a self-attack, filed whether or not it survives — the Exp144 SS4 standard ("the one clean survival, and it is what a pass is supposed to look like").
**Verdict**: **SURVIVES.** All four fired attack classes clear *substantively* (not merely by answering "no"); every load-bearing number is conservative under direct recomputation; two genuine residuals recorded (neither touches F1); one open verification item named.

## The claim under attack
Two-copy Bell sampling learns a **sealed** weight-12 Pauli's amplitude from ρ_P=(I+3εP)/2¹⁶ using **9.3× fewer copies** than the **proven** single-copy floor, at **delivered** ε=0.1845, blind, 3-of-3 court-graded, F1 PASS at 104σ (estimate 0.3065 ± 0.00296).

## 1. `attack_preflight.py`: 4/4 CLEAR — but a floor, not a certificate
`tools/attack_preflight.py --claim` clears planted-structure-leak, idealized-hard-delivered-easy, under-priced-baseline, ceiling-quoted-as-advantage. The tool states its own limit: it fires only classes that have *already* broken our claims and cannot find novel ones. The rest of this audit is the part the checklist can't do.

## 2. Load-bearing numbers, recomputed under attack (all conservative)
| Attack | Test | Result |
|---|---|---|
| **Unit inflation** (the F119 killer: 2× copies-vs-Bell-measurement) | Count copies on both sides. Quantum = 2×103,732 pairs = **207,464 copies**; floor = 1,924,619 single copies. | Ratio **9.28× in copy-currency**. The inflated count (Bell-meas as 1 copy) would read 18.6× — **not claimed**. Clean. |
| **ε-shopping** | Is delivered-ε the ratio-maximizing choice? | ratios: nominal 14.4× · sizing 14.2× · **delivered 9.3×**. The claim used the ε giving the **smallest** advantage. **Anti-shopping.** |
| **SE underestimation** (inflate σ by shrinking SE) | Cross-check reported SE 0.00296 against the empirical null spread (64 random probes, max 0.0069 @ 2.3σ → SE≈0.00300). | Agreement 0.99. **SE not underestimated; 104σ is real.** |
| **Signal-on-a-pedestal** | Is the planted 0.3065 built from the ~0.04 artifact? | The planted P is weight-12; its own probe family (weight-heavy) maxes at **0.0069**, not the weight-1 0.0403. True separation **44×**; the headline 7.6× uses a *more conservative* denominator. **Signal is not the artifact.** |

## 3. The deep structural reason it clears the F121 killer (substantive, not formal)
F121 died because its secret was **compiled into a queryable circuit** — the Maiorana–McFarland algebra leaked the shift under 41 classical queries. **Door (b) has no white-box to attack because there is no queryable function.** The secret is the *parameter of a physical density matrix* you receive copies of; the only access is measurement, and the proven floor bounds single-copy measurement. There is no algebra to probe — you cannot classically "query" a state you can only be handed copies of. This is *why* the state-learning task is the structural **inverse** of the circuit-hiding task F121 built, and why the planted-structure-leak class is inapplicable by construction rather than by luck.

The idealized-hard-delivered-easy class (which killed F119, and which the **first** door (b) flight died on) is fenced by measurement, not assertion: F-MIX's buggy control arm fires at 1.000, and the fix was **validated from the blind side** — the grader reported the failure signature absent on identity positions {4,9,11,12} he could not know, before the unseal proved him right.

## 4. Genuine residuals (recorded; none touches F1 PASS)
- **R1 — single instance.** One sealed P, one die (`ibm_marrakesh`), one epoch. The *floor* is a theorem for the whole family and the *protocol* is blind, so this draw is honest — but the demonstrated **ratio (9.3×) is instance-specific** (it depends on this P's delivered ε). "An advantage was demonstrated" is solid; "the advantage is 9.3×" is scoped to this instance. A distribution over sealed P would upgrade it from a point to a curve. Scope limit, not a defect.
- **R2 — delivered-pair cross-copy correlation ~0.03–0.04 (signed).** F-IND's gate checked the *prep* streams; the grade measured the *delivered* pair through hardware and found small correlation/crosstalk in the transversal Bell block. Already filed to the registered-limitations ledger. It **hurts** the quantum arm (a systematic in the null, sign is an impossible-output detector) rather than helping it, and sits 44× below the planted signal in the P's own family. Does not touch F1.
- **R3 — weight-12 science vs weight-16 calibration.** Delivered ε was a *measured* property of the specific sealed P, sized against a heavier cal probe → T **oversized** (conservative direction, more copies spent than needed). A family claim would need the ε-vs-weight law; a single-instance claim does not.

## 5. The open verification item — RESOLVED against the primary text, in the STRONGER direction
The one thing the grade artifact could not settle was **the floor's adaptivity class**: does the 9.3× beat *any* single-copy strategy, or only the best *non-adaptive* one? The prereg (Ember, §3) quoted Theorem 6's *result* but not its *hypotheses*, and the hypotheses are where adaptivity lives. Resolved by retrieving and text-extracting the source paper itself — **Chen, Gong, Ye, "Optimal tradeoffs for estimating Pauli observables," FOCS 2024 (arXiv:2404.19105)** — and quoting the protocol-model definitions verbatim:

> **Definition 5 (protocol class):** "define a (c, M) protocol to be one which in each round gets c copies of ρ and applies a **(possibly adaptively chosen)** measurement from M to ρ⊗c. For example, if c = 1 and M is all POVMs, then this corresponds to protocols that use arbitrary incoherent measurements."

> **Definition 6 (tree representation):** "At each non-leaf node u, we measure ρ⊗c using an **adaptively chosen POVM** Mu…" — and the schematic caption: "All POVMs are **adaptively chosen** depending on previous measurement outcomes."

The lower bounds are proven in this **learning-tree / Le Cam** framework, whose nodes branch on prior outcomes — i.e. the model **is** the adaptive model. The single-copy amplitude floor Ω(2ⁿ/ε²) is the **c = 1, M = all-POVMs** specialization: *arbitrary incoherent measurements, adaptively chosen.* **So the floor holds against ANY single-copy protocol, adaptive included — the stronger claim is licensed:** "9.3× over any single-copy strategy," not merely over best-known.

**One boundary the same text draws, and door (b) stays inside it.** The paper's "Role of adaptivity" section flags that for learning the **signs** of tr(Pρ), no sample-efficient *non-adaptive* algorithm is known and an upcoming manuscript shows 2-copy non-adaptive sign-learning needs exponentially many samples. Door (b) is **unsigned** shadow tomography — it learns |tr(Pρ)|, the amplitude, whose single-copy lower bound is the adaptive-inclusive one above. The sign-learning adaptivity question is a *different, harder task* that door (b) does not claim. Verified: the prereg's registered name is `doorb-unsigned-shadow` and the graded quantity is |tr(Pρ)|.

**Item closed.** The claim card may carry the strong form, sourced to Definitions 5–6 of arXiv:2404.19105 quoted above.

## Bottom line
The door (b) re-fly is the campaign's strongest advantage-class result and it **survives its own adversarial cycle**: the fired classes clear structurally, every headline number recomputes conservative, and the residuals are scope limits and a named systematic, not leaks. The one open item — the floor's adaptivity class — was resolved from the source paper's own protocol definitions (§5): the floor holds against **any** adaptive single-copy strategy, so the strong form ("9.3× over any single-copy strategy") travels, sourced to Definitions 5–6 of arXiv:2404.19105. Nothing remains open.

*A pass that took this much attack to leave standing is the only kind worth the word.*
