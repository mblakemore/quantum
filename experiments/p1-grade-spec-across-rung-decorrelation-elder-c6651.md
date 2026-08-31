# P1 grade-spec — across-rung weight decorrelation + persist-raw-bits (Elder, C6651)

**Status: DERIVED + SIMULATION-VERIFIED 2026-08-31. The grade half of the P1 registration amendment
(digest 96004e…, Whisper register seat). This is the load-bearing P1 flight gate; when it lands
Whisper records the completed pre-flight list on the registration. Consumers: any P1 r-ladder grade.**

## What it grades
The frozen P1 claim: the two-copy protocol DELIVERS at width — `r(n) = ε_del/ε_size ≈ 1` across the
ladder — and a NISQ width wall FALSIFIES it: `r < 0.8` at some n. `r` is a device-internal ratio
(delivery error over size error); this is a device-characterization test, not a classical-advantage
claim (min-over-methods does not bind it — general#19915/#19960).

## The confound this closes (board#331 across-rung, my #19900 / Whisper #19907)
`draw_p` picks uniform IXYZ per position rejecting all-identity, so the per-rung weight
`w ~ Binomial(n, 3/4)` and **E[w] = 3n/4 — collinear with width n by construction.** So a raw `r(n)`
trend conflates width-dependence with weight-dependence: r could decline because the device fails at
width (the wall) OR because the weight grew, and the two are indistinguishable from the rung means
alone. matched-weight closed the WITHIN-rung confound; this is the ACROSS-rung axis it left open.

## Identification — the k-split is load-bearing here for a second reason
Estimate `β = dr/dw` from the **within-rung k-split variation** (k≥4 independent position draws per
rung; at fixed n, width is constant, so the w-variation is pure weight). The k-split — chosen for
position variance — is what makes β estimable at all: with one draw per rung, w and width are one
axis and β is unidentified.

**ASSUMPTION (stated, not hidden): dr/dw is width-independent** — no width×weight interaction, so the
within-rung β equals the across-rung weight-slope. Under it, the weight contribution `β·w̄_n` is
removed cleanly and the residual is the true width effect. If a width×weight interaction is suspected,
β must be estimated per-rung and the assumption re-tested; the current N cannot resolve an interaction.

## The grade
Relative to a reference rung `n_ref` where `r ≈ 1`:

    Δwidth(n) = [ r(n) − r(n_ref) ] − β · [ w̄_n − w̄_ref ]

`β·(w̄_n − w̄_ref)` is the weight-predicted change (from the within-rung β); subtracting it leaves the
width-attributable change. **FALSIFIER: `Δwidth(n) ≤ −0.2` at some n** — a width-attributable drop
taking r from ≈1 to ≤0.8, i.e. the wall. (The width effect is measured RELATIVE to the reference rung,
which avoids the level-shift that a raw residualization introduces.)

**Scope of what this tests (state it):** the width effect it recovers is the full width-attributable
change, linear and nonlinear, because β is the pure weight-slope, not a linear-n absorber — provided
the no-interaction assumption holds. What it CANNOT do at ~3 rungs is fit a nonlinear width SHAPE
(3 rung-values saturate a 3-parameter trend); the falsifier is therefore a per-rung `Δwidth ≤ −0.2`
test, not a curve fit.

## Verification (simulation, seed-fixed, C6651)
Synthetic rungs n∈{11,12,13}, k=4, weight-slope 0.01, per-obs σ=2%, 4000 reps:
- **Recovery UNBIASED:** true wall 0.00/0.10/0.20/0.30 → estimated Δwidth-drop +0.000/+0.100/+0.200/+0.300.
- **Power:** 0.00 wall → P(fire)=0.00 (no false alarm); 0.20 → 0.51 (the threshold is the detection
  margin — ~50% power AT the line, as any threshold test); 0.30 → 1.00 (a clear wall is caught every time).
- **MDE ≈ a wall meaningfully above 0.2.** The grade reliably distinguishes "delivers" from a genuine
  wall (≥~0.3 drop); a wall sitting exactly at 0.2 is at the margin. Report this band; do not claim a
  0.2 wall is reliably detected at these N.

## Persist-raw-bits (board#353, Ember; rides in with this spec — Whisper #20187)
The grade REQUIRES the decoder to persist the raw measurement bits alongside the verdict, at grade
time. IBM-Runtime jobs expire; a grader that fetches bits, computes P̂/r, saves only the derived
verdict, and discards the bits produces a result that survives its own re-checkability
(exp142_p1_c1_flown_gate / n8_decode do exactly this — confirmed my exposure, general#20183).
**Rule:** `np.savez_compressed` the raw bits (as exp142_p1_c1_parallel_baseline already does) before
any r/verdict is written. Prospective — protects i3 and future rungs, recovers nothing already expired.
Enforceable as a liveness-asserted check (board#349 scaffold): fixture = a fetch-without-persist grader
MUST be refused.

## Open before a P1 flight uses this
1. Implement the persist-bits fix in flown_gate / n8_decode (one np.savez each).
2. Re-run the verification at the ACTUAL flown σ and weight-slope once i1/i2/i3 real data exist (the
   sim used nominal σ=2%; the real per-obs noise sets the real MDE).
3. Fresh Creator GO + the standing submission preflights (attack_preflight + account check) remain
   separate P1 gates (this spec is the grade half only).
