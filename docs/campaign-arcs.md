# The Campaign Since June 2026 — Findings 28+ and the F-Series, Arc by Arc

*Moved out of the root README (Whisper C4534) to keep the front door consumable — content unchanged, links adjusted.*


*The core numbered line (Findings 1–27 above) continues as Findings 28–44 below; from roughly F48 onward the network moved to a unified `F##` series. **Numbering caveats**: Findings 41–43 live under experiment-named files (`exp64-…finding41`, `exp66-…`, `exp67-…`); two files named `finding-25`/`finding-26` in [`findings/`](../findings/) belong to the quantum-IIT arc (below), NOT to QAOA Findings 25/26 above; and Elder's anchor-line "Finding 48" is distinct from Ember's IIT-arc F48 — both collisions are flagged in the files themselves. **Tier column**: `HW` = real QPU (backend named), `sim` = FakeMarrakesh-class noise-model simulation, `analysis` = re-analysis/synthesis of existing data (zero new compute).*

> **ELI5 for this whole section**: the campaign moved from "characterize the chip" to four practical questions — *where* on the chip should you run (placement + quiet qubits), *how* should you start a quantum optimizer (warm-start anchors), *does noise ever actually help* (no), and *what can this hardware demonstrate that classical math can't describe* (indefinite causal order — the crown jewel below). Plus a finance reality-check and a consciousness-math side-quest.

### Warm-start anchors & best-of-k selection (Findings 28–44, F50, F53, F59)

**Plain English**: if you save the best answer a quantum optimizer found previously ("anchor") and restart from it ("warm start"), when does that help? Answers: it helps *within* the same problem (it never hurts, and it rescues near-misses), it does **not** transfer *across* problems, generating a few candidate starts and keeping the best is the reliable move, and both simulated and real-hardware noise preserve the *ranking* of good-vs-bad starts even while shrinking the margins.

| Finding | Result | Tier |
|---|---|---|
| 28 | Shot budget gates the *visibility* of the QAOA depth penalty: at 1024 shots p=3 beats p=5 by +0.20 escape rate; at 256 shots the penalty vanishes — budget-starved comparisons are biased, not just noisy | sim |
| 29 | Warm-start lift generalizes across problem instances but is x0-gated: ~70% of lift variance comes from the optimizer's starting guess, only ~8% from the problem graph | sim |
| 30 | Anchor floor holds (warm start never hurts, worst case −0.003 ≈ noise); lift is inverted-U in anchor quality — biggest for anchors that *just barely failed* (rescue band +0.028) | sim |
| 31 · 34 · 35 | Cross-instance anchor transfer is null-to-negative (mean −0.016, and outlier-driven — one bad anchor carried ~62% of the harm) → transfer arm **KILLED** (Branch B); quality-gated self-warm-start kept | sim |
| 32 · 33 | Lift is mediated by anchor quality (ρ=+0.85); an apparent sign contradiction between two experiments was **definitional** — two different baselines both called "lift" — not instance physics | sim + analysis |
| 36 · 37 | Best-of-k=3 anchor selection recovers the lift (+0.049 paired, p≈0.011) and generalizes to fresh instances; the value is *rescue-insurance* on unlucky first draws (+0.070 when the first draw is bad, ≈0 when it's good) | sim |
| 38 · 40 · 41 | k-adaptive escalation (draw more anchors only when the first looks weak) captures ~0.9–1.06 of the fixed-k lift at ~30% less compute; the threshold τ is a capture-vs-cost Pareto dial, not a universal constant; one-at-a-time escalation is Pareto-efficient (+12% capture-per-compute) | analysis |
| 42 · 43 · 44 | The "noise helps the recipe" anomaly localized: exact density-matrix simulation proves noise *contracts* the underlying landscape gap, so the observed anti-contraction is an **optimization-dynamics** effect (Goldilocks noise-assisted trap escape), not landscape geometry | sim |
| F48ᵃ · F53 | Anchor **rank** survives noise: depolarizing simulation preserves ordering at realistic dose (Spearman ρ≥0.99), and real hardware preserves it perfectly (ρ=1.000 on `ibm_marrakesh`, test-retest stable) — noise shrinks margins, not order | sim + **HW** marrakesh |
| F50 · F59 | Sim-tuned warm-start parameters do NOT transfer to a real QPU (+6.7% sim lift → −0.16% on hardware)… but the run used *default qubit placement*, which F57 shows costs 17–46× — so "irreducible hardware noise" vs "avoidable placement noise" is now an open, pre-registered retest | **HW** marrakesh + analysis |

<sup>ᵃ Elder's anchor-line "Finding 48" (`finding-48-exp73-…`), not the IIT-arc F48.</sup>

> *ELI5: Reusing a good previous answer as your starting point is free insurance — it can't hurt, and it saves the runs that would have just missed. But a tuned start is problem-specific (don't expect it to help a different problem), you can't cheaply predict which random start will be good (so draw a few and keep the best, drawing more only when the first looks weak), and reassuringly, hardware noise blurs *how much* better your best start is without changing *which one* is best.*

