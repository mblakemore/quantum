# Exp ρ_t-CURVE — clean multi-depth magic-tax law — **FROZEN** (2026-07-23)

**FREEZE RECORD**: Creator go ("Fly the clean multi-depth rho_t curve"). Ember 2 seals
quantum@df02012 (#694: rung0_n40 73e941b3…, race_n40 de55b58e… shared by all 3 padded t80 arms;
GREEN — "pad-not-fold is the right discriminator"). Elder ACK #695, freeze-ready, WITH
conflict-of-interest disclosure on the record: H_perslot is HIS reading from an under-powered
2-point cross-die fit; he pre-commits to grading its falsification straight ("this flight
should SUPERSEDE my 2-point reading REGARDLESS of outcome"). This commit is the freeze.**

*Whisper C4983, 2026-07-23, substrate claude-fable-5. Creator directive: "Fly the clean
multi-depth rho_t curve." This is the named open question of map v1.1.1 (Elder #689: "clean
multi-depth curve (≥3 clean points) remains the named open question"). Court: same 3-of-3.
Path-A DEVICE PHYSICS flight — no advantage grading, no WIN rule, no classical arm; the
deliverable is a measured law.*

## The question, pre-registered as hypothesis discrimination

At fixed T-count (t=80), how does the magic tax ρ_t depend on depth? Two hypotheses from the
c4982b clean pair (0.801@167 kingston / 0.754@217 marrakesh):
- **H_perslot** (v1.1.1 refined reading): ρ_t(d) = exp(−λ_x·d), λ_x ≈ 0.0013/slot.
  Prediction at the three flown depths: computed at freeze from the drawn d₀.
- **H_Tlocal**: ρ_t(d) = constant ≈ 0.75–0.80 (tax attaches to the 80 T-gates, not the slots).
**Frozen discrimination rule**: fit ln ρ_t vs d over the ≥3 clean points (both estimators,
flag-excluded bits per the c4982b convention, 1k-pub bootstrap on the slope): slope CI excludes
0 ⇒ per-slot (report λ_x); CI includes 0 with mean ρ_t ∈ [0.70, 0.85] ⇒ T-localized; anything
else ⇒ new structure, reported as measured. All three outcomes are deliverables.

## Design — one circuit, three depths, T-count pinned

The key trick (reusing the race-6-validated twin machinery): **pad, don't fold**. Folding a
t=80 circuit triples its T-count; padding with its OWN 2q-layer pairs (L·L = I, dose-matched,
crit-path-advancing — the build_twin padding) adds pure Clifford depth at **fixed t=80**.
- Draw d₀ = best-of-100 kingston routing of the t=80 race-class circuit (clean best-of rule
  NOT needed — no exclusion list on kingston; the pre-gate + flags govern).
- Depths: **d₀, d₀+60, d₀+120** (even offsets preserve parity). Each depth gets a matched pair:
  t=0 twin (padded t=0 source, race final layout, overlap ≥30/40, parity-feasible selection)
  and t=80 arm (padded race circuit).

| Block | Structure | Shots |
|---|---|---|
| READOUT-CAL | all-0 + all-1, measure_all | 20k |
| LADDER | m ∈ {0,1} of the t=0 source, 4 twirls × 5k | 40k |
| TWIN(d₀), TWIN(d₀+60), TWIN(d₀+120) | t=0, 8 twirls × 6,250 each | 3 × 50k |
| T80(d₀), T80(d₀+60), T80(d₀+120) | t=80, 16 twirls × 6,250 each | 3 × 100k |

~74 pubs, 510k shots ≈ **145–165 s** of ~2,427 s pool. Die: **kingston** (clean-class proven;
single-die requirement of the curve). Seals: Ember, 2 fresh strings (rung0_n40 for
ladder+twins; race_n40 for all three t=80 arms — same string, same logical circuit, purely
padded). Exactness gate + logical round-trips as standing.

## Frozen rules

1. **CLEAN-LADDER PRE-GATE (labeling, not abort)**: both ladder rungs exact ⇒ the curve is
   booked CLEAN. Ladder not exact ⇒ the flight still measures but every point is labeled
   CONFOUNDED (register), the curve is NOT booked as the clean law, and a re-fly on the other
   die is the named follow-up. (No race grade exists here, so no seal-consumption risk; reveals
   proceed either way after ŝ posts.)
2. **ρ_t per depth**: flag-excluded bits (calibration flags pre-listed before reveal), BOTH
   estimators (signed-toward-s and unsigned |frac−0.5|) — booked only where they agree within
   0.03 (the c4982b convergence criterion); a divergence triggers the #634 localization
   playbook before booking.
3. **Decoder**: frozen calibrated per-bit majority (race-4 lineage) for ŝ + HD reporting;
   two-stage reveal (ladder+twins ŝ → rung0 reveal → t80 ŝ → race-string reveal).
4. **Named failure modes**: (a) dirty register (rule 1 labeling); (b) padding non-convergence
   (abort pre-submission, card 8c class); (c) a t80 arm decodes so poorly that bias ≈ 0 at
   d₀+120 (deep-point censoring: report as upper bound, fit on remaining points only if ≥3
   clean points remain, else curve INCOMPLETE — booked as measured, no law).
5. No QPU beyond this job without a fresh card. QPU after ≈ 2,262–2,282 s.

## Fences

Device physics on one die, one calibration window, one instance family; ρ_t is an aggregate
per-bit bias ratio on flag-excluded bits — not a fidelity, not an advantage claim; F120/F121
untouched. λ_x, if measured, feeds the map's pricing rule (v1.2). *Contact: Mike Blakemore.*
