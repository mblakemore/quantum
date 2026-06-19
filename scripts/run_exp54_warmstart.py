#!/usr/bin/env python3
"""
Exp54: Warm-Start QAOA (p-Escalation Initialization)
Elder C5852 (pre-reg) → C5965 (build + smoke-test)

Pre-registration: /droid/repos/quantum/findings/exp54-warmstart-preregistration.md

HYPOTHESES (from pre-reg):
  H1 (primary): p=5 warm-start escape rate > p=5 cold-start (Exp53 baseline 0.667 @1024sh)
                refute if warm-start escapes <= cold-start across 10 seeds
  H2 (mechanism): warm-start benefit concentrates on seeds cold-start MISSES (rescue diversity)
  H3 (escalation): 3→4→5 escalation > 3→5 direct jump

INTERPRETATION SCOPE (added C3836; full text in pred_c3835_001 record):
  H1 is a WITHIN-QAOA initialization comparison (warm-start vs cold-start, SAME substrate),
  NOT a QAOA-vs-classical claim — a positive H1 is not structural quantum advantage (true by
  construction; do NOT invoke Omega(sqrt N) — that bound is for unstructured search, not this).
  EDGES_20 is a SINGLE random instance (numpy seed=46); the 10 seeds vary only x0, not the graph,
  so H1 speaks only to warm-start convergence-under-noise ON THIS INSTANCE. Separating exploitable
  STRUCTURE from optimization-landscape convenience (Elder C5972, N&C Ch6) needs a structured-
  instance arm — future work (Exp56-class), not built here.

DESIGN (matches Exp53 substrate exactly — same EDGES_20, FakeMarrakesh noise, seeds 42-51,
ESCAPE_THRESHOLD 0.640, COBYLA, transpile-once):
  Per seed:
    1. p=3 COBYLA from random x0 (seeded)  → capture best (γ,β)_p3  [the warm-start SOURCE]
    2. Exp54A: pad (γ,β)_p3 → p=5 [γ..,0,0, β..,0,0], COBYLA warm-start → escape@p5
    3. Exp54B: pad p3→p4, COBYLA → pad p4→p5, COBYLA → escape@p5 (escalation)
  Baseline: p=5 cold-start rate from Exp53 (0.667 @1024sh) — NOT re-run here.

PADDING (pre-reg conservative scheme): append zeros for new layers (identity warm-start).
  p=3 vector convention (evaluate_with_transpiled): params[:p]=gammas, params[p:]=betas
  → [γ1,γ2,γ3, β1,β2,β3]  pad→p5  [γ1,γ2,γ3,0,0, β1,β2,β3,0,0]

WHY THIS SCRIPT EXISTS (the build): Exp53 only persisted {seed,ratio,escaped} — NOT the
optimized (γ,β) vectors. Warm-start REQUIRES those vectors, so optimize_cobyla had to be
extended to RETURN best_x (params at best ratio), not just the ratio. That is the novel
plumbing here; everything else reuses run_exp46_fast / run_exp51 verbatim.

C5860 DISCIPLINE: full p=5 1024sh runs are ~3.7h/seed. This run is checkpoint/resume per
seed (atomic write after every seed) so a kill resumes from the last completed seed.

USAGE:
  python3 run_exp54_warmstart.py --smoke        # 2 seeds, 128sh, max_iter 10 (~minutes) — proves plumbing
  python3 run_exp54_warmstart.py --full         # 10 seeds, 1024sh — the real campaign (HARNESS-GATED, do not launch w/o coordinating Exp55)
  python3 run_exp54_warmstart.py --arm A         # only the 3→5 direct arm
"""
import sys, os, json, time, argparse
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

# ── Substrate constants (identical to Exp53) ──────────────────────────────────
ESCAPE_THRESHOLD = 0.640
SEEDS = list(range(42, 52))          # 42..51, same as Exp51/52/53
OPT_LEVEL = 1
P5_COLDSTART_BASELINE = 0.667        # Exp53 p5_cobyla_1024sh rate (the H1 comparator)

CKPT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "..", "results", "exp54_checkpoint.json")
RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "experiments", "exp54_results.json")


def _load_ckpt():
    if os.path.exists(CKPT):
        try:
            return json.load(open(CKPT))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_ckpt(c):
    os.makedirs(os.path.dirname(CKPT), exist_ok=True)
    tmp = CKPT + ".tmp"
    json.dump(c, open(tmp, "w"), indent=2)
    os.replace(tmp, CKPT)            # atomic


