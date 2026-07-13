#!/usr/bin/env python3
"""run_exp118_submit.py — Exp118 hidden-order diagnostics (Whisper C4634).
Prereg: experiments/exp118-hidden-order-preregistration.md (FROZEN).
Design: experiments/exp118-hidden-order-diagnostics-design.md (C4624).

Site selection happens at submit time from the LIVE coupling map, but the
selection RULES below are frozen in the prereg — deterministic given the
calibration snapshot, no discretion.

Usage: --scan (FREE: selection + transpile audit) | --submit.
"""
import argparse
import json
import os
import sys
from collections import deque

import numpy as np
from qiskit import transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "experiments"))
from run_exp66_qpu_partb import _get_ibm_service  # noqa: E402
from exp118_hidden_order_sim import probe, K  # noqa: E402

SHOTS = 6000
TRANSPILE_SEED = 4634
SHUFFLE_SEED = 4634
DEAD = 0.5          # error >= DEAD (or None/NaN) disqualifies a qubit/edge
MIN_CTRL_HOPS = 3   # control site: min graph distance between the two pairs


def _twoq_name(target):
    for cand in ("cz", "ecr", "cx"):
        if cand in target.operation_names:
            return cand
    raise RuntimeError("no native 2q gate found in target")


def _calib(target):
    """Undirected edge -> 2q error; qubit -> readout error; adjacency."""
    name = _twoq_name(target)
    err, ro, adj = {}, {}, {}
    for key, inst in target[name].items():
        e = tuple(sorted(key))
        v = getattr(inst, "error", None)
        if v is None or not np.isfinite(v) or v >= DEAD:
            continue
        err[e] = min(err.get(e, 1.0), float(v))
        adj.setdefault(e[0], set()).add(e[1])
        adj.setdefault(e[1], set()).add(e[0])
    for (q,), inst in target["measure"].items():
        v = getattr(inst, "error", None)
        if v is not None and np.isfinite(v) and v < DEAD:
            ro[q] = float(v)
    return name, err, ro, adj


def _dist_from(srcs, adj):
    d = {s: 0 for s in srcs}
    dq = deque(srcs)
    while dq:
        u = dq.popleft()
        for v in adj.get(u, ()):  # noqa: B905
            if v not in d:
                d[v] = d[u] + 1
                dq.append(v)
    return d


