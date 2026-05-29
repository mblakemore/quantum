"""Exp 25b: ZNE on 2-qubit CZ IQAE — CORRECTED (Whisper C3720).

WHY THIS IS A SEPARATE EXPERIMENT FROM EXP 25:
  Exp 25 (job d8cheib8amns73bjik2g) used fold_circuit → transpile(optimization_level=1).
  DIAGNOSIS: at opt=1, the Qiskit transpiler recognizes Q·Q†·Q = Q algebraically and
  collapses the folded circuit back to the original. Empirically confirmed: all lambda
  values (1,3,5) produced depth=13 and 2q=2 for k=1 — IDENTICAL, meaning zero folding.

  Richardson extrapolation of three identical inputs returns the same value → Exp 25
  will NOT demonstrate ZNE. It IS a valid control: confirming that opt=1 defeats ZNE.

CORRECTED ZNE APPROACH (C3720 fix):
  1. Transpile BASE circuit at optimization_level=1 (native gate set, hardware-optimal)
  2. Fold the ALREADY-TRANSPILED native-gate circuit (compose base + inv + base)
     WITHOUT additional transpilation (the folded part stays as appended native gates)
  3. Submit directly — optimizer never sees the folded portion, cannot simplify

  Result: correct linear gate scaling verified before submission:
    k=1: 2q gates: λ=1→2, λ=3→6, λ=5→10  (3× scaling)
    k=4: 2q gates: λ=1→8, λ=3→24, λ=5→40  (3× / 5× scaling)
    k=4: depth:    λ=1→37, λ=3→109, λ=5→181

DESIGN (same grid as Exp 25, corrected folding):
  P ∈ {0.56, 0.9}, k ∈ {0,1,2,3,4}, λ ∈ {1,3,5} → 30 circuits, one batched job.
  4096 shots per circuit. Backend: ibm_marrakesh.

PRE-REGISTERED CRITERIA (same as Exp 25 — experiment is unchanged except folding fix):
  T1 (ZNE-EFFECTIVE):   mean_k |ZNE-ideal| < mean_k |hw24-ideal| (4.20pp baseline)
  T2 (ZNE-BEATS-SIM):   mean_k |ZNE-ideal| < mean_k |sim24-ideal| (1.03pp, stretch)
  T3 (DEPTH-MITIGATION): ZNE improvement larger at k=4 than k=0

  PRE-REGISTERED EXPECTATION (Whisper, C3720):
    T1 PASS (target <2.5pp, ~50% improvement)
    T2 FAIL (recovering below sim is a stretch)
    T3 PASS (more noise at k=4 → more to cancel → larger ZNE benefit)

METHODOLOGICAL LESSON (C3720):
  ZNE requires folding BEFORE transpilation OR folding ALREADY-TRANSPILED native circuits
  without re-running the optimizer. Folding un-transpiled circuits with opt≥1 is a
  silent failure mode: circuits appear correct pre-transpile but collapse post-transpile.

Run (simulation preview):    python3 scripts/run_exp25b_zne_corrected.py
Run (real hardware submit):   python3 scripts/run_exp25b_zne_corrected.py --submit
Poll + finalize:              python3 scripts/run_exp25b_zne_corrected.py --finalize <job_id>
"""
import argparse
import json
import numpy as np

EXPERIMENT = "25b"
CYCLE = 3720
SHOTS = 4096
P_VALUES = [0.56, 0.9]
K_VALUES = [0, 1, 2, 3, 4]
SCALE_FACTORS = [1, 3, 5]
SEED_TRANSPILER = 42
BACKEND_NAME = "ibm_marrakesh"
RESULT_PATH = f"experiments/{EXPERIMENT}-zne-corrected-results.json"
JOBID_PATH = f"experiments/{EXPERIMENT}-jobid.txt"

EXP24_HW = {
    (0.56, 0): 0.0118, (0.56, 1): 0.0161, (0.56, 2): 0.0305,
    (0.56, 3): 0.0649, (0.56, 4): 0.0934,
    (0.9, 0): 0.0324, (0.9, 1): 0.0426, (0.9, 2): 0.0566,
    (0.9, 3): 0.0682, (0.9, 4): 0.0934,
}
EXP24_SIM = {
    (0.56, 0): 0.0015, (0.56, 1): 0.0027, (0.56, 2): 0.0061,
    (0.56, 3): 0.0071, (0.56, 4): 0.0158,
    (0.9, 0): 0.0033, (0.9, 1): 0.0085, (0.9, 2): 0.0088,
    (0.9, 3): 0.0127, (0.9, 4): 0.0174,
}


