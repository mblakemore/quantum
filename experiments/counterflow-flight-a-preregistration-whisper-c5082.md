# Counterflow Flight A — the ladder / crossing witness: PRE-REGISTRATION (FROZEN)

**Whisper · C5082 · 2026-08-25 · board #195 (closes #143 en route)**
**Status: FROZEN pending Creator GO. Nothing submits until a GO cites this file's digest.**
**Classical arm:** `counterflow_sim_a_whisper_c5080.py` (validated; eps=N/(N+1) exact N=2..6).
**Frame:** LABELED ENGINEERING ARTIFACT (Exp139b precedent) — a working counterflow heat exchanger
on qubits. NOT a quantum-advantage claim: the crossing is a classically-expected heat-exchanger
effect realized on quantum carriers. Graded by whether it SURVIVES on hardware against two controls,
not by beating a classical baseline.

## The claim, one sentence
An N=3 counterflow ladder (partial-SWAP contacts, mid-circuit-measurement reset for advection),
run on IBM hardware with hot stream prepared at excited-population p_hot=0.40 and cold at p_cold=0.05,
produces a **temperature crossing** — the cold stream EXITS with higher excited population than the
hot stream exits — that the co-flow control (identical contacts, co-current pairing) does NOT, and
the counterflow effectiveness exceeds the co-flow cap eps=1/2.

## Observable (billing currency FROZEN: excited-state population p1, same estimator all arms)
- `p1(q)` = P(measure 1) on the exit qubit, readout-error-mitigated with the SAME per-qubit
  calibration (cal0/cal1 rows) applied identically to every arm.
- **crossing** = p1(cold_exit) − p1(hot_exit)   [population units; a POSITIVE crossing = cold exits hotter]
- **eps_cf** = (p1(cold_exit) − p_cold) / (p_hot − p_cold)   [effectiveness; co-flow caps at 0.5]

## Arms (all in one job, same layout, same shots)
1. **COUNTERFLOW** — the ladder: hot flows stage 0→N-1, cold flows N-1→0, partner at each contact is
   the counter-propagating parcel; MCM-reset re-prepares a fresh inlet parcel each advection.
2. **CO-FLOW control** — identical contacts and identical count, but PAIRING ORDER co-current (both
   streams paired same-direction). This is the ONLY difference from arm 1 (the confound-free control:
   same gates, same depth, same qubits — only which parcels meet differs). Co-flow eps ≤ 0.5 by construction.
3. **EQUAL-STREAM NULL** — both streams prepared at the SAME population (the mean, ~0.225). Any
   nonzero crossing here is a readout/layout artifact, not physics. Bounds the instrument's own bias.

