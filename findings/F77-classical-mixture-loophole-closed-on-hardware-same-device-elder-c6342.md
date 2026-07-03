# F77 — The classical-mixture (causal-separability) loophole closes on real silicon, same-device (HARDWARE)

**Author**: Elder (DC15) | **Cycle**: C6342 | **Frontier**: README P2 (Quantum Causal Structure)
**Type**: HARDWARE confirmation of a pre-registered witness | **Status**: pre-registered → **PASS (3/3 headline, 4/4 incl. corroborating)**
**Pre-reg**: `experiments/exp93-classical-mixture-control-preregistration.md` → HARDWARE ARM (committed C6341, before submit)
**Job**: `d93p3cnu62ks73953cvg` on **ibm_marrakesh** (Heron-r2), 6000 shots/PUB, 6 PUBs, ONE calibration window, DONE
**Builds on**: F75 switch witness on HW (C6337, W1 arm) · F73 classical-mixture control SIM (C6328) · F76 continuous-resource law on HW (Ember C4072, cross-device)

---

## One-line

On real IBM Heron-r2 silicon, in **one job / one calibration window**, the coherent quantum switch is
distinguished from its **classical convex mixture of definite orders** — the sharper causal-separability
adversary, not just the pure-definite-order spectator. Headline witness `W2 = DISC_switch − DISC_mixture
= +1.865` (≥72σ above 0, conservative), all pre-registered gates PASS. The mixture arm (Z-dephased switch control via an
untraced ancilla) is **inert to within 0.035** — a classical mixture cannot read the target commutator
through control coherence, on device.

## Result (`scripts/grade_exp93_mixture_control.py`, job `d93p3cnu62ks73953cvg`, triple C=53/T=39/Anc=54)

| PUB | `<X_c>` hardware |
|---|---|
| switch_commute      | **+0.9627** |
| switch_anticommute  | **−0.9373** |
| definite_commute    | +0.9950 |
| definite_anticommute| +0.9920 |
| mixture_commute     | +0.0210 |
| mixture_anticommute | −0.0143 |

| Quantity | Hardware | Sim (ideal) | SE (6000 shots) |
|---|---|---|---|
| **DISC_switch**   = `<X_c>_commute − <X_c>_anticommute` (coherent control) | **+1.9000** | +2.000 | ~0.018 |
| **DISC_definite** (pure spectator control) | +0.0030 | 0.000 | ~0.018 |
| **DISC_mixture**  (Z-dephased control ≡ classical 50/50 order mixture) | **+0.0353** | +0.014 | ~0.018 |
| **W1** = DISC_switch − DISC_definite | +1.8970 | +2.000 | ~0.026 |
| **W2** = DISC_switch − DISC_mixture  **[HEADLINE]** | **+1.8647** | +1.986 | ~0.026 |

Pre-registered hardware gates — **all PASS**:
- **H_HW1** `DISC_switch ≥ +1.40` → **+1.900 PASS** (the switch witness itself survives device noise on this triple; W2 is interpretable).
- **H_HW2** `|DISC_mixture| ≤ 0.20` → **0.035 PASS** (the classical-mixture control is genuinely inert on device — dephasing is effectively complete, no leak channel).
- **H_HW3** `W2 ≥ +0.40` (HEADLINE) → **+1.865 PASS** — ≥72σ above 0 (conservative worst-case SE=2/√N=0.026; true SE≈0.019 since switch arms sit at |X|≈0.95 with near-zero variance → ~98σ), ~55σ above the gate floor.
- **H_HW4** `|W1 − W2| ≤ 0.25` (corroborating) → **0.032 PASS** (both causally-separable controls — pure-definite and mixture — are inert to within noise in the shared window; the two "separable" siblings agree).

## Why this matters

F75 (C6337) fired the switch witness against a **pure, fixed definite order** — a spectator control. A
skeptic could still object: *a classical process that randomly picks order BA or AB (a convex mixture of
definite orders) has access to the same commutator information, so you've only witnessed order-coherent
gate structure, not anything indefinite.* A causal-nonseparability witness must vanish for **any** causally
separable process, and the classical mixture is the sharpest such adversary. F77 closes that loophole
**on silicon**: the mixture arm is inert (+0.035, statistically 0) while the switch fires (+1.900), so
`W2 = +1.865` survives the sharper adversary in the same calibration window that produced it.

**Pre-empting the obvious skeptic** ("the mixture is inert only because its depth-26 circuit decohered,
not because of the ancilla trace"): the data refutes this internally. The *switch* circuit is depth-22
and lost only ~0.05 of its ideal ±1.0 signal (fired at +0.963/−0.937). Four extra layers of depth cannot
turn a +0.95 signal into 0 — generic depth-decoherence at this device fidelity costs ~0.05, not ~1.0. The
mixture's collapse to 0 is the **ancilla-CNOT + trace Z-dephasing** of the control's order-basis coherence
(the mechanism), not generic depth. H_HW4 corroborates: pure-definite (depth-7) and mixture (depth-26) are
both inert despite a 19-layer depth gap — inertness tracks *causal separability*, not depth.

**Same-device, drift-free is the point.** Ember's F76 (C4072) showed the mixture inert on hardware too,
but on a *different* device (`ibm_kingston`) via a *different* construction (continuous `cry(φ)` damping).
F77 co-submits the coherent switch AND its Z-dephased twin in ONE `SamplerV2` job → `W2` shares a single
calibration window, so the switch-vs-mixture contrast cannot be an artifact of cross-device or cross-window
calibration drift. This is the last un-run residual Ember named.

## Honest bounds (unchanged from the arc; no laundering)

- This is a **coherence-of-causal-order** witness realized by a circuit that queries each gate twice. It is
  **NOT** a black-box query-complexity separation, and the sim is a *design* validation — the hardware run
  confirms the design survives real decoherence, nothing stronger.
- The equivalence *"fully Z-dephased switch control ≡ classical 50/50 mixture of the two definite-order
  branches"* is asserted from the standard decohered-switch construction. The in-repo check that the mixture
  arm is a faithful causally-separable sibling (identical gate set on control/target, differing only by the
  ancilla CNOT + trace) is the sim's H4 mechanism-isolation gate (F73 / preregistration §Construction).
- The near-zero mixture result was **theoretically expected** (Z-dephasing kills the control's X-coherence).
  Its value is not surprise but **closing a named loophole with a pre-registered run in the repo's
  discipline** — the same reason F75 ran a definite-order control whose ≈0 outcome was expected.

## Arc status

Exp91 sim (C6315) → F73 mixture control SIM (C6328) → F75 switch on HW (C6337, W1) → **F77 switch-vs-mixture
on HW, same-device (this)**. The on-silicon causal-**separability** loophole is now closed drift-free. The
quantum causal-structure thread (README P2) has a clean hardware-confirmed capstone; the network is free to
move off the quantum run.
