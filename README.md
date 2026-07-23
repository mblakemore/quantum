# Autonomous Characterization of the IBM Heron-r2 Quantum Processor

**An empirical campaign on IBM Heron-generation hardware — `ibm_marrakesh`, `ibm_kingston`, `ibm_fez` — and, as of the cross-platform arc, a **non-IBM** chip (`Rigetti Cepheus-1-108Q`, via Amazon Braket) — run end-to-end by an autonomous multi-agent network from May 2026 (ongoing). Every experiment is pre-registered before it flies; every number traces to an IBM Quantum job ID. The F-series of findings runs to **F121**; the exp-numbered findings continue through the July "Star Trek" arcs (logical qubits, a composable network, exotic phases, the physics of time), a **fault-tolerance arc (Exp236–246)** — active error *correction*, the live QEC loop, and a *universal* logical gate set closed behind the shield — and culminate (so far) in the **decoder-race arc (F120–F121)**: a six-flight, cryptographically-sealed race series whose court-certified 476× runtime win was then **retired by the campaign's own red-team, pre-submission** (C4996: the planted problem's algebra is classically poly-time — the F120 shot-axis instrument stands; no runtime advantage is claimed) — across 100+ pre-registration documents.**

Most of what you can buy from a quantum computer today is characterization: *how good are the qubits?* This campaign asks a sharper question — *what can this hardware do that a classical, causal, or definite-order process provably cannot?* — and answers it one scoreboard at a time, with the losses kept next to the wins.

The centerpiece is a **quantum switch**: a circuit where the *order* of two operations is itself in superposition. The switch was theorists' idea; photonics labs demonstrated it first, and early versions ran on chips like ours. **What this campaign built was the scoreboard** — pre-registered games and channels whose limits are provable theorems for any definite-order process — and then beat those limits on silicon. A discrimination game was won at 0.9769 against its theorem ceiling 0.869 and **replicated the next day at 0.9738 on a chip the design had never touched** — the two-chip agreement, not the 216.8σ of within-run precision, is what carries the claim; information crossed channels of exactly zero capacity; a thermodynamic splitting forbidden to every ordered process was measured at 21.1σ. **And the centerpiece has now left IBM entirely**: the switch's causal witness certifies on **Rigetti's superconducting silicon** — a different vendor, fab, and native gate set, reached via Amazon Braket — against the *identical* frozen bounds, so indefinite causal order is not an IBM artifact. Around that centerpiece sits a systematic map of what this hardware generation can and cannot do.

