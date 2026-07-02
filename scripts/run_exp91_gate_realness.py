#!/usr/bin/env python3
"""
Exp91 (Whisper C4453) — Gate REALNESS at held placement: echo-canceling CZ.CZ=I fold vs
amplitude-moving SWAP.SWAP=I pad, matched 2q-count, SAME placement.

WHY (F69's own flagged caveat, now the target): F67/F68/F69 all reach ~208 gates at HELD placement
by folding CZ.CZ=I (self-inverse) into the ONE routed base circuit. F69 measured the gate-count-only
term (W158 - W_FIX208) = -0.018 ~ 0 and concluded "gate-count is second-order AT HELD PLACEMENT."
BUT F69 explicitly flagged: "FIX reaches 208 via folded CZ.CZ=I identities (GENTLE), not genuine
routed 2q-gates ... the effect of adding 50 REAL routed 2q-gates at held placement is never cleanly
isolated." The mechanism of the gentleness: an immediate self-inverse pair (CZ then CZ) lets coherent
over-rotation errors ECHO-CANCEL, so +50 folded CZ inject far less effective error than +50 generic
2q-gates. This experiment ISOLATES that: pad the SAME base to ~208 with an amplitude-moving,
echo-DEFEATED identity (SWAP.SWAP = I ; each SWAP = ~3 native CZ, populations move, inverse copies
are not the trivially-canceling diagonal pair), at MATCHED count and HELD placement. If the witness
drops relative to the CZ fold at matched count -> F69's "second-order" was partly a fold artifact
(SELF-QUALIFICATION). If it does not -> gate-count is second-order even for real gates (F69
STRENGTHENED beyond the fold caveat).

  Objects (5 circuits x 2 bases = 10 PUBs, single job, one calibration window):
    ANCHOR    158 : opt=2 seed=100 folds=0            (shared base; identical circuit)
    FIX-CZ    178 : base + 10 CZ.CZ=I folds           (diagonal, echo-canceling, +20 2q)
    FIX-CZ    208 : base + 25 CZ.CZ=I folds           (diagonal, echo-canceling, +50 2q)
    FIX-SWAP ~176 : base + 3  SWAP.SWAP=I pads         (real, echo-defeated,  +6/pair 2q)
    FIX-SWAP ~206 : base + 8  SWAP.SWAP=I pads         (real, echo-defeated,  +6/pair 2q)

  Placement is HELD for ALL objects (every pad/fold reuses the base's physical edges; no new qubit,
  no re-transpile, no re-placement). Ideal witness is preserved ALGEBRAICALLY: CZ.CZ=I (self-inverse,
  as F87) and SWAP.SWAP=I where the native SWAP decomposition is Operator-verified == SWAP once, 2q.

  KEY ISOLATE (pre-committed): Delta_type = W(FIX-CZ 208) - W(FIX-SWAP ~206), matched count + held
  placement -> attributes purely to gate REALNESS (echo-canceling vs echo-defeated).

PRE-COMMITTED CLAIM BOUNDARY (see experiments/exp91-gate-realness-preregistration.md):
  BRANCH A  ECHO-ARTIFACT / F69 QUALIFIED : Delta_type > +0.08 (SWAP degrades more at matched count)
            -> F69's held-placement "gate-count second-order" was partly a coherent-echo artifact of
               the CZ.CZ fold; genuine echo-defeated 2q activity DOES lower the witness.
  BRANCH B  TYPE-IMMATERIAL / F69 STRENGTHENED : |Delta_type| <= 0.08 (matched within tie floor)
            -> gate-count is second-order at held placement even for real, echo-defeated gates.
  BRANCH C  REVERSE : Delta_type < -0.08 (SWAP reads HIGHER) -> unexpected; report honestly, treat
            as a confound flag (decomposition/relabeling), do NOT over-interpret as "SWAP is gentler".
  Floor: |Delta| < ~0.08 is within ~2sigma of 0 (difference of two W's, 2000 shots) = "tie".

Provenance reuse (no re-derivation): code/circuit/grade from Exp84; CZ fold_routed + BASE point from
Exp87; noiseless-codeword-verify pattern from Exp86; same-window single-job harness from Exp88/89.

Usage:
  python3 run_exp91_gate_realness.py --scan     # FREE: build all 5 objects, verify identity+counts+placement, no QPU
  python3 run_exp91_gate_realness.py --submit   # QPU: one 10-PUB job on ibm_fez
  python3 run_exp91_gate_realness.py --grade     # grade (same cycle if done, else next)
"""
import sys, os, argparse, json, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_exp84_toric_bell_proxy import setup_code, build_circuit, grade, corr
from run_exp87_fixed_placement_folding import fold_routed, _count_2q, BASE_OPT, BASE_SEED, BASE_TWOQ

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")

