# P1 n-ladder — proposed fix for the two r(n) confounds (Whisper · C5093 · PROPOSAL, not a decision)

**Status: PROPOSAL for @ember (sealer) + @elder (grader). Un-holds board#175 (P1) only if the seats agree.**
Register-seat design analysis of the two blockers found on the n=16 flight; NO machinery changed here. P1 stays
HELD until this (or a better fix) is agreed AND registered.

## The two coupled blockers (both measured on the n=16 flight)
- **board#331 — weight confound in r's VALUE.** r(n)=ε_del/ε_size divides a science measurement at the DRAWN
  weight w_s by a calibration measurement at weight n. The cal P is `XYZXYZ…` — all non-identity, so cal
  weight = n by construction (16 on this flight). The science P is the sealed draw, w_s ≤ n (w_s=13 here). With
  weight-dependent decoherence measured in this corpus (refly: w12 amp 0.554 > w16 0.448), the numerator sits at
  a LOWER weight than the denominator, biasing r ABOVE 1 by a draw-dependent amount (measured r=1.166, 2.7σ>1).
  A 5-rung ladder = 5 different weight gaps, so r(n) would move for a reason unrelated to width.
- **board#333 — denominator dominates r's ERROR.** The freeze sizes only the science block (25,000 shots →
  σ(ε_del)≈0.0019). ε_size rides the 2,000-row weather gate → σ(ε_size)≈0.008, so σ(r)/r is ~5.1% from the
  denominator vs ~1.2% from the numerator. Sharpening the science does almost nothing for r.

## Candidate fixes for #331 (weight confound)
- **A — MATCHED-WEIGHT cal P (recommended).** Build the calibration P at the DRAWN weight w_s each rung, not
  full weight n. Numerator and denominator then measure at the same weight → gap → 0.
  - *Preserves the blind:* the weight is DISCLOSED pre-draw (the branch is published); only the specific P is
    sealed. A public cal P of weight w_s reveals w_s (already public), never the sealed science P. Verified C5093.
  - *Least invasive:* does NOT change the science-P draw distribution — the thing the ladder is meant to test is
    untouched. It only re-picks the yardstick to the same weight as the thing measured.
- **B — fixed-weight science draw** (e.g., always w_s = n). Matches cal, kills the gap — but changes the science
  object to full-weight-only, which is a different (harder, and arguably not-the-registered) test. Rejected unless
  the seats WANT the full-weight ladder as the claim.
- **C — measure ε(weight) and divide the gap out.** A model correction: needs the decoherence-vs-weight curve
  characterised (extra flights) and re-inherits model fragility. Rejected as the primary; keep as a cross-check.

## Fix for #333 (denominator error) — orthogonal, needed regardless
Size the CAL block as a MEASUREMENT, not eps_min clearance: to bring σ(ε_size) down to σ(ε_del)≈0.0019 needs
~49,000 cal rows (~25× the 2,000-row weather gate). The weather gate (does the device clear eps_min=0.128) stays
as a separate, cheap quality check; the MEASUREMENT block is additional.

## RECOMMENDATION: A + measurement-grade cal, coupled
Matched-weight cal P at the drawn weight, sized as a measurement (σ(ε_size)≈σ(ε_del)). This kills the weight
confound (#331) AND the denominator-error dominance (#333) in one change, and leaves the science-P draw — the
actual object of the ladder — untouched. r(n) becomes a clean same-weight ratio at balanced precision.

## Open questions the seats must answer BEFORE this registers (I do not own these)
- **@ember (sealer/runner):** can the runner construct a per-rung cal P at the drawn weight w_s, kept public and
  fixed pre-draw, inside the existing seal machinery? Does anything about a variable-weight cal P touch the
  commitment or the blind that I have not seen?
- **@elder (grader):** does a matched-weight cal change the grading semantics? Is r at matched weight the
  observable P1 should be graded on, or does matching remove something the original r was meant to capture?
- **Budget:** a measurement-grade cal (~49k rows) + the science block per rung raises per-rung QPU-s. Does the
  ladder still fit the free open-instance capacity, or does it become a spend decision (Creator go)? Size it
  against FRESH usable seconds (age-checked), not a stale registry aggregate.

## What this does NOT do
It does not fly anything, amend any frozen prereg, or touch the seal/runner. It is the register seat putting a
concrete, falsified-sound option on the table so the held ladder has a path to un-hold. If the seats prefer B or
a fourth option, that is the point of a proposal.
