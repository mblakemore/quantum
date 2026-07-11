# The Quantum Switch — Full Apparatus Specification

**Author**: Whisper (DC15W), C4559 (2026-07-11), Creator-directed ("write the spec doc").
**Purpose**: single-document engineering spec of the quantum switch *as we build, measure, and
grade it* — circuit family, exact theory statistics, measured-results ledger, reusable
methodology, pitfall registry, and honest scope. Consolidates what previously lived across six
preregistrations, the findings series (F73–F85), and the Pearl-bridge paper draft. The paper
(`pearl-bridge-paper-draft.md`) is the narrative for causal-inference readers; **this is the
spec for whoever builds experiment N+1.**

---

## 1. Definition

The quantum switch is a **higher-order operation** (a supermap): given two black-box channels
𝒜 = {Kᵢ}, ℬ = {Lⱼ} and a control qubit, it applies them in an order entangled with the control:

    W_ij = Kᵢ Lⱼ ⊗ |0⟩⟨0|_c  +  Lⱼ Kᵢ ⊗ |1⟩⟨1|_c        (control |+⟩, summed incoherently over i,j)

Three properties are load-bearing for everything below:

1. **Decomposition independence** — the switch is well-defined on *channels*: any Kraus
   decomposition gives the same output. This licenses the pooling estimators (§4).
2. **Linearity in each slot** — S(Σₖ pₖ𝒜ₖ, ℬ) = Σₖ pₖ S(𝒜ₖ, ℬ). This licenses classical
   mixing of circuit variants as an *exact* channel mixture (Exp106/107/108 estimator logic).
3. **The commute/anticommute readout** — for unitaries, measuring the control in |±⟩ computes
   the predicate COMMUTE(A,B) with one query of each: control unchanged if [A,B]=0, flipped if
   {A,B}=0. No fixed-order circuit computes this at that query count (Chiribella). This is the
   sense in which the switch **is a logic gate over operations rather than bits** (C4557).

**Scope statement (applies to every claim in this document)**: our implementations are
**device-characterized** — definite-order gate-model circuits that reproduce the switch's
statistics on characterized hardware. We do not claim indefinite spacetime order (the photonic
device-independent program is orthogonal, not competing). See §8.

## 2. The circuit family (five variants, all on IBM Heron-r2)

| Variant | Experiment | Qubits | 2q cost (routed) | Control readout | Target readout |
|---|---|---|---|---|---|
| V1 witness | Exp91 | 2 | ~4 CZ | X basis | — |
| V2 padded game | Exp105/105b | 2 | **uniform 4-CZ skeleton** | X basis | — |
| V3 channel-twirl 2-switch | Exp106 | 2 | uniform 4-CZ skeleton | X (clbit 0) | Z (clbit 1) |
| V4 cyclic-3 | Exp107 | 3 + 2q control | 92–110 CZ | inverse-prep basis | Z |
| V5 SWAP-dilation thermal | Exp108 | 4 (c,t,a1,a2) | uniform 22 CZ | X (clbit 0) | Z (clbit 1) |

**V1/V2 (unitary switch, control-only readout)**: control |+⟩; controlled-order application of
two single-qubit unitaries; H on control; measure. V2 adds the **skeleton-uniformity rule**
(C4525 sibling cross-check, adopted pre-freeze): every circuit in a job transpiles to the
*identical* 2q skeleton (controlled-𝟙 barrier-fenced CZ·CZ pads), so pairs differ only in local
gates — the graded contrast can then never be a depth artifact. Live audit aborts on histogram
drift (Exp106 froze `{4: 32}`).

**V3 (switch of channels via Pauli twirl)**: the completely depolarizing channel = uniform
Pauli mixture; by properties 1–2, running the 16 (Pauliᵢ, Pauliⱼ) switch circuits at equal
shots and POOLING is the exact switch-of-depolarizing-channels. Null arm: same pairs, definite
order, control spectator.

**V4 (cyclic-3)**: three channels in superposition of the 3 cyclic orders; 2-qubit
qutrit-encoded control, 9 CC-U via CCZ+natives (C4531 transpile audit: 92 CZ feasible; the full
6-order switch is 341 CZ / depth 1323+ — **not this hardware generation**).

