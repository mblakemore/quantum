#!/usr/bin/env python3
"""
quiet_qubits.py (Elder C6273) — package the noise MAP as reusable, general-purpose, cross-DC tooling.

Creator ask: package the map into something reusable + "compute something useful in the quietness."
The useful thing IS the map, as OPERATIONAL hardware tooling the network runs blind to. Generalizes
the F57 single-circuit dodge into a library any experiment / any DC can call, on any backend.

API:
  load_map(backend)              -> {readout[], gate_err{(a,b)}, adj{q:set}, n}
  pick(backend, n, objective=True, mode='best')
                                 -> {qubits:[...], layout:[...], score, readout:[...], summary}
       greedy connected n-qubit subset minimizing (objective-weighted readout + internal 2q error).
       objective=True puts the most-measured logical qubit (highest index, e.g. the answer bit) on
       the subset's QUIETEST readout qubit. mode='worst' for the cautionary opposite.
  snapshot(backend)              -> appends a calibration snapshot to results/device-health/<backend>.jsonl
       (seeds drift tracking; the corpus noted ±7pp daily drift but never TRACKED it). ONE run = ONE
       point — this builds the hook, it is not yet a populated drift series.
  health(backend, run=False)     -> CHSH S on the QUIETEST pair vs DEFAULT vs WORST = a one-number
       "how good is the chip right now" benchmark. HONEST SCOPE: S is a device-quietness / entanglement-
       FIDELITY number, NOT "certified randomness" (device-independent randomness needs loophole-free
       Bell / space-like separation, which co-located cloud qubits cannot provide; that framing would be
       an over-claim). Tests whether quiet placement raises S toward Tsirelson 2√2≈2.828.

CLI:
  python3 quiet_qubits.py --pick N [--worst]          # offline-ish (needs live backend properties)
  python3 quiet_qubits.py --snapshot                  # log a calibration snapshot
  python3 quiet_qubits.py --health [--sim]            # CHSH benchmark (sim validates S≈2.83)
"""
import sys, os, json, math, argparse
from datetime import datetime, timezone
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qiskit import QuantumCircuit, transpile

HEALTH_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "device-health")
os.makedirs(HEALTH_DIR, exist_ok=True)
SHOTS = 4096
SEED_TRANSP = 42


# ───────── noise map ─────────
def load_map(backend):
    props = backend.properties(); n = backend.num_qubits
    readout = np.array([props.readout_error(q) for q in range(n)])
    adj = {q: set() for q in range(n)}
    gate_err = {}
    for e in backend.coupling_map.get_edges():
        a, b = int(e[0]), int(e[1]); adj[a].add(b); adj[b].add(a)
        for g in ("cz", "ecr", "cx"):
            try:
                gate_err[(a, b)] = gate_err[(b, a)] = props.gate_error(g, [a, b]); break
            except Exception:
                continue
    return {"readout": readout, "gate_err": gate_err, "adj": adj, "n": n}


def _edge(gmap, a, b):
    return gmap["gate_err"].get((a, b), 0.5)


def pick(backend, n, objective=True, mode="best", n_seeds=24):
    """Greedy connected n-qubit subset. mode='best' minimizes error, 'worst' maximizes."""
    gm = load_map(backend); ro = gm["readout"]; adj = gm["adj"]
    sign = 1 if mode == "best" else -1
    order = np.argsort(sign * ro)            # best: low readout first; worst: high first
    best = None
    for seed_q in order[:n_seeds]:
        sub = [int(seed_q)]
        while len(sub) < n:
            # candidate neighbors of the current connected subset
            cands = set()
            for q in sub:
                cands |= adj[q]
            cands -= set(sub)
            if not cands:
                break
            def inc(q):
                e = min((_edge(gm, q, s) for s in sub if s in adj[q]), default=0.5)
                return ro[q] + e
            pick_q = (min if mode == "best" else max)(cands, key=inc)
            sub.append(int(pick_q))
        if len(sub) < n:
            continue
        # score: objective-weighted readout + internal 2q edges (spanning)
        msb = (min if mode == "best" else max)(sub, key=lambda q: ro[q])
        ro_term = (3.0 * ro[msb] + sum(ro[q] for q in sub if q != msb)) if objective else sum(ro[q] for q in sub)
        edges = [(_edge(gm, sub[i], sub[j])) for i in range(len(sub)) for j in range(i + 1, len(sub)) if sub[j] in adj[sub[i]]]
        sc = ro_term + sum(edges)
        sc = sc if mode == "best" else -sc
        if best is None or sc < best[0]:
            best = (sc, sub, msb)
    if best is None:
        raise RuntimeError(f"no connected {n}-subset found")
    _, sub, msb = best
    rest = [q for q in sub if q != msb]
    layout = rest + [msb]                     # objective (highest virtual index) -> msb (quietest)
    return {"qubits": [int(x) for x in sub], "layout": [int(x) for x in layout],
            "objective_phys": int(msb), "objective_readout": float(ro[msb]),
            "readout": [float(ro[q]) for q in layout],
            "score": float(abs(best[0])), "mode": mode}


