#!/usr/bin/env python3
"""
Exp58 — Exp55-G1 genuine noise toggle. Resolves the C4153 r=1 open item.
Whisper C4223 | Pre-reg: experiments/exp58-exp55g1-noise-toggle-preregistration.md

WHY (the single open item):
  Exp55's noise arm was killed (NO-GO C4194/C4217) because Arm 1 moved THREE variables at once
  (x0, shot realization, noise model). The C4153 matched control + Exp55c (n=29) showed noiseless
  re-init escapes are STRUCTURAL -> Arm-1 escapes carry no noise attribution. ONE thing stayed open:
  at seed 51, r=1, a single CLEAN toggle (same x0, same seed_simulator, noise the only variable)
  flipped 0.600 (trapped) -> 0.680 (escaped). N=1, and COBYLA is hyper-sensitive to the shot
  realization, so that gap could be trajectory noise. C4153 tagged r=1 "a candidate to retest under
  G1." THIS is the G1 retest.

THE GENUINE TOGGLE (G1): for the DEFINED trap x0 = np.random.seed(51), and each realization seed s:
    noiseless: AerSimulator(seed_simulator=s)                        -> r_off(s)
    noisy:     AerSimulator(noise_model=FakeMarrakesh, seed_simulator=s) -> r_on(s)
  IDENTICAL x0 AND IDENTICAL seed_simulator on both sides. The noise model is the ONLY variable.

TWO STAGES (power-per-CPU-hour):
  Stage A (cheap ~31s/run): noiseless across a broad sim panel -> find Trapped_off (r_off < 0.640).
  Stage B (expensive ~hrs/run): noisy at the SAME (x0, s) for ONLY s in Trapped_off. Routing the
    expensive noisy runs to the trapped realizations is the whole efficiency point.

DECISION RULE (pre-committed, see pre-reg):
  GO   : median Δ over Trapped_off > 0 AND rescue_rate > anti_rescue_rate.
  NO-GO: median Δ ≤ 0 OR rescue_rate ≤ anti_rescue_rate.
  POWER GUARD: if |Trapped_off| < 3 -> anecdote, not a rate; do NOT issue GO/NO-GO; escalate to a
    robust trap via --trap-seeds.

INTEGRITY (C4038): imports build_circuit + optimize_cobyla_capture + ALL constants from the live
  exp55 module (__main__-guarded -> import is side-effect-free). Own namespaced artifacts
  (exp58_g1_*). Touches NO exp55 checkpoint and NO live process.

LAUNCH GATE: do NOT run while Exp54 ArmA is contending for CPU. Stage A is cheap but still yields;
  Stage B must wait for ArmA completion. This file is committed design — running it is a separate,
  gated decision.
"""
import sys, os, json, argparse
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# EXACT circuit + optimizer + constants from the live exp55 module (side-effect-free import).
from run_exp55_noise_assisted_escape import (
    build_circuit, optimize_cobyla_capture,
    ESCAPE_THRESHOLD, P, SHOTS, MAX_ITER,
)
from qiskit_aer import AerSimulator

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
CHECKPOINT_PATH = os.path.join(RESULTS_DIR, "exp58_g1_checkpoint.json")
RESULTS_PATH = os.path.join(RESULTS_DIR, "exp58_g1_results.json")

# Realization-seed panel namespace: disjoint from Arm-0 (1000) and Arm-1 (2000..2004).
SIM_BASE = 3000
K_A = 24                         # Stage-A noiseless panel size (broad, to harvest trapped sims)
DEFAULT_TRAP_SEEDS = [51]        # the original defined trap (carries the r=1 open item)


def _load_json(path, default):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default


def _save_json(path, obj):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)


def trap_x0(seed):
    """Reproduce the Exp55 Arm-0 x0 for a trap seed EXACTLY (np.random.seed(seed))."""
    np.random.seed(seed)
    return np.random.uniform(0, 2 * np.pi, 2 * P)


def _key(trap_seed, sim, arm):
    return f"t{trap_seed}_s{sim}_{arm}"


def run_one(circ, gp, bp, edges, max_cut, n_qubits, x0, sim_seed, noise_model):
    """One COBYLA optimization at fixed x0 and fixed seed_simulator. noise_model=None -> noiseless."""
    if noise_model is None:
        sim = AerSimulator(seed_simulator=sim_seed)
    else:
        sim = AerSimulator(noise_model=noise_model, seed_simulator=sim_seed)
    best = optimize_cobyla_capture(circ, gp, bp, P, sim, edges, max_cut, n_qubits,
                                   SHOTS, MAX_ITER, x0)
    return float(best["ratio"])


def stage_a(circ, gp, bp, edges, max_cut, n_qubits, trap_seeds, ckpt):
    """Noiseless panel -> r_off(s) for each (trap_seed, sim). Cheap."""
    print(f"\n=== STAGE A (noiseless panel, K_A={K_A}) ===", flush=True)
    for ts in trap_seeds:
        x0 = trap_x0(ts)
        for i in range(K_A):
            s = SIM_BASE + i
            k = _key(ts, s, "off")
            if k in ckpt:
                continue
            r = run_one(circ, gp, bp, edges, max_cut, n_qubits, x0, s, None)
            ckpt[k] = r
            _save_json(CHECKPOINT_PATH, ckpt)
            tag = "TRAP" if r < ESCAPE_THRESHOLD else "escaped"
            print(f"  trap{ts} sim{s} noiseless: {r:.4f}  {tag}", flush=True)
    return ckpt


