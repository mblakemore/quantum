# Finding — Exp191: THE SHIELDED HANDSHAKE — logical qubits entangled at 57σ, and the shielded pair beat the bare one

**Cycle**: C4883 · **Date**: 2026-07-19 · **Backend**: ibm_fez · **Job**: `d9e64rsjeosc73fid0gg`
(8 circuits, 8000 shots; two [[4,2,2]] blocks, 8 qubits, transversal CNOT). **Shields arc
stage (iii): all four pre-registered criteria HELD.** Creator go: general#137.

## Result

| arm | ZZ_L1 / XX_L1 | S_L1 (bound 1) | S_L2 (control) | acceptance Z/X |
|-----|---------------|-----------------|----------------|----------------|
| **logical** | +0.975 / +0.995 | **1.970 — 57σ** | **0.998** | 0.871 / 0.845 |
| logical_idle (0.5 μs echoed) | +0.945 / +0.956 | **1.902 — 46σ** | 0.953 | 0.659 / 0.670 |
| nocx (falsifier) | −0.017 / +0.006 | −0.011 | 1.012 | 0.924 / 0.928 |
| bare physical Bell | +0.939 / +0.964 | 1.902 | — | 1.0 |

1. **Two logical qubits, each inside its own [[4,2,2]] shield, entangled across blocks by the
   transversal CNOT and certified at S = 1.970 — 57σ past the separable bound.** Both logical
   correlators individually ≥ 0.975.
2. **The in-shot internal control performed exactly as the theorem demands**: the second
   logical pair — riding the *same shots* through the *same transversal gate* in a product
   state — landed at S_L2 = **0.998**, dead-center on the separable bound of 1 (and 1.012 in
   the falsifier arm). The witness calibrated itself inside the dataset.
3. **The buried headline: the shielded pair BEAT the bare physical pair** — 1.970 vs 1.902
   (Δ ≈ 0.068, ~3.4σ). The code's postselection (14% of shots paid) scrubs the accepted
   ensemble cleaner than raw physical qubits manage at all. Stage (ii) showed the shield pays
   on stored *states*; stage (iii) shows it pays on *entanglement* — post-hoc observation,
   labeled as such (not pre-registered; the registered reference claim was only S_bare band).
4. **Operating point validated**: with 0.5 μs of quarter-echoed idle (stage (ii)'s mapped
   regime), the logical pair still certifies at 46σ — the resource survives long enough to use.
5. Falsifier exact: no transversal CX → L1 stone dead (−0.011) while L2 stays at the bound.

## Ledger

All four registered criteria held. Two band-misses HIGH (S_L1 1.970 vs 1.55–1.85; idle 1.902
vs 1.35–1.75): bands were priced per item 10 from the recent condition window — which was the
anomalous-dephasing day; today recovered. Miss direction benign, criteria unaffected; the
condition-pricing rule stands (price from same-day when available — these circuits had no
same-day precursor).

## Fence

Distance-2 detection + postselection; one syndrome-equivalent check per basis (terminal
stabilizer parity); transversal CX is FT-native but no repeated-round fault tolerance is
claimed; ⟨ȲȲ⟩ unmeasured (two-setting witness suffices, bound is a theorem); logical-beats-bare
is a postselected comparison — the 14% acceptance cost is the price of the cleaner ensemble.

## The arc

(i) shields up ✓ → (ii) pays-map + coverage ✓ → **(iii) shielded entanglement ✓ at 57σ** →
(iv) THE SHIELDED TRANSPORTER: teleport a logical qubit using this pair, the frame machinery
(Exp177), and the mapped operating point. All resources now certified.
