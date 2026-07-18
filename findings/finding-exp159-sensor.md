# Finding — Exp159/159b: THE QUANTUM SENSOR — blind sealed-phase metrology, failed honestly, then certified

**Cycle**: C4848 · **Date**: 2026-07-18 · **Backend**: ibm_fez ·
**Jobs**: v1 `d9dsc34inv1c73apfu60`, v2 `d9dsdfineu4c739nmef0` (4 + 6 circuits, 4096 shots each).
Creator directive: fly the metrology sensor. Successor to the GHZ Sextant exhibit: the Sextant
proved the *resource* (entangled probes beat the SQL); this flies the *instrument* — and an
instrument is its error bar.

## Protocol — the sensor calls its shot blind

A secret field strength θ\* is drawn and sealed (sha256 commitment in the manifest before
flight; seal file withheld until reveal). Two sensors read the field at identical interrogation
budget (5 qubits × 4096 shots): **product** — five independent Ramsey probes (slope 1, SQL
strategy); **GHZ** — one GHZ-5 probe with disentangling readout (slope 5, Heisenberg strategy).
Each publishes estimate ± CI *from the data alone*; then the seal opens. Pre-registered gates:
(1) **coverage** — both 95% CIs must contain θ\*; (2) **head-to-head** — GHZ variance < 0.5× at
matched budget (ideal 0.20); (3) within-job calibration arms only (C4199 baseline-to-qubits).

## v1 — the Heisenberg gain was real and the error bar lied (8σ)

θ\* = 0.3325. Product: 0.3287 ± 0.0074 — **HIT** (0.5σ). GHZ: 0.3030 ± 0.0037 — **MISS at 8σ**.
Variance ratio 0.249 (gain real). Pre-registered verdict: **FAILED**, published as-is.
The failure was the pre-named risk: the slope-5 fringe amplifies a GHZ-epoch systematic
(~0.03 rad) and the single θ=0 calibration arm **cannot see it** — cos is even, so one
calibration point conflates contrast with phase offset. The entangled sensor was more precise
*and wrong*: textbook precision-without-accuracy, caught by the blind coverage gate — by
protocol, not luck.

## v2 — two-point calibration, disease injected in sim, then certified on silicon

Fix: each sensor gets **two** calibration arms (applied 0 and a known reference 0.35); three
fringe points determine contrast, offset, and field (bisection + parametric bootstrap through
the full solve). The selftest includes an **injected-disease gate**: v1's −0.03 systematic is
added to the GHZ arms in sim and the pipeline must still cover truth (it measures −0.0325 and
lands 0.3σ off — the correction machinery is proven pre-flight; v1's pipeline provably fails
this same gate).

**Flight** (fresh seal, θ\* = 0.4152, commitment verified):

| sensor | contrast | measured offset | reads | vs truth |
|--------|----------|-----------------|-------|----------|
| product | 0.995 | −0.0062 | 0.4105 ± 0.0100 | HIT, 0.5σ |
| **GHZ** | 0.865 | **−0.0345** | **0.4161 ± 0.0052** | **HIT, 0.2σ** |

Variance ratio **0.271** (< 0.5 gate; ideal 0.20). **VERDICT: SENSOR CERTIFIED** — blind,
bias-corrected, entanglement-enhanced. The measured GHZ offset (−0.0345) is the same systematic
that sank v1 (−0.030 implied) — quasi-static across the two jobs, measured in-job and corrected
without ever seeing the sealed value.

## What this adds beyond the Sextant

The Sextant showed entangled probes carry more Fisher information. This shows the full
instrument loop under blind conditions: *the entangled advantage survives honest error bars
only if the calibration model is rich enough to see every parameter the slope amplifies.*
One-point calibration is degenerate (contrast/offset); the Heisenberg slope amplifies the bias
you didn't model by N. Coverage — not variance — is the certificate.

## Prediction record

v1: 0.65 on full pass — wrong verdict call, but the named risk (GHZ coverage miss via slope-5
systematic) is exactly what happened, and the ratio band held. v2: all predictions held
(coverage HIT, δ_g in [−0.06, −0.01], ratio in band). Calibration 82.3%.

## Fence

Phase sensor on 5 qubits; dynamic range 2π/5 (θ\* committed inside the unambiguous window —
range public, value sealed); offset assumed quasi-static within a job (held true today; Exp158
shows other systematics drift in hours — different systematics have different lifetimes); a
blind-certification demonstration, not a field-deployed magnetometer.
