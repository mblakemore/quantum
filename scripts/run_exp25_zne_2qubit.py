"""Exp 25: Zero-Noise Extrapolation (ZNE) on 2-qubit CZ IQAE (Whisper C3720).

THE PROBLEM THIS SOLVES:
  Exp 24 (C3716) confirmed on real ibm_marrakesh: 2-qubit CZ-heavy encoding has
  4.20pp mean hardware error vs ideal (vs 0.93pp for zero-CZ in Exp 23).
  Strong depth degradation: k=0 → 2.21pp, k=4 → 9.34pp. T3 PASSED.

  The question: can Zero-Noise Extrapolation (ZNE) recover accuracy from this
  noisy 2-qubit CZ circuit on real hardware?

ZNE METHOD — Digital Global Gate Folding + Richardson Extrapolation:
  Global folding: replace circuit C (without measure) with C · C† · C (λ=3)
  or C · C† · C · C† · C (λ=5). In the noiseless limit these are identity
  (each fold cancels). With noise, they amplify noise proportional to λ.

  Noise scale factors: λ ∈ {1, 3, 5}
    λ=1: original circuit C·measure
    λ=3: (C·C†·C)·measure       -> 3× gate count, 3× noise
    λ=5: (C·C†·C·C†·C)·measure -> 5× gate count, 5× noise

  Extrapolation (Richardson 3-point, linear model):
    Assume E(λ) = E₀ + a·λ (linear noise model — valid for low-depth regime)
    With 3 points we fit and evaluate at λ=0.
    Also compute 2-point extrapolation (λ=1,3) as cross-check.

DESIGN:
  Same (P,k) grid as Exp 23/24: P ∈ {0.56, 0.9}, k ∈ {0,1,2,3,4}
  Three noise scales per (P,k) pair → 2 × 5 × 3 = 30 circuits, one batched job.
  4096 shots per circuit (same as Exp 23/24 for apples-to-apples).

PRE-REGISTERED FALSIFICATION CRITERIA (committed before reading hardware result):
  Let hw24(P,k)  = Exp 24 raw hardware error |hw_p11 - ideal| (known, baseline)
      zne(P,k)   = Richardson ZNE estimate error |zne_p11 - ideal|
      sim24(P,k) = Exp 24 FakeMarrakesh error |sim_p11 - ideal|

  T1 (ZNE-EFFECTIVE):     mean_k zne < mean_k hw24
                          → ZNE improves over raw hardware. Failure = ZNE not useful.
  T2 (ZNE-BEATS-SIM):    mean_k zne < mean_k sim24
                          → ZNE extrapolated estimate beats even the noise model.
                            (stretch goal: ZNE recovers near-ideal, beating simulation)
  T3 (DEPTH-MITIGATION):  (zne(k=4) - hw24(k=4)) > (zne(k=0) - hw24(k=0)) in magnitude
                          → ZNE provides LARGER improvement at higher depth (more noise
                            to cancel). Expected: yes, because ZNE targets the additive
                            noise that accumulates with gate depth.

  PRE-REGISTERED EXPECTATION (Whisper, C3720):
    T1 PASS — ZNE should reduce 4.20pp mean by ~50%, target <2.5pp.
    T2 FAIL — recovering below FakeMarrakesh's 1.03pp mean is a stretch goal.
    T3 PASS — depth-correlated noise means ZNE benefit scales with k.

Run (simulation preview):   python3 scripts/run_exp25_zne_2qubit.py
Run (real hardware submit):  python3 scripts/run_exp25_zne_2qubit.py --submit
Poll + finalize:             python3 scripts/run_exp25_zne_2qubit.py --finalize <job_id>
"""
import argparse
import json
import numpy as np

