#!/usr/bin/env python3
"""run_exp122b_submit.py — Exp122b phase-blind twin retest (Whisper C4653).
Prereg: experiments/exp122b-phase-blind-preregistration.md (FROZEN).
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
from run_exp122_submit import select_chain, LADDER_FRACS, CAL_FRACS  # noqa: E402
from exp122b_phase_blind_sim import build_b  # noqa: E402
from exp122_twin_paradox_sim import build_calib  # noqa: E402

SHOTS_IFM = 20000
SHOTS_CAL = 10000
SEED = 4653


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--backend", default="ibm_marrakesh")
    ap.add_argument("--tag", default="exp122b")
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
    dt3, dt4 = ladder[2], ladder[3]
    print(f"SITE: {json.dumps(site, default=int)} | published T1 K={t1K:.1f} "
          f"L={t1L:.1f} Tbar={tbar:.1f} | ladder {ladder}")

    pubs = []
    for arm, excited, echo, dts in (("exc", True, False, ladder),
                                    ("vac", False, False, ladder),
                                    ("exc_echo", True, True,
                                     [ladder[0], dt3, dt4])):
        for dt in dts:
            for ro in ("x", "y"):
                pubs.append((f"{arm}_{dt}_{ro}",
                             build_b(excited, dt, ro, echo), SHOTS_IFM,
                             {"arm": arm, "dt_us": dt, "readout": ro}))
    for vq, lane in ((1, "K"), (2, "L")):
        for dt in cal_lad:
            pubs.append((f"cal{lane}_{dt}", build_calib(vq, dt), SHOTS_CAL,
                         {"arm": f"cal{lane}", "dt_us": dt}))

    legal = set(layout)
    tqcs, metas, ok = [], [], True
    cls_counts = {}
    for lab, qc, shots, meta in pubs:
        tqc = transpile(qc, backend, initial_layout=layout,
                        seed_transpiler=SEED, optimization_level=1,
                        scheduling_method="asap")
        tw = [tuple(sorted(tqc.find_bit(q).index for q in i.qubits))
              for i in tqc.data if i.operation.num_qubits == 2
              and i.operation.name != "barrier"]
        inside = all(set(e) <= legal for e in tw)
        cls = ("echo" if meta["arm"] == "exc_echo" else
               "ifm" if meta["arm"] in ("exc", "vac") else "cal")
        cls_counts.setdefault(cls, set()).add(len(tw))
        if not inside or (cls == "cal" and len(tw) != 0):
            ok = False
            print(f"  AUDIT MISS {lab}")
        tqcs.append(tqc)
        metas.append({"label": lab, **meta, "shots": shots,
                      "twoq": len(tw), "depth": tqc.depth()})
    for cls in ("ifm", "echo"):
        if len(cls_counts.get(cls, set())) != 1:
            ok = False
            print(f"  AUDIT MISS: {cls} 2q counts {cls_counts.get(cls)}")
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
        "experiment": "exp122b-phase-blind-twin", "cycle": "C4653-whisper",
        "backend": args.backend, "tag": args.tag,
        "prereg": "experiments/exp122b-phase-blind-preregistration.md",
        "parent": "exp122 (win-as-frozen, mechanism confounded C4651)",
        "site": site, "layout": layout,
        "published_t1_us": {"K": t1K, "L": t1L, "Tbar": tbar},
        "ladder_us": ladder, "cal_ladder_us": cal_lad,
        "gates": {"G0": "V(0)>0.7 both", "W_TWIN": "V_vac-V_exc 5sig at dt3 OR dt4",
                  "W_ROT": "echoX-rawX 5sig at dt3",
                  "classes": "MIXED | AGING-CLEAN | CLOCK-PULL | UNRESOLVED"},
        "transpile_seed": SEED, "shuffle_seed": SEED,
        "job_id": jid, "metas": metas,
    }
    outp = os.path.join(HERE, "..", "results", f"{args.tag}_jobids.json")
    json.dump(manifest, open(outp, "w"), indent=1, default=float)
    print(f"SUBMITTED job {jid}; manifest -> {outp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
