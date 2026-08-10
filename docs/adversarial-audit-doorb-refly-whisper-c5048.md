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

## 5. One open verification item (the only thing the grade artifact cannot settle)
**The floor's adaptivity class.** The 9.3× rests on Ω(2ⁿ/ε²) being the **single-copy** floor including **adaptive** strategies. If the cited theorem's proven bound covers only *non-adaptive* single-copy measurements, an adaptive classical strategy could in principle sit below it. The prereg cites a proven floor; the exact statement (adaptive vs non-adaptive, and the precise family constant) should be confirmed against the source theorem before external submission. This does not affect F1 (a measured 104σ recovery), only the *magnitude and universality* of the classical floor it beats. **Recommend: cite the theorem's exact hypotheses on the claim card, and confirm adaptivity coverage.**

## Bottom line
The door (b) re-fly is the campaign's strongest advantage-class result and it **survives its own adversarial cycle**: the fired classes clear structurally, every headline number recomputes conservative, and the residuals are scope limits and a named systematic, not leaks. The one thing left to nail before it travels externally is a citation-level confirmation of the floor's adaptivity class — the difference between "9.3× over the best-known single-copy strategy" and "9.3× over *any* single-copy strategy." Both are real; the second needs the theorem quoted exactly.

*A pass that took this much attack to leave standing is the only kind worth the word.*
