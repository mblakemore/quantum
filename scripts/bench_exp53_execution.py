#!/usr/bin/env python3
"""
Exp53 execution-strategy micro-benchmark (Elder C5876).

PURPOSE: Before resuming the Exp53 p5_1024sh arm (~25h of compute, the 15h-runaway
I killed at C5860), determine the FASTEST execution strategy for a single noisy QAOA
evaluation on the actual workload (p=5, 20q, FakeMarrakesh noise). Advisor-framed:
the bottleneck is shot-trajectory COUNT, not statevector size (16MB at 20q), so the
GPU question is whether the batched-shots GPU path helps — NOT a naive device='GPU'.

Compares per single 1024-shot evaluation:
  1. CPU default (auto method)            -- baseline (what the harness uses)
  2. CPU explicit statevector             -- confirm method
  3. GPU naive (device='GPU')             -- the naive (likely-losing) path
  4. GPU batched-shots (batched_shots_gpu)-- the path that SHOULD help at small q
And reports core count for the orthogonal lever: multiprocessing across the 7
remaining independent seeds.

Reports the auto-selected simulation METHOD (gates whether GPU is even relevant —
if MPS, GPU is moot). Verifies all methods produce a consistent cut ratio.
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from run_exp46_fast import (
    EDGES_20, N_QUBITS_20, brute_force_max_cut,
    build_parameterized_xbasis_qaoa, evaluate_with_transpiled,
)
from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime.fake_provider import FakeMarrakesh

SHOTS = int(os.environ.get("BENCH_SHOTS", "1024"))
P = 5
OPT_LEVEL = 1

print("=" * 64)
print(f"EXP53 EXECUTION-STRATEGY BENCHMARK | p={P} q={N_QUBITS_20} shots={SHOTS}")
print(f"cores={os.cpu_count()}")
print("=" * 64, flush=True)

fake = FakeMarrakesh()
noise_model = NoiseModel.from_backend(fake)
n_qubits = N_QUBITS_20
edges = EDGES_20
max_cut = brute_force_max_cut(n_qubits, edges)

qc, gammas, betas = build_parameterized_xbasis_qaoa(P, n_qubits, edges)
base_sim = AerSimulator(noise_model=noise_model)
tqc = transpile(qc, backend=base_sim, optimization_level=OPT_LEVEL)
print(f"transpiled depth={tqc.depth()} | params={len(gammas)+len(betas)}", flush=True)

# Fixed params so every method evaluates the identical bound circuit.
np.random.seed(42)
params = np.random.uniform(0, np.pi, 2 * P)

def run_one(label, sim, n_reps=1):
    ratios, times = [], []
    method_used = None
    for _ in range(n_reps):
        t0 = time.time()
        try:
            r = evaluate_with_transpiled(params, tqc, gammas, betas, P, sim,
                                         edges, max_cut, n_qubits, SHOTS)
        except Exception as e:
            print(f"  {label:32s} FAILED: {type(e).__name__}: {str(e)[:80]}", flush=True)
            return None
        dt = time.time() - t0
        ratios.append(r); times.append(dt)
    # method actually used (from result metadata of a fresh run)
    try:
        bound = tqc.assign_parameters(
            {**{gammas[i]: params[i] for i in range(P)},
             **{betas[i]: params[P+i] for i in range(P)}})
        meta = sim.run(bound, shots=8).result().results[0].metadata
        method_used = meta.get("method", "?")
    except Exception:
        method_used = "?"
    best = min(times)
    print(f"  {label:32s} {best:8.1f}s  ratio={np.mean(ratios):.4f}  method={method_used}", flush=True)
    return {"label": label, "time_s": best, "ratio": float(np.mean(ratios)), "method": method_used}

results = []
# 1. CPU default (harness baseline)
results.append(run_one("CPU default (auto)", AerSimulator(noise_model=noise_model)))
# 2. CPU explicit statevector
results.append(run_one("CPU statevector", AerSimulator(noise_model=noise_model, method="statevector")))

# GPU paths — guarded: only if GPU present in available_devices
gpu_ok = "GPU" in AerSimulator().available_devices()
print(f"\n  GPU available in aer: {gpu_ok}", flush=True)
if gpu_ok:
    # 3. GPU naive
    results.append(run_one("GPU naive (device=GPU)",
                           AerSimulator(noise_model=noise_model, device="GPU")))
    # 4. GPU batched shots
    results.append(run_one("GPU batched_shots",
                           AerSimulator(noise_model=noise_model, device="GPU",
                                        batched_shots_gpu=True)))
else:
    print("  (skipping GPU paths — not in aer.available_devices())", flush=True)

print("\n" + "=" * 64)
results = [r for r in results if r]
if results:
    base = next((r for r in results if r["label"] == "CPU default (auto)"), results[0])
    print(f"BASELINE (CPU default): {base['time_s']:.1f}s/eval")
    for r in sorted(results, key=lambda x: x["time_s"]):
        spd = base["time_s"] / r["time_s"] if r["time_s"] else 0
        print(f"  {r['label']:32s} {r['time_s']:8.1f}s  {spd:5.2f}x  method={r['method']}")
    # multiprocessing projection (7 remaining seeds, ncores)
    cores = os.cpu_count() or 1
    per_seed_iters = 50  # MAX_ITER_P5
    fastest = min(r["time_s"] for r in results)
    serial_h = base["time_s"] * per_seed_iters * 7 / 3600
    mp_workers = min(7, cores - 1)
    mp_h = base["time_s"] * per_seed_iters * 7 / mp_workers / 3600
    print(f"\n  REMAINING ARM (7 seeds × {per_seed_iters} iters):")
    print(f"    serial CPU-default:        ~{serial_h:.1f}h")
    print(f"    CPU multiproc ({mp_workers} workers): ~{mp_h:.1f}h")
print("=" * 64)