def trapped_off(trap_seed, ckpt):
    """Realizations where the noiseless run is genuinely trapped (r_off < threshold)."""
    out = []
    for i in range(K_A):
        s = SIM_BASE + i
        r = ckpt.get(_key(trap_seed, s, "off"))
        if r is not None and r < ESCAPE_THRESHOLD:
            out.append(s)
    return out


def stage_b(circ, gp, bp, edges, max_cut, n_qubits, trap_seeds, ckpt):
    """Noisy at the SAME (x0, sim) for ONLY the noiselessly-trapped realizations. Expensive."""
    print(f"\n=== STAGE B (noisy toggle on Trapped_off only) ===", flush=True)
    for ts in trap_seeds:
        x0 = trap_x0(ts)
        toff = trapped_off(ts, ckpt)
        print(f"  trap{ts}: |Trapped_off|={len(toff)} -> {toff}", flush=True)
        if not toff:
            print(f"  trap{ts}: nothing trapped noiselessly; no noisy runs needed.", flush=True)
        for s in toff:
            k = _key(ts, s, "on")
            if k in ckpt:
                continue
            _, _, _, _, _, _, noise_model = build_circuit()  # FakeMarrakesh NoiseModel
            r = run_one(circ, gp, bp, edges, max_cut, n_qubits, x0, s, noise_model)
            ckpt[k] = r
            _save_json(CHECKPOINT_PATH, ckpt)
            r_off = ckpt[_key(ts, s, "off")]
            flag = "RESCUED" if r >= ESCAPE_THRESHOLD else "still trapped"
            print(f"  trap{ts} sim{s} noisy: {r:.4f} (off={r_off:.4f}, Δ={r - r_off:+.4f}) {flag}",
                  flush=True)
    return ckpt


def finalize(trap_seeds, ckpt):
    """Compute pre-registered paired metrics + decision per trap seed."""
    report = {"threshold": ESCAPE_THRESHOLD, "per_trap": {}}
    for ts in trap_seeds:
        toff = trapped_off(ts, ckpt)
        deltas, rescues = [], 0
        for s in toff:
            r_on = ckpt.get(_key(ts, s, "on"))
            if r_on is None:
                continue
            r_off = ckpt[_key(ts, s, "off")]
            deltas.append(r_on - r_off)
            if r_on >= ESCAPE_THRESHOLD:
                rescues += 1
        # anti-rescue: noiselessly-escaped realizations that noise pushes back below threshold.
        esc = [SIM_BASE + i for i in range(K_A)
               if (ckpt.get(_key(ts, SIM_BASE + i, "off")) is not None
                   and ckpt[_key(ts, SIM_BASE + i, "off")] >= ESCAPE_THRESHOLD
                   and ckpt.get(_key(ts, SIM_BASE + i, "on")) is not None)]
        anti = sum(1 for s in esc if ckpt[_key(ts, s, "on")] < ESCAPE_THRESHOLD)
        n_toff_done = len(deltas)
        median_delta = float(np.median(deltas)) if deltas else None
        rescue_rate = rescues / n_toff_done if n_toff_done else None
        anti_rescue_rate = anti / len(esc) if esc else None

        if n_toff_done < 3:
            decision = "UNDERPOWERED (anecdote, not a rate; escalate to robust trap via --trap-seeds)"
        elif median_delta is not None and median_delta > 0 and (
                anti_rescue_rate is None or rescue_rate > anti_rescue_rate):
            decision = "GO (noise rescues this trap; escalate to G3 |T|>=2 for across-seed claim)"
        else:
            decision = "NO-GO (r=1 was trajectory noise; noise-as-resource closed at this substrate)"

        report["per_trap"][str(ts)] = {
            "trapped_off_sims": toff,
            "n_trapped_off_completed": n_toff_done,
            "median_delta": median_delta,
            "rescue_rate": rescue_rate,
            "anti_rescue_rate": anti_rescue_rate,
            "decision": decision,
        }
    _save_json(RESULTS_PATH, report)
    print("\n=== FINALIZE ===")
    print(json.dumps(report, indent=2))
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["A", "B", "finalize"], default="A",
                    help="A = cheap noiseless panel (default); B = expensive noisy toggle (gated on "
                         "ArmA completion); finalize = compute metrics from checkpoint.")
    ap.add_argument("--trap-seeds", type=int, nargs="+", default=DEFAULT_TRAP_SEEDS)
    args = ap.parse_args()

    ckpt = _load_json(CHECKPOINT_PATH, {})

    if args.stage == "finalize":
        finalize(args.trap_seeds, ckpt)
        return

    print("Building shared FakeMarrakesh-transpiled circuit (exp55 harness)...", flush=True)
    circ, gp, bp, edges, max_cut, n_qubits, _ = build_circuit()
    print(f"  depth={circ.depth()}  n_qubits={n_qubits}  max_cut={max_cut}", flush=True)

    if args.stage == "A":
        stage_a(circ, gp, bp, edges, max_cut, n_qubits, args.trap_seeds, ckpt)
        for ts in args.trap_seeds:
            print(f"\ntrap{ts}: Trapped_off = {trapped_off(ts, ckpt)} "
                  f"(run --stage B when ArmA is done, then --stage finalize)", flush=True)
    elif args.stage == "B":
        stage_b(circ, gp, bp, edges, max_cut, n_qubits, args.trap_seeds, ckpt)
        finalize(args.trap_seeds, ckpt)


if __name__ == "__main__":
    main()
