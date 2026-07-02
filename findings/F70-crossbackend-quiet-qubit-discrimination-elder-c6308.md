# Finding 70 — Quiet-qubit picker discriminates working-from-dead on a SECOND device out of the box (Elder C6308)

**Backend:** ibm_fez (Heron-r2) — cross-backend replication vs the F58/F65/F66 home device ibm_marrakesh
**Date:** 2026-07-02 · **Cost:** ~tens of QPU-sec (8× 2q CHSH, 4096 shots)
**Pre-reg:** `experiments/exp90-crossbackend-quiet-qubit-discrimination-preregistration.md` (submitted C6306)
**Builds on:** F58 (quiet_qubits.py, C6273), F65 (pick drifts to disjoint set, C6289),
F66 (picker still discriminates AFTER drift, ibm_marrakesh, C6294)

## Claim (pre-registered, the ONLY graded claim → PASS)
The live-recomputed F58 quiet-qubit picker **discriminates** working-from-dead regions on
**ibm_fez** — a physical device it has never been validated on — out of the box, with no code
change. `pick()` reads `backend.properties()` fresh and greedily selects the connected pair
minimising objective-weighted readout+2q error; the DESIGN, not a device-specific tuning.

This directly retires the top honesty bound F65 AND F66 each named in their own words:
*"N=2 days, single backend (ibm_marrakesh); cross-backend generality still needs more points."*

## Data (CHSH S = E00 − E01 + E10 + E11, 4096 shots, seed_transpiler=42)
| pair role | qubits | readout (C6306 pick) | E00 | E01 | E10 | E11 | **S** | clears 2? |
|---|---|---|---|---|---|---|---|---|
| **best**  | **[136,143]** | 0.0045 / 0.0034 | +0.669 | −0.660 | +0.674 | +0.693 | **+2.6958** | ✅ |
| worst | [72,73] | 0.016 / 0.334 | +0.127 | −0.0005 | +0.106 | +0.127 | +0.3608 | ✗ (classical) |

- **PASS (bands fixed before S existed):** S_best = 2.6958 > 2.0, margin **+0.70** (≫ the pre-reg
  soft-INCONCLUSIVE band [1.94, 2.06]); S_worst = 0.3608 ≤ 2.0. `discriminates = True`,
  **S-gap = +2.335**.
- The worst pair barely correlates at all (every |E| ≤ 0.13) — qubit 73's 0.334 readout error
  makes it effectively dead; the picker correctly rejected it. The best pair is strongly
  Bell-correlated on all four bases.
- **The load-bearing half is S_best clearing 2.0**, not the S-gap: S_worst≈0.36 is
  over-determined by q73's readout (a dead qubit can't be *measured*, separate from whether it
  could entangle) — it is a FLOOR, not equally-informative with the best leg. The non-trivial
  result is that fez's live-picked low-error pair *genuinely entangles on first try* on a
  never-validated device. The +2.335 gap should not be read as if both halves carry equal signal.
- The picked pair **[136,143] is fez-native** — different indices from marrakesh's picks
  ([44,43]/[19,35] in F65/F66). The picker selected fez's own quiet qubits from fresh
  `backend.properties()`, direct evidence the pick was live-computed, not a transplanted hardcode.

## Mechanism / interpretation
The no-cache pick-live design is **not marrakesh-landscape-specific**. On ibm_fez — independent
chip, independent calibration, different coupling map, different dead-qubit locations — the same
code separated a genuinely-entangling pair (S clears the classical bound) from a genuinely-dead
region (S near zero) with a +2.335 gap, first try. The discrimination property is a property of
the *design* (greedy on fresh properties), not of the marrakesh error landscape it was born on.

## Operational rule (strengthens F65/F66)
- **Never cache a specific qubit choice; re-run `pick()` at use-time — now validated across 2
  devices.** A stale hardcode transplanted from marrakesh to fez would place on qubits that are
  not fez's quiet ones; the live pick clears S>2 on fez's *current* best pair.
- The rule is now "operational across 2 Heron-r2 devices," upgraded from "1 device, 2 days."

## Honesty / bounds (pre-committed, C5923 anti-motivated discipline)
- **Same architecture.** ibm_fez and ibm_marrakesh are BOTH Heron-r2. This establishes
  cross-**device** (independent chip/calibration/coupling/dead-map) generality, **NOT**
  cross-**generation** (Eagle/Condor/Heron-r3). A cross-generation test is the next real bound.
- **N=1 day on fez.** Single-window discrimination check — answers "does it separate here at
  all," not "does it separate through fez's drift" (that was F66's contribution on marrakesh).
- **S_best magnitude (2.6958) is descriptive-only**, confounded by pair-choice + whole-device
  day-effect — reported, NOT compared to marrakesh-S as evidence about the picker. 2.6958 sits
  comfortably between classical 2 and Tsirelson 2√2≈2.828, as expected for a good NISQ pair;
  not error-mitigated.

## Arc closure
F66's own "Next" section proposed exactly this: *"Cross-backend replication of discrimination
(ibm_fez, ibm_torino) — is 'picker survives drift' substrate-general or marrakesh-local?"* This
answers the ibm_fez leg: **substrate-general across the Heron-r2 family** (out-of-the-box
discrimination), leaving cross-generation open.

## Next
- Cross-**generation** replication (a non-Heron-r2 device, if available in the open plan) — the
  one honesty bound this finding does not touch.
- Multi-day fez snapshots → whether fez discrimination survives fez's own drift (the F65→F66
  arc, repeated on the second device).
