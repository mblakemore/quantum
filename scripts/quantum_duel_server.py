#!/usr/bin/env python3
"""Quantum Duel shot server (Whisper C4543) — makes demo/static-duel LIVE.

The demo's quantum bot normally REPLAYS July's measured statistics. Run this server
with IBM credentials and every roll instead consumes ONE real measured shot from a
fresh switch job. That is the honest sense in which you "play against a quantum
opponent": the entropy driving the quantum lane was produced by ibm_marrakesh
minutes ago, through the actual two-censor switch circuits.

Usage:
  python3 quantum_duel_server.py --submit      # ONE job: 32 circuits x 256 shots
                                               #   (~2-3 QPU-sec) -> results/duel_shots.json
  python3 quantum_duel_server.py --serve       # http://localhost:8787/shots?n=4000
  python3 quantum_duel_server.py --dry-run     # build a pool from Exp106's stored counts
                                               #   (replay-grade; no key, no spend)

Budget honesty: --submit spends ~2-3 quantum-seconds (window-science/outreach tranche;
8k shots ~ thousands of demo rounds). It never auto-resubmits: when the pool runs dry
the server says so and you decide.
"""
import argparse
import itertools
import json
import os
import random
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "experiments"))
POOL = os.path.join(HERE, "..", "results", "duel_shots.json")
PAULIS = "1XYZ"


def counts_to_shots(counts, input_bit):
    """Count keys 'tc': k[0]=target bit, k[1]=control bit (0 = '+' = stamp UP)."""
    out = []
    for k, n in counts.items():
        out += [{"t": input_bit, "s": int(k[1]), "m": int(k[0])}] * n
    return out


def do_submit():
    from qiskit import transpile
    from qiskit_ibm_runtime import SamplerV2
    from run_exp66_qpu_partb import _get_ibm_service
    from run_exp105_causal_game_submit import pick_pair
    from exp106_capacity_activation import build_circuit

    svc = _get_ibm_service()
    backend = svc.backend("ibm_marrakesh")
    u = svc.usage()
    print(f"budget: {u.get('usage_remaining_seconds')}s remaining")
    pair, cost, _ = pick_pair(backend)
    print(f"pair {pair} cost {cost:.5f}; submitting 32 circuits x 256 shots (~2-3 qsec)")
    tqcs, metas = [], []
    for a, b in itertools.product(PAULIS, repeat=2):
        for bit in (0, 1):
            qc = build_circuit(a, b, bit)
            tqcs.append(transpile(qc, backend, initial_layout=list(pair),
                                  seed_transpiler=4543, optimization_level=1))
            metas.append(bit)
    job = SamplerV2(mode=backend).run([(t, None, 256) for t in tqcs])
    print(f"job {job.job_id()} submitted; waiting for result...")
    res = job.result()
    shots = []
    for pr, bit in zip(res, metas):
        db = pr.data
        reg = getattr(db, "c", None) or getattr(db, "meas", None)
        shots += counts_to_shots(reg.get_counts(), bit)
    random.shuffle(shots)
    json.dump({"job": job.job_id(), "backend": "ibm_marrakesh", "shots": shots}, open(POOL, "w"))
    print(f"banked {len(shots)} real shots -> {POOL}")


def do_dry_run():
    src = json.load(open(os.path.join(HERE, "..", "results", "exp106_hw_results.json")))
    shots = []
    for r in src["rows"]:
        if r["kind"] != "switch":
            continue
        # rows carry p_plus only; reconstruct a proportional pseudo-count pool per circuit.
        n = r["shots"]
        # p_plus = P(control '0'); split target by measured conditional structure is not
        # stored per-row -> dry-run pools are marginal-faithful only. Fine for TESTING;
        # REPLAY mode in the demo is already statistics-faithful, and --submit is the
        # real thing. Label accordingly.
        n_up = round(r["p_plus"] * n)
        for s, cnt in ((0, n_up), (1, n - n_up)):
            for _ in range(cnt):
                shots.append({"t": r["input_bit"], "s": s, "m": random.randint(0, 1)})
    random.shuffle(shots)
    json.dump({"job": "DRY-RUN (marginals only — use --submit for the real thing)",
               "backend": "none", "shots": shots}, open(POOL, "w"))
    print(f"dry-run pool: {len(shots)} pseudo-shots -> {POOL}")


class H(BaseHTTPRequestHandler):
    pool = None

    def do_GET(self):
        q = urlparse(self.path)
        if q.path != "/shots":
            self.send_response(404); self.end_headers(); return
        n = int(parse_qs(q.query).get("n", ["1000"])[0])
        take = H.pool["shots"][:n]
        H.pool["shots"] = H.pool["shots"][n:]
        body = json.dumps({"job": H.pool["job"], "shots": take,
                           "remaining": len(H.pool["shots"])}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)
        if len(H.pool["shots"]) < 2000:
            print(f"⚠ pool low ({len(H.pool['shots'])} left) — rerun --submit when you "
                  f"want fresh entropy (never auto-spends)")

    def log_message(self, *a):
        pass


def do_serve():
    if not os.path.exists(POOL):
        print("no shot pool — run --submit (real) or --dry-run first"); return 1
    H.pool = json.load(open(POOL))
    print(f"serving {len(H.pool['shots'])} shots from {H.pool['job']} "
          f"on http://localhost:8787/shots?n=N")
    HTTPServer(("localhost", 8787), H).serve_forever()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--serve", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.submit:
        do_submit()
    if a.dry_run:
        do_dry_run()
    if a.serve:
        sys.exit(do_serve())
    if not (a.submit or a.serve or a.dry_run):
        print(__doc__)
