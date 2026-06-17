#!/usr/bin/env python3
"""
Exp55: Noise-Assisted Escape — Is Structured Hardware Noise a Computational Resource?
Whisper C4128 | Pre-registered 2026-06-16 (C4108)

Pre-registration: /droid/repos/quantum/experiments/exp55-noise-assisted-escape-preregistration.md

HYPOTHESES (pre-registered, see .md for full text + confidence):
  H1: On trapped subset T (noiseless ratio < 0.640), FakeMarrakesh noise rescues
      >=20% of T (>=1 of R noise realizations reaches ratio >= 0.640).  conf 45%
  H3: Noise-escapes are genuine, not measurement-variance: params discovered under
      noise, re-evaluated NOISELESSLY, retain ratio >= 0.640 for >=50% of escapes. conf 50%
  H2: (gated on H1 pass) structured FakeMarrakesh > matched depolarizing.  -> Arm 2,
      deferred to a follow-on run, pre-reg sequencing (only run if H1 passes).

DESIGN (sole manipulated variable = the noise channel):
  - EDGES_20, 20 qubits, escape threshold 0.640 (ratio-to-max-cut).
  - Seeds 42-51 (same as Exp51/52/53). p=3, 1024 shots, COBYLA max_iter=50.
  - ONE FakeMarrakesh-transpiled circuit (seed_transpiler pinned) used for BOTH arms,
    so the ONLY difference between Arm 0 and Arm 1 is whether the noise model is applied.
  - Arm 0 (noiseless): AerSimulator() no noise -> defines T.
  - Arm 1 (structured): AerSimulator(noise_model=FakeMarrakesh), R=5 noise realizations
    per trapped seed (distinct seed_simulator). Capture optimized params for H3.
  - H3: re-evaluate each Arm-1 escape's params on the noiseless sim.

C4038 collision guard: all outputs namespaced exp55_* (own checkpoint + log).
C5860 lesson reused: per-unit checkpoint flush for observability + resume.
Harness reuse: Elder's Exp46/Exp51/Exp53 infrastructure (EDGES_20, x-basis QAOA,
evaluate_with_transpiled). Only the noise-toggle arm logic + param capture are new.
"""
import sys, os, json, time
import numpy as np
from scipy.optimize import minimize

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_exp46_fast import (
    EDGES_20, N_QUBITS_20,
    brute_force_max_cut,
    build_parameterized_xbasis_qaoa,
    evaluate_with_transpiled,
)
from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime.fake_provider import FakeMarrakesh

# ---- Pre-registered constants ----
ESCAPE_THRESHOLD = 0.640
SEEDS = list(range(42, 52))      # 42..51, same as Exp51/52/53
P = 3
SHOTS = 1024
MAX_ITER = 50
N_REALIZATIONS = 5               # R in the pre-reg (Arm 1)
OPT_LEVEL = 1
SEED_TRANSPILER = 42             # pinned (README actionable #6, anti-confound)
SEED_SIM_NOISELESS = 1000        # fixed for Arm 0 + H3 reproducibility
SEED_SIM_NOISE_BASE = 2000       # realization r uses SEED_SIM_NOISE_BASE + r

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
CHECKPOINT_PATH = os.path.join(RESULTS_DIR, "exp55_checkpoint.json")
RESULTS_PATH = os.path.join(RESULTS_DIR, "exp55_results.json")


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


def optimize_cobyla_capture(transpiled_qc, gamma_params, beta_params, p,
                            sim, edges, max_cut, n_qubits, shots, max_iter, x0):
    """COBYLA best-tracking V2 (mirrors run_exp51) BUT also captures the params
    that achieved the best ratio, so H3 can re-evaluate them noiselessly."""
    best = {"ratio": 0.0, "x": np.array(x0, dtype=float)}

    def objective(x):
        r = evaluate_with_transpiled(
            x, transpiled_qc, gamma_params, beta_params,
            p, sim, edges, max_cut, n_qubits, shots)
        if r > best["ratio"]:
            best["ratio"] = r
            best["x"] = np.array(x, dtype=float)
        return -r

    minimize(objective, x0, method='COBYLA',
             options={'maxiter': max_iter, 'rhobeg': 0.5})
    return float(best["ratio"]), best["x"].tolist()


def build_circuit():
    """Build + transpile ONCE against FakeMarrakesh (pinned). Returns the shared
    transpiled circuit, the param objects, edges/max_cut/n_qubits, and the noise model."""
    edges = EDGES_20
    n_qubits = N_QUBITS_20
    max_cut = brute_force_max_cut(n_qubits, edges)

    fake_backend = FakeMarrakesh()
    noise_model = NoiseModel.from_backend(fake_backend)

    qc, gamma_params, beta_params = build_parameterized_xbasis_qaoa(P, n_qubits, edges)
    transpiled_qc = transpile(qc, backend=fake_backend,
                              optimization_level=OPT_LEVEL,
                              seed_transpiler=SEED_TRANSPILER)
    return transpiled_qc, gamma_params, beta_params, edges, max_cut, n_qubits, noise_model


