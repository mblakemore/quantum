# Exp58 — Exp55-G1 genuine noise toggle (resolves the C4153 r=1 open item)

**Status**: PRE-REGISTERED (design + runner committed). **NOT LAUNCHED.**
**Author**: Whisper (DC15W), C4223 (2026-06-20, Sat).
**Lineage**: This is the **valid Exp55 relaunch** the C4153 audit pre-specified as G1.
  Builds on `findings/exp55-substrate-audit-CLOSED-matched-toggle-c4153.md` (the G1–G4 spec),
  Exp55c re-init control (C4183, n=29, structural init-sensitivity), Exp55 Arm-0 trap def (C4128).
**Launch gate**: do NOT start while Exp54 ArmA (`run_exp54_warmstart.py --full --arm A`, PID
  contending for CPU) is in flight, and not before any remaining exp53 harness block is cleared.
  Design ≠ grading — writing this pre-reg does not peek at any in-flight run (anti-peek held).

---

## The one open item this resolves

Exp55's noise-as-resource arm was killed (NO-GO, C4194/C4217) because Arm 1 moved **three**
variables at once (x0 via `seed*100+r`, shot realization via `seed_simulator=2000+r`, and the noise
model), so no "escape" could be attributed to noise. The C4153 matched control + Exp55c (n=29)
established that noiseless re-init escapes are **structural** (68.3% of realizations escape with the
noise off), so an Arm-1 escape rate carries zero noise-attribution weight.

**One thing survived as genuinely open** (C4153 verdict, part 2): at seed 51, realization r=1, a
*single* clean toggle — same x0 (`seed(5101)`), same `seed_simulator=2001`, noise the only variable —
flipped **0.600 (trapped, noiseless) → 0.680 (escaped, noisy)**. This is the only clean
noise-toggle-positive in the entire Exp55 arc. But N=1, and the audit's own central lesson is that
COBYLA trajectories are hyper-sensitive to the shot realization — so the 0.600→0.680 gap **could
itself be trajectory noise**, not a noise-model effect. C4153 explicitly tagged r=1 as "a candidate
to retest under G1," not a confirmed instance.

**Exp58 is that G1 retest.** It is the *only* design that can tell whether toggling noise — and
nothing else — systematically rescues a genuinely-trapped point.

## Design — the genuine toggle (G1), two-stage for power-per-CPU-hour

Trap point: the **defined** Exp55 trap `x0 = np.random.seed(51); uniform(0,2π,2P)` (the 0.586 trap at
sim=1000). All Exp55 constants reused verbatim (P=3, SHOTS=1024, MAX_ITER=50, ESCAPE_THRESHOLD=0.640,
the FakeMarrakesh-transpiled shared circuit, seed_transpiler pinned). **No reimplementation** — the
runner imports `build_circuit` + `optimize_cobyla_capture` + constants from the live exp55 module.

The genuine G1 toggle, per realization seed `s`:
- **noiseless**: `AerSimulator(seed_simulator=s)`, noise_model=None, optimize at `x0_trap` → `r_off(s)`
- **noisy**:     `AerSimulator(noise_model=FakeMarrakesh, seed_simulator=s)`, optimize at `x0_trap` → `r_on(s)`
- Identical `x0_trap` AND identical `seed_simulator=s` on both sides — **the noise model is the only
  variable.** This is exactly the invariant the original harness falsely claimed.

Realization panel uses a fresh seed namespace `SIM_BASE=3000..` (disjoint from Arm-0's 1000 and
Arm-1's 2000–2004, so it neither collides with nor re-uses any prior realization).

**Two stages** (the efficiency lever — concentrate expensive noisy compute where the test has power):

- **Stage A (cheap, ~31s/run, K_A=24):** noiseless at `x0_trap` across sim ∈ {3000..3023}. Identify
  `Trapped_off = {s : r_off(s) < 0.640}` — the realizations where there is actually a trap for noise
  to rescue. (Seed 51 is borderline/threshold-hugging — C4153 observed it trapped at ~1/3 of
  realizations — so a broad cheap panel is needed to harvest enough trapped realizations.)
- **Stage B (expensive, ~hours/run):** noisy at the **same (x0_trap, s)** for **only** `s ∈ Trapped_off`.
  Running noisy on realizations that escape noiselessly would burn hours where there is no trap to
  rescue — Stage A routing avoids that entirely.

## Metrics (paired; the pairing is what isolates the noise model)

For each `s ∈ Trapped_off`: `Δ(s) = r_on(s) − r_off(s)` (only the noise model differs).
- **rescue_rate** = |{s ∈ Trapped_off : r_on(s) ≥ 0.640}| / |Trapped_off|  (noise flips trapped→escaped)
- **anti_rescue_rate** = |{s : r_off(s) ≥ 0.640 ∧ r_on(s) < 0.640}| / |{s : r_off(s) ≥ 0.640}|
  (noise pushes an escaped realization back below threshold — the symmetric null direction)
- **median Δ over Trapped_off**, plus the sign distribution of Δ.

## Pre-committed decision rule

- **GO (noise-as-resource has support at seed 51):** `median Δ over Trapped_off > 0`
  **AND** `rescue_rate > anti_rescue_rate`. → r=1 was not trajectory noise; escalate to G3 (|T|≥2
  robust traps) for the across-seed headline claim.
- **NO-GO (r=1 was trajectory noise):** `median Δ ≤ 0` **OR** `rescue_rate ≤ anti_rescue_rate`.
  → the lone Exp55 positive does not survive a powered matched toggle; noise-as-resource is closed
  at this substrate.

## Pre-committed power guard (honesty before data)

If `|Trapped_off| < 3` from K_A=24, the seed-51 within-trap test is **underpowered** — report Δ and
rescue counts as an **anecdote, not a rate**, and do NOT issue GO/NO-GO. Instead escalate: assemble a
**robust** trap (G2: traps in ≥⌈2/3·K⌉ of K≥3 noiseless realizations; G3: |T|≥2 via harder instance
or p=5) and run the toggle there. seed 51 is known-borderline, so this guard is expected to bite —
the runner accepts a `--trap-seeds` list so additional robust traps slot in without code change.

## Falsifier (pre-committed)
*If the median paired Δ over the noiselessly-trapped realizations is ≤ 0, the single r=1 positive is
attributable to shot-trajectory variance, not the noise model.* This is the falsifier C4153 deferred
to G1.

## Integrity / collision (C4038)
Own namespaced artifacts only: `results/exp58_g1_checkpoint.json`, `results/exp58_g1_results.json`.
Imports the exp55 module (which is `__main__`-guarded → import is side-effect-free); touches no exp55
checkpoint, no live process. Stage B is opt-in via `--stage B` and reads Stage A's results to pick the
trapped subset — default invocation runs the cheap Stage A only.
