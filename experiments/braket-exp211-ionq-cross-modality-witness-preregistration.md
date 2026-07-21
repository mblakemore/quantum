# Exp211 (Braket) — Cross-MODALITY causal-order witness on IonQ Forte-1 (trapped ion)

**Pre-registration — frozen before submission. Substrate: claude-opus-4-8. Whisper, C4941.**

## Question
Is indefinite causal order a property of superconducting hardware, or of quantum mechanics itself?
Exp210 certified it cross-*vendor* (Rigetti, still superconducting). This is the deeper test:
**IonQ Forte-1 stores each qubit in a single trapped atom** — all-to-all connectivity, native
gates GPI/GPI2/MS (Mølmer–Sørensen), and **none of the CZ Z-bias** the whole campaign noise story
rests on. If the causal witness fires there against the same theory bound, indefinite causal order
is not a superconducting artifact at all — it spans the deepest hardware divide.

## Scope (honest, budget-driven) — WITNESS ONLY, not the full PASS-CAUSAL card
IonQ costs $0.08/shot; the full frozen axis (68 pubs, 112k shots) would be ~$9k. Under the $200
ceiling this flies the **witness W only** (the 4 `w_` pubs), NOT the capacity (Rbar) or null (D)
arms. So the claim is narrower than Exp210's: **"the causal witness fires on trapped ions"**
(W crosses the causal-mixture bound 0 at ≥5σ), not the three-number PASS-CAUSAL certification.
The null-integrity check that rules out a spurious offset is **not run** — the comm/anti arm
structure is the in-flight control. Stated plainly so the result is not over-read.

## Frozen instrument
- Circuits: `tools/switch_bench.py::build_causal()` witness pubs VERBATIM — 4 pubs
  (`w_{start,end}_{c,a}`), the exact circuits flown on every Heron die and on Rigetti (Exp210).
- Grader: `scripts/braket_switch_causal.py::grade_witness` — W = mean(⟨X_c⟩_comm − ⟨X_c⟩_anti),
  seW = √(2·2/(2·shots)). **Bound is the theory constant 0** (causal mixture). PASS rule:
  **W − 5·seW > 0** — identical to the frozen bench's causal-pass rule.
- Shots: **500/pub** (not the bench's 4000). This is a cost choice: fewer shots WIDEN seW
  (0.063 vs 0.022), making the 5σ bar *harder*; it does **not** retune the bound. Trapped-ion
  fidelity clears it with large margin even so (local-sim: W 2.0000, 31.6σ over 0, FIRED).
- Submission: `backend.run(native=True)` — compiles the abstract circuit to IonQ's Target-native
  (GPI/GPI2/MS) + verbatim box, the same path that worked on Rigetti (Exp210). Counts read via
  qiskit `get_counts()` (bit convention preserved).
- Local-sim validation: witness-only build + grader reproduce ideal **W=2.0000 → WITNESS-FIRED**.

## Device & cost
IonQ Forte-1 (`arn:aws:braket:us-east-1::device/qpu/ionq/Forte-1`), trapped ion, us-east-1.
- **Smoke** (1 circuit × 100 shots): 1×$0.30 + 100×$0.08 = **$8.30** — port/format check on IonQ.
- **Witness** (4 circuits × 500 shots): 4×$0.30 + 2000×$0.08 = **$161.20**.
- **Total ≈ $169.50** < $200 ceiling (us-east-1). Canary-first: no witness flight until the smoke passes.

## Pre-filed prediction (honest, before the number)
- **Predict WITNESS-FIRED, confidence ~0.85.** The bar is low (W>0) and trapped-ion 2-qubit
  fidelity (~99%+) is high, so the shallow witness circuit should run near-ideal.
- **W will likely land HIGH — ~1.7–2.0** — comparable to or *better than* Heron's ~1.90, and far
  above Rigetti's degraded 1.11 (ions have no routing overhead on this 2-qubit circuit and higher
  gate fidelity). If so, the cross-modality point is not just "it fires" but "it fires *cleanly*."
- **Named failure mode**: if the native GPI/GPI2/MS compilation or the verbatim box mangles the
  switch's control structure, W could come back near 0 (WITNESS-FAIL) — which would be a port bug
  to diagnose, not evidence against the physics. The smoke check guards the port before the spend.
- No band-shopping: whatever W/seW come back, graded against W−5seW>0 as-is; a FAIL is kept.

## What each outcome means
- **FIRED** → indefinite causal order fires on a trapped-ion machine — different modality, different
  gates, no CZ Z-bias. The strongest device-independence statement the campaign can make short of
  the full multi-axis card: it is not a superconducting artifact. Three substrates now (IBM Heron,
  Rigetti SC, IonQ ion).
- **FAIL / near-0** → either a real modality dependence (surprising, publishable) or a port defect
  (the smoke check makes the latter unlikely). Either way kept in the record.
