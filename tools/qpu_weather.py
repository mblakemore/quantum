#!/usr/bin/env python3
"""qpu_weather.py — THE QPU WEATHER SERVICE (Whisper C4681; audit item (e), the
zero-qubit advantage. Substrate claude-opus-4-8).

THE PREMISE (F81): a QPU is a fluctuating channel whose quality is cheaply
MEASURABLE but poorly PUBLISHED — IBM's calibration feed was FLAT across a 3x
deep-circuit quality swing, and our live sentinel out-predicted it. This tool
operationalizes that into a user-facing SCHEDULING oracle: a cheap live NOWCAST
that predicts how well a deep circuit will run RIGHT NOW, benchmarked against
the vendor's published forecast. No quantum speedup — a real, sellable
scheduling advantage for anyone running these machines.

The report:
  - QUIET-QUBIT MAP: best-placement line, ranked from published calibration.
  - LIVE READOUT WEATHER: measured readout error vs published (drift detector).
  - MIRROR LADDER: P(|0..0>) of a Clifford mirror (L^K (L^K)^-1 -> |0..0> ideal)
    at shallow (K=1) and deep (K=4) depth = live fidelity at each depth.
  - NOWCAST: extrapolate the shallow mirror to deep depth (sentinel forecast).
  - VENDOR FORECAST: predict the deep mirror from published per-gate errors.
  - VERDICT: whichever forecast is closer to the measured deep fidelity wins the
    window; plus a GO / NO-GO for deep work at a fidelity threshold.

Usage: python3 tools/qpu_weather.py --backend <name> [--scan|--nowcast] [--report <job>]
"""
import argparse
import json
import math
import os

import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
K_SHALLOW, K_DEEP = 1, 4
GO_THRESHOLD = 0.30          # deep-mirror P0 below this = NO-GO for deep work


def pick_line(backend, length=4):
    target = backend.target
    twoq = 'cz' if 'cz' in target.operation_names else 'ecr'
    err, adj = {}, {}
    for (a, b), inst in target[twoq].items():
        e = getattr(inst, 'error', None)
        if e is None:
            continue
        err[(a, b)] = err[(b, a)] = e
        adj.setdefault(a, set()).add(b)
        adj.setdefault(b, set()).add(a)
    ro = {q: (getattr(i, 'error', 0.0) or 0.0)
          for (q,), i in target['measure'].items()}
    best, bc = None, 1e9

    def dfs(path, cost):
        nonlocal best, bc
        if len(path) == length:
            tot = cost + sum(ro.get(q, 0) for q in path)
            if tot < bc:
                bc, best = tot, list(path)
            return
        for nb in adj.get(path[-1], ()):
            if nb not in path:
                dfs(path + [nb], cost + err[(path[-1], nb)])
    for a in adj:
        for b in adj[a]:
            dfs([a, b], err[(a, b)])
    return best, bc, err, ro


def mirror_circuit(n, K):
    """L^K then (L^K)^-1 -> |0..0> ideal. L = CZ chain + H layer (self-inverse
    gates), so the inverse is the reversed gate list. P(|0..0>) = fidelity."""
    qc = QuantumCircuit(n, n)
    ops = []
    for _ in range(K):
        for i in range(n - 1):
            ops.append(("cz", i, i + 1))
        for i in range(n):
            ops.append(("h", i))
    for name, *qs in ops:
        getattr(qc, name)(*qs)
    qc.barrier()
    for name, *qs in reversed(ops):
        getattr(qc, name)(*qs)
    qc.measure(range(n), range(n))
    return qc


def readout_probe(n, ones):
    qc = QuantumCircuit(n, n)
    if ones:
        qc.x(range(n))
    qc.measure(range(n), range(n))
    return qc


def p_all_zero(counts):
    tot = sum(counts.values())
    return counts.get("0" * len(next(iter(counts))), 0) / tot


def build_all(n):
    return [("ro0", readout_probe(n, False)),
            ("ro1", readout_probe(n, True)),
            ("mir_shallow", mirror_circuit(n, K_SHALLOW)),
            ("mir_deep", mirror_circuit(n, K_DEEP))]


