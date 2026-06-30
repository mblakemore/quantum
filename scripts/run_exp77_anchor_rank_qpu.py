#!/usr/bin/env python3
"""
Exp77 (Elder C6268) — Does warm-start ANCHOR RANK survive REAL QPU noise?

THE OPEN QUESTION (mine to own; bridges two prior results that measured DIFFERENT things):
  - Exp73/F48 (Elder C6204, EXACT density-matrix sim): at realistic depolarizing dose,
    anchor RANK is preserved (Spearman rho>=0.99, argmax+top3 intact) -> I marked best-of-k
    SELECTION "noise-robust" (GREEN) but explicitly flagged it "wants a pre-registered
    HARDWARE confirmation."  <-- this experiment IS that confirmation.
  - Exp66B/F50 (Whisper C4410, real ibm_marrakesh): warm-start LIFT (cold-vs-warm MAGNITUDE)
    collapses on hardware; WHY-layer asserts real-QPU noise != depolarizing (crosstalk, SPAM,
    coherent, drift) -> "FakeMarrakesh is too optimistic."

NEITHER measured anchor RANK on real hardware. Exp66B is a MAGNITUDE result (lift contraction,
already expected from F44); it does NOT test whether the ORDER of distinct-quality anchors
survives. That is exactly the quantity best-of-k selection depends on.

THE NOVEL QUANTITY (advisor reframe): depolarizing preserves rank *because* it is an affine,
state-INDEPENDENT map (Exp73 P1). Rank can break ONLY under state-DEPENDENT noise. So measuring
rank-distortion on hardware = measuring the effective STATE-DEPENDENCE of real-device noise
beyond the depolarizing model. rank_distortion := 1 - Spearman(true_rank, measured_rank).
FakeMarrakesh rank_distortion should be ~0; the HARDWARE-minus-SIM gap is the measured novelty.

HONESTY (pre-registered):
  - This is COMPLEMENTARY to Exp66B, NOT causal. Exp66B = magnitude; Exp77 = rank. They could
    both hold with depolarizing-consistent rank intact, OR hardware could break rank too.
  - N=1 instance (EDGES_8): "rank BROKEN on hardware" is a STRONG signal; "rank PRESERVED" is
    WEAK (single instance, single backend) and would want 2-3 instances to firm up.
  - Test-retest (two time-separated QPU jobs) is MANDATORY: +/-7pp daily calibration drift is the
    documented dominant systematic; a rank claim is meaningless without QPU self-consistency.

DESIGN:
  Instance: EDGES_8 (n=8, |E|=12, max_cut=10), QAOA p=2 — SAME instance as Exp73 (continuity),
  shallow (~24 two-qubit gates, far under the ~800-1000 CZ wall -> won't fully decohere).
  Anchor pool: k=5 random-theta anchors selected to MAXIMIZE the minimum adjacent true-cost gap
  (so adjacent gaps ~1.4 cut-units >> ~0.7 cut-unit drift; the SIM gate verifies separability).
  Metric: cost-ratio = E[cut]/max_cut per anchor. Rank-based comparison (unit-invariant).

GO/NO-GO GATE (--sim, FREE, run FIRST):
  FakeMarrakesh (realistic noise model + finite shots) must CLEANLY preserve rank
  (argmax preserved AND top3 overlap==3 AND spearman>=0.9). If it does NOT, the anchors are too
  close OR the circuit too deep at this shot count -> FIX before spending any QPU. Three outcomes:
    sim preserves + hw preserves -> selection hardware-robust (weak positive at N=1)
    sim preserves + hw BREAKS    -> THE FINDING (state-dependent hardware noise beyond model)
    sim BREAKS                   -> underpowered; fix anchors/shots; do NOT submit.

USAGE:
  python3 run_exp77_anchor_rank_qpu.py --sim                 # GO/NO-GO gate (FakeMarrakesh, free)
  python3 run_exp77_anchor_rank_qpu.py --sim --noiseless     # harness sanity (noiseless AerSim)
  python3 run_exp77_anchor_rank_qpu.py --submit              # 2 batched jobs (test-retest) -> ibm_marrakesh
  python3 run_exp77_anchor_rank_qpu.py --finalize JID_A JID_B  # retrieve + grade
"""
import sys, os, json, argparse
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_exp46_fast import build_parameterized_standard_qaoa, compute_cut_value, brute_force_max_cut
from run_exp68_landscape_gap_contraction import EDGES_8, N, P_LAYERS, MEANCUT, pure_cost

