"""
Exp55 H3 SPOT-CHECK (Whisper C4147) — one-off, read-only.

Arm 1 is mid-flight (r=0 of R=5 done on the sole trapped seed 51). The script's own
_finalize() H3 pass only runs after ALL realizations complete. This spot-checks the
pre-registered H3 anti-artifact control on the FIRST escape we have:

  Is seed-51 r=0's noise-escape (noisy ratio 0.6573 >= 0.640) a genuine move to a better
  basin, or a lucky high-variance shot? Test = re-score the noise-found params NOISELESSLY.
  H3 logic replicated byte-for-byte from _finalize (lines 212-229).

READ-ONLY on results/exp55_checkpoint.json. Writes results/exp55_h3_spotcheck_c4147.json.
Importing run_exp55 is safe (it is __main__-guarded; main() does not run on import).
This does NOT touch / relaunch the running Exp55 process (C4038).

Scope honesty: r=0 of R=5, |T|=1 -> this is an N=1 spot-check, NOT H1/H3 resolution
(those need all R=5; see exp55-arm0-finding-c4128.md). Reported for "keep repo updated".
"""
import sys, os, json
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from run_exp55_noise_assisted_escape import (
    build_circuit, evaluate_with_transpiled, P, SHOTS, ESCAPE_THRESHOLD,
    SEED_SIM_NOISELESS, CHECKPOINT_PATH,
)
from qiskit_aer import AerSimulator

ckpt = json.load(open(CHECKPOINT_PATH))
seed = 51
arm0 = ckpt["arm0"][str(seed)]
rz0 = ckpt["arm1"][str(seed)]["realizations"][0]
assert rz0["r"] == 0 and rz0["escaped"], "expected r=0 escape on seed 51"

x0 = np.array(arm0["x"])          # cold-start (trapped) params, noiseless ratio = arm0['ratio']
x1 = np.array(rz0["x"])           # noise-found params, noisy ratio = rz0['ratio']

(transpiled_qc, gamma_params, beta_params,
 edges, max_cut, n_qubits, _) = build_circuit()

# Canonical H3 number — exactly as _finalize would compute it (single eval, fixed seed)
noiseless_sim = AerSimulator(seed_simulator=SEED_SIM_NOISELESS)
h3_canonical = float(evaluate_with_transpiled(
    x1, transpiled_qc, gamma_params, beta_params, P,
    noiseless_sim, edges, max_cut, n_qubits, SHOTS))
retained = h3_canonical >= ESCAPE_THRESHOLD

# Supplementary: sampling-variance band on the noiseless re-eval of x1 (1024 shots ->
# the eval itself is stochastic; 0.6573 sat only +0.017 above threshold, so characterize it)
band = []
for s in range(SEED_SIM_NOISELESS, SEED_SIM_NOISELESS + 8):
    sim = AerSimulator(seed_simulator=s)
    band.append(float(evaluate_with_transpiled(
        x1, transpiled_qc, gamma_params, beta_params, P,
        sim, edges, max_cut, n_qubits, SHOTS)))
band = np.array(band)

# Same variance band on x0 (trapped cold-start), for reference
band_x0 = []
for s in range(SEED_SIM_NOISELESS, SEED_SIM_NOISELESS + 8):
    sim = AerSimulator(seed_simulator=s)
    band_x0.append(float(evaluate_with_transpiled(
        x0, transpiled_qc, gamma_params, beta_params, P,
        sim, edges, max_cut, n_qubits, SHOTS)))
band_x0 = np.array(band_x0)

out = {
    "cycle": "C4147",
    "scope": "N=1 spot-check, r=0 of R=5, |T|=1 — NOT H1/H3 resolution (needs all R=5)",
    "threshold": ESCAPE_THRESHOLD,
    "seed": seed,
    "x0_coldstart_noiseless_ratio_arm0": arm0["ratio"],
    "x1_noisefound_noisy_ratio_arm1_r0": rz0["ratio"],
    "H3_canonical_noiseless_recheck_of_x1": h3_canonical,
    "H3_retained_this_realization": bool(retained),
    "x1_noiseless_band_mean": float(band.mean()),
    "x1_noiseless_band_std": float(band.std()),
    "x1_noiseless_band_min": float(band.min()),
    "x1_noiseless_band_max": float(band.max()),
    "x1_noiseless_band_frac_ge_threshold": float((band >= ESCAPE_THRESHOLD).mean()),
    "x0_noiseless_band_mean": float(band_x0.mean()),
    "x0_noiseless_band_std": float(band_x0.std()),
    "params_distinct": float(np.linalg.norm(x1 - x0)),
}
outpath = os.path.join(os.path.dirname(CHECKPOINT_PATH), "exp55_h3_spotcheck_c4147.json")
json.dump(out, open(outpath, "w"), indent=2)

print(json.dumps(out, indent=2))
print(f"\nwrote {outpath}")
