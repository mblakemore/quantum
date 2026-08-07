# P-CCM Classical Solver — Build Plan

**Whisper C5021 · substrate claude-fable-5 · Creator directive: "Create a comprehensive plan for
building the solver, revisit the plan for gaps and adding pre-dev planning structure, then build it!"**

Two passes, both kept. **§1–§4 are pass 1** (the plan as I first drew it). **§5 is the gap review**,
**§6 is the revised buildable plan (v2)**, and v2 is what gets built. Pass 1 is retained unedited so
the revision is auditable — the changes between them are the point, not an embarrassment.

---

## 0. WHAT THIS IS FOR, AND THE CORRECTION THAT OPENS IT

> ### ⊘ SCOPE CORRECTION (C5027, 2026-08-07) — READ BEFORE THE SENTENCE BELOW
>
> The opening sentence of this plan defines the classical arm as *"how long would it take a
> classical computer to reproduce what the QPU did."* **That is the baseline my own red-team
> retired fifteen days before I wrote it.**
>
> `docs/exp-hss-race6-REDTEAM-whitebox-break-whisper-c4996.md` (2026-07-23, Creator directive
> C4995, 3/3 court seats) broke the campaign's 476× runtime advantage by showing the planted MM
> problem falls to a classical **41-query linear-structure solve in ~0.25 ms** against a **1,818 s
> simulation floor** — a factor of ~7,000. F121 retired; F120 downgraded to an instrument result.
>
> **A SIMULATION-COST RATIO IS A CEILING ON THE CLASSICAL COST, NOT AN ADVANTAGE.** The binding
> constraint is the best *problem-specific* classical algorithm, and I demonstrated myself that the
> gap between the two can be four orders of magnitude on a problem we designed.
>
> **Nothing technical below is retracted** — every gate, the measured 0.39–0.41 ns/t³ unit, the
> δ-control result and the end-to-end verification all stand exactly as reported, and a measured
> ceiling beats the projection the campaign had. What changes is what the number may be used to
> claim: **any advantage claim built on this solver must run the problem-specific attack FIRST**
> and report the simulation cost as an upper bound a clever algebraist may walk straight past.

The campaign's quantum-advantage claims rest on a **classical arm**: how long would it take a
classical computer to reproduce what the QPU did? Every advantage ratio quoted is a ratio against
that number. Until now the classical arm has been a *projection* built on a cost model. This solver
makes it a *measurement*.

**Correction to C5020, stated first because the whole plan sits on it.** I stopped last cycle saying:

> "the sparsification outputs χ, and χ multiplies every cost figure downstream, where no gate can see it."

That was wrong, and wrong in the direction that matters. The construction (Bravyi–Gosset §V) supplies
a **closed-form fidelity**:

```
|<H^t | L>|^2  =  2^k · nu^(2t) / Z(L)          (Eq 35)
Z(L)           =  SUM_{x in L} 2^(-|x|/2)        (Eq 34)      nu = cos(pi/8)
```

`Z(L)` is exactly computable in O(2^k). So the achieved fidelity of the sparsified decomposition is
not estimated, not bounded — it is **computed exactly, cheaply, at full scale**, and separately
checkable against an explicit statevector at small t. ①b is not the ungateable component. It is the
**best-gated component in the project.** My stopping reason was sound as a policy and false as a fact.

**Second correction — the χ numbers.** I quoted χ(t=80) = 345,901. That is `2^(0.228·80)`, the
*asymptotic scaling with constants dropped*. The construction's actual rank is fixed by Eq 38:

```
k = unique positive integer with   4 >= 2^k · nu^(2t) · delta >= 2
```

| t | nu^-2t | χ = 2^k, δ=0.5 | χ = 2^k, δ=0.1 | exact pairing 2^(t/2) |
|---:|---:|---:|---:|---:|
| 40 | 563 | 4,096 (k=12) | 16,384 (k=14) | 1,048,576 |
| 48 | 2,000 | 8,192 (k=13) | 65,536 (k=16) | 16,777,216 |
| 60 | 13,371 | 65,536 (k=16) | 524,288 (k=19) | 1,073,741,824 |
| **80** | **317,354** | **2,097,152 (k=21)** | **8,388,608 (k=23)** | **1,099,511,627,776** |

So at t=80, δ=0.5 the real rank is **2,097,152 — 6.1× my quoted figure**, and the exact-vs-sparsified
gap is **524,288×**, not 3.2 million×. Both of last night's headline numbers were off, in opposite
directions. The cost consequence (the arm is ~6× more expensive than the 2.1-day figure) is carried
into §4 rather than being buried here.

**Third fact, and the one that makes this tractable.** Each sparsified term is

```
|x~_1 (x) x~_2 (x) ... (x) x~_t>,      x in L,      |0~> = |0>,  |1~> = |+>
```

a **product of |0> and |+>** — the simplest stabilizer states there are — and **all χ coefficients
are equal** (`1/sqrt(2^k Z(L))`). No coefficient bookkeeping, no phases, no normalisation drift. I had
budgeted for a hard construction; the hard part was finding it, not implementing it.

---

## 1. TARGET (pass 1)

> Given a Clifford+T circuit `U` on `n` qubits with `c` Clifford gates and `t` T-gates, and an output
> register `Q_out` of `w` qubits, produce samples `x ~ P~_out` with `||P~_out − P_out||_1 <= eps`.

This is the paper's **second** algorithm (Eq 3), the γ ≈ 0.228 one — the algorithm whose cost model
every advantage ratio in this campaign has been quoting. Cost:

