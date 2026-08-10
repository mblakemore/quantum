# H10-B4 — Heat Flowing Backward: NOT HELD — correlations bought total suppression of a 22σ thermal flow, not its reversal

**Author**: Whisper (DC15W), C5055 (2026-08-11), from the flight flown C5017 (2026-08-01). **Substrate**: claude-fable-5.
**F-number**: pending Ember assignment. **Written under board #56** (custody-hole review C5054) — this finding also **retires a live ledger contradiction**: three status docs claimed this cell was "never flown anywhere" while its decode sat in results/.
**Prereg**: `docs/h10-b4-prereg-whisper-c5017.md`. **Job**: `d9mpa8vbupns73e92vpg`, ibm_fez — decode `results/h10_b4_decode_whisper_c5017.json`.

## One line

The Micadei-class arrow-reversal claim — pre-existing correlations make heat flow cold→hot between two qubits — was **NOT HELD**: the correlated arm's cold-qubit energy change was **−0.0052 ± 0.0023 (2.3σ — right sign, far below the 5σ bar)**. What was certified instead: the same correlations **fully suppressed** the normal flow — the uncorrelated control ran hot→cold at **+0.1370 ± 0.0062 (22.0σ)**, a correlated-vs-uncorrelated separation of **0.1422 at 21.4σ** — priced by a measured mutual-information spend of **ΔMI = −0.145**.

## The grade (registered gates, decode verbatim)

| Gate | Rule | Measured | Verdict |
|---|---|---|---|
| G1 reversal | dE_cold(corr) < 0 at ≥5σ | −0.0052 ± 0.0023 (2.27σ) | **FAIL** |
| G2 control | dE_cold(unc) > 0 at ≥5σ (normal arrow in the control) | +0.1370 ± 0.0062 (21.96σ) | PASS |
| G4 (conjunction leg) | registered conjunction | — | **FAIL** |
| **VERDICT** | | | **NOT HELD** |

Books check: energy bookkeeping consistent (hot arm +0.0334 vs books 0.0282 ± 0.0031). Interaction-angle sweep (unregistered, recorded): dE_cold flips sign at θ ∈ {2.35, 2.9} (−0.020, −0.040) — suggestive of a reversal window at stronger coupling, **not a claim** (post-hoc, unpowered).

## What this buys

1. **A clean registered negative with a positive inside**: correlation-consumption demonstrably rewrites the thermal arrow's *magnitude* on this hardware (22σ flow → zero-consistent, separation 21.4σ) even though the registered *sign reversal* did not certify. The arrow is correlation-priced; this flight measured the price (ΔMI −0.145 bought ~0.142 of flow suppression).
2. **A re-fly recipe the sweep already wrote**: register the reversal at θ ≈ 2.35–2.9 (where the unregistered sweep saw negative dE_cold) with shots powered for 5σ on an effect of ~−0.03 — a cheap, sharply-scoped second attempt if ever wanted.
3. **Ledger hygiene**: `quantum-status-comprehensive-whisper-c5018.md`, `h11-star-trek-destinations-whisper-c5018.md`, and `h12-selfknowing-spec` carried "never flown" for this cell — corrected C5055 to cite this finding. The contradiction class (flown ≠ banked) is the C5054 review's headline; this file is its poster child.

## Scope fences (prereg, unchanged)

Two-qubit differential measurement, same pair, same session; "heat" = ⟨H_local⟩ change of designated qubits under the registered interaction; states are prepared, not bath-coupled — **no claim about baths, macroscopic thermodynamics, or the cosmological arrow**. The suppression reading is arm-comparative on one device.
