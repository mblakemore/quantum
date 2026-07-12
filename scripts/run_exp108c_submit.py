#!/usr/bin/env python3
"""run_exp108c_submit.py — Exp108c drift-tolerant re-fly (Whisper C4592).

Prereg: experiments/exp108c-native-thermal-refly-preregistration.md (FROZEN).
Reuses ALL Exp108b machinery; overrides ONLY the three frozen 108c constants
(calib band, therm band, null shots) and recomputes delays from fresh
calibration at submit. Overrides recorded in the manifest for the grader.

Usage: --scan (FREE) | --submit (spends ~25s QPU)
"""
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

# ---- FROZEN 108c overrides (prereg C4592) ----
m108.CALIB_BAND = (0.12, 0.47)
m108.THERM_BAND = 0.10
m108.SHOTS_NULL = 6000

import run_exp108b_submit as sub  # noqa: E402  (imports AFTER overrides)

SHUFFLE_SEED = 4592      # pub-order shuffle only
TRANSPILE_SEED = 4562    # FROZEN with the 22-CZ skeleton (108b); routing depends on it —
                         # scan with seed 4592 produced a 37-CZ skeleton (audit caught it)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--backend", default="ibm_marrakesh")
    ap.add_argument("--tag", default="exp108c")
    args = ap.parse_args()

    assert m108.self_validate()
    svc = _get_ibm_service()
    backend = svc.backend(args.backend)
    st = backend.status()
    print(f"Backend {backend.name}: operational={st.operational} "
          f"pending={st.pending_jobs}", flush=True)

    ok, rep = sub.live_calibration_check(backend)
    print("Live calibration:", json.dumps(rep, indent=1, default=float))
    if not ok:
        print("NO-GO per prereg: dead qubit / bad edge. ABORT (no spend).")
        return 1

    t1_a = rep[6]["T1_us"] * 1e-6
    t1_b = rep[8]["T1_us"] * 1e-6
    d_a = t1_a * np.log(1 / m108.P_TARGET)
    d_b = t1_b * np.log(1 / m108.P_TARGET)
    print(f"fresh T1: q6={t1_a*1e6:.0f}us q8={t1_b*1e6:.0f}us -> "
          f"delays {d_a*1e6:.0f}/{d_b*1e6:.0f}us")

    # rebuild pubs with 108c shot counts (sub.build_pubs reads module-level
    # SHOTS_NULL imported at sub's import time — rebuild here with overrides)
    ent = []
    for arm, shots in (("switch", m108.SHOTS_SWITCH), ("null_fwd", m108.SHOTS_NULL),
                       ("null_rev", m108.SHOTS_NULL)):
        for t0 in (0, 1):
            ent.append((f"{arm}_t{t0}", arm, t0, shots))
    for arm in ("calib_a", "calib_b"):
        ent.append((arm, arm, 0, m108.SHOTS_CALIB))
    rng = np.random.default_rng(SHUFFLE_SEED)
    ent = [ent[i] for i in rng.permutation(len(ent))]
    entries = [(n, a, m108.build_circuit_native(t0, a, d_a, d_b), s,
                {"label": n, "kind": a, "t0": t0, "shots": s})
               for n, a, t0, s in ent]
    sents = [(f"sent_{r}_retention", "retention",
              m108.build_circuit_native(0, "retention", d_a, d_b), m108.SHOTS_SENT,
              {"label": f"sent_{r}_retention", "kind": "sentinel", "replicate": r,
               "shots": m108.SHOTS_SENT}) for r in ("start", "mid", "end")]
    deco = [("sent_mid_deconull", "deco",
             m108.build_circuit_native(0, "deco", d_a, d_b), m108.SHOTS_SENT,
             {"label": "sent_mid_deconull", "kind": "sentinel", "replicate": "mid",
              "shots": m108.SHOTS_SENT})]
    mid = len(entries) // 2
    pubs = [sents[0]] + entries[:mid] + [sents[1]] + deco + entries[mid:] + [sents[2]]

    tqcs, metas, hist, audit_ok = [], [], {}, True
    for lab, kind, qc, shots, meta in pubs:
        tqc = transpile(qc, backend, initial_layout=sub.LAYOUT,
                        seed_transpiler=TRANSPILE_SEED, optimization_level=3)
        n2 = sum(1 for inst in tqc.data if inst.operation.num_qubits == 2
                 and inst.operation.name != "barrier")
        if kind == "switch":
            hist[n2] = hist.get(n2, 0) + 1
            if n2 != 22:
                audit_ok = False
        tqcs.append(tqc)
        metas.append({**meta, "twoq": n2, "depth": tqc.depth()})
    print(f"switch 2q histogram: {hist} | AUDIT: {'PASS' if audit_ok else 'FAIL'} "
          f"({len(tqcs)} pubs)")
    if not audit_ok:
        print("ABORT per prereg: switch skeleton drifted from 22 CZ.")
        return 1
    if not args.submit:
        print("--scan complete (FREE). Re-run with --submit to spend QPU.")
        return 0

    from qiskit_ibm_runtime import SamplerV2
    job = SamplerV2(mode=backend).run(
        [(t, None, m["shots"]) for t, m in zip(tqcs, metas)])
    jid = job.job_id()
    manifest = {
        "experiment": "exp108c-native-thermal-refly", "cycle": "C4592-whisper",
        "backend": args.backend, "tag": args.tag,
        "prereg": "experiments/exp108c-native-thermal-refly-preregistration.md",
        "gates": {"calib_band": [0.12, 0.47], "retention_min": 0.80,
                  "therm_band": 0.10, "win_floor": 0.06,
                  "cooling": "p1|+ + 5SE < min(p_a, p_b)"},
        "overrides_vs_108b": {"CALIB_BAND": [0.12, 0.47], "THERM_BAND": 0.10,
                              "SHOTS_NULL": 6000},
        "shuffle_seed": SHUFFLE_SEED, "chain": list(sub.CHAIN), "layout": sub.LAYOUT,
        "t1_us": {"a1_q6": t1_a * 1e6, "a2_q8": t1_b * 1e6},
        "delays_us": {"a1": d_a * 1e6, "a2": d_b * 1e6},
        "calibration_report": rep, "job_id": jid, "metas": metas,
    }
    outp = os.path.join(HERE, '..', 'results', f'{args.tag}_jobids.json')
    with open(outp, "w") as f:
        json.dump(manifest, f, indent=1, default=float)
    print(f"SUBMITTED job {jid}; manifest -> {outp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
