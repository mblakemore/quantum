# Finding — Exp184: THE HANDSHAKE ACROSS TIME — states with disjoint lifetimes, entangled at 40σ, by a choice made after both were gone

**Cycle**: C4874 · **Date**: 2026-07-19 · **Backend**: ibm_fez · **Job**: `d9e3ngcinv1c73appedg`
(12 circuits: 4 arms × ZZ/XX/YY, 8000 shots). **Foundations class**: delayed-choice entanglement
swapping (Peres 2000 / Ma et al. 2012 / Megidish et al. 2013), eleventh flight of the campaign.
Creator go: ship-computer general#61.

## Result

| arm | schedule | ZZ / XX / YY | F(Φ⁺) |
|-----|----------|--------------|-------|
| **acrosstime** | A measured → *then* D created → late swap | +0.824 / +0.759 / −0.745 | **0.832 (40σ over 1/2)** |
| standard | ordinary swap, verify at end | +0.846 / +0.771 / −0.764 | 0.845 |
| **latechoice** | same early schedule, late **product** measurement | −0.004 / −0.017 / −0.018 | **0.249** |
| nomeas | (B,C) never measured | ≈ 0 | 0.250 |

1. **The handshake**: qubit A's state was measured — destroyed, its record classical — strictly
   before qubit D's state was prepared (circuit-schedule enforced). A later Bell measurement on
   the middles, frame-sifted, leaves A's early record and D's late record **certified entangled
   at F = 0.832, 40σ past the separable bound**. Two states whose lifetimes never overlapped.
2. **The late choice decides**: run the *identical* early schedule and replace the late Bell
   measurement with a product measurement — the same class of early data sorts to F = 0.249,
   XX/YY dead flat. Whether A and D "were entangled" is settled by a measurement performed after
   both states are gone. Entanglement is not a substance carried through time; it is structure
   in the correlation record, indifferent to schedule.
3. **No signaling, audited in-data**: A's marginal distributions are identical across every
   later choice (max spread 0.0191, pre-registered gauge < 0.02 — held, barely; noted). Nothing
   propagates backward; the "retro" is entirely in the sifted ensembles, as in every
   delayed-choice experiment since Wheeler.
4. **Null exact**: no middle measurement → 0.250.

## The secondary that failed into a better model (honest accounting)

Pre-registered window-model secondary: "dead qubits cannot dephase → acrosstime should BEAT
standard by one spectator's window dose." **Not confirmed**: Δ = −0.013 at −1.1σ — a
statistical tie. The post-mortem found the error in my ledger, not in the law: **A's own early
measurement is itself a mid-circuit window, and B idles entangled through it.** Corrected dose
count: acrosstime = B (through A's measurement) + D (through the swap) = 2 doses; standard =
A + D (both through the swap) = 2 doses. **Equal doses → the corrected model predicts exactly
the tie we measured.** The law survives; my accounting didn't. Rule refined: count a window
dose for *every* spectator that idles entangled through *any* measurement episode — including
the handshake partner's own death. (Fourth instance of the arc's meta-lesson: the model was
right once its structure was written down completely.)

## Fence

One die: "disjoint lifetimes" refers to the *states* — A's state is destroyed before D's state
is prepared, enforced by circuit schedule and barriers; the physical transmons exist
throughout (as Megidish's optical modes did). Sifting uses the relay's published outcomes
(Exp180's operational model). The late "choice" is compiled per circuit, not drawn from a
quantum random number mid-flight (the standard hardware-characterization form; an
RNG-in-the-loop version is a named, priced follow-up, not claimed). No signaling occurs or is
implied — audited above.

## What this closes

The campaign asked what secret of the universe the stack could reach: this one — **the
atemporality of quantum correlation structure** — certified with the same theorem-fixed
witness, same-job falsifiers, and frame-sifting machinery the network wing built for
engineering. Eleven pre-registered flights; the falsifiers are eleven for eleven.
