#!/usr/bin/env python3
"""run_exp116b_submit.py — Exp116b delay ladder (Whisper C4611).
Prereg: experiments/exp116b-delay-ladder-preregistration.md (FROZEN).
Usage: --scan (FREE) | --submit."""
import argparse
import json
import os
import sys

import numpy as np
from qiskit import transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'experiments'))
from run_exp66_qpu_partb import _get_ibm_service  # noqa: E402
import exp108b_native_thermal as m108  # noqa: E402
m108.P_TARGET = 0.45
import run_exp108b_submit as sub  # noqa: E402

RUNGS = {"r1": 1.5, "r2": 1.85, "r3": 2.2}
SHOTS_SWITCH = 14000
SHOTS_NULL = 4000
SHOTS_CALIB = 6000
SHOTS_SENT = 2000
SHUFFLE_SEED = 4611
TRANSPILE_SEED = 4562   # frozen with the 22-CZ skeleton


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--backend", default="ibm_marrakesh")
    ap.add_argument("--tag", default="exp116b")
    args = ap.parse_args()

    assert m108.self_validate()
    svc = _get_ibm_service()
    backend = svc.backend(args.backend)
    print(f"Backend {backend.name}: pending={backend.status().pending_jobs}")
    ok, rep = sub.live_calibration_check(backend)
    print("Live calibration:", json.dumps({k: v for k, v in rep.items()
                                           if k in (6, 8)}, default=float))
    if not ok:
        print("NO-GO: dead qubit / bad edge. ABORT.")
        return 1
    t1a_pub = rep[6]["T1_us"] * 1e-6
    t1b_pub = rep[8]["T1_us"] * 1e-6

    ent = []
    delays = {}
    for rung, r in RUNGS.items():
        d_a = r * t1a_pub * np.log(1 / m108.P_TARGET)
        d_b = r * t1b_pub * np.log(1 / m108.P_TARGET)
        delays[rung] = {"r": r, "d_a_us": d_a * 1e6, "d_b_us": d_b * 1e6}
        for arm, shots in (("switch", SHOTS_SWITCH), ("null_fwd", SHOTS_NULL),
                           ("null_rev", SHOTS_NULL)):
            for t0 in (0, 1):
                ent.append((f"{rung}_{arm}_t{t0}", rung, arm, t0,
                            m108.build_circuit_native(t0, arm, d_a, d_b), shots))
        for arm in ("calib_a", "calib_b"):
            ent.append((f"{rung}_{arm}", rung, arm, 0,
                        m108.build_circuit_native(0, arm, d_a, d_b), SHOTS_CALIB))
    print("delays:", json.dumps(delays, indent=None, default=float))
    rng = np.random.default_rng(SHUFFLE_SEED)
    ent = [ent[i] for i in rng.permutation(len(ent))]
    d_mid_a = RUNGS["r2"] * t1a_pub * np.log(1 / m108.P_TARGET)
    d_mid_b = RUNGS["r2"] * t1b_pub * np.log(1 / m108.P_TARGET)
    sents = [(f"sent_{rep_}_retention", "shared", "retention", 0,
              m108.build_circuit_native(0, "retention", d_mid_a, d_mid_b),
              SHOTS_SENT) for rep_ in ("start", "mid", "end")]
    deco = [("sent_mid_deconull", "shared", "deco", 0,
             m108.build_circuit_native(0, "deco", d_mid_a, d_mid_b), SHOTS_SENT)]
    third = len(ent) // 3
    pubs = (sents[0:1] + ent[:third] + sents[1:2] + deco + ent[third:2 * third]
            + ent[2 * third:] + sents[2:3])

    tqcs, metas, hist, audit_ok = [], [], {}, True
    for lab, rung, arm, t0, qc, shots in pubs:
        tqc = transpile(qc, backend, initial_layout=sub.LAYOUT,
                        seed_transpiler=TRANSPILE_SEED, optimization_level=3)
        n2 = sum(1 for i in tqc.data if i.operation.num_qubits == 2
                 and i.operation.name != "barrier")
        if arm == "switch":
            hist[n2] = hist.get(n2, 0) + 1
            if n2 != 22:
                audit_ok = False
        tqcs.append(tqc)
        metas.append({"label": lab, "rung": rung, "kind": arm, "t0": t0,
                      "shots": shots, "twoq": n2, "depth": tqc.depth()})
    print(f"switch 2q histogram: {hist} | AUDIT: "
          f"{'PASS' if audit_ok else 'FAIL'} ({len(tqcs)} pubs, "
          f"{sum(m['shots'] for m in metas)} shots)")
    if not audit_ok:
        return 1
    if not args.submit:
        print("--scan complete (FREE).")
        return 0

    from qiskit_ibm_runtime import SamplerV2
    job = SamplerV2(mode=backend).run(
        [(t, None, m["shots"]) for t, m in zip(tqcs, metas)])
    jid = job.job_id()
    manifest = {
        "experiment": "exp116b-delay-ladder", "cycle": "C4611-whisper",
        "backend": args.backend, "tag": args.tag,
        "prereg": "experiments/exp116b-delay-ladder-preregistration.md",
        "selection_rule": "qualifying: both calib p in (0.35, 0.4677); pick mean closest to 0.45",
        "gates": {"passive": "p+5SE<0.5 each", "retention_min": 0.80,
                  "therm_band": 0.10, "win": "p1m - 5SE > 0.5"},
        "rungs": delays, "t1_pub_us": {"q6": t1a_pub * 1e6, "q8": t1b_pub * 1e6},
        "shuffle_seed": SHUFFLE_SEED, "chain": list(sub.CHAIN),
        "layout": sub.LAYOUT, "job_id": jid, "metas": metas,
    }
    outp = os.path.join(HERE, '..', 'results', f'{args.tag}_jobids.json')
    with open(outp, "w") as f:
        json.dump(manifest, f, indent=1, default=float)
    print(f"SUBMITTED job {jid}; manifest -> {outp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
