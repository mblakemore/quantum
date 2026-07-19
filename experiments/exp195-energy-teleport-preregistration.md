# Exp195 Pre-registration — BEAM THE POWER: quantum energy teleportation

**Cycle**: C4886 · **Backend**: ibm_fez · **Shots**: 8000 × 6 · Creator go: "fly the 3".
**Class**: Hotta's quantum energy teleportation (QET) — the most Star Trek sentence on the board.

## The protocol & question
A two-qubit Hamiltonian H = h(Z_A + Z_B) + k X_A X_B has an entangled ground state |g>. Alice
measures Z_A (outcome s = +-1), sends the classical bit to Bob. Bob applies a conditional
unitary U(s) = exp(i s theta Y_B). The QET claim: <H>_B DROPS BELOW the ground-value baseline on
Bob's side — Bob extracts energy his lab did not contain, paid for by the A-B correlations and
Alice's measurement (which INJECTED energy at A, none of which travelled). No energy crosses.
We measure the local energy change Delta E_B = <k X_A X_B + h Z_B>_after(conditioned) minus its
ground value. Optimal angle theta* from h,k analytically (selftest-verified).

## Circuits (6)
qet_XX, qet_ZB (the two energy terms, conditioned on Alice's bit via decode) ·
noLOCC_XX, noLOCC_ZB (Bob applies U with a RANDOM bit — falsifier: no extraction) ·
nomeasure_XX, nomeasure_ZB (Alice never measures — falsifier: correlation unused).
Ground state prepared by a verified 2-qubit rotation; h=1, k=1.5 (theta* ~ 0.5 rad).

## Criteria (formulas; se_E from term variances)
- **Primary**: Delta E_B < 0 at >=5 sigma (Bob's local energy drops). Band [-0.35, -0.08].
- **Falsifiers**: |Delta E_B(noLOCC)| <= 0.03 (random bit extracts nothing);
  |Delta E_B(nomeasure)| <= 0.03 (unused correlation extracts nothing).
- **Energy bookkeeping (reported)**: Alice's injected energy Delta E_A > 0 (measurement costs)
  and Delta E_A + |Delta E_B| consistent with no net free lunch (QET moves, never creates).
## Fences
Local energy accounting on a 2-qubit model Hamiltonian (not the device Hamiltonian); "energy" is
<H_model>; extraction is on the conditioned ensemble (LOCC), the standard QET form; one round;
one die. Selftest: Delta E_B = analytic optimum < 0; falsifiers ~ 0.