**V5 (switch of non-unitary channels via SWAP dilation, C4558)**: a fully-thermalizing channel
is SWAP with a fresh ancilla in τ = diag(g, 1−g); τ is a classical mixture of basis states, so
the 8 basis-prep circuits pooled with weights w(t₀)w(a1₀)w(a2₀) are the exact channel+input
mixture. The two-order switch becomes a **controlled permutation** on (t, a1, a2):
c=0 → C₃ = SWAP(t,a1)·SWAP(t,a2); c=1 → C₃⁻¹ = C₃²; implemented as U = (𝟙⊗C₃)·CC₃ with
CC₃ = two Fredkins. At g = ½ this family degenerates to V3's channel (constant-to-𝟙/2 IS
depolarizing), which is the **fixed-point self-validation anchor** (§6.5).

## 3. Exact theory statistics (derived, not recalled — see §6.5)

**Witness (V1/V2)**: ideal DISC = ⟨X_c⟩_commute − ⟨X_c⟩_anticommute = **2**; any causally
separable process (fixed order, classical mixture, dynamical order) has DISC bounded far below;
the λ-mixture adversary is exactly inert (DISC = 0).

**Game (V2)**: Chiribella discrimination, Araújo/Branciard/Costa/Feix NJP 17 102001 finite
10-unitary variant, 𝒢 = {1, X, Y, Z, (X±Y)/√2, (X±Z)/√2, (Y±Z)/√2}. Causally-separable
ceilings (SDP, reproduced independently to 1e-3, `scripts/causal_game_sdp.py`, C4524 — which
also recovered the optimal pair distribution q\* the paper omitted):
**0.8690** (q\*-weighted, the graded bound) / 0.9039 (uniform pairs) / **0.9098** (uniform-prior
variant — the "91% ceiling" quoted in the public demos). Ideal switch wins with certainty.

**Capacity activation (V3, N=2)**: two completely depolarizing channels; every causal
composition transmits **exactly 0** (channel algebra — all orders of two depolarizing channels
are depolarizing; no SDP needed). Switch: P(c=+) = 5/8, target|+ = (ρ+2𝟙)/5,
target|− = (2𝟙−ρ)/3, symmetrized discriminator R̄ = 8/15 ≈ **0.5333**, MI = **0.0489 bits**.

**Capacity activation (V4, N=3 cyclic)**: causal value exactly 0; ideal R̄ = **0.6730**,
MI = **0.0833 bits** — activation *grows* with N in theory.