## Parameters (frozen)
- N = 3 stages (6 data qubits, 3 stage-pairs). τ = 0.5 per contact (partial-SWAP fraction; θ=π/4).
- p_hot = 0.40, p_cold = 0.05 (prepared by Ry rotations; the sim's ideal parameters).
- Contact = excitation-conserving partial-SWAP (~2 CZ + 1Q gates), MCM reset for advection.
- Shots = 10,000 per arm (matches the sim's noise sweep). Exit read after the ladder reaches its
  frozen tick count (transients converge in ≤24 ticks per the sim; the circuit runs the settled depth).
- Backend: PINNED by name to ibm_fez (a FREE open-instance device), via the #151 spend gate. Pinned rather than "least-busy" so no scan-order selection enters the pipeline (index-space preflight).

## Pre-registered PREDICTIONS (frozen before any hardware data)
- **P1 (the crossing):** COUNTERFLOW crossing > 0, resolved (≥ 5σ on the shot budget). Sim ideal at
  these params gives crossing ≈ +0.175; hardware noise sweep held it at 0.16–0.17 (worst z=101.5),
  so ≥ 5σ is conservative.
- **P2 (counterflow beats co-flow):** crossing_counterflow > crossing_coflow, and eps_cf > 0.5 while
  eps_coflow ≤ 0.5 (within its CI). The two arms differ ONLY in pairing order.
- **P3 (null arm clean):** |crossing_null| ≤ 0.02 (the sim's equal-stream arm gave ≤ 0.004; 0.02 is a
  loose hardware-readout allowance). A null-arm crossing above this VOIDS the result — the instrument
  is confounded and P1/P2 are not believable.
- **#143 thermal head (en route):** the MCM-reset idle segments carry an idle-heating measurement;
  reset baths vs idle populations recorded as the #143 deliverable. (Descriptive, not gated.)

## Pre-registered FALSIFIERS (any one fires → the claim FAILS, recorded as an honest negative)
- crossing_counterflow ≤ 0 (no crossing) → the ladder does not exchange as designed on hardware.
- crossing_counterflow ≤ crossing_coflow → pairing order is not the operative variable → the sim's
  counterflow advantage did not survive to hardware.
- eps_cf ≤ 0.5 → no super-co-flow effectiveness → the crossing witness is not demonstrated.
- |crossing_null| > 0.02 → readout/layout confound → result VOID (not a negative, an instrument failure).

## Attack-preflight (C5027 standing rule — run even though this is engineering, not an advantage claim)
The 6 registry attack classes are fired at the claim via `tools/attack_preflight.py --claim`. Expected
disposition (stated in advance, to be confirmed by the run): the advantage classes
(planted-structure-leak, idealized-hard-delivered-easy, under-priced-baseline, ceiling-quoted-as-
advantage) DO NOT APPLY — there is no quantum-vs-classical advantage claimed and no classical baseline
to under-price; the effect IS classical and the artifact is labeled engineering. billing-currency is
PINNED (population p1, one estimator all arms). index-space-underdetermined: the three arms are the
complete partition (counterflow / co-flow / null), no permutable container. A passing preflight is a
FLOOR, not a certificate.

## Budget
~10 QPU-seconds estimated (3 arms × a shallow ladder × 10k shots; the account has ~736 free QPU-s).
Single free device, single calibration window. No paid instance (spend gate refuses them).

## What a GO authorizes (single-use)
Submission of EXACTLY the flight script built to this prereg (its digest recorded at submit), to the
free open-instance, once. Any re-fly needs a fresh GO citing the new object's digest. The flight
script is dry-run classically against `counterflow_sim_a` before submit; the sim's ideal numbers are
the expected values, and a hardware result inside the noise-sweep band (crossing 0.16–0.17) confirms.

---
## AMENDMENT 1 (C5082, during the circuit build — MATERIAL, re-freeze digest)
The flight circuit build surfaced a real mechanism the naive spec missed, validated by $0 Aer dry-run:
- **The classical (sim-A) crossing REQUIRES inter-contact DEPHASING.** Parcels prepared with coherent
  gates (Ry) and contacted by a coherent partial-SWAP accumulate coherence across contacts and drive
  the ladder to eps->1 (this is sim D's COHERENT result, independently reproduced on the circuit —
  eps=0.97). To realize sim A's CLASSICAL eps=0.75, each parcel is DEPHASED in the Z basis between
  contacts (a mid-circuit measurement whose outcome is discarded). WITH dephasing: eps=0.745,
  crossing=+0.172 — matches sim A to the third decimal. This is the circuit that flies.
- **Depth is feasible.** The dephased ladder converges at T=2 ticks (no coherent transient): 28
  two-qubit gates for N=3. Noisy Aer (0.7% two-qubit depolarizing, marrakesh-class): crossing +0.171
  (ideal +0.174) — the classical crossing is ROBUST to depolarizing (unlike a coherent signal).
- **Arms re-confirmed on the validated circuit:** counterflow crossing +0.17 (eps 0.75); co-flow
  eps=0.50, crossing ~0; equal-stream null ~0.
- Parameters otherwise unchanged. The claim is unchanged (classical crossing witness). The dephasing
  is the MECHANISM that makes the artifact classical; it is now part of the frozen circuit.

---
## AMENDMENT 2 (C5082, after the first fly VOIDed — re-freeze, re-fly on a FRESH GO)
First fly (job da6gir60ukec73821t1g, ibm_fez): counterflow crossing +0.1805 (eps 0.770) — the crossing
APPEARED — but VOID by falsifier P3: the equal-stream null arm read -0.049 (> |0.02|), an uncorrected
READOUT asymmetry on the hot-exit qubit. Root cause: this prereg specified per-qubit readout mitigation
and the FIRST flight script omitted it (measured raw counts).
FIX: the flight script now runs two calibration circuits (all-|0>, all-|1>) on the exit qubits IN THE
SAME JOB and corrects each arm's populations by the measured per-qubit r0/r1. Re-validated on Aer WITH
an asymmetric readout-error model (0.03/0.06) that reproduces the first fly's confound: mitigated result
counterflow +0.175, co-flow +0.001 (eps 0.49), null -0.005 (CLEAN), verdict CONFIRMED, all 5 checks pass.
The claim, parameters, and falsifiers are UNCHANGED; only the readout mitigation (already specified) is now
implemented. A re-fly requires a FRESH Creator GO citing this amended prereg's digest.

---
## AMENDMENT 3 (C5082, THIRD fly — matched qubits via noise-aware layout, on the Creator's directive)
Fly 2 VOIDed on a STRUCTURAL null-arm bias (-0.074): the two exit qubits landed on mismatched-error
hardware because flights 1-2 transpiled at optimization_level=1 (NOT noise-aware). The A/B role-swap
symmetrization was built and a $0 dry-run PROVED it does not cancel a role-dependent bias (recorded).
The fix that attacks the CAUSE: transpile at optimization_level=3 (noise-aware SabreLayout), placing all
six qubits — both exits included — on low-error matched hardware (ibm_fez best qubits: readout ~0.004-0.005,
matched pairs available e.g. q142/q143 diff 0.0004). Readout mitigation retained. Script:
counterflow_flight_a_v3_whisper_c5082.py; reports the exit physical qubits at submit. Claim/params/
falsifiers UNCHANGED. Null-cleanliness is a HARDWARE question this fly answers. Fresh GO: Creator
"pick matched qubits and fly the third".
