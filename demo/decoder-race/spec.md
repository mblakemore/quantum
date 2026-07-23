# The Decoder Race — a sealed answer read through noise

`Findings F120 · F121`  ·  `Experiments Exp-HSS races 1–6 + instrument flights (C4973–C4985)`  ·  `Backends ibm_marrakesh, ibm_kingston (Heron r2)`  ·  `Winning job d9gps850k0jc738h6blg`  ·  `Wing IV · H8 P9 (CLOSED-WON)`

> **⊘ VERDICT — WON 3-of-3, THEN SUPERSEDED (C4996, own red-team, pre-submission).** The graded race stands as run (476× vs the frozen simulation floor, bar 10×), but the floor priced *simulation*; the planted MM problem's algebra falls to a 41-query linear-structure solve (~0.25 ms). **No runtime advantage is claimed.** F120 (shot-axis decoder) stands as an instrument result; F119 under re-audit.

Full Specification Sheet

Every number on the exhibit page is drawn from this sheet; every number here traces to a committed results file or court post in the repo. Nothing is hand-tuned for display.

## 1 · The idea, in plain language

The Roetteler hidden-shift problem plants a secret 40-bit string in a scrambled Boolean function; a quantum circuit can read it out in one shot *in principle*, while the best classical solvers grind (stabilizer-rank simulation, cost ~2^(αT) in the T-gate count). At the depth the interesting instances need, the chip's single most-frequent output decays to uselessness — measured, published as **window-closed** (C4973), with the exact number a future machine would need.

The re-read of that verdict's own discarded calibration data (C4974) found the fold's deep rungs were not noise: the most-common output at depth was the planted answer **with two typos**. Each shot is the answer ⊕ sparse errors — so N shots are N noisy transmissions of one codeword, and per-bit majority voting across shots reads the answer through noise that destroys every individual shot. **F120**: the per-bit information decays at λ_bit ≈ 0.003/slot — ~30× slower than the modal-answer law (λ_modal ≈ 0.09/slot at width 40).

## 2 · The court

- **Sealer (Ember)**: generates the answer, commits SHA-256(s‖salt) to the public repo **before any circuit exists**; holds the reveal until the decoder's answer is posted publicly.
- **Flyer/Decoder (Whisper)**: builds (necessarily embedding s in the oracle — blindness is procedural), flies, decodes with a frozen mechanical decoder that consumes only counts, posts ŝ before any reveal opens.
- **Grader (Elder)**: owns the classical band, frozen days before the races (edge-robust: the classical side is granted its fastest plausible tool at every edge).

Every card frozen before data; two-stage reveals; no rescue rules anywhere; every fold booked.

## 3 · The winning race (race-6, C4981)

| Quantity | Value | Source |
|---|---|---|
| Die / job | ibm_kingston / `d9gps850k0jc738h6blg` | manifest |
| Race depth (d2q) | 167 (best-of-100 routing; cap 200) | manifest |
| Pre-gate | free t=0 ladder EXACT ×2 → register certified clean **before** the seal was risked | reveal #670 |
| Twin gate | t=0 twin EXACT at race depth (register unification 37/40) | reveal #670 |
| Decode | ŝ == s **exactly** (HD-0), from the smallest pre-registered subsample: **12,500 shots** | reveal #672 |
| Decoder | frozen calibrated per-bit majority; atomic 2⁻⁴⁰ null; no search, no rescue | card c4980 |
| Quantum wall | **3.82 s** (anti-flattering: all 104 job-seconds incl. calibration spread over non-cal shots) | `results/exp_hss_race6_quantum_wall.json` |
| Classical floor (harshest edge, ×4500) | 1,818 s → ~~476×~~ (WIN bar 10×, cleared 48×; floor = simulation cost) | Elder C6563 band, grade quantum@52c689c |
| Red-team linear-structure solve (C4996) | **~0.25 ms / 41 queries** → supersedes the race floor by ~7×10⁶× | whitebox + blackbox variants; 3 seats confirmed, 2 disjoint implementations |
| Classical operating (best all-core) | 23,460 s → **~6,100×** | same |
| Robustness | maximally conservative wall (full 200k shots = 57.8 s) still clears 3× | grade #674 |

## 4 · The fold ladder (what each race bought)

C4973 fold: wrong observable (modal) → F120. Race-1 (C4976) fold: endianness convention → round-trip gates. Race-2 (C4977) fold by ONE bit: gate placed 20% past race depth → gates at race depth, shot-matched. Race-3 (C4978) fold: two readout-defective qubits → whole-chip calibration + per-bit ML thresholds; first ρ_t measurements. Race-4 (C4979): hygiene validated (exact blind at d2q=217, deepest of the race arc; campaign blind-exact record now d2q=310, organic-arc lad_d_hi) but exclusion cost +92 depth → cap branch; lesson: fix defects in the estimator. Race-5 (C4980): pre-registered control — dropped exclusion to test if it was load-bearing; it was; miss booked, clean-ladder pre-gate + seal preservation born. Race-6: WIN. Post-win red-team (C4996): the win's supersedable clause fired by our own hand pre-submission — runtime advantage retired; F120 instrument stands.

## 5 · The physics the arc measured (map v1.1 → v1.2)

- **Per-bit law**: bias(d) ≈ b₀·e^(−λ_bit·d); slope is a die bulk constant (marrakesh 0.0029–0.0030 across register eras); the **intercept is a register-quality meter** (0.96/0.91 clean vs 0.69 dirty).
- **Magic-tax decomposition** (organic pad-free flight, Elder grading against his own hypothesis): the stochastic tax of 80 T-gates is **T-localized and depth-flat** (ρ ≈ 0.66–0.75); the apparent per-slot decay is a **depth-growing coherent few-bit drift** — RC-resistant, readout-cal-invisible, detected by estimator divergence.
- **Routing lottery**: d2q is a per-day random variable (125–287 across draws of the same circuit class).
- **Defect taxonomy**: tilted (threshold-correctable) · stuck-at-readout (cal-visible, uncorrectable) · circuit-level-bad (cal-invisible; only a dynamic pre-gate catches it).

## 6 · Fences, printed on the result

One instance family (Maiorana–McFarland hidden shift, n=40, t=80). One die per race, one calibration window. Best-known-solver **engineering race** — not a complexity theorem (F119 holds the theorem-floored seat in sample-complexity currency). Joules one-sided (QPU power unpublished). **Supersedable-by-design**: a classical solver beating 1,818 s on this family retires the entry — that mechanism is the point. F54's brute-force circuit-simulation wall is untouched and unclaimed.

## 7 · Exhibit model note

The interactive uses the measured clean-register constants (b₀=0.91, λ_bit=0.0029, ρ_t=0.75) with i.i.d. per-bit flips — a simplification (real silicon adds the coherent few-bit drift at depth, which is why the real races needed the full fence stack). The hidden string in the demo is the actual race-6 revealed answer.
