#!/usr/bin/env python3
"""
Exp81 (Elder C6272) — "Dodge the noise using the map": does noise-aware qubit PLACEMENT shrink the
hardware bias of the QQQ tail-probability loader? (Creator: "if we know where the noise is, maybe we
can get by it.")

This operationalizes the ONE noise lever that actually works (route AROUND noise, not subtract it):
pick the physical qubits the calibration map says are quietest. NOT mitigation (no post-hoc subtract);
pure placement.

DESIGN:
  - Reuse the VALIDATED Exp78 loader (genuine lognormal QQQ distribution -> P(top bit = 1) = P(S_T>K)),
    but RECENTER the strike to K=752 so a_true ~ 0.246 (NOT ~0.48). Reason: depolarizing/readout noise
    pulls the answer toward 0.5; at a_true~0.48 the bias is invisible (near the fixed point) — the trap
    flagged in the deconvolution idea. At a_true~0.25 the bias is large and the placement contrast is
    resolvable.
  - Noise map (ibm_marrakesh backend.properties()): readout error spans 0.0029 (q44) .. 0.50 (171x),
    2q gate error 0.001 .. 1.0 (dead couplers). Huge room for placement to matter.
  - Pick connected 3-qubit paths; objective qubit (virtual q2 = MSB, the answer = P(MSB=1)) gets the
    path's best (or worst) readout qubit:
       BEST  = min combined (readout, weighted on MSB) + 2q-edge error
       WORST = max combined (the cautionary range)
       DEFAULT = plain transpile (does the tool already auto-dodge?)
  - Run all three (test-retest, 8192 shots), measure a_hw = P(MSB=1), bias = a_hw - a_true_discrete.

PRE-REGISTERED PREDICTION (committed before HW):
  |bias(BEST)| << |bias(WORST)| (the map buys a lot, given 171x readout spread) — BUT |bias(BEST)| > 0
  (you get BY the noise, not PAST it: placement is a constant-factor dodge, it does not move the wall).
  DEFAULT likely close to BEST IF modern transpile is already noise-aware (an honest "the tool does it
  for you" outcome).

USAGE:
  python3 run_exp81_noise_dodge_placement.py --sim       # validate recentered loader + pick triples (free)
  python3 run_exp81_noise_dodge_placement.py --submit    # BEST/WORST/DEFAULT x2 reps -> ibm_marrakesh
  python3 run_exp81_noise_dodge_placement.py --finalize <jobids.json>
"""
import sys, os, json, argparse
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qae_qqq_tail_demo as D
D.STRIKE = 752.0   # recenter for a_true ~ 0.246 (resolvable bias)
from qiskit import transpile

SHOTS = 8192
SEED_TRANSP = 42
BACKEND_NAME = "ibm_marrakesh"
EXP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "experiments")
RES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
JOBIDS_PATH = os.path.join(EXP_DIR, "exp81_jobids.json")
os.makedirs(EXP_DIR, exist_ok=True); os.makedirs(RES_DIR, exist_ok=True)


def pick_triples(backend):
    """From the live noise map, pick BEST and WORST connected 3-qubit paths.
    Returns dict: {label: {"layout":[p0,p1,p2 with p2=MSB], "score":..., "ro":[...], "msb_ro":..}}"""
    props = backend.properties()
    cm = backend.coupling_map
    n = backend.num_qubits
    ro = np.array([props.readout_error(q) for q in range(n)])
    adj = {q: set() for q in range(n)}
    ge = {}
    for e in cm.get_edges():
        a, b = int(e[0]), int(e[1]); adj[a].add(b); adj[b].add(a)
        for gname in ("cz", "ecr", "cx"):
            try:
                ge[(a, b)] = ge[(b, a)] = props.gate_error(gname, [a, b]); break
            except Exception:
                continue
    def edge_err(a, b):
        return ge.get((a, b), 0.5)
    # enumerate connected paths q0-q1-q2 (q1 = middle)
    paths = []
    for q1 in range(n):
        nb = [x for x in adj[q1]]
        for i in range(len(nb)):
            for j in range(len(nb)):
                if i == j: continue
                q0, q2 = nb[i], nb[j]
                if q0 == q2: continue
                paths.append((q0, q1, q2))
    def score(p, msb):
        # combined readout (MSB weighted 3x since answer = P(MSB=1)) + path 2q errors
        others = [q for q in p if q != msb]
        ro_term = 3.0 * ro[msb] + sum(ro[q] for q in others)
        ge_term = edge_err(p[0], p[1]) + edge_err(p[1], p[2])
        return ro_term + ge_term
    best = None; worst = None
    for p in paths:
        # assign MSB (virtual q2) to the path endpoint with the better/worse readout depending on arm
        endpoints = [p[0], p[2]]
        msb_best = min(endpoints, key=lambda q: ro[q])
        msb_worst = max(endpoints, key=lambda q: ro[q])
        sb = score(p, msb_best); sw = score(p, msb_worst)
        if best is None or sb < best[0]:
            best = (sb, p, msb_best)
        if worst is None or sw > worst[0]:
            worst = (sw, p, msb_worst)
    out = {}
    for label, (sc, p, msb) in (("BEST", best), ("WORST", worst)):
        # layout: virtual [0,1,2] -> physical; virtual2 (MSB) = msb; the other two on the remaining path qubits
        rest = [q for q in p if q != msb]
        layout = [rest[0], rest[1], msb]   # virtual0->rest0, virtual1->rest1, virtual2(MSB)->msb
        out[label] = {"layout": [int(x) for x in layout], "score": float(sc),
                      "path": [int(x) for x in p], "msb_phys": int(msb),
                      "msb_readout": float(ro[msb]), "ro": [float(ro[q]) for q in layout]}
    return out


