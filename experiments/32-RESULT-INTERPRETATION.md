# Exp32 — Transient-Floor Spectroscopy: RESULT INTERPRETATION

**Cycle**: C3740 (Whisper) | **Backend**: ibm_kingston | **Job**: `d8culgdmdsks73d337gg` (DONE, 17 circuits)
**Purpose**: Turn the Exp31 confound (anomalous ~20.36pp gate-independent Bell fidelity floor) into a *mapped signal*, and answer Creator's three transient-floor questions with hardware.

## The do() generalization

Exp29/30 used `do(gate-count)` vs `do(duration)` to sever a collinearity. Exp32 applies the same intervention logic to four candidate floor sources — each arm is a `do()` on one axis while holding the Bell circuit fixed:

| Arm | Intervention | Question answered | Result |
|---|---|---|---|
| A — SPAM | `do(basis-prep)`: prep \|00/01/10/11⟩, X-only, no entangle | "map it" (Q1) | readout floor **2.744pp = 13.5%** of the 20.36pp Bell floor |
| B — Layout | `do(layout)`: same Bell on 3 CZ pairs | "map it" (Q1) | floors **7.84 / 9.01 / 99.10pp** — layout is the dominant lever |
| C — Drift | `do(time)`: bookend Bells at circuit #0 and #last | "before AND after / time vector" (Q2) | drift **0.195pp ≈ 0** — floor is **stable, not transient** |
| D — Collision | `do(coherent-phase)`: inject RZ(θ), sweep, fit A·cos(θ+φ) | "collide w/ perturbations" (Q3) | **φ = −0.039 rad ≈ 0** (no coherent stray-Z); (1−A) → **6.80pp incoherent** |

## Findings

**1. The floor is NOT transient (Q2 answered, framing corrected).** Bookend Bell error first=7.08pp, last=6.885pp → drift 0.195pp, within shot noise. This holds *even though the device recalibrated mid-run* (submit 19:14:50 → finalize 19:30:06 UTC, `recalibrated_during_run=True`). The floor is a **stable structural property**, not a time-varying transient. Creator's "transient floor" label is corrected to **structural floor**.

**2. The floor is NOT coherent miscalibration (Q3 answered).** ARM D's injected-phase response fits a clean cosine with φ≈0 (−2.2°). A coherent stray-Z would show up as a non-zero phase offset; it doesn't. The residual (1−A=0.068 → 6.80pp) is amplitude-damping/depolarizing — **incoherent**. This is the cleanest possible split: coherent ≈ 0, incoherent = 6.8pp.

**3. Layout quality is the dominant lever, and one dead qubit explains the worst case (Q1 answered).** Calibration confirms the mechanism, not just the magnitude:
- Pair (73,74): floor 7.84pp, ZZ=0.922 — **good** (q146-free)
- Pair (69,78): floor 9.01pp, ZZ=0.910 — **good**
- Pair (146,147): floor **99.10pp**, ZZ=0.009 — **dead**: q146 readout_error=**0.518** (coin flip), T1/T2=**null** (uncharacterizable), cz_146_147 error=**1.0** (gate flagged 100% broken).

This is decisive: the floor is a *function of layout*, ranging 8→99pp. `floor_uniform_high=False` rules out a device-wide floor.

**4. SPAM is real but a minority (Q1).** 2.744pp / 13.5%, and it is T1-asymmetric: readout error grows |00⟩ 0.95pp → |01⟩ 1.62 → |10⟩ 3.75 → |11⟩ 4.65pp. The |1⟩-heavy states relax 1→0 during the measurement window — a recognized, mechanistic readout error, not a mystery.

## Verdict — floor classification

Of the four C3739 candidate classes (SPAM / bad-pair / coherent-miscal / device-wide-transient):

- ❌ **coherent-miscal** — ruled out by ARM D (φ≈0)
- ❌ **device-wide-transient** — ruled out by ARM C (no drift) + ARM B (non-uniform)
- ✅ **bad-pair** — decisive for the 99pp case (dead q146; calibration-confirmed)
- ✅ **SPAM** — real minority (13.5%, T1-asymmetric readout)
- ✅ **incoherent decoherence** — on a *good* pair, residual ≈ 6.8pp, consistent with the Exp29/30 duration/decoherence mechanism (T2 ~110–160µs on these qubits)

**On a good pair, the floor decomposes ≈ 2.7pp SPAM + 6.8pp incoherent decoherence ≈ 9pp** (matches the (69,78) 9.01pp observation). Exp31's higher 20.36pp likely reflects a worse pair / deeper circuit — the floor is not a universal scalar.

## Consequence for ORQ#1 (X-basis immunity cross-backend)

Exp31 was confounded because it landed on/near a bad layout. **Clean retest recipe**: select layout pairs by calibration (reject any qubit with readout_error > ~0.05 or null T1/T2; reject CZ error ≥ 0.01), run on a verified-good pair where the floor is ~9pp and stable, then the ~3× X/Z fidelity ratio (the mechanism under test) is no longer swamped. The dominant residual on a good pair is incoherent — exactly the channel X-basis measurement is hypothesized to dodge, so the retest is now well-posed.

## Honest caveats

- `corr(floor, recorded_cz)=None`: the per-pair recorded-CZ fields were null in the ARM B rows, so the floor↔calibration correlation is qualitative (dead-pair calibration nails the worst case) not a fitted coefficient. Wiring `backend.target` CZ errors into ARM B rows is a one-line fix for next run.
- n=3 layout pairs; the 99pp pair is a single (calibration-confirmed) anecdote.
- ARM C is one before/after bookend pair; "no detectable drift" within shot noise, not "proven zero."
