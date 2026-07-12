# Friction Report 03 — Published Calibration Data Does Not Predict Deep-Circuit Window Quality

**Status: DRAFT, NOT FILED** (Creator approval required to file). Target: IBM Quantum
calibration/properties data. Extracted C4595 from findings F81 and F84 (the findings remain
the scientific record; this is the actionable summary).

## Summary

Deep-circuit fidelity on `ibm_marrakesh` varies by ~3× between runs of the SAME circuits on
the SAME qubits hours apart ("window lottery", F81, 11 h apart), while the published
calibration data was **flat across the swing** — and a pre-registered test (F84, frozen
Spearman gate) found **time-since-calibration does not predict window quality** (its own
null; quality clustered by queue-drain episode instead). Users scheduling deep circuits get
no usable quality signal from the published data.

## Data

- F81: identical loader circuits, identical qubits, 11 h apart — estimator error 0.154 vs
  0.0003 (~500×); published calibration unchanged across the swing.
  (`findings/F81-loader-depth-boundary-not-stable-same-circuits-same-qubits-11h-apart-elder-c6378.md`)
- F84: pre-registered H-TSC test across nine windows — calibration age vs window quality:
  NULL under a frozen gate. (`findings/F84-window-quality-not-calibration-age-htsc-null-elder-design-whisper-grade-c4542.md`)
- Working mitigation (ours, available to anyone): co-batch a same-depth-class sentinel and
  gate on its in-run reading — detection instead of forecasting (used in F85, F86, F88).

## What we ask

Expose *any* in-drain quality signal (even coarse), or document that deep-circuit performance
is not inferable from the published calibration so users know to carry their own sentinels.

## Environment / Reproduction

Same stack as reports 01–02. Sentinel pattern: any known-output circuit at the payload's
depth class, co-batched in the same job.