# CZ-fold axis (diagonal, echo-canceling) — reuses Exp87/89 exactly.
CZ_SCHEDULE = [
    {"label": "cz178", "folds": 10, "target_twoq": 178},
    {"label": "cz208", "folds": 25, "target_twoq": 208},
]
# SWAP-pad axis (amplitude-moving, echo-defeated). n_pairs chosen at scan time to land near targets.
SWAP_SCHEDULE = [
    {"label": "swap176", "n_pairs": 3, "approx_twoq": 176},
    {"label": "swap206", "n_pairs": 8, "approx_twoq": 206},
]
# Prior within-window references (Exp88/89 same base). Context only; not used in the grade math.
REF = {"exp89_anchor_158": 1.1321, "exp89_fix_208": 1.1501, "exp87_cz_178": 0.904}


def _base_transpile(code, basis, backend):
    from qiskit import transpile
    qc = build_circuit(code, basis)
    return transpile(qc, backend=backend, optimization_level=BASE_OPT, seed_transpiler=BASE_SEED)


def _native_swapswap(backend):
    """Build the SWAP.SWAP=I identity block in the backend's native basis, ONCE, on 2 abstract
    qubits. Returns (swapswap_circuit, cz_per_swap). Verifies (a) native decomp == SWAP and
    (b) block == Identity via 2-qubit Operator equivalence (exact, tractable). Raises on failure."""
    from qiskit import QuantumCircuit, transpile
    from qiskit.quantum_info import Operator
    basis_gates = list(backend.target.operation_names)
    sw = QuantumCircuit(2)
    sw.swap(0, 1)
    native = transpile(sw, basis_gates=basis_gates, optimization_level=1, seed_transpiler=BASE_SEED)
    if not Operator(native).equiv(Operator(sw)):
        raise RuntimeError("native SWAP decomposition != SWAP — abort (do NOT spend QPU).")
    cz_per_swap = _count_2q(native)
    block = QuantumCircuit(2)
    block.compose(native, qubits=[0, 1], inplace=True)   # SWAP
    block.compose(native, qubits=[0, 1], inplace=True)    # SWAP.SWAP
    ident = QuantumCircuit(2)
    if not Operator(block).equiv(Operator(ident)):
        raise RuntimeError("SWAP.SWAP block != Identity — abort (do NOT spend QPU).")
    return block, cz_per_swap


def pad_swapswap(tqc, n_pairs, block):
    """Return a copy of the routed circuit with a SWAP.SWAP=I block (native, == I) inserted on the
    physical edge of each of the first n_pairs native 2q-gates. Net unitary identical (block == I).
    Placement/layout untouched (blocks reuse existing physical edges; no new qubit, no re-transpile).
    +2*cz_per_swap 2q-gates per pad."""
    if n_pairs == 0:
        return tqc.copy()
    new = tqc.copy_empty_like()
    padded = 0
    for inst in tqc.data:
        new.append(inst.operation, inst.qubits, inst.clbits)
        if inst.operation.num_qubits == 2 and padded < n_pairs:
            qi = [new.find_bit(inst.qubits[0]).index, new.find_bit(inst.qubits[1]).index]
            new.compose(block, qubits=qi, inplace=True)
            padded += 1
    if padded != n_pairs:
        raise RuntimeError(f"requested {n_pairs} pads but circuit only had {padded} 2q-gates.")
    return new


def _physical_edges(tqc):
    """Multiset of physical (min,max) qubit pairs used by the ORIGINAL 2q gates — placement fingerprint."""
    edges = []
    for inst in tqc.data:
        if inst.operation.num_qubits == 2:
            a = tqc.find_bit(inst.qubits[0]).index
            b = tqc.find_bit(inst.qubits[1]).index
            edges.append((min(a, b), max(a, b)))
    return sorted(edges)


