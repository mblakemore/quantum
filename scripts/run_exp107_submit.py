#!/usr/bin/env python3
"""Exp107 cyclic-3 capacity activation — HARDWARE SUBMIT (Whisper C4532).
Pre-reg: experiments/exp107-cyclic3-capacity-preregistration.md (FROZEN pre --submit).
First LOAD-BEARING deployment of sentinel-gated window harvesting: payload is 92-110 CZ
(F81 lottery zone), so a DEEP-retention sentinel ((X,Y,Z) triple, ideal |000> w.p. 1)
gates the window at START/MID/END alongside the F77 shallow triplet.

Usage: --scan (FREE) | --submit ; --backend ibm_marrakesh ; --tag exp107
"""
import argparse
import itertools
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'experiments'))
from run_exp66_qpu_partb import _get_ibm_service
from run_exp105_causal_game_submit import pick_pair
from exp105_causal_game_feasibility import build_game_circuit
from three_switch_transpile_audit import cyclic3_circuit

SHOTS_SWITCH, SHOTS_NULL, SHOTS_SENT = 800, 500, 1500
SHUFFLE_SEED = 4532


def build_entries():
    ent = []
    for ops in itertools.product("1XYZ", repeat=3):
        nm = "".join(ops)
        for bit in (0, 1):
            ent.append((f"sw({nm})b{bit}", "switch",
                        cyclic3_circuit(ops, bit), SHOTS_SWITCH,
                        {"label": f"sw({nm})b{bit}", "kind": "switch",
                         "ops": nm, "input_bit": bit, "shots": SHOTS_SWITCH}))
            ent.append((f"nu({nm})b{bit}", "null",
                        cyclic3_circuit(ops, bit, definite=True), SHOTS_NULL,
                        {"label": f"nu({nm})b{bit}", "kind": "null",
                         "ops": nm, "input_bit": bit, "shots": SHOTS_NULL}))
    rng = np.random.default_rng(SHUFFLE_SEED)
    ent = [ent[i] for i in rng.permutation(len(ent))]
    sent = []
    for rep in ("start", "mid", "end"):
        # shallow F77 pair (apparatus integrity)
        for pname, pr, comm in (("(X,X)", ("X", "X"), True), ("(X,Z)", ("X", "Z"), False)):
            sent.append((f"sent_{rep}_{'commute' if comm else 'anticommute'}", "sentinel",
                         build_game_circuit(pr[0], pr[1]), SHOTS_SENT,
                         {"label": f"sent_{rep}_{'commute' if comm else 'anticommute'}",
                          "kind": "sentinel", "pair": pname, "commuting": comm,
                          "replicate": rep, "shots": SHOTS_SENT}))
        # DEEP retention sentinel: (X,Y,Z) cyclic triple, ideal |000> w.p. 1
        sent.append((f"deep_{rep}", "deep_sentinel",
                     cyclic3_circuit(("X", "Y", "Z"), 0), SHOTS_SENT,
                     {"label": f"deep_{rep}", "kind": "deep_sentinel",
                      "replicate": rep, "shots": SHOTS_SENT}))
    mid = len(ent) // 2
    return sent[0:3] + ent[:mid] + sent[3:6] + ent[mid:] + sent[6:9]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--backend", default="ibm_marrakesh")
    ap.add_argument("--tag", default="exp107")
    args = ap.parse_args()

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

    pair, cost, twoq_name = pick_pair(backend)
    # payload needs 3 qubits: extend the calibration-gated pair with its best neighbour
    target = backend.target
    cmap = {tuple(sorted(e)) for e in target.build_coupling_map().get_edges()}
    best3, bcost = None, 1e9
    for (a, b) in [pair]:
        for (x, y) in cmap:
            for cand in ((x, y), (y, x)):
                if cand[0] in (a, b) and cand[1] not in (a, b):
                    try:
                        e2 = target[twoq_name][tuple(sorted((cand[0], cand[1])))].error \
                            if tuple(sorted((cand[0], cand[1]))) in target[twoq_name] \
                            else target[twoq_name][(cand[0], cand[1])].error
                    except Exception:
                        continue
                    if e2 is not None and e2 < bcost:
                        bcost, best3 = e2, (a, b, cand[1])
    triple = list(best3) if best3 else [pair[0], pair[1], pair[1] + 1]
    print(f"Calibration-gated pair {pair} (cost {cost:.5f}) -> layout triple {triple} "
          f"(3rd-edge err {bcost:.5f})", flush=True)

    entries = build_entries()
    total_shots = sum(e[3] for e in entries)
    print(f"PUBs: {len(entries)} (switch 128 / null 128 / shallow-sent 6 / deep-sent 3), "
          f"total shots {total_shots}, shuffle seed {SHUFFLE_SEED}", flush=True)

    from qiskit import transpile
    print("Transpiling + LIVE audit...", flush=True)
    tqcs, metas = [], []
    hist = {}
    for lab, kind, qc, shots, meta in entries:
        lay = triple if qc.num_qubits == 3 else [triple[0], triple[1]]
        tqc = transpile(qc, backend, initial_layout=lay,
                        seed_transpiler=SHUFFLE_SEED, optimization_level=1)
        n2 = sum(1 for inst in tqc.data if inst.operation.num_qubits == 2
                 and inst.operation.name != "barrier")
        metas.append({**meta, "twoq": n2, "depth": tqc.depth()})
        tqcs.append(tqc)
        if kind == "switch":
            hist[n2] = hist.get(n2, 0) + 1
    print(f"  switch 2q histogram on LIVE target: {dict(sorted(hist.items()))}")
    mx = max(hist)
    audit_ok = mx <= 130
    print(f"  LIVE AUDIT (max 2q {mx} <= 130): {'PASS' if audit_ok else 'FAIL'}", flush=True)
    if not audit_ok:
        print("ABORT per pre-reg: payload deeper than audited class.")
        return 1
    if args.scan or not args.submit:
        print("\n--scan complete (FREE).")
        return 0

    from qiskit_ibm_runtime import SamplerV2
    sampler = SamplerV2(mode=backend)
    job = sampler.run([(t, None, m["shots"]) for t, m in zip(tqcs, metas)])
    jid = job.job_id()
    manifest = {"experiment": "exp107-cyclic3-capacity", "cycle": "C4532-whisper",
                "backend": args.backend, "tag": args.tag,
                "prereg": "experiments/exp107-cyclic3-capacity-preregistration.md",
                "gates": {"sentinel_min_disc": 1.60, "deep_min_p000": 0.55,
                          "null_D_band": 0.05, "win_floor": 0.10},
                "shuffle_seed": SHUFFLE_SEED, "pair": list(pair), "triple": triple,
                "job_id": jid, "metas": metas}
    outp = os.path.join(HERE, '..', 'results', f'{args.tag}_jobids.json')
    json.dump(manifest, open(outp, 'w'), indent=1)
    print(f"\nSubmitted ONE job, {len(tqcs)} PUBs -> job_id={jid}")
    print(f"Manifest -> {os.path.abspath(outp)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
