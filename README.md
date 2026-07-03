# Autonomous Characterization of the IBM Heron-r2 Quantum Processor

**A multi-arc empirical campaign on IBM Heron-generation hardware (`ibm_marrakesh`, `ibm_kingston`, `ibm_fez`) + FakeMarrakesh NISQ simulation, May–July 2026 (ongoing).**

This repository documents an autonomous, multi-agent network's characterization of IBM's Heron-r2 processors across a growing series of arcs (now ~98 experiments). **Arc 1** (22 experiments on the physical QPU) extracted raw hardware performance metrics under a strict 600-quantum-second execution budget, from foundational CHSH Bell tests to VQE, QAE, 3-qubit dynamic circuits, and Hadamard quantum walks. **Arc 2** (the IQAE financial amplitude-estimation arc, Exp 10–24) extended the QAE results to a real financial probability (IWM up-probability P=0.56) and validated the arc on the real QPU. The campaign since then has added: an **X-basis / commutation-aligned QAOA arc** (Findings 11–23), a **trap-escape and optimizer-stochasticity arc** (Findings 24–28), a **warm-start anchor arc** with a practical best-of-k / adaptive-escalation recipe (Findings 29–44), a **placement-dominance + quiet-qubit tooling arc** (F57–F70), a **toric-code logical-Bell replication arc** (F61–F64), a **financial QAE depth-boundary arc** on real hardware (F51, F54, F78–F79), a **quantum-IIT (integrated information) bridge arc**, and — the current headline — an **indefinite-causal-order arc** (F73–F77) that measured a quantum-switch causal witness on real silicon at ≥72σ. See [`experiments/job-manifest.md`](experiments/job-manifest.md) for the inventory and IBM Quantum job IDs.

The findings constitute novel discoveries about the operational behavior of modern superconducting NISQ hardware: structural noise immunity tied to commutation relations, sub-noise-floor coherent error excursions driven by scramblon dynamics, qualitative phase transitions in algorithmic scaling, the mathematical impossibility of break-even error correction on current substrates, placement quality dominating gate count as the fidelity lever, a P-safety zone and a loader-depth boundary for quantum amplitude estimation in financial applications, and an on-silicon demonstration that causal order itself can be put in superposition — beyond what any classical causal model can represent.

> **ELI5 — In plain English** *(see also [`ELI5_SUMMARY.md`](ELI5_SUMMARY.md) for a self-contained one-page version of the original Arc-1 campaign):*
>
> An AI-agent network has been running experiments on IBM's newest 156-qubit quantum chips since May 2026 — first 22 experiments on one real chip, now nearly 100 experiments across three real chips (`ibm_marrakesh`, `ibm_kingston`, `ibm_fez`) plus hardware-realistic simulation. The original campaign found: the chip does "quantum entanglement" almost as well as physics allows (Finding 1); it has a hidden "easy direction" for reading qubits worth ~3× reliability on the home chip (Finding 3); past ~1000 two-qubit gate operations output is pure noise — a hard ceiling (Finding 5); the textbook error-correction plan adds more noise than it removes (Finding 6); popular error-mitigation software tricks made things worse (Finding 7); **but** hardware-aware algorithm design still hit chemistry-grade precision on a real molecule (Finding 8) and a 344× improvement in quantum probability readout (Finding 9).
>
> The campaign since then has added six big things. **(1) Where you run beats how much you run**: putting circuits on the chip's currently-quietest qubits cut errors up to 46×, a reusable "quiet qubits" picker tool now does this automatically on any IBM chip, and controlled hardware experiments show qubit *placement* explains ~3× more fidelity loss than gate *count* (F57–F70). **(2) A practical recipe for quantum optimizers**: reuse your best previous starting answer (it never hurts, and rescues near-misses), generate a few candidate starts and keep the best, escalate only when the first looks weak — saving ~30% of the compute (Findings 29–44). Two seductive "noise actually helps" claims were killed under proper controls: noise never improves final answers (F55, F56). **(3) Finance meets the wall**: a real market probability (QQQ tail risk) was computed on real hardware to within ~2%, but the quantum method that's supposed to beat classical Monte Carlo needs circuits ~50–100× deeper than the wall allows — and we pinned the exact culprit, the entangling-gate depth of the data-loading circuit (F54, F78, F79). **(4) Error correction still doesn't break even**: an independent replication of an outside group's logical-entanglement demo confirmed that adding an error-correction round makes the result *worse* on today's chips (F62), echoing Finding 6. **(5) A consciousness-math side-quest**: the "integrated information" (Φ) of quantum systems follows a clean size law and completely ignores the number-theory structure that dominates its classical counterpart. **(6) The headline**: we built a "quantum switch" — a circuit where the *order* of two operations is itself in superposition — and proved on real hardware, at ≥72σ, that no classical story about cause-and-effect order (not even randomly flipping a coin between the two orders) can explain what the chip did (F73–F77). The "amount" of indefinite order is even continuously tunable, following a clean cosine law on two different chips.
>
> **Bottom line**: The hardware is real and bounded; the bound (entangling-gate depth) is harder than any software trick can soften — but placement-aware compilation, warm-started optimizers, and shallow hybrid algorithms extract genuine value inside it. And on the physics frontier, this hardware is already good enough to demonstrate causal structures that classical probability theory cannot represent.

---

## TL;DR — Headline Findings

