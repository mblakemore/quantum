# Exp212 (Braket) — PLAN: a structurally-matched, entangled definite-order null to close the IonQ loophole

**PLAN (not yet a frozen pre-registration). Substrate: claude-opus-4-8. Whisper, C4942.**
Follows the Exp211b failure + Exp211c calibration: the IonQ cross-modality certification was **withdrawn**
because the definite-order null failed (W_def=1.96) and the calibration ruled out a bit-order artifact.
Diagnosis: the bench's `definite=True` control has **zero entangling gates** (h:2, unitary:2) vs the
witness's 4 CZ, so it compiled anomalously on IonQ's all-to-all native path. This plan fixes that.

## 1. Goal & the "aha"
Build a definite-order control that is **structurally identical to the witness** — same 4 CZ, same depth,
differing *only* in the control-qubit preparation (|+⟩ → a classical mixture of |0⟩ and |1⟩). Because the
gate structure is identical, it compiles the same way on IonQ as the witness, removing the confound that
sank Exp211b. A causally-separable (classical-mixture) process **must** give W ≤ 0; if the matched null
gives W ≈ 0 while the witness gives W ≈ 1.9 **on the same platform, same window**, the loophole is closed
and the cross-modality certification can be restored. If it does not, the IonQ claim stays withdrawn.

**aha**: "the control that failed wasn't wrong physics — it was a different-shaped circuit. Match the shape
(keep the entanglement, only change the control's coin from quantum to classical) and the test is fair."

## 2. The design (grounded in `exp106_capacity_activation.build_circuit`)
The switch (definite=False): `h(0)` [control→|+⟩] · 4 controlled-unitaries (a,b,b,a → 4 CZ) · `h(0)` · measure.
q0 = control (X-basis, clbit0), q1 = target (Z-basis, clbit1).

**Matched definite-order control = classical mixture of two definite orders, full structure kept:**
- **Circuit D0**: the switch circuit with the *initial* `h(0)` **removed** (control prepared |0⟩) — one fixed order.
- **Circuit D1**: the switch circuit with the initial `h(0)` **replaced by `x(0)`** (control |1⟩) — the other fixed order.
- Everything else identical to the witness (the 4 controlled-unitaries stay → 4 CZ each). Read W on the
  50/50 classical mixture of D0 and D1 (average the counts). A classical mixture of definite orders is
  causally separable → **W_matched ≤ 0** by theorem.
- Build D0/D1 **manually** from the witness circuit (do NOT use `definite=True`, which simplifies away the CZ).

## 3. Validation plan (local-sim, FREE, before any spend)
1. Assert **D0 and D1 each have the SAME 2q/CZ count and depth as the witness** (the whole point).
2. Assert **W_matched (mixture of D0,D1) ≈ 0** on the local simulator (the abstract control is causally separable).
3. Assert the witness still gives **W ≈ 2** (unchanged). Separation ≈ 2 on sim.

## 4. Port check — use the ASYMMETRIC entangled calibration (the Exp211b lesson)
The Exp211b smoke used swap-invariant `'00'/'11'` states and was **blind** to bit-order permutation. The
port/convention check for Exp212 MUST use the **asymmetric, entangled** calibration already built
(`ionq_bitorder_cal.py`: X·X·CX → |q0=1,q1=0⟩, returns `'01'` if convention preserved). Fly it (or reuse
the C4942 result: IonQ returned `'01'`, convention preserved) as the first gate; only proceed if it confirms
the entangled-circuit bit convention.

## 5. Gap review (v1)
| # | gap / risk | fix |
|---|---|---|
| G1 | **D0/D1 not actually structure-matched** (the whole point) | §3.1 asserts identical CZ-count + depth vs witness before flight; abort if they differ. |
| G2 | **A single definite order (D0 alone) may not be ≤0** | Use the **classical mixture** of D0 *and* D1 — provably causally separable; do not rely on one order. |
| G3 | **Same anomalous compilation could still hit** | Because D0/D1 are gate-identical to the witness (only 1 single-qubit prep differs), they get the witness's compilation; verify 2q count in the *transpiled* IonQ circuit (free scan), not just the abstract. |
| G4 | **Same-instrument-not-same-instant** (witness flown earlier) | Re-fly the **witness AND the matched null in the SAME session/window** so the comparison is same-window; do not reuse the old W=1.894. |
| G5 | **Port-check blind spot recurs** | Mandatory asymmetric-entangled calibration gate (§4); never a swap-invariant smoke again. |
| G6 | **Budget** | See §7 — needs a cap bump; current IonQ spend ~$211 of $220. |
| G7 | **Reading rule not pre-committed** | §8 freezes it before the number. |

## 6. Pre-dev structure (standard form)
1. **Builder**: a `--matched-null` mode in `scripts/braket_switch_causal.py` that constructs D0/D1 by copying
   the witness circuit and swapping the initial control prep (remove h(0) / replace with x(0)); + a
   `grade_matched` that averages D0/D1 counts and computes W_matched with seW from actual shots.
2. **Asserts** (sim, in-code): CZ(D0)==CZ(D1)==CZ(witness); W_matched(sim)∈[-0.1,0.1]; W_witness(sim)≈2.
3. **Free scan**: transpile D0/D1/witness for IonQ (`native=True` dry path) → confirm identical 2q counts.
4. **Flight order** (all one window): (i) asymmetric calibration gate → convention OK; (ii) witness (4 pubs);
   (iii) matched null (D0,D1). Task handles persisted before `.result()`; background submit; no short timeout.
5. **Grade**: witness W vs bound 0 (fires); matched-null W_matched vs bound 0 (must be ≤ ~0.3 in-band);
   separation (W_witness − W_matched) in σ. Update the white paper per the outcome.

## 7. Cost & the budget decision
IonQ Forte-1, $0.30/task + $0.08/shot, **min 100 shots**.
- **Minimal** (matched null only, reuse C4942 calibration + old witness): D0+D1 × 100 shots = 2×$0.30 + 200×$0.08 = **$16.60**.
- **Clean same-window** (witness 4 + D0 + D1, 100 shots; calibration already have): 6×$0.30 + 600×$0.08 = **$49.80**.
- **Recommended: the clean same-window ($49.80)** — G4 (same-instant) matters for a claim that was just
  withdrawn; a reused-witness minimal version would carry a same-window caveat.
- **Budget**: ~$211 spent of $220 → **only ~$9 left**. Even the minimal $16.60 needs a bump. The clean
  $49.80 needs the cap raised to ~$265. **This is a Creator decision; nothing flies until the cap is set.**

## 8. Reading rule — pre-committed (to be frozen at submission)
- **W_matched ≤ 0.3 AND W_witness − W_matched > 1.0** → **LOOPHOLE CLOSED**: restore the IonQ cross-modality
  certification (witness + validated matched null, same window). Update the paper: withdrawal → certified.
- **W_matched > 0.3** (matched null does NOT collapse) → the witness genuinely does not discriminate ICO on
  IonQ; **cross-modality claim stays permanently withdrawn**, and this is recorded as a hardware finding.
- Either outcome kept in the record with full weight; no band-shopping, no shot/band changes post-hoc.

## 9. Acceptance
Matched null structurally identical to the witness (verified CZ-count + transpiled 2q), sim shows W_matched≈0,
asymmetric calibration confirms convention, flight in one window, reading rule applied as frozen, white paper
updated to the honest outcome (restore or permanent-withdraw).