def map_summary(backend):
    gm = load_map(backend); ro = gm["readout"]; ge = np.array(list(gm["gate_err"].values()))
    return {"n_qubits": gm["n"],
            "readout": {"min": float(ro.min()), "median": float(np.median(ro)), "max": float(ro.max())},
            "gate2q": {"min": float(ge.min()), "median": float(np.median(ge)), "max": float(ge.max())},
            "best8_readout": [[int(q), float(ro[q])] for q in np.argsort(ro)[:8]]}


def snapshot(backend, cycle=None, ts=None):
    """Append a calibration snapshot to the per-backend drift log (seeds drift tracking)."""
    s = map_summary(backend)
    # C6289: default ts to capture time. A drift log with no timestamps can't measure
    # drift RATE — the F58 seed logged ts=None, making the interval between points
    # unknowable. Stamp UTC-now when the caller doesn't supply one.
    ts = ts or datetime.now(timezone.utc).isoformat()
    rec = {"backend": backend.name, "cycle": cycle, "ts": ts, "summary": s,
           "best_pick_n2": pick(backend, 2)["qubits"], "best_pick_n3": pick(backend, 3)["qubits"]}
    path = os.path.join(HEALTH_DIR, f"{backend.name}.jsonl")
    with open(path, "a") as f:
        f.write(json.dumps(rec) + "\n")
    return path, rec


# ───────── CHSH health benchmark ─────────
# Optimal CHSH angles (radians): Alice {0, π/2}, Bob {π/4, -π/4}. To measure along plane-angle θ,
# rotate by Ry(-2θ)/2 ... we validate numerically in --sim (noiseless must give |S|≈2.828).
A_ANGLES = [0.0, math.pi / 2]
B_ANGLES = [math.pi / 4, 3 * math.pi / 4]


def _chsh_circuit(qa, qb, ang_a, ang_b, nq):
    qc = QuantumCircuit(nq, 2)
    qc.h(qa); qc.cx(qa, qb)                  # Bell |Φ+>
    qc.ry(-ang_a, qa); qc.ry(-ang_b, qb)     # measure along plane-angle theta: Ry(-theta) then Z
    qc.measure(qa, 0); qc.measure(qb, 1)
    return qc


def _corr(counts):
    tot = sum(counts.values()); e = 0
    for bs, c in counts.items():
        b = bs.replace(" ", "")
        par = 1 if b.count("1") % 2 == 0 else -1   # +1 if even parity (same), -1 if odd
        e += par * c
    return e / tot


def _S_from_corrs(E):
    # E indexed [a][b]; standard CHSH combination
    return E[0][0] - E[0][1] + E[1][0] + E[1][1]


def health(backend, run=False, sim=False):
    """CHSH S on quiet vs default vs worst pair. sim=True validates the circuit (noiseless ~2.83)."""
    if sim:
        from qiskit_aer import AerSimulator
        bk = AerSimulator()
        E = [[0, 0], [0, 0]]
        for i, aa in enumerate(A_ANGLES):
            for j, bb in enumerate(B_ANGLES):
                qc = _chsh_circuit(0, 1, aa, bb, 2)
                cn = bk.run(transpile(qc, bk, seed_transpiler=SEED_TRANSP), shots=SHOTS).result().get_counts()
                E[i][j] = _corr(cn)
        return {"sim_S": _S_from_corrs(E), "E": E}
    return None  # hardware path handled by --health (submit) below


def _run_chsh_pair(backend, qa, qb, label, service):
    from qiskit_ibm_runtime import SamplerV2
    E = [[None, None], [None, None]]
    jobmap = {}
    for i, aa in enumerate(A_ANGLES):
        for j, bb in enumerate(B_ANGLES):
            qc = _chsh_circuit(qa, qb, aa, bb, backend.num_qubits)
            tqc = transpile(qc, backend=backend, optimization_level=1, seed_transpiler=SEED_TRANSP)
            sampler = SamplerV2(mode=backend); sampler.options.default_shots = SHOTS
            job = sampler.run([(tqc,)])
            jobmap[(i, j)] = job.job_id()
    return jobmap


def _counts_from_pub(res_pub):
    """Extract counts from a SamplerV2 PrimitiveResult pub, register-name agnostic."""
    db = res_pub.data
    try:
        arr = list(db.values())[0]          # DataBin mapping interface (newer qiskit)
    except Exception:
        arr = getattr(db, "c")              # default classical register name fallback
    return arr.get_counts()