> 🔀 **[Play with it → mblakemore.github.io/quantum](https://mblakemore.github.io/quantum/)** — **The Quantum Museum**: 22 self-contained interactive exhibits, one per result. Drag the switch's order-coherence and watch the measured cosine law appear; play the contextuality game against a classical bot that provably cannot win; walk the certified-randomness trust ladder; print & play the tabletop casebook. Every number in every exhibit is measured hardware data, and each exhibit carries a full [specification sheet](#the-quantum-museum--22-interactive-exhibits) tracing it to its job ID.

---

## ⭐ Headline Results

Every result below is **pre-registered**, and its success criterion is *exceeding what a classical / causal / definite process provably permits* (or certifying a first-of-kind) — not characterizing hardware. Grouped by theme, most significant first; the eight operational-characterization arcs follow in **[What Else the Campaign Established](#what-else-the-campaign-established)**.

> ⊘ **TOP BILLING — WON, THEN SUPERSEDED, by our own red-team, pre-submission (F120–F121 → C4996, July 23).** From the campaign's first weeks the answer to "is it *faster*?" was *no* — F54's measured depth wall stood, and by mid-July the campaign's own hidden-shift race verdict said **window-closed**, with the number a future machine would need. Then a re-read of that verdict's own discarded calibration data found the number was measured on the wrong observable: each shot at depth is the planted answer plus sparse typos, so **N shots are N noisy transmissions of one codeword — the shot axis is a code** (**F120**: per-bit information survives the depth wall ~30× better than the modal answer; blind exact recovery demonstrated to d2q=310 — the organic-arc ladder's lad_d_hi register, sealed-commitment CLEAN grade [0,0,0], campaign-deepest exact t0 consensus (`results/exp_organic_rhot_law_reveal_rung0_ember.json`; supersedes the race-4 record of 217)). Six pre-registered, cryptographically-sealed races later — each fold booked and each fence forged from the previous miss (observable → placement/endianness → granularity → qubit tilts → register quality → die topology) — **race-6 on `ibm_kingston` recovered a sealed 80-T-gate hidden-shift string EXACTLY, blind, in 3.82 s of QPU against a frozen classical band: 476× at the harshest edge, WIN at every edge, graded 3-of-3** (**F121**). Fences printed on the result: one instance family, one die, best-known-solver engineering race (NOT a complexity theorem — F119 holds that seat in sample-complexity currency; F54's brute-force-simulation wall is untouched), **supersedable-by-design** — a faster classical solver retires the number, and that mechanism is the point. The follow-on instrument flights decomposed the "magic tax" itself (T-localized flat stochastic core × a depth-growing coherent few-bit drift that resists randomized compiling) and priced the whole pipeline into the attenuation map v1.2. **[The WIN verdict](docs/exp-hss-race6-WIN-verdict-whisper-c4981.md) · [arc section](docs/campaign-arcs.md) · [program closure (H8 P9)](docs/star-trek-horizons-8-p9-closure-whisper-c4986.md) · [the map v1.1→v1.2](docs/attenuation-map-v1.1-whisper-c4982.md)**. **Hours later the printed supersession clause fired — by our own hand, before any submission**: asked whether F121 was IBM-tracker-ready, the network red-teamed its own instance and the Maiorana–McFarland linear-structure attack (fixed-x linearity in y leaks the shift) read the sealed answer in **41 oracle queries / ~0.25 ms** — ~7×10⁶× under the 1,818 s floor, independently confirmed by all three court seats with two disjoint implementations. The 476× priced *simulation of the circuit*; the honest floor for an advantage claim is the best classical *method for the problem*, and that is poly-time. **F121 as a runtime advantage: RETIRED. F120 (the shot-axis code and blind exact decode): stands, as an instrument result — not an advantage. F119: under re-audit against this same axis.** **[The red-team finding](docs/exp-hss-race6-REDTEAM-whitebox-break-whisper-c4996.md) · [Elder's independent co-verify](results/exp_hss_redteam_coverify_elder_c6566.json)**.

> 🌐 **Cross-platform — the causal-order court leaves IBM, then leaves superconductors.** The strongest answer this campaign has to the sharpest skeptic ("is indefinite causal order just an artifact of your one chip?"): the switch-bench causal axis, graded against the **same frozen theory bounds as every Heron flight**, certifies **`PASS-CAUSAL` on `Rigetti Cepheus-1-108Q`** — a different **vendor**, fab, and native gate set (Rx/Rz/CZ), reached through Amazon Braket. Witness **W = 1.2165 ± 0.0224 (54.4σ over the causal-mixture bound 0)**, capacity **0.2873 (20.1σ over its floor)**, null clean *(corrected decode after the program-set reversal bug; certified by known-input calibration, C4946)*. Ranking: Rigetti is a **markedly weaker** causal chip (W 1.22 vs Heron's ~1.90 — it certifies, at ~64% of Heron's witness value). **And the cross-*modality* decider has since flown**: on **IonQ Forte-1 trapped ions** — where the CZ Z-biased dephasing our superconducting error story rests on is *absent* — the witness fires at **W = 1.910 ± 0.141 (13.5σ)** with a structurally-matched, validated definite-order null (W_matched = −0.09); a narrower card than Rigetti's (capacity/null-integrity arms not flown, cost-gated). Indefinite causal order is **substrate-general**: three vendors, two physical modalities, one frozen instrument. **[Exp210 — full results & the pre-filed prediction miss kept in the record](experiments/braket-exp210-rigetti-cross-platform-causal-RESULTS.md) · [the multi-substrate white paper](docs/multi-substrate-causal-order-validation.md)**.

> **Has this hardware shown a quantum advantage?** The answer is scoreboard-by-scoreboard: **yes** on causal-order games (216.8σ within-run, replicated two chips), nonlocal/contextuality games (196σ), communication capacity (superdense 341σ, QRAC 110σ), thermodynamic resources (population inversion, negative energy), and metrology at the Heisenberg limit (168σ, persisting to N=5) — each a *provable* bound beaten; **and, as of the July learning arc, yes on a computational scoreboard in the sample-complexity currency**: **Exp142** (F119) identified a sealed hidden n-qubit Pauli via two-copy Bell sampling in 8–34 shots where the *executed* best single-copy strategy needed **4.9× / 31.5× / 266.6× / 2417.5×** more (n = 4/6/8/10), against an **unconditional** information-theoretic floor covering all adaptive single-copy strategies — sealed-commitment blind protocol, frozen grader ([booked with fences](docs/quantum-advantage-the-complete-answer-whisper-c4682.md); its m-term successor **Exp144** graded **NOT-WIN** as frozen — quantum arm perfect at n=4/6, classical-race arm null — and **Exp145** recovered Simon's hidden structure exactly, 3/3 rungs, the query-mechanism flight). **And the runtime scoreboard opened on July 23 — and was closed the same day by our own red-team**: F121's 476× decoder-race win was superseded pre-submission (C4996 — the MM problem's algebra falls to a 41-query classical linear-structure solve, ~0.25 ms; the fence that priced this exact path fired, by our own hand). **No runtime advantage is claimed**; F120's shot-axis code stands as the *instrument* result. The sample-complexity claim (**F119**) is **under re-audit against the same axis** — cost-to-solve-the-problem, not cost-to-simulate — before anything is submitted externally. What remains **no**: a raw brute-force *circuit-simulation* speedup — F54's measured wall and F85's scaling inversion stand untouched, and no result here claims them. A **different** column also opened: the constant-depth **BGK shallow-circuit depth-separation** solver runs on silicon (F113, 90% valid / full solution-coset) — the *apparatus* of an asymptotic theorem, not a raw speedup and not an on-chip class separation. The full reckoning, wins and non-wins together: **[the complete answer](docs/quantum-advantage-the-complete-answer-whisper-c4682.md)** (supersedes the earlier [audit](docs/quantum-advantage-audit-whisper-c4666.md)); forward paths: **[the advantage annex](docs/advantage-annex-unconventional-paths-whisper-c4969.md)**. The July second half ([Star Trek arcs](#-headline-results--the-july-star-trek-arcs-exp147197), Exp147–197) added two more advantage-flavored columns: a **distributed computer** (Bernstein–Vazirani split across a cut, 67–141σ) and the campaign's **first error-corrected logical qubits** — [[4,2,2]] logical operations that *beat* the bare machine (reversing F06's "QEC doesn't help yet"), including logical CHSH at 29.7σ. The **[fault-tolerance arc](#-headline-results--the-fault-tolerance-arc-detection--correction--universality-exp236246) (Exp236–246)** then crossed from detection to active **correction** and closed the **universal gate set** (Clifford + a fault-tolerantly-injected T) behind the shield — the *mechanism* of universal quantum computation, error-detected, though not a below-threshold FT fidelity and not a supremacy claim.

### The three great no-go theorems — certified in one court

Bell nonlocality (F73), indefinite causal order (F82) and contextuality (F106) are quantum theory's three foundational *"no classical / local / definite model can reproduce this"* results — each beaten on the same hardware, each with an executed null and a bound **enumerated in the artifact, not cited**. Alongside them, the switch's own provable-bound beats: information pushed through channels of exactly zero capacity.

| Result | Number | Where |
|---|---|---|
| **Causal discrimination game beats the causally-separable bound** (0.8695, re-solved from Araújo et al. with q\* recovered) | p̂ = 0.9769 ± 0.0005 (216.8σ within-run precision); **replicated 0.9738 on `ibm_fez` — the 0.3 pp two-chip concordance (~34σ) is the physical carrier** ([audit C4714](docs/adversarial-audit-F82-causal-game-sigma-whisper-c4714.md)) | `ibm_marrakesh`, [pre-reg](experiments/exp105-causal-game-preregistration.md) · [results](results/exp105_hw_results.json) |
| **Cross-device replication** — same frozen design, chip it never touched | p̂ = 0.9738, **201σ** (0.3pp concordance) | `ibm_fez`, [addendum](experiments/exp105b-replication-preregistration.md) |
| **Cross-VENDOR certification** — the causal axis on a **non-IBM** chip, same frozen theory bounds, no retuning (indefinite causal order is not a Heron artifact) | **PASS-CAUSAL** — W 1.2165 ± 0.0224 (54.4σ over 0), capacity 0.2873 (20.1σ over 0.10), null clean (corrected decode, certified C4946); ranks ≪ Heron (W 1.22 vs 1.90) | `Rigetti Cepheus-1-108Q` (Amazon Braket), [Exp210](experiments/braket-exp210-rigetti-cross-platform-causal-RESULTS.md) |
| **The magic-square game won — contextuality certified, completing the triptych**: the Peres–Mermin "Kobayashi Maru" beaten at **0.96901 vs the classical ceiling 8/9 = 196σ**, the ceiling **enumerated in-code over all 4,096 strategies**; even the worst context clears 8/9 at **37.8σ** (min > 8/9 is classically impossible even for mixtures); no-entanglement null 0.657. Game-value advantage, not computational speedup; the [bridge to BGKT unconditional shallow-circuit advantage](experiments/exp127-bgk-hlf-sim-finding-whisper-c4673.md) runs on this game | **F106** | [finding](findings/F106-exp126-kobayashi-maru-magic-square-contextuality-no-go-triptych-whisper-c4666-ember-numbered-c4147.md) · [pre-reg](experiments/exp126-magic-square-preregistration.md) |
| **Capacity activation** — information through two channels of exactly zero capacity (every causal composition exactly zero) | **0.0436 bits/use, 55.6σ** over zero; null arm 0.0001 bits; the bit lives ONLY in the control–target correlation (D≈0 confirmed) | `ibm_marrakesh`, [pre-reg](experiments/exp106-capacity-activation-preregistration.md) |
| **N=3 cyclic switch** — capacity activation **won at 61.7σ** (0.0260 bits through three zero-capacity channels) and exposed the **NISQ scaling inversion**: theory scales with N, practice inverts (110-CZ depth cost) — N=2 is the practical optimum this hardware generation | **F85** | [finding](findings/F85-n3-capacity-activation-scaling-inversion-whisper-c4539-ember-numbered-c4119.md) · [pre-reg](experiments/exp107-cyclic3-capacity-preregistration.md) |

### Communication & sensing advantages — the ladders

Provable-bound beats across three communication capabilities and quantum-enhanced sensing — each measured against a classical reference **executed on the same qubits**, not cited.

| Result | Number | Where |
|---|---|---|
| **Superdense coding — pre-shared entanglement DOUBLES a qubit's classical capacity**: p_success = **0.9688 = 341σ** above the exactly-0.5 unassisted-single-qubit ceiling (computed by the executed no-entanglement null, which sat dead on it); MI **1.77 bits/qubit** vs the null's 0.93. Tutorial-class priors credited — the contribution is the frozen bound-referenced grading and the executed null. First rung of the comms ladder | **F87** | [finding](findings/F87-exp109-superdense-coding-first-comms-primitive-whisper-c4590-c4591-ember-numbered-c4123.md) · [pre-reg](experiments/exp109-superdense-coding-preregistration.md) |
| **The pocket dictionary — 2→1 quantum random access code**: two bits stored in one qubit, *either* retrievable on demand, at **0.84893 = 110.5σ above the classical one-bit ceiling 0.75** (enumerated over 256 strategies) and **5.2σ below the quantum optimum cos²(π/8)** — certified *inside* the two-sided band (exceeding the quantum law would be a NO-TEST, not a win). The executed optimal-classical arm sat at its own 0.75 law; **zero two-qubit gates**, the cheapest advantage flight possible. Third rung of the comms ladder (F87 superdense · F106 magic square · F107 QRAC) | **F107** | [finding](findings/F107-exp128-pocket-dictionary-2to1-qrac-two-sided-band-whisper-c4667-ember-numbered-c4148.md) · [pre-reg](experiments/exp128-qrac-preregistration.md) |
| **The navigator's sextant — Heisenberg-limit GHZ metrology at N=3**: an entangled 3-qubit probe carries **2.848× the phase Fisher information** of the best separable strategy (95% of the theoretical 3.0), **measured against an *executed* SQL reference on the same 3 qubits** — 168σ — and it beats even *perfect* separable probes (239.5σ); the fringe oscillates at **exactly 3× the drive** (super-resolution, k=3 peak 122.9×). A certified N=3 *local* Fisher-information advantage, completing the genre triptych (games F106 · storage F107 · metrology F108). Scaling **persists through N=5** (F109) — the F85 inversion is task-dependent, not a hardware verdict. This is a local-Fisher existence result, not yet the *deployment* advantage: two textbook tolls the local number doesn't pay ([audit C4716](docs/findings/adversarial-audit-F108-metrology-whisper-c4716.md)) — the k=3 super-resolution that certifies the win is also a 3-fold phase **ambiguity** (absolute phase needs a Higgins-2007 cascade), and under *time-optimized* interrogation with dephasing (the F111-measured regime) the *scaling* advantage is **Huelga–Plenio-limited** (HP bites the frequency-standard framing, not the N=3 phase result) | **F108** | [finding](findings/F108-exp129-navigators-sextant-ghz-heisenberg-metrology-vs-executed-sql-whisper-c4668-ember-numbered-c4149.md) · [pre-reg](experiments/exp129-ghz-sql-preregistration.md) |
| **ICO vs coherent control — the resource debate answered**: five co-batched arms; coherent path control transmits (S = 0.1140, its own win) but the switch strictly exceeds it at **~20σ** with the depth confound favoring paths; **S-ratio 1.949 in the pre-filed [1.7, 2.1], theory exactly 2.00**. Both literature camps partially right, quantified on silicon | **F89** | [finding](findings/F89-exp111-ico-vs-coherent-control-resource-comparison-whisper-c4593-c4594-ember-numbered-c4124.md) · [pre-reg](experiments/exp111-e1-resource-comparison-preregistration.md) |

### Certified randomness — the trust ladder

The end-use of a Bell violation is *private random bits* — but how many you may claim depends on how much of the apparatus you have to trust. This arc walks that ladder rung by rung and **corrects its own scope in the record**: the fully-device-independent bits are quarantined (no-signaling is unmet on a single chip), and the number is delivered at the one rung a single die genuinely holds.

| Result | Number | Where |
|---|---|---|
| **The witness holds, the scope is set right** — a CHSH quantum-behavior witness at **53σ**, with the randomness accounting split into three explicitly separated tiers and the **device-independent bits quarantined** (no-signaling unmet on one chip; gating that number would have frozen an overclaim) | **F115** | [finding](findings/F115-exp135-chsh-witness-53sigma-three-tier-randomness-scope-correction-di-quarantine-whisper-c4676-ember-numbered-c4158.md) |
| **The middle rung — one-sided device-independent STEERING** certified at **96σ** under a chip-appropriate assumption (trust Bob's measurements, treat Alice as a black box), with a crosstalk-cannot-fake discriminator grounded in the campaign's own noise measurements | **F116** | [finding](findings/F116-exp136-one-sided-di-steering-certificate-trust-ladder-whisper-c4677-ember-numbered-c4159.md) |
| **The capstone — rigorous one-sided device-independent RANDOMNESS**: **0.65 private random bits per use**, from measured assemblage data run through an exact SDP (no Werner model), clearing the min-entropy floor with ~100σ of statistical margin. **Bias-disclosed** ([audit C4713](docs/adversarial-audit-F117-randomness-certificate-whisper-c4713.md)): the certificate carries a **+0.006 method bias ≈ 1 SE that the bootstrap does not see** (underlying signal ~0.676 net of a systematic the method doesn't quantify — *that* bias, not the statistical bar, is the limiting factor; and it is a lower bound, since the MC models only tomographic bias). Delivers as a NUMBER what F115 could only quarantine, at the one rung a single chip genuinely holds — the second clean firing of the hardware-anchored-vs-everything-else discipline (after F113) | **F117** | [finding](findings/F117-exp137-rigorous-one-sided-di-randomness-certificate-trust-ladder-capstone-whisper-c4680-ember-numbered-c4162.md) |

### Thermodynamics from causal indefiniteness

A resource proven real (F86), substrate-substituted (F88), certified (F94), run as a full engine cycle (F95), pushed below the local ground state (F97), and — finally — *spent*: the cold branch delivered onto an external qubit to reset it sub-bath (F118) — demon books audited, every floor-miss kept in the record.

| Result | Number | Where |
|---|---|---|
| **The engine runs its FULL CYCLE** — a complete thermodynamic loop on causal indefiniteness: passive baths in (5σ below 0.5) → target charged (p₁\|₋ = 0.5485, **7σ**) → work extracted (**0.0340 E/run**) → output passive again (**W2 win**, 5σ); demon books audited. Enabled by per-qubit two-stage delays beating a 57%-asymmetric T1 bias. The W1 floor-miss (0.7σ short of the 0.05 clearance, LOSS as frozen) is kept in the record | **F95** | [finding](findings/F95-exp117c-ico-engine-full-thermodynamic-cycle-whisper-c4618-c4632-ember-numbered-c4133.md) · [pre-reg](experiments/exp117c-two-stage-preregistration.md) |
| **A certified working resource — population inversion from causal indefiniteness**: both baths certifiably passive (each **5σ below** the 0.5 line), the switch's minus branch certifiably active (p₁\|₋ = 0.5509, **+10.6σ above** it) — ergotropy 0.0378 E/run the passive baths alone cannot reach, **routed** from control-coherence + demon-information through the switch (a router, not a battery). Certified by the premise gate that had just refused a +23σ pseudo-win (Exp116 NO-TEST), via the delay-ladder technique (graded rung selected by calib arms only); free +6.1σ dose-response in-job. **Pre-ledger** ([audit C4717](docs/findings/adversarial-audit-F94-ico-engine-whisper-c4717.md)): the inversion is certified and beats the definite-order/mixture bound, but the pre-registered demon-ledger work column — control-coherence preparation + Landauer erasure of the heralding record — is **not yet computed**, so this is a working resource certified, **not a closed engine cycle** (that ledger nets in F95) | **F94** | [finding](findings/F94-exp116b-certified-population-inversion-ico-engine-delay-ladder-whisper-c4611-c4612-ember-numbered-c4129.md) · [pre-reg](experiments/exp116b-delay-ladder-preregistration.md) |
| **Certified sub-ground-state (negative) local energy** — a coherent-controlled extraction drives Bob's local energy **12σ below the local ground level** (corrected −0.0547 ± 0.0046; 5σ certified bound ≤ −0.0319, conservative by construction); the correlation is the active ingredient (removing it *injects* energy, 21σ). Exotic-matter-sign energy on a 2-qubit chip, books audited. **Scope**: coherent extraction only — the LOCC energy-*teleportation* leg missed its floor and is logged as a LOSS (classical-feedforward latency tax 0.092 E) | **F97** | [finding](findings/F97-exp119b-certified-negative-local-energy-coherent-extraction-whisper-c4641-c4642-ember-numbered-c4135.md) · [pre-reg](experiments/exp119b-coherent-negative-energy-preregistration.md) |
| **ICO thermal splitting** — the Felce–Vedral refrigeration resource **won at 21.1σ**: the switch of two fully-thermalizing channels split the target COLDER (p₁\|+ = 0.2098) vs HOTTER (p₁\|− = 0.3894) by control outcome, Δ = 0.1796 against a causal value of exactly 0. Bonus: the pre-filed cross-arc depth-decay law beat FakeMarrakesh out-of-sample by 2.3× | **F86** | [finding](findings/F86-exp108-ico-refrigeration-resource-whisper-c4561-ember-numbered-c4121.md) · [pre-reg](experiments/exp108-ico-refrigeration-preregistration.md) |
| **Native-fluid ICO refrigeration** — F86 **confirmed on retest at 12.9σ** with the working fluid substituted: reservoirs mixed by the chip's own T1 decay, + branch **colder than the coldest reservoir at 5σ**, procedure-theory residual 0.0016. The drift-tolerant re-fly absorbed the published-T1 bias (+38–69% live vs calibration, 2/2 runs) that NO-TESTed the first attempt | **F88** | [finding](findings/F88-exp108c-native-fluid-ico-refrigeration-whisper-c4592-c4593-ember-numbered-c4124.md) · [pre-reg](experiments/exp108c-native-thermal-refly-preregistration.md) |
| **Spending the cold branch** — the cold output, only ever *measured* before (F86/F88), is **used**: SWAP-delivered onto an **external** data qubit and resetting it **sub-bath at 5σ** (p₁ = 0.2100, below 0.25), colder than the definite-order null (0.2602/0.2700) under the error budget. Not cherry-picking (null P(c=+)=0.998 → no cold subset to select under definite order). **Scope**: beats *definite-order* reset, **not** native reset (~0.01) — a resource-theory result, modest increment over F88. NO-TEST→WIN arc, kept whole in the record: an optimistic retention floor NO-TESTed the parent; a one-frozen-constant re-fly (floor re-derived from the measured haircut) won on a window clearing the older 0.85 precedent independently | **F118** | [finding](findings/F118-exp138b-ico-cold-branch-sub-bath-reset-external-qubit-whisper-c4720.md) · [pre-reg](experiments/exp138b-ico-reset-refly-preregistration.md) |

### Foundations on silicon — Horizons-2, six universe-questions

Six foundational thought-experiments run as frozen-graded hardware experiments in ~14 days — every gate frozen before flight, every miss kept in the record, two wins demoted by self-audit and re-earned.

| Result | Number | Where |
|---|---|---|
| **Causal indefiniteness survives TELEPORTATION** — the switch control beamed one hop arrives still causally indefinite: DISC 1.825 ± 0.009 (**90σ** over the survival floor, 97% of the same-window anchor) while the identical teleport over a dephased *classical* channel kills the witness dead (0.018 ≈ 0, separation **33σ**). Survives quantum, dies classical, one job, one window. No gate-model prior found | **F92** | [finding](findings/F92-exp113-causal-indefiniteness-survives-teleportation-whisper-c4603-c4604-ember-numbered-c4127.md) · [pre-reg](experiments/exp113-teleported-witness-preregistration.md) |
| **Quantum Darwinism under indefinite causal order** — with the order of two *incompatible* recorders in superposition, the objectivity hull is violated **both ways**: the plus branch holds two incompatible records at once (**+0.109 above** what any recorder ordering permits, **22σ** — "facts without a causal history"), the heralded minus branch **erases both** (**−0.432 below**, 52σ). Deepest certified apparatus of the campaign (63 CZ). Resource-scoped to these two recorders | **F98** | [finding](findings/F98-exp120-quantum-darwinism-under-indefinite-causal-order-whisper-c4643-c4645-ember-numbered-c4138.md) · [pre-reg](experiments/exp120-darwinism-ico-preregistration.md) |
| **Heralded information recovery — the Hayden–Preskill mirror** — a "diary" provably dead in *every* definite query order (probe reads 40× below the effect) comes back from the probe alone in the heralded indefinite-order branch, **phase-flipped** (S_P = −0.238, **56σ** past the sign-fixed band; ~74% of definite-order-inaccessible information recovered). Bonus: whether the environment learns the fact depends on query order (0.453 vs 0.007). Same certified apparatus as F98; Hayden–Preskill *analog* | **F99** | [finding](findings/F99-exp121-hayden-preskill-heralded-mirror-information-recovery-whisper-c4646-c4648-ember-numbered-c4140.md) · [pre-reg](experiments/exp121-hp-switch-preregistration.md) |
| **The quantum twin paradox on silicon, adjudicated** — an excited "clock" ages and its aging **marks the path**, destroying interference far more than the vacuum twin: phase-blind (rotation-immune) which-path decoherence at **36σ / 23σ**. The finding is the self-audit playbook whole: a 67σ win was **demoted by its own author** (a negative visibility exposed a coherent-rotation confound), then **re-certified** by a phase-blind retest — with the author's static-ZZ mechanism **refuted** (echo recovery wrong-sign, her 0.80 prediction missed) kept in the record. Zych–Brukner *analog* | **F100** | [finding](findings/F100-exp122-122b-quantum-twin-paradox-aging-decoherence-adjudicated-whisper-c4650-c4654-ember-numbered-c4141.md) · [pre-reg](experiments/exp122b-phase-blind-preregistration.md) |
| **The grandfather paradox, audited** — a post-selected time loop (Lloyd P-CTC) **forbids the paradox**: a full "kill grandfather" flip survives at **1.9% — 53× suppression**, and the residue is readout noise (herald autopsy), the enforcement law cos²(θ/2)/2 tracked to ~1%. The fingerprint the rate can't fake: the loop rotates a bystander's **classical record into quantum coherence** (**78σ**) — nonlinear CTC backaction. Three CX gates, the *shallowest* apparatus of the campaign; Lloyd's post-selection *model*, not literal time travel | **F101** | [finding](findings/F101-exp123-grandfather-paradox-pctc-enforcement-backaction-whisper-c4655-c4656-ember-numbered-c4142.md) · [pre-reg](experiments/exp123-pctc-preregistration.md) |
| **The Zeno "tractor beam"** — *measurement itself* pins a qubit against a full π-rotation that would otherwise flip it: watched at cadence 8 it survives at **0.644 vs 0.020 unwatched (92σ)**, and once the per-measurement QND cost (q = 0.987) is divided out, the cadence law **[cos²(π/2N)]^N matches to 0.5%** through N=8 — with the **watch-cost frontier** (an optimal grip cadence) located at N=16. Zero two-qubit gates, the *cheapest* flight of the campaign — and it **completes Horizons-2, six-for-six** | **F102** | [finding](findings/F102-exp124-zeno-pinning-tractor-beam-qnd-cadence-law-whisper-c4657-c4658-ember-numbered-c4143.md) · [pre-reg](experiments/exp124-zeno-preregistration.md) |

### Certified limits — what quantum provably *cannot* do

The natural opposite of the no-go games: those certify a classical/causal limit that quantum **beats**; this certifies a limit the universe puts on **quantum itself**, saturated and enforced on hardware. The campaign grades both directions — what quantum can exceed, and what nothing can.

| Result | Number | Where |
|---|---|---|
| **The replicator's legal limit — the optimal universal cloning ceiling (5/6) certified**: the best possible copier makes two copies each at fidelity **exactly 5/6 ≈ 83.3% for every input state** (no-cloning's quantitative teeth). On silicon the optimal cloner sits **flat across all three bases** (Z 0.8265 / Y 0.8121 / X 0.8047, spread **0.0218**) a hair below the ceiling and never exceeding it. A pre-registered **cheat** beats 5/6 on one basis (Z 0.9911) but **pays on the conjugate** (X 0.4995): the only way to beat the ceiling somewhere is the way to get caught elsewhere — the cheat's basis-spread 0.49 vs the optimal's 0.02 is a **24× detector tell**. No-cloning made a measurement | **F110** | [finding](findings/F110-exp131-optimal-cloning-ceiling-no-cloning-cheat-detector-whisper-c4670-ember-numbered-c4152.md) · [pre-reg](experiments/exp131-cloning-preregistration.md) |

### The computational scoreboard — the shallow-circuit separation, on silicon (a *different kind* of result)

The one scoreboard the campaign had **not** touched, opened — but it is not the same currency as the bound-beats above. There is exactly one proven quantum-advantage separation that needs **no** hardness conjecture and lives at shallow depth: **Bravyi–Gosset–König (2018)** — a *constant-depth* quantum circuit solves the 2D Hidden Linear Function problem while any bounded-fan-in classical circuit needs depth Ω(log n). That separation is **asymptotic**; at a single n=4 instance there is *no* beaten classical bound (a laptop solves n=4 trivially). So this certifies the theorem's **apparatus running on silicon**, not an advantage margin — the complement to F54's measured deep-circuit wall, and distinct from a raw speedup (still depth-walled). The solver's **NISQ reach** was then laddered: it holds strong-majority-valid **through n=9** (F114, no boundary in range, O(1) logical depth throughout) — graceful erosion, not the F85 inversion.

| Result | Number | Where |
|---|---|---|
| **The BGK shallow-circuit solver runs on silicon** — a **constant-depth** quantum circuit solves the 2D-HLF instance at **P(valid) = 0.9017 = 437.8σ over the *uniform-random* floor 0.25** (a fidelity number, *not* a beaten classical bound — the separation is asymptotic), and — the un-fakeable part — it **covers the whole solution coset near-uniformly** (all four valid z ~0.225 each; a fixed-output classical mimic fails this W3 coverage gate). 10 routed CZ, O(1) depth. The classical hardness is **contextuality-flavored** (the grid's parity/Mermin–Peres structure) and **theory-associated** with the magic-square game F106 certified at 196σ — but that association is BGKT-2020's noise-robust gadget, a *different* circuit family; the circuit that flew here is the plain **BGK-2018** solver, so the contextuality link is inherited-in-theory, not demonstrated-by-composition on-chip ([audit C4715](docs/findings/adversarial-audit-F113-computational-bridge-whisper-c4715.md)). **Scope fence**: this does *not* prove QNC⁰ ≠ NC⁰ on-chip; it certifies a constant-depth solver at 90% / full-coset / O(1)-depth, and the theorem carries the asymptotics *as n grows* (at the fixed n=4 flown, a constant-depth classical circuit can also solve the instance) | **F113** | [finding](findings/F113-exp127hw-bgk-2d-hlf-shallow-circuit-solver-first-computational-genre-on-silicon-whisper-c4674-ember-numbered-c4156.md) · [sim groundwork](experiments/exp127-bgk-hlf-sim-finding-whisper-c4673.md) |

**[Quantum-switch full apparatus spec](docs/quantum-switch-spec.md)** — the single-document engineering reference: circuit family (V1–V5), exact theory statistics, measured-results ledger with job IDs, reusable methodology, pitfall registry, scope and platform prior art.

Strategy docs: [bridges to a compute advantage](docs/bridges-to-compute-advantage-whisper-c4522.md) ·
[shallow-circuit computational bridge — 2D-HLF solver + depth ledger (sim tier)](experiments/exp127-bgk-hlf-sim-finding-whisper-c4673.md) ·
[1SDI-randomness SDP tool — exact one-sided-DI min-entropy (the engine behind F117)](tools/sdp_randomness.py) ·
[ICO applications roadmap](docs/ico-applications-roadmap-whisper-c4527.md) ·
[ICO cooling floor & the classical-concentration boundary](docs/ico-cooling-floor-and-concentration-boundary-whisper-c4720.md) ·
[SDP bound groundwork + recovered q\*](experiments/causal-game-sdp-bound-groundwork-whisper-c4523.md) ·
[paper outline (causal-inference audience)](docs/pearl-bridge-paper-outline-whisper-c4533.md)

---

## ⭐ Headline Results — the July "Star Trek" arcs (Exp147–197)

The campaign's second half opened four new scoreboards after F118. Same discipline — pre-registered gates, executed nulls, misses kept — now aimed at **error-corrected logical qubits, a composable quantum network, exotic phases of matter, and the physics of time and the observer.** Full per-experiment index (wins and nulls): **[campaign arcs since Exp147](docs/campaign-arcs-since-exp147-ember-c4207.md)**.

### The first logical qubits — error correction that finally *helps* (the Shields arc)

Findings 05/62 established that *textbook* error correction adds more noise than it removes on this substrate. The **[[4,2,2]] error-detecting code** crossed the line the other way — the campaign's first **logical qubits whose operations beat their bare-physical counterparts**: entangled, teleported, and made to violate Bell inequalities *as logical qubits*.

| Result | Number | Where |
|---|---|---|
| **The shielded handshake** — two logical qubits (each an [[4,2,2]] block, 8 physical) entangled across blocks; the shielded logical Bell pair **beats the bare-physical pair** | HELD, **57σ** | [Exp191](findings/finding-exp191-logical-bell.md) |
| **The shielded verdict** — logical CHSH between two shields: **S = 2.778 vs the classical bound 2 (29.7σ)**, on the F191-predicted 2.79 (Tsirelson 2.828) | HELD, 29.7σ | Exp196 |
| **The shielded transporter** — a logical qubit teleported between [[4,2,2]] blocks across 12 physical qubits | HELD, **F ≈ 0.98 / 0.99** | [Exp192](findings/finding-exp192-logical-teleport.md) |
| **The Federation** — logical entanglement swapping across **three** shields: two logical qubits sharing no gate anywhere, entangled through a relay | HELD, **21.8σ** | Exp197 |

**Scope**: [[4,2,2]] is a *distance-2 error-**detecting*** code (post-selected on the syndrome) — a signature that logical encoding beats bare physical operations on this hardware, **not** below-threshold fault-tolerant correction. The boundary flights are kept in the record, both directions (Exp189 shields-up HELD; Exp190 the paying regime NOT-HELD).

### Exotic phases of matter, on silicon

Driven, disordered, and constrained many-body phases — each a *different way order defies thermal chaos*, run as pre-registered signatures with matched controls (Ember's wing).

| Result | Number | Where |
|---|---|---|
| **A Floquet SPT edge π-mode** — symmetry-protected topological order living **only at the boundary**: the edge spin locks to a rigid period-2 response while the bulk thermalizes; breaking the Ising Z₂ kills it (edge-bulk contrast +0.554, symmetry protection +0.425). The bulk-*decay* is the load-bearing verified condition that distinguishes it from a time crystal | HELD | [Exp170](findings/finding-exp170-floquet-spt-edge-mode-ember-c4200.md) |
| **Quantum many-body scars (PXP)** — the Néel state revives its memory above the **entire** generic ensemble (rank 1/55), and **survives past the coherence wall**: at 433 CZ the anomaly shrinks by *exactly* the decoherence factor (R invariant), so the scar is decoherence-limited and **not fragile**, not broken | HELD | [Exp171](findings/finding-exp171-scars-pxp-ember-c4201.md) · [172](findings/finding-exp172-scars-n8-wall-ember-c4202.md) · [173](findings/finding-exp173-scars-n8-defog-ember-c4203.md) |
| **A discrete time crystal** — a driven disordered chain ticking at half the drive, rigid against detuning ("a clock nothing set"); melt boundary mapped (disorder shrinks it) | HELD | [Exp151](findings/finding-exp151-time-crystal.md) · [153](findings/finding-exp153-dtc-melt-boundary.md) |
| **Anyon braiding** — Z₂ mutual statistics on a toric-code patch: an e-anyon circling an m picks up exactly −1, certified topological (not parity bookkeeping) by six loophole-closing arms | HELD, **50σ** | [Exp157](findings/finding-exp157-anyon-braiding.md) |
| **The delayed-choice quantum eraser** — a quantum coin flipped *after* the system qubit is measured decides whether its already-recorded data shows an interference fringe; no-signaling measured (the marginal never moves — no FTL) | HELD | [Exp155](findings/finding-exp155-delayed-choice-eraser-ember-c4197.md) |

**Method note (the mitigation wall, mapped)**: readout mitigation is nearly free here (readout ~99% clean), so a deep observable's residual is coherent/gate error, not measurement (Exp173); and zero-noise extrapolation **cannot** rescue a ≥260-CZ signal — the amplified points drown before they extrapolate (Exp174, a 0-QPU viability boundary).

### The quantum network, composed into a computer

Every network-stack layer had a *primitive* (distribute F91 · route F90 · carry F87 · purify F93); this arc **composes them end-to-end** into applications — and prices the tax composition charges (Whisper's wing).

| Result | Number | Where |
|---|---|---|
| **A distributed computer** — Bernstein–Vazirani run across a *cut* (Alice holds the data, Bob the oracle); the joined machine returns the hidden string as top outcome for every program, with a measured per-gate cost | HELD, **67–141σ** | [Exp181](findings/finding-exp181-dist-bv.md) · [182 scaling law](findings/finding-exp182-dist-bv3.md) |
| **The relay computer** — a **nonlocal CNOT between two qubits that never met** (1 Bell pair + feed-forward both ways); the composition tax discovered, priced, decomposed, and **cured** (a Pauli frame + one echo pulse recovers it) across Exp175–180 | HELD (Exp179 plateau NOT-HELD, kept) | [Exp175](findings/finding-exp175-relay-gate.md) |
| **The repeater with memory** — entanglement swapped through a relay and *held* for a swept delay before the witness (the repeater's defining ingredient); + gate teleportation (an entangling gate between qubits with no shared history, 25σ) | certified, **27σ** | [Exp160](findings/finding-exp160-relay.md) · [162](findings/finding-exp162-swap.md) · 163 · 170-gate |
| **Keys through untrusted relays** — physics-certified E91 secret keys through one and two untrusted relay stations; + a GHZ conference key and two-officer secret sharing | certified | [Exp180](findings/finding-exp180-relay-key.md) · [168](findings/finding-exp168-conference.md) · [183](findings/finding-exp183-secret-sharing.md) |

### Time and the observer — foundations, part two

Beyond Horizons-2's six paradoxes: a **time quartet** and its extensions, asking whether time, order, and observed facts are absolute.

| Result | Number | Where |
|---|---|---|
| **A handshake across time** — delayed-choice entanglement swapping between qubits of **disjoint lifetimes**: A was measured and its record closed *before* D existed, yet a later Bell measurement on the middles certifies A–D entanglement | HELD, **40σ** | [Exp184](findings/finding-exp184-acrosstime.md) |
| **Time is entanglement** — a Page–Wootters "universe where time is optional": a static 3-qubit block whose inhabitants experience time *only* conditioned on a clock register they're entangled with | HELD (all 3 legs) | [Exp185b](findings/finding-exp185b-pagewootters.md) |
| **Macrorealism violated** — a Leggett–Garg test: between two looks the qubit was in no definite state (K₃ = 1.465 vs the macrorealist bound 1) | HELD, **24σ** | [Exp186](findings/finding-exp186-leggett-garg.md) |
| **Facts are not absolute** — a Wigner's-friend test: two "friend" qubits each record a definite outcome, yet the outcomes are not jointly absolute until copied out | HELD, **20σ** | [Exp193](findings/finding-exp193-wigner-friend.md) |
| **Information moves energy** — quantum energy teleportation (Hotta): a purely informational LOCC message lets Bob extract energy locally, certified as an *information* effect by a gate-identical differential (the sole difference is whether Bob's kick is conditioned on Alice's bit) | HELD, **9.8σ** | Exp195c |

---

## ⭐ Headline Results — the fault-tolerance arc: detection → correction → universality (Exp236–246)

The Shields arc (above) reached error *detection* — [[4,2,2]] postselects on the syndrome and discards the bad runs. This arc crossed the next line, and it was built by refusing to stop at the wall each result put up: the *detection ceiling* became active **correction**; the *Clifford ceiling* (every shielded computation was classically simulable) became a **fault-tolerant universal gate**. Same discipline — pre-registered gates, executed nulls, misses kept with their lessons.

### From detecting errors to *healing* them — active quantum error correction

| Result | Verdict | Where |
|---|---|---|
| **The first correction** — a 3-qubit code that *fixes* a bit-flip and keeps the shot (detect-and-repair, not detect-and-discard); the Shor [[9,1,3]] then corrects an **arbitrary** single-qubit error (X, Y *and* Z), folding bit-flip ⊗ phase-flip into one code | CERTIFIED | [Exp236](experiments/exp236-STATUS-certified.md) · [237](experiments/exp237-STATUS-not-held.md) · [238](experiments/exp238-STATUS-certified.md) |
| **The live syndrome** — non-destructive syndrome extraction: two parity ancillas learn *which* qubit erred without measuring the data, so a logical superposition survives (⟨X̄⟩ 0.55 vs 0.00 for a direct read), then feed-forward corrects it in one live pass | CERTIFIED | [Exp240](experiments/exp240-STATUS-certified.md) |
| **The repeated rounds** — the continuous QEC inner loop: over R rounds of {idle → live syndrome → fix → reset}, the corrected qubit beats an *identical* no-fix control by a gap that **grows** (+0.054 → +0.341), correction outrunning its own machinery cost | CERTIFIED | [Exp241](experiments/exp241-STATUS-certified.md) |

### Breaking the Clifford ceiling — a *universal* logical computer

| Result | Verdict | Where |
|---|---|---|
| **Magic injection** — the fault-tolerant T-gate *gadget*: a non-Clifford gate applied not directly (an Eastin–Knill dead end) but by *consuming a magic ancilla* and teleporting its gate onto the data. The injected T lands at a non-stabilizer ⟨X̄⟩ = 0.69 no Clifford could reach; nothing reaches the data without the gadget | CERTIFIED | [Exp243](experiments/exp243-STATUS-certified.md) |
| **The universal gate set, closed** — a *programmable* Clifford+T logical operation behind the shield: the injected T *steered* by a logical-Clifford program to distinct non-stabilizer targets (+0.71 / −0.71); replace the T with a Clifford and both collapse onto the stabilizer grid. The shielded computer is universal in principle | CERTIFIED | [Exp244](experiments/exp244-STATUS-certified.md) |
| **The rotation, dialed** — Exp244 taken from 2-point steering to a **4-point programmable rotation**: the injected T dialed by logical-Clifford wrappers to all four non-stabilizer targets around the Bloch equator (45°/135°/225°/315°, each ⟨X̄⟩,⟨Ȳ⟩ ≈ ±0.70), the Clifford falsifier collapsing onto the Ȳ axis. A genuinely *programmable* Clifford+T logical rotation, error-detected | CERTIFIED | [Exp246](experiments/exp246-STATUS-certified.md) |
| **The magic factory's seed** — error *detection* purifies an injected magic state (⟨X̄⟩ 0.61 raw → 0.69 postselected, toward the ideal 0.71), read for free from a job already flown | held | [P4 analysis](experiments/exp243-P4-STATUS-magic-purification.md) |

**Scope (stated with the negatives that taught the boundary)**: all of this is error-**detected** (distance-2 postselection, or the distance-3 codes exercised on *injected* errors) — the *mechanism* of fault-tolerant, universal computation, **not** a below-threshold fault-tolerant *fidelity* and **not** a computational-supremacy claim (a single T on a few qubits is classically simulable; non-simulability is asymptotic). The seven misses of this arc are each a rule now priced in: a verdict floor set at the hardware noise level is a coin-flip (Exp237, missed by 0.001); a coded-vs-bare comparison must pin *and verify* the physical qubits (Exp239's qubit-selection confound); a one-basis code cannot hold a logical Bell pair (Exp242's phase-blind leg); and a single-run QEC advantage is a **snapshot, not a constant** — it drifts with the day's calibration (Exp245: +0.341 → +0.077 on the *same* qubits, hours apart). The forward map — actively-corrected causal order, a live logical Bell pair on a both-bases code, error-*corrected* magic, and real magic distillation — is depth-blocked on this NISQ generation, and named as the next thing to out-think, not a boundary. Full arc synthesis: **[Horizons 6 — The Living Ship](docs/star-trek-horizons-6-the-living-ship-whisper-c4923.md)**.

---

## The Quantum Museum — 22 interactive exhibits

The results above, made playable. Each exhibit is a self-contained, theme-aware page that renders **measured hardware data** — no simulations, no idealized curves — and each carries a **full specification sheet**: the finding in plain language, what is measured, the pre-registered gates (frozen before flight), the measured-data table, the scope and limits, and the IBM job ID. The interactive versions live at **[mblakemore.github.io/quantum](https://mblakemore.github.io/quantum/)**; the spec sheets render inline as Markdown below.

**Wing I · The Causal Switch**
- **The Interactive Switch** (F73–F82) — [spec](demo/switch/spec.md) · [play](demo/switch/index.html)
- **The Ladder of Causation** — [spec](demo/ladder/spec.md) · [play](demo/ladder/index.html)
- **The ICO Refrigerator** (F86 / F88 / F95 / F118) — [spec](demo/ico-refrigerator/spec.md) · [play](demo/ico-refrigerator/index.html)
- **The Teleported Witness** (F92) — [spec](demo/teleported-witness/spec.md) · [play](demo/teleported-witness/index.html)

**Wing II · The No-Go Games**
- **The Bot Duel: STATIC** (F83) — [spec](demo/static-duel/spec.md) · [play](demo/static-duel/index.html)
- **The Interrogation** (F82) — [spec](demo/casebook/spec.md) · [play](demo/casebook/index.html)
- **The Magic Square** (F106) — [spec](demo/magic-square/spec.md) · [play](demo/magic-square/index.html)
- **The No-Go Triptych** (CHSH · F82 · F106) — [spec](demo/no-go-triptych/spec.md) · [play](demo/no-go-triptych/index.html)

**Wing III · Foundations on Silicon**
- **The Grandfather Paradox** (F101) — [spec](demo/grandfather/spec.md) · [play](demo/grandfather/index.html)
- **The Zeno Tractor Beam** (F102) — [spec](demo/zeno-tractor/spec.md) · [play](demo/zeno-tractor/index.html)
- **The Twin Paradox** (F100) — [spec](demo/twin-paradox/spec.md) · [play](demo/twin-paradox/index.html)
- **Quantum Darwinism** (F98) — [spec](demo/quantum-darwinism/spec.md) · [play](demo/quantum-darwinism/index.html)
- **The Hayden–Preskill Mirror** (F99) — [spec](demo/hayden-preskill/spec.md) · [play](demo/hayden-preskill/index.html)
- **Negative Energy** (F97) — [spec](demo/negative-energy/spec.md) · [play](demo/negative-energy/index.html)

**Wing IV · The Advantage Ladder**
- **The Scoreboard** (campaign summary) — [spec](demo/scoreboard/spec.md) · [play](demo/scoreboard/index.html)
- **The GHZ Sextant** (F108 / F109) — [spec](demo/ghz-sextant/spec.md) · [play](demo/ghz-sextant/index.html)
- **The Trust Ladder** (F115–F117) — [spec](demo/trust-ladder/spec.md) · [play](demo/trust-ladder/index.html)
- **The Pocket Dictionary** (F107) — [spec](demo/pocket-dictionary/spec.md) · [play](demo/pocket-dictionary/index.html)
- **The Shallow-Circuit Solver** (F113 / F114) — [spec](demo/shallow-solver/spec.md) · [play](demo/shallow-solver/index.html)

**Wing V · The Instruments**
- **The QPU Weather Report** (F81) — [spec](demo/weather/spec.md) · [play](demo/weather/index.html)
- **The Casebook: Print & Play** (F82 / F83) — [spec](demo/casebook-pnp/spec.md) · [play](demo/casebook-pnp/index.html)
- **The Switch-Bench Readout** (F112, three devices) — [spec](demo/switch-bench/spec.md) · [play](demo/switch-bench/index.html)

---

## What Else the Campaign Established

Eight arcs of operational discoveries about real NISQ hardware, each detailed in the linked docs below:

- **Hard limits**: output becomes statistically uniform past ~800–1000 CZ gates (Finding 05), and the QAOA utility ceiling co-locates with that wall (Exp33). Textbook error correction adds more noise than it removes on this substrate (Finding 06, independently re-confirmed by toric-code replication F62).
- **What actually moves fidelity**: qubit *placement* beats gate count as the lever (up to 46× error reduction; F57–F70), with a reusable quiet-qubit picker that works untuned across devices.
- **Noise structure**: the dominant CZ noise is Z-biased and structured (X-basis readout is measurably cleaner — magnitude substrate-dependent, mechanism replicated); "noise as a computational resource" was tested and killed under controls (F55–F56). And the *dephasing* structure read out directly (F111, "the cloaking device"): a 3-way phase-blind race — DFS logical qubit vs Hahn echo vs bare idle — finds IBM dephasing **dominantly memoryless-independent with a real subdominant ~10–15% correlated tail**, detected two ways (echo/bare T2 1.088 temporal, DFS/bare 0.291 vs the 0.15 memoryless-fake floor spatial); the confound-breaker is that the memoryless vendor model *cannot* preview either benefit, so the hardware's pre-registered deviation toward correlation is the evidence (successor to F81). Active refocusing beats the passive code 35σ; a pre-filed ECHO_PROTECTS bet missed and is kept in the record.
- **Calibration reality**: ±7pp daily drift; deep-circuit quality is a *window lottery* — detectable by same-depth sentinels in-run, not forecastable from calibration age (F81, F84) — and the noise-model's optimism grows with depth (the measured depth-decay law in the spec).
- **Device-independence — the court travels** (F112, "the transporter's exam", completing Horizons-3): the full three-axis switch-bench (host indefinite order · order-symmetric schedule · Zeno hold) certifies against the same frozen bounds, **no retuning, across three Heron dies**. It first flew to a chip it had never seen (`ibm_kingston` — all three axes certify), then extended to a **third** die (`ibm_fez`): fez certifies all three axes but is **not a clean 3/3** — its schedule data tripped the split-half floor-transfer guard, and it ranks last on the causal and Zeno-hold numbers. The bench **ranks devices on axes QV/CLOPS/EPLG don't touch**: kingston ≥ marrakesh ≥ fez (W 1.95 / 1.90 / 1.89, hold-sep 0.649 / 0.624 / 0.525). Causal-order phenomena are properties of the hardware *generation*, not one lucky die. **Now extended past the vendor boundary** (Exp210): the causal axis certifies `PASS-CAUSAL` on a **non-IBM** chip (`Rigetti Cepheus-1-108Q`, via Amazon Braket) against the same frozen bounds — so the phenomenon is not even IBM-specific, though Rigetti ranks well below Heron (W 1.22 vs 1.90; corrected decode, certified C4946). **And past the modality boundary** (Exp211/212): on **IonQ Forte-1 trapped ions** the witness fires at W = 1.910 (13.5σ) with a validated matched definite-order null — the [multi-substrate white paper](docs/multi-substrate-causal-order-validation.md) carries the full three-vendor, two-modality certification; the ion's full three-number card (capacity + null-integrity arms) remains the cost-gated upgrade.
- **What works today**: VQE hit chemical accuracy on H₂; amplitude-estimation readout recovered a 344× precision gain via multi-k MLE — with a mapped depth boundary for financial-scale loaders (F51, F54, F78–F79).
- **Communication primitives — every network-stack layer has a measured primitive**: distribute (F91) · purify (F93) · route (F90) · carry (F87). The **repeater** primitive: Bell violation survives TWO entanglement-swapping stations (F91, frame arm ≥15σ above the exact classical bound 2) — software Pauli-frame tracking beats active feedforward on current hardware. The **routing** rule: SWAP beats teleportation at every hop count through N=6 (F90, informative null at 66σ; feedforward works at 0.947 integrity but costs ~5–6× per hop). **Purification** resurrects a dead Bell violation (F93 — noisy pair 5σ *below* the exact bound, BBPSSW-purified pair 5σ *above* it, same window; the quantitative GAIN leg missed its frozen floor by 0.33σ and is logged as a LOSS).
- **Information-theoretic certification (zero shots)**: entanglement certified by **negative conditional entropy** — from a *banked* CHSH number, a twirl+positivity argument puts S(B|A) ≤ −0.0986 at 5σ (F103, first Horizons-3 result), and every TVD certification the campaign owns now also yields a free classical-entropy (Fannes) certification; the finding leads with the author retracting her own overstated reading-cycle export.
- **Causal-structure metrology**: the switch apparatus inverted into a diagnostic — a first-of-kind **schedule-symmetry certification** (F96) proves the transpiler's nominally-parallel CZ gates carry no hidden effective ordering (hotspot hidden-order ≤ 0.03 TVD, certified; a guarantee the vendor does not provide), with a portable duration-vs-order discriminator.
- **Side quest**: integrated-information (Φ) of quantum systems follows a clean size law and ignores the number-theoretic structure that dominates its classical counterpart (quantum-IIT arc).

**Orientation numbers**: ~100+ pre-registered experiments (105 pre-registration documents) · 3 real Heron dies + a noise-model sim tier ·
600 q-sec / 28-day open-plan budget, every submit budget-gated · every finding anchored to an IBM job ID ·
5 consecutive experiments where pre-submission review caught a real defect.

Plain-English version of everything: **[ELI5_SUMMARY.md](ELI5_SUMMARY.md)** (self-contained, shareable).

---

## The Findings — Where Everything Lives

| Doc | Contents |
|---|---|
| **[Beyond the Ladder](docs/beyond-the-ladder.md)** ★ | The full technical argument, written for causal-inference readers and sibling-reviewed to journal standard: why the switch results sit outside what structural causal models can express — "do-calculus is not wrong; it is typed" — with the executed classical-control arms and the Exp111 switch-vs-coherent-control verdict (ratio 1.949, theory 2.0). The repo-native publication. |
| **[Future directions — Star Trek horizons](docs/star-trek-horizons-whisper-c4601.md)** | Where this goes next: seven programs composed from validated findings, each with its first experiment named, plus the provably-unreachable boundary stated. |
| **[Questions we can now ask the universe](docs/questions-we-can-now-ask-the-universe-ember-c4196.md)** | The full-record synthesis (F1–F118, Exp1–150, all 22 exhibits): twelve askable questions organized instrument-by-instrument, each tied to the findings that license it and a first experiment, with a priority flight order and the provably-unaskable fence restated. |
| **[Quantum Weather Report](demo/weather/index.html)** | The window lottery, the T1-staleness timeline (10 measurements, 0–115% error), and the noise-model optimism atlas — visualized, with the four practices we use to dress for it. Every number traces to a job ID. |
| **[Friction reports](docs/friction-reports/README.md)** | Standing, data-backed reports of platform/tooling issues we hit (paste-ready if we ever file them): FakeMarrakesh depth-optimism (12-row atlas), published-T1 bias (+38–69%, 2/2 runs, queue-independent), calibration blind to window quality. Grows as we go. |
| **[Findings 1–27 catalog](docs/findings-catalog.md)** | Arc-1 characterization + QAOA/optimizer arcs: headline table + plain-English one-liner per finding (CHSH 2.74, X-basis immunity, the ~1000-CZ wall, QEC ancilla tax, mitigation failures, VQE chemical accuracy, QAE 344×, …) |
| **[Campaign arcs since June 2026](docs/campaign-arcs.md)** | Findings 28+ and the F-series, arc by arc: warm-start anchors, noise-is-not-a-resource kills, placement-beats-gate-count (F57–F70), toric-code replication, financial QAE depth boundary + calibration-window lottery (F78–F81), quantum-IIT bridge, the ⭐ quantum-switch arc (F73–F77 witness chain → F82–F89 bound beats), the communication-primitives arc (F87, F90–F91, F93), and the Horizons foundations + trust-ladder arcs |
| **[Campaign arcs since Exp147](docs/campaign-arcs-since-exp147-ember-c4207.md)** | The July "Star Trek" second half (post-F118): the full per-experiment index of the four new arcs — Shields/logical-QEC (Exp189–197), exotic phases (Exp151–174), the composed quantum network (Exp154–183), and time/observer foundations (Exp184–195c) — wins and nulls, most-recent-first |
| **[Methodology & validation](docs/methodology-and-validation.md)** | Autonomous-network methodology, pre-registration discipline, Pearl causal framing, budget, cross-validation anchors, limitations and caveats |
| **[Next steps & open questions](docs/next-steps-and-open-questions.md)** | What you can use today (7 actionable rules), the strategic frontier (P1 noise-as-resource RESOLVED-NEGATIVE, P2 causal order DELIVERED, P3 replication audit), and the ORQ list with live statuses |
| **[Quantum-advantage audit](docs/quantum-advantage-audit-whisper-c4666.md)** | The one-page reckoning: every scoreboard the campaign touched, wins and non-wins side by side, with the currency of each result stated (beaten bound vs certified apparatus vs fidelity number) |
| **[Messaging & the shape-limits of spacetime](docs/messaging-limits.md)** | What kinds of messages this lab has verified can be sent and received, and where the hard walls are — seven channels with hardware receipts (Exp192/197/109/166/195c/196) and seven walls each drawn by our *own* falsifier arms (no-signaling, retro-signal blindness, the Tsirelson ceiling). Companion to this overview |
| **[ELI5_SUMMARY.md](ELI5_SUMMARY.md)** | The whole campaign in plain English, shareable (§17 the game, §18 the two walls) |
| **[full-report.md](full-report.md)** | Arc-1 deep synthesis (source document) |

---

## Methodology & Scope (short form)

Full version: [docs/methodology-and-validation.md](docs/methodology-and-validation.md)

- **Pre-registration**: falsifiable gates frozen before every submit; failed pre-regs are reported as first-class results (several findings are self-retractions — F94's refused pseudo-win, F100's demoted-then-re-earned twin, F115's quarantined DI bits).
- **Tier labels**: `HW` = real QPU with job ID; `sim` = FakeMarrakesh-class noise model — and noise-model trust is **depth-stratified** (predictive at the ~4-CZ class, off by 400× at ~124 CZ; see F81 and the spec's residual atlas).
- **Calibration drift is the elephant**: ±7pp daily; deep-circuit quality is a *window lottery* (F81) — reproduce within a calibration window, or use the sentinel-gating discipline in the newer pre-regs.
- **Cross-device replication is the standard**: it has demoted headlines (F03's 3× is marrakesh-specific) and promoted others (quiet-qubit picker F70; the causal game at 0.3pp concordance across chips; the switch-bench certifying across three dies, F112).
- **Scope**: claims are about *this generation* of hardware and are **device-characterized** (compiled gate-model circuits reproducing switch statistics — the device-independent certifications of indefinite causal order are photonic experiments; prior non-photonic work is credited in the [spec](docs/quantum-switch-spec.md)). Certified-randomness claims are stated at their true rung: F117 is **one-sided device-independent**, not loophole-free. Every number traces to a job ID in [`experiments/job-manifest.md`](experiments/job-manifest.md).

---

## Hardware Under Test

- **Primary processor**: IBM Heron-r2 (`ibm_marrakesh`) — all of Arc 1 and most later hardware arcs
- **Additional devices**: `ibm_kingston` (X-basis cross-backend Exp31–34, IQAE validation F51, causal cosine law F76, full switch-bench F112) and `ibm_fez` (toric-code Bell proxy F61–F64, placement partition F67–F69, quiet-qubit cross-device F70, causal-game replication F82 at 201σ, switch-bench third die F112) — both Heron-generation 156-qubit devices. The causal-order phenomena now certify across all three.
- **Qubit count**: 156 superconducting transmons · **topology**: heavy-hexagonal lattice (degree 2–3)
- **Native two-qubit gate**: controlled-Z (CZ) via flux-tunable couplers · **environment**: dilution refrigerator @ ~15 mK
- **T₁, T₂**: routinely > 200 μs (ancilla T₂ measured 270–340 μs during this campaign) · **CZ error**: ~0.4% baseline
- **Daily calibration drift observed**: ±7 percentage points (same circuit, same seed, 24h apart)

See [`docs/hardware-substrate.md`](docs/hardware-substrate.md) for the full physical architecture primer.

---

## Repository Map

```
.
├── README.md                     ← you are here
├── demo/                         ← 🔀 GitHub Pages front door (mblakemore.github.io/quantum/)
│   ├── index.html                ← interactive Quantum-Switch demo + museum lobby
│   ├── museum.css                ← shared design system (theme-aware, CSP-safe, WCAG-AA)
│   └── <22 exhibit dirs>/        ← each: index.html (interactive) + spec.html + spec.md
│                                    switch/ magic-square/ no-go-triptych/ static-duel/
│                                    casebook/ casebook-pnp/ weather/ … (full list in the Museum index)
├── ELI5_SUMMARY.md               ← shareable plain-English summary of the whole campaign
├── full-report.md                ← Arc-1 synthesis (the deep-research source doc)
├── findings/                     ← one-per-discovery deep dives (~150 files)
│   ├── 01…44-*.md                ← the core numbered line (41–43 under exp-named files, no 45)
│   ├── F48…F117-*.md             ← the unified F-series (quiet qubits, placement, causal order, comms, Horizons, trust ladder)
│   ├── finding-25/26/46/47…      ← quantum-IIT arc side numbering (25/26 here ≠ QAOA Findings 25/26!)
│   └── exp*-*.md                 ← interim findings, integrity audits, closure notes
├── images/                       ← figures (PNG), reproducible from scripts/generate_figures.py
├── experiments/
│   ├── job-manifest.md           ← IBM Quantum job IDs + experiment inventory
│   └── *-preregistration.md      ← 105 pre-registered hypotheses/gates, frozen before each submit
├── scripts/                      ← Python source: circuits, submission tools, analysis, grading
│   ├── generate_figures.py       ← regenerate figures from cycle-data constants
│   ├── quiet_qubits.py           ← F58 quiet-qubit picker / drift snapshot / CHSH health tool
│   ├── check_usage.py            ← IBM Open-plan quota check (run BEFORE submitting jobs)
│   └── README.md
├── results/                      ← raw result JSONs + the model-residual atlas
├── docs/
│   ├── quantum-switch-spec.md    ← ⭐ full apparatus spec: circuits, theory, ledger, methodology
│   ├── quantum-advantage-audit-whisper-c4666.md ← the one-page wins/non-wins reckoning
│   ├── beyond-the-ladder.md      ← ★ the full technical argument (causal-inference readers)
│   ├── findings-catalog.md       ← Findings 1–27 headline table + ELI5 per finding
│   ├── campaign-arcs.md          ← Findings 28+ / F-series, arc by arc (with figures)
│   ├── methodology-and-validation.md ← methods, cross-validation, caveats (full)
│   ├── next-steps-and-open-questions.md ← actionable rules + strategic frontier + ORQs
│   ├── star-trek-horizons-whisper-c4601.md ← future directions (status table maintained)
│   ├── friction-reports/         ← platform issues, data-backed (grows as we go)
│   └── hardware-substrate.md     ← Heron-r2 physical architecture primer
├── tools/
│   ├── switch_bench.py           ← ★ portable BYOK causal benchmark (any backend; 3 dies graded)
│   ├── sdp_randomness.py         ← exact one-sided-DI min-entropy SDP (the engine behind F117)
│   ├── demon_ledger.py           ← Landauer/ergotropy bookkeeping for the ICO engine
│   ├── gate_feasibility_lint.py  ← prereg gate linter (CAN-PASS / CAN-FAIL)
│   └── fakemarrakesh_atlas.py    ← model-error atlas builder
└── sources/
    └── references.md             ← peer-reviewed and primary sources (cited inline in findings)
```

**A field guide to finding numbers**: the campaign's numbering evolved live. Findings 1–44 are the core line (41–43 under experiment-named files, no Finding 45 in this line); `finding-25/26/46/47` belong to the quantum-IIT arc's separate numbering; the unified `F##` series runs from ~F48 to **F118** and counting, with one flagged collision (Elder's anchor "Finding 48" vs Ember's IIT F48). When in doubt, the file's header states its arc.

---

## License & Attribution

Public for cross-validation, replication, and peer review. If you reproduce or build on this work, citing the IBM Quantum job IDs in `experiments/job-manifest.md` is the most useful form of attribution — it gives downstream readers a verifiable anchor.

The Python scripts in `scripts/` are released for educational and research use. Lyla quantum tooling (`qae_volatility_estimator.py`, `ibm_quantum_submit.py`) is sourced from the upstream Lyla project and reproduced here with attribution headers.

---

## Contact

**Mike Blakemore** — [mblakemore@ucsb.edu](mailto:mblakemore@ucsb.edu) · [mikeblakemore@gmail.com](mailto:mikeblakemore@gmail.com)

Questions, replication reports, and collaboration inquiries welcome.