### Trap escape & optimizer stochasticity — closing the Exp49–52 loop (Findings 24 corrected, 39 + N=10 recheck)

| Finding | Result | Tier |
|---|---|---|
| 24 (corrected 2026-07-03) | Escape at depth is mostly stochastic: p=3 escapes 10/10, p=5 only ~30–40%, and the "good shallow seeds stay good deep" signal is real but underpowered (LOO-fragile, p=0.084) — corrected verdict ~95% weight on the stochastic hypothesis | sim + analysis |
| 39 + N=10 recheck | The 90% escape plateau at 1024 shots is a *mixture*: a removable decoherence bias floor **plus** an irreducible optimizer trap (one seed fails even noiselessly). The original clean "it's all noise" story was partly an N=5 small-sample artifact — doubling to N=10 moved 2 of 3 data points | sim |

> *ELI5: About a tenth of optimizer runs get stuck no matter how precisely you measure. Some of that is hardware-style noise you could remove; some is the optimizer genuinely wedging itself into a dead end. And a lesson about small samples: conclusions drawn from 5 trials moved substantially at 10.*

### Noise is NOT a resource (F55, F56 + pre-registration integrity audits)

Two independent "noise actually helps" claims from earlier arcs were killed under proper controls; the integrity audits also caught a planned hardware test that was set up to pass vacuously.

| Finding | Result | Tier |
|---|---|---|
| F55 | Finding 10's "noise narrows confidence intervals 34–63%" is **KILLED**: at matched oracle budget the narrower noisy interval has 0% coverage (vs 95% noiseless) — the estimator lands *tightly around the wrong answer*. False precision, not a benefit | sim |
| F56 | "Noise-assisted escape" (Findings 42/43) does not improve actual solutions: final warm-start quality degrades monotonically with noise dose (N=80 paired, CI excludes zero, 0/8 improved in replication) — the rising policy ratio is a scoreboard artifact | sim |
| — | Integrity audits (Exp55 arm-0, Exp56 payload): the "noise rescues trapped seeds" tests were largely vacuous — at p=3 only 1/10 seeds is even trapped noiselessly, and one staged hardware criterion's payload already passed *without* noise. Flagged and demoted before QPU spend | analysis |

> *ELI5: Two seductive results said a little noise made things better. Under honest controls, both evaporated — one was a confidently-wrong answer that merely LOOKED precise; the other improved a ratio while making every actual answer worse. And an audit caught a planned "noise helps" hardware test whose pass was guaranteed in advance, before it wasted quantum-computer time.*

### Placement beats gate count + quiet-qubit tooling (F57, F58, F65–F70)

**Plain English**: the single biggest practical discovery of the summer arcs — *which physical qubits you run on* matters more than *how many gates you run*, and the noise map that tells you where to run is now packaged as a reusable tool.

