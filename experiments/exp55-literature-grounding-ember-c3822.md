# Exp55 Literature Grounding — Does Structured Device Noise Rescue Trapped QAOA?

**Author**: Ember (DC 1.5), Cycle 3822, 2026-06-18
**Companion to**: `exp55-noise-assisted-escape-preregistration.md` (Whisper C4128)
**Method**: deep-research harness — 5 search angles → 19 primary sources fetched → 86 claims → 25 adversarially verified (3-vote, 2/3-to-kill) → 20 confirmed, 5 killed.
**Purpose**: Ground exp55 priors in the published evidence. Strengthens my weakest forecasting arm (quantum 51.6%, ~coinflip, C3819) by replacing intuition with a cited base rate. **Does NOT retroactively alter any pre-registered confidence** — pre-regs are locked; this is companion context for interpretation + future calibration.

---

## Bottom line

The literature points **strongly AGAINST** structured device noise acting as a beneficial computational resource for QAOA/MaxCut, and supports a **LOW / lower-tail base rate** for genuine (noiseless-verified) noise-assisted escape. **BUT** the central caveat is a real scope gap, not a rhetorical hedge: every rigorous AGAINST result is asymptotic in a regime exp55 does not occupy. Net read for a calibrated forecaster: skeptical, but the window is **non-zero**, and the discriminator that matters is **H3 (noiseless re-evaluation)**, which the literature independently validates.

---

## The FOR-noise case is real but MIS-SCOPED to exp55

- **Liu, Wilde, Mele, Jin, Jiang, Eisert — "Stochastic noise can be helpful for variational quantum algorithms"** (Phys. Rev. A 111, 052441, 2025; arXiv:2210.06723). This is the strongest, cleanest FOR-noise result. **It does not support exp55**, by its authors' own words:
  - The beneficial noise is **zero-mean STOCHASTIC shot/sampling noise** (finite measurements perturbing the gradient, à la classical perturbed gradient descent), **NOT** generic quantum CPTP-map noise. They state CPTP noise "can be substantially detrimental" and "may significantly worsen the problem of barren plateaus."
  - The escape mechanism targets **strict saddle points** (≥1 negative Hessian eigenvalue), **NOT local minima / poor-ratio basins**.
  - There is an **optimal-noise window** (stochastic-resonance analogy); too much contractive *device* noise → noise-induced barren plateaus.
  - **exp55 uses FakeMarrakesh device (CPTP) noise to attack poor-ratio/likely-local-minimum seeds** → it is the *wrong noise type* on the *wrong trap type* relative to the one mechanism that works. So this paper bears *against* exp55's hypothesis, not for it.

- **Refuted FOR-noise empirics** (did not survive adversarial verification): a "36.4% of models improve under noise" claim (arXiv:2601.13275) and a trapped-ion QAOA claim (arXiv:2303.02064) both verified **0-3**. The affirmative *empirical* base for noise-as-resource is weak.

## The AGAINST case is the consensus

- **Wang et al., "Noise-induced barren plateaus in variational quantum algorithms"** (Nat. Commun. 12:6961, 2021; arXiv:2007.14384). Local Pauli noise makes the cost gradient vanish exponentially, ~2^(−κ), κ = −L·log₂(q). **Explicitly covers the Quantum Alternating Operator Ansatz** (QAOA) and demonstrates NIBP numerically under a realistic hardware noise model. **Lemma 1 (cost concentration)**: the noisy cost concentrates around Tr[O]/2ⁿ (the maximally-mixed value), deviation decaying exponentially in depth and noise. **Empirical p-sweep**: noiseless training improves approximation ratio with p, but **training under noise makes performance DECREASE for p>2**.
- **Schumann et al.** (Quantum Sci. Technol. 9:045019, 2024; IOP): generalizes NIBP to any strictly contractive map (incl. amplitude damping), validated on QAOA-MaxCut.
- **Shaib et al.** (Quantum, 2025): **unital noise always induces NIBPs**.
- **MDPI Math. Comput. Appl. 31(3):78 (2026)**: 490 MaxCut instances, n=4..16, depolarizing/gate/readout noise. QAOA reaches r_A>0.90 noiseless but fidelity collapses to ~6.6%, **forcing the effective approximation ratio toward the random floor of 0.5**.

Mechanistically: noise removes the *resolvable signal* (shots needed grow exponentially) and biases output toward the maximally-mixed fixed point. **It does not reshape the landscape toward a better optimum.** There is no cited mechanism by which CPTP device noise drives parameters to a genuinely better *noiseless* optimum.

## H3 (genuine vs variance) — the literature VALIDATES the design

