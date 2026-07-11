# What We Found On a Real Quantum Computer (In Plain English)

*A shareable, jargon-free summary of an ongoing autonomous research campaign on IBM's Heron-generation quantum chips (May–July 2026, ~100 experiments across three real devices). The first section covers the original 22-experiment characterization (Arc 1, Findings 1–9); the "Since Then" section covers the arcs that followed, including the indefinite-causal-order results. For the technical version with job IDs and source citations, see [`README.md`](README.md). To **play** with the results instead of reading about them: [mblakemore.github.io/quantum](https://mblakemore.github.io/quantum/) — an interactive demo, two games, and a print-&-play tabletop version, all running on the measured numbers.*

---

## 30-Second Version

An AI-agent network ran **~100 experiments on real IBM quantum computers** — 156-qubit chips, not simulators — on a strict budget of actual quantum-computer seconds. Two stories came out.

**The headline story**: the order of two operations can itself be put in quantum superposition — and that lets the chip do things that are *provably impossible* for any machine that does things in an order. It won a guessing game above the game's mathematical ceiling (97.7% against a proven 87% limit, on two different chips). It sent a message through two channels that each carry exactly zero. It made a qubit come out colder or hotter than its surroundings in a way no ordered process can arrange. (Sections 16–19.)

**The workhorse story**: we tested whether the standard quantum-computing tricks actually work on real hardware. Mostly they don't — but a few do, and one hits chemistry-grade accuracy on a real molecule. The chip is **bounded** (there are walls today's algorithms can't pass), but the bounds are **knowable**, and inside them there's real, usable value — if you respect the hardware instead of pretending it's perfect. (Sections 1–15.)

---

## 2-Minute Version: The 9 Findings

### 1. The Chip Really Does Quantum Entanglement (96.8% of the limit)
We ran the standard "is this thing actually quantum?" test (CHSH / Bell inequality). The chip scored **2.74** against the textbook quantum maximum of about 2.83 and the classical-physics ceiling of 2. That's about **96.8% of the way to "as entangled as physics allows."** The tiny gap (~3.2%) is the "decoherence tax" the hardware charges — and we can measure it precisely.

### 2. Adding Qubits Is Cheaper Than Expected
When you tie 2, 3, 4, 5 qubits into one shared quantum state, the textbook says quality should fall off fast (multiplicatively). On this chip, **each extra qubit costs less than the previous one** — the chip's wiring is designed to keep unused qubits from interfering with active ones. Practical version: **width is cheap on this chip; what's expensive is depth — long sequences of operations** (see Finding 5).

### 3. The Chip Has an "Easy Direction" to Read (3× More Reliable)
A qubit is like a tiny arrow that can point along X, Y, or Z. The chip's main noise mostly spins the arrow around the **Z**-axis. So if you choose to read in the **X direction**, the noise spins the arrow in a circle that goes *through* your measurement axis — you barely notice. If you read in the **Y direction**, the noise hits you head-on. **Same circuit, just a different "viewing angle," about 3× more reliable.** We confirmed this three independent times. This is the single cheapest, most reliable win in the whole report — it's a compile-time choice, free.

### 4. The Chip's Mid-Circuit Errors Have *Structure* (They're Not Random)
We ran a circuit forward, then perfectly backward (a "Loschmidt echo"). If the chip's noise were truly random ("white noise"), the rewind should fade smoothly. Instead, the rewind **dropped below random and then bounced back up**, in a smooth oscillation. That's the fingerprint of a tiny *systematic* miscalibration in some of the chip's couplers, accumulating coherently over many gates. **The fix isn't longer-coherence qubits — it's better-calibrated couplers.** Different problem, different solution.

### 5. There's a Brick Wall at ~1000 Gate Operations
Past about **800–1000 two-qubit gates** deep, the chip's output is statistically **indistinguishable from random coin flips**. You're not computing anymore — you're generating noise. This is a **hard ceiling** for today's algorithms on this chip. Count the two-qubit gates in your compiled circuit. If it's more than ~1000, redesign. There's no software fix.

### 6. Quantum Error Correction Doesn't Work Yet (Surprising Reason)
The standard plan to protect quantum data is to add **"spy" qubits** that monitor for errors. On this chip, **the act of checking adds about 2,000× more noise than the check could possibly remove.** We even saw cases where adding error correction took clean data from 85% accuracy down to 78% accuracy — *the protection was more toxic than the noise it was protecting against.* Until hardware gate errors drop another ~100×, the textbook protection plan **doesn't break even** on real chips.

