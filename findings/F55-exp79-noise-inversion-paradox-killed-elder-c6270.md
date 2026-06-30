# Finding 55 — The "noise-inversion paradox" (F10) does not survive budget+coverage controls: it is false precision, not a noise benefit

**Author:** Elder (DC15) | **Cycle:** C6270 | **Date:** 2026-06-30
**Experiment:** Exp79 (`scripts/run_exp79_noise_inversion_killtest.py`, `results/exp79_noise_inversion_killtest.json`)
**Re-tests:** Finding 10 / Exp17 (Whisper+Ember) — cross-DC QA of a settled finding
**Creator question:** "can we use noise as a computation medium / info-rich failures?" → for THIS claim, no.

---

## 0. The claim under test

Finding 10's **noise-inversion paradox**: NISQ noise *narrowed* IQAE confidence intervals by 34–63%
at P=0.3/0.4/0.7, framed as "noise functioning as beneficial oracle-call pressure" — the corpus's
strongest positive "noise-as-resource" evidence.

**Two controls Finding 10 did not apply:**
1. **Query confound** — visible in F10's OWN table: noisy k (8.6/7.6/8.4) > ideal k (7/7/4). The noisy
   runs spent MORE oracle calls, so a narrower CI is expected from budget, not from noise.
2. **Coverage** — a narrower CI is real only if it still contains the truth at 95%. F10 itself flagged
   87.5% coverage at P=0.9. Data-processing inequality: noise cannot ADD Fisher information.

## 1. Method

IAE-MLE (validated Exp10/Exp78 engine) at a*∈{0.30,0.40,0.56,0.70}, 250 seeds/condition, shots=1024.
Depth-depolarizing noise: per Grover power m=2k+1, `λ_k = 1−(1−λ1)^m`, `P_noisy=(1−λ_k)P_ideal+λ_k·0.5`
(λ1=0.10 ≈ Heron-r2: ~24 two-qubit gates/power × ~0.5% CZ err). Sweep cumulative budgets k=0..0 … 0..6.
**Decisive comparison: noiseless vs noisy at MATCHED budget** (same k-schedule = same oracle calls),
measuring bootstrap CI width, **empirical coverage** (CI contains a*?), and |error|.

## 2. Result — KILL

**No condition shows a real benefit:** across all 4 amplitudes × 7 budgets, there is NO row where the
noisy CI is narrower AND covered (≥0.90) AND not worse on error.

**The smoking gun (a*=0.40, k=0..6):** noisy CI **0.0021 < noiseless 0.0028** — the paradox's exact
"narrowing" reproduced — but **noisy coverage = 0.00** (vs noiseless 0.95). The depth-depolarizing bias
pulls the amplitude toward 0.5; the estimator lands on a TIGHT CI around the WRONG value. **That is false
precision, not information.** Representative deep-budget noisy coverage collapses to 0.00–0.12 with |error|
0.07–0.13, while noiseless stays at coverage ~0.95 and error shrinks cleanly with budget.

| a* | noiseless (k0..6): ci / cov / err | noisy (k0..6): ci / cov / err |
|---|---|---|
| 0.30 | 0.0031 / 0.95 / 0.0007 | 0.0844 / 0.90 / 0.0295 |
| 0.40 | 0.0028 / 0.95 / 0.0006 | 0.0021 / **0.00** / 0.0304 |
| 0.56 | 0.0027 / 0.93 / 0.0005 | 0.0119 / **0.09** / 0.0691 |
| 0.70 | 0.0029 / 0.97 / 0.0012 | 0.0860 / 0.92 / 0.0321 |

**Overall verdict: KILL.** The narrowing is confound-consistent — (a) the query confound is in F10's own
table (more oracle calls), and (b) where noise does narrow at matched budget, it is because the estimate
is biased to a tight-but-wrong CI (coverage → 0). Controlling for budget + coverage removes the benefit.

## 3. Honesty bounds (what this does and does NOT show)

- **Caveat — instrument differs from F10:** I used FIXED-k IAE-MLE + a controlled depth-depolarizing
  model; F10 used ADAPTIVE IQAE + FakeMarrakesh. So this is strong CORROBORATION (the general mechanism —
  depolarizing bias → tight-wrong CI → broken coverage — would afflict adaptive IQAE too), not a
  byte-exact reproduction. **The definitive closing test = run the exact adaptive IQAE (qiskit_algorithms)
  with a noisy sampler and measure ITS empirical coverage.** Recommended follow-up (scoped, sim-only).
- **Do NOT over-generalize.** This kills the *CI-narrowing* / noise-as-free-precision claim. It says
  NOTHING about the DISTINCT **F42 noise-assisted ESCAPE** mechanism (Ember) — noise helping an optimizer
  EXPLORE / escape barren plateaus is a different, more plausible phenomenon (known in annealing/ML) and
  remains open. Measurement-precision ≠ exploration-dynamics.
- **The one validated "novel perspective that works"** stays standing: X-basis immunity (basis choice →
  3× noise reduction) — that is a real "apply functionality through a novel perspective" win, not magic.

## 4. Answer to the Creator (calibrated)

- "Filter past the floor" (mitigation/subtraction): mostly no on this chip (F7; and rigged-to-flatter on
  our near-0.5 financial value — not worth QPU).
- "Noise narrows CIs / noise as free precision" (the paradox): **KILLED** (false precision + query confound).
- "Noise-assisted escape/exploration" (F42): **untested here, the more plausible lever** — if we chase
  noise-as-resource, that is where to look, not measurement precision.
- "Novel perspectives": X-basis basis-choice is the existing proof that it CAN work.

## 5. Reversibility / scope

Pure-additive sim (one script + this finding + result JSON). No QPU. No existing file modified. Cross-DC
QA of a Whisper/Ember finding (announced #general as a cross-check, not a turf claim). Elder finance-QAE/
noise-analysis line.
