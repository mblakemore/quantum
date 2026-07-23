# What We Found On a Real Quantum Computer (In Plain English)

*A shareable, jargon-free summary of an ongoing autonomous research campaign on IBM's Heron-generation quantum chips (May–July 2026, ~100 experiments across three real devices). The first section covers the original 22-experiment characterization (Arc 1, Findings 1–9); the "Since Then" section covers the arcs that followed, including the indefinite-causal-order results. For the technical version with job IDs and source citations, see [`README.md`](README.md). To **play** with the results instead of reading about them: [mblakemore.github.io/quantum](https://mblakemore.github.io/quantum/) — an interactive demo, two games, and a print-&-play tabletop version, all running on the measured numbers.*

---

## 30-Second Version

An AI-agent network ran **~150 experiments on real IBM quantum computers** — 156-qubit chips, not simulators — on a strict budget of actual quantum-computer seconds. Three stories came out.

**The headline story**: the order of two operations can be put in quantum superposition. The idea came from theorists; photonics labs demonstrated it first, and early versions ran on chips like ours. **What this campaign added was the scoreboard** — and the switch delivered: it won a guessing game above the game's proven ceiling (97.7% against a mathematical 87% limit, on two different chips), sent a message through two channels that each carry exactly zero, and made a qubit come out colder or hotter than its surroundings in a way no ordered process can arrange. (Sections 16–19.)

**The newest story (July)**: for a year the scoreboard said the quantum computer could not beat a classical program at any *timed race*. It turns out the referee had been listening only for the machine's single loudest answer — while every repeat of the experiment was quietly whispering the SAME hidden answer with a few random typos. Average the whispers letter-by-letter and you can read the answer through noise that destroys every individual shout. Six carefully-refereed rematches later (each loss teaching one specific fix, with the answer sealed in a cryptographic envelope by one AI teammate and the stopwatch held by another), the machine read a sealed 40-letter answer perfectly in **under 4 seconds** where the best classical program needs **half an hour at minimum** — a certified **476× win**, which prints its own expiry rule: if anyone's classical program ever beats it, the entry retires itself. (Section "The Decoder Races" below.)

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

## The Decoder Races: How a "Closed Window" Became a 476× Win (July, newest)

**The setup.** There's a puzzle family (finding a hidden 40-letter "shift" in a scrambled function) where a quantum chip *should* be fast and a classical program provably has to grind. Our first attempt ended in an honest loss: at the depth the puzzle needs, the chip's single most-frequent answer decayed to uselessness, and we published "window closed" with the exact number a future machine would need to beat.

**The overlooked thing.** The next morning, re-reading that failed run's own discarded calibration data: the most-common answer at depth wasn't garbage — it was the right answer *with two typos*. Every shot was whispering the truth with a few random letter-flips. **Averaging thousands of whispers letter-by-letter reads the answer through noise that kills the shout** — the repeats form an error-correcting code in time. That insight (finding F120) made the "closed" window measurably 30× wider than the old referee could see.

**Six rematches, six honest losses-that-taught.** Each race was run like a courtroom: one AI teammate sealed the secret answer cryptographically before the machine flew; a second flew and decoded blind; a third held a frozen classical stopwatch. Race 1 lost to a bookkeeping bug in bit-ordering (caught by the court in minutes). Race 2 lost by ONE letter at a checkpoint placed 20% too deep. Race 3 lost to two bad readout wires on the chip. Race 4 fixed those and proved the method exact at record depth — but drew an unlucky deep layout. Race 5 deliberately dropped a safety measure to test whether it was needed (it was — lesson bought and booked). Every rule was frozen before data; nobody got to move a goalpost, including us.

**Race 6: the win.** On a fresh chip region certified clean by a free self-test *before* the sealed answer was risked, the machine read the sealed 40-letter answer **perfectly** — from just 12,500 repeats, in **3.82 seconds** of quantum-computer time, versus a classical floor of **30 minutes** with its best tool (and ~6.5 hours realistically). That's **476× at the harshest comparison, graded by all three AI seats independently** (finding F121). The scoreboard entry prints its own retirement clause: any classical program that beats the floor supersedes it. That's not a weakness — that's how honest racing works.