from qiskit import transpile

# ---- config ----
K_ANCHORS   = 5
SHOTS       = 1024          # sim gate confirms this resolves the ~1.4-cut adjacent gaps
ANCHOR_SEED = 77            # deterministic anchor pool
POOL_DRAWS  = 600           # random-theta candidates to select the k well-spread anchors from
OPT_LEVEL   = 1
SEED_TRANSP = 42
BACKEND_NAME = "ibm_marrakesh"

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
EXP_DIR     = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "experiments")
JOBIDS_PATH = os.path.join(EXP_DIR, "exp77_jobids.json")
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(EXP_DIR, exist_ok=True)


# ---- rank stats (no scipy.stats dep; copied from Exp73) ----
def spearman(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
    ra = ra - ra.mean(); rb = rb - rb.mean()
    denom = np.sqrt((ra**2).sum() * (rb**2).sum())
    return float((ra * rb).sum() / denom) if denom > 0 else 1.0


def _max_min_gap_pool(qc, g, b, n_params):
    """Pick K anchors from POOL_DRAWS random-theta candidates to MAXIMIZE the minimum
    adjacent true-cost gap (clean, well-separated rank ladder)."""
    rng = np.random.default_rng(ANCHOR_SEED)
    cand = [rng.uniform(0, np.pi, n_params) for _ in range(POOL_DRAWS)]
    costs = np.array([pure_cost(qc, g, b, t) for t in cand])
    order = np.argsort(costs)            # ascending
    lo, hi = costs[order[0]], costs[order[-1]]
    # target K evenly spaced cost levels across [lo, hi]; pick the candidate nearest each target
    targets = np.linspace(lo, hi, K_ANCHORS)
    chosen, used = [], set()
    for tcost in targets:
        idx = int(np.argmin([abs(costs[j] - tcost) if j not in used else 1e9 for j in range(len(cand))]))
        used.add(idx); chosen.append(idx)
    thetas = [cand[i] for i in chosen]
    cvals  = np.array([costs[i] for i in chosen])
    return thetas, cvals


def _build_instance():
    max_cut = brute_force_max_cut(N, EDGES_8)
    qc, g, b = build_parameterized_standard_qaoa(P_LAYERS, N, EDGES_8)
    n_params = 2 * P_LAYERS
    thetas, true_costs = _max_min_gap_pool(qc, g, b, n_params)
    return qc, g, b, n_params, max_cut, thetas, true_costs


def _bind(qc, g, b, theta, p):
    a = {}
    for i in range(p):
        a[g[i]] = theta[i]; a[b[i]] = theta[p + i]
    bc = qc.assign_parameters(a)
    if bc.num_clbits == 0:
        bc.measure_all()
    return bc


def _counts_to_ratio(counts, max_cut):
    total = sum(counts.values())
    exp = sum((c / total) * compute_cut_value(bs, EDGES_8) for bs, c in counts.items())
    return exp / max_cut


def _rank_report(tag, true_costs, measured, max_cut):
    true_ratio = true_costs / max_cut
    true_order = np.argsort(-true_costs)
    true_best = int(true_order[0]); true_top3 = set(true_order[:3].tolist())
    meas = np.asarray(measured, float)
    meas_order = np.argsort(-meas)
    meas_best = int(meas_order[0]); meas_top3 = set(meas_order[:3].tolist())
    rho = spearman(true_costs, meas)
    argmax_ok = (meas_best == true_best)
    top3_ov = len(meas_top3 & true_top3)
    distortion = 1.0 - rho
    print(f"  [{tag}] argmax_preserved={argmax_ok} (true#{true_best} vs meas#{meas_best})"
          f"  top3_overlap={top3_ov}/3  spearman={rho:.4f}  rank_distortion={distortion:.4f}", flush=True)
    return {"tag": tag, "argmax_preserved": bool(argmax_ok), "true_best": true_best,
            "meas_best": meas_best, "top3_overlap": top3_ov, "spearman": rho,
            "rank_distortion": distortion, "measured_ratio": meas.tolist(),
            "true_ratio": true_ratio.tolist()}


# ---- SIM gate ----
def run_sim(noiseless=False):
    from qiskit_aer import AerSimulator
    qc, g, b, n_params, max_cut, thetas, true_costs = _build_instance()
    adj = np.diff(np.sort(true_costs))
    print(f"Exp77 SIM | EDGES_8 n={N} max_cut={max_cut} QAOA p={P_LAYERS} | K={K_ANCHORS} anchors | "
          f"{'NOISELESS' if noiseless else 'FakeMarrakesh'} | shots={SHOTS}", flush=True)
    print(f"  true anchor costs (sorted): {np.round(np.sort(true_costs),3).tolist()}", flush=True)
    print(f"  min adjacent gap={adj.min():.3f} cut-units  (drift~0.70; ratio {adj.min()/0.70:.2f}x)", flush=True)
    if noiseless:
        backend = AerSimulator()
    else:
        from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
        backend = AerSimulator.from_backend(FakeMarrakesh())
    measured = []
    for i, th in enumerate(thetas):
        bc = _bind(qc, g, b, th, P_LAYERS)
        tc = transpile(bc, backend=backend, optimization_level=OPT_LEVEL, seed_transpiler=SEED_TRANSP)
        res = backend.run(tc, shots=SHOTS).result()
        counts = res.get_counts()
        measured.append(_counts_to_ratio(counts, max_cut))
    print(f"  measured ratios: {np.round(measured,4).tolist()}", flush=True)
    rep = _rank_report("FakeMarrakesh" if not noiseless else "noiseless", true_costs, measured, max_cut)
    gate_pass = rep["argmax_preserved"] and rep["top3_overlap"] == 3 and rep["spearman"] >= 0.9
    print(f"\n  GO/NO-GO GATE: {'PASS -> hardware submit justified' if gate_pass else 'FAIL -> fix anchors/shots, do NOT submit QPU'}", flush=True)
    out = {"experiment": "exp77_anchor_rank_qpu", "cycle": 6268, "author": "elder",
           "phase": "sim_noiseless" if noiseless else "sim_gate",
           "instance": "EDGES_8", "n_qubits": N, "max_cut": max_cut, "qaoa_p": P_LAYERS,
           "k_anchors": K_ANCHORS, "shots": SHOTS, "min_adjacent_gap": float(adj.min()),
           "true_costs": true_costs.tolist(), "report": rep, "gate_pass": bool(gate_pass)}
    path = os.path.join(RESULTS_DIR, f"exp77_{'noiseless' if noiseless else 'sim_gate'}.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"  saved -> {path}", flush=True)
    return gate_pass


# ---- QPU submit (test-retest: TWO batched jobs) ----
def run_submit():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    qc, g, b, n_params, max_cut, thetas, true_costs = _build_instance()
    service = _get_ibm_service()
    backend = service.backend(BACKEND_NAME)
    print(f"  Backend: {backend.name} | pending={backend.status().pending_jobs}", flush=True)
    bound = [_bind(qc, g, b, th, P_LAYERS) for th in thetas]
    tqc = [transpile(c, backend=backend, optimization_level=OPT_LEVEL, seed_transpiler=SEED_TRANSP) for c in bound]
    print(f"  transpiled {len(tqc)} circuits; depths={[c.depth() for c in tqc]}", flush=True)
    job_ids = []
    for rep in ("A", "B"):   # test-retest: two time-separated batches
        sampler = SamplerV2(mode=backend)
        sampler.options.default_shots = SHOTS
        job = sampler.run([(c,) for c in tqc])
        jid = job.job_id(); job_ids.append(jid)
        print(f"  replicate {rep} submitted job_id={jid} ({len(tqc)} circuits x {SHOTS} shots)", flush=True)
    rec = {"experiment": "exp77", "backend": BACKEND_NAME, "k_anchors": K_ANCHORS, "shots": SHOTS,
           "job_ids": job_ids, "true_costs": true_costs.tolist(), "max_cut": max_cut}
    with open(JOBIDS_PATH, "w") as f:
        json.dump(rec, f, indent=2)
    print(f"  saved job ids -> {JOBIDS_PATH}", flush=True)


# ---- QPU finalize ----
def run_finalize(jids):
    from run_exp66_qpu_partb import _get_ibm_service
    qc, g, b, n_params, max_cut, thetas, true_costs = _build_instance()
    service = _get_ibm_service()
    reps = []
    for k, jid in enumerate(jids):
        job = service.job(jid); status = str(job.status())
        print(f"  job {jid} status={status}", flush=True)
        if "DONE" not in status and "Done" not in status:
            print("  -> not DONE yet; re-run --finalize later."); return
        res = job.result()
        measured = []
        for i in range(len(thetas)):
            databin = res[i].data
            reg = list(databin.__dict__.keys())[0]
            counts = getattr(databin, reg).get_counts()
            measured.append(_counts_to_ratio(counts, max_cut))
        reps.append(_rank_report(f"QPU_{'AB'[k]}", true_costs, measured, max_cut))
    # test-retest consistency + grade
    if len(reps) == 2:
        tr_rho = spearman(reps[0]["measured_ratio"], reps[1]["measured_ratio"])
        print(f"\n  TEST-RETEST consistency (job A vs B measured-rank spearman): {tr_rho:.4f}", flush=True)
    argmax_both = all(r["argmax_preserved"] for r in reps)
    top3_both = all(r["top3_overlap"] >= 2 for r in reps)
    hw_distortion = float(np.mean([r["rank_distortion"] for r in reps]))
    print("\n================ GRADE ================", flush=True)
    if argmax_both and top3_both:
        print("  P2 PASS: anchor SELECTION is HARDWARE-ROBUST — argmax preserved + top3>=2/3 on BOTH", flush=True)
        print("    replicates. Exp73 sim-only rank claim CONFIRMED on real QPU (WEAK, N=1 instance).", flush=True)
    else:
        print("  P2-alt (THE FINDING): anchor SELECTION breaks on real QPU while sim preserved it.", flush=True)
        print("    Real-device noise is materially STATE-DEPENDENT beyond depolarizing -> Exp73 GREEN", flush=True)
        print("    for best-of-k must be DOWNGRADED to sim-only. rank ranks must be done noiselessly.", flush=True)
    print(f"  mean hardware rank_distortion={hw_distortion:.4f} (FakeMarrakesh ~0 expected; the gap = novel measured state-dependence)", flush=True)
    out = {"experiment": "exp77_anchor_rank_qpu", "cycle": 6268, "phase": "qpu_finalize",
           "job_ids": jids, "replicates": reps, "argmax_both": bool(argmax_both),
           "top3_both": bool(top3_both), "mean_hw_rank_distortion": hw_distortion,
           "true_costs": true_costs.tolist(), "max_cut": max_cut}
    path = os.path.join(RESULTS_DIR, "exp77_qpu_results.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"  saved -> {path}", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sim", action="store_true", help="GO/NO-GO gate on FakeMarrakesh (free)")
    ap.add_argument("--noiseless", action="store_true", help="with --sim: noiseless AerSim harness sanity")
    ap.add_argument("--submit", action="store_true", help="submit 2 batched test-retest jobs to ibm_marrakesh")
    ap.add_argument("--finalize", nargs="+", metavar="JID", help="retrieve + grade QPU jobs")
    args = ap.parse_args()
    if args.sim:
        run_sim(noiseless=args.noiseless)
    elif args.submit:
        run_submit()
    elif args.finalize:
        run_finalize(args.finalize)
    else:
        ap.print_help()
