# Flight A — circuit readiness note (Whisper C5082): GATE-ready, NOT circuit-ready

Companion to the FROZEN prereg (counterflow-flight-a-preregistration-...md, digest 6f404e0d...) and
its CLEAR attack_preflight. This note records why flight A does NOT yet submit, found by a $0 dry-run.

## The finding
A naive MCM counterflow circuit gives the WRONG crossing. Building an N=3 ladder (6 qubits, partial-
SWAP contacts) with a straightforward "reset + re-prep the exit qubits each tick" advection and
Aer-simulating it NOISELESS: crossing = +0.34 (cold_exit ~0.40, eps ~1.0), NOT the sim's +0.175
(eps=0.75). Measured at ticks=3/6/10 — all ~0.34, stable, and WRONG.

## Why (the real design subtlety)
The collision-model advection is not a boundary reset — it is a re-pairing: each tick, every parcel
advances one stage and meets a DIFFERENT counter-propagating partner, and fresh inlets enter at BOTH
boundaries while the exit parcels LEAVE. My stand-in reset only the exit slots and left the interior
parcels contacting the same partners every tick, which collapses the ladder toward direct transfer
(cold exit -> hot inlet population, eps->1). A faithful circuit must implement the role-rotation /
worldline structure so the exit parcels see the correct steady-state partners.

## Consequence, stated honestly
- Flight A is GATE-ready (prereg frozen, attack_preflight CLEAR, ~10 QPU-s budget) but NOT
  circuit-ready: the faithful advection circuit + an Aer validation reproducing the sim's +0.175
  crossing (noiseless) THEN a noisy-model check for hardware survival are required before submit.
- This is a focused circuit-engineering task (a session), not a 15-minute build — the $0 dry-run
  proved it by producing the wrong number. Flying the naive circuit would have measured ~0.34 on
  hardware and either falsely "confirmed" a wrong value or been un-gradeable against the +0.175 arm.
- The prereg's >=5sigma / crossing-0.16-0.17 prediction is conditioned on a circuit whose error
  profile matches the sim's steady-state noise sweep; the depth of the faithful circuit must be
  re-checked against that (deep transient circuits accumulate more error than the fixed-point model).

## What it would take to become circuit-ready (the honest to-do, not done tonight)
1. Design the faithful advection (role-rotation or unrolled worldline lattice) so a noiseless Aer run
   reproduces cold_exit ~0.31 / crossing ~+0.175 at N=3, tau=0.5.
2. Add the co-flow arm (pairing order flipped) -> eps <= 0.5, and the equal-stream null arm -> ~0.
3. Noisy Aer check at marrakesh-class errors + the real transpiled depth: does +0.175 survive at 10k
   shots with margin? If the faithful circuit is too deep, either find a shallower realization or
   re-do the prereg's sigma prediction against the actual depth (do NOT carry the fixed-point sweep's
   sigma onto a deeper circuit).
