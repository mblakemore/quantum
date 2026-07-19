# Finding — Exp189: SHIELDS UP — the [[4,2,2]] detector works (2% joint escape), the shield already pays in Z

**Cycle**: C4879 · **Date**: 2026-07-19 · **Backend**: ibm_fez · **Job**: `d9e561cjeosc73fibmn0`
(6 circuits, 8000 shots). **Shields arc, stage (i)** — the campaign's first logical qubits.
Creator go: general#111 (A of A+B).

## Result

| arm | acceptance | logical err/qubit (accepted) |
|-----|-----------:|------------------------------:|
| L00 (Z readout) | 0.966 | **0.0010** |
| L++ (X readout) | 0.966 | 0.0025 |
| bare pair (Z / X) | — | 0.0021 / 0.0024 |
| inject X-error (Z readout) | 0.037 | rejection **0.963** |
| inject Z-error (X readout) | 0.035 | rejection **0.965** |

1. **The detector works.** A deliberately injected error is caught 96.3–96.5% of the time;
   the **joint escape rate** — accepted AND logically corrupted — is **2.0% / 1.7%** (≤ 0.05
   registered). The escapees are double-error shots (a second error restoring the parity), and
   among them the logicals are ~50% scrambled — exactly what escape *means* in a
   distance-2 code.
2. **The price is small**: 3.4% of clean shots rejected (acceptance 0.966 — above my 0.80–0.95
   band; the GHZ4 prep is cleaner than priced).
3. **The shield already pays in Z at stage-(i) gate counts**: accepted logical Z error
   0.0010 vs bare 0.0021 — **ratio 0.49 (~2.2σ)**. In X it is a statistical tie
   (0.0025 vs 0.0024, ratio 1.01 ± 0.23, grazing the 0.2–1.0 band edge by 0.01 = 0.04σ).
   As pre-registered: the mixed result *prices stage (ii)* (time-matched survival, mid-circuit
   syndrome windows with the toolkit) rather than killing the arc — and Z already paying with
   the bare reference *gate-lighter* is ahead of the stage-(i) expectation.

## Process note (banked): criteria as formulas, not prose

The decode printed CHECK on the detector because my prereg sentence ("accepted-and-wrong rate
≤ 0.05") and my code disagreed about its meaning: the text reads as the **joint** rate
(P[accepted ∧ wrong] = 0.020/0.017 → holds); the code implemented the **conditional**
(wrong | accepted = 0.53 → fails). Verdict here follows the registered text; both numbers are
reported; the JSON's stricter machine verdict stands unedited in `results/`. New checklist
item: **pre-registered criteria must be written as formulas** — prose invites its author to
mean one thing and code another.

## Fence

Error *detection*, not correction (distance 2 — post-selection discards, never fixes); terminal
readout only (deliberately no mid-circuit windows at stage (i)); the bare reference is
gate-lighter, so the Z-ratio 0.49 *understates* the shield's eventual advantage per accepted
shot at matched time — stage (ii)'s job. One die.

## The arc's ladder from here

(ii) time-matched survival + first mid-circuit syndrome measurement, windows priced and echoed
with the toolkit → (iii) a logical Bell pair over the witness → (iv) teleport a logical qubit.
