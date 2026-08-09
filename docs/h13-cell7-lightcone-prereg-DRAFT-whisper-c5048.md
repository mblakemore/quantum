# H13 Cell 7 — The Speed of Subspace (emergent light cone) — PREREG DRAFT

**Author**: Whisper (DC15W), C5048 · **Status**: DRAFT — freeze at fly time with live quiet-line pick.
**Queue**: behind door(b) on ALT3. Cost ~15-25s (16 circuits, wide-shallow).

## Claim (instrument genre — a new standing constant, plus its constant-vs-weather test)
Correlations in a brickwork chain spread inside a cone: the connected correlator C(r,d) between
the perturbed site and site r after d brickwork layers is ≈0 outside r > v·d and turns on inside
it. Deliverables: (1) the measured front velocity v_LR in sites/layer with CI (strict circuit
bound: 2 sites/layer — the measured front must sit AT or INSIDE it, a NO-TEST fires if outside);
(2) outside-cone correlators certified ≤ ε at 5σ (wall №6 measured from inside); (3) the SAME
16 circuits re-flown in a second calibration window → v_LR labeled CONSTANT or WEATHER — the
taxonomy's first purpose-built datapoint.

## Apparatus
Quiet line of 21 qubits (live picker, never cached), site 0 perturbed (X), brickwork CZ+Ry
layers d ∈ {1..8}, ALL sites measured each shot — one circuit per depth serves every separation
r ∈ {1..10} from the same dataset (no per-pair circuits). Two arms: perturbed and unperturbed
reference (connected correlator = difference), so 8 depths × 2 arms = 16 circuits × 4000 shots.
2q count per circuit ≈ 20×d ≤ 160 — inside every standing ceiling.

## Gates (bands freeze at fly time)
G1: front arrival d*(r) monotone in r; fitted v inside [1, 2] sites/layer with the circuit bound
2 as a NO-TEST wall, not a claim. G2: outside-cone |C| ≤ ε (5σ), pooled over all (r,d) with
r > 2d + 1. G3: inside-cone signal — C(1, d≥1) ≥ 5σ above the outside-cone pool. G4 (window 2):
v_window2 vs v_window1 — agreement band frozen BEFORE window 2 flies; verdict labels the
constant-vs-weather ledger. No postselection; the reference arm is the falsifier structure.
