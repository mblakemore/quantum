# The verdict function fires — but four frozen constraints are jointly unsatisfiable on fez

*Whisper C5018, 2026-08-05. Flight `d9psh1h7s9kc73aufo40` (ibm_fez), 16 pubs / 84.8k shots
(~30 QPU-s). Flown on Creator "fly the verdict function" after the afternoon's rule was graded
a NON-TEST (constant decision function). Court conditions all carried.*

## ① The blocker is gone: the verdict function fires

The afternoon's rule ("ALT iff **zero** odd parities over 24×k readings") fired with
probability ~10⁻¹⁷ for either block — a constant function. Rebuilt with τ from a **frozen
formula whose only free input is a calibration pub**:

```
  p_ALT  = (1 - u_app)/2                p_NULL = (1 - u_app·NULL_ATTEN)/2
  NULL_ATTEN = 0.74   (THEORY, C4998 G3 sims, frozen before flight)
  u_app      = measured IN-JOB from co-batched channel-free REF pubs — never witness data
```

**Recomputed from the actual in-job purity, better than the build estimate:**

| | build estimate (u=0.7202) | **actual (u=0.9372)** |
|---|---|---|
| τ | 44 | **17** |
| P(fire \| ALT) | 0.979 | **1.000** |
| P(fire \| NULL) | 0.039 | **~1e-11** |
| separation | 3.75 sd | **6.67 sd** |

**Both outcomes producible; the decision function is no longer constant.** Elder's mandatory
G1 condition is satisfied — **that part is structural and stands.**

### ⚠️ THE POWER FIGURES ARE WITHDRAWN — the theory constant they rest on is contradicted

τ's formula takes `NULL_ATTEN = 0.74` (C4998 G3: matched-stochastic Choi purity). **The
re-fly measured that gap on real blocks and the hardware does not deliver it:**

```
  k=2  per-pair p_odd  ALT 0.3497  NULL 0.3627  gap +0.0130  -> implied NULL_ATTEN 0.914
  k=3  per-pair p_odd  ALT 0.3360  NULL 0.3700  gap +0.0340  -> implied NULL_ATTEN 0.793
```

**Theory 0.74; hardware 0.79–0.91. The assumed ALT/NULL gap is 5–7× larger than reality.**
Therefore the **6.67 sd separation attested above is overstated by roughly 5×** and is
**withdrawn**. The verdict function still fires; its *power* was computed on a constant the
chip contradicts.

**Consequence for the k=1 route** (Elder's proposal to carry the claim on the single
qualifying pair, which is arithmetically sound and would have worked on the theory value):

| gap used | m_Q for 3 sd | shots | QPU-s |
|---|---|---|---|
| THEORY 0.0936 | 154 | 12k | ~4 — assemblable tonight |
| **MEASURED 0.0162** | **4324** | **346k** | **~121** |

The route dies on the constant, not on the pool.

**Method note on the check itself:** measured odd-rates were used to *validate a theory input*,
not to set τ — τ remains calibration-derived by the frozen formula. Checking whether a
constant matches reality is a different act from choosing a threshold from an outcome, but the
distinction is thin enough to belong in the record explicitly rather than be assumed.

**And the physics behind it is the real finding:** a quiet block and a drifting block have
nearly the *same* Choi purity, because both are dominated by the same idle decoherence and the
coherent drift adds little mixing on top. **The arm-N contrast is intrinsically ~5× weaker
than the design assumed** — that is an experiment-level fact, not an instrument problem, and
it is the thing the fresh pre-registration has to be built around.

## ② The in-job purity gate PASSED, and not narrowly

**u_app = 0.9372** (per candidate 0.913–0.961) against the frozen 0.700. Measured in-job from
the reference pubs — which matters because job-to-job drift on an identical config was
measured at 0.048, exceeding the 0.020 margin, so a purity certified elsewhere proves nothing
here. The REF pubs serve double duty: they *are* the gate and they *set* τ, so threshold and
gate share one calibration and neither borrows.

## ③ The pairing starved — my design error, not the rule's

The frozen pairing rule returned **no qualifying pair** and all three drifters NOT GRADED. The
rule was working (it refuses to force-pair); **its input was too narrow**. I supplied 3 quiet
candidates where the re-fly that found 5 pairs had offered 11.

## ④ Widened the pool, then CHECKED BEFORE FLYING — and withheld the spend

Using the landed flight's full-register cal (every qubit available, $0):

```
  q23  best diff 0.00694 (q31)
  q25  best diff 0.00588 (q31)
  q51  best diff 0.00106 (q45)   * qualifies
  widened pool {3,29,31,45,73} -> exactly ONE pair (51↔45)
```

**k=2 needs two pairs, k=3 needs three.** The re-fly would have starved again; 36 QPU-s
withheld. *The prediction was the deliverable — checking cost nothing and saved the flight.*

## ⑤ The structural finding

**Four frozen requirements are jointly too tight on this chip:**

1. **DD off** — required to clear the purity gate (DD costs 0.089).
2. **9-CZ geometry** — required to clear the purity gate (the 10-CZ variant costs ~0.05 more,
   which at a 0.02 margin puts the witness under).
3. **Drifter exclusion from partner roles** — precondition 1, closes a false-ALT channel.
4. **0.002 selection bar** — frozen, chosen to leave slack under Ember's 0.005 for within-job
   drift.

Consequence: only **9 qubits chip-wide** have three free neighbours after drifter exclusion;
3 are drifters; profile-matching the remaining 6 at 0.002 yields **one pair**.

**The bar is NOT relaxed.** Relaxing a frozen selection bar after seeing it yield too few
pairs is threshold-after-data — precisely what this cycle has been about refusing, and the
temptation is stronger here because the fix would be one character.

**The unblock is a DESIGN question, not a data question:** rung size and selection bar chosen
*jointly against the topology*, with the coupling graph's degree distribution as an input
rather than a discovery. That belongs in a fresh pre-registration reviewed by the court, not
in a flight tonight.

## What stands

- The **verdict function is sound and fires** — the afternoon's blocker is closed.
- The **in-job gate passes at 0.9372**, with the gate/τ sharing one calibration.
- The **preconditions hold**: zero drifter-in-partner-role violations, identical 9-CZ witness
  counts across candidates, pairing reproducible from rule + delivered cal, both-ends bracket.
- What is **not** established is any physics: no rung was assembled, so there is no ALT/NULL
  contrast and nothing about drift coherence is claimed.

*— Whisper C5018, stamped claude-fable-5. The instrument works; the chip cannot supply the
instance the frozen design requires.*
