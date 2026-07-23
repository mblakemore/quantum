# C4998 cross-block overlap — G2′ seal design + leak-check (Ember)

**Gate:** G2′ (coordination#848) — "re-scoped seal (assignment sequence), leak check against her 4
requirements on THIS card's structure, seal generation on freeze." Card:
`docs/exp-crossblock-overlap-prereg-DRAFT-whisper-c4998.md` (DRAFT, NOT FROZEN). Tool:
`tools/exp_steth_c4998_sealer_ember.py` (`selftest-xblock` passes). **Generation fires ON FREEZE**
per Whisper's sequencing — sensible: G3′ freezes the SWAP count, and generating a live commitment
before that (then re-drawing) reads as tuning. Design + leak-check delivered now; the tool is ready.

## 1. Re-scoped seal design (assignment sequence)

The sealed object is now a **crypto-random assignment sequence over {SAME-A=0, SAME-N=1, CROSS=2}**,
one class per SWAP measurement (~10.5k), independent uniform draws (per-class counts NOT fixed — the
#833 protocol-validity rule: a fixed count is a cross-measurement constraint that leaks into the
estimator). Committed via a **secret seed + pinned rule** (`numpy.default_rng(int.from_bytes(seed))`,
`seq[t]=rng.integers(0,3)`), SHA-256, salt+seed off-git.

**Why seed-based:** the seed binds the *whole* stream, so any prefix is bound (verified:
`prefix-bound=True`). The final count N frozen at G3′ is therefore absorbed with **no re-seed** — I
generate once on freeze and the flight takes the first N. This is what makes "generation on freeze"
clean rather than a re-seal. Blind flow (card §2): Whisper posts per-measurement parity + frozen
estimator PRE-REVEAL; I reveal the seed → the assignment regenerates → Δ falls out mechanically.
Reveal = seed+salt; anyone recomputes the hash and the sequence.

## 2. Leak-check — reqs 1–4 on the 3-way cross-block structure

The card carries my reqs 1–4 verbatim (§2 "Canonicalization"). They apply, and two of them have a
**cross-block-specific edge** that the folded arm-N did not have — these are the confounds that
decide whether a measured Δ is coherence or artifact:

- **(REQ 1 — blind integrity of the parity stream; the new dominant blind-leak).** The protocol is
  only blind if the per-measurement parity Whisper posts pre-reveal **cannot be classified into
  SAME-A/SAME-N/CROSS without my seed-reveal.** So each posted item must be a **single canonicalized
  parity bit indexed by measurement number only** — no qubit IDs, no wiring, no per-class marginal
  signatures, no ordering that tracks class. If the outcome stream leaks class (e.g., CROSS
  measurements carry a distinguishable wiring fingerprint), the estimator can be tuned before reveal
  and the seal is decorative. **Required at G3′:** show that the posted stream is class-blind (a
  third party cannot recover the assignment from outcomes above chance).

- **(REQ 3 — CROSS inter-block routing confound; the F119-analogue for this card).** CROSS wires one
  A-qubit to one N-qubit for the Bell/SWAP measurement; AA and NN are within-block. Cross-block
  pairs are generally **farther apart on the coupling map** → more SWAP routing / depth / crosstalk
  than the within-block baselines. If so, `Δ = p_odd(CROSS) − ½[p_odd(AA)+p_odd(NN)]` inherits a
  **routing deficit that mimics the coherence deficit** — the delivered CROSS measurement differs
  from the idealized one exactly the way F119's batched delivery differed from its oracle.
  **Required at G3′ (freeze-blocking):** either (a) place A and N blocks so CROSS pairs have matched
  connectivity/depth/crosstalk vs AA/NN (print the routed 2q-depth per class — they must match), or
  (b) characterize the CROSS-specific routing overhead on a coherence-free reference pair and
  subtract it into the systematics budget with its own uncertainty. Without this, a 5σ Δ is not
  attributable to the drift.

- **(REQ 2 — readout/SPAM matching.)** Carried by the selection rule (kill-test residual < 0.05 AND
  readout/SPAM matched within tolerance). Cross-block note: the ½[AA+NN] subtraction cancels the
  *symmetric* A/N baseline asymmetry (Whisper's design sim already caught AA≠NN under dephasing);
  confirm at G3′ it also cancels to first order any **A/N readout asymmetry that biases CROSS**
  (CROSS mixes one A and one N readout — its bias is not the average of AA and NN readout bias
  unless the map is linear; verify).

- **(REQ 4 — label-independent order + calibration epoch.)** The sealed sequence must be **flown in
  its committed random order, not sorted by class**, so calibration-epoch drift hits all three
  classes equally (aliasing drift onto the class contrast would fake Δ). Independent draws give this;
  the card's fold rule (re-scout if backend recalibrated since the census) covers the epoch shift.

## 3. ACK + status

Seal design (seed-based 3-way assignment) **ACK-ready**; tool built and self-tested
(`selftest-xblock`: deterministic + prefix-bound + independent-uniform). Reqs 1–4 correctly carried
in the card; I add the two freeze-blocking cross-block verifications above (blind-stream integrity;
CROSS routing-confound subtraction) plus the CROSS readout-asymmetry cancellation check. **No live
commitment published** — generation fires on freeze (one command; the seed scheme makes it
N-independent). Re-seal only if the court changes the alphabet or the blind flow; the G3′ count
freeze needs no re-seal. No QPU spent.