def main():
    print("=" * 64, flush=True)
    print("EXP55: Noise-Assisted Escape (Whisper C4128)", flush=True)
    print(f"  p={P} shots={SHOTS} seeds={SEEDS} thr={ESCAPE_THRESHOLD} "
          f"max_iter={MAX_ITER} R={N_REALIZATIONS}", flush=True)
    print("=" * 64, flush=True)

    (transpiled_qc, gamma_params, beta_params,
     edges, max_cut, n_qubits, noise_model) = build_circuit()
    print(f"  Circuit depth (transpiled, FakeMarrakesh basis): {transpiled_qc.depth()}", flush=True)
    print(f"  max_cut={max_cut} | params={2*P}", flush=True)

    noiseless_sim = AerSimulator(seed_simulator=SEED_SIM_NOISELESS)

    ckpt = _load_checkpoint()

    # ---------- ARM 0: noiseless baseline -> defines T ----------
    arm0 = ckpt.get("arm0", {})
    print("\n" + "=" * 64, flush=True)
    print("ARM 0 — noiseless baseline (defines trapped subset T)", flush=True)
    print("=" * 64, flush=True)
    for seed in SEEDS:
        if str(seed) in arm0:
            print(f"  [resume] seed {seed}: ratio={arm0[str(seed)]['ratio']:.4f}", flush=True)
            continue
        np.random.seed(seed)
        x0 = np.random.uniform(0, 2 * np.pi, 2 * P)
        t0 = time.time()
        ratio, x_best = optimize_cobyla_capture(
            transpiled_qc, gamma_params, beta_params, P,
            noiseless_sim, edges, max_cut, n_qubits, SHOTS, MAX_ITER, x0)
        trapped = ratio < ESCAPE_THRESHOLD
        arm0[str(seed)] = {"seed": seed, "ratio": ratio, "trapped": trapped, "x": x_best}
        tag = "TRAPPED" if trapped else "escaped"
        print(f"  seed={seed}: ratio={ratio:.4f}  {tag}  ({time.time()-t0:.1f}s)", flush=True)
        ckpt["arm0"] = arm0
        _save_json(CHECKPOINT_PATH, ckpt)

    T = sorted(int(s) for s, r in arm0.items() if r["trapped"])
    print(f"\n  TRAPPED SUBSET T (noiseless ratio < {ESCAPE_THRESHOLD}): {T}  (|T|={len(T)})", flush=True)
    ckpt["T"] = T
    _save_json(CHECKPOINT_PATH, ckpt)

    if not T:
        print("\n  T is EMPTY — no trapped seeds noiselessly. H1/H3 undefined on this config.", flush=True)
        print("  Pre-reg note: this itself is a finding (cold-start has no traps at p=3/1024).", flush=True)
        _finalize(ckpt, arm0, T, {})
        return

    # ---------- ARM 1: structured FakeMarrakesh noise on T ----------
    arm1 = ckpt.get("arm1", {})
    print("\n" + "=" * 64, flush=True)
    print(f"ARM 1 — structured FakeMarrakesh noise on T, R={N_REALIZATIONS} realizations/seed", flush=True)
    print("=" * 64, flush=True)
    for seed in T:
        if str(seed) in arm1 and len(arm1[str(seed)]["realizations"]) == N_REALIZATIONS:
            print(f"  [resume] seed {seed} done", flush=True)
            continue
        realizations = arm1.get(str(seed), {}).get("realizations", [])
        done_r = {rz["r"] for rz in realizations}
        for r in range(N_REALIZATIONS):
            if r in done_r:
                continue
            noisy_sim = AerSimulator(noise_model=noise_model,
                                     seed_simulator=SEED_SIM_NOISE_BASE + r)
            np.random.seed(seed * 100 + r)  # distinct x0 per realization, reproducible
            x0 = np.random.uniform(0, 2 * np.pi, 2 * P)
            t0 = time.time()
            ratio, x_best = optimize_cobyla_capture(
                transpiled_qc, gamma_params, beta_params, P,
                noisy_sim, edges, max_cut, n_qubits, SHOTS, MAX_ITER, x0)
            escaped = ratio >= ESCAPE_THRESHOLD
            realizations.append({"r": r, "ratio": ratio, "escaped": escaped, "x": x_best})
            print(f"  seed={seed} r={r}: ratio={ratio:.4f}  "
                  f"{'ESCAPED' if escaped else 'trapped'}  ({time.time()-t0:.1f}s)", flush=True)
            arm1[str(seed)] = {"seed": seed, "realizations": realizations}
            ckpt["arm1"] = arm1
            _save_json(CHECKPOINT_PATH, ckpt)

    _finalize(ckpt, arm0, T, arm1)


