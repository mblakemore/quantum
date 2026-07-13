#!/usr/bin/env python3
"""run_exp119b_submit.py — Exp119b coherent negative energy (Whisper C4641).
Prereg: experiments/exp119b-coherent-negative-energy-preregistration.md (FROZEN).
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
from run_exp105_causal_game_submit import pick_pair  # noqa: E402
from run_exp119_submit import build_cal, EXPECT_2Q  # noqa: E402
import exp119_qet_sim as m  # noqa: E402

THETA = 0.161
SEED = 4641
SHOTS = {"qet_def": 100000, "ground": 100000, "fixp": 20000, "fixm": 20000,
         "cal0": 25000, "cal1": 25000}


def all_pubs():
    pubs = []
    for arm in ("qet_def", "ground", "fixp", "fixm"):
        for basis in ("zb", "xx"):
            qc = (m.build_def_cry(basis, THETA) if arm == "qet_def"
                  else m.build(arm, basis, THETA))
            pubs.append((f"{arm}_{basis}", arm, qc, SHOTS[arm]))
    for c in ("cal0", "cal1"):
        pubs.append((c, c, build_cal(c), SHOTS[c]))
    return pubs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--backend", default="ibm_marrakesh")
    ap.add_argument("--tag", default="exp119b")
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
        if not good:
            ok = False
            print(f"  AUDIT MISS {lab}: 2q={len(tw)} (want {EXPECT_2Q[arm]})")
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
        "experiment": "exp119b-coherent-negative-energy",
        "cycle": "C4641-whisper", "backend": args.backend, "tag": args.tag,
        "prereg": "experiments/exp119b-coherent-negative-energy-preregistration.md",
        "parent": "exp119 (FAIL-EXISTENCE C4640; this is the scope-honest retest)",
        "theta": THETA, "pair": list(pair),
        "gates": {"G0": "raw ground+5SE<0 -> NO-TEST",
                  "V1": "corrected E_B(def)+5SE_c < 0 (HEADLINE)",
                  "V2": "corrected def-ground < 0 at 5sigma",
                  "V3": "raw def-fixpooled < 0 at 5sigma"},
        "transpile_seed": SEED, "shuffle_seed": SEED,
        "job_id": jid, "metas": metas,
    }
    outp = os.path.join(HERE, "..", "results", f"{args.tag}_jobids.json")
    json.dump(manifest, open(outp, "w"), indent=1, default=float)
    print(f"SUBMITTED job {jid}; manifest -> {outp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
