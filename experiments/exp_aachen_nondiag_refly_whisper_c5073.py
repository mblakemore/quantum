#!/usr/bin/env python3
"""AACHEN NON-DIAGONAL AXIS RE-FLY, layout-gated (Whisper C5073, Creator GO in-terminal).

The first aachen attempt returned NO-TEST at the instrument's own gate: auto-routing landed
the switch on weak 2q real estate (floor +0.003, polarity healthy -0.961). This re-fly is the
named remedy: CALIBRATION-GATED placement - every linear 4-qubit path in the coupling map is
scored (sum of path-edge 2q errors + readout errors), the best path taken, control at an
interior node. Same circuits (imported - one code path), same frozen P-G3 rule with
gate-count-normalized floor, same gates (floor >= 0.3, polarity <= -0.5). If the floor STILL
collapses on the best-scored path, that is itself a die statement (aachen cannot host the
45-CZ switch at this cal quality) and is reported as such - NO-TEST-WITH-MECHANISM, not
silence. Account IBMQ_TOKEN.
"""
import argparse, json, os, sys, math
import numpy as np
from qiskit import transpile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
from exp_gear3_switch_gearbox_whisper_c5073 import switch_circuit

BACKEND = os.environ.get("NONDIAG_BACKEND", "ibm_aachen")
ACCOUNT = os.environ.get("NONDIAG_ACCOUNT", "IBMQ_TOKEN")
SHOTS = 8000
OUT = os.path.join(HERE, "..", "results",
                   f"exp_nondiag_bestpath_{BACKEND.replace('ibm_','')}_c5073_manifest.json"
                   if os.environ.get("NONDIAG_BACKEND") else
                   "exp_aachen_nondiag_refly_c5073_manifest.json")


def best_path(backend, length=4):
    """Score all linear paths of `length` qubits: sum 2q err on path edges + readout err."""
    target = backend.target
    twoq = "cz" if "cz" in target.operation_names else "ecr"
    err2 = {}
    for (a, b) in target[twoq]:
        e = target[twoq][(a, b)].error
        err2[(a, b)] = err2[(b, a)] = (e if e is not None else 0.05)
    ro = {}
    for (q,) in target["measure"]:
        e = target["measure"][(q,)].error
        ro[q] = e if e is not None else 0.05
    adj = {}
    for (a, b) in err2:
        adj.setdefault(a, set()).add(b)
    best, best_score = None, 1e9
    def extend(path):
        nonlocal best, best_score
        if len(path) == length:
            s = sum(err2[(path[i], path[i+1])] for i in range(length-1)) + sum(ro[q] for q in path)
            if s < best_score:
                best, best_score = list(path), s
            return
        for nxt in adj.get(path[-1], ()):
            if nxt not in path:
                path.append(nxt); extend(path); path.pop()
    for q in adj:
        extend([q])
    return best, best_score


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--submit", action="store_true")
    a = ap.parse_args()
    from qiskit_ibm_runtime import SamplerV2
    from ibm_multi_account import service_for_submission
    svc = service_for_submission(ACCOUNT)
    backend = svc.backend(BACKEND)
    props = backend.properties()
    print(f"aachen cal epoch: {props.last_update_date}")
    path, score = best_path(backend)
    print(f"[$0-validate] best calibration-scored path: {path} (score {score:.4f})")
    # control (logical 0) at interior node path[1]; targets around it
    layout = [path[1], path[0], path[2], path[3]]

    pubs, meta = [], []
    for arm in ("floor", "science", "polarity"):
        qc = switch_circuit(arm)
        tqc = transpile(qc, backend, optimization_level=1, seed_transpiler=3,
                        initial_layout=layout)
        pubs.append((tqc, None, SHOTS))
        meta.append({"block": arm, "shots": SHOTS, "depth": tqc.depth(),
                     "cz_count": sum(1 for i in tqc.data if i.operation.num_qubits == 2)})
        print(f"  [$0-validate] {arm}: depth {tqc.depth()}, 2q {meta[-1]['cz_count']}")

    man = {"card": "exp_aachen_nondiag_refly", "cycle": "C5073", "substrate": "claude-fable-5",
           "backend": BACKEND, "cal_epoch": str(props.last_update_date), "shots": SHOTS,
           "account": ACCOUNT, "layout": layout, "path_score": score,
           "purpose": "Third currency axis on aachen, layout-gated (remedy for the auto-routing NO-TEST)",
           "prereg": "P-G3 + gates verbatim from ec8dace; floor-collapse-on-best-path = NO-TEST-WITH-MECHANISM (die statement), stated pre-flight",
           "pubs_meta": meta}
    if a.submit:
        man["pending_jobs_at_submit"] = backend.status().pending_jobs
        job = SamplerV2(mode=backend).run(pubs)
        man["job_id"] = job.job_id()
        print(f"SUBMITTED {man['job_id']} to {BACKEND} (pending at submit: {man['pending_jobs_at_submit']})")
    else:
        print("[dry] not submitted")
    json.dump(man, open(OUT, "w"), indent=1)
    print(f"manifest -> {OUT}")


if __name__ == "__main__":
    main()
