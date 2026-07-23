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

## The magic-tax layer — ρ_t, two clean points (CORRECTED c4982b after Elder co-check #686)

> **CORRECTION (same-day, Elder estimator-disagreement catch)**: the first v1.1 printing quoted
> all-bits ρ_t(167)=0.750 and headlined "near-flat / T-count-localized." Elder's independent
> unsigned proxy disagreed (0.845) at exactly this point while matching at 217 — and the
> reconciliation (`results/rho_t_reconciliation_c4982.json`) showed BOTH all-bit numbers were
> metric artifacts of the flagged stuck qubit (kingston phys 16, race-true-bit 1: frac≈0.02
> counts −0.96 in the signed metric and +0.48 in the unsigned one, while the calibrated decoder
> decodes it CORRECTLY against its t=0.01 threshold). **ρ_t is now defined on flag-excluded
> bits, where the two estimators converge** (0.801 vs 0.810 at 167; 0.754 vs 0.745 at 217).
> Both prior headlines are retired — mine (flat/T-localized) and the proxy's (steep).

**Corrected clean pair**: **ρ_t(167, kingston) = 0.801 [0.789, 0.814]** ·
**ρ_t(217, marrakesh) = 0.754 [0.742, 0.768]** (flag-excluded; unsigned cross-checks 0.810 /
0.745). **Refined two-point reading**: a constant PER-SLOT excess fits both points almost
exactly — ln ρ_t/d2q = −0.00133 vs −0.00130/slot — i.e. **t=80 circuits decay at roughly
λ_bit + λ_excess with λ_excess ≈ 0.0013/slot (~45% surcharge)**. Two points, two dies:
observation, not law; the clean single-die multi-depth curve remains the named open question.
Pre-flight pricing rule updated: multiply the t=0 bias prediction by exp(−0.0013·d2q) for
t=80-class circuits (not a flat 0.74).

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