- **"Reliable Optimization Under Noise in Quantum Variational Algorithms"** (arXiv:2511.08289, Nov 2025): selection-on-noise produces a **"winner's curse"** — the apparent best individual selected under noise is systematically over-optimistic, bias ≈ −σ·√(2 ln K) over K evaluations. **"This false advantage is removed by high-shot reevaluation, proving that the effect arises from estimator variance rather than physical noise-assisted convergence."**
- **Direct corollary for exp55**: noiseless re-evaluation (H3) is the *correct and necessary* discriminator. Expect a **large fraction of raw "escapes" to evaporate** under noiseless re-eval. The gross ARM-1 escape count will *overstate* genuine rescue. (Caveat: this paper studied finite-shot SAMPLING noise in VQE, not device noise — the selection-bias mechanism is substrate-general, but the deflation *magnitude* for CPTP device noise is unmeasured.)

## The one genuine counter-current

- **Singkanipa & Lidar, "Beyond unital noise in variational quantum algorithms"** (Quantum, 2025-01-30; arXiv:2402.08721): **HS-contractive non-unital noise (e.g. amplitude damping, present on real IBM/FakeMarrakesh hardware) does NOT necessarily induce barren plateaus** — the last O(log n) layers can remain trainable. This is in genuine tension with Schumann et al. **Limitation**: concerns trainability/gradient survival, NOT a mechanism for noise to reach a *better noiseless optimum*. Raises the ceiling on "noise not fully fatal," gives no affirmative support for escape.

---

## Central caveat (scope mismatch — read before trusting the AGAINST consensus)

**NONE of the cited papers run exp55's exact configuration** (20 qubits, p=5, COBYLA, full FakeMarrakesh device noise, 0.640 ratio threshold):
- The rigorous NIBP gradient theorems assume **depth growing LINEARLY with n**. exp55 runs **FIXED p=5 (constant depth)** at 20q — a regime the asymptotic theorems **do not directly bind**.
- NIBP / cost-concentration concern **TRAINABILITY and GRADIENTS** — an axis distinct from *final-solution-quality rescue*. They make noise-assisted escape implausible but do **not mathematically preclude rare transient escapes at modest fixed depth**.
- Wang's p-sweep used n=5; Schumann's QAOA validation n=6 (weak noise); MDPI topped out at n=16. **All degradation evidence reaches exp55's point only by extrapolation.**

So: the asymptotic theory constrains but does not *settle* exp55. The empirical run is genuinely informative precisely in the gap the theory leaves open.

---

## Calibrated takeaways for exp55 forecasting

1. **Base rate for genuine noise-assisted rescue is LOW** but non-zero. Treat any raw ARM-1 escape as *probably variance* until it survives noiseless re-evaluation.
2. **H3 is the load-bearing test**, not H1. Winner's curse predicts H1's gross count is inflated; the real signal is the H3 survival fraction. A calibrated forecaster should expect **most escapes to NOT survive** noiseless re-eval.
3. **My existing preds were already directionally right** (pred_c3791_001: "partial regression, NOT full restoration"; pred_c3816_001: H1-PASS at |T|=1 is "single-seed degeneracy, NOT a population result"). The literature supplies the *why* (NIBP + winner's curse), upgrading those from instinct to grounded.
4. **NEW critical question this surfaces** (open in the literature, actionable for exp55): **Are the trapped seeds (47 at p=5, 51 at p=3) in true LOCAL MINIMA or in STRICT SADDLE POINTS?** If a meaningful fraction are saddles, the Liu et al. shot-noise mechanism *could* partially apply — but FakeMarrakesh's CPTP noise is still the wrong type to exploit it. This distinction determines whether *any* FOR-noise mechanism is even in play. Cheap to probe: examine the Hessian eigenvalue spectrum at the trapped optimum, or whether shot-noise-only (no device noise) perturbation escapes.

## Sources (all primary / peer-reviewed)

- Wang et al., Nat. Commun. 12:6961 (2021) — arXiv:2007.14384 — NIBP, cost concentration, p>2 degradation
- Schumann et al., Quantum Sci. Technol. 9:045019 (2024) — contractive-map NIBP generalization, QAOA-MaxCut
- Shaib et al., Quantum (2025) — unital noise always → NIBP
- Singkanipa & Lidar, Quantum (2025-01-30) — arXiv:2402.08721 — non-unital exception
- Liu, Wilde, Mele, Jin, Jiang, Eisert, Phys. Rev. A 111, 052441 (2025) — arXiv:2210.06723 — beneficial SHOT noise, saddle-only, CPTP detrimental
- "Reliable Optimization Under Noise in QVAs", arXiv:2511.08289 (2025) — winner's curse, noiseless-reeval discriminator
- MDPI Math. Comput. Appl. 31(3):78 (2026) — doi:10.3390/mca31030078 — 490-instance MaxCut-under-noise, collapse to 0.5 floor
