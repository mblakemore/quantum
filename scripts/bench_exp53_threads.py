#!/usr/bin/env python3
"""Exp53 thread-scaling probe (Elder C5876). Times ONE 1024-shot noisy eval at the
aer thread count given by AER_THREADS env. Tells us whether the per-seed sim already
saturates the 8 cores (=> parallel-across-seeds won't help) or under-uses them
(=> run N seeds concurrently single-threaded for a real wall-clock win)."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from run_exp46_fast import (EDGES_20, N_QUBITS_20, brute_force_max_cut,
                            build_parameterized_xbasis_qaoa, evaluate_with_transpiled)
from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime.fake_provider import FakeMarrakesh

THREADS = int(os.environ.get("AER_THREADS", "8"))
SHOTS = int(os.environ.get("BENCH_SHOTS", "1024"))
P = 5
nm = NoiseModel.from_backend(FakeMarrakesh())
edges, nq = EDGES_20, N_QUBITS_20
mc = brute_force_max_cut(nq, edges)
qc, g, b = build_parameterized_xbasis_qaoa(P, nq, edges)
sim = AerSimulator(noise_model=nm, max_parallel_threads=THREADS,
                   max_parallel_experiments=1)
tqc = transpile(qc, backend=sim, optimization_level=1)
np.random.seed(42)
params = np.random.uniform(0, np.pi, 2 * P)
t0 = time.time()
r = evaluate_with_transpiled(params, tqc, g, b, P, sim, edges, mc, nq, SHOTS)
dt = time.time() - t0
meta = sim.run(tqc.assign_parameters({**{g[i]:params[i] for i in range(P)},
              **{b[i]:params[P+i] for i in range(P)}}), shots=8).result().results[0].metadata
print(f"AER_THREADS={THREADS} shots={SHOTS}: single_eval={dt:.1f}s ratio={r:.4f} "
      f"method={meta.get('method')} omp={meta.get('parallel_state_update','?')}", flush=True)
