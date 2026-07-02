#!/usr/bin/env python3
"""
Exp88 (Whisper C4442) — Same-window placement/gate-count partition.

WHY (the open caveat F67 named):
  F67 partitioned the Exp86 witness-decline into gate-count (~40%) vs placement (~60%) by comparing
  Exp87's FIXED-placement fold slope against Exp86's VARY-placement slope. But those two axes were
  run in DIFFERENT calibration windows: the 158-gate object read 1.064 (Exp86 window) vs 1.108
  (Exp87 window) = +0.044 pure cross-window drift, comparable to the fold-10 step (0.024). So the
  "~40/60" split was an ESTIMATE, not a measurement. F67 explicitly flagged: "A clean same-window
  replication of the Exp86 placement axis would tighten the partition."

THIS EXPERIMENT does exactly that: co-submit BOTH axes in ONE job -> ONE calibration window, so the
placement contribution is a direct within-window subtraction, drift-free.

  Objects (5 distinct circuits x 2 bases = 10 PUBs, single job):
    ANCHOR 158 : opt=2 seed=100 folds=0   (shared base; identical circuit for both axes)
    FIX   178  : base folded +10 (CZ.CZ=I) -> SAME placement, +20 2q-gates
    FIX   208  : base folded +25          -> SAME placement, +50 2q-gates
    VAR   178  : opt=3 seed=7             -> DIFFERENT placement (Exp86 MID recipe)
    VAR   208  : opt=1 seed=31337         -> DIFFERENT placement (Exp86 HIGH recipe)

  Within-window partition (all read in the SAME window; no drift term):
    Total decline (vary)      = W(158) - W(VAR 208)
    Gate-count-only (fixed)   = W(158) - W(FIX 208)
    Placement contribution    = W(FIX 208) - W(VAR 208)      <-- the number F67 could only estimate

PRE-COMMITTED CLAIM BOUNDARY (both directions bank a clean result):
  - If placement contribution > gate-count-only contribution IN-WINDOW -> F67's "placement dominates"
    is CONFIRMED as a measurement (drift removed), and the split is quantified.
  - If the two are comparable / gate-count >= placement in-window -> F67's 60/40 was inflated by the
    +0.044 drift; the honest revision is "gate-count and placement are co-equal levers", and I say so.
  - Depth stays coupled to gate-count under folding (stated bound, same as Exp87): FIX axis measures
    the JOINT gate-count+depth quantity, not gate-count alone. Not claiming a mechanism (witness is
    a scalar).

Provenance reuse (no re-derivation): fold from Exp87, vary-place recipe + codeword verification from
Exp86, code/circuit/grading from Exp84.

Usage:
  python3 run_exp88_same_window_partition.py --scan     # FREE: verify all 5 objects, no QPU
  python3 run_exp88_same_window_partition.py --submit   # QPU: one 10-PUB job on ibm_fez
  python3 run_exp88_same_window_partition.py --grade     # grade (same cycle if job done, else next)
"""
import sys, os, argparse, json, time
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_exp84_toric_bell_proxy import setup_code, build_circuit, grade, corr
from run_exp87_fixed_placement_folding import fold_routed, _count_2q, BASE_OPT, BASE_SEED, BASE_TWOQ
from run_exp86_gatecount_isolation import _verify_opt_preserves_codeword

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")

# Vary-place axis = Exp86 MID/HIGH recipes (the 158 anchor is the shared fold base, not repeated here).
VAR_POINTS = [
    {"opt": 3, "seed": 7,     "label_twoq_Z": 178},   # Exp86 MID placement
    {"opt": 1, "seed": 31337, "label_twoq_Z": 208},   # Exp86 HIGH placement
]
# Fixed-place axis = fold the ONE base transpilation (opt=2,seed=100) that also = the 158 anchor.
FIX_FOLDS = [
    {"folds": 10, "target_twoq": 178},
    {"folds": 25, "target_twoq": 208},
]
# Exp87 fixed-place reference (prior window) and Exp86 vary-place reference (prior window), for context.
EXP87_FIX_REF = {"158": 1.108, "178": 1.084, "208": 1.000}
EXP86_VAR_REF = {"158": 1.064, "178": 0.904, "208": 0.785}


def _base_transpile(code, basis, backend):
    from qiskit import transpile
    qc = build_circuit(code, basis)
    return transpile(qc, backend=backend, optimization_level=BASE_OPT, seed_transpiler=BASE_SEED)


