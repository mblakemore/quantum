#!/usr/bin/env python3
"""C4153 — Matched-realization NOISELESS control for Exp55 seed 51 (main p=3 run).

Closes the substrate audit Whisper opened at C4148 (which covered optionA seed 47, p=5).
This is the MAIN exp55 run's trapped seed: 51, p=3, noiseless ratio 0.586 (C4128) — a
DEEPER trap than 47's 0.626, so the best positive candidate for genuine noise-assisted escape.

THE CONFOUND (read from run_exp55_noise_assisted_escape.py):
  Arm 0 (defines trap):  x0 = seed(51);        noiseless;  seed_simulator=1000  -> 0.586 TRAP
  Arm 1 ("escape"):      x0 = seed(51*100+r);  +noise;     seed_simulator=2000+r -> escapes
So Arm 1 changes THREE things vs Arm 0: noise model, shot realization, AND the initial point.
The script's stated invariant (line 20: "the ONLY difference ... is whether noise is applied")
is FALSE in code.

THE CONTROL (isolates the noise model, holding x0 AND realization fixed to Arm 1's own values):
  For each r: x0 = seed(51*100+r);  NOISELESS;  seed_simulator=2000+r.
  If these ESCAPE too -> noise contributed nothing -> Arm-1 escape is x0/realization-driven (VACUOUS).
  If these stay TRAPPED while Arm-1 (noisy, same x0+realization) escaped -> genuine noise-assisted escape.

Read-only: does NOT touch any live process, results/exp55_*, or checkpoints. Output -> /tmp + stdout.
"""
import sys, os, json, time
import numpy as np
from scipy.optimize import minimize

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_exp46_fast import (
    EDGES_20, N_QUBITS_20, brute_force_max_cut,
    build_parameterized_xbasis_qaoa, evaluate_with_transpiled,
)
from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime.fake_provider import FakeMarrakesh

# Mirror exp55 constants EXACTLY
ESCAPE_THRESHOLD = 0.640
P = 3
SHOTS = 1024
MAX_ITER = 50
N_REALIZATIONS = 5
OPT_LEVEL = 1
SEED_TRANSPILER = 42
SEED_SIM_NOISELESS = 1000
SEED_SIM_NOISE_BASE = 2000
SEED = 51


def optimize_cobyla(transpiled_qc, gamma_params, beta_params, sim, edges, max_cut, n_qubits, x0):
    best = {"ratio": 0.0}
    def objective(x):
        r = evaluate_with_transpiled(x, transpiled_qc, gamma_params, beta_params,
                                     P, sim, edges, max_cut, n_qubits, SHOTS)
        if r > best["ratio"]:
            best["ratio"] = r
        return -r
    minimize(objective, x0, method='COBYLA', options={'maxiter': MAX_ITER, 'rhobeg': 0.5})
    return float(best["ratio"])


def main():
    print("=" * 70, flush=True)
    print("C4153 — Exp55 seed 51 matched-realization NOISELESS control (p=3)", flush=True)
    print("=" * 70, flush=True)

    edges, n_qubits = EDGES_20, N_QUBITS_20
    max_cut = brute_force_max_cut(n_qubits, edges)
    fake_backend = FakeMarrakesh()
    qc, gamma_params, beta_params = build_parameterized_xbasis_qaoa(P, n_qubits, edges)
    transpiled_qc = transpile(qc, backend=fake_backend,
                              optimization_level=OPT_LEVEL, seed_transpiler=SEED_TRANSPILER)
    print(f"  depth={transpiled_qc.depth()} max_cut={max_cut}", flush=True)

    # --- Reproduce Arm-0 trap (x0=seed51, noiseless, sim=1000) as a sanity check ---
    noiseless_arm0 = AerSimulator(seed_simulator=SEED_SIM_NOISELESS)
    np.random.seed(SEED)
    x0_arm0 = np.random.uniform(0, 2 * np.pi, 2 * P)
    t0 = time.time()
    r_arm0 = optimize_cobyla(transpiled_qc, gamma_params, beta_params,
                             noiseless_arm0, edges, max_cut, n_qubits, x0_arm0)
    print(f"\n  [Arm-0 reproduce] x0=seed({SEED}) noiseless sim=1000: ratio={r_arm0:.4f} "
          f"{'TRAP' if r_arm0 < ESCAPE_THRESHOLD else 'escaped'}  ({time.time()-t0:.1f}s)", flush=True)

    # --- THE CONTROL: noiseless at Arm-1's own (x0, realization) for r=0..4 ---
    print(f"\n  MATCHED CONTROL — noiseless COBYLA at Arm-1's own x0=seed({SEED}*100+r), sim=2000+r:", flush=True)
    rows = []
    for r in range(N_REALIZATIONS):
        sim = AerSimulator(seed_simulator=SEED_SIM_NOISE_BASE + r)  # matched realization, NO noise
        np.random.seed(SEED * 100 + r)                              # matched x0
        x0 = np.random.uniform(0, 2 * np.pi, 2 * P)
        t0 = time.time()
        ratio = optimize_cobyla(transpiled_qc, gamma_params, beta_params,
                                sim, edges, max_cut, n_qubits, x0)
        esc = ratio >= ESCAPE_THRESHOLD
        rows.append({"r": r, "noiseless_ratio": ratio, "escaped": bool(esc)})
        print(f"    r={r} (x0=seed{SEED*100+r}, sim={SEED_SIM_NOISE_BASE+r}, NOISELESS): "
              f"ratio={ratio:.4f}  {'ESCAPED' if esc else 'trapped'}  ({time.time()-t0:.1f}s)", flush=True)

    n_esc = sum(1 for x in rows if x["escaped"])
    print(f"\n  RESULT: {n_esc}/{N_REALIZATIONS} of Arm-1's (x0,realization) points escape NOISELESSLY.", flush=True)
    if n_esc >= 1:
        print("  => At the points Arm 1 actually optimizes, escape does NOT require noise.", flush=True)
        print("  => Arm-1's 'noise-assisted escape' on seed 51 is VACUOUS (x0/realization-driven),", flush=True)
        print("     same verdict as optionA seed 47 (C4148). Confound: Arm 1 re-randomizes x0 AND realization.", flush=True)
    out = {"cycle": 4153, "seed": SEED, "p": P,
           "arm0_reproduce_ratio": r_arm0,
           "matched_noiseless_control": rows,
           "n_escape_noiseless": n_esc, "R": N_REALIZATIONS,
           "verdict": "VACUOUS — noise-assisted escape premise false at sampled points"
                      if n_esc >= 1 else "noiseless stays trapped — candidate genuine noise effect"}
    with open("/tmp/c4153_exp55_seed51_control.json", "w") as f:
        json.dump(out, f, indent=2)
    print("\n  wrote /tmp/c4153_exp55_seed51_control.json", flush=True)


if __name__ == "__main__":
    main()