**The physics bonus round.** With the win banked, two instrument flights measured *why* deep circuits die: the "magic tax" (the extra noise cost of the gates that make quantum computers more than fancy classical ones) turns out to be a **flat ~30% fee, not a growing toll** — what grows with depth is a strange slow coherent *twist* on a few specific bits that none of the standard software cures can touch (we caught it because two different measuring conventions started disagreeing — the disagreement itself was the detector). One of our own hypotheses and one teammate's died honest deaths along the way, each graded by its own author.

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


---

## 20. The week we built a network and an engine (plain English)

In three days the quantum switch went from a certified curiosity to a working resource:

- **Two bits in one qubit** (superdense coding): with pre-shared entanglement, one sent
  qubit carried two bits of information — 341σ above the proven no-entanglement ceiling,
  and the control run *without* entanglement landed exactly on that ceiling (0.4988 vs 0.5).
- **The great debate, settled on silicon**: skeptics said the switch's magic is just
  "coherent routing," no exotic causal stuff needed. We ran both, side by side, same hour:
  routing alone DOES work (its own win) — and the switch beats it by **exactly 2×**, just
  as theory predicted (measured ratio 1.949 vs theory 2.000).
- **Beaming the arrow of time**: we teleported the qubit that *decides the causal order*
  one hop across the chip — and it arrived still causally indefinite (97% intact), while
  the same teleport over a deliberately classical channel killed the effect stone dead.
  Survives quantum, dies classical: that pair of facts is the whole claim.
- **A repeater**: a Bell violation survived TWO entanglement-swapping relay stations —
  the basic building block of a quantum internet, graded against the exact classical limit.
- **Resurrection**: we deliberately poisoned entangled pairs until their Bell violation
  died (below the classical line), then *purified* two dead pairs into one living one
  (back above the line, same test, same hour). One sub-claim missed its pre-set bar by a
  hair (0.33σ) and is recorded as a loss — the rules don't bend after the data exists.
- **The engine**: two heat baths, each certified too bland to power anything (5σ below
  the useful line) — put causal indefiniteness between them and one output branch comes
  out *charged* (+10.6σ above the line): extractable work, paid for by the demon's
  information, books audited by a Landauer ledger. Along the way the same gate structure
  refused a +23σ *fake* win caused by bad vendor calibration data — the proudest
  non-result of the campaign.
- **The engine ran its full cycle** (the capstone, F95): intake (both baths certified
  passive — after measuring each qubit's *actual* decay rate, because the vendor's
  published numbers were off by 111% on one qubit and 35% on its neighbor), compression
  (battery charged, 7σ), power stroke (work drawn: 0.0340 energy-units per run), exhaust
  (the drained output certified passive *again*, 5σ — nothing usable left behind). The
  demon's meter read +0.0051 per action. One pre-set quantitative bar was missed by 0.7σ
  and stands in the record as a loss, right next to the win.
- **The lie detector, pointed at the scheduler** (F96): after months of *building*
  machines that run on scrambled cause-and-effect, we flipped the tool around and asked
  the chip a suspicious question — when you're told to fire two gates "at the same
  time," do you secretly run one first? Answer, measured at the worst spot on the chip
  with the effect amplified 8×: **no.** Simultaneous means simultaneous, certified down
  to our measurement floor — a guarantee the vendor doesn't offer. Bonus catch: the
  naive analysis would have cried "hidden order!" (parallel runs *do* look different) —
  but they differ *equally from both orderings*, the fingerprint of "faster, not
  sneakier."
- **Energy below zero, certified** (F97): we made a tiny patch of the chip hold
  *less energy than empty* — the energy-sign that warp-drive math asks for — twelve
  sigma below the ground level, with books so conservative the real effect must be
  bigger than we claim. The honest half of the story is in the same record: the
  sci-fi version (beaming energy with a classical radio message) FAILED — the radio
  delay costs more than the energy it moves, and we measured that price exactly.
  What worked is the quantum-controlled version. Sister finding: the winning move
  came from a near-miss we refused to count until it passed a fresh, pre-registered
  retest.
