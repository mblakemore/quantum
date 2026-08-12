# H13 Cell 8 Rung 2 — G0 clause 1: the SDP ceiling **re-derived in-code**, not cited

**Author**: Whisper (DC15W), C5060 · **Board**: #72 · **Creator GO**: general#10566 ("item 2 go")
**Spec**: `docs/h13-cell8-switch-under-oath-spec-whisper-c5053.md` — seats clause assigns the
in-code ceiling re-derivation and the scoreboard framing to this seat. **QPU spent: none.**
**Artifact**: `results/causal_game_sdp_qij.json`, regenerated at freeze by
`scripts/causal_game_sdp.py`.

## Why this document exists

Rung 2 is the arc's **second advantage-class object**, and its spec requires the causally-separable
ceiling to be **re-derived in-code at freeze, never cited from F82** (the F87 discipline: a bound
that enters a claim by quotation is a bound nobody checked). This is that derivation, run now,
before any seal or flight.

## The number

```
dual (minimax)     0.8690277398739925
primal at q*       0.8690277186779367
PRIMAL–DUAL GAP    2.12e-08
deviation vs the registered 0.8690    2.77e-05
```

**Ceiling = 0.869028.** Both of the script's own paper gates pass: Haar/continuous witness
0.928813 against Araújo Eq. (84) 0.9288, finite 10-set 0.869028 against Eq. (H3) 0.8690.

## ⚠️ The solver status, stated rather than glossed

**The finite-set solve returns `optimal_inaccurate`**, not clean `optimal` — CVXPY raises *"Solution
may be inaccurate."* The Haar solve returns `optimal`.

**It does not move the number, and here is why rather than an assurance**: the primal evaluated at
the recovered q\* agrees with the dual minimax value to **2.12×10⁻⁸**. Primal and dual bracket the
true optimum from opposite sides, so a gap that small certifies the value independently of the
solver's own confidence flag. The warning is about internal tolerance; the answer is bracketed.

**This is recorded because a claim that rests on an SDP inherits the SDP's status**, and a future
reader finding `optimal_inaccurate` in the log without this paragraph would be right to stop.

## Independent validations in the same run

| Check | Value | Meaning |
|---|---|---|
| V1 process-vs-circuit max error | **2.2e-16** | the process matrix and the circuit agree to machine precision |
| V4 switch under Haar | **1.000000000000** | the switch wins with certainty in the ideal case, as theory requires |
| V5 Pauli-only subset | **1.000000000** | the Pauli sub-game saturates — the consistency check Elder's ladder predicts |
| q\* class weights | **0.6165 / 0.3835** | recovered independently, matching the sampled priors |

The q\* distribution matters on its own: the paper omitted it, and it was recovered in-house at
C4524. The ceiling is only meaningful **against the distribution that achieves it**, so both are
frozen here together.

## What this clause does and does not clear

**Cleared**: G0 clause 1 — the ceiling is re-derived in-code, with its solver status and its
primal–dual bracket on the record.

**Not cleared, and not by this document**: the mixture-arm bands (frozen from F73 + haircut
envelope), and the **billing-currency preflight class** — the spec is explicit that Rung 2 either
gets that class adopted by the court or **waits**. Both arms must be counted in the same query
currency (controlled-calls, identically counted), and until that class exists in
`attack_preflight.py` this rung cannot claim.

**Nor does re-running our own solver make the derivation independent of us.** It removes the
citation, not the shared authorship: if the 2015-vintage formulation encoded in this script is
wrong, re-running it reproduces the error faithfully. What it *is* checked against — the two
published paper values, the primal–dual bracket, and four internal consistency gates — is stated
above so a reader can see the shape of the assurance rather than infer it.
