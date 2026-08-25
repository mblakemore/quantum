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

---
## AMENDMENT 4 (C5082, WEATHER-AWARE — applying our own qpu_weather work, on the Creator's prompt)
Flights 1-3 ignored the quantum-weather discipline (F81/F84: published calibration can be flat across a
3x live quality swing; window drift). Corrections for the 4th fly (v4 script):
- EXITS PLACED IN THE QUIET LINE. `qpu_weather.py --scan` on ibm_fez gave quiet line [136,143,142,141].
  v3's opt_level=3 had put an exit on q123 (ro 0.0088, OUTSIDE the quiet line). v4 pins initial_layout to
  the quiet neighborhood {123,136,143,142,141,144}; exits transpile to q142 (ro 0.0044) + q144 (ro 0.0070),
  mismatch 0.0026 (was worse). Readout mitigation retained.
- WINDOW GATE. A `qpu_weather.py --nowcast` sentinel (mirror ladder, live fidelity vs published forecast)
  is flown FIRST; v4 flies only on a GO verdict for the current window — do not fly deep work in a bad
  window (the plausible cause of the null-bias drift -0.049 -> -0.074 across flights 1-2).
Claim/params/falsifiers UNCHANGED. This is the honest instrument: weather-checked window + quiet matched
exits + readout mitigation. Fresh GO: Creator "build v4 ... run it right".

