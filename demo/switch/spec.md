# The order of events, put into superposition — and witnessed on silicon

`Findings F73–F77 (headline F75)`  ·  `Experiment Quantum-switch causal-order witness`  ·  `Backend ibm_marrakesh + ibm_kingston (Heron r2)`  ·  `Job d939bmooamcc73dbv9b0 (F75)`

> **✓ WITNESS FIRES ON HARDWARE — W = +1.781 (F75) · loophole closed at ≥72σ (F77)**

Full Specification Sheet

This sheet is the source-of-truth specification behind the interactive exhibit. Every number on the exhibit page is drawn from the pre-registered switch runs on IBM's Heron-r2 processors — measured, not modeled (the only fitted object is the `2·cos(φ/2)` line, which the measurements confirmed). The finding chain runs simulation → hardware → adversarial control: **F73** (hardest classical adversary, sim) → **F74** (continuous law, sim) → **F75** (fires on real silicon) → **F76** (cross-device cosine law) → **F77** (classical-mixture loophole closed same-device, drift-free).

## 1 · The idea, in plain language

Normally two operations happen in **some** order: A then B, or B then A. The **quantum switch** puts a **control qubit** in charge of that order and leaves it in superposition — so both orders run **coherently at once**. If the control stays coherent, reading it out tells you whether the two operations **cared** about their order. A classical process that merely flips a coin to pick an order **cannot** produce that readout.

> **The witness**
> Measure the control in the X basis. `DISC = ⟨X_c⟩commute − ⟨X_c⟩anticommute` — the difference in the control's reading when the two target operations commute vs anticommute. A coherent switch gives `≈ +2`; any classical mixture of definite orders gives `≈ 0`. That gap is the proof that the order-coherence is a real, measurable resource.

**Scope up front:** ibm_marrakesh is a fixed-causal-order chip. The switch is realized by **controlled routing** on a definite-order circuit — an operational **witness of order-coherence**, not a claim that the hardware itself has an indefinite past. See §5.

## 2 · What we measure — and the continuous dial

The exhibit's dial applies a partial controlled-rotation that copies "which order" into an untraced ancilla, dephasing the control's order-basis coherence by a factor `cos(φ/2)`. So the witness should scale as `DISC(φ) = 2·cos(φ/2)`: `φ = 0` is the fully coherent switch, `φ = π` is a complete which-order copy ≡ the classical 50/50 mixture. **F74** derived this law in simulation (max residual `0.0195`); **F76** confirmed it on **ibm_kingston** at Pearson `0.9992`.

The mechanism gauge on the exhibit shows the real per-circuit control readouts from **ibm_marrakesh** (F75): in the coherent switch the control swings from `+0.865` (commute) to `−0.905` (anticommute) — it has read that order matters. In the definite-order spectator it barely moves (`+0.864` vs `+0.874`) — order-blind, exactly the classical limitation.

## 3 · Pre-registered gates

The decision rules were frozen before flight; F75 reports all three pre-registered gates PASS.

- **F75** — Witness above the drift bar: `W = +1.781` on ibm_marrakesh, **~25×** the `±0.07` drift bar — **all 3 pre-registered gates** PASS.
- **F76** — Cosine law on a second device: Pearson `0.9992`, perfectly monotone (ibm_kingston); the `φ=π` endpoint doubles as the classical mixture and reads **inert**. CONFIRMED.
- **F77** — Loophole closed, one calibration window: `DISC_switch +1.900` vs `DISC_mixture +0.035` (inert) ⇒ `W₂ = +1.865`, **≥72σ**. PASS.

F77 is the load-bearing control: the skeptic's best objection is that a classical process which **randomly picks** order B·A or A·B also has access to the commutator. So the real test is switch vs a genuine **classical mixture of definite orders** — and the switch fires while both classical controls stay inert.

## 4 · The measured data

Two threads. First, F77's single-window loophole test on ibm_marrakesh — the switch against its hardest classical adversary:

| arm (F77 · ibm_marrakesh) | DISC | reading |
| --- | --- | --- |
| coherent switch (order superposed) | +1.900 | fires |
| classical mixture (random B·A / A·B) | +0.035 | inert |
| definite order (fixed spectator) | +0.003 | inert |
| headline witness W₂ = switch − mixture | **+1.865** | **≥72σ** |

The depth-26 mixture and the depth-7 definite control are **both** inert despite a 19-layer depth gap — inertness tracks causal separability, not decoherence. Second, F76's continuous cosine law on ibm_kingston, the five measured points against the confirmed `2·cos(φ/2)` line:

| φ (rad) | ideal 2·cos(φ/2) | measured DISC (ibm_kingston) |
| --- | --- | --- |
| 0 | 2.000 | 1.936 |
| π/4 | 1.848 | 1.713 |
| π/2 | 1.414 | 1.353 |
| 3π/4 | 0.765 | 0.718 |
| π (≡ classical mixture) | 0.000 | 0.027 |

The φ=0 point reads a few percent low of the ideal (`+1.936` vs `+2.000`) from hardware amplitude damping; the load-bearing results are the **sign**, the **cosine shape** (Pearson 0.9992), and the ≥72σ separation — all robust to that attenuation.

## 5 · Scope & caveats

- **A causal WITNESS, a lab resource — not a claim about spacetime event-order.** This certifies that a single control qubit can detect that two operations were applied in an **indefinite order** (order-coherence), on a fixed-causal-order chip realized by controlled routing. It is **not** a claim that the hardware's physical past is indefinite, and **not** a claim about the ordering of events in spacetime.
- **Order-coherence, not a speed-up.** The witness reports that the control encodes which order was applied (an interference signature). It is **not** a demonstrated computational or query-complexity advantage of the quantum switch.
- **The shape is the claim, not the amplitude.** Amplitude damping reads DISC a few percent low of ideal (φ=0 measured +1.936 vs +2.000). Sign, cosine shape, and ≥72σ separation are the robust results.
- **Coherence-of-causal-order witness, not a black-box query separation.** F73–F77 query each gate twice; this is a coherence witness, the scope of this family (the game-form and capacity-form bound beats are separate findings, F82/F83).

## 6 · Provenance

- **F75** switch witness · ibm_marrakesh · job `d939bmooamcc73dbv9b0` · W = +1.781
- **F76** continuous cos law · ibm_kingston · job `d93khvl958jc73bt5c2g` · Pearson 0.9992
- **F77** classical-mixture loophole · ibm_marrakesh · job `d93p3cnu62ks73953cvg` · W₂ = +1.865 (≥72σ)
- **F73** (sim) hardest classical adversary: W₂ = +2.00 noiseless / +1.93 under the noise model, mixture arm inert (DISC 0.000) · **F74** (sim) continuous law DISC(φ)=2·cos(φ/2), max residual 0.0195
- **Backends:** ibm_marrakesh & ibm_kingston (both Heron r2, 156 qubits) · **Shots:** 2000–6000/circuit · **Gates frozen** pre-flight, pre-registered
- **Family:** Indefinite causal order — the switch on real silicon; siblings include the causal game (F82) and the zero-capacity channel activation (F83)

---

*Rendered from [`demo/switch/spec.html`](spec.html) — the interactive exhibit is at [`demo/switch/`](index.html). Part of [The Quantum Museum](../).*
