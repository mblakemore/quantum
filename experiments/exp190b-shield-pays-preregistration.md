# Exp190b Pre-registration — THE SHIELD PAYS, redesigned (Shields stage iib)

**Cycle**: C4881 · **Date**: 2026-07-19 · **Backend**: ibm_fez · **Shots**: 8000 × 10 circuits
**Derived from Exp190's three owned flaws + retro R2 — every fix rule-cited, none data-located.**
Creator go: "Retro then fly" (general#133). Checklist template items 8–10 applied at design time.

## The redesign (flaw → fix)

1. **Short-T sweep into the p² regime** (190 flew at p ≈ 0.06–0.11 where distance-2 loses):
   T ∈ {0, 0.5 μs, 1 μs} (0/1000/2000 dt).
2. **State-population-fair echoes** (item 8; 190's bare arm ate T1 in |11⟩ half the idle):
   quarter-point pairs — idle T/4 · X · idle T/2 · X · idle T/4 — net identity, symmetric
   excited-state exposure for every computational state, both arms (X per bare qubit, XXXX =
   the stabilizer on the logical block).
3. **Differential coverage vs attrition-matched nulls** (item 7-extended; 190's absolute bars
   drowned in 44–61% baseline attrition): four arms — {clean, inject-Z} × {mid-syndrome,
   no-mid} — and the registered quantities are the *differentials*.
4. **No window-echo rung** (item 9: at 190's logical-error 0.38 nothing resolves; that rung
   returns in stage iii where it has headroom).
5. **Condition-aware bands** (item 10 / retro R2): priced from TODAY's measured bare curve
   (6.4%/qubit at 2 μs echoed → ~1.5–4.5% at 1 μs quarter-point-echoed), not from prior days.

## Circuits (10)

Survival X-family: Lx_T0, Lx_T1, Lx_T2 · bx_T0, bx_T1, bx_T2 (all quarter-point echoed).
Coverage quad (Z-family, one 1 μs idle each side of the syndrome block):
synd_clean_mid · inject_z_mid · clean_nomid · inject_z_nomid.

## Pre-registered criteria (formulas)

Let e_L(T) = accepted logical X-err/qubit, e_b(T) = bare X-err/qubit, se(e,N)=√(e(1−e)/N),
N_L = 2·8000·acceptance, N_b = 16000; rej(c) = rejected/total for coverage arm c.

- **Survival primary**: `z = (e_b(T2) − e_L(T2)) / √(se_L² + se_b²) ≥ 3` with T2 = 1 μs;
  ratio band e_L/e_b ∈ **0.25–0.90**. Registered-expected non-goal: e_L(T0) > e_b(T0)
  (encode overhead); the **crossover time** (interpolated e_L = e_b) is a reported deliverable.
- **Coverage**: `Δ_mid = rej(inject_z_mid) − rej(synd_clean_mid) ≥ 0.40` (attrition-matched:
  same circuit ± one Z) AND `Δ_nomid = rej(inject_z_nomid) − rej(clean_nomid) ∈ [−0.05, +0.10]`
  (terminal blindness: the Z adds nothing without the mid syndrome).
- **Gauges**: acceptance Lx_T2 ≥ 0.80 (short idle); coverage-arm acceptances reported with
  their differentials (no absolute bars — that was the flaw).

## Fences

As 190 (distance-2 detection; one syndrome round; one die) + the boundary context: 190
established the losing end at 2–4 μs on a brutal day; iib maps the winning end and the
crossover. If today's dose stays anomalous even at 1 μs (bare > 6%), the regime may again be
out of reach — that outcome would *extend* the boundary measurement, not void it (registered
two-sided).

## Discipline

ps aux: clean; claim exp190 series (whisper C4880/81). Ledger pre-submit. Prereg committed
before decode. Selftest gates: all clean arms exact; quarter-point pairs exact identities;
Δ_mid = 1.0 and Δ_nomid = 0.0 noiselessly.
