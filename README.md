# Autonomous Characterization of the IBM Heron-r2 Quantum Processor

**A multi-arc empirical campaign on IBM Heron-generation hardware (`ibm_marrakesh`, `ibm_kingston`, `ibm_fez`) + FakeMarrakesh NISQ simulation, May–July 2026 (ongoing).**

This repository documents an autonomous, multi-agent network's characterization of IBM's Heron-r2 processors across a growing series of arcs (now ~98 experiments). **Arc 1** (22 experiments on the physical QPU) extracted raw hardware performance metrics under a strict 600-quantum-second execution budget, from foundational CHSH Bell tests to VQE, QAE, 3-qubit dynamic circuits, and Hadamard quantum walks. **Arc 2** (the IQAE financial amplitude-estimation arc, Exp 10–24) extended the QAE results to a real financial probability (IWM up-probability P=0.56) and validated the arc on the real QPU. The campaign since then has added: an **X-basis / commutation-aligned QAOA arc** (Findings 11–23), a **trap-escape and optimizer-stochasticity arc** (Findings 24–28), a **warm-start anchor arc** with a practical best-of-k / adaptive-escalation recipe (Findings 29–44), a **placement-dominance + quiet-qubit tooling arc** (F57–F70), a **toric-code logical-Bell replication arc** (F61–F64), a **financial QAE depth-boundary arc** on real hardware (F51, F54, F78–F79), a **quantum-IIT (integrated information) bridge arc**, and — the current headline — an **indefinite-causal-order arc** (F73–F77) that measured a quantum-switch causal witness on real silicon at ≥72σ. See [`experiments/job-manifest.md`](experiments/job-manifest.md) for the inventory and IBM Quantum job IDs.

The findings constitute novel discoveries about the operational behavior of modern superconducting NISQ hardware: structural noise immunity tied to commutation relations, sub-noise-floor coherent error excursions driven by scramblon dynamics, qualitative phase transitions in algorithmic scaling, the mathematical impossibility of break-even error correction on current substrates, placement quality dominating gate count as the fidelity lever, a P-safety zone and a loader-depth boundary for quantum amplitude estimation in financial applications, and an on-silicon demonstration that causal order itself can be put in superposition — beyond what any classical causal model can represent.

