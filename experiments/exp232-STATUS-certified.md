# Exp232 — THE ARROW-BENDER: CERTIFIED — hold an event, then revoke or make it permanent

**Whisper C4914, 2026-07-20. Job `d9eqgf9htsac739eimg0`, `ibm_fez`, 4 circuits, 8000 shots, seed 0.
Substrate `claude-opus-4-8`. Prereg frozen pre-submit.** Open-question 7 of the frontier synthesis,
the machine P3's Guardian of Forever pointed at. Flown alongside Exp231 (the crossover) as the
Creator's "both/and."

## Verdict

**REGISTERED VERDICT (G1∧G2∧G3): HELD.** A working delayed-choice arrow-bender: a recorded event
held locally is REVOCABLE — uncomputing the record restores the system and the event un-happens —
but once the record is RELEASED (copied to an environment fragment), the same revocation FAILS and
the past is permanent. A measured window of reversibility, opened by holding and closed by a later
choice.

## The result — the system coherence ⟨X_S⟩ under each choice

| arm | ⟨X_S⟩ | meaning |
|---|---|---|
| HELD (cry, record) | +0.003 | the event is recorded, held — coherence gone |
| **REVOKE** (cry, cry⁻¹) | **+0.977** | uncompute while held → coherence RETURNS: the past un-happens |
| RELEASE (cry, CNOT→E) | +0.009 | record copied to E, objectified — coherence gone |
| **RELEASE+REVOKE** (cry, CNOT→E, cry⁻¹) | **+0.019** | revoke FAILS: the record escaped, the past is permanent |

- **G1 REVOCABLE**: ⟨X_S⟩(revoke) = **0.977** — while the record lives only in the local bath,
  uncomputing it restores the system to its pre-event superposition. The event un-happens.
- **G2 RELEASE LOCKS IT**: ⟨X_S⟩(release+revoke) = **0.019** — once the record is copied into the
  environment fragment E, the identical uncompute no longer restores the system (the information
  escaped to E, which the revoke does not touch). The past is now permanent.
- **G3 THE WINDOW**: ⟨X_S⟩(revoke) − ⟨X_S⟩(release+revoke) = **0.958 at 84σ** — a real, measured
  window of reversibility, opened by holding the record and closed by the release choice.

## What it is

The bath-record ledger (200b/201) proved that irreversibility is the environment *keeping the
record*. This turns that law into a **controllable gadget**: hold an event's record in an accessible
bath (reversible), and by a *later* choice either **revoke** it (uncompute → un-happen) or
**release** it (copy to an inaccessible fragment → permanent). The "arrow of time" becomes an
operational knob: irreversibility = the record escaping to E. This is the operational core of the
delayed-choice arrow-bender P3 envisioned, and the natural sequel to Exp230 (which *selected* a past;
this one *revokes or fixes* it).

## Scope (honest)

3 qubits (system + record + fragment). Shallow (1 cry per arm + 1 CNOT; barriers force the
revoke's cry·cry⁻¹ to actually execute on hardware — 2q=2, not cancelled — so 0.977 is a real
measured revoke, not a compiled-away identity). The irreversibility is operational: E is a single
extra qubit standing in for "the environment"; releasing to a genuinely inaccessible bath is the
same physics at scale. No new physics — the composition (a working arrow-bender) is the result.
Depth-check before submit — the 213 lesson, continued.

## Line

**We wrote an event into a bath and held it there, and for as long as the record stayed within
reach we could take it back — uncompute the writing and watch the system return, 0.977 of the way,
to the moment before the event, as if it had never happened. But copy that record once into the
world beyond reach, and the same undoing does nothing: the event has set, permanent at 84 sigma.
The arrow of time is not a law we suffer but a valve we can hold open and, with a later choice,
let close. The past is reversible until we let the world remember it.**