def _vary_transpile(code, basis, backend, opt, seed):
    from qiskit import transpile
    qc = build_circuit(code, basis)
    return transpile(qc, backend=backend, optimization_level=opt, seed_transpiler=seed)


def _build_all(code, backend, verify_codeword=True):
    """Return (pubs, pub_meta) for all 5 objects x 2 bases. Verifies each object is legitimate.
    ANCHOR + FIX rely on the algebraic self-inverse guarantee (fold_routed raises if unsafe).
    VAR points are verified as true codewords the same way Exp86 did (19q noiseless witness ~2.0)."""
    n = code["n"]
    pubs, meta = [], []
    ok = True

    # --- ANCHOR 158 (shared base, folds=0) + FIX folds (same placement) ---
    base = {b: _base_transpile(code, b, backend) for b in ("Z", "X")}
    for b in ("Z", "X"):
        bt = _count_2q(base[b])
        if b == "Z" and bt != BASE_TWOQ:
            print(f"  ABORT: base Z 2q={bt} != {BASE_TWOQ} (calibration/transpiler moved).", flush=True)
            ok = False
    # anchor
    for b in ("Z", "X"):
        pubs.append(base[b].copy())
        meta.append({"axis": "anchor", "label_twoq_Z": 158, "folds": 0, "basis": b,
                     "twoq": _count_2q(base[b])})
    # fixed-place folds (same physical qubits; CZ.CZ=I -> fold_routed raises if native 2q not self-inverse)
    for f in FIX_FOLDS:
        for b in ("Z", "X"):
            folded = fold_routed(base[b], f["folds"])
            tq = _count_2q(folded)
            match = (tq == f["target_twoq"])
            ok = ok and match
            pubs.append(folded)
            meta.append({"axis": "fix", "label_twoq_Z": f["target_twoq"], "folds": f["folds"],
                         "basis": b, "twoq": tq})
            print(f"  FIX  folds={f['folds']:>2} basis={b} 2q={tq:>4} (target {f['target_twoq']}) "
                  f"{'OK' if match else '!! MISMATCH'}", flush=True)

    # --- VAR points (different placements, Exp86 recipe) ---
    for pt in VAR_POINTS:
        tqc = {b: _vary_transpile(code, b, backend, pt["opt"], pt["seed"]) for b in ("Z", "X")}
        if verify_codeword:
            res = {b: _verify_opt_preserves_codeword(code, b, n, backend, pt["opt"], pt["seed"])
                   for b in ("Z", "X")}
            zz = corr(res["Z"])
            xb0 = corr({k: v for k, v in res["X"].items() if k[0] == 0})
            xb1 = corr({k: v for k, v in res["X"].items() if k[0] == 1})
            w = zz + (abs(xb0) + abs(xb1)) / 2
            cw_ok = abs(w - 2.0) <= 0.05
            ok = ok and cw_ok
            print(f"  VAR  opt={pt['opt']} seed={pt['seed']} label={pt['label_twoq_Z']} "
                  f"routed-noiseless W={w:.4f} {'OK true-codeword' if cw_ok else '!! NOT codeword'}",
                  flush=True)
        for b in ("Z", "X"):
            tq = _count_2q(tqc[b])
            pubs.append(tqc[b])
            meta.append({"axis": "var", "label_twoq_Z": pt["label_twoq_Z"], "opt": pt["opt"],
                         "seed": pt["seed"], "basis": b, "twoq": tq})
            print(f"  VAR  opt={pt['opt']} seed={pt['seed']} basis={b} 2q={tq}", flush=True)

    return pubs, meta, ok