def _build_all(code, backend):
    """Return (pubs, meta, ok). Anchor + 2 CZ-fold + 2 SWAP-pad, each x {Z,X}. Placement held for all."""
    pubs, meta = [], []
    ok = True
    block, cz_per_swap = _native_swapswap(backend)
    print(f"  native SWAP = {cz_per_swap} CZ  ->  SWAP.SWAP pad = +{2*cz_per_swap} 2q per pair "
          f"(Operator-verified == SWAP and block == I)", flush=True)

    base = {b: _base_transpile(code, b, backend) for b in ("Z", "X")}
    base_edges = {b: _physical_edges(base[b]) for b in ("Z", "X")}
    for b in ("Z", "X"):
        bt = _count_2q(base[b])
        if b == "Z" and bt != BASE_TWOQ:
            print(f"  ABORT: base Z 2q={bt} != {BASE_TWOQ} (calibration/transpiler moved).", flush=True)
            ok = False

    # ANCHOR 158
    for b in ("Z", "X"):
        pubs.append(base[b].copy())
        meta.append({"axis": "anchor", "label": "anchor158", "basis": b, "twoq": _count_2q(base[b])})

    # FIX-CZ (diagonal, echo-canceling) — algebraic self-inverse guarantee (fold_routed raises if unsafe)
    for f in CZ_SCHEDULE:
        for b in ("Z", "X"):
            folded = fold_routed(base[b], f["folds"])
            tq = _count_2q(folded)
            # folds add self-inverse copies on the SAME physical edges -> placement held by construction
            match = (b != "Z") or (tq == f["target_twoq"])
            ok = ok and match
            pubs.append(folded)
            meta.append({"axis": "cz", "label": f["label"], "basis": b, "twoq": tq,
                         "folds": f["folds"], "target": f["target_twoq"]})
            print(f"  FIX-CZ  {f['label']} basis={b} 2q={tq:>4} (target {f['target_twoq']}) "
                  f"{'OK' if match else '!! MISMATCH'}", flush=True)

    # FIX-SWAP (amplitude-moving, echo-defeated) — block == I guarantee; verify held placement explicitly
    for s in SWAP_SCHEDULE:
        for b in ("Z", "X"):
            padded = pad_swapswap(base[b], s["n_pairs"], block)
            tq = _count_2q(padded)
            # HELD PLACEMENT check: the original base edges must all still be present (as a sub-multiset).
            padded_edges = _physical_edges(padded)
            base_ok = all(padded_edges.count(e) >= base_edges[b].count(e) for e in set(base_edges[b]))
            ok = ok and base_ok
            pubs.append(padded)
            meta.append({"axis": "swap", "label": s["label"], "basis": b, "twoq": tq,
                         "n_pairs": s["n_pairs"]})
            print(f"  FIX-SWAP {s['label']} basis={b} 2q={tq:>4} (~{s['approx_twoq']}, {s['n_pairs']} pads) "
                  f"placement-held={'OK' if base_ok else '!! MOVED'}", flush=True)

    return pubs, meta, ok


def scan(backend_name="ibm_fez"):
    from run_exp66_qpu_partb import _get_ibm_service
    code = setup_code(L=3)
    service = _get_ibm_service()
    backend = service.backend(backend_name)
    print(f"Backend: {backend.name} | pending_jobs={backend.status().pending_jobs}", flush=True)
    print(f"Base transpile: opt={BASE_OPT} seed={BASE_SEED} (expect {BASE_TWOQ} Z 2q)\n", flush=True)
    pubs, meta, ok = _build_all(code, backend)
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(os.path.join(RESULTS_DIR, "exp91_scan.json"), "w") as f:
        json.dump({"meta": meta, "n_pubs": len(pubs), "ref": REF}, f, indent=2)
    print(f"\nSaved results/exp91_scan.json | {len(pubs)} PUBs | "
          f"{'READY for --submit' if ok else 'ABORT (mismatch/placement moved)'}")
    return ok


