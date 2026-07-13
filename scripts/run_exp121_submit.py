#!/usr/bin/env python3
"""run_exp121_submit.py — Exp121 HP x switch, heralded mirror (Whisper C4647).
Prereg: experiments/exp121-hp-switch-preregistration.md (FROZEN).
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
from run_exp120_submit import select_star  # noqa: E402  (frozen rule REUSED)
from exp121_hp_switch_sim import build  # noqa: E402

SHOTS = 30000
SEED = 4647


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--backend", default="ibm_marrakesh")
    ap.add_argument("--tag", default="exp121")
    args = ap.parse_args()

    svc = _get_ibm_service()
    backend = svc.backend(args.backend)
    print(f"Backend {backend.name}: pending={backend.status().pending_jobs}")
    site = select_star(backend.target)
    print("STAR SITE (frozen rule, reused):", json.dumps(site, default=int))
    layout = [site["C"], site["S"], site["F1"], site["F2"]]  # C,P,E1,E2
    legal = set(layout)

    tqcs, metas, ok = [], [], True
    cls_counts = {}
    for arm in ("ordZX", "ordXZ", "switch", "null"):
        for diary in ("+", "-"):
            tqc = transpile(build(arm, diary), backend,
                            initial_layout=layout, seed_transpiler=SEED,
                            optimization_level=1)
            tw = [tuple(sorted(tqc.find_bit(q).index for q in i.qubits))
                  for i in tqc.data if i.operation.num_qubits == 2
                  and i.operation.name != "barrier"]
            inside = all(set(e) <= legal for e in tw)
            cls = "skeleton" if arm in ("switch", "null") else "definite"
            cls_counts.setdefault(cls, set()).add(len(tw))
            if not inside:
                ok = False
                print(f"  AUDIT MISS {arm}_{diary}: 2q outside site")
            tqcs.append(tqc)
            metas.append({"label": f"{arm}_{diary}", "arm": arm,
                          "diary": diary, "shots": SHOTS, "twoq": len(tw),
                          "depth": tqc.depth()})
    for cls, cs in cls_counts.items():
        if len(cs) != 1:
            ok = False
            print(f"  AUDIT MISS: {cls} unequal 2q counts {cs}")
    print(f"AUDIT {'PASS' if ok else 'FAIL'} ({len(tqcs)} pubs, "
          f"{sum(m['shots'] for m in metas)} shots) "
          f"counts={ {k: sorted(v) for k, v in cls_counts.items()} }")
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
        "experiment": "exp121-hp-switch-heralded-mirror",
        "cycle": "C4647-whisper", "backend": args.backend, "tag": args.tag,
        "prereg": "experiments/exp121-hp-switch-preregistration.md",
        "site": site, "layout": layout,
        "gates": {"PREMISE_DEAD": "|S_P(def)|<0.05 both, else NO-TEST",
                  "N1": "|S_P(null)|<0.05 and S_E2(null)<0.25, else NO-TEST",
                  "H1": "minus-rate in [0.10,0.40], else NO-TEST",
                  "W_MIRROR": "S_P(minus)+5SE < -0.05 (sign fixed)",
                  "W_PLUS": "S_P(plus)-5SE > +0.05 (sign fixed)"},
        "twoq_counts": {k: sorted(v) for k, v in cls_counts.items()},
        "transpile_seed": SEED, "shuffle_seed": SEED,
        "job_id": jid, "metas": metas,
    }
    outp = os.path.join(HERE, "..", "results", f"{args.tag}_jobids.json")
    json.dump(manifest, open(outp, "w"), indent=1, default=int)
    print(f"SUBMITTED job {jid}; manifest -> {outp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
