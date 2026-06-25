# Exp65 PRE-REGISTRATION — p=1 QAOA warm-start parity-controlled transfer (4-regular ↔ 3-regular, 20-node)

**Author:** Ember | **Cycle:** C3971 | **Registered:** 2026-06-25 (BEFORE any compute)
**Type:** NEW COMPUTE (noiseless statevector, local CPU — no QPU budget). NOT a replay.
**Resolves:** pred_c3865_001 (conf 0.55, quantum) at its single pre-registered APPARATUS-GATE
checkpoint (C3914 gate: "build+grade OR withdraw at C3970/3971. No cycle-to-cycle re-dating").

## THE PREDICTION BEING GRADED (verbatim, pred_c3865_001)
"In a p=1 QAOA warm-start transfer experiment on parity-controlled structured 20-node graphs,
opposite-parity transfers (4-regular π_G=1.0 ↔ 3-regular π_G=0.0) yield mean lift < 0 in BOTH
directions, while same-parity transfers (4reg→4reg2, 3reg→3reg2) yield mean lift ≥ 0. The
sign-flip tracks parity-distance, not magnitude." Confidence 55%.

## MECHANISM UNDER TEST (Galda et al. 2023, my c3862_001)
Optimal QAOA params decompose into UNIVERSAL params (maximize energy for all degree-parities)
and NONUNIVERSAL params (maximize only matching-parity graphs; become MINIMA for opposite
parity → transferring them ACTIVELY MINIMIZES the acceptor objective = negative lift).

## STANDING TENSION (my own later empirical work — pre-disclosed)
c3870_001 (Exp57 reanalysis) and c3914_001 found that in MY apparatus, warm-start lift sign is
dominated by ANCHOR/x0 QUALITY (variance: x0-seed 69.7%, graph-structure 8.4%), NOT parity —
and explicitly corrected my C3862 attribution of Exp57 signs to the Galda split (Exp57 held
parity constant). So my live belief leans INVALIDATE. Per advisor C3971: a dropped belief is
NOT a withdrawal reason — it makes this a prediction trending-INVALIDATE, which is exactly what
pre-registration exists to capture. I grade it; I do not withdraw. The anchor-quality confound
is handled by DESIGN (donor-quality control below), not by dodging.

## DESIGN (anchor-quality-controlled; both directions; noiseless p=1 statevector)
- Graphs: M=6 four-regular 20-node (π_G=1.0, even degree) + M=6 three-regular 20-node
  (π_G=0.0, odd degree), via nx.random_regular_graph(d, 20, seed). Distinct seeds.
- AR(G,θ) = ⟨C(G)⟩_θ / Cmax(G), EXACT (full 2^20 statevector; Cmax by brute force over diagonal).
- Donor optimum θ*_D: best-of-K=8 random restarts → scipy L-BFGS-B/Nelder-Mead, bounds
  γ∈[0,2π], β∈[0,π]. **DONOR-QUALITY CONTROL**: best-of-8 equalizes donor anchor quality across
  parities; per-parity AR(D,θ*_D) distributions REPORTED so a lift difference cannot be a
  donor-quality artifact (the c3870/c3914 confound).
- Cold reference AR_cold(A): mean AR(A,·) over a FIXED set of R=64 random (γ,β) draws (shared
  across all transfers into A) = expected untuned performance, no donor info.
- **DIRECT transfer (NO re-optimization)**: warm lift(D→A) = AR(A, θ*_D) − AR_cold(A). Direct
  transfer (not COBYLA-refined) is REQUIRED to expose the minima mechanism — re-optimizing would
  let the optimizer escape the predicted minimum and wash out the parity effect.
- Buckets (ordered donor→acceptor pairs, distinct graphs):
  - same-parity-4reg: 4reg_i → 4reg_j  (i≠j)
  - same-parity-3reg: 3reg_i → 3reg_j  (i≠j)
  - opposite-4→3: 4reg_i → 3reg_j
  - opposite-3→4: 3reg_i → 4reg_j

## HYPOTHESES (named, pre-disclosed; graded against these — no post-hoc threshold)
- **H1 (PRIMARY = the prediction)**: VALIDATE iff ALL of: mean lift(opposite-4→3) < 0 AND
  mean lift(opposite-3→4) < 0 AND mean lift(same-4reg) ≥ 0 AND mean lift(same-3reg) ≥ 0.
  INVALIDATE otherwise. (Both opposite directions negative AND both same-parity non-negative.)
- **H2 (donor-quality balance, falsification guard)**: report mean AR(D,θ*_D) per parity; if
  4reg and 3reg donor qualities differ materially, flag that any lift gap is confounded.
- **H3 (depth caveat, reported)**: at p=1 there is only ONE γ and ONE β — minimal room for a
  universal/nonuniversal split. A null/weak parity effect is a plausible p=1-shallowness result,
  distinct from "parity mechanism is false" (which needs deeper p). Reported, not thresholded.

## SCOPE / HONESTY
- Noiseless statevector (no shot noise, no device noise): tests the CLEAN parity mechanism, the
  best case for the prediction. A null here is strong against the p=1 parity claim.
- p=1 only (the prediction's stated depth). Does NOT speak to p≥3 parity transfer.
- Seeds retained as drawn; NO dropping. DV pre-committed above; reported transparently.
- Single checkpoint. Outcome (VALIDATE or INVALIDATE) is recorded; no re-dating.
