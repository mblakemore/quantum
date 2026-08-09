# Finding — H13 Cell 5: THE EVENT THAT NEVER HAPPENS — Hardy's impossible event logged at 8.7%, 15.7σ past every local-realist accounting

**Cycle**: C5048 · **Date**: 2026-08-09 · **Backend**: `ibm_fez` · **Job**: `d9rufh0pdb6s73e5datg`
(8 circuits: 4 Hardy settings × 8000 shots + 4 null settings × 4000; account IBMQ_ALT; pair (137,147)). **Prereg**: [FROZEN at e7ca10d](../docs/h13-cell5-hardy-prereg-FROZEN-whisper-c5048.md) with the design numeric `tools/h13_cell5_hardy_freeze.py` committed alongside. Creator GO: general#7376. **All four frozen gates HELD — verdict PASS.** Second flight of H13; fills the Hardy gap in the no-go wing between CHSH (inequality) and the magic square (all-or-nothing).

## Result

| quantity | measured | frozen criterion | verdict |
|---|---|---|---|
| **W = q − z₁ − z₂ − z₃** | **+0.0576 ± 0.0037 (15.7σ over the LHV bound 0)** | > 0 at ≥5σ, band [0.02, 0.09] | **G1 HELD** |
| the three "zeros" | 0.0039 / 0.0138 / 0.0116 | each ≤ 0.03 | **G2 HELD** |
| Hardy fraction q = P(11\|A₁B₁) | **0.0869** (ideal 0.0928, theory max 0.0902) | ∈ [0.05, 0.12] | **G3 HELD** |
| null arm (\|00⟩, same settings) | W_null = −0.675; separation **72.8σ** | W_null < 0, diff ≥5σ | **G4 HELD** |

## The sentence made true

Three joint events were pinned near zero (measured: 0.4%, 1.4%, 1.2%). For any local-realist description — any story where the two qubits carry definite instruction sets — those three zeros force the fourth event to (at most) their sum. It happened **8.7% of the time**, 15.7σ more than every such story combined allows, in the *inequality-free* form Hardy found in 1992: no Tsirelson-style optimization, just counting. The same four settings pointed at a product state (the null) obey the classical bound by 0.675 — the apparatus does not manufacture the effect.

This is nonlocality certified by a **difference of raw frequencies with the bound derived from the measured zeros themselves** — nothing cited, nothing tuned: the imperfect zeros *weaken* W and it cleared 5σ anyway, with the measured q landing 96% of Hardy's ideal maximum.

## Ledger

- Freeze-numeric predictions vs measured: q 0.096 → 0.0869 · zeros ~0.014 → 0.004–0.014 · W 0.053 → 0.0576. Every quantity inside its band; W slightly *above* prediction because the zeros came in cleaner than priced.
- Bit-order defect caught **pre-flight** at selftest (freeze numeric indexes A as MSB; qiskit's StatePreparation makes q1 the MSB) — the Aer selftest reproduced q = 0.092838 exactly before submission.
- No postselection; all shots kept; probabilities are raw relative frequencies.
- **Cost accounting (miss, kept)**: estimated 2–3 QPU-s, billed **15 QPU-s** (same ~3–5× under-pricing class as Cell 3, same lesson). ALT now reads 609/600. Both alt accounts are drained; further H13 flights wait on top-up or roll-off.

## Fence

Device-characterized, single-chip, both wings on one die — detection and locality loopholes are open as in every campaign Bell-class flight (F73 scope), and no device-independence is claimed. The claim is the frozen-rule statistical one: these counts, these settings, this bound, derived in-code.

*Filed as promised: the impossible event showed up, and the ledger says exactly how often.*
