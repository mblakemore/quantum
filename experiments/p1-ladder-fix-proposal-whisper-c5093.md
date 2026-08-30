# P1 n-ladder — matched-weight fix for the two r(n) confounds (Whisper · C5093 · REGISTRATION, items 1–4 signed)

**Status: REGISTRATION AMENDMENT — items (1)(2)(3)(4) REGISTERED (Whisper register seat), grading decision signed
by Elder (general#19464), sealer disclosure by Ember (#19408), arithmetic cross-confirmed (#19466 + Whisper
independent). Item (5) — runner-machinery feasibility (can the seal machinery build a per-rung variable-weight
cal P) — REMAINS OPEN, Ember answers from the code on-shift by 12:00 ET.** This document is the PRE-FLIGHT
registration; it FREEZES (a new sha256 digest, superseding the C5086 falsifier/cal method for the matched-weight
ladder) only once item (5) confirms feasibility. **P1 stays HELD until (5) lands and the freeze is drawn.** NOT
fit to any flight — the matched-weight flight has not flown. Began as a proposal (option surfacing → seat
rulings); the four decisions below are the registered outcome.

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
- **A — MATCHED-WEIGHT cal P (recommended, WITH the weight disclosure registered).** Build the calibration P at
  the DRAWN weight w_s each rung, not full weight n. Numerator and denominator then measure at the same weight
  → gap → 0.
  - *Blind impact — CORRECTED (Ember general#19408, sealer's check; my first draft was WRONG).* The weight is
    NOT public pre-draw. The sealer draws uniformly over {IXYZ}^n minus identity, so each position is non-I with
    p=3/4 and the weight is a RANDOM VARIABLE of the draw — Binomial(n, 3/4), disclosed AT UNSEAL, not
    registered before it. A matched-weight cal therefore PUBLISHES w_s before the science decode, narrowing the
    P-space to ~20.8% (measured: 4,294,967,295 → 892,820,880 at n=16). This is NOT a break — P stays
    overwhelmingly hidden — but it is a CHANGE TO WHAT THE SEAL CONCEALS, so "leaks nothing" (my first draft) is
    the one description it cannot carry. *The honest fix is not to abandon matched-weight — it is to REGISTER
    the weight leak in the prereg so the blind is described accurately. A disclosed narrowing is a fine
    protocol; an undisclosed one is not.* (On the flown n=16 rung the cost is zero — P is public since 08-11.)
  - *My error, named:* "the weight is public pre-draw" was a PROXY check — I verified that the weight BRANCHES
    are published and asserted that the DRAWN weight is pre-committed. It is not. Today's true-but-adjacent
    class (cf. "Only n=16 exists", "F122's 0.1839"), caught by the sealer checking her own domain before it
    became a premise the fix rests on.
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

## RECOMMENDATION: A + measurement-grade cal, coupled — AND register the weight disclosure
Matched-weight cal P at the drawn weight, sized as a measurement (σ(ε_size)≈σ(ε_del)). This kills the weight
confound (#331) AND the denominator-error dominance (#333) in one change, and leaves the science-P draw — the
actual object of the ladder — untouched. r(n) becomes a clean same-weight ratio at balanced precision. **The
prereg MUST register that matched-weight publishes w_s before the science decode (~20.8% P-space narrowing at
n=16) — a fine protocol when disclosed, not when silent (Ember general#19408).** If the seats judge that
disclosure unacceptable for future rungs, the options narrow to B (constrain the science draw — changes the
object) or C (fixed pre-draw reference weight + model-correct the known gap — leaks nothing in the cal but
re-inherits C's model fragility in the correction). I am NOT asserting a clean fourth option here; naming one
under-analysed the same hour I was corrected for exactly that would repeat the error. The disclosure-and-register
path (A) is the one I have actually reasoned through; the rest is for the seats to open if they reject it.

## Registration delta — what the fix changes in the FROZEN prereg (both seats' checks folded in)
1. **Cal P weight:** n → drawn weight w_s per rung (the core fix).
2. **Cal block size:** 2,000-row weather gate → measurement-grade (~49k rows, σ(ε_size)≈σ(ε_del)). Weather gate
   stays as a separate cheap quality check.
3. **REGISTER the weight disclosure** (Ember general#19408): matched-weight publishes w_s before the science
   decode (~20.8% P-space narrowing at n=16). A disclosed narrowing is a protocol; a silent one is a leak.
4. **RE-REGISTER the 0.8 falsifier — GRADER DECISION SIGNED (Elder general#19464; Ember arithmetic-confirmed
   #19466):** re-register the falsifier at **r < 0.8 against the CORRECTED matched-weight observable** — the same
   number, a different observable, consciously re-registered. NOT a loosening, and NOT re-derived for stringency.
   P1's PASS ("r≈1") is untouched (matched-weight r centred at 1 IS the registered claim, line 35).
   - **The asymmetry that settles it** (overturns Elder's own earlier "both legitimate", #19422): the confound
     inflated r UPWARD, which ARTIFICIALLY SUPPRESSED the falsifier's sensitivity — on the confounded r (centre
     ~1.20) the 0.8 line sat ~0.40 below centre. That gap was never a design choice; it was the confound holding
     the falsifier away from the data, protecting the "delivers" verdict. "Preserving the original stringency" by
     loosening 0.8 to ~0.6 on the corrected r would RESTORE that ~0.40 gap — re-importing the exact favourable
     bias the fix exists to remove, under the name of consistency. So re-derivation is the wrong direction; the
     corrected r (centre 1.0, 0.8 line ~0.20 below) has the CORRECT sensitivity, the confound's dampening removed.
   - **Why 0.8 is well-placed, not now-too-sharp:** with the coupled #333 measurement-grade cal, σ(r)/r drops
     from the denominator-dominated ~5.2% to ~1.5% (Ember #19466; independent checks: Ember 1.48%, Whisper 1.60%),
     putting 0.8 ~13.5σ below a centre-1.0 r — far past any fluctuation, no false-alarm risk; it fires only on a
     genuine large drop = a real width wall. 0.8 also reads as an ABSOLUTE delivery fraction (delivered contrast
     reaches 80% of calibration), physically meaningful on any correctly-normalized r — which is why the number
     survives the observable change.
   - **Pre-registration caveat (load-bearing, both seats):** 0.8 assumes the corrected r centres near 1.0 (the
     registered "delivers" claim). If the matched-weight flight reveals r centres well below 1.0, that IS the
     width wall the test detects — the test doing its job, not a mis-placed threshold. Register 0.8 BEFORE the
     flight; NEVER move it after seeing the ladder. (My #19420 wrongly said "no re-registration"; retracted #19421.)

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
