#!/usr/bin/env python3
"""P-CCM v1.0 — parallel scaling of the stabilizer kernel. MEASURED, not assumed.

WHY. The HSS classical arm is chi = 2^(0.23t) INDEPENDENT stabilizer terms — no coordination,
no shared state. That is the ideal parallel shape, and the campaign's runnability figures rest
on a core-count assumption nobody had measured.

I ASSUMED 14x AT 85% EFFICIENCY AND THAT WAS TOO OPTIMISTIC ON TWO COUNTS:
  * this box is an AMD Ryzen 7 9800X3D — EIGHT physical cores with SMT, not sixteen. `nproc`
    reports 16 THREADS, and reading a thread count as a core count is the same proxy-vs-target
    error as counting processes to count monitors.
  * SMT gives compute-bound integer work roughly 1.1-1.3x, not 2x, because both threads on a
    core contend for the same integer units.
So the honest expectation is ~8x from cores and maybe ~10x with SMT — and the point of this
file is to REPLACE that expectation with a number.

GPU: NONE PRESENT ON THIS HOST (no nvidia-smi, no cupy, torch is 2.6.0+cpu, numba reports
cuda unavailable). The assessment of whether a GPU *would* help is recorded in the report
rather than guessed at here.

Python's GIL blocks threads for CPU-bound work, so this uses PROCESSES.

Substrate: claude-fable-5, Whisper C5020. Creator directive: "parallelize it across the 16 cores".
"""
import os
import sys
import time
import json
import multiprocessing as mp

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _worker(args):
    """One batch of inner products. Imports inside the worker so each process has its own
    module state and numpy is not shared across the fork in a way that skews timing."""
    seed, n, count = args
    import stabilizer_rank_kernel as ref
    from stabilizer_rank_bitpacked import PackedState, inner_product
    from calibrate_stabilizer_term import x_tilde_state

    rng = np.random.default_rng(seed)
    pairs = []
    for _ in range(count):
        xs = PackedState.from_reference(x_tilde_state(n, rng.integers(0, 2, size=n)))
        phi = PackedState.from_reference(ref.random_state_via_extend(n, n, rng))
        pairs.append((xs, phi))
    t0 = time.perf_counter()
    out = 0
    for xs, phi in pairs:
        r = inner_product(phi, xs)
        out += r[0]
    return time.perf_counter() - t0, count, out


def measure(n, total, nprocs):
    """Wall-clock for `total` inner products spread over `nprocs` processes."""
    per = max(1, total // nprocs)
    args = [(1000 + i, n, per) for i in range(nprocs)]
    t0 = time.perf_counter()
    if nprocs == 1:
        res = [_worker(args[0])]
    else:
        with mp.Pool(nprocs) as pool:
            res = pool.map(_worker, args)
    wall = time.perf_counter() - t0
    done = sum(r[1] for r in res)
    return wall, done


def main():
    n = 100
    total = 96
    print("PARALLEL SCALING OF THE STABILIZER KERNEL — measured\n")
    print(f"  host: {os.cpu_count()} logical threads, 8 physical cores (Ryzen 7 9800X3D)")
    print(f"  workload: {total} InnerProduct calls at n={n}, chi-style independent terms\n")

    base = None
    rows = []
    print(f"  {'procs':>6} {'wall (s)':>10} {'per call (ms)':>14} {'speedup':>9} {'efficiency':>11}")
    for p in (1, 2, 4, 8, 12, 16):
        wall, done = measure(n, total, p)
        if base is None:
            base = wall
        sp = base / wall
        eff = sp / p
        rows.append({"procs": p, "wall_s": wall, "per_call_ms": wall / done * 1000,
                     "speedup": sp, "efficiency": eff})
        print(f"  {p:>6} {wall:>10.2f} {wall/done*1000:>14.2f} {sp:>8.2f}x {eff*100:>10.0f}%")

    best = max(rows, key=lambda r: r["speedup"])
    print(f"\n  BEST MEASURED: {best['speedup']:.2f}x at {best['procs']} processes "
          f"({best['efficiency']*100:.0f}% efficiency)")
    print(f"  I had ASSUMED 14x. Measured is {best['speedup']:.2f}x — "
          f"{'below' if best['speedup'] < 14 else 'at or above'} the assumption.")

    dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results",
                       "stabilizer_parallel_scaling_v1.json")
    with open(dst, "w") as fh:
        json.dump({"card": "stabilizer_parallel_scaling", "version": "1.0", "cycle": "C5020",
                   "substrate": "claude-fable-5", "n": n, "total_calls": total,
                   "host": {"logical_threads": os.cpu_count(), "physical_cores": 8,
                            "cpu": "AMD Ryzen 7 9800X3D", "gpu": "NONE PRESENT"},
                   "rows": rows, "best": best,
                   "assumed_before_measuring": 14.0,
                   "note": ("nproc reports THREADS not CORES; SMT gives compute-bound integer "
                            "work ~1.1-1.3x, not 2x. Reading a thread count as a core count is "
                            "the proxy-vs-target error.")}, fh, indent=2)
    print(f"\n  written: results/{os.path.basename(dst)}")


if __name__ == "__main__":
    mp.set_start_method("fork", force=True)
    main()
