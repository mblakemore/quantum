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

---

## 10. Gap review v2 (C4943, fresh-eyes pass — substrate claude-fable-5)

### 10.1 FINDING: the Exp211b failure diagnoses itself in the ungraded target bit ($0 re-analysis)
The C4942 diagnosis ("zero-entangling-gate null compiled anomalously") was reached without grading the
**target bit** of the recorded counts. Doing so now:

| pub | theory ('tc') | measured | note |
|---|---|---|---|
| `wnull_c` (X,X) | `'00'` | `'00'` 99/100 | permutation-INVARIANT (blind) |
| `wnull_a` (X,Z) | **`'10'`** (target MUST read 1: Z·X\|0⟩=−\|1⟩) | **`'01'`** 99/100 | exactly `'10'` with the two bits **swapped** |

A single bit-order permutation maps perfect execution onto the recorded data in both arms, and reproduces
W_def = +1.96 to the digit (deterministic target `1` lands in the control slot → ⟨X_c⟩_anti = −0.98).
Two independent gross errors (control phase flip + dropped X on target) would be required otherwise. The
hardware very likely executed the null **correctly**; the *instrument's counts bookkeeping* failed.

### 10.2 Client side exonerated by exact reproduction (free, done)
The precise `run(native=True)` compile path (`_resolve_compilation_args` → `to_braket` with IonQ target +
angle restrictions) was rebuilt offline for both null pubs. The compiled GPI/GPI2 circuits, simulated on the
Braket local simulator, give the **correct** outcomes (`wnull_c`→'00', `wnull_a`→'10' in tc order, 2000/2000).
The client-side compile is faithful; "compiled anomalously" is ruled out at the client.

### 10.3 Localized artifact class: server-side bit handling of ENTANGLER-FREE programs
The C4942 calibration (X·X·CX → returned '01', "convention preserved") **contains a CX**: it certifies the
counts convention only for the *entangled* circuit class — the class the witness lives in (4 RZZ, so
W=1.894 remains a plausible genuine reading). It never tested the **gate-free class the null lives in**.
Precedent already in the repo (`ionq_bitorder_cal.py` docstring): calibration v1's idle qubit was **dropped
server-side** (1-bit result) — IonQ's ingestion demonstrably re-handles qubits when circuit structure allows.
"The calibration ruled out endianness" (C4942) over-reached its class.

**Cheap decisive test (recommended add, ~$8.30)**: a **gate-free asymmetric calibration** — `x(0)` and a
non-idle 1q dressing on q1 (e.g. X·X), NO entangler, expected 'tc'='01'. If IonQ returns '10', the
Exp211b NULL-FAIL is *proven on-device* to be a bookkeeping permutation, not physics. Either way the paper's
root-cause paragraph becomes evidence-based. **This does NOT un-withdraw anything** — the retraction
pre-commitment stands; restoration still requires the matched null of this plan.

### 10.4 Corrections to this plan
1. **Pub count / cost error (§6–7).** W = ⟨X_c⟩_comm − ⟨X_c⟩_anti requires BOTH arms per prep. The matched
   null is **4 pubs** (D0_c, D0_a, D1_c, D1_a), not "D0+D1"=2. Corrected costs: **minimal $33.20**
   (4×$0.30 + 400×$0.08); **clean same-window $66.40** (witness 4 + null 4 = 8 tasks, 800 shots);
   **+$8.30** gate-free calibration → **~$75 total; cap needs ~$290** (spent ~$211).
2. **Grade EVERY bit (the §10.1 lesson).** Pre-register exact two-bit sim predictions per pub and grade
   target AND control marginals, not just W_matched. Sim (verified this cycle): D0/D1, both preps —
   comm: t=0 deterministic, c 50/50; anti: **t=1 deterministic**, c 50/50. The deterministic, arm-asymmetric
   target bit is itself a mapping/permutation detector; a swap would also move the deterministic bit into
   the c-slot and drive |W_matched| → ~2 (decisively caught). Also require **per-prep** bands
   (|W_D0| and |W_D1| each ≤ 0.3) so an artifact cannot hide in the D0/D1 average.
3. **Reading rule missing branch (§8).** As written it has no branch for "null clean but the same-window
   witness fails to re-fire." Freeze: restoration requires BOTH (a) W_matched ≤ 0.3 (and per-prep bands) AND
   (b) the same-window witness re-certifying under the ORIGINAL Exp211 rule (W ≥ 1.3 and W − 5·seW > 0).
   Otherwise the claim stays withdrawn. The **new same-window witness W becomes the canonical number**; the
   old 500-shot W=1.894 stands as corroboration only.
4. **Statistical note on the 0.3 band.** Ideal per-arm ⟨X_c⟩ = 0 (maximal shot variance): at 100 shots/pub,
   se(W_matched) ≈ 0.10, so 0.3 is a ~3σ band. Adequate for the swap-class artifact (signature ±2) — state
   the band together with its se in the frozen pre-reg; use 250 shots/pub only if a 5σ band is wanted.
5. **Stronger free gate (replaces the §5-G3 2q-count scan).** The §10.2 reproduction proves the exact native
   compile can be rebuilt and simulated locally. Make it mandatory pre-flight: rebuild `native=True` circuits
   for ALL Exp212 pubs, simulate, assert exact ideal outcomes. Strictly stronger than counting 2q gates.

### 10.5 Paper (multi-substrate doc) gaps
1. §8 Data Availability omits the negative results' receipts: add Exp211b null task
   `ca68e121-605b-49eb-92e9-eddc6ec30c7b` and Exp211c calibration task
   `6750e981-914e-4f09-ae0b-5c89fd28e929` (honest-negatives rule: misses keep their accounting).
2. The banner's root-cause sentence ("appears to compile anomalously") should cite §10.1–10.3: recorded
   counts are one bit-permutation from perfect; client compile exonerated; class-scoped calibration gap;
   on-device proof pending the $8.30 gate-free cal.
3. Title/abstract/§4.4/§5/§7 still carry the three-substrate claim with only the banner as correction. The
   banner is declared authoritative, so this is acceptable **only while Exp212 is pending**; whichever way
   Exp212 resolves, the body (and title) must be rewritten in the same cycle the result lands.
