# Causal Structure Beyond the Ladder: Hardware Experiments Where do-Calculus Has No Input

**DRAFT v0.2 (Whisper C4546, 2026-07-10) — §1–§5 drafted in full; §6–§7 data-complete stubs;
figures fig15/fig16 rendered. Outline: `pearl-bridge-paper-outline-whisper-c4533.md`. Audience:
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

## §2. The witness chain — from simulation to a cross-device law

The apparatus is small enough to describe completely. A control qubit is prepared in an equal
superposition; conditioned on the control, a target qubit passes through the two local
operations in one order or the other; the control is then read out in the superposition basis.
If the two operations commute, an ideal switch leaves the control unchanged; if they
anticommute, it flips it. The witness observable DISC — the difference in the control's
expectation between a commuting and an anticommuting pair — reaches 2 for an ideal switch,
while any *causally separable* process (§1) is bounded far below.

The evidential chain was built in the order a skeptic would demand. In simulation, the witness
separates the switch from the strongest classical adversary — not merely a fixed order but a
50/50 *mixture* of the two orders, the physical realization of the latent selector λ — with the
mixture arm exactly inert (F73). On hardware, the witness fired at W = +1.781 against
pre-registered gates (F75). The decisive control came next: switch and mixture arms co-compiled
into a single job on one device in one calibration window, eliminating drift as an explanation —
DISC_switch = +1.900 versus DISC_mixture = +0.035, a separation of ≥72σ (F77). A second device
then reproduced not a number but a *law*: dialing the coherence of the order-control through
angle φ traces DISC(φ) = 2·cos(φ/2) with Pearson correlation 0.9992 (F76) — causal definiteness
behaves as a continuous resource, and its φ = π endpoint doubles as the classical mixture,
closing the loop between the two devices. One proposed corroboration — an "independent" fit of
the data to classical DAG families — was retracted by its own author before running, after
proving to be an exact rescaling of the witness itself (F80); we keep the retraction in the
record because a test that cannot fail proves nothing, and the discipline is part of the result.

For a causal-inference reader, the chain's shape matters more than its numbers: it is the same
escalation used in the best Bell experiments — beat the straw man, then beat the strongest
classical model (the λ-mixture), then close the loopholes your own apparatus could open (drift,
device-specificity) — but aimed at the *structure axis* rather than the locality axis.

## §3. From witness to game — a provable ceiling, beaten twice

A witness certifies; a *game* quantifies. Chiribella's discrimination task turns the same
apparatus into an operational question with a scoreboard: two operations are promised either to
commute ("partners") or anticommute ("rivals"), each may be used exactly once, and the player
must say which. The classical value of this game — the maximum average success of ANY causally
separable strategy, over all fixed orders, latent-selector mixtures, and dynamical orders — is
computable by semidefinite programming.

Three properties of that bound shaped the experiment, and each is a small lesson in its own
right. First, the bound is *measure-dependent*: on Pauli-only operation pairs it equals 1 —
there is no game at all, because a causally ordered circuit (apply both operations to half an
entangled pair, then measure in the Bell basis) decides those cases perfectly. Second, on the
standard finite set of ten operations with an optimized input distribution, the bound is
0.869028; we re-derived it from the primary source rather than citing it, reproducing both
published values to 3×10⁻⁵ and recovering the optimal input distribution the original paper
omitted — which turned out to carry design-critical structure (class-imbalanced priors; 75% of
the weight on non-Pauli operations). Third, the *identity* operands are load-bearing: delete
them to simplify the hardware and the bound silently returns to 1 — the game's hardness lives in
its most trivial-looking cases. Each of these facts was caught by re-solving the bound before
spending hardware time; the general rule — a classical optimum is a function of the input
distribution, not of the task's name — will be familiar to anyone who has quoted a benchmark
computed on someone else's population.

The hardware protocol was frozen before data: fifty-one game circuits sharing one identical
compiled skeleton (after a review catch in which the transpiler silently optimized away the
padding that guaranteed pair-independence), sentinel circuits at the start, middle, and end of
the batch, a definite-order null arm, and a grading rule fixed to the constant 0.8695. The
switch scored p̂ = 0.9769 ± 0.0005 — 216.8σ above the ceiling — while the null arm scored
0.6146, statistically indistinguishable from the game's class prior of 0.6165: on the same chip,
in the same window, a definite order buys exactly what Pearl says it buys, and nothing more.
The following day the identical frozen design ran on a second processor with no prior history of
switch circuits and returned p̂ = 0.9738 — a 0.3-percentage-point concordance across devices,
same verdict, 201σ. (Figure: fig15 — the per-pair measured successes sitting wholly inside the
forbidden zone above the ceiling, with the classical kits' averages below it.)

## §4. Information through causally-forbidden structure

The discrimination game bounds a *decision*; the capacity experiment bounds a *resource*. Take a
completely depolarizing channel — a mechanism that outputs uniform noise regardless of input.
One such channel transmits zero information. Two in sequence transmit zero in either order, in
any mixture of orders, under any adaptive scheme: the algebra is closed, the causal value is
exactly 0, and — unlike §3 — no optimization is needed to prove it. This is the cleanest
inequality in the paper: the entire causally separable set sits at a single point.

On hardware, the switch of two such channels transmitted 0.0436 ± 0.0005 bits per use — 55.6σ
from zero — with the definite-order null arm measuring 0.00012 bits (the theorem, on a chip).
The pre-registered signature is the part we most want causal-inference readers to see: the
*target alone* remains exactly depolarized even in the switch configuration (measured
D = +0.004). All of the transmitted information lives in the correlation between the message
and the order-control — each marginal is noise; jointly they carry the bit. A reader who has
taught graduate students that "marginal independence does not imply joint ignorance" will
recognize the shape; here the principle funds a communication channel through two perfect
erasers.

Scaling the switch to three channels in a superposition of the three cyclic orders tests
whether the resource grows. In theory it does: the ideal transmitted information rises from
0.0489 to 0.0833 bits. On hardware the experiment won again — 0.0260 bits, 61.7σ from the
causal zero — but *less* than the two-channel result: the deeper circuit (110 versus 4
entangling gates) costs more fidelity than the larger superposition gains. Theory scales;
practice inverts; both facts were measured under a single pre-registration, and the inversion
is the more useful number, because it locates the current hardware generation's frontier
(Figure: fig16 — the capacity ladder with the inversion annotated). The run also field-tested a
methodological answer developed earlier in the campaign: circuit quality at this depth is a
lottery that cannot be forecast from calibration metadata (a pre-registered null of its own,
F84), so the experiment carried a same-depth sentinel that measured its own window in-run —
detection replacing forecasting.

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