# ── Warm-start-capable COBYLA: returns (best_ratio, best_x) ───────────────────
# Extends run_exp51.optimize_cobyla, which returns only the ratio and starts from
# a random x0. Here we (a) accept an explicit x0 (the warm-start vector) and
# (b) track the PARAM VECTOR that achieved the best ratio — that vector is what
# the next p-layer pads from.
def optimize_cobyla_ws(x0, transpiled_qc, gamma_params, beta_params, p,
                       sim, edges, max_cut, n_qubits, shots, max_iter):
    best = {"ratio": 0.0, "x": np.array(x0, dtype=float)}

    def objective(x):
        r = evaluate_with_transpiled(
            x, transpiled_qc, gamma_params, beta_params,
            p, sim, edges, max_cut, n_qubits, shots)
        if r > best["ratio"]:
            best["ratio"] = r
            best["x"] = np.array(x, dtype=float)
        return -r

    minimize(objective, np.array(x0, dtype=float), method='COBYLA',
             options={'maxiter': max_iter, 'rhobeg': 0.5})
    return float(best["ratio"]), best["x"]


def pad_params(x_p, p_from, p_to):
    """Pad a length-2*p_from param vector to length 2*p_to with zeros for new layers.
    Convention: x = [gammas(p_from) ... | betas(p_from) ...]. New layers -> 0 (identity)."""
    x_p = np.asarray(x_p, dtype=float)
    gammas = x_p[:p_from]
    betas = x_p[p_from:]
    new = p_to - p_from
    g = np.concatenate([gammas, np.zeros(new)])
    b = np.concatenate([betas, np.zeros(new)])
    return np.concatenate([g, b])


def build_for_p(p, sim, n_qubits, edges):
    qc, gp, bp = build_parameterized_xbasis_qaoa(p, n_qubits, edges)
    tqc = transpile(qc, backend=sim, optimization_level=OPT_LEVEL)
    return tqc, gp, bp


