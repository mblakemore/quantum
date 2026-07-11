#!/usr/bin/env python3
"""Exp108b native-noise ICO thermal splitting — HARDWARE SUBMIT (Whisper C4562).
Pre-reg: experiments/exp108b-native-thermal-preregistration.md (FROZEN 4ef8276 pre --submit).
Apparatus REUSED from Exp108 (chain (5,6,7,8), layout [5,7,6,8]) — controlled working-fluid
substitution. Live T1 pull calibrates the per-ancilla delays; NO-GO abort on dead qubits.

Usage:  --scan (FREE)  |  --submit (spends ~20s QPU)
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'experiments'))
from run_exp66_qpu_partb import _get_ibm_service
from exp108b_native_thermal import (build_circuit_native, self_validate, P_TARGET,
                                    SHOTS_SWITCH, SHOTS_NULL, SHOTS_CALIB, SHOTS_SENT)

SHUFFLE_SEED = 4562
CHAIN = (5, 6, 7, 8)
LAYOUT = [5, 7, 6, 8]        # logical (c,t,a1,a2) -> physical; a1=q6, a2=q8
MAX_2Q = 40
NOGO = {"readout": 0.10, "t1_s": 50e-6, "cz": 0.10}


def live_calibration_check(backend):
    t = backend.target
    report, ok = {}, True
    for q in CHAIN:
        qp = t.qubit_properties[q]
        ro = t['measure'][(q,)].error or 0.0
        report[q] = {"T1_us": qp.t1 * 1e6, "readout": ro}
        if ro > NOGO["readout"] or (qp.t1 or 0) < NOGO["t1_s"]:
            ok = False
    for pair in [(5, 6), (6, 7), (7, 8)]:
        e = None
        for cand in (pair, pair[::-1]):
            if cand in t['cz']:
                e = t['cz'][cand].error
                break
        report[f"cz{pair}"] = e
        if e is None or e >= NOGO["cz"]:
            ok = False
    return ok, report


def build_pubs(d_a, d_b):
    ent = []
    for arm, shots in (("switch", SHOTS_SWITCH), ("null_fwd", SHOTS_NULL),
                       ("null_rev", SHOTS_NULL)):
        for t0 in (0, 1):
            ent.append((f"{arm}_t{t0}", arm, t0, shots))
    for arm in ("calib_a", "calib_b"):
        ent.append((arm, arm, 0, SHOTS_CALIB))
    rng = np.random.default_rng(SHUFFLE_SEED)
    shuffled = [ent[i] for i in rng.permutation(len(ent))]
    entries = [(name, arm, build_circuit_native(t0, arm, d_a, d_b), shots,
                {"label": name, "kind": arm, "t0": t0, "shots": shots})
               for name, arm, t0, shots in shuffled]
    sent = [(f"sent_{rep}_retention", "retention",
             build_circuit_native(0, "retention", d_a, d_b), SHOTS_SENT,
             {"label": f"sent_{rep}_retention", "kind": "sentinel", "replicate": rep,
              "shots": SHOTS_SENT}) for rep in ("start", "mid", "end")]
    deco = [("sent_mid_deconull", "deco", build_circuit_native(0, "deco", d_a, d_b),
             SHOTS_SENT, {"label": "sent_mid_deconull", "kind": "sentinel",
                          "replicate": "mid", "shots": SHOTS_SENT})]
    mid = len(entries) // 2
    return [sent[0]] + entries[:mid] + [sent[1]] + deco + entries[mid:] + [sent[2]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--backend", default="ibm_marrakesh")
    ap.add_argument("--tag", default="exp108b")
    args = ap.parse_args()

    assert self_validate()
    svc = _get_ibm_service()
    backend = svc.backend(args.backend)
    st = backend.status()
    print(f"Backend {backend.name}: operational={st.operational} pending={st.pending_jobs}",
          flush=True)
    try:
        u = svc.usage()
        print(f"QPU budget: {u.get('usage_remaining_seconds')}s remaining", flush=True)
    except Exception as e:
        print("usage probe:", e)

    ok, rep = live_calibration_check(backend)
    print("Live calibration:", json.dumps(rep, indent=1, default=float))
    if not ok:
        print("NO-GO per pre-reg: dead qubit / bad edge on the reused chain. ABORT (no spend).")
        return 1

    t = backend.target
    t1_a = t.qubit_properties[6].t1
    t1_b = t.qubit_properties[8].t1
    d_a = t1_a * np.log(1 / P_TARGET)
    d_b = t1_b * np.log(1 / P_TARGET)
    print(f"Delays: a1(q6) T1={t1_a*1e6:.0f}us -> {d_a*1e6:.0f}us | "
          f"a2(q8) T1={t1_b*1e6:.0f}us -> {d_b*1e6:.0f}us", flush=True)

    pubs_meta = build_pubs(d_a, d_b)
    total_shots = sum(p[3] for p in pubs_meta)
    print(f"PUBs: {len(pubs_meta)}, total shots {total_shots}, shuffle seed {SHUFFLE_SEED}",
          flush=True)

    from qiskit import transpile
    tqcs, metas, hist = [], [], {}
    audit_ok = True
    for lab, kind, qc, shots, meta in pubs_meta:
        tqc = transpile(qc, backend, initial_layout=LAYOUT,
                        seed_transpiler=SHUFFLE_SEED, optimization_level=3)
        n2 = sum(1 for inst in tqc.data if inst.operation.num_qubits == 2
                 and inst.operation.name != "barrier")
        meta = {**meta, "twoq": n2, "depth": tqc.depth()}
        if kind in ("switch", "retention", "deco"):
            hist[n2] = hist.get(n2, 0) + 1
            if n2 > MAX_2Q:
                audit_ok = False
        tqcs.append(tqc)
        metas.append(meta)
    print(f"  switch-skeleton 2q histogram on LIVE target: {hist}")
    print(f"  LIVE AUDIT: {'PASS' if audit_ok else 'FAIL'} (bound <= {MAX_2Q})", flush=True)
    if not audit_ok:
        print("ABORT per pre-reg: payload exceeded the audited 2q class.")
        return 1
    if args.scan or not args.submit:
        print("\n--scan complete (FREE). Re-run with --submit to spend QPU.")
        return 0

    from qiskit_ibm_runtime import SamplerV2
    sampler = SamplerV2(mode=backend)
    job = sampler.run([(t_, None, m["shots"]) for t_, m in zip(tqcs, metas)])
    jid = job.job_id()
    manifest = {
        "experiment": "exp108b-native-thermal", "cycle": "C4562-whisper",
        "backend": args.backend, "tag": args.tag,
        "prereg": "experiments/exp108b-native-thermal-preregistration.md",
        "gates": {"calib_band": [0.12, 0.40], "retention_min": 0.80,
                  "therm_band": 0.06, "win_floor": 0.06,
                  "cooling": "p1|+ + 5SE < min(p_a, p_b)"},
        "shuffle_seed": SHUFFLE_SEED, "chain": list(CHAIN), "layout": LAYOUT,
        "t1_us": {"a1_q6": t1_a * 1e6, "a2_q8": t1_b * 1e6},
        "delays_us": {"a1": d_a * 1e6, "a2": d_b * 1e6},
        "calibration_report": rep, "job_id": jid, "metas": metas,
    }
    outp = os.path.join(HERE, '..', 'results', f'{args.tag}_jobids.json')
    with open(outp, 'w') as f:
        json.dump(manifest, f, indent=1, default=float)
    print(f"\nSubmitted ONE job, {len(tqcs)} PUBs -> job_id={jid}")
    print(f"Manifest -> {os.path.abspath(outp)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
