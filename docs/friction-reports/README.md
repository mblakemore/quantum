# Friction Reports — Documented Platform/Tooling Issues, With Data

**What this is** (Creator direction, C4595): a standing home for reproducible, data-backed
reports of friction we hit in the quantum software/hardware stack — the kind of thing that
would be an upstream bug report or vendor feedback if filed. We accumulate them here as we go;
each is written to be paste-ready if the Creator decides to file one externally. Nothing in
this directory is filed anywhere without Creator approval.

**The bar for a report**: measured on our jobs (job IDs + analysis pointers), reproducible
from repo artifacts, states the anticipated rebuttal and answers it, and names the concrete
ask (doc fix, characterization, or API change). One file per issue, numbered; update a
report in place as new evidence rows land (note the cycle).

## Index

| # | Report | Target | Status | Evidence base |
|---|---|---|---|---|
| 01 | [FakeMarrakesh noise model is optimistic, error grows with depth and splits by observable family](01-fakemarrakesh-depth-optimism.md) | `qiskit-ibm-runtime` fake_provider | DRAFT, not filed | 12-row residual atlas (`results/model_residual_atlas.json`), 3 independently flagged incidents |
| 02 | [Published T1 systematically underestimates live T1 (queue-length-independent)](02-published-t1-bias.md) | IBM Quantum calibration data | DRAFT, not filed | Exp108b + Exp108c back-computed T1s: +38–69% on 2/2 runs (F88 §mechanism) |
| 03 | [Published calibration data does not predict deep-circuit window quality](03-calibration-blind-to-window-quality.md) | IBM Quantum calibration data | DRAFT, not filed | F81 (flat calibration across a 3× quality swing), F84 (pre-registered H-TSC null: window ≠ calibration age) |

| 04 | [Dynamic-circuit conditional executed with inverted effective polarity (one pub class)](04-dynamic-conditional-polarity.md) | Qiskit Runtime dynamic circuits | DRAFT, not filed; discriminating micro-refly queued | Exp112 banked-data forensics: deterministic Ψ+ fingerprint, logical+transpiled circuits verified correct (C4625) |

## Adding a report (for future cycles)

1. Write `NN-short-slug.md` with: Summary → Data (job IDs, tables) → Anticipated objection,
   answered → Why it matters to users → What we ask → Environment → Reproduction.
2. Add the index row above with evidence pointers.
3. Cross-reference the finding(s) it grew from; findings stay the scientific record, the
   report is the actionable extract.
4. Filing externally = Creator approval, always (outward-action rule).
