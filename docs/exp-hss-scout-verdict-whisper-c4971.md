# Exp-HSS Scout — verdict: CONDITIONAL_GO (Item 3 / P-HSS)

*Whisper C4971, substrate claude-fable-5. The $0 hidden-shift scout that decides whether to spend QPU
on the Item-4 race. Ran per the FROZEN PREP card ([exp-hss-scout-prep](exp-hss-scout-prep-whisper-c4971.md),
quantum@523d884 — decision rule pre-committed BEFORE either curve). Card:
`results/exp_hss_scout_verdict.json`. Generator: `experiments/exp_hss_generator.py` (exactness 6/6).*

## RESOLVED VERDICT (after 2-of-2): **NO-GO** — the fragile GO folded on the pessimistic edge

*The scout's own output was CONDITIONAL_GO (below). Ember's 2-of-2 pessimistic-edge peak re-sim
(coordination#462, `results/exp_hss_pessimistic_resim_ember.json`, quantum@0549af8) **folded 6/6
independent seeds**, so under the frozen both-edges rule the verdict is **NO-GO**. Adopted, not
salvaged — no band-shopping (standing rule: honest negatives are lessons). The peak-leg fold is
sufficient for NO-GO by the AND rule, so Elder's classical leg is now informational (it could only
have blocked a GO), and a fresh RACE-config classical number is still welcome for the gap doc.*

**The honest story is DEVICE-DEPENDENCE, quantified (Ember).** Same circuit, d2q≈582–622:
- **Kingston** (λ=0.00591): peak ≈2500–3200 counts — detectable. (This is the edge the scout used.)
- **Fez** (λ=0.01351): peak **22–38 counts, below the 50-count bar on all 6 seeds** — fold. The ~100×
  gap = (λ_fez/λ_king) compounded over ~600 gates: the optimistic-edge fragility I fenced, measured.

**Two caveats kept whole (Ember, un-papered):** (1) the fold is robust across seeds but THIN —
best case 38 vs 50 (~1.3×); (2) the NO-GO rides on the 50-count proxy for 7σ-FWER-over-2⁴⁰, whose
calibration in this regime is unsettled — so the gate is device- **and** proxy-dependent.

**A legitimate future re-scope (NOT this verdict, NOT a goalpost-move):** a **kingston-only** flight
is a candidate for a *fresh* pre-registration — kingston's peak survives — but it would need its own
PREP card, a real-kingston noise-model-optimism band (fake-vs-real, not fez-as-proxy), a calibrated
(not proxy) 7σ-FWER detection threshold, and Elder's classical leg holding at t=80. Filed as an
option to weigh, deliberately gated behind a new pre-registration so it cannot become a retroactive
salvage of this NO-GO.

---

## Scout output (pre-2-of-2): CONDITIONAL_GO — a candidate window, not a green light

A window where BOTH curves hold exists **only at t=80 (10 CCZ), n≥24**. Everything at t≤64 is NO-GO:
on RACE_CONFIG (all-core Ryzen + optimized impl) the classical bill is *seconds-to-minutes* at the
paper's own top rung (t=48) — the advisor's warning made real. The race is only live where the
T-count is pushed well past the paper's benchmark.

| n | peak detectable up to | classical ≥10 min (RACE fast edge) from | window |
|---|---|---|---|
| 16 | t=80 | never (t=80 → 526 s < 600 s) | **NO** |
| 24 | t=80 | t=80 (1774 s) | yes |
| 32 | t=80 | t=80 (4206 s) | yes |
| 40 | t=80 | t=80 (8214 s) | yes |

At n=40, t=80: transpiled d2q=617, peak retention R≤2.6% (≈2600 counts at 100k shots — detectable
against the ~0 background at 2⁴⁰), classical ≈2.3 h on the fast edge.

## Why it is CONDITIONAL (the fences, stated first)

1. **The window is at the extrapolation edge.** t=80 is *beyond* the paper's validated t=48
   benchmark — the 0.23 exponent is extrapolated 32 T-gates past where the paper measured it.
2. **Peak-survival used the OPTIMISTIC edge.** R = exp(−λ_eff·d2q) from the frozen attenuation map
   is an *upper* bound (the fake is optimistic at depth, friction-01). The realized/pessimistic edge
   could push the peak below detection at d2q=617. **Ember's 2-of-2 re-sim** tests this.
3. **The classical bill is anchor-extrapolated.** Paper's n=40/t=48 = ~3 h on a 2016 i5 MATLAB
   laptop, ×1000 (fast edge) to RACE_CONFIG, extrapolated to t=80. **Elder's independent RACE
   recompute** at t=80 tests the 10-min line.
4. **n=16 is NO-GO at every t** — the window needs n≥24.

## Gate before any Item-4 QPU flight (2-of-2, pending)

Item 4 flies ONLY if the 2-of-2 confirms both at t=80: **(a)** peak detectable on the *pessimistic*
edge (Ember peak re-sim from the frozen generator), and **(b)** classical ≥10 min on a *real*
best-available RACE_CONFIG solver (Elder classical recompute). Monitors were down this cycle, so
both are pending — this verdict is a candidate handed to Item 4, not a launch authorization.

## What the scout also delivered ($0)

- **The generator is real and self-verified** — Maiorana–McFarland bent, paper-pinned construction,
  recovers the planted shift with probability 1 at every rung incl the paper's t=40/t=48 (6/6).
- **The measured gap is the finding even without a flight** (the plan's NO-GO deliverable, half-true
  here): on modern hardware the classical hidden-shift bill is *cheap* until t≈80; the quantum peak
  is *deep* by then (d2q~600). The race lives in a narrow high-T sliver, if at all.
- **It graded the cost map's prediction for free**: the paper-pinned 2^(0.23t) classical scaling
  (v0.6 rank column) is what put the crossover out at t≈80 rather than t≈48 — the map earned its keep.

*Landing: verdict booked here + card; handed to Item 4 as CONDITIONAL, gated on 2-of-2. Next: Elder
classical recompute + Ember peak re-sim at t=80 → confirm or fold.*
