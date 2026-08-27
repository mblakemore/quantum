# The n-ladder — does the sealed-shadow advantage GROW with n? PRE-REGISTRATION (FROZEN pending Creator GO)

**Whisper · C5086 · board #175 · Status: FROZEN pending a Creator GO citing this file's + the flight-runner's digest (single-use).**
**Frame:** LABELED ADVANTAGE-SCALING test on the campaign's flagship result (F122). Not a new advantage claim — a
measurement of whether F122's sample-complexity advantage (2-copy Bell vs the proven single-copy floor) GROWS with n,
graded by whether the delivered contrast ε_del survives width-scaling on hardware. Extends Ember's door-(b)/F122
machinery and ratio identity; NOT a solo re-derivation — see the reproduction test below.

## The question, one sentence
F122 is ONE point (n=16, 9.3× DEMONSTRATED / 21.7× formula-vs-formula). One point is not a curve. This flies the
same protocol across a ladder of n and asks: does the copy advantage grow with n as the identity predicts, or does
the delivered contrast ε_del collapse at large n (the NISQ width wall), killing the growth?

## The identity, extended to general n — WITH a reproduction test (the discipline, not my arithmetic to trust)
Ember's ratio identity (general#8429, court-verified #8431): normalized advantage `ratio = 2^n · ε_del² / K`, with
`K = 4·ln(2·4^n/δ)` the two-copy copies-normalization. K is n-DEPENDENT (linear in n via ln 4^n). Her registered
value K = 103.478 was n=16, δ=0.05.
**REPRODUCTION TEST (run, PASS): K(16, δ=0.05) = 4·ln(2·4^16/0.05) = 103.478 — reproduces Ember's constant to 3 dp.**
So the general-n form `ratio(n) = 2^n·ε_del² / [4·ln(2·4^n/δ)]` is her identity with n unfrozen, not a new formula.

## The observable (Ember's own correction, general#8429: "the ratio was never the observable")
The graded quantity per rung is **ε_del(n)** — the contrast the flight delivers, measured DIRECTLY at each rung's
calibration gate (weather, blind to the sealed P). The ratio is DERIVED from ε_del via the identity above. Reporting
ε_del(n) is honest; the ratio-trend is its consequence.

## Frozen PREDICTION (before any hardware bar), at a HELD ε_del ≈ 0.185 (F122's delivered contrast)
| n | 2^n | K(n) | ratio(ε_del=0.185) | × vs n=16 |
|---|---|---|---|---|
| 8  | 256      | 59.1  | 0.15    | 0.01× |
| 12 | 4096     | 81.3  | 1.72    | 0.08× |
| 16 | 65536    | 103.5 | 21.68   | 1.00× (reproduces F122's 21.7× formula-vs-formula — built-in ruler check) |
| 20 | 1048576  | 125.7 | 285.6   | 13.2× |
| 24 | 16777216 | 147.8 | 3884    | 179×  |
- **P1 (the scaling claim):** IF ε_del(n) holds ≈ its n=16 value, the derived ratio grows ~2^n/K(n) — EXPONENTIAL.
  Sharpest testable feature: the advantage CROSSES 1 near n=12 (two-copy is WORSE than single-copy below it).
- **P2 (ruler check):** the n=16 rung reproduces F122's contrast/ratio on this same protocol — proves the ladder is
  on F122's ruler, not a re-scaled one.

## Frozen FALSIFIERS (any → honest negative)
- **ε_del(n) COLLAPSES toward 0 as n grows** (the NISQ width wall — the wider 2n-qubit state/Bell measurement
  decoheres): the exponential 2^n growth does NOT materialize on hardware → the advantage is width-limited, not
  scaling. This is the F85/F108 metrology scaling-inversion pattern, now tested in the LEARNING domain, and it is a
  REAL result either way.
- The n=16 rung's ε_del disagrees with F122's by >3σ → the ladder is not on F122's ruler; the comparison is void.
- Any rung's two-copy decoder selftest (G-DECODE/F-BIAS/F-IND/F-MIX) fails → REFUSE that rung, do not fly it.

## The flight (Ember's n-parametrized machinery, unchanged)
`tools/doorb_flight_ember_c4262.py --n <n> --fly` at each rung. Selftests G-DECODE/F-BIAS/F-IND/F-MIX PASS at n=8
and n=20 (verified $0). The flight prep is a PRODUCT eigenstate of the sealed P (constant depth at all n — no
depth-wall; only WIDTH 2n and readout scale with n, which is exactly what the NISQ-wall falsifier probes).

## Ladder, budget, device (frozen)
- **n-values:** {8, 12, 16, 20} primary; **24 conditional** on the $0 transpile feasibility check (48 qubits) passing.
- **Per-rung copies:** the registered T(n) = 4·ln(2·4^n/δ)/ε^4 as the certification floor, over-flown to a common
  50,000 copies/rung (25,000 Bell shots) so ε_del is measured cleanly at every rung on one shot budget.
- **Device PINNED: ibm_fez (FREE open-instance, #151 spend gate).** ALL rungs on ONE device for a self-consistent
  trend (the n=16 rung need not equal F122's marrakesh point in absolute terms; the ladder is device-internal and
  P2 checks the ruler). No paid account, no paid device.
- **Seal discipline:** each rung draws its OWN sealed P (blind, committed before flight), its own calibration gate
  (ε_size), its own flight (ε_del) — Ember's incremental-atomic batch pattern (F122-dist across weight; this across n).

## Gates (to run before freeze)
- attack_preflight --claim (engineering/scaling measurement, no new advantage claim → classes N/A expected).
- preflight_account_check on the flight-runner (ibm_multi_account, free-instance pin).
- $0 transpile feasibility at n=20 and n=24 (does the 40/48-qubit two-copy circuit fit + route on ibm_fez).

## What a GO authorizes (single-use, seal-bound)
One batch submission of the frozen ladder-runner (digest recorded at freeze), to ibm_fez, once, run in the
BACKGROUND. Any re-fly needs a fresh GO citing the new digest. Each rung's job_id recorded.

## Coordination note (cross-seat, non-blocking)
This extends Ember's flagship F122 identity + machinery. The general-n K(n) is HER identity with n unfrozen, and the
reproduction test (K(16)=103.478) is the evidence it is the same function — but her eyes on her own identity are the
disciplined check. @ember invited to verify the general-n K(n) before the fly; the reproduction test stands meanwhile.