**Thermal splitting (V5, g = 0.75, input τ)**: every causal composition outputs exactly τ,
uncorrelated with control → Δ_causal = **0 exactly**. Switch: P(c=+) = 0.71875,
p₁|+ = **0.1848** (colder than τ's 0.25), p₁|− = **0.4167** (hotter),
Δ = p₁|− − p₁|+ = **0.2319**. Conditional states are **input-dependent** in general (a recalled
closed form was refuted by direct Kraus computation, C4558); input is pooled to τ, the
Felce-Vedral cycle-relevant state. Demon honesty: without feedback the branches cancel exactly
(0.719×0.0652 = 0.281×0.1667) — the switch yields a *conditional resource*, not free cooling.

## 4. Measured results ledger (hardware, all pre-registered, frozen rules)

| # | What | Device / job | Result | Finding |
|---|---|---|---|---|
| 1 | Witness fires | marrakesh `d939bmooamcc73dbv9b0` | ⟨X_c⟩: +0.865 commute / −0.905 anticommute; **W = +1.781** (ideal 2, noise-model 1.934), 3/3 gates | F75 |
| 2 | λ-mixture control, same window co-compiled | marrakesh | DISC_switch +1.900 vs DISC_mixture +0.035 — **≥72σ**, drift excluded | F77 |
| 3 | Cosine law, second device | kingston `d93khvl958jc73bt5c2g` | DISC(φ) = 2·cos(φ/2), **Pearson 0.9992** — order-coherence is a continuous resource; φ=π endpoint = the classical mixture | F76 |
| 4 | Game beats causal ceiling | marrakesh `d9826lkqp3as739sd2lg` | **p̂ = 0.9769 ± 0.0005 vs 0.8690** = **216.8σ**; all 51 pairs individually above the bound (worst 0.9650); null arm at/below ceiling on-chip | F82 |
| 5 | Game replication | fez `d982qssqp3as739sdmmg` | **0.9738 ± 0.0005 = 201.0σ**, frozen design verbatim, 0.3pp concordance | F82 |
| 6 | Capacity activation N=2 | marrakesh `d983ek52su3c739ip92g` | **R̄ = +0.5034 ± 0.0091 = 55.6σ** (causal: exactly 0); **0.0436 bits/use**; unconditioned target exactly depolarized (bit lives only in the correlation) | F83 |
| 7 | Capacity N=3 + scaling inversion | marrakesh `d9845dif47jc73a7ehe0` | **R̄ = +0.3817 ± 0.0062 = 61.7σ**; MI **0.0260 bits** — theory scales up (0.0489→0.0833), practice inverts (0.0436→0.0260): ~110 CZ depth-noise eats the gain. **N=2 is the practical optimum this generation** | F85 |
| 8 | Thermal splitting (ICO refrigeration resource) | marrakesh `d98vqfsqp3as739tfg0g` | **SUBMITTED C4558, queued** — grade per frozen rule (WIN floor Δ−5SE > 0.08 + cooling direction; FakeMarrakesh preview 0.2275 ± 0.0077) | Exp108 prereg |

Related null with the same discipline: **F84** (Elder design, Whisper mechanical grade) —
window *quality*, not calibration age, drives depth-class outcomes; graded NULL and published.

## 5. Provable bounds referenced by the family

- **Game ceiling**: SDP over causally-separable processes (fixed, mixed, AND dynamical
  outcome-dependent order) = 0.8690 under q\*; the bound binds every gadget/adaptive scheme
  under definite order — beating it is not "better strategy", it is a different model class.
- **Capacity**: causal value is **exactly zero by channel algebra** for V3/V4/V5 (the cleanest
  possible benchmark — a point, not an inequality; no measure-dependence).
- **Query separation**: COMMUTE(A,B) in one query of each (V1/V2 operationalize it). The
  N-switch Fourier-promise separation exists in theory (O(N) vs O(N²), later narrowed by
  Renner-Brukner PRResearch 3.043012) but is **out of reach this generation** (C4531: 341 CZ).

## 6. Reusable methodology (the part that transfers to experiment N+1)

1. **Pre-registration, frozen**: hypotheses + grade rule committed BEFORE submission; the rule
   cannot change after data. NO-TEST semantics: integrity gates (sentinel, null) failing ⇒ the
   run grades NO-TEST, not LOSS. Grader ≠ owner where the network allows; sibling cross-checks
   with receipts (C4525 changed Exp105 pre-freeze).
2. **Sentinels, two kinds** (Bridge-2 lesson, F85): *shallow apparatus* sentinels (F77
   commute/anticommute pair, DISC ≥ 1.60, START/MID/END) certify the apparatus; a **deep
   same-skeleton retention sentinel** meters the calibration window at payload depth — a 4-CZ
   sentinel cannot certify a 100-CZ window (F81 window lottery; FakeMarrakesh is optimistic
   specifically at depth: predicted 0.744/R̄≈0.518, hardware delivered 0.655/0.382).
3. **Pooling estimators**: mixed-unitary channels → equal-shot Pauli-label pooling (V3);
   classical-mixture states/inputs → weighted basis-prep pooling (V5). Exact by switch
   linearity, not approximations. Conditioning on pooled JOINT counts is valid because the
   joint is linear in the input.
4. **Null arms on-chip**: every claim ships with its own falsifier — definite-order arms must
   reproduce the causal value on the same chip in the same job (V3: unconditioned D ≈ 0;
   V5: p₁ = 1−g each order; game: null arm ≤ ceiling).
5. **Derive, don't recall + fixed-point self-validation** (C4558): theory targets are computed
   from first principles at prereg time, and the theory code must reproduce a
   *hardware-confirmed* fixed point of the family before it is trusted (V5's `exact_targets()`
   asserts the g=½ = Exp106 identity on every run). "New code agrees with new derivation" is
   circular; "new code agrees with measured numbers" is anchored.
6. **Submission hygiene**: calibration-gated qubit pick (min 2q-error + readout; `pick_pair` /
   `pick_chain4` with free 24-permutation layout scan), pre-registered shuffle seed, live
   transpile re-audit with a frozen 2q-class bound (abort on drift), ONE SamplerV2 job, never
   auto-resubmit, cost stated up front.
7. **Conditional observables starve on degenerate arms** (C4529, recurred + caught again
   C4558): a spectator control yields no minority-outcome samples — null gates must be
   UNCONDITIONED observables. This is now a design check, not a discovery.
8. **Retraction discipline**: F80 — a proposed corroboration was retracted by its own author
   pre-run after proving to be an exact rescaling of the witness (a test that cannot fail
   proves nothing). Kept in the record deliberately.

## 7. What the switch is good for (verified application map, C4557/C4527)

- **As a logic gate over bits: nothing.** On our hardware the switch is a definite-order
  circuit of native gates; any Boolean gate built from it is strictly costlier than the native
  gate. Its value is never as a gate primitive.
- **As a logic gate over operations: the COMMUTE oracle** — measured at 216.8σ/201.0σ (F82);
  nearest-term practical reading: unitary property testing / black-box device certification
  with fewer queries.
- **Communication**: capacity activation through dead channels — measured (F83/F85), N=2
  practical optimum; physics result, not an engineering comms claim (coherent-control critiques
  cap the interpretation).
- **Thermodynamics**: the Felce-Vedral conditional temperature splitting — Exp108 (pending).
- **Query-complexity scaling (Fourier promise)**: postponed — not this hardware generation.

## 8. Honest scope (what we do NOT claim)

Device-characterized throughout (§1). Not device-independent; not a spacetime claim; not Bell
(the swapped axis is causal definiteness, not locality — the model class is W_sep, not local
hidden variables); not Rung-3 counterfactual access (see paper §5: do-calculus is not wrong,
it is *typed* — the executed-control-arm hinge). Witness ≠ query separation (F80 retraction
neighborhood). Generation-bounded engineering claims are labeled as such (the N-inversion is
temporary; the theorems are not).

## 9. Public artifacts

- **Demo hub**: https://mblakemore.github.io/quantum/demo/ — switch page (drag order-coherence,
  F73–F77 data), **static duel** (capacity activation as a decoding race; LIVE mode consumes
  real marrakesh shots via bring-your-own-key `scripts/quantum_duel_server.py`), **Interrogation
  casebook** (the F82 game playable; kits Rookie 57.5% / Casefile 75% / Switch = measured 97.8%
  column vs the 91% uniform-prior ceiling; Switch Badge named for this apparatus).
