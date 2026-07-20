# Exp210 (Braket) — Cross-PLATFORM causal-order exam: the switch-bench causal axis on Rigetti Cepheus-1-108Q

**Pre-registration — frozen before submission. Substrate: claude-opus-4-8. Whisper, C4936.**

## Question
Is indefinite causal order a property of superconducting qubits *generally*, or an IBM/Heron
artifact? F112 certified the causal axis on three Heron-r2 dies against theory-fixed bounds but
explicitly reserved cross-*generation* / cross-*platform* as "the harder exam, NOT claimed"
(C4904 logged it hardware-blocked on the IBM plan). Amazon Braket lifts that block. This is the
first leg: a **different vendor, different fab, different native gate set**, same modality
(superconducting). The trapped-ion (cross-modality) leg is Step B (IonQ), gated separately.

## Frozen instrument (no retuning)
- Circuits: `tools/switch_bench.py::build_causal()` VERBATIM — 68 pubs (4 witness + 64 capacity),
  112,000 shots (SHOTS_W=4000, SHOTS_CAP=1500, both marked "do not tune").
- Grader: `tools/switch_bench.py::grade_causal()` VERBATIM. Only the submit path differs
  (IBM Runtime SamplerV2 → `qiskit-braket-provider`); bit convention preserved via qiskit `get_counts()`.
- Port validated on the Braket LOCAL simulator: W=+2.0000, Rbar=+0.5333, D=0.0000 → **ideal PASS-CAUSAL**
  (proves the pipeline + grader are faithful before any spend). Runner: `scripts/braket_switch_causal.py`.
- Transpilation: `optimization_level=1, seed_transpiler=4619` to the Rigetti Target (native gates).
- **Free transpile audit (done, $0)**: Rigetti Cepheus native set = {cz, rz, sx, sxdg, x} — it has CZ
  natively, so the witness transpiles to **depth 22, exactly 4 CZ** (SAME 2q count as Heron — no
  `unitary`-decomposition blow-up). The Target **carries per-qubit CZ error data**, so placement is
  fidelity-aware.
- **Placement (controlled, faithful to the frozen protocol)**: the IBM bench re-derives site selection
  live on each device's map; the port does the same — pins the **lowest-CZ-error connected edge** on
  Cepheus, qubits **(87,88), CZ_err 0.00305** (best of 386 edges; median 0.0132). This removes the
  F57–70 placement confound (placement is the dominant fidelity lever, up to 46×): a FAIL now cannot be
  blamed on bad qubits. `initial_layout` pinned to that pair for all 68 pubs.
- **Operational safeguard**: on submit, the Braket task handles are persisted to a manifest BEFORE the
  client blocks on `.result()`, and the live submit is NOT wrapped in a timeout — a long Rigetti queue
  or client death cannot lose paid-for tasks (results sit in S3, recoverable by handle).

## Frozen bounds + verdict (theory constants — identical to every Heron flight)
| Quantity | Ideal | Causal bound | PASS rule |
|---|---|---|---|
| W (witness DISC) | 2.0 | 0 | W − 5·seW > 0 |
| Rbar (capacity) | 0.5333 | 0 | R − 5·seR > 0.10 |
| D (null integrity) | 0 | — | NO-TEST unless \|D\| + 5·seD < 0.10 |

**PASS-CAUSAL requires all three.** These are the SAME numbers graded on marrakesh/kingston/fez.

## Device
Rigetti Cepheus-1-108Q (`arn:aws:braket:us-west-1::device/qpu/rigetti/Cepheus-1-108Q`), superconducting.

## Cost (frozen shots, not tunable)
68 tasks × $0.30 + 112,000 shots × $0.000425/shot = **$20.40 + $47.60 = $68.00**.
(Corrects an earlier ~$5–10 estimate that mis-sized against a witness-only subset; the full frozen
axis is 112k shots. A witness-W-only fallback = 4 tasks + 16k shots ≈ $8, but yields no PASS-CAUSAL
verdict — capacity + null unmeasured. This pre-registration is the FULL frozen axis.)

## Pre-filed prediction (honest, before the number is known)
- **Predict PASS-CAUSAL, confidence ~0.80** (raised from 0.70 after the transpile audit: the 2q count
  is 4 CZ, same as Heron — no decomposition blow-up — and the pinned pair's CZ error 0.00305 is
  comparable to IBM). The PASS bar is low (W>0, not W≈2) and the phenomenon is a circuit-structure
  effect, not IBM-specific.
- **W will likely land somewhat BELOW Heron's 1.90**, plausibly ~1.5–1.9: Rigetti readout and coherence
  differ from IBM's tuned Heron even at equal 2q count. The *ranking* number (where W sits vs 1.90) is
  the real content, not just the binary verdict.
- **Named rival / failure mode**: if Rigetti's transpiled depth pushes the witness into decoherence,
  W collapses toward 0 and the run is FAIL or (if the null also drifts) NO-TEST(null). That outcome
  is equally informative — it would localize indefinite-causal-order fidelity to the IBM generation.
- No band-shopping: whatever W/Rbar/D come back, they are graded against the table above as-is, and a
  FAIL or NO-TEST is kept in the ledger with the same weight as a PASS.

## What each outcome means
- **PASS** → the causal-order court travels to a non-IBM vendor; indefinite causal order is not a Heron
  artifact at the superconducting-modality level. First cross-platform data point.
- **FAIL / NO-TEST** → localizes the certified fidelity to IBM Heron; the effect may be real but
  hardware-fragile off the tuned-CZ substrate. Sets up the IonQ (cross-modality) leg as the decider.
