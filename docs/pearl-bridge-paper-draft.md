# Causal Structure Beyond the Ladder: Hardware Experiments Where do-Calculus Has No Input

**DRAFT v0.1 (Whisper C4545, 2026-07-10) — §1 and §5 drafted in full; §2–§4, §6–§7 are
data-complete stubs. Outline: `pearl-bridge-paper-outline-whisper-c4533.md`. Audience:
causal-inference (UAI / Journal of Causal Inference / perspective venue).**

> **Abstract (working).** Pearl's ladder of causation rests on an assumption it never needs to
> state: that there *is* a definite causal structure — every structural causal model fixes an
> order among its mechanisms before Rung 1 begins. We report superconducting-hardware
> experiments in which the causal order of two (and three) operations is placed in coherent
> quantum superposition, and show — under pre-registered, frozen grading rules, with
> cross-device replication — that the resulting statistics exceed bounds obeyed by every process
> the SCM formalism can represent: every fixed order, every classical mixture of orders, and
> every dynamical (outcome-dependent) order. Crucially, the SCM-native model of "uncertain
> order" — a latent order-selector λ — is not a straw man we argue against, but a control arm we
> physically executed on the same chip in the same calibration window: it behaves exactly as
> Pearl's framework predicts, and the measured gap above it (a discrimination game won at
> 0.977 against a 0.8695 ceiling; 0.0436 bits transmitted through a configuration whose every
> causal composition has exactly zero capacity) is a physical quantity with no name inside
> do-calculus. We argue this is not a defect of the calculus but a boundary of its type system —
> and that the boundary is now an experimental object.

---

## §1. Process matrices for causal-inference readers

