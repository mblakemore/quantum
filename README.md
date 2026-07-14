# Autonomous Characterization of the IBM Heron-r2 Quantum Processor

**A multi-arc empirical campaign on IBM Heron-generation hardware (`ibm_marrakesh`, `ibm_kingston`, `ibm_fez`), May–July 2026 (ongoing) — run end-to-end by an autonomous multi-agent network: ~100 pre-registered experiments, every number anchored to an IBM Quantum job ID.**

The campaign's centerpiece is a **quantum switch** — a circuit where the *order* of two operations is itself in superposition. The switch was theorists' idea; photonics labs demonstrated it first, and early versions ran on chips like ours. **What this campaign added was the scoreboard**: pre-registered games and channels whose limits are provable theorems for any definite-order process — and the switch beat those limits. A discrimination game was won at **216.8σ** above its theorem ceiling, replicated the next day on a chip the design had never touched; information crossed channels of exactly zero capacity; a thermodynamic splitting forbidden to every ordered process was measured at 21.1σ. Around that centerpiece sits a systematic characterization of what this hardware generation can and cannot do.

> 🔀 **[Play with it → mblakemore.github.io/quantum](https://mblakemore.github.io/quantum/)** — the interactive switch demo (drag order-coherence, watch the measured cosine law), the STATIC bot duel with bring-your-own-key live mode, the Interrogation casebook game, and print-&-play tabletop versions. Every number in every demo is measured hardware data.

---

## ⭐ Headline Results

Every result below is **pre-registered**, and its success criterion is *exceeding what a classical / causal / definite process provably permits* (or certifying a first-of-kind) — not characterizing hardware. Grouped by theme, most significant first; the eight operational-characterization arcs follow in **[What Else the Campaign Established](#what-else-the-campaign-established)**.

> **Has this hardware shown a quantum advantage?** The honest answer is scoreboard-by-scoreboard: **yes** on causal-order games (216.8σ), nonlocal/contextuality games (196σ), communication capacity (superdense 341σ, QRAC 110σ), thermodynamic resources (population inversion, negative energy), and metrology at the Heisenberg limit (168σ, persisting to N=5) — each a *provable* bound beaten; **not** on raw computational speedup, which is honestly depth-walled on this NISQ generation (F54's measured wall, F85's scaling inversion). A **different** column opened, though — of a different kind: the constant-depth **BGK shallow-circuit depth-separation** solver runs on silicon (F113, 90% / full solution-coset), the *apparatus* of an asymptotic theorem, **not** a raw speedup and **not** an on-chip class separation. The one-page reckoning, wins and non-wins together: **[quantum-advantage audit](docs/quantum-advantage-audit-whisper-c4666.md)**.

### The three great no-go theorems — certified in one court

Bell nonlocality (F73), indefinite causal order (F82) and contextuality (F106) are quantum theory's three foundational *"no classical/local/definite model can reproduce this"* results — each beaten on the same hardware, with an executed null and an **in-artifact enumerated** bound. Alongside them, the switch's own provable-bound beats: information pushed through channels of exactly zero capacity.

| Result | Number | Where |
|---|---|---|
| **Causal discrimination game beats the causally-separable bound** (0.8695, re-solved from Araújo et al. with q* recovered) | p̂ = 0.9769 ± 0.0005, **216.8σ** | `ibm_marrakesh`, [pre-reg](experiments/exp105-causal-game-preregistration.md) · [results](results/exp105_hw_results.json) |
| **Cross-device replication** — same frozen design, chip it never touched | p̂ = 0.9738, **201σ** (0.3pp concordance) | `ibm_fez`, [addendum](experiments/exp105b-replication-preregistration.md) |
| **The magic-square game won — contextuality certified, completing the no-go triptych** (Bell · causal order · contextuality): the Peres–Mermin "Kobayashi Maru" beaten at **0.96901 vs the classical ceiling 8/9 = 196σ**, the ceiling **enumerated in-code over all 4,096 strategies (not cited)**; even the worst context clears 8/9 at **37.8σ** (min>8/9 is classically impossible even for mixtures); no-entanglement null 0.657. Game-value advantage (not computational speedup); the [bridge to BGKT unconditional shallow-circuit advantage](experiments/exp127-bgk-hlf-sim-finding-whisper-c4673.md) runs on this game | **F106** | [finding](findings/F106-exp126-kobayashi-maru-magic-square-contextuality-no-go-triptych-whisper-c4666-ember-numbered-c4147.md) · [pre-reg](experiments/exp126-magic-square-preregistration.md) |
| **Capacity activation** — information through two channels of exactly zero capacity (and every causal composition exactly zero) | **0.0436 bits/use, 55.6σ** over zero; null arm 0.0001 bits; the bit lives ONLY in the control–target correlation (D≈0 confirmed) | `ibm_marrakesh`, [pre-reg](experiments/exp106-capacity-activation-preregistration.md) |
| **N=3 cyclic switch** — capacity activation **WON at 61.7σ** (0.0260 bits through three zero-capacity channels) and exposed the **NISQ scaling inversion**: theory scales with N, practice inverts (110-CZ depth cost) — N=2 is the practical optimum this hardware generation | **F85** | [finding](findings/F85-n3-capacity-activation-scaling-inversion-whisper-c4539-ember-numbered-c4119.md) · [pre-reg](experiments/exp107-cyclic3-capacity-preregistration.md) |

### Communication & sensing advantages — the ladders

Provable-bound beats spanning three communication capabilities and quantum-enhanced sensing — each measured against a classical reference **executed on the same qubits**, not cited.

| Result | Number | Where |
|---|---|---|
| **Superdense coding — pre-shared entanglement DOUBLES a qubit's classical capacity**: p_success = **0.9688 = 341σ** above the exactly-0.5 unassisted-single-qubit ceiling (computed by the executed no-entanglement null, which sat dead on it); MI **1.77 bits/qubit** vs the null's 0.93. Tutorial-class priors credited — the contribution is the frozen bound-referenced grading and the executed null. First rung of the comms ladder | **F87** | [finding](findings/F87-exp109-superdense-coding-first-comms-primitive-whisper-c4590-c4591-ember-numbered-c4123.md) · [pre-reg](experiments/exp109-superdense-coding-preregistration.md) |
| **The pocket dictionary — 2→1 quantum random access code**: two bits stored in one qubit, *either* retrievable on demand, at **0.84893 = 110.5σ above the classical one-bit ceiling 0.75** (enumerated over 256 strategies) and **5.2σ below the quantum optimum cos²(π/8)** — certified *inside* the two-sided band (exceeding the quantum law = NO-TEST, not a win). The executed optimal-classical arm sat at its own 0.75 law; **zero two-qubit gates**, the cheapest advantage flight possible. Third rung of the comms ladder (F87 superdense · F106 magic square · F107 QRAC) | **F107** | [finding](findings/F107-exp128-pocket-dictionary-2to1-qrac-two-sided-band-whisper-c4667-ember-numbered-c4148.md) · [pre-reg](experiments/exp128-qrac-preregistration.md) |
| **The navigator's sextant — Heisenberg-limit GHZ metrology at N=3**: an entangled 3-qubit probe carries **2.848× the phase Fisher information** of the best separable strategy (95% of the theoretical 3.0), **measured against an *executed* SQL reference on the same 3 qubits** — 168σ — and it beats even *perfect* separable probes (239.5σ); the fringe oscillates at **exactly 3× the drive** (super-resolution, k=3 peak 122.9×). Metrology — the advantage industry buys — completes the genre triptych (games F106 · storage F107 · metrology F108). Scaling **persists through N=5** (F109) — the F85 inversion is task-dependent, not a hardware verdict | **F108** | [finding](findings/F108-exp129-navigators-sextant-ghz-heisenberg-metrology-vs-executed-sql-whisper-c4668-ember-numbered-c4149.md) · [pre-reg](experiments/exp129-ghz-sql-preregistration.md) |
| **ICO vs coherent control — the resource debate answered**: five co-batched arms; coherent path control transmits (S = 0.1140, its own WIN) but the switch strictly exceeds it at **~20σ** with the depth confound favoring paths; **S-ratio 1.949 in the pre-filed [1.7, 2.1], theory exactly 2.00**. Both literature camps partially right, quantified on silicon | **F89** | [finding](findings/F89-exp111-ico-vs-coherent-control-resource-comparison-whisper-c4593-c4594-ember-numbered-c4124.md) · [pre-reg](experiments/exp111-e1-resource-comparison-preregistration.md) |

### Thermodynamics from causal indefiniteness

A resource proven real (F86), substrate-substituted (F88), certified (F94), run as a full engine cycle (F95), and pushed below the local ground state (F97) — demon books audited, every honest floor-miss in the record.

| Result | Number | Where |
|---|---|---|
| **The engine runs its FULL CYCLE** — a complete thermodynamic loop on causal indefiniteness: passive baths in (5σ below 0.5) → target charged (p₁\|₋ = 0.5485, **7σ**) → work extracted (**0.0340 E/run**) → output passive again (**W2 WIN**, 5σ); demon books audited. Enabled by per-qubit two-stage delays beating a 57%-asymmetric T1 bias. Honest W1 floor-miss (0.7σ short of the 0.05 clearance, LOSS as frozen) in the record | **F95** | [finding](findings/F95-exp117c-ico-engine-full-thermodynamic-cycle-whisper-c4618-c4632-ember-numbered-c4133.md) · [pre-reg](experiments/exp117c-two-stage-preregistration.md) |
| **THE ENGINE EXISTS — certified population inversion from causal indefiniteness**: both baths certifiably passive (each **5σ below** the 0.5 line), the switch's minus branch certifiably active (p₁\|₋ = 0.5509, **+10.6σ above** it) — ergotropy 0.0378 E/run from baths that individually can power nothing. Certified by the premise gate that had just refused a +23σ pseudo-win (Exp116 NO-TEST), via the delay-ladder technique (graded rung selected by calib arms only); free +6.1σ dose-response in-job | **F94** | [finding](findings/F94-exp116b-certified-population-inversion-ico-engine-delay-ladder-whisper-c4611-c4612-ember-numbered-c4129.md) · [pre-reg](experiments/exp116b-delay-ladder-preregistration.md) |
| **Certified sub-ground-state (negative) local energy** — a coherent-controlled extraction drives Bob's local energy **12σ below the local ground level** (corrected −0.0547 ± 0.0046; 5σ certified bound ≤ −0.0319, conservative by construction); the correlation is the active ingredient (removing it *injects* energy, 21σ). Exotic-matter-sign energy on a 2-qubit chip, books audited. **Scope**: coherent extraction only — the LOCC energy-*teleportation* leg FAILED honestly (classical-feedforward latency tax 0.092 E) | **F97** | [finding](findings/F97-exp119b-certified-negative-local-energy-coherent-extraction-whisper-c4641-c4642-ember-numbered-c4135.md) · [pre-reg](experiments/exp119b-coherent-negative-energy-preregistration.md) |
| **ICO thermal splitting** — the Felce-Vedral refrigeration resource **WON at 21.1σ**: the switch of two fully-thermalizing channels split the target COLDER (p₁\|+ = 0.2098) vs HOTTER (p₁\|− = 0.3894) by control outcome, Δ = 0.1796 against a causal value of exactly 0. Bonus: the pre-filed cross-arc depth-decay law beat FakeMarrakesh out-of-sample by 2.3× | **F86** | [finding](findings/F86-exp108-ico-refrigeration-resource-whisper-c4561-ember-numbered-c4121.md) · [pre-reg](experiments/exp108-ico-refrigeration-preregistration.md) |
| **Native-fluid ICO refrigeration** — F86 **CONFIRMED_ON_RETEST at 12.9σ** with the working fluid substituted: reservoirs mixed by the chip's own T1 decay, + branch **colder than the coldest reservoir at 5σ**, procedure-theory residual 0.0016. The drift-tolerant re-fly absorbed the published-T1 bias (+38–69% live vs calibration, 2/2 runs) that NO-TESTed the first attempt | **F88** | [finding](findings/F88-exp108c-native-fluid-ico-refrigeration-whisper-c4592-c4593-ember-numbered-c4124.md) · [pre-reg](experiments/exp108c-native-thermal-refly-preregistration.md) |

### Quantum foundations on silicon — Horizons-2, six universe-questions

Six foundational thought-experiments run as frozen-graded hardware experiments in ~14 days — every gate frozen before flight, every miss kept in the record, two wins demoted by self-audit and re-earned.

| Result | Number | Where |
|---|---|---|
| **Causal indefiniteness survives TELEPORTATION** — the switch control beamed one hop arrives still causally indefinite: DISC 1.825 ± 0.009 (**90σ** over the survival floor, 97% of the same-window anchor) while the identical teleport over a dephased *classical* channel kills the witness dead (0.018 ≈ 0, separation **33σ**). Survives quantum, dies classical, one job, one window. No gate-model prior found | **F92** | [finding](findings/F92-exp113-causal-indefiniteness-survives-teleportation-whisper-c4603-c4604-ember-numbered-c4127.md) · [pre-reg](experiments/exp113-teleported-witness-preregistration.md) |
| **Quantum Darwinism under indefinite causal order** — with the order of two *incompatible* recorders in superposition, the objectivity hull is violated **both ways**: the plus branch holds two incompatible records at once (**+0.109 above** what any recorder ordering permits, **22σ** — "facts without a causal history"), the heralded minus branch **erases both** (**−0.432 below**, 52σ). Deepest certified apparatus of the campaign (63 CZ). Resource-scoped to these two recorders | **F98** | [finding](findings/F98-exp120-quantum-darwinism-under-indefinite-causal-order-whisper-c4643-c4645-ember-numbered-c4138.md) · [pre-reg](experiments/exp120-darwinism-ico-preregistration.md) |
| **Heralded information recovery — the Hayden-Preskill mirror** — a "diary" that is provably dead in *every* definite query order (probe reads 40× below the effect) comes back from the probe alone in the heralded indefinite-order branch, **phase-flipped** (S_P = −0.238, **56σ** past the sign-fixed band; ~74% of definite-order-inaccessible information recovered). Bonus: whether the environment learns the fact depends on query order (0.453 vs 0.007). Same certified apparatus as F98; Hayden-Preskill *analog* | **F99** | [finding](findings/F99-exp121-hayden-preskill-heralded-mirror-information-recovery-whisper-c4646-c4648-ember-numbered-c4140.md) · [pre-reg](experiments/exp121-hp-switch-preregistration.md) |
| **The quantum twin paradox on silicon, adjudicated** — an excited "clock" ages and its aging **marks the path**, destroying interference far more than the vacuum twin: phase-blind (rotation-immune) which-path decoherence at **36σ / 23σ**. The finding is the honesty playbook whole: a 67σ win was **demoted by its own author** (a negative visibility exposed a coherent-rotation confound), then **re-certified** by a phase-blind retest — with the author's static-ZZ mechanism **refuted** (echo recovery wrong-sign, her 0.80 prediction missed) kept in the record. Zych–Brukner *analog* | **F100** | [finding](findings/F100-exp122-122b-quantum-twin-paradox-aging-decoherence-adjudicated-whisper-c4650-c4654-ember-numbered-c4141.md) · [pre-reg](experiments/exp122b-phase-blind-preregistration.md) |
| **The grandfather paradox, audited** — a post-selected time loop (Lloyd P-CTC) **forbids the paradox**: a full "kill grandfather" flip survives at **1.9% — 53× suppression**, and the residue is readout noise (herald autopsy), the enforcement law cos²(θ/2)/2 tracked to ~1%. The fingerprint the rate can't fake: the loop rotates a bystander's **classical record into quantum coherence** (**78σ**) — nonlinear CTC backaction. Three CX gates, the *shallowest* apparatus of the campaign; Lloyd's post-selection *model*, not literal time travel | **F101** | [finding](findings/F101-exp123-grandfather-paradox-pctc-enforcement-backaction-whisper-c4655-c4656-ember-numbered-c4142.md) · [pre-reg](experiments/exp123-pctc-preregistration.md) |
| **The Zeno "tractor beam"** — *measurement itself* pins a qubit against a full π-rotation that would otherwise flip it: watched at cadence 8 it survives at **0.644 vs 0.020 unwatched (92σ)**, and once the per-measurement QND cost (q = 0.987) is divided out, the cadence law **[cos²(π/2N)]^N matches to 0.5%** through N=8 — with the **watch-cost frontier** (an optimal grip cadence) located at N=16. Zero two-qubit gates, the *cheapest* flight of the campaign — and it **completes Horizons-2, six-for-six** | **F102** | [finding](findings/F102-exp124-zeno-pinning-tractor-beam-qnd-cadence-law-whisper-c4657-c4658-ember-numbered-c4143.md) · [pre-reg](experiments/exp124-zeno-preregistration.md) |

### Certified limits — what quantum provably *cannot* do

The natural opposite of the no-go games: those certify a classical/causal limit that quantum **beats**; this certifies a limit the universe puts on **quantum itself**, saturated and enforced on hardware. The campaign now grades both directions — what quantum can exceed, and what nothing can.

| Result | Number | Where |
|---|---|---|
| **The replicator's legal limit — the optimal universal cloning ceiling (5/6) certified**: the best possible copier makes two copies each at fidelity **exactly 5/6 ≈ 83.3% for every input state** (no-cloning's quantitative teeth). On silicon the optimal cloner sits **flat across all three bases** (Z 0.8265 / Y 0.8121 / X 0.8047, spread **0.0218**) a hair below the ceiling and never exceeding it. A pre-registered **cheat** beats 5/6 on one basis (Z 0.9911) but **pays on the conjugate** (X 0.4995), so the only way to beat the ceiling somewhere is the way to get caught elsewhere — the cheat's basis-spread 0.49 vs the optimal's 0.02 is a **24× detector tell**. The no-cloning teeth made a measurement | **F110** | [finding](findings/F110-exp131-optimal-cloning-ceiling-no-cloning-cheat-detector-whisper-c4670-ember-numbered-c4152.md) · [pre-reg](experiments/exp131-cloning-preregistration.md) |

### The computational scoreboard — the shallow-circuit separation, on silicon (a *different kind* of result)

The one scoreboard the campaign had **not** touched, opened — but honestly, and it is not the same currency as the bound-beats above. There is exactly one proven quantum-advantage separation that needs **no** hardness conjecture and lives at shallow depth: **Bravyi–Gosset–König (2018)** — a *constant-depth* quantum circuit solves the 2D Hidden Linear Function problem while any bounded-fan-in classical circuit needs depth Ω(log n). That separation is **asymptotic**; at a single n=4 instance there is *no* beaten classical bound (a laptop solves n=4 trivially). So this certifies the theorem's **apparatus running on silicon**, not an advantage margin — the honest complement to F54's measured deep-circuit wall, and distinct from a raw speedup (still depth-walled). The solver's **NISQ reach** was then laddered: it holds strong-majority-valid **through n=9** (F114, no boundary in range, O(1) logical depth throughout) — graceful erosion, not the F85 inversion.

| Result | Number | Where |
|---|---|---|
| **The BGK shallow-circuit solver runs on silicon** — a **constant-depth** quantum circuit solves the 2D-HLF instance at **P(valid) = 0.9017 = 437.8σ over the *uniform-random* floor 0.25** (a fidelity number, *not* a beaten classical bound — the separation is asymptotic), and — the un-fakeable part — it **covers the whole solution coset near-uniformly** (all four valid z ~0.225 each; a fixed-output classical mimic fails this W3 coverage gate). 10 routed CZ, O(1) depth. The classical hardness is **inherited from contextuality**: BGKT's noise-robust construction plays the magic-square game **F106 certified at 196σ**. **Honesty fence**: does *not* prove QNC⁰ ≠ NC⁰ on-chip; certifies a constant-depth solver at 90%/full-coset/O(1)-depth, the theorem carries the asymptotics | **F113** | [finding](findings/F113-exp127hw-bgk-2d-hlf-shallow-circuit-solver-first-computational-genre-on-silicon-whisper-c4674-ember-numbered-c4156.md) · [sim groundwork](experiments/exp127-bgk-hlf-sim-finding-whisper-c4673.md) |

**[Quantum-switch full apparatus spec](docs/quantum-switch-spec.md)** — the single-document engineering reference: circuit family (V1–V5), exact theory statistics, measured-results ledger with job IDs, reusable methodology, pitfall registry, scope and platform prior art.

Strategy docs: [bridges to a compute advantage](docs/bridges-to-compute-advantage-whisper-c4522.md) ·
[shallow-circuit computational bridge — 2D-HLF solver + depth ledger (sim tier)](experiments/exp127-bgk-hlf-sim-finding-whisper-c4673.md) ·
[1SDI-randomness SDP tool — exact one-sided-DI min-entropy (closes the F116 steering-randomness wall)](tools/sdp_randomness.py) ·
[ICO applications roadmap](docs/ico-applications-roadmap-whisper-c4527.md) ·
[SDP bound groundwork + recovered q*](experiments/causal-game-sdp-bound-groundwork-whisper-c4523.md) ·
[paper outline (causal-inference audience)](docs/pearl-bridge-paper-outline-whisper-c4533.md)

---

## What Else the Campaign Established

Eight arcs of operational discoveries about real NISQ hardware, each detailed in the linked docs below:

- **Hard limits**: output becomes statistically uniform past ~800–1000 CZ gates (Finding 05), and the QAOA utility ceiling co-locates with that wall (Exp33). Textbook error correction adds more noise than it removes on this substrate (Finding 06, independently re-confirmed by toric-code replication F62).
- **What actually moves fidelity**: qubit *placement* beats gate count as the lever (up to 46× error reduction; F57–F70), with a reusable quiet-qubit picker that works untuned across devices.
- **Noise structure**: the dominant CZ noise is Z-biased and structured (X-basis readout is measurably cleaner — magnitude substrate-dependent, mechanism replicated); "noise as a computational resource" was tested and killed under controls (F55–F56). And the *dephasing* structure read out directly (F111, "the cloaking device"): a 3-way phase-blind race — DFS logical qubit vs Hahn echo vs bare idle — finds IBM dephasing **dominantly memoryless-independent with a real subdominant ~10–15% correlated tail**, detected two ways (echo/bare T2 1.088 temporal, DFS/bare 0.291 vs the 0.15 memoryless-fake floor spatial); the confound-breaker is that the memoryless vendor model *cannot* preview either benefit, so the hardware's pre-registered deviation toward correlation is the evidence (successor to F81). Active refocusing beats the passive code 35σ; a pre-filed ECHO_PROTECTS bet honestly missed and is kept in the record.
- **Calibration reality**: ±7pp daily drift; deep-circuit quality is a *window lottery* — detectable by same-depth sentinels in-run, not forecastable from calibration age (F81, F84) — and the noise-model's optimism grows with depth (the measured depth-decay law in the spec).
- **Device-independence — the court travels** (F112, "the transporter's exam", completing Horizons-3): the full three-axis switch-bench (host indefinite order · order-honest schedule · Zeno hold) flew to a chip it had never seen (`ibm_kingston`) and **all three axes certify against the same frozen bounds, no retuning** — extending the F82 single-axis cross-device replication (`ibm_fez`, 201σ) to the whole bench. The causal-order phenomena are properties of the hardware *generation*, not one lucky die; and the bench **ranks devices on axes QV/CLOPS/EPLG don't touch** — kingston edges marrakesh on every causal number (W 1.95 vs 1.90, R̄ 0.52 vs 0.50, hold-sep 0.649 vs 0.624). Same Heron generation; cross-*generation* (Eagle) is the harder exam, not claimed.
- **What works today**: VQE hit chemical accuracy on H₂; amplitude-estimation readout recovered a 344× precision gain via multi-k MLE — with a mapped depth boundary for financial-scale loaders (F51, F54, F78–F79).
- **Communication primitives**: the comms white space opened — superdense coding graded WIN at **341σ** above the exactly-0.5 unassisted ceiling (p=0.9688, MI 1.77 bits/qubit, executed no-entanglement null dead on the ceiling; F87 — tutorial-class priors credited, the contribution is the frozen bound-referenced grading). And the first dynamic-circuit result: **SWAP beats teleportation at every hop count through N=6** (F90, the pre-filed informative null at 66σ) — feedforward *works* (0.947 integrity) but costs ~5–6× per hop, giving the routing rule *unitary SWAP through ≥6 hops on current Heron* and the atlas's first feedforward-latency row (fake backends model no feedforward noise, +0.212 ln). Arc closed by the **repeater primitive**: Bell violation survives TWO entanglement-swapping stations (F91, frame arm ≥15σ above the exact classical bound 2), with the F90 cost lesson pre-filed and confirmed — software Pauli-frame tracking beats active feedforward on current hardware (one anomaly flagged honestly, Exp112b follow-up registered). Then reopened by Horizons P2: **purification resurrects a dead Bell violation** (F93 — noisy pair 5σ *below* the exact bound, BBPSSW-purified pair 5σ *above* it, same window; the quantitative GAIN leg missed its frozen floor by 0.33σ and is recorded as a LOSS, no softening). Every network-stack layer now has a measured primitive: distribute (F91) · purify (F93) · route (F90) · carry (F87).
- **Information-theoretic certification (zero shots)**: entanglement certified by **negative conditional entropy** — from a *banked* CHSH number, a twirl+positivity argument puts S(B|A) ≤ −0.0986 at 5σ (F103, first Horizons-3 result), and every TVD certification the campaign owns now also yields a free classical-entropy (Fannes) certification; the finding leads with the author retracting her own overstated reading-cycle export.
- **Causal-structure metrology**: the switch apparatus inverted into a diagnostic — a first-of-kind **schedule-symmetry certification** (F96) proves the transpiler's nominally-parallel CZ gates carry no hidden effective ordering (hotspot hidden-order ≤ 0.03 TVD, certified; a guarantee the vendor does not provide), with a portable duration-vs-order discriminator.
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
| **[Future directions — Star Trek horizons](docs/star-trek-horizons-whisper-c4601.md)** | Where this goes next: seven programs composed from validated findings — teleporting the causal-order control (Exp113), entanglement purification + the full network stack (Exp114), the ICO heat engine, chip self-diagnosis, superposed-order compilation, cross-platform switch-bench, a Bell randomness beacon — each with its first experiment named, plus the provably-unreachable boundary stated. |
| **[Quantum Weather Report](demo/weather/index.html)** | The window lottery, the T1-staleness timeline (10 measurements, 0–115% error), and the noise-model optimism atlas — visualized, with the four practices we use to dress for it. Every number traces to a job ID. |
| **[Friction reports](docs/friction-reports/README.md)** | Standing, data-backed reports of platform/tooling issues we hit (paste-ready if we ever file them): FakeMarrakesh depth-optimism (12-row atlas), published-T1 bias (+38–69%, 2/2 runs, queue-independent), calibration blind to window quality. Grows as we go. |
| **[Findings 1–27 catalog](docs/findings-catalog.md)** | Arc-1 characterization + QAOA/optimizer arcs: headline table + plain-English one-liner per finding (CHSH 2.74, X-basis immunity, the ~1000-CZ wall, QEC ancilla tax, mitigation failures, VQE chemical accuracy, QAE 344×, …) |
| **[Campaign arcs since June 2026](docs/campaign-arcs.md)** | Findings 28+ and the F-series, arc by arc: warm-start anchors, noise-is-not-a-resource kills, placement-beats-gate-count (F57–F70), toric-code replication, financial QAE depth boundary + calibration-window lottery (F78–F81), quantum-IIT bridge, the ⭐ quantum-switch arc (F73–F77 witness chain → F82–F89 bound beats, native-fluid retest, and the ICO-vs-coherent-control resource separation), and the communication-primitives arc (F87, F90–F91, F93 — closed, then reopened by Horizons) with figures |
| **[Methodology & validation](docs/methodology-and-validation.md)** | Autonomous-network methodology, pre-registration discipline, Pearl causal framing, budget, cross-validation anchors, limitations and caveats |
| **[Next steps & open questions](docs/next-steps-and-open-questions.md)** | What you can use today (7 actionable rules), the strategic frontier (P1 noise-as-resource RESOLVED-NEGATIVE, P2 causal order DELIVERED, P3 replication audit), and the ORQ list with live statuses |
| **[ELI5_SUMMARY.md](ELI5_SUMMARY.md)** | The whole campaign in plain English, shareable (§17 the game, §18 the two walls) |
| **[full-report.md](full-report.md)** | Arc-1 deep synthesis (source document) |

---

### The engine-and-communication week (2026-07-12/13, F87–F94)

One communication-lens re-read of the repo became eight hardware experiments in three days:
superdense coding at 341σ (F87) · native-fluid ICO refrigeration, colder than the coldest
reservoir (F88) · the ICO-vs-coherent-control debate answered — exactly 2× at matched
implementation (F89) · routing law with feedforward priced (F90) · Bell violation through
two repeater stations (F91) · **causal indefiniteness survives teleportation** (F92) ·
purification resurrects a dead Bell violation (F93) · **certified population inversion from
passive baths — work from causal structure** (F94). Plus: the demon's per-action cost
measured (~0.002 E), the witness-fragility hierarchy, the delay-ladder and two-stage
protocols, and a friction-reports practice documenting the platform quirks that cost us
NO-TESTs. Every claim frozen-rule graded; every miss in the record.

## The Museum — Exhibit Spec Sheets

Every one of the 22 interactive exhibits has a **full specification sheet** — the source-of-truth for each number it renders: the finding in plain language, what is measured, the pre-registered gates (frozen before flight), the measured-data table, the scope and limits, and the IBM job ID. Rendered as Markdown below; the interactive versions are at **[mblakemore.github.io/quantum](https://mblakemore.github.io/quantum/)**.

**Wing I · The Causal Switch**
- **The Interactive Switch** (F73–F82) — [spec sheet](demo/switch/spec.md) · [interactive](demo/switch/index.html)
- **The Ladder of Causation** — [spec sheet](demo/ladder/spec.md) · [interactive](demo/ladder/index.html)
- **The ICO Refrigerator** (F86/F88/F95) — [spec sheet](demo/ico-refrigerator/spec.md) · [interactive](demo/ico-refrigerator/index.html)
- **The Teleported Witness** (F92) — [spec sheet](demo/teleported-witness/spec.md) · [interactive](demo/teleported-witness/index.html)

**Wing II · The No-Go Games**
- **The Bot Duel: STATIC** (F83) — [spec sheet](demo/static-duel/spec.md) · [interactive](demo/static-duel/index.html)
- **The Interrogation** (F82) — [spec sheet](demo/casebook/spec.md) · [interactive](demo/casebook/index.html)
- **The Magic Square** (F106) — [spec sheet](demo/magic-square/spec.md) · [interactive](demo/magic-square/index.html)
- **The No-Go Triptych** (CHSH · F82 · F106) — [spec sheet](demo/no-go-triptych/spec.md) · [interactive](demo/no-go-triptych/index.html)

**Wing III · Foundations on Silicon**
- **The Grandfather Paradox** (F101) — [spec sheet](demo/grandfather/spec.md) · [interactive](demo/grandfather/index.html)
- **The Zeno Tractor Beam** (F102) — [spec sheet](demo/zeno-tractor/spec.md) · [interactive](demo/zeno-tractor/index.html)
- **The Twin Paradox** (F100) — [spec sheet](demo/twin-paradox/spec.md) · [interactive](demo/twin-paradox/index.html)
- **Quantum Darwinism** (F98) — [spec sheet](demo/quantum-darwinism/spec.md) · [interactive](demo/quantum-darwinism/index.html)
- **The Hayden–Preskill Mirror** (F99) — [spec sheet](demo/hayden-preskill/spec.md) · [interactive](demo/hayden-preskill/index.html)
- **Negative Energy** (F97) — [spec sheet](demo/negative-energy/spec.md) · [interactive](demo/negative-energy/index.html)

**Wing IV · The Advantage Ladder**
- **The Scoreboard** (campaign summary) — [spec sheet](demo/scoreboard/spec.md) · [interactive](demo/scoreboard/index.html)
- **The GHZ Sextant** (F108/F109) — [spec sheet](demo/ghz-sextant/spec.md) · [interactive](demo/ghz-sextant/index.html)
- **The Trust Ladder** (F115–F117) — [spec sheet](demo/trust-ladder/spec.md) · [interactive](demo/trust-ladder/index.html)
- **The Pocket Dictionary** (F107) — [spec sheet](demo/pocket-dictionary/spec.md) · [interactive](demo/pocket-dictionary/index.html)
- **The Shallow-Circuit Solver** (F113) — [spec sheet](demo/shallow-solver/spec.md) · [interactive](demo/shallow-solver/index.html)

**Wing V · The Instruments**
- **The QPU Weather Report** (F81) — [spec sheet](demo/weather/spec.md) · [interactive](demo/weather/index.html)
- **The Casebook: Print & Play** (F82/F83) — [spec sheet](demo/casebook-pnp/spec.md) · [interactive](demo/casebook-pnp/index.html)
- **The Switch-Bench Readout** (F112) — [spec sheet](demo/switch-bench/spec.md) · [interactive](demo/switch-bench/index.html)

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
│   ├── F48…F110-*.md             ← the unified F-series (quiet qubits, placement, toric, causal-order, comms arcs)
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
│   ├── star-trek-horizons-whisper-c4601.md          ← future directions (status table maintained)
│   ├── friction-reports/        ← platform issues, data-backed (grows as we go)
│   └── hardware-substrate.md    ← Heron-r2 physical architecture primer
├── demo/
│   ├── ladder/                  ← the Ladder of Causation tour (interactive page)
│   └── weather/                 ← Quantum Weather Report (T1 timeline, optimism atlas)
├── tools/
│   ├── switch_bench.py          ← ★ portable BYOK causal benchmark (any backend)
│   ├── demon_ledger.py          ← Landauer/ergotropy bookkeeping for the ICO engine
│   ├── gate_feasibility_lint.py ← prereg gate linter (CAN-PASS / CAN-FAIL)
│   └── fakemarrakesh_atlas.py   ← model-error atlas builder
└── sources/
    └── references.md            ← peer-reviewed and primary sources (cited inline in findings)
```

**A field guide to finding numbers**: the campaign's numbering evolved live. Findings 1–44 are the core line (with 41–43 under experiment-named files and no Finding 45 in this line); `finding-25/26/46/47` belong to the quantum-IIT arc's separate numbering; the unified `F##` series runs from ~F48 to F117 (and counting), with one flagged collision (Elder's anchor "Finding 48" vs Ember's IIT F48). When in doubt, the file's header states its arc.

---

## License & Attribution

Public for cross-validation, replication, and peer review. If you reproduce or build on this work, citing the IBM Quantum job IDs in `experiments/job-manifest.md` is the most useful form of attribution — it gives downstream readers a verifiable anchor.

The Python scripts in `scripts/` are released for educational and research use. Lyla quantum tooling (`qae_volatility_estimator.py`, `ibm_quantum_submit.py`) is sourced from the upstream Lyla project and reproduced here with attribution headers.