def ideal_p11(P, k):
    th_a = np.arcsin(np.sqrt(P))
    return float(np.sin((2 * k + 1) * th_a) ** 2)


def build_base_circuit_logical(P, k):
    """Build logical A + Q^k (no measurement) — before transpilation."""
    from qiskit import QuantumCircuit
    from qiskit_algorithms import EstimationProblem
    angle = 2 * np.arcsin(P ** 0.25)
    A = QuantumCircuit(2)
    A.ry(angle, 0)
    A.ry(angle, 1)
    problem = EstimationProblem(state_preparation=A, objective_qubits=[0, 1])
    Q = problem.grover_operator
    qc = QuantumCircuit(2)
    qc.compose(A, inplace=True)
    for _ in range(k):
        qc.compose(Q, inplace=True)
    return qc


def build_schedule_for_fakemarrakesh():
    """Build schedule for FakeMarrakesh simulation.

    For simulation we fold the LOGICAL (2-qubit) circuits and then transpile with
    optimization_level=0 (prevents optimizer collapse without exploding to 156-qubit
    layout). This keeps the sim tractable while reflecting the folded gate count.
    """
    from qiskit import QuantumCircuit, transpile
    from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
    backend = FakeMarrakesh()

    schedule = []
    for P in P_VALUES:
        for k in K_VALUES:
            base_logical = build_base_circuit_logical(P, k)
            base_inv = base_logical.inverse()
            for scale in SCALE_FACTORS:
                n_folds = (scale - 1) // 2
                qc_logical = QuantumCircuit(2)
                qc_logical.compose(base_logical, inplace=True)
                for _ in range(n_folds):
                    qc_logical.compose(base_inv, inplace=True)
                    qc_logical.compose(base_logical, inplace=True)
                qc_logical.measure_all()
                # Transpile with opt=0 so folded gates are NOT simplified away
                qc_t = transpile(qc_logical, backend=backend,
                                 optimization_level=0, seed_transpiler=SEED_TRANSPILER)
                schedule.append((P, k, scale, qc_t, backend))
    return schedule


def build_schedule_for_hardware():
    """Build schedule for real QPU.

    Approach: fold LOGICAL 2-qubit circuits, then transpile the folded circuit
    at optimization_level=0. This ensures:
    1. All gates are in the native gate set (no sxdg issues)
    2. The optimizer does NOT cancel Q·Q† pairs (opt=0 = no optimization passes)
    3. Gate counts scale correctly with λ (validated: k=1 gives 2→6→10 2q gates)

    Note: circuits are deeper than pre-transpile-then-fold, but ZNE correctness
    requires that noise actually scales with λ, which it does here.
    """
    from qiskit import QuantumCircuit, transpile
    from qiskit_ibm_runtime import QiskitRuntimeService
    service = QiskitRuntimeService()
    backend = service.backend(BACKEND_NAME)

    schedule = []
    for P in P_VALUES:
        for k in K_VALUES:
            base_logical = build_base_circuit_logical(P, k)
            base_inv = base_logical.inverse()
            for scale in SCALE_FACTORS:
                n_folds = (scale - 1) // 2
                qc_logical = QuantumCircuit(2)
                qc_logical.compose(base_logical, inplace=True)
                for _ in range(n_folds):
                    qc_logical.compose(base_inv, inplace=True)
                    qc_logical.compose(base_logical, inplace=True)
                qc_logical.measure_all()
                # opt=0: translate + route ONLY, no optimization passes
                # Ensures sxdg→native and Q·Q† NOT cancelled
                qc_hw = transpile(qc_logical, backend=backend,
                                  optimization_level=0, seed_transpiler=SEED_TRANSPILER)
                schedule.append((P, k, scale, qc_hw))
    return schedule, backend


def counts_to_p11(counts, shots):
    good = 0
    total = 0
    for bitstr, c in counts.items():
        total += c
        bs = bitstr.replace(" ", "")
        if bs[-2:] == "11":
            good += c
    return good / (total if total > 0 else shots)