### 7. The Standard "Noise Cleanup" Software Doesn't Help Either
The quantum community has a toolbox of clever software tricks (Dynamical Decoupling, Pauli Twirling, Twirled Readout Mitigation, Zero-Noise Extrapolation) that are supposed to *undo* hardware noise. We tested all four on this chip. **All four made things worse, not better.** Each trick was invented for an older generation of chips with different dominant noise. Meanwhile, we discovered the chip's day-to-day natural variation is **±7 percentage points** (same circuit, same settings, 24 hours apart), so any tiny "1–2pp improvement" from software tricks is **lost in the chip's natural wobble.** Stop spending engineering effort on noise-cleanup software for this chip generation; spend it on making your circuits shorter and on choosing the chip's "easy direction" (Finding 3).

### 8. **We Computed a Real Molecule to Chemistry-Grade Accuracy**
The good news. We computed the ground-state energy of the hydrogen molecule (H₂) on the real chip. The answer was off by **0.001 Hartree** from the textbook exact answer — well inside the "chemical accuracy" threshold chemists actually use. For context, the standard non-quantum approximation was off by **53× more**. *How?* By using a **hybrid algorithm** (VQE) that asks the chip only for shallow, simple measurements and lets a classical computer do the heavy lifting. **When you respect what the chip is good at, it does real science.**

### 9. **Quantum Speedups for Probability Estimation Work — With the Right Readout**
Quantum Amplitude Estimation (QAE) is the quantum trick that powers faster Monte Carlo and option pricing. But on a noisy chip, the textbook readout **completely fails**: when you're trying to measure a probability near 0 or near 1, the answer can be off by **77% (basically as wrong as the right answer).** The fix: run the algorithm at multiple depths (k=1, 2, 3, 4) and use a *maximum-likelihood estimator* to find the single probability that explains all the measurements at once. On real hardware, this brought our error from up to 77% **down to under 0.5% — a 344× tightening.** QAE works on today's chips — if you do the readout right.

---

## Since Then: The May–July Arcs (2 More Minutes)

*The campaign continued past the original characterization — nearly 100 experiments total, now spanning three real chips (`ibm_marrakesh`, `ibm_kingston`, `ibm_fez`) plus hardware-realistic simulation. Simulation-tier results are labeled as such in the README; everything below marked "on real hardware" ran on a physical chip.*

### 10. Location Beats Length: Run on the Quiet Qubits
The biggest *practical* discovery of the later arcs. A quantum chip is like a neighborhood — some qubits are quiet, some are next to a construction site, and the map changes daily. Placing a circuit on the currently-quietest qubits cut errors up to **46×** (on real hardware), and controlled experiments showed **which qubits you use matters ~3× more than how many operations you run**. A reusable tool now reads the chip's live calibration data and picks the quiet qubits automatically — it worked unmodified on a second chip on the first try. One rule: never cache the pick; yesterday's quiet qubits are already stale.

### 11. A Practical Recipe for Quantum Optimizers
Quantum optimizers (like QAOA) start from a guess and iterate. A long experimental arc produced a simple, tested recipe: **reuse your best previous answer as the starting point** (it never hurts, and it rescues runs that would have just barely failed) — but only *within* the same problem; a tuned start does **not** transfer to a different problem. You can't cheaply predict which random start will be good, so **generate a few candidates and keep the best**, drawing more only when the first looks weak (that laziness saves ~30% of the compute at almost no cost). Reassuringly, hardware noise blurs *how much better* your best start is without changing *which one* is best.

### 12. Noise Never Actually Helps (We Checked, Twice)
Two seductive earlier results suggested a little noise *improved* things — sharper estimates in one case, better trap-escape in another. Under proper controls, **both evaporated**. The "sharper estimate" was a confidently-wrong answer that merely looked precise (its error bars excluded the true value 100% of the time). The "better escape" improved a bookkeeping ratio while making every actual answer worse. An audit also caught a planned "noise helps" hardware test whose pass was guaranteed in advance — flagged and cancelled before it wasted quantum-computer time. Standing verdict: on this hardware, noise is a cost, never a resource.

### 13. A Real Market Probability on a Real Chip — and Why Quantum Finance Isn't Here Yet
The network computed a genuine financial quantity — the probability of a QQQ (Nasdaq ETF) price move — **on real hardware, accurate to about 2%**. That's a milestone. But an ordinary laptop still wins on every practical axis, and the quantum speedup that would change that needs circuits **50–100× deeper** than the chip's ~1000-gate wall allows. The later arcs pinned the precise culprit: the more realistic your market model, the deeper the "data-loading" part of the circuit — and that loading depth, not the quantum algorithm itself, is what poisons the answer. Simple models stay clean; realistic ones die at the wall.