def vendor_forecast(line, err, ro, n2_deep):
    """Predict deep-mirror P0 from PUBLISHED per-gate errors: product of
    (1-err) over the deep circuit's 2q gates + readout."""
    edges = [(line[i], line[i + 1]) for i in range(len(line) - 1)]
    e2 = np.mean([err[e] for e in edges])
    ro_mean = np.mean([ro.get(q, 0) for q in line])
    return float((1 - e2) ** n2_deep * (1 - ro_mean) ** len(line))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="ibm_marrakesh")
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--nowcast", action="store_true")
    ap.add_argument("--report", metavar="JOB_ID")
    ap.add_argument("--n", type=int, default=4)
    args = ap.parse_args()
    n = args.n

    from qiskit_ibm_runtime import QiskitRuntimeService
    svc = QiskitRuntimeService()
    backend = svc.backend(args.backend)
    line, cost, err, ro = pick_line(backend, n)
    edges = [(line[i], line[i + 1]) for i in range(n - 1)]

    if args.report:
        job = svc.job(args.report)
        res = job.result()
        man = json.load(open(os.path.join(HERE, "..", "results",
                                          "qpu_weather_job.json")))
        line = man["line"]
        edges = [(line[i], line[i + 1]) for i in range(len(line) - 1)]
        d = {lab: res[i].data.c.get_counts()
             for i, (lab, _) in enumerate(build_all(len(line)))}
        ro0 = p_all_zero(d["ro0"])
        ro1 = d["ro1"].get("1" * len(line), 0) / sum(d["ro1"].values())
        shallow = p_all_zero(d["mir_shallow"])
        deep = p_all_zero(d["mir_deep"])
        # nowcast: SPAM-corrected extrapolation. P0(K) ~ SPAM * f^K, SPAM from
        # the readout probe (prep+measure floor), f = per-K-block gate fidelity
        # from the shallow point. deep_pred = SPAM * (P0_shallow/SPAM)^K_deep.
        spam = max(ro0, 1e-6)
        f_layer = (shallow / spam) ** (1.0 / K_SHALLOW) if shallow > 0 else 0
        nowcast_deep = spam * f_layer ** K_DEEP
        vend = vendor_forecast(line, err, ro, man["n2_deep"])
        e_now = abs(nowcast_deep - deep)
        e_vend = abs(vend - deep)
        winner = "SENTINEL" if e_now < e_vend else "VENDOR"
        go = deep >= GO_THRESHOLD
        report = {
            "backend": args.backend, "line": line, "job": args.report,
            "quiet_qubit_line": line, "line_cost": cost,
            "live_readout": {"P0_all0": ro0, "P1_all1": ro1,
                             "published_readout_mean": float(np.mean(
                                 [ro.get(q, 0) for q in line]))},
            "mirror_ladder": {"shallow_K1_P0": shallow, "deep_K4_P0": deep},
            "nowcast_deep_pred": nowcast_deep,
            "vendor_deep_pred": vend, "measured_deep": deep,
            "nowcast_error": e_now, "vendor_error": e_vend,
            "forecast_winner": winner,
            "verdict": ("GO" if go else "NO-GO") + " for deep work",
            "substrate": "claude-opus-4-8"}
        print("=" * 60)
        print(f"QPU WEATHER REPORT — {args.backend} (job {args.report})")
        print("=" * 60)
        print(f"  QUIET-QUBIT LINE : {line} (cost {cost:.4f})")
        print(f"  LIVE READOUT     : |0..0>={ro0:.4f} |1..1>={ro1:.4f}  "
              f"(published mean err {report['live_readout']['published_readout_mean']:.4f})")
        print(f"  MIRROR LADDER    : shallow(K1) P0={shallow:.4f}  "
              f"deep(K4) P0={deep:.4f}")
        print(f"  NOWCAST forecast : deep P0 -> {nowcast_deep:.4f}  "
              f"(|err|={e_now:.4f})")
        print(f"  VENDOR forecast  : deep P0 -> {vend:.4f}  (|err|={e_vend:.4f})")
        print(f"  FORECAST WINNER  : {winner}  (closer to measured {deep:.4f})")
        print(f"  VERDICT          : {report['verdict']} "
              f"(threshold {GO_THRESHOLD})")
        json.dump(report, open(os.path.join(HERE, "..", "results",
                                            "qpu_weather_report.json"), "w"),
                  indent=1, default=float)
        print("wrote results/qpu_weather_report.json")
        return 0

    # scan / nowcast: build + audit, optionally submit
    print(f"Backend {backend.name}: quiet line={line} cost={cost:.5f}")
    tqcs, n2s = [], {}
    for lab, qc in build_all(n):
        tqc = transpile(qc, backend, initial_layout=line,
                        seed_transpiler=4681, optimization_level=1)
        n2 = sum(1 for inst in tqc.data if inst.operation.num_qubits == 2
                 and inst.operation.name != "barrier")
        n2s[lab] = n2
        tqcs.append((lab, tqc))
    print(f"  mirror 2q counts: shallow={n2s['mir_shallow']} "
          f"deep={n2s['mir_deep']}")
    print(f"  vendor deep forecast (from published cal): "
          f"{vendor_forecast(line, err, ro, n2s['mir_deep']):.4f}")
    if not args.nowcast:
        print("--scan complete (FREE). Re-run with --nowcast to fly the sentinel.")
        return 0
    from qiskit_ibm_runtime import SamplerV2
    shots = {"ro0": 4000, "ro1": 4000, "mir_shallow": 8000, "mir_deep": 8000}
    job = SamplerV2(mode=backend).run(
        [(tqc, None, shots[lab]) for lab, tqc in tqcs])
    jid = job.job_id()
    json.dump({"backend": args.backend, "line": line,
               "n2_deep": n2s["mir_deep"], "n2_shallow": n2s["mir_shallow"],
               "job_id": jid}, open(os.path.join(HERE, "..", "results",
                                                 "qpu_weather_job.json"), "w"),
              indent=1)
    print(f"SUBMITTED {jid}; report with: "
          f"python3 tools/qpu_weather.py --backend {args.backend} --report {jid}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