*(This section assumes fluency with SCMs and no quantum mechanics beyond "measurement outcomes
are probabilistic.")*

Start with what a structural causal model takes as given. An SCM over variables
V = {V₁,…,Vₙ} supplies (i) a set of **mechanisms** fᵢ, (ii) a wiring diagram — the DAG — saying
which variables feed which mechanisms, and (iii) exogenous noise. Everything the ladder does —
conditioning at Rung 1, graph surgery at Rung 2, abduction-action-prediction at Rung 3 —
operates *within* a fixed wiring diagram, or a known family of them. When we are uncertain about
the wiring, the standard move is to add a latent selector: a variable λ whose value chooses the
diagram, so that uncertainty about structure becomes ordinary uncertainty about a variable. This
move feels innocent, and for every system causal inference has ever been applied to, it is.

The process-matrix framework (Oreshkov, Costa &amp; Brukner 2012) asks the question the SCM
never asks: what is the *most general* way that fixed local mechanisms can be wired together,
consistent with quantum theory holding locally? Translate the vocabulary as follows:

| Causal-inference object | Process-matrix object |
|---|---|
| a mechanism fᵢ with its local noise | a **local operation** in a closed lab (input system in, output system out) |
| the DAG / wiring between mechanisms | the **process** W — everything outside the labs |
| "A precedes B" | W routes A's output (possibly transformed) into B's input, never the reverse |
| a definite DAG | a **causally ordered** process (mathematically: a quantum *comb*) |
| a latent structure-selector λ, with any prior | a **classical mixture** of ordered processes |
| λ *influenced by earlier outcomes* (structure that unfolds) | a **dynamical-order** process |
| **the union of all of the above** | the **causally separable** set, W_sep |

Two points matter for what follows. First, the causally separable set is *exactly* the image of
Pearl's world in this formalism: anything representable as "there is a definite order in each
run, possibly random, possibly unfolding as outcomes arrive" lives in W_sep. If a system's
statistics can be captured by any SCM with any latent selector, its process is causally
separable. Second — and this is the framework's reason to exist — quantum theory admits *valid
processes outside W_sep*. The canonical example is the **quantum switch**: a process in which a
control quantum system determines the order in which two labs act on a target system, and the
control is placed in superposition. Not "order unknown": order *in superposition*, in the same
sense a qubit can be in superposition of 0 and 1 — with the same operationally testable
consequences (interference), and the same impossibility of a hidden-value account.

The claims in this paper are inequalities on W_sep, measured on hardware. They have the same
logical shape as Bell-inequality experiments — a bound obeyed by an entire classical model
class, violated by a quantum system — but the model class is different: Bell experiments bound
*locality*; these experiments bound *causal definiteness*. For a causal-inference reader the
important sentence is this one: **W_sep is closed under everything you know how to write down.**
Mixtures, hierarchical priors over DAGs, structure learned online, adversarially chosen orders —
all of it is inside the bound. What is outside is not a cleverer prior over structures; it is
the absence of a fact-of-the-matter about structure.

*(§1 continues with the one-paragraph description of the switch circuit and the two measured
observables — the discrimination game and capacity activation — deferring apparatus detail to
§2–§4.)*

## §2. The witness chain — sim → hardware → adversarial controls → cross-device law [STUB]

Data inventory: F73 (mixture-adversary witness, sim, W₂=+2.00/+1.93); F75 (hardware witness
fires, W=+1.781, all pre-reg gates); F77 (same-device drift-free switch-vs-mixture, one
calibration window, DISC_switch=+1.900 vs mixture +0.035, W₂=+1.865, ≥72σ); F76 (continuous
cosine law DISC(φ)=2cos(φ/2) on a second device, Pearson 0.9992); F80 (a proposed corroboration
retracted by its own author as circular — kept as a methods exhibit).

## §3. From witness to game — a provable ceiling, beaten [STUB]

Data inventory: the Araújo et al. (2015) bound family (Pauli-only pairs: ceiling 1 — no game;
Haar: 0.9288; the finite 10-unitary game with optimal input distribution: 0.869028, re-derived
from scratch, validated primal=dual to 2×10⁻⁸, optimal q\* recovered — class-imbalanced 0.6165,
75% of weight on non-Pauli reflections); the identity operands proven load-bearing (drop them
and the ceiling returns to 1); frozen pre-registration with skeleton padding after the
transpiler silently cancelled null CZ·CZ blocks; Exp105 WIN p̂=0.976931±0.000495 (216.8σ over
the bound) on `ibm_marrakesh`; Exp105b replication on `ibm_fez`, a device with no prior switch
history, p̂=0.9738 — 0.3pp concordance, same frozen design, next day.

## §4. Information through causally-forbidden structure [STUB]

Data inventory: Exp106 capacity activation — two completely depolarizing channels (every causal
composition exactly zero-capacity by channel algebra, distribution-free) transmit 0.0436
bits/use in the switch (55.6σ); the pre-registered signature confirmed: the target *alone* is
exactly depolarized even in the switch arm (D=+0.004) — the bit lives only in the control–target
correlation; the null arm measured 0.00012 bits. Exp107, N=3 cyclic orders: WIN at 61.7σ
(0.0260 bits through *three* total censors) **and** the honest scaling twist: ideal capacity
grows with N (0.0489→0.0833) while measured capacity falls (0.0436→0.0260) — the depth cost of
the larger switch exceeds the scaling gain on this hardware generation. Theory scales; practice
inverts; both measured under one pre-registration.

## §5. What this means for the ladder

The temptation is to read these results as "quantum mechanics breaks causal inference." That
reading is wrong in both directions, and the point of this section is to replace it with a
sharper one: **do-calculus is not wrong; it is typed.** Its input type is a causal structure —
definite, or mixed by a latent selector, or unfolding dynamically. Every rung presupposes a
value of that type. The quantum switch is a physical object that does not inhabit the type, and
so the calculus does not produce wrong answers about it; it produces *no* answers, the way a
function produces nothing when handed an argument outside its domain.

The strongest evidence we can offer for this reading is that we did not merely argue it — we
*executed the typed part*. The SCM-native model of our apparatus is: λ → order, do(λ = AB), or
a mixture over λ. That model is not hypothetical. It is three physical control arms, run on the
same chip as the coherent arm, in the same calibration window, under the same frozen analysis:

| Arm (SCM description) | Pearl's prediction | Measured |
|---|---|---|
| do(λ): definite order, control decohered | game success = the class prior; channel capacity = 0 | game null: 0.6146 (prior: 0.6165); capacity null: 0.00012 bits |
| mixture over λ | witness inert | DISC = +0.035 (inert) |
| *(coherent λ — no SCM exists)* | — | game: 0.977 / 0.974 on two chips (ceiling 0.8695); capacity: 0.0436 bits (ceiling: exactly 0) |

The first two rows are a success story *for* the ladder: where the causal skeleton is definite
or classically mixed, Pearl's predictions were quantitatively correct on quantum hardware, to
within a fraction of a percentage point. The framework does exactly what it claims on every
input in its domain. The third row is the boundary made visible: a measured gap standing above
everything the type can express, at a statistical distance (55σ–217σ) that forecloses the
possibility that some unmodeled selector is hiding in the noise.

Three clarifications guard the claim's edges. *First*, this is not Rung 3. Counterfactuals
stress the ladder's top; the switch undercuts its floor. A counterfactual asks "what would Y
have been had X been different, in this structure?" — it still quantifies over a definite
structure. Our object has amplitude over structures, which is not a rung above but a step off.
*Second*, this is not the old observation that quantum mechanics has non-classical
*correlations*. Bell experiments live comfortably inside definite causal structure (a common
cause in the past light cone; the DAG is fixed). What is in superposition here is the DAG
itself. *Third*, our claims are device-characterized, not device-independent: we trust the
compilation of the local operations, in the same way (and to the same degree) that the
quantum-executed do-calculus literature trusts its circuit encodings. A photonic
device-independent certification of causal nonseparability exists; our contribution is the
game-form, provable-ceiling, pre-registered version on gate-model hardware, with the executed
classical controls that make the comparison to SCM predictions quantitative rather than
rhetorical.

What should a causal-inference researcher *do* with this? Three things, in ascending ambition.
(1) **Vocabulary**: "causally separable" is a precise, theorem-bearing name for the closure of
the SCM world under latent and dynamical structure selection — a useful concept even for
readers who never touch a qubit, because it marks what latent-selector tricks can and cannot
buy. (2) **A calibration point**: the quantum-executed causal inference programme (do-calculus
circuit surgery on trapped ions; quantum-kernel structure learning on superconducting chips —
see §6/related work) shows quantum *hardware* faithfully running classical causal *semantics*;
our results show the same hardware natively realizing structure outside those semantics. Both
are true; the pair defines where the semantics end. (3) **An open problem**: is there a
conservative extension of the do-calculus typed over *superpositions* of structures — a
calculus whose restriction to W_sep is Pearl's, and whose new sentences (e.g., the value of our
game, the capacity of our channel pair) become derivable rather than merely measurable? The
process-matrix community has the objects; the causal-inference community has the calculus
discipline. The gap between them is now an experimental quantity with error bars, which in our
experience is the kind of gap that gets closed.

## §6. Methods as a contribution [STUB]

Pre-registration with frozen grade rules (all six hardware experiments); adversarial sibling
review (five consecutive experiments where review caught a real defect pre-spend: measure-
dependent bound / class-imbalanced q\* / skeleton non-uniformity + the vacuous no-identity game /
transpiler pad-cancellation / null-observable starvation); cross-device replication as standard;
sentinel-gated calibration windows (the lottery is detectable, not forecastable: F81, F84,
Exp107's load-bearing deep sentinel); ~3.5 QPU-minutes total for the results in §3–§4.

## §7. Honest scope [STUB]

Device-characterized (not DI; cite photonic DI line). Coherence-of-order witnesses query each
operation twice — not a black-box query-complexity separation. NISQ-generation claims only;
the N-scaling inversion (§4) is itself evidence of the generation boundary. All job IDs,
pre-registrations, code, and raw results are public in the repository.

---

*Figures planned: (i) the hinge table above as the central figure; (ii) the ceiling plot —
classical kits converging under 0.9098, switch column above it, per-case measured points;
(iii) DISC(φ)=2cos(φ/2) (exists, fig12); (iv) capacity ladder N=1(=0)/N=2/N=3 ideal-vs-measured
showing the inversion.*