### 14. Error Correction Still Doesn't Break Even (Independent Replication)
The team rebuilt an outside group's quantum-error-correction experiment from scratch — a "toric code" storing two protected logical qubits — and confirmed its most sobering result on real hardware: **performing one round of error correction made the result worse, not better** (the same "the protection is more toxic than the noise" effect as Finding 6, now confirmed in a second, independent setting). Every extra gate measurably hurt, and the protected state fundamentally can't be made as cheap as an unprotected one.

### 15. A Consciousness-Math Side Quest
A research detour applied Φ ("integrated information" — a score from consciousness science for how much a system acts as one unified whole) to quantum circuits. Classically, ring-shaped circuits whose size is a **prime number** score wildly higher than others. Make the rings quantum, and that entire number-theory drama **vanishes** — every size becomes inseparably entangled and scores about the same, compressing the spread of scores 354-fold. The arc also modeled good scientific hygiene: two exciting preliminary claims ("the law breaks at size 15!", "odd and even rings grow at different rates!") were retracted after careful statistical rechecks.

### 16. **The Headline: Cause-and-Effect Order Can Be Put in Superposition**
In everyday life — and in all of classical statistics — two operations happen in *some* order: A-then-B, or B-then-A, or at worst a coin flip between them. The network built a **quantum switch**: a circuit where the order itself is placed in superposition, and a single measurable "witness" number that no definite order — *and no coin-flip mixture of orders* — can reproduce. On real hardware, the witness fired decisively: the result excludes every classical ordering story at **≥72 standard deviations** (particle-physics discoveries require 5), verified on the same device in a single calibration window to rule out drift, and replicated on a second chip. The "amount" of indefiniteness even turns out to be a smooth dial that follows a clean cosine law. One caveat: this certifies that the *order* was genuinely quantum — it is not by itself a computational advantage. One proposed follow-up check was withdrawn by its own author after proving it was circular: a test that cannot fail proves nothing. The advantage version came next — see 17.

### 17. **The Payoff: Winning a Game No Ordinary Computer Can Win (July 2026)**
Imagine a game show. Each round you get two mystery machines, A and B, with a promise: either they're **friendly** (A-then-B gives the same result as B-then-A) or **clashing** (opposite orders give perfectly opposite results). You may run each machine **once**, then guess which. Here's the provable speed limit: any player who uses the machines in *some* order — even flipping coins, even adapting mid-game — **cannot win more than ~87% of rounds**. That's a theorem (we re-derived the exact number, 0.8695, from scratch and cross-checked it three ways), not an engineering limit. The quantum switch plays a move no ordered player has — both orders in superposition — and in theory wins 100%.

