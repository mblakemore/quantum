# H9-P2 "The Diplomat" — grading-gap closure (Whisper C5007)

*Creator directive: "close the H9-P2 grading gap." Whisper C5007, substrate claude-fable-5. This is the
missing CONSOLIDATED status the C5007 inventory flagged ("witness data in hand but no sealed 5σ
artifact — is the deliverable met?"). It resolves the AMBIGUITY definitively; it is NOT a manufactured
PASS. QEC/witness grading is Elder's grader seat — this consolidates the sourced status and invites his
ratification.*

## The deliverable (verbatim, first-contact doc C5000)
> **P2 — The Diplomat**: cross-block coherence witness (cal-passed λ_hold≈1.0), Δ=¼‖ρ_A−ρ_N‖²_HS.
> First deliverable: **Blind 5σ coherence witness on the RC-resistant pad-drift — or a valid null**
> falsifying the stable-unitary model. Cost class: **1 flight (250s), queued.**

## VERDICT: NOT YET MET — and NOT closeable with data in hand (needs the queued flight)

The formal deliverable is a **blind, sealed, 5σ measurement of the overlap witness Δ** via the AA/NN/CROSS
three-block circuit. **That flight was never submitted** — no such job exists.

Cross-block jobs that DO exist (all CHARACTERIZATION, not the witness main block):
| job (…tail) | card | what it is |
|---|---|---|
| …f2ns90 | `exp_crossblock_cal` | readout calibration |
| …eq5ds0 | `exp_crossblock_depthsweep_B` | mechanism sweep (4-point |⟨Z⟩|) |
| …f30gq0 | `exp_crossblock_driftalive_scout` | drift DETECTION scout |
| …ad58vg | `exp_crossblock_widesweep_B2` | deep-depth revival test |

There is **no `exp_crossblock_overlap` / main-block AA/NN/CROSS manifest or job.** The characterization
circuits measure single-block |⟨Z⟩| depth-decay; they do **not** carry the ancilla-mediated AA/NN/CROSS
overlap structure the Δ witness requires, so the witness **cannot be synthesized from the banked data** —
it needs its own circuit and flight.

## What IS established in hand (the GO-basis for the queued flight — this part is real)
- **Drifter block confirmed**: {phys53, phys26} at drift-DETECTION σ **5.98 / 3.87** (Elder grader read,
  driftalive). ⚠️ This is per-qubit **excess-decay-vs-population** — a DIFFERENT statistic from the
  overlap witness Δ. It sizes/justifies the block; it is **not** the 5σ witness.
- **Coherence evidence**: widesweep (C5005) found coherent **revival** confined to {26,53,73} — evidence
  the drift carries coherent structure, but a single-block non-blind signature, **not** the formal Δ witness.
- **Witness algebra + design margin GRADED**: G1PRIME (Elder) confirmed the estimator/CI/conditional-label
  algebra; `design_margin_c4998` predicts Δ ≈ **0.052 (dephased) – 0.069 (ideal)**, needing **~1961–3481
  meas/class for 5σ**. The flight is design-ready.

## Load-bearing caveats that must ride the eventual grade (from Elder's component grades)
1. **Differential witness** (G1PRIME): Δ=0 if both blocks share the *same* rotation. The claim is only
   "the drifter block carries coherent structure the matched non-drifter lacks."
2. **Coherent-rotation attribution is DESIGN-CONDITIONAL** (matched-systematics budget) — a referee could
   recast a residual readout/purity mismatch as "coherence." Not an unconditional coherence claim.
3. **Mechanism unpinned without purity** (depthsweep grade, RETRACTED decoherent call): |⟨Z⟩|-magnitude
   can't separate coherent-sub-π/2 from incoherent; the clean discriminator is purity-vs-depth (unflown).
4. **Null branch has a REQUIRED gate** (holdchannel): a null (Δ≈0) is valid only if measured
   λ_hold,witness > threshold; else it FOLDS as H-suppressed-ambiguous.

## Closure statement
The "grading gap" resolves to: **the P2 blind-5σ deliverable is NOT met; the witness main-block flight is
queued/unflown (needs QPU, ~250s, behind the floored instance).** The ambiguity ("met but ungraded?") is
removed — it is *unmet, pending flight*, with characterization + algebra + design-margin all GO-ready.
This is the honest closure: not a PASS I could formalize $0, but a definitive, sourced status. When IBM
time returns, this flight is one of the cheapest high-value items queued.
