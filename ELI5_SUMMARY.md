# What We Found On a Real Quantum Computer (In Plain English)

*A shareable, jargon-free summary of the 22-experiment characterization of IBM's Heron-r2 quantum chip (`ibm_marrakesh`, May 2026). For the technical version with job IDs and source citations, see [`README.md`](README.md).*

---

## 30-Second Version

An AI-agent network ran **22 experiments on a real IBM quantum computer** — a 156-qubit chip, not a simulator — using a strict budget of 600 seconds of actual quantum-computer time. We tested whether the standard quantum-computing tricks people talk about actually work on real hardware.

**They mostly don't. But a few do, and one approach hits chemistry-grade accuracy on a real molecule.**

The chip is **bounded** (there are walls today's algorithms can't pass), but those bounds are **knowable**, and inside them there's **real, usable quantum value** — if you respect the hardware instead of pretending it's perfect.

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

## The Bigger Picture (60 seconds)

There are three things people commonly believe about quantum computers that this campaign **refines**:

1. **"Quantum computers are basically classical computers with extra speed."** No — they have entirely different cost structures. On *this* chip, *width is cheap* and *depth is the wall.* Algorithms designed assuming classical-style cost trade-offs (especially deep Grover-type search) hit a hard ceiling that no amount of software can move.

2. **"Software error mitigation will smooth over hardware noise."** Mostly false on this generation. Four canonical mitigation techniques all *degraded* signal; the chip's natural day-to-day wobble dwarfs anything the tricks could fix. The real path forward is **hardware-aware compilation** (pinning the compiler's choices, choosing the chip's easy measurement direction, keeping circuits short).

3. **"Today's quantum computers can't do anything useful."** Also false. When you respect what the hardware is genuinely good at (shallow circuits, hybrid quantum-classical algorithms, X-basis measurements), you can hit **chemistry-grade accuracy on real molecules** and **production-grade precision on quantum amplitude estimation**. Useful science is happening right now, inside the hardware's actual constraints.

---

## Why You Should Trust This

- **Every single number** in this report traces back to a specific IBM Quantum job ID (a permanent record on IBM's servers), a calibration date, and a Python script. The full inventory is in [`experiments/job-manifest.md`](experiments/job-manifest.md).
- **Pre-registration discipline**: every experiment defined falsifiable pass/fail criteria *before* the job ran. Failed pre-regs are reported as honestly as passed ones — the campaign treats "the data refuted our hypothesis" as a first-class result, not a failure to hide.
- **No simulators, no extrapolations**: all 22 experiments ran on physical quantum hardware (`ibm_marrakesh`, a 156-qubit Heron-r2 chip).
- **Honest scope**: these findings describe **this generation** of superconducting NISQ hardware. They are not claims about the long-term ceiling of quantum computing. The methodology generalizes; the absolute numbers may not.

---

## What This Means For You

**If you're a quantum-algorithm designer**: read [`README.md`](README.md) section "Next Steps — What Can Be Done Now." The 7 actionable items there will save you weeks of dead-end engineering.

**If you're a researcher**: the 7 open research questions in that same section are the next campaign's targets.

**If you're a curious technologist**: the chip is real, it works, it's bounded, and the bounds are knowable. The popular narrative ("quantum is magic" / "quantum is hype") is wrong on both ends. The truth is more interesting: it's *real engineering*, with real trade-offs, and the trade-offs are now measured.

**If you're a science journalist or educator**: feel free to use this document directly. Citation: link to this repo (`github.com/mblakemore/quantum`) and reference the IBM Quantum job IDs for any specific number.

---

*Full technical version: [`README.md`](README.md). Per-finding deep dives: [`findings/`](findings/). Reproducible figures: [`scripts/generate_figures.py`](scripts/generate_figures.py). Sources: [`sources/references.md`](sources/references.md).*
