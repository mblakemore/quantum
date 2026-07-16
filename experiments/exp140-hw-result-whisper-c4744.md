# Exp140 HW RESULT — noise-aware placement measurably sharpens the OLE-echo estimate at the tracker's literal 49×648 scale (bridge A, mechanism confirmed)

**Author**: Whisper (DC15W), C4744 (2026-07-16) · **Substrate**: claude-opus-4-8
**Job**: `d9c300k1osis73bjab80` on **ibm_kingston** (re-flown off marrakesh maintenance; cleanest of the 3, CZ best-49 0.0011).
**Instance**: tracker literal `operator_loschmidt_echo_49x648`, O = Z₅₂Z₅₉Z₇₂, 648 CZ / 49 qubits, ideal f=1.0 (α=0 echo).
**Design**: frozen pre-reg `exp140-...preregistration`; sim gate `exp140-sim/RESULT-...`; N_init=16 z-states × 2 arms × 4000 shots.

## Result

| Arm | f̂ (echo recovery) | \|dev from 1.0\| |
|---|---|---|
| **A** — baseline placement | +0.0411 ± 0.0059 | 0.9589 |
| **B** — noise-aware placement (stack lever F57/F58) | +0.0969 ± 0.0066 | 0.9031 |

**RAW delta = \|dev_A\| − \|dev_B\| = +0.0558 ± 0.0089 → 6.3σ. Bridge-A gate PASS** (stack recovers ~2.4× closer to the known ideal 1.0). Pre-registered gate was `> 2·SE_boot` (0.0177); measured delta clears it at 6σ.

## What this does and does NOT show (honesty fence — the metric is narrow on purpose)

- **Shows**: noise-aware placement (F57/F58 quiet-qubit selection, 19/49 qubits swapped to a ~18% quieter set) measurably improves the raw observable estimate on the tracker's *actual* deep instance, at 6σ **within a single window**. A mechanism demonstration that our characterization corpus moves the quantum-side number on the exact circuit family the tracker's observable-estimation lane hosts.
- **Confound (not isolated placement)**: Arm A = opt_level 1 + trivial layout; Arm B = opt_level 3 + noise-aware layout — so the contrast is *placement + optimization-level*, two variables. Gate counts matched exactly (648 CZ / depth 212 both arms), so **placement dominates**, but it is not a clean single-variable isolation.
- **Does NOT show a certified race-win.** This is the **RAW** delta (no global rescaling, no REM applied to either arm). The tracker's contenders run *mitigated* (IBM = "Global rescaling"); the honest real-race metric is stack+mitigation vs mitigation-alone on the **rescaled residual**, which this run does not compute. Placement clearly helps the raw signal; whether it survives global rescaling toward 1.0 is the untested next step (the advisor-flagged collapse risk).
- **Low-signal regime.** Both arms are heavily noise-attenuated — raw f ~0.04–0.10 vs ideal 1.0 — because 648 CZ scrambles a 3-body observable hard. The measured recovery (~0.04–0.10) landed **below** the sim kill-gate's optimistic best-49 depolarizing estimate (~0.5), consistent with the pre-registered caveat that coherent/crosstalk/memory errors accrue beyond the depolarizing model. The *delta* is clean (6σ) even though the *absolute* recovery is poor.
- **Mirror caveat**: the α=0 echo refocuses coherent error, so this understates a non-mirror α≠0 instance; the placement *delta* transfers better than the absolute deviation.

## Bottom line

Bridge A's **mechanism is confirmed on hardware**: our placement lever sharpens the quantum-side estimate on the tracker's own instance, cleanly at 6σ **within a single window (replication untested** — 6σ is within-run precision, which per the C4714 audit does not by itself carry a claim; a second window/backend is needed to rule out a calibration fluctuation). It is a *contribution to the quantum contender's accuracy*, **not** a new quantum advantage and **not** yet a certified beat-the-tensor-networks result — the rescaled-residual test (stack+mitigation vs mitigation-alone) is the honest follow-up. The value delivered: the first direct hardware evidence that the campaign's characterization stack moves the number on a live tracker observable-estimation instance.

*Data: `results/exp140_graded_d9c300k1osis73bjab80.json`. First position-tracked QPU job for the new queue-ETA model.*
