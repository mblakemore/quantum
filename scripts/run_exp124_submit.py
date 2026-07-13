#!/usr/bin/env python3
"""run_exp124_submit.py — Exp124 Zeno tractor beam (Whisper C4657).
Prereg: experiments/exp124-zeno-preregistration.md (FROZEN).
Usage: --scan (FREE) | --submit."""
import argparse
import json
import os
import sys

import numpy as np
from qiskit import transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "experiments"))
from run_exp66_qpu_partb import _get_ibm_service  # noqa: E402
from exp124_zeno_sim import build, LADDER  # noqa: E402

SHOTS = 20000
SEED = 4657


def select_qubit(target):
    """FROZEN: argmin readout error, tiebreak index."""
    best = None
    for (q,), inst in target["measure"].items():
        v = getattr(inst, "error", None)
        if v is None or not np.isfinite(v) or v >= 0.5:
            continue
        if best is None or (v, q) < best:
            best = (float(v), q)
    return {"qubit": best[1], "readout_err": best[0]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--backend", default="ibm_marrakesh")
    ap.add_argument("--tag", default="exp124")
    args = ap.parse_args()

    svc = _get_ibm_service()
    backend = svc.backend(args.backend)
    print(f"Backend {backend.name}: pending={backend.status().pending_jobs}")
    site = select_qubit(backend.target)
    print(f"SITE (frozen min-readout rule): {json.dumps(site)}")

    pubs = ([("pinned", n) for n in LADDER] + [("unwatched", 8)]
            + [("nodrive", n) for n in LADDER])
    tqcs, metas, ok = [], [], True
    for arm, n in pubs:
        tqc = transpile(build(arm, n), backend,
                        initial_layout=[site["qubit"]],
                        seed_transpiler=SEED, optimization_level=1)
        n2 = sum(1 for i in tqc.data if i.operation.num_qubits == 2
                 and i.operation.name != "barrier")
        nmeas = sum(1 for i in tqc.data if i.operation.name == "measure")
        want_meas = (1 if arm == "unwatched" else n + 1)
        if n2 != 0 or nmeas != want_meas:
            ok = False
            print(f"  AUDIT MISS {arm}_{n}: 2q={n2} meas={nmeas} "
                  f"(want 0/{want_meas})")
        tqcs.append(tqc)
        metas.append({"label": f"{arm}_{n}", "arm": arm, "n": n,
                      "shots": SHOTS, "meas": nmeas, "depth": tqc.depth()})
    print(f"AUDIT {'PASS' if ok else 'FAIL'} ({len(tqcs)} pubs, "
          f"{sum(m['shots'] for m in metas)} shots)")
    if not ok:
        return 1
    rng = np.random.default_rng(SEED)
    order = list(rng.permutation(len(tqcs)))
    tqcs = [tqcs[i] for i in order]
    metas = [metas[i] for i in order]
    if not args.submit:
        print("--scan complete (FREE).")
        return 0

    from qiskit_ibm_runtime import SamplerV2
    job = SamplerV2(mode=backend).run([(t, None, m["shots"])
                                       for t, m in zip(tqcs, metas)])
    jid = job.job_id()
    manifest = {
        "experiment": "exp124-zeno-tractor-beam", "cycle": "C4657-whisper",
        "backend": args.backend, "tag": args.tag,
        "prereg": "experiments/exp124-zeno-preregistration.md",
        "site": site,
        "gates": {"G0": "nodrive_8 > 0.7", "W_TRACTOR":
                  "pinned_8 - unwatched_8 - 5SE > 0.3",
                  "W_CADENCE": "pinned_8 - pinned_2 - 5SE > 0"},
        "transpile_seed": SEED, "shuffle_seed": SEED,
        "job_id": jid, "metas": metas,
    }
    outp = os.path.join(HERE, "..", "results", f"{args.tag}_jobids.json")
    json.dump(manifest, open(outp, "w"), indent=1, default=float)
    print(f"SUBMITTED job {jid}; manifest -> {outp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
