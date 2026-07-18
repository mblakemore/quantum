# The delayed-choice quantum eraser on silicon — a future coin toggles the past's fringe (Ember, C4197)

**🖖 Star-Trek directive (Creator, 2026-07-18):** *"fly the most frontier/futuristic/star trek like
experiments you can come up with"* until Quantinuum access. Deconflicted from Whisper's teleportation
(Exp154). Intrinsic-falsifier bar (Elder). **Job** `d9dr5vqneu4c739nkt20`, `ibm_fez`, 24 circuits
(3 arms × 8 phase points), 4000 shots. **Pre-reg** (0.60, frozen in manifest before decode):
`V_erase − V_whichpath > 0.2 AND V_marginal < 0.1`. **Verdict: HELD.**

---

## What was asked of the universe

Put a system qubit S in superposition and copy its *which-path* information onto a marker qubit M
(this destroys S's interference). Does S's fringe **reappear** if we later choose to **erase** the
which-path info — and can that choice be made *after* S is already measured?

## The result

| arm | fringe visibility V | reading |
|---|---|---|
| **STATIC erase** — H(M) in conjugate basis | **0.946** | near-perfect interference fringe restored by erasure |
| **STATIC which-path** — M measured in Z (MATCHED CONTROL, identical coincidence sort) | **0.068** | flat: post-selection **alone** makes no fringe |
| **DYNAMIC coin=1** — future quantum coin erases | **0.797** | fringe, idle-degraded (see below) |
| **DYNAMIC coin=0** — future quantum coin keeps which-path | **0.155** | flat |
| **NO-SIGNALING marginal** P(S=0), unconditioned | V=**0.055** | flat at every phase → no FTL |

- **Erasure signal `V_erase − V_whichpath = +0.878`** (gate >0.2). The near-ideal fringe (0.946) is
  present *only* when we erase; the matched control that pays the identical post-selection cost stays
  flat (0.068). So the fringe is the **erasure**, not the sorting.
- **Delayed-choice signal `V(coin=1) − V(coin=0) = +0.642`.** In the dynamic arm a quantum coin is
  flipped by an ancilla measured **after** S is recorded; a real feed-forward `if_test` then erases M
  iff the coin is 1. Sorting S's already-registered data by that future coin shows a fringe when the
  future said "erase" and flatness when it said "keep." **The choice is causally in S's future.**
- **No-signaling holds (V_marg=0.055 < 0.1).** The unconditioned marginal is flat everywhere — the
  fringe lives only in coincidence with M. Nothing about M's future choice is visible in S's marginal.
  No FTL, no retrocausal *signaling*. This flatness is the honesty fence **and** a measured number.

## The bonus finding — the delayed choice costs exactly the idle-error the network just mapped

The dynamic erase visibility (**0.797**) is degraded from the static erase (0.946). This is
**pre-registered** and it is the marker-idle dephasing signature Elder/Whisper just characterized:
in the dynamic arm M must idle through S's measurement, the coin's measurement, and the feed-forward
latency before its own H — the same idle-error class that split Exp154's teleportation (Z 0.96 vs
X/Y 0.88) and drowned Exp144. Here it is the ~0.15 tax on the delayed choice, not a wall: the signal
still clears the gate by +0.642. **The instrument that floors negative results is here just the
texture on a positive one** — the same lesson Whisper drew from Exp154, now on a second Trek flight.
The forward lever is a DD sequence on M across the feed-forward window (Elder's Exp154 note).

## Method — why this is a clean result and not a light show

1. **Self-verifying (intrinsic falsifier):** we hold φ and derived the exact conditional
   `P(S=0|M=0) = (1+cos φ)/2`; the noiseless truth-gate reproduces it (V=1.000) and the hardware
   traces it (cond = 0.99, 0.86, 0.52, 0.17, 0.03, 0.16, 0.48, 0.84). No seals, no trust.
2. **Matched control (Ember C4196 discipline):** the which-path arm runs the *identical* coincidence
   post-selection; `H(M)` is the **only** independent variable. This is the axis-matched control —
   had post-selection manufactured the fringe, the control would show it. It does not (0.068).
3. **Advisor-hardened axis:** the first design measured S first in a *static* circuit to stage the
   "delayed choice." The advisor caught that this is **observationally vacuous** — with no feed-forward,
   `measure(S)` and the marker ops commute, so measure-first buys zero observable delayedness while
   paying marker idle. The genuine delayed choice was moved into the **dynamic** arm (real `if_test`
   feed-forward), where measurement order is physical. Same class of catch as C4196's duration-vs-2q-count.
4. **No-signaling fence measured, not asserted:** the marginal flatness is a first-class output.

## What the universe answered

Erasing which-path information restores a quantum interference fringe — and the erase-or-keep choice
can be made by a quantum coin flipped *after* the interfering qubit is already measured, with the
fringe appearing or vanishing accordingly, **while no signal is transmitted** (the marginal never
moves). Wheeler's delayed-choice quantum eraser runs on IBM silicon: erasure signal +0.878, delayed
signal +0.642, no-signaling margin intact. The "retrocausal" language is a fence, not a claim — the
order is temporal (coin after S), the correlation is coincidence-only, and causation is not violated.

**Numbering:** new experiment (Exp155), quantum-network/foundations museum wing. Resolves a Q-slot in
the frontier doc (docs `questions-we-can-now-ask-the-universe-ember-c4196.md`). Twin lesson to Exp154:
feed-forward latency = idle dephasing, now visible as texture on a second positive Trek result.
