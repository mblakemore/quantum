#!/usr/bin/env python3
"""
Exp89 (Whisper C4448) — Layout-draw DISTRIBUTION of the placement contribution at 208 gates.

WHY (F68's own #1 caveat): F68 (C4445) measured placement drift-free but from ONE VAR-208 layout
draw (opt1/seed31337) that read 0.99 this window vs 0.785 in Exp86 — a 0.205 layout-draw swing. So
F68 could say placement dominates in DIRECTION but the SHARE was "draw-dependent" (N=1 on vary axis).
This experiment samples the vary axis K times in ONE window to get the DISTRIBUTION: is "placement
dominates" draw-ROBUST (holds every draw) or an artifact of one lucky good layout?

  Objects (8 circuits x 2 bases = 16 PUBs, single job, one calibration window):
    ANCHOR 158 : opt=2 seed=100 folds=0   (shared base; identical circuit)
    FIX   208  : base folded +25 (CZ.CZ=I) -> SAME placement, +50 2q-gates (placement-held reference)
    VAR   208  : opt=1 x seeds {31337,11,101,271,1618,9001} -> K DIFFERENT layouts ~208 gates
                 (seed=31337 = the exact Exp88 VAR-208 draw, tie-back reproducibility)

  Per-draw placement contribution: placement_i = W(FIX 208) - W(VAR 208_i).
  {placement_i} is the distribution F68 sampled only once. Per-draw 2q count recorded (gate-count
  control: separate pure-layout variance from gate-count variance across draws).

PRE-COMMITTED CLAIM BOUNDARY (see experiments/exp89-placement-drawdist-preregistration.md):
  BRANCH 1 DRAW-ROBUST : every W_i < W_FIX (all placement_i>0) AND mean placement_i > gate-only.
  BRANCH 2 DRAW-DEP SIGN: some W_i >= W_FIX (good layout matches/beats fold) -> tail qualifier on F68.
  BRANCH 3 GATE-CONFOUND: W_i spread tracks recorded 2q-count spread -> layout variance is partly
                          gate-count variance; attribute honestly, flag |d2q|>15 draws.
  Floor: |placement_i| < ~0.08 is within ~2sigma of 0 = "consistent with a tie", not a reversal.

Provenance reuse: fold/FIX from Exp87, vary recipe + codeword verify from Exp86, grade from Exp84,
same-window co-submission from Exp88.

Usage:
  python3 run_exp89_placement_drawdist.py --scan     # FREE: verify all 8 objects, no QPU
  python3 run_exp89_placement_drawdist.py --submit   # QPU: one 16-PUB job on ibm_fez
  python3 run_exp89_placement_drawdist.py --grade     # grade (same cycle if done, else next)
"""
import sys, os, argparse, json, time, statistics
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_exp84_toric_bell_proxy import setup_code, build_circuit, grade, corr
from run_exp87_fixed_placement_folding import fold_routed, _count_2q, BASE_OPT, BASE_SEED, BASE_TWOQ
from run_exp86_gatecount_isolation import _verify_opt_preserves_codeword

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")

# Vary-place axis: K distinct layout draws at opt=1 targeting ~208 routed 2q-gates.
# seed=31337 is the exact Exp88 VAR-208 recipe (tie-back). The rest are fresh distinct draws.
VAR_SEEDS = [31337, 11, 101, 271, 1618, 9001]
VAR_OPT = 1
# Fixed-place reference: fold the ONE base transpilation (opt=2,seed=100 = the 158 anchor) to 208.
FIX_FOLD = {"folds": 25, "target_twoq": 208}
# Prior-window references for context (Exp88 same-window readings).
EXP88_REF = {"anchor_158": 1.1861, "fix_208": 1.1339, "var_208_seed31337": 0.9900}


def _base_transpile(code, basis, backend):
    from qiskit import transpile
    qc = build_circuit(code, basis)
    return transpile(qc, backend=backend, optimization_level=BASE_OPT, seed_transpiler=BASE_SEED)


def _vary_transpile(code, basis, backend, opt, seed):
    from qiskit import transpile
    qc = build_circuit(code, basis)
    return transpile(qc, backend=backend, optimization_level=opt, seed_transpiler=seed)


