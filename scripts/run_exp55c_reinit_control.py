#!/usr/bin/env python3
"""
Exp55c: Noiseless re-initialization CONTROL — the attribution arm Exp55 was missing.
Whisper C4183 | Control for Exp55 (Whisper C4128) / Exp55b screen (C4182)

WHY (attribution confound found C4183, advisor-flagged):
  Exp55's Arm 1 (the expensive ~6h/realization "noise-assisted escape" arm) changes TWO
  variables at once relative to Arm 0:
    - Arm 0 (defines traps): np.random.seed(seed)        -> ONE fixed x0 per seed, noiseless.
    - Arm 1 (noise arm):     np.random.seed(seed*100 + r) -> a DIFFERENT x0 per realization,
                                                            AND adds FakeMarrakesh noise.
  So when seed 51 "escapes" 4/4 under Arm 1 (ratios 0.657/0.680/0.678/0.662 > 0.640), the
  escape is NOT attributable to noise: it is equally consistent with the trap being fragile
  to ANY re-initialization of the optimizer (init-sensitivity), with noise playing no role.
  Ember's C3817 determinism check resolved SELECTION (the traps are genuinely trapped) but
  NOT ATTRIBUTION (that NOISE specifically causes the escape).

WHAT THIS CONTROL DOES:
  For each trapped seed, run R noiseless optimizations using Arm 1's EXACT x0 schedule
  (np.random.seed(seed*100 + r)) on the NOISELESS simulator. This holds the init-perturbation
  variable identical to Arm 1 while removing the noise variable. It is ~31s/run (like Arm 0),
  i.e. ~1000x cheaper than Arm 1's ~6h/run.

DECISION RULE (gates the Exp55 noise-arm go/no-go):
  - If noiseless re-init ALSO escapes at a rate ~= Arm 1's noise-escape rate
      -> escape is INIT-SENSITIVITY, not noise. The 12-day noise arm is UNINTERPRETABLE as
         "noise-assisted." NO-GO (redesign: noise vs re-init must be a 2-arm contrast).
  - If noiseless re-init STAYS TRAPPED while Arm 1 (noise) escapes
      -> genuine NOISE effect. GO on a powered subsample (advisor: R=2-3 across MORE seeds,
         since H1 is an across-seed proportion; seeds are the unit of power, not realizations).
  Either way this control becomes the proper NULL/control rate the noise arm must beat.

INTEGRITY (apples-to-apples): imports build_circuit + optimize_cobyla_capture + ALL constants
  from the live exp55 module (same transpiler seed, opt level, FakeMarrakesh transpilation,
  shots, max_iter, threshold, SEED_SIM_NOISELESS). No reimplementation. The ONLY difference
  vs Arm 0 is the x0 schedule (seed*100+r), chosen to MATCH Arm 1 exactly.

C4038 collision guard: own namespaced checkpoint/log (exp55c_reinit_*). Does NOT touch
  exp55_checkpoint.json (owned by the live main proc) or any running noise arm. Module import
  is safe: run_exp55_noise_assisted_escape is __main__-guarded.

DEVIATION NOTE: This is a transparent follow-on control, not part of the original pre-reg.
  It is a methodological correction to make Arm 1 interpretable. Original n=1 noise run stands.
"""
import sys, os, json, time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the EXACT circuit + optimizer + constants from the live exp55 module.
# Safe: that module is __main__-guarded, so import does not trigger its run.
from run_exp55_noise_assisted_escape import (
    build_circuit, optimize_cobyla_capture,
    ESCAPE_THRESHOLD, P, SHOTS, MAX_ITER, N_REALIZATIONS, SEED_SIM_NOISELESS,
)
from qiskit_aer import AerSimulator

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
CHECKPOINT_PATH = os.path.join(RESULTS_DIR, "exp55c_reinit_checkpoint.json")
RESULTS_PATH = os.path.join(RESULTS_DIR, "exp55c_reinit_results.json")
SCREEN_RESULTS = os.path.join(RESULTS_DIR, "exp55_seedscreen_results.json")

# seed 51 = original Arm-0 trap (has Arm-1 noise data to compare against).
ORIGINAL_TRAP = [51]


def _load_json(path, default):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default


def _save_json(path, obj):
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)


def trapped_seeds():
    """seed 51 (original) + T_new from the C4182 noiseless screen."""
    screen = _load_json(SCREEN_RESULTS, {})
    t_new = screen.get("T_new", [])
    seeds = ORIGINAL_TRAP + [s for s in t_new if s not in ORIGINAL_TRAP]
    return seeds


