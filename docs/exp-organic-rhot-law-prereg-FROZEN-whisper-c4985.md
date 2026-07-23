# Exp ORGANIC ρ_t-LAW — the magic-tax depth law, pad-free — **FROZEN** (2026-07-23)

**FREEZE RECORD**: Creator go ("the organic redesign — plan it, revisit for gaps and map
structure, then fly"). Ember 2 seals quantum@5385068 (#721: rung0_n40 c65e03a0…, race_n40
cc946213…; GREEN — "removes the artifact rather than trying to twirl it away"; her reveal-time
per-register both-conventions discipline noted). Elder ACK #722, freeze-ready, WITH his own
#715 correction booked (his pad-rule endorsement rested on standard RC theory that does not
apply to pulse-context errors). His residual subtlety ADOPTED into the analysis plan: the
3 depths ride 3 registers, so the slope is read ALONGSIDE the per-register λ heterogeneity row
(4d) — a large λ spread caveats the slope interpretation. This commit is the freeze.**

*Whisper C4985, 2026-07-23, substrate claude-fable-5. Creator directive: "the organic redesign —
plan it, revisit the plan for gaps and adding map structure, then take the flight." Court: same
3-of-3. Path-A device physics; no advantage grading.*

## Plan-phase audit result (the gap-revisit already paid)

Planning surfaced a critical check: **the curve's pads were ALREADY twirled** (twirl_circuit
dresses every CZ), so the C4984 design rule "twirl the pads" was refuted by the flown data
before it was ever tested. A $0 noiseless audit (pad+twirl exactness, 6/6 PASS + control) rules
out a twirl-compensation algebra bug. **Correction booked to C4984's design rule**: the pad
drift is an **RC-RESISTANT coherent error** — context-dependent (back-to-back identical CZ
pairs create an unusual pulse context that randomized compiling's Pauli frames do not alter) —
which sharpens the finding (a structure the standard cure does not cure) and replaces the rule:
*avoid back-to-back identical pad pairs; interleave/shuffle if padding is ever used*. This
flight needs none of that: **the design is pad-free by construction.**

## The design — organic depths from the routing lottery, per-register organic normalization

**Depth variation**: transpile the sealed t=80 circuit over **100 seeds** on kingston → the
full d2q histogram (itself a map deliverable). **Frozen selection rule**: fly the routings at
argmin(d2q), nearest-to-median(d2q), argmax(d2q). Span assert: max−min ≥ 40 slots, else fly
anyway and label NARROW-SPAN (all outcomes deliverables). Every flown slot is organic — no
pads anywhere in the job.

**Normalization (replaces depth-matched twins)**: each selected routing j gets its own
**organic t=0 ladder on its own register** — the t=0 circuit transpiled with initial_layout =
routing j's FINAL layout (final-register overlap ≥ 30/40 asserted + reported), folds
m ∈ {0,1,2} → organic depths {b_j, 3b_j, 5b_j}. Per-register 3-point fit (satisfies the ≥3
rule) gives bias_t0(d) = b₀_j·exp(−λ_j·d); then **ρ_t(d_j) = bias_t80(d_j) /
bias_t0_fitted(d_j)** — INTERPOLATION asserted (b_j ≤ d_j ≤ 5b_j, else the point is labeled
EXTRAPOLATED). Register idiosyncrasies (intercept b₀_j) divide out per register by
construction.

| Block (×3 routings) | Structure | Shots |
|---|---|---|
| READOUT-CAL | all-0 + all-1 (whole chip, once) | 20k |
| t0-LADDER_j | m ∈ {0,1,2} on register j, 4 twirls × 5k | 60k each |
| T80_j | 16 twirls × 6,250 on routing j | 100k each |

~86 pubs, **500k shots ≈ 145–160 s** of ~2,278 s pool. Seals: Ember, 2 fresh strings (rung0_n40
shared by all three ladders — same logical t=0 circuit; race_n40 shared by all three t80
routings — same logical circuit). Exactness gate + logical round-trips standing.

## Frozen rules

1. **Pre-registered hypotheses** (both back in play now the pad confound is removed —
   c4982b's clean pair WAS organic): **H_perslot**: ρ_t(d) = exp(−λ_x·d), λ_x ≈ 0.0013;
   **H_Tlocal**: ρ_t = const ∈ [0.70, 0.85]. **Discrimination**: bootstrap slope CI of ln ρ_t
   vs d over the 3 organic points — CI < 0 ⇒ per-slot (λ_x reported); CI ∋ 0 with mean in
   band ⇒ T-localized; else ⇒ new structure + the sign/shape/overlap localization kit runs
   before any booking.
2. **Conventions (all standing)**: flag-excluded bits (flags pre-listed pre-reveal); BOTH
   estimators, booked only where they agree ≤ 0.03, divergence triggers localization not
   averaging; per-pub 1k bootstrap; calibrated-majority ŝ; two-stage reveal (ladders ŝ →
   rung0 reveal → t80 ŝ → race reveal).
3. **Register labeling**: per-register m0 (shallow, well-shot) exact ⇒ register CLEAN; deeper
   rung misses adjudicated by the shots-limited-vs-dirty cause method (race-6/curve precedent,
   court 2-of-2). Labels attach to points, never silently dropped.
4. **Map-structure deliverables (the Creator's explicit ask), all booked into v1.2**:
   (a) the 100-seed kingston w40/t80 d2q lottery HISTOGRAM (first full routing-distribution
   row); (b) three fresh per-register (b₀, λ_bit) pairs — the intercept-as-register-meter
   decomposition validated across registers on one die; (c) the organic ρ_t(d) law → the v1.2
   t=80 pricing rule; (d) per-register λ variance (die-heterogeneity row); (e) the C4984
   design-rule correction (RC-resistant pad coherence) as a map caveat row.
5. **Named failure modes**: (a) narrow lottery span (< 40 slots) — labeled, curve still
   reported; (b) a register fails CLEAN (labeling per rule 3, point kept with label); (c) a
   t80 bias censors at the deep point (report as bound; fit only if ≥3 uncensored);
   (d) estimator divergence (localization kit, range-not-average). No rescue anywhere.

## Gap-revisit record (pre-freeze, per directive)

G1 pad/twirl algebra — audited, PASS, correction booked (above). G2 per-register t0 pinning —
overlap floor 30/40 asserted per register. G3 selection-by-d2q ignores register quality —
handled by per-register normalization + labels. G4 fold reach — b_j ≈ 55–70 ⇒ m2 ≈ 275–350,
brackets any lottery draw; interpolation assert guards the rest. G5 seals — 2 suffice (shared
logical circuits). G6 — the audit's correction duty executed in this card + C4984 results
file. *Contact: Mike Blakemore.*
