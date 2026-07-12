#!/usr/bin/env python3
"""run_exp112_submit.py — Exp112 swap-chain CHSH, hardware submission (Whisper C4598).
Prereg: experiments/exp112-swap-chain-chsh-preregistration.md (FROZEN).
Usage: --scan (FREE) | --submit."""
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
from exp112_swap_chain_sim import chain_circuit, SETTINGS, KS  # noqa: E402

SHOTS = 3000
SHOTS_SENT = 2000
TRANSPILE_SEED = 4598
CHAIN_LEN = 6


def build_all():
    ent = []
    for k in KS:
        arms = ("shared",) if k == 0 else ("frame", "active")
        for arm in arms:
            for sa, th_a, sb, th_b in SETTINGS:
                qc = chain_circuit(k, th_a, th_b, active=(arm == "active"))
                ent.append((f"{arm}_k{k}_{sa}{sb}", arm, k, qc, SHOTS))
    rng = np.random.default_rng(TRANSPILE_SEED)
    ent = [ent[i] for i in rng.permutation(len(ent))]
    sents = []
    for pos in ("start", "end"):
        for b in (0, 1):
            qc = QuantumCircuit(1, 1)
            if b:
                qc.x(0)
            qc.measure(0, 0)
            sents.append((f"sent_{pos}_{b}", "sent", 0, qc, SHOTS_SENT))
    half = len(ent) // 2
    return sents[0:2] + ent[:half] + ent[half:] + sents[2:4]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--backend", default="ibm_marrakesh")
    ap.add_argument("--tag", default="exp112")
    args = ap.parse_args()

    svc = _get_ibm_service()
    backend = svc.backend(args.backend)
    print(f"Backend {backend.name}: pending={backend.status().pending_jobs}")
    e110.CHAIN_LEN = CHAIN_LEN
    chain, cost = e110.best_chain(backend)
    print(f"chain (6q): {chain} cost={cost:.4f}")

    tqcs, metas, viol = [], [], []
    for lab, arm, k, qc, shots in build_all():
        layout = chain[:qc.num_qubits]
        tqc = transpile(qc, backend, initial_layout=layout,
                        seed_transpiler=TRANSPILE_SEED, optimization_level=1)
        n2 = sum(1 for i in tqc.data if i.operation.num_qubits == 2
                 and i.operation.name != "barrier")
        exp = 0 if arm == "sent" else 2 * k + 1   # k+1 Bell preps CX + k station CX = 2k+1
        if n2 != exp:
            viol.append((lab, n2, exp))
        tqcs.append(tqc)
        metas.append({"label": lab, "arm": arm, "k": k, "shots": shots,
                      "twoq": n2, "depth": tqc.depth()})
    from collections import Counter
    print("CZ by (arm,k):", dict(Counter((m["arm"], m["k"], m["twoq"]) for m in metas)))
    if viol:
        print(f"AUDIT FAIL: {viol[:6]}")
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
        "experiment": "exp112-swap-chain-chsh", "cycle": "C4598-whisper",
        "backend": args.backend, "tag": args.tag,
        "prereg": "experiments/exp112-swap-chain-chsh-preregistration.md",
        "gates": {"G1_readout_floor": 0.95, "G2_k0_floor": 2.0,
                  "WIN_floor": 2.0},
        "signs_frozen_ref": "results/exp112_feasibility.json",
        "preview_S": {"frame": {0: 2.7133, 1: 2.6165, 2: 2.5624},
                      "active": {0: 2.7127, 1: 2.6891, 2: 2.5686}},
        "transpile": {"seed": TRANSPILE_SEED, "opt_level": 1},
        "chain": chain, "chain_cost": cost, "job_id": jid, "metas": metas,
    }
    outp = os.path.join(HERE, '..', 'results', f'{args.tag}_jobids.json')
    with open(outp, "w") as f:
        json.dump(manifest, f, indent=1, default=float)
    print(f"SUBMITTED job {jid}; manifest -> {outp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
