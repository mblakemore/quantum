# Clearing the fog at N=8 — the fog is coherent, not readout; and the scar is not fragile (Ember, C4203)

**Creator directive (2026-07-18):** *"clear the fog at N=8 instead"* of going deeper to N=10. Rather than
add more fog with depth, sharpen the Exp172 read with error mitigation. **Job** `d9dv4qsinv1c73apjff0`,
`ibm_fez`, 37 circuits (5 inits × step 0..6 + 2 in-job readout-cal), 8000 shots, pinned to 8 physical
qubits. **Pre-reg** (0.55, frozen): `R_rel = s_scar/s_gen > 0.85 (no scar-specific fragility) AND
readout mitigation lifts the F-channel R more than the Neel R`. **Verdict: HELD.**

---

## Two results

### 1. The fog is coherent Trotter/gate error — NOT readout

| channel | raw R | mitigated R | readout lift |
|---|---|---|---|
| Néel (readout-robust) | 0.59 | 0.60 | +0.01 |
| F (readout-limited) | 0.31 | 0.33 | +0.03 |

Readout fidelities measured **in-job** on the pinned qubits: a = P(0|0) = 0.993, b = P(1|1) = 0.989 —
fez's readout is *already excellent*. So readout mitigation is a small correction: it lifts the F
channel 3× more than Néel (+0.03 vs +0.01 — F *is* the more readout-sensitive channel, the directional
prediction held), but both lifts are tiny **because there was little readout fog to remove**. The
decisive point is the **residual**: even after mitigation, Néel R = 0.60, not 1.0. That **40% signal
loss is not readout** (readout is 0.99) and not the 2q-gate depolarizing model (already divided out in
s). It is **coherent Trotter error + single-qubit/idle decoherence** — the fog readout mitigation
cannot touch. "Clearing the fog" located the fog: not in the measurement, but in the algorithm (finite
Trotter step) and gate coherence.

### 2. The scar is not fragile (the non-circular result)

`R_rel = s_scar / s_gen = 0.627 / 0.669 = **0.94** ≈ 1`. Fitting the scar's decay and the generic
ensemble's decay **separately** (independent normalizers), the N=8 scar decays at essentially the same
rate as the generic pack. **No scar-specific fragility** — |Z₂⟩ is not more delicate than generic
states under the hardware noise; they all decohere together. Combined with Exp172 (scar survives, R
invariant from N=6), the scar mechanism is robust; only the shared coherent/decoherence budget limits
how far it reads.

## The methodology that makes both trustworthy (the advisor catch)

The first design was **circular** and the advisor caught it: I normalized the anomaly by a global s
**fit from the same ⟨Z⟩ that build the anomaly**, so `R = s/s = 1` identically — the truth-gate
"passed" by validating a tautology, not by detecting a broken scar. This is the **sixth recurrence**
this session of one theme — a reference derived from the thing it tests (matched-control duration
C4196, estimator C4198, decay baseline C4199, borrowed-CZ C4199, cherry-picked control C4201,
self-referential normalizer here). The fix, both halves with **independent** normalizers:

- **Absolute R** uses an independent gate-model s (priced on the pinned qubits, C4199) — so "does
  mitigation lift R" is well-posed.
- **Relative fragility** `R_rel = s_scar/s_gen` fits scar and generics **separately** — non-circular by
  construction. The truth-gate now *proves* it can detect what it exists to detect: injecting a
  scar-specific ×0.8 decay drives R_rel to 0.80, while pure global depolarizing gives 1.00.

Readout calibration was measured **in-job** on the same pinned qubits (no borrowed backend rate — the
C4199 lesson), and the readout model is tensored (per-qubit); the rigorous claim rides the per-qubit
Néel channel (F's tensored correction is approximate).

## Fence

Single pinned 8-qubit line, tensored readout model, one revival step. The "residual is coherent"
attribution is by elimination (not readout, not 2q-depolarizing); a direct measurement of the coherent
part would need ZNE (drowns at 433 CZ) or a finer-Trotter reference (deeper). A sharper *read* of the
Exp172 scar, not a new physics claim.

## What the universe answered

Asked to clear the fog rather than go deeper: the fog on the N=8 scar is **not in the readout** (which
is already 99% clean) — it is **coherent Trotter + gate error** (40% residual), the part error
mitigation of the measurement cannot remove. And the scar itself is **not fragile** — it decays like
the generic ensemble (R_rel=0.94). To actually sharpen this scar one must reduce *algorithmic* error
(fewer/finer Trotter steps, or amplitude-based ZNE), not measurement error. The wall here is coherence,
not readout.

**Numbering:** new experiment (Exp173), exotic-phases wing; the mitigation companion to Exp172.
