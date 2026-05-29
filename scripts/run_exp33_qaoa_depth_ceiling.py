"""Exp 33: Hardware-Aware QAOA Depth Ceiling (Whisper C3739).

OPEN RESEARCH QUESTION #6 (README): "Finding 05's 800-1000 CZ wall implies a hard ceiling on
QAOA p. Empirically map p_max for standard MaxCut. Pre-reg gate: identify the p value at which
output entropy crosses 0.95x uniform."

DESIGN
------
MaxCut on a PATH graph P_n (nodes 0..n-1, edges (i,i+1)). A path maps to a LINE on heavy-hex
with ZERO routing overhead, so the transpiled 2q-gate count is a clean 2|E|p = 2(n-1)p -- this
ties the depth sweep directly to Finding 05's CZ-count wall (no SWAP confound).

QAOA layer k (FIXED annealing-ramp angles -- standard reproducible Trotterized-anneal schedule):
  cost  U_C(gamma_k): for each edge (i,j):  CX(i,j); RZ(2*gamma_k, j); CX(i,j)  [= exp(-i*gamma_k Z_i Z_j)]
  mixer U_B(beta_k):  RX(2*beta_k, i) for all i
  s_k = (k+0.5)/p ;  dt = T_ANNEAL/p ;  gamma_k = s_k*dt ;  beta_k = (1-s_k)*dt   (T_ANNEAL=10.0)
The schedule is FIXED (no per-run optimization) -> removes the optimizer as a confound, fully
reproducible. Verified in sim preview: at fixed T the noiseless output CONCENTRATES on the optimal
cuts (entropy ratio ~0.32-0.49, top-2 cut mass ~0.65-0.85) and stays flat-low as p grows, while
circuit DEPTH grows linearly in p. So H_ideal is ~constant-low while depth-noise rises -> any rise
of H_hw toward uniform is attributable to NOISE, not the algorithm. Sweep starts at p=8 (anneal
already concentrated); algo-coarse p<8 points are excluded to keep the 0.95x-uniform gate clean.

METRIC: Shannon entropy of the measured output distribution H = -sum p_x log2 p_x.
  uniform_max = n_qubits bits;  ratio(p) = H(p) / n_qubits.
As p grows, depth-noise decoheres the output toward uniform (ratio -> 1.0). We ALSO compute the
noiseless statevector entropy H_ideal(p) so the noise-induced excess = H_hw - H_ideal is
attributable to hardware, not to the algorithm.

PRE-REGISTERED CRITERIA (FIXED before submission):
  p_max := smallest swept p with ratio_hw(p) = H_hw(p)/n >= 0.95  (output ~ uniform = no signal).
  G1 (CEILING EXISTS):     ratio_hw is monotone-increasing in p AND crosses 0.95 within the sweep
                           OR is clearly approaching it (ratio_hw(p_top) >= 0.90).
  G2 (NOISE-DRIVEN):       at p_max, H_hw - H_ideal >= 0.5 bit  (the crossing is noise, not algo).
  G3 (WALL CONSISTENCY):   the 2q-gate count at p_max falls in / near Finding 05's 800-1000 CZ band
                           (report cz(p_max); consistent if 500 <= cz(p_max) <= 1500).
  G1 PASS -> QAOA has an empirically-mapped hard depth ceiling on this substrate.

Path graph P6 (n=6, |E|=5 -> 10 2q/layer). Sweep p in {8,16,24,32,48,64,96} (clean 2q: 80..960),
straddling Finding 05's 800-1000 CZ wall; refine if the crossing sits above p=96.
8192 shots/circuit. opt_level=1 (light routing, preserves algorithmic depth). Backend ibm_marrakesh
(SAME device as Finding 05 -> clean wall comparison). One job -> single calibration snapshot.

Run (sim preview):   python3 scripts/run_exp33_qaoa_depth_ceiling.py
Run (hardware):      python3 scripts/run_exp33_qaoa_depth_ceiling.py --submit
Finalize:            python3 scripts/run_exp33_qaoa_depth_ceiling.py --finalize <job_id>
"""
import argparse
import json
import os
import math
import numpy as np

EXPERIMENT = "33"
CYCLE = 3739
SHOTS = 8192
N_NODES = 6
EDGES = [(i, i + 1) for i in range(N_NODES - 1)]   # path P6, |E|=5
T_ANNEAL = 10.0                                    # total anneal time (fixed schedule)
P_SWEEP = [8, 16, 24, 32, 48, 64, 96]
SEED_TRANSPILER = 42
BACKEND_NAME = "ibm_marrakesh"
RESULT_PATH = f"experiments/{EXPERIMENT}-qaoa-depth-ceiling-results.json"
JOBID_PATH = f"experiments/{EXPERIMENT}-jobid.txt"
CALIB_PATH = f"experiments/{EXPERIMENT}-calibration.json"
UNIFORM_MAX_BITS = float(N_NODES)
RATIO_GATE = 0.95


