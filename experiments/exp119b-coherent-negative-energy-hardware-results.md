# Exp119b — Coherent Negative Local Energy: HARDWARE RESULTS

**Whisper C4642.** Job `d9a9sp2f47jc73a9vurg` (C4641 freeze, 10 pubs, 530k shots,
ibm_marrakesh pair (3,4)), graded by FROZEN grader `scripts/grade_exp119b.py`.
Grade record: `results/exp119b_grade.json`. Parent: Exp119 (LOCC claim FAILED C4640 —
stays failed; this certifies the strictly weaker coherent claim).

## VERDICT: **NEGATIVE-LOCAL-ENERGY-CERTIFIED (coherent)** — all gates pass

| Gate | Result | Number |
|---|---|---|
| G0 apparatus guard | clean | ground raw +0.1049 ± 0.0052 (positive side, as physics requires) |
| **V1 HEADLINE** | **WIN** | corrected E_B(def) = **−0.0547 ± 0.0046** (12σ below zero); **5σ certified bound: E_B ≤ −0.0319** |
| V2 below-ground | WIN | def − ground = −0.1000 ± 0.0071 (14σ) |
| V3 correlation control | WIN | def − fix_pooled = −0.2030 ± 0.0097 (21σ) |

Predictions: P1 (0.70) **HIT**, P2 (0.85) **HIT**, P3 correctly no.

## The claim, precisely

On a 2-qubit region of ibm_marrakesh carrying the Hotta Hamiltonian
H = Z_A + Z_B + 2X_AX_B (+offsets), a coherent-controlled extraction pulse drives
the measured local energy ⟨H_B + V⟩ to −0.0547 ± 0.0046 — **below the local ground
level**, the energy-sign condition of exotic matter. By the one-sided-conservatism
argument frozen at prereg (every residual noise term biases E_B POSITIVE; readout
correction removes only the readout part), the TRUE local energy is **at most
−0.0319 at 5σ** — the certification under-reports the effect by construction.
Theory value −0.1147: we certify ~48% of it raw-corrected, bound ~28%.

**NOT claimed**: LOCC energy teleportation (parent's classical-feedforward version
failed as frozen; the 0.092 E latency tax stands, friction 05).

## Retest discipline — what earned the CONFIRMED status

The parent's coherent arm read −0.0341 ± 0.0082 (4.2σ) as an unplanned diagnostic —
promoted to NOTHING at C4640. This experiment pre-registered the claim, disclosed the
pro-hypothesis provenance, power-calculated the budget (c4130_001: 100k shots/basis,
1.45× margin), froze an exact-SE-propagation grader, and let fresh data decide.
Fresh data: **deeper than the parent** (−0.0547 vs −0.0341; better calibration window,
F_readout ≈ 0.989–0.995). The F82 CONFIRMED_ON_RETEST pattern completes: near-miss →
disclosed retest → certified.

## Books

E_A(ground) = +0.0114 (baseline clean); fix± controls at +0.197/+0.231 raw — rotating
WITHOUT the control correlation injects energy (+21σ separation from the extraction
arm): the control-line correlation is the active ingredient, not the pulse. Raw
(uncorrected) def arm: +0.0110 ± 0.0044 — raw positivity is readout bias, removed by
the same-window frozen correction; disclosed, not hidden.

## Status

Horizons-2 Q1 CLOSES in two legs: LOCC teleportation = honest LOSS with a new
measured constant (feedforward tax 0.092 E); negative local energy = **CERTIFIED**.
Ember numbering requested (candidate: first certified sub-ground-state local energy
on a superconducting QPU inside a frozen-rule court).
