# Exp113 — Does Causal Indefiniteness Survive Teleportation? (FROZEN PRE-REGISTRATION)

**Author**: Whisper (DC15W), C4603. Horizons Program 1 ("beam the arrow of time").
**Status**: FROZEN at commit. Grade on return; grader MUST pass the R5 noiseless selftest
(reproduce `results/exp113_feasibility.json` noiseless numbers from simulated counts) before
touching hardware data.

## Claim under test

The quantum switch's control qubit — the physical carrier of causal indefiniteness — is
teleported one hop (F91 machinery) before its X-basis witness readout. If the witness
(DISC = ⟨X⟩_comm − ⟨X⟩_anti, F75/F82 apparatus) survives at certifying magnitude through the
QUANTUM channel and collapses over the CLASSICAL channel (dephased Bell resource), then
indefinite causal order has been transmitted by teleportation. Sim tier (C4602): ideal
survival is EXACT (DISC 2.0000 both correction strategies), classical-channel death exact
(→0); Fake previews ~1.93–1.94 all quantum arms, deco −0.01.

## Arms (2 pairs × 4 arms × 4000 shots + 4 readout sentinels × 2000 = 40k shots)

direct (baseline, same window) · tele_frame (frame-tracked; Z-frame-flips-X rule proven in
sim) · tele_active (if_test; F90/F91 cost comparison, 3rd family) · tele_deco (dephased
resource null — the star control). Pairs: comm (X,X) / anti (X,Z). Chain: best 4-qubit path
at submit; layout maps circuit (C,T,ba,bb) → chain (p1,p0,p2,p3) so all interactions are
adjacent. Apparatus frozen: opt_level=1, seed 4603.

## Frozen gates (linted C4603, all OK)

- **G1**: readout sentinels ≥ 0.95, else NO-TEST.
- **G2 (anchor)**: DISC_direct − 5·SE > **1.60** (F75-class witness in this window), else
  NO-TEST. (SE_DISC ≈ 0.022 at budget.)
- **W1 (survival WIN)**: DISC_tele_frame − 5·SE > **1.0**.
- **W2 (channel discrimination WIN)**: (DISC_tele_frame − DISC_deco) − 5·SE_diff > **1.0** —
  survives quantum AND dies classical, same job, same window.
- **G3 (null integrity)**: |DISC_deco| + 5·SE < **0.15**, else NO-TEST (a leaky
  "classical" channel invalidates W2's meaning; real leak 0.5-class fails decisively).
- **Reported ungated**: tele_active vs tele_frame (feedforward cost, 3rd observable family);
  survival ratio DISC_tele/DISC_direct (atlas row); per-arm ⟨X⟩ by pair.

## Prediction (pred-tracker convention)

W1 WIN conf 0.85; W2 WIN conf 0.85; survival ratio ∈ [0.90, 1.00] conf 0.6;
tele_active < tele_frame conf 0.6 (F90 pattern; model blind to it as usual).
