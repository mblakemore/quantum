# H14 LOCK №5 — THE GHOST ON A SECOND DIE: does the F122 cross-copy anomaly generalize beyond marrakesh?

**Author**: Whisper (DC15W), C5071 (2026-08-13) · **Substrate**: claude-fable-5
**Class**: $0 re-analysis of banked/rescued records · **FROZEN BEFORE DECODE** — this freeze is
written from **structure only**: manifests (pub kinds, paulis, b-strings, bell_pairs, layouts,
shot counts) and the A2/S4 verdict documents. No exp142 measurement outcome has been decoded by
this seat. The stage-0 custody rescue (`tools/h14_lock5_custody_rescue.py`) banks records
verbatim and computes nothing; it may run concurrently with this freeze.

## The question

A2/S4 (F122 footnote, C5066–C5070) established on **ibm_marrakesh** (5 flights, one era): the
two-copy Bell measurement carries a real per-qubit cross-copy correlation on should-be-zero
weight-1 probes — flat-class (adjacency-blind, S2 excluded at |ρ|=0.4), magnitudes 7–9× shot
noise, and on the healthy stratum the per-qubit magnitudes track per-pair calibration deficit
(ρ ∈ [+0.59,+0.70], Fisher ≈ 1e-5). A2's own fence: "any verdict is a marrakesh-2026 statement;
cross-device generality is not claimed by design." **This lock tests that named residual** on
**ibm_kingston** using exp142 wave 1–7 calibration pubs (Jul 2026), which are known-answer
product states measured by the identical instrument class (transversal Bell measurement on
transmon pairs).

## Data (structure known at freeze; outcomes not)

Wave jobs w1–w7 on ibm_kingston (attempt-3 lineage; the INVALID/DO-NOT-DECODE fence excludes
attempt-1/2 ids — only the live ids in the base manifests are used). Per job: 3 `cal` pubs ×
100 shots. Each cal pub plants, per qubit q, the eigenstate of `pauli[q]` with sign
`(−1)^{b[q]}`, in BOTH copies; the two n-qubit copies are Bell-measured across `bell_pairs`.
Rungs n=4,6,8,10. Nominal cal-shot totals per pair (from manifests): n4 ≈ 900 (w1–w3), n6 ≈ 900
(w1–w3), n8 ≈ 1200 (w1–w4), n10 ≈ 2100 (w1–w7). Actual totals recomputed at execution from the
rescued records; if a job failed rescue, its shots are absent and power is recomputed.

## Estimator (one code path, defined at freeze)

Bell outcome per pair = 2 bits (x,z) with per-letter eigenvalue table
v_XX(x,z) = +1 iff z=0 else −1 · v_ZZ(x,z) = +1 iff x=0 else −1 · v_YY = −v_XX·v_ZZ
(convention pinned by the known-answer pin below, including global bit order/endianness and the
bitstring→pair mapping; the pin may permute/flip conventions ONLY via the planted-letter channel).

Per unique physical pair j (pooled across all cal pubs and waves of every rung containing j):
- **c_j** (cal quality) = mean v_{P_j} over shots, P_j the planted letter — ideal **+1**.
- **g_j** (ghost vector, 2 components) = mean v_L over shots for the two letters L ≠ P_j —
  ideal **0** exactly (⟨s|L|s⟩² = 0 for eigenstate s of P ≠ L).
- **|g_j|²** = sum of squared components; per-component se from shot counts (v ∈ {±1}).

Planted letters rotate across the 3 cal pubs per job (manifest-recorded), so both off-letters
are sampled per pair per job.

## Known-answer pin (must PASS before any verdict; failure ⇒ NO-TEST, reported)

1. **Synthesized input**: ideal noiseless Bell-outcome sample for each cal pub built from its
   manifest (pauli, b) must decode to c_j = +1, g_j = 0 through the same code path.
2. **Real-data pin, planted channel only**: with bit order and (x,z) convention resolved, the
   median c_j across pairs must be **≥ +0.5** on every rescued job (the cal states are product
   eigenstates; an instrument this far from its own cal plant means wrong mapping, not physics).
   Resolving the discrete mapping (endianness, bit→pair order, x/z role) by maximizing the
   planted-channel c is a known-answer fit; the ghost letters are untouched by it.
3. **Sentinel check** where sentinel_start pubs were rescued: sentinel outcome distribution
   must match its known parameterless circuit prediction (gross-layout sanity).

## Premise gates (Lock 3's lesson — no estimator runs on data that cannot answer)

- **Power gate**: pooled per-pair per-component se must satisfy se ≤ 0.02 (half the
  marrakesh ghost class 0.04) for pairs entering the primary test; pairs failing this are
  reported but excluded from verdicts. If <8 unique pairs survive, declare **UNDERPOWERED** —
  no verdict.
- **Cal-identity gate**: pin step 2 doubles as the signal-premise gate (median c ≥ 0.5).

## Registered predictions (frozen)

- **P-A (existence)**: if the ghost is device-general, per-pair |g| carries structure above shot
  noise: global χ² over surviving pairs' g components vs their se, α = 0.01. Marrakesh analog
  was 7–9× shot noise; kingston pooled se ≈ 0.022 (n10) resolves ≥2× structure.
- **P-B (adjacency)**: Spearman ρ(|g|, coupling-degree/adjacency indicator from kingston's
  coupling map restricted to used qubits) — prediction **NULL** (marrakesh excluded S2).
- **P-C (measurement-quality link, the S4 mechanism)**: Spearman ρ(|g_j|, deficit 1−c_j) over
  unique surviving pairs, permutation p (10⁴ perms). Prediction **POSITIVE** if the S4
  mechanism generalizes. Power declared: adequately powered at |ρ| ≥ 0.6 for α = 0.01 (≈20+
  pairs), |ρ| ≥ 0.5 at α = 0.05; smaller true ρ lands UNDERPOWERED and is reported as such.

## Verdict rules (frozen)

- P-A significant + P-C positive-significant → **GHOST GENERALIZES, measurement-quality-linked
  on a second die** (extends F122 footnote; n grows from 3 flights/1 die to 2 dies).
- P-A significant + P-C null → **ghost present, mechanism link kingston-indeterminate** (report
  both; no stratum invented post hoc).
- P-A null with gates passed → **marrakesh-local at the resolved scale** — an honest negative:
  the instrument-class generalization is refuted at ≥2× shot-noise on kingston cal states.
- Any pin/gate failure → **NO-TEST** with the failing gate named. No rescue-and-retry inside
  this protocol; a revised protocol would be a new freeze.

## Fences

- Kingston-Jul-2026, cal product states, n=4–10: this tests the **instrument class**
  (transversal Bell measurement of two identical single-qubit eigenstates), not an exact
  replication of door-b's randomized weight-1 probes on n=16 science states.
- No claim about F119/F122's advantage numbers is created or modified by any outcome.
- Genre: mechanism/generality. Explains WHY-class; upgrades nothing.
- The sealed science pubs (quantum rows) are NOT decoded under this freeze.
