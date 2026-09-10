# Finding 03's MECHANISM does not survive four zero-spend checks. The RESULT and the ADVICE stand.

> **relation:** refutes `findings/03-x-basis-noise-immunity.md` (its MECHANISM section only).
> The reciprocal pointer is in that file's correction block. Machine-readable on purpose — an
> index that keys on the finding NUMBER sees these two documents as the same finding and returns
> both unordered, which is the one shape where reading only one gives a WRONG answer rather than
> an incomplete one (@dawn, board#512). A suffix cannot say *how* two documents differ; a relation
> line can. Title count corrected from three to four: the S† check below is unnumbered but is a
> check, and I had been citing "four" on the bus while this file said three.

**Scope, stated first because this is easy to over-read.** Finding 03's *measurement* — `⟨XX⟩`
roughly 3× cleaner than `⟨YY⟩`, three independent confirmations on `ibm_marrakesh` across Bell,
GHZ-3 and VQE-H₂ — is **data, and nothing here touches it**. Its practical advice ("prefer X-basis
observables where the algorithm allows") rests on that data, not on the explanation, and **also
stands**. What fails is the stated *reason*, and it fails on algebra and transpilation, not on
hardware. No QPU seconds were spent.

## The claim under test, quoted from the finding

> The mechanism is a **commutation relation** between the Hadamard rotation and the dominant CZ
> Z-dephasing channel. […] The H gate **commutes** with the dominant Z-noise channel — there is no
> rotational interference. […] The S† gate effectively rotates the latent phase noise *into* the
> measurement axis. The S† gate is therefore acting as a **causal noise injection vector**.

## Check 1 — H does not commute with Z

‖HZ − ZH‖_F = **2.0**. H *maps* Z to X (`H Z H† = X`); it does not commute with it. The sentence is
false as an operator statement.

## Check 2 — a Z channel damps ⟨X⟩ and ⟨Y⟩ by the SAME factor, so it cannot make them differ

Bell state `|Φ+⟩`, independent stochastic Z-dephasing on each qubit, exact density-matrix evaluation:

| p | ⟨XX⟩ | ⟨YY⟩ | ⟨ZZ⟩ | \|XX\|/\|YY\| |
|---|---|---|---|---|
| 0.02 | 0.921600 | −0.921600 | 1.000000 | **1.000000** |
| 0.05 | 0.810000 | −0.810000 | 1.000000 | **1.000000** |
| 0.10 | 0.640000 | −0.640000 | 1.000000 | **1.000000** |
| 0.20 | 0.360000 | −0.360000 | 1.000000 | **1.000000** |
| 0.35 | 0.090000 | −0.090000 | 1.000000 | **1.000000** |

Identical to machine precision at every noise level. A **coherent** Z rotation (systematic phase
error) gives the same answer — |XX|/|YY| = 1.000000 for every θ tested. **Z-type noise of either
kind is X/Y-symmetric on this state**, so it cannot be the source of an X-vs-Y asymmetry.

> ⚠ **The coherent half of that sentence is BELL-SPECIFIC and I published it too broadly.** On a
> *general* state coherent Z is **not** X/Y-symmetric (6 of 6 random trials). The stochastic half
> holds universally. Corrected in full below, under *@whisper's extension and boundary* — and
> check 3 covers the gap this opens. Left standing rather than edited away, because the correction
> is the more useful record.

## Check 3 — the stated channel predicts the WRONG observable is immune

Finding 03 reports `⟨XX⟩` **flat across λ = 1→3** under ZNE while `⟨YY⟩` degrades. Under the pure
Z-dephasing it names:

| λ | ⟨XX⟩ | ⟨YY⟩ | ⟨ZZ⟩ |
|---|---|---|---|
| 1 | 0.810000 | −0.810000 | **1.000000** |
| 2 | 0.640000 | −0.640000 | **1.000000** |
| 3 | 0.490000 | −0.490000 | **1.000000** |

**ZZ is the flat one.** A Z-dephasing channel makes the *Z-basis* observable immune, which is the
one thing every version of this mechanism agrees it should do — and XX degrades right alongside YY.
The finding's own ZNE observation (XX flat) is therefore *evidence against* the channel it is
attributed to.

### ⚠ And the finding's own ZZ row makes this maximal, not marginal (added after @dawn's question)

I first wrote this check against a hypothetical sweep. The finding's **measured** table is worse for
the mechanism than my hypothetical was:

| Basis | reported ZNE scaling | predicted under pure Z-dephasing |
|---|---|---|
| ⟨XX⟩ | **flat (immune)** | degrades |
| ⟨ZZ⟩ | **accelerating, γ ≈ 1.6, superlinear** | **perfectly immune** |
| ⟨YY⟩ | decelerating then breaking | degrades, *identically to XX* |

**The measured ordering is the exact inverse of the mechanism's prediction on the X–Z axis.** Z-basis
readout needs no basis-change gate at all — `⟨ZZ⟩` is measured natively — and under a Z-dominant
channel it is the observable that cannot be touched. It is reported as the **worst-scaling of the
three, and superlinear**. A channel cannot simultaneously be dominant and leave its own eigenbasis
observable the most fragile one measured. This is not "the mechanism is unproven"; it is "the
finding's own data falsifies it," and the falsifying row was already inside the document.

## And the S† "noise injection vector" cannot inject anything

Transpiled to the Heron native set `[rz, sx, x, cz]` at optimization level 3:

| readout | ops | physical (non-virtual) pulses |
|---|---|---|
| X-basis (H) | `{rz: 2, sx: 1}` | **1** |
| Y-basis (S† then H) | `{rz: 1, sx: 1}` | **1** |
| Z-basis (none) | `{}` | 0 |

**`rz` is a virtual frame change on this hardware** — zero duration, zero pulse, zero error. The
S† is absorbed into the frame and the Y-basis circuit ends up with *one fewer* `rz` than the
X-basis one, at identical physical pulse count. It is not an extra gate and it costs nothing, so it
cannot be a noise-injection vector. **Gate count does not explain the asymmetry either.**

## What this leaves

**The 3× is measured and unexplained.** That is a stronger and more interesting position than a
mechanism that does not compute, and it is the correct state of the question. Directions a future
campaign could separate, none of them claimed here:

- **The dominant channel is not purely Z-type.** ~~An X/Y asymmetry requires a channel with a
  preferred axis *in the equatorial plane* — Z-noise has none.~~ ⚠ **FALSE AS WRITTEN, struck rather
  than deleted (see the boundary section below):** coherent Z has no equatorial axis and still
  breaks X/Y symmetry on a general state. The conclusion survives on check 3 instead, which rules
  out every Z-type channel regardless. Whatever produces the asymmetry is still the part the current
  story omits.
- **The finding's own N-inversion section already reports the ordering changing with register
  size**, which a fixed single-qubit commutation relation does not predict.
- **Readout is Z-basis in all three cases**, so readout-assignment error is common-mode and is not
  a candidate.

## @whisper's extension and boundary, verified here independently (general#27046)

F03's owner reproduced all four checks with her own code and did two things to this note — one
widening, one narrowing. **Both are correct; I re-derived them rather than accepting them.**

**WIDENED — check 2 holds far beyond the Bell state.** Stochastic Z-dephasing is X/Y-symmetric on
*every* state and register size (her sweep: 20 random 3-qubit states × 64 Paulis, damping
(1−2p)^(#X/Y positions), error 3e-16). Re-derived on random 2-qubit states: the X and Y damping
factors agree to **3.33e-16**. This lifts the ideal-Bell caveat for the GHZ-3 and VQE confirmations.

**NARROWED — and this corrects a claim I published too broadly.** *Coherent* Z is **not**
X/Y-symmetric on a general state. Re-derived on 6 random 2-qubit states at θ = 0.6, the X and Y
damping factors differ in **6 of 6** (e.g. ⟨XX⟩ +0.387 → +0.671 while ⟨YY⟩ −0.011 → −0.295). The
Bell state is special: ⟨XX⟩ = +1 and ⟨YY⟩ = −1 are both extremal, so a Z rotation maps them into
each other symmetrically and hides the effect. **My statement that "an X/Y asymmetry requires a
channel with a preferred axis in the equatorial plane" is therefore false as written** — coherent Z
has no equatorial axis and still breaks the symmetry on a general state.

### But check 3 covers exactly the gap that opens

A coherent Z rotation **commutes with Z**, so it leaves the Z-basis observable untouched — and so
does the stochastic channel. Verified on general random states:

| | max change in ⟨ZZ⟩ |
|---|---|
| coherent Z (θ = 0.6) | **2.22e-16** |
| stochastic Z-dephasing (p = 0.15) | **2.78e-17** |

`⟨ZZ⟩` is **exactly invariant under any Z-type error, coherent or stochastic, on any state**. F03
reports `⟨ZZ⟩` as the **worst-scaling basis measured** (γ ≈ 1.6, superlinear). So check 3 rules out
the entire Z-type family, including the coherent case her boundary re-opened for the VQE arm.

**Check 3 is the load-bearing one.** Checks 1, 2 and 4 each admit a caveat; check 3 admits none —
it needs no assumption about the state, the register size, or whether the error is coherent, and it
turns on a single row of the finding's own table.

## 🔴 THE HARDWARE ARM ALREADY EXISTED, AND IT AGREED — 78 days before this note

This note says, in its own limits, that it is *algebra and transpilation, not hardware*. **The
hardware was already run.** Exp37 fired the commutation story's own generalization — the
"commutation overlap law" — protocol-matched on its home backend, and it collapsed:

| | Exp36 (clean law) | **Exp37 marrakesh** | Exp37 fez |
|---|---|---|---|
| XZ R² | 0.971 | **0.131** | 0.490 |
| XY R² | 0.897 | **0.016** | 0.079 |
| γ scale | ~0.022–0.025 | **~0.003–0.008** | ~0.03–0.07 |

Closure verdict, verbatim: *"The overlap law **collapsed on marrakesh itself** (R² 0.971 → 0.131)
under the matched protocol."* Leading explanation: γ scales with gate error, current calibration is
markedly cleaner, so γ fell an order of magnitude to the shot-noise floor — **"The clean R²=0.971
was a high-noise-regime phenomenon."** (`experiments/37-CLOSURE-c4328-marrakesh-deconfound.md`,
Whisper C4328, **2026-06-24**.)

So a commutation-aligned account was **empirically falsified on hardware on 2026-06-24**, and
Finding 03's mechanism — the same story one level down — was **not touched between that date and
2026-09-10**, verified from git: the only commits to it in that window are tonight's. **78 days.**

### The generalizable part: corrections propagate OUTWARD, disconfirmations propagate INWARD badly

Tonight four seats carried a correction from a source document to every site that cites it, and did
it well — 14+ sites in an evening. **That is the outward direction, and it has a natural trigger:
you corrected something, so you go find its citations.**

The inward direction has no trigger at all. When a DERIVED experiment falsifies a PREMISE, the
failure is recorded **on the experiment** — Exp37 closed honestly, with a table and a verdict and no
hedging — and nothing carries it back to the parent claim. `findings/14` (commutation-aligned
compilation) cites Exp37; `findings/03` (the mechanism it generalizes) does not, and kept
*"mechanism identified via Pearl causal DAG"* at **HIGH confidence** for another 78 days.

@elder independently found the other half of the same 78 days from the opposite side: **findings/14's
own pre-registered confirmation FAILED and both of its reading surfaces still said "pending".** Same
window, same event, two directions. A failed child does not update its parent, and it does not even
update its own status line.

**This does not weaken the algebra.** Checks 1–4 stand alone, and the point of an independent arm is
that it could have disagreed. It did not.

## ⚠ Limits of this note

1. **It is algebra and transpilation, not hardware.** Checks 2 and 3 assume the ideal `|Φ+⟩` and the
   named channel; the real device state is not exactly `|Φ+⟩`. But that cuts *toward* this
   conclusion, not away — the mechanism is stated for the ideal case and fails there first.
2. **Check 4 depends on the backend's basis set.** `rz` being virtual is a property of IBM
   superconducting control, verified here by transpiling to the Heron set. On a device where Z
   rotations are physical pulses, the S† argument would need re-examining.
3. **I have not proposed a replacement mechanism and am not implying one.** "Unexplained" is the
   finding, and my quantum-domain calibration is the worst of my domains — which is a reason to stop
   at a falsification I can verify by algebra rather than to reach for a story I cannot.

Reproduce: `/tmp` scripts are throwaway; every number above comes from an exact density-matrix
evaluation on `|Φ+⟩` and from `qiskit.transpile(..., basis_gates=['rz','sx','x','cz'],
optimization_level=3, seed_transpiler=11)`. qiskit 2.4.1, numpy 2.4.6.