def main():
    print("=" * 64, flush=True)
    print("EXP55c: Noiseless re-init CONTROL (Whisper C4183)", flush=True)
    print(f"  p={P} shots={SHOTS} thr={ESCAPE_THRESHOLD} max_iter={MAX_ITER} R={N_REALIZATIONS}", flush=True)
    print("  x0 schedule = np.random.seed(seed*100+r)  [IDENTICAL to Arm 1, but NOISELESS]", flush=True)
    print("=" * 64, flush=True)

    (transpiled_qc, gamma_params, beta_params,
     edges, max_cut, n_qubits, _noise_model) = build_circuit()
    print(f"  Circuit depth (transpiled, FakeMarrakesh basis): {transpiled_qc.depth()}", flush=True)
    print(f"  max_cut={max_cut} | params={2*P}", flush=True)

    noiseless_sim = AerSimulator(seed_simulator=SEED_SIM_NOISELESS)

    seeds = trapped_seeds()
    print(f"\n  Control over {len(seeds)} trapped seeds: {seeds}", flush=True)

    ckpt = _load_json(CHECKPOINT_PATH, {"control": {}})
    control = ckpt["control"]

    for seed in seeds:
        existing = control.get(str(seed), {}).get("realizations", [])
        if len(existing) == N_REALIZATIONS:
            print(f"  [resume] seed {seed}: {len(existing)} realizations done", flush=True)
            continue
        realizations = existing
        for r in range(len(realizations), N_REALIZATIONS):
            np.random.seed(seed * 100 + r)          # IDENTICAL to Arm 1
            x0 = np.random.uniform(0, 2 * np.pi, 2 * P)
            t0 = time.time()
            ratio, x_best = optimize_cobyla_capture(
                transpiled_qc, gamma_params, beta_params, P,
                noiseless_sim, edges, max_cut, n_qubits, SHOTS, MAX_ITER, x0)
            escaped = ratio >= ESCAPE_THRESHOLD
            realizations.append({"r": r, "ratio": ratio, "escaped": escaped})
            tag = "ESCAPED" if escaped else "trapped"
            print(f"  seed={seed} r={r}: ratio={ratio:.4f}  {tag}  ({time.time()-t0:.1f}s)", flush=True)
            control[str(seed)] = {"seed": seed, "realizations": realizations}
            ckpt["control"] = control
            _save_json(CHECKPOINT_PATH, ckpt)

    # ---------- summarize ----------
    per_seed = []
    total_real = 0
    total_escaped = 0
    seeds_any_escape = 0
    for seed in seeds:
        rzs = control.get(str(seed), {}).get("realizations", [])
        n_esc = sum(1 for x in rzs if x["escaped"])
        total_real += len(rzs)
        total_escaped += n_esc
        if n_esc > 0:
            seeds_any_escape += 1
        per_seed.append({"seed": seed, "n": len(rzs), "escaped": n_esc,
                         "ratios": [round(x["ratio"], 4) for x in rzs]})

    summary = {
        "experiment": "exp55c_reinit_control",
        "cycle": "C4183",
        "purpose": "attribution control: isolate init-sensitivity from noise effect in Exp55 Arm 1",
        "p": P, "shots": SHOTS, "threshold": ESCAPE_THRESHOLD, "R": N_REALIZATIONS,
        "x0_schedule": "np.random.seed(seed*100+r) [matches Arm 1], evaluated NOISELESSLY",
        "n_seeds": len(seeds),
        "control_escape_rate_realizations": (total_escaped / total_real) if total_real else None,
        "seeds_with_any_escape": seeds_any_escape,
        "per_seed": per_seed,
        "interpretation_rule": (
            "If this noiseless re-init escape rate ~= Arm 1 noise-escape rate -> escape is "
            "INIT-SENSITIVITY (noise arm uninterpretable, NO-GO). If this stays trapped while "
            "Arm 1 escapes -> genuine NOISE effect (GO on powered subsample, R=2-3 x more seeds)."
        ),
    }
    _save_json(RESULTS_PATH, summary)

    print("\n" + "=" * 64, flush=True)
    print("CONTROL COMPLETE", flush=True)
    print("=" * 64, flush=True)
    rate = summary["control_escape_rate_realizations"]
    print(f"  noiseless re-init escape rate (realizations): "
          f"{total_escaped}/{total_real} = {rate:.3f}" if rate is not None else "  no data", flush=True)
    print(f"  seeds with >=1 re-init escape: {seeds_any_escape}/{len(seeds)}", flush=True)
    print(f"  COMPARE to Arm 1 seed-51 noise escapes (0.657/0.680/0.678/0.662 -> 4/4 escaped).", flush=True)
    print(f"  written -> {RESULTS_PATH}", flush=True)


if __name__ == "__main__":
    main()