- **Reality's notebook, scrambled on purpose** (F98): objective facts exist because
  the world keeps redundant records. We made the ORDER of two competing record-keepers
  (one writing down "which way," one writing down "which phase") quantum-indefinite —
  and the rules of fact-making bent both ways. In three runs out of four, BOTH
  incompatible notebooks came out ~80% right at once — a sharing of reality that no
  ordering of those two writers can produce. In the fourth run — flagged in advance
  by a herald qubit — both notebooks came back blank. Runs where no fact was written,
  announced before anyone looked.
- **The black-hole diary trick** (F99): write a secret in a qubit, let two
  "horizon" recorders read it in either order — and the secret is provably GONE
  from the qubit; we measured the emptiness forty times below the effect. But hold
  the ORDER of the two readings in quantum superposition, and in one heralded run
  out of four the qubit hands the secret back — every bit flipped, 56-sigma sure.
  The mirror only works if you refuse to say when you looked. Bonus rule of the
  universe, measured almost exactly on theory: ask the wrong question first and
  NOBODY — not even the recorders — gets to learn the fact.
- **The twin paradox, on a chip — finding #100** (F100): send a ticking clock down
  two roads at once. If the clock is running (aging, radiating), the universe can
  tell which road it took — and the two roads stop interfering: 36-sigma certain,
  measured in a way no phase-trick can fake. An identical but STOPPED clock keeps
  the roads perfectly ambiguous. The best part is the provenance: our first run of
  this experiment "won" but we flagged our own reading as possibly fooled (the
  signal had rotated into an axis we weren't watching); the retest watched every
  axis, refuted our own favorite excuse, and certified the real thing. Finding
  one hundred is the honesty machine itself.
- **The grandfather paradox, with a receipt** (F101): we built a quantum time
  loop (Lloyd's recipe — the loop is a post-selection rule, stated up front) and
  sent in a qubit trying to flip its own past. The universe's answer, measured:
  the full paradox survives at 1.9% — pure readout noise; the math says exactly
  zero — and the "how forbidden is it" curve tracks theory to one percent. Better:
  an innocent bystander who merely SHOOK HANDS with the time traveler came out
  changed — its ordinary classical record turned into quantum coherence, 78-sigma
  sure. Time loops don't just punish paradoxes; they leave fingerprints on
  everyone in the room.
- **And the weather report went public**: the platform's moods (T1 values that swing 2×
  in a day, a noise model blind to feedforward) are now charts anyone can read
  ([demo/weather](demo/weather/index.html)), with the four tricks we use to work through
  them.

Findings F87–F101, every one pre-registered, every miss in the record.

---

## 21. Since F101: games, sensors, limits, and a cold qubit put to work (F102–F118)

The campaign kept flying. Seventeen more findings, same house rules: every bar written down before the job runs, every number chained to a real IBM chip, every miss left in the record next to the wins. As before, "σ" is just a confidence dial — how many times bigger the effect is than the noise that could fake it; past about 5σ you stop worrying it was luck.

- **The triptych closed** (F106): there are three great "no classical picture can do this" games in all of quantum physics — Bell's nonlocality (won back at F73), scrambled cause-and-effect (F82), and *contextuality* (the idea that a measurement's answer can't have been sitting there waiting, independent of what you measure alongside it). We won the third one — the Peres–Mermin "magic square," a grid puzzle no classical strategy can fill in perfectly — at **196σ**, with the classical ceiling (8/9) not *cited* but *counted*, by having the computer check all 4,096 possible classical cheats. Even the puzzle's hardest single row beats what any classical mixture allows. Three-for-three, all on the same chip. It's a game-score win, not a speed-up — that distinction matters and we keep making it.

- **A measurement used as a tractor beam** (F102): watching a qubit hard enough *pins it in place* against a rotation that would otherwise flip it — the quantum Zeno effect. Watched at the right cadence it survived at 0.644 where the unwatched qubit flipped to 0.020 (**92σ**), and the "how often to look" law matched theory to half a percent. Zero two-qubit gates — the cheapest flight of the whole campaign — and it completed the "Horizons-2" set of six universe-questions, six-for-six.

- **A pocket dictionary in a single qubit** (F107): we crammed *two* bits into one qubit such that a reader can pull out *either* one on demand (not both — that's forbidden). That beats the one-bit classical ceiling (**110σ above 0.75**) while landing honestly *inside* the quantum speed limit — going past *that* would have meant something was wrong, not something was won. Cheapest possible advantage: no two-qubit gates at all.

- **A navigator's sextant at the ultimate precision** (F108/F109): three entangled qubits, used as one sensor, carried **2.848× the phase information** of the best that three *un*-entangled qubits could — measured against a real separable sensor run on the same three qubits, **168σ** — and the advantage held as we grew the probe to five qubits. The honesty here is load-bearing: this is an *existence* result about information content in a lab, **not** a deployment win. The very trick that sharpens it (a fringe oscillating 3× faster) also introduces a threefold ambiguity about *which* peak you're on, and under real-world timing-with-noise the scaling advantage runs into a known textbook wall (the Huelga–Plenio limit). A sharper needle, not yet a better compass.

- **Two limits the universe puts on quantum itself** (F110, F111): the campaign usually beats classical bounds; here it certified bounds that bind *quantum*. The best possible copier can only clone a qubit at 83.3% fidelity (5/6) — measured flat across every basis, a hair under the ceiling and never over it. A pre-registered *cheat* beat the ceiling in one direction (0.99) but paid for it in the conjugate direction (0.50): the only way to beat no-cloning somewhere is the way to get caught elsewhere, a 24× tell. And a "cloaking device" readout (F111) mapped the chip's own forgetfulness — is its phase-noise memoryless or does it remember? — finding it *mostly* memoryless with a real, subdominant ~10–15% correlated tail. A bet that active error-echoing would win by a specific margin missed and stayed in the record.

- **The court that travels** (F112): the causal-order test-bench was carried to **three different chips** and certified against the same frozen bars with *no retuning* — proving these effects belong to the hardware *generation*, not one lucky die. It even ranks the three devices on axes the standard vendor benchmarks don't touch. One die wasn't a clean sweep (a data guard tripped on one axis) — noted, not buried. This completed "Horizons-3."

- **A genuinely different scoreboard, flown very honestly** (F113/F114): there's exactly one proven quantum speed advantage that needs no unproven assumptions — Bravyi–Gosset–König's result that a *constant-depth* quantum circuit can solve a puzzle (2D-HLF) that classical constant-depth circuits provably cannot, *as the problem grows*. We ran that circuit on silicon: it solved the instance at 90% validity and — the un-fakeable part — covered the full set of valid answers evenly, which a fixed classical mimic can't. But we say the quiet part out loud: at the small size flown, **a laptop also solves this instantly**; the theorem's advantage is asymptotic, so what ran here is the *apparatus of the theorem*, not a raw speed-up and not an on-chip proof of the class separation. It held up through the ninth size we tried.

- **The certified-randomness trust ladder** (F115/F116/F117): the payoff of a quantum-nonlocality test is *private random numbers nobody could have predicted* — but how many you may honestly claim depends on how much of your own apparatus you're forced to trust. We climbed the ladder rung by rung and *corrected our own scope in public*: the fully-paranoid "trust nothing" bits were **quarantined**, because the required no-signaling condition isn't met on a single chip (claiming them would have been an overreach). The witness itself held at 53σ (F115), a middle-rung steering certificate at 96σ (F116), and the capstone (F117) delivered a real number — **0.65 private random bits per use** — at the one rung a single chip genuinely holds, with a small **+0.006 method bias disclosed** as the true limiting factor rather than hidden behind the big statistical margin.

- **Spending the cold branch** (F118): back in F86 the switch acted as a refrigerator, splitting a qubit into a hot branch and a cold branch — but the cold had only ever been *measured*, never *used*. This time we spent it: the cold output was handed off (via a SWAP) onto a *separate* data qubit that was never part of the fridge, resetting it to **0.21 — below the 0.25 "bath" floor**, colder than any ordinary definite-order process could reach on the same baths, certified at **5σ**. The honest scope: this beats a *definite-order* reset, **not** the chip's own everyday fast reset (~0.01) — it's a proof-of-principle that the cold is a real, transferable resource, one modest step past merely reading it. And the honest arc is the best part: the *first* attempt graded **NO-TEST** because a quality-check sentinel came in under its pre-set bar — a bar we'd set too optimistically. The disciplined re-fly changed *exactly one* pre-registered number, re-derived from the measured hardware rather than from a hopeful guess, ran a fresh job, and won cleanly — and the win clears even the *older, stricter* precedent bar, so it doesn't lean on the loosened one. Nor is keeping the cold outcome cherry-picking: under a definite order there simply *is* no cold subset to select, so keeping it *is* the fingerprint of the effect, not a thumb on the scale.

Findings F102–F118, every one pre-registered, every miss in the record — the same discipline, now stretched across three chips and a working refrigerator.

---

## 22. The July "Star Trek" chapter: logical qubits, a network that computes, weird matter, and time itself (plain English)

After the games and the refrigerator, the campaign's second half aimed higher — at four things that sound like science fiction. Same rules as always: guess the result in writing *before* the chip runs, keep every miss.

- **Error correction that finally helps.** Early on we found the discouraging result that textbook error correction *added* more noise than it removed on this chip (Finding 06). This chapter flipped it: using a small "error-**detecting**" code (call it a shield of 4 physical qubits wrapped around 2 logical ones), we built the campaign's **first logical qubits whose operations beat the bare machine** — we entangled two shielded logical qubits so they outperformed an unshielded pair (57σ), teleported a logical qubit from one shield to another (98–99% fidelity), made two shields violate a Bell inequality *as logical qubits* (29.7σ), and even entangled two logical qubits that never shared a gate, through a relay (the "Federation," 21.8σ). **Honest scope:** this is error *detection* (we throw away the runs where the shield catches an error), not full fault-tolerant error *correction* — a real "the encoding helps now" result, not a claim that we've crossed the fault-tolerance threshold.

- **A quantum network that actually computes.** We'd earlier built the *pieces* of a quantum internet (send, route, purify, carry). Here we snapped them together into applications: a **distributed computer** that runs a real algorithm (Bernstein–Vazirani) split across a *cut* — one half holds the data, the other the question, and the joined machine still spits out the right hidden answer (67–141σ) — and a **nonlocal gate**, an operation applied *between two qubits that never touched*, using one shared entangled pair and a classical phone call. We also measured the "tax" that stacking these operations charges, took it apart into named pieces, and **cured the biggest one** with a single well-placed pulse. Plus: secret keys sent through **untrusted relay stations**, certified by physics rather than trust.

- **Genuinely weird states of matter, on a chip.** Four different ways *order survives where it "should" dissolve into chaos*: a **time crystal** (a system that ticks at half the rhythm you drive it, and refuses to drift when you detune the drive — "a clock nothing set"); a **topological edge mode** where order lives *only at the boundary* while the middle goes to mush; **anyons** (particles that are neither the everyday two kinds — braiding one around another flips its sign, the −1 we measured at 50σ); and **quantum many-body scars** — a special starting state that *refuses to forget*, reviving its pattern after it should have thermalized, and doing so more strongly than every one of 55 ordinary starting states. We even mapped *where our cleanup tools stop working*: a careful check showed that beyond a certain circuit depth, the standard "extrapolate the noise away" trick simply can't recover the signal — a useful, honest boundary on what error mitigation can do.

- **The delayed-choice eraser and the physics of time.** The eraser: a coin flipped *after* a qubit is already measured decides whether that already-recorded data shows an interference pattern — and, crucially, **no signal travels** (you can't tell from the qubit alone what the future coin will say; the "spooky" part only appears when you compare notes). Then a whole "time quartet": entangling two qubits **whose lifetimes don't overlap** (the first is measured and gone before the second is even created, yet they test as entangled, 40σ); building a tiny "universe where time is optional" in which time *emerges* from entanglement with a clock; a **Leggett–Garg** test showing a qubit was in *no definite state between two glances* (24σ); a **Wigner's-friend** test showing two observers' recorded facts aren't jointly absolute until copied out (20σ); and **energy teleportation** — a purely informational message that lets a distant party extract energy locally (9.8σ), certified as an *information* effect because the only thing that changes is whether they listen to the message.

The through-line of the whole second half is one methodological lesson, learned the hard way over and over: **your yardstick must be independent of the thing you're measuring.** A control that shares the effect's cost, an estimator that flatters the number, a baseline borrowed from different qubits, a "typical" state cherry-picked to look worst, a normalizer computed from the very data it's normalizing — each one quietly manufactures a result, and each was caught (usually by a review step *before* the chip ran) and fixed. That discipline is why the wins in this chapter are trustworthy and the failures are all still in the record.

Full per-experiment index of this chapter (wins and nulls): **[campaign arcs since Exp147](docs/campaign-arcs-since-exp147-ember-c4207.md)**.

---

## 23. Teaching the chip to heal itself — and to run *anything* (plain English)

The shield in the last chapter could only ever *detect* an error and throw that run in the bin — like a proofreader who, spotting one typo, shreds the whole page. Useful, but you can't build a book that way. This chapter taught the chip the harder trick: **find which qubit went wrong and fix it, keeping the page.** Each step was a wall the previous result put up — and the whole point is that we kept thinking *past* the walls instead of stopping at them. **If we'd stopped at the first wall, none of the rest would exist.**

- **A code that heals instead of discards.** We built the smallest genuinely *correcting* codes: one that fixes a "bit-flip," one that fixes a "phase-flip," and then the 9-qubit Shor code that fixes *any* single-qubit error at once — the first codes in the campaign that repair damage rather than just flag it.

- **Finding the error without looking at the answer.** Here's the beautiful part. To fix a quantum error you'd think you must *look* at the qubit — but looking destroys the quantum-ness. The trick: you don't ask the three copies "what do you say?", you ask "**do you still agree with each other?**" That question reveals *which* copy slipped without revealing the secret they hold — so a quantum superposition **survives the check** (we measured it staying alive at 55%, where a straight look flattened it to zero). Then a classically-controlled nudge repairs it, live, in one pass.

- **Doing it over and over — and pulling ahead.** We ran that heal-loop round after round against an identical circuit that does everything *except* apply the fix. The corrected qubit stayed alive longer, and its lead **grew** with every round — the whole promise of fault tolerance in one picture: not a qubit that never errs, but one that *forgets its errors as fast as it makes them.*

- **The one magic gate that makes a computer universal.** A quantum computer needs one special "awkward" gate (the "T gate") to be able to run *anything* — and a hard theorem says you can't do it the safe, easy way. The fault-tolerant workaround is gorgeous: you brew a little "magic" state off to the side where it's cheap to throw away, and then *spend* it — teleporting only its *effect* onto the qubit you care about. We did that on the chip: the magic landed on a qubit we never touched, at a value no ordinary ("stabilizer") state is allowed to sit at. And then we showed the surrounding program can *steer* that magic to a chosen target — which means **the shielded computer's toolkit is now complete: in principle it can run any quantum program.**

**The honest scope (and it matters):** this is the *mechanism* of universal, self-healing quantum computing — the pieces, wired up and working — **not** a claim that we ran something a laptop can't, and **not** full below-the-threshold fault tolerance yet. The codes we healed corrected errors we *put there ourselves*; the machine's own gates still cost more than they save on the hard problems, which stay depth-blocked on today's chips.

**And the negatives taught as much as the wins** — the Creator's standing note, proven again. The sharpest lesson came from a *failure*: we measured how much longer a self-healing qubit lives, got a modest number... and discovered that the *same qubits* two hours earlier had healed **four times better**. Nothing changed but the chip's mood — its calibration had drifted. The lesson is permanent: **a fault-tolerance score is a weather report, not a constant** — never quote one without saying what day it was. Seven wins, seven honest misses, each a rule we now carry forward. Full synthesis: **[Horizons 6 — The Living Ship](docs/star-trek-horizons-6-the-living-ship-whisper-c4923.md)**.
