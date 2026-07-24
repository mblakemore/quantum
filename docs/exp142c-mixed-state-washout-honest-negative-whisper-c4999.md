# Exp142c — The Mixed-State Delivery Washed the Signal: Honest Negative, Substantially Mine

*Whisper C4999, 2026-07-24, substrate claude-fable-5. The F119 remedy re-fly (Exp142c) flew clean
(10/10 jobs, zero OOM) and graded a BLIND NO-WIN: the true-basis parity washed to ~0.5 instead of
1.0 — the (I+P) coherence is gone on-device. Caught blind by Elder's frozen estimator pre-reveal
(the integrity mechanism working). Booked per the Creator's honest-negatives rule: full accounting,
the rule it teaches, no spin, no band-shopping. This doc owns MY part — the mixed-state delivery
was my proposal and my construction.*

## What happened (measured)

- n=4 flown data at the revealed true basis ZYYZ: even-rate over 20 reps = **0.548 ≈ 0.5** — the
  true basis reads like every wrong basis. The weight-n coherence is destroyed. Monotone worse to
  n=8. q_n ≈ 0.003 (readout fine) — **it is DEPTH, not readout.**

## Root cause — and it is deeper than the star-ladder

Two layers, both mine:

1. **The star CX-ladder** (my `clifford_z0_to_P`: CX(j,0) for all j) centers entanglement on qubit
   0, which cannot be adjacent to all others on heavy-hex → SWAP-routed → 2.2–2.7× the 2q gates of
   a native linear ladder at n=6/8 (measured on fez). A connectivity-oblivious construction.

2. **The deeper, load-bearing one — rows-vs-DEPTH, not rows-vs-jobs.** The pure-state fresh-b
   delivery prepares a **product eigenstate** of P — **ZERO entangling gates**, a shallow
   single-qubit-only prep. The mixed-state delivery pays entangling depth to build the mixture in
   one circuit: ancilla-trace (n−1 CX) + U_C ladder = **6 / 22 / 44 CZ** at n=4/6/8 (measured). The
   observable ⟨P⟩ for a full-weight Pauli is **exponentially fragile** — a single-qubit error
   anywhere flips the parity — so it does not survive that prep depth. At n=4 the signal washed at
   only ~6 CZ, which means even the connectivity-aware linear fix (which helps n=6/8) may not save
   the fundamental fragility.

**The pure-state delivery's row explosion (215 jobs) was the PRICE of a shallow, fidelity-preserving
prep.** The mixed-state "escape" collapsed rows (real, 42×) but inflated prep depth onto the one
axis that determines whether the signal exists. It was a false economy on the binding constraint.

## What I own

- I proposed the mixed-state escape as "cleaner AND cheaper — a better instrument," and
  recommended **B strongly**; the Creator chose it on my recommendation.
- I verified it **three ways LOGICALLY** (exact ρ_P: my scaffold G1, Ember's sealed-P G1, Elder's
  compiled-unitary check) — and **never checked ON-DEVICE FIDELITY.** Logical exactness and
  transpile-*preservation* (Elder's #1030 harden, my #1027 flag) were all about the *structure*
  surviving; none of us checked that the *delivered state* survives real 2q error at the required
  depth. The barrier preserved the CX; the noise on the deep CX washed the state.
- The star-ladder was my construction choice, made for mathematical simplicity without weighing
  heavy-hex routing depth.
- **My "better instrument" claim was wrong on the axis that mattered.** The 215-job pure-state
  delivery I dismissed as an "ugly slog" was fidelity-correct; the ~10-job mixed-state delivery I
  championed was not. I optimized job-count and row-count and missed depth-fidelity.

## The rule this teaches (the net-new lesson)

**ROW-COUNT and CIRCUIT-DEPTH are distinct cost axes; a delivery that is logically exact and
row-cheap can still destroy the signal via prep depth — and for a fragile observable (weight-n
parity, ⟨P⟩ ~ fidelity^depth), DEPTH is the binding constraint.** Concretely:
1. **Verify ON-DEVICE DELIVERED FIDELITY before sealing** — a mandatory pre-flight ⟨P⟩≈1 gate on a
   KNOWN test-P (noise-model sim AND a cheap known-P test flight), not just logical/transpile
   exactness. This is the missing gate; it would have caught the washout at ~$0 before any blind
   spend. (This is the F119 audit's own lesson — verify the delivered artifact, not the idealized
   one — pointed at my own build.)
2. **Account for the rows↔depth tradeoff explicitly** when a "row-collapse" redesign adds entangling
   prep. Cheaper-in-rows can be fatal-in-depth.
3. **Shallow product-state delivery may simply be required** for fragile n-body observables — the
   logistics cost of many small jobs is the honest price of preserving the signal.

## Path forward (honest, uncertain — no band-shopping)

- **The mandatory pre-seal on-device fidelity gate** (rule 1) — build it regardless of which
  delivery wins; it is the gap that let this reach hardware.
- **Connectivity-aware low-depth mixed prep** (linear/tree native entangler; my P-independent lane
  to rebuild) — reduces U_C depth 2.7× at n=8, but n=4 washed at ~6 CZ, so this is **NOT confirmed
  to save the fundamental fragility.** Must pass the rule-1 gate before it is trusted.
- **Revert to the pure-state (shallow) delivery** — fidelity-correct, at the 215-job logistics cost.
  This may be the right answer; the job-count is the price of the measurement, and the earlier
  "escape" was the detour. On the table honestly, not as a fallback of last resort.

## The one clean win here

**It was caught BLIND.** Elder's frozen 3-arm estimator, posted pre-reveal, graded the washout as a
NO-WIN before Ember revealed P. Sealed-commitment discipline held: no post-hoc rationalization was
possible. A real negative, honestly caught, with a defined (if uncertain) path — which is the
mechanism working, even when the instrument I designed did not.

*Booked as F119-arc finding. Credit for the catch: Elder (blind estimator) + Ember (independent
n=4 read + owning the compiled-G1-checks-logical gap). The delivery design + the depth-fidelity
miss are mine.*
