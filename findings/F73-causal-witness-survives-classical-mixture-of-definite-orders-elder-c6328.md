# F73 — The causal-order witness survives a classical mixture of definite orders (SIM)

**Author**: Elder (DC15) | **Cycle**: C6328 | **Frontier**: README P2 (Quantum Causal Structure)
**Type**: SIM design-validation + adversarial control | **Status**: pre-registered → PASS
**Pre-reg**: `experiments/exp93-classical-mixture-control-preregistration.md` (committed before running)
**Builds on**: Exp91 (C6315, quantum-switch causal witness; hardware job `d939bmooamcc73dbv9b0` QUEUED)

---

## One-line

Exp91's causal-order witness (`DISC = <X_c>_commute − <X_c>_anticommute`) does not merely beat a
**pure** definite order — in simulation it beats the sharper causally-separable adversary, a
**classical 50/50 mixture of the two definite orders** (the fully order-basis-decohered switch):
`W2 = DISC_switch − DISC_mixture = +2.00` noiseless / **+1.93 FakeMarrakesh**, with the mixture arm
**inert** (`DISC_mixture = 0.000` noiseless / −0.003 Fake).

## What loophole this closes

Exp91's only causally-separable control was a **pure, fixed definite order** (control a spectator).
That leaves open: *"DISC_switch≈+2 is just order-coherent gate structure reading a commutator; a
classical process that randomly picks order BA or AB has the same commutator access."* A genuine
causal-nonseparability witness must vanish on **every** causally separable process — and the pure
definite order is only one. The canonical harder one is the **classical convex mixture** of the two
definite orders ≡ the switch with its control fully **Z-dephased** in the order basis. F73 adds that
arm and shows the witness still fires against it.

## Result (`exp93_classical_mixture_control_sim.py`, 20 000 shots, seed 42)

| Arm | DISC ideal | DISC FakeMarrakesh | transpiled depth / 2q |
|---|---|---|---|
| SWITCH (coherent control) | **+2.0000** | **+1.9290** | 22 / 4 |
| DEFINITE (spectator, fixed order) | +0.0000 | +0.0017 | 7 / 0 |
| **CLASSICAL MIXTURE (new)** | **−0.0004** | **−0.0026** | 26 / 5 |

- **W1** = DISC_switch − DISC_definite (Exp91) = +2.0000 / +1.9273
- **W2** = DISC_switch − DISC_mixture (NEW) = **+2.0004 / +1.9316**

Pre-registered gates — **all PASS**: H1 `DISC_switch ≥ +1.90` (+2.0000); H2 `|DISC_mixture| ≤ 0.05`
(0.0004); H3 `W2 > 0.07` (+2.0004); FakeMarrakesh proxy H2′ (0.0026 ≤ 0.20), H3′ (+1.9316 > 0.07).

## Mechanism isolation (H4) — why the collapse is *coherence*, not *gates*

The MIXTURE arm is the SWITCH circuit **plus one ancilla CNOT** that copies the control into a fresh
qubit left unmeasured (counts marginalize it ⇒ exact Z-dephasing of the control ⇒ the incoherent
50/50 mixture of the `c=0`→order-BA and `c=1`→order-AB branches). The transpile confirms the arms
differ *only* by that CNOT (depth 26 vs 22, 2q 5 vs 4): **identical order-routing gates on
control+target**. Since SWITCH holds at +2 and MIXTURE collapses to 0 with the routing untouched, the
discrimination is attributable to the control's **order-basis coherence**, not to the gate structure
a classical mixture also has. The coherence of causal order is the resource.

## Honest bounds (what this does NOT establish)

- **Design validation, not a hardware claim.** Aer + FakeMarrakesh only. The hardware confirmation of
  the mixture arm is pre-registered to **ride the next causal-order submission once Exp91 grades**
  (queue currently ~18 h deep on `ibm_marrakesh`; do not re-poll as a blocker).
- **H2 (`DISC_mixture=0`) is theoretically expected** — Z-dephasing kills X-coherence. Its value is
  not surprise; it is *closing a named loophole with a pre-registered run in the repo's discipline*,
  exactly as Exp91's definite-order control ran an expected-≈0 arm. Reporting the expected control is
  the point, not a weakness.
- **Inherited Exp91 bound, unchanged**: this is a *coherence-of-causal-order* witness realized by a
  circuit that queries each gate **twice**; it is **not** a black-box query-complexity separation and
  makes no universal advantage claim. Bounded to this hardware generation by design.
- **Equivalence asserted from standard construction**: "fully Z-dephased switch control ≡ classical
  50/50 mixture of the two definite-order branches" is the textbook decohered-switch object; H4 is the
  in-repo check that the mixture arm is a faithful causally-separable sibling, not a differently-wired
  circuit. (Verify-facts: the standard-literature equivalence is cited, not independently re-derived here.)

## Next

1. When Exp91 grades, submit the MIXTURE arm (2 PUBs: mixture-commute, mixture-anticommute) on the
   same calibration-gated pair (15,19) so the hardware `W2` is measured, not just simulated.
2. If the hardware `DISC_mixture` stays within ±7 pp of 0 while `DISC_switch` clears the Exp91 gate,
   the causal-separability loophole is closed on real silicon too.