```
tau = O~( w(w+t)(c+t) + w(n+t)^3 + 2^(gamma t) t^3 w^3 eps^-4 )
```

## 2. COMPONENT DAG (pass 1)

```
  (1a) exact magic decomposition        BUILT, gate 10/10        chi = 2^(t/2)
  (1b) sparsified decomposition         Section V, random L      chi = 2^k
        |
  (2)  gadgetization                    T -> Clifford + |A> injection + postselect bit y
        |
  (3)  Clifford propagation             apply V_y to each stabilizer term
        |
  (3b) projection / postselection       <psi|Pi_G|psi>  (shrink already does this)
        |
  (4)  norm estimator                   xi = (d/L) SUM |<theta_i|psi>|^2, median over J
        |
  (5)  conditional bit sampler          sample x bit by bit from P_out(z|x_1..x_{j-1})
```

## 3. PER-COMPONENT SPEC (pass 1)

**①b sparsification.** `sparsify(t, k, rng, tries)` → `(Lbasis (k×t F2), Z, fidelity)`. Sample uniform
k-dim `L ⊆ F₂^t`, compute `Z(L)`, accept if `Z(L) <= (1 + 2^k nu^2t)(1 + δ/2)`, `O(1/δ)` tries.
Gate: Eq 35 vs explicit statevector, t ≤ 12.

**② gadgetization.** T-gate gadget consumes one `|A>`, measures, applies a classically-controlled S.
Replace each measurement outcome by a uniform postselection bit `y_j`; replace the controlled Clifford
by the corresponding uncontrolled one. Gate: gadgetized P_out vs direct statevector, n ≤ 8.

**③ Clifford propagation.** Need `H, S, X, Y, Z, CNOT, CZ` on the `(n,k,h,G,Ḡ,Q,D,J)` standard form.
I have `apply_H` only. Gate: statevector comparison, random Clifford circuits, n ≤ 10.

**④ norm estimator.** `ξ = (2^t/L) Σ|⟨θ_i|ψ⟩|²`, `L = 4ε⁻²`, median over `J = O(log 1/p_f)`.
Gate: ξ vs exact ‖ψ‖², small t.

**⑤ conditional sampler.** Eq 29 bit-by-bit. Gate: empirical distribution vs exact P_out, n ≤ 8.

## 4. COST (pass 1)

At `t = 80`, `χ = 2^21`, measured inner-product cost `0.62 ns` per `t³` unit, 6.76× parallel:

```
per inner product        0.62e-9 * 80^3          = 3.17e-4 s
per estimate (chi terms) 3.17e-4 * 2.10e6        = 665 s
L = 4 eps^-2, eps = 0.1  -> L = 400
J = 5 repeats            -> 2000 estimates       = 1.33e6 s = 15.4 days (1 core)
/ 6.76 parallel                                  = 2.3 days
```

---

# 5. GAP REVIEW

Pass 1 is a component list with gates attached. Re-reading it as something to actually *build*, seven
things are wrong or missing. Five are structural; two are arithmetic.

### GAP 1 — the build order is conceptual, not gate-driven. **(structural, worst one)**

Pass 1 orders components ①→⑤ because that is the order the paper explains them. But ⑤ cannot be
gated until ④ works, ④ cannot be gated until ③ works, and ③ cannot be gated until ② produces
something to propagate. Building in that order means **the first end-to-end check happens last** —
exactly the shape that hides an integration bug behind five green unit gates.

**Fix: build the EXACT path end-to-end first, then swap in the sparsification.** ①a is already built
and exact, so a full pipeline `①a → ② → ③ → ③b → ④` can be checked against a brute-force statevector
at n,t ≤ 10 *before ①b exists*. Then ①b enters a pipeline that is already known-good, and any
discrepancy after the swap is attributable to ①b alone. This inverts pass 1's order and is the single
highest-value change in the review.

### GAP 2 — no uniform stabilizer-state sampler, and pass 1 did not notice. **(structural)**

④'s variance bound comes from `M2 = ‖ψ‖²/d`, `M4 = 2‖ψ‖⁴/(d(d+1))`, which hold because uniform
stabilizer states form a 3-design. The existing `random_state_via_extend` says so in its own docstring:

> *"it does not claim to sample Haar-uniformly over stabilizer states"*

It was written to feed the **timing** harness, where the distribution is irrelevant. Using it in ④
would produce an estimator that runs, returns plausible numbers, and has **no valid error bar** —
a silent failure of exactly the class this campaign keeps getting caught by. Lemma 5 gives the correct
sampler: draw `d ~ P(d) = |S_n^{n-d}| / Σ_m |S_n^m|`, then a uniform `K` of dim `k = n−d`, then uniform
`(Q, D, J)`. This is a **new required component ④a**, absent from pass 1.

### GAP 3 — no interface contract, so components cannot be built or gated independently. **(structural)**

Pass 1 names components but not the objects passed between them. Without fixed signatures and stated
invariants, each gate tests a component against *whatever the neighbouring component happens to
produce*, which is how a shared misconception passes two gates in a row. Contracts must be fixed
**before** building — added as §6.2.

### GAP 4 — no pre-registration. **(structural)**

Every number this solver produces (χ, fidelity, runtime, the advantage ratio) is one I have a stake in.
Pass 1 has no mechanism preventing me from reading a result and deciding afterwards that it is what I
expected. Given this campaign's specific history — `ρ_t = 0.743` matched to the wrong lane, a λ range
invented 2.7× wider than measured, four consecutive mis-called hot-spot shares — the predictions must
be **written down before the code runs**. Added as §6.4.

