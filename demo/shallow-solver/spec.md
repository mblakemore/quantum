# A circuit too shallow for any classical machine to match

`Finding F113`  ·  `Experiment Exp127hw (BGK 2D-HLF, n=4)`  ·  `Backend ibm_marrakesh (Heron r2)`  ·  `Job d9amnlvu62qs738o8nt0`

> **✓ CONSTANT-DEPTH SOLVER — P(valid) 0.9017, 437.8σ, full coset covered**

Full Specification Sheet

> **Scope — read this first**
> This does **not** prove the complexity separation (QNC⁰ ≠ NC⁰) **on the chip**. That separation is **asymptotic** — it lives in the limit of large `n`, and the **theorem** carries the asymptotics. What the hardware certifies is a concrete instance: a **constant-depth** quantum circuit that solves the `n=4` problem at **90% fidelity**, covering the **whole** solution set, in **O(1) logical depth**. It is the complement to F54's deep-circuit wall — the campaign's one computational-genre result, scoped exactly.

## 1 · The idea, in plain language

**Depth** is how many layers of gates a circuit has, one after another. A **constant-depth** (shallow) circuit has a **fixed** number of layers no matter how big the problem grows — every gate fires in a few parallel rounds. Bravyi, Gosset & König (2018) proved something remarkable: there is a problem a **quantum** constant-depth circuit can solve that **no classical** constant-depth circuit can — and the proof needs **no unproven assumptions** (unlike "P ≠ NP"). It is one of the few **unconditional** quantum advantages known.

The problem is the **2D Hidden Linear Function**: given a quadratic puzzle laid out on a grid, find a hidden linear rule. It has **many equally-valid answers** — a whole **solution set (a coset)** — and a good solver must be able to produce **any** of them.

## 2 · The un-fakeable test — coverage

> **Why "how often is it valid" is not enough**
> A cheap classical mimic could just **memorize one** valid answer and output it every time — scoring 100% on "is the answer valid?" while doing none of the actual computation. So the real gate is **coverage**: the solver must spread its answers across the **entire** solution set. A one-answer mimic has **zero** probability on the other valid answers and **fails**. Only a genuine solver covers the coset.

## 3 · The measured result

At `n=4` the coset has **four** valid answers out of 16 possible outputs (uniform-random floor = 4/16 = **0.25**). The quantum solver:

| quantity | value | note |
| --- | --- | --- |
| P(valid answer) | **0.9017 ± 0.0015** | 437.8σ over the 0.25 floor |
| valid z = 0001 | 0.2237 | the four cover the  
coset near-uniformly |
| valid z = 1000 | 0.2229 |  |
| valid z = 0110 | 0.2308 |  |
| valid z = 1111 | 0.2243 |  |
| min valid (coverage) | **0.2229** | the un-fakeable W3 gate |
| hardware depth | 23 | 10 routed CZ · O(1) logical depth |

Pre-filed success band `[0.82, 0.93]` — **hit at the top**. Sentinels 0.985 / 0.957.

## 4 · Pre-registered gates (frozen before flight)

- **W1_SOLVER** — P(valid) > the uniform floor 0.25 by ≫5·SE. PASS (0.9017, 437.8σ).
- **W2_MAJORITY** — A majority of shots land on a valid answer. PASS (90%).
- **W3_COVERAGE** — **the un-fakeable one:** every valid answer gets real weight (a one-answer mimic fails). PASS (min 0.2229).
- **G_SENT** — Readout sentinels healthy. PASS (0.985 / 0.957).

## 5 · The through-line — hardness is contextuality-flavored (theory-associated)

> **Contextuality → computational separation (in theory)**
> Why **can't** a classical shallow circuit keep up *as the problem grows*? The hardness is **contextuality-flavored** — the grid's Peres–Mermin parity structure, the same resource family the museum certifies at 196σ (**F106**). One caution about the strength of that link: the magic-square gadget lives in the **BGKT-2020** noise-robust construction, a *different* circuit family; **the circuit we flew is the plain BGK-2018 solver**, and F106 certified the magic-square game in a **separate experiment**. So the no-go (contextuality) and the computational advantage are the **same resource in theory** — an association argued, **not a composition demonstrated on one chip**. Not "closed end to end": the two are linked by the theorem, not by a measured on-silicon chain.

## 6 · Scope & caveats

- **Asymptotic separation, not on-chip.** (See the fence above.) The n=4 result is a **fidelity** demonstration of the solver; the classical impossibility is a theorem about the large-n limit.
- **A fidelity number, not a beaten bound.** At n=4 there is no finite classical bound being crossed — 0.9017 measures how well the constant-depth circuit runs, and coverage proves it isn't a one-answer trick.
- **Textbook priors credited.** Bravyi–Gosset–König (2018) for the separation; BGKT (2020) for the noise-robust / contextuality construction. The contribution is the frozen, coverage-gated hardware run.

## 7 · Provenance

- **Grade file:** `results/exp127hw_hw_results.json` · **Job:** d9amnlvu62qs738o8nt0
- **Groundwork:** `experiments/exp127-bgk-shallow-advantage-groundwork-whisper-c4666.md` · sim finding `…-sim-finding-whisper-c4673.md`
- **Backend:** ibm_marrakesh (Heron r2) · **Depth:** 23 hardware / O(1) logical · **10 routed CZ**
- **Through-line:** F106 (magic-square contextuality, 196σ) — the inherited hardness · complement to F54 (deep-circuit wall)

---

*Rendered from [`demo/shallow-solver/spec.html`](spec.html) — the interactive exhibit is at [`demo/shallow-solver/`](index.html). Part of [The Quantum Museum](../).*
