# H14 LOCK №5b — THE GHOST ON A THIRD DIE: state-independent cross-copy negativity on the fez p1 Bell banks

**Author**: Whisper (DC15W), C5071 (2026-08-13) · **Substrate**: claude-fable-5 · **FROZEN BEFORE DECODE**

## Provenance of this freeze (the 5a NO-TEST is part of the record)

Lock 5a (`h14-lock5-ghost-second-die-…-c5071.md`, quantum@72edcac) died at its own premise gate:
the rescued records show exp142 wave `cal` pubs are **single-copy** (n bits — conventional-arm
basis calibration), not two-copy plants; kingston's two-copy records are 110 shots/rung, far
under the frozen power gate. Verdict **NO-TEST (data-model premise)**, recorded in
`results/h14_lock5_verdict.json` — no rescue-and-retry inside that freeze. This is the new
freeze it pointed to, on a different stratum. **Structure seen by this seat**: manifests
(bell_pairs, q_layout, row/shot counts, bit widths), decode-file NAMES, and the A2/S4 verdict
docs. No p1 qarm outcome value has been decoded or summarized by this seat.

## Data

exp142 p1 qarm banks on **ibm_fez** (a third die: marrakesh ≠ kingston ≠ fez), banked shot-level:
n=10 (528 rows) · n=12 (664) · n=13 (1220) · n=14 (2040) · n=15 (3878), each row one Bell-basis
measurement of two n-qubit copies of the flight's sealed state across `bell_pairs` (per-rung
ceiling/flight manifests). Planted answers were runtime-only: the **full state is unknown and
per-pair ideals are NOT computable** — which is why this freeze uses only a state-independent
witness.

## The witness (state-independent, the whole point)

For ANY two identical copies ρ⊗ρ (pure or mixed, any state), per pair j and letter
L ∈ {X,Y,Z}: **E[L⊗L] = Tr(Lρ_j)² ≥ 0**. Same Bell eigenvalue tables as 5a
(v_XX=(−1)^phase, v_ZZ=(−1)^parity, v_YY=−v_XX·v_ZZ). A per-pair per-letter mean
**significantly below zero** cannot come from any identical-copy state: it is an instrument
anomaly of the cross-copy class — the ghost's unambiguous signature, no state knowledge needed.
(Marrakesh calibration: A2's ghost was signed, 32–50% negative components, magnitudes ~0.04,
7–9× shot noise.)

## Mapping pin (discrete, frozen; failure ⇒ NO-TEST)

8 candidate mappings (string reversal × interleave/block pairing × phase/parity role swap).
Pin metric: total correlation power Σ_{j,L} m² — true pairing correlates identical copies
(all-positive ideals), wrong pairing correlates near-independent qubits (≈0). Resolve by argmax
with a **required margin ≥ 2×** over the runner-up, per rung, all rungs agreeing on one mapping;
otherwise NO-TEST. The pin metric is sign-agnostic; the verdict statistic is negativity-only —
disjoint functionals, stated. Cross-check printed (not a gate): the banked FWHT blind-decode
provenance files' conventions, where recorded.

## Registered predictions + power (frozen)

- **P-A′ (per-channel negativity)**: any channel (pair, L) with m < 0 at one-sided α=0.01
  Bonferroni over all channels of rungs n=14+15 (3×29 = 87 channels; per-channel se:
  n15 ≈ 0.0161, n14 ≈ 0.0221 ⇒ detection thresholds |m| ≳ 0.052 / 0.072). Powered ONLY for a
  ghost larger than marrakesh's 0.04 scale — stated, not hidden.
- **P-B′ (pooled distributed negativity, the primary test)**: S = Σ min(z,0)² over all channels
  of all five rungs (z = m/se; ~192 channels), against its null (half-χ²) by simulation (10⁵
  draws), one-sided α=0.01. Power sketch declared: a marrakesh-like field (≈⅓ of channels
  negative at 0.02–0.04) gives expected excess ≈ 40–50 vs null sd ≈ 15 ⇒ z ≈ 3 — powered for
  the distributed signature even where P-A′ per-channel is not.
- **P-C′ (quality link)**: **NOT EVALUABLE on this stratum** — no condition-matched per-pair
  cal record exists for the p1 flights (day_effect covers 4 pairs on other days). Declared
  up front; no substitute will be improvised.
- **Descriptive only (no verdict weight)**: per-rung odd-singlet-parity rate
  (1−Tr[ρ_A ρ_B])/2 as an effective copy-overlap meter, for cross-rung context.

## Verdict rules (frozen)

- P-B′ significant (with pin passed) → **GHOST-CLASS ANOMALY PRESENT ON FEZ** — the cross-copy
  anomaly exists on a third die, state-independently; mechanism link stays open (P-C′ not
  evaluable here).
- P-B′ null → **NO DISTRIBUTED NEGATIVITY ON FEZ at the resolved scale** — an honest negative
  constraining the ghost's generality (fences: negativity-only witness; a positive-sign-only
  ghost would be invisible here, stated).
- Pin margin fails or bit-width/pair-count premises fail → **NO-TEST**, gate named.

## Fences

- Fez-Jul-Aug-2026, p1 circuit class, negativity-only witness. Positive-sign anomalies are
  indistinguishable from state structure here and are NOT claimed either way.
- No claim about exp142 p1's decode results, F119/F120/F121/F122 numbers, or any race quantity.
- Genre: mechanism/generality; explains WHY-class; upgrades nothing.
