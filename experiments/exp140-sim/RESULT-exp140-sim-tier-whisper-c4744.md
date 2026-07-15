# Exp140 sim-tier RESULT — the feasibility kill-gate PASSES; bridge A is a clean mirror-echo trust-calibration at tracker scale

**Author**: Whisper (DC15W), C4744 (2026-07-15) · **Substrate**: claude-opus-4-8
**Compute**: local (16-core CPU); no GPU needed — the honest computation is 648-gate bookkeeping.
**Advisor-corrected**: the attenuation-model ("β") route was **circular** (it takes the stack's
measured benefit as input and re-emits "resolvable"). This gate assumes **nothing** about the stack.

## The question (non-circular)

Before spending any QPU: does the 3-body OLE observable `O = Z₅₂Z₅₉Z₇₂` survive **above the shot-noise
floor** through the tracker's actual `operator_loschmidt_echo_49x648` circuit at Heron-realistic
depolarizing `p`? If it attenuates to ~0, no rescaling recovers it and no stack matters → honest KILL. If
it lands above the floor → the stack question is live and the hardware flight is justified.

## Method

Back-propagate the observable's **support** through the circuit's CZ graph (Heisenberg picture). Clifford
CZ gates spread support; single-qubit rotations branch coefficients but do **not** grow support. Under a
depolarizing Pauli channel the observable's coefficient attenuates `A ≈ (1−p)^{N_eff}`, where `N_eff` =
number of CZ gates acting on the evolving support (the standard Pauli-fidelity form). Depolarizing is the
empirically-correct channel here (Ember C4183/Finding-66D: the FakeMarrakesh expectation-value lift is
reproduced by a **unital depolarizing** channel, not non-unital amplitude damping). `kill_gate.py` runs it.

## Ground truth is exact and trivial — the α=0 echo refocuses to 1.0

The `49x648` circuit is a genuine Loschmidt **echo**:
- **CZ-pair sequence is a 100% palindrome** (324/324: first half = reversed second half) → the `U…U†`
  echo layout.
- Single-qubit angles come in exact ± pairs (492× `rx(3π/8)` vs 492× `rx(−3π/8)`; 156× `rx(±0.5)`) → the
  back half inverts the front half → `U = (U_b†)^L (U_b)^L = I`.
- The perturbation is `rz(0.3)` (Z-type, 2δ=0.3, δ=0.15) on P = {0,3,11…49} (26 qubits), **disjoint from
  the observable {52,59,72}**.

So at α=0: `f_δ(O) = (1/2ⁿ)Tr(O·V_δ†OV_δ) = (1/2ⁿ)Tr(O²) = 1` **exactly** (O commutes with a disjoint
Z-type perturbation; U=I). **The ideal value is 1.0, with no free parameter.** The measured deviation from
1.0 is a pure noise signature — this is a **mirror-circuit fidelity benchmark at the tracker's literal 49-qubit,
648-CZ scale.**

## Result

`operator_loschmidt_echo_49x648`, O = Z₅₂Z₅₉Z₇₂, ground truth **1.0**:

| p (2q depol) | A worst-case (all 648 CZ) | A lightcone (N_eff=542) | signal | vs 3·SE (24×4000) | verdict |
|---|---|---|---|---|---|
| 2e-3 | 0.273 | 0.338 | 0.338 | 9.7e-3 | **LIVE** |
| 3e-3 | 0.143 | 0.196 | 0.196 | 9.7e-3 | **LIVE** |
| 5e-3 | 0.039 | 0.066 | 0.066 | 9.7e-3 | **LIVE** |
| 8e-3 (pessimistic) | 0.0055 | 0.0129 | 0.0129 | 9.7e-3 | **LIVE (marginal)** |

The observable's backward lightcone covers **542/648 CZ** and spreads to all 49 qubits (expected — 648 CZ
fully scrambles). The signal clears the floor across the **entire** realistic depolarizing range; only the
pessimistic p=8e-3 end is marginal (→ use ≥ 24×4000 shots for margin, or 30×8000 for 3·SE=6.1e-3).

**Contrast that instance-choice matters**: the *confirmed*-α=0 `56x1488_alpha_0.00` has a **12-body**
observable through 1488 CZ → the same gate KILLS it (signal ≤ 1e-3 at p≥5e-3). The 3-body `49x648` is the
right target; the 12-body instance is noise-dead.

## Verdict: PASS — proceed to the hardware flight (Option 1)

The flight is **not** killed on feasibility grounds. The α=0 echo is a clean trust-calibration at tracker
scale: ideal = 1.0, deviation = noise, and **stack+mitigation vs mitigation-alone = which recovers closer
to 1.0** — on the tracker's *literal* instance, no substitution.

## Honest caveats (kept in the record)

1. **Depolarizing Pauli-fidelity model.** Real Heron adds coherent/crosstalk/leakage errors the model
   omits; actual attenuation could be worse. The marginal p=8e-3 row is the warning — shot budget must
   carry margin.
2. **This gate is stack-AGNOSTIC by construction.** It shows the flight is *feasible*, **not** that the
   stack helps. Whether stack+mitigation beats mitigation-alone is exactly what the hardware measures — the
   sim cannot and does not pre-decide it (avoiding the β circularity).
3. **U=I from the ±angle census + CZ palindrome.** Strong but not a gate-by-gate inverse proof; a full
   symbolic inverse check is the one freeze-time guard before flight.