---
## PROVENANCE CONVENTION (C5082, Dawn #15942 — a NOTE, not a claim/param/falsifier change)
Not a change to the claim, parameters, or falsifiers; a build directive for the NEXT flight script
(the symmetric-exit redesign) and any re-fly. Recorded here rather than left on the bus because a
resolution in a bus post is worth nothing (Ember #15921) — the artifact the next flight is built
against is where it has to live.

FLOWN SCRIPTS ARE NOT EDITED. counterflow_flight_a{,_v3,_v4}_whisper_c5082.py auto-write the GENERIC
`results/counterflow_flight_a_{tag}_c5082.json`, so each hardware fly OVERWROTE the last — fly1 and
fly2 both wrote `_hw_c5082.json`; fly2's raw file now survives only at quantum@1c15874, and the v4
`_v4_hw_` file is a MANUAL copy I made post-run. That manual copy is the fragility: preservation that
depends on remembering to rename is the same silent-substitution class we spent 2026-08-25 on (the new
file is plausible, the old one is gone, nothing announces it). Editing the flown scripts to fix it
would change their digests and break the "this exact digest flew" provenance — so they stay as-is;
their result files live safely in git history and are cited by job-id.

THE CONVENTION (next script onward): the result filename INCLUDES the job_id for hardware runs —
`results/counterflow_flight_a_{tag}_{job_id}_c5082.json` (dry-runs may keep the generic name; they
carry no provenance). A job_id is unique per flight, so no rerun can silently replace a prior flight's
record, and the per-flight file exists without a manual copy. The generic name, if kept at all, is
written as an ADDITIONAL "latest" pointer, never as the sole record.

---
## AMENDMENT 5 (C5082, SYMMETRIC-EXIT redesign — the clean-null instrument, Creator GO "go ahead with the symmetric-exit redesign and fly it")
Flights 1-4 VOIDed on the null arm; the bias survived readout mitigation (v2) AND noise-aware matched-qubit
placement (v4). It FLIPPED SIGN with layout (−0.074 → +0.077) = a QUBIT-FIXED bias tied to which physical
qubit reads which exit. This amendment fixes the INSTRUMENT, not the claim/params/falsifiers (all UNCHANGED).

WHY THE FULL-RELAYOUT A/B DOES NOT FIX IT ($0-proven): counterflow_flight_a_sym mirrors the WHOLE chain in
layout B, landing the cold-stream ry re-prep on a gate-noisy qubit — null_A=+0.001 (clean), null_B=+0.151
(biased), average VOID. Averaging a clean arm with a biased one is not symmetrization.

THE FIX — terminal exit-swap averaging on ONE layout (counterflow_flight_a_symexit_whisper_c5082.py).
Two versions per arm, IDENTICAL physics/qubits/error-profile, differing ONLY by a single terminal
SWAP(C0,H2) before the exit measurement. DIRECT measures cold on its home qubit, hot on the other;
SWAPPED measures cold on the OTHER qubit, hot on the home one. Average cancels the per-read-qubit bias
d{C0,H2} exactly; in the NULL arm both parcels are identical, so any qubit-fixed confound is ANTISYMMETRIC
under the swap and cancels. Readout mitigation retained, corrected to the per-version qubit→bit mapping
(a mapping bug caught and fixed in the $0 dry-run — the swapped bits come from the opposite physical qubits).

$0 VALIDATION (before any hardware):
- Three injected QUBIT-FIXED confound models, all give a CLEAN null via the direct/swapped antisymmetry:
  M1 readout asym → null −0.0035 CONFIRMED; M2 amp-damping (path-accumulated) → null +0.0056 CONFIRMED
  (direct −0.017 / swapped +0.028, the cancellation visible); M3 combined-adversarial (both exits
  mismatched on every axis, 2-3× harsher than real fez) → null −0.0005 (P3 clean; its only failing check
  is co-flow eps 0.557 vs 0.55 cap under the deliberately extreme noise — not a null failure).
- GOLD-STANDARD from_backend (REAL ibm_fez noise snapshot + REAL routing, since 2 of 3 contacts are
  non-adjacent on heavy-hex and MUST route): VERDICT CONFIRMED, null +0.0039, crossing +0.163 (eps 0.783),
  co-flow −0.0015 (eps 0.513). vs v4 single-measurement null +0.077 — a ~20× reduction into the clean band.
Exit pair C0=q142/H2=q143 confirmed ADJACENT, so the terminal swap is native; direct and swapped
transpile to identical depth (82) and 2q-gate count (27), so the bulk routing is shared and the
cancellation survives transpilation.

WHAT THE GO AUTHORIZES: one submission of counterflow_flight_a_symexit_whisper_c5082.py (digest recorded
at submit) to the free open-instance, ibm_fez, once. Result filename carries the job_id (PROVENANCE
CONVENTION above). Claim, parameters, and falsifiers UNCHANGED — null-cleanliness remains the hardware
question, now with an instrument $0-shown to answer it.

---
## AMENDMENT 6 (C5082, POPULATION-SWAP — the transpile-proof clean-null instrument; $0-validated, awaiting fresh GO)
v5 (Amendment 5, terminal exit-swap) VOIDed on hardware (null +0.067): the transpiler VIRTUALIZED the
pre-measurement SWAP into a classical bit-relabel, so both versions read the SAME physical qubits
(clbit0<-q142, clbit1<-q144) and NO exchange/cancellation happened. Its M1/M2/M3 dry-runs passed only
because they ran the LOGICAL circuit where the swap is a real gate. Lesson: a physical-gate-structure fix
must be validated on the TRANSPILED circuit; a pre-measure SWAP is exactly what a transpiler removes.

FIX — population-swap. Two versions per arm force the exit exchange through the STATE PREPARATION (ry
angles) + classical BIT WIRING, neither virtualizable:
  A: hot-pop on H-chain (exit H2), cold-pop on C-chain (exit C0) -> bit0<-C0(cold), bit1<-H2(hot)
  B: cold-pop on H-chain (exit H2), hot-pop on C-chain (exit C0) -> bit0<-H2(cold), bit1<-C0(hot)
  average -> cold - hot; per-exit-qubit bias cancels. Readout mitigation per-version.

$0 VALIDATION ON THE TRANSPILED CIRCUIT (counterflow_flight_a_popswap_validate, quantum@7bc91b8) — the
check v5 skipped:
- PRECONDITION VERIFIED transpile-proof: ver A reads bit0<-phys q142, ver B reads bit0<-phys q144
  (DIFFERENT physical qubits into the cold bit — the exchange v5 failed to achieve).
- A/B average cleans localized PHYSICAL confounds on the transpiled circuit: q142 A-only null +0.051 ->
  avg -0.006; q144 A-only -0.054 -> avg +0.001. Robust to WHICH exit qubit is bad = weather-robustness.
- from_backend (real ibm_fez noise + routing): null +0.004, crossing +0.169, co-flow eps 0.542, CONFIRMED.
Flight script counterflow_flight_a_popswap_whisper_c5082.py --dry-run (from_backend): CONFIRMED, null
+0.0006, crossing +0.167. Claim/params/falsifiers UNCHANGED. Residual risk: under EXTREME single-qubit
damping the co-flow eps can exceed the 0.55 cap (a FALSIFIED honest-negative, not a VOID; realistic noise
keeps it at 0.53). A fresh Creator GO is required — the v5 GO was consumed by the VOIDed v5 flight.