### GAP 5 — no kill criteria. **(structural)**

Pass 1 has no statement of what would make me stop. Without one, a partially-working solver invites
indefinite fixing. Added as §6.5.

### GAP 6 — the δ the paper's own experiments used does not satisfy its own theory. **(arithmetic)**

Eq 19 requires `|⟨A^t|ψ⟩|² ≥ 1 − ε²/25` for the *sampling* guarantee. The paper's reported runs used
`|⟨A^t|ψ⟩| ≈ 0.81` and `0.69`, i.e. `δ ≈ 0.34` and `0.52`. For δ = 0.34 the theory would only license
`ε ≈ 2.9` — a vacuous bound on an L1 distance that cannot exceed 2. **The paper's own simulations ran
far outside the regime its theorem covers**, relying on structure specific to the chosen bent
functions. So my §4 cost at δ=0.5 is *the paper's practical regime, not its guaranteed one*, and any
advantage ratio quoted from it must say so. Pass 1's cost table silently inherited this.

### GAP 7 — the cost model omits ③, and ③ may not be negligible. **(arithmetic)**

§4 counts only χ inner products. But **③ Clifford propagation runs per term too** — each of the χ
terms must have the full gadgetized Clifford circuit `V_y` applied to it, at `O((n+t)²)` per gate for
`c + O(t)` gates. At the campaign's operating point that is `~6.7e3` per gate × `~1e3` gates ≈ `6.7e6`
operations per term, against an inner product's `~5e5`. **The propagation could dominate the inner
product by an order of magnitude**, and pass 1's cost table does not contain it at all. This is the
same Amdahl error I made four times in one night — a correct mechanism attached to an unmeasured
share — and it is in the plan again. §6.6 handles it by *measuring* rather than projecting.

---

# 6. PLAN v2 — WHAT ACTUALLY GETS BUILT

## 6.1 Build order (gate-driven, per GAP 1)

```
STAGE A   (3) Clifford propagation + (3b) projection      gate: statevector, n<=10
STAGE B   (4a) uniform stabilizer sampler                 gate: chi^2 vs Lemma 5 counts
STAGE C   (4) norm estimator                              gate: xi vs exact ||psi||^2
STAGE D   (2) gadgetization -> EXACT end-to-end P_out     gate: vs brute-force statevector
STAGE E   (1b) sparsification, swapped into the good pipe gate: Eq 35 + fidelity vs statevector
STAGE F   (5) conditional sampler                         gate: empirical L1 vs exact P_out
STAGE G   cost measurement at the real operating point    no gate — this IS the measurement
```

Stages A–D use **①a (exact)**, so the pipeline is verifiable end-to-end before the approximation
enters. Stage E is the swap. This is the inversion GAP 1 called for.

## 6.2 Interface contracts (per GAP 3)

```
Term            = (coeff: complex, state: StabState)          # one stabilizer term
Decomposition   = list[Term]                                  # sum_a z_a |phi_a>, ||sum|| = 1

(1a) exact_decomposition(t)            -> Decomposition        chi = 2^(t/2)
(1b) sparsify(t, k, rng, tries)        -> (Lbasis, Z, fid)
     decomposition_from_L(Lbasis, t)   -> Decomposition        chi = 2^k, equal coeffs

(3)  apply_clifford(st, gate, qubits)  -> StabState (in place) # H,S,X,Y,Z,CNOT,CZ
     INVARIANT: st.check_invariants() holds after every gate
     INVARIANT: st.statevector() equals gate @ old_statevector  (n <= 10 only)

(3b) project(st, pauli, outcome)       -> (StabState | None, p) # p in {0, 1/2, 1}
(4a) random_stabilizer_state(n, rng)   -> StabState             # UNIFORM over S_n
(4)  estimate_norm2(decomp, eps, p_f)  -> (xi, halfwidth)
(2)  gadgetize(circuit)                -> (V_y builder, t, postselect_bits)
(5)  sample(circuit, Qout, eps)        -> x in {0,1}^w
```

## 6.3 Correctness gates — oracle, scale, and the silent-failure shape

| # | oracle | scale | passes if | **what a silent failure looks like** |
|---|---|---|---|---|
| A | explicit 2ⁿ statevector | n ≤ 10, 200 random circuits | max abs amp err < 1e-10 | a gate correct up to global phase — invisible in ⟨·⟩, fatal in a **sum** of terms |
| B | Lemma 5 closed-form counts | n ≤ 6, χ² over 200k draws | p > 0.01 | plausible-looking states, wrong measure, **no valid error bar** on ④ |
| C | exact ‖ψ‖² | t ≤ 10 | ‖ξ/‖ψ‖²−1‖ < 3ε | correct mean, wrong variance → confidence interval a lie |
| D | brute-force P_out | n,t ≤ 8 | max rel err < 1e-9 | postselection bookkeeping off by a factor 2^t — **exactly cancels** in ratios |
| E | Eq 35 vs statevector | t ≤ 12 | agree to 1e-12 | fidelity right, χ wrong → every runtime downstream wrong |
| F | exact P_out, L1 | n ≤ 8, 200k samples | L1 < 2ε | bias below sampling noise at the gate's scale |

**Gate A's global-phase note is the load-bearing one.** A propagation routine that is right up to a
per-term phase passes any single-term check and destroys a linear combination. It must be gated on
**amplitudes, not probabilities**.

## 6.4 Pre-registration — written before any code runs (per GAP 4)

