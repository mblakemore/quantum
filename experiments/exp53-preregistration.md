# Exp53 Pre-Registration: Depth vs Shots Tradeoff
**Author**: Elder C5846 | **Date**: 2026-06-15
**Based on**: Finding 26 (SPSA=landscape ceiling) + Finding 27 (COBYLA optimal at 1024sh, plateau at 2048sh)

---

## Motivation

Finding 27 established that 1024 shots is the optimal COBYLA budget for p=3 QAOA on EDGES_20/FakeMarrakesh
(90% escape rate, no gain at 2048sh). Finding 26 showed landscape topology governs the ceiling, not
optimizer noise.

The next question: **Is p=3 + 1024sh the right place to invest, or does p=5 + fewer shots beat it?**

At p=3 we have 6 parameters (2p). At p=5 we have 10 parameters. Two competing forces:
- **Depth helps**: p=5 has greater expressibility — can represent more complex landscapes
- **Depth hurts**: more parameters → harder optimization landscape (curse of dimensionality)
  + deeper circuits → more FakeMarrakesh decoherence noise

Finding 25 established that COBYLA's escape rate is a *landscape* property. Does a deeper circuit
create a more escape-friendly landscape (richer minima structure) or a more trap-heavy one?

---

## Hypotheses (Pre-registered)

**H1** (Depth penalty at equal shots): p=5 COBYLA escape rate at 1024 shots < p=3 COBYLA at 1024 shots.
Predicted direction: p=5 will be LOWER than 90%. Threshold: p5_1024sh < 80% (10pp gap).
Reasoning: More parameters + more decoherence from deeper circuits outweighs expressibility gain;
at p=3 we're already hitting the landscape ceiling, not an expressibility ceiling.

**H2** (Depth penalty at low shots): p=5 COBYLA escape rate at 256 shots < p=3 COBYLA at 256 shots (60%).
Predicted direction: p=5 + 256sh < 60%. Threshold: p5_256sh < 50%.
Reasoning: Low shots + deeper circuit = double penalty (noise in evaluations + parameter-space density).

**H3** (Depth gap widens with shots): The penalty gap between p=3 and p=5 is LARGER at 1024 shots
than at 256 shots.
Formula: gap_1024 = p3_1024sh − p5_1024sh > gap_256 = p3_256sh − p5_256sh
Reasoning: At low shots, noise masks the landscape signal for both depths; at high shots, the
landscape difference becomes the limiting factor. p=5's parameter-space curse only reveals
itself when evaluation noise is reduced enough to see the landscape clearly.

**Calibration:**
- H1: 65% confidence (depth penalty likely but not certain — expressibility could outweigh it at p=5)
- H2: 70% confidence (double penalty more likely to dominate at low shots)
- H3: 55% confidence (non-obvious; gap could also narrow if p=5 escapes more with better shots)

---

## Design

### Problem Instance
- Same: EDGES_20 from run_exp46_fast.py (20 qubits, 30 edges, MaxCut=26)
- Same: FakeMarrakesh AerSimulator (consistent noise model across Exp46-53)
- Same escape threshold: 0.640 (ratio-to-max-cut)
- Same seeds: 42-51 (10 seeds, same as Exp51/52)

### Arms

**Reused from Exp51/52 (NO rerun):**
- Arm A: p=3, COBYLA, 256sh → 6/10 = 0.60 (Exp51 Phase A)
- Arm B: p=3, COBYLA, 1024sh → 9/10 = 0.90 (Exp51 Phase C / Exp52)

**New runs:**
- Arm C: p=5, COBYLA, 256 shots, seeds 42-51, max_iter=50 (more params → more iterations)
- Arm D: p=5, COBYLA, 1024 shots, seeds 42-51, max_iter=50

Total new runs: 20 (2 × 10 seeds)

### Key Change vs Exp52
Only `p` changes (3 → 5). All else identical (same EDGES_20, same noise model, same seeds,
same optimizer, same escape threshold). This is a controlled single-variable experiment.

### Parameter Count
- p=3: 6 QAOA parameters (3 gammas + 3 betas)
- p=5: 10 QAOA parameters (5 gammas + 5 betas)
- max_iter increased 30→50 to give COBYLA room to search the larger parameter space

### Expected Timing (FakeMarrakesh)
- Arm C (p=5, 256sh, 10 seeds): ~30-60 min (deeper circuit, same shots as Exp51-A)
- Arm D (p=5, 1024sh, 10 seeds): ~90-180 min (both depth and shots add cost)
- Total wall time: ~2-4 hours (background run)

---

## Success Criteria

H1 CONFIRMED: p5_1024sh < 80% escape rate
H1 REFUTED: p5_1024sh ≥ 80% (p=5 competitive with p=3 at 1024sh)

H2 CONFIRMED: p5_256sh < 50% escape rate
H2 REFUTED: p5_256sh ≥ 50% (p=5 matches p=3 performance even at low shots)

