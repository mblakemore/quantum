# Exp108b — NATIVE-Noise ICO Thermal Splitting: the chip's own T1 decay as the working fluid (PRE-REGISTRATION)

**Author**: Whisper (DC15W), C4562 (2026-07-11) — Creator-directed ("Run Exp108b with the
native-noise variant"). Roadmap T2.4 delivered on the Exp108 harness (the C4560 synthesis §2.1
connection).
**Status**: FROZEN at the pre-submission commit. Exp105 checklist self-applied (§Self-review);
siblings may object post-hoc, the rule cannot change after data.
**Lineage**: Exp108 WIN (21.1σ, `d98vqfsqp3as739tfg0g`) with SYNTHETIC reservoirs (classically
pooled basis preps) → this experiment replaces only the reservoir preparation: each ancilla is
prepared |1⟩ and **idles for a per-qubit T1-calibrated delay**, so its mixedness is produced by
genuine system–environment entanglement — the chip's own amplitude damping is the working fluid.

## Claim under test

Same theorem as Exp108 (every causally-separable composition of two fully-thermalizing channels
outputs the reservoir state, uncorrelated with any control — conditional discriminator EXACTLY 0
by channel algebra), now with **natively-generated thermal reservoirs**. Demon-honesty upgrade:
in Exp108 the experimenters held each shot's ancilla record (a demon could exploit it); here the
record is held only by the environment — the entropy consumed is real.

**Why not "idle decay in the switch" directly**: two idle delays on the SAME qubit commute
trivially — time cannot be routed. The SWAP-dilation routing is what makes two copies of native
decay orderable. SWAP with a decayed ancilla is FULL thermalization (γ=1) to that ancilla's
state regardless of how it got mixed — the native part is where the entropy comes from, cleanly.

## Design (frozen)

- **Apparatus**: Exp108's graded chain and layout REUSED verbatim (marrakesh chain (5,6,7,8),
  layout [5,7,6,8], 22-CZ controlled-3-cycle skeleton) — a controlled comparison in which ONLY
  the reservoir preparation changes. NO-GO abort (documented, no spend) if live calibration
  shows a dead qubit on the chain (readout err > 0.10, T1 < 50 µs, or cz err ≥ 0.10).
- **Reservoir prep**: X on each ancilla, then `delay(tᵢ)` with tᵢ = T1ᵢ·ln(1/0.25) from the
  LIVE backend T1s at submit (design-time: a1=q6 ≈ 201 µs → ~279 µs; a2=q8 ≈ 155 µs → ~215 µs).
  Reservoirs are **asymmetric by nature** (per-qubit T1) — the true two-reservoir setting.
- **Schedule**: delays fire while control/target sit in |0⟩ (Z-eigenstates, T1-stable) behind a
  barrier; target prep + H(control) follow the delay. Depth-class exposure of the graded
  observable stays 22 CZ (law-comparable to Exp108). All arms, INCLUDING sentinels, carry the
  same delays (identical wall-time exposure).
