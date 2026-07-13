#!/usr/bin/env python3
"""run_exp123_submit.py — Exp123 P-CTC time-loop courtroom (Whisper C4655).
Prereg: experiments/exp123-pctc-preregistration.md (FROZEN).
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
from run_exp122_submit import select_chain  # noqa: E402
from exp123_pctc_sim import build, THETAS  # noqa: E402

SHOTS = 15000
SEED = 4655


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--backend", default="ibm_marrakesh")
    ap.add_argument("--tag", default="exp123")
    args = ap.parse_args()

    svc = _get_ibm_service()
    backend = svc.backend(args.backend)
    print(f"Backend {backend.name}: pending={backend.status().pending_jobs}")
    site = select_chain(backend.target)
    # mapping: T = hub (interacts with both A and S)
    layout = [site["K"], site["C"], site["L"]]      # [A, T, S]
    legal = set(layout)
    print(f"SITE: hub T={site['C']}, A={site['K']}, S={site['L']}")

    tqcs, metas, ok = [], [], True
    cls_counts = {}
    for arm in ("loop", "broken"):
        for t in THETAS:
            for sb in ("z", "x"):
                tqc = transpile(build(arm, t, sb), backend,
                                initial_layout=layout, seed_transpiler=SEED,
                                optimization_level=1)
                tw = [tuple(sorted(tqc.find_bit(q).index for q in i.qubits))
                      for i in tqc.data if i.operation.num_qubits == 2
                      and i.operation.name != "barrier"]
                inside = all(set(e) <= legal for e in tw)
                cls_counts.setdefault(arm, set()).add(len(tw))
                if not inside:
                    ok = False
                    print(f"  AUDIT MISS {arm}_{t:.4f}_{sb}: outside site")
                tqcs.append(tqc)
                metas.append({"label": f"{arm}_{t:.4f}_{sb}", "arm": arm,
                              "theta": float(t), "s_basis": sb,
                              "shots": SHOTS, "twoq": len(tw),
                              "depth": tqc.depth()})
    for arm, cs in cls_counts.items():
        if len(cs) != 1:
            ok = False
            print(f"  AUDIT MISS: {arm} 2q counts {cs}")
    print(f"AUDIT {'PASS' if ok else 'FAIL'} ({len(tqcs)} pubs, "
          f"{sum(m['shots'] for m in metas)} shots) "
          f"counts={ {k: sorted(v) for k, v in cls_counts.items()} }")
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
        "experiment": "exp123-pctc-time-loop", "cycle": "C4655-whisper",
        "backend": args.backend, "tag": args.tag,
        "prereg": "experiments/exp123-pctc-preregistration.md",
        "site": site, "layout_ATS": layout,
        "gates": {"G0": "p(0) in [0.40,0.60] both arms",
                  "N1": "X_S(broken,0) < 0.25",
                  "W_PARADOX": "p(pi)/p(0) + 5SE < 0.1 (loop)",
                  "W_LOOP": "X_S(loop,0)-X_S(broken,0) - 5SE > 0.5"},
        "transpile_seed": SEED, "shuffle_seed": SEED,
        "job_id": jid, "metas": metas,
    }
    outp = os.path.join(HERE, "..", "results", f"{args.tag}_jobids.json")
    json.dump(manifest, open(outp, "w"), indent=1, default=float)
    print(f"SUBMITTED job {jid}; manifest -> {outp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
