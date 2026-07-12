#!/usr/bin/env python3
"""run_exp110_submit.py — Exp110 SWAP-vs-teleport, hardware submission (Whisper C4596).

Prereg: experiments/exp110-swap-vs-teleport-preregistration.md (FROZEN).
Usage: --scan (FREE) | --submit. Chain: best 13-qubit connected path by
(CZ + readout) cost on the live target, found at submit and recorded.
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
from exp110_crossover_sim import swap_chain, teleport_chain, PREPS, HOPS  # noqa: E402
from qiskit import QuantumCircuit  # noqa: E402

SHOTS = 3000
SHOTS_SENT = 2000
TRANSPILE_SEED = 4596
SHUFFLE_SEED = 4596
CHAIN_LEN = 13


def best_chain(backend):
    """Greedy DFS: best 13-qubit simple path minimizing sum(cz err) + sum(readout err)."""
    t = backend.target
    edges = {}
    for (a, b), inst in t['cz'].items():
        e = getattr(inst, 'error', None)
        if e is not None:
            edges.setdefault(a, {})[b] = e
            edges.setdefault(b, {})[a] = e
    ro = {q: (t['measure'][(q,)].error or 0.0) for q in range(backend.num_qubits)}
    best_path, best_cost = None, 1e9

    def dfs(path, cost):
        nonlocal best_path, best_cost
        if cost >= best_cost:
            return
        if len(path) == CHAIN_LEN:
            best_path, best_cost = list(path), cost
            return
        for nxt, e in sorted(edges.get(path[-1], {}).items(), key=lambda kv: kv[1])[:4]:
            if nxt not in path:
                dfs(path + [nxt], cost + e + ro.get(nxt, 0))

    starts = sorted(ro, key=ro.get)[:20]
    for s in starts:
        dfs([s], ro.get(s, 0))
    return best_path, best_cost


def sentinel_readout(bit):
    qc = QuantumCircuit(1, 1)
    if bit:
        qc.x(0)
    qc.measure(0, 0)
    return qc


def build_all():
    ent = []
    for arm, builder in (("swap", swap_chain), ("teleport", teleport_chain)):
        for n in HOPS:
            for p in PREPS:
                qc, _ = builder(n, p)
                ent.append((f"{arm}_N{n}_{p}", arm, n, qc, SHOTS))
    rng = np.random.default_rng(SHUFFLE_SEED)
    ent = [ent[i] for i in rng.permutation(len(ent))]
    qc_drift, _ = swap_chain(6, "0")
    sents = [("sent_ro_start_0", "sent", 0, sentinel_readout(0), SHOTS_SENT),
             ("sent_ro_start_1", "sent", 0, sentinel_readout(1), SHOTS_SENT),
             ("sent_mid_swapN6p0", "sent", 6, qc_drift, SHOTS_SENT),
             ("sent_ro_end_0", "sent", 0, sentinel_readout(0), SHOTS_SENT),
             ("sent_ro_end_1", "sent", 0, sentinel_readout(1), SHOTS_SENT)]
    half = len(ent) // 2
    return sents[0:2] + ent[:half] + [sents[2]] + ent[half:] + sents[3:5]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--backend", default="ibm_marrakesh")
    ap.add_argument("--tag", default="exp110")
    args = ap.parse_args()

    svc = _get_ibm_service()
    backend = svc.backend(args.backend)
    st = backend.status()
    print(f"Backend {backend.name}: operational={st.operational} "
          f"pending={st.pending_jobs}")
    chain, cost = best_chain(backend)
    print(f"chain ({CHAIN_LEN}q): {chain} cost={cost:.4f}")

    tqcs, metas, viol = [], [], []
    for lab, kind, n, qc, shots in build_all():
        layout = chain[:qc.num_qubits]
        tqc = transpile(qc, backend, initial_layout=layout,
                        seed_transpiler=TRANSPILE_SEED, optimization_level=1)
        n2 = sum(1 for i in tqc.data if i.operation.num_qubits == 2
                 and i.operation.name != "barrier")
        exp = {"swap": 3 * n, "teleport": 2 * n,
               "sent": 3 * n if "swap" in lab else 0}[kind]
        if n2 != exp:
            viol.append((lab, n2, exp))
        tqcs.append(tqc)
        metas.append({"label": lab, "kind": kind, "hops": n, "shots": shots,
                      "twoq": n2, "depth": tqc.depth()})
    from collections import Counter
    print("CZ by label-class:", dict(Counter((m["kind"], m["twoq"]) for m in metas)))
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
        "experiment": "exp110-swap-vs-teleport", "cycle": "C4596-whisper",
        "backend": args.backend, "tag": args.tag,
        "prereg": "experiments/exp110-swap-vs-teleport-preregistration.md",
        "gates": {"G1_readout_floor": 0.95, "G2_teleport_N1_floor": 0.75,
                  "A_no_crossover_meanD_floor": 0.005, "B_crossover_5se": True},
        "prefiled_law": {1: 0.9482, 2: 0.9346, 4: 0.9081, 6: 0.8823},
        "prefiled_fake_swap": {1: 0.9912, 2: 0.9882, 4: 0.9559, 6: 0.9644},
        "prefiled_fake_tele": {1: 0.9824, 2: 0.9541, 4: 0.9446, 6: 0.9237},
        "transpile": {"seed": TRANSPILE_SEED, "opt_level": 1},
        "shuffle_seed": SHUFFLE_SEED, "chain": chain, "chain_cost": cost,
        "job_id": jid, "metas": metas,
    }
    outp = os.path.join(HERE, '..', 'results', f'{args.tag}_jobids.json')
    with open(outp, "w") as f:
        json.dump(manifest, f, indent=1, default=float)
    print(f"SUBMITTED job {jid}; manifest -> {outp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