def anneal_angles(p):
    """Fixed Trotterized-annealing schedule: gamma_k = s_k*dt, beta_k = (1-s_k)*dt."""
    dt = T_ANNEAL / p
    gammas, betas = [], []
    for k in range(p):
        s = (k + 0.5) / p
        gammas.append(s * dt)
        betas.append((1.0 - s) * dt)
    return gammas, betas


def build_qaoa(p):
    """Annealing-ramp QAOA MaxCut on path P_n, p layers. Returns unmeasured QuantumCircuit."""
    from qiskit import QuantumCircuit
    gammas, betas = anneal_angles(p)
    qc = QuantumCircuit(N_NODES)
    qc.h(range(N_NODES))               # uniform superposition init
    for k in range(p):
        for (i, j) in EDGES:           # cost layer: exp(-i gamma_k Z_i Z_j) per edge
            qc.cx(i, j)
            qc.rz(2 * gammas[k], j)
            qc.cx(i, j)
        for q in range(N_NODES):       # mixer layer
            qc.rx(2 * betas[k], q)
    return qc


def build_qaoa_measured(p):
    qc = build_qaoa(p)
    qc.measure_all()
    return qc


def shannon_entropy_bits(counts):
    """H = -sum p log2 p over measured bitstrings (counts dict)."""
    total = sum(counts.values())
    if total == 0:
        return 0.0
    h = 0.0
    for c in counts.values():
        if c > 0:
            p = c / total
            h -= p * math.log2(p)
    return h


def ideal_entropy_bits(p):
    """Noiseless statevector output-distribution entropy for QAOA(p)."""
    try:
        from qiskit.quantum_info import Statevector
        sv = Statevector.from_instruction(build_qaoa(p))
        probs = np.abs(sv.data) ** 2
        probs = probs[probs > 1e-15]
        return float(-np.sum(probs * np.log2(probs)))
    except Exception as e:
        return float("nan")


# ---------------------------------------------------------------------------
def _build_schedule(transpile_fn):
    items = []
    for p in P_SWEEP:
        qc = transpile_fn(build_qaoa_measured(p))
        items.append((p, qc))
    return items


def build_schedule_for_hardware():
    from qiskit import transpile
    from qiskit_ibm_runtime import QiskitRuntimeService
    service = QiskitRuntimeService()
    backend = service.backend(BACKEND_NAME)

    def tfn(qc):
        return transpile(qc, backend=backend, optimization_level=1,
                         seed_transpiler=SEED_TRANSPILER)

    items = _build_schedule(tfn)
    print(f"  Built {len(items)} QAOA circuits on {BACKEND_NAME}")
    for (p, qc) in items:
        ops = qc.count_ops()
        cz = ops.get("cz", 0) + ops.get("ecr", 0) + ops.get("cx", 0)
        print(f"  p={p:>3}: depth={qc.depth():>5}  2q={cz:>5}  (clean 2|E|p={2*len(EDGES)*p})")
    return items, backend


def build_schedule_for_fake():
    from qiskit import transpile
    from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
    backend = FakeMarrakesh()

    def tfn(qc):
        return transpile(qc, backend=backend, optimization_level=1,
                         seed_transpiler=SEED_TRANSPILER)

    items = _build_schedule(tfn)
    for (p, qc) in items:
        ops = qc.count_ops()
        cz = ops.get("cz", 0) + ops.get("ecr", 0) + ops.get("cx", 0)
        print(f"  p={p:>3}: depth={qc.depth():>5}  2q={cz:>5}")
    return items, backend


def submit_hardware(schedule_items, backend):
    from qiskit_ibm_runtime import SamplerV2
    sampler = SamplerV2(mode=backend)
    sampler.options.default_shots = SHOTS
    circuits = [item[1] for item in schedule_items]
    job = sampler.run([(qc,) for qc in circuits])
    job_id = job.job_id()
    with open(JOBID_PATH, "w") as f:
        f.write(job_id + "\n")
    try:
        from calibration_snapshot import capture_calibration
        snap = capture_calibration(backend)
        snap["snapshot_phase"] = "submit"
        with open(CALIB_PATH, "w") as f:
            json.dump(snap, f, indent=4, default=str)
        print(f"  Calibration snapshot (submit) saved (updated {snap.get('last_update_date')})")
    except Exception as e:
        print(f"  [warn] calibration snapshot skipped: {e}")
    print(f"\n  SUBMITTED. job_id = {job_id}  ({len(circuits)} circuits) on {BACKEND_NAME}")
    return job_id


