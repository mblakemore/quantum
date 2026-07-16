# Proposal — Bridge C: A Computational Advantage With an Executable Classical Counterpart (Quantum Learning / Sample Complexity)

**Author**: Whisper (DC15W), C4745 (2026-07-16) · **Substrate**: claude-fable-5
**Status**: PROPOSAL — no QPU spend yet; local feasibility sim run and passing (see §5).
**Directive**: Creator (2026-07-16) — *"review our quantum repo work and all experiment results… look for any creative ways to leverage what we have to achieve a computational quantum advantage over a measurable classical counterpart."*
**Sits alongside**: Bridge A (observable-estimation race; rescaled-residual test still the open item, Exp140 arc closed) · Bridge B (2D-HLF verifiable family; wrong-hardness-class for a cost race, `proposal-hlf-classically-verifiable-family-whisper-c4744.md`).

---

## 1. Why the computational scoreboard is still empty — and what would fill it

The campaign's own synthesis (`quantum-advantage-the-complete-answer-whisper-c4682.md`) leaves exactly one scoreboard without a live advantage:

- **F54 measured the wall**: Grover/QAE time-to-solution needs ~10⁴ two-qubit gates vs the ~10³ scrambling wall. No constant-factor stack closes it.
- **Bridge B (HLF, F113/F114)** is the right *shape* but the wrong *hardness class*: 2D-HLF ∈ P, so no n produces a cost race against a real classical computer. The separation it carries is depth-asymptotic, theorem-carried.
- **Bridge A** is a live estimator race but its decisive test (rescaled-residual) is deferred.

What would fill the scoreboard is a task where **(a)** the quantum resource wins by a margin that **grows with problem size**, **(b)** the classical counterpart is not a theorem abstraction but a strategy we can **execute and meter on the same chip, same window** (the F108 house standard), and **(c)** the classical floor is **unconditional** — no hardness conjecture (the Scoreboard-1 house standard).

There is a genre that satisfies all three, and this corpus has never touched it (recall + grep verified C4745): **quantum advantage in learning from experiments** — sample-complexity separations between learners with quantum memory (entangled two-copy measurements) and *any* conventional single-copy strategy. Chen–Cotler–Huang–Li (FOCS 2021) and Huang et al. (*Science* 376, 2022 — demonstrated on Sycamore up to 40 qubits) prove **exponential** separations via information-theoretic lower bounds that cover *adaptive* conventional strategies. No conjectures. ⚠️ House rule applies: the exact theorem statement and its conditions on our ensemble must be pulled from the papers and pinned in the pre-registration, **not** trusted from memory (this paragraph is the flag, not the citation).

**The honest name for the currency**: this is a *computational advantage in the number of experiments* (samples) required to accomplish a learning task — the standard resource in learning theory — not a laptop-runtime race. Both arms consume shots on the same QPU; the classical arm is "classical" in its *information architecture* (single-copy measurements + unlimited classical compute), not in its substrate. Stated up front, this fence is what makes the claim defensible.

## 2. The proposed task (Exp142): hidden-Pauli identification

**Instance.** A hidden full-weight product Pauli **P = ⊗ᵢ Pᵢ, Pᵢ ∈ {X,Y,Z}**, on n qubits. Nature's state is **ρ_P = (I + P)/2ⁿ**.

**Preparation costs zero two-qubit gates** (verified analytically, C4745): ρ_P is *exactly* the uniform mixture over product eigenstates ⊗ᵢ|Pᵢ, bᵢ⟩ with even-parity sign string b. Per shot: draw random even-parity b, apply depth-1 single-qubit gates. Every proper-subset marginal is maximally mixed — that is *why* single-copy learners are blind.

**Quantum arm** (2n qubits): prepare two independent copies, measure transversal Bell basis (n CX + n H + measure; depth ~3, ~n two-qubit gates — two orders of magnitude under the wall). Math (derived C4745): the outcome is a **uniformly random Pauli Q commuting with P** (anticommuting if P has odd Y-count; the decoder tests both hypotheses). Each shot is one F₂ symplectic linear constraint; **~2n+O(1) shots identify P exactly** by Gaussian elimination.

**Conventional arm** (n qubits, same chip, same window): the best-known single-copy strategy is full-basis parity elimination — measure all n qubits in candidate basis A; any mismatch position makes the parity uniform (odd parity eliminates A); the true basis shows even parity always. Expected cost **~3ⁿ shots** (with a confirmation threshold scaled as ~1.6n+7 to keep family-wise false-accept <1%; naive fixed thresholds collapse — caught in sim v1). The *theorem* floor (2^Ω(n), covering adaptive strategies) backs the executed baseline.

**Verification is free and blind-able**: another DC (Elder or Ember) draws P, commits a salted hash of it to the repo *before* the run; both learners submit their identified P; grading = hash comparison. Self-verifying, no classical simulation of anything.

## 3. Feasibility numbers (local sim, C4745 — `experiments/exp142_learning_advantage_sim.py`)

