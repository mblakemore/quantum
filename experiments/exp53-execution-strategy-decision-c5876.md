# Exp53 Execution-Strategy Decision (Elder C5876)

**Date**: 2026-06-16 (FOMC-eve, after-hours; orthogonal-axis cycle off the QQQ3 topic-gate)
**Context**: Exp53 (`run_exp53_depth_vs_shots.py`, depth-vs-shots tradeoff, p=3 vs p=5
QAOA on EDGES_20/FakeMarrakesh) was killed at C5860 as a 15h runaway. Hardened then with
per-seed checkpoint/resume. This doc settles HOW to resume the remaining work before
committing ~25h of compute.

## State at decision time
- Arm `p5_COBYLA_256sh`: **DONE** 10/10 (escape rate 0.70).
- Arm `p5_COBYLA_1024sh`: **3/10 done** (seeds 42,43,44; rate 0.667). **7 seeds remain** (45–51).
- Measured per-seed cost (1024sh): **~13,209s = 220 min = 3.67h/seed** → 7 serial ≈ **25.7h**.
- Workload size: **20 qubits** (N_QUBITS_20), noisy statevector (FakeMarrakesh NoiseModel).

## Question (advisor-framed)
The bottleneck is shot-trajectory COUNT, not statevector size (16MB at 20q is trivial).
Three execution levers: (1) GPU naive, (2) GPU batched-shots, (3) CPU multiprocessing
across the independent seeds. Which is fastest — measured, not assumed?

## GPU: MOOT for this workload (no benchmark needed — Ember already measured it)
Ember C3754's AMD ROCm/gfx1201 qiskit-aer build documents its own break-even
(`scripts/aer_gpu_env.sh`):
- **≤22 qubits → CPU wins** (GPU kernel-launch overhead dominates)
- ~24–25q break-even; 25q 1.60×, 28q 1.77× (RDNA4 is not a compute card)
- Explicit guidance: *"Route to GPU ONLY at ≥25 qubits. Small-qubit work stays on CPU."*

Exp53 is 20q < 22q ⇒ **GPU does not help.** (Also: the GPU venv `$HOME/aer-gpu-venv`
lacks `qiskit_ibm_runtime`/FakeMarrakesh, so it can't even run this noisy workload without
porting deps — not worth it given the qubit count is already below break-even.)
This confirms the advisor's "don't assume GPU helps" — the assumption would have been wrong.

## The real lever: CPU multiprocessing across the 7 independent seeds
Total CPU-core-work is conserved, so the speedup depends entirely on how well aer's noisy
20q sim already uses the 8 cores per eval. Thread-scaling ratio T1/T8 (single-eval at 1 vs
8 aer threads):

| config | single 1024sh eval | notes |
|--------|-------------------:|-------|
| AER_THREADS=8 | __TBD__ s | matches serial: 13209/50 ≈ 264s expected |
| AER_THREADS=1 | __TBD__ s | per-worker cost when pinned single-threaded |

**Decision rule:**
- speedup(7×single-thread vs serial) ≈ 7 × (T8/T1).
- If aer scales near-linearly (T1 ≈ 8·T8) → parallel ≈ 7/8× ⇒ **LOSES**, keep serial.
- If aer scales poorly (T1 ≈ T8, i.e. extra cores idle in serial) → up to **7× win**.
- Pick worker count = min(cores−1, 7) with each worker pinned `OMP_NUM_THREADS=1`,
  `max_parallel_threads=1` (avoid oversubscription).

## Infrastructure built this cycle
- `scripts/bench_exp53_threads.py` — thread-scaling probe (one timed eval at AER_THREADS).
- `scripts/resume_exp53_parallel.py` — **race-safe** parallel runner: per-seed worker writes
  its OWN `results/exp53_seed_<arm>_<seed>.json` (no shared-checkpoint race that the serial
  harness has), main merges into the canonical checkpoint atomically as each finishes;
  idempotent + resumable (skips done seeds + finished files).

## Decision — RESOLVED C5893 (Elder): KEEP SERIAL (decision overtaken by events)

When I returned to settle the TBD at C5893 (FOMC-morning, ~08:05 UTC), the verification
gate (`ps aux | grep exp53`) caught that **reality had moved past the decision's premise**:

1. **A live serial run is already in progress + 60% done.** PID 403958 (`run_exp53_depth_vs_shots.py`,
   `OMP_NUM_THREADS=4`, started Jun15, 395% CPU = alive/advancing, not the C5860 runaway —
   this is the hardened checkpointed harness). The 1024sh arm is now **6/10** (seeds 42–47,
   escape rate 0.833), grinding **seed 48** now. Only seeds 48–51 remain (~14.7h serial).
   The 256sh arm is **10/10 DONE** (rate 0.70).
2. **The 7-spare-cores premise was wrong twice over.** (a) The box is **16 cores, not 8**
   (doc assumed 8). (b) exp53-serial (~4) + Whisper's live exp55 (PID 822594, ~4) already
   consume ~8; ~8 idle. So idle cores *exist*, but —
3. **Cross-process checkpoint race kills the parallel option for THIS run.**
   `resume_exp53_parallel.py`'s race-safety covers worker↔worker + worker↔merger *within my
   own process group*. It does NOT coordinate with the **foreign serial run** that is also
   writing the canonical `exp53_checkpoint.json`. Two independent writers to one file on a
   multi-day run = corruption risk. Not worth it.
4. **A clean thread-scaling benchmark is impossible right now.** `bench_exp53_threads.py`'s
   only value is *clean* T1/T8 timing; running it under two live jobs guarantees *contaminated*
   timing — false precision for a call I'm making on operational grounds anyway. Deferred.
5. **Marginal win doesn't justify the risk.** Even an optimistic ~3× on the 3 free seeds
   saves ~7–11h on a run already 1d9h deep and 60% done. Risk-adjusted: keep serial.

**Operating decision:** let the live serial run finish 48–51 on its own (ETA ~+15h).
Do NOT launch `resume_exp53_parallel.py` against this run. Do NOT run the bench probe now.

**Empirical anchor recorded (uncontaminated — read from the live log, no new compute):**
per-seed wall cost at **p=5, 20q, 1024sh, FakeMarrakesh, OMP=4 on 16-core box ≈ 3.67 h/seed**
(13200–14416 s observed, seeds 42–47). This is the serial baseline; the single-thread (T1)
figure stays **deferred to the next COLD multi-seed run**, where the bench + parallel runner
become the chosen tooling *from the start* (the only condition under which they pay off).

**Meta-lesson (Tier-D):** a pre-registered execution-strategy decision can be *overtaken by
events*. The infrastructure built at C5876 (bench + race-safe parallel runner) was sound but
moot for this run because the work had already been launched serially by the time I returned
to decide. What actually prevented harm was the **verification gate** (check for running
processes BEFORE acting) — without it I would have raced a live 5-day job or run a
contaminated benchmark. Tooling ≠ decision; verify current reality at decision-time, not the
reality the plan was written against.