def scan(backend_name="ibm_fez"):
    from run_exp66_qpu_partb import _get_ibm_service
    code = setup_code(L=3)
    service = _get_ibm_service()
    backend = service.backend(backend_name)
    print(f"Backend: {backend.name} | pending_jobs={backend.status().pending_jobs}", flush=True)
    print(f"Base transpile: opt={BASE_OPT} seed={BASE_SEED} (expect {BASE_TWOQ} Z 2q)\n", flush=True)
    pubs, meta, ok = _build_all(code, backend, verify_codeword=True)
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(os.path.join(RESULTS_DIR, "exp88_scan.json"), "w") as f:
        json.dump({"meta": meta, "n_pubs": len(pubs), "exp87_fix_ref": EXP87_FIX_REF,
                   "exp86_var_ref": EXP86_VAR_REF}, f, indent=2)
    print(f"\nSaved results/exp88_scan.json | {len(pubs)} PUBs | "
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
    job = sampler.run(pubs)                  # ONE job -> ONE window for all 10 circuits
    jid = job.job_id()
    print(f"\nSubmitted ONE job with {len(pubs)} PUBs -> job_id={jid}", flush=True)
    manifest = {"backend": backend_name, "shots": shots, "job_id": jid, "pub_meta": meta,
                "base_opt": BASE_OPT, "base_seed": BASE_SEED, "base_twoq": BASE_TWOQ,
                "exp87_fix_ref": EXP87_FIX_REF, "exp86_var_ref": EXP86_VAR_REF,
                "submitted_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(os.path.join(RESULTS_DIR, "exp88_jobids.json"), "w") as fh:
        json.dump(manifest, fh, indent=2)
    print("Manifest saved: results/exp88_jobids.json (grade this cycle if done, else next)")
    return manifest


def _witness(cb, code, n):
    gz = grade(cb["Z"], code, "Z", n); gx = grade(cb["X"], code, "X", n)
    zz = corr(gz)
    xb0 = corr({k: v for k, v in gx.items() if k[0] == 0})
    xb1 = corr({k: v for k, v in gx.items() if k[0] == 1})
    return zz + (abs(xb0) + abs(xb1)) / 2


def grade_run():
    from run_exp66_qpu_partb import _get_ibm_service
    with open(os.path.join(RESULTS_DIR, "exp88_jobids.json")) as fh:
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
    by = defaultdict(dict)   # (axis,label) -> {basis: counts}
    for i, meta in enumerate(man["pub_meta"]):
        counts = res[i].data.c.get_counts() if hasattr(res[i].data, "c") else res[i].join_data().get_counts()
        by[(meta["axis"], meta["label_twoq_Z"])][meta["basis"]] = counts

    W = {}
    for (axis, lbl), cb in by.items():
        W[(axis, lbl)] = _witness(cb, code, n)

    # Anchor (158) is shared by both axes.
    w158 = W[("anchor", 158)]
    w_fix178, w_fix208 = W[("fix", 178)], W[("fix", 208)]
    w_var178, w_var208 = W[("var", 178)], W[("var", 208)]

    total_decline = w158 - w_var208            # vary-place: gate-count + placement + (no drift, same window)
    gate_only     = w158 - w_fix208            # fixed-place: gate-count(+coupled depth) only
    placement     = w_fix208 - w_var208        # the isolated placement contribution, drift-free
    gate_frac = gate_only / total_decline if abs(total_decline) > 1e-9 else float("nan")
    plc_frac  = placement / total_decline if abs(total_decline) > 1e-9 else float("nan")

    print(f"\n{'object':>12} | {'W(this window)':>14} | {'prior-window ref':>16}")
    print(f"{'ANCHOR 158':>12} | {w158:>14.4f} | fix {man['exp87_fix_ref']['158']} / var {man['exp86_var_ref']['158']}")
    print(f"{'FIX 178':>12} | {w_fix178:>14.4f} | {man['exp87_fix_ref']['178']:>16}")
    print(f"{'FIX 208':>12} | {w_fix208:>14.4f} | {man['exp87_fix_ref']['208']:>16}")
    print(f"{'VAR 178':>12} | {w_var178:>14.4f} | {man['exp86_var_ref']['178']:>16}")
    print(f"{'VAR 208':>12} | {w_var208:>14.4f} | {man['exp86_var_ref']['208']:>16}")
    print(f"\n--- IN-WINDOW PARTITION (158 -> 208, drift-free) ---")
    print(f"  Total decline (vary-place)   = {total_decline:+.4f}")
    print(f"  Gate-count-only (fixed-place) = {gate_only:+.4f}  ({gate_frac*100:.0f}% of total)")
    print(f"  Placement contribution        = {placement:+.4f}  ({plc_frac*100:.0f}% of total)")
    verdict = ("PLACEMENT DOMINATES (F67 confirmed as measurement)" if placement > gate_only
               else "GATE-COUNT >= PLACEMENT in-window (F67 60/40 was drift-inflated)")
    print(f"  VERDICT: {verdict}")

    out = {"W": {f"{a}_{l}": v for (a, l), v in W.items()},
           "total_decline": total_decline, "gate_only": gate_only, "placement": placement,
           "gate_frac": gate_frac, "placement_frac": plc_frac, "verdict": verdict,
           "reference": man}
    with open(os.path.join(RESULTS_DIR, "exp88_graded.json"), "w") as fh:
        json.dump(out, fh, indent=2)
    print("Saved results/exp88_graded.json")
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