- **Targets are a frozen PROCEDURE, not frozen numbers**: two calibration arms (X + delay +
  SWAP into target + measure target — the payload's own readout path) measure p̂_A, p̂_B; exact
  targets computed post-hoc as `exact_targets_2tau(p̂_A, p̂_B, input=diag(0.75,0.25))` (direct
  Kraus, `exp108b_native_thermal.py`). Theory code self-validates on every run at TWO anchors:
  the Exp108 fixed-point chain (→ Exp106 hardware numbers) and the symmetric-point identity
  vs Exp108's frozen targets.
- **Arms** (12 PUBs, 36k shots, ONE SamplerV2 job, shuffle seed 4562): 2 switch @3000 (input
  pooled 0.75/0.25, frozen nominal), 2+2 definite-order nulls @2500 (fwd → τ_B, rev → τ_A),
  2 calib @6000, 3 same-skeleton retention sentinels @2000 (START/MID/END), 1 deco-null @2000.

## Sim gates (both tiers PASSED pre-freeze, results/exp108b_feasibility.json)

Noiseless (basis-pooled equivalent — exactly equal statistics by switch-slot linearity):
Δ = 0.2362±0.0051 vs theory 0.2319, nulls exact, retention 1.0 → WIN.
FakeMarrakesh (REAL delay circuits against its T1 model; its own T1s q6=284/q8=253 µs used for
calibration, as submit will): calib p̂ = 0.249/0.253 (the native prep lands ON target),
retention 0.9555, therm nulls match p̂ to <0.1pp; Δ across seeds {0.203, 0.206, 0.215} ± 0.013
→ WIN all seeds.
**Frozen-rule defect caught by the tiers**: the drafted therm gate (0.05) was IMPOSSIBLE at
draft shot counts (5·SE alone = 0.069 with zero real deviation) → band 0.06 + shots raised
(calib 6000, null 2500), leaving ~1.8pp for real breakage. Fixed PRE-freeze.

## Frozen grade rule

1. **Calibration gate**: p̂_A, p̂_B ∈ (0.12, 0.40) each, else NO-TEST (delay mis-calibration /
   T1 drift — the native prep itself failed, nothing downstream is interpretable).
2. **Sentinel gate**: min retention P(c=+,t=0) ≥ **0.80** over 3 replicates, else NO-TEST.
3. **Thermalization gate**: |p₁_null_fwd − p̂_B| + 5·SE < **0.06** AND |p₁_null_rev − p̂_A| +
   5·SE < 0.06, else NO-TEST.
4. **WIN** iff Δ_switch − 5·SE > **0.06** AND p₁|+ + 5·SE < **min(p̂_A, p̂_B)** — the +branch
   colder than the COLDEST reservoir (unambiguous refrigeration resource, stronger than
   Exp108's symmetric gate).
5. **LOSS** iff Δ_switch + 5·SE < 0.06 with gates passing; else AMBIGUOUS.
6. Reported, ungraded: P(+) vs theory(p̂); p₁|− vs theory; deco-null P(c=+) ∈ 0.5 ± 0.06;
   null spectator P(c=+); Δ(108b) vs Δ(108) = 0.1796 (the working-fluid substitution effect,
   same apparatus).

## Depth-decay-law note (informal, pre-data — C4560 ledger discipline)

Same 22-CZ class → law predicts ratio 0.866 → Δ ≈ 0.87 × Δ_theory(p̂) ≈ **0.201 at p̂ ≈ 0.25**;
FakeMarrakesh central ≈ 0.208 — the two predictors nearly AGREE at this depth (the Exp108
discrimination came from the model's optimism at depth-class; at 22 CZ + delays they converge).
The informative comparison this time is **window-relative**: Exp108's mediocre window delivered
ratio 0.774; if retention again lands ~0.85, expect Δ ≈ 0.18. Each future job accumulates
(depth, ratio, retention) triples for the law's window term.

## Self-review (Exp105 checklist)

- Skeleton uniformity: ✓ payload/sentinels share the 22-CZ skeleton + identical delays; live
  audit aborts if any payload circuit exceeds 40 routed 2q gates or skeleton histogram splits.
- Estimator validity: ✓ input pooling exact (frozen weights); no ancilla pooling on hardware —
  the mixedness is physical (sim tier validates the equivalence by slot linearity).
- Null observable: ✓ unconditioned (C4529/C4558 starvation lesson, third deployment); BOTH
  definite orders, each checked against ITS reservoir (fwd→τ_B, rev→τ_A — asymmetric-aware).
- Drift: ✓ shuffle seed 4562, sentinels START/MID/END, calib arms in-job (same window as
  payload by construction).
- Bound applicability: ✓ causal value exactly 0 by channel algebra; measured-p̂ procedure
  cannot move it (any constant channels compose to control-uncorrelated output).
- Gate feasibility: ✓ verified non-vacuous AND passable on both tiers (the 0.05→0.06 fix).
- Device-characterized scope: ✓ same concession as the family, stated.

## Prediction (pred_c4562_001, conf 0.60 quantum cap)

All three integrity gates pass; p̂_A, p̂_B ∈ [0.20, 0.30]; Δ ∈ [0.14, 0.23] → WIN with the
colder-than-coldest gate met. Risks named: T1 drift since design-time probe moves p̂ (calib
band absorbs ±massive drift); thermal excitation during long delays pumps target/control
slightly (would show in retention + deco rows); the colder-than-coldest gate is STRICTER than
Exp108's and is the most plausible single point of failure into AMBIGUOUS.

## Cost

36k shots with ~280 µs mean added delay ≈ 12 s delay + execution ≈ **~20 s QPU** of 517 s
remaining (post-Exp108). ONE job, never auto-resubmits.
