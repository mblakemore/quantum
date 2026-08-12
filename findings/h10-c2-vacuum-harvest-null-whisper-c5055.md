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

---

## ADDENDUM (C5060, 2026-08-12) — G2 passed **vacuously**, and that is the transferable finding

*Added after re-deriving this flight from the artifacts. The grade above records "G2 (sanity): PASS"
without comment; this addendum states what that pass is worth, because the answer is nothing.*

**G2 predicted zero and measured zero — on an apparatus that was returning zero on every arm**,
including A1, which was registered at 0.0488. Its pass carries no information about instrument
health. Had G1 been the only failing gate, this flight would have read *"signal absent, control
clean"* — a sentence that sounds like a physics result and here means only that the chip was dark.

The ungated legs are what establish the apparatus was dead rather than quiet: detector excitation
measured **0.628 / 0.502** against a predicted 0.063 / 0.062 (≈ coin-flip — detectors that have
stopped reporting their own state), field energy **−3.548** against **+0.884** (wrong sign), and the
light-cone front running **backwards** (0.091 → 0.022 → −0.051 where the prediction climbs
0.004 → 0.093 → 0.292 → 0.437). Three independent instruments agreeing on depolarisation.

**A CONTROL WHOSE CORRECT ANSWER IS ZERO IS NOT A CONTROL.** It is a consistency check, and it must
never stand as the apparatus-health leg of a registered verdict. The same week's flights make the
contrast exactly:

| Flight | Control's prediction | What its result proved |
|---|---|---|
| **H10-B1** time flip | tightened **pre-data** against *computed* fault values | caught a real fault — under the band as originally sealed, the flight would have passed all five gates |
| **H10-B4** heat backward | **+0.1308** (nonzero) | landed at +0.13695 at 22σ — **apparatus verified working**, which is the only reason its negative is publishable |
| **H10-C2** *this flight* | **0** | nothing — the whole chip was reading zero |

This is the counter-example behind the positive-and-missable rule that H10-B1's Amendment 1 later
stated: *"a control band must be narrow enough to miss on the specific faults of the flown circuit,
and the fault values must be computed, not guessed."*

**Provenance of this addendum, stated because it is unflattering**: it exists because I searched for
this finding with a malformed regex (`grep -icE "a\|b"` — in an extended regex `\|` is a *literal
pipe*), read the 0 as absence, and rewrote all three C5055 findings from scratch believing them
missing. The rewrites are deleted; this paragraph is the only part that was not already here.
