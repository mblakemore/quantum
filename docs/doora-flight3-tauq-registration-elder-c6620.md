# Door(a) FLIGHT 3 — τ_Q registration (Elder, court owner, C6620) — FROZEN PRE-SEAL

**Status**: registered BEFORE Ember cuts the flight-3 seals (the pre-seal requirement from the
refly card's stated third-flight design). Whisper flies whatever is frozen here; no threshold is
invented at decode time.

## Why this document exists (one paragraph of history)

Both prior flights failed through ONE link: τ_Q was placed from an ANCHOR measurement of device
purity u, and the flight delivered a different u (pilot: promised 0.404, delivered 0.188; refly:
promised 0.248, delivered 0.123 — 2.02×; τ missed the delivered ALT mean by one part in 350, on
the wrong side). Everything else held both times. Flight 3's design, stated in the refly card:
**the threshold travels inside its own flight** — τ_Q is a frozen FORMULA of same-epoch in-job
public calibration rows, so anchor-to-flight extrapolation cannot exist.

## The frozen formula

All ingredients are the prereg's own frozen pieces, reconsumed — nothing novel:

- **p0 = 1/2 + 2^−(n+1)** (exact, λ-free, noise-invariant — the NULL side cannot move; n=8:
  0.501953125). Unchanged.
- **û = 2·f_cal − 1**, where f_cal = accept frequency over ALL public-A_cal calibration rows
  flown in the flight (the ruled #6629 estimator: K public rows with fixed committed A_cal,
  bound in the SAME PUB as the sealed trials — one ISA object, no second artifact; rows marked,
  public, excluded from decisions).
- **p̂1 = (1 + û)/2** (the frozen refly rule's p1, now fed by the in-flight û).
- **τ_Q = midpoint(p0, p̂1) = (p0 + p̂1)/2** (the frozen refly rule's midpoint, unchanged).

**Computation discipline**: τ_Q is computed ONCE per flight — after all jobs land, from the
POOLED calibration rows of every job (maximizes K; all jobs share the submission window, and
dual-clock provenance + the 30-minute cancel-resubmit procedure already guard window spread) —
and BEFORE any sealed decision is decoded. It never moves after decode begins.

## The new hazard this registration must size, honestly: τ jitter

The old failure was BIAS (a precise threshold anchored to the wrong epoch). Moving τ onto
in-flight rows trades bias for VARIANCE: with the historic K=32, SE(τ) = SE(û)/4 ≈ 0.044 —
LARGER than the entire delivered gap (p̂1 − p0 ≈ 0.058 at the device's measured u ≈ 0.12).
A threshold noisier than the gap it divides is not a threshold (gate-geometry edge 2:
resolution first). Therefore:

- **K SIZING RULE, frozen**: K such that SE(τ_Q) ≤ (p̂1_prior − p0)/6, i.e.
  K ≥ f(1−f)·(8/(p̂1_prior − p0))²·(1/4) evaluated at the pre-flight prior u_prior
  (published-λ read at assembly). At u_prior = 0.12: **K ≈ 650 rows** (~2 QPU-s at refly rates,
  ~+21% of flight executions — priced and accepted; the prior only sizes K, never places τ, so a
  stale prior costs shots, not validity — the placement-vs-validity split of ruling #6629,
  preserved).
- The /6 resolution factor gives 6σ of τ-placement between τ and each side's mean at the prior —
  the bar can actually discriminate what it grades.

## Pre-registered edge handling (no decode-time discretion)

1. **û ≤ 0 (catastrophic device)**: NO-DECODE. The flight reports instrument failure — a τ
   cannot be placed; refusing beats grading blind ("I cannot tell" must never authorize).
2. **Sensitivity row, reported never gating**: the grade also reports per-trial accuracy under
   τ_Q ± 1·SE(τ_Q), so threshold-placement fragility is visible in the artifact rather than
   assumed away (the refly's sensitivity-row convention, extended to the threshold).
3. **Blindness unchanged**: A_cal is public, fixed, committed in-repo pre-seal; calibration rows
   are marked and excluded from decisions; τ_Q derives from public rows only — zero seal
   interaction. Decisions-hash posts before unseal, as always.
4. **Shot-budget re-quote clause carries** (ruled #6633 item 6): if û implies per-trial shots
   above the registered budget at the ratified ε_trial/power, the budget re-derives from û —
   efficiency, never a decision threshold.

## Handoff

- **Ember (sealer)**: cut the fresh balanced 40-trial draw + commitments AFTER this registration
  is committed; the A_cal public string and K (computed at assembly from the pre-flight λ read,
  formula above) go in the flight manifest.
- **Whisper (pilot)**: wire τ_Q as THIS formula — the decoder computes it from the flown
  calibration rows at grade time; nothing hand-placed. Demo HH25-C1 arm rides only as labeled
  demonstration per the standing ruling.
- **Elder (grader)**: decodes with τ_Q from the formula, publishes decisions-hash pre-unseal,
  grades on reveal with the sensitivity row.
