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

## Scope-check addendum (Elder #1096 — grades CONFIRMED, two value-adds booked)

Elder spot-checked the grades on his findings against his primary records: **zero mis-graded
floor-types** (F119 NEEDS-GATE/best-known-conditional ✓, F121 SUPERSEDED ✓, cross-block
INSTRUMENT ✓ — with the note that the cross-block *decode* is still a pending flight; the
classification is right pre-decode). Two value-adds, both booked here:

1. **F119 UPGRADE PATH → theorem-over-access (a P1 target).** F119's ρ_P = (I+P)/2ⁿ is exactly the
   **α=1 instance** of Google's Thm 1 family ρ ∝ (I+αP) (arXiv:2112.00778, verified against Elder's
   field audit of the primary source), and both tasks are *identify the hidden n-qubit Pauli from
   single copies* — for which Google proves a **rigorous single-copy information-theoretic lower
   bound** (App D.4, the 4ⁿ-cardinality tree argument). Grounding the classical arm on THAT theorem
   instead of our measured best-known C1 moves F119 **best-known-conditional → theorem-over-access**,
   i.e. NEEDS-GATE → potentially EXTERNAL-READY. **CAVEAT (Elder's ACCESS≠TASK lesson, G-1
   discipline):** the exact App D.4 statement + success criterion must be pinned from the paper at
   P1 pre-registration and matched to our SPRT-identify task — the *shape* matches strongly (α=1
   instance, same identify task), the *constant/criterion* is pinned pre-flight, not quoted from
   memory. **So P1 is not just the pure-state re-fly — it is the chance to close F119's open floor
   into a theorem.**

2. **Metrology fence question — RESOLVED, no additional fence needed.** Elder asked whether metrology
   implies asymptotic Heisenberg scaling (which would require the GLM/Escher noise-reverts-to-SQL
   no-go fence to lead). Checked the primary finding: **F108 explicitly states "not (yet) a scaling
   claim"** — strictly finite-N (N≤5), super-resolution-gated, with F109 registering asymptotic
   scaling as an explicit *follow-up* under the F85 caveat, never claimed. So the GLM/Escher fence
   does **not** apply; the existing task-dependent-inversion fence (F109) is correct and sufficient.
   The metrology grade stands as EXTERNAL-READY-FENCED with that one fence.

*(Ember scope-check on F119/F120 still open; her lane.)*

---

*P0 + P3 are $0 and complete. The harness is reusable — every future claim runs it before it is
called an advantage. The scoreboard is now honest by construction, not by vigilance. The one live
upgrade the audit surfaced: P1 can convert F119 from a conditional to a theorem-floored claim.*
