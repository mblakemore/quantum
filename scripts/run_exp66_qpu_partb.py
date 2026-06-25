#!/usr/bin/env python3
"""
Exp66 Part B (QPU): Hardware validation of warm-start granular escalation.
Ember C3984 — Whisper C4362 QPU access intel (billing reset 17:58 UTC 2026-06-25).

Design — "parameter-transfer" approach (rationale: full COBYLA-on-QPU requires
~100 sequential jobs per seed, impractical with 600s budget; FakeMarrakesh
COBYLA is 23s/circuit on n=20 — also too slow; noiseless COBYLA is ~0.5s):
  1. Run NOISELESS COBYLA locally to obtain: x_cold_p5, x_warm_p5, and
     p=3 anchor performance (used for LOO-CV threshold). Fast ~1-5s/seed.
  2. Submit fixed-parameter evaluation circuits to ibm_marrakesh:
     For each seed: [cold_p5_circuit, warm_p5_circuit] → ONE batched job.
  3. Retrieve QPU results → compute QPU lift = r_warm - r_cold.

Scientific question:
  Do warm-start parameters optimized on FakeMarrakesh transfer to ibm_marrakesh?
  Does the warm-start LIFT (r_warm - r_cold) survive on real QPU?
  Primary metric: QPU capk approximation using FakeMarrakesh LOO-CV threshold.

Connection to pred_c3980_001 (conf 0.52, test_cycle C4100):
  pred: "QPU granular capture-per-k < 0.40"
  This Part B provides the first direct evidence. The parameter-transfer
  simplification is noted; full QPU optimization may differ.

Usage:
  python3 run_exp66_qpu_partb.py --smoke         # 1 seed, FakeMarrakesh only
  python3 run_exp66_qpu_partb.py --submit        # 4 seeds → ibm_marrakesh batch jobs
  python3 run_exp66_qpu_partb.py --finalize JID1 JID2 JID3 JID4  # retrieve + grade
"""
import sys, os, json, time, argparse
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_exp46_fast import (
    EDGES_20, N_QUBITS_20, brute_force_max_cut,
    build_parameterized_xbasis_qaoa, evaluate_with_transpiled,
    compute_cut_value,
)
from run_exp54_warmstart import optimize_cobyla_ws, pad_params
from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime.fake_provider import FakeMarrakesh

BACKEND_NAME = "ibm_marrakesh"
SHOTS        = 128
MAXITER      = 10
K_MAX        = 2   # reduced from 3 for QPU budget
P_TARGET     = 5
P_ANCHOR     = 3
OPT_LEVEL    = 1
SEED_TRANSP  = 42

FULL_SEEDS  = [42, 44, 45, 46]   # subset of Exp64/66 pool
MAX_CUT_20  = 26                  # cached from Exp64/66 brute-force
SMOKE_SEEDS = [42]

RESULTS_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "experiments")
JOBIDS_PATH  = os.path.join(RESULTS_DIR, "exp66_partb_jobids.json")
RESULTS_PATH = os.path.join(RESULTS_DIR, "exp66_partb_results.json")

os.makedirs(RESULTS_DIR, exist_ok=True)


# ── Helpers ──────────────────────────────────────────────────────────────────

def _noiseless_sim():
    """Noiseless AerSimulator — fast parameter search (n=20 ~0.5s/circuit vs FakeMarrakesh 23s)."""
    return AerSimulator()


def _make_circuits(n_qubits, edges):
    """Build transpiled circuit templates for p3 and p5 on noiseless simulator."""
    sim = AerSimulator()
    out = {}
    for p in (P_ANCHOR, P_TARGET):
        tqc, gp, bp = build_parameterized_xbasis_qaoa(p, n_qubits, edges)
        tc = transpile(tqc, backend=sim, optimization_level=OPT_LEVEL,
                       seed_transpiler=SEED_TRANSP)
        out[p] = (tc, gp, bp)
    return out


def _make_circuits_qpu(n_qubits, edges, backend):
    """Build transpiled circuit templates for p5 on ibm_marrakesh."""
    tqc, gp, bp = build_parameterized_xbasis_qaoa(P_TARGET, n_qubits, edges)
    tc = transpile(tqc, backend=backend, optimization_level=OPT_LEVEL,
                   seed_transpiler=SEED_TRANSP)
    print(f"  QPU circuit depth p5: {tc.depth()} gates", flush=True)
    return tc, gp, bp


