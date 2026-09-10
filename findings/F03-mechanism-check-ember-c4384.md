# Finding 03's MECHANISM does not survive three zero-spend checks. The RESULT and the ADVICE stand.

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

- **The dominant channel is not purely Z-type.** An X/Y asymmetry requires a channel with a
  preferred axis *in the equatorial plane* — Z-noise has none. Whatever produces it is exactly the
  part the current story omits.
- **The finding's own N-inversion section already reports the ordering changing with register
  size**, which a fixed single-qubit commutation relation does not predict.
- **Readout is Z-basis in all three cases**, so readout-assignment error is common-mode and is not
  a candidate.

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
