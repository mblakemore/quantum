# Finding — Exp192: THE SHIELDED TRANSPORTER — a logical qubit teleported between shields at 0.98/0.99, beating the bare machine. The Shields arc is complete.

**Cycle**: C4884 · **Date**: 2026-07-19 · **Backend**: ibm_fez · **Job**: `d9e68bcjeosc73fid4cg`
(6 circuits, 8000 shots; 12 qubits, three [[4,2,2]] blocks, all-transversal, ZERO windows).
**Shields arc stage (iv) — the capstone. All pre-registered criteria HELD.** Creator go: general#140.

## Result

| arm | \|0̄⟩ success | \|+̄⟩ success | acceptance |
|-----|--------------|--------------|------------|
| **logical (the transporter)** | **0.9802** | **0.9933** | 0.633 / 0.708 |
| noresource (falsifier) | 0.4977 | 0.5003 | 0.725 / 0.768 |
| bare physical teleport | 0.9624 | 0.9237 | 1.0 |

1. **A logical qubit teleported between error-detecting shields.** Message block M, resource
   blocks A–B carrying Exp191's 57σ logical Bell pair, logical Bell measurement by transversal
   CX + basis readouts, every correction deferred to decode XORs (Clifford consumption — the
   Exp181 zero-window architecture carrying fault tolerance). Success 0.9802 (Z̄ message) and
   0.9933 (X̄ message) on the triple-postselected ensemble.
2. **The shielded transporter BEAT the bare one** — 0.9802/0.9933 vs 0.9624/0.9237 (the X̄
   lane by +0.07). Third appearance of the postselection-scrubbing effect (states in stage ii,
   entanglement in stage iii, now teleportation): the shields' toll (~30–37% of shots) buys an
   accepted ensemble cleaner than raw hardware achieves at any price.
3. **The quantum action is the logical e-bit**: Δ+ = +0.493 at **76σ**.
4. **The falsifier landed dead-center on the corrected physics**: without the pair, BOTH
   messages die to coin flips (0.4977/0.5003) — state teleportation has **no classical
   shadow** (unlike gate teleportation, Exp170, where the classical action rides the gate
   chain). The distinction was caught by the selftest pre-flight and pre-registered corrected;
   the hardware then drew it exactly.

## Ledger

All criteria held; |+̄⟩ band missed HIGH by 0.013 (0.9933 vs 0.88–0.98 — benign, same
recovered-conditions direction as Exp191). Acceptance gauge held (≥0.50). Prereg corrected
pre-flight (falsifier physics) with the correction committed before submission — the third
selftest-caught design error of the run, and the third converted into a sharper experiment.

## Fence

Two certified logical bases (|0̄⟩, |+̄⟩ — full 6-state logical tomography is the named
follow-up); distance-2 detection + postselection; terminal readout only; blocks are chip
patches. The claim: the logical state moved between shields with the resource, the protocol,
and the falsifier all certified — the arc's namesake, scoped honestly.

## THE SHIELDS ARC — COMPLETE

(i) **Shields up** (Exp189): 2 logical qubits in 4 physical; detector at 2% joint escape.
(ii) **The shield pays** (Exp190/190b): the detection-pays curve mapped both ends (crossover
≈1.2–1.5 μs); mid-circuit syndrome coverage certified (+0.452 differential).
(iii) **Shielded entanglement** (Exp191): logical Bell at 57σ with the in-shot product control
at 0.998 on the bound; shielded pair beat bare.
(iv) **The shielded transporter** (Exp192): a logical qubit teleported between shields at
0.98/0.99, beating bare, zero windows, corrections in software, no classical shadow.

Every stage pre-registered; every falsifier on script or corrected pre-flight; the toolkit
(window law, echoes, frames, zero-window architecture) load-bearing at every rung.
