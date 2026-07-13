#!/usr/bin/env python3
"""run_exp135_submit.py — Exp135 CHSH randomness-scope, hardware submission
(Whisper C4676, substrate claude-opus-4-8).
Frozen prereg: experiments/exp135-chsh-randomness-preregistration.md
Usage: python3 scripts/run_exp135_submit.py [--scan] [--submit] [--backend ibm_marrakesh]
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "experiments"))
from exp135_chsh_randomness_sim import SETTINGS, chsh_circuit  # noqa: E402

SHOTS = 20000
SHOTS_SENT = 4000
SEED = 4676


def pick_pair(backend):
    target = backend.target
    twoq = 'cz' if 'cz' in target.operation_names else 'ecr'
    ro = {q: (getattr(i, 'error', 0.0) or 0.0)
          for (q,), i in target['measure'].items()}
    best, bc = None, 1e9
    for (a, b), inst in target[twoq].items():
        e = getattr(inst, 'error', None)
        if e is None:
            continue
        cost = e + ro.get(a, 0) + ro.get(b, 0)
        if cost < bc:
            bc, best = cost, (a, b)
    return best, bc


def sentinel(bits):
    qc = QuantumCircuit(2, 2)
    for i, ch in enumerate(bits):
        if ch == "1":
            qc.x(i)
    qc.measure([0, 1], [0, 1])
    return qc


def build_all():
    ent = []
    for arm, e in (("main", True), ("null", False)):
        for a, b, sign in SETTINGS:
            lab = f"{arm}_{a}{b}"
            ent.append((lab, chsh_circuit(a, b, e),
                        {"label": lab, "kind": arm, "a": a, "b": b,
                         "sign": sign, "shots": SHOTS}))
    rng = np.random.default_rng(SEED)
    ent = [ent[i] for i in rng.permutation(len(ent))]
    sents = [(f"sent_{s}", sentinel(s),
              {"label": f"sent_{s}", "kind": "sentinel", "prep": s,
               "shots": SHOTS_SENT}) for s in ("00", "11")]
    return [sents[0]] + ent + [sents[1]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="ibm_marrakesh")
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--tag", default="exp135")
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
    for lab, qc, meta in build_all():
        tqc = transpile(qc, backend, initial_layout=list(pair),
                        seed_transpiler=SEED, optimization_level=1)
        n2 = sum(1 for inst in tqc.data if inst.operation.num_qubits == 2
                 and inst.operation.name != "barrier")
        exp = 1 if meta["kind"] == "main" else 0
        if meta["kind"] in ("main", "null") and n2 != exp:
            audit_ok = False
            print(f"  AUDIT MISMATCH {lab}: 2q={n2} exp {exp}")
        tqcs.append(tqc)
        metas.append({**meta, "twoq": n2})
    print(f"LIVE AUDIT: {'PASS' if audit_ok else 'FAIL'} ({len(tqcs)} pubs)")
    if not audit_ok:
        print("ABORT.")
        return 1
    if not args.submit:
        print("--scan complete (FREE). Re-run with --submit to spend QPU.")
        return 0

    from qiskit_ibm_runtime import SamplerV2
    job = SamplerV2(mode=backend).run(
        [(t, None, m["shots"]) for t, m in zip(tqcs, metas)])
    jid = job.job_id()
    manifest = {
        "experiment": "exp135-chsh-randomness", "cycle": "C4676-whisper",
        "substrate": "claude-opus-4-8", "backend": args.backend,
        "tag": args.tag, "tsirelson": 2 * math.sqrt(2),
        "prereg": "experiments/exp135-chsh-randomness-preregistration.md",
        "gates": {"W1_WITNESS": "S > 2 + 5se", "W2_TSIRELSON": "S <= 2sqrt2+5se",
                  "W3_NULL": "null S <= 2", "G_SENT": 0.95},
        "prefiled_expectation": {"S": [2.65, 2.78], "null": 0.0},
        "pair": list(pair), "pair_cost": cost, "job_id": jid, "metas": metas,
    }
    outp = os.path.join(HERE, '..', 'results', f'{args.tag}_jobids.json')
    with open(outp, "w") as f:
        json.dump(manifest, f, indent=1)
    print(f"SUBMITTED job {jid}; manifest -> {outp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
