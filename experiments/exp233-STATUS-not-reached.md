# Exp233 — THE HARD-REGIME CROSSOVER: NOT REACHED (honest) — bounding where FT pays

**Whisper C4914, 2026-07-20. Job `d9eqnbcinv1c73aqi9c0`, `ibm_fez`, 10 circuits, 8000 shots.
Substrate `claude-opus-4-8`. Prereg frozen pre-submit.** The honest complement to Exp231 — flown as
the "FT" half of the Creator's second Both/And.

## Verdict

**REGISTERED VERDICT (G1 trend): MISS. G2 hard crossover: NOT REACHED — and that is the result.**
When the logical gate is genuinely EXPENSIVE (in-block CNOT forced to 3 real physical CX, so logical
2q = 9→51 vs bare 4→32), the [[4,2,2]] shield's distance-2 detection does **not** overcome the
encoding overhead: the logical arm falls *behind* bare and the gap *widens* with depth. This bounds
the Exp231 crossover precisely to the cheap-Clifford regime.

## The curve — the crossover running backward

| D | F_logical (accept) | F_bare | Δ = F_log − F_bare |
|---|---|---|---|
| 1 | 0.988 (0.94) | 0.983 | +0.005 |
| 2 | 0.975 (0.92) | 0.978 | −0.003 |
| 4 | 0.958 (0.88) | 0.973 | −0.015 |
| 6 | 0.942 (0.83) | 0.963 | −0.022 |
| 8 | 0.912 (0.80) | 0.950 | **−0.038** |

Where Exp231 (cheap in-block CZ, logical 2q constant) had Δ climb from −0.002 to **+0.040**, here
(expensive SWAP-based CNOT, logical 2q growing) Δ *falls* from +0.005 to **−0.038**, and the shield
acceptance drops faster (0.94 → 0.80) as more real 2q gates trigger detected errors. The overhead
outruns the detection.

## What this establishes (with Exp231)

The two flights together answer the frontier's linchpin question — *where does error-corrected beat
bare?* — as a genuine **characterization**, not a slogan:

- **Cheap-Clifford regime (Exp231):** the code makes the gates free (in-block CZ = 0 physical 2q),
  so logical carries only the encoding prep + detection. **Crossover at D≈2, advantage grows to
  +0.040.** FT pays, early.
- **Expensive-gate regime (Exp233):** the logical gate costs real 2q gates (~1.5× bare), so logical
  accumulates more physical error than the distance-2 code can detect away. **Crossover not reached;
  Δ goes negative and widens.** FT does not pay here, at these depths, on this hardware.

This is the honest map: on the [[4,2,2]] code, fault tolerance pays exactly when the computation is
dominated by the code's *cheap* transversal/in-block Cliffords, and stops paying when it is
dominated by *expensive* (non-transversal-class) logical gates. A distance-2 code detects one error;
tripling the physical 2q count per logical gate simply produces more than one error per accepted
shot at depth. The path to the expensive-gate crossover is a higher-distance code (d≥3, actual
correction), not d=2 detection — a concrete, valuable pointer.

## Scope (honest)

2 logical qubits vs 2 physical; expensive logical gate = in-block CNOT forced to 3 real CX with
barriers (defeating the transpiler's virtual-SWAP — a trap caught pre-flight, the same class as
Exp231's mirror-cancellation). Mirror-circuit fidelity, ZZZZ postselection, full depth sweep. The
registered G1 (Δ non-decreasing) missed because the hard-regime trend genuinely runs the other way —
that opposite trend *is* the finding, kept without spin.

## Line

**We took the crossover that worked and made it work for its living: instead of the code's free
gates we forced it to spend three real entangling gates for every one the bare qubit paid, and asked
if catching errors could still win. It could not — the coded qubit slipped behind at depth two and
kept falling, minus thirty-eight thousandths by depth eight, while its acceptance bled away. So now
we know the shape of the answer and not just its sign: distance-two error DETECTION pays when the
gates are cheap and loses when they are dear, and the road to fault tolerance for the expensive
gates runs through a bigger code that CORRECTS, not merely one that watches.**
