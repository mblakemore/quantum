# H10-C2 PRE-REGISTRATION — Vacuum Entanglement Harvest with the Exchange Channel Removed

*Whisper C5018, 2026-08-02, substrate claude-fable-5. Status: **FROZEN TEXT, awaiting Ember
spec-seal + Creator GO** (Elder grader seat at landing; his co-check = deterministic re-runs
of the committed scripts). Parents: scout `h10-c2-entanglement-harvesting-scout-whisper-
c5018.md` (§§1-8, GO), campaign artifacts `h10_c2_harvest_sim_c5018*.json`, route
`h10_c2_asflown_r_c5018.json`, prep `h10_c2_givens_prep_c5018.json`, arm bars
`h10_c2_armbars_r6_c5018.json`. Every number below is computed in committed artifacts;
every frozen input is reproducible from committed code.*

## 1. Claim shape (printed first)

Two detector qubits, coupled to **provably non-interacting halves** of a lattice field
sharing an entangled vacuum, end the protocol entangled — while the identical protocol on a
product state yields exactly zero. **The claim is about THIS chain's ground state as an
entanglement resource** (Reznik's vacuum-harvesting, in its sharpest operational form: the
exchange channel is REMOVED by construction, not bounded); no claim about spacetime, the EM
vacuum, or cosmology. Statistic categories per the C5014 rule: G1 is a SIGN+BAND test on an
entanglement monotone; G2 is a NULL-consistency test; everything else is reported. The
famous-sounding sentence this flight can earn, stated with its fence: *entanglement was
mined from a (lattice) vacuum by detectors that could not talk* — "could not talk" meaning
the coupling graph between the halves was empty, certified by construction and by the
measured cone arm.

## 2. Frozen design

- **Field**: XX chain, L=8, J=1 (H_f = J Σ (X_jX_{j+1}+Y_jY_{j+1})/2), open boundary.
- **Vacuum prep (EXACT, no variational error)**: Givens network, **22 adjacent-pair real
  rotations** (angles frozen in the committed artifact), applied to |11110000⟩ — the
  half-filled Slater determinant. KA passed at machine precision (fidelity
  1.000000000000, energy resid 1.5e-14).
- **Detectors**: 2 ancillas, gap Ω=1.5 (H_d = Ω|e⟩⟨e|), UDW-coupled at s1=2, s2=5 (d=3):
  H_int = λ [X_{s1}X_{d1} + X_{s2}X_{d2}], λ=0.6, **top-hat** window T=2.5 (the smooth-
  switching literature prediction failed to port on this lattice — scout §7, tested).
- **Evolution (as-flown route, frozen)**: circuit-faithful 2nd-order stepping, **r=6**
  (per step: half-sweep of bonds in order, detector couplings + detector phases, reversed
  half-sweep). KA: r=64 reproduces the exact campaign at 3.8e-6; the r=6 bias is +0.9% and
  is IN the registered bars (like-for-like).
- **The cut (the fence as a construction)**: the harvest arm evolves with bond (3,4)
  REMOVED — the two halves have an empty coupling graph; no exchange channel exists. The
  full-chain arm (bond restored) measures the exchange contribution as a difference.
- **Backend**: any Heron ≥10 qubits; ALT2 open instance (explicitly named account;
  `service_for_submission`, no fallback — the c4217_018 discipline).

## 3. Arms, registered gates, reported rows (as-flown r=6 values)

| Arm | Prediction | Status |
|---|---|---|
| A1 cut harvest (tomography) | **N_cut = 0.0488** | **G1: N̂ > 0 at ≥5σ AND within 0.0488 ± max(3σ_N, 0.015)** |
| A4 product control, cut (tomography) | **N = 0 exactly** | **G2: N̂ consistent with 0 (≤2σ)** |
| A2 full-chain arm (tomography) | N_full = 0.0427 | R1 (reported): exchange contribution N_full−N_cut = −0.0061 with CI — the exchange-damages-the-harvest specimen. **Deliberately NOT gated: the gap is ~0.4σ at these budgets — a gate that cannot be powered must not be registered** (the Amendment-1 lesson applied at design time). |
| A3 no-coupling floor (Z-basis) | zeros | R2 (reported) |
| A5 cone certification | front curve R(d,t) per the committed campaign table; hardware: ε=π/4 X-kick at s1, ⟨X_{s2}⟩(t), 8 points | R3 (reported): measured front vs exact overlay — the empirical cone the construction replaces |
| A6 books | P_e1 = 0.0626, P_e2 = 0.0622, ΔE_field = +0.884 | R4 (reported): the switching work that pays for the mining, each within 3σ |

**Registered verdict = G1 ∧ G2.** Everything else is published either way.

**Decode (frozen)**: 9-setting 2-detector tomography → linear-inversion ρ̂ → negativity
N(ρ̂); uncertainty via parametric bootstrap, seed 20260802, 4000 resamples; P_e from the
same Z-marginals. No mitigation (the claim is arm-comparative on one device, F94/F95
grammar; readout asymmetry lands in R4's books).

## 4. Budget

Tomography arms A1/A2/A4: 9 settings × 11,000 shots = 99k each (5σ on N=0.0488 needs
~10.5k/setting). A3: 10k. A5: 8 × 5k = 40k. A6 field-energy settings: 2 × 10k = 20k.
**Total ≈ 456k shots ≈ 40–80 QPU-s** (10-qubit, ~300-gate circuits) against ALT2 ~576s at
drafting — re-read at every submission, per rule. Single stage (no pilot needed: the gates'
power does not depend on an attenuation unknown — negativity contrast degrades gracefully
and G1's band is the honesty check; if hardware washes the state, G1 FAILS loudly and that
is the registered outcome).

## 5. Kill / no-fly conditions

1. **Flight-script KA fence (mandatory)**: an instruction walker over the AS-BUILT pubs
   must reproduce every §3 number at 1e-6 (prep from the frozen Givens angles, r=6 route,
   both cut and full arms, the A4 zero, the A5 front points). Non-completion = FAIL.
2. **Depth HOLD**: transpiled 2q count > 500 on the chosen chain → hold (logical
   284–306; routed estimate 454–490 vs the C1-calibrated 475 ceiling — the transpiler's
   actual number decides, against a stated bar, not hope).
3. Calibration hold: median 2q error on the chain > 0.5% → hold.
4. Pool re-read at submission; overdraw → not submitted.

## 6. Seats

Whisper: flight + decode + this text (decode is frozen §3 arithmetic). Ember: spec-seal
(ancestry commit pre-submission; no secret to hold). Elder: grader at landing (mechanical
against §3) + deterministic re-run co-check of the four committed scripts at his
convenience. Creator: GO (~456k shots, ~40–80 QPU-s, ALT2).

*Frozen text ends. Changes after Ember's seal require a numbered amendment. A different
instrument (L≠8, different chain, interferometric variants) re-enters at scout, not by
amendment — the laundry rule.*
