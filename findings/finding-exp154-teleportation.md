# Finding — Exp154: quantum teleportation with verified fidelity on ibm_fez ("beam me up")

**Cycle**: C4844 · **Date**: 2026-07-18 · **Backend**: ibm_fez · **Jobs**: `d9dinncinv1c73ap52ng`
(teleport + no-entanglement control), `d9dios1htsac739d4dd0` (no-correction control).
First piece of a new **quantum-network** museum wing. Creator directive: fly the most Star-Trek
self-verifying frontier experiment (Quantinuum access pending).

## The result — genuine teleportation, decisively

Teleport each of the six cardinal states across a real feed-forward circuit (mid-circuit Bell
measurement → conditional X/Z correction on the receiver, fez dynamic circuits), then verify the
output against the KNOWN input. Self-verifying — no seals.

| state | F (teleport) | F (no-entanglement) | F (no-correction) |
|-------|--------------|---------------------|-------------------|
| Z+ | 0.959 | 0.990 | 0.516 |
| Z− | 0.959 | 0.972 | 0.467 |
| X+ | 0.896 | 0.502 | 0.505 |
| X− | 0.894 | 0.510 | 0.496 |
| Y+ | 0.884 | 0.502 | 0.499 |
| Y− | 0.884 | 0.504 | 0.507 |
| **avg** | **0.913** | 0.663 | 0.498 |

**Average teleportation fidelity 0.913 vs the 2/3 measure-and-prepare bound — margin +0.246.**
Every state clears the bound. Genuine quantum teleportation on silicon.

## Two falsifiers, two mechanisms (Elder, C4844)
Teleportation needs both the shared entanglement and the classical correction; removing either must
fail, and each fails *differently*, so no partial cheat passes both:
- **No entanglement** → the superposition states collapse to chance (X/Y ≈ 0.50); the Z states
  survive by accident (a qubit left near |0⟩ answers |0⟩ right), so this control's *average* (0.663)
  is not the 2/3 bound — the bound is a theorem, not this circuit.
- **No correction** → *all six* states collapse to chance (avg 0.498): the receiver is correct only
  up to a random Pauli that the classical bits were meant to undo.

Only genuine teleportation clears 2/3 **and** survives both falsifiers. This run does.

## The residual is a known signature (Elder diagnostic, confirmed)
The ~0.09 below perfect is **not** uniform: Z states 0.96 vs superpositions 0.88–0.90. That gap is
the **receiver-idle dephasing signature** — the Z eigenstate is T2-robust, while the X/Y
superpositions dephase during the measure→classical→correction latency window. It is exactly the
idle-error class from Exp143/144, now visible in a *positive* result rather than a negative one.
It did not cap the result (0.88 ≫ 0.667). **Forward lever:** dynamical decoupling on the receiver
across the correction latency lifts the X/Y states specifically → average from 0.913 toward ~0.95
(the same DD move as the Exp147 QEC next-rung).
**Update (C4846, Ember C4198)**: the DD lever is now empirically tempered — on the eraser's marker
qubit (an analogous feedforward-idle window), a Hahn echo recovered only +0.019±0.012 of the gap
(z=1.53, not resolvable), and part of the apparent idle cost there was estimator bias. Transfer
boundary: different circuit/qubit, so the ~0.95 projection here is unverified extrapolation until
DD is tested on this receiver directly; treat the lever as *plausible, not established*.
**Final (C4847, Exp158)**: the direct receiver test came back **NULL** (Δ = +0.0021 ± 0.0020,
bracket control clean) — and the same-circuit baseline re-flown 10 h later ran at 0.936 with the
Z-vs-X/Y gap nearly gone (0.00–0.02). The lever is **not established**, and the ~0.07 deficit
this table shows is a *same-day snapshot of calibration-dependent drift*, not a stable device
signature. The dephasing mechanism remains the best explanation of that day's pattern; treat the
per-state split as dated evidence. See `finding-exp158-dd-teleport-receiver.md`.

## Gates (passed pre-flight) + fences
Truth-gate (noiseless Aer): F=1 for all six states; no-entanglement control fails on the
superpositions (falsifiability). No-correction arm verified noiseless (0.498) before flight.
Transpile: depth 18 / 2 CX with real `if_else` feed-forward. **Fence:** single-hop, finite fidelity
(SPAM + 1 entangling gate + correction latency); a hardware demonstration of the teleportation
primitive, not a deployed quantum network.
