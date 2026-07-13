#!/usr/bin/env python3
"""run_exp122_submit.py — Exp122 proper-time interferometer (Whisper C4650).
Prereg: experiments/exp122-twin-paradox-preregistration.md (FROZEN).
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
from exp122_twin_paradox_sim import build, build_calib  # noqa: E402

SHOTS_IFM = 20000
SHOTS_CAL = 10000
SEED = 4650
LADDER_FRACS = [0.0, 0.15, 0.3, 0.6, 1.2]
CAL_FRACS = [0.0, 0.3, 0.6, 1.2]
DEAD = 0.5


def select_chain(target):
    """FROZEN RULE: hub h + its two lowest-2q-error neighbor edges;
    C=h, K=better edge, L=other. Dead guard; tiebreak readout then index."""
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
    cands = []
    for h, nbrs in adj.items():
        if len(nbrs) < 2 or h not in ro:
            continue
        edges = sorted((err[tuple(sorted((h, n)))], n) for n in nbrs
                       if n in ro)[:2]
        if len(edges) < 2:
            continue
        cands.append((edges[0][0] + edges[1][0], ro[h], h,
                      edges[0][1], edges[1][1]))
    cands.sort()
    _, _, h, k, l = cands[0]
    return {"C": h, "K": k, "L": l, "sum_err": cands[0][0]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--backend", default="ibm_marrakesh")
    ap.add_argument("--tag", default="exp122")
    args = ap.parse_args()

    svc = _get_ibm_service()
    backend = svc.backend(args.backend)
    print(f"Backend {backend.name}: pending={backend.status().pending_jobs}")
    site = select_chain(backend.target)
    layout = [site["C"], site["K"], site["L"]]
    t1K = backend.target.qubit_properties[site["K"]].t1 * 1e6
    t1L = backend.target.qubit_properties[site["L"]].t1 * 1e6
    tbar = 2.0 / (1.0 / t1K + 1.0 / t1L)
    ladder = [round(f * tbar, 1) for f in LADDER_FRACS]
    cal_lad = [round(f * tbar, 1) for f in CAL_FRACS]
    print(f"SITE (frozen chain rule): {json.dumps(site, default=int)}")
    print(f"published T1: K={t1K:.1f}us L={t1L:.1f}us -> Tbar={tbar:.1f}us")
    print(f"ladder(us): {ladder} | calib: {cal_lad}")

    pubs = []
    for excited in (True, False):
        for dt in ladder:
            pubs.append((f"{'exc' if excited else 'vac'}_{dt}",
                         build(excited, dt), SHOTS_IFM,
                         {"arm": "exc" if excited else "vac", "dt_us": dt}))
    for vq, lane in ((1, "K"), (2, "L")):
        for dt in cal_lad:
            pubs.append((f"cal{lane}_{dt}", build_calib(vq, dt), SHOTS_CAL,
                         {"arm": f"cal{lane}", "dt_us": dt}))

    legal = set(layout)
    tqcs, metas, ok = [], [], True
    ifm_counts = set()
    for lab, qc, shots, meta in pubs:
        tqc = transpile(qc, backend, initial_layout=layout,
                        seed_transpiler=SEED, optimization_level=1,
                        scheduling_method="asap")
        tw = [tuple(sorted(tqc.find_bit(q).index for q in i.qubits))
              for i in tqc.data if i.operation.num_qubits == 2
              and i.operation.name != "barrier"]
        inside = all(set(e) <= legal for e in tw)
        if meta["arm"] in ("exc", "vac"):
            ifm_counts.add(len(tw))
        elif len(tw) != 0:
            ok = False
            print(f"  AUDIT MISS {lab}: calib has 2q gates")
        if not inside:
            ok = False
            print(f"  AUDIT MISS {lab}: 2q outside site")
        tqcs.append(tqc)
        metas.append({"label": lab, **meta, "shots": shots,
                      "twoq": len(tw), "depth": tqc.depth()})
    if len(ifm_counts) != 1:
        ok = False
        print(f"  AUDIT MISS: interferometer 2q counts unequal {ifm_counts}")
    print(f"AUDIT {'PASS' if ok else 'FAIL'} ({len(tqcs)} pubs, "
          f"{sum(m['shots'] for m in metas)} shots) ifm_2q={sorted(ifm_counts)}")
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
        "experiment": "exp122-proper-time-interferometer",
        "cycle": "C4650-whisper", "backend": args.backend, "tag": args.tag,
        "prereg": "experiments/exp122-twin-paradox-preregistration.md",
        "site": site, "layout": layout,
        "published_t1_us": {"K": t1K, "L": t1L, "Tbar": tbar},
        "ladder_us": ladder, "cal_ladder_us": cal_lad,
        "gates": {"G0": "V(0)>0.7 both arms else NO-TEST",
                  "W_AGE": "V_vac(dt*)-V_exc(dt*) > 5SE at ladder[2]",
                  "W_AGE_LADDER": "same at ladder[3]",
                  "law": "REPORTED subclaim only (excess-decay pre-filed)"},
        "transpile_seed": SEED, "shuffle_seed": SEED,
        "job_id": jid, "metas": metas,
    }
    outp = os.path.join(HERE, "..", "results", f"{args.tag}_jobids.json")
    json.dump(manifest, open(outp, "w"), indent=1, default=float)
    print(f"SUBMITTED job {jid}; manifest -> {outp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