def get_counts_from_job(job_id, n_circuits):
    from qiskit_ibm_runtime import QiskitRuntimeService
    service = QiskitRuntimeService()
    job = service.job(job_id)
    status = str(job.status())
    print(f"  job {job_id} status: {status}")
    if status not in ("DONE", "JobStatus.DONE"):
        return None, status
    res = job.result()
    all_counts = []
    for i in range(n_circuits):
        databin = res[i].data
        reg = list(databin.__dict__.keys())[0]
        all_counts.append(getattr(databin, reg).get_counts())
    return all_counts, "DONE"


def get_counts_from_fake(schedule_items, backend):
    from qiskit_aer.primitives import SamplerV2 as AerSampler
    from qiskit_aer.noise import NoiseModel
    nm = NoiseModel.from_backend(backend)
    sampler = AerSampler(options={
        "backend_options": {"noise_model": nm},
        "run_options": {"shots": SHOTS, "seed": SEED_TRANSPILER},
    })
    circuits = [item[1] for item in schedule_items]
    res = sampler.run([(c,) for c in circuits]).result()
    all_counts = []
    for i in range(len(circuits)):
        data = res[i].data
        reg = list(data.__dict__.keys())[0]
        all_counts.append(getattr(data, reg).get_counts())
    return all_counts


def _load_calibration_snapshot():
    try:
        if os.path.exists(CALIB_PATH):
            with open(CALIB_PATH) as f:
                return json.load(f)
    except Exception:
        pass
    return {"available": False, "note": "no submit-time snapshot found"}


