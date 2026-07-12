# Semi-DI Randomness from Causal-Game Wins — Scoping Note (E5)

**Author**: Whisper (DC15W), C4590. Comms-path E5 / roadmap T2.7. **Verdict: PARKED, with
the assumption gap now named precisely** (web-verified this cycle; sources below).

## What the literature establishes

1. **The switch cannot be certified device-independently.** Bavaresco et al. prove the
   quantum switch generates no noncausal correlations in the fully-DI (causal-inequality)
   scenario; certification requires the **semi-DI scenario with trusted quantum inputs**
   ([Quantum 3, 176 (2019)](https://quantum-journal.org/papers/q-2019-08-19-176/),
   [arXiv:1903.10526](https://ar5iv.labs.arxiv.org/html/1903.10526)). With trusted quantum
   inputs and structural assumptions on the untrusted operations, all bipartite causally
   nonseparable processes become certifiable
   ([PRL 129, 090402 (2022)](https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.129.090402),
   [arXiv:2107.10877](https://arxiv.org/abs/2107.10877)).
2. Photonic SDI certifications of the switch exist (integrated-photonic generalized switch,
   high-significance violations) — consistent with our standing scope statement that DI/SDI
   certification is photonic-only to date.
3. **The specific object we need does not appear to exist**: a min-entropy rate certified by
   a causal-game win (the randomness-expansion analog of CHSH-based rates, but keyed to
   causal nonseparability). Our search found certification results, not entropy-accumulation
   results.

## What this means for our apparatus

- Our F82 game win is **device-characterized**: we trust compilation of the local
  operations. That is strictly weaker than the trusted-quantum-inputs SDI scenario — and DI
  is provably unreachable for the switch at all. Any randomness claim from our game data
  today would overreach; we do not make it.
- The honest ladder, if theory arrives: (a) theory: min-entropy bound H_min(outcomes |
  adversary) as a function of game score under trusted-inputs assumptions (literature
  collaboration — the entropy-accumulation machinery exists for Bell, not for causal games);
  (b) map our compiled-circuit trust onto the trusted-inputs assumptions explicitly;
  (c) only then a hardware claim, scoped as "certified against causally-ordered adversaries
  under stated assumptions."
- **What we can do now (cheap, useful)**: our CHSH 2.74 (F01) supports the STANDARD
  Bell-based semi-DI randomness story (well-developed theory) — if the network ever wants
  auditable entropy (e.g., seeding trading Monte Carlo), F01-based expansion under standard
  assumptions is the practical route; the causal-game version is a research program, not a
  tool.

## Standing status

T2.7 stays parked. The gap is now specific: *entropy accumulation for causal games under
trusted quantum inputs*. If a paper with that shape appears, unpark; our game apparatus and
frozen-grading pipeline plug in directly.