def submit(backend_name="ibm_fez", shots=2000):
    from qiskit_ibm_runtime import SamplerV2
    from run_exp66_qpu_partb import _get_ibm_service
    code = setup_code(L=3)
    service = _get_ibm_service()
    backend = service.backend(backend_name)
    print(f"Backend: {backend.name} | pending_jobs={backend.status().pending_jobs}", flush=True)
    pubs, meta, ok = _build_all(code, backend)
    if not ok:
        print("\nABORT: build/verify failed; not spending QPU.", flush=True)
        return None
    sampler = SamplerV2(mode=backend)
    sampler.options.default_shots = shots
    job = sampler.run(pubs)                  # ONE job -> ONE window for all 10 circuits
    jid = job.job_id()
    print(f"\nSubmitted ONE job with {len(pubs)} PUBs -> job_id={jid}", flush=True)
    manifest = {"backend": backend_name, "shots": shots, "job_id": jid, "pub_meta": meta,
                "base_opt": BASE_OPT, "base_seed": BASE_SEED, "base_twoq": BASE_TWOQ, "ref": REF,
                "submitted_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(os.path.join(RESULTS_DIR, "exp91_jobids.json"), "w") as fh:
        json.dump(manifest, fh, indent=2)
    print("Manifest saved: results/exp91_jobids.json (grade this cycle if done, else next)")
    return manifest


def _witness(cb, code, n):
    gz = grade(cb["Z"], code, "Z", n); gx = grade(cb["X"], code, "X", n)
    zz = corr(gz)
    xb0 = corr({k: v for k, v in gx.items() if k[0] == 0})
    xb1 = corr({k: v for k, v in gx.items() if k[0] == 1})
    return zz + (abs(xb0) + abs(xb1)) / 2


def grade_run():
    from collections import defaultdict
    from run_exp66_qpu_partb import _get_ibm_service
    with open(os.path.join(RESULTS_DIR, "exp91_jobids.json")) as fh:
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
    by = defaultdict(dict)
    twoq = {}
    for i, meta in enumerate(man["pub_meta"]):
        key = meta["label"]
        counts = res[i].data.c.get_counts() if hasattr(res[i].data, "c") else res[i].join_data().get_counts()
        by[key][meta["basis"]] = counts
        if meta["basis"] == "Z":
            twoq[key] = meta["twoq"]

    W = {k: _witness(cb, code, n) for k, cb in by.items()}
    w158 = W["anchor158"]
    w_cz178, w_cz208 = W["cz178"], W["cz208"]
    w_sw176, w_sw206 = W["swap176"], W["swap206"]

    gate_only_cz = w158 - w_cz208                 # F69-style: diagonal echo-canceling fold
    gate_only_sw = w158 - w_sw206                 # echo-defeated real 2q activity
    delta_type = w_cz208 - w_sw206                # KEY ISOLATE: gate realness at matched count+placement
    d2q = twoq["cz208"] - twoq["swap206"]         # count mismatch of the matched pair (should be small)

    TIE = 0.08
    if delta_type > TIE:
        branch = ("BRANCH A ECHO-ARTIFACT / F69 QUALIFIED — SWAP pad degrades more at matched count; "
                  "held-placement 'gate-count second-order' was partly a CZ-fold echo artifact")
    elif delta_type < -TIE:
        branch = ("BRANCH C REVERSE — SWAP reads HIGHER (unexpected); treat as confound flag "
                  "(decomposition/relabeling), do not over-interpret")
    else:
        branch = ("BRANCH B TYPE-IMMATERIAL / F69 STRENGTHENED — matched within tie floor; gate-count "
                  "second-order at held placement even for real echo-defeated gates")

    print(f"\n{'object':>14} | {'W':>8} | {'2q':>4}")
    for lab, w in [("anchor158", w158), ("cz178", w_cz178), ("cz208", w_cz208),
                   ("swap176", w_sw176), ("swap206", w_sw206)]:
        print(f"{lab:>14} | {w:>8.4f} | {twoq[lab]:>4}")
    print(f"\n--- SLOPES (held placement, drift-free single window) ---")
    print(f"  CZ-fold   slope 158->208 (gate_only_cz) = {gate_only_cz:+.4f}  (diagonal, echo-canceling)")
    print(f"  SWAP-pad  slope 158->206 (gate_only_sw) = {gate_only_sw:+.4f}  (real, echo-defeated)")
    print(f"  >>> Delta_type = W(cz208) - W(swap206)  = {delta_type:+.4f}  (matched count, d2q={d2q:+d})")
    print(f"      tie floor = +/-{TIE}")
    print(f"  VERDICT: {branch}")

    out = {"W": W, "gate_only_cz": gate_only_cz, "gate_only_sw": gate_only_sw,
           "delta_type": delta_type, "d2q_matched": d2q, "tie_floor": TIE,
           "verdict": branch, "twoq": twoq, "reference": man}
    with open(os.path.join(RESULTS_DIR, "exp91_graded.json"), "w") as fh:
        json.dump(out, fh, indent=2)
    print("Saved results/exp91_graded.json")
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
