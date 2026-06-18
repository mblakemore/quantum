#!/usr/bin/env python3
"""
Exp52 SPSA_1024sh RE-RUN — Whisper C4180

WHY: The original run_exp52_spsa_final.py crashed entering the SPSA_1024sh arm
with qiskit_aer's intermittent
    ValueError: QuantumError: invalid probability vector total (1.000000 != 1)
The SAME sim/noise model cleared all 10 SPSA_512sh seeds first, so the model is
not deterministically broken — it's a transient float-validation hiccup. Fix
shipped in run_exp46_fast.py:evaluate_with_transpiled (bounded retry that
re-ISSUES sim.run each attempt; a failed AerJob caches its exception so
re-calling .result() alone re-raises identically). This script re-runs ONLY the
missing 1024sh arm on top of that fix.

UNBLOCKS (Ember, divergent — the 1024 number adjudicates between them):
  - pred_c3707_004: SPSA_1024 >= 70% parity with COBYLA
  - pred_c3727_001: SPSA_1024sh = 50-70%, will NOT reach 70%
  - pred_c3740_002: SPSA_1024sh within 5pp of 512sh (22%) = decoherence-bound

USAGE (calibrate first, then commit the rest):
  python3 run_exp52_spsa_1024_rerun.py 42            # one seed: prove fix + time
  python3 run_exp52_spsa_1024_rerun.py 43 44 45 ...  # remaining seeds
  python3 run_exp52_spsa_1024_rerun.py               # all 10 (42..51)

Incremental: writes results/exp52_spsa_1024_rerun.json after EACH seed, merging
with any prior partial results, so a mid-run kill never loses completed seeds.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from run_exp52_spsa_final import (
    build_sim_and_circuit, ESCAPE_THRESHOLD, MAX_ITER_SPSA, SPSA_PARAMS, SEEDS,
)
from run_exp51_spsa_vs_cobyla import optimize_spsa
from run_exp46_fast import EDGES_20, N_QUBITS_20
import numpy as np

SHOTS = 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "results", "exp52_spsa_1024_rerun.json")


def load_prior():
    if os.path.exists(OUT):
        try:
            with open(OUT) as f:
                return json.load(f)
        except (ValueError, OSError):
            pass
    return {"arm": "SPSA_1024sh", "shots": SHOTS,
            "escape_threshold": ESCAPE_THRESHOLD, "seeds": {}}


def save(data):
    data["seeds_done"] = sorted(int(s) for s in data["seeds"])
    escs = [v["escaped"] for v in data["seeds"].values()]
    data["n_escaped"] = sum(escs)
    data["n_seeds"] = len(escs)
    data["escape_rate"] = (sum(escs) / len(escs)) if escs else None
    tmp = OUT + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, OUT)


def main():
    seeds = [int(a) for a in sys.argv[1:]] or SEEDS
    print(f"EXP52 SPSA_1024sh RE-RUN (W C4180) | seeds={seeds} | shots={SHOTS}")
    sys.stdout.flush()

    sim, transpiled_qc, gamma_params, beta_params, max_cut = build_sim_and_circuit()
    data = load_prior()

    for seed in seeds:
        np.random.seed(seed)
        t0 = time.time()
        ratio = optimize_spsa(
            transpiled_qc, gamma_params, beta_params, 3,
            sim, EDGES_20, max_cut, N_QUBITS_20, SHOTS, MAX_ITER_SPSA,
            **SPSA_PARAMS
        )
        elapsed = time.time() - t0
        escaped = ratio > ESCAPE_THRESHOLD
        status = "✓ ESCAPED" if escaped else "✗ trapped"
        print(f"  [SPSA_1024sh] seed={seed}: ratio={ratio:.4f} {status} ({elapsed:.1f}s)")
        sys.stdout.flush()
        data["seeds"][str(seed)] = {"seed": seed, "ratio": float(ratio),
                                    "escaped": bool(escaped), "elapsed_s": elapsed}
        save(data)

    print(f"\n  ARM RESULT: {data['n_escaped']}/{data['n_seeds']} = "
          f"{data['escape_rate']:.2f} escape rate" if data.get('escape_rate') is not None
          else "\n  (no seeds completed)")
    print(f"  Written: {OUT}")


if __name__ == "__main__":
    main()
