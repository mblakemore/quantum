# H13 Cell 6 — The Silent Tripwire (Elitzur-Vaidman IFM + Zeno ladder) — PREREG DRAFT

**Author**: Whisper (DC15W), C5048 · **Substrate**: claude-fable-5 · **Status**: DRAFT — freeze at fly time with live-calibration bands.
**Design sim**: `tools/h13_cell6_ifm_design_sim.py` → `results/h13_cell6_ifm_design_c5048.json` (CORRECTED model: the sim's first version used a persistent bomb qubit and eta froze at 0.25 — the Zeno mechanism REQUIRES per-segment bomb measurement + reset; the correction is the design study's finding and stays on the page).
**Proposed venue**: ALT3 (`ibm_fez`/`ibm_marrakesh`), QUEUED BEHIND the door(b) re-fly per Creator directive 2026-08-09 (general context: whisper-de is a PAID instance — off-limits without explicit authorization; earlier draft proposed it in error, inferring free-plan from the 0/63 counter). Cost ~15-20s (13 circuits, MCM-heavy, 4x heuristic per the C5048 lesson).

## Claim
Interaction-free detection: the bomb's presence certified by runs where it provably never fired, at the EV base rate (~25% at N=2), climbing the Kwiat-Zeno ladder eta(N) toward the noise ceiling — with the rollover point (where per-segment gate noise beats marginal Zeno gain) measured as a deliverable.

## Apparatus
Probe qubit + bomb qubit. N segments: Ry(pi/N) on probe → CX(probe→bomb) → mid-circuit measure bomb → reset. Explosion = any bomb bit fired. Detection = probe reads 0 AND no fire (bomb-present arm). Ladder N ∈ {1,2,4,8,16} × {bomb, no-bomb control} + bomb-faithfulness premise circuit = 13 circuits × 4000 shots.

## Gates (bands to freeze at fly time from design-sim + live readout numbers)
G1: eta(N) rises monotonically N=2→8 and lands in per-N bands (sim: 0.25/0.52/0.70 at N=2/4/8; ideal 0.25/0.53/0.73). G2: no-bomb control P(probe=1) ≥ 0.95 all N. G3: bomb-faithfulness — directly probed bomb fires ≥ 0.95. G4: N=1 point at the EV-degenerate value (eta ≈ 0). UNDERPOWERED/FAIL/NO-TEST per house three-state rules; postselection: none — explosion runs are counted, not discarded (their fraction IS P_explode).

## Fences
No advantage claim (foundations/law-match genre; no claim card). The "interaction-free" scope: certified counterfactually via the fired/unfired record under the projective-query model; per-segment MCM quality enters via the faithfulness gate.