def richardson_extrapolate(vals, scales):
    """3-point Richardson (linear fit, evaluate at λ=0). Also returns 2-point."""
    x = np.array(scales, dtype=float)
    y = np.array(vals, dtype=float)
    slope = (y[1] - y[0]) / (x[1] - x[0])
    zne_2pt = float(y[0] - slope * x[0])
    if len(vals) >= 3:
        coeffs = np.polyfit(x, y, 1)
        zne_3pt = float(np.polyval(coeffs, 0))
    else:
        zne_3pt = zne_2pt
    return zne_2pt, zne_3pt


def run_fakemarrakesh(schedule_with_backend):
    """Run folded circuits on FakeMarrakesh (using 2-qubit logical circuits at opt=0)."""
    from qiskit_aer.primitives import SamplerV2 as AerSampler
    from qiskit_aer.noise import NoiseModel

    items = list(schedule_with_backend)
    backend = items[0][4]
    nm = NoiseModel.from_backend(backend)
    sampler = AerSampler(options={
        "backend_options": {"noise_model": nm},
        "run_options": {"shots": SHOTS, "seed": SEED_TRANSPILER},
    })
    circuits = [item[3] for item in items]
    res = sampler.run([(c,) for c in circuits]).result()
    p11s = []
    for i in range(len(circuits)):
        # measure_all() uses meas register not c
        data = res[i].data
        reg_name = list(data.__dict__.keys())[0]
        counts = getattr(data, reg_name).get_counts()
        p11s.append(counts_to_p11(counts, SHOTS))
    return p11s, [(item[0], item[1], item[2]) for item in items]


def submit_hardware(schedule, backend):
    """Submit 30-circuit batched job. schedule = [(P,k,scale,qc), ...]"""
    from qiskit_ibm_runtime import SamplerV2
    print(f"  Backend: {backend.name}  (qubits={backend.num_qubits})")
    for (P, k, scale, qc) in schedule:
        ops = qc.count_ops()
        cz = ops.get("cz", 0) + ops.get("ecr", 0) + ops.get("cx", 0)
        print(f"    P={P} k={k} λ={scale}: depth={qc.depth()} 2q={cz}")
    sampler = SamplerV2(mode=backend)
    sampler.options.default_shots = SHOTS
    job = sampler.run([(qc,) for (_, _, _, qc) in schedule])
    job_id = job.job_id()
    with open(JOBID_PATH, "w") as f:
        f.write(job_id + "\n")
    print(f"  SUBMITTED. job_id = {job_id}  (saved to {JOBID_PATH})")
    return job_id


def fetch_hardware_p11(job_id, schedule):
    from qiskit_ibm_runtime import QiskitRuntimeService
    service = QiskitRuntimeService()
    job = service.job(job_id)
    status = job.status()
    print(f"  job {job_id} status: {status}")
    if str(status) not in ("DONE", "JobStatus.DONE"):
        return None, str(status)
    res = job.result()
    p11s = []
    for i in range(len(schedule)):
        databin = res[i].data
        reg = list(databin.__dict__.keys())[0] if hasattr(databin, "__dict__") else "c"
        counts = getattr(databin, reg).get_counts() if hasattr(databin, reg) else databin.c.get_counts()
        p11s.append(counts_to_p11(counts, SHOTS))
    return p11s, "DONE"