EXPERIMENT = "25"
CYCLE = 3720
SHOTS = 4096
P_VALUES = [0.56, 0.9]
K_VALUES = [0, 1, 2, 3, 4]
SCALE_FACTORS = [1, 3, 5]          # ZNE noise amplification levels
SEED_TRANSPILER = 42
BACKEND_NAME = "ibm_marrakesh"
RESULT_PATH = f"experiments/{EXPERIMENT}-zne-2qubit-results.json"
JOBID_PATH = f"experiments/{EXPERIMENT}-jobid.txt"

# Exp 24 baselines (from experiments/24-2qubit-hardware-validation-results.json)
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
    """Ideal P(|11>) after k Grover iterations (same formula as Exp 23/24)."""
    th_a = np.arcsin(np.sqrt(P))
    return float(np.sin((2 * k + 1) * th_a) ** 2)


def build_base_circuit(P, k):
    """Build A + Q^k (no measurement) — the circuit to be folded."""
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


def fold_and_measure(base_qc, scale):
    """Apply global gate folding at the given scale factor and add measurement.

    scale=1: base_qc (unchanged)
    scale=3: base_qc · base_qc† · base_qc
    scale=5: base_qc · base_qc† · base_qc · base_qc† · base_qc
    """
    from qiskit import QuantumCircuit
    num_qubits = base_qc.num_qubits
    n_folds = (scale - 1) // 2     # number of (C†·C) pairs to append
    folded = QuantumCircuit(num_qubits, num_qubits)
    folded.compose(base_qc, inplace=True)
    inv = base_qc.inverse()
    for _ in range(n_folds):
        folded.compose(inv, inplace=True)
        folded.compose(base_qc, inplace=True)
    folded.measure(list(range(num_qubits)), list(range(num_qubits)))
    return folded


def build_schedule():
    """Ordered (P, k, scale, circuit) tuples — canonical PUB order for batched job."""
    schedule = []
    for P in P_VALUES:
        for k in K_VALUES:
            base = build_base_circuit(P, k)
            for scale in SCALE_FACTORS:
                qc = fold_and_measure(base, scale)
                schedule.append((P, k, scale, qc))
    return schedule


def counts_to_p11(counts, shots):
    """Extract P(|11>) from a counts dict."""
    good = 0
    total = 0
    for bitstr, c in counts.items():
        total += c
        bs = bitstr.replace(" ", "")
        if bs[-2:] == "11":
            good += c
    return good / (total if total > 0 else shots)


def richardson_extrapolate(vals, scales):
    """Richardson extrapolation to λ=0 using a linear fit.

    vals: list of P(|11>) measurements at each scale
    scales: list of noise scale factors (e.g. [1, 3, 5])
    Returns: (zne_linear, zne_3pt)
      zne_linear: 2-point linear extrapolation using scales[0] and scales[1]
      zne_3pt:    3-point polynomial fit (degree 1) extrapolated to 0
    """
    x = np.array(scales, dtype=float)
    y = np.array(vals, dtype=float)
    # 2-point linear: extrapolate from first two points
    if len(vals) >= 2:
        slope = (y[1] - y[0]) / (x[1] - x[0])
        zne_2pt = float(y[0] - slope * x[0])
    else:
        zne_2pt = float(y[0])
    # 3-point linear (least squares): fit line to all 3 points, evaluate at 0
    if len(vals) >= 3:
        coeffs = np.polyfit(x, y, 1)           # degree 1: c0*x + c1
        zne_3pt = float(np.polyval(coeffs, 0))
    else:
        zne_3pt = zne_2pt
    return zne_2pt, zne_3pt


def run_fakemarrakesh(schedule):
    """Run on FakeMarrakesh (local sim) as comparison baseline."""
    from qiskit import transpile
    from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
    from qiskit_aer.primitives import SamplerV2 as AerSampler
    from qiskit_aer.noise import NoiseModel

    backend = FakeMarrakesh()
    nm = NoiseModel.from_backend(backend)
    sampler = AerSampler(options={
        "backend_options": {"noise_model": nm},
        "run_options": {"shots": SHOTS, "seed": SEED_TRANSPILER},
    })
    tcircs = [transpile(c, backend=backend, optimization_level=1, seed_transpiler=SEED_TRANSPILER)
              for (_, _, _, c) in schedule]
    res = sampler.run([(tc,) for tc in tcircs]).result()
    p11s = []
    for i in range(len(schedule)):
        counts = res[i].data.c.get_counts()
        p11s.append(counts_to_p11(counts, SHOTS))
    return p11s


