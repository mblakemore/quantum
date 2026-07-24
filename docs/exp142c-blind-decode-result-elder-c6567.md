# Exp142c mixed-state F119 re-fly — BLIND DECODE RESULT (Elder C6567, grader seat)

**Verdict: NO-WIN. The hardware delivery carries no recoverable Pauli signal — the flown state is
consistent with the maximally-mixed I/2ⁿ at every rung. Caught BLIND (before Ember's P reveal).**

Frozen estimator: `experiments/exp142c_decode_estimator_elder_c6567.py` @ commit `d687677`
(committed PRE-REVEAL — race-arc discipline held). Pulled flown outcomes from the DONE jobs in
`results/exp142c_n{4,6,8}_manifest.json` (n=4 job `d9herrjsbqfc73epuun0`, +3 jobs n=6, +6 jobs n=8).

## What the P-blind decode found

| rung | copies-to-stop (median) | frozen C1 benchmark | s_hat identified | censor frac |
|------|------------------------|---------------------|------------------|-------------|
| n=4  | 374                    | 408                 | none (5% false)  | 0.95        |
| n=6  | 3815                   | 4482                | **none**         | 1.00        |
| n=8  | 38502                  | 55589               | **none**         | 1.00        |

The copies-to-stop *track the full-schedule walk* because the true basis is ELIMINATED along with
every wrong basis — the SPRT never confirms any basis (LLR never reaches A). That is the fingerprint
of "no basis is deterministic," i.e. ⟨A⟩≈0 for **all** A.

## Three independent checks — all agree it is genuine signal absence, not a decode bug

1. **Exhaustive per-basis scan (n=4, all 81 bases).** Even-parity rate = 0.5 ± noise everywhere.
   Most-deterministic basis: even-rate 0.446 (|dev| 0.054); median over 81 bases 0.506;
   max|⟨A⟩| ≤ 0.11. No deterministic basis exists in the data.

2. **The null is POWERED, not under-powered.** 135 shots/basis (M×C) would render a true ⟨P⟩=1 as a
   ~7σ even-rate spike (→1.0). Observed max deviation 0.054 ≈ 1.3σ — *below* the expected max of 81
   half-normals (~0.125). A real signal would be blinding; its total absence is a genuine powered
   null (⟨P⟩ ≤ ~0.1, not merely attenuated). [feedback: under-powered-null-≠-absence — this null IS
   powered.]

3. **Read-path verified in noiseless sim.** Built `flight_template` for a *made-up* full-weight
   P="XYZX" (stays blind to Ember's sealed P), simulated the exact basis rows, read via the identical
   popcount-parity path: even-rate **1.000** at the true P, 0.48 at wrong bases. My decode read is
   correct → the hardware data lost the signal, the reader did not.

## Where the signal died (sim-exact, hardware-washed)

- `compiled_G1` verified `parity_at_P=1.0, worst_off=0.0` on the LOGICAL circuit; I separately
  verified the mixture survives transpile at opt=1 AND opt=3. So the delivery is **exact in ideal
  simulation**, including post-transpile.
- The prep's signal (the P term of (I+P)/2ⁿ) is a **global n-body coherence** — the single most
  fragile object under 2-qubit-gate noise. The prep uses an ancilla-trace Bell layer + a CX ladder
  that targets qubit 0 from all others (`for j in 1..n-1: cx(j,0)`) + U_C. That all-to-qubit-0
  ladder has no native connectivity → the transpiler routes it into SWAP chains → accumulated
  entangling-gate error collapses ⟨P⟩ → 0. Readout is fine (q_n≈0.003); the killer is prep entangling
  depth/routing, and it already fully washes at **n=4** (worsening monotonically to n=8, as an
  entangling-depth explanation predicts).

## Consequence for the arc

- Both meter arms need a signal: the two-copy Q meter and the C1 SPRT decoder BOTH find nothing.
  **No advantage can be certified from this flight.** This is the delivery-artifact failure mode the
  F119 discipline exists to catch — surfaced blind, on hardware, not hand-waved.
- The remedy is NOT a decoder change (decoder is verified) — it is a **low-depth, connectivity-aware
  mixed-state prep** that avoids the all-to-qubit-0 CX ladder + long SWAP routing (e.g. a linear-chain
  CX cascade matched to the device coupling map, or a prep that localizes the coherence). Until the
  prep delivers ⟨P⟩≈1 on hardware (re-run `compiled_G1`-style check but MEASURED on-device on a known
  test P first), the flight cannot grade an advantage.

## POST-REVEAL routing forensics — the washout was mostly a LAYOUT OWN-GOAL, not fundamental fragility

Measured ⟨P⟩ at the revealed true bases (blind phase over): n=4 (ZYYZ) 0.096, n=6 (YYZZXZ) 0.069,
n=8 (YYZYZXYX) 0.219 — all at the noise floor, non-monotonic → the washed data is too
noise-dominated to fit a reliable ⟨P⟩=f^depth law (my first fit returned f=1.0018>1, a bug-signal I
discarded; do not use it). The RELIABLE lever is the transpile 2q-gate count (deterministic):

| n | logical 2q | as-flown routed (readout-layout, opt1) | conn-aware routed (opt3) |
|---|-----------|----------------------------------------|--------------------------|
| 4 | 6         | **213 (36×)**                          | **6 (1.0×)**             |
| 6 | 10        | 358                                    | 17 (1.7×)                |
| 8 | 14        | 362                                    | 38 (2.7×)                |

**Root cause, sharpened:** the flight forced `initial_layout` = the 7 LOWEST-READOUT qubits (chosen
for q_n, connectivity-blind — scattered across the chip) then opt=1 routed the star-ladder through
~207 SWAPs at n=4. A connectivity-aware transpile collapses the SAME logical prep 213→6 at n=4 — the
n=4 signal would have SURVIVED (⟨P⟩≈0.99^6≈0.94). So the as-flown result OVER-states the fragility:
~10–36× of the depth was an avoidable layout own-goal, not the prep.

**But the star-ladder is genuinely SWAP-bound at n≥5:** `cx(j,0) ∀j` needs qubit-0 degree n−1, while
heavy-hex maxes at degree 3 — so even best-case relayout leaves 17/38 routed 2q at n=6/8. At a
conservative f≈0.99/CZ that predicts ⟨P⟩(n=8)≈0.99^38≈**0.68 — borderline, just misses the 0.7 gate.**

**Consequence for path (b) vs (c):** the (b)-vs-(c) decision must compare a *connectivity-aware*
mixed prep against pure-state — NOT the as-flown star-ladder (which conflated prep-depth with a
layout own-goal). A LINEAR/tree entangler that keeps routed≈logical≈2(n−1)=14 at n=8 predicts
⟨P⟩≈0.99^14≈**0.87 (clears 0.7), while RETAINING the ~20× job savings.** So path (b) is NOT dead —
it needs both a connectivity-aware layout AND a linear-prep redesign (not just relayout). Path (c)
pure-state stays the fidelity-guaranteed fallback (0 entangling gates, ⟨P⟩≈0.976, 215-job cost).
The f≈0.99 is an ESTIMATE (washed data couldn't fit it) — the on-device pre-seal ⟨P⟩ gate MEASURES
it and is authoritative; my prediction for the linear prep at n=8 is ~0.87, and that is the number
to test before defaulting to (c)'s job cost.

## Attack / independence arms (cond 3 / cond 4) — vacuous here, reported for completeness

Determinism-attack score 0.26/0.23/0.17 and lag-1 shot-correlation ≈ 0 (−0.02/−0.006/0.0001). These
are consistent with i.i.d. fair coins (exactly what I/2ⁿ delivers) — the attack finds nothing to
exploit, but only because there is no signal at all, so cond 3/4 are **not meaningfully testable on
this data** (a null delivery trivially defeats the determinism attack). They become graded conditions
only once a prep that actually delivers ⟨P⟩≈1 is flown.
