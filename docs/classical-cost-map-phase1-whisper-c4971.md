# Classical Cost Map (Item 2 / `P-CCM`) — Phase 1 built: the metering harness

*Whisper C4971, 2026-07-21, substrate claude-fable-5. Creator directive: "Build Item 2, the
classical-cost-map harness." Plan: [advantage-annex-execution-plan-whisper-c4970.md](advantage-annex-execution-plan-whisper-c4970.md)
§A Item 2. This delivers **Phase 1 only** (the meter + its self-test); Phases 2–5 remain.*

## What Phase 1 is

`tools/classical_cost_meter.py` — the solver-agnostic instrument that meters ONE unit of classical
simulation work and returns a frozen row. Every future crossover / race statement (Items 3–4)
*quotes* rows this produces, so the meter had to be trustworthy before any curve is drawn.

Run it:
```
python3 tools/classical_cost_meter.py --selftest      # 6/6 checks, ~5s
python3 tools/classical_cost_meter.py --fingerprint   # machine + preflight + race config JSON
```

## The one load-bearing decision: fork + os.wait4 + SIGKILL

Each solve runs in a **forked child**, reaped with `os.wait4` (real per-child rusage), killable with
`SIGKILL` (real censoring). Four requirements each fail without it, so it is not optional:

| requirement | why in-process fails | the fix |
|---|---|---|
| timeout / censoring | a native C++ solver (Aer) can't be interrupted from Python; a thread-pool timeout returns control while the C++ keeps eating cores | only a separate OS process can be SIGKILL'd to actually stop at the cap |
| shared-machine safety (C4415) | a "timeout" that leaves the computation running IS the saturation failure mode on a box shared with Elder/Ember | killable child = the abort discipline made real; `preflight_cpu()` is the pre-launch half |
| peak memory | `tracemalloc` misses Aer's C++ allocations | per-child `ru_maxrss` via wait4 is exact and un-contaminated by prior rows |
| CPU accounting | in-process rusage mixes rows | per-child user+sys via wait4 |

Solver-agnostic by construction — works for the non-Aer stabilizer-rank adversaries gap **G1**
demands (racing only Aer would overstate the quantum side).

## The correctness gate (crown jewel), and its coupling to the MPS cost axis

Every row REQUIRES a `verified` field; the Phase-5 card builder must **structurally refuse to place
an unverified row on a cost curve — segregate, never drop** (a fast wrong solver poisons the map —
the Exp144 detector lesson applied classically). Three row states, all SEEN to fire in the self-test:

- **verified** — worker recomputed the answer from ground truth and it matched → eligible for a curve.
- **unverified (segregated)** — the self-test's *poisoned* solver lies (`verified=True`, answer
  `deadbeef`); the row preserves the lie so a second seat (Ember replicates rows) catches it. This
  is *why* verification is computed by the worker from ground truth AND independently replicated.
- **censored** — a 60 s worker under a 2 s cap is SIGKILL'd at 2.0 s and recorded `>cap`, never
  dropped.

**MPS gate = cost axis (the subtle one).** Statevector is exact; MPS at fixed bond dimension χ is
approximate *by construction* — too small a χ returns the WRONG answer. So for MPS,
`verified` = "returned the planted answer AT THIS χ", and **the minimum χ that verifies IS the cost
signal**. Verification is per-(instance, χ); the "verify small, trust large" shortcut is invalid
here. Demonstrated on GHZ₈ in the self-test:

```
mps chi-gate: verified-by-chi={1: False, 2: True, 8: True} -> min verifying chi=2 (= the GHZ_8 cost signal)
```

χ=1 (product state) truncates GHZ to `['00000000']` (missing the `11111111` branch) → `verified=False`.

## Honesty fences already wired in

- **Energy (gap G2)** — RAPL `energy_uj` is root-only since the CVE-2020-8694 side-channel patch and
  is not chmod-fixable on this box. Rows emit `energy_j: null, energy_method:
  "rapl_permission_denied"`. A TDP×busy-time number is produced ONLY when a TDP is explicitly
  supplied, labeled `energy_bound_not_measured` (an upper bound, not a measurement). No fabricated
  estimates. `intel-rapl` is the powercap FRAMEWORK name — the fingerprint stamps the real vendor
  (**AMD** here) so no one misreads it.
- **Threads** — "CPU-seconds" is meaningless without the thread config, so every row records it. The
  self-test already surfaces the empirical reason we meter rather than trust the flag: with
  `max_parallel_threads=1`, `cpu_s (1.18) > wall_s (0.38)` — Aer does not fully honor the flag, so
  single-thread vs all-core must be *measured*, not declared.
- **Race config declared in advance** — `RACE_CONFIG` (all-core, performance governor) is frozen in
  the source now, C4971, so the Item-4 race config is not chosen post-hoc to favor either arm.

## Machine (this build)

`AMD Ryzen 7 9800X3D` · 16 logical cores · 60.4 GB · governor `performance` · Linux 6.17 · Py 3.12.

## GPU note (Creator offered 32GB AMD, C4971)

`AerSimulator.available_devices()` advertises `['GPU']`, but an actual GPU run raises
`RuntimeError: Simulation device "GPU" is not supported on this system` — the installed
`qiskit-aer` wheel is CUDA-flavored while the box is AMD/ROCm (`/opt/rocm` present). A working GPU
adversary (which gap **G1** would welcome — 32 GB pushes exact statevector to higher n) needs a
**ROCm rebuild of qiskit-aer** (experimental HIP path). Decision: harness carries a first-class
`device` slot in the fingerprint so a working GPU backend drops in as another config row; standing
up ROCm-Aer is a scoped follow-up (good Uhura infra-delegation candidate), NOT on the critical path.

## Remaining (Phases 2–5, plan §A Item 2)

2. **Solver bench** — the three solver classes wrapped as workers, each correctness-gated; plus the
   **G1 survey-and-adopt** pass for a stronger stabilizer-rank impl (Bravyi–Gosset lineage) or, if
   none adoptable, a published-scaling lower bound labeled as such.
3. **Instance generator** — the hidden-shift family (shared with Item 3, its own freeze), HLF
   (F113 receipts cross-check), random-Clifford+T control.
4. **Sweep + fit** — log-cost vs n (statevector), vs T (stabilizer-rank), vs χ (MPS); censored fits
   for `>cap`; single-thread AND all-core; **preflight headroom gate before launch** (C4415).
   **G6**: deliver the stabilizer-rank curve as v0.5 first — it's the only column Item 3 needs, and
   shipping it early unblocks the scout ~1 cycle sooner.
5. **Card** — `results/classical_cost_map_v1.json` + doc, attenuation-map freeze discipline; future
   races quote it and each race grades its prediction for free.

**Roles** (plan): Whisper builds · Elder red-teams fits + correctness gates · Ember replicates
sampled rows on a second machine (machine-relativity → a variance column, not a dispute).
