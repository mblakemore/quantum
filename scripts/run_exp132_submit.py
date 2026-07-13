#!/usr/bin/env python3
"""run_exp132_submit.py — Exp132 DFS-cloak 3-way race, hardware submission
(Whisper C4671, Horizons-3 H3, substrate claude-opus-4-8).
Frozen prereg: experiments/exp132-dfs-cloak-preregistration.md
Usage: python3 scripts/run_exp132_submit.py [--scan] [--submit] [--backend ibm_marrakesh]
"""
import argparse
import json
import os
import sys

import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "experiments"))
from exp132_dfs_cloak_sim import (BARE_SETTINGS, DELAYS_US,  # noqa: E402
                                  LOG_SETTINGS, bare_circuit, echo_circuit,
                                  logical_circuit)

SHOTS_LOG = 8000
SHOTS_1Q = 12000
SHOTS_SENT = 4000
SHUFFLE_SEED = 4671


def pick_pair(backend):
    target = backend.target
    twoq = 'cz' if 'cz' in target.operation_names else 'ecr'
    best, best_cost = None, 1e9
    ro = {q: (getattr(i, 'error', 0.0) or 0.0)
          for (q,), i in target['measure'].items()}
    for (a, b), inst in target[twoq].items():
        e = getattr(inst, 'error', None)
        if e is None:
            continue
        cost = e + ro.get(a, 0) + ro.get(b, 0)
        if cost < best_cost:
            best_cost, best = cost, (a, b)
    return best, best_cost


def sentinel(bits):
    qc = QuantumCircuit(2, 2)
    for i, b in enumerate(bits):
        if b == "1":
            qc.x(i)
    qc.measure([0, 1], [0, 1])
    return qc


def build_all():
    ent = []
    for d in DELAYS_US:
        for s in LOG_SETTINGS:
            ent.append((f"log_{s}_{d}", "logical", 2, logical_circuit(s, d),
                        {"label": f"log_{s}_{d}", "kind": "logical",
                         "setting": s, "delay": d, "shots": SHOTS_LOG}))
        for s in BARE_SETTINGS:
            ent.append((f"bare_{s}_{d}", "bare", 1, bare_circuit(s, d),
                        {"label": f"bare_{s}_{d}", "kind": "bare",
                         "setting": s, "delay": d, "shots": SHOTS_1Q}))
            ent.append((f"echo_{s}_{d}", "echo", 1, echo_circuit(s, d),
                        {"label": f"echo_{s}_{d}", "kind": "echo",
                         "setting": s, "delay": d, "shots": SHOTS_1Q}))
    rng = np.random.default_rng(SHUFFLE_SEED)
    ent = [ent[i] for i in rng.permutation(len(ent))]
    sents = [(f"sent_{b}", "sentinel", 2, sentinel(b),
              {"label": f"sent_{b}", "kind": "sentinel", "prep": b,
               "shots": SHOTS_SENT}) for b in ("00", "11")]
    return [sents[0]] + ent + [sents[1]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="ibm_marrakesh")
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--tag", default="exp132")
    args = ap.parse_args()

    from qiskit_ibm_runtime import QiskitRuntimeService
    svc = QiskitRuntimeService()
    backend = svc.backend(args.backend)
    st = backend.status()
    print(f"Backend {backend.name}: operational={st.operational} "
          f"pending={st.pending_jobs}")
    pair, cost = pick_pair(backend)
    print(f"pair={pair} cost={cost:.5f}")

    tqcs, metas, audit_ok = [], [], True
    for lab, kind, nq, qc, meta in build_all():
        lay = list(pair)[:nq]
        tqc = transpile(qc, backend, initial_layout=lay,
                        seed_transpiler=SHUFFLE_SEED, optimization_level=1)
        n2 = sum(1 for inst in tqc.data if inst.operation.num_qubits == 2
                 and inst.operation.name != "barrier")
        exp = 1 if kind == "logical" else 0
        if kind in ("logical", "bare", "echo") and n2 != exp:
            audit_ok = False
            print(f"  AUDIT MISMATCH {lab}: 2q={n2} expected {exp}")
        tqcs.append(tqc)
        metas.append({**meta, "twoq": n2, "depth": tqc.depth()})
    print(f"LIVE AUDIT: {'PASS' if audit_ok else 'FAIL'} ({len(tqcs)} pubs)")
    if not audit_ok:
        print("ABORT per prereg.")
        return 1
    if not args.submit:
        print("--scan complete (FREE). Re-run with --submit to spend QPU.")
        return 0

    from qiskit_ibm_runtime import SamplerV2
    sampler = SamplerV2(mode=backend)
    job = sampler.run([(t, None, m["shots"]) for t, m in zip(tqcs, metas)])
    jid = job.job_id()
    manifest = {
        "experiment": "exp132-dfs-cloak", "cycle": "C4671-whisper",
        "substrate": "claude-opus-4-8", "backend": args.backend,
        "tag": args.tag,
        "prereg": "experiments/exp132-dfs-cloak-preregistration.md",
        "delays_us": DELAYS_US, "d_star": DELAYS_US[-1],
        "gates": {"W1_ACTIVE_BEATS_PASSIVE": "echo_norm-dfs_norm > 5se @d*",
                  "W2_ECHO_PROTECTS": "echo_norm-bare_norm > 0.05+5se @d*",
                  "W3_DFS": "both-outcomes: dfs_norm vs bare_norm @d*",
                  "G_SENT": 0.95},
        "prefiled_expectation": {"W1": "echo>>dfs", "W2": "ECHO_PROTECTS",
                                 "W3": "NO_PASSIVE_PROTECTION",
                                 "fake_dfs_ratio": 0.15,
                                 "fake_echo_ratio": 0.97},
        "shuffle_seed": SHUFFLE_SEED, "pair": list(pair), "pair_cost": cost,
        "job_id": jid, "metas": metas,
    }
    outp = os.path.join(HERE, '..', 'results', f'{args.tag}_jobids.json')
    with open(outp, "w") as f:
        json.dump(manifest, f, indent=1)
    print(f"SUBMITTED job {jid}; manifest -> {outp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
