# Quantum Communication — What We Already Hold, and the Discovery Paths

**Author**: Whisper (DC15W), C4588 (2026-07-12), Creator-directed ("look over everything we've
done — explore quantum communication research and discovery paths").
**Method**: full-repo review through a communication lens + literature verification by web
search this cycle (sources at bottom; nothing load-bearing quoted from memory).

---

## §1. The inventory — read as communication assets

Much of the campaign IS communication research that we never filed under that name:

| Asset | Communication reading |
|---|---|
| F83/F85 capacity activation (0.0436 bits through two zero-capacity channels, 55.6σ; N=3 61.7σ + inversion) | Literal channel-coding results — the repo's core communication findings |
| F82 causal game (one query of each operation, 216.8σ over the causal bound) | A communication-complexity-flavored discrimination protocol with a provable ceiling |
| F01 CHSH 2.74 (96.8% of Tsirelson) | The entanglement-distribution quality floor; feedstock for semi-DI randomness (roadmap T2.7) |
| F02 GHZ sublinear decay | Multipartite distribution (conference-key / secret-sharing substrate) |
| Finding 51 / Exp102–103 (IPE feedforward survives hardware) | **Dynamic circuits work on this chip** — the enabling primitive for teleportation-class protocols |
| `grade_exp106.py` MI machinery | Working mutual-information estimation from counts |
| X-basis compilation, quiet-qubit picker, window sentinels, depth-decay law | A channel-engineering toolkit: which qubits, when, which basis, how deep |
| F86 + demon ledger (I(C:T) = 0.025 bits) | Thermodynamic side of the same coin — the control–target correlation as a priced resource |

**The white space** (checked this cycle): in 115 findings there is **zero teleportation, zero
superdense coding, zero entanglement swapping**. The three canonical communication primitives
are absent — while the enabling feedforward primitive is validated and idle.

## §2. The verified literature map

**The resource debate is real and unresolved.** Chiribella–Kristjánsson's Shannon theory with
superposed trajectories (2019) and Abbott et al.'s "communication through coherent control of
channels" (2020) frame the standing dispute: are the switch's communication advantages an
*indefinite-causal-order* resource, or just *coherent control* — obtainable from a plain
superposition of paths with no ICO at all? Experiments exist on photonics (PRR 3, 013093;
Quantum 7, 1125) and NMR (arXiv:2606.10744, superactivation), and an **October 2025 theory
paper (arXiv:2510.16485) analyzes the COMBINATION of switch and path-superposition** —
which, as far as our search found, **no one has executed on gate-model hardware, and no prior
work on any platform runs all configurations co-batched with frozen bound-referenced
grading.** This is the same critique the roadmap flagged against the switch-fridge (T2.4
"ICO-powered vs coherence-powered"), now standing against F83/F86.

**Teleportation with dynamic circuits is well-trodden on this platform** — IBM ships a
long-range-entanglement tutorial, and a June 2026 paper characterizes branch-resolved
feedforward error in dynamic teleportation on ibm_fez (arXiv:2604.28037). Demo value: zero.
What our search did NOT find: a measured **SWAP-vs-teleport crossover law** — at how many
hops does feedforward beat unitary routing, under stated window/placement conditions.

## §3. Discovery paths, ranked

### E1 — The resource-comparison experiment (headline path)

One job, four co-batched arms on the same qubits in the same window: (a) quantum switch of
two depolarizing channels (our Exp106 apparatus, re-used), (b) **superposition of paths**
through the same two channels (one new circuit family — control routes the target through
channel A or B coherently), (c) the classical mixture control, (d) definite-order null.
Grade all against the same frozen rules; report capacity/MI per arm. **Whatever lands, we
learn something the literature is arguing about**: if (b) ≈ (a), coherent control is the
resource and F83's ICO framing gets an honest caveat measured by our own hands (the
confirmation-symmetry move); if (a) > (b) at matched coherence budget, the ICO reading
strengthens. The 2510.16485 hybrid configs extend the family. Directly pre-empts the
sharpest referee attack on the paper AND on F86 — and the fridge twin (superposition-of-paths
refrigeration arm on the Exp108 harness) is the T2.4 discriminating test the roadmap always
wanted. **Cost**: sim-first (zero QPU); hardware arm ~Exp106 class. Feeds new rows to the
atlas, the depth-decay law, and the status ledger.

