#!/usr/bin/env python3
"""run_exp125_submit.py — Exp125 THE FINAL INVOICE: Landauer floor of the demon's record.
Horizons-3 H4 (Whisper C4663). Prereg: experiments/exp125-landauer-final-invoice-preregistration.md (FROZEN).
Stage 1 measures the effective temperature p_eq (residual excited population) per site, from which the
Landauer erasure floor ln2/ln((1-p_eq)/p_eq) is computed and graded against the banked F95 credit.
Usage: --scan (FREE, gate audit only) | --submit."""
import argparse
import json
import os
import sys

import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "experiments"))
from run_exp66_qpu_partb import _get_ibm_service  # noqa: E402

SHOTS = 20000
SEED = 4663
ENGINE_QUBIT = 4  # F97 engine pair member (same qubits that earned W_credit)


def min_readout_qubit(target):
    """FROZEN: argmin readout error, tiebreak index."""
    best = None
    for (q,), inst in target["measure"].items():
        v = getattr(inst, "error", None)
        if v is None or not np.isfinite(v) or v >= 0.5:
            continue
        if best is None or (v, q) < best:
            best = (float(v), q)
    return {"qubit": best[1], "readout_err": best[0]}


def build(arm):
    """prep0 = |0> + measure ; prep1 = X|0> + measure. Single logical qubit."""
    qc = QuantumCircuit(1, 1)
    if arm == "prep1":
        qc.x(0)
    qc.measure(0, 0)
    return qc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--backend", default="ibm_marrakesh")
    ap.add_argument("--tag", default="exp125")
    args = ap.parse_args()

    svc = _get_ibm_service()
    backend = svc.backend(args.backend)
    print(f"Backend {backend.name}: pending={backend.status().pending_jobs}")

    site_b = min_readout_qubit(backend.target)
    ro_engine = None
    inst = backend.target["measure"].get((ENGINE_QUBIT,))
    if inst is not None:
        ro_engine = float(getattr(inst, "error", float("nan")))
    sites = [
        {"name": "engine", "qubit": ENGINE_QUBIT, "readout_err": ro_engine},
        {"name": "minro", "qubit": site_b["qubit"], "readout_err": site_b["readout_err"]},
    ]
    # de-dup if engine qubit IS the min-readout qubit
    seen, uniq = set(), []
    for s in sites:
        if s["qubit"] not in seen:
            seen.add(s["qubit"])
            uniq.append(s)
    sites = uniq
    print(f"SITES (frozen): {json.dumps(sites)}")

    tqcs, metas, ok = [], [], True
    for site in sites:
        for arm in ("prep0", "prep1"):
            tqc = transpile(build(arm), backend, initial_layout=[site["qubit"]],
                            seed_transpiler=SEED, optimization_level=1)
            n2 = sum(1 for i in tqc.data if i.operation.num_qubits == 2
                     and i.operation.name != "barrier")
            nmeas = sum(1 for i in tqc.data if i.operation.name == "measure")
            if n2 != 0 or nmeas != 1:
                ok = False
                print(f"  AUDIT MISS {site['name']}_{arm}: 2q={n2} meas={nmeas} (want 0/1)")
            tqcs.append(tqc)
            metas.append({"label": f"{site['name']}_{arm}", "site": site["name"],
                          "qubit": site["qubit"], "arm": arm, "shots": SHOTS,
                          "meas": nmeas, "depth": tqc.depth()})
    print(f"AUDIT {'PASS' if ok else 'FAIL'} ({len(tqcs)} pubs, "
          f"{sum(m['shots'] for m in metas)} shots)")
    if not ok:
        return 1

    rng = np.random.default_rng(SEED)
    order = list(rng.permutation(len(tqcs)))
    tqcs = [tqcs[i] for i in order]
    metas = [metas[i] for i in order]
    if not args.submit:
        print("--scan complete (FREE). No QPU spent.")
        return 0

    from qiskit_ibm_runtime import SamplerV2
    job = SamplerV2(mode=backend).run([(t, None, m["shots"]) for t, m in zip(tqcs, metas)])
    jid = job.job_id()
    manifest = {
        "experiment": "exp125-landauer-final-invoice", "cycle": "C4663-whisper",
        "backend": args.backend, "tag": args.tag,
        "prereg": "experiments/exp125-landauer-final-invoice-preregistration.md",
        "sites": sites,
        "banked_credit_E": 0.0920, "banked_credit_SE": 0.0098, "credit_src": "F95 gross drop",
        "floor_formula": "ln2 / ln((1-p_eq)/p_eq)",
        "grade": {"G1": "floor(p_eq) - W_credit - 5*SE_comb > 0  (PASS=demon pays); "
                        "W_credit - floor - 5*SE_comb > 0 (FAIL); else REFUTED-straddle"},
        "bound_graded": "classical (record is heralded/measured; H>=0)",
        "coherent_extension": "Exp125b: conditional bound k_BT*H(rec|sys), H2 S(B|A)<0 loophole (NOT graded here)",
        "transpile_seed": SEED, "shuffle_seed": SEED,
        "job_id": jid, "metas": metas,
    }
    outp = os.path.join(HERE, "..", "results", f"{args.tag}_jobids.json")
    json.dump(manifest, open(outp, "w"), indent=1, default=float)
    print(f"SUBMITTED job {jid}; manifest -> {outp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
