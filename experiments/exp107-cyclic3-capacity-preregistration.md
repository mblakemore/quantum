# Exp107 — Cyclic-3 Capacity Activation, sentinel-gated (PRE-REGISTRATION)

**Author**: Whisper (DC15W), C4532 (2026-07-10) — Creator-directed ("go ahead with Exp107")
**Status**: FROZEN at the pre-submission commit. Exp105 checklist self-applied (§Self-review);
siblings may object post-hoc, the rule cannot change after data.
**Lineage**: C4531 audit (cyclic-3 = 92–110 CZ routed, feasible; full-6 not this generation) →
this doc. Theory family: Ebler–Salek–Chiribella PRL 120 120502; N-channel cyclic extension
arXiv:2004.14339 cited as qualitative support (capacity grows with N). **The graded target is
OUR protocol's exact value, derived by noiseless simulation** (decoder-specific MI is a lower
bound on Holevo; we do not claim the paper's Holevo numbers).

## Claim under test

Three completely depolarizing channels in a superposition of the 3 CYCLIC orders transmit
classical information; every causally-separable composition of them transmits EXACTLY zero
(channel algebra). N=3 exceeds N=2: our exact noiseless targets are R̄ = +0.6730 and
MI = 0.0833 bits (vs 0.5333 / 0.0489 at N=2; Exp106 measured 0.5034 / 0.0436 on hardware).

## Why this experiment is structurally new for us

The payload is **92–110 CZ — inside the F81 calibration-window lottery zone** where the noise
model is unreliable (C4530 depth-stratification rule). This is the first LOAD-BEARING deployment
of Bridge-2 window harvesting: a **deep-retention sentinel** gates the window. The deep sentinel
is the (X,Y,Z) cyclic triple — same skeleton as the payload, and its three cyclic products all
equal −i·𝟙, so ideal output is |000⟩ with probability 1; retention P(000) is a direct
same-depth-class window meter (Exp101 Rec#5: a 4-CZ sentinel cannot certify a ~100-CZ window;
Exp100 row 7 showed k0 error anti-correlates with window quality).

## Design (frozen)

- 64 Pauli triples × 2 inputs, switch arm (800 shots) + definite-order null arm (500 shots),
  pooled = exact 3-channel twirl (mixed-unitary incoherence; Exp106 estimator logic).
- Sentinels at START/MID/END: F77 shallow pair (X,X)/(X,Z) @1500 (apparatus integrity) AND
  deep (X,Y,Z) retention @1500 (window meter). 265 PUBs, ~215k shots, ONE job.
- Layout: calibration-gated pair extended to the best coupled triple; shuffle seed 4532;
  live audit aborts if switch 2q max exceeds 130 (audited class).
- Control readout in the prep basis (inverse-prep + computational); '00' = prep-state class
  (c=0), else c=1. Discriminator R̄ = mean over inputs of ⟨Z_t|c=0⟩ − ⟨Z_t|c=1⟩ signed by bit;
  null observable = unconditioned D (Exp106 lesson).

## Frozen grade rule

1. **Shallow sentinel gate**: min replicate DISC ≥ +1.60, else NO-TEST (apparatus).
2. **Deep sentinel gate**: min replicate P(000) ≥ **0.55**, else **NO-TEST-WINDOW** — an
   expected, valid outcome that feeds the F82 window-statistics line (this gate is
   exploratory-calibrated: FakeMarrakesh-grade retention is 0.744, threshold = FM − 0.19
   drift allowance; N=0 hardware prior at this depth class, stated plainly).
3. **Null gate**: |D_null| + 5·SE < 0.05, else NO-TEST.
4. **WIN** iff R̄_switch − 5·SE > **0.10**; LOSS iff R̄ + 5·SE < 0.10 with gates passing;
   else AMBIGUOUS.
5. Reported, ungraded: MI vs 0.0833 (ideal) / 0.0485 (FM); P(c=0) vs 0.4953 (noiseless);
   deep-sentinel P(000) values as F82-relevant window data REGARDLESS of verdict.

## Self-review (checklist)

- Skeleton: all switch circuits share the cyclic-3 template; identity operands SKIP (no CC-U) —
  unlike Exp105/106 the per-triple 2q count varies with identity count. **Named honestly**: the
  pair-independence concession is weaker here; the causal bound (exactly 0) does not depend on
  a distribution, so the Exp105-style skeptic argument has less purchase — the claim is about
  the CHANNELS (device-characterized), not a sampled game. Padding 27–110 CZ uniformly would
  add pure noise for no bound benefit; documented trade-off, chosen: no padding.
- Null observable: unconditioned D (Exp106 lesson, already applied).
- Drift: shuffle seed 4532 + BOTH sentinel families at START/MID/END gating on MIN.
- Estimator: pooling = exact twirl ✓. Deep-sentinel is also IN the payload set — its dedicated
  replicates are separate PUBs; no double-use of shots.
- Budget: ~75–90s expected remaining; job est. 30–60s. If the usage probe at submit shows
  < 40s, ABORT and wait for refresh (pre-committed).

## Prediction (pred_c4532_001, conf 0.50 — lottery zone, uncertainty is the point)

Two-branch, both pre-registered as informative: (a) deep gate PASSES (P(000) ≥ 0.55) and
R̄ ∈ [0.30, 0.60] → WIN [p≈0.5]; (b) deep gate FAILS → NO-TEST-WINDOW, retention values feed
F82 [p≈0.35]; residual: gates pass but R̄ below/straddling floor [p≈0.15]. The F81 lottery is
exactly why confidence sits at 0.50 rather than the 0.60 cap.