def run_sim():
    probs, mids, w = D.bucket_probs()
    a_cont = D.true_tail_continuous(); a_disc = D.true_tail_discrete(probs)
    print(f"Exp81 SIM | recentered K={D.STRIKE} | a_cont={a_cont:.4f} a_discrete={a_disc:.4f} (target ~0.25)", flush=True)
    A = D.build_A(probs, measure=True)
    from qiskit_aer import AerSimulator
    sim = AerSimulator()
    cn = sim.run(transpile(A, sim, seed_transpiler=SEED_TRANSP), shots=SHOTS).result().get_counts()
    print(f"  noiseless P(MSB=1) = {D._msb_one_prob(cn):.4f} vs a_disc {a_disc:.4f} -> loader OK", flush=True)
    print("  (triple selection requires live backend; run --submit)", flush=True)


def run_submit():
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    probs, mids, w = D.bucket_probs()
    a_disc = D.true_tail_discrete(probs); a_cont = D.true_tail_continuous()
    A = D.build_A(probs, measure=True)
    service = _get_ibm_service(); backend = service.backend(BACKEND_NAME)
    print(f"  Backend {backend.name} pending={backend.status().pending_jobs} | a_disc={a_disc:.4f}", flush=True)
    triples = pick_triples(backend)
    print(f"  BEST  layout={triples['BEST']['layout']} msb_phys={triples['BEST']['msb_phys']} msb_ro={triples['BEST']['msb_readout']:.4f}", flush=True)
    print(f"  WORST layout={triples['WORST']['layout']} msb_phys={triples['WORST']['msb_phys']} msb_ro={triples['WORST']['msb_readout']:.4f}", flush=True)
    arms = {}
    # BEST / WORST: forced initial_layout; DEFAULT: plain transpile (auto-layout)
    arms["BEST"]  = transpile(A, backend=backend, initial_layout=triples["BEST"]["layout"],  optimization_level=1, seed_transpiler=SEED_TRANSP)
    arms["WORST"] = transpile(A, backend=backend, initial_layout=triples["WORST"]["layout"], optimization_level=1, seed_transpiler=SEED_TRANSP)
    arms["DEFAULT"] = transpile(A, backend=backend, optimization_level=1, seed_transpiler=SEED_TRANSP)
    jobids = {}
    for arm, tqc in arms.items():
        jobids[arm] = []
        for rep in ("A", "B"):
            sampler = SamplerV2(mode=backend); sampler.options.default_shots = SHOTS
            job = sampler.run([(tqc,)]); jobids[arm].append(job.job_id())
            print(f"  {arm} rep{rep} job={job.job_id()} depth={tqc.depth()}", flush=True)
    rec = {"experiment": "exp81", "a_discrete": a_disc, "a_continuous": a_cont,
           "strike": D.STRIKE, "triples": triples, "jobids": jobids, "shots": SHOTS}
    with open(JOBIDS_PATH, "w") as f: json.dump(rec, f, indent=2)
    print(f"  saved -> {JOBIDS_PATH}", flush=True)


def run_finalize(path):
    from run_exp66_qpu_partb import _get_ibm_service
    rec = json.load(open(path))
    a_disc = rec["a_discrete"]
    service = _get_ibm_service()
    print(f"  a_discrete (truth) = {a_disc:.4f}", flush=True)
    res = {}
    for arm, jids in rec["jobids"].items():
        vals = []
        for jid in jids:
            job = service.job(jid); st = str(job.status())
            if "DONE" not in st.upper(): print(f"  {arm} {jid} {st} -> retry later"); return
            r = job.result(); db = r[0].data; reg = list(db.__dict__.keys())[0]
            vals.append(D._msb_one_prob(getattr(db, reg).get_counts()))
        m = float(np.mean(vals))
        res[arm] = {"a_hw_reps": vals, "a_hw_mean": m, "bias": m - a_disc,
                    "msb_readout": rec["triples"].get(arm, {}).get("msb_readout")}
        print(f"  {arm:<8} a_hw={m:.4f}  bias={m-a_disc:+.4f}  (msb_readout={res[arm]['msb_readout']})", flush=True)
    print("\n================ DODGE GRADE ================", flush=True)
    if "BEST" in res and "WORST" in res:
        print(f"  |bias BEST|={abs(res['BEST']['bias']):.4f}  vs  |bias WORST|={abs(res['WORST']['bias']):.4f}", flush=True)
        shrink = abs(res['WORST']['bias']) - abs(res['BEST']['bias'])
        print(f"  noise-aware placement shrinks |bias| by {shrink:+.4f}  ({'DODGE WORKS' if shrink>0 else 'no help'})", flush=True)
        print(f"  BEST bias still nonzero ({res['BEST']['bias']:+.4f}) = get BY the noise, not PAST it" , flush=True)
        if "DEFAULT" in res:
            print(f"  DEFAULT |bias|={abs(res['DEFAULT']['bias']):.4f} (tests whether plain transpile already auto-dodges)", flush=True)
    out = {"experiment": "exp81_noise_dodge_placement", "cycle": 6272, "a_discrete": a_disc, "arms": res}
    p = os.path.join(RES_DIR, "exp81_results.json")
    with open(p, "w") as f: json.dump(out, f, indent=2)
    print(f"  saved -> {p}", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sim", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--finalize", metavar="JOBIDS_JSON")
    a = ap.parse_args()
    if a.sim: run_sim()
    elif a.submit: run_submit()
    elif a.finalize: run_finalize(a.finalize)
    else: ap.print_help()
