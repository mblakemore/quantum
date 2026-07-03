# Exp93 HARDWARE ARM — Results (Elder C6342)

**Graded**: 2026-07-03 (C6342) | **Job**: `d93p3cnu62ks73953cvg` on `ibm_marrakesh` (Heron-r2)
**Grader**: `scripts/grade_exp93_mixture_control.py` → `results/exp93_mixture_control_grade.json`
**Pre-reg (locked before submit)**: `exp93-classical-mixture-control-preregistration.md` §HARDWARE ARM (C6341)
**Triple**: control C=53, target T=39, ancilla Anc=54 (cost 0.00714) | 6 PUBs, 6000 shots/PUB, ONE calibration window

---

## Verdict: **PASS** — causal-separability loophole closed on silicon, same-device, drift-free.

### Per-PUB control expectation `<X_c>`
| mode | commute (X,X) | anticommute (X,Z) | DISC = commute − anticommute |
|---|---|---|---|
| switch   | +0.9627 | −0.9373 | **+1.9000** |
| definite | +0.9950 | +0.9920 | +0.0030 |
| mixture  | +0.0210 | −0.0143 | **+0.0353** |

### Witnesses
- **W1** = DISC_switch − DISC_definite = **+1.8970**  (SE~0.026)
- **W2** = DISC_switch − DISC_mixture  = **+1.8647**  (SE~0.026, ~72σ > 0) **[HEADLINE]**

### Pre-registered gates
| gate | criterion | value | result |
|---|---|---|---|
| H_HW1 | DISC_switch ≥ +1.40 | +1.900 | **PASS** |
| H_HW2 | \|DISC_mixture\| ≤ 0.20 | 0.035 | **PASS** |
| H_HW3 | W2 ≥ +0.40 (headline) | +1.865 | **PASS** |
| H_HW4 | \|W1 − W2\| ≤ 0.25 (corroborating) | 0.032 | **PASS** |

Verdict rule PASS = H_HW1 ∧ H_HW2 ∧ H_HW3 (H_HW4 corroborating) → **PASS 3/3 headline, 4/4 total**.

## Interpretation
- The switch fires (+1.900, near Exp91's silicon +1.781) while BOTH causally-separable controls are inert:
  pure-definite +0.003 and classical-mixture +0.035 — statistically indistinguishable from 0 at 6000 shots.
- Same-device / same-window: the switch-vs-mixture contrast is drift-free (no cross-device, cross-window
  calibration artifact) — the distinction from Ember's F76 (inert mixture, but `ibm_kingston` + continuous
  `cry(φ)` damping).
- Honest bound: coherence-of-causal-order witness (queries each gate twice), design validated in sim, now
  hardware-confirmed against the sharpest causally-separable adversary. NOT a black-box query separation.

## Prediction accuracy
Pre-registered expectation W2 ≈ +1.78; observed +1.865 (mixture slightly more inert than the +1.78
back-of-envelope, since the observed DISC_switch on this triple, +1.900, ran a touch above the Exp91
+1.781 estimate). All four gates cleared with large margin — decisively powered, as pre-registered (~68σ).

Full report → `findings/F77-classical-mixture-loophole-closed-on-hardware-same-device-elder-c6342.md`.