| # | prediction | resolves at |
|---|---|---|
| P1 | ①b achieves fidelity ≥ 1−δ within 10 random-L tries at δ=0.5, for t ∈ {20,40,60,80} | Stage E |
| P2 | Eq 35 agrees with the explicit statevector to < 1e-12 at t ≤ 12 | Stage E |
| P3 | **③ Clifford propagation costs MORE per term than the inner product** at n=40,t=80 (GAP 7) | Stage G |
| P4 | the measured t=80 arm lands in **10–40 days** single-core (§4 said 15.4, GAP 7 says higher) | Stage G |
| P5 | `random_state_via_extend` **fails** the Lemma-5 χ² test (it does not claim uniformity) | Stage B |
| P6 | the exact end-to-end pipeline passes gate D at n,t ≤ 8 without needing ①b | Stage D |

Predictions P3 and P5 are ones I expect to be *right about being wrong* — P5 says my existing tool is
unfit and P3 says my own cost model omits the dominant term. Registering those before measuring is the
point of registering at all.

## 6.5 Kill criteria (per GAP 5)

- **Any gate A–F fails and is not fixed within the stage** → stop, report the failure, do not proceed
  to a stage that depends on it. A red gate is a result, not an obstacle.
- **Stage G measures the t=80 arm at > 1 year single-core** → the arm is not runnable as scoped; report
  the measured number and re-scope t, not the method.
- **③ turns out to need a representation change** (i.e. the standard form cannot carry a general
  Clifford) → stop and say so; that is a real finding about the representation, not a bug to grind on.
- **Running past a red gate to preserve a narrative** is the failure mode this list exists to prevent.

## 6.6 Cost measurement, not projection (per GAP 7)

Stage G measures, at the real operating point and with a stopwatch:
`t_propagate` per term, `t_inner` per term, `t_Z(L)`, and the achieved fidelity — then reports the arm
as `χ · (t_propagate + L·J·t_inner)` **with the measured split shown**, so the dominant term is visible
rather than assumed. No runtime is quoted from a model when it can be timed.

## 6.7 Definition of done

Done = **Stage D green** (an exact, statevector-verified end-to-end P_out) **plus Stage E green** (the
sparsification swapped in, fidelity confirmed by two independent routes) **plus Stage G reported**
(the arm, measured, with its cost split). Stage F (sampling) is desirable and explicitly *not* required
for the classical-arm number, which needs P_out estimation, not sampling.

**Anything not reached is named as not reached.**

---

# 7. BUILD RESULTS — C5021

## 7.1 What was built and gated

| stage | component | file | gates |
|---|---|---|---|
| E | ①b sparsification | `tools/magic_sparsify.py` | **12/12** |
| B | ④a uniform stabilizer sampler (Lemma 5) | `tools/stabilizer_estimator.py` | **12/12** |
| C | ④ norm estimator + exact O(χ²) oracle | `tools/stabilizer_estimator.py` | (same run) |
| G | arm measurement | `tools/solver_arm_measure.py` | njit == reference at t=40, 80 |

**Not built, and named as not reached: ② gadgetization, ⑤ conditional sampler, and therefore
Stage D (the exact end-to-end P_out). By §6.7 this build is NOT done.** What exists is a verified
decomposition, a verified estimator, and a measured arm — not a solver that takes a circuit in.

## 7.2 Pre-registration outcomes

| # | prediction | outcome |
|---|---|---|
| P1 | fidelity ≥ 1−δ within 10 tries at δ=0.5, t ∈ {20,40,60,80} | **CONFIRMED, beaten** — 1 try each; fidelity 0.88–0.93 vs the paper's own 0.81 / 0.69 |
| P2 | Eq 35 agrees with the statevector to < 1e-12 at t ≤ 12 | **CONFIRMED** — max err 2.7e-15 |
| P3 | ③ Clifford propagation costs more per term than the inner product | **VOID — the premise was wrong.** Eq 3's `(n+t)³` is additive, not per-term; the Clifford is propagated once in the Heisenberg picture (Eq 28). GAP 7 does not exist |
| P4 | measured t=80 arm lands in 10–40 days single-core | **REFUTED at first measurement (324 d), CONFIRMED after the fix (22.3 d)** — see §7.3 |
| P5 | `random_state_via_extend` fails the Lemma-5 χ² test | **CONFIRMED** — χ² = 12,533 on dof 479, p = 0. The Lemma-5 sampler passes at p = 0.636 |
| P6 | exact pipeline passes gate D at n,t ≤ 8 | **CONFIRMED (C5022)** — 124 (circuit, y) cases at n ≤ 5, t ≤ 4, max err 3.3e-16 |

## 7.3 The defect the pre-registration caught

The first arm measurement returned **324 days** against a registered band of 10–40. Because the
prediction was written down first, that gap read as *"find the bug"* rather than as *"the answer is
bigger than I thought"* — and there was a bug. The `ns per t³ unit` column was not flat:

```
            BEFORE                       AFTER
 t     t_inner     ns/t^3        t_inner     ns/t^3
40    229.5 us      3.586        28.8 us      0.450
60   1074.0 us      4.972        85.4 us      0.395
80   3032.6 us      5.923       207.2 us      0.405     <- flat = the complexity is right
```

`inner_product_njit` computed `Jn = Rm J2w Rmᵀ` as four nested loops over `k, k, k2, k2` — **O(t⁴)**,
a full factor of `t` above the O(t³) the paper specifies. Factoring it into two sequential matrix
products restores O(t³). Re-gated **75/75 against the reference** at t ∈ {6,10,20,40,80} before any
new timing was emitted.

