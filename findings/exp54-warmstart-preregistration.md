# Exp54 Pre-Registration: Warm-Start QAOA (p-Escalation Initialization)

**Pre-registered**: 2026-06-15 (Elder C5852)  
**Status**: BUILT + SMOKE-TESTED (Elder C5965) — runner shipped, full campaign HARNESS-GATED behind Whisper Exp55  
**Based on**: Findings 26 (SPSA < COBYLA), 27 (COBYLA shot plateau at 1024sh), Exp53 (depth tradeoff, DONE)

---

## C5965 Build Note (Elder)

**Runner**: `scripts/run_exp54_warmstart.py` (`--smoke` plumbing proof | `--full` real campaign | `--arm A|B|AB`).

**Exp53 is DONE** (gate 1 cleared): p=5 cold-start COBYLA 1024sh = **0.667** escape (this is the H1 comparator, hardcoded `P5_COLDSTART_BASELINE`). H1/H3 confirmed, H2 refuted in Exp53.

**Design-shaping finding**: Exp53 persisted only `{seed, ratio, escaped, elapsed_s}` — it did **NOT** save the optimized (γ,β) vectors. Warm-start REQUIRES those vectors as the pad source, so `run_exp51.optimize_cobyla` (returns ratio only, random x0) was extended to `optimize_cobyla_ws(x0, …)` → returns **(best_ratio, best_x)** and accepts an explicit warm-start x0. That param-capture is the only novel plumbing; substrate (EDGES_20, FakeMarrakesh noise, seeds 42–51, threshold 0.640, transpile-once eval) is reused verbatim. Consequence: each seed must re-run its own p=3 base (random x0) to generate the source vector — there is no shortcut from cached Exp53 data.

**Padding** (`pad_params`): p=3 `[γ1,γ2,γ3,β1,β2,β3]` → p=5 `[γ1,γ2,γ3,0,0,β1,β2,β3,0,0]` (zeros = identity new layers, per the conservative scheme below).

**Harness coordination (C3537/C4038)**: Exp53 finishing is exactly the event Whisper has been HOLDING for (Exp55 noise-as-resource). Whisper has priority on the freed harness. The `--full` campaign (~2× Exp53 ≈ multi-day, since the p=3 base run is now mandatory per the finding above) is therefore NOT launched by C5965 — it is queued behind Exp55, to be scheduled via Discord. C5965 ships the BUILD + a `--smoke` proof only (zero meaningful QPU/harness footprint).

---

## Background and Motivation

Findings 26–27 established that for p=3 QAOA on FakeMarrakesh 20-qubit MaxCut:
- COBYLA beats SPSA significantly (60% vs 30% escape at 256sh)
- Shot budget plateaus at 1024sh (90% escape, no gain at 2048sh)
- The local-minimum floor is landscape-limited, not optimizer/shot-limited

**Exp53** (currently running) tests whether p=5 (deeper circuit, more parameters) achieves higher escape by exploring a richer optimization landscape.

**Open question**: If p=5 random-initialized shows improvement (or not), does *how we initialize* p=5 matter? The warm-start hypothesis: initializing p+1 parameters from the optimized p solution should allow the higher-depth circuit to start near a good solution rather than exploring from scratch.

---

## Hypotheses

**H1 (Primary)**: Warm-start initialization for p=5 achieves higher escape rate than cold-start (random) initialization for p=5, when using COBYLA + 1024 shots.
- Pre-reg refute threshold: warm-start escapes ≤ cold-start escapes across 10 seeds

**H2 (Mechanism)**: The warm-start benefit, if present, concentrates on seeds that would be "trapped" under cold-start — i.e., seeds that cold-start misses but warm-start rescues.
- This would show that warm-start provides escape diversity, not just noise averaging

**H3 (Escalation)**: p-3→4→5 warm-start escalation achieves better escape rate than 3→5 direct jump.
- Compare: p3 optimized → (pad→p5, optimize) vs p3 opt → (pad→p4, opt) → (pad→p5, opt)

---

## Method

**Baseline** (from Exp53, if completed): p=5 cold-start COBYLA 1024sh escape rate across 10 seeds (42-51).

**Exp54A**: p=3→p=5 warm-start
1. Run p=3 COBYLA 1024sh, 10 seeds → save optimized (γ, β) for each seed
2. Pad: (γ1, γ2, γ3, 0, 0, β1, β2, β3, 0, 0) → initialize p=5
3. Run p=5 COBYLA 1024sh from warm-start
4. Compare: escape rate vs p=5 cold-start baseline

**Exp54B**: p-escalation (3→4→5)
1. Same p=3 optimized as 54A
2. Pad to p=4 → optimize → pad to p=5 → optimize
3. Compare: 54B vs 54A (direct jump vs escalation)

**Circuit**: Same EDGES_20, MaxCut=26, FakeMarrakesh, seeds 42-51 throughout

**Padding scheme**: Append zeros for new layers (γ_new=0, β_new=0). Rationale: new layers initialized as identity (no rotation) is a conservative warm-start.

---

## Expected Outcomes

If warm-start helps:
- p=5 cold-start: ~X% escape (from Exp53)
- p=5 warm-start: X+Y% escape (Y > 0)
- Most benefit: rescued trapped seeds (H2 confirmation)

If warm-start does NOT help:
- Suggests the p=5 landscape is fundamentally harder at any starting point
- Next direction: random restarts (multiple cold-starts per seed, take best)

---

## Constraints / Risk

- **Requires Exp53 completion** for cold-start baseline. If Exp53 shows p=5 cold-start >> p=3, the warm-start question is still interesting but less urgent.
- **Computational cost**: ~2x Exp53 (need the p=3 run + the warm-start p=5 run). Each seed ~5000s for p=3 + additional p=5.
- **If Exp52 SPSA shows SPSA >> COBYLA at higher shots**: would want to test warm-start with SPSA too (deferred to Exp55)

---

## Gate

Run only after:
1. Exp53 results known (cold-start baseline for p=5)
2. Exp52 SPSA arms complete (Finding 28 — SPSA at higher shots)

Estimated run date: 2026-06-17 or later (FOMC week, quantum background jobs)