def select_sites(target):
    """FROZEN RULES (prereg §Sites).
    Hotspot: disjoint edges A,B + spectator s (not in A∪B) adjacent to >=1
    qubit of EACH edge; minimize err(A)+err(B); tiebreak spectator readout
    error, then lexicographic (A,B,s).
    Control: disjoint edges A,B with graph distance(A,B) >= 3 hops; spectator
    = neighbor of A (not in A∪B, not adjacent to B) with lowest readout
    error; minimize err(A)+err(B); tiebreak lexicographic. No exclusion
    against reusing hotspot qubits (rule frozen: none needed physically)."""
    name, err, ro, adj = _calib(target)
    edges = sorted(err)

    hot = []
    for i, ea in enumerate(edges):
        for eb in edges[i + 1:]:
            if set(ea) & set(eb):
                continue
            for s in sorted((adj.get(ea[0], set()) | adj.get(ea[1], set()))
                            & (adj.get(eb[0], set()) | adj.get(eb[1], set()))
                            - set(ea) - set(eb)):
                if s in ro:
                    hot.append((err[ea] + err[eb], ro[s], ea, eb, s))
    if not hot:
        raise RuntimeError("no hotspot candidate on live map")
    hot.sort()
    h_score, h_ro, hA, hB, hS = hot[0]

    ctrl = []
    for i, ea in enumerate(edges):
        da = _dist_from(list(ea), adj)
        for eb in edges[i + 1:]:
            if set(ea) & set(eb):
                continue
            gap = min(da.get(q, 10**9) for q in eb)
            if gap < MIN_CTRL_HOPS:
                continue
            cands = [(ro[s], s) for s in
                     sorted((adj.get(ea[0], set()) | adj.get(ea[1], set()))
                            - set(ea) - set(eb))
                     if s in ro and not (set(adj.get(s, set())) & set(eb))]
            if not cands:
                continue
            s_ro, s = min(cands)
            ctrl.append((err[ea] + err[eb], ea, eb, s, s_ro))
    if not ctrl:
        raise RuntimeError("no control candidate on live map")
    ctrl.sort()
    c_score, cA, cB, cS, c_ro = ctrl[0]

    return name, {
        "hotspot": {"pairA": hA, "pairB": hB, "spectator": hS,
                    "sum_2q_err": h_score, "spect_ro": h_ro},
        "control": {"pairA": cA, "pairB": cB, "spectator": cS,
                    "sum_2q_err": c_score, "spect_ro": c_ro,
                    "min_hops": MIN_CTRL_HOPS},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--backend", default="ibm_marrakesh")
    ap.add_argument("--tag", default="exp118")
    args = ap.parse_args()

    svc = _get_ibm_service()
    backend = svc.backend(args.backend)
    print(f"Backend {backend.name}: pending={backend.status().pending_jobs}")
    twoq, sites = select_sites(backend.target)
    print("SITE SELECTION (frozen rules):",
          json.dumps(sites, indent=1, default=str))

    pubs, metas, audit_ok = [], [], True
    for site in ("hotspot", "control"):
        sel = sites[site]
        layout = [sel["pairA"][0], sel["pairA"][1], sel["spectator"],
                  sel["pairB"][0], sel["pairB"][1]]
        legal = {tuple(sorted(sel["pairA"])), tuple(sorted(sel["pairB"]))}
        for sch in ("seqAB", "seqBA", "par"):
            tqc = transpile(probe(sch), backend, initial_layout=layout,
                            seed_transpiler=TRANSPILE_SEED,
                            optimization_level=1)
            tw = [tuple(sorted(tqc.find_bit(q).index for q in i.qubits))
                  for i in tqc.data
                  if i.operation.num_qubits == 2
                  and i.operation.name != "barrier"]
            ok = (len(tw) == 2 * K and set(tw) <= legal
                  and all(i.operation.name in (twoq, "barrier")
                          for i in tqc.data
                          if i.operation.num_qubits == 2))
            audit_ok &= ok
            print(f"  {site}/{sch}: 2q={len(tw)} (want {2 * K}) "
                  f"edges={sorted(set(tw))} depth={tqc.depth()} "
                  f"audit={'PASS' if ok else 'FAIL'}")
            pubs.append(tqc)
            metas.append({"label": f"{site}_{sch}", "site": site,
                          "schedule": sch, "layout": layout,
                          "shots": SHOTS, "twoq": len(tw),
                          "depth": tqc.depth()})
    print(f"AUDIT: {'PASS' if audit_ok else 'FAIL'} ({len(pubs)} pubs, "
          f"{sum(m['shots'] for m in metas)} shots)")
    if not audit_ok:
        return 1

    rng = np.random.default_rng(SHUFFLE_SEED)
    order = list(rng.permutation(len(pubs)))
    pubs = [pubs[i] for i in order]
    metas = [metas[i] for i in order]
    print("pub order (shuffled, seed %d):" % SHUFFLE_SEED,
          [m["label"] for m in metas])

    if not args.submit:
        print("--scan complete (FREE).")
        return 0

    from qiskit_ibm_runtime import SamplerV2
    job = SamplerV2(mode=backend).run([(t, None, m["shots"])
                                       for t, m in zip(pubs, metas)])
    jid = job.job_id()
    manifest = {
        "experiment": "exp118-hidden-order-diagnostics",
        "cycle": "C4634-whisper", "backend": args.backend, "tag": args.tag,
        "prereg": "experiments/exp118-hidden-order-preregistration.md",
        "twoq_gate": twoq, "k": K, "shots_per_arm": SHOTS,
        "floor": 0.0223, "sigma_rule": 5, "bootstrap": {"B": 200,
                                                        "seed": 4634},
        "sites": sites, "transpile_seed": TRANSPILE_SEED,
        "shuffle_seed": SHUFFLE_SEED, "job_id": jid, "metas": metas,
    }
    outp = os.path.join(HERE, "..", "results", f"{args.tag}_jobids.json")
    with open(outp, "w") as f:
        json.dump(manifest, f, indent=1, default=str)
    print(f"SUBMITTED job {jid}; manifest -> {outp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
