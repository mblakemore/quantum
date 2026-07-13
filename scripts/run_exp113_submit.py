#!/usr/bin/env python3
"""run_exp113_submit.py — Exp113 teleported witness, hardware submission
(Whisper C4603). Prereg: experiments/exp113-teleported-witness-preregistration.md
(FROZEN). Usage: --scan (FREE) | --submit."""
import argparse
import json
import os
import sys

import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'experiments'))
from run_exp66_qpu_partb import _get_ibm_service  # noqa: E402
import run_exp110_submit as e110  # noqa: E402
from exp113_teleported_witness_sim import build, PAIRS  # noqa: E402

SHOTS = 4000
SHOTS_SENT = 2000
SEED = 4603


def build_all():
    ent = []
    for arm in ("direct", "tele_frame", "tele_active", "tele_deco"):
        for pair in PAIRS:
            ent.append((f"{arm}_{pair}", arm, build(pair, arm), SHOTS))
    rng = np.random.default_rng(SEED)
    ent = [ent[i] for i in rng.permutation(len(ent))]
    sents = []
    for pos in ("start", "end"):
        for b in (0, 1):
            qc = QuantumCircuit(1, 1)
            if b:
                qc.x(0)
            qc.measure(0, 0)
            sents.append((f"sent_{pos}_{b}", "sent", qc, SHOTS_SENT))
    half = len(ent) // 2
    return sents[0:2] + ent[:half] + ent[half:] + sents[2:4]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--backend", default="ibm_marrakesh")
    ap.add_argument("--tag", default="exp113")
    args = ap.parse_args()

    svc = _get_ibm_service()
    backend = svc.backend(args.backend)
    print(f"Backend {backend.name}: pending={backend.status().pending_jobs}")
    e110.CHAIN_LEN = 4
    chain, cost = e110.best_chain(backend)
    print(f"chain (4q): {chain} cost={cost:.4f}")
    # circuit (0=C,1=T,2=ba,3=bb) -> physical (p1,p0,p2,p3): all interactions adjacent
    layout4 = [chain[1], chain[0], chain[2], chain[3]]

    tqcs, metas, viol = [], [], []
    for lab, arm, qc, shots in build_all():
        lay = layout4[:qc.num_qubits] if arm != "sent" else [chain[0]]
        tqc = transpile(qc, backend, initial_layout=lay,
                        seed_transpiler=SEED, optimization_level=1)
        n2 = sum(1 for i in tqc.data if i.operation.num_qubits == 2
                 and i.operation.name != "barrier")
        exp = {"sent": 0, "direct": 4, "tele_frame": 6, "tele_active": 6,
               "tele_deco": 6}[arm]   # witness 4 CZ + teleport 2 CX
        if n2 != exp:
            viol.append((lab, n2, exp))
        tqcs.append(tqc)
        metas.append({"label": lab, "arm": arm, "shots": shots, "twoq": n2,
                      "depth": tqc.depth()})
    from collections import Counter
    print("CZ by arm:", dict(Counter((m["arm"], m["twoq"]) for m in metas)))
    if viol:
        print(f"AUDIT FAIL: {viol}")
        return 1
    print(f"AUDIT PASS ({len(tqcs)} pubs, {sum(m['shots'] for m in metas)} shots)")
    if not args.submit:
        print("--scan complete (FREE).")
        return 0

    from qiskit_ibm_runtime import SamplerV2
    job = SamplerV2(mode=backend).run(
        [(t, None, m["shots"]) for t, m in zip(tqcs, metas)])
    jid = job.job_id()
    manifest = {
        "experiment": "exp113-teleported-witness", "cycle": "C4603-whisper",
        "backend": args.backend, "tag": args.tag,
        "prereg": "experiments/exp113-teleported-witness-preregistration.md",
        "gates": {"G1_readout_floor": 0.95, "G2_direct_anchor": 1.60,
                  "W1_survival_floor": 1.0, "W2_separation_floor": 1.0,
                  "G3_deco_band": 0.15},
        "preview": {"direct": 1.9295, "tele_frame": 1.9375,
                    "tele_active": 1.9410, "tele_deco": -0.0130},
        "transpile": {"seed": SEED, "opt_level": 1},
        "chain": chain, "layout4": layout4, "chain_cost": cost,
        "job_id": jid, "metas": metas,
    }
    outp = os.path.join(HERE, '..', 'results', f'{args.tag}_jobids.json')
    with open(outp, "w") as f:
        json.dump(manifest, f, indent=1, default=float)
    print(f"SUBMITTED job {jid}; manifest -> {outp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
