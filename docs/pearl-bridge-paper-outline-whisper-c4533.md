# Paper Outline — "Causal Structure Beyond the Ladder: Hardware Experiments Where do-Calculus Has No Input"

**Author**: Whisper (DC15W), C4533 (2026-07-10) — roadmap T3.8, Creator-directed fold-in of the
quantum-causal-inference related-work comparison. Working outline for a paper aimed at the
**causal-inference community** (UAI / Journal of Causal Inference / perspective venue), NOT the
quantum-information community — that audience already knows the switch; the causal-inference
audience has never seen a hardware measurement that sits outside the SCM formalism.

## Thesis (one paragraph)

Pearl's ladder presupposes what it never states as an assumption: that there IS a definite causal
structure — every SCM fixes a definite order among its mechanisms before Rung 1 begins. We report
gate-model superconducting experiments in which the causal order of two (and three) operations is
placed in coherent superposition, and show — with pre-registered, frozen grading rules and
cross-device replication — that the resulting statistics exceed bounds obeyed by every process
representable in the SCM formalism: every fixed order, every classical mixture of orders (latent
order-selector), and every dynamical (outcome-dependent) order. The gap between the coherent-order
arm and its own decohered control, measured on one chip in one calibration window, is a physical
quantity that has no name inside do-calculus.

## The 2×2 that organizes the related work

|  | **Causal object classical** | **Causal object quantum** |
|---|---|---|
| **Substrate classical** | All of classical causal inference (Pearl) | — (not physically realizable) |
| **Substrate quantum** | Quantum-EXECUTED causal inference: Kang, arXiv:2509.00744 (do-calculus "circuit surgery" on IonQ Aria — SCM nodes as qubit registers, Simpson's-paradox resolution, 10-qubit healthcare SCM); Kawaguchi et al., arXiv:2110.04485 / PLOS One (qLiNGAM — quantum kernels inside DirectLiNGAM's independence measure on ibm_kawasaki); also arXiv:2501.05007 (quantum-enhanced discovery, small-N) | **THIS PAPER**: the causal skeleton itself carries amplitude (quantum switch); F73–F77 witness chain + Exp105/105b discrimination game + Exp106/107 capacity activation |

The bottom-left cell's success criterion is **agreement with the classical baseline** (hardware
faithfully executes Pearl); the bottom-right cell's success criterion is **provable disagreement**
(hardware exceeds what any Pearl-representable process permits). Complementary programs — the
same machines that can run do-calculus can also realize structure do-calculus cannot type.

## The experimental hinge (the paper's central figure)

The SCM-native way to model "uncertain order" is a latent selector: λ → order, with do(λ) and
mixtures over λ. **We ran that model, on the same chip, in the same calibration window, as the
coherent arm** — it is exactly our decohered-control / null arms:

| Arm | SCM description | Measured |
|---|---|---|
| Definite order (do(λ=AB)) | one fixed graph | game: 0.6146 = the class prior (0.6165); capacity: 0.00012 bits ≈ 0 |
| Classical mixture over λ | latent order-selector | F77 mixture arm: DISC +0.035 (inert) |
| **Coherent order** | **no SCM exists** | game: 0.977/0.974 (bound 0.8695, ≥200σ, two chips); capacity: 0.0436 bits (bound exactly 0, 55.6σ) |

Rhetorical core for the causal audience: the latent-selector model is not a straw man we argue
against — it is a control arm we EXECUTED, and it behaves exactly as Pearl predicts. The new
physics is the measured gap above it.

## Section plan

1. **For causal-inference readers: what a process matrix is** (2 pages, no prior QI assumed) —
   variables → labs; mechanisms → local operations; the process = everything between labs;
   causal ordering = comb structure. Definite order ≡ SCM-representable (with citation to the
   causal-separability literature); the cone W_sep and why "dynamical order" is still inside it.
2. **The witness chain** (F73→F75→F77→F76): sim → hardware → adversarial mixture control,
   same-device drift-free → cross-device cosine law. The continuous resource DISC(φ)=2cos(φ/2).
3. **From witness to game** (Exp105/105b): the Chiribella discrimination task; the
   measure-dependence lesson (Pauli-only bound = 1 — the identity pairs are load-bearing);
   re-solved SDP bound 0.869028 with recovered q*; frozen-rule WIN at 216.8σ / replication 201σ.
4. **Information through zero-capacity structure** (Exp106, +107 if graded WIN): capacity
   activation; the D=0 signature (each readout static, jointly informative); N=3 scaling.
5. **What this means for the ladder** (the F80 synthesis, expanded): do-calculus is not wrong —
   it is *typed*; its input is a definite (possibly latent-mixed, possibly dynamical) causal
   structure, and the switch is a physical object outside that type. Interventions ON the order
   variable (our null arms) are well-typed and behave classically; coherence of the order
   variable is the untyped remainder. Include the F80 retraction as a methods lesson (a proposed
   DAG-fit corroboration was withdrawn by its own author as circular before running).
6. **Methods as a contribution**: pre-registration, frozen grade rules, adversarial sibling
   review (4-catches pipeline), cross-device replication, sentinel/window gating — practices
   imported from empirical-forecasting discipline into hardware QI, likely novel to BOTH
   audiences.
7. **Honest scope**: device-characterized (not device-independent — cite the photonic DI line,
   Nature Comms 2023); coherence-of-order witnesses (each gate queried twice), not a black-box
   query-complexity separation; NISQ-generation hardware claims only.

## Data inventory (all with job IDs, pre-regs, and frozen rules in-repo)

F73–F77, F80 (witness chain + Pearl synthesis); Exp105 (marrakesh WIN 216.8σ), Exp105b (fez
201σ), Exp106 (capacity 55.6σ, MI 0.0436 bits), Exp107 (cyclic-3, N=3 scaling — pending drain,
either branch usable: WIN extends §4; NO-TEST-WINDOW feeds the methods section's window-harvest
narrative), plus the SDP solver + bounds (0.9288/0.8690 reproduced ±3e-5, q* recovered).

## Next actions

- After Exp107 grades: freeze the data inventory and draft §1+§5 first (the audience-defining
  sections); figures fig11/fig12 exist, need the game/capacity/hinge-table figures.
- Elder/Ember: finding numbers for 105/105b/106(/107) before citation freeze.
- Venue scouting + arXiv decision = Creator call.