def health_finalize(service, jobs_path):
    """Retrieve a submitted CHSH health run, compute S per pair. Grades the submit-and-later gap.

    Reads {backend}_chsh_jobs.json (best/worst pairs, 4 job_ids each), pulls counts,
    computes E[i][j] and S = E00 - E01 + E10 + E11 per pair. Writes a sibling _results.json.
    PASS discrimination = S_best clears the classical bound 2 while S_worst does not.
    """
    spec = json.load(open(jobs_path))
    out = {"best_pair": spec.get("best_pair"), "worst_pair": spec.get("worst_pair"),
           "shots": SHOTS, "results": {}}
    for label, jobmap in spec["jobs"].items():
        E = [[None, None], [None, None]]
        for key, jid in jobmap.items():
            i, j = int(key[0]), int(key[1])
            counts = _counts_from_pub(service.job(jid).result()[0])
            E[i][j] = _corr(counts)
        S = _S_from_corrs(E)
        out["results"][label] = {"E": E, "S": S,
                                 "violates_classical_bound": abs(S) > 2.0}
    b = out["results"].get("best", {}).get("S")
    w = out["results"].get("worst", {}).get("S")
    if b is not None and w is not None:
        out["discriminates"] = bool(abs(b) > 2.0 and abs(w) <= 2.0)
        out["S_gap_best_minus_worst"] = abs(b) - abs(w)
    rpath = jobs_path.replace(".json", "_results.json")
    json.dump(out, open(rpath, "w"), indent=2)
    return out, rpath


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pick", type=int, metavar="N")
    ap.add_argument("--worst", action="store_true")
    ap.add_argument("--snapshot", action="store_true")
    ap.add_argument("--health", action="store_true")
    ap.add_argument("--health-finalize", dest="health_finalize", action="store_true")
    ap.add_argument("--jobs-file", default=None, help="path to a _chsh_jobs.json to finalize")
    ap.add_argument("--sim", action="store_true")
    ap.add_argument("--cycle", type=int, default=None)
    ap.add_argument("--backend", default="ibm_marrakesh")
    args = ap.parse_args()

    if args.sim and args.health:
        r = health(None, sim=True)
        print(f"[sim] CHSH noiseless S = {r['sim_S']:.4f}  (Tsirelson 2√2≈2.828; classical bound 2)", flush=True)
        print(f"      E matrix = {[[round(x,3) for x in row] for row in r['E']]}", flush=True)
        return

    from run_exp66_qpu_partb import _get_ibm_service
    service = _get_ibm_service()

    if args.health_finalize:
        jpath = args.jobs_file or os.path.join(HEALTH_DIR, f"{args.backend}_chsh_jobs.json")
        out, rpath = health_finalize(service, jpath)
        for label, r in out["results"].items():
            flag = "✅ >2 (quantum)" if r["violates_classical_bound"] else "classical (≤2)"
            print(f"  {label:5s} pair={out[label+'_pair'] if label+'_pair' in out else ''} S = {r['S']:+.4f}  {flag}", flush=True)
        if "discriminates" in out:
            print(f"  discriminates (best>2 & worst≤2): {out['discriminates']}  | S-gap = {out['S_gap_best_minus_worst']:+.4f}", flush=True)
        print(f"  results -> {rpath}", flush=True)
        return

    backend = service.backend(args.backend)

    if args.pick:
        p = pick(backend, args.pick, mode="worst" if args.worst else "best")
        print(json.dumps(p, indent=2))
    elif args.snapshot:
        path, rec = snapshot(backend, cycle=args.cycle)
        print(f"snapshot appended -> {path}")
        print(json.dumps(rec["summary"], indent=2))
    elif args.health:
        # submit CHSH on best / default / worst pairs
        best = pick(backend, 2, mode="best"); worst = pick(backend, 2, mode="worst")
        print(f"best pair={best['qubits']} (ro {best['readout']}) | worst pair={worst['qubits']} (ro {worst['readout']})", flush=True)
        jobs = {"best": _run_chsh_pair(backend, best["qubits"][0], best["qubits"][1], "best", service),
                "worst": _run_chsh_pair(backend, worst["qubits"][0], worst["qubits"][1], "worst", service)}
        jpath = os.path.join(HEALTH_DIR, f"{backend.name}_chsh_jobs.json")
        json.dump({"best_pair": best["qubits"], "worst_pair": worst["qubits"],
                   "jobs": {k: {f"{i}{j}": v for (i, j), v in m.items()} for k, m in jobs.items()}},
                  open(jpath, "w"), indent=2)
        print(f"submitted CHSH jobs -> {jpath}; finalize with --health-finalize (see file)", flush=True)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