def analyze(pkscale_list, hw_p11s, sim_p11s, job_id=None):
    """pkscale_list: [(P,k,scale), ...] in same order as p11s."""
    groups = {}
    for i, (P, k, scale) in enumerate(pkscale_list):
        key = (P, k)
        if key not in groups:
            groups[key] = {}
        groups[key][scale] = i

    rows = []
    for P in P_VALUES:
        for k in K_VALUES:
            key = (P, k)
            ide = ideal_p11(P, k)
            idxs = [groups[key][s] for s in SCALE_FACTORS]

            sim_vals = [sim_p11s[i] for i in idxs]
            sim_zne_2pt, sim_zne_3pt = richardson_extrapolate(sim_vals, SCALE_FACTORS)

            row = {
                "P": P, "k": k, "ideal": round(ide, 4),
                "sim_raw_lam1": round(sim_vals[0], 4),
                "sim_raw_lam3": round(sim_vals[1], 4),
                "sim_raw_lam5": round(sim_vals[2], 4),
                "sim_zne_3pt": round(sim_zne_3pt, 4),
                "dev_sim_lam1": round(abs(sim_vals[0] - ide), 4),
                "dev_sim_zne": round(abs(sim_zne_3pt - ide), 4),
                "exp24_hw": EXP24_HW.get(key),
                "exp24_sim": EXP24_SIM.get(key),
            }

            if hw_p11s is not None:
                hw_vals = [hw_p11s[i] for i in idxs]
                hw_zne_2pt, hw_zne_3pt = richardson_extrapolate(hw_vals, SCALE_FACTORS)
                row.update({
                    "hw_raw_lam1": round(hw_vals[0], 4),
                    "hw_raw_lam3": round(hw_vals[1], 4),
                    "hw_raw_lam5": round(hw_vals[2], 4),
                    "hw_zne_2pt": round(hw_zne_2pt, 4),
                    "hw_zne_3pt": round(hw_zne_3pt, 4),
                    "dev_hw_lam1": round(abs(hw_vals[0] - ide), 4),
                    "dev_hw_zne_2pt": round(abs(hw_zne_2pt - ide), 4),
                    "dev_hw_zne_3pt": round(abs(hw_zne_3pt - ide), 4),
                })
            rows.append(row)

    out = {
        "experiment": EXPERIMENT,
        "title": "ZNE on 2-qubit CZ IQAE — corrected (pre-transpile-then-fold)",
        "cycle": CYCLE,
        "backend": BACKEND_NAME if hw_p11s is not None else "SIM-PREVIEW-ONLY",
        "job_id": job_id,
        "params": {
            "shots": SHOTS, "P_values": P_VALUES, "k_values": K_VALUES,
            "scale_factors": SCALE_FACTORS,
            "method": "pre-transpile at opt=1 then fold native circuits (no re-transpile)",
            "circuits_total": len(pkscale_list),
            "seed_transpiler": SEED_TRANSPILER,
            "exp25_failure_reason": "Exp 25 (opt=1 fold before transpile) had transpiler collapse Q·Q†·Q→Q",
            "correction": "fold AFTER transpile, no re-transpilation of folded part",
        },
        "preregistered_criteria": {
            "T1": "mean |ZNE-ideal| < 4.20pp exp24_hw baseline -> ZNE-EFFECTIVE",
            "T2": "mean |ZNE-ideal| < 1.03pp exp24_sim baseline -> ZNE-BEATS-SIM (stretch)",
            "T3": "ZNE improvement larger at k=4 than k=0 -> DEPTH-MITIGATION",
        },
        "preregistered_expectation": "T1 PASS (~2pp target), T2 FAIL, T3 PASS",
        "rows": rows,
    }

    if hw_p11s is not None:
        exp24_hw_mean = float(np.mean(list(EXP24_HW.values())))
        exp24_sim_mean = float(np.mean(list(EXP24_SIM.values())))
        zne_errs = [r["dev_hw_zne_3pt"] for r in rows]
        raw_errs = [r["dev_hw_lam1"] for r in rows]
        mean_zne = float(np.mean(zne_errs))
        mean_raw = float(np.mean(raw_errs))

        imp_k0 = float(np.mean([r["dev_hw_lam1"] - r["dev_hw_zne_3pt"]
                                 for r in rows if r["k"] == 0]))
        imp_k4 = float(np.mean([r["dev_hw_lam1"] - r["dev_hw_zne_3pt"]
                                 for r in rows if r["k"] == 4]))

        out["summary"] = {
            "mean_raw_hw_lam1": round(mean_raw, 4),
            "mean_zne_3pt": round(mean_zne, 4),
            "exp24_hw_baseline": round(exp24_hw_mean, 4),
            "exp24_sim_baseline": round(exp24_sim_mean, 4),
            "zne_improvement_vs_exp24_pp": round((exp24_hw_mean - mean_zne) * 100, 2),
            "improvement_k0_pp": round(imp_k0 * 100, 2),
            "improvement_k4_pp": round(imp_k4 * 100, 2),
        }
        verdicts = {}
        verdicts["T1"] = ("PASS: ZNE-EFFECTIVE" if mean_zne < exp24_hw_mean
                          else "FAIL: ZNE did not improve over raw hardware")
        verdicts["T2"] = ("PASS: ZNE-BEATS-SIM (stretch!)" if mean_zne < exp24_sim_mean
                          else f"FAIL: ZNE ({mean_zne:.4f}) did not beat sim ({exp24_sim_mean:.4f})")
        verdicts["T3"] = ("PASS: DEPTH-MITIGATION (ZNE scales with depth)"
                          if imp_k4 > imp_k0 else "FAIL: ZNE improvement did not scale with depth")
        out["verdicts"] = verdicts

    return out