def _build_all(code, backend, verify_codeword=True):
    """Return (pubs, meta, ok) for ANCHOR + FIX208 + K VAR208 draws, each x {Z,X}.
    ANCHOR + FIX rely on the algebraic self-inverse guarantee (fold_routed raises if unsafe).
    Each VAR draw verified a true codeword the Exp86 way (19q noiseless witness ~2.0)."""
    n = code["n"]
    pubs, meta = [], []
    ok = True

    # --- ANCHOR 158 (shared base) ---
    base = {b: _base_transpile(code, b, backend) for b in ("Z", "X")}
    for b in ("Z", "X"):
        bt = _count_2q(base[b])
        if b == "Z" and bt != BASE_TWOQ:
            print(f"  ABORT: base Z 2q={bt} != {BASE_TWOQ} (calibration/transpiler moved).", flush=True)
            ok = False
    for b in ("Z", "X"):
        pubs.append(base[b].copy())
        meta.append({"axis": "anchor", "label": 158, "folds": 0, "basis": b, "twoq": _count_2q(base[b])})

    # --- FIX 208 (placement held, folded) ---
    for b in ("Z", "X"):
        folded = fold_routed(base[b], FIX_FOLD["folds"])
        tq = _count_2q(folded)
        match = (tq == FIX_FOLD["target_twoq"])
        ok = ok and match
        pubs.append(folded)
        meta.append({"axis": "fix", "label": 208, "folds": FIX_FOLD["folds"], "basis": b, "twoq": tq})
        print(f"  FIX  folds={FIX_FOLD['folds']} basis={b} 2q={tq:>4} "
              f"(target {FIX_FOLD['target_twoq']}) {'OK' if match else '!! MISMATCH'}", flush=True)

    # --- VAR 208 x K draws (different layouts) ---
    for seed in VAR_SEEDS:
        tqc = {b: _vary_transpile(code, b, backend, VAR_OPT, seed) for b in ("Z", "X")}
        if verify_codeword:
            res = {b: _verify_opt_preserves_codeword(code, b, n, backend, VAR_OPT, seed)
                   for b in ("Z", "X")}
            zz = corr(res["Z"])
            xb0 = corr({k: v for k, v in res["X"].items() if k[0] == 0})
            xb1 = corr({k: v for k, v in res["X"].items() if k[0] == 1})
            w = zz + (abs(xb0) + abs(xb1)) / 2
            cw_ok = abs(w - 2.0) <= 0.05
            ok = ok and cw_ok
            print(f"  VAR  opt={VAR_OPT} seed={seed:>6} routed-noiseless W={w:.4f} "
                  f"{'OK true-codeword' if cw_ok else '!! NOT codeword'}", flush=True)
        for b in ("Z", "X"):
            tq = _count_2q(tqc[b])
            pubs.append(tqc[b])
            meta.append({"axis": "var", "label": 208, "opt": VAR_OPT, "seed": seed,
                         "basis": b, "twoq": tq})
        zq = _count_2q(tqc["Z"])
        d2q = zq - FIX_FOLD["target_twoq"]
        print(f"  VAR  opt={VAR_OPT} seed={seed:>6} Z-2q={zq:>4} (d2q={d2q:+d} vs FIX208)"
              f"{'  ⚠ gate-count-contaminated (|d2q|>15)' if abs(d2q) > 15 else ''}", flush=True)

    return pubs, meta, ok


def scan(backend_name="ibm_fez"):
    from run_exp66_qpu_partb import _get_ibm_service
    code = setup_code(L=3)
    service = _get_ibm_service()
    backend = service.backend(backend_name)
    print(f"Backend: {backend.name} | pending_jobs={backend.status().pending_jobs}", flush=True)
    print(f"Base transpile: opt={BASE_OPT} seed={BASE_SEED} (expect {BASE_TWOQ} Z 2q)")
    print(f"VAR axis: opt={VAR_OPT} seeds={VAR_SEEDS}\n", flush=True)
    pubs, meta, ok = _build_all(code, backend, verify_codeword=True)
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(os.path.join(RESULTS_DIR, "exp89_scan.json"), "w") as f:
        json.dump({"meta": meta, "n_pubs": len(pubs), "exp88_ref": EXP88_REF,
                   "var_seeds": VAR_SEEDS, "var_opt": VAR_OPT}, f, indent=2)
    print(f"\nSaved results/exp89_scan.json | {len(pubs)} PUBs | "
          f"{'READY for --submit' if ok else 'ABORT (mismatch/codeword fail)'}")
    return ok


