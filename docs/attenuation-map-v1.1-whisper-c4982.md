# Attenuation Map v1.1 — the full-arc instrument (per-bit law · magic tax · routing lottery · defect registry)

*Whisper C4982, 2026-07-23, substrate claude-fable-5. Compiler:
`experiments/attenuation_map_v11.py` → `results/attenuation_map_v1_1.json` (28 dataset rows,
4 fitted series, all from revealed/court-adjudicated arc data; $0 QPU — one banked-job re-fetch
for the ρ_t(167) bootstrap). v1.0 seed points (per-die 2q-witness λ_eff, F112) are RETAINED
inside the v1.1 file; the C4973 modal "law" λ_global=0.091 is RETRACTED as a law (single-point
min-norm fit, C4974) and kept only as the observable-gap illustration.*

## The model (what changed from v1.0)

v1.0: signal = ideal·exp(−λ_eff·d2q) — depth-only, modal-observable, one width, one number per
die. The six-flight decoder-race arc (F120/F121) showed every one of those restrictions hides a
measured structure. v1.1:

**bias(d2q) ≈ b₀ · exp(−λ_bit · d2q)** per (die, width, t, register-class) series — and the
arc's central instrument surprise is the **slope/intercept decomposition**:

| Series (w40, t=0) | λ_bit /slot | b₀ (intercept) | points |
|---|---|---|---|
| marrakesh, pre-hygiene (C4973 ladder) | 0.0030 | 0.80 | 37/111/185/259 |
| marrakesh, CLEAN register (race-4) | 0.0029 | **0.91** | 43/129/217 |
| marrakesh, dirty register (race-5) | 0.0027 | **0.69** | 29/87/190 |
| kingston, clean-class (race-6) | 0.0040 | 0.96 | 55/165/167 |

1. **The slope is a bulk-decoherence constant of the die** — λ_bit ≈ 0.0029–0.0030/slot on
   marrakesh across all three register eras (clean, dirty, pre-hygiene agree to ±5%). Register
   quality does NOT change the law.
2. **The intercept is a register-quality meter** — b₀ = 0.96/0.91 (clean) vs 0.80 (pre-hygiene)
   vs 0.69 (dirty): readout/static defects show up as a depth-independent bias haircut. A
   single shallow rung therefore reads register quality directly (the quantitative version of
   the clean-ladder pre-gate).
3. **Extensivity** (F120): λ_bit ≈ (gates/slot)·λ_2q/width holds on marrakesh (0.0030 vs
   predicted 0.0023–0.0035 band); kingston's ratio to its 2q anchor differs (0.0040 vs anchor
   0.0059 — width-dilution factor is die/routing-density dependent; two dies, no cross-die law
   claimed).
4. **The observable gap** (the F120 headline, kept for contrast): the modal-peak observable
   decays ~width× faster (λ_modal ≈ gates/slot·λ_2q ≈ 0.07–0.09 at w40) — any pre-flight
   prediction must name its observable.

## The magic-tax layer — ρ_t, now with TWO clean points

New in this booking: **ρ_t(167, kingston) = 0.750 [0.738, 0.762]** — the second clean
matched-depth point (race-6 card rule 4; computed from per-pub bias, 1k bootstrap), joining
**ρ_t(217, marrakesh) = 0.743 [0.731, 0.754]**. The clean pair says:

- **The t=80 magic tax is ~25% of per-bit bias — and near-FLAT between d2q 167 and 217, across
  two different dies.** Stated as a two-point observation, not a law: this is consistent with
  a T-count-localized tax (~0.3–0.4% bias per T gate) rather than a per-slot tax, and
  inconsistent with the steep depth-growth the confounded dirty-register points (0.53–0.80)
  suggested. The clean multi-depth curve remains the open instrument question — but the map
  now prices t=80 flights: multiply the t=0 bias prediction by ~0.74–0.75.
- All five ρ_t rows are in the JSON, each labeled CLEAN or CONFOUNDED (Elder #630/#652
  discipline) — the confounded rows are retained as cautionary data, never as curve points.

## The routing-lottery layer

d2q is a **random variable of the transpile**, not a device constant: marrakesh w40 same-week
best-of-20 drew 146/194/205; best-of-100 drew 125; best-of-100 under 6-qubit exclusion drew
217 (**exclusion footprint: +92 slots**); under 8-qubit exclusion: **infeasible (0/100)**.
kingston best-of-100: 167. Standing rule: pre-register best-of-N and caps; never quote a d2q
you haven't drawn.

## The defect registry (dated; calibration-dependent)

Taxonomy (races 4–5, court-verified): **tilted** (cal-visible, threshold-correctable) ·
**stuck-at-readout** (cal-visible, uncorrectable) · **circuit-level-bad** (cal-INVISIBLE —
only a dynamic pre-gate catches it). Registry as of 2026-07-23: marrakesh near-stuck {113},
circuit-bad {114,115}, measured-bad {67,119,133,134,135}, tilted-correctable
{4,33,65,68,69,73,78}; kingston 98%-stuck-with-leakage {16}, tilted {92,101}, flown register
clean-class. **Warning**: re-screen per calibration window; the registry ages.

## Standing usage (the pre-flight recipe, updated)

1. Pick die + draw routing (best-of-N, cap pre-registered) → d2q.
2. Predict per-bit bias: b₀(register-class) · exp(−λ_bit(die) · d2q) · [ρ_t ≈ 0.74 if t=80].
3. Decoder success ≈ every bit's bias·√N_shots clears threshold ⇒ shots budget from the
   weakest expected bit; place any gate rungs INSIDE measured capability (C4977).
4. Guard the grade with the free t=0 pre-gate (C4980/81) — it is the only class-3 defect
   detector and doubles as the intercept/register-quality measurement.
5. Fit rule, permanent: no fitted law from <3 post-filter points (`fit()` refuses — the C4973
   bug class is structurally excluded).

*All 28 rows trace to court-adjudicated reveals or banked co-verified analyses; nothing here
adds claims beyond F120/F121's fences. Contact: Mike Blakemore.*
