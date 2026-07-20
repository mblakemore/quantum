# What Heron-r2 Can Actually Do: the practical capability envelope of the whole campaign

*Whisper C4933, 2026-07-20. Creator: "What can we do with all of this on Heron hardware?"* Not the
aspirational horizons, not the paths-past-walls — the honest here-and-now: given everything certified,
what is *usable* on the real `ibm_fez` / `ibm_marrakesh` / `ibm_kingston` (Heron-r2) chips, with the
useful/demonstrative/not-yet fence kept sharp.

---

## The honest Heron envelope (the real constraints everything below respects)

- **156 qubits, heavy-hex** (degree ≤ 3). Width is cheap; **depth is the wall** — a ~1000 two-qubit-gate
  coherence limit (F05/F54), and **routing** is the binding cost for anything multi-block (we measured
  it: a two-distance-3-block gate is 82 gates on heavy-hex vs 41 on a grid — routing, not logic).
- **Readout ~99% clean** — measurement mitigation is nearly free; a deep observable's residual is
  gate/coherence error, not readout (Exp173).
- **Calibration drifts hour-to-hour** — a fault-tolerance/QEC advantage is a *snapshot, not a constant*
  (Exp245: +0.341 → +0.077 on the same qubits, hours apart). Quote a range, schedule for good weather.
- **Sweet spot: shallow (≤ ~30 two-qubit gates), postselected, single- or few-logical-qubit circuits.**

---

## Tier 1 — genuinely USEFUL now (real utility, not a demo)

1. **Certified private randomness.** F117 delivers **0.65 private random bits per use** with a rigorous
   one-sided device-independent certificate (and the paranoid rungs honestly *quarantined* because a
   single chip can't meet no-signaling). This is a real cryptographic primitive that *runs on Heron
   today* — randomness whose unpredictability is certified by a Bell/steering violation, not trusted.
2. **Entanglement-enhanced sensing.** Heisenberg-limit metrology certified to N=5 (F108/F109, 168σ) — a
   genuine (small-N) sensing advantage over the standard quantum limit, on-chip. And 205 showed the
   [[4,2,2]] shield *preserves* Fisher information, so a *protected* sensor is on the table.
3. **Provable-bound benchmarking.** The causal-order (216σ), contextuality (196σ), and Bell games are
   *certified* benchmarks — a game-value clearance of a provable ceiling is a sharper, more meaningful
   hardware figure of merit than random-circuit fidelity for the properties they test.
4. **A fault-tolerance-primitive testbed.** This is the newest and, for the field, most useful: Heron is
   now a validated platform to *develop and test the FT software toolkit before scalable QEC exists* —
   magic injection (243), the closed+dialed universal gate set (244/246), Clifford-frame tracking, the
   logical-ISA compilation, the sham-control and byproduct-robust-readout methods. You can validate a
   logical compiler on real error-detected hardware today.
5. **The QPU weather service** (`tools/qpu_weather.py`) — a real scheduling/characterization tool that
   turns the drift (constraint #3) into an asset: run depth-sensitive work in the low-noise windows.

## Tier 2 — real physics you can DEMONSTRATE now (valuable, not "useful")

- **A protected, universal, programmable single-logical-qubit processor.** The whole magic arc composes
  into one usable object on Heron: prepare *any* single-qubit state/rotation (Clifford + a
  fault-tolerantly-injected T — a dense set) **behind error detection**, at ~19–30 gate depth, better
  than bare via postselection. Closed (244) and *dialed to any equator angle* (246). It is the mechanism
  of universal computation on a protected qubit, running.
- **The error-corrected inner loop.** Detect→correct→arbitrary-error (236/238), non-destructive live
  syndrome (240), repeated rounds that pay (241) — the continuous QEC loop, demonstrable and
  characterizable on Heron (with the drift caveat).
- **The foundations suite** — indefinite causal order + its thermodynamics (a closed engine cycle,
  negative energy, QET), the network stack (distribute/route/purify/carry/teleport/nonlocal-CNOT/
  distributed-BV/QKD/secret-sharing), exotic phases (time crystal, scars, anyons, SPT edge modes), and
  the time/observer instruments (Page–Wootters, Leggett–Garg, Wigner's friend, the objectivity dial).
  Every one runs on Heron and beats a provable bound or certifies a first-of-kind.

## Tier 3 — the honest not-yet (what Heron cannot do, stated plainly)

- **Raw computational speedup** — depth-walled (F54's measured wall; no constant factor closes a 10×
  depth deficit). The BGK constant-depth solver runs (F113) but its advantage is asymptotic; a laptop
  still beats the flown instance.
- **Scalable fault tolerance** — below threshold on this generation; the codes we ran corrected errors
  we *injected*, and the machinery still costs more than it saves on hard problems.
- **Deep multi-logical-qubit composition** — the routing wall (error-corrected magic 82 > the ~54 clean
  zone). *This is a heavy-hex topology limit, not fundamental* — see below.

---

## What the fault-tolerance arc specifically buys on Heron — and the on-ramp to the next chip

- **On Heron today**: a protected universal single-qubit computer + the FT-primitive testbed (Tier 1.4)
  — the place to *build and de-risk the FT software stack* while the hardware catches up.
- **Quantified on-ramp to the next hardware**: we *measured* that error-corrected magic is
  **heavy-hex-routing-limited, not logic-limited** (pure logic 25 gates; heavy-hex 82; **surface-native
  grid 41, under the clean zone**). So the two-logical-qubit corrected primitives — a live logical Bell
  pair, error-corrected magic, a distributed logical gate — are **flyable the moment a grid-connectivity
  Heron-successor arrives**, and we know the exact target (≤ ~41 gates). The blocks are built and
  waiting; the missing piece is topology, and it is on IBM's roadmap.

---

## The three most useful things to actually build on Heron next (each shallow, each real)

1. **A certified-randomness *service*** — wrap F117 into a repeatable, weather-scheduled pipeline that
   emits certified private bits with the certificate attached. The one Tier-1 result that is a *product*,
   not a demo. (Compose F117 + the weather service.)
2. **A protected sensor** — the shield-preserves-Fisher result (205) + the Heisenberg metrology
   (F108/9): an entanglement-enhanced field estimate *with error detection*, testing whether the shield
   buys a more robust small-N sensor. Shallow, useful, genuinely new composition.
3. **The logical-ISA testbed** — publish the certified logical instruction set (encode · frame-tracked
   Clifford · inject-T · dial · live-correct · decode) as a small API + a logical-circuit CI that
   depth-counts and sim-verifies before spending QPU. Turns the whole arc into a *reusable platform* for
   FT-software development on real hardware.

**One-line answer:** *On Heron today we can run a protected, universal, programmable single-qubit
computer and a suite of certified provable-advantage instruments — genuinely useful for certified
randomness, enhanced sensing, benchmarking, and as the testbed where the fault-tolerant software stack
gets built and de-risked before the hardware scales. What we cannot do (speedup, scalable FT, deep
multi-qubit correction) we have mapped precisely — and for the multi-qubit corrected primitives, the
only missing piece is grid connectivity, with the exact gate target already in hand.*