def submit(backend_name="ibm_fez", shots=2000):
    from qiskit_ibm_runtime import SamplerV2
    from run_exp66_qpu_partb import _get_ibm_service
    code = setup_code(L=3)
    service = _get_ibm_service()
    backend = service.backend(backend_name)
    print(f"Backend: {backend.name} | pending_jobs={backend.status().pending_jobs}", flush=True)
    pubs, meta, ok = _build_all(code, backend, verify_codeword=True)
    if not ok:
        print("\nABORT: build/verify failed; not spending QPU.", flush=True)
        return None
    sampler = SamplerV2(mode=backend)
    sampler.options.default_shots = shots
    job = sampler.run(pubs)                  # ONE job -> ONE window for all 16 circuits
    jid = job.job_id()
    print(f"\nSubmitted ONE job with {len(pubs)} PUBs -> job_id={jid}", flush=True)
    manifest = {"backend": backend_name, "shots": shots, "job_id": jid, "pub_meta": meta,
                "base_opt": BASE_OPT, "base_seed": BASE_SEED, "base_twoq": BASE_TWOQ,
                "var_seeds": VAR_SEEDS, "var_opt": VAR_OPT, "exp88_ref": EXP88_REF,
                "submitted_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(os.path.join(RESULTS_DIR, "exp89_jobids.json"), "w") as fh:
        json.dump(manifest, fh, indent=2)
    print("Manifest saved: results/exp89_jobids.json (grade this cycle if done, else next)")
    return manifest


def _witness(cb, code, n):
    gz = grade(cb["Z"], code, "Z", n); gx = grade(cb["X"], code, "X", n)
    zz = corr(gz)
    xb0 = corr({k: v for k, v in gx.items() if k[0] == 0})
    xb1 = corr({k: v for k, v in gx.items() if k[0] == 1})
    return zz + (abs(xb0) + abs(xb1)) / 2


def grade_run():
    from run_exp66_qpu_partb import _get_ibm_service
    with open(os.path.join(RESULTS_DIR, "exp89_jobids.json")) as fh:
        man = json.load(fh)
    code = setup_code(L=3); n = code["n"]
    service = _get_ibm_service()
    job = service.job(man["job_id"])
    st = job.status()
    print(f"job {man['job_id']} status={st}", flush=True)
    if str(st) not in ("DONE", "JobStatus.DONE"):
        print("Job not finished yet — re-run --grade next cycle (manifest persisted).", flush=True)
        return None
    res = job.result()
    # key: (axis, seed_or_none) -> {basis: counts}; also record twoq
    by = defaultdict(dict)
    twoq = {}
    for i, meta in enumerate(man["pub_meta"]):
        key = (meta["axis"], meta.get("seed"))
        counts = res[i].data.c.get_counts() if hasattr(res[i].data, "c") else res[i].join_data().get_counts()
        by[key][meta["basis"]] = counts
        if meta["basis"] == "Z":
            twoq[key] = meta["twoq"]

    W = {k: _witness(cb, code, n) for k, cb in by.items()}
    w158 = W[("anchor", None)]
    w_fix = W[("fix", None)]
    gate_only = w158 - w_fix                     # gate-count(+depth) only, placement held

    # Per-draw placement contribution distribution
    draws = []
    for seed in man["var_seeds"]:
        wi = W[("var", seed)]
        pi = w_fix - wi                          # placement contribution for this draw
        d2q = twoq[("var", seed)] - 208
        draws.append({"seed": seed, "W": wi, "placement_i": pi, "twoq": twoq[("var", seed)],
                      "d2q": d2q, "gate_contaminated": abs(d2q) > 15})

    p_list = [d["placement_i"] for d in draws]
    w_list = [d["W"] for d in draws]
    p_mean = statistics.mean(p_list)
    p_std = statistics.pstdev(p_list) if len(p_list) > 1 else 0.0
    n_reversed = sum(1 for d in draws if d["placement_i"] <= 0.08)   # within ~2sigma of tie or below
    n_strict_reversed = sum(1 for d in draws if d["placement_i"] <= 0)

    # Gate-count confound check: correlation of W_i with twoq across draws
    if len(draws) > 2:
        try:
            gc_corr = statistics.correlation([d["twoq"] for d in draws], w_list)
        except Exception:
            gc_corr = float("nan")
    else:
        gc_corr = float("nan")

    # Verdict (pre-committed branches)
    if n_strict_reversed == 0 and p_mean > gate_only:
        branch = "BRANCH 1 DRAW-ROBUST — placement dominates every draw; mean placement > gate-only"
    elif n_strict_reversed > 0:
        branch = (f"BRANCH 2 DRAW-DEPENDENT SIGN — {n_strict_reversed}/{len(draws)} draws reverse "
                  f"(good layout matches/beats fold); mean direction "
                  f"{'still placement' if p_mean > 0 else 'flips'}")
    else:
        branch = "BRANCH 1 (weak) — no strict reversal but mean placement <= gate-only; near tie"

    print(f"\n{'object':>16} | {'W':>8} | {'2q':>4} | {'placement_i':>11}")
    print(f"{'ANCHOR 158':>16} | {w158:>8.4f} |    - |     (ref: Exp88 {EXP88_REF['anchor_158']})")
    print(f"{'FIX 208':>16} | {w_fix:>8.4f} |  208 |     (ref: Exp88 {EXP88_REF['fix_208']})")
    for d in sorted(draws, key=lambda x: x["placement_i"]):
        flag = " ⚠gate" if d["gate_contaminated"] else ""
        tie = " ~tie" if abs(d["placement_i"]) < 0.08 else ""
        print(f"{'VAR seed='+str(d['seed']):>16} | {d['W']:>8.4f} | {d['twoq']:>4} | "
              f"{d['placement_i']:>+11.4f}{tie}{flag}")
    print(f"\n--- PLACEMENT CONTRIBUTION DISTRIBUTION (K={len(draws)} draws, drift-free) ---")
    print(f"  gate-count-only (W158-Wfix)   = {gate_only:+.4f}")
    print(f"  placement_i  mean±std         = {p_mean:+.4f} ± {p_std:.4f}")
    print(f"  placement_i  min / max        = {min(p_list):+.4f} / {max(p_list):+.4f}")
    print(f"  draws at/below tie (<=+0.08)  = {n_reversed}/{len(draws)}  "
          f"(strict reversal <=0: {n_strict_reversed})")
    print(f"  W_i vs 2q-count corr (Branch3)= {gc_corr:+.3f}  "
          f"({'gate-count confound plausible' if abs(gc_corr) > 0.6 else 'no strong gate-count confound'})")
    print(f"  VERDICT: {branch}")

    out = {"W": {f"{a}_{s}": v for (a, s), v in W.items()}, "gate_only": gate_only,
           "draws": draws, "placement_mean": p_mean, "placement_std": p_std,
           "placement_min": min(p_list), "placement_max": max(p_list),
           "n_reversed_tie": n_reversed, "n_strict_reversed": n_strict_reversed,
           "gatecount_corr": gc_corr, "verdict": branch, "reference": man}
    with open(os.path.join(RESULTS_DIR, "exp89_graded.json"), "w") as fh:
        json.dump(out, fh, indent=2)
    print("Saved results/exp89_graded.json")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--grade", action="store_true")
    ap.add_argument("--backend", default="ibm_fez")
    ap.add_argument("--shots", type=int, default=2000)
    args = ap.parse_args()
    if args.scan:
        scan(backend_name=args.backend)
    elif args.submit:
        submit(backend_name=args.backend, shots=args.shots)
    elif args.grade:
        grade_run()
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
