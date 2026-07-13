# Exp131 Pre-Registration — THE REPLICATOR'S LEGAL LIMIT: Optimal Universal Cloning Ceiling (Horizons-3 H1)

**Author**: Whisper (DC15W), C4670 (2026-07-13) · **Substrate**: claude-opus-4-8
**Status**: FROZEN before hardware submission
**Directive**: Creator ("F109 numbered, next one!") — Horizons-3 H1. A genre-shift within the
quantum lane: after four advantage certifications (games F106, storage F107, metrology
F108/F109), a **limit/no-go certification** — the exact ceiling the universe puts on copying,
with a built-in cheat-detector.

## Scope, stated first

- **What this is**: certification that the optimal symmetric universal 1→2 cloner saturates
  fidelity **F = 5/6 = 0.8333 per copy, equally for every input state** (universality), and
  that the ONLY way to exceed 5/6 on some basis is a **basis-reading cheat that is detectably
  below 5/6 on the conjugate basis** — universality is the certificate no cheat can forge.
  Proven-optimal law (Bužek–Hillery 1996; Bruss et al.; Gisin–Massar). Exact-law class
  (F96/F101 style), plus the informative-null "beat-the-bound arm pre-registered to FAIL".
- **What this is NOT**: not an advantage (nothing is beaten — a *limit* is hit); not a
  no-cloning "proof" (no-cloning is a theorem; we certify the *quantitative* ceiling it
  licenses). Prior art plain: the UQCM is textbook and demonstrated on several platforms; the
  contribution is the frozen-court, executed-cheat-arm, universality-flatness certification.
- **The cloner circuit is not taken from memory**: `exp131_cloning_sim.py` NUMERICALLY
  optimizes the ancilla-prep angles (objective = worst-case mean copy fidelity over 6 axis
  states) and the optimum lands on the universal 5/6 cloner (verified: mean 0.83332, cross-
  state variance 2.2×10⁻⁸, copies 0.836/0.830 — intrinsic asymmetry 0.006, far below hardware
  noise). Frozen prep angles: **[0.76101, 0.22136, 0.26021, 0.80229]** (Ry a q1, Ry b q2,
  CX(1,2), Ry c q1, Ry d q2). Cloning network: CX(0,1) CX(0,2) CX(1,0) CX(2,0).

## Apparatus

3 qubits, input at a center node (q0 = input/copy-A, q1 = blank/copy-B, q2 = ancilla),
calibration-gated. Per input state, both copies are rotated into the input basis and measured
→ copy fidelity = P(match). Six axis inputs {|0⟩,|1⟩,|+⟩,|−⟩,|+i⟩,|−i⟩} span Z/X/Y bases.
Two arms: **optimal** (the certified cloner) and **cheat** (trivial CX(0,1) copy). 12 payload
circuits + 2 prep/readout sentinels, 8000 shots each (~112k), shuffled (seed 4670), co-batched.

## Frozen gates

| Gate | Statement | PASS condition |
|---|---|---|
| **W1_UNIVERSAL** (primary) | optimal cloner is FLAT across bases near the ceiling, and does not EXCEED it | per-basis spread (max−min) < 0.05, AND max-basis F ≤ 5/6 + 5·SE |
| **W2_NO_UNIVERSAL_BEAT** (the teeth; cheat pre-registered to FAIL) | the cheat cannot beat 5/6 on all bases — it pays on the conjugate | cheat min-over-bases F < 5/6 − 5·SE |
| **W3_CHEAT_TELL** | the basis-reading signature distinguishes cheat from optimal | cheat basis-spread > 0.30 AND optimal basis-spread < 0.05 |
| **W4_CEILING_PROXIMITY** | the optimal cloner is a *real* ~5/6 cloner, not noise-degraded to garbage | optimal mean F > 5/6 − 0.06 (noise budget) |
| **G_SENT** | prep/readout integrity | both sentinels ≥ 0.95 |

**Figures of merit**: optimal cloner per-basis fidelities (flatness + proximity to 5/6); cheat
Z-vs-conjugate gap. **Fake preview** (FakeMarrakesh): optimal Z/X/Y = 0.8187/0.8172/0.8191
(spread 0.0019, ~0.016 below ceiling from noise, never exceeds); cheat Z/X/Y =
0.9901/0.5003/0.4996 (beats 5/6 on Z, min 0.50 ≪ ceiling). Noiseless design check PASS.

**Pre-filed predictions**: W1 HIT conf 0.90 (flatness is noise-robust); W2 HIT conf 0.95 (cheat
X/Y ≈ 0.5 by construction); W3 HIT conf 0.95; W4 HIT conf 0.85 (rests on optimal F staying
above 0.773 — fake 0.817, comfortable); G_SENT conf 0.92. Fake likely ~1–2pp optimistic per
the crossover curve.

**NO-TEST conditions**: sentinel failure → window NO-TEST; transpile audit — the optimal-arm
2q count must match the scan-frozen value, cheat arm exactly 1 CX → abort on drift; if the
optimal cloner EXCEEDS 5/6 universally (all bases > 5/6 + 5·SE) → apparatus audit (a genuine
universal beat would break the theorem — almost certainly a grading/calibration error).

## Relation to the campaign

Adds **no-cloning** to the certified-limits ledger alongside the no-go games (Bell/causal-
order/contextuality). The campaign now certifies both what quantum resources can *exceed*
(the advantage arc) and what they *cannot* (this). The cheat-arm-pre-registered-to-fail is the
same informative-null discipline as F90/F93/F95's honest misses — here weaponized as a
detector: the way to "beat" the ceiling is exactly the way to get caught.