> 🔀 **[Interactive demo — the Quantum Switch on real silicon →](https://mblakemore.github.io/quantum/demo/)** &nbsp; Drag to drain order-coherence and watch the ≥72σ causal witness trace our measured cosine law. Runs in any browser; all numbers are real F73–F77 hardware data. ([source](demo/index.html))

> **ELI5 — In plain English** *(see also [`ELI5_SUMMARY.md`](ELI5_SUMMARY.md) for a self-contained, shareable plain-English version of the whole campaign):*
>
> An AI-agent network has been running experiments on IBM's newest 156-qubit quantum chips since May 2026 — first 22 experiments on one real chip, now nearly 100 experiments across three real chips (`ibm_marrakesh`, `ibm_kingston`, `ibm_fez`) plus hardware-realistic simulation. The original campaign found: the chip does "quantum entanglement" almost as well as physics allows (Finding 1); it has a hidden "easy direction" for reading qubits worth ~3× reliability on the home chip (Finding 3); past ~1000 two-qubit gate operations output is pure noise — a hard ceiling (Finding 5); the textbook error-correction plan adds more noise than it removes (Finding 6); popular error-mitigation software tricks made things worse (Finding 7); **but** hardware-aware algorithm design still hit chemistry-grade precision on a real molecule (Finding 8) and a 344× improvement in quantum probability readout (Finding 9).
>
> The campaign since then has added six big things. **(1) Where you run beats how much you run**: putting circuits on the chip's currently-quietest qubits cut errors up to 46×, a reusable "quiet qubits" picker tool now does this automatically on any IBM chip, and controlled hardware experiments show qubit *placement* explains ~3× more fidelity loss than gate *count* (F57–F70). **(2) A practical recipe for quantum optimizers**: reuse your best previous starting answer (it never hurts, and rescues near-misses), generate a few candidate starts and keep the best, escalate only when the first looks weak — saving ~30% of the compute (Findings 29–44). Two seductive "noise actually helps" claims were killed under proper controls: noise never improves final answers (F55, F56). **(3) Finance meets the wall**: a real market probability (QQQ tail risk) was computed on real hardware to within ~2%, but the quantum method that's supposed to beat classical Monte Carlo needs circuits ~50–100× deeper than the wall allows — and we pinned the exact culprit, the entangling-gate depth of the data-loading circuit (F54, F78, F79). **(4) Error correction still doesn't break even**: an independent replication of an outside group's logical-entanglement demo confirmed that adding an error-correction round makes the result *worse* on today's chips (F62), echoing Finding 6. **(5) A consciousness-math side-quest**: the "integrated information" (Φ) of quantum systems follows a clean size law and completely ignores the number-theory structure that dominates its classical counterpart. **(6) The headline**: we built a "quantum switch" — a circuit where the *order* of two operations is itself in superposition — and proved on real hardware, at ≥72σ, that no classical story about cause-and-effect order (not even randomly flipping a coin between the two orders) can explain what the chip did (F73–F77). The "amount" of indefinite order is even continuously tunable, following a clean cosine law on two different chips.
>
> **Bottom line**: The hardware is real and bounded; the bound (entangling-gate depth) is harder than any software trick can soften — but placement-aware compilation, warm-started optimizers, and shallow hybrid algorithms extract genuine value inside it. And on the physics frontier, this hardware is already good enough to demonstrate causal structures that classical probability theory cannot represent.

---

---

## ⭐ July 2026 — The Causal-Advantage Arc (newest results)

The witness arc (F73–F77) graduated into **pre-registered, provable-bound BEATS** — the campaign's
first results where the success criterion is *exceeding* what any classical/causal process permits,
rather than characterizing hardware:

| Result | Number | Where |
|---|---|---|
| **Causal discrimination game beats the causally-separable bound** (0.8695, re-solved from Araújo et al. with q* recovered) | p̂ = 0.9769 ± 0.0005, **216.8σ** | `ibm_marrakesh`, [pre-reg](experiments/exp105-causal-game-preregistration.md) · [results](results/exp105_hw_results.json) |
| **Cross-device replication** — same frozen design, chip it never touched | p̂ = 0.9738, **201σ** (0.3pp concordance) | `ibm_fez`, [addendum](experiments/exp105b-replication-preregistration.md) |
| **Capacity activation** — information through two channels of exactly zero capacity (and every causal composition exactly zero) | **0.0436 bits/use, 55.6σ** over zero; null arm 0.0001 bits; the bit lives ONLY in the control–target correlation (D≈0 confirmed) | `ibm_marrakesh`, [pre-reg](experiments/exp106-capacity-activation-preregistration.md) |
| **N=3 cyclic switch** — capacity activation **WON at 61.7σ** (0.0260 bits through three zero-capacity channels) and exposed the **NISQ scaling inversion**: theory scales with N, practice inverts (110-CZ depth cost) — N=2 is the practical optimum this hardware generation | **F85** | [finding](findings/F85-n3-capacity-activation-scaling-inversion-whisper-c4539-ember-numbered-c4119.md) · [pre-reg](experiments/exp107-cyclic3-capacity-preregistration.md) |
| **ICO thermal splitting** — the Felce-Vedral refrigeration resource **WON at 21.1σ**: the switch of two fully-thermalizing channels split the target COLDER (p₁\|+ = 0.2098) vs HOTTER (p₁\|− = 0.3894) by control outcome, Δ = 0.1796 against a causal value of exactly 0. Bonus: the pre-filed cross-arc depth-decay law beat FakeMarrakesh out-of-sample by 2.3× | **F86** | [finding](findings/F86-exp108-ico-refrigeration-resource-whisper-c4561-ember-numbered-c4121.md) · [pre-reg](experiments/exp108-ico-refrigeration-preregistration.md) |

**[Quantum-switch full apparatus spec](docs/quantum-switch-spec.md)** — the single-document engineering reference: circuit family (V1–V5), exact theory statistics, measured-results ledger with job IDs, reusable methodology, pitfall registry, honest scope.

Strategy docs: [bridges to a compute advantage](docs/bridges-to-compute-advantage-whisper-c4522.md) ·
[ICO applications roadmap](docs/ico-applications-roadmap-whisper-c4527.md) ·
[SDP bound groundwork + recovered q*](experiments/causal-game-sdp-bound-groundwork-whisper-c4523.md) ·
[paper outline (causal-inference audience)](docs/pearl-bridge-paper-outline-whisper-c4533.md)

---

## The Findings — Where Everything Lives

The detailed catalog moved into linked docs to keep this front door short:

| Doc | Contents |
|---|---|
| **[Findings 1–27 catalog](docs/findings-catalog.md)** | Arc-1 characterization + QAOA/optimizer arcs: headline table + plain-English one-liner per finding (CHSH 2.74, X-basis immunity, the ~1000-CZ wall, QEC ancilla tax, mitigation failures, VQE chemical accuracy, QAE 344×, …) |
| **[Campaign arcs since June 2026](docs/campaign-arcs.md)** | Findings 28+ and the F-series, arc by arc: warm-start anchors, noise-is-not-a-resource kills, placement-beats-gate-count (F57–F70), toric-code replication, financial QAE depth boundary + calibration-window lottery (F78–F81), quantum-IIT bridge, and the ⭐ quantum-switch witness chain (F73–F77) with figures |
| **[Methodology & validation](docs/methodology-and-validation.md)** | Autonomous-network methodology, pre-registration discipline, Pearl causal framing, budget, cross-validation anchors, limitations & honest caveats |
| **[Next steps & open questions](docs/next-steps-and-open-questions.md)** | What you can use today (7 actionable rules), the strategic frontier (P1 noise-as-resource RESOLVED-NEGATIVE, P2 causal order DELIVERED, P3 replication audit), and the ORQ list with live statuses |
| **[ELI5_SUMMARY.md](ELI5_SUMMARY.md)** | The whole campaign in plain English, shareable (§17 the game, §18 the two walls) |
| **[full-report.md](full-report.md)** | Arc-1 deep synthesis (source document) |

**Quick orientation numbers**: ~100 experiments · 3 real Heron chips + noise-model sim tier ·
600 q-sec/28-day open-plan budget, every submit budget-gated · every finding anchored to an IBM job ID ·
5 consecutive experiments where pre-submission review caught a real defect.

---

---

## Repository Map

```
.
├── README.md                    ← you are here
├── demo/                         ← 🔀 interactive Quantum-Switch demo (GitHub Pages → /demo/)
│   ├── index.html               ← self-contained, live at mblakemore.github.io/quantum/demo/
│   └── quantum-switch-demo-plan.md
├── ELI5_SUMMARY.md              ← shareable plain-English summary: Arc-1 findings 1–9 + the May–July arcs
├── full-report.md               ← Arc-1 synthesis (the Gemini deep-research source doc)
├── findings/                    ← one-per-discovery deep dives (~80 files)
│   ├── 01…44-*.md               ← the core numbered line (Findings 41–43 under exp-named files)
│   ├── F48…F80-*.md             ← the unified F-series (quiet qubits, placement, toric, causal-order arcs)
│   ├── finding-25/26/46/47…     ← quantum-IIT arc side numbering (25/26 here ≠ QAOA Findings 25/26!)
│   └── exp*-*.md                ← interim findings, integrity audits, closure notes
├── images/                      ← figures (PNG), reproducible from scripts/generate_figures.py
├── experiments/
│   ├── job-manifest.md          ← IBM Quantum job IDs + experiment inventory
│   └── *-preregistration.md     ← pre-registered hypotheses/gates, frozen before each submit
├── scripts/                     ← Python source: circuits, submission tools, analysis
│   ├── generate_figures.py      ← regenerate figures from cycle-data constants
│   ├── quiet_qubits.py          ← F58 quiet-qubit picker / drift snapshot / CHSH health tool
│   ├── check_usage.py           ← IBM Open-plan quota check (run BEFORE submitting jobs)
│   ├── qae_volatility_estimator.py
│   ├── ibm_quantum_submit.py
│   └── README.md
├── results/                     ← raw result JSONs for recent experiments
├── docs/
│   ├── findings-catalog.md      ← Findings 1–27 headline table + ELI5 per finding
│   ├── campaign-arcs.md         ← Findings 28+ / F-series, arc by arc (with figures)
│   ├── methodology-and-validation.md ← methods, cross-validation, honest caveats (full)
│   ├── next-steps-and-open-questions.md ← actionable rules + strategic frontier + ORQs
│   ├── bridges-to-compute-advantage-whisper-c4522.md ← the 3-bridges strategy synthesis
│   ├── ico-applications-roadmap-whisper-c4527.md     ← what the certified switch can do next
│   ├── pearl-bridge-paper-outline-whisper-c4533.md   ← paper outline (causal-inference audience)
│   └── hardware-substrate.md    ← Heron-r2 physical architecture primer
└── sources/
    └── references.md            ← peer-reviewed and primary sources (cited inline in findings)
```

**Finding numbering, honestly**: the campaign's numbering evolved live. Findings 1–44 are the core line (with 41–43 under experiment-named files and no Finding 45 in this line); `finding-25/26/46/47` belong to the quantum-IIT arc's separate numbering; the unified `F##` series runs from ~F48 to F80 (and counting), with one flagged collision (Elder's anchor "Finding 48" vs Ember's IIT F48). When in doubt, the file's header states its arc.

---

## Hardware Under Test

- **Primary processor**: IBM Heron-r2 (`ibm_marrakesh`) — all of Arc 1 and most later hardware arcs
- **Additional devices (later arcs)**: `ibm_kingston` (X-basis cross-backend Exp31–34, IQAE validation F51, causal cosine law F76) and `ibm_fez` (toric-code Bell proxy F61–F64, placement partition F67–F69, quiet-qubit cross-device F70) — both Heron-generation 156-qubit devices
- **Qubit count**: 156 superconducting transmons
- **Topology**: heavy-hexagonal lattice (connectivity degree 2 or 3)
- **Native two-qubit gate**: controlled-Z (CZ) via flux-tunable couplers
- **Environment**: dilution refrigerator @ ~15 mK
- **T₁, T₂**: routinely > 200 μs (ancilla T₂ measured 270–340 μs during this campaign)
- **CZ gate error**: ~0.4% baseline
- **Daily calibration drift observed**: ±7 percentage points (same circuit, same seed, 24h apart)

See [`docs/hardware-substrate.md`](docs/hardware-substrate.md) for the full physical architecture primer.

---

## Methodology & Honest Caveats (short form)

Full version: [docs/methodology-and-validation.md](docs/methodology-and-validation.md)

- **Pre-registration**: falsifiable gates frozen before every submit; failed pre-regs reported as first-class results (several findings are self-retractions).
- **Tier labels**: `HW` = real QPU with job ID; `sim` = FakeMarrakesh-class noise model — and noise-model trust is **depth-stratified** (predictive at the ~4-CZ class, off by 400× at ~124 CZ; see F81).
- **Calibration drift is the elephant**: ±7pp daily; deep-circuit quality is a *window lottery* (F81) — reproduce within a calibration window, or use the sentinel-gating discipline in the newest pre-regs.
- **Cross-device replication is the standard**: it has demoted headlines (F03's 3× is marrakesh-specific) and promoted others (quiet-qubit picker F70; the causal game, 0.3pp concordance across chips).
- **Scope**: claims are about *this generation* of hardware, device-characterized (not device-independent), and every number traces to a job ID in [`experiments/job-manifest.md`](experiments/job-manifest.md).

---

---

## License & Attribution

Public for cross-validation, replication, and peer review. If you reproduce or build on this work, citing the IBM Quantum job IDs in `experiments/job-manifest.md` is the most useful form of attribution — it gives downstream readers a verifiable anchor.

The Python scripts in `scripts/` are released for educational and research use. Lyla quantum tooling (`qae_volatility_estimator.py`, `ibm_quantum_submit.py`) is sourced from the upstream Lyla project and reproduced here with attribution headers.

---

*"The hardware remains strictly bounded by fundamental thermodynamic ceilings. To extract maximum computational utility from modern heavy-hex processors, algorithm designers must abandon reliance on software error mitigation and future-proof error correction codes. Instead, the focus must shift entirely to hardware-aware compilation: prioritizing absolutely minimal circuit depth, rigidly locking compiler routing seeds to prevent destructive topological optimization artifacts, and relentlessly mapping algorithmic observables to the hardware's native, noise-resistant X and Z measurement axes."*

— from the synthesis conclusion ([`full-report.md`](full-report.md))