H3 CONFIRMED: (p3_1024sh - p5_1024sh) > (p3_256sh - p5_256sh)
H3 REFUTED: gap narrows or reverses at high shots

---

## Connection to Research Arc

Exp53 completes the "optimization geometry" trilogy:
- Exp51: Optimizer choice is not the escape lever (COBYLA > SPSA)
- Exp52: Shot budget curve — 1024sh is optimal ceiling for p=3
- **Exp53: Depth tradeoff — is p=5 worth the extra parameters?**

Together these three experiments fully characterize the operational design space for this QAOA
instance: optimal optimizer (COBYLA), optimal shots (1024), optimal depth (p=3 or p=5?).

If H1+H2 CONFIRMED (p=5 worse): The finding is "p=3 is the practical sweet spot for this graph
size + noise model. Going deeper isn't worth it — the parameter landscape becomes harder without
gaining enough expressibility advantage."

If H1+H2 REFUTED (p=5 competitive): "The expressibility advantage of deeper circuits compensates
for the parameter curse — deeper QAOA remains viable within the CZ-gate budget ceiling."

---

## Next Steps After Exp53

If p=5 penalized (H1+H2 confirmed):
→ Exp54: Cross-graph-size depth ceiling — does the p=3 sweet spot hold for 30-node or 40-node graphs?
→ Or: investigate the exact p where the crossover from "more depth helps" to "more depth hurts" occurs

If p=5 competitive (H1/H2 refuted):
→ Exp54: p=7 or p=10 — find the actual depth ceiling for this noise model
→ Pre-reg QPU test once quota frees June 21 (p=5 vs p=3 on real marrakesh hardware)

---

## Coordination Note
Ember C3731 is running Exp52 SPSA final arm (PID 59915, Seeds 42-51 at ~6h+ runtime).
Exp53 is fully parallel — uses same seeds/graph but different p value, no data dependency.
Elder C5846 authors this pre-registration and launches Arm C + Arm D.

---

## ⚠️ C5860 EXECUTION STATUS — RUNAWAY KILLED, HARNESS HARDENED, RUN DEFERRED

**Elder C5860 (2026-06-15 ~18:40 ET)** — operational correction, hypotheses UNCHANGED (still pre-registered, ungraded).

### What happened
The C5852 launch of `run_exp53_depth_vs_shots.py` was found running **15+ hours** (PID 100765,
started 07:38, ~8050 CPU-min, ~8.8× core saturation) with a **0-byte log and no results file** —
the run was block-buffered (no `-u`/flush) and had **no checkpointing**. A second duplicate launch
attempt (`run_exp53_depth_tradeoff.py`, "Launched C5852") had already died silently on session-end
(empty log, no results) — the classic un-detached-process loss.

### Root causes (4)
1. **No checkpointing** — results were written only by the final `json.dump`; any kill = total loss.
2. **No observability** — block-buffered stdout to a file → 15h of zero visible progress.
3. **Wrong time estimate** — pre-reg said "~2-4 h"; reality is **~15 h+**. p=5 noisy-*trajectory*
   simulation (FakeMarrakesh full noise model, per-shot statevector trajectory) scales with the
   deeper transpiled circuit. A 1-seed/256sh smoke at 4 threads did **not** finish in 280 s.
4. **Duplicate scripts** — two scripts implement the identical 20-run Exp53 (`depth_vs_shots` C5846
   + `depth_tradeoff` C5852). Canonical = `depth_vs_shots`. (Not deleted — not authored this cycle;
   surfaced for owner to reconcile.)

### Fix shipped (C5860)
`run_exp53_depth_vs_shots.py` hardened (pure-additive, py_compile OK):
- **Atomic per-seed checkpoint** → `results/exp53_checkpoint.json` (write-tmp + `os.replace`).
- **Resume**: on relaunch, completed seeds are skipped (unit-verified: run2 over seeds 42-46 after a
  42-44 checkpoint made only 2 new optimizer calls).
- **`flush=True`** on arm/seed prints → progress visible even when redirected to a file.

### Why the full run was NOT relaunched this cycle
Killing the runaway **freed the machine** (load 17.8 → 0.49). Tue 6/16 is the QQQ3 v9.1 bot's first
clean pure-execution day in FOMC week; a ~15 h CPU-saturating sim would contend with the
latency-sensitive bot (the primary goal). **Relaunch deferred to a market-closed window (weekend,
bot dormant)**, ideally thread-capped (`OMP_NUM_THREADS`) to leave headroom. Resume-safe now, so it
can run in segments across cycles. Command:
```bash
cd /droid/repos/quantum/scripts && setsid nohup python3 -u run_exp53_depth_vs_shots.py \
  > ../results/exp53_log.txt 2>&1 < /dev/null &   # resumes from checkpoint if interrupted
```
