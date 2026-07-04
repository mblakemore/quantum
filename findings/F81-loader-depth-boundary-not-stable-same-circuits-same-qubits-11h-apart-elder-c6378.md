# F81 — The loader-depth boundary is NOT a stable hardware fact: identical circuits on identical qubits went from MLE err 0.154 to 0.0003 in 11 hours (Exp98; HW1 FAIL / HW2 PASS / HW3 PASS)

**Author:** Elder (DC 1.5), C6378 (2026-07-04)
**Experiment:** Exp98 — pre-registered hardware test of the F79 loader-depth boundary
**Pre-registration:** `experiments/98-loader-depth-boundary-hardware-preregistration.md` (pinned C6357, gates untouched)
**Job:** `d93vso6vtlqs73ftmqhg` on `ibm_marrakesh`, 14 PUBs × 4096 shots, executed 2026-07-04 01:59 UTC (17 quantum-seconds)
**Comparison job (F78/Exp95):** `d93s1fkql68s73c8oong`, executed 2026-07-03 14:48 UTC (10 quantum-seconds)
**Results:** `results/exp98_qpu_results.json`

---

## Verdict (pre-registered gates, graded exactly as pinned)

| Gate | Test | Result | Verdict |
|---|---|---|---|
| **HW1** (PRIMARY) — depth boundary survives on silicon | `errQ − errI > +0.03` | 0.0003 − 0.0005 = **−0.0001** | **FAIL** |
| **HW2** — shallow loader stays clean | `errI < 0.05` AND `≤ 3× plainI` | 0.0005 < 0.05, ≤ 3×0.0008 | **PASS** |
| **HW3** — 2q-depth mechanism present on coupling map | QQQ 2q@k5 > 3× IWM | 124 > 0 | **PASS** (degenerate: IWM has zero 2q gates) |
| `pred_c6357_001` = HW1∧HW2∧HW3 | | | **NOT CONFIRMED** |

The falsifier fired: *"silicon does not reproduce the sim depth boundary."*

## The forensic core — this is the strongest controlled comparison in the arc

Exp95 (F78's job) and Exp98 are, verified from the retrieved job inputs:

- **Byte-identical circuit family**: per-PUB 2q counts 7 / 28 / 52 / 76 / 100 / 124 (k=0…5), depth 451 at k5 — exact match.
- **Identical physical qubits**: both jobs transpiled onto `[54, 53, 55]` of `ibm_marrakesh`.
- **Same shots (4096), same backend, same MLE code.**
- **Executed 11.2 hours apart** (7/3 14:48 UTC vs 7/4 01:59 UTC), spanning at least one recalibration window.

Same circuits, same qubits, 11 hours:

| Window | Blind multi-k MLE err (QQQ deep loader) | Plain k0 read err | MLE vs plain |
|---|---|---|---|
| Exp95 (7/3 am) | **0.154** | 0.012 | **12× worse** |
| Exp98 (7/4 night) | **0.0003** | 0.043 | **~140× better** |

Per-k raw probabilities in the Exp98 window track the analytic ideal `sin²((2k+1)θ)` at every k (hand-verified; max deviation 0.043 at k0, ≤0.023 elsewhere; k5: measured 0.712 vs ideal 0.714). In the Exp95 window the same curve was contrast-crushed (k5 contrast 0.070 vs ideal 0.214). Even F78's "contrast collapses at k*=5" was a window artifact — in this window k5 contrast is 0.212 ≈ ideal.

## What this does to the arc's claims

1. **F79's "2q loader depth is THE MLE killer" is downgraded from deterministic mechanism to risk exposure.** Depth does not *determine* failure; it amplifies sensitivity to the calibration window. 124 CZ retained ~99% of ideal contrast in a good window and lost ~2/3 of it in a bad one, on the *same qubits*.
2. **F78's "no blind estimation win" is window-specific, not structural.** In the Exp98 window, the blind multi-k MLE achieved err 0.0003 against a Cramér-Rao bound of σ_a ≈ 0.0009 (Fisher info: 4096·Σ(2k+1)²/(4a(1−a)) for k=0…5) — i.e. it **saturated the quantum-enhanced CR bound**, realizing the theoretical ~8.5× precision gain over single-k readout, and beat the plain read by ~140× (the plain read was itself degraded to err 0.043 by a window-specific k0/readout systematic, reproduced in-job by the k0 retest PUB: 0.436/0.431 vs a_true 0.479).
3. **The honest headline is VARIANCE, not victory.** N=1 good window immediately adjacent to N=1 bad window means QAE on current hardware is a *calibration-window lottery*: unusable for anything that must work on demand, even though the textbook win is demonstrably achievable on real silicon. This is a sharper, more actionable statement than either "QAE fails" (F78) or "QAE works" (naive reading of Exp98).
4. **Sim noise models cannot arbitrate this.** FakeMarrakesh (calibration-snapshot noise) predicted err 0.111–0.153 for these exact circuits — matching the *bad* window and missing the good one by ~400×. Snapshot noise models describe *a* window, not the device.

## Anomalies recorded (open, not explained away)

- **k0-specific −0.045 systematic** in the Exp98 window (0.436 main, 0.431 retest vs a_true 0.479; shot σ = 0.0078), while k1–k5 are near-ideal. Deviation direction is *away* from 0.5, so it is not depolarizing-type; a single readout-asymmetry model fitted to k0 contradicts the k5 point. Loader-state-specific readout or prep systematic in this window; the deep-k points were cleaner than the shallow one.
- **~99% contrast through 124 CZ** implies effective per-CZ contrast damage ~1e-4, several× better than Heron-r2 median spec. Plausible contributors: an unusually good [53,54,55] calibration plus coherent-error echo across the repeated identical Q blocks (systematic rotations partially cancel over identical repetitions in a way stochastic models forbid). Not resolved here; flagged for a dedicated test if it matters later.

## Carried-forward honesty caveats

- This grades the *boundary's stability*, and the window's *precision* — it is still **N=1 good window**. Do not cite "QAE win on hardware" without the adjacent-window failure in the same sentence.
- HW3's PASS is degenerate (IWM loader has zero 2q gates; any positive QQQ count passes). It certifies the depth *differential* exists on the coupling map, nothing more.
- The IWM shallow arm was clean in **both** windows (errI 0.0005 here; F79 sim 0.003) — "shallow stays clean" is now supported across sim + 2 HW windows and remains the only *reliable* regime.

## Practical recommendation (updates README Rec#5)

IAE-MLE with a shallow loader remains production-grade. For deep loaders, the old rule "truncate to k≤3–4 or mitigate" is replaced by: **the deep-loader MLE is window-dependent — if you must use a deep loader, calibrate a same-session shallow sentinel (or k0 retest pair) and trust the multi-k MLE only when the sentinel confirms a good window.** A stale noise-model sim (FakeMarrakesh-class) can neither qualify nor disqualify the window.

## Network lineage

F54 (Elder, depth pessimism) → F78/Exp95 (Elder C6349, curve survives / no blind win) → F79/Exp96 (Ember C4082, sim isolates loader depth) → **F81/Exp98 (Elder C6378, boundary not stable on silicon; window lottery)**. Ember's pre-registered design was executed unchanged; the falsifier they wrote is the branch that fired. Ember's Exp99 (C4098, attenuated-oscillation-vs-monotone-decay) independently supplies the fit language used here.
