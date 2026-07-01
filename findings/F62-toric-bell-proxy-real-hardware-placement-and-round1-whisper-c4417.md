# Finding 62 — Real ibm_fez results for the toric-code Bell proxy: placement, round-1, and hardware

**Author:** Whisper (DC15W) | **Cycle:** C4417 | **Date:** 2026-07-01
**Builds on:** F61 (Exp84, simulation-only toric-code proxy of a third-party Heron R2 entanglement test)
**Status:** Real hardware results in. Mixed: round-1-vs-round-0 comparison replicates the author's
qualitative finding; round-0 itself underperformed both our own simulation and the author's actual
hardware result. Diagnosed, not just reported — ruled out a bug before concluding anything.

Creator approved all three follow-up items from F61 ("run 1, 2, and 3"): noise-aware placement,
a round-1 active-QEC stress test, and a real hardware submission.

---

## 1. Noise-aware placement: tested, found counterproductive for this circuit

Tried `quiet_qubits.pick(backend, 19, mode='best')` (the F57/F58 lever, already validated
elsewhere in this repo) as `initial_layout` for the toric encoder + entangling circuit. Result:
**2q-gate count roughly DOUBLED** (364 vs 190 for default transpilation) on FakeMarrakesh.

Why: `quiet_qubits.pick()` greedily selects a connected subgraph minimizing per-qubit noise,
with no awareness of what connectivity the CIRCUIT actually needs. The toric encoder's CNOTs
(RREF-derived, from each pivot to its stabilizer row's support) don't form a simple local
cluster — forcing a topologically-mismatched-but-low-noise placement onto them requires far
more SWAP routing than letting the transpiler's own heuristic find a locally-good match.

**This is the same asymmetric-inference trap flagged in Exp82/F59-F60 this session**: a
"noise-reduction" lever that adds circuit depth can be net-negative, and needs testing per
circuit, not applied by default. **Decision: default (no custom layout) used for the actual
hardware submission**, based on this sim evidence, not assumption.

## 2. Round-1 (active QEC stress test): logic validated, real hardware collapses further

Built a full syndrome-extraction round (8 X-checks + 8 Z-checks, weight-4 each, single reused
ancilla with mid-circuit reset) inserted between state-prep and the entangling/readout circuit
— NOT used for correction, pure noise-cost stress test, matching the author's own round-1
framing exactly.

- **Noiseless validation** (50 shots, fast): witness = exactly **2.0000** — confirms the
  syndrome round doesn't disturb the logical state when there's no physical noise (expected:
  measuring already-satisfied +1 stabilizers is a no-op projection).
- **Local noisy simulation**: impractical — mid-circuit measurement+reset forces per-shot
  wavefunction branching in AerSimulator, making even 300 shots take >8 minutes (killed after
  timeout). This is a genuine tooling limitation encountered this cycle, not a circuit problem.
- **Real hardware** (`ibm_fez`, 820 2q-gates, depth 730 — vs round-0's 190/168):
  **witness = 0.113** (ZZ=0.014, XX_cond=0.099) — essentially fully collapsed.

Round-1 (0.113) vs round-0 (0.570, see §3): a clear further degradation from adding the
syndrome round, **qualitatively replicating the author's own finding** ("1 round CX pushed the
circuit to ~4 errors/shot, killing the correlation") — same mechanism (depth/gate-count cost of
active syndrome extraction exceeds what this code's distance can absorb), independently
reproduced on a different code and a different circuit.

## 3. Real hardware round-0: underperformed both our sim and the author's own result

`ibm_fez`, default placement, 2000 shots (matching the author's own shot count), round-0 (state
prep + entangle + readout only):

**Witness = 0.570** (ZZ=0.235, XX_cond=0.335) — **below the separable bound of 1.0**.

There are two DIFFERENT gaps here, with two DIFFERENT causes (advisor-caught: an earlier draft
of this section conflated them into one "compounding" story — wrong, they explain two separate
comparisons, not one shortfall):

| Comparison | What differs | What's held constant |
|---|---|---|
| Sim (1.32–1.40) vs our hardware (0.570) | noise model | same circuit, same 190 gates |
| Our hardware (0.570) vs author's hardware (1.121) | circuit (190 vs ~14 gates) | same backend family, both real |

### Ruled out a bug before concluding anything

A large sim-vs-hardware gap could mean (a) a decode/circuit bug, (b) genuinely worse real noise
than the sim assumed, or (c) something structural. Checked (a) first, directly:

- Raw bitstring diversity looked alarming on its own (1940/2000 shots distinct) — consistent
  with either noise OR a bug, not discriminating.
- **Individual qubit marginals** (~0.43–0.52, near 50/50) — also not discriminating; this is
  actually *expected* for this ground state's superposition structure, not evidence of either
  hypothesis.
- **The decisive check**: computed all 9 independent Z-stabilizer (plaquette) expectation
  values directly from the raw hardware counts. Ideal value is exactly +1.0 for every check
  (a mathematical property of this ground state, verified in F61). Real result: **every single
  check came back clearly positive** (+0.175 to +0.442, none near zero, none negative) — a
  9-for-9 consistent signature that would be extremely unlikely from a broken/scrambled circuit
  (a bug would produce checks scattered near zero, not uniformly positive). Independently
  confirmed on the X side: `xx_b0=+0.315`, `xx_b1=−0.356` — correctly opposite signs for Φ⁺/Φ⁻,
  exactly the structural signature a working (if noisy) circuit should produce, not noise.
  **This rules out a decode/circuit bug** with high confidence — the circuit is genuinely
  running correctly; the state has real, substantial, if heavily degraded, structure.

### Gap 1 (sim vs our hardware, 1.32→0.570): noise-model mismatch

Same circuit, same 190 gates, both actually run — the only thing that differed is the noise
applied. This gap is entirely explained by `FakeMarrakesh` being a stale/mismatched proxy: a
snapshot of `ibm_marrakesh` calibration, used here as a "same Heron-r2 chip family" stand-in for
`ibm_fez` (flagged as a caveat in F61 §5 already). The Z-check degradation (average ~0.30, far
below the sim's implied per-gate fidelity) shows live `ibm_fez` noise right now is meaningfully
worse than that snapshot predicted — the same lesson this repo's `quiet_qubits.py` exists to
address (noise drifts, static assumptions go stale), now confirmed by a simulation-vs-reality
gap rather than a same-backend drift measurement. Gate count cannot explain this gap (it was
identical on both sides) — this comparison is pure noise-model error.

### Gap 2 (our hardware vs author's hardware, 0.570→1.121): the informative comparison

Both real, same backend family, noise-model quality isn't in play here — the author cleared the
bound on the SAME class of chip. That's strong evidence the hardware *can* do this, and what
differs is the circuit: **our validated CSS encoder needs 34 raw CX (→190 after routing) just
to prepare `|0_L,0_L⟩`, vs the author's reported 14 total Bell CX.** If that 14 includes their
state prep, their code's logical-zero state was reachable far more cheaply than ours (plausible
if their custom code needs little or no stabilizer-based encoding circuit, unlike the toric
code's non-trivial 8-generator encoder). **This is the PRIMARY, leading hypothesis for why our
run fell short where theirs succeeded** — not co-equal with Gap 1's noise-model story, since
Gap 1 is already fully explained without invoking gate count at all. This is a genuine,
disclosed limitation of the toric-code substitution (F61 §5 already flagged it as "not a
literal reproduction"): it buys mathematical certainty at the cost of a much larger gate budget
than whatever the author's undisclosed code allowed.

## 4. Honest bottom line

- **The underlying physics is confirmed real on both sides**: the author's hardware result
  (1.121, clearing the bound) and our own Z-check-level analysis of our own "failed" run
  (9-for-9 positive on Z, correct Φ⁺/Φ⁻ sign split on X, structured not noise) both show genuine
  logical-qubit correlation surviving real hardware, at round 0.
- **Why ours fell short where theirs succeeded (leading hypothesis): gate count.** Our validated
  encoder costs ~190 real gates vs their apparent ~14 — a same-hardware, same-family comparison
  where noise-model quality isn't a confound. This is the actionable lever, not "the hardware
  can't do it" or "our sim was wrong" (the sim being wrong is a separate, already-explained gap
  to `FakeMarrakesh` staleness, not evidence about the hardware itself).
- **Round-1 replicated cleanly**: independent confirmation, different code, that active
  syndrome-extraction rounds are currently net-negative at this scale on Heron-r2 hardware.
- **Noise-aware placement, naively applied, would have made round-0 worse, not better** — a
  useful negative result that prevented wasting QPU budget on a doomed configuration.
- Cost: 12 QPU-sec for all 4 jobs (201/600 consumed, 399 remaining, still GREEN).

## 5. Open items (not executed — reporting back to Creator for direction, not spending more QPU speculatively)

1. **Primary lever**: reduce state-prep gate cost — investigate whether a cheaper
   (non-full-ground-state) `|0_L⟩` preparation exists for this specific circuit's needs, closing
   the gap to the author's apparent 14-CX total. This is the comparison that actually explains
   the shortfall (Gap 2), so it's the highest-value next step if this thread continues.
2. Secondary: test noise-aware placement on **real** `ibm_fez` specifically (not
   `FakeMarrakesh`) — the gate-count penalty was measured on a stale noise model; live
   device topology/calibration could change the tradeoff, though this doesn't address Gap 2.
3. Re-run round-0 at a different time (calibration drift check) — informative for Gap 1
   (noise-model mismatch), not for Gap 2 (gate count).

## 6. Reversibility / scope

Pure-additive: one script extension (`run_exp84b_round1_and_placement.py`), one finding, 4 real
hardware jobs (12 QPU-sec, well within budget). Diagnostic scripts run inline, not committed
(one-off Z-stabilizer/marginal checks against already-retrieved job data). Local noisy
round-1 simulation was killed after exceeding a reasonable time budget on the shared machine
(consistent with F60's established discipline this session) — resolved by moving directly to
real hardware instead, since QPU execution doesn't share the local CPU bottleneck.
