# Exp123 — THE TIME-LOOP COURTROOM (P-CTC): PREREGISTRATION (FROZEN)

**Author**: Whisper (DC15W), C4655. Creator: "run Q5." Design+sim+freeze+fly one
cycle (Exp119-class: known protocol, 3 qubits, trivial depth, sim margins 60σ).
Sim: `exp123_pctc_sim.py` → `results/exp123_feasibility.json`.

## Claim under test (honest scope FIRST)

Lloyd's postselected closed timelike curve, SIMULATED as Lloyd himself did: the
"time loop" is a Bell pair (A,T) closed by Bell-projection onto Φ+; postselection
IS the timeline. Within that stated scope, two frozen laws:

1. **The enforcement rate**: a traveler attempting a θ-strength grandfather flip
   (Ry(θ)) is postselected at p(θ) = cos²(θ/2)/2 — and the full paradox (θ=π) has
   **exactly zero self-consistent amplitude** (0 to machine precision in the exact
   tier). The timeline forbids the paradox by making it un-happen; we measure the
   enforcement rate. Disclosed plainly: the broken-loop arm shares this RATE shape
   — the projection is the mechanism, which is the P-CTC point, not a loophole.
2. **The loop's fingerprint on bystanders** (the discriminator the rate can't
   fake): a chronology-respecting bystander S, correlated with the traveler
   BEFORE the loop closes, is heralded into coherence: X_S(loop) = 1.0 exactly at
   every θ, versus the broken-loop arm's X_S = 0, Z_S = 1. The self-consistency
   projection rotates the bystander's classical record into a quantum coherence —
   nonlinear CTC backaction on ordinary matter, the thing a trivial-postselection
   reading cannot produce on the bystander.

## Frozen apparatus (builders byte-identical: `exp123_pctc_sim.py::build`)

Qubits [A,T,S]; arms loop/broken (broken = identical circuit minus H(A) —
structure-invariant); θ ∈ {0, π/4, π/2, 3π/4, π}; S read in Z and X.
**20 pubs × 15,000 = 300k shots, one job, ibm_marrakesh.** Site: frozen chain rule
(`run_exp122_submit.select_chain`), mapping T = hub, A/K-slot, S/L-slot. Seeds 4655.
Audit: uniform 2q counts per arm class (4 CX-class each), all inside site.

## Frozen gates (R2 selftest required 4/4 before hardware grading)

- **G0 (NO-TEST)**: p(0) ∈ [0.40, 0.60] both arms (fake 0.496/0.491).
- **N1 (NO-TEST)**: X_S(broken, 0) < 0.25 (miswire guard; fake −0.02).
- **W_PARADOX (headline 1)**: p(π)/p(0), loop arm, < 0.1 with 5σ (ratio SE by
  propagation) → **PARADOX-ENFORCED** (fake ratio 0.016 ≈ 60× suppression;
  measured suppression factor reported as figure of merit).
- **W_LOOP (headline 2)**: X_S(loop, 0) − X_S(broken, 0) > 0.5 at 5σ →
  **CTC-BACKACTION-CERTIFIED** (fake diff ≈ 0.99 at ~60σ).
- **Subclaims (reported)**: rate-law residuals vs cos²(θ/2)/2 across the ladder,
  both arms; heralded S trajectories vs θ; paradox-point herald autopsy (the few
  surviving heralds are error events — their S stats reported).

## Predictions (registered at freeze)

- **P1** W_PARADOX: **0.90** (readout floor would need to exceed ~5% of p(0) to
  fail; fake floor 1.6%).
- **P2** W_LOOP: **0.90** (60σ fake margin; shallow circuit).
- **P3** NO-TEST: **0.05**.

Lint: `experiments/exp123_gate_lint_spec.json` → `results/exp123_gate_lint.txt`.
Grader `scripts/grade_exp123.py` FROZEN with this prereg (selftest output
`results/exp123_selftest.txt`).
