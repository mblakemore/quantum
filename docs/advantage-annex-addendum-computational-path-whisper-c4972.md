# Annex Addendum — What the Data Still Held, and the Path to a Runtime-Race Advantage

*Whisper C4972, 2026-07-22, substrate claude-fable-5. Creator directive: "Take a look at our latest
experiments and results (the C4969 annex + the H1–H8 arcs) — is there anything in the data we
overlooked? How can we get to a demonstrable computational quantum advantage with a measurable
classical counterpart from here?" This addendum answers both, with one new $0 measurement flown
this cycle (`experiments/exp_hss_threshold_calibration.py` →
`results/exp_hss_threshold_calibration.json`).*

*Standing fences up front: the C4971 hidden-shift NO-GO **stays booked** — it correctly followed its
frozen rule, and nothing here reopens it. Everything below feeds a possible **fresh**
pre-registration, exactly as the verdict doc itself gated ("a legitimate future re-scope… behind a
new pre-registration so it cannot become a retroactive salvage").*

---

## Part 1 — Five things the data was still holding

### 1.1 ⭐ The 50-count detection bar is ~12× conservative, and detection is shots-scalable — the fez fold is a budget artifact, not a physics wall

The NO-GO verdict itself flagged its weakest joint: *"the NO-GO rides on the 50-count proxy for
7σ-FWER-over-2⁴⁰, whose calibration in this regime is unsettled."* Calibrating it was cheap, and it
moves the verdict's foundation:

- **Exact diffuse-background FWER (Part A, analytic)**: with N shots spread over M = 2ⁿ outcomes,
  the per-cell background is Poisson(N/M); union-bounding the max over all cells, the 7σ-FWER
  (p ≤ 2.6×10⁻¹²) threshold at **n=40, 100k shots is kc = 4 counts** (FWER ≤ 3×10⁻¹⁸ there;
  N/M ≈ 9×10⁻⁸ makes the outcome space almost empty). Even at 1M shots kc = 4–5. The frozen
  50-count proxy was **~12× conservative**. *(Ember 2-of-2 CONFIRMED, coordination#517:
  independent recompute exact at n=40; refinement adopted — for upper-tail excess detection the
  one-sided convention (p ≤ 1.28×10⁻¹²) is the honest choice, which nudges only the small-n bars
  (n=16/100k: 22 not 21; n=24/1M: 11 not 10) and leaves n=40 = 4 identical both ways.)* Ember's pessimistic-edge fez peaks of **22–38 counts
  clear the calibrated diffuse bar by 5–8×** on all six seeds.
- **Shots-scaling was left on the table**: peak counts grow *linearly* in shots while the FWER bar
  grows only logarithmically. The scout froze 100k shots; at 1M shots the fez pessimistic-edge peak
  is 220–380 counts — above even the over-conservative 50 bar. A fixed-shot fold is a *budget*
  statement, not a *detectability* statement.
- **The load-bearing caveat is structured noise, and it is measurable (Part B, empirical)**: at n=40
  the diffuse floor is ~0–1 counts, so the only way the modal outcome isn't s is a **structured
  competitor** — noise mass concentrated on a specific wrong string. Measured at n=16 (transpiled
  circuit, depolarizing + 1% readout, 20k shots): modal = s at every rung tested; the runner-up is
  always a **Hamming-distance-1 neighbor of s** (readout-flip structure) with ρ = runner/peak =
  0.019 / 0.044 / 0.083 at R = 0.66 / 0.39 / 0.18. **ρ grows as R falls.**
- **In-regime measurement (landed this cycle, 200k shots, total dose λ·d ≈ fez-at-t80's ~8)**
  (`results/exp_hss_threshold_calibration_inregime.json`): at R = 3.3×10⁻³, peak 656 vs runner
  292 @ HD1 (ρ = 0.45); at **R = 6.7×10⁻⁴, peak 134 vs runner 109 @ HD1 (ρ = 0.81)** — modal is
  *still* s at both rungs, but the raw-modal margin has degraded to ~1.2× in the fez class. The
  competitor is single-gate-error mass concentrating at HD1 (well above the ~1% pure-readout
  expectation), exactly the structured mechanism named above. **Consequence, stated plainly: the
  fresh pre-reg's frozen detection statistic must be the ball/per-bit decoder, not raw
  modal-outcome.** The ball statistic's margin stays decisive where raw modal thins: ball(s)
  collects the peak *plus every* HD-1 lump (all of them are readout/single-error scatter *of s*),
  while any competitor's ball holds only its own lump — in the landed data, ball(s) ≈ 656+292+…
  vs any rival ball ≤ its single lump. Freezing that statistic (and its slightly-corrected FWER
  bar) is Phase-A work with the empirical support now in hand.
- **The structure is friendly, not hostile**: HD-1 lumps are *evidence for s*, not against it. A
  grader that scores the **HD ≤ 1 ball around each candidate** (or per-bit majority) collects the
  peak *plus* its readout-scattered mass — the dominant structured competitor becomes signal. A
  fresh pre-reg should freeze a ball/decoder-aware detection statistic with its own calibrated FWER
  bar (the ball statistic's null is 41 cells' worth of background per candidate, a negligible
  correction at 2⁴⁰).

**Net**: under the calibrated bar, the race is plausibly live on **both** devices — kingston with
enormous margin (2500–3200 counts vs bar 4) and even pessimistic-edge fez by 5–8×, before any shot
boost. The device-dependence story softens; the twirl requirement (below) is what carries the
stochastic-noise premise the calibration rests on.

### 1.2 ⭐ The race currency was mis-scoped: shots ARE the quantum runtime — and runtime is the currency the Tracker wants

The scout's decision rule raced *fixed-shot detectability* against *classical seconds*. But the
tracker-shaped question is **time-to-verified-solution on both arms**. Reframed: the quantum arm's
cost is `shots-to-detection × per-shot time + queue-honest overhead` — at 1M shots on a Heron,
**minutes of wall time** — while the classical arm at t=80 is **≥ tens of minutes (fast-edge
extrapolation: 1774 s at n=24, 8214 s ≈ 2.3 h at n=40) to months (paper's config)**, with the
joules column (cost map v1.0) pricing both sides' energy for free (QPU side one-sided per G2). The
crossover doesn't need the peak to survive at 100k shots; it needs
`quantum_minutes < classical_hours`, which the calibrated bar + shot-scaling delivers with margin.
This reframing — detection-threshold currency → runtime currency — is what converts the C4971
NO-GO's world into a live race without touching its frozen rule.

### 1.3 Exp144's conventional arm is banked — the NOT-WIN may hide a $0 second ratio

The complete-answer update books Exp144 as NOT-WIN because "the conventional-race arm went NULL
(baseline detector falsified/halted, unmetered — no valid ratio)." But the results directory holds
**30+ `exp144_conv_*` manifests spanning n=4/6/8, k=1–5, multiple waves** — the raw single-copy
data appears to be substantially banked; what failed was the *detector post-processing* (the
verdict/mixture-fit layer), not the data collection. **If** the banked conventional waves are
sufficient (Elder's call — he holds the grader), a fresh-frozen detector re-analysis over
already-banked shots ("Exp144b") is a **$0-QPU** path to converting the quantum arm's 5/5 perfect
sealed-vector recovery at n=4 AND n=6 into a second valid computational ratio. The NOT-WIN stays
booked; 144b would be a new, separately pre-registered analysis. (If the banked waves are
insufficient because the halt truncated them, this becomes a small QPU spend instead — still the
cheapest live path to a second F-number-class computational result.)

### 1.4 §3(a)'s "4th flight" may already be in the can: λ_anc was measured by the 3rd

The ZZ-aware pinned re-fly isolated ancilla-survival as the residual and *measured the ancilla
dephasing factors in the same job* (ratio X ≈ 0.64, Z ≈ 0.9), and dividing them out already
recovered λ_sys to 1% (0.609/0.64 ≈ 0.95 vs conventional 0.954). Before pricing an
"ancilla-survival-calibrated re-fly," do the **$0 re-analysis**: extract λ_P,anc per Pauli from the
banked reference/idle arms of `exp_steth_a_zzaware_decoded.json`, apply the division across ALL
arms with propagated CIs, and check whether two-copy-vs-conventional agreement lands inside CIs at
n=1 and n=2. If yes, the "clean measured λ_sys agreement" deliverable is already earned and the
QPU item disappears; if the CIs are too wide, the re-fly is then a *sized* spend (we'd know exactly
how many shots the CI needs). Either way the stethoscope's 2^(n/3) separation — whose classical
counterpart is the *executed, already-clean* conventional arm (Z = 1.000) — remains the campaign's
best *native-task* sample-complexity advantage candidate at n ≥ 9.

### 1.5 The classical arm must be measured, not extrapolated — promote Elder's t=80 recompute to gating

The scout's classical leg is a ×1000 config extrapolation of a 2016 laptop anchor, with γ = 0.23
itself extrapolated **32 T-gates past the paper's validated t=48**. Two consequences: (a) Elder's
RACE-config recompute at t = 64–80, currently filed "informational," is **gating** for any fresh
pre-reg — the race's classical counterpart should be a *measured, verified, censoring-disciplined*
row from the cost-map harness (which was built for exactly this), with joules, on the named Ryzen;
(b) the measurement cuts both ways — if the best fieldable solver (extstab at verified settings,
all-core) comes in *under* 10 minutes at t=80, the window slides to higher t, which the calibrated
bar + shot-scaling keeps reachable (R_kingston at t≈96–112 is still thousands of counts at 1M
shots). The window's *location* is uncertain; its *existence* no longer hinges on one
extrapolation.

*(Smaller, also unpriced by the scout: quiet-qubit placement (F57/F58 tooling) and the steth-arc's
twirl+DD machinery — both lower the effective dose λ_eff·d2q below the generic-map value the scout
used, i.e., every R above is itself conservative.)*

---

## Part 2 — The path to a demonstrable computational advantage with a measurable classical counterpart

The shape we lack (per C4762/C4682) is the Tracker's: **classically attemptable, runtime-scored,
supersedable-by-design**. The hidden-shift race is the one candidate all the instruments now
converge on, and every gate except the flight itself is $0.

**Phase A — $0 gates (order matters, nothing flies until all four hold):**
1. **Threshold calibration** ✅ *(this cycle)* — calibrated FWER bar (kc = 4–6 in-window), ρ
   structure measured at n=16, in-regime ρ run in flight. Remaining: freeze the ball/decoder-aware
   detection statistic and its bar into a PREP card.
2. **Real-device noise band** — real-kingston (and re-priced fez) fake-vs-real band, twirled
   circuits mandated (the twirl machinery from the steth arc enforces the stochastic-noise premise
   the calibration rests on — cross-arc payoff).
3. **Measured classical arm** (Elder, gating) — verified extstab-at-tuned-settings + any better
   fieldable solver, RACE_CONFIG all-core, t = 64/72/80 sweep through the cost-map harness
   (censored, joules column). This IS the "measurable classical counterpart": named box, named
   solver, verified answers, measured seconds and an energy upper bound.
4. **Fresh PREP card** (2-of-2 before submission) — kingston-primary; n = 32–40, t chosen where the
   measured classical row ≥ 10× the predicted quantum wall; 1M-shot budget; pinned quiet-qubit
   placement; Pauli-twirled oracles; both arms metered; frozen ball-decoder + calibrated 7σ-FWER
   bar; sealed planted s (another DC commits, 3-of-3 reveal — the Exp142 court).

**Phase B — one deliberate QPU spend (~5–10 min wall, fits the ~5–6-day runway):**
Fly the race once on the best die. Deliverable: **measured runtime ratio (quantum minutes vs
classical hours) per verified solution, plus the one-sided joules comparison** — the first entry on
the campaign's empty Tracker-shaped scoreboard. Honest outcomes both ways: if the peak dies or the
classical solver wins, the measured two-frontier gap is the finding (the computational twin of
F54's wall), booked NO-SPIN like every miss before it.

**Phase C — parallel cheap wins (independent of A/B):**
- **Exp144b** conventional-arm re-analysis over banked manifests, fresh frozen detector ($0 if the
  waves suffice; Elder adjudicates).
- **§3(a) $0 ancilla-calibration re-analysis** of the banked ZZ-aware job; only if CIs are too wide
  does the calibrated re-fly go back on the deliberate-spend list, now correctly sized.

**Why this is the right order**: the race's *scientific* risk (peak survival, classical bill) is
retired entirely by $0 instruments the campaign already built — attenuation map, cost-map harness,
twirl machinery, threshold calibration — so the single QPU spend buys only the thing no instrument
can fake: the head-to-head number on silicon.

---

*Fences, restated once: supersedable-by-design is a feature and will be printed on the result; the
classical arm is best-fieldable-solver engineering, not a complexity theorem (Exp142/F119 remains
the theorem-floored result, different currency, both booked); QPU joules stay one-sided until IBM
publishes power draw; and the C4971 NO-GO remains the correct verdict of its frozen rule — this
addendum is the fresh pre-registration path it explicitly left open. Contact: Mike Blakemore.*
