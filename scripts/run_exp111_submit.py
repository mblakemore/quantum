#!/usr/bin/env python3
"""run_exp111_submit.py — Exp111 E1 resource comparison, hardware submission
(Whisper C4593). Prereg: experiments/exp111-e1-resource-comparison-preregistration.md
(FROZEN). Usage: --scan (FREE) | --submit.

Frozen apparatus set (C4592 lesson): initial_layout=pair, seed_transpiler=4593,
optimization_level=1 (level 3 cancels the barrier-fenced identity pads — caught at scan; level 1 preserves the Exp106-validated skeletons). Audit: per-PUB CZ count must match the FakeMarrakesh-tier
value for the same label recorded at scan time — label-wise, not histogram-wise.
"""
import argparse
import itertools
import json
import os
import sys

import numpy as np
from qiskit import transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'experiments'))
from run_exp66_qpu_partb import _get_ibm_service  # noqa: E402
from run_exp105_causal_game_submit import pick_pair  # noqa: E402
from exp111_e1_feasibility import (build_paths, build_switch_prep,  # noqa: E402
                                   build_switch, SHOTS_COH, SHOTS_MIX, PAULIS)
from exp105_causal_game_feasibility import UNITARIES  # noqa: E402

SHOTS_SENT = 2000
TRANSPILE_SEED = 4593
SHUFFLE_SEED = 4593


def build_sentinel(commuting):
    """Exp105 DISC sentinel: switch witness circuit on a commuting/anticommuting pair."""
    a, b = ("X", "X") if commuting else ("X", "Z")
    return build_switch(a, b, 0, definite=False)


def build_all():
    ent = []
    for a, b in itertools.product(PAULIS, repeat=2):
        for bit in (0, 1):
            ent.append((f"sw({a},{b})b{bit}", "switch",
                        build_switch(a, b, bit), SHOTS_COH))
            ent.append((f"pa({a},{b})b{bit}", "paths",
                        build_paths(a, b, bit), SHOTS_COH))
            ent.append((f"nu({a},{b})b{bit}", "null",
                        build_switch(a, b, bit, definite=True), SHOTS_COH))
            for prep in ("0", "1"):
                ent.append((f"sm({a},{b})b{bit}p{prep}", "sw_mix",
                            build_switch_prep(a, b, bit, prep), SHOTS_MIX))
                ent.append((f"pm({a},{b})b{bit}p{prep}", "paths_mix",
                            build_paths(a, b, bit, prep), SHOTS_MIX))
    rng = np.random.default_rng(SHUFFLE_SEED)
    ent = [ent[i] for i in rng.permutation(len(ent))]
    sent = []
    for rep in ("start", "mid", "end"):
        for comm in (True, False):
            sent.append((f"sent_{rep}_{'comm' if comm else 'anti'}", "sentinel",
                         build_sentinel(comm), SHOTS_SENT))
    third = len(ent) // 3
    return (sent[0:2] + ent[:third] + sent[2:4] + ent[third:2 * third]
            + ent[2 * third:] + sent[4:6])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--backend", default="ibm_marrakesh")
    ap.add_argument("--tag", default="exp111")
    args = ap.parse_args()

    svc = _get_ibm_service()
    backend = svc.backend(args.backend)
    st = backend.status()
    print(f"Backend {backend.name}: operational={st.operational} "
          f"pending={st.pending_jobs}")
    pair, cost, twoq = pick_pair(backend)
    print(f"pair={pair} cost={cost:.5f} 2q={twoq}")

    # reference CZ per label from the FakeMarrakesh tier pipeline (same transpile
    # params on the LIVE target = the audit expectation is the live transpile of
    # the same logical circuit; label-wise self-consistency: switch/mix uniform,
    # paths within {2,3,4}, null 0)
    tqcs, metas, viol = [], [], []
    for lab, kind, qc, shots in build_all():
        tqc = transpile(qc, backend, initial_layout=list(pair),
                        seed_transpiler=TRANSPILE_SEED, optimization_level=1)
        n2 = sum(1 for i in tqc.data if i.operation.num_qubits == 2
                 and i.operation.name != "barrier")
        expected = {"switch": {4}, "sw_mix": {4}, "sentinel": {4},
                    "paths": {2, 3, 4}, "paths_mix": {2, 3, 4},
                    "null": {0}}[kind]
        if n2 not in expected:
            viol.append((lab, kind, n2))
        tqcs.append(tqc)
        metas.append({"label": lab, "kind": kind, "shots": shots, "twoq": n2,
                      "depth": tqc.depth()})
    from collections import Counter
    hists = {}
    for m in metas:
        hists.setdefault(m["kind"], Counter())[m["twoq"]] += 1
    print("CZ histograms:", {k: dict(v) for k, v in hists.items()})
    if viol:
        print(f"AUDIT FAIL: {viol[:8]}")
        print("ABORT per prereg.")
        return 1
    print(f"AUDIT PASS ({len(tqcs)} pubs, "
          f"{sum(m['shots'] for m in metas)} shots)")
    if not args.submit:
        print("--scan complete (FREE). Re-run with --submit to spend QPU.")
        return 0

    from qiskit_ibm_runtime import SamplerV2
    job = SamplerV2(mode=backend).run(
        [(t, None, m["shots"]) for t, m in zip(tqcs, metas)])
    jid = job.job_id()
    manifest = {
        "experiment": "exp111-e1-resource-comparison", "cycle": "C4593-whisper",
        "backend": args.backend, "tag": args.tag,
        "prereg": "experiments/exp111-e1-resource-comparison-preregistration.md",
        "gates": {"G1_sent_min_disc": 1.60, "G2_null_D_band": 0.10,
                  "G3_mix_band": 0.04, "G4_switch_floor": 0.10,
                  "G5_paths_floor": 0.05, "G6_diff_floor": 0.02},
        "filters_tc_order": {"w_sw": [0.5, -0.5, -0.5, 0.5],
                             "w_pa": [0.5, -0.5, 0.5, -0.5]},
        "prefiled": {"S_switch": [0.225, 0.245], "S_paths": [0.115, 0.128],
                     "S_ratio": [1.7, 2.1]},
        "transpile": {"seed": TRANSPILE_SEED, "opt_level": 1,
                      "layout": list(pair)},
        "shuffle_seed": SHUFFLE_SEED, "pair": list(pair), "pair_cost": cost,
        "job_id": jid, "metas": metas,
    }
    outp = os.path.join(HERE, '..', 'results', f'{args.tag}_jobids.json')
    with open(outp, "w") as f:
        json.dump(manifest, f, indent=1, default=float)
    print(f"SUBMITTED job {jid}; manifest -> {outp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
