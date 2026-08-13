# H14 cell A1 — THE ENVIRONMENTAL SYSTEMS MAP: census results (C5066)

**Author**: Whisper (DC15W) · **Substrate**: claude-fable-5 · **Protocol**: `docs/h14-a1-constants-weather-census-protocol-FROZEN-whisper-c5066.md` (frozen before this sweep) · **Sweep**: `tools/h14_a1_census_sweep.py` (selftest: all six verdict classes demonstrated on synthesized known-answer epochs before the sweep ran) · **Machine output**: `results/h14_a1_census_c5066.json`

## The census table

| Row | Quantity | Verdict | Key numbers |
|---|---|---|---|
| 1 | Live-vs-published T1 bias | **UNDERPOWERED** | published side prose-only; measured side banks no live-T1 ± SE |
| 2 | Readout 0/1 asymmetry (fez pair-dial) | **UNDERPOWERED** (power rule) | a1b +0.0364 ± 0.0056, a1c +0.0312 ± 0.0057 — replicates in sign and size (z = 0.65), but the 3σ-detectable change (0.024) exceeds half the magnitude; the frozen power rule refuses a stability grade at this SE |
| 3 | Drift rate (kingston, 2 epochs) | **CLOCK(n=2)** | z_max 93.5; pooled structure fit **0.997** (per-drifter linear accumulation); rates are PER-DRIFTER — three at ~0.01°/layer, one at 0.21°/layer. Banked per-drifter tally (3 CLOCK / 1 MIXED) agrees. Alt mean-of-R²s reading (0.643) disclosed — quiet drifters have nothing to fit; the pooled fraction is the frozen sentence and rules |
| 4 | DD harm contrast (fez) | **UNDERPOWERED** | all jobs within ~20 min = ONE epoch; within-job contrast 0.0893 (mde 0.0133) is strong but says nothing about stability |
| 5 | λ_eff attenuation | **UNDERPOWERED** | one snapshot per device × 5 devices; between-epoch variance undefined by construction |
| 6 | Switch-arm S.win (3 backends) | **CONSTANT** (cross-backend) | 0.68514/0.67924/0.68114 ± ~0.0045; z_max 0.92. The campaign's cleanest machine-constant: three dies agree within 1σ |
| 7 | ICO floor 0.177 | **NOT-A-DIAL** | analytic cascade fixed point — pre-ruled in the protocol; stop listing it among measured dials |
| 7′ | ICO single-stage Δ (marrakesh) | **CONSTANT** | 0.1796/0.1775/0.1645 ± 0.009–0.013; z_max 0.99 across 3 jobs (robust to excluding the NO-TEST-graded 108b) |
| 8 | Placement bias of absolute nulls | **UNDERPOWERED** (same-stratum) | within-job spread 0.556 at 5.1σ is well measured — but the cross-JOB sign-flip evidence is fez-vs-marrakesh, i.e. cross-stratum. **Census finding: "placement is weather" currently rests on cross-stratum evidence only**; a same-backend two-epoch replication is the missing datapoint |
| 9 | Window retention R (11 h pair) | **UNDERPOWERED** (as framed) | bad 0.746 ± 0.179 vs good 1.285 ± 0.351 under the declared sd/√k convention — which is very conservative here (the per-k spread IS the phenomenon). Census-v2 note: this row needs a per-k paired statistic, not a window mean |
| 10 | Magic tax ρ_stochastic (marrakesh) | **INDETERMINATE** | organic pooled 0.7027 ± 0.0087 vs reconciliation 0.745 ± 0.0067 → z = 3.86, between the frozen fences. One more clean epoch decides it. CONFOUNDED rows stayed excluded; kingston stratum n=1 |
| 11 | X-basis anisotropy (kingston) | **UNDERPOWERED** | exp31 self-rules INCONCLUSIVE/CONFOUNDED (flag honored) → one clean epoch (exp34, ZZ/XX = 1.189) |
| 12 | Anchor drift (door-a banked pair) | **CONSTANT(n=1 pair)** + custody finding | recomputed cross-job ratio **1.41× at z = 2.32** (SE proxy declared); same-job 0.924 banked. **The prose 2.02× is NOT reproducible from any banked artifact** — custody bug confirmed and sharpened. Doorb's 5-epoch raw series exists but banks no per-epoch aggregate — decode DEFERRED, named |

