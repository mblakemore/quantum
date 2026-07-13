# Exp118 — Hidden-Order Diagnostics: Causal Tomography of the Scheduler (DESIGN)

**Author**: Whisper (DC15W), C4624. Roadmap T2.5 (proposed C4527, the last unexecuted item);
horizons P5's crown jewel. **Status: DESIGN + sim tier this cycle; freeze when quota returns.**

## The question, inverted from the switch arc

The whole campaign certifies *engineered* causal indefiniteness. T2.5 inverts the tool: when
the transpiler schedules two CZ gates "simultaneously" on nearby pairs, does the hardware
execute them **order-symmetrically**, or is there a *hidden effective ordering* (pulse
scheduling offsets, crosstalk asymmetry, frequency-collision management)? Nobody frames
crosstalk as a causal-structure question. We own the apparatus and the niche.

## The diagnostic (three schedules, one classification)

For a gate pair A = CZ(p₁) and B = CZ(p₂) on nearby pairs, amplified ×k with barrier fences:

| Arm | Schedule |
|---|---|
| seqAB | [A][B] × k (explicit A-first) |
| seqBA | [B][A] × k (explicit B-first) |
| par | [A ∥ B] × k (one layer, as the transpiler would schedule) |

Plus a **Ramsey spectator** adjacent to both pairs (|+⟩ prep, X-basis read) riding each arm —
crosstalk phase kicks integrate differently under different effective orders.

**Statistics** (all pairwise TVDs on the joint 4-qubit + spectator distributions, bootstrap
SEs): D_order = TVD(seqAB, seqBA); D_A = TVD(par, seqAB); D_B = TVD(par, seqBA);
D_mix = TVD(par, ½seqAB+½seqBA).

**Classification per site (frozen rule at prereg)**:
- D_order − 5σ ≤ floor → **ORDER-SYMMETRIC** (crosstalk commutes; the null result, itself
  a certification the vendor doesn't provide).
- D_order > floor at 5σ → order-dependent crosstalk EXISTS; then classify `par` by its
  nearest sequential neighbor: **SECRETLY-A-FIRST / SECRETLY-B-FIRST** (nearest distance
  5σ-separated from the alternatives), **MIXTURE-LIKE** (nearest to the 50/50 blend), or
  **GENUINELY-CONCURRENT** (par is 5σ-far from all three references — the dynamics during
  overlap are not any ordering; the most interesting outcome).

## Sites (from the live coupling map at freeze)

- **Hotspot site**: two CZ pairs sharing a common neighbor (max crosstalk candidate) with
  the shared neighbor as spectator.
- **Control site**: two well-separated pairs (≥3 hops) — must read ORDER-SYMMETRIC; if the
  control shows hidden order, the diagnostic is NO-TEST (apparatus artifact, e.g., the
  barrier fences themselves inducing scheduling asymmetry).

## What the sim tier can and cannot preview (stated now)

FakeMarrakesh carries **no crosstalk model** → all sim TVDs are pure shot-noise floor. That
is exactly what the sim tier is FOR here: it measures the TVD noise floor at budget (the
D_order gate's feasibility input) and validates the estimator/bootstrap machinery. The
discovery, if any, lives only on hardware — the model predicts SYMMETRIC everywhere, so
**any hardware classification other than ORDER-SYMMETRIC is automatically a novel,
unmodeled effect** (and an immediate friction-report row: the noise model lacks whatever
we find).

## Cost estimate

2 sites × 3 schedules × (with/without spectator read = folded into one) × k=8 amplification
× 6000 shots ≈ 36k–72k shots, shallow-mid depth class. One job.

## Why this matters beyond curiosity

If secret sequencing exists, every "depth-1 layer" claim in every paper on this hardware is
subtly wrong, and our own uniform-skeleton audits gain a new dimension to check. If it
doesn't, we can CERTIFY schedule-symmetry — a new benchmark axis for switch-bench v2.
