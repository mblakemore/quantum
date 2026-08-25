# Counterflow Flight C — the Information Recuperator (directional QET): PRE-REGISTRATION (FROZEN)

**Whisper · C5082 · board #196 · Status: FROZEN pending the Creator GO citing this file's + the flight script's digest.**
**Frame:** LABELED PHYSICS RESULT (not a quantum-advantage claim). A directional QET effect realized on qubits,
graded by whether the pre-registered SIGN-FLIP survives on hardware against its own controls — not by beating any classical baseline.
**Classical/exact reference:** `counterflow_sim_c_whisper_c5080.py` (density-matrix sim; every circuit piece validated against it).

## The claim, one sentence
In a thermal gradient realized by local generalized amplitude damping (GAD), the DIRECTION of the QET information
stream — measure the COLD site and rotate the HOT site (counterflow) vs the mirror (co-flow) — changes which flow
extracts more local energy, and that preference **flips sign** as the gradient strength γ increases.

## Observable (frozen)
- Per arm: `extract = e_post(θ*) − e_pre`, where `e = <obs_rot>` on the rotated site, `obs_rot = Z_rot + 2 X_rot X_meas`.
  Since the measured site is read in X (outcome μ), `X_meas → μ`, so `obs = Z_rot + 2 μ X_rot`, binned by μ,
  readout-error-mitigated with a bare-qubit per-qubit calibration applied identically to every arm.
- `direction = extract_cf − extract_co`  (the graded quantity).
- `info_value = extract_cf − extract_cf_severed`  (control: the measured bit vs a fresh fair coin).

## Arms (all in one job)
1. **counterflow (cf)** — measure COLD site (s0, bath P_COLD), conditional-rotate HOT site (s1, bath P_HOT).
2. **co-flow (co)** — mirror: measure HOT (s1), rotate COLD (s0).
3. **severed** — cf schedule and θ*, but the rotation is DECOUPLED from μ (50/50 average of Ry(±2θ*_cf) applied
   unconditionally = a fresh fair coin). Isolates what the measured BIT buys.

## Frozen parameters (pre-registered; the hardware uses these, NO live scan)
- N=2 sites. H = Z0+Z1+2 X0X1 (offset E_ground=0). Ground prep |g>=cos a|00>−sin a|11> → ry(−2a,0); cx(0,1).
- Gradient: local GAD toward P_HOT=0.40 (hot, s1) and P_COLD=0.05 (cold, s0) at strength γ, realized as a
  partial-SWAP(φ=arcsin√γ) with a MIXED bath ancilla (Ry to p_bath + env-qubit trace). Validated == sim.gad_kraus to 4 dp.
- Two regimes: **γ_lo = 0.2, γ_hi = 0.5**.
- θ* (argmin of e_post from the exact sim, FROZEN): (0.2,cf)=+0.1440, (0.2,co)=+0.0654, (0.5,cf)=+0.0785, (0.5,co)=−0.3665.
- Shots = 20,000 per circuit. Backend ibm_fez (free open-instance, #151 spend gate).

## Pre-registered PREDICTIONS (frozen before hardware)
- **P1:** direction(γ_lo=0.2) < 0 (co-flow extracts more at low gradient). Ideal −0.0558.
- **P2:** direction(γ_hi=0.5) > 0 (counterflow extracts more at high gradient). Ideal +0.1966.
- **P3 (the claim):** the SIGN FLIPS — P1 and P2 both hold.
- **P4 (control):** info_value(γ_lo) < 0 — the measured bit enables energy extraction a fresh coin does not, in the
  regime where the effect is large (sim −0.14). The high-γ info_value is small (sim −0.024) and noise-scattered, so it is
  REPORTED, not gated (registered this way after the dry-run showed high-γ info_value scatter across zero).

## Pre-registered FALSIFIERS (any → the claim fails, recorded as an honest negative)
- direction(γ_lo) ≥ 0 OR direction(γ_hi) ≤ 0 → no sign-flip → the directional claim did not survive to hardware.
- info_value(γ_lo) ≥ 0 → the bit does no work even where the effect is largest → the QET information channel is not demonstrated.

## Validation before this freeze (all $0)
- Core QET circuit reproduces the exact γ=0 extract: circuit −0.114 vs sim −0.1147.
- GAD circuit == sim.gad_kraus channel to 4 decimals across γ∈{0.2,0.5,0.8}, p∈{0.05,0.40}.
- Ideal sign-flip: γ0.2 −0.063 (sim −0.056), γ0.5 +0.195 (sim +0.197).
- Representative ibm_fez noise (0.4% 2q, 0.7% readout) + full θ range + readout mitigation: two independent dry-runs
  CONFIRMED — γ0.2 direction −0.072/−0.097 (NEG), γ0.5 +0.178/+0.194 (POS), info_value(low) −0.13. Sign-flip robust.
- Feasibility: transpiled 7 2q-gates, depth 19 (shallow; base QET hardware-certified, exp119). Depth/routing are non-issues.

## Attack-preflight (C5027 standing rule; engineering/physics, no advantage claim)
Fired via `tools/attack_preflight.py --claim`. Expected: all advantage classes DO NOT APPLY (no quantum-vs-classical
advantage, no classical baseline to under-price, no ratio). billing-currency PINNED: one estimator (local energy
`<obs_rot>`, readout-mitigated) for every arm, one shot budget, θ* frozen. index-space-underdetermined: the arms are
NAMED (cf/co/severed), no permutable container; direction is fixed arithmetic on two named extracts.

## What a GO authorizes (single-use)
One submission of EXACTLY `counterflow_flight_c_whisper_c5082.py` (digest recorded at submit), to the free open-instance,
ibm_fez, once. Any re-fly needs a fresh GO citing the new digest. Result filename carries the job_id.
