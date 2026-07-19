# Exp189 Pre-registration — SHIELDS UP: the [[4,2,2]] error-detecting code (Shields arc, stage i)

**Cycle**: C4879 · **Date**: 2026-07-19 · **Backend**: ibm_fez · **Shots**: 8000 × 6 circuits
**Arc**: THE SHIELDS (A of the Creator's A+B go, general#111) — stage (i) of: shields up →
does the shield pay → shielded entanglement → the shielded transporter.

## The question

Everything this campaign certified ran on bare qubits. Stage (i) raises the shield: encode
**2 logical qubits in 4 physical** ([[4,2,2]], stabilizers XXXX and ZZZZ — the smallest
error-*detecting* code) and demonstrate, on hardware: (a) the code detects errors (an injected
error is caught essentially always), (b) post-selecting on clean syndrome yields logical error
**below** the bare-physical reference, (c) the acceptance price is measured.

Detection by final readout (the standard [[4,2,2]] form — deliberately no mid-circuit
syndrome extraction at stage (i); the window law says that is where the cost lives, and
stage (ii) will pay it knowingly, with the toolkit):
- Z-basis readout of all 4 gives the ZZZZ syndrome AND the logical values Z̄₁ = z₁⊕z₃,
  Z̄₂ = z₁⊕z₂ in the same shots.
- X-basis readout gives the XXXX syndrome and X̄₁ = x₁⊕x₂, X̄₂ = x₁⊕x₃.

## Circuits (6)

| circuit | what |
|---------|------|
| L00_Z | encode \|0̄0̄⟩ = (\|0000⟩+\|1111⟩)/√2 (H+3CX), read Z⁴ — accept on ZZZZ=+1, logical error = any Z̄ flip among accepted |
| Lpp_X | encode \|+̄+̄⟩ (= H⊗⁴ of the above; direct prep), read X⁴ — accept on XXXX=+1 |
| bare_Z / bare_X | 2 bare qubits \|00⟩ / \|++⟩, matched barrier structure — the unshielded reference |
| inject_Z | L00_Z with a deliberate X inserted on q0 — the detector-works falsifier: ZZZZ flips, shot REJECTED |
| inject_X | Lpp_X with a deliberate Z on q0 — XXXX flips, rejected |

## Pre-registered predictions

- **Detection leg (hard)**: injected-error rejection ≥ 0.90 in both bases (ideal 1.0 —
  a single X flips ZZZZ deterministically); accepted-and-WRONG rate on injected arms ≤ 0.05.
- **Acceptance price**: clean-arm acceptance ∈ 0.80–0.95 per basis (GHZ4 prep error mostly
  *detected*, i.e. rejected rather than passed).
- **Shield leg (the interesting number, banded honestly)**: accepted logical error rate
  (per logical qubit, averaged over the two logicals and bases) **≤ bare-pair error rate**,
  ratio band **0.2–1.0** at matched readout; reported with the caveat that stage (i)'s bare
  reference is gate-count-lighter — the code pays 4 extra gates to buy detection; stage (ii)
  does time-matched survival. A ratio > 1 does not kill the arc; it prices stage (ii)'s job.
- **Criteria form** (checklist): rejection/acceptance are counts; the shield leg is a ratio of
  same-job error rates; no absolutes.

## Fences

Error *detection*, not correction (the [[4,2,2]] distance is 2); post-selection discards, it
does not fix; the bare reference at stage (i) is depth-lighter (named above — the honest
comparison matures in stage (ii)); one die, terminal readout only.

## Discipline

ps aux: clean (claim covers 188+189, whisper C4879). Ledger prediction pre-submit. Prereg
committed before decode. Selftest gates: acceptance 1.0, logical errors 0, injected arms
rejected ~100%, bare arms exact.
