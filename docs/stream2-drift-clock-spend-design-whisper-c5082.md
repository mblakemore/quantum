# Stream 2 — "Spend the drift clock": design record (board #145) — Whisper C5082

**Status: DESIGNED TO A NEGATIVE, from banked data, $0. No flight recommended.**
**Creator GO** general#11436 (stream 2, design work). **Charter text** (#145): *a phase-sensitive
design where a needed Z-rotation is obtained by timed idle against the measured clock instead of a
gate, verified by phase accrual matching the in-window clock prediction. Needs: current-window clock
rates, gate-vs-idle comparison metric, freeze before flight.*

This record does what the charter asks — names the rates, names the comparison metric — and the
comparison kills the design three independent ways before a freeze is worth writing. Each wall is a
number from an artifact we already paid for. Per the standing rule (Creator C4925 / C4928): the
negative is kept with its full accounting, and each wall is treated as a prompt for the next use,
not an endpoint — three uses were tried, and the record shows where each stops.

## 0. Prior-art pass (the F-arc rule, run BEFORE designing)
- `knowledge-index settled "drift clock in-window precession free Z rotation timed idle"` → #144
  (revival scout, DONE), #147 (turbine design, DONE — "the wheel was correctly NOT built"), H11 T0 №4
  census, F100 (twin paradox), #142 (sentinel siphon). `buildable "Ramsey clock rate rider epoch fit"`
  → #145 itself, the gear-1 rider survey (C5073), the Aachen currency-map decode.
- Nothing settled the *spend* question; the census settled the *rate* question. So the design's
  inputs exist and its output does not — the right shape for a design row.

## 1. The rates (charter need #1), from banked artifacts
| quantity | value | source | scope |
|---|---|---|---|
| single-qubit coherent drift, gate-depth clock | **~0.21°/layer ≈ 3.7 mrad/layer**, epoch-stable, monotone 38.8° → 82.3° over the census depths at 50–90σ/row | `docs/h11-tier0-drift-clock-or-coin-census-whisper-c5018.md` (q73 flagship; CLOCK 3-of-4) | census drifters; *per layer of the census circuit*, not per µs |
| pure-idle time clock | q45 TIME-clock (population 0.200→0.034→0.248 over 0–30 µs, turning 0.213 vs 0.057 noise); q7/24/27/31/34 GATE/FLAT | `results/exp_turbine_mechsplit_decoded_c5072.json` | **population (Z-basis) only — no phase-vs-delay is banked**, so an idle *phase* rate in rad/µs does not exist in our data |
| conditional rider on native CZ | e.g. [148,152] **56.4 mrad/CZ** (se 0.33), [139,109] 276.7 mrad/CZ (se 1.94); single-qubit riders 10–41 mrad/CZ | `results/exp_gear1_rider_decoded_c5073.json` | **verdict RIDERS-BELOW-RESOLUTION: P-A 2/14 edges, P-B (in-window stability) FAILED, worst z = 79** |

The charter's premise "stable in-window" holds for the census clock in gate-depth and **fails** for
the rider field at the mrad scale (P-B). Those are different quantities; the design has to say which
one it spends.

## 2. The comparison metric (charter need #2) — and wall 1: the baseline is already free
The charter compares *gate vs idle*. On this hardware the gate is **`Rz(θ)` = a virtual frame
change**: zero duration, zero pulse, exact to the phase resolution of the compiler. Any Z-rotation a
timed idle can produce, the frame change produces at **zero cost and zero decoherence**, and for
every subsequent single-frame operation the two are indistinguishable by construction (a physical
precession relative to the drive frame *is what the virtual Z emulates*).

So the honest metric is not "idle cheaper than gate?" — it is "does idle do anything the free gate
cannot?" — and for an unconditional Z the answer is no. This is the **under-priced-baseline** class
from `tools/attack_preflight.py` (F121 lineage; my own C5027 solver framing fell to the same class):
the classical arm was priced as "a gate" when the real arm is "a free frame relabel."
**Wall 1 kills the efficiency framing of #145 outright.** Not weakly: there is no ratio to report
because the denominator is zero.

## 3. Wall 2 — even as pure metrology, the angle is coherence-limited
Suppose the aim is only the charter's *verification*: predict the accrued phase from the clock and
match it. At 3.7 mrad/layer:
- a **π/2** needs **≈ 430 idle layers**; a **π/4 ≈ 215**; the largest angle inside the depth where
  the census still resolves dθ (d160) is **≈ 0.21° × 160 ≈ 34°** — with the visibility the census
  itself reports already halved at that depth (q34: 0.25 → 0.08 across the ladder).
- The rider survey's own NO-TEST branch fires at visibility < 0.2 at 2k = 64; the census clock needs
  2.5× that depth for a quarter turn.
A Z-rotation that costs the qubit most of its coherence to reach 34° is not an actuator; it is a
thermometer reading. The metrology claim ("the clock predicts idle phase to X mrad") is *already
certified by the census at 50–90σ per row* — it does not need a flight to be re-certified, and it
does not become a gate at any depth we can reach.

## 4. Wall 3 — the one use virtual-Z cannot emulate, and it loses on the error budget
A **conditional** phase is physical: virtual Z cannot produce `CPhase(φ)`. The rider field gives one
for free by repetition — `[CZ]×2k` is ideal identity plus `k·φ_rider` conditional phase, no pulse
calibration. Priced against the native decomposition (arbitrary `CPhase(φ)` ≈ 2 CZ + 1Q gates):
- edge [148,152], 56.4 mrad/CZ: **π/4 needs 2k = 28 CZs** vs 2 native → ~14× the two-qubit error;
- edge [139,109], 276.7 mrad/CZ (the largest rider): **2k = 6 CZs** vs 2 → 3× — *and* that edge's
  r² pair is [0.75, 0.997] with the survey's overall P-B failed, so the phase it delivers is not the
  phase it delivered an hour earlier.
Wall 3 is softer than walls 1–2 (a 3× error cost on a lucky edge is a number, not a zero) but it is
walled twice: by the native decomposition and by the survey's own stability verdict. It would need
the rider field to be both large AND in-window stable, and the survey measured it as neither.

## 5. What survives (the walls as prompts)
1. **The clock is a certified instrument, not an actuator.** Its live uses are already boarded:
   A4's PUF/fingerprint candidate (H14 charter), the sentinel siphon (#142), the epoch-stability
   question (h11 (i): *is 0.21°/layer a constant or a walk?* — the one open measurement, and it
   rides free on any idle ladder anyone flies).
2. **No phase-vs-delay is banked anywhere.** If a future idle-ladder flight adds an X/Y-basis arm
   (two extra pubs), it buys the rad/µs number this design lacked at zero marginal cost — a siphon,
   not a flight. That is the only ask this record leaves behind, and it is filed as a note on #142's
   class, not as a new row (no speculative rows).
3. **The conditional-rider CPhase is a design that becomes live only if a survey ever finds an edge
   with a rider ≥ ~0.5 rad/CZ that passes P-B.** Gear-1's decode is the gate; nothing to fly now.

## 6. Disposition
- #145: **closed as designed-to-a-negative**, evidence = this record. The Creator's GO bought a
  design; the design's product is three measured walls and one free follow-on measurement.
- Not run: `attack_preflight.py --claim` — there is no advantage claim to fire it at; the class that
  applies (under-priced-baseline) is named in §2 and is the reason there is no claim.
- Not spent: 0 QPU-seconds. Every number above is from an artifact already in `results/` or `docs/`.
