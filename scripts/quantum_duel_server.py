#!/usr/bin/env python3
"""Quantum Duel shot server (Whisper C4543) — makes demo/static-duel LIVE.

The demo's quantum bot normally REPLAYS July's measured statistics. Run this server
with IBM credentials and every roll instead consumes ONE real measured shot from a
fresh switch job. That is the honest sense in which you "play against a quantum
opponent": the entropy driving the quantum lane was produced by ibm_marrakesh
minutes ago, through the actual two-censor switch circuits.

BRING YOUR OWN KEY (public quickstart — see demo/static-duel/README.md):
  1. Free IBM Quantum account -> API token: https://quantum.ibm.com
  2. pip install qiskit qiskit-ibm-runtime
  3. export QISKIT_IBM_TOKEN=<your token>     (or use a saved ~/.qiskit account)
  4. python3 quantum_duel_server.py --submit --serve
  5. open the demo (GitHub Pages or local) and click "try LIVE"

Usage:
  --submit            ONE job: 32 circuits x 256 shots (~2-3 sec of YOUR quota;
                      asks for confirmation, prints the estimate first) -> duel_shots.json
  --serve             http://localhost:8787/shots?n=N (never spends; never auto-resubmits)
  --dry-run           test pool without a key or spend (marginal-faithful only)
  --backend NAME      default ibm_marrakesh; any Heron open-plan device works
  --yes               skip the confirmation prompt

Key safety: the token is read from the standard qiskit locations only (env var or your
saved account); this tool never writes, logs, or transmits it anywhere except to IBM.
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


def get_service():
    """Standard public auth chain: saved account, else QISKIT_IBM_TOKEN env var."""
    from qiskit_ibm_runtime import QiskitRuntimeService
    try:
        return QiskitRuntimeService()
    except Exception:
        tok = os.environ.get("QISKIT_IBM_TOKEN") or os.environ.get("IBMQ_TOKEN")
        if not tok:
            sys.exit("No IBM credentials found. Set QISKIT_IBM_TOKEN or save an account "
                     "(see demo/static-duel/README.md).")
        return QiskitRuntimeService(channel="ibm_quantum_platform", token=tok)


def pick_pair(backend):
    """Least-noisy coupled pair by 2q error + readouts (self-contained for public use)."""
    target = backend.target
    twoq = 'cz' if 'cz' in target.operation_names else (
        'ecr' if 'ecr' in target.operation_names else None)
    best, best_cost = None, 1e9
    for (a, b), inst in (target[twoq] if twoq else {}).items():
        e = getattr(inst, 'error', None)
        if e is None:
            continue
        try:
            e += target['measure'][(a,)].error + target['measure'][(b,)].error
        except Exception:
            pass
        if e < best_cost:
            best_cost, best = e, (a, b)
    return best, best_cost


def do_submit(backend_name, assume_yes):
    from qiskit import transpile
    from qiskit_ibm_runtime import SamplerV2
    from exp106_capacity_activation import build_circuit

    svc = get_service()
    backend = svc.backend(backend_name)
    try:
        u = svc.usage()
        print(f"your quota: {u.get('usage_remaining_seconds')}s remaining "
              f"of {u.get('usage_limit_seconds')}s")
    except Exception:
        pass
    pair, cost = pick_pair(backend)
    print(f"backend {backend.name}, best pair {pair} (err {cost:.5f})")
    print("COST: one job, 32 circuits x 256 shots = 8192 shots, typically 2-3 seconds "
          "of YOUR quantum quota (thousands of demo rounds per refill).")
    if not assume_yes and input("submit? [y/N] ").strip().lower() != "y":
        print("aborted, nothing spent"); return False
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
    json.dump({"job": job.job_id(), "backend": backend.name, "shots": shots}, open(POOL, "w"))
    print(f"banked {len(shots)} real shots -> {POOL}")
    return True


def do_dry_run():
    """Test pool WITHOUT a key or spend. Synthesized from Exp106's measured AGGREGATE
    statistics (P_up, conditional agree rates) — statistics-faithful but not real shots;
    the pool is labeled accordingly and the demo banner will say so."""
    src = json.load(open(os.path.join(HERE, "..", "results", "exp106_hw_results.json")))
    sw = src["switch"]
    p_up = (sw["p_plus_b0"] + sw["p_plus_b1"]) / 2
    s = ((sw["R_b0"] - sw["R_b1"]) / 2) / (8 / 15)
    p_agree_up, p_agree_dn = (1 + s / 5) / 2, (1 - s / 3) / 2
    shots = []
    for _ in range(8192):
        t = random.randint(0, 1)
        up = random.random() < p_up
        agree = random.random() < (p_agree_up if up else p_agree_dn)
        shots.append({"t": t, "s": 0 if up else 1, "m": t if agree else 1 - t})
    json.dump({"job": "DRY-RUN (synthesized from measured aggregates — not real shots; "
                      "use --submit for the real thing)",
               "backend": "none", "shots": shots}, open(POOL, "w"))
    print(f"dry-run pool: {len(shots)} synthesized shots -> {POOL}")


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
    ap.add_argument("--backend", default="ibm_marrakesh")
    ap.add_argument("--yes", action="store_true")
    a = ap.parse_args()
    if a.submit:
        if not do_submit(a.backend, a.yes):
            sys.exit(0)
    if a.dry_run:
        do_dry_run()
    if a.serve:
        sys.exit(do_serve())
    if not (a.submit or a.serve or a.dry_run):
        print(__doc__)
