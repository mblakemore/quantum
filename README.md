# Autonomous Characterization of the IBM Heron-r2 Quantum Processor

**A multi-arc empirical campaign on IBM Heron-generation hardware (`ibm_marrakesh`, `ibm_kingston`, `ibm_fez`), May–July 2026 (ongoing) — run end-to-end by an autonomous multi-agent network: ~100 pre-registered experiments, every number anchored to an IBM Quantum job ID.**

The campaign's centerpiece is a **quantum switch** — a circuit where the *order* of two operations is itself in superposition. The switch was theorists' idea; photonics labs demonstrated it first, and early versions ran on chips like ours. **What this campaign added was the scoreboard**: pre-registered games and channels whose limits are provable theorems for any definite-order process — and the switch beat those limits. A discrimination game was won at **216.8σ** above its theorem ceiling, replicated the next day on a chip the design had never touched; information crossed channels of exactly zero capacity; a thermodynamic splitting forbidden to every ordered process was measured at 21.1σ. Around that centerpiece sits a systematic characterization of what this hardware generation can and cannot do.

> 🔀 **[Play with it → mblakemore.github.io/quantum](https://mblakemore.github.io/quantum/)** — the interactive switch demo (drag order-coherence, watch the measured cosine law), the STATIC bot duel with bring-your-own-key live mode, the Interrogation casebook game, and print-&-play tabletop versions. Every number in every demo is measured hardware data.

---

## ⭐ The Causal-Advantage Arc (headline results)

The witness arc (F73–F77, ≥72σ on silicon) graduated into **pre-registered, provable-bound BEATS** —
results whose success criterion is *exceeding* what any classical/causal process permits, rather than
characterizing hardware:

| Result | Number | Where |
|---|---|---|
| **Causal discrimination game beats the causally-separable bound** (0.8695, re-solved from Araújo et al. with q* recovered) | p̂ = 0.9769 ± 0.0005, **216.8σ** | `ibm_marrakesh`, [pre-reg](experiments/exp105-causal-game-preregistration.md) · [results](results/exp105_hw_results.json) |
| **Cross-device replication** — same frozen design, chip it never touched | p̂ = 0.9738, **201σ** (0.3pp concordance) | `ibm_fez`, [addendum](experiments/exp105b-replication-preregistration.md) |
| **Capacity activation** — information through two channels of exactly zero capacity (and every causal composition exactly zero) | **0.0436 bits/use, 55.6σ** over zero; null arm 0.0001 bits; the bit lives ONLY in the control–target correlation (D≈0 confirmed) | `ibm_marrakesh`, [pre-reg](experiments/exp106-capacity-activation-preregistration.md) |
| **N=3 cyclic switch** — capacity activation **WON at 61.7σ** (0.0260 bits through three zero-capacity channels) and exposed the **NISQ scaling inversion**: theory scales with N, practice inverts (110-CZ depth cost) — N=2 is the practical optimum this hardware generation | **F85** | [finding](findings/F85-n3-capacity-activation-scaling-inversion-whisper-c4539-ember-numbered-c4119.md) · [pre-reg](experiments/exp107-cyclic3-capacity-preregistration.md) |
| **ICO thermal splitting** — the Felce-Vedral refrigeration resource **WON at 21.1σ**: the switch of two fully-thermalizing channels split the target COLDER (p₁\|+ = 0.2098) vs HOTTER (p₁\|− = 0.3894) by control outcome, Δ = 0.1796 against a causal value of exactly 0. Bonus: the pre-filed cross-arc depth-decay law beat FakeMarrakesh out-of-sample by 2.3× | **F86** | [finding](findings/F86-exp108-ico-refrigeration-resource-whisper-c4561-ember-numbered-c4121.md) · [pre-reg](experiments/exp108-ico-refrigeration-preregistration.md) |

**[Quantum-switch full apparatus spec](docs/quantum-switch-spec.md)** — the single-document engineering reference: circuit family (V1–V5), exact theory statistics, measured-results ledger with job IDs, reusable methodology, pitfall registry, scope and platform prior art.

Strategy docs: [bridges to a compute advantage](docs/bridges-to-compute-advantage-whisper-c4522.md) ·
[ICO applications roadmap](docs/ico-applications-roadmap-whisper-c4527.md) ·
[SDP bound groundwork + recovered q*](experiments/causal-game-sdp-bound-groundwork-whisper-c4523.md) ·
[paper outline (causal-inference audience)](docs/pearl-bridge-paper-outline-whisper-c4533.md)

---

## What Else the Campaign Established

Eight arcs of operational discoveries about real NISQ hardware, each detailed in the linked docs below:

- **Hard limits**: output becomes statistically uniform past ~800–1000 CZ gates (Finding 05), and the QAOA utility ceiling co-locates with that wall (Exp33). Textbook error correction adds more noise than it removes on this substrate (Finding 06, independently re-confirmed by toric-code replication F62).
- **What actually moves fidelity**: qubit *placement* beats gate count as the lever (up to 46× error reduction; F57–F70), with a reusable quiet-qubit picker that works untuned across devices.
- **Noise structure**: the dominant CZ noise is Z-biased and structured (X-basis readout is measurably cleaner — magnitude substrate-dependent, mechanism replicated); "noise as a computational resource" was tested and killed under controls (F55–F56).
- **Calibration reality**: ±7pp daily drift; deep-circuit quality is a *window lottery* — detectable by same-depth sentinels in-run, not forecastable from calibration age (F81, F84) — and the noise-model's optimism grows with depth (the measured depth-decay law in the spec).
- **What works today**: VQE hit chemical accuracy on H₂; amplitude-estimation readout recovered a 344× precision gain via multi-k MLE — with a mapped depth boundary for financial-scale loaders (F51, F54, F78–F79).
- **Communication primitives**: the comms white space opened — superdense coding graded WIN at **341σ** above the exactly-0.5 unassisted ceiling (p=0.9688, MI 1.77 bits/qubit, executed no-entanglement null dead on the ceiling; F87 — tutorial-class priors credited, the contribution is the frozen bound-referenced grading).
- **Side quest**: integrated-information (Φ) of quantum systems follows a clean size law and ignores the number-theoretic structure that dominates its classical counterpart (quantum-IIT arc).

**Orientation numbers**: ~100 experiments · 3 real Heron chips + a noise-model sim tier ·
600 q-sec/28-day open-plan budget, every submit budget-gated · every finding anchored to an IBM job ID ·
5 consecutive experiments where pre-submission review caught a real defect.

Plain-English version of everything: **[ELI5_SUMMARY.md](ELI5_SUMMARY.md)** (self-contained, shareable).

---

## The Findings — Where Everything Lives

| Doc | Contents |
|---|---|
| **[Beyond the Ladder](docs/beyond-the-ladder.md)** ★ | The full technical argument, written for causal-inference readers and sibling-reviewed to journal standard: why the switch results sit outside what structural causal models can express — "do-calculus is not wrong; it is typed" — with the executed classical-control arms and the Exp111 switch-vs-coherent-control verdict (ratio 1.949, theory 2.0). The repo-native publication. |
| **[Findings 1–27 catalog](docs/findings-catalog.md)** | Arc-1 characterization + QAOA/optimizer arcs: headline table + plain-English one-liner per finding (CHSH 2.74, X-basis immunity, the ~1000-CZ wall, QEC ancilla tax, mitigation failures, VQE chemical accuracy, QAE 344×, …) |
| **[Campaign arcs since June 2026](docs/campaign-arcs.md)** | Findings 28+ and the F-series, arc by arc: warm-start anchors, noise-is-not-a-resource kills, placement-beats-gate-count (F57–F70), toric-code replication, financial QAE depth boundary + calibration-window lottery (F78–F81), quantum-IIT bridge, the ⭐ quantum-switch arc (F73–F77 witness chain → F82–F86 bound beats), and the communication-primitives arc (F87) with figures |
| **[Methodology & validation](docs/methodology-and-validation.md)** | Autonomous-network methodology, pre-registration discipline, Pearl causal framing, budget, cross-validation anchors, limitations and caveats |
| **[Next steps & open questions](docs/next-steps-and-open-questions.md)** | What you can use today (7 actionable rules), the strategic frontier (P1 noise-as-resource RESOLVED-NEGATIVE, P2 causal order DELIVERED, P3 replication audit), and the ORQ list with live statuses |
| **[ELI5_SUMMARY.md](ELI5_SUMMARY.md)** | The whole campaign in plain English, shareable (§17 the game, §18 the two walls) |
| **[full-report.md](full-report.md)** | Arc-1 deep synthesis (source document) |

---

## Methodology & Scope (short form)

Full version: [docs/methodology-and-validation.md](docs/methodology-and-validation.md)

- **Pre-registration**: falsifiable gates frozen before every submit; failed pre-regs reported as first-class results (several findings are self-retractions).
- **Tier labels**: `HW` = real QPU with job ID; `sim` = FakeMarrakesh-class noise model — and noise-model trust is **depth-stratified** (predictive at the ~4-CZ class, off by 400× at ~124 CZ; see F81 and the spec's residual atlas).
- **Calibration drift is the elephant**: ±7pp daily; deep-circuit quality is a *window lottery* (F81) — reproduce within a calibration window, or use the sentinel-gating discipline in the newest pre-regs.
- **Cross-device replication is the standard**: it has demoted headlines (F03's 3× is marrakesh-specific) and promoted others (quiet-qubit picker F70; the causal game, 0.3pp concordance across chips).
- **Scope**: claims are about *this generation* of hardware and are **device-characterized** (compiled gate-model circuits reproducing switch statistics — the device-independent certifications of indefinite causal order are photonic experiments; prior non-photonic work is credited in the [spec](docs/quantum-switch-spec.md)). Every number traces to a job ID in [`experiments/job-manifest.md`](experiments/job-manifest.md).

---

## Hardware Under Test

- **Primary processor**: IBM Heron-r2 (`ibm_marrakesh`) — all of Arc 1 and most later hardware arcs
- **Additional devices (later arcs)**: `ibm_kingston` (X-basis cross-backend Exp31–34, IQAE validation F51, causal cosine law F76) and `ibm_fez` (toric-code Bell proxy F61–F64, placement partition F67–F69, quiet-qubit cross-device F70, causal-game replication F82) — both Heron-generation 156-qubit devices
- **Qubit count**: 156 superconducting transmons · **topology**: heavy-hexagonal lattice (degree 2–3)
- **Native two-qubit gate**: controlled-Z (CZ) via flux-tunable couplers · **environment**: dilution refrigerator @ ~15 mK
- **T₁, T₂**: routinely > 200 μs (ancilla T₂ measured 270–340 μs during this campaign) · **CZ error**: ~0.4% baseline
- **Daily calibration drift observed**: ±7 percentage points (same circuit, same seed, 24h apart)

See [`docs/hardware-substrate.md`](docs/hardware-substrate.md) for the full physical architecture primer.

---

## Repository Map

```
.
├── README.md                    ← you are here
├── demo/                         ← 🔀 GitHub Pages front door (mblakemore.github.io/quantum/)
│   ├── index.html               ← interactive Quantum-Switch demo
│   ├── static-duel/             ← 📺 classic bot vs quantum bot (bring-your-own-key live mode)
│   ├── casebook/                ← 🕵️ the Interrogation casebook game
│   └── casebook-pnp/            ← 🃏 print & play tabletop version
├── ELI5_SUMMARY.md              ← shareable plain-English summary of the whole campaign
├── full-report.md               ← Arc-1 synthesis (the deep-research source doc)
├── findings/                    ← one-per-discovery deep dives (~80 files)
│   ├── 01…44-*.md               ← the core numbered line (Findings 41–43 under exp-named files)
│   ├── F48…F87-*.md             ← the unified F-series (quiet qubits, placement, toric, causal-order, comms arcs)
│   ├── finding-25/26/46/47…     ← quantum-IIT arc side numbering (25/26 here ≠ QAOA Findings 25/26!)
│   └── exp*-*.md                ← interim findings, integrity audits, closure notes
├── images/                      ← figures (PNG), reproducible from scripts/generate_figures.py
├── experiments/
│   ├── job-manifest.md          ← IBM Quantum job IDs + experiment inventory
│   └── *-preregistration.md     ← pre-registered hypotheses/gates, frozen before each submit
├── scripts/                     ← Python source: circuits, submission tools, analysis, grading
│   ├── generate_figures.py      ← regenerate figures from cycle-data constants
│   ├── quiet_qubits.py          ← F58 quiet-qubit picker / drift snapshot / CHSH health tool
│   ├── check_usage.py           ← IBM Open-plan quota check (run BEFORE submitting jobs)
│   └── README.md
├── results/                     ← raw result JSONs + the model-residual atlas
├── docs/
│   ├── quantum-switch-spec.md   ← ⭐ full apparatus spec: circuits, theory, ledger, methodology
│   ├── findings-catalog.md      ← Findings 1–27 headline table + ELI5 per finding
│   ├── campaign-arcs.md         ← Findings 28+ / F-series, arc by arc (with figures)
│   ├── methodology-and-validation.md ← methods, cross-validation, caveats (full)
│   ├── next-steps-and-open-questions.md ← actionable rules + strategic frontier + ORQs
│   ├── bridges-to-compute-advantage-whisper-c4522.md ← the 3-bridges strategy synthesis
│   ├── ico-applications-roadmap-whisper-c4527.md     ← what the certified switch can do next
│   ├── beyond-the-ladder.md                          ← ★ the full technical argument (causal-inference readers)
│   └── hardware-substrate.md    ← Heron-r2 physical architecture primer
└── sources/
    └── references.md            ← peer-reviewed and primary sources (cited inline in findings)
```

**A field guide to finding numbers**: the campaign's numbering evolved live. Findings 1–44 are the core line (with 41–43 under experiment-named files and no Finding 45 in this line); `finding-25/26/46/47` belong to the quantum-IIT arc's separate numbering; the unified `F##` series runs from ~F48 to F87 (and counting), with one flagged collision (Elder's anchor "Finding 48" vs Ember's IIT F48). When in doubt, the file's header states its arc.

---

## License & Attribution

Public for cross-validation, replication, and peer review. If you reproduce or build on this work, citing the IBM Quantum job IDs in `experiments/job-manifest.md` is the most useful form of attribution — it gives downstream readers a verifiable anchor.

The Python scripts in `scripts/` are released for educational and research use. Lyla quantum tooling (`qae_volatility_estimator.py`, `ibm_quantum_submit.py`) is sourced from the upstream Lyla project and reproduced here with attribution headers.
