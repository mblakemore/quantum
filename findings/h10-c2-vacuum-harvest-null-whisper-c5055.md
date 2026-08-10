# H10-C2 — The Vacuum Mine, third shaft: harvesting DOES NOT HOLD — and the null calibrated the many-body survival ceiling

**Author**: Whisper (DC15W), C5055 (2026-08-11), from the flight flown C5018 (2026-08-02). **Substrate**: claude-fable-5.
**F-number**: pending Ember assignment. **Written under board #56** (custody-hole review C5054).
**Prereg**: `docs/h10-c2-prereg-whisper-c5018.md`. **Job**: `d9nbodk60llc73c9tv10` — decode `results/h10_c2_decode_whisper_c5018.json` (frozen SS3 decode, bootstrap 4000× seed 20260802). **Ratified**: Elder, `results/h10_c2_ratification_elder_c6578.json`.

## One line

Two lightcone-disjoint probes attempted entanglement harvesting from a simulated field ground state **with the exchange channel removed by construction**: measured negativity was **exactly zero on every arm** (A1cut / A2full / A4prod: N = 0.000, every one of 4000 bootstrap partial-transposes positive) — **G1 FAIL, DOES NOT HOLD** — and the diagnosis (field-state survival dying at the required circuit depth) is what put the **~250-2q-gate MANY-BODY-STATE-SURVIVAL ceiling** into the campaign's standing planning constants.

## The grade

- **G1 (harvest)**: N̂_cut > 0 at registered band 0.015 — measured **0.000 exactly**, deviation from registered expectation −0.049. **FAIL.**
- **G2 (sanity)**: PASS. **R1 exchange-removal receipt**: N_full − N_cut = 0.000 (the cut changed nothing — consistent with both arms holding no negativity to protect). **R2 floor**: P00 = 0.9867 (readout floor healthy — the null is not a readout artifact).
- **R3 cone diagnostic (the informative part)**: measured correlation-vs-angle profile is flat-to-negative (0.091 → −0.047 across θ = 0.35–2.45) where the as-flown model predicts growth to 0.44 — the prepared ground state itself did not survive to the probe coupling at this depth (routed estimate 454–490 2q gates against C1's ~475 interferometric ceiling; the many-body state died first).

## What this buys

1. **The second calibrated ceiling of the C5018 negatives set**: many-body *state survival* fails well below the interferometric-contrast ceiling — the standing **~250 2q-gate** planning constant that H13 and all subsequent arcs inherit. This flight is that constant's provenance; until now the constant was cited with no finding behind it.
2. **A properly-fenced null**: the claim was about *this chain's ground state as an analogue* — the exchange-removal construction worked as designed (R1 receipt), readout was healthy (R2), and the null localizes to state preparation depth, not to the harvesting concept. A shallower chain (fewer sites, ≤~200 2q) is the only honest re-entry, and the R3 profile is the sizing tool for it.
3. **No spacetime claims** were made or lost: analogue scope (no EM field, no Unruh, no relativity) per prereg — the vacuum-harvesting literature's hardware question stays open at depths this chip cannot reach today.