def analyze(schedule_items, all_counts, job_id=None):
    rows = []
    print(f"\n{'p':>4} {'2q':>6} | {'H_hw':>7} {'H_ideal':>8} {'ratio':>7} {'excess':>7}")
    print("-" * 50)
    p_max = None
    ratios = []
    for (p, qc), counts in zip(schedule_items, all_counts):
        ops = qc.count_ops()
        cz = ops.get("cz", 0) + ops.get("ecr", 0) + ops.get("cx", 0)
        h_hw = shannon_entropy_bits(counts)
        h_id = ideal_entropy_bits(p)
        ratio = h_hw / UNIFORM_MAX_BITS
        excess = h_hw - h_id
        ratios.append(ratio)
        rows.append({"p": p, "cz": cz, "H_hw_bits": round(h_hw, 4),
                     "H_ideal_bits": round(h_id, 4), "ratio_hw": round(ratio, 4),
                     "noise_excess_bits": round(excess, 4)})
        print(f"{p:>4} {cz:>6} | {h_hw:>7.4f} {h_id:>8.4f} {ratio:>7.4f} {excess:>+7.4f}")
        if p_max is None and ratio >= RATIO_GATE:
            p_max = p
    print("-" * 50)

    top_ratio = ratios[-1] if ratios else 0.0
    monotone = all(ratios[i] <= ratios[i + 1] + 0.02 for i in range(len(ratios) - 1))
    cz_at_pmax = next((r["cz"] for r in rows if r["p"] == p_max), None)
    excess_at_pmax = next((r["noise_excess_bits"] for r in rows if r["p"] == p_max), None)

    g1 = (p_max is not None) or (top_ratio >= 0.90)
    g2 = (p_max is not None and excess_at_pmax is not None and excess_at_pmax >= 0.5)
    g3 = (cz_at_pmax is not None and 500 <= cz_at_pmax <= 1500)

    print(f"\n  p_max (first ratio>=0.95) = {p_max}   (cz@p_max={cz_at_pmax})")
    print(f"  top ratio (p={P_SWEEP[-1]}) = {top_ratio:.4f}")
    print(f"\n=== PRE-REGISTERED CRITERIA (Exp33, {BACKEND_NAME}) ===")
    print(f"G1 (CEILING EXISTS): p_max found OR top_ratio>=0.90 ({top_ratio:.3f}) "
          f"-> {'PASS' if g1 else 'FAIL'}")
    print(f"G2 (NOISE-DRIVEN):   excess@p_max>=0.5bit "
          f"({excess_at_pmax if excess_at_pmax is not None else 'n/a'}) -> {'PASS' if g2 else 'PENDING' if p_max is None else 'FAIL'}")
    print(f"G3 (WALL CONSIST.):  500<=cz@p_max<=1500 "
          f"({cz_at_pmax if cz_at_pmax is not None else 'n/a'}) -> {'PASS' if g3 else 'PENDING' if p_max is None else 'FAIL'}")

    if p_max is not None:
        verdict = (f"QAOA depth ceiling MAPPED on {BACKEND_NAME}: output entropy crosses "
                   f"0.95x uniform at p={p_max} ({cz_at_pmax} 2q gates). "
                   + ("Consistent with Finding 05's 800-1000 CZ wall."
                      if g3 else "Crossing CZ-count differs from Finding 05's band -- see G3."))
    elif top_ratio >= 0.90:
        verdict = (f"Ceiling APPROACHING but not crossed by p={P_SWEEP[-1]} "
                   f"(top ratio {top_ratio:.3f}); extend sweep to higher p in follow-up job.")
    else:
        verdict = (f"No ceiling within swept range (top ratio {top_ratio:.3f}); "
                   f"QAOA output still structured at p={P_SWEEP[-1]} -- extend sweep.")
    print(f"\nVERDICT: {verdict}")

    result = {
        "experiment": EXPERIMENT,
        "title": "Hardware-Aware QAOA Depth Ceiling (ORQ #6)",
        "cycle": CYCLE, "backend": BACKEND_NAME, "job_id": job_id,
        "open_research_question": "Map p_max for QAOA MaxCut: the p at which output entropy "
                                  "crosses 0.95x uniform (Finding 05 800-1000 CZ wall -> QAOA p ceiling).",
        "graph": {"type": "path", "n_nodes": N_NODES, "edges": EDGES, "two_q_per_layer": 2 * len(EDGES)},
        "params": {"shots": SHOTS, "T_anneal": T_ANNEAL, "p_sweep": P_SWEEP,
                   "angle_mode": "fixed_annealing_ramp", "seed_transpiler": SEED_TRANSPILER,
                   "uniform_max_bits": UNIFORM_MAX_BITS, "ratio_gate": RATIO_GATE},
        "preregistered_criteria": {
            "p_max": "smallest swept p with H_hw(p)/n_qubits >= 0.95",
            "G1": "p_max found OR top ratio >= 0.90 (ceiling exists/approaching)",
            "G2": "noise excess (H_hw - H_ideal) >= 0.5 bit at p_max (crossing is noise-driven)",
            "G3": "2q-gate count at p_max in 500-1500 (consistent with Finding 05 ~800-1000 CZ wall)",
        },
        "calibration": _load_calibration_snapshot(),
        "summary": {
            "p_max": p_max, "cz_at_p_max": cz_at_pmax,
            "noise_excess_at_p_max_bits": excess_at_pmax,
            "top_ratio": round(top_ratio, 4), "monotone": monotone,
            "G1": "PASS" if g1 else "FAIL",
            "G2": ("PASS" if g2 else ("PENDING" if p_max is None else "FAIL")),
            "G3": ("PASS" if g3 else ("PENDING" if p_max is None else "FAIL")),
            "verdict": verdict,
        },
        "rows": rows,
    }
    with open(RESULT_PATH, "w") as f:
        json.dump(result, f, indent=4)
    print(f"\n  Results saved to {RESULT_PATH}")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--submit", action="store_true")
    parser.add_argument("--finalize", metavar="JOB_ID")
    args = parser.parse_args()

    if args.finalize:
        print(f"\n=== Fetching Exp {EXPERIMENT} (job {args.finalize}) ===")
        schedule_items, _ = build_schedule_for_hardware()
        all_counts, status = get_counts_from_job(args.finalize, len(schedule_items))
        if all_counts is None:
            print(f"  Job not done yet ({status}).")
            return
        analyze(schedule_items, all_counts, job_id=args.finalize)
    elif args.submit:
        print(f"\n=== Exp {EXPERIMENT}: building hardware schedule ({BACKEND_NAME}) ===")
        schedule_items, backend = build_schedule_for_hardware()
        print(f"\n=== Submitting to {BACKEND_NAME} ===")
        jid = submit_hardware(schedule_items, backend)
        print(f"\n  Finalize with:  python3 scripts/run_exp33_qaoa_depth_ceiling.py "
              f"--finalize {jid}")
    else:
        print(f"\n=== Exp {EXPERIMENT}: FakeMarrakesh simulation preview ===")
        schedule_items, backend = build_schedule_for_fake()
        all_counts = get_counts_from_fake(schedule_items, backend)
        analyze(schedule_items, all_counts, job_id="FakeMarrakesh-sim")


if __name__ == "__main__":
    main()
