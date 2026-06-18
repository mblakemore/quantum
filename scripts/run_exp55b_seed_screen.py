#!/usr/bin/env python3
"""
Exp55b: Expanded noiseless seed screen — grow the trapped subset T.
Whisper C4182 | Follow-on to Exp55 (Whisper C4128, pre-reg C4108)

WHY (Ember C3816 + my own recognition):
  Exp55's pre-registered seed set (42-51) yielded |T|=1 trapped seed in BOTH arms
  (p=3: seed 51; p=5: seed 47). With |T|=1, H1 ("noise rescues >=20% of T") collapses
  to a single Bernoulli trial — it can only read 0% or 100%, not a population estimate.
  Ember's compute-aware fix (C3816, conf 0.8 on the read): the noiseless Arm-0 screen is
  ~FREE (~10s/seed at p=3); the noise arm is the ~6h/realization cost. So BUY POWER WHERE
  IT IS FREE — screen many more seeds noiselessly first, THEN run the expensive noise arm
  only on confirmed-trapped seeds.

WHAT THIS IS (and is NOT):
  - This is the DESCRIPTIVE screen only: it identifies which additional seeds are noiselessly
    trapped. It does NOT run the expensive noise arm. The H1 re-test on the expanded T remains
    a SEPARATE, pre-registered follow-on (deliberate go/no-go, given the downstream cost).
  - Apples-to-apples integrity: imports build_circuit + optimize_cobyla_capture + ALL constants
    from the live exp55 module so the screen is IDENTICAL to the original Arm 0 (same transpiler
    seed, opt level, FakeMarrakesh transpilation, EDGES_20, shots, max_iter, threshold,
    SEED_SIM_NOISELESS, and the np.random.seed(seed)->x0 mapping). No reimplementation.
  - C4038 collision guard: own namespaced checkpoint/log (exp55_seedscreen_*). Does NOT touch
    exp55_checkpoint.json (owned by the live main proc) or the running noise arms.

DEVIATION NOTE (anti-overclaim, network discipline): seeds 52-131 extend beyond the
  pre-registered 42-51. This is a transparent follow-on amendment, not a silent change. The
  screen is observation (which seeds trap), not the hypothesis test.
"""
import sys, os, json, time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# Import the EXACT circuit + optimizer + constants from the live exp55 module.
# Safe: that module is __main__-guarded, so import does not trigger its run.
from run_exp55_noise_assisted_escape import (
    build_circuit, optimize_cobyla_capture,
    ESCAPE_THRESHOLD, P, SHOTS, MAX_ITER, SEED_SIM_NOISELESS,
)
from qiskit_aer import AerSimulator

# New seeds only — do not re-screen 42-51 (already in exp55_checkpoint arm0).
SCREEN_SEEDS = list(range(52, 132))   # 52..131 = 80 new seeds

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
CHECKPOINT_PATH = os.path.join(RESULTS_DIR, "exp55_seedscreen_checkpoint.json")
RESULTS_PATH = os.path.join(RESULTS_DIR, "exp55_seedscreen_results.json")


def _load_checkpoint():
    if os.path.exists(CHECKPOINT_PATH):
        try:
            with open(CHECKPOINT_PATH) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=2)
    os.replace(tmp, path)  # atomic


def main():
    print("=" * 64, flush=True)
    print("EXP55b: Expanded noiseless seed screen (Whisper C4182)", flush=True)
    print(f"  p={P} shots={SHOTS} thr={ESCAPE_THRESHOLD} max_iter={MAX_ITER}", flush=True)
    print(f"  screening seeds {SCREEN_SEEDS[0]}..{SCREEN_SEEDS[-1]} "
          f"(N={len(SCREEN_SEEDS)} new seeds, noiseless Arm-0 only)", flush=True)
    print("=" * 64, flush=True)

    (transpiled_qc, gamma_params, beta_params,
     edges, max_cut, n_qubits, _noise_model) = build_circuit()
    print(f"  Circuit depth (transpiled, FakeMarrakesh basis): {transpiled_qc.depth()}", flush=True)
    print(f"  max_cut={max_cut} | params={2*P}", flush=True)

    noiseless_sim = AerSimulator(seed_simulator=SEED_SIM_NOISELESS)

    ckpt = _load_checkpoint()
    screened = ckpt.get("screened", {})

    print("\n" + "=" * 64, flush=True)
    print("NOISELESS SCREEN (defines expanded trapped subset T)", flush=True)
    print("=" * 64, flush=True)
    for seed in SCREEN_SEEDS:
        if str(seed) in screened:
            r = screened[str(seed)]
            print(f"  [resume] seed {seed}: ratio={r['ratio']:.4f} "
                  f"{'TRAPPED' if r['trapped'] else 'escaped'}", flush=True)
            continue
        np.random.seed(seed)  # IDENTICAL x0 mapping to exp55 Arm 0
        x0 = np.random.uniform(0, 2 * np.pi, 2 * P)
        t0 = time.time()
        ratio, x_best = optimize_cobyla_capture(
            transpiled_qc, gamma_params, beta_params, P,
            noiseless_sim, edges, max_cut, n_qubits, SHOTS, MAX_ITER, x0)
        trapped = ratio < ESCAPE_THRESHOLD
        screened[str(seed)] = {"seed": seed, "ratio": ratio, "trapped": trapped, "x": x_best}
        tag = "TRAPPED" if trapped else "escaped"
        print(f"  seed={seed}: ratio={ratio:.4f}  {tag}  ({time.time()-t0:.1f}s)", flush=True)
        ckpt["screened"] = screened
        _save_json(CHECKPOINT_PATH, ckpt)

    # Expanded T from THIS screen (52-131). Original T (51) lives in exp55_checkpoint.
    T_new = sorted(int(s) for s, r in screened.items() if r["trapped"])
    trap_rate = len(T_new) / len(screened) if screened else 0.0
    print("\n" + "=" * 64, flush=True)
    print("SCREEN COMPLETE", flush=True)
    print("=" * 64, flush=True)
    print(f"  screened {len(screened)} seeds (52-131)", flush=True)
    print(f"  NEW trapped seeds T_new (ratio < {ESCAPE_THRESHOLD}): {T_new}  "
          f"(|T_new|={len(T_new)})", flush=True)
    print(f"  observed trap rate (this screen): {trap_rate:.1%}", flush=True)
    print(f"  combined with original seed 51 -> full T candidate pool for a powered "
          f"noise re-test", flush=True)
    print(f"\n  DOWNSTREAM COST (NOT run here): a noise arm on |T| trapped seeds = "
          f"|T| x R(5) x ~6h ≈ heavy multi-day local sim. Go/no-go is a deliberate "
          f"decision, not auto-launched.", flush=True)

    ckpt["T_new"] = T_new
    ckpt["trap_rate"] = trap_rate
    ckpt["screened_count"] = len(screened)
    _save_json(CHECKPOINT_PATH, ckpt)
    _save_json(RESULTS_PATH, {
        "experiment": "exp55b_seed_screen",
        "cycle": "C4182",
        "p": P, "shots": SHOTS, "threshold": ESCAPE_THRESHOLD,
        "screened_seeds": [SCREEN_SEEDS[0], SCREEN_SEEDS[-1]],
        "screened_count": len(screened),
        "T_new": T_new,
        "trap_rate": trap_rate,
        "note": "Descriptive screen only; noise arm not run. H1 re-test on expanded T "
                "remains a separate pre-registered follow-on.",
    })
    print(f"\n  written -> {RESULTS_PATH}", flush=True)


if __name__ == "__main__":
    main()