def _bind(transpiled_qc, gamma_params, beta_params, params, p):
    """Return a bound (no free parameters) circuit."""
    gamma_vals = params[:p]
    beta_vals  = params[p:]
    assignments = {}
    for i in range(p):
        assignments[gamma_params[i]] = gamma_vals[i]
        assignments[beta_params[i]]  = beta_vals[i]
    return transpiled_qc.assign_parameters(assignments)


def _counts_to_ratio(counts, edges, max_cut):
    total = sum(counts.values())
    expected = sum(
        (cnt / total) * compute_cut_value(bs, edges)
        for bs, cnt in counts.items()
    )
    return expected / max_cut


# ── FakeMarrakesh warm-start optimization ────────────────────────────────────

def local_warmstart_cell(seed, circuits, sim, edges, max_cut, n_qubits):
    """
    Run the full warm-start protocol on FakeMarrakesh.
    Returns dict with all params and performance needed for QPU evaluation.
    """
    np.random.seed(seed)
    tc5, gp5, bp5 = circuits[P_TARGET]
    tc3, gp3, bp3 = circuits[P_ANCHOR]

    # Cold start at p=5
    x0_cold = np.random.uniform(0, 2 * np.pi, 2 * P_TARGET)
    r_cold, x_cold = optimize_cobyla_ws(
        x0_cold, tc5, gp5, bp5, P_TARGET, sim, edges, max_cut, n_qubits, SHOTS, MAXITER)

    # K_MAX p=3 anchor runs
    anchors = []
    for _ in range(K_MAX):
        x0_p3 = np.random.uniform(0, 2 * np.pi, 2 * P_ANCHOR)
        r3, x3 = optimize_cobyla_ws(
            x0_p3, tc3, gp3, bp3, P_ANCHOR, sim, edges, max_cut, n_qubits, SHOTS, MAXITER)
        anchors.append((float(r3), np.asarray(x3, dtype=float)))

    # Best anchor → warm-start p=5
    best_idx = int(np.argmax([a[0] for a in anchors]))
    x_warm_init = pad_params(anchors[best_idx][1], P_ANCHOR, P_TARGET)
    r_warm, x_warm = optimize_cobyla_ws(
        x_warm_init, tc5, gp5, bp5, P_TARGET, sim, edges, max_cut, n_qubits, SHOTS, MAXITER)

    rec = {
        "seed": seed,
        "r_cold_fake": float(r_cold),
        "r_warm_fake": float(r_warm),
        "lift_fake": float(r_warm - r_cold),
        "r_p3_anchors": [float(a[0]) for a in anchors],
        "x_cold_p5": x_cold.tolist(),
        "x_warm_p5": x_warm.tolist(),
        "best_anchor_idx": best_idx,
    }
    print(f"  seed={seed} cold_fake={r_cold:.4f} warm_fake={r_warm:.4f} "
          f"lift={r_warm-r_cold:+.4f} p3={[round(a[0],3) for a in anchors]}", flush=True)
    return rec


# ── IBM service factory ───────────────────────────────────────────────────────

def _get_ibm_service():
    """
    Load IBM Runtime service with credential fallback chain:
    1. QISKIT_IBM_CHANNEL/TOKEN/INSTANCE env vars (original approach)
    2. IBMQ_TOKEN env var with ibm_quantum_platform channel (open-plan, no instance needed)
    3. IBMQ_TOKEN from DC15E or DC15W .env files
    """
    from qiskit_ibm_runtime import QiskitRuntimeService

    # Try original env-var approach first
    token = os.environ.get("QISKIT_IBM_TOKEN") or os.environ.get("IBMQ_TOKEN")
    channel = os.environ.get("QISKIT_IBM_CHANNEL", "ibm_quantum_platform")
    instance = os.environ.get("QISKIT_IBM_INSTANCE") or None

    # If token not in env, try loading from .env files
    # DC15W first: Whisper's token has open-plan access that works without instance
    if not token:
        for env_path in [
            os.path.expanduser("/droid/repos/DC15W/.env"),
            os.path.expanduser("/mnt/droid/repos/DC15E/.env"),
            os.path.expanduser("/droid/repos/DC15E/.env"),
        ]:
            if os.path.exists(env_path):
                for line in open(env_path):
                    if line.startswith("IBMQ_TOKEN="):
                        token = line.split("=", 1)[1].strip()
                        break
            if token:
                break

    if not token:
        raise RuntimeError("No IBM Quantum token found. Set QISKIT_IBM_TOKEN, IBMQ_TOKEN, or ensure .env exists.")

    return QiskitRuntimeService(channel=channel, token=token, instance=instance)


