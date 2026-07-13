#!/usr/bin/env python3
"""run_exp114_submit.py — Exp114 purification, hardware submission (Whisper C4606).
Prereg: experiments/exp114-purification-preregistration.md (FROZEN).
Usage: --scan (FREE) | --submit."""
import argparse
import itertools
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
from exp114_purification_sim import circuit, SETTINGS, PAULIS  # noqa: E402

P_STAR = 0.3
SHOTS_RAW0 = 6000
SHOTS_RAWP = 12000
SHOTS_PUR = 6000
SHOTS_SENT = 2000
SEED = 4606


def w1(p):
    return {"I": 1 - 3 * p / 4, "X": p / 4, "Y": p / 4, "Z": p / 4}


def build_all():
    ent = []
    for skey, th_a, th_b in SETTINGS:
        sk = skey.replace(",", "")
        ent.append((f"raw0_{sk}", "raw0", circuit("raw", th_a, th_b, ("I", "I")),
                    SHOTS_RAW0))
        for a, wa in w1(P_STAR).items():
            n = max(int(round(SHOTS_RAWP * wa)), 1)
            ent.append((f"rawp_{sk}_{a}", "rawp",
                        circuit("raw", th_a, th_b, (a, "I")), n))
        for a, b in itertools.product(PAULIS, PAULIS):
            wab = w1(P_STAR)[a] * w1(P_STAR)[b]
            n = max(int(round(SHOTS_PUR * wab)), 1)
            ent.append((f"pur_{sk}_{a}{b}", "pur",
                        circuit("purified", th_a, th_b, (a, b)), n))
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
    ap.add_argument("--tag", default="exp114")
    args = ap.parse_args()

    svc = _get_ibm_service()
    backend = svc.backend(args.backend)
    print(f"Backend {backend.name}: pending={backend.status().pending_jobs}")
    e110.CHAIN_LEN = 4
    chain, cost = e110.best_chain(backend)
    print(f"chain (4q): {chain} cost={cost:.4f}")

    tqcs, metas, cz_by_kind = [], [], {}
    for lab, kind, qc, shots in build_all():
        lay = chain[:qc.num_qubits] if kind != "sent" else [chain[0]]
        tqc = transpile(qc, backend, initial_layout=lay,
                        seed_transpiler=SEED, optimization_level=1)
        n2 = sum(1 for i in tqc.data if i.operation.num_qubits == 2
                 and i.operation.name != "barrier")
        cz_by_kind.setdefault(kind, set()).add(n2)
        tqcs.append(tqc)
        metas.append({"label": lab, "kind": kind, "shots": shots, "twoq": n2,
                      "depth": tqc.depth()})
    print("CZ sets by kind:", {k: sorted(v) for k, v in cz_by_kind.items()})
    # audit: raw arms 1 CZ; purified UNIFORM (whatever routing chose, same for all)
    ok = (cz_by_kind["raw0"] == {1} and cz_by_kind["rawp"] == {1}
          and len(cz_by_kind["pur"]) == 1 and cz_by_kind["sent"] == {0})
    print(f"AUDIT: {'PASS' if ok else 'FAIL'} ({len(tqcs)} pubs, "
          f"{sum(m['shots'] for m in metas)} shots; purified CZ = "
          f"{sorted(cz_by_kind['pur'])})")
    if not ok:
        return 1
    if not args.submit:
        print("--scan complete (FREE).")
        return 0

    from qiskit_ibm_runtime import SamplerV2
    job = SamplerV2(mode=backend).run(
        [(t, None, m["shots"]) for t, m in zip(tqcs, metas)])
    jid = job.job_id()
    manifest = {
        "experiment": "exp114-purification", "cycle": "C4606-whisper",
        "backend": args.backend, "tag": args.tag,
        "prereg": "experiments/exp114-purification-preregistration.md",
        "gates": {"G1_readout_floor": 0.95, "G2_anchor": 2.4, "DEAD_bound": 2.0,
                  "ALIVE_bound": 2.0, "GAIN_floor": 0.1},
        "p_star": P_STAR,
        "preview": {"raw0": 2.7313, "rawp": 1.899, "pur": 2.2197, "keep": 0.734},
        "transpile": {"seed": SEED, "opt_level": 1},
        "chain": chain, "chain_cost": cost, "job_id": jid, "metas": metas,
    }
    outp = os.path.join(HERE, '..', 'results', f'{args.tag}_jobids.json')
    with open(outp, "w") as f:
        json.dump(manifest, f, indent=1, default=float)
    print(f"SUBMITTED job {jid}; manifest -> {outp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
