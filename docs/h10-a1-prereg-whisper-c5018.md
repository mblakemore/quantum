# H10-A1 PRE-REGISTRATION — The Quorum Fact: objectivity with an access-control list

*Whisper C5018, 2026-08-02. Status: **FROZEN TEXT, awaiting Ember spec-seal + Creator GO**
(Elder grader at landing). Parents: scout `h10-a1-quorum-fact-scout-whisper-c5018.md` (GO;
campaign exact), bars `results/h10_a1_prereg_bars_c5018.json`, campaign
`results/h10_a1_quorum_sim_c5018.json`. Every number computed in committed artifacts. The
full C5018 doctrine set is applied by construction: four-edge gates (resolution / ceiling /
fault ladder / validity), three-state verdicts, positive-condition controls, co-batched
single-job validity, exact-fraction registered values, job-named artifacts.*

## 1. Claim shape (printed first)

A recorded fact whose custody is (2,3)-quorum-gated on a chip: any 2 of 3 record shares
read it (deterministically), any single share is provably blind, a sub-quorum can neither
revive the recorded event's superposition nor destroy the fact, and the record's erasure
has exactly the three auditable exits the campaign derived — refund (unanimous uncompute),
conversion (measured erasure selecting the story, flat unsorted receipt), exile (shares
leave, custody goes with them). **The claim is the THRESHOLD SHAPE of objectivity — a step
at quorum — against a plain-redundancy control on the same hardware.** Chip analogue;
statistic categories: G1/G2/G4 are BAND tests on operational dial readings, G3/G5 are
THRESHOLD tests on contrasts; the scramble-exit is NOT flown (forbidden by physics —
campaign W4 — and stated as such, not tested).

## 2. Frozen design

- **Encoding**: coherent (2,3) Shamir over GF(4) (committed constructor): D + 6 share
  qubits, all-Clifford, ~30 CX logical. Mask register uncomputed in-circuit.
- **Dial readout (the depth gift, stated)**: the pair decoder is GF(4)-LINEAR — Lagrange
  reconstruction is a classical XOR of share bits — so EVERY dial pub is Z-basis
  measurement + pre-registered classical decoding. **No Helstrom rotations exist in this
  flight** (the B1-P lesson applied at design: max pub depth ≈ encoding + 3 CX).
  Dial(coalition) ≡ 2·p̂(correct b) − 1 with the frozen decoder.
- **Arms (one co-batched job — edge-4 validity by construction)**:
  A1 threshold dial: {3 singles, 3 pairs, triple} × b∈{0,1}, 500 shots/pub (14 pubs).
  A2 redundancy control: same 14 pubs with the plain-copy map.
  A3 revival: encode → uncompute → X(D), 2000 shots.
  A4 sub-quorum: seeded random 2-qubit scramble on share 3 (3 frozen seeds) × {D-contrast
  pub, pair-(1,2)-dial pub}, 1000 shots each.
  A5 story: all shares X-basis + D X-basis, 4000 shots (16-outcome sort).
  Total ≈ 30k shots ≈ **2–4 QPU-s. The cheapest flight of the campaign.**
- **Backend**: any Heron ≥7 qubits, ALT2 (`service_for_submission`, no fallback), ALAP+DD
  hardening as standard from B1b onward (identity at logical level).

## 3. Registered gates (three-state each: PASS / FAIL / UNDERPOWERED) and values

| # | Gate | Bar | Edge audit |
|---|---|---|---|
| G1 | threshold shape | all three singles dial ≤ **0.10** AND all three pairs dial ≥ **0.85** | resolution: step 0.75 ≥ 17σ at 500/pub · ceiling: dial ≤ 1 by construction · faults: mask-stuck reads singles = 1.0 → FAILS the cap |
| G2 | control health (positive) | control-map singles dial ≥ **0.85** | a dead apparatus reads ≈ 0 → FAILS; positive & missable |
| G3 | revival | D X-contrast ≥ **0.80** | catches the dial-INVISIBLE fault: no-b-on-share encoding fault leaves every dial reading ideal but kills revival to ≈ 0 (computed: b=1 branch overlap exactly 0) |
| G4 | sub-quorum custody | post-scramble D-contrast ≤ **0.10** AND pair-(1,2) dial ≥ **0.85** | both directions of the custody claim, each positive/missable |
| G5 | story selection (positive) | sorted weighted mean \|⟨X⟩_D\| ≥ **0.70** | the flat unsorted marginal (\|⟨X⟩\| ≤ 3σ) is the REPORTED no-signalling receipt — a null row, deliberately not gated |

**Registered verdict = G1 ∧ G2 ∧ G3 ∧ G4 ∧ G5.** Ideal values: dial tables exactly
{singles 0, pairs 1, triple 1} threshold / {1,1,1} control; revival 1; story sorted 1,
unsorted 0 — all exact fractions/integers (no truncated literal exists in this prereg;
the fence targets are the integers 0 and 1).

**The fault-coverage matrix is part of the registration** (each computed fault names its
catching gate): mask-stuck → G1 singles-cap; no-b-encoding → G3; dead apparatus → G2;
scramble-leak → G4. A fault with no catching gate would be a registration gap — none is
known; any found later documents, it does not re-band.

## 4. Kill / no-fly conditions

1. KA fence: exact walker over as-built pubs reproduces every §3 ideal at **1e-9**
   (integer targets — satisfiable by construction; the satisfiability checker should
   find nothing).
2. Depth HOLD: any transpiled pub > **100** 2q gates (estimate ~35 with routing).
3. Calibration hold: median 2q error on used qubits > 0.5%.
4. Pool re-read at submission; DD-failure HOLD (as B1b).

## 5. Seats

Whisper: flight + decode + text (decode = counts → classical Lagrange/decoders → gates;
no discretion). Ember: spec-seal (prefix recipe; satisfiability check as first customer).
Elder: grader at landing. Creator: GO (~30k shots, 2–4 QPU-s, ALT2).

*Frozen text ends. Changes after seal by numbered amendment; outcome entries append under
the prefix convention; text freezes at the seal-request post.*
