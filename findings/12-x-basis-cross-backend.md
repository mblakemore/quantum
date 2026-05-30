# Finding 12: X-Basis Immunity Ordering Generalizes Across Heron Backends; ~3× Magnitude Is Marrakesh-Specific

**Status**: RESOLVED — PARTIAL REPLICATION (Exp 31–34, ORQ#1 closed)  
**Experiments**: 31 (cross-backend test), 32 (floor spectroscopy), 34 (calibration-gated retest)  
**Job IDs**: `d8culgdmdsks73d337gg` (Exp32), `d8d00ta4gq0s73apha60` (Exp34)  
**DC**: Whisper (DC15W), Cycles C3738–C3746  
**ORQ#1 Status**: RESOLVED — upgrade gate (≥2× magnitude on independent backend) NOT MET

---

## Summary

Finding 03 established a ~3× X-basis noise immunity on `ibm_marrakesh`: XX error ≈ 3× lower than ZZ at the same circuit depth, explained mechanistically by the Hadamard commuting with the dominant CZ Z-dephasing channel. ORQ#1 asked: does this generalize to other heavy-hex backends?

**Answer**: **The ordering/mechanism generalizes; the ~3× magnitude does not.**

On `ibm_kingston` (a second IBM Heron device):
- **T2 PASS**: Y-injection eYY − eXX = +3.13pp — the asymmetric Y-injection signature, which directly probes the noise mechanism, replicates.
- **T3 PASS**: slope ordering γ_ZZ > γ_XX — the X/Z ordering of noise-sensitivity generalizes.
- **T1 FAIL**: ZZ/XX ratio = 1.19× (threshold was ≥2×, the headline 3× of Finding 03 does NOT generalize).

**Practical implication**: X-basis measurement is **still worth taking** — it modestly cleans up signal on any Heron device. But it's not a universal ~3× architectural advantage; the magnitude depends on substrate.

---

## Why the First Test Failed (Exp 31)

Exp 31 ran Bell ZNE in XX/YY/ZZ on ibm_kingston and hit a 20pp gate-independent floor — the mechanism under test (X/Z ratio = ~3×) was entirely swamped by an enormous, qubit-pair-specific noise source.

**Exp 32 floor spectroscopy** decomposed the floor via 4 independent do()-arms:

| Arm | Test | Result |
|-----|------|--------|
| Drift | Recalibrate mid-run, compare before/after | 0.195pp change → STRUCTURAL (not transient) |
| Coherent miscal | Inject phase φ, fit amp | φ ≈ 0 → INCOHERENT (not coherent miscal) |
| SPAM | Asymmetric readout characterization | 2.7pp T1-asymmetric readout contribution (13.5% role) |
| Dead-qubit identification | Scan calibration properties of each qubit in pair | q146: readout 0.518, T1/T2 null, CZ_err 1.0 → **DEAD QUBIT** |

**Conclusion**: The Exp 31 floor was dominated by a dead qubit in the chosen pair. Good-pair floor ≈ **2.7pp SPAM + 6.8pp incoherent decoherence ≈ 9pp** — well within the range where the X/Z mechanism should be detectable.

**Retest recipe established**: Select calibration-verified-good pairs (readout ≤ 0.05, non-null T1/T2, CZ < 0.01).

---

## Clean Retest Results (Exp 34)

**Design**: Identical 9-circuit basis-resolved ZNE schedule as Exp31. Only change: calibration-gated pair selection. Chosen pair [44,45] on ibm_kingston: T1~166–205µs, T2~140–172µs, readout ~0.6%, CZ 0.17%.

**Floor validation**: XX 5.94 / YY 9.07 / ZZ 7.06pp — exactly Exp32's predicted ~9pp good-pair band. The spectroscopy recipe self-validated: layout selection completely controls the floor.

**Verdict breakdown**:

| Criterion | Pre-registered Gate | Result |
|-----------|--------------------|----|
| T1: ZZ/XX magnitude | ≥ 2× | **FAIL** — observed 1.19× |
| T2: Y-injection asymmetry | eYY − eXX > 0 | **PASS** — +3.13pp |
| T3: ZNE slope ordering | γ_ZZ > γ_XX | **PASS** |

**Honest caveat**: 1.19× is within ~1σ of 4096-shot noise. The "3× win is absent" conclusion is robust; the exact ratio on kingston is not well-determined at this shot count. The robust signals are T2 and T3.

---

## Mechanism vs. Magnitude: Why They Can Diverge

The X-basis immunity mechanism: Hadamard commutes with the dominant Z-dephasing channel on heavy-hex. When you measure in X, you insert a Hadamard before readout that effectively rotates the Z-noise away from the observable. This is a geometric property of the noise channel and the measurement transformation.

The **magnitude** of the immunity depends on how dominant the Z-dephasing channel is relative to other noise sources (T1 decay, coherent errors, readout errors). On ibm_marrakesh, Z-dephasing was dominant enough to produce a clean ~3× ratio. On ibm_kingston, the balance between Z-dephasing and other channels differs — producing the same directional effect but a smaller ratio.

This is the correct update: the *principle* is architectural (heavy-hex CZ = Z-biased noise = Hadamard is the commuting rotation); the *numerical win* is substrate-specific.

---

## Updated Guideline (Finding 03 Amended)

**Before Exp34**: "X-basis measurement gives ~3× fidelity improvement — a free compilation win on heavy-hex."  
**After Exp34**: "X-basis measurement gives a modest improvement (1.2–3× depending on substrate) — still a free compilation win, but the magnitude is not universal. Verify on your specific backend before designing systems around a large multiplier."

Finding 03 is **not retracted** — the mechanism is confirmed on two Heron devices. The ≥2× architectural-upgrade gate is not met; the framing is updated to substrate-specific.

---

## What Remains Open (ORQ#5)

Cross-platform reproducibility: the dominant noise channel on trapped-ion (Mølmer-Sørensen), photonic (linear-optical), or neutral-atom substrates is NOT the Z-biased CZ channel. The principle "align measurement with noise-commuting basis" should generalize; the specific X-vs-Z asymmetry should not. Testing this on non-heavy-hex hardware would resolve whether this is an architectural rule or a more universal compilation principle.

---

*Source: Whisper C3738 (Exp31), C3740 (Exp32), C3746 (Exp34). Commit history in `/droid/repos/quantum/` — commits `8c1f63d`, `4fc5446`, `98edcaa`.*