**Effect: 14.6× on the inner product at t=80; the arm falls from 324 days to 22.3 days single-core
(3.3 days at the measured 6.76× parallel).** Fitted complexity exponent **3.72 → 3.14** over
t ≥ 50 (2.64 over the full range, where small-t points are fixed-overhead-dominated).

This is the **third** instance of one failure class in two cycles: an algorithmic defect that
compilation, vectorisation, GPU offload and parallelism all faithfully preserve, because each of
those makes the *wrong amount of work* go faster. C5020 found the dense-vs-sparse add-row (20×
slower than a 2016 MATLAB); this is the same shape one level up. **The detector is not profiling —
profiling showed this block as ordinary. The detector is checking that measured scaling matches the
complexity the source specifies.** Flatness of a `time / t^expected` column is a cheap, general
defect test and should be standing practice for any timed kernel in this campaign.

It also retires a figure I have been quoting: **"0.62 ns per t³ unit, 6.7× faster than the paper's
2016 MATLAB"** was measured at a small `t` where the quartic term had not yet taken over. The correct
figure is **0.39–0.41 ns/unit in the t ≥ 50 operating region** — better than 0.62, but it was right
by accident and would have been badly wrong extrapolated upward, which is exactly what the arm
estimate did.

## 7.4 The measured arm

`T_arm = χ · [ 80·t_shrink + L·J·t_inner ]`, at ε=0.1, p_f=0.05 → L=400, J=11; δ=0.5.

| t | χ = 2^k | fidelity | projections | inner products | 1 core | ×6.76 |
|---:|---:|---:|---:|---:|---:|---:|
| 40 | 4,096 | 0.9431 | 7 s | 519 s | 8.8 min | 78 s |
| 60 | 65,536 | 0.9087 | 238 s | 24,626 s | 6.9 h | 61 min |
| **80** | **2,097,152** | **0.9321** | 13,209 s | 1,911,703 s | **22.3 d** | **3.3 d** |

Cost split at t=80: **99.3% inner products, 0.7% projections.** Shown rather than assumed.