def _finalize(ckpt, arm0, T, arm1):
    # ---------- H1 ----------
    rescued = []
    for seed in T:
        rzs = arm1.get(str(seed), {}).get("realizations", [])
        if any(rz["escaped"] for rz in rzs):
            rescued.append(seed)
    h1_rate = (len(rescued) / len(T)) if T else 0.0
    h1_pass = h1_rate >= 0.20

    # ---------- H3: re-evaluate noise-escape params NOISELESSLY ----------
    noiseless_sim = AerSimulator(seed_simulator=SEED_SIM_NOISELESS)
    transpiled_qc, gamma_params, beta_params, edges, max_cut, n_qubits, _ = build_circuit()
    h3_total, h3_retained, h3_detail = 0, 0, []
    for seed in T:
        for rz in arm1.get(str(seed), {}).get("realizations", []):
            if not rz["escaped"]:
                continue
            h3_total += 1
            r_noiseless = evaluate_with_transpiled(
                np.array(rz["x"]), transpiled_qc, gamma_params, beta_params,
                P, noiseless_sim, edges, max_cut, n_qubits, SHOTS)
            retained = r_noiseless >= ESCAPE_THRESHOLD
            if retained:
                h3_retained += 1
            h3_detail.append({"seed": seed, "r": rz["r"],
                              "noisy_ratio": rz["ratio"],
                              "noiseless_recheck": float(r_noiseless),
                              "retained": retained})
    h3_rate = (h3_retained / h3_total) if h3_total else 0.0
    h3_pass = (h3_rate >= 0.50) if h3_total else False

    # mean-ratio change on T (expected negative — noise lowers the ceiling)
    mean_deltas = []
    for seed in T:
        base = arm0[str(seed)]["ratio"]
        rzs = arm1.get(str(seed), {}).get("realizations", [])
        if rzs:
            mean_noisy = np.mean([rz["ratio"] for rz in rzs])
            mean_deltas.append(mean_noisy - base)
    mean_ratio_change = float(np.mean(mean_deltas)) if mean_deltas else None

    if h1_pass and h3_pass:
        verdict = "NOISE-ASSISTED ESCAPE IS REAL -> evaluate H2 (Arm 2 follow-on)"
    elif h1_pass and not h3_pass:
        verdict = "Escape is MEASUREMENT-VARIANCE, not landscape movement -> null on resource claim"
    else:
        verdict = "Noise is a PURE PENALTY on this arc (confirms prior; clean citable null)"

    summary = {
        "experiment": "Exp55 Noise-Assisted Escape",
        "author": "Whisper C4128",
        "config": {"p": P, "shots": SHOTS, "seeds": SEEDS, "threshold": ESCAPE_THRESHOLD,
                   "max_iter": MAX_ITER, "R": N_REALIZATIONS,
                   "seed_transpiler": SEED_TRANSPILER},
        "T": T, "T_size": len(T),
        "H1": {"rescued_seeds": rescued, "rate": h1_rate, "threshold": 0.20, "pass": h1_pass},
        "H3": {"escapes_total": h3_total, "retained": h3_retained, "rate": h3_rate,
               "threshold": 0.50, "pass": h3_pass, "detail": h3_detail},
        "mean_ratio_change_on_T": mean_ratio_change,
        "verdict": verdict,
        "arm0": arm0,
        "arm1": arm1,
    }
    _save_json(RESULTS_PATH, summary)

    print("\n" + "=" * 64, flush=True)
    print("EXP55 RESULTS", flush=True)
    print("=" * 64, flush=True)
    print(f"  |T| = {len(T)}  T = {T}", flush=True)
    print(f"  H1 escape-rate on T = {h1_rate:.0%}  (rescued {rescued})  "
          f"=> {'PASS' if h1_pass else 'FAIL'} (thr 20%)", flush=True)
    print(f"  H3 noiseless-retention = {h3_rate:.0%} ({h3_retained}/{h3_total})  "
          f"=> {'PASS' if h3_pass else 'FAIL'} (thr 50%)", flush=True)
    print(f"  mean ratio change on T = "
          f"{mean_ratio_change:.4f} (expect <0: noise lowers ceiling)"
          if mean_ratio_change is not None else "  mean ratio change: n/a", flush=True)
    print(f"  VERDICT: {verdict}", flush=True)
    print(f"\n  written -> {RESULTS_PATH}", flush=True)


if __name__ == "__main__":
    main()
