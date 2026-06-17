#!/usr/bin/env python3
"""
Exp53 race-safe PARALLEL resume runner (Elder C5876).

WHY: The serial harness (run_exp53_depth_vs_shots.py) runs seeds one-at-a-time with a
read-modify-write checkpoint that is NOT multiprocess-safe (two workers appending to the
same arm => lost update). At ~220 min/1024sh-seed × 7 remaining seeds = ~25.7h serial
(the 15h-runaway I killed C5860). Exp53 is 20q => below Ember's C3754 GPU break-even
(<=22q CPU wins), so the lever is CPU multiprocessing across the INDEPENDENT seeds.

DESIGN (race-safe): each seed runs in its own worker that writes its OWN result file
(results/exp53_seed_<arm>_<seed>.json) — no shared-file contention. Workers are pinned
single-threaded (OMP_NUM_THREADS=1, max_parallel_threads=1) so N workers fit N cores
cleanly without oversubscription. The MAIN process merges completed per-seed files into
the canonical checkpoint atomically (same _save_checkpoint as the harness). Idempotent:
re-running skips seeds already in the checkpoint AND seeds with a finished result file.

USAGE:  WORKERS=7 python3 resume_exp53_parallel.py [--arm p5_COBYLA_1024sh] [--dry-run]
Resumable: kill anytime; completed per-seed files + checkpoint survive; re-run continues.
"""
import sys, os, json, time, argparse
# Pin BLAS/OpenMP BEFORE importing numpy/aer so each worker is single-threaded.
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
import multiprocessing as mp
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ARM_DEFAULT = "p5_COBYLA_1024sh"
ALL_SEEDS = list(range(42, 52))
ESCAPE_THRESHOLD = 0.640
MAX_ITER_P5 = 50
SEEDDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
CKPT = os.path.join(SEEDDIR, "exp53_checkpoint.json")

def arm_params(arm):
    # arm label encodes p and shots: p5_COBYLA_1024sh
    p = int(arm.split("_")[0][1:])
    shots = int(arm.split("_")[-1].replace("sh", ""))
    return p, shots

def seed_file(arm, seed):
    return os.path.join(SEEDDIR, f"exp53_seed_{arm}_{seed}.json")

def load_ckpt():
    if os.path.exists(CKPT):
        try:
            return json.load(open(CKPT))
        except Exception:
            return {}
    return {}

def save_ckpt(c):
    os.makedirs(SEEDDIR, exist_ok=True)
    tmp = CKPT + ".tmp"
    json.dump(c, open(tmp, "w"), indent=2)
    os.replace(tmp, CKPT)

def worker(args):
    """Run one seed single-threaded; write its own result file; return summary."""
    arm, seed = args
    p, shots = arm_params(arm)
    import numpy as np
    from qiskit import transpile
    from qiskit_aer import AerSimulator
    from qiskit_aer.noise import NoiseModel
    from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
    from run_exp46_fast import (EDGES_20, N_QUBITS_20, brute_force_max_cut,
                                build_parameterized_xbasis_qaoa)
    from run_exp51_spsa_vs_cobyla import optimize_cobyla
    nm = NoiseModel.from_backend(FakeMarrakesh())
    edges, nq = EDGES_20, N_QUBITS_20
    mc = brute_force_max_cut(nq, edges)
    qc, g, b = build_parameterized_xbasis_qaoa(p, nq, edges)
    sim = AerSimulator(noise_model=nm, max_parallel_threads=1,
                       max_parallel_experiments=1)
    tqc = transpile(qc, backend=sim, optimization_level=1)
    np.random.seed(seed)
    t0 = time.time()
    ratio = optimize_cobyla(tqc, g, b, p, sim, edges, mc, nq, shots, MAX_ITER_P5)
    elapsed = time.time() - t0
    rec = {"seed": seed, "ratio": float(ratio),
           "escaped": bool(ratio > ESCAPE_THRESHOLD), "elapsed_s": float(elapsed)}
    json.dump(rec, open(seed_file(arm, seed), "w"), indent=2)
    return rec

def merge_into_ckpt(arm):
    """Fold any finished per-seed files into the canonical checkpoint."""
    p, shots = arm_params(arm)
    c = load_ckpt()
    existing = {int(r["seed"]): r for r in c.get(arm, {}).get("data", [])}
    for s in ALL_SEEDS:
        f = seed_file(arm, s)
        if os.path.exists(f):
            try:
                existing[s] = json.load(open(f))
            except Exception:
                pass
    data = [existing[s] for s in sorted(existing)]
    esc = sum(1 for r in data if r["escaped"])
    c[arm] = {"p": p, "shots": shots, "max_iter": MAX_ITER_P5,
              "escaped": esc, "completed": len(data),
              "rate_so_far": esc / len(data) if data else 0, "data": data}
    save_ckpt(c)
    return c[arm]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", default=ARM_DEFAULT)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    arm = args.arm
    workers = int(os.environ.get("WORKERS", "6"))
    c = load_ckpt()
    done = {int(r["seed"]) for r in c.get(arm, {}).get("data", [])}
    done |= {s for s in ALL_SEEDS if os.path.exists(seed_file(arm, s))}
    remaining = [s for s in ALL_SEEDS if s not in done]
    print(f"[resume] arm={arm} done={sorted(done)} remaining={remaining} workers={workers}", flush=True)
    if args.dry_run or not remaining:
        if not remaining:
            print("[resume] nothing remaining — merging + done", flush=True)
            print(json.dumps(merge_into_ckpt(arm), indent=2)[:400], flush=True)
        return
    t0 = time.time()
    with mp.Pool(min(workers, len(remaining))) as pool:
        for rec in pool.imap_unordered(worker, [(arm, s) for s in remaining]):
            status = "ESCAPED" if rec["escaped"] else "trapped"
            print(f"[done] seed={rec['seed']} ratio={rec['ratio']:.4f} {status} "
                  f"({rec['elapsed_s']:.0f}s) wall={time.time()-t0:.0f}s", flush=True)
            merge_into_ckpt(arm)  # fold in as each finishes (crash-safe progress)
    final = merge_into_ckpt(arm)
    print(f"\n[resume] COMPLETE arm={arm}: {final['escaped']}/{final['completed']} "
          f"= {final['rate_so_far']:.2f} | total wall={time.time()-t0:.0f}s", flush=True)

if __name__ == "__main__":
    main()