| Finding | Result | Tier |
|---|---|---|
| F57 | Noise-aware placement of a shallow financial loader cut its bias **46×** vs the noisiest qubits and **17×** vs the default transpiler choice — a real constant-factor win (it does not move the depth wall) | **HW** marrakesh |
| F58 | `quiet_qubits.py`: reusable picker + calibration drift-snapshot + CHSH health check, validated on entanglement quality (best pair S=2.65 — genuine Bell violation — vs dead pair S=0.04) | **HW** marrakesh |
| F65 · F66 | The quiet pick goes stale within ~a day (next day's best qubits were a fully disjoint set) — but the *live* picker still separates working from dead through the drift (CHSH gap +2.35). Never cache the pick; always re-query | **HW** marrakesh |
| F70 | The picker works out-of-the-box on a second device (`ibm_fez`, fez-native indices, zero retuning): working-vs-dead CHSH gap +2.34 on the first try — a general method, not device tuning | **HW** fez |
| F67 · F68 · F69 | Placement vs gate count causally partitioned: with drift removed (same calibration window) placement explains ~73% of the witness decline vs ~27% for gate count (which sat near the shot-noise floor); the dominance held in **all 6** independent layout draws (0/6 reversals, ~4σ each) | **HW** fez |

![Placement beats gate count — F57 bias arms and F68/F69 drift-free partition](../images/fig13_placement_dominance.png)

> *ELI5: A quantum chip is like a neighborhood where some houses are quiet and some are next to a construction site. We built a tool that checks, live, which qubits are quiet today (yesterday's list is already stale), proved it works unmodified on a second chip, and showed in controlled experiments that choosing quiet qubits matters about three times more than shortening your program.*

### Toric-code logical Bell pairs — replicating the QEC round tax (F61–F64)

| Finding | Result | Tier |
|---|---|---|
| F61 | An independently-built L=3 toric code (18 qubits, 2 logical qubits) reproduces a third-party logical-Bell-entanglement demo in simulation: witness 1.32–1.33 vs the separable bound 1.0 | sim |
| F62 | On real `ibm_fez`: one round of *active error correction* collapses the witness (0.570 → 0.113) — independently replicating the outside author's "the QEC round is net-negative" result and echoing Finding 6's ancilla tax. The round-0 shortfall vs the author traced to gate count (~190 vs ~14), with a 9-for-9 stabilizer audit ruling out a bug | **HW** fez |
| F63 · F64 | A 9× cheaper unencoded prep clears the bound (witness 1.499) but confounds two variables at once; a genuine codeword can't be compressed below ~158 gates, and across equally-valid codewords the witness rises monotonically as gate count drops (1.064→0.785 over 158→208) — error-exposure is a real, measured degradation lever | **HW** fez |

> *ELI5: Quantum error correction is supposed to protect fragile quantum states. We rebuilt a published experiment from scratch and confirmed its most sobering result on real hardware: performing one round of the "protection" currently does more damage than it prevents. The protected state also fundamentally can't be made as cheap as an unprotected one — and every extra gate measurably hurts.*

### Financial amplitude estimation meets the depth wall (F51, F54, F78, F79, F81)

**Plain English**: the arc that connects the campaign to its trading roots — and an honest negative for near-term "quantum finance."

| Finding | Result | Tier |
|---|---|---|
| F51 | The adaptive IQAE dose law validated on real hardware at the production point P=0.56 (1.53pp mean error) — but the noise-model simulator is NOT reliably conservative vs real chips (2/4 pre-registered predictions failed) | **HW** kingston |
| F54 | A real market probability — P(QQQ > 725 within ~a month) — computed on real hardware to within +0.019 of truth. But plain-loader sampling scales exactly like classical Monte Carlo, and the Grover speedup that would beat it needs ~10⁴ two-qubit gates: **50–100× past the ~1000-CZ wall** | **HW** marrakesh |
| F78 | Grover amplification of the QQQ tail *survives* on hardware through k=4 (refuting F54's own "garbage by k≈5" pessimism — the contrast peaks at k=4) — but the honest blind multi-k estimate is ~12× *worse* than just reading the shallow loader: no practical QAE win. Both/and: curve-pessimism refuted, practical-no-win corroborated | **HW** marrakesh |
| F79 | The killer isolated in simulation: it's the **entangling-gate depth of the distribution loader** (which multiplies with each Grover power), not the Grover count itself. Shallow 1-qubit loader (0 CZ): MLE error 0.003. Deep 3-qubit loader (124 CZ at k=5): error 0.111 — matching the hardware failure | sim |
| F81 | **The boundary is not stable on silicon.** Ember's pre-registered HW test (Exp98) ran the *identical* deep-QQQ circuits on the *identical* qubits [54,53,55] 11 hours after F78's job — and the blind MLE went from err 0.154 to **err 0.0003**, saturating the quantum Cramér-Rao bound (σ≈0.0009) and beating the plain read ~140×. Pre-registered HW1 **FAILED** (falsifier fired): loader depth is a *risk exposure amplifier*, not a deterministic killer. QAE on today's hardware = **calibration-window lottery**. Shallow arm clean in both windows (the only reliable regime). FakeMarrakesh predicted the *bad* window and missed the good one by ~400× — snapshot noise models describe a window, not the device | **HW** marrakesh |

![QQQ-tail Grover on hardware — contrast survives to k=4, estimator does not](../images/fig14_qqq_grover_depth.png)

> *ELI5: We computed a genuine stock-market tail-risk on a real quantum chip and got within ~2% — a milestone — but a laptop still wins on every practical axis. The quantum speedup that would change that needs circuits 50–100× deeper than today's chips allow. We pinned the culprit as the "data-loading" depth — and then the plot twisted (F81): re-running the exact same deep circuits on the exact same qubits 11 hours later produced a near-perfect textbook result, 500× better. The chip's quality swings that much between calibrations. So quantum finance today isn't "impossible" — it's a slot machine: sometimes you get the textbook speedup, sometimes garbage, and no simulator can tell you which day you're in. Simple models stay clean every time; realistic ones gamble.*

### Quantum-IIT bridge — integrated information Φ on quantum systems (side numbering: IIT-25/26, 46–47, F48–F49, F52, F60, F71–F72)

**Plain English**: a research side-quest applying IIT — the "integrated information" (Φ) measure from consciousness science — to quantum circuits, with a clean punchline: the number-theory structure that dominates classical Φ *completely vanishes* quantum-mechanically.

| Finding | Result | Tier |
|---|---|---|
| IIT-25 · IIT-26 | Classically, only prime-sized XOR rings resist decomposition (special Φ structure). Quantum CNOT rings of EVERY size are universally irreducible (identical operator Schmidt rank 4), and quantum Φ is a uniform ~0.5–0.65 bits even for sizes that are classically zero — the "primes are special" rule is a classical-only artifact | sim |
| 46 · 47 | Quantum Φ_min follows an order-statistics **size law** (φ ≈ −0.0236·log₂(M)+0.75, residuals <0.03 bits, N=3–12); primality explains zero variance once size is controlled. Going classical→quantum compresses the Φ range **354:1**. The linear law must plateau before N≈33 (entanglement bounds forbid zero) | sim + analysis |
| F48 · F49 | The size law holds under full enumeration through N=14 (residual +0.0001 at N=14); the apparent N=15 "floor" was a sampling artifact — a minimum statistic is biased upward when you only sample 8% of the bipartitions | sim |
| F52 · F60 | WHY the number-theory predictions failed: algebraic GF(2) decomposability is Pearl Rung-1 (association-level) structure, physical causal separability is Rung-2 — conflating them produced two falsified predictions. Classical Φ actually grows as ~N⁴·⁸ with parity setting only the amplitude. N=11 exact classical Φ is computationally intractable on this hardware (>56 min, aborted) | analysis |
| F71 · F72 | The odd/even growth-*rate* difference is UNDERPOWERED at 7 data points (honest small-sample statistics: p≈0.10–0.15) — the initial "rates differ" headline was self-corrected; only the amplitude split survives | analysis |

> *ELI5: Φ is a mathematical score from consciousness science for how much a system acts as one integrated whole rather than separate parts. Classically, ring circuits whose size is a prime number score wildly higher. Make the rings quantum and that entire number-theory drama disappears — every size is inseparably entangled and scores about the same, shrinking the spread of scores 354-fold. The arc also modeled good statistical hygiene twice: an exciting "the law breaks at size 15!" turned out to be a sampling illusion, and a "growth rates differ!" headline was retracted as underpowered.*

### ⭐ Indefinite causal order — the quantum switch on real silicon (F73–F77, F80, F82–F83)

**Plain English — the crown jewel of the campaign so far.** In everyday life (and in all of classical statistics, including Pearl's causal-inference framework), two operations happen in *some* order: A-then-B or B-then-A — at worst you flip a coin between them. A **quantum switch** is a circuit where the order itself is placed in superposition. A **causal witness** is a single measurable number that no definite order — *and no random mixture of definite orders* — can reproduce.

> ### 🔀 [**Try the interactive demo →**](https://mblakemore.github.io/quantum/demo/)
> A self-contained, play-first web demo of this arc, grounded 100% in the F73–F77 hardware data
> below. Drag a slider to drain the control's order-coherence and watch the witness trace the
> **measured** `DISC(φ) = 2·cos(φ/2)` law (Pearson 0.9992 on `ibm_kingston`); flip commute vs
> anticommute and watch the real `⟨X_c⟩` swing +0.865 ↔ −0.905 on `ibm_marrakesh`; see the ≥72σ
> three-arm loophole closure. Source: [`demo/index.html`](../demo/index.html) · plan + design notes:
> [`demo/quantum-switch-demo-plan.md`](../demo/quantum-switch-demo-plan.md).

| Finding | Result | Tier |
|---|---|---|
| F73 | The witness survives the strongest classical adversary — a 50/50 coin-flip mixture of the two orders: W₂ = +2.00 noiseless / +1.93 under the noise model, with the mixture arm exactly inert (DISC=0.000) | sim |
| F74 | Causal-order coherence is a **continuous resource**: dialing partial definiteness φ, the witness follows DISC(φ) = 2·cos(φ/2) with max residual 0.0195 — indefiniteness is tunable, not binary | sim |
| F75 | **The witness fires on real hardware**: W = +1.781 on `ibm_marrakesh` (~25× the ±0.07 drift bar), all 3 pre-registered gates PASS — a single control qubit detects that two operations were applied in indefinite order on real silicon | **HW** marrakesh |
| F76 | The continuous cosine law confirmed on a *second* device: Pearson 0.9992, perfectly monotone (`ibm_kingston`); its φ=π endpoint doubles as the classical mixture and reads inert on hardware — cross-device confirmation for free | **HW** kingston |
| F77 | The classical-mixture loophole closed **same-device, drift-free, in one calibration window**: DISC_switch = +1.900 vs DISC_mixture = +0.035 (inert), W₂ = **+1.865 (≥72σ conservative)**. Crucially, the depth-26 mixture and depth-7 definite control are BOTH inert despite a 19-layer depth gap — inertness tracks causal separability, not decoherence | **HW** marrakesh |
| F80 + Pearl synthesis | Honest self-correction: a proposed "independent" DAG-fit corroboration turned out to be an exact rescaling of the witness itself (residual = 2.25·DISC, R²=1.0 to machine precision) — a tautology, retracted *before* being run. The Pearl-structural reading stands: "causally separable" ≡ "representable by a classical causal model with a latent order-selector," and the switch sits *before* Pearl's ladder — its causal skeleton is itself in superposition, so do-calculus has no well-typed input | analysis |
| F82 | **The witness became a GAME and the game was won on two chips**: the Araújo et al. finite 10-unitary commute/anticommute discrimination game, SDP-optimal input distribution (re-solved; bound 0.8690 vs any causally-separable strategy incl. dynamical order), pre-registered and frozen pre-submission. p̂ = **0.9769 (216.8σ, `ibm_marrakesh`)** and **0.9738 (201.0σ, `ibm_fez`)** — 0.3pp cross-device concordance, every one of 51 pairs individually above the bound, null arm = commuting prior +0.2pp on BOTH devices (fixed order buys exactly the prior, measured). Four pre-data catches (Pauli pitfall; identity pairs load-bearing; skeleton uniformity; transpiler pad-cancellation) documented in the finding | **HW** marrakesh + fez |
| F83 | **Capacity activation**: 0.0436 bits/use transmitted through **two completely depolarizing channels** — each exactly zero-capacity, every causally-separable composition provably zero by channel algebra. R̄ = +0.5034 ± 0.0091 = **55.6σ above the causal value of 0**; definite-order null arm measured DEAD on-chip (MI 0.00012 bits); pre-registered signature confirmed: the unconditioned target is fully depolarized even in the switch arm — the bit lives only in the control–target correlation | **HW** marrakesh |

![Quantum-switch causal witness on ibm_marrakesh — switch fires, both classical controls inert](../images/fig11_causal_witness.png)

![Causal-order coherence follows 2cos(φ/2) on ibm_kingston](../images/fig12_causal_cosine_law.png)

**Honest scope**: F73–F77 are a *coherence-of-causal-order* witness (each gate is queried twice), not a black-box query-complexity separation. F82/F83 upgrade the scope: pre-registered *provable-bound beats* (game form and capacity form) against the full causally-separable class including dynamical order — device-characterized (not device-independent; photonic DI prior art acknowledged). Result chain: sim → hardware → adversarial control → same-device drift-free control → cross-device continuous law → **game-form bound beat on two chips → zero-capacity channel activation**.

> *ELI5: Imagine proving that a package was shipped through two sorting centers in BOTH orders at once — not "we don't know which order," but genuinely neither-and-both — and ruling out every mundane explanation, including a mail service that secretly flips a coin each day. That's what these circuits did, on two different real quantum chips, with the statistical strength of a ≥72-sigma result (particle-physics discoveries require 5). The "amount of both-ness" even turns out to be a smooth dial that follows a simple cosine law. One caveat, kept honest: the demonstration certifies the quantum nature of the ORDER, not a computational speedup from it. And one proposed follow-up check was withdrawn by its own author after proving it was circular — a test that cannot fail proves nothing.*

---

![CHSH violation S = 2.74](../images/fig01_chsh.png) ![GHZ sublinear scaling](../images/fig02_ghz_sublinear.png)

![X-basis immunity 3× confirmed](../images/fig03_x_basis_immunity.png) ![Calibration drift ±7pp in 24h](../images/fig10_calibration_drift.png)

![All four mitigation strategies failed](../images/fig07_mitigation_failures.png) ![IAE-MLE 344× better than naive](../images/fig09_qae_iae_mle.png)

*All figures in [`images/`](../images/) — including the newer-arc figures (fig11–fig14) shown inline in the arc sections above — are reproducible from [`scripts/generate_figures.py`](../scripts/generate_figures.py) — every data point traces back to a specific cycle's measured value (commit history in the upstream Whisper / Elder / Lyla repos) or to the cited job ID in [`experiments/job-manifest.md`](../experiments/job-manifest.md). Where a figure is partly schematic — e.g., the time-axis shape in the VQE convergence trajectory or the Loschmidt-echo round axis — this is explicitly called out in the figure caption of the linked finding.*
