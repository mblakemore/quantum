# H9 · P3 — The Prime Directive Audit: The Honest External Scoreboard

*Whisper C5001, 2026-07-25, substrate claude-fable-5. H9 program P3 (Creator: "start P0 and P3, the
$0 programs"). Every advantage-flavored column in the campaign, graded through the
[P0 claim-grade harness](../tools/claim_grade_harness.py) (the five gates the C4998-4999 arc forged).
Machine-readable: `results/h9_p3_claim_ledger.json` → `_graded.json`. This is the scoreboard an
external auditor would demand — and the one we now hold ourselves to before First Contact.*

## The reckoning (verdicts)

| Column | σ / result | Floor-type | **Verdict** |
|---|---|---|---|
| Superdense capacity / QRAC | 341σ / 110σ | theorem-over-access (Holevo, bits) | **EXTERNAL-READY** |
| Causal-order (switch) | 216.8σ, 2 chips | theorem-over-access (SDP ceiling) | **EXTERNAL-READY-FENCED** |
| CHSH / contextuality | 196σ | theorem-over-access (Tsirelson) | **EXTERNAL-READY-FENCED** |
| Heisenberg metrology | 168σ, N=5 | theorem-over-access (SQL) | **EXTERNAL-READY-FENCED** |
| BGK shallow-circuit solver (F113) | 90% valid | asymptotic-apparatus | **INSTRUMENT-NOT-ADVANTAGE** |
| F120 shot-axis code | d2q=310 blind | none (decoder instrument) | **INSTRUMENT-NOT-ADVANTAGE** |
| Cross-block coherence witness | cal-passed | none (physics witness) | **INSTRUMENT-NOT-ADVANTAGE** |
| F119 sample-complexity | Exp142/c | best-known-conditional | **NEEDS-GATE** |
| F121 runtime (decoder race) | 476× (retired) | best-known-conditional | **SUPERSEDED/RETIRED** |

## What the audit says, plainly

1. **The campaign's genuine external-facing advantages are the PROVABLE-BOUND columns.** Superdense
   is the single clean **EXTERNAL-READY** claim (Holevo bound, communication currency, no scope
   caveat). Causal-order, CHSH, and metrology are **EXTERNAL-READY-FENCED** — real theorem-beaten
   bounds, but each carries a scope fence that MUST lead any external framing: causal-order is
   device-characterized (not spatially-enforced indefinite order); CHSH is DI-quarantined (witness,
   not a device-independent certificate); metrology has task-dependent inversion (F109). The fence
   isn't a weakness — it's the difference between a claim that survives First Contact and one an
   auditor shreds.

2. **The "computational advantage" columns are honestly NOT clean advantages** — and the audit
   refuses to pretend otherwise: F120 and F113 are real INSTRUMENTS (a decoder, a theorem's
   apparatus), not speedups; F121 is SUPERSEDED by our own red-team; F119 is NEEDS-GATE (the
   pure-state re-fly must clear the pre-seal fidelity gate before it's a claim). This is the exact
   line the C4998-4999 arc drew, now enforced mechanically.

3. **Nothing graded EXTERNAL-READY that shouldn't.** The five-gate harness is deliberately
   conservative: a theorem floor alone isn't enough — the ensemble must be buildable (G2), the state
   must survive on-device (G3), and the court + red-team must have run (G4/G5). Only claims that pass
   all five reach EXTERNAL-READY(-FENCED).

## P0 self-caught a bug (the harness working on itself)

First run graded the four provable columns ADVANTAGE-INTERNAL — because the harness checked the
red-team field for `True` while the ledger wrote `"yes"` (a type mismatch), and it had no
scope-fence handling. Caught on inspection before the audit shipped, fixed (normalize G4/G5;
scope_fence → EXTERNAL-READY-FENCED). *Verify the tool before trusting its output* — the same lesson
that governs the claims now governs the instrument that grades them.

## What this positions for the rest of H9

- **P1 First Contact** targets the one NEEDS-GATE computational column (F119) — the pure-state re-fly
  behind the gate is exactly what converts NEEDS-GATE → ADVANTAGE-CONDITIONAL (best-known floor,
  said so).
- **The EXTERNAL-READY(-FENCED) provable columns are the campaign's strongest First-Contact
  material** — if the Creator ever directs external framing, superdense leads, the fenced three
  follow with their caveats prominent.
- **The instrument columns (F120, F113, cross-block) stay labeled** — real, cited as instruments,
  never dressed as speedups. P2 (cross-block physics) is booked here as an instrument/physics result
  by construction, which is correct.

---

*P0 + P3 are $0 and complete. The harness is reusable — every future claim runs it before it is
called an advantage. The scoreboard is now honest by construction, not by vigilance.*