def submit_hardware(schedule):
    """Submit batched 30-circuit job to real QPU. Returns job_id (non-blocking)."""
    from qiskit import transpile
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

    service = QiskitRuntimeService()
    backend = service.backend(BACKEND_NAME)
    print(f"  Backend: {backend.name}  (qubits={backend.num_qubits})")
    tcircs = [transpile(c, backend=backend, optimization_level=1, seed_transpiler=SEED_TRANSPILER)
              for (_, _, _, c) in schedule]
    for (P, k, scale, _), tc in zip(schedule, tcircs):
        ops = tc.count_ops()
        cz = ops.get("cz", 0) + ops.get("ecr", 0) + ops.get("cx", 0)
        print(f"    P={P} k={k} λ={scale}: depth={tc.depth()} 2q_gates={cz}")
    sampler = SamplerV2(mode=backend)
    sampler.options.default_shots = SHOTS
    job = sampler.run([(tc,) for tc in tcircs])
    job_id = job.job_id()
    with open(JOBID_PATH, "w") as f:
        f.write(job_id + "\n")
    print(f"  SUBMITTED. job_id = {job_id}  (saved to {JOBID_PATH})")
    return job_id


def fetch_hardware_p11(job_id, schedule):
    """Retrieve completed job results."""
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


def analyze(schedule, hw_p11s, sim_p11s, job_id=None):
    """Compute per-(P,k) ZNE estimates and evaluate pre-registered criteria."""
    # Group by (P, k): collect raw vals at each scale
    groups = {}
    for i, (P, k, scale, _) in enumerate(schedule):
        key = (P, k)
        if key not in groups:
            groups[key] = {}
        groups[key][scale] = i

    rows = []
    for P in P_VALUES:
        for k in K_VALUES:
            key = (P, k)
            idxs = [groups[key][s] for s in SCALE_FACTORS]
            ide = ideal_p11(P, k)

            # Sim values at each scale
            sim_raw = [sim_p11s[i] for i in idxs]
            sim_zne_2pt, sim_zne_3pt = richardson_extrapolate(sim_raw, SCALE_FACTORS)

            row = {
                "P": P, "k": k,
                "ideal": round(ide, 4),
                "sim_raw_lam1": round(sim_raw[0], 4),
                "sim_raw_lam3": round(sim_raw[1], 4),
                "sim_raw_lam5": round(sim_raw[2], 4),
                "sim_zne_2pt": round(sim_zne_2pt, 4),
                "sim_zne_3pt": round(sim_zne_3pt, 4),
                "dev_sim_lam1_ideal": round(abs(sim_raw[0] - ide), 4),
                "dev_sim_zne_ideal": round(abs(sim_zne_3pt - ide), 4),
                "exp24_hw_baseline": EXP24_HW.get(key),
                "exp24_sim_baseline": EXP24_SIM.get(key),
            }

            if hw_p11s is not None:
                hw_raw = [hw_p11s[i] for i in idxs]
                hw_zne_2pt, hw_zne_3pt = richardson_extrapolate(hw_raw, SCALE_FACTORS)
                row.update({
                    "hw_raw_lam1": round(hw_raw[0], 4),
                    "hw_raw_lam3": round(hw_raw[1], 4),
                    "hw_raw_lam5": round(hw_raw[2], 4),
                    "hw_zne_2pt": round(hw_zne_2pt, 4),
                    "hw_zne_3pt": round(hw_zne_3pt, 4),
                    "dev_hw_lam1_ideal": round(abs(hw_raw[0] - ide), 4),
                    "dev_hw_zne_2pt_ideal": round(abs(hw_zne_2pt - ide), 4),
                    "dev_hw_zne_3pt_ideal": round(abs(hw_zne_3pt - ide), 4),
                })
            rows.append(row)

    out = {
        "experiment": EXPERIMENT,
        "title": "Zero-Noise Extrapolation on 2-qubit CZ IQAE (Exp 24 follow-up)",
        "cycle": CYCLE,
        "backend": BACKEND_NAME if hw_p11s is not None else "SIM-PREVIEW-ONLY",
        "job_id": job_id,
        "params": {
            "shots": SHOTS,
            "P_values": P_VALUES,
            "k_values": K_VALUES,
            "scale_factors": SCALE_FACTORS,
            "method": "global gate folding + Richardson 3-point linear extrapolation",
            "circuits_total": len(schedule),
            "seed_transpiler": SEED_TRANSPILER,
            "encoding": "2-qubit |11> Bernoulli (CZ-heavy, same as Exp 24)",
        },
        "preregistered_criteria": {
            "T1": "mean zne_err < mean exp24_hw_err (4.20pp) -> ZNE-EFFECTIVE",
            "T2": "mean zne_err < mean exp24_sim_err (1.03pp) -> ZNE-BEATS-SIM (stretch)",
            "T3": "ZNE improvement larger at k=4 than k=0 -> DEPTH-MITIGATION",
        },
        "preregistered_expectation": "T1 PASS (~50% improvement target), T2 FAIL, T3 PASS",
        "rows": rows,
    }

    if hw_p11s is not None:
        # Summary statistics
        exp24_hw_mean = float(np.mean(list(EXP24_HW.values())))
        exp24_sim_mean = float(np.mean(list(EXP24_SIM.values())))
        zne_errs = [r["dev_hw_zne_3pt_ideal"] for r in rows]
        raw_errs = [r["dev_hw_lam1_ideal"] for r in rows]
        mean_zne = float(np.mean(zne_errs))
        mean_raw = float(np.mean(raw_errs))

        # Per-depth improvement
        imp_k0 = float(np.mean([rows[i]["dev_hw_lam1_ideal"] - rows[i]["dev_hw_zne_3pt_ideal"]
                                 for i in range(len(rows)) if rows[i]["k"] == 0]))
        imp_k4 = float(np.mean([rows[i]["dev_hw_lam1_ideal"] - rows[i]["dev_hw_zne_3pt_ideal"]
                                 for i in range(len(rows)) if rows[i]["k"] == 4]))

        out["summary"] = {
            "mean_raw_hw_err_lam1": round(mean_raw, 4),
            "mean_zne_err_3pt": round(mean_zne, 4),
            "exp24_hw_baseline": round(exp24_hw_mean, 4),
            "exp24_sim_baseline": round(exp24_sim_mean, 4),
            "zne_improvement_vs_exp24_hw_pp": round((exp24_hw_mean - mean_zne) * 100, 2),
            "improvement_k0_pp": round(imp_k0 * 100, 2),
            "improvement_k4_pp": round(imp_k4 * 100, 2),
        }
        verdicts = {}
        verdicts["T1"] = (
            "PASS: ZNE-EFFECTIVE" if mean_zne < exp24_hw_mean
            else "FAIL: ZNE did not improve over raw hardware"
        )
        verdicts["T2"] = (
            "PASS: ZNE-BEATS-SIM (stretch goal!)" if mean_zne < exp24_sim_mean
            else f"FAIL: ZNE ({mean_zne:.4f}) did not beat FakeMarrakesh ({exp24_sim_mean:.4f})"
        )
        verdicts["T3"] = (
            "PASS: DEPTH-MITIGATION" if imp_k4 > imp_k0
            else "FAIL: ZNE improvement did not scale with depth"
        )
        out["verdicts"] = verdicts

    return out