def run_seed(seed, shots, max_iter_by_p, arms, sim, n_qubits, edges, max_cut, circuits):
    """One seed: p=3 base → warm-start arm(s). Returns a record dict."""
    np.random.seed(seed)
    rec = {"seed": seed, "shots": shots}
    t0 = time.time()

    # ---- p=3 base (random x0) — the warm-start SOURCE ----
    tqc3, gp3, bp3 = circuits[3]
    x0_p3 = np.random.uniform(0, 2 * np.pi, 6)
    r3, x3 = optimize_cobyla_ws(x0_p3, tqc3, gp3, bp3, 3, sim, edges, max_cut,
                                n_qubits, shots, max_iter_by_p[3])
    rec["p3_base"] = {"ratio": r3, "escaped": bool(r3 > ESCAPE_THRESHOLD),
                      "x": x3.tolist()}
    print(f"  seed={seed} p3-base ratio={r3:.4f} {'✓' if r3>ESCAPE_THRESHOLD else '✗'}", flush=True)

    # ---- Arm A: p3 → p5 direct warm-start ----
    if "A" in arms:
        tqc5, gp5, bp5 = circuits[5]
        x0_A = pad_params(x3, 3, 5)
        rA, xA = optimize_cobyla_ws(x0_A, tqc5, gp5, bp5, 5, sim, edges, max_cut,
                                    n_qubits, shots, max_iter_by_p[5])
        rec["A_p3to5"] = {"ratio": rA, "escaped": bool(rA > ESCAPE_THRESHOLD),
                          "x": xA.tolist()}
        print(f"        ArmA p3→p5  ratio={rA:.4f} {'✓ ESCAPED' if rA>ESCAPE_THRESHOLD else '✗ trapped'}", flush=True)

    # ---- Arm B: p3 → p4 → p5 escalation ----
    if "B" in arms:
        tqc4, gp4, bp4 = circuits[4]
        x0_B4 = pad_params(x3, 3, 4)
        r4, x4 = optimize_cobyla_ws(x0_B4, tqc4, gp4, bp4, 4, sim, edges, max_cut,
                                    n_qubits, shots, max_iter_by_p[4])
        tqc5, gp5, bp5 = circuits[5]
        x0_B5 = pad_params(x4, 4, 5)
        rB, xB = optimize_cobyla_ws(x0_B5, tqc5, gp5, bp5, 5, sim, edges, max_cut,
                                    n_qubits, shots, max_iter_by_p[5])
        rec["B_p3to4to5"] = {"ratio": rB, "p4_ratio": r4,
                             "escaped": bool(rB > ESCAPE_THRESHOLD), "x": xB.tolist()}
        print(f"        ArmB p3→p4→p5 ratio={rB:.4f} (p4={r4:.4f}) {'✓ ESCAPED' if rB>ESCAPE_THRESHOLD else '✗ trapped'}", flush=True)

    rec["elapsed_s"] = time.time() - t0
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true",
                    help="2 seeds, 128 shots, max_iter 10 — proves plumbing fast")
    ap.add_argument("--full", action="store_true",
                    help="10 seeds, 1024 shots — HARNESS-GATED real campaign")
    ap.add_argument("--arm", choices=["A", "B", "AB"], default="AB",
                    help="which warm-start arm(s) to run")
    args = ap.parse_args()

    if not (args.smoke or args.full):
        print("Specify --smoke (fast plumbing proof) or --full (real campaign). Refusing to guess.")
        sys.exit(2)

    arms = list(args.arm)  # "AB" -> ["A","B"]

    if args.smoke:
        seeds, shots = [42, 43], 128
        max_iter_by_p = {3: 10, 4: 10, 5: 10}
        mode = "SMOKE"
    else:
        seeds, shots = SEEDS, 1024
        max_iter_by_p = {3: 30, 4: 40, 5: 50}
        mode = "FULL"

    print("=" * 64)
    print(f"Exp54 Warm-Start QAOA — {mode} | arms={arms} | seeds={seeds} | shots={shots}")
    print(f"Threshold={ESCAPE_THRESHOLD} | p5 cold-start baseline (Exp53)={P5_COLDSTART_BASELINE}")
    print("=" * 64, flush=True)

    fake = FakeMarrakesh()
    sim = AerSimulator(noise_model=NoiseModel.from_backend(fake))
    edges, n_qubits = EDGES_20, N_QUBITS_20
    max_cut = brute_force_max_cut(n_qubits, edges)

    need_p = {3, 5} | ({4} if "B" in arms else set())
    circuits = {p: build_for_p(p, sim, n_qubits, edges) for p in sorted(need_p)}
    for p in sorted(need_p):
        print(f"  p={p}: transpiled depth={circuits[p][0].depth()}", flush=True)

    ckpt = _load_ckpt()
    # Mode/arms guard (Ember C3835): resume only when the checkpoint matches THIS run.
    # A SMOKE checkpoint (128sh/maxiter10) silently reused in a FULL run would skip
    # already-"done" seeds and contaminate the 1024sh campaign with sanity-only numbers.
    ck_mode, ck_arms = ckpt.get("mode"), ckpt.get("arms")
    if ckpt.get("data") and (ck_mode != mode or ck_arms != arms):
        bak = CKPT + f".stale-{ck_mode}-{''.join(ck_arms or [])}.bak"
        os.replace(CKPT, bak)
        print(f"  [reset] checkpoint was mode={ck_mode} arms={ck_arms} "
              f"!= this run mode={mode} arms={arms} — not resuming; backed up to {bak}",
              flush=True)
        ckpt = {}
    done = {int(r["seed"]): r for r in ckpt.get("data", [])}
    if done:
        print(f"  [resume] {len(done)} seed(s) done: {sorted(done)}", flush=True)
    results = [done[s] for s in seeds if s in done]

    for seed in seeds:
        if seed in done:
            continue
        rec = run_seed(seed, shots, max_iter_by_p, arms, sim, n_qubits, edges, max_cut, circuits)
        results.append(rec)
        ckpt = _load_ckpt()
        ckpt["mode"] = mode
        ckpt["arms"] = arms
        ckpt["data"] = results
        _save_ckpt(ckpt)

    # ── Summary ──
    def rate(key):
        vals = [r[key]["escaped"] for r in results if key in r]
        return (sum(vals), len(vals), (sum(vals) / len(vals) if vals else 0.0))

    print("\n" + "=" * 64)
    print("SUMMARY")
    print("=" * 64)
    eb = rate("p3_base"); print(f"  p3 base:        {eb[0]}/{eb[1]} = {eb[2]:.3f}")
    if "A" in arms:
        ea = rate("A_p3to5"); print(f"  ArmA p3→p5:     {ea[0]}/{ea[1]} = {ea[2]:.3f}  (vs cold-start {P5_COLDSTART_BASELINE})")
    if "B" in arms:
        ebb = rate("B_p3to4to5"); print(f"  ArmB p3→p4→p5:  {ebb[0]}/{ebb[1]} = {ebb[2]:.3f}")

    if mode == "FULL":
        out = {"experiment": "Exp54", "title": "Warm-Start QAOA p-escalation",
               "author": "Elder", "mode": mode, "arms": arms,
               "escape_threshold": ESCAPE_THRESHOLD, "seeds": seeds, "shots": shots,
               "p5_coldstart_baseline": P5_COLDSTART_BASELINE,
               "summary": {"p3_base_rate": eb[2],
                           "A_rate": rate("A_p3to5")[2] if "A" in arms else None,
                           "B_rate": rate("B_p3to4to5")[2] if "B" in arms else None},
               "data": results}
        json.dump(out, open(RESULTS, "w"), indent=2)
        print(f"\n  Wrote {RESULTS}")
    else:
        print("\n  SMOKE mode: plumbing proof only — NOT written to experiments/ results.")
        print("  (low shots/iter => escape numbers are NOT science, just sanity.)")


if __name__ == "__main__":
    main()