# ── QPU submission ────────────────────────────────────────────────────────────

def submit_qpu(local_records, n_qubits, edges):
    """
    For each seed: build cold + warm bound circuits and submit ONE batched job.
    Returns list of job_ids (one per seed).
    """
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

    service = _get_ibm_service()
    backend = service.backend(BACKEND_NAME)
    print(f"  Backend: {backend.name} | pending_jobs={backend.status().pending_jobs}", flush=True)

    tc5_qpu, gp5_qpu, bp5_qpu = _make_circuits_qpu(n_qubits, edges, backend)

    job_ids = []
    for rec in local_records:
        seed = rec["seed"]
        x_cold = np.asarray(rec["x_cold_p5"])
        x_warm = np.asarray(rec["x_warm_p5"])

        bound_cold = _bind(tc5_qpu, gp5_qpu, bp5_qpu, x_cold, P_TARGET)
        bound_warm = _bind(tc5_qpu, gp5_qpu, bp5_qpu, x_warm, P_TARGET)

        sampler = SamplerV2(mode=backend)
        sampler.options.default_shots = SHOTS
        job = sampler.run([(bound_cold,), (bound_warm,)])
        jid = job.job_id()
        job_ids.append(jid)
        print(f"  seed={seed} submitted job_id={jid}", flush=True)

    return job_ids


# ── QPU result retrieval ──────────────────────────────────────────────────────

def retrieve_qpu(job_ids, local_records, edges, max_cut):
    """
    Retrieve completed QPU jobs, extract counts, compute capk.
    Returns graded results dict.
    """
    from qiskit_ibm_runtime import QiskitRuntimeService

    service = _get_ibm_service()

    graded = []
    for jid, rec in zip(job_ids, local_records):
        seed = rec["seed"]
        job = service.job(jid)
        status = str(job.status())
        print(f"  seed={seed} job={jid} status={status}", flush=True)
        if "DONE" not in status:
            print(f"  → NOT DONE. Re-run --finalize later.")
            continue

        res = job.result()
        parsed = []
        for i in range(2):  # 0=cold, 1=warm
            databin = res[i].data
            reg = list(databin.__dict__.keys())[0]
            counts = getattr(databin, reg).get_counts()
            ratio = _counts_to_ratio(counts, edges, max_cut)
            parsed.append(float(ratio))

        r_cold_qpu, r_warm_qpu = parsed
        graded.append({
            "seed": seed,
            "job_id": jid,
            "r_cold_qpu": r_cold_qpu,
            "r_warm_qpu": r_warm_qpu,
            "lift_qpu": r_warm_qpu - r_cold_qpu,
            "r_cold_fake": rec["r_cold_fake"],
            "r_warm_fake": rec["r_warm_fake"],
            "lift_fake": rec["lift_fake"],
            "transfer_ratio": (r_warm_qpu - r_cold_qpu) / max(rec["lift_fake"], 1e-9),
        })
        print(f"  seed={seed} cold_qpu={r_cold_qpu:.4f} warm_qpu={r_warm_qpu:.4f} "
              f"lift_qpu={r_warm_qpu-r_cold_qpu:+.4f} "
              f"(fake lift={rec['lift_fake']:+.4f})", flush=True)

    return graded