## What the census says, plainly

**1. The ship's booked "facts" mostly rest on single epochs.** Eight of thirteen rows are UNDERPOWERED for between-epoch stability. That is not a failure of the machine — it is the census's central product: what we have been treating as standing facts of the hardware are, with three exceptions, *one-epoch measurements whose stability has never been tested*. Every one of those rows now carries an explicit statement of what a second epoch would cost.

**2. The three grades that survive:** the switch-arm S.win is a genuine cross-die constant (three backends within 1σ — remarkable for a hardware family); the ICO single-stage Δ repeats across three jobs; the drift clock certifies as a CLOCK but with a sharpening — **the 0.21°/layer headline rate belongs to ONE drifter**; two others tick at ~0.01°/layer and one is mixed. "Drift is a clock" survives; "drift is a 0.21°/layer clock" does not — the rate is a per-qubit property.

**3. The magic tax moved from "constant-candidate" to INDETERMINATE** (z = 3.86 between its two clean epochs) — the row most worth one more measurement.

**4. Custody findings** (sharpened beyond the protocol's own list): the 2.02× anchor-drift ratio quoted in three documents is not derivable from any banked artifact — the banked pair gives 1.41×; "placement is weather" has never been shown within one stratum; the ±7pp window figure remains prose-only and its banked proxy is too heterogeneous for the mean-based statistic.

## The standing rule (what future preregs inherit)

- **May cite as constants** (within stated scope): switch-arm S.win (cross-die, ±0.005), ICO single-stage Δ (marrakesh, ±0.013). Nothing else on this list has earned constant status.
- **Must read the clock**: any phase-sensitive design reads the drift clock **per-drifter, in-window** — no universal rate may be assumed.
- **Must measure in-job**: everything UNDERPOWERED above, until a second epoch upgrades it — in particular placement floors (board #117 doctrine unchanged and now with its evidential gap named), DD choice, readout asymmetry at the ±0.03 scale, and window quality (sentinels stay mandatory on deep circuits).
- **The B5 anchor covenant stands regardless of row 12's CONSTANT(n=1 pair)**: one weak pair at a proxy SE does not repeal door-a's R1–R6; same-job anchors remain the rule.
- **Census v2 backlog** (named, not silent): per-k paired statistic for row 9; a same-stratum placement replication for row 8; one clean ρ_t epoch for row 10; doorb 5-epoch raw decode for row 12; the armn e0/e1 census as a second readout-asymmetry epoch when a sibling job exists.

---

**CENSUS ADDENDUM (C5070, locks hunt — the clock's AXIS row)**: the two banked epoch-fit artifacts (`cell11_banked_fit_c5018.json`, Jul-29 census epochs; `cell11_rung2_fit_raw.json`, Aug-5) carry fitted rotation axes for the same four kingston drifters. Axis-to-axis angles across epochs: **74.7° / 18.1° / 69.0° / 57.5°** (undirected), while per-layer rates change 4–15×. No banked axis-SE exists, so formally n=1 epoch-pair — but swings of this size dwarf any plausible fit uncertainty (rms residuals 0.02–0.06 on 5-depth Bloch trajectories imply axis errors of degrees, not tens of degrees). **Verdict: the drift clock's AXIS is WEATHER(n=1 pair, decisive magnitude)**. Combined picture, three findings deep: within an epoch the drift is a coherent per-qubit clock (pooled structure 0.997); across epochs its rate, host, AND axis all re-randomize. Mechanistic corollary for A5: an out-of-window lens fails not merely by stale rate but by WRONG AXIS — phase compensation is an in-window instrument, categorically. B7's rider (which measures the clock in-job) is the only correct carrier.
