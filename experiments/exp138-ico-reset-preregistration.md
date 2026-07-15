# Exp138 — ICO heralded sub-bath reset (PRE-REGISTRATION, FROZEN)

**Author**: Whisper (DC15W), C4720 (2026-07-15), Creator-directed ("run actual QPU jobs to do
something with the temp difference").
**Status**: FROZEN before submission. Grade rule below cannot change after data.
**Apparatus**: the Exp108 ICO fridge (Felce–Vedral SWAP-dilated thermalizing channels, g=0.75 →
bath p₁ = 1−g = 0.25) + one data qubit + one SWAP. Circuit: `experiments/exp138_ico_reset.py`.

## 1. One-line claim
The **cold + branch** of the switch refrigerator can be **spent** — SWAP-delivered onto an
external data qubit D that was never part of the fridge — leaving D **colder than any
definite-order process on the same warm baths can make it**, heralded on control = +.

## 2. What is new vs the existing ledger (verified, not recalled)
- F86/F88 **measured** the split (+ branch colder than the baths, colder than the coldest
  reservoir) — **in place, on the fridge's own working fluid**.
- F95 **extracted work**, but from the **hot / population-inverted (−) branch** (charged a battery).
- The **cold (+) branch has only ever been read, never spent** (confirmed by re-reading
  F95/F104/F105: the engine uses the − branch; C4519 memory — episodic recall ≈ 0%, so this was
  checked, not remembered).
- **Exp138 spends it**: delivery of the cold onto an **external computational qubit** + a **fresh
  data-qubit null**. Modest, clean extension.

## 3. HONEST SCOPE (frozen — do not oversell)
This is a **resource-theory** demonstration: *sub-bath cooling of an arbitrary target using warm
baths + the switch only.* The absolute number (~0.19–0.21) is **NOT** competitive with the chip's
native measurement-reset (~0.01–0.02); the floor beaten is the **definite-order reset (0.25)**, not
native reset. The transfer SWAP is trivial by itself (it moves a state); the **result** is the
Nσ beat over the definite-order null on a fresh qubit. Heralded (keep control = + runs,
P ≈ 0.72); the herald measurement is the cost, tying to the F104 demon ledger.

## 4. Circuit (5 qubits, 2 clbits) — same skeleton class as Exp108 (F86 winner)
- q0 = control (X readout, clbit0 = herald), q1 = t (working fluid, traced after transfer),
  q2 = a1, q3 = a2 (bath ancillas, pooled to τ), q4 = D (data qubit, Z readout, clbit1).
- `reset` arm: CC3 (two Fredkins) + C3 = Exp108 switch on (t,a1,a2); **then `swap(t,D)`**; H on
  control; measure control(X) + D(Z).
- `null_fwd` / `null_rev`: definite order C3 / C3⁻¹ on (t,a1,a2); **then `swap(t,D)`**; measure.
- Pooling over the 8 fridge basis labels (t0,a10,a20), weights w(t0)w(a10)w(a20), w(0)=g — the
  exact channel+input mixture (Exp108 logic, unchanged). D-init = |1> FIXED (not pooled); the
  measured D population is **D-init-independent** (SWAP overwrites) — the sim asserts this
  (`d_init_invariance`, |Δ| < 1e-3).
- Payload depth: **23 CZ** (FakeMarrakesh), Exp108-class (22 CZ). Live transpile re-audit aborts
  on skeleton drift from the frozen seed (4720), same discipline as Exp108.

## 5. Theory targets (g = 0.75, input τ; derived via `exp108.exact_targets`)
- reset `p1_D|+` (heralded) = **0.184783** (cold); `p1_D|−` = 0.416667 (hot); P(+) = 0.71875.
- null (both definite orders): `p1_D` = **0.25 exactly** (causal value; SWAP just relocates τ).

## 6. FROZEN grade rule
Let reset `p1₊ ± se₊` = heralded + branch on D; `n_f, n_r` = the two definite-order nulls (p₁ ± se).

- **INTEGRITY gates (any fail ⇒ NO-TEST, not LOSS):**
  1. Null band: `|n_x − 0.25| + 5·se_x < 0.05` for **both** x ∈ {fwd, rev}.
  2. Retention sentinel (fridge all-|0>, D=|1>): `P(c=+, D=0) ≥ 0.90` (transfer integrity: a |1>
     D is reset to |0>).
  3. Deco-null sentinel (fridge t=1): `P(c=+) ∈ [0.40, 0.60]` (no faked interference).
  4. Live skeleton within the frozen 2q-class bound (abort on drift).
- **PRIMARY (WIN condition):** beats the definite-order reset on the same chip, depth-conservative:
  `min(n_f, n_r) − p1₊ − 5·√(se₊² + se_null²) > 0.02`.
- **SECONDARY (F95-style, may be an honest LOSS):** absolute sub-bath certification:
  `p1₊ + 5·se₊ < 0.25`. Reported as WIN/LOSS on its own; the finding is the primary result plus
  whether the absolute leg cleared.

**Result label**: WIN if INTEGRITY pass **and** PRIMARY pass. SECONDARY reported separately.
No auto-resubmit; one SamplerV2 job; pre-registered pub-order shuffle seed.

## 7. Feasibility preview (FREE, informational — not the grade)
- Noiseless (AerSimulator): `p1_D|+` = 0.1876±0.0008, null 0.2500, beat 0.0624 — all gates PASS.
- FakeMarrakesh (noise model, optimistic at depth per F81): `p1_D|+` = 0.1917±0.0031, null
  0.2502, beat 0.0585, retention 0.9725, deco 0.5035 — all gates PASS. Sub-bath margin ~0.043.
- Risk: the extra SWAP's depth pulls `p1_D|+` up on hardware (F86 in-place was 0.2098); the
  PRIMARY beat is depth-conservative (deeper reset arm vs shallow null) and expected robust; the
  SECONDARY absolute sub-bath is the tighter leg and is the honest LOSS candidate.

## 8. Submission hygiene (inherited from Exp108)
Calibration-gated qubit pick (min 2q-error + readout; a 5-qubit chain c-t-a1-a2-D), pre-registered
shuffle seed, live transpile re-audit vs frozen 2q bound (abort on drift), ONE SamplerV2 job,
never auto-resubmit, cost stated up front. Backend ibm_marrakesh (Heron r2).

## 9. Provenance
Extends F86 (`results/exp108_grade.json`) and the F88 native-fluid retest; theory via
`exp108_ico_refrigeration.exact_targets` (self-validates against Exp106 g=½). Resource:
Felce–Vedral PRL 125 070603. Family: Wing I, The Causal Switch — first **use** of the cold branch.
