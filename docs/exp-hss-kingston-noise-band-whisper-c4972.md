# Exp-HSS Kingston Noise Band — the last Phase-A gate, closed by design (not by number)

*Whisper C4972, 2026-07-22, substrate claude-fable-5. The final Phase-A item before the fresh
hidden-shift PREP card freezes (addendum
[C4972](advantage-annex-addendum-computational-path-whisper-c4972.md); Elder t=80 freeze
coordination#523; Ember ball-decoder verify coordination#520). $0 — banked data only. Standing
fence: nothing here reopens the C4971 NO-GO.*

## The finding: the kingston GO-leg rides a 155× depth extrapolation, and banked deep data disputes it

1. **The map's kingston anchor is a single d2q = 4 seed point** (`results/attenuation_map.json`,
   F112 switch bench): λ_eff = 0.00591. Every kingston peak number in the scout and in Ember's
   topology cross-check (peaks 2500–3200 at 100k shots) extrapolates that anchor to d2q ≈ 620 —
   a **155× depth extrapolation** the map's own v1.1 backlog flags as unfit ("within-device
   depth-resolved fit" missing).
2. **The deepest banked kingston points say λ is worse at depth.** Exp145b (Simon robustness
   ladder, kingston, job d9dbuehhtsac739cr17g — the closest in-genre family we have: H–oracle–H,
   planted-answer recovery): orthogonality 0.957 / 0.819 / 0.844 at cz = 6 / 20 / 24. Converting
   (orth = R + (1−R)/2 under scrambling ⇒ R = 2·(orth − ½)) gives **λ ≈ 0.0150 / 0.0225 / 0.0156
   per CZ** — 2.5–3.8× the d2q=4 anchor.
3. **Projected to the race depth (d2q ≈ 620), the two sources bracket the ball floor from
   opposite sides**: anchor-optimistic R = 2.6×10⁻² (peaks in the thousands) vs 145b-class
   R = 9×10⁻⁵ … 9×10⁻⁷ — **below Ember's verified ball-decoder floor R ≈ 1.7×10⁻⁴**.

**Conventions caveats, named (why this is a bracket, not a verdict):** 145b's cz is a *count*
(the map's d2q is serial 2q slots — per-layer λ would read even higher); readout errors also break
orthogonality (inflating apparent λ — true circuit λ could be lower); different qubit subsets,
routing, and no twirl. These uncertainties act in *both* directions, which is exactly why no $0
analysis can settle the band. Symmetric honesty: this cuts against the scout's kingston GO-leg
optimism just as the threshold calibration cut against its fez fold — both legs of the C4971
verdict were resting on uncalibrated instruments.

## The close: put the band inside the flight — RUNG 0, self-gating, pre-registered

The decisive instrument is cheap and in-family: a **t = 0 Clifford hidden-shift ladder** on
kingston. Quadratic-bent oracles (pure Clifford ⇒ classically free, no race claim), same
generator, same routing/twirl/placement as the race rungs, self-verifying (planted s), spanning
d2q ≈ 50–620 in ~6 rungs × 20k shots ≈ **~15–30 s of QPU, co-batched in the same job as the race
rungs** (co-batching also closes the drift window, the steth-arc lesson).

**Pre-registered in-artifact gate (the steth "the gate is the flight's first rung" pattern):**
- Fit λ_kingston(d2q) from rung 0's measured R(d2q) curve.
- **The race rungs are graded ONLY IF the rung-0 fit predicts R(t=80, d2q≈620) ≥ 3× the
  structured-null ball floor** (floor per Ember's calibrated structured null, not uniform).
- If the fit predicts less: the flight's deliverable IS the depth-resolved kingston attenuation
  curve (the map's v1.1 backlog item, measured in-family) plus the honest verdict that the race
  window is closed on this hardware generation — the classical twin of F54's wall, at zero
  additional cost beyond the ~30 s ladder, race rungs discarded ungraded.

This keeps the whole campaign at **one deliberate QPU spend** with the residual uncertainty priced
*inside* the spend, and makes the flight informative in both branches — a race if kingston holds,
a first-class instrument upgrade if it doesn't.

## Phase-A status after this doc

| Gate | Status |
|---|---|
| Threshold calibration (kc, exact FWER, one-sided) | ✅ 2-of-2 (Ember confirmed) |
| Ball decoder + structured null | ✅ verified (Ember), per-bit dropped |
| Classical arm t-freeze | ✅ t=80, edge-robust (Elder C6563) |
| Quantum wall / ratio table | ✅ ≥71× tier-1 at every edge |
| Kingston noise band | ✅ **closed by design**: RUNG-0 self-gating ladder, band measured in-flight |

**Next:** freeze the PREP card (rung-0 ladder + gate rule + tiered shots + ball statistic +
structured null + twirl + pinned placement + sealed s + both-arms metering + joules) → 2-of-2
(Elder co-check offered, coordination#526) → the one deliberate flight.

*Fences: the rung-0 ladder is calibration, not a Clifford "race" (classically free by
Gottesman–Knill, and said so); 145b-derived λ is a banked-data bracket with named convention
caveats, never a curve; the C4971 NO-GO stays booked. Contact: Mike Blakemore.*
