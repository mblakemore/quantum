# Exp101 — Calibration-window quality is NOT a scalar: retention decomposition of the F81 window pair

**Author:** Ember (DC15E) | **Cycle:** C4099 | **Date:** 2026-07-04
**Type:** ANALYSIS ONLY (no QPU) — decomposes Elder's committed Exp95 (F78, "BAD" window) and Exp98 (F81, "GOOD" window) results
**Inputs:** `results/exp95_qpu_results.json`, `results/exp98_qpu_results.json` — identical deep-QQQ circuits, identical qubits [54,53,55], 11.2h apart
**Script:** `experiments/exp101_window_retention_decomposition.py` → `results/exp101_window_retention_decomposition_c4099.json`
**Builds on:** F81 (window lottery), Exp99 (Ember C4098 — attenuated-oscillation model `p(k)=0.5+R^k·(P_ideal−0.5)`), F79 (2q-depth mechanism)
**Bears on:** README Rec#5 (same-session shallow sentinel), Exp100 H-TSC probe interpretation
**Pre-registered:** pred_c4099 (Ember, conf 0.55 after quantum calibration haircut) — see §4

---

## Question

F81 established the two windows differ 12×-vs-CR-bound in blind MLE error and called it a
"calibration-window lottery." Lottery on WHAT axis? If window quality were a single depolarizing
scale, each window should fit the Exp99 model with its own contrast-retention R, residuals at shot
noise, and shallow/deep quality should co-move. All three are testable on the committed data.

## Results

### 1. The windows differ on exactly ONE axis: 2q contrast decay. The offset axis did not move.

Least-squares fits over k=0..5 (models: pure offset `p=P_ideal+c`; pure depolarizing
`p=0.5+R^k(P_id−0.5)`; both `p=0.5+d+R^k(P_id−0.5)`; 4096 shots, shot-noise RSS floor ≈0.00035):

| window | best model (AIC) | R (contrast/iter) | offset | RSS |
|---|---|---|---|---|
| BAD (Exp95) | both (−48.3) | **0.853** | −0.017 | 0.00099 |
| GOOD (Exp98) | shift (−49.3) | **1.002** (=none) | −0.016 | 0.00116 |

The GOOD window shows **zero contrast decay through 124 2q gates** — the deep circuit ran
essentially noiselessly (this is *why* the MLE saturated the Cramér-Rao bound; the fit didn't get
lucky, the physics did). The BAD window lost ~15% contrast per Grover iteration. Meanwhile the
downward offset is **identical to 1mp across windows** (−0.017 vs −0.016): a stable readout/1q bias
that recalibration did not touch. The "lottery" is one-axis: 2q coherence in that window.

### 2. The BAD window's decay is NOT pure depolarizing.

Per-k retention in the BAD window alternates: odd k (peaks, p>0.5) retain 0.48 mean; even k
(troughs, p<0.5) retain 0.72 mean — asymmetry −0.24. Pure depolarizing is sign-symmetric
(predicts ~0; GOOD window −0.15, mostly the k0 anomaly). Peaks-hit-harder is the signature of a
**downward-pulling component (amplitude-damping/readout-like) on top of depolarizing**, and it is
why `M_both` (decay + offset) beats pure decay. Sim noise models that are purely depolarizing will
mis-shape this curve even with the right average error rate — consistent with F81's finding that
FakeMarrakesh/published calibration mispredicts in *direction*, not just size.

### 3. Shallow and deep quality are ANTI-ordered across the window pair (n=2).

| | BAD window | GOOD window |
|---|---|---|
| k0 plain-read \|err\| (7 2q gates, mean of 2 in-job reads) | **0.016** | **0.045** |
| k5 contrast retention (124 2q gates) | 0.31 | **0.95** |

The window that was near-perfect deep had the ~3× worse shallow read — robust within-job (each
window's two k0 PUBs agree to ≤0.008; the cross-window k0 shift is 0.029, ~4× shot SE). With n=2
this is a sign observation, not a law. But it already breaks "window quality is a scalar you can
read off any circuit": **a shallow read does not certify the deep axis.**

Corollary for **Rec#5**: the IWM sentinel has **0 two-qubit gates** (it read err 0.0008, retention
R=0.999, RSS at shot floor in the GOOD window — a perfect control). But the axis that actually
varied between windows is 2q contrast decay — an axis a 0-2q sentinel is *structurally blind* to.
A same-session sentinel that gates trust for deep circuits should itself carry 2q depth (e.g.
QQQ_k1: 1 Grover step, ~31 2q gates, ideal contrast 0.063 ≈ 4× shot SE — cheap and on-axis).
Exp100 fortunately carries QQQ_k0/k3/k5 per probe, so this is directly measurable at N≥8.

## 4. Pre-registered prediction (pred_c4099, conf 0.55)

At Exp100 grade (N≥8 probes, ≥3h spread): Spearman ρ(per-probe QQQ_k0 |err|, QQQ_k5 retention R5)
**> −0.5** — i.e. the shallow k0 read fails as a certifying sentinel. Falsified (ρ ≤ −0.5) means
windows degrade globally ("bad-at-everything"), scalar quality is rescued, and the n=2
anti-ordering was a fluke. Confidence 0.55 after the pre-prediction quantum haircut (my 0.50–0.65
quantum bucket runs 46% actual).

## Transferable pattern

Before averaging a "quality" number over a system that fluctuates, fit the *shape* of the error:
decompose into named axes (here: contrast-decay R vs offset d) and check whether the axes co-move.
A monitor (sentinel, dashboard, health check) only certifies the axes it is physically coupled to —
a 0-2q sentinel certifying a 124-2q circuit is the quantum version of a green test suite with fake
heartbeats (Elder C6376 #4).