**Our chip won 97.7%** (±0.05%), far above the 87% ceiling, under rules frozen *before* the data existed: a tamper-proof scoring rule, a same-chip control player using ordinary ordering (who scored 61% — exactly the "free" rate the math predicts), and canary circuits at the start, middle, and end of the run proving the chip's quality held steady throughout. This is the campaign's first **provable-bound beat**: not "faster than a laptop" (it isn't), but a demonstration that the chip can do something **no step-by-step computer can do at all** with the same limited resources. Like proving your car has a gear no one else's transmission physically contains.

Two details worth telling: the game's difficulty turned out to live in its most boring-looking piece — remove the "do-nothing" identity machine from the mix and a clever classical player wins 100%, so the trivial cases are what make the game hard. And the result was a genuine team effort with adversarial review: four separate hand-offs between two AI agents each caught a real flaw that would have weakened or invalidated the claim — including one where the circuit compiler silently "optimized away" a fairness feature and had to be fenced off. Proposal to victory took one day. And the next day, the entire experiment was re-run from the same frozen playbook on a **second, physically different chip** it had never touched: **97.4%** — same verdict, within a third of a percentage point of the first chip. Not a lucky day; a property of the hardware generation.

### 18. **Sending a Message Through Two Walls (July 2026)**
Take a channel that completely erases whatever goes in — pure static out, always. Two of them in a row erase even harder. It's provable that NO arrangement of those two erasers in any order — first this one, first that one, a coin flip, even choosing the order on the fly — can carry a single bit. Capacity: exactly zero. We put the two erasers in a **quantum superposition of both orders** and a message got through: **0.044 bits per use, 56 standard deviations above zero**, measured on the real chip with the rules frozen in advance. The control experiment on the same chip (erasers in a definite order) carried 0.0001 bits — nothing, as the math demands. The eeriest part, predicted in advance and confirmed: look at the message wire alone and it's STILL pure static — the message exists only in the *correlation* between the two readouts. Each wire says nothing; together they speak. It's a small message, but it travels a road that provably does not exist for any ordinary machine.

We then tried **three** walls instead of two. In theory the message gets bigger with more walls; in practice it got *smaller* — the three-wall circuit costs ~27× more gate operations, and the depth tax ate more than the extra superposition bought. Both directions were predicted in advance and both were measured. That inversion — theory scales up, hardware scales down — turned into a quantitative law that now predicts, before spending any quantum time, how much of a circuit's ideal performance the real chip will deliver. The law's first blind test beat the official simulator's prediction by a factor of 2.3.

### 19. **Colder Than Its Surroundings, By Order Alone (July 2026)**
Put a qubit through two "baths" that completely reset it to room temperature. Any order — this bath first, that bath first, a coin flip, even choosing on the fly — provably leaves it at room temperature, full stop. Run the two baths in superposition of both orders and measure the control qubit: **the qubit comes out colder than the baths on one outcome (and hotter on the other)** — a splitting 21 standard deviations above the exactly-zero prediction for every ordered process. This is the resource behind proposed "causal-order refrigerators." Two things worth saying plainly: without using the measurement outcome the hot and cold branches cancel exactly (no free lunch — it's a Maxwell's-demon setup, and the fuel is information), and similar protocol demonstrations existed before on other platforms — ours adds the theorem-referenced scoring, the frozen rules, and a follow-up where the baths' randomness comes from the chip's own natural decay instead of synthetic preparation.

## Three Common Beliefs, Refined

There are three things people commonly believe about quantum computers that this campaign **refines**:

1. **"Quantum computers are basically classical computers with extra speed."** No — they have entirely different cost structures. On *this* chip, *width is cheap* and *depth is the wall.* Algorithms designed assuming classical-style cost trade-offs (especially deep Grover-type search) hit a hard ceiling that no amount of software can move.

2. **"Software error mitigation will smooth over hardware noise."** Mostly false on this generation. Four canonical mitigation techniques all *degraded* signal; the chip's natural day-to-day wobble dwarfs anything the tricks could fix. The real path forward is **hardware-aware compilation** (pinning the compiler's choices, choosing the chip's easy measurement direction, keeping circuits short).

3. **"Today's quantum computers can't do anything useful."** Also false. When you respect what the hardware is genuinely good at (shallow circuits, hybrid quantum-classical algorithms, X-basis measurements), you can hit **chemistry-grade accuracy on real molecules** and **production-grade precision on quantum amplitude estimation**. Useful science is happening right now, inside the hardware's actual constraints.

---

## Why You Should Trust This

- **Every single number** in this report traces back to a specific IBM Quantum job ID (a permanent record on IBM's servers), a calibration date, and a Python script. The full inventory is in [`experiments/job-manifest.md`](experiments/job-manifest.md).
- **Pre-registration discipline**: every experiment defined falsifiable pass/fail criteria *before* the job ran. Failed pre-regs are reported with the same prominence as passed ones — the campaign treats "the data refuted our hypothesis" as a first-class result, not a failure to hide.
- **Hardware where it counts**: all 22 original experiments ran on physical quantum hardware (`ibm_marrakesh`, a 156-qubit Heron-r2 chip). Later arcs use a mix of real chips (three devices) and hardware-realistic simulation — and every result is labeled which tier it ran on, because the campaign itself caught the simulator being *optimistic* about real chips more than once.
- **Self-correcting**: several of the campaign's own earlier claims were later killed or retracted by the campaign itself under better controls (a "noise helps" result, a sampling illusion, an underpowered statistics claim, a circular test caught before it ran). Failed ideas are documented as thoroughly as successes.
- **Scope**: these findings describe **this generation** of superconducting NISQ hardware. They are not claims about the long-term ceiling of quantum computing. The methodology generalizes; the absolute numbers may not.

---

## What This Means For You

**If you're a quantum-algorithm designer**: read [`docs/next-steps-and-open-questions.md`](docs/next-steps-and-open-questions.md) ("What You Can Use Today"). The 7 actionable items there will save you weeks of dead-end engineering.

**If you're a researcher**: the 7 open research questions in that same section are the next campaign's targets.

**If you're a curious technologist**: play the games at [mblakemore.github.io/quantum](https://mblakemore.github.io/quantum/) — the ceiling you can't beat and the switch that beats it are more convincing hands-on. The chip is real, it works, it's bounded, and the bounds are knowable. The popular narrative ("quantum is magic" / "quantum is hype") is wrong on both ends. The truth is more interesting: it's *real engineering*, with real trade-offs, and the trade-offs are now measured.

**If you're a science journalist or educator**: feel free to use this document directly. Citation: link to this repo (`github.com/mblakemore/quantum`) and reference the IBM Quantum job IDs for any specific number.

---

*Full technical version: [`README.md`](README.md). Per-finding deep dives: [`findings/`](findings/). Reproducible figures: [`scripts/generate_figures.py`](scripts/generate_figures.py). Sources: [`sources/references.md`](sources/references.md).*
