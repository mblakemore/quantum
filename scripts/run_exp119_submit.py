#!/usr/bin/env python3
"""run_exp119_submit.py — Exp119 certified QET (Whisper C4639).
Prereg: experiments/exp119-certified-qet-preregistration.md (FROZEN).
Usage: --scan (FREE) | --submit."""
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
from run_exp105_causal_game_submit import pick_pair  # noqa: E402
import exp119_qet_sim as m  # noqa: E402

THETA = 0.161            # frozen (sim argmin scan)
SHOTS_PROT = 30000
SHOTS_CAL = 20000
SEED = 4639
EXPECT_2Q = {"ground": 1, "qet_ff": 1, "fixp": 1, "fixm": 1, "qet_def": 3,
             "cal0": 0, "cal1": 0}


def build_cal(which):
    qc = QuantumCircuit(2, 3)
    if which == "cal1":
        qc.x([0, 1])
    qc.measure(0, 1)
    qc.measure(1, 2)
    return qc


def all_pubs():
    pubs = []
    for arm in ("ground", "qet_ff", "qet_def", "fixp", "fixm"):
        for basis in ("zb", "xx"):
            qc = (m.build_def_cry(basis, THETA) if arm == "qet_def"
                  else m.build(arm, basis, THETA))
            pubs.append((f"{arm}_{basis}", arm, qc, SHOTS_PROT))
    for c in ("cal0", "cal1"):
        pubs.append((c, c, build_cal(c), SHOTS_CAL))
    return pubs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--backend", default="ibm_marrakesh")
    ap.add_argument("--tag", default="exp119")
    args = ap.parse_args()

    svc = _get_ibm_service()
    backend = svc.backend(args.backend)
    print(f"Backend {backend.name}: pending={backend.status().pending_jobs}")
    pair, cost, twoq = pick_pair(backend)
    print(f"pair={pair} (frozen min-2q-error rule) cost={cost:.5f}")

    legal = {tuple(sorted(pair))}
    tqcs, metas, ok = [], [], True
    for lab, arm, qc, shots in all_pubs():
        tqc = transpile(qc, backend, initial_layout=list(pair),
                        seed_transpiler=SEED, optimization_level=1)
        tw = [tuple(sorted(tqc.find_bit(q).index for q in i.qubits))
              for i in tqc.data if i.operation.num_qubits == 2
              and i.operation.name != "barrier"]
        good = len(tw) == EXPECT_2Q[arm] and set(tw) <= legal
        if arm == "qet_ff":
            has_if = any(getattr(i.operation, "name", "") == "if_else"
                         for i in tqc.data)
            good = good and has_if
        if not good:
            ok = False
            print(f"  AUDIT MISS {lab}: 2q={len(tw)} (want {EXPECT_2Q[arm]}) "
                  f"edges={sorted(set(tw))}")
        tqcs.append(tqc)
        metas.append({"label": lab, "arm": arm, "shots": shots,
                      "twoq": len(tw), "depth": tqc.depth()})
    print(f"AUDIT {'PASS' if ok else 'FAIL'} ({len(tqcs)} pubs, "
          f"{sum(x['shots'] for x in metas)} shots)")
    if not ok:
        return 1
    rng = np.random.default_rng(SEED)
    order = list(rng.permutation(len(tqcs)))
    tqcs = [tqcs[i] for i in order]
    metas = [metas[i] for i in order]
    print("pub order:", [x["label"] for x in metas])
    if not args.submit:
        print("--scan complete (FREE).")
        return 0

    from qiskit_ibm_runtime import SamplerV2
    job = SamplerV2(mode=backend).run([(t, None, x["shots"])
                                       for t, x in zip(tqcs, metas)])
    jid = job.job_id()
    manifest = {
        "experiment": "exp119-certified-qet", "cycle": "C4639-whisper",
        "backend": args.backend, "tag": args.tag,
        "prereg": "experiments/exp119-certified-qet-preregistration.md",
        "theta": THETA, "pair": list(pair),
        "gates": {"G0": "NO-TEST if E_B(ground)+5SE<0",
                  "W1a": "E_B(ff)-E_B(ground) < 0 at 5sigma",
                  "W1b": "E_B(ff)-E_B(scram_pooled) < 0 at 5sigma",
                  "W2": "E_B(ff)+5SE < 0 raw",
                  "W2c": "corrected E_B(ff)+5SE < 0"},
        "transpile_seed": SEED, "shuffle_seed": SEED,
        "job_id": jid, "metas": metas,
    }
    outp = os.path.join(HERE, "..", "results", f"{args.tag}_jobids.json")
    json.dump(manifest, open(outp, "w"), indent=1, default=float)
    print(f"SUBMITTED job {jid}; manifest -> {outp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