- **Print-and-play**: Casebook of Detective Whisper (C4541), d100 thresholds from measured data.
- **Paper**: `docs/pearl-bridge-paper-draft.md` (v0.3 complete draft, sibling review pending).

## 10. File index

| What | Where |
|---|---|
| Preregistrations (frozen) | `experiments/exp91-*.md`, `exp105-*.md`, `exp105b-*.md`, `exp106-*.md`, `exp107-*.md`, `exp108-*.md` |
| Circuit + feasibility code | `experiments/exp105_causal_game_feasibility.py`, `exp106_capacity_activation.py`, `exp108_ico_refrigeration.py` |
| Submit / grade scripts | `scripts/run_exp*_submit.py`, `scripts/grade_exp*.py`, `scripts/causal_game_sdp.py` |
| Findings | `findings/F75,F76*,F77*,F82,F83,F85-*.md`, `findings/pearl-structure-of-the-quantum-switch-witness-whisper-c4487.md` |
| Applications | `docs/bridges-to-compute-advantage-whisper-c4522.md`, `docs/ico-applications-roadmap-whisper-c4527.md` |
| 6-order feasibility audit | C4531 (quantum repo commit trail; summary in `exp107` prereg lineage) |
| Job manifests / results | `results/exp*_jobids.json`, `results/exp108_feasibility.json` |

---

*Maintenance rule: when an experiment in this family is graded, update the §4 ledger row in the
same cycle as the grade commit. This document is spec, not narrative — numbers here must match
the findings files exactly; on conflict, the finding is ground truth and this doc gets fixed.*
