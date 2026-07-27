# Probe B — many-body Renyi-2 entanglement entropy (design, Whisper C5010)

*Creator "Start A and B when possible." B rides on the two-copy purity instrument steth validates, and
reuses Ember's DELIVERED SWAP-purity circuit (exp_steth_3b) — so the honest "start" is design +
coordination, not a premature re-implementation of her kit. QPU-floored: this is build-ready-on-steth,
fly-on-time.*

## The question
"How does entanglement spread in a quantum system the device runs — does it thermalize / scramble?"
Directly probed by watching the Renyi-2 entanglement entropy of a subsystem grow under evolution.

## The measurement
For a subsystem A of a state |ψ(t)⟩, **S₂(A) = −log₂ tr(ρ_A²)**, and **tr(ρ_A²)** is read by a two-copy
SWAP test on the A-registers of two copies (single-copy tomography of ρ_A is exponential in |A| — this
is where the two-copy kit is genuinely REQUIRED, unlike probe A's single-qubit case).

## First concrete experiment (minimal, decisive)
- **State**: a shallow scrambling quench — L layers of a fixed brickwork of native entangling gates on
  m≈6 qubits (chaotic enough that S₂ grows, shallow enough to stay on-device).
- **Sweep**: L = 0,1,2,3,… ; at each L, two copies, SWAP-test the A-subsystem (|A| = 1,2,3).
- **Observable**: tr(ρ_A²)(L) → S₂(A)(L). Expect S₂ RISES with L toward the Page value (≈|A| bits for a
  scrambled state) — the direct signature of entanglement spreading.
- **Control**: L=0 (product state) must give S₂(A)=0 (tr ρ_A²=1); a scrambled deep-L must approach Page.

## Reuse + dependency (why it starts as design)
- **Reuses**: Ember's delivered two-copy SWAP-purity circuit (exp_steth_3b) + Choi/DD prep patterns —
  the SAME kit steth flies. B is that kit pointed at a *subsystem* of an *evolving* state instead of a
  channel Choi.
- **Gated on**: steth's λ_anc pre-seal gate PASS (validates the two-copy purity readout on-device). Once
  steth validates the instrument, B's build is mechanical (swap the Choi-prep for the quench + subsystem
  SWAP). Building B's circuit *before* that validation would duplicate Ember's kit and pre-empt the gate.
- **Coordination**: @ember owns the SWAP-purity circuit; B should be built WITH her kit, not beside it.

## Scope discipline (session rule: claim = observable)
- This is a PHYSICS PROBE (entanglement dynamics), NOT an advantage claim. No floor, no separation
  asserted — S₂ is a measured quantity.
- Renyi-2-via-SWAP is established physics (Islam 2015 et al.); the news is our validated kit reaching it.
- On-device: SWAP-test purity is readout- and depth-limited; S₂ from a noisy tr(ρ_A²) is a LOWER-bounded
  estimate (noise inflates apparent mixedness → over-estimates S₂). Report tr(ρ_A²) with its error and
  treat S₂ as noise-bounded, not exact — same "match the claim to the observable" rule as probe A.

## Status
DESIGN-READY, gated on steth. Ordering: A (single-copy, buildable now — BUILT + $0-validated C5010) is
the immediate probe; B follows steth's instrument validation. Neither displaces the advantage queue.
