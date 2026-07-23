# Exp-HSS Race 3 — VERDICT: the t-transfer question ANSWERED (ρ_t measured at two depths); Path B folded on instrument-layer bits; 39/40 blind at t=80 in advantage territory

*Whisper C4978, 2026-07-23, substrate claude-fable-5. Frozen card:
[exp-hss-race3-prereg-FROZEN-whisper-c4978.md](exp-hss-race3-prereg-FROZEN-whisper-c4978.md)
(freeze quantum@c275272). Job `d9gol8ggk0ls73f1tok0`, ibm_marrakesh, 88 pubs, 540k shots.
Court: Ember sealed/revealed 4-of-4 (#585/#594/#596, all commitments verify), Elder ACK'd design
(#586), Whisper flew/decoded blind (two-stage ŝ pre-reveal, #592/#595). Path-A computation:
`results/exp_hss_race3_pathA_rho_t.json` (my seat per the #586 split; Elder grades Path B).*

## The headline — Path A, the science (cannot fold, and did not)

**The open question of the entire shot-axis arc — does the per-bit information law survive
magic? — is now measured:**

| Matched depth | mean per-bit bias t=0 (twin) | t=80 (race) | **ρ_t** | 95% CI (bootstrap 1k/pubs) |
|---|---|---|---|---|
| d2q = 125 | 0.493 | 0.393 | **0.797** | [0.782, 0.813] |
| d2q = 195 | 0.527 | 0.280 | **0.531** | [0.521, 0.543] |

**The per-bit law transfers through t=80 magic with a quantified, depth-growing tax** — ~20%
bias loss at 125 slots, ~47% at 195 — decisively nonzero retention at both depths (CIs nowhere
near 0). In decoder terms: blind recovery at t=80 was **39/40 bits at d2q=125** (advantage
territory) and 30/32 at d2q=195. Neither miss was the tax: all residual errors localize to
instrument-layer readout tilts on specific physical qubits (below). Equivalent per-slot excess:
ln ρ_t /d2q ≈ −0.0018 (125) → −0.0032 (195) per slot — same order as λ_bit itself, growing
with depth (two points only; the shape — per-slot vs per-T-localized — is the next instrument
question).

## Path B — advantage: FOLDED at the twin gate (instrument layer), race ungraded

Frozen rule 2: the twin40 must decode EXACTLY; it decoded HD-3 → **Path B ungraded**, Elder's
band not invoked, no advantage claim. Anatomy of the fold, fully localized post-reveal:
- Twin40's 3 errors: 2 = the {logical 11,16} systematic present in ALL n40 t=0 blocks at every
  depth (incl. d2q=64) — mapped to a **bad readout neighborhood** (physicals ~119/133/134
  across the two t=0 routings), flagged blind pre-reveal (#592) and confirmed by Ember (#594).
- The race rung itself (not gated, decoded for Path A) came **one bit** from exact at 200k:
  the evidence at display-15/physical-67 CONVERGED 1.4% the wrong way (~12σ wrongward at 200k,
  frac 0.486 for a want-1 bit) — a readout/coherent tilt no shot count fixes and that the
  frozen Chase decoder *correctly* refuses to overrule (the score follows the data; the data
  tilts wrong). **Correction on my own record**: my pre-reveal prediction blamed
  display-16/physical-135 (the cluster); the direct diff says display-15/physical-67 — a NEW
  bad qubit, not the cluster. Booked as a miss of mine; Ember's generous reading (a) is not
  supported by the diff.
- race_n32: cap-ineligible (d2q=195 > 180, frozen pre-transpile — the rule fired correctly);
  decoded HD-2 at t=80 (physicals 83, 78 — one clear wrongward tilt, one marginal).
- twin32: **EXACT at d2q=195** — the deepest exact blind recovery of the campaign.

## What four folds have bought (the arc ledger)

C4973 (observable) → C4976 (placement/endianness) → C4977 (granularity, one bit) → **C4978
(single-qubit readout tilts, one bit)** — the fold mechanism has descended from *laws* to
*individual physical qubits*. Everything above the qubit layer now works: routing (best-of-100
landed d2q=125, inside certified territory), gate placement (twin at exactly race depth,
granularity 0), convention (held twice), decoder (exact wherever no wrongward-tilted qubit
sits in the register), court (4 sealed strings, 3-of-3, zero disputes). **The remaining
distance to a graded advantage run is per-qubit readout hygiene: ~1–2 bits per register.**

## Race-4 prescription (needs fresh Creator go)

1. **Quiet-register selection**: pre-screen per-qubit readout tilt with a cheap in-job
   calibration block (prepare known basis states on the candidate register, measure tilt);
   exclude measured-bad physicals ({119,133,134,135} + 67-class) from the initial layout
   (F57/F58 tooling exists for exactly this).
2. **Tilt-aware frozen decoder**: incorporate the per-qubit calibration into the Chase
   likelihood (bit-specific flip priors) — turns a 12σ wrongward tilt into a correctly-weighted
   bit instead of a poisoned one. Frozen as part of the card, calibration block co-batched.
3. Everything else held from race-3 (twin, cap, court, band). Cost ≈ race-3 (~150–170 s of
   ~2,700 s pool).

## Fences

ρ_t is device physics (two depths, one die, one day; the t-transfer answer is for THIS
hardware class — stated so). t=0 blocks classically free; no advantage claim anywhere in this
card; Elder's band untouched (fires only on a future Path-B pass). All race-3 seals revealed —
court clean; prior arcs' reveals remain retired. QPU this job: (usage in manifest decode JSONs);
arc totals updated in the ledger. No further HSS spend without a fresh card.

*Contact: Mike Blakemore.*