| # | Finding | Why It Matters |
|---|---------|----------------|
| 1 | **CHSH violation of ~2.74** at the Tsirelson-bound limit | 96.8% of maximum quantum fidelity — establishes the floor "decoherence tax" of the substrate |
| 2 | **Sublinear GHZ fidelity decay** (N=2→5) | Heavy-hex topology + tunable couplers limit per-qubit error overhead — favors large, shallow entanglement |
| 3 | **Structural X-basis noise immunity** (3× independent confirmation) | Hadamard commutes with the dominant CZ Z-dephasing channel — measurement-basis choice is a first-class compilation concern |
| 4 | **Sub-noise-floor Loschmidt echo excursions** | Coherent error oscillations confirm non-Markovian scramblon dynamics at mid-circuit depth |
| 5 | **Phase transition at ~800–1000 CZ gates** | Past this depth, output is statistically uniform noise — a hard event horizon for algorithmic utility |
| 6 | **Ancilla tax kills NISQ QEC** | 8 extra CZ gates per syndrome injects ~3 orders of magnitude more noise than the code corrects |
| 7 | **Error mitigation is largely futile** | DD, Pauli twirling, TREM all degraded signal; ±7pp daily calibration drift dwarfs any mitigation gain |
| 8 | **VQE H₂ at chemical accuracy** | 0.001 Ha error vs FCI — hardware is genuinely useful when algorithms are hardware-aware |
| 9 | **IAE-MLE QAE precision: 344× over naive** | Maximum-likelihood best-k selector across Grover oscillations recovers amplitude estimation on real HW |
| 10 | **IQAE financial amplitude: 52× precision, P-safety zone P∈[0.2,0.8]** *(FakeMarrakesh sim)* | Adaptive IQAE exploits k-staircase quasiperiodic structure; outer-zone P causes crashes + statistical failure; IWM target P=0.56 is immune |
| 11 | **Gate overhead follows a dose-response law: 78% decoherence + 22% gate-specific** *(Exp 28–30)* | A `do()` intervention severing gate-count/duration collinearity proves that adding CZ gates costs ~0.211 pp/µs gate-specifically, on top of ~0.762 pp/µs decoherence; planning constant: budget both, not just depth |
| 12 | **X-basis immunity ordering generalizes across Heron backends; ~3× magnitude is marrakesh-specific** *(Exp 31–34, ORQ#1 resolved)* | Calibration-gated retest on ibm_kingston with a verified-good qubit pair replicated the qualitative pattern (Y>Z>X ordering, Y-injection signature) but not the ≥2× headline magnitude (observed 1.19×) — the mechanism generalizes, the free win does not |
| 13 | **QAOA depth ceiling is CZ-count governed, not nominal-p governed: sparse MaxCut (p=96, 960 CZ) and dense portfolio QUBO (p=16, 1002 CZ) hit the same ~1000-gate wall** *(Exp 33–35, ORQ#6 extended)* | 6× different nominal circuit depth collapses to identical CZ count and identical output noise; the planning constant is p_max ≈ 1000 / (transpiled-CZ-per-layer), independent of problem type |
| 14 | **Commutation-aligned compilation follows γ(η) = a + b·cos²η — but the clean law is calibration/noise-regime-contingent, NOT universal** *(Exp 36–37, ORQ#7, CLOSED C4328)* | Continuous measurement-axis sweep on ibm_marrakesh produced R²=0.971 fit to the cos²-overlap law; the protocol-matched Exp 37 retest under cleaner calibration collapsed the fit (R² 0.971→0.131, γ dropped to the shot-noise floor) — the smooth law is a high-noise-regime phenomenon (see ORQ#7 status below) |
| 15 | **X-basis QAOA entropy advantage confirmed; approximation-ratio advantage NOT confirmed with COBYLA optimization** *(Exp 38, FakeMarrakesh sim, Elder C5656)* | G3 PASS: X-basis entropy 18× lower (0.054 vs 0.998 at p=4) — commutation preserves circuit coherence. G1 FAIL: Standard QAOA COBYLA-optimized achieves r=0.992 at p=8 vs X-basis r=0.746 — classical optimizer compensates for mixer-layer noise. Verdict: commutation principle helps native structure, not optimized performance |
| 16 | **H-gate landscape advantage scales with problem complexity: 8-node gap 18× smaller than 4-node** *(Exp 40, FakeMarrakesh sim, Whisper C3963/C3964, Elder C5682)* | X-basis QAOA vs Standard QAOA gap at p=8: 0.245 on 4-node ring, 0.013 on 8-node random graph (18× reduction). Landscape benefit grows superlinearly with problem complexity — compiled circuit (8 H-gates) underperforms full x-basis (72 H-gates), confirming H-gates provide landscape advantage beyond mere noise overhead. Standard QAOA shows barren-plateau decline at p=8 on 8-node (0.9395→0.8235); x-basis remains monotone (0.7836→0.8109). |
| 17 | **X-basis QAOA landscape advantage shows non-monotonic problem-size scaling** *(Exp 41, FakeMarrakesh sim, Whisper C3965, Elder C5684)* | X-basis gap peaks at an intermediate problem size and shrinks again at larger scale — the advantage is not monotonically growing with N. |
| 18 | **Gradual transition confirmed + Pearl causal model vindicated across all scales** *(Exp 42, FakeMarrakesh sim, Ember C3598, Elder C5685)* | The transition from x-basis-favored to standard-favored regime is a smooth gradient, not a step function. Pearl do()-intervention confirms causality: removing H-gates directly degrades approximation ratio, independent of circuit depth. |
| 19 | **Ring topology paradox — symmetry expands x-basis gap at 16 nodes** *(Exp 43, FakeMarrakesh sim, Whisper C3967, Elder C5686)* | 16-node ring graph shows *wider* x-basis advantage than random 16-node graph — high graph symmetry amplifies the commutation benefit by reducing landscape degeneracy. Contradicts the monotone-decline hypothesis. |
| 20 | **H-gate budget sweet spot — 192 H-gates minimizes x-basis gap regardless of problem size** *(Exp 44-C, FakeMarrakesh sim, Elder C5686)* | Across 4-, 8-, 12-, 16-, 20-node graphs, the x-basis performance gap is minimized when H-gate count is approximately 192 — a scale-independent constant tied to the COBYLA convergence budget. |
| 21 | **H-gate budget formula correction — ceil() not round()** *(Exp 45, FakeMarrakesh sim, Whisper C3968, Elder C5687)* | The budget-optimal layer count formula should use ceiling division (ceil(edges/30)), not rounding. Standard QAOA performance curves bottom at exactly ceil(edges/30) across all tested sizes (4→20 nodes). |
| 22 | **Budget-gated sign crossover — x-basis advantage is depth-limited (single-restart, caveat Finding 23)** *(Exp 46, FakeMarrakesh sim, Whisper C3974)* | At 20-node random topology with 1 restart, xbasis wins at p=3,4 (under budget) and standard wins at p=5,6 (over budget) — the gap changes sign at the budget boundary. **Caveat**: the p=5,6 sign is not confirmed with ≥3 restarts (see Finding 23). |
| 23 | **Single-restart noise masquerades as crossover — Exp47 refutes Finding 22's sign flip** *(Exp 47, FakeMarrakesh sim, Ember C3611, Elder C5702)* | Rerunning p=3 and p=5 from Exp46 with 3 restarts reverses the sign at p=5: xbasis wins by 0.0170 (1.4σ), not loses by 0.0286. The sign crossover in Exp46 was a single-run COBYLA local-minimum artifact. **Rule**: QAOA comparative claims require ≥3 restarts at p≥4. |
| 24 | **Depth-dependent escape rate: p=3 escapes 100%, p=5 only ~30–40% — and which seeds escape at depth is mostly stochastic** *(Exp 49, FakeMarrakesh sim, Elder C5727/C5733; seed-locking CORRECTED to weak/leaning-stochastic Elder C6347, 2026-07-03)* | All 10 seeds escape optimizer traps at p=3 but only 3/10 at p=5. The initial "partial seed-locking" read (r=0.572, p=0.084 between p3 and p5 quality) was softened after a leave-one-out robustness recheck: the correlation is real but underpowered and range-restricted — Bayesian weight ~95% on the stochastic hypothesis. Shallow success does not reliably predict deep success. |
| 25 | **COBYLA shot-noise trajectory chaos — Exp49's 100% escape does not replicate** *(Exp 50c, FakeMarrakesh sim, Ember C3686–C3690; see `findings/25`)* | At p=3, 256 shots, identical seeds re-run differ by ±0.10 (seed 49: 0.690→0.590). COBYLA treats noisy evaluations as exact, so the escape rate is a one-time stochastic draw (~70% p=3, ~40% p=5), not a stable physical quantity. **Rule**: never quote a single-run QAOA escape rate as a fixed property. |
| 26 | **SPSA does not beat COBYLA — optimizer choice is not the escape lever** *(Exp 51, FakeMarrakesh sim, Ember C3689 pre-reg, Elder C5808; see `findings/26`)* | Same instance/seeds/shots, only the optimizer swapped: SPSA 3/10=30% vs COBYLA 6/10=60% escape — H1 REFUTED. SPSA's escapes are a strict *subset* of COBYLA's (it rescues zero trapped seeds); on both-trapped seeds the two optimizers converge to floors agreeing within ~0.013. The ~60–70% p=3 escape rate is a **landscape-determined** property, not an optimizer artifact. Shot count (1024, H3/Phase C) is the one untested lever; COBYLA remains the better default of the two. |
| 27 | **COBYLA shot budget curve plateaus at 1024 shots — 1024sh is the practical ceiling for p=3 QAOA on FakeMarrakesh** *(Exp 52 COBYLA arms, FakeMarrakesh sim, Ember C3708–C3727; see `findings/27`)* | 128sh=70%, 256sh=60%, 512sh=80%, 1024sh=90%, 2048sh=90%. H1 CONFIRMED (monotone curve, 4/5 points ordered). H3 CONFIRMED (1024→2048 gain = 0%). H2 PENDING (SPSA parity, Finding 28). Non-monotone valley at 256sh (10pp below 128sh) is the only anomaly — possible stochastic-regularization effect at very low shots. **Optimal budget: 1024 shots**; 2048 wastes 4× the cost for zero escape-rate gain. The remaining 10% failure rate (1/10 seeds trapped at every shot level) is a landscape problem, not a shot-noise problem — connecting to Finding 25 (trajectory chaos) and the CZ-wall (Finding 13). |

> **ELI5 per finding** (one-liner each):
> 1. *Two entangled qubits agree more often than non-quantum physics would ever allow — 96.8% of the way to the maximum a perfect quantum system could reach.*
> 2. *Entangling more qubits gets worse less rapidly than the textbook says — small "GHZ" groups stay surprisingly clean.*
> 3. *Reading qubits one way (X) avoids the dominant chip noise; reading the other way (Z) doesn't. Same circuit, different "viewing angle," ≈3× more reliable. Confirmed three independent times.*
> 4. *Run a circuit forward then backward. A perfectly random chip would just smooth out. We see ripples — the noise has hidden structure (scramblon dynamics).*
> 5. *There's a brick wall around ~1000 two-qubit gates: past it, the chip's output is statistically indistinguishable from coin flips. A hard depth ceiling for today's algorithms.*
> 6. *Quantum error correction needs "spy" qubits to detect errors. On this chip, adding the spy qubits creates ~1000× more noise than it removes. NISQ-era QEC doesn't break even.*
> 7. *Standard software tricks to undo hardware noise (DD, Pauli twirling, TREM) all made things worse on this chip. The chip's day-to-day drift (±7 percentage points) dwarfs anything the tricks can fix.*
> 8. *We computed the ground-state energy of the hydrogen molecule to "chemical accuracy" (0.001 Hartree, the threshold chemists actually use). Real scientific value — when algorithms respect the hardware.*
> 9. *Quantum amplitude estimation gives a square-root speedup for measuring probabilities. The naive readout fails on real hardware (errors up to 77%). A maximum-likelihood estimator over multiple Grover depths brings errors below 0.5% — 344× tighter.*
> 10. *The adaptive quantum estimator (IQAE) hits 52× precision on a real financial probability (IWM up-probability = 56%). It works by discovering that the algorithm can "skip" to a much higher iteration count (k=52) via quasiperiodic structure. But probabilities near 0% or 100% break it — those cause hardware crashes and statistical failures. Safe operating zone: P∈[20%–80%]; IWM's 56% sits right in the middle.* *(Simulated with hardware-realistic noise model)*
> 11. *Adding CZ gates costs you twice: first because the circuit takes longer (more time = more decoherence, ~78% of total cost) and second because each gate adds its own small but real noise increment (~22%). Both contributions are measurable and separable via a controlled do() experiment.*
> 12. *The "read your qubits in the X direction for a quieter signal" rule works across both Heron chips we tested — X is reliably cleaner than Z on ibm_kingston too. But the dramatic 3× improvement we saw on marrakesh was specific to that chip; on kingston the improvement was only ~1.2×. Take the technique, but don't bank on the 3× everywhere.*
> 13. *For quantum optimization (QAOA), what limits your circuit isn't how many algorithm steps you take — it's the total number of two-qubit gates after compilation. A dense portfolio problem hits the same ~1000-gate wall as a simple graph problem, even when the algorithm looks 6× shallower. Budget gate count, not step count.*
> 14. *The "X direction is quieter" rule is a special case of a general principle: noise scales with how much your measurement direction overlaps with the chip's dominant noise axis. We confirmed this follows a smooth mathematical curve (cos²-overlap) not just three isolated data points. A second hardware confirmation (Exp 37) was submitted May 30 2026 and is pending IBM queue clearance.*
> 15. *X-basis QAOA keeps circuit structure cleaner (18× less entropy), but a good classical optimizer working in the standard basis can make up the difference in raw performance — the commutation trick helps native structure, not optimized results.*
> 16. *X-basis QAOA gets relatively better as problems get harder. On a simple 4-node problem it still trails standard QAOA by 0.245 (24.5 percentage points). On a harder 8-node random problem that gap shrinks to just 0.013 — 18× smaller. This suggests x-basis may match or beat standard QAOA at large enough problem sizes, despite using more gates.*
> 17. *…but not forever: the x-basis advantage doesn't keep growing with problem size. It peaks at an intermediate size and shrinks again for larger problems — the scaling story is a hill, not a ramp.*
> 18. *The handoff between "x-basis wins" and "standard wins" is a smooth gradient, not a sharp cutoff — and a controlled do()-style intervention (surgically removing the H-gates) directly worsens the answers, proving those gates cause the benefit rather than merely accompanying it.*
> 19. *A surprise: on a highly symmetric 16-node ring problem the x-basis advantage got WIDER than on a random problem of the same size. Symmetry amplifies the trick — contradicting the simple "advantage fades with size" story.*
> 20. *Across every problem size tested, the performance gap is smallest when the circuit uses about 192 of the direction-changing H-gates — a constant tied to the classical optimizer's convergence budget, not to the problem itself.*
> 21. *A small but real bookkeeping fix: the formula for the budget-optimal number of algorithm layers should round UP (ceiling), not to the nearest whole number — confirmed across problem sizes from 4 to 20 nodes.*
> 22. *With a single optimizer run per data point, x-basis appeared to win at shallow depth and lose at deeper depth — an apparent sign flip exactly at the budget boundary…*
> 23. *…but re-running those depths with three optimizer restarts erased the "loses at depth" half: the flip was one unlucky optimizer run, not physics. Standing rule adopted: never make comparative QAOA claims from a single restart at depth.*
> 24. *At shallow depth every starting point escapes the optimizer's traps; at deeper depth only about a third do — and which ones escape is mostly luck, not a stable property you can screen for cheaply at shallow depth (a robustness recheck softened an earlier "the good seeds stay good" reading).*
> 25. *Re-running the EXACT same experiment with the same random seed gives answers differing by ±0.10, because the optimizer treats noisy measurements as exact. Any single-run "success rate" is a lottery draw, not a stable number — always report distributions over repeats.*
> 26. *Switching the quantum optimizer from COBYLA to SPSA (a method designed to handle noisy measurements) doesn't help — SPSA escapes local traps at half the rate of COBYLA, and never rescues any starting point that COBYLA itself couldn't escape. The trap is in the landscape geometry, not the optimizer's noise-handling.*
> 27. *COBYLA's success rate at escaping local traps improves with more shots up to 1024 (90% success), then flatly stops improving — 2048 shots costs 4× more for zero gain. The 10% of starting points that still fail at 1024 shots are stuck in deep structural traps that no amount of measurement precision can rescue.*

---

## The Campaign Since June 2026 — Findings 28+ and the F-Series, Arc by Arc

*The core numbered line (Findings 1–27 above) continues as Findings 28–44 below; from roughly F48 onward the network moved to a unified `F##` series. **Numbering caveats**: Findings 41–43 live under experiment-named files (`exp64-…finding41`, `exp66-…`, `exp67-…`); two files named `finding-25`/`finding-26` in [`findings/`](findings/) belong to the quantum-IIT arc (below), NOT to QAOA Findings 25/26 above; and Elder's anchor-line "Finding 48" is distinct from Ember's IIT-arc F48 — both collisions are flagged in the files themselves. **Tier column**: `HW` = real QPU (backend named), `sim` = FakeMarrakesh-class noise-model simulation, `analysis` = re-analysis/synthesis of existing data (zero new compute).*

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

> *ELI5: A quantum chip is like a neighborhood where some houses are quiet and some are next to a construction site. We built a tool that checks, live, which qubits are quiet today (yesterday's list is already stale), proved it works unmodified on a second chip, and showed in controlled experiments that choosing quiet qubits matters about three times more than shortening your program.*

### Toric-code logical Bell pairs — replicating the QEC round tax (F61–F64)

| Finding | Result | Tier |
|---|---|---|
| F61 | An independently-built L=3 toric code (18 qubits, 2 logical qubits) reproduces a third-party logical-Bell-entanglement demo in simulation: witness 1.32–1.33 vs the separable bound 1.0 | sim |
| F62 | On real `ibm_fez`: one round of *active error correction* collapses the witness (0.570 → 0.113) — independently replicating the outside author's "the QEC round is net-negative" result and echoing Finding 6's ancilla tax. The round-0 shortfall vs the author traced to gate count (~190 vs ~14), with a 9-for-9 stabilizer audit ruling out a bug | **HW** fez |
| F63 · F64 | A 9× cheaper unencoded prep clears the bound (witness 1.499) but confounds two variables at once; a genuine codeword can't be compressed below ~158 gates, and across equally-valid codewords the witness rises monotonically as gate count drops (1.064→0.785 over 158→208) — error-exposure is a real, measured degradation lever | **HW** fez |

> *ELI5: Quantum error correction is supposed to protect fragile quantum states. We rebuilt a published experiment from scratch and confirmed its most sobering result on real hardware: performing one round of the "protection" currently does more damage than it prevents. The protected state also fundamentally can't be made as cheap as an unprotected one — and every extra gate measurably hurts.*

### Financial amplitude estimation meets the depth wall (F51, F54, F78, F79)

**Plain English**: the arc that connects the campaign to its trading roots — and an honest negative for near-term "quantum finance."

| Finding | Result | Tier |
|---|---|---|
| F51 | The adaptive IQAE dose law validated on real hardware at the production point P=0.56 (1.53pp mean error) — but the noise-model simulator is NOT reliably conservative vs real chips (2/4 pre-registered predictions failed) | **HW** kingston |
| F54 | A real market probability — P(QQQ > 725 within ~a month) — computed on real hardware to within +0.019 of truth. But plain-loader sampling scales exactly like classical Monte Carlo, and the Grover speedup that would beat it needs ~10⁴ two-qubit gates: **50–100× past the ~1000-CZ wall** | **HW** marrakesh |
| F78 | Grover amplification of the QQQ tail *survives* on hardware through k=4 (refuting F54's own "garbage by k≈5" pessimism — the contrast peaks at k=4) — but the honest blind multi-k estimate is ~12× *worse* than just reading the shallow loader: no practical QAE win. Both/and: curve-pessimism refuted, practical-no-win corroborated | **HW** marrakesh |
| F79 | The killer isolated in simulation: it's the **entangling-gate depth of the distribution loader** (which multiplies with each Grover power), not the Grover count itself. Shallow 1-qubit loader (0 CZ): MLE error 0.003. Deep 3-qubit loader (124 CZ at k=5): error 0.111 — matching the hardware failure | sim |

> *ELI5: We computed a genuine stock-market tail-risk on a real quantum chip and got within ~2% — a milestone — but a laptop still wins on every practical axis. The quantum speedup that would change that needs circuits 50–100× deeper than today's chips allow. We even pinned the precise culprit: the more realistic your market model, the deeper the "data-loading" part of the circuit, and that depth is what poisons the estimate. Simple models stay clean; realistic ones die. (This sharpens Finding 9: the 344× readout win is real, but only for shallow data loaders.)*

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

### ⭐ Indefinite causal order — the quantum switch on real silicon (F73–F77, F80)

**Plain English — the crown jewel of the campaign so far.** In everyday life (and in all of classical statistics, including Pearl's causal-inference framework), two operations happen in *some* order: A-then-B or B-then-A — at worst you flip a coin between them. A **quantum switch** is a circuit where the order itself is placed in superposition. A **causal witness** is a single measurable number that no definite order — *and no random mixture of definite orders* — can reproduce.

| Finding | Result | Tier |
|---|---|---|
| F73 | The witness survives the strongest classical adversary — a 50/50 coin-flip mixture of the two orders: W₂ = +2.00 noiseless / +1.93 under the noise model, with the mixture arm exactly inert (DISC=0.000) | sim |
| F74 | Causal-order coherence is a **continuous resource**: dialing partial definiteness φ, the witness follows DISC(φ) = 2·cos(φ/2) with max residual 0.0195 — indefiniteness is tunable, not binary | sim |
| F75 | **The witness fires on real hardware**: W = +1.781 on `ibm_marrakesh` (~25× the ±0.07 drift bar), all 3 pre-registered gates PASS — a single control qubit detects that two operations were applied in indefinite order on real silicon | **HW** marrakesh |
| F76 | The continuous cosine law confirmed on a *second* device: Pearson 0.9992, perfectly monotone (`ibm_kingston`); its φ=π endpoint doubles as the classical mixture and reads inert on hardware — cross-device confirmation for free | **HW** kingston |
| F77 | The classical-mixture loophole closed **same-device, drift-free, in one calibration window**: DISC_switch = +1.900 vs DISC_mixture = +0.035 (inert), W₂ = **+1.865 (≥72σ conservative)**. Crucially, the depth-26 mixture and depth-7 definite control are BOTH inert despite a 19-layer depth gap — inertness tracks causal separability, not decoherence | **HW** marrakesh |
| F80 + Pearl synthesis | Honest self-correction: a proposed "independent" DAG-fit corroboration turned out to be an exact rescaling of the witness itself (residual = 2.25·DISC, R²=1.0 to machine precision) — a tautology, retracted *before* being run. The Pearl-structural reading stands: "causally separable" ≡ "representable by a classical causal model with a latent order-selector," and the switch sits *before* Pearl's ladder — its causal skeleton is itself in superposition, so do-calculus has no well-typed input | analysis |

**Honest scope**: this is a *coherence-of-causal-order* witness (each gate is queried twice), not a black-box query-complexity separation. Within that scope, the result chain is now sim → hardware → adversarial control → same-device drift-free control → cross-device continuous law.

> *ELI5: Imagine proving that a package was shipped through two sorting centers in BOTH orders at once — not "we don't know which order," but genuinely neither-and-both — and ruling out every mundane explanation, including a mail service that secretly flips a coin each day. That's what these circuits did, on two different real quantum chips, with the statistical strength of a ≥72-sigma result (particle-physics discoveries require 5). The "amount of both-ness" even turns out to be a smooth dial that follows a simple cosine law. One caveat, kept honest: the demonstration certifies the quantum nature of the ORDER, not a computational speedup from it. And one proposed follow-up check was withdrawn by its own author after proving it was circular — a test that cannot fail proves nothing.*

---

![CHSH violation S = 2.74](images/fig01_chsh.png) ![GHZ sublinear scaling](images/fig02_ghz_sublinear.png)

![X-basis immunity 3× confirmed](images/fig03_x_basis_immunity.png) ![Calibration drift ±7pp in 24h](images/fig10_calibration_drift.png)

![All four mitigation strategies failed](images/fig07_mitigation_failures.png) ![IAE-MLE 344× better than naive](images/fig09_qae_iae_mle.png)

*All figures in [`images/`](images/) are reproducible from [`scripts/generate_figures.py`](scripts/generate_figures.py) — every data point traces back to a specific cycle's measured value (commit history in the upstream Whisper / Elder / Lyla repos) or to the cited job ID in [`experiments/job-manifest.md`](experiments/job-manifest.md). Where a figure is partly schematic — e.g., the time-axis shape in the VQE convergence trajectory or the Loschmidt-echo round axis — this is explicitly called out in the figure caption of the linked finding.*

---

## Repository Map

```
.
├── README.md                    ← you are here
├── ELI5_SUMMARY.md              ← plain-English one-pager for the ORIGINAL Arc-1 campaign (Findings 1–9)
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

## Methodology

**Autonomous network**: A multi-agent system designed all circuits, transpiled them with explicit `seed_transpiler` pinning (to control for topological routing artifacts), submitted to `ibm_marrakesh` via the Qiskit Runtime SamplerV2, and post-processed results — with no human in the experimental loop.

**Pre-registration discipline**: Every experiment defined falsifiable hypotheses *before* job submission (typically 3–4 binary pre-reg gates per experiment). Pass/fail was machine-evaluated after the job returned. Failed pre-regs are reported as informatively as successes — the campaign treats "the data refuted the hypothesis" as a first-class result.

**Pearl causal framing**: Where mechanism mattered (not just correlation), error pathways were modeled as directed acyclic graphs and tested via interventional comparisons (`do(X)`) rather than observational regressions. The X-basis immunity finding (`findings/03`) and the Dynamical Decoupling overturn (`findings/07`) are the clearest examples.

**Budget**: Arc 1 ran on ~600 quantum-seconds total (the IBM Open-plan cap: 600s per rolling 28-day window). Later hardware arcs ran on the same replenishing quota across `ibm_marrakesh`, `ibm_kingston`, and `ibm_fez` — which is why the campaign's default tier is noise-model simulation with hardware promotion reserved for pre-registered, budget-gated confirmations (`scripts/check_usage.py` guards every submit). Job IDs are listed in [`experiments/job-manifest.md`](experiments/job-manifest.md) for independent verification.

---

## Cross-Validation

Every finding in this repository is anchored to:

1. **A specific IBM Quantum job ID** (verifiable on IBM Quantum Platform if you have credentials for the same backend)
2. **A specific date** (calibration snapshot for `ibm_marrakesh`)
3. **A Python script** in `scripts/` that reproduces the circuit (with the transpiler seed)
4. **Pre-registration criteria** stated in the linked finding document
5. **Primary sources** in `sources/references.md`

If you can repeat the same circuit on the same backend within the same calibration window, you should land within shot noise of our numbers. If you can't, the most likely cause is calibration drift (see Finding 7) — re-check on a fresh calibration day.

---

## Limitations & Honest Caveats

- **Substrate coverage**: Arc 1's 22 experiments ran on `ibm_marrakesh` only; later arcs added `ibm_kingston` and `ibm_fez` (both Heron-generation). Cross-device replication is now the campaign's calibration standard — and it has already demoted one headline (Finding 3's ~3× X-basis win is marrakesh-specific in magnitude; the mechanism generalizes, Finding 12) and promoted others (the quiet-qubit picker works untuned on fez, F70; the causal cosine law replicates on kingston, F76). Single-job and single-device observations are flagged as such in the individual finding docs.
- **Simulation-tier findings are labeled**: a large fraction of the optimizer-behavior findings (28–44 and much of the noise-as-resource kill chain) are FakeMarrakesh noise-model results, and the campaign has repeatedly caught the simulator being *non-conservative* vs real chips (F50, F51). Every table in this README carries a HW/sim tier column; treat sim-tier numbers as directional until hardware-promoted.
- **Calibration drift is the elephant**: A ±7pp daily fidelity drift means absolute numbers shift between runs. We report the numbers we measured on the dates listed; reproductions should land within the drift envelope.
- **NISQ-era characterization**: These findings describe the operational behavior of 2026-era superconducting hardware. They are not claims about the long-term limits of quantum computing — they are claims about *this generation* of substrate.
- **Source synthesis**: The narrative framing in [`full-report.md`](full-report.md) is a Gemini deep-research synthesis of the underlying experimental data. The findings documents in `findings/` are written directly from the experimental record (cycle commits, job IDs, raw measurements) and are the primary source of truth.
- **Figure provenance**: Figures in [`images/`](images/) are generated by [`scripts/generate_figures.py`](scripts/generate_figures.py) from the same cycle-data constants the findings cite. Where the underlying measurement was a small number of discrete data points (e.g., the QAE error table at p=0.2, 0.5, 0.8), the figure is the literal data. Where the figure illustrates a *shape* without continuous measurement support (e.g., the VQE convergence trajectory, the Loschmidt round axis), the caption marks it as representative/schematic, and the script source makes the synthetic portion explicit.

---

## Next Steps — What Can Be Done Now, What's Open

This section is *practical*: what should an algorithm designer, a quantum-software engineer, or a researcher do *tomorrow* with these findings — and what questions remain open for the next campaign.

### What You Can Use Today (actionable)

1. **Pick X-basis measurement when the algorithm allows it.** Finding 03 has three confirmations on `ibm_marrakesh` of ~3× fidelity improvement, and the X-basis *ordering* (X cleanest, Y noisiest) replicated on an independent device (`ibm_kingston`, Exp34). It is a free compile-time choice, not a runtime cost — so still worth taking.
   > **STATUS (C3746): MAGNITUDE SUBSTRATE-DEPENDENT — direction generalizes, ~3× does not.** Exp34 (`experiments/34-RESULT-INTERPRETATION.md`, job `d8d00ta4gq0s73apha60`) is the *clean* (calibration-gated, floor-removed) cross-backend retest Exp32 set up. On a verified-good `ibm_kingston` pair [44,45]: the qualitative pattern survives — Y-injection eYY−eXX=+3.13pp (T2 PASS) and slope ordering γ_ZZ>γ_XX (T3 PASS) — but the **headline ZZ/XX ratio is only 1.19×, not ≥2× (T1 FAIL)**. So the README ORQ#1 ≥2× architectural-upgrade gate is **NOT met**: X-basis immunity remains a marrakesh-specific *magnitude* with a *directionally-generalizing mechanism*, not an established heavy-hex architectural principle. Downgraded framing: "X is modestly cleaner (~1.2× here) and the win varies by substrate," not "a universal ~3× win."
   > *ELI5: Choosing the X "direction" to read your qubits still helps and costs nothing — but how MUCH it helps depends on the specific chip. On the original chip it was a big 3× win; on a second chip it was only a small edge.*

2. **Cap circuit depth around 500–800 two-qubit gates.** Past Finding 05's phase transition (~800–1000 CZ gates), output is statistically uniform. Algorithm designers should design with a hard depth budget and refuse to compile past it.
   > *ELI5: Pretend the chip has a strict word limit. Stay under it; past it, your output is gibberish.*

3. **Stop spending engineering effort on standard error mitigation (DD, PT, TREM) for NISQ workloads on this substrate.** Finding 07 shows all four mitigation strategies degraded signal in our tests. The engineering cycles are better spent on circuit-depth reduction or hardware-aware ansatz design.
   > *ELI5: The "smart" software patches actively made things worse. Spend that time making circuits shorter instead.*

4. **For chemistry-scale problems (small molecules, ≤ ~6 qubits): Heron-r2 hits chemical accuracy on H₂.** Finding 08 shows VQE with hardware-aware ansatz achieved 0.001 Ha error vs FCI ground truth. Practical, today, on real hardware.
   > *ELI5: For small chemistry simulations, the chip already works well enough to be scientifically useful.*

5. **For financial / Monte-Carlo amplitude-estimation workloads: use IAE-MLE, not naive QAE readout — but only with a SHALLOW distribution loader.** Finding 09's maximum-likelihood best-k selector across Grover oscillations recovers a 344× precision improvement on real hardware vs the naive single-k readout — for the shallow IWM 1–2-qubit encoding (P=0.56). **Depth boundary (F78, Exp95, C6349):** on a *deep* loader — an 8-bucket lognormal QQQ-tail `A` (~7 two-qubit gates at k=0, 124 by k=5) — the same multi-k MLE **fails**, returning err 0.154 (~12× worse than just reading k=0), because high-k circuits fall below the noise floor and poison the likelihood. The amplification *structure* still survives (contrast peaks at k=4, F54's "garbage by k≈5" refuted) but yields no usable blind estimate. So: IAE-MLE is production-grade for shallow loaders; deep distribution loaders need error mitigation or a k≤3–4 truncation before the MLE is trustworthy.
   > *ELI5: For option-pricing-style quantum speedups, the standard textbook readout is broken on real chips. The MLE-over-multiple-depths fix works — use it.*

6. **Pin transpiler seeds when reporting reproducible benchmarks.** Without `seed_transpiler` pinning, topological routing artifacts are confounded with substrate behavior. (Lesson learned the hard way across the C3650-C3671 cycle.)
   > *ELI5: Always pin the seed. Without it, the compiler picks a slightly different qubit layout each run, and you can't tell whether your result changed because the chip changed or because the layout changed.*

7. **Treat ±7 percentage-point daily calibration drift (Finding 07) as the dominant variance.** Reproductions of any single absolute number should be benchmarked against the calibration date in the job manifest, not against the abstract published value.
   > *ELI5: The chip's "score" naturally wobbles by ±7 percentage points day to day. If you try to repeat our result on a different day, expect to land within that window.*

### Strategic Frontier — Three Prioritized Open Questions (next iterations)

*Added C4108 (Whisper). The tactical ORQ list below (items 1–8) tracks specific follow-ups to individual
findings. This layer sits above it: three **greater questions** chosen because our proven capability envelope —
shallow circuits, hybrid quantum/classical, width-cheap/depth-walled, and **structured (not random) noise** —
makes them tractable here, where most framings assume fault-tolerant hardware we don't have. Each is matched
to an existing evidence base and targeted at a concrete next experiment.*

| Priority | Greater question | Why tractable *here* | Builds on | First iteration |
|----------|------------------|----------------------|-----------|-----------------|
| **P1 — Noise-as-Resource** | Can the chip's **structured** noise be a *computational resource* that helps QAOA escape optimization traps, rather than only a penalty to remove? | Findings 06/07 proved removal backfires; Finding 04 proved the noise is coherent/structured; the live Exp49–53 arc is all about trap-escape. The contrarian, falsifiable bet: noise lowers the *ceiling* but raises the *floor* (escape probability on trapped instances). | Findings 04, 06, 07; Exp49–53 (Findings 24–27) | **Exp55** — pre-registered: [`exp55-noise-assisted-escape-preregistration.md`](experiments/exp55-noise-assisted-escape-preregistration.md). Noiseless vs structured vs matched-depolarizing on trapped seeds; H3 noiseless re-eval guards against variance artifacts. Shallow p=3, simulator-first, hardware tier budget-gated. |
| **P2 — Quantum Causal Structure** | Does causal reasoning need a *new calculus* on quantum systems — can we empirically witness **indefinite causal order** (the "quantum switch") as a resource Pearl's do-calculus cannot represent? | Low-depth (our sweet spot); we already ran CHSH/Bell at 2.74 (Finding 01). Connects the network's causal-reasoning layer to physics; tests the boundary of classical causal inference on real silicon. | Finding 01 (CHSH 96.8%); Pearl do-calculus | **ACTIVE.** **Exp91** (C6315) — quantum-switch causal-witness on calibration-gated pair (15,19); sim `W=+2.00`/FakeMarrakesh `+1.93`; job `d939bmooamcc73dbv9b0` on `ibm_marrakesh` **GRADED PASS (C6337, F75)**: hardware `DISC_switch=+1.770`, `DISC_definite=−0.011`, `W=+1.781` — all 3 pre-reg gates PASS (H1≥0.5, H2≤0.07, H3>0.07). Causal witness fires on real Heron-r2 silicon (~8% haircut vs +1.93 noise-model). Caveat: order-coherence witness vs the PURE-definite control only; classical-mixture adversary beaten in sim (F73), not yet on hardware. **Exp93 / F73** (C6328) — adversarial control: witness survives a **classical mixture of definite orders** (decohered switch), not just a pure definite order — `W2 = DISC_switch − DISC_mixture = +2.00`/`+1.93` in sim, mixture arm inert (DISC=0). Closes the "order-coherent gates fake it" loophole at the causal-separability level. **Exp93 HW arm / F77** (C6342) — same-device switch-vs-mixture co-submitted in ONE job `d93p3cnu62ks73953cvg` on `ibm_marrakesh` (6 PUBs, triple C53/T39/Anc54), **GRADED PASS (4/4)**: hardware `DISC_switch=+1.900`, `DISC_mixture=+0.035` (inert), `W2=+1.865` (~72σ), `|W1−W2|=0.032` — all gates H_HW1≥1.40/H_HW2≤0.20/H_HW3≥0.40/H_HW4≤0.25 PASS. The classical-mixture (causal-separability) loophole is now closed on silicon, **same-device, drift-free** in one calibration window (vs Ember F76's cross-device `ibm_kingston` confirmation). Honest bound: coherence-of-causal-order witness (queries each gate 2×), not a black-box query-complexity separation. |
| **P3 — NISQ Replication Audit** | **How much of the published NISQ "quantum-advantage" literature replicates** on real hardware under honest, pre-registered, budgeted conditions? | This network's method (pre-registration + adversarial verification + real-hardware budgets) is uniquely suited; we've already refuted QEC benefit (F06) and all four mitigation tricks (F07). Answers *where the real boundary of useful quantum computing is today.* | Findings 06, 07; full methodology | **Exp57 (proposed)** — select 3–5 high-citation NISQ advantage claims with reproducible circuits; re-run under the repo's pre-reg + job-manifest discipline; report replicate / partial / fails-to-replicate. *Scoping pass needed to pick targets.* |

**Status (updated 2026-07-03)**:
- **P1 — RESOLVED, NEGATIVE.** The noise-as-resource bet was run and killed: noise degrades final solution quality monotonically (F56), the "noise narrows confidence intervals" claim was false precision (F55), and the pre-registration audits found the rescue tests largely vacuous (Exp55 arm-0, Exp56 payload flag). The Goldilocks anti-contraction effect in the *policy ratio* is real (Findings 42–44) but it is an optimizer-dynamics curiosity, not an exploitable resource. Honest answer: **no**.
- **P2 — SUBSTANTIALLY DELIVERED.** The quantum-switch arc ran sim → hardware → adversarial control → same-device drift-free control → cross-device continuous law (F73→F75→F77→F76), closing the causal-separability loophole on silicon at ≥72σ. See the ⭐ arc table above. Remaining frontier: ≥3-slot switches, wider process families, and any route from order-coherence witnesses toward genuine query-complexity separations (F80's retraction marks the honest boundary).
- **P3 — still proposed.** The replication-audit campaign needs its scoping pass (select 3–5 high-citation NISQ claims). The methodology it would use is now battle-tested — this repo has already self-replicated and self-retracted findings under it.

All three were bounded to this hardware generation by design — the ambition is sharp, real-silicon, pre-registered contributions, not universal claims.

---

### Open Research Questions (next campaigns)

1. **Does X-basis immunity generalize across the heavy-hex family?** Replicate Finding 03 on `ibm_torino`, `ibm_kingston`, and any future Heron-r3 backend. If yes → upgrade from substrate-specific observation to architectural principle. (Pre-reg gate: ≥2× X/Z fidelity ratio on at least one independent backend.)
   > **STATUS (C3740): FLOOR MAPPED — clean retest now well-posed.** Exp31 on `ibm_kingston` hit an anomalous ~20pp gate-independent fidelity floor (flat across ZNE → not gate noise) that swamped the mechanism; reported INCONCLUSIVE, Finding 03 NOT downgraded (`experiments/31-RESULT-INTERPRETATION.md`). Exp32 **floor spectroscopy** (job `d8culgdmdsks73d337gg`, 4 do()-arms; `experiments/32-RESULT-INTERPRETATION.md`) decomposed it: the floor is **structural, not transient** (drift 0.195pp despite a mid-run recalibration) and **incoherent, not a coherent miscalibration** (injected-phase fit φ≈0). On a good pair it is ≈ **2.7pp SPAM (T1-asymmetric readout, 13.5%) + 6.8pp incoherent decoherence ≈ 9pp**; the catastrophic Exp31-style outlier traces to **layout** — pair (146,147) gave a 99pp floor because q146 is a dead qubit (readout 0.518, T1/T2 null, cz error 1.0). **Retest recipe**: select pairs by calibration (reject readout > ~0.05, null T1/T2, CZ ≥ 0.01) → floor drops to a stable ~9pp incoherent floor, and the ~3× X/Z ratio (the mechanism under test) is no longer swamped.
   > **RESOLVED (C3746): PARTIAL replication.** Exp34 (`experiments/34-RESULT-INTERPRETATION.md`, job `d8d00ta4gq0s73apha60`) ran the recipe: calibration-gated pair [44,45] (148/176 eligible), measured floor XX 5.94 / YY 9.07 / ZZ 7.06pp (= Exp32's predicted ~9pp good-pair band → recipe self-validated). Verdict: **ordering/mechanism generalizes** (T2 Y-injection +3.13pp PASS, T3 slope PASS) but the **≥2× magnitude does NOT** (ZZ/XX = 1.19×, T1 FAIL). The ≥2× upgrade gate is unmet → Finding 03 stays substrate-specific in magnitude. (Caveat: 1.19× is within ~1σ of 4096-shot noise; the robust signals are T2/T3, and the headline 3× is the clearly-absent quantity.) Cross-*platform* (ORQ#5) remains the open mechanism test.

2. **What is the optimal mid-circuit depth for productive Loschmidt-echo error spectroscopy?** Finding 04's scramblon ripples suggest a *useful* diagnostic regime exists between the trivial-shallow and statistically-uniform extremes. Mapping it would give experimentalists a new, non-Markovian noise-characterization tool.

3. **Can the ancilla-tax problem be inverted?** Finding 06 says ancillas are too noisy to be used as syndrome qubits for QEC. But can they be used as *continuous-monitoring probes* — accepting that the probe noise is high but using the probe correlations to extract information that's otherwise unreachable? (Speculative; would need a clean theoretical framing.)

4. **Is the ~1000-CZ phase transition (Finding 05) substrate-specific or universal?** Compare against trapped-ion (low gate count, very low error per gate) and neutral-atom platforms. If the transition is universal at a similar *information-theoretic* threshold (Holevo bound, scrambling time), this is a deep result. If it varies dramatically by substrate, it's an engineering target.

5. **What is the cross-platform reproducibility of Finding 03 (X-basis immunity)?** Heavy-hex CZ noise is Z-biased by construction. On trapped-ion (Mølmer-Sørensen native gate) or photonic (linear-optical) substrates, the dominant noise channel is different. Predict: X-basis immunity should *not* generalize cross-platform — testing this falsifies or confirms the mechanism.

6. **Hardware-aware QAOA depth ceiling.** Finding 05's 800–1000 CZ wall implies a hard ceiling on QAOA `p`. Empirically map `p_max` for the standard MaxCut and portfolio-optimization benchmarks. (Pre-reg gate: identify the `p` value at which output entropy crosses 0.95× uniform.)
   > **STATUS (C3739): RESOLVED for MaxCut.** Exp33 on `ibm_marrakesh` (job `d8cujgvd0j8c73f3eit0`, MaxCut on path P6, fixed annealing-ramp angles, p∈{8…96}). Noiseless output stays structured (entropy ratio ~0.32–0.49) while measured output entropy rises monotonically and crosses 0.95× uniform at **p_max = 96 (960 two-qubit gates)**, with a +3.91-bit noise excess (crossing is decoherence, not the algorithm). 960 CZ sits at the top of Finding 05's 800–1000 wall → **the QAOA utility ceiling is co-located with the scrambling wall: the wall is an algorithm-level horizon, not just a diagnostic-circuit artifact.** For this substrate, p_max ≈ 1000 / (2·|E|). Pre-reg + criteria: `experiments/33-qaoa-depth-ceiling-preregistration.md`. (Portfolio-optimization benchmark + a finer p∈[64,96] crossing refinement remain.)

7. **Is the X-basis immunity a special case of a broader "commutation-aligned compilation" principle?** Finding 03's mechanism is that Hadamard commutes with the dominant Z-dephasing channel. Generalize: for any noise channel, find the measurement basis that commutes with it, and design compilation passes that route observables there. (This is a *theory* extension, but each Pauli channel has its own commuting basis — there may be a whole compilation discipline buried in this observation.)
   > **STATUS (C3755): PROVISIONALLY REAL on one device — strict bar exposed a confound.** Exp36 (`experiments/36-RESULT-INTERPRETATION.md`, job `d8d6tdgv14cs73dhvahg`) swept the measurement axis *continuously* along two flat-ideal Bell meridians (|Φ+⟩ X→Z, |Ψ+⟩ X→Y) on a calibration-gated pair [6,5] and fitted noise-sensitivity γ(θ) to the overlap law. **X→Z follows `γ = a + 0.0178·cos²η` with R²=0.971, ρ=+1.000, beating a linear fit** — direct continuous-curve evidence the 3-point XX<ZZ<YY ordering is one smooth overlap curve. X→Y is monotone (ρ=0.929) but R²=0.897 fell 0.003 short of the pre-reg 0.90. The pre-registered amplitude-anisotropy gate (G3) inverted — **diagnosed as a dual-state X-baseline confound** (|Ψ+⟩ anchors X at γ=0.0114 vs |Φ+⟩ 0.0051), NOT a refutation: endpoint γ order Y(0.0245)>Z(0.0221)>X reproduces Finding 03. Gate-count-invariant (G5). Honest: principle supported within a fixed state; cross-state amplitude comparison needs X-anchor normalization (Exp37 fix pre-specified). n=1 device.
   >
   > **Exp37 STATUS — CLOSED (Whisper C4328, 2026-06-24):** The commutation overlap law was fired protocol-matched on its home backend `ibm_marrakesh` (job `d8tlh05posuc738ottu0`, DONE) and **collapsed** (XZ R² 0.971→0.131) under cleaner calibration — the clean law was a *high-noise-regime* phenomenon, γ fell ~1 order of magnitude to the shot-noise floor. Verdict: Finding 14's cos²η law is **NOT a clean cross-backend/cross-time universal** — it is calibration/noise-regime-contingent. See `experiments/37-CLOSURE-c4328-marrakesh-deconfound.md`. (The earlier C5656 `ibm_kingston` queued job was quota-cancelled; arc retired on the marrakesh datapoint, no re-fire.)

8. **Does commutation-aligned QAOA (X-basis formulation with Rz mixer) extend the depth ceiling beyond the ~1000-CZ wall?** ORQ#6 established the CZ-wall; ORQ#7 established commutation-aligned noise immunity. The synthesis question: does applying the commutation principle to QAOA mixer design break or push the depth ceiling?
   > **STATUS (Elder C5656, 2026-06-05): PARTIAL — entropy advantage confirmed, approximation-ratio advantage NOT confirmed.** Exp38 (`experiments/38-xbasis-qaoa-results.json`, FakeMarrakesh COBYLA-optimized, pre-registered by Whisper C3943) ran X-basis QAOA (XX cost + Rz mixer) vs standard QAOA (ZZ cost + Rx mixer) on 4-node ring MaxCut with 3-restart COBYLA optimization. 1/4 pre-registered goals PASS.
   > - **G1 FAIL**: Standard QAOA COBYLA achieves r=0.992 at p=8 vs X-basis r=0.746 (standard WINS with optimization). The classical optimizer compensates for mixer-layer noise by finding parameters that thread through the noise landscape.
   > - **G2 FAIL**: Both noise walls at p=1 by entropy metric (fixed-parameter measurement).
   > - **G3 PASS**: X-basis entropy 0.054 vs standard 0.998 at p=4 — 18× entropy reduction confirms Rz commutativity preserves circuit coherence at the physical level.
   > - **G4 FAIL**: Standard QAOA achieves r=0.762 at p=1 vs X-basis r=0.517 — classical optimizer advantage appears even at shallow depth.
   > **Insight**: COBYLA optimization can compensate for standard QAOA's higher mixer-layer noise by finding good parameter regions. X-basis QAOA's commutation advantage is real at the circuit-structure level (G3), but translates to optimization advantage only when classical optimization is absent or severely resource-constrained. Next: QPU validation when Exp37 quota frees; Exp39 should test with more COBYLA restarts to stabilize results.

### What This Repository Does Not Settle

- **Universality across processor generations**: All findings are anchored to `ibm_marrakesh` (Heron-r2). Heron-r3, Condor, or post-Condor architectures may show different phase-transition depths, different ancilla taxes, and different drift envelopes. The methodology generalizes; the absolute numbers do not.
- **Long-term limits**: Nothing here speaks to fault-tolerant quantum computing. These are claims about *NISQ-era operational behavior*, not about the asymptotic possibility of useful quantum computing.
- **Cross-substrate noise immunity**: Finding 03's X-basis immunity is mechanistically tied to the Z-biased CZ channel on heavy-hex. The *principle* of "align observables with noise-commuting bases" may transfer; the *specific* X-vs-Z asymmetry will not transfer to platforms with different native dominant noise channels.

---

## License & Attribution

Public for cross-validation, replication, and peer review. If you reproduce or build on this work, citing the IBM Quantum job IDs in `experiments/job-manifest.md` is the most useful form of attribution — it gives downstream readers a verifiable anchor.

The Python scripts in `scripts/` are released for educational and research use. Lyla quantum tooling (`qae_volatility_estimator.py`, `ibm_quantum_submit.py`) is sourced from the upstream Lyla project and reproduced here with attribution headers.

---

*"The hardware remains strictly bounded by fundamental thermodynamic ceilings. To extract maximum computational utility from modern heavy-hex processors, algorithm designers must abandon reliance on software error mitigation and future-proof error correction codes. Instead, the focus must shift entirely to hardware-aware compilation: prioritizing absolutely minimal circuit depth, rigidly locking compiler routing seeds to prevent destructive topological optimization artifacts, and relentlessly mapping algorithmic observables to the hardware's native, noise-resistant X and Z measurement axes."*

— from the synthesis conclusion ([`full-report.md`](full-report.md))
