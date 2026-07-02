#!/usr/bin/env python3
"""
Exp87 (Whisper C4439) — Fixed-placement gate-count isolation via unitary folding.

See experiments/exp87-fixed-placement-gate-folding-preregistration.md for the pre-committed
claim boundary. In one line: Exp86 varied 2q-gate count by re-transpiling (opt,seed), which also
moved the PLACEMENT (which physical qubits) and depth. This holds placement FIXED and scales
2q-count by inserting CZ.CZ = I pairs into the ONE routed physical circuit -> removes the placement
confound. Depth stays coupled (stated bound; cannot separate gate-count from depth by folding).

Semantics preservation is ALGEBRAIC (CZ self-inverse: CZ.CZ.CZ = CZ), not simulated -- so no
19-qubit sim is needed, unlike Exp86. We only assert (a) the native 2q gate is self-inverse and
(b) inserted copies act on the same physical qubit pair.

Usage:
  python3 run_exp87_fixed_placement_folding.py --scan     # FREE: build folds, verify counts, no QPU
  python3 run_exp87_fixed_placement_folding.py --submit   # QPU: one 6-PUB job on ibm_fez
  python3 run_exp87_fixed_placement_folding.py --grade     # next cycle
"""
import sys, os, argparse, json, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_exp84_toric_bell_proxy import setup_code, build_circuit, grade as grade_witness, corr

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")

# Fixed placement point (= Exp86 LOW true-codeword). All folds derive from THIS one transpilation.
BASE_OPT, BASE_SEED, BASE_TWOQ = 2, 100, 158
# fold_n gates -> +2 * fold_n 2q-gates. Targets overlay Exp86's 158/178/208 axis.
FOLD_SCHEDULE = [
    {"folds": 0,  "target_twoq": 158},   # unfolded baseline (Exp86 LOW object, byte-identical)
    {"folds": 10, "target_twoq": 178},   # matches Exp86 MID gate-count, SAME placement
    {"folds": 25, "target_twoq": 208},   # matches Exp86 HIGH gate-count, SAME placement
]
SELF_INVERSE_2Q = {"cz", "cx", "cnot", "swap"}  # G.G = I ; native Heron 2q = cz


def _count_2q(qc):
    return sum(1 for i in qc.data if i.operation.num_qubits == 2)


def fold_routed(tqc, n_folds):
    """Return a copy of the routed circuit with the first n_folds native 2q-gates folded G->G.G.G.
    Net unitary identical (self-inverse gate). Placement/layout untouched. +2 2q-gates per fold."""
    if n_folds == 0:
        return tqc.copy()
    new = tqc.copy_empty_like()
    folded = 0
    for inst in tqc.data:
        new.append(inst.operation, inst.qubits, inst.clbits)
        if inst.operation.num_qubits == 2 and folded < n_folds:
            name = inst.operation.name.lower()
            if name not in SELF_INVERSE_2Q:
                raise RuntimeError(f"native 2q gate '{name}' is not self-inverse; "
                                   f"cannot fold safely -- abort (do NOT spend QPU).")
            # insert two more copies on the SAME physical qubits -> G.G.G = G
            new.append(inst.operation, inst.qubits, inst.clbits)
            new.append(inst.operation, inst.qubits, inst.clbits)
            folded += 1
    if folded != n_folds:
        raise RuntimeError(f"requested {n_folds} folds but circuit only had {folded} 2q-gates.")
    return new


def _build_folded_isa(code, basis, backend, n_folds):
    """Transpile the base point ONCE, then fold. Returns (folded_isa_circuit, twoq_count)."""
    from qiskit import transpile
    qc = build_circuit(code, basis)
    base = transpile(qc, backend=backend, optimization_level=BASE_OPT, seed_transpiler=BASE_SEED)
    folded = fold_routed(base, n_folds)
    return folded, _count_2q(folded), _count_2q(base)