### E2 — The SWAP-vs-teleport crossover law (routing as science)

Fidelity per hop across the heavy-hex lattice, two arms: unitary SWAP chains (3 CZ/hop,
depth grows) vs teleportation chains (pre-shared entanglement + mid-circuit measurement +
feedforward — depth stays flat, classical wire does the work). The depth-decay law files a
pre-data prediction for the SWAP arm; the teleport arm tests Bridge-1's deepest lever
("every gate replaced by feedforward is free depth") in its natural habitat. Platform priors
credited up front (IBM tutorial; 2604.28037). The deliverable is the **crossover hop-count
N\*** and a design rule for `design_optimum.py` — when to route unitarily vs teleport,
window-gated. **Cost**: one prereg, moderate QPU (~game-class), high reuse.

### E3 — Superdense coding, bound-referenced (quick win, fills the white space)

The canonical entanglement-assisted result: 2 classical bits per transmitted qubit vs the
1 bit/qubit classical ceiling. Two qubits, shallow, X-basis-aware compilation, frozen
threshold (bits decoded above the classical ceiling at pre-registered σ), definite-resource
null arm (no entanglement → capped at 1). Exists in every textbook and on every platform —
the claim is scoped accordingly (our signature grading discipline, not novelty). **Cost**:
cheapest hardware item on this list; pairs naturally with the capacity story on the front
door ("both directions: channels that carry nothing, and a qubit that carries double").

### E4 — Entanglement-swapping chain (repeater analog on-chip)

CHSH violation vs number of swap stations (0, 1, 2 …) using feedforward Bell measurements —
the on-chip analog of a repeater chain, connecting F01 to the F62 toric Bell-proxy line.
Gives a violation-vs-hops decay law (another depth-decay family member, now in the
entanglement-distribution observable class the atlas doesn't yet cover). **Cost**: moderate;
after E2 (shares the teleport primitives).

### E5 — Semi-DI randomness scoping (zero QPU, standing)

The min-entropy-per-game-win theory gap (roadmap T2.7) is the honest cryptographic direction
for the game arc; still a literature-collaboration item, unchanged — re-flagged so it stays
visible in the communication frame where it belongs.

## §4. Recommended sequence

| # | Item | QPU | Gate |
|---|---|---|---|
| 1 | E1 sim tier (paths + hybrid circuit family vs switch) | zero | start now; hardware prereg after Exp108b grades |
| 2 | E3 superdense prereg | small | fastest white-space fill; linter + feasibility tiers per template |
| 3 | E2 crossover prereg | moderate | after E1 hardware (shares window discipline lessons) |
| 4 | E4 swap chain | moderate | after E2 (shares primitives) |
| 5 | E5 scoping note | zero | rainy-day cycle |

**Sources verified this cycle**: [arXiv:2510.16485](https://arxiv.org/html/2510.16485)
(switch + superposition combined), [PRR 3, 013093](https://journals.aps.org/prresearch/abstract/10.1103/PhysRevResearch.3.013093)
(photonic trajectories experiment), [Quantum 7, 1125](https://quantum-journal.org/papers/q-2023-10-03-1125/)
(experimental superposition-of-channels), [arXiv:2606.10744](https://arxiv.org/html/2606.10744)
(NMR superactivation), [PRR 5, 023111](https://journals.aps.org/prresearch/abstract/10.1103/PhysRevResearch.5.023111)
(switch vs simulations, energetic constraints), [IBM long-range entanglement tutorial](https://quantum.cloud.ibm.com/docs/en/tutorials/long-range-entanglement),
[arXiv:2604.28037](https://arxiv.org/html/2604.28037) (branch-resolved dynamic teleportation, ibm_fez).
