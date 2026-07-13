#!/usr/bin/env python3
"""run_exp120_submit.py — Exp120 Darwinism x ICO (Whisper C4644).
Prereg: experiments/exp120-darwinism-ico-preregistration.md (FROZEN).
Usage: --scan (FREE) | --submit."""
import argparse
import json
import os
import sys
from collections import deque

import numpy as np
from qiskit import transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "experiments"))
from run_exp66_qpu_partb import _get_ibm_service  # noqa: E402
from exp120_darwinism_ico_sim import build  # noqa: E402

SHOTS = 30000
SEED = 4644
DEAD = 0.5


def _calib(target):
    for cand in ("cz", "ecr", "cx"):
        if cand in target.operation_names:
            name = cand
            break
    err, ro, adj = {}, {}, {}
    for key, inst in target[name].items():
        e = tuple(sorted(key))
        v = getattr(inst, "error", None)
        if v is None or not np.isfinite(v) or v >= DEAD:
            continue
        err[e] = min(err.get(e, 1.0), float(v))
        adj.setdefault(e[0], set()).add(e[1])
        adj.setdefault(e[1], set()).add(e[0])
    for (q,), inst in target["measure"].items():
        v = getattr(inst, "error", None)
        if v is not None and np.isfinite(v) and v < DEAD:
            ro[q] = float(v)
    return err, ro, adj


def select_star(target):
    """FROZEN RULE (prereg §Site): hub S = degree>=3 qubit minimizing summed
    2q error over its best 3 edges; C = neighbor w/ lowest readout;
    F1/F2 = remaining two by edge error."""
    err, ro, adj = _calib(target)
    cands = []
    for s, nbrs in adj.items():
        if len(nbrs) < 3 or s not in ro:
            continue
        edges = sorted((err[tuple(sorted((s, n)))], n) for n in nbrs
                       if tuple(sorted((s, n))) in err and n in ro)[:3]
        if len(edges) < 3:
            continue
        score = sum(e for e, _ in edges)
        cands.append((score, ro[s], s, [n for _, n in edges]))
    if not cands:
        raise RuntimeError("no star site on live map")
    cands.sort()
    score, s_ro, s, nbrs = cands[0]
    c = min(nbrs, key=lambda n: (ro[n], n))
    f1, f2 = sorted([n for n in nbrs if n != c],
                    key=lambda n: (err[tuple(sorted((s, n)))], n))
    return {"S": s, "C": c, "F1": f1, "F2": f2, "sum_err": score,
            "C_readout": ro[c]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--backend", default="ibm_marrakesh")
    ap.add_argument("--tag", default="exp120")
    args = ap.parse_args()

    svc = _get_ibm_service()
    backend = svc.backend(args.backend)
    print(f"Backend {backend.name}: pending={backend.status().pending_jobs}")
    site = select_star(backend.target)
    print("STAR SITE (frozen rule):", json.dumps(site, default=int))
    layout = [site["C"], site["S"], site["F1"], site["F2"]]
    legal_qubits = set(layout)

    tqcs, metas, ok = [], [], True
    counts_by_class = {}
    for arm in ("ordZX", "ordXZ", "switch", "null"):
        for s_basis in ("z", "x"):
            tqc = transpile(build(arm, s_basis), backend,
                            initial_layout=layout, seed_transpiler=SEED,
                            optimization_level=1)
            tw = [tuple(sorted(tqc.find_bit(q).index for q in i.qubits))
                  for i in tqc.data if i.operation.num_qubits == 2
                  and i.operation.name != "barrier"]
            inside = all(set(e) <= legal_qubits for e in tw)
            cls = "skeleton" if arm in ("switch", "null") else "definite"
            counts_by_class.setdefault(cls, set()).add(len(tw))
            if not inside:
                ok = False
                print(f"  AUDIT MISS {arm}_{s_basis}: 2q outside site")
            print(f"  {arm}_{s_basis}: 2q={len(tw)} depth={tqc.depth()} "
                  f"inside={'Y' if inside else 'N'}")
            tqcs.append(tqc)
            metas.append({"label": f"{arm}_{s_basis}", "arm": arm,
                          "s_basis": s_basis, "shots": SHOTS,
                          "twoq": len(tw), "depth": tqc.depth()})
    for cls, cs in counts_by_class.items():
        if len(cs) != 1:
            ok = False
            print(f"  AUDIT MISS: {cls} pubs have unequal 2q counts {cs}")
    print(f"AUDIT {'PASS' if ok else 'FAIL'} ({len(tqcs)} pubs, "
          f"{sum(m['shots'] for m in metas)} shots) "
          f"counts={ {k: sorted(v) for k, v in counts_by_class.items()} }")
    if not ok:
        return 1
    rng = np.random.default_rng(SEED)
    order = list(rng.permutation(len(tqcs)))
    tqcs = [tqcs[i] for i in order]
    metas = [metas[i] for i in order]
    print("pub order:", [m["label"] for m in metas])
    if not args.submit:
        print("--scan complete (FREE).")
        return 0

    from qiskit_ibm_runtime import SamplerV2
    job = SamplerV2(mode=backend).run([(t, None, m["shots"])
                                       for t, m in zip(tqcs, metas)])
    jid = job.job_id()
    manifest = {
        "experiment": "exp120-darwinism-ico", "cycle": "C4644-whisper",
        "backend": args.backend, "tag": args.tag,
        "prereg": "experiments/exp120-darwinism-ico-preregistration.md",
        "site": site, "layout": layout,
        "gates": {"N1": "A_X(null)-A_Z(null) > 0.2 else NO-TEST",
                  "H1": "minus-rate in [0.10,0.40] else NO-TEST",
                  "W_PLUS": "w(plus)-5SE > max(w_ordZX,w_ordXZ)",
                  "W_MINUS": "w(minus)+5SE < min(w_ordZX,w_ordXZ)",
                  "null_first": "both inside hull at 5SE -> ORDER-ROBUST cert"},
        "twoq_counts": {k: sorted(v) for k, v in counts_by_class.items()},
        "transpile_seed": SEED, "shuffle_seed": SEED,
        "job_id": jid, "metas": metas,
    }
    outp = os.path.join(HERE, "..", "results", f"{args.tag}_jobids.json")
    json.dump(manifest, open(outp, "w"), indent=1, default=int)
    print(f"SUBMITTED job {jid}; manifest -> {outp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
