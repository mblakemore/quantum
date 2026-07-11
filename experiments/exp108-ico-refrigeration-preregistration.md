# Exp108 — ICO Refrigeration Resource: conditional temperature splitting from the quantum switch of two thermalizing channels (AUDIT + PRE-REGISTRATION)

**Author**: Whisper (DC15W), C4558 (2026-07-11) — Creator-directed ("I like it — write the
audit doc and run it").
**Status**: FROZEN at the pre-submission commit. Exp105 sibling-review checklist self-applied
(§Self-review); siblings may object post-hoc, the rule cannot change after data.
**Lineage**: C4557 answer to Creator's logic-gates question → this doc. The key reuse insight:
**Exp106's completely depolarizing channels are the g=1/2 (infinite-temperature) point of THIS
experiment's channel family** — the constant-to-τ channel at τ=𝟙/2 IS the depolarizing channel,
and the switch is Kraus-decomposition-independent. Exp108 moves the same apparatus to finite
temperature, where the conditional splitting acquires a THERMODYNAMIC meaning.
**Theory**: Felce & Vedral, PRL 125, 070603 (2020) (ICO refrigeration). Prior art stated
honestly: photonic/optical simulations of the F-V cycle exist (arXiv:2101.07979 and successors);
ours is the gate-model superconducting, pre-registered, sentinel-gated version.

## Claim under test

A fully-thermalizing qubit channel outputs τ = diag(g, 1−g) regardless of input. EVERY
causally-separable composition of two of them outputs EXACTLY τ, uncorrelated with any control
system — the discriminator below has causal value EXACTLY 0 by channel algebra (no SDP, no
measure-dependence; same clean structure as Exp106). In the quantum switch with control |+⟩,
measuring the control in X splits the target: outcome + (likely) leaves it COLDER than the
reservoir, outcome − leaves it HOTTER. That conditional splitting is the resource that powers
the Felce-Vedral refrigeration cycle.

**Exact theory targets** (g = 0.75, input pooled to τ — the cycle-relevant input; derived C4558
by direct Kraus computation of the switch supermap, `exp108_ico_refrigeration.py::exact_targets`):

    P(control = +) = 0.71875
    p₁|+ = 0.184783   (reservoir: 0.250 → COLDER)
    p₁|− = 0.416667   (          → HOTTER)
    Δ := p₁|− − p₁|+ = 0.231884 ;  causal value = 0 EXACTLY

**Derivation discipline notes** (both caught pre-freeze, C4558):
1. A recalled closed form (τ ± τ²)/(1 ± Tr τ²) was REFUTED by the direct computation — the
   conditional states are input-dependent in general; the numbers above are for input τ.
2. The theory code self-validates at g = 1/2 against Exp106's independently-derived targets
   (P(+) = 5/8, ρ|+ = (ρ+2𝟙)/5, ρ|− = (2𝟙−ρ)/3) — asserted on every run.

## Design (frozen)

- **Channels**: fully-thermalizing = SWAP with a fresh ancilla prepared in τ. τ is a classical
  mixture of basis states, so the 8 basis-prep circuits (t₀,a1₀,a2₀) ∈ {0,1}³ at equal shots,
  POOLED with exact weights w(t₀)w(a1₀)w(a2₀), w(0)=g, are the exact channel+input mixture
  (the switch supermap is linear in each channel slot; Exp106 estimator logic; conditioning on
  the pooled JOINT is valid because the joint is linear in the input).
- **Switch circuit**: controlled permutation on (t,a1,a2). c=0 branch = SWAP(t,a1)·SWAP(t,a2)
  = C₃; c=1 branch = C₃⁻¹ = C₃². Implemented as U = (𝟙⊗C₃)·CC₃ with CC₃ = two Fredkins.
  q0=control (X readout, clbit 0), q1=target (Z readout, clbit 1), q2/q3 ancillas (traced).
  **Transpiled payload: 21 two-qubit gates** (FakeMarrakesh, opt level 3) — mid-depth, well
  below the F81 lottery zone (~100 CZ) and the audited <130 class.
- **Null arms**: BOTH definite orders (C₃ and C₃⁻¹), control |+⟩ spectator, same 8 preps each.
  **C4529 lesson recurred and was caught pre-freeze again**: the conditional discriminator
  STARVES on a spectator control (no c=− samples; first sim run returned Δ_null = NaN) — the
  null gate is therefore on UNCONDITIONED p₁ (thermalization integrity), exactly as Exp106
  redefined its null. The two null arms are pooled-identical by ancilla-exchange symmetry in
  sim; on hardware they ride different routing and count as independent checks.
- **Sentinels** (same-skeleton, Exp107 Bridge-2 lesson — a shallow sentinel cannot certify a
  deeper window): RETENTION (all-|0⟩ prep = fixed point of both branches → ideal P(c=+,t=0)=1)
  at START/MID/END @2000; DECOHERENCE-NULL (t=1,a=00 → branch registers orthogonal → ideal
  P(c=+)=1/2 exactly, t=0 always — certifies the apparatus cannot fake interference) ×1 @2000.
- **Arms total**: 8 switch + 8 null_fwd + 8 null_rev @1500 + 4 sentinels @2000 = 28 PUBs,
  44k shots, ONE SamplerV2 job. Shuffle seed 4558.
- **Backend**: ibm_marrakesh, calibration-gated qubits (exp91 pick_pair extended to a coupled
  4-chain).

## Sim gates (both tiers PASSED pre-freeze, results/exp108_feasibility.json)

Noiseless: Δ = 0.2280±0.0020 (theory 0.2319), p₁|+ = 0.1855, null p₁ = 0.2500 exactly both
orders, retention 1.0000, deco-null P(+) = 0.4875 — all gates PASS.
FakeMarrakesh: Δ = 0.2275±0.0077, p₁|+ = 0.1903, null p₁ = 0.2548±0.0011, retention 0.9575,
deco-null P(+) = 0.4895 → preview WIN with large margin.

## Frozen grade rule

1. **Sentinel gate**: min over the 3 RETENTION replicates of P(c=+,t=0) ≥ **0.85**
   (FakeMarrakesh preview 0.9575 minus margin), else NO-TEST.
2. **Thermalization gate**: |p₁_null − 0.25| + 5·SE < **0.05** for EACH definite order, else
   NO-TEST (if the definite-order arm is not at the reservoir state, the channel
   implementation is broken).
3. **WIN** iff Δ_switch − 5·SE > **0.08** (theory 0.232, sim-with-noise 0.228, causal value
   exactly 0) **AND** cooling direction holds: p₁|+ + 5·SE < 0.25.
4. **LOSS** iff Δ_switch + 5·SE < 0.08 with gates passing; else AMBIGUOUS.
5. Reported, ungraded consistency checks: P(+) vs 0.719; p₁|− vs 0.417; null spectator
   coherence P(c=+) vs 1; DECOHERENCE-NULL P(c=+) ∈ 0.5 ± 0.05 band; per-label input
   consistency.

## Honest scope (stated before data)

- **Device-characterized**, same concession as Exp105/106/107: this is a definite-order
  circuit implementing the switch statistics, not a claim of indefinite spacetime order.
- **Demon honesty**: with no feedback, expected heat flow is ZERO — the + branch cooling and
  − branch heating cancel exactly (P(+)·(0.25−p₁|+) = P(−)·(p₁|−−0.25), verified in the
  targets: 0.719×0.0652 = 0.281×0.1667 = 0.0469). Refrigeration requires USING the control
  measurement record (feedback/post-selection); the fuel is control purity, as Felce-Vedral
  state. We measure the conditional splitting Δ — the resource — and the cycle's heat
  arithmetic follows from it; we do not claim measured net cooling of a physical reservoir.
- **What would make this MORE than a demo**: nothing in this experiment; the honest framing is
  a pre-registered gate-model measurement of the F-V resource with an exact zero causal
  benchmark. The real-world hook (cooling costs energy at the quantum scale) is motivational,
  not a measured deliverable.

## Prediction (pred_c4558_001, conf 0.60 quantum cap)

Sentinel + thermalization gates pass; Δ_switch ∈ [0.15, 0.24] → WIN with cooling direction;
p₁|+ ∈ [0.17, 0.22]. Risk named: 4-qubit chain quality is the new unknown (first 4q payload
in this line); readout error on the target dilutes Δ multiplicatively; if the chain draws a
bad edge the retention sentinel should catch it (that is what it is for).

## Cost

44k shots ≈ 10–20s QPU (Exp106: 108k ≈ 25–45s). Creator authorized the line of work
("API budget is OK ... don't assume it is depleted"); ONE job, never auto-resubmits.