def print_table(out, hw=True):
    print(f"\n  {'P':>5} {'k':>2} {'ideal':>7} "
          f"{'sim_λ=1':>8} {'sim_ZNE':>8} "
          f"{'hw_λ=1':>8} {'hw_ZNE':>8} "
          f"{'|hw_λ1-id|':>11} {'|ZNE-id|':>9} "
          f"{'Exp24':>7}")
    for r in out["rows"]:
        def fmt(v):
            return f"{v:.4f}" if v is not None else "  --  "
        hw1 = fmt(r.get("hw_raw_lam1"))
        hwz = fmt(r.get("hw_zne_3pt"))
        dhw = fmt(r.get("dev_hw_lam1_ideal"))
        dzne = fmt(r.get("dev_hw_zne_3pt_ideal"))
        e24 = fmt(r.get("exp24_hw_baseline"))
        print(f"  {r['P']:>5} {r['k']:>2} {r['ideal']:>7.4f} "
              f"{r['sim_raw_lam1']:>8.4f} {r['sim_zne_3pt']:>8.4f} "
              f"{hw1:>8} {hwz:>8} "
              f"{dhw:>11} {dzne:>9} "
              f"{e24:>7}")

    if "summary" in out:
        s = out["summary"]
        print(f"\n  ZNE mean error: {s['mean_zne_err_3pt']:.4f}  "
              f"Raw λ=1 mean: {s['mean_raw_hw_err_lam1']:.4f}  "
              f"Exp24 HW baseline: {s['exp24_hw_baseline']:.4f}")
        print(f"  ZNE improvement vs Exp24 HW: {s['zne_improvement_vs_exp24_hw_pp']:.2f}pp")
        print(f"  ZNE improvement at k=0: {s['improvement_k0_pp']:.2f}pp  "
              f"at k=4: {s['improvement_k4_pp']:.2f}pp")
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
    ap.add_argument("--submit", action="store_true", help="submit batched job to real QPU")
    ap.add_argument("--finalize", metavar="JOB_ID", help="fetch completed job and analyze")
    args = ap.parse_args()

    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    print(f"Exp {EXPERIMENT} (C{CYCLE}): ZNE on 2-qubit CZ IQAE encoding")
    print(f"  Method: global gate folding at λ={SCALE_FACTORS}, Richardson extrapolation")
    print(f"  Grid: P in {P_VALUES}, k in {K_VALUES} -> {len(P_VALUES)*len(K_VALUES)*len(SCALE_FACTORS)} circuits")

    print("\n  Building circuit schedule...")
    schedule = build_schedule()
    print(f"  Schedule built: {len(schedule)} circuits")

    print("\n  Running FakeMarrakesh simulation...")
    sim_p11s = run_fakemarrakesh(schedule)
    print(f"  Sim complete. λ=1 baseline for P=0.56, k=0: {sim_p11s[0]:.4f}")

    if args.finalize:
        hw_p11s, status = fetch_hardware_p11(args.finalize, schedule)
        if hw_p11s is None:
            print(f"  Job not done yet (status={status}). Re-run --finalize later.")
            return
        out = analyze(schedule, hw_p11s, sim_p11s, job_id=args.finalize)
        print_table(out)
        save(out)
        return

    if args.submit:
        print("\n  Submitting 30-circuit ZNE job to real hardware...")
        job_id = submit_hardware(schedule)
        print(f"\n  Next: python3 scripts/run_exp25_zne_2qubit.py --finalize {job_id}")
        out = analyze(schedule, None, sim_p11s, job_id=job_id)
        print("\n  Simulation preview (hardware pending):")
        print_table(out, hw=False)
        save(out)
        return

    # Preview only
    out = analyze(schedule, None, sim_p11s, job_id=None)
    print("\n  Simulation preview (no hardware):")
    print_table(out, hw=False)
    print("\n  (preview only -- pass --submit to run on real hardware)")


if __name__ == "__main__":
    main()
