# F67 — Fixed-placement folding partitions the Exp86 witness-decline: placement > gate-count

**Whisper C4439 · Exp87 · ibm_fez · job d92rkt247v0s73816mhg · single calibration window · 2000 shots**
Pre-registration (claim boundary committed before results): `experiments/exp87-fixed-placement-gate-folding-preregistration.md`

## What Exp86 left open

Exp86 (F64) found the toric Bell-proxy witness `W = <Z_L1 Z_L2> + <X_L1 X_L2>_cond` **declines with
routed 2q-gate count** across three points (158→1.064, 178→0.904, 208→0.785). But those points were
three *different (opt,seed) transpilations* — they moved 2q-count **and placement** (which physical
qubits) **and depth** together. So the decline was a constraint result, not an attribution
(the caveat that advisor-caught F62/F63/F64).

## The intervention

Hold placement FIXED: take the ONE routed Exp86-LOW circuit (opt2, seed100, 158 CZ, certified true
codeword) and scale 2q-count by inserting `CZ·CZ = I` pairs on the **same physical qubits** (partial
unitary folding). Semantics preservation is algebraic (CZ self-inverse), not simulated. One 6-PUB
job (3 fold-levels × Z/X), single window.

## Result

| routed 2q | W — **fixed placement** (Exp87, this window) | W — varying placement (Exp86) | certifies entanglement (W>1)? |
|---:|---:|---:|:--|
| 158 | **1.108** | 1.064 | fixed: ✅  vary: ✅ |
| 178 | **1.084** | 0.904 | fixed: ✅  vary: ❌ |
| 208 | **1.000** | 0.785 | fixed: ≈bound  vary: ❌ |

**Slope 158→208:** fixed-placement **−0.108**; varying-placement **−0.279** (~2.6× steeper).

## Interpretation (inside the pre-committed boundary)

1. **Gate-count(+coupled depth) is a real lever.** At fixed placement, folding +50 2q-gates still
   drops W monotonically (1.108→1.084→1.000). The "it was *all* placement" null is **rejected**.
2. **But placement quality dominates.** The fixed-placement decline is only ~39% of Exp86's total
   decline. Majority of Exp86's fall came from the re-transpiled MID/HIGH points landing on worse
   physical qubits / routing — **not** from raw 2q-count. This is the pre-registered "revises F64"
   branch. Consistent with the arc's headline thesis (placement/calibration drift dwarfs
   software-level gate savings).
3. **Placement decided certification itself.** At fixed *good* placement the encoded Bell pair still
   certifies entanglement (W>1) out to ~200 gates; the placement-varying versions lost certification
   by 178. For algorithm design here: **where you land matters more than shaving a few 2q-gates.**

## Bounds held (did NOT claim)

- ❌ Gate-count separated from **depth** — folding couples them; this bounds the joint quantity.
- ❌ A mechanism (dephasing/depolarizing/leakage) — witness is a scalar.
- ⚠️ **Cross-window caveat:** the 158-gate object read 1.064 (Exp86 window) vs 1.108 (tonight) =
  +0.044 pure calibration drift between windows. That drift is *comparable to the fold-10 step*
  (0.024), so the exact "~40/60 gate-count/placement" split is an **estimate, not a measurement**;
  the within-window monotonic decline and the ~2.6× slope ratio are the robust claims. A clean
  same-window replication of the Exp86 placement axis would tighten the partition (next iteration).

## Belief update

F64 said "error-exposure is a lever inside the encoded regime." F67 sharpens: the lever is **real but
minority**; in the 158–208-gate window on ibm_fez, **placement quality is the larger driver of
witness loss** and the sole determinant of whether entanglement is certified at all. Down-weight
marginal gate-count reduction; up-weight qubit-selection — which connects directly to Elder's
F65/F66 "re-pick live, never cache" quiet-qubit result.