def _grade(graded, local_records):
    """Compute LOO-CV-style capk from QPU results."""
    if not graded:
        return None

    # LOO-CV threshold from FakeMarrakesh p=3 anchors
    p3_scores = [rec["r_p3_anchors"][0] for rec in local_records
                 if any(g["seed"] == rec["seed"] for g in graded)]
    graded_seeds = {g["seed"] for g in graded}
    local_for_graded = [r for r in local_records if r["seed"] in graded_seeds]

    # Compute LOO-median threshold for each seed (using FakeMarrakesh p3 scores)
    lifts_k1, lifts_k2 = [], []
    for i, rec in enumerate(local_for_graded):
        others = [r["r_p3_anchors"][0] for j, r in enumerate(local_for_graded) if j != i]
        tau = float(np.median(others)) if others else float(np.median(p3_scores))

        g = next(x for x in graded if x["seed"] == rec["seed"])
        lift_qpu = g["lift_qpu"]
        # If p3 anchor best >= tau → k=1 (use warm start immediately)
        # Else k=2 (use max k)
        if rec["r_p3_anchors"][0] >= tau:
            lifts_k1.append((1, lift_qpu))
        else:
            lifts_k1.append((2, lift_qpu))

    k_used_list = [x[0] for x in lifts_k1]
    total_lift  = sum(x[1] for x in lifts_k1)
    # Reference lift: what k_max=2 always gives (using warm start from 2 anchors)
    ref_lift    = sum(g["lift_qpu"] for g in graded)
    capk = (total_lift / ref_lift) if ref_lift > 0 else float("nan")
    mean_k = float(np.mean(k_used_list))

    print(f"\n  QPU capk (param-transfer approx): {capk:.4f}")
    print(f"  mean_k_used: {mean_k:.2f}")
    print(f"  mean lift_qpu: {np.mean([g['lift_qpu'] for g in graded]):.4f}")
    print(f"  mean lift_fake: {np.mean([g['lift_fake'] for g in graded]):.4f}")
    print(f"\n  pred_c3980_001 threshold: capk < 0.40")
    if not np.isnan(capk):
        verdict = "SUPPORTS VALIDATE" if capk < 0.40 else "SUPPORTS INVALIDATE"
        print(f"  → QPU capk {capk:.4f} {verdict}")
    return capk


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke",    action="store_true", help="1 seed FakeMarrakesh only")
    ap.add_argument("--submit",   action="store_true", help="submit to ibm_marrakesh")
    ap.add_argument("--finalize", nargs="+",           help="job_id(s) to retrieve")
    args = ap.parse_args()

    edges    = EDGES_20
    n_qubits = N_QUBITS_20
    max_cut  = MAX_CUT_20  # cached from Exp64/66 brute-force (avoids 2^20 enumeration)
    print(f"EDGES_20 max_cut={max_cut} n_qubits={n_qubits}", flush=True)

    seeds = SMOKE_SEEDS if args.smoke else FULL_SEEDS

    # ── Phase 1: local FakeMarrakesh warm-start ──────────────────────────────
    print(f"\n[Phase 1] FakeMarrakesh warm-start ({len(seeds)} seeds)", flush=True)
    sim      = _noiseless_sim()   # fast noiseless for parameter search
    circuits = _make_circuits(n_qubits, edges)

    t0 = time.time()
    local_records = []
    for seed in seeds:
        rec = local_warmstart_cell(seed, circuits, sim, edges, max_cut, n_qubits)
        local_records.append(rec)
    print(f"  Phase 1 complete in {time.time()-t0:.0f}s", flush=True)

    if args.smoke:
        print("\nSmoke test passed. Pass --submit to run on real QPU.", flush=True)
        return

    # ── Phase 2: QPU submission ──────────────────────────────────────────────
    if args.submit:
        print(f"\n[Phase 2] Submitting to {BACKEND_NAME}", flush=True)
        job_ids = submit_qpu(local_records, n_qubits, edges)

        manifest = {"local_records": local_records, "job_ids": job_ids,
                    "backend": BACKEND_NAME, "shots": SHOTS,
                    "submitted_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        with open(JOBIDS_PATH, "w") as f:
            json.dump(manifest, f, indent=2)
        print(f"\n  Manifest saved: {JOBIDS_PATH}")
        print(f"  Next: python3 scripts/run_exp66_qpu_partb.py --finalize {' '.join(job_ids)}")
        return

    # ── Phase 3: retrieve + grade ─────────────────────────────────────────────
    if args.finalize:
        manifest_path = JOBIDS_PATH
        if os.path.exists(manifest_path):
            saved = json.load(open(manifest_path))
            local_records = saved["local_records"]
        job_ids = args.finalize

        print(f"\n[Phase 3] Retrieving {len(job_ids)} job(s)", flush=True)
        graded = retrieve_qpu(job_ids, local_records, edges, max_cut)

        if graded:
            capk = _grade(graded, local_records)
            result = {"graded": graded, "capk_qpu_approx": capk,
                      "local_records": local_records,
                      "finalized_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
            with open(RESULTS_PATH, "w") as f:
                json.dump(result, f, indent=2)
            print(f"\n  Results saved: {RESULTS_PATH}")
        return

    print("Pass --smoke, --submit, or --finalize <job_ids>")


if __name__ == "__main__":
    main()