def scan(backend_name="ibm_fez"):
    from run_exp66_qpu_partb import _get_ibm_service
    code = setup_code(L=3)
    service = _get_ibm_service()
    backend = service.backend(backend_name)
    # identify the native 2q gate name
    twoq_names = [op for op in backend.target.operation_names if op.lower() in SELF_INVERSE_2Q]
    print(f"Backend: {backend.name} | native self-inverse 2q gates present: {twoq_names}", flush=True)
    print(f"Base transpilation: opt={BASE_OPT} seed={BASE_SEED} (Exp86 LOW, expect {BASE_TWOQ} 2q)\n")
    rows = []
    ok = True
    for basis in ["Z", "X"]:
        for f in FOLD_SCHEDULE:
            circ, twoq, base_twoq = _build_folded_isa(code, basis, backend, f["folds"])
            match = (twoq == f["target_twoq"])
            base_ok = (base_twoq == BASE_TWOQ)
            ok = ok and match and base_ok
            rows.append({"basis": basis, "folds": f["folds"], "twoq": twoq,
                         "target": f["target_twoq"], "base_twoq": base_twoq})
            print(f"  basis={basis} folds={f['folds']:>2}  2q={twoq:>4} "
                  f"(target {f['target_twoq']}, base {base_twoq})  "
                  f"{'OK' if match and base_ok else '!! MISMATCH'}", flush=True)
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(os.path.join(RESULTS_DIR, "exp87_scan.json"), "w") as f:
        json.dump({"rows": rows, "base_opt": BASE_OPT, "base_seed": BASE_SEED,
                   "exp86_reference": {"158": 1.064, "178": 0.904, "208": 0.785}}, f, indent=2)
    print(f"\nSaved results/exp87_scan.json  |  overall: {'READY for --submit' if ok else 'ABORT (mismatch)'}")
    return ok


def submit(backend_name="ibm_fez", shots=2000):
    from qiskit_ibm_runtime import SamplerV2
    from run_exp66_qpu_partb import _get_ibm_service
    code = setup_code(L=3)
    service = _get_ibm_service()
    backend = service.backend(backend_name)
    print(f"Backend: {backend.name} | pending_jobs={backend.status().pending_jobs}", flush=True)

    pubs, pub_meta = [], []
    for f in FOLD_SCHEDULE:
        for basis in ["Z", "X"]:
            circ, twoq, base_twoq = _build_folded_isa(code, basis, backend, f["folds"])
            if base_twoq != BASE_TWOQ:
                print(f"  ABORT: base 2q={base_twoq} != {BASE_TWOQ} (calibration/transpiler moved).")
                return None
            pubs.append(circ)
            pub_meta.append({"folds": f["folds"], "basis": basis, "twoq": twoq,
                             "target_twoq": f["target_twoq"]})
            print(f"  queued basis={basis} folds={f['folds']:>2} 2q={twoq}", flush=True)

    sampler = SamplerV2(mode=backend)
    sampler.options.default_shots = shots
    job = sampler.run(pubs)                 # ISA circuits, single window
    jid = job.job_id()
    print(f"\nSubmitted ONE job with {len(pubs)} PUBs -> job_id={jid}", flush=True)
    manifest = {"backend": backend_name, "shots": shots, "job_id": jid, "pub_meta": pub_meta,
                "base_opt": BASE_OPT, "base_seed": BASE_SEED, "base_twoq": BASE_TWOQ,
                "exp86_reference": {"158": 1.064, "178": 0.904, "208": 0.785},
                "submitted_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(os.path.join(RESULTS_DIR, "exp87_jobids.json"), "w") as fh:
        json.dump(manifest, fh, indent=2)
    print("Manifest saved: results/exp87_jobids.json (grade next cycle)")
    return manifest


def grade_run():
    from run_exp66_qpu_partb import _get_ibm_service
    from collections import defaultdict
    with open(os.path.join(RESULTS_DIR, "exp87_jobids.json")) as fh:
        man = json.load(fh)
    code = setup_code(L=3); n = code["n"]
    service = _get_ibm_service()
    job = service.job(man["job_id"])
    print(f"job {man['job_id']} status={job.status()}", flush=True)
    res = job.result()
    by = defaultdict(dict)
    for i, meta in enumerate(man["pub_meta"]):
        counts = res[i].data.c.get_counts() if hasattr(res[i].data, "c") else res[i].join_data().get_counts()
        by[(meta["folds"], meta["target_twoq"])][meta["basis"]] = counts
    ref = man["exp86_reference"]
    print(f"\n{'2q':>5} | {'W(fixed-place)':>14} | {'W(Exp86 vary-place)':>18}")
    out = []
    for (folds, tgt), cb in sorted(by.items(), key=lambda kv: kv[0][1]):
        gz = grade_witness(cb["Z"], code, "Z", n); gx = grade_witness(cb["X"], code, "X", n)
        zz = corr(gz)
        xb0 = corr({k: v for k, v in gx.items() if k[0] == 0})
        xb1 = corr({k: v for k, v in gx.items() if k[0] == 1})
        w = zz + (abs(xb0) + abs(xb1)) / 2
        e86 = ref.get(str(tgt), None)
        out.append({"twoq": tgt, "folds": folds, "witness": w, "exp86_witness": e86})
        print(f"{tgt:>5} | {w:>14.4f} | {str(e86):>18}", flush=True)
    with open(os.path.join(RESULTS_DIR, "exp87_graded.json"), "w") as fh:
        json.dump({"points": out, "reference": man}, fh, indent=2)
    print("Saved results/exp87_graded.json")


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
