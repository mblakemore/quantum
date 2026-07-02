# Exp91 — Gate REALNESS at held placement: echo-canceling CZ·CZ=I vs amplitude-moving SWAP·SWAP=I (pre-registration)

**Whisper C4453 · ibm_fez · single calibration window · pre-registered before any QPU result.**
Provenance reuse (no re-derivation): code/circuit/grade from Exp84; CZ `fold_routed` + BASE point (opt=2,seed=100,158 2q) from Exp87; noiseless-codeword-verify pattern from Exp86; same-window single-job harness from Exp88/89.

## The open caveat this targets (F69's own flag)

F67→F69 all reach ~208 gates **at held placement** by folding `CZ·CZ = I` into the ONE routed base circuit. F69 measured the gate-count-only term `W(158) − W(FIX 208) = −0.018 ≈ 0` and concluded **"gate-count is second-order AT HELD PLACEMENT."** But F69 explicitly flagged the load-bearing caveat:

> *"FIX reaches 208 via folded CZ·CZ=I identities (gentle), not genuine routed 2q-gates … the effect of adding 50 REAL routed 2q-gates at held placement is never cleanly isolated (bundled into placement_i)."*

**Hypothesised mechanism of the "gentleness":** an immediate self-inverse pair (CZ then CZ on the same edge) lets coherent over-rotation errors **echo-cancel**, so +50 folded CZ inject far less *effective* error than +50 generic 2q-gates. F69 could not separate "gate count doesn't matter at held placement" from "the *fold* doesn't matter because it self-echoes."

Note F69 has *partial* evidence the count is second-order for real gates (W_i-vs-2q corr = +0.092 across K=6 VAR draws spanning 172–208 gates), **but that correlation is confounded**: the VAR draws vary placement AND count together. This experiment removes that confound — placement held, count varied by two *different gate types*.

## The intervention

One `sampler.run` → ONE window (drift removed by construction). 5 objects × {Z, X} = **10 PUBs**, 2000 shots. **Placement is HELD for every object** (all folds/pads reuse the base's physical edges; no new qubit, no re-transpile, no re-placement — verified in scan).

| object | construction | 2q | gate character |
|---|---|---:|---|
| ANCHOR 158 | opt2/seed100 base | 158 | — |
| FIX-CZ 178 | base + 10 `CZ·CZ=I` folds | 178 | diagonal, **echo-canceling** |
| FIX-CZ 208 | base + 25 `CZ·CZ=I` folds | 208 | diagonal, **echo-canceling** |
| FIX-SWAP ~176 | base + 3 `SWAP·SWAP=I` pads | ~176 | amplitude-moving, **echo-defeated** |
| FIX-SWAP ~206 | base + 8 `SWAP·SWAP=I` pads | ~206 | amplitude-moving, **echo-defeated** |

Ideal witness preserved **algebraically**: `CZ·CZ=I` (self-inverse, as Exp87) and `SWAP·SWAP=I` where the native SWAP decomposition is `Operator`-verified `== SWAP` once on 2 qubits, and the doubled block `== Identity` (both exact, tractable). No 156-qubit sim needed (same guarantee Exp87/88/89 relied on).

**KEY ISOLATE:** `Δ_type = W(FIX-CZ 208) − W(FIX-SWAP ~206)` — matched 2q-count (|Δ2q|≤~2), held placement → attributes purely to gate **realness** (echo-canceling vs echo-defeated).

## PRE-COMMITTED CLAIM BOUNDARY (decided before any QPU result)

- **BRANCH A — ECHO-ARTIFACT / F69 QUALIFIED:** `Δ_type > +0.08` (SWAP pad degrades more at matched count). → F69's held-placement "gate-count second-order" was **partly a coherent-echo artifact of the CZ·CZ fold**; genuine echo-defeated 2q activity *does* lower the witness. Report Δ_type and both slopes; this **qualifies** (does not overturn) F69 — placement still dominates, but the *fold* under-reports real-gate cost.

- **BRANCH B — TYPE-IMMATERIAL / F69 STRENGTHENED:** `|Δ_type| ≤ 0.08` (matched within tie floor). → gate-count is second-order at held placement **even for real, echo-defeated gates**; F69's headline strengthened beyond the fold caveat.

- **BRANCH C — REVERSE:** `Δ_type < −0.08` (SWAP reads HIGHER). → unexpected; report honestly and treat as a **confound flag** (decomposition/relabeling artifact), do NOT over-interpret as "SWAP is gentler."

Floor: `|Δ| < ~0.08` is within ~2σ of 0 (difference of two W's, 2000 shots, X post-selected → ~1000 eff/half, per-W std ≈ 0.03, difference std ≈ 0.04) = "tie."

## Bounds I will NOT claim (stated before results)

- ❌ **Proof of the echo mechanism.** BRANCH A is *consistent with* coherent-echo cancellation; the scalar witness cannot prove the channel. "Gate realness matters at held placement" is the claim; "because of coherent echo" is the hypothesis, labelled as such.
- ❌ A mechanism / error-channel attribution (dephasing/leakage/depolarizing) — scalar witness only.
- ⚠️ SWAP count ~206 vs CZ 208: |Δ2q| ≤ ~2, matched **within shot-noise tolerance** (Exp89 flagged >15 as contaminated); reported exactly, not assumed.
- ⚠️ Held placement is verified for the WITNESS/base edges (SWAP block reuses existing physical edges); the pads add depth on those edges — **depth stays coupled to count** (same standing bound as Exp87 folding; I isolate gate *type* at matched count, not depth).
- ⚠️ One window, K=1 per object; the two-level slope characterizes direction, not a precise dose-response curve.

## Success = a banked result on ANY branch

The value is turning F69's own flagged caveat ("real routed gates at held placement never cleanly isolated") into a measured `Δ_type`. Whether real gates degrade more (A, self-qualifies F69), match the fold (B, strengthens F69), or reverse (C, confound), each is a genuine sharpening. Pre-committed so the grade cannot be motivated after the fact.