| n | Quantum shots (ideal / ×2.2 noise-inflated) | Conventional shots (measured in sim, acc 1.00) | Measured ratio |
|---|---|---|---|
| 4 | 8.7 / 19 | 93 | 5× |
| 6 | 12.6 / 28 | 733 | 26× |
| 8 | 16.5 / 36 | 6,782 | ~190× |
| 10 | 20.5 / 45 | 64,069 | ~1,400× |
| 12 | 24.6 / 54 | 531,441 (analytic) | ~10,000× |

- Through **n=10 both arms are fully executable** (64k shots is a routine budget — F108 used 196k). n=12 conventional (531k) is still executable if we want one deep rung; beyond that, the executed curve + theorem carry the extrapolation.
- The ×2.2 quantum inflation is a conservative placeholder (~10 CX @ 0.4% + 2n readout @ 1.5% → ~30% shot-corruption at n=10, robust-decoder overhead). The realistic decoder (constraint-consistency filtering / REM on the Bell readout) is pre-flight homework, sim-gated on FakeMarrakesh before any submission.
- Even if noise costs the quantum arm **10×** its ideal count, the n=10 ratio is still ~300× and grows 3× per qubit. The separation has enormous headroom against our known noise floor — this is the structural reason the genre fits NISQ.

## 4. Why this leverages what we already have

| Existing asset | Role in Exp142 |
|---|---|
| Bell/GHZ fidelity numbers (F01 CHSH 2.74; F108 V₃=0.96) | the transversal Bell measurement is the *entire* quantum circuit |
| Quiet-qubit picker + noise-dodge placement (F57/F58/F70) | pick the n best CX pairs on the chip |
| Calibration-window sentinel + co-batching (F77/F81, Bridge 2) | both arms in one job = same window by construction — the fairness guarantee |
| REM tooling + readout characterization | Bell-outcome error filtering |
| Executed-classical-reference discipline (F108) | the conventional arm is run, not assumed |
| Pre-registration + frozen-grader + blind-commitment culture | Elder/Ember seal P; grader frozen with prereg |
| Network structure (3 DCs) | natural nature/learner/verifier role separation |

## 5. The follow-on that makes it *useful* (rung C2): entangled noise spectroscopy of the chip itself

The same theorem family (Chen et al., process-learning) gives an exponential separation for **learning Pauli-channel eigenvalues with vs without entangled probes**. Applied to our own hardware: characterize a chip region's noise channel with entangled ancilla probes vs conventional probe-measure — potentially an exponential speedup in **device characterization**, which is this campaign's home turf (and feeds the QPU weather service). Proposed as the second rung after the clean Exp142 demonstration; needs its own theorem-conditions check.

## 6. Alternatives considered (ranked below Bridge C)

1. **Hidden Matching / QRAC-family communication race** — provable exponential one-way communication separation (Ω(√n) classical bits vs O(log n) qubits); F107 is the n=2 rung. Clean, shallow, but the currency (communication) extends Scoreboard 2 rather than filling the computational one. Good second target.
2. **Peaked-circuit verifiable sampling** (planted-peak RCS) — the only true *runtime* cost-race candidate on our hardware: ~60 qubits × depth ~10 sits under the wall, verification is free (the peak). But hardness is **conjectural** and peak-visibility at our fidelity (~e^(−0.005·500) ≈ 8%) is marginal. Moonshot rung; one sim-tier probe could price it.
3. **Bridge A rescaled-residual test** — unchanged standing open item; orthogonal to this proposal.
4. **What NOT to redo** (receipts): Grover/QAE at production depth (F54), mitigation stacks (F07), noise-as-resource (F55/F56), NISQ QEC (F06/F62), placement-as-lever (Exp140/140b: REM-controlled non-replication).

## 7. Pre-flight homework (all gated before any QPU submission)

1. **Pin the exact lower-bound theorem** (Chen–Cotler–Huang–Li FOCS 2021 / Huang et al. Science 2022) and verify our even-parity product ensemble meets its conditions — from the papers, not memory. If our exact ensemble isn't covered, either adapt the ensemble or derive the bound for it (the tree-representation technique) and have it checked by a second DC.
2. **Robust decoder** under realistic noise (FakeMarrakesh sim): constraint-consistency filtering, REM on Bell readout, measured (not assumed) inflation factor. Kill-gate: sim decoder identifies P with ≥99% success at ≤5× ideal shots under the FakeMarrakesh noise model, else redesign before flight.
3. **Blind-commitment protocol**: Elder/Ember draws P, commits salted hash to repo pre-run.
4. **Pre-registration** with frozen grader: primary metric = measured shot-ratio at n ∈ {4, 6, 8, 10} with CIs; secondary = quantum-arm absolute count vs theorem-scaling; win/loss/null criteria stated.

## 8. The claim this would support, stated exactly

*"On IBM Heron silicon, a learner using 2n qubits and entangled two-copy measurements identified a hidden n-qubit Pauli in ~O(n) experiments, while the best conventional single-copy strategy — executed head-to-head on the same chip, same calibration window — required ~3ⁿ, a measured ratio of ~10²–10³ at n=8–10 and growing exponentially; an information-theoretic theorem (no hardness conjecture) forbids ANY conventional strategy, adaptive included, from closing the gap."*

That is a computational quantum advantage over a measurable classical counterpart — measured, not extrapolated; unconditional, not conjectured; and it turns the corpus's two proudest disciplines (theorem ceilings + executed references) into a single experiment.
