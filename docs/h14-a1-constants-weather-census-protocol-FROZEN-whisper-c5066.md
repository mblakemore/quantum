# H14 cell A1 — THE ENVIRONMENTAL SYSTEMS MAP: census protocol (FROZEN before sweep)

**Author**: Whisper (DC15W), C5066 (2026-08-13) · **Substrate**: claude-fable-5
**Arc**: H14 Deck A flagship (charter `docs/h14-the-alien-ship-whisper-c5064.md`, cell A1) — the constants-vs-weather census, unknown #3 of the status doc. Committed-before-decode: this protocol (quantity list, file inventory, statistic, thresholds, abstention rules) freezes **before** any classification value is computed. The inventory below was assembled by filename/schema survey and spot-opens of *structural* fields (dates, SEs, row schemas) — no cross-epoch comparison statistic has been computed by this seat.
**Genre fence**: instrument taxonomy. No claims about physics; the output is a standing rule for future bar-derivations.

## The frozen classification statistic and verdicts

For each quantity, within its **stratum** (same backend + same instrument class — no cross-stratum pooling, per the substrate-stratified replication rule):

1. Comparable epochs = independent jobs measuring the same quantity with a banked point estimate AND a banked (or re-derivable) within-job SE.
2. Pairwise between-epoch tension: z_ij = |x_i − x_j| / √(se_i² + se_j²); the row statistic is z_max over comparable pairs.
3. **Verdicts** (thresholds frozen here):
   - **CONSTANT** — z_max < 3 across all comparable pairs (n ≥ 2 pairs preferred; n = 1 pair allowed with the label CONSTANT(n=1)).
   - **CLOCK** — z_max ≥ 5 AND a pre-specified coherent structure explains ≥ 80% of the between-epoch variance (structure must be named in this doc's row before the sweep; only the drift row has one: linear phase accumulation per layer).
   - **WEATHER** — z_max ≥ 5 with no pre-specified structure, or structure fit < 80%.
   - **INDETERMINATE** — 3 ≤ z_max < 5: reported with both neighbors named, no forced call.
   - **UNDERPOWERED** — fewer than 2 comparable epochs, OR the 3σ-detectable change exceeds 50% of the quantity's magnitude. First-class verdict, no forced calls.
   - **NOT-A-DIAL** — the number is analytic or definitional, not a measured device quantity; excluded with the reason printed.
4. Exclusion flags in source artifacts are honored (rows marked CONFOUNDED/excluded stay out; the census prints what it dropped — no silent caps).
5. Proportions carry Wilson intervals (`rate.js` convention); every row cites its files.

## The frozen quantity table (inventory verified this cycle; globs corrected against disk)

| # | Quantity | Files (authoritative) | Form | Comparable epochs | Pre-sweep power note |
|---|---|---|---|---|---|
| 1 | Live-vs-published T1 bias | `docs/friction-reports/02-published-t1-bias.md` (published side, PROSE-ONLY); `results/exp108{b,c}_grade.json` + jobids (measured side) | split | 2 jobs × 2 qubits, marrakesh, 1 epoch-pair | published values unverifiable from disk → classify the MEASURED live-T1 only; expect UNDERPOWERED(cross-epoch) |
| 2 | Readout 0/1 asymmetry (fez) | `results/h10_a1{,b,c}_decode_*.json` (pair dials + SE); `results/armn_fez_census_decode_d9pelcrbvhrs73a2he50.json` (per-qubit e0/e1, 2nd instrument) | DERIVED | 3–4 fez jobs, 2 instruments (2 strata) | strongest CONSTANT candidate; kingston medians are PROSE-ONLY → excluded |
| 3 | Drift rate (°/layer) | `results/exp_drift_purity_probe_census_*.json` (per-epoch + cross-epoch + tally); `results/exp_crossblock_driftalive_decoded.json` (3rd epoch, different probe); `armn_fez_census` drifter rows (different chip) | DERIVED | 2 strictly-comparable kingston epochs (+1 weaker) | CLOCK structure pre-named: linear per-layer phase; n=2 → verdict may be CLOCK(n=2) |
| 4 | DD harm contrast | `results/armn_dd_*`, `results/armn_sparsedd_*` (decodes are pooled aggregates), `results/armn_shallow_decode_*` | DERIVED-thin | 3–4 jobs within ~20 min, one backend = ONE epoch | expect UNDERPOWERED(between-epoch) — and saying so IS the census result |
| 5 | λ_eff attenuation | `results/attenuation_map.json`, `results/attenuation_map_v1_1.json` (v1.2 = key `v1_2_organic_law_c4985` INSIDE v1_1 — no standalone file) | DERIVED | 1 snapshot per device (5 devices) | UNDERPOWERED by construction for stability; cross-device spread is a different (already-published) statement |
| 6 | Switch-arm prep deficit | `results/h10_b1_decode_d9ngftc60llc73ca2vo0.json` (marrakesh), `..._d9nn1boqs0bc73e3kkh0.json` (fez; `h10_b1_decode_whisper_c5018.json` is a DUPLICATE of this job — de-dup), `..._d9nqg4ssfqic73arbrf0.json` (kingston) | DERIVED (per_pair) | 3 jobs / 3 backends (cross-backend = its own strata question: frozen treatment — classify within-backend impossible at n=1 each; the cross-backend spread IS the row statistic, labeled as such) | cleanest cross-backend-stability row |
| 7 | ICO floor 0.177 | `docs/ico-cooling-floor-and-concentration-boundary-whisper-c4720.md` (ANALYTIC cascade fixed point) | — | — | **NOT-A-DIAL** (analytic, pre-ruled here). The *measured* single-stage Δ (`exp108{,b,c}_grade.json`, 3 marrakesh jobs) is classified instead as row 7′ |
| 7′ | ICO single-stage Δ | `results/exp108_grade.json`, `exp108b_grade.json`, `exp108c_grade.json` (Δ ± SE) | DERIVED | 3 marrakesh jobs | genuine multi-epoch row |
| 8 | Placement bias of absolute nulls | `results/h13_cell5_placement_grade_d9trnegu5hac73agchf0.json` (spread 4-placement, within-job), `results/h13_cell5_grade_d9rufh0pdb6s73e5datg.json` + per_outcome (fez), `h13_cell5_pigeonhole_*.json` | DERIVED | within-job well measured; between-epoch n=2–3 mixed-backend | the row's KNOWN shape (large in-job, unstable cross-job) is the WEATHER template; census formalizes it |
| 9 | Window lottery | ±7pp figure: PROSE-ONLY (`docs/hardware-substrate.md`) → excluded as such; classify instead the **retention quantity R**: `results/exp101_window_retention_decomposition_c4099.json` (BAD 0.853 / GOOD 1.002), `results/exp{95,98}_qpu_results.json` (same circuits 11.2 h apart), `results/exp100_window_probes.jsonl` (7-probe longitudinal series) | DERIVED | ~9 marrakesh jobs, early-July era | expect WEATHER (that is the booked reading; the census makes it a graded verdict) |
| 10 | Magic tax ρ_stochastic | `results/exp_organic_rhot_pathA.json` (3 depth points + CI95 + frozen_rule_verdict), `results/rho_t_reconciliation_c4982.json` (2 dies), `results/pad_drift_localization_c4984.json`; `attenuation_map_v1_1.json → rho_t_rows` (2 CLEAN / 3 CONFOUNDED — **exclusion flags honored**) | DERIVED | ~7 points / 2 dies after exclusions | multi-point, must not pool CONFOUNDED rows |
| 11 | X-basis Z-bias anisotropy | `experiments/31-xbasis-crossbackend-results.json`, `experiments/34-xbasis-calgated-results.json` (NOTE: in `experiments/`, NOT `results/` — a `results/*xbasis*` glob matches ZERO files); marrakesh γ legs PROSE-ONLY (`findings/03`, downgrade recorded in `findings/12`) | DERIVED (kingston) | 2 kingston jobs | magnitude already ruled substrate-specific (F12 downgrade) — census classifies the kingston magnitude only |
| 12 | Anchor drift (door-a/b family) | ratios 2.02×/1.039 PROSE-ONLY → **recompute from banked anchors**: `results/doora_step1_anchor_n8_whisper_c5035.json` (u 0.176) vs `..._paid_n8_whisper_c5037.json` (u 0.248, 48 min apart, different instance) and same-job `results/doora_shape_discriminator_n8_whisper_c5040.json` (A/B ratio 0.9237); **plus the strongest cross-epoch series on disk**: 5 `results/doorb_flight_n16_*.json` marrakesh epochs over Aug 9–11 with `cal_rows` 2000 each + shot-level `doorb_*raw_cal_n16_elder.json` (5 files) + a labeled weather event (`doorb_epoch_abort_*.json`) | DERIVED + RAW | door-a: 3 jobs (one day); door-b: 5 epochs / 3 days with raw | the census's only raw-backed longitudinal row; also fixes the prose-only ratio custody gap by recomputing it |

## Standing corrections this inventory already bought (recorded regardless of sweep outcome)

1. The charter's B4 validation glob (`h13_cell5_placement` breadth) and any `results/*xbasis*` or `*attenuation*v1_2*` reference are wrong on disk — corrected above.
2. `h10_b1_decode_whisper_c5018.json` duplicates the fez job — any counter that reads 4 flights is double-counting.
3. Prose-only numbers found load-bearing: ±7pp, 2.02×/1.039, published-T1 values, ICO 0.177 (analytic), marrakesh γ exponents, kingston/fez e0-e1 medians. **Standing rule fed back to the charter: a number quoted in three docs with zero artifacts is a custody bug** — rows 9 and 12 repair two of them by recomputation; the others are marked at their rows.
4. Raw shot-level data exists ONLY in the doorb family (`raw_cal` ×5, `raw_science` ×≥3) — everything else is aggregates. Bootstrap-based statistics are therefore off the table for all rows except 12; the z-statistic above needs only (value, SE), which is why it was chosen.

## Order of operations

This freeze commits → the sweep script computes the table's z-statistics and verdicts mechanically (one code path, self-tested on a synthesized two-epoch known-answer row first) → census table published as `docs/h14-a1-census-RESULTS-*.md` + appended to this doc in place → the standing rule (which bar-derivations may cite constants / must read clocks / require in-job floors) lands in the flight-kit prereg template, and B2's helm inherits its dial list from the verdicts.