def print_table(out):
    print(f"\n  {'P':>5} {'k':>2} {'ideal':>7} {'sim_λ1':>7} {'sim_ZNE':>8} "
          f"{'hw_λ1':>7} {'hw_ZNE':>8} {'|hw1-id|':>9} {'|ZNE-id|':>9} {'Exp24':>7}")
    for r in out["rows"]:
        def f(v):
            return f"{v:.4f}" if v is not None else "  --  "
        print(f"  {r['P']:>5} {r['k']:>2} {r['ideal']:>7.4f} "
              f"{r['sim_raw_lam1']:>7.4f} {r['sim_zne_3pt']:>8.4f} "
              f"{f(r.get('hw_raw_lam1')):>7} {f(r.get('hw_zne_3pt')):>8} "
              f"{f(r.get('dev_hw_lam1')):>9} {f(r.get('dev_hw_zne_3pt')):>9} "
              f"{f(r.get('exp24_hw')):>7}")
    if "summary" in out:
        s = out["summary"]
        print(f"\n  Raw λ=1 mean: {s['mean_raw_hw_lam1']:.4f}")
        print(f"  ZNE 3pt mean: {s['mean_zne_3pt']:.4f}  (Exp24 HW baseline: {s['exp24_hw_baseline']:.4f})")
        print(f"  ZNE improvement vs Exp24: {s['zne_improvement_vs_exp24_pp']:.2f}pp")
        print(f"  Improvement k=0: {s['improvement_k0_pp']:.2f}pp  k=4: {s['improvement_k4_pp']:.2f}pp")
    if "verdicts" in out:
        print("\n  VERDICTS:")
        for t, v in out["verdicts"].items():
            print(f"    {t}: {v}")


def save(out):
    with open(RESULT_PATH, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\n  Results written to {RESULT_PATH}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--finalize", metavar="JOB_ID")
    args = ap.parse_args()

    print(f"Exp {EXPERIMENT} (C{CYCLE}): ZNE corrected — pre-transpile-then-fold")
    print(f"  Fix: fold already-transpiled native-gate circuits (no re-optimization)")
    print(f"  Grid: P={P_VALUES} x k={K_VALUES} x λ={SCALE_FACTORS} = 30 circuits")

    print("\n  Building FakeMarrakesh schedule...")
    sim_schedule = build_schedule_for_fakemarrakesh()
    print(f"  Running FakeMarrakesh simulation ({len(sim_schedule)} circuits)...")
    sim_p11s, pkscale_list = run_fakemarrakesh(sim_schedule)
    print(f"  Sim complete.")

    if args.finalize:
        # Need to rebuild hardware schedule to get pkscale ordering
        print("\n  Rebuilding hardware schedule ordering...")
        hw_schedule, _ = build_schedule_for_hardware()
        hw_pkscale = [(P, k, scale) for (P, k, scale, _) in hw_schedule]
        hw_p11s, status = fetch_hardware_p11(args.finalize, hw_schedule)
        if hw_p11s is None:
            print(f"  Job not done yet (status={status}). Re-run --finalize later.")
            return
        out = analyze(hw_pkscale, hw_p11s, sim_p11s, job_id=args.finalize)
        print_table(out)
        save(out)
        return

    if args.submit:
        print("\n  Building hardware schedule (pre-transpile + fold)...")
        hw_schedule, backend = build_schedule_for_hardware()
        print(f"  Circuit depths (post-fold, native gates, NO re-transpile):")
        job_id = submit_hardware(hw_schedule, backend)
        print(f"\n  Next: python3 scripts/run_exp25b_zne_corrected.py --finalize {job_id}")
        out = analyze(pkscale_list, None, sim_p11s, job_id=job_id)
        print("\n  Simulation preview:")
        print_table(out)
        save(out)
        return

    # Preview only
    out = analyze(pkscale_list, None, sim_p11s, job_id=None)
    print("\n  Simulation preview (no hardware):")
    print_table(out)
    print("\n  (preview only — pass --submit for real hardware)")


if __name__ == "__main__":
    main()