**Scope, stated because it bounds every ratio taken from this table:** this is the per-probability
cost of the sampling algorithm's dominant term. It excludes the additive `O((n+t)³)` Clifford
propagation (amortised, per Eq 3) and it is quoted at **δ = 0.5 — the paper's practical regime, not
its guaranteed one** (GAP 6: Eq 19 needs fidelity² ≥ 1 − ε²/25, which δ=0.5 does not meet; the
paper's own published runs did not meet it either).

---

# 8. C5022 — COMPONENT ② GADGETIZATION

`tools/gadgetize.py`, **33/33 gates.**

## 8.1 What it does

```
T gate                 ->  CNOT(data, magic_j) + S^{y_j} on data,  magic_j postselected onto y_j
measurement outcome    ->  a uniform postselection bit y_j
the whole Clifford V_y ->  propagated ONCE in the Heisenberg picture onto the t magic qubits
                           giving  P^y_out(x) = 2^-u <psi|Pi_G|psi> / 2^-v <psi|Pi_H|psi>   [Eq 28]
```

Postselection is deferred to the end of the circuit, which is legitimate because nothing touches
magic qubit `n+j` after its CNOT. The reduction is: `Pi_S' = 2^-r Σ_{P∈S'} P`; `<0^n|P_A|0^n>`
vanishes unless `P_A` is Z-type and equals **+1** when it is (both `<0|I|0>` and `<0|Z|0>` are 1),
so the surviving subgroup is the **null space of the generators' X-parts on the data register**,
and `u = r − dim(null)`.

## 8.2 The gates

| # | check | result |
|---|---|---|
| G1 | every conjugation rule vs explicit matrices, **all** Paulis, m ≤ 3 | 25 rules × up to 256 Paulis, 0 mismatches |
| G2 | the T gadget really implements T, both outcomes, phase included | 100 branches, 0 bad |
| **G3** | **`P^y_out(x)` == brute-force `P_out(x)` for EVERY y** (Eq 18) | **124 cases, max err 3.3e-16** |
| G4 | the denominator is the postselection weight, `p_y = 2^-t` | max err 1.1e-16 |
| G5 | `Σ_x P^y_out(x) = 1` | exact |
| G6 | **①b swapped in** — sparsified state end-to-end vs its own bound | 68 cases, max err **0.109** vs `√δ = 0.383` |

**G3 is the load-bearing one.** Eq 18 says the final state of the n computational qubits is
`U|0^n⟩` *regardless of y*, so with the exact magic state every `y` must reproduce `P_out(x)`
exactly. That single equality exercises the gadget, all 25 conjugation rules, the null-space
reduction and the exponent `u` at once — a phase error anywhere breaks it.

**G6 removes the last reason to need per-term Cliffords.** Since `|A⟩ = e^{iπ/8} H S† |H⟩`, the
frame change `(HS†)^⊗t` folds into `V_y`, so the decomposition stays in the H frame where ①b
produces it. Nothing is applied to the terms.

## 8.3 Where this leaves the solver

**The mathematics of the full pipeline is now verified end to end.** Circuit in → `(G, H, u, v)` →
sparsified magic state → `P_out(x)`, agreeing with brute force exactly in the exact case and inside
its own exactly-known error bound in the approximate case.

**What is still missing is the part that makes it worth running.** `<psi|Pi_G|psi>` is evaluated
here with explicit `2^t` matrices. Doing it on the stabilizer standard form needs a **general-Pauli
projection of a stabilizer state — component ③**, which does not exist: the kernel's `shrink`
handles Z-type projections only, and `apply_H` is a stub that raises. Until ③ exists the solver
runs only at sizes where a statevector would have done, which is exactly the regime where
verification is easy and value is zero.

**③ is now the single remaining blocker,** and it is a well-posed one: extend `shrink` to a general
Pauli `i^k X^α Z^β`, where the `Z^β` part is a linear phase update (`Q += 4(β·h)`, `D_a += 4(β·g_a)`)
and the `X^α` part is a shift of the affine space — both cheap; the work is the case analysis when
the projection reduces the dimension.

---

# 9. C5023 — COMPONENT ③, AND THE SOLVER CLOSED

`tools/pauli_project.py` (**4/4**) and `tools/solver.py` (**6/6**).

## 9.1 ③ — general-Pauli projection

`(I + i^κ X^α Z^β)/2` on the standard form. The `Z^β` part is an affine phase update (4·XOR is
linear mod 8); the `X^α` part is *just* `h ^= α`. Everything else is the case split on whether
`α ∈ L(K)`:

| case | condition | effect | cost |
|---|---|---|---|
| **B** | `α ∉ L(K)` | dimension **grows** by 1, new basis vector `α`, `D_{k+1} = 2κ+4(β·h)`, `J_{a,k+1} = 4(β·g_a)` | O(n) |
| **A-i** | `α ∈ L(K)`, `r₀ ≡ 0 mod 4` | `r ∈ {0,4}` → an affine hyperplane → **reuses the gated `shrink`** | O(k²) |
| **A-ii** | `α ∈ L(K)`, `r₀ ≡ 2 mod 4` | `r ∈ {2,6}` → dimension unchanged, **phases only** | O(k²) |

The `r mod 4` argument is what makes the split exhaustive: for the result to be a stabilizer state
the amplitude *modulus* `|1 + ω^r|` must be constant on the support, which forces every `r_a ∈ {0,4}`
and leaves exactly these branches. A constant `r ∈ {2,6}` would give `⟨φ|P|φ⟩ = ±i`, impossible for
Hermitian `P` — asserted, not assumed. A-i deliberately calls the existing `shrink` rather than
reimplementing it: that code is already inside the 81/81 reference gate.

**Gates: H1** amplitudes vs explicit `(I+P)/2` — 560 cases, max err **1.6e-16**, with **every branch
exercised** (grow 261, shrink 87, phase 85, same 64, empty 63); **H2** idempotence, exact; **H3**
group projection vs an explicit product of projectors, 89 commuting groups, 1.3e-16.

## 9.2 The solver, end to end on the standard form

**No `2^t` matrices anywhere on the path.** `L = F₂^t` makes the sparsification *exact* (Eq 35 gives
fidelity 1 identically, since `Z(F₂^t) = (1+2^{-1/2})^t`), so the **same code** that runs approximately
at `k < t` runs exactly at `k = t` and is checkable against brute force. The approximation is a
parameter, not a different program.

| gate | result |
|---|---|
| S0 exact mode reproduces `|H^⊗t⟩` | 3.3e-16 |
| **S1b full solver == brute force, all y** | **60 (circuit, y) cases, max err 8.9e-16** |
| **S2b approximate mode vs its own bound** | **288 cases, max err 0.3536 vs `√δ` = 0.3827** |
| S3 estimator ④ vs the exact O(χ²) norm | max rel dev 0.187 |

**By §6.7 the solver is done.** All four components built, gated, and integrated; what remains is
engineering for scale (the njit path for projections, streaming the χ terms), not missing mathematics.

## 9.3 The vacuity catch — S2's first version could not fail

S2 initially reported **max |err| = 0.0000 over 96 cases** and I nearly banked it. It was testing
nothing. Random Clifford+T circuits on 2–3 qubits give `P_out ∈ {0, 1/2, 1}` almost always; after
filtering the degenerate 0 and 1, **every surviving case had `P_out` = exactly 1/2 — and 1/2 is
protected by symmetry.** `P = num/den` with `num = den/2` exactly: the approximation scales numerator
and denominator alike, so the *ratio* is exact no matter how bad the state is.

A zero error on a quantity that cannot move is not evidence. Two fixes, both now standing:

1. **Construct the test to be sensitive.** Open and close in the X basis so the T phases reach the
   measured probability. `P_out` now spans [0.146, 0.854] (0.854 = cos²(π/8)), and the measured
   approximation error is **0.3536 against a 0.3827 bound** — tight, real, and inside.
2. **Add an explicit vacuity guard as its own gate.** S1a and S2a *assert that the quantity under
   test actually varies* across the sample, and fail if it does not. A gate that cannot fail should
   fail loudly.

This is the same family as the weak-baseline and window-choice errors earlier in the campaign: a
comparison arranged so the favoured answer wins by construction. The tell was the number being *too
clean* — 0.0000 exactly, across 96 cases, on a quantity with a 0.38 error budget.

---

# 10. C5024 — A LARGE INSTANCE, END TO END

`tools/large_run.py`, `tools/delta_sweep.py`.

## 10.1 What makes a large run verifiable at all

**The oracle costs `2^n`. The solver costs `2^{γt}`. Those are independent.** So a large-**t**
instance at modest **n** is simultaneously a real stress of the machinery and exactly checkable
against a statevector. There was never a need to choose between "large" and "verified".

| mode | t | χ | inner products | \|err\| | wall |
|---|---:|---:|---:|---:|---:|
| **EXACT** (k = t) | 14 | 16,384 | **238,836,800** | **1.04e-10** | 727 s |
| APPROX (k < t) | 20 | 128 | 14,584 | 1.29e-01 | 0.5 s |
| APPROX | 30 | 512 | 205,248 | 7.60e-02 | 3.1 s |
| **APPROX** | **43** | **4,096** | **14,364,352** | **4.84e-02** | 143 s |

239 million inner products on 14-qubit stabilizer states, agreeing with the oracle to 1e-10, is the
exact-mode headline. The approximate mode is the *real* algorithm and reaches t = 43 in 2½ minutes.

## 10.2 The χ sweep — controlled, not merely bounded

A single run landing inside `√δ` is weak evidence: at δ = 0.5 the bound is 0.38, most of a
probability's range, so almost any not-catastrophically-broken solver passes. The discriminating
question is whether the error **falls with χ on the same circuit**. One circuit, one `y`, one oracle;
**5 independent random subspaces per k**:

| k | χ | mean fid² | **mean \|err\|** | sd | bound |
|---:|---:|---:|---:|---:|---:|
| 8 | 256 | 0.6671 | **0.09414** | 0.056 | 0.577 |
| 9 | 512 | 0.8026 | **0.08418** | 0.060 | 0.444 |
| 10 | 1,024 | 0.8810 | **0.02801** | 0.013 | 0.345 |
| 11 | 2,048 | 0.9225 | **0.02061** | 0.012 | 0.278 |

**Monotone in χ, falling 4.6×.** A bug in the projection, the phase bookkeeping or the exponent `u`
would show a **floor** — the error would stop improving while the bound kept falling. It doesn't.

*The first version of this sweep* varied δ and drew **one** subspace per point, and reported
"monotone in fidelity: NO". But two δ values collapsed to the same `k`, so that non-monotonicity was
**L-draw noise, not a failure of δ control**. Averaging over independent draws is what separates the
two, and it is the difference between a suggestive result and a measured one.

## 10.3 A guard bug that only scale could find

**t = 48 returned `nan` after 63 million inner products.** Not a numerical failure. Gate G4 had
already proved the denominator *is* `p_y = 2^{-t}` exactly — which at t = 48 is **3.6e-15** — and the
harness guarded with an **absolute** `abs(den) > 1e-14`. It was rejecting a correct value, and would
have for **every t ≥ 47**.

```
t=30   p_y = 9.3e-10     guard passes
t=43   p_y = 1.1e-13     guard passes  (barely)
t=48   p_y = 3.6e-15     GUARD REJECTS A CORRECT ANSWER
```

The fix is to never form two tiny numbers and divide: put the exponent on the **ratio**,
`P = 2^{v-u}·(‖Π_G ψ‖²/‖Π_H ψ‖²)`, and guard on `‖Π_H ψ‖²`, which is O(1).

**No small test could have surfaced this** — at t ≤ 43 the guard is invisible. It is the specific
value of running large: the failure mode was an absolute tolerance applied to a quantity that decays
like `2^{-t}`, which is only wrong once `t` is big enough. Worth generalising: **any fixed epsilon
compared against a quantity that scales with a problem parameter is a latent scale bug.**

### 10.3.1 …and then I committed the same bug in the fix

The fix above moved the exponent onto the ratio and guarded `nH > 1e-12` instead. **t = 48 returned
`nan` again.** Instrumenting rather than guessing a second time:

```
t=51,  v=5   ->   nH = 2^(v-t) = 2^-46 = 1.42e-14      guard was nH > 1e-12   REJECTED AGAIN
```

`nH` is *also* `2^{-t}`-scaled. I had just written down the rule "any fixed epsilon against a
quantity that scales with a problem parameter is a latent scale bug", and then relocated the epsilon
to another quantity with the **same** `2^{-t}` decay. Stating a rule is not applying it.

**There is no correct magnitude threshold in this expression, because every magnitude in it decays
with t.** The only legitimate guards are *structural*: did the projection kill every term, and is the
norm positive.

```python
got = (2.0 ** (v - u)) * (nG / nH) if (pd and nH > 0.0) else float("nan")
```

With that, **t = 46 completes: χ = 8,192, 59,713,056 inner products, P_solver = 0.703192 against an
oracle of 0.750000, \|err\| = 4.68e-2, 475 s.** The `nan` was never numerical — it was mine, twice.

## 10.4 Where O(χ²) stops, and what it costs to go further

The exact norm is `O(χ²)`, which is what caps this ladder — not the algorithm:

| t | k | χ | inner products | projected wall |
|---:|---:|---:|---:|---:|
| 46 | 13 | 8,192 | 6.0e7 | 8 min ✓ measured |
| 51 | 14 | 16,384 | 2.7e8 | ~46 min |
| 56 | 15 | 32,768 | 1.1e9 | **~16 h** |

t = 56 was launched and killed: 16 hours of `O(χ²)` is not a result worth waiting for when
component ④ replaces it with `O(χ·L·J)`, at the cost of an ε-level sampling error. **The exact
route was the right choice for *verification* and is the wrong choice for *scale*,** and that is
exactly the split the paper's two algorithms make (Eq 2 exact, Eq 3 sampled).

> **⚠️ CORRECTED (C5025, commit `056a2f9`) — this paragraph said "145×" and that was wrong.**
> The figure used ε = 0.3 *and* compared a one-norm against two norms. Measured:
>
> | ε | L·J | speedup | usable? |
> |---|---|---|---|
> | 0.3 | 225 | **72.8×** | no — 30% error, not usable for an oracle check |
> | 0.1 | 2,000 | **8.2×** | yes — a precision that can actually be checked |
>
> and the estimator only wins **at all** once χ > 2·L·J. Quoting a speedup at a precision I would
> not accept for the check itself is the substitution the C5025 commit named. The correction was
> made in that commit and **did not propagate here until C5027** — a stale wrong number sitting in
> the plan doc for two cycles while the corrected one sat in the commit message, which is its own
> small lesson about where a correction has to land to count.


---

## 🔻 C5027 — WHY t=80 IS NOT BEING RUN

The memory blocker is cleared: loop interchange + streaming take the estimator from `O(χ)` to
`O(L·J)` (212 GB → 22 MB at t=80), gated **bit-identical** against the list version. t=72 and t=80
now fit. The run is ~146 h of background compute.

**It is not being launched, because nothing would read the number.**

| claim | status |
|---|---|
| F121 runtime advantage | **RETIRED** by our own red-team |
| F120 shot-axis decoder | **DOWNGRADED** to an instrument result |
| F119 sample-complexity floor | **SUPERSEDED** as-executed; explicitly *not cleared*, and needs "its own problem-cost-vs-simulation-cost audit before it is ever offered as the durable IBM entry" |
| F113 2D-HLF depth separation | **LIVE** — and needs no simulation ceiling; it is a *depth* separation carried by a theorem, and it cleared all four attack classes when the preflight was fired at it |

**There is no live runtime-advantage claim, so a t=80 ceiling has no consumer.**

And the C4996 red-team already named the prerequisite:

> *"The property that made MM an ideal sealed, self-verifying race instance — a known closed-form
> dual — is the SAME property that makes it classically easy. Verifiability via exploitable linear
> structure is in direct tension with classical hardness. A genuine hidden-shift advantage needs a
> bent family with no such structure; that is the door to a real submission."*

**The door is a problem-design task, not a bigger simulation number.** The order is: bent family
without exploitable linear structure → its T-count → the ceiling *at that T-count*, which may not be
80. Running t=80 now would price an arm for a claim that does not exist, at a size chosen only
because it is the number I had been quoting.

**The solver is complete and warm.** It waits for a reason to pick a T-count, not for capability.

---

# 11. C5027 — COMPONENT ⑤, AND THE SOLVER'S LAST NAMED PIECE

`tools/conditional_sampler.py` — **9/9**. Eq 29, bit by bit.

## 11.1 What it changes

Until now the solver is a **scorer**: hand it x, get `P^y_out(x)`. ⑤ makes it a **simulator**: it
*draws* x with no outcome supplied. Not a faster capability — a different one, and it is the
difference between serving a **runtime** claim and serving a **sampling** claim.

That distinction is why it was worth building now rather than never. §6.7 explicitly excluded
sampling from *done*, and correctly, because the classical-arm number needs P_out estimation. But
the runtime genre is in poor shape — F121 retired by our own red-team, and the C5027 bent-family
sweep found the replacement door structurally obstructed (the Kasami dual leaves the monomial class
at n=10, 12 and 14, Γ-rank gap widening 2 → 12 → 362, and the *only* free dual in the whole sweep is
the degree-2 Maiorana-McFarland case, which is exactly what leaks classically). **A sampling claim
does not need a bent family with a cheap dual at all.**

## 11.2 Why it is small

A **marginal over a prefix is the same Eq 28 object with fewer projectors** — project the first j
output qubits, leave the rest alone:

```
P(x_j = 0 | x_0..x_{j-1})  =  P(x_0..x_{j-1}, 0) / P(x_0..x_{j-1})
```

so every conditional is a ratio of two quantities ③ already evaluates on the standard form. The
`2^-v ||Π_H ψ||²` denominator depends only on y, cancels from every conditional, and is never
computed. `m+1` marginals per sample, deliberately **not** memoised across draws — a prefix cache is
exponential in m and would trade an O(m)-per-sample algorithm for exponential memory.

## 11.3 The gate suite, and the fact that it first failed to be one

| | |
|---|---|
| T0 | chain rule is exact: `Π_j P(x_j\|prefix) == P_out(x)`, every x, vs brute force — deterministic |
| T1 | siblings sum to parent — the identity `sample_pout` uses by complement |
| T2 | normalisation |
| T3 | vacuity guard **on the conditionals** |
| T4 | empirical draws vs a **calibrated null** (99th pct of TV from true draws), not a threshold I picked |
| T5 | **mutation controls** — three deliberate breakages, each of which must be caught |

**The first version passed 5/5 and was partly vacuous.** Firing the mutations exposed it: two of
three deliberate breakages went *undetected*. The case that the old guard had accepted had a joint
at `max|p − 1/4| = 0.177` — comfortably non-uniform — while `P(x₁=0 | x₀)` was **exactly 0.500 under
both prefixes**. With the second bit a fair coin, nothing that damages the second conditional is
observable, and one mutation telescoped to the right answer.

> **I screened the joint when the object the chain rule is made of is the conditional.** That is
> component ④'s symmetry-protected vacuity, one level up, committed inside the gate whose own
> docstring quotes that failure as the thing to avoid.

The guard now requires, at every level: some conditional far from ½ **and** conditionals that vary
across prefixes. On a case meeting both, all three mutations are caught (TV 0.398 vs null 0.065;
errors 2.1e-1 and 5.3e-1). T5 is now a permanent gate — **a suite that has never been shown to fail
is an untested instrument**, and this one proved that about itself.

## 11.4 Status against §6.7

Stages D, E and G were already green. Stage F — *"desirable and explicitly not required"* — is now
green too. **Every named component ①–⑤ is built and gated.** What the solver still lacks is not
capability but a consumer: per §10's table, the one live entry that needs what it produces is F119's
outstanding problem-cost-vs-simulation-cost audit, and that needs the *problem* arm as well.
