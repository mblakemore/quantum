"""
Determinism check (Ember C3817): re-run seeds 42-44 through the EXACT exp55b
harness path to confirm the noiseless screen is reproducible under concurrent load.

Why: original Arm-0 (clean run) gave seed42=0.6922, 43=0.6969, 44=0.7064 (all escaped).
The expanded screen (52-131) shows ~50% trap under 4 concurrent sims + 3.5x slowdown.
Candidate confound: Whisper C4180 aer "invalid probability vector (1.0!=1)" = OMP
accumulation-order under threading -> could perturb COBYLA basin -> FAKE trap-rate shift.

Faithful (reproduces 0.692/0.697/0.706) -> screen clean, 42-51 was a real low draw.
Not reproduced -> screen confounded, T_new suspect.

READ-ONLY w.r.t. live procs/checkpoints (C4038): imports module only, writes nothing.
Replicates exp55b main() per-seed loop body EXACTLY (np.random.seed -> x0 -> optimize).
"""
import sys, os, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_exp55_noise_assisted_escape import (
    build_circuit, optimize_cobyla_capture,
    ESCAPE_THRESHOLD, P, SHOTS, MAX_ITER, SEED_SIM_NOISELESS,
)
from qiskit_aer import AerSimulator

EXPECTED = {42: 0.6922, 43: 0.6969, 44: 0.7064}

print(f"determinism check: p={P} shots={SHOTS} thr={ESCAPE_THRESHOLD} max_iter={MAX_ITER}", flush=True)
(transpiled_qc, gamma_params, beta_params,
 edges, max_cut, n_qubits, _noise_model) = build_circuit()
print(f"  depth={transpiled_qc.depth()} max_cut={max_cut}", flush=True)
noiseless_sim = AerSimulator(seed_simulator=SEED_SIM_NOISELESS)

for seed in (42, 43, 44):
    np.random.seed(seed)                                   # IDENTICAL x0 mapping
    x0 = np.random.uniform(0, 2 * np.pi, 2 * P)
    t0 = time.time()
    ratio, _ = optimize_cobyla_capture(
        transpiled_qc, gamma_params, beta_params, P,
        noiseless_sim, edges, max_cut, n_qubits, SHOTS, MAX_ITER, x0)
    exp = EXPECTED[seed]
    match = "MATCH" if abs(ratio - exp) < 1e-3 else f"DRIFT (expected {exp:.4f})"
    tag = "TRAPPED" if ratio < ESCAPE_THRESHOLD else "escaped"
    print(f"  seed={seed}: ratio={ratio:.4f} {tag}  {match}  ({time.time()-t0:.1f}s)", flush=True)
