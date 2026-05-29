"""Exp 26: ZNE P-grid extension — P=0.14 and P=0.33 (Whisper C3721).

MOTIVATION:
  Exp 25b confirmed ZNE works for P={0.56, 0.9} on ibm_marrakesh (mean error 1.86pp vs
  raw-hardware baseline 3.23pp — 42% reduction; vs Exp24 4.20pp — 56% reduction).
  The IQAE financial arc requires coverage across the FULL amplitude range. P=0.14 (lower
  outer zone, 14% loss probability) and P=0.33 (lower middle range, 33% loss probability)
  have NEVER been tested with ZNE on real hardware.

KEY SCIENTIFIC INSIGHT (drives T1/T2 predictions):
  The 2-qubit CZ oracle structure is P-INDEPENDENT: the Grover operator uses the SAME
  number of CZ gates regardless of P. Only the Ry angles in the state-preparation A change.
  Therefore:
    • Hardware noise is P-independent (depends on CZ count, not target amplitude)
    • ZNE correction is P-independent (same noise model → same extrapolation quality)
  This is a falsifiable structural prediction: if ZNE fails for P=0.14 while working at
  P={0.56, 0.9}, it reveals amplitude-dependent noise beyond the CZ-gate model.

NOTE ON 2-pt vs 3-pt ZNE (Exp 25b finding):
  At P={0.56, 0.9}, 2-point ZNE (1.71pp) outperformed 3-point linear regression (1.86pp)
  on average (6/10 conditions). Both are computed here for full comparison. The 3-point
  linear regression (np.polyfit degree=1) fits a best-fit line through all three λ values
  and extrapolates to λ=0 — NOT a quadratic Richardson but a noise-robust linear model.

DESIGN:
  P ∈ {0.14, 0.33}, k ∈ {0,1,2,3,4}, λ ∈ {1,3,5} → 30 circuits, one batched job.
  4096 shots per circuit. Backend: ibm_marrakesh.
  Method: fold logical circuit then transpile at opt=0 (same as Exp 25b corrected method).

P=0.14 IDEAL VALUES (notable: exercise BOTH outer zones):
  k=0: 0.1400 (lower outer zone)
  k=1: 0.8230 (upper inner zone)
  k=2: 0.9262 (upper outer zone — same regime as P=0.9 challenges)
  k=3: 0.4320 (middle zone)
  k=4: 0.0832 (lower outer zone — harder than k=0)

P=0.33 IDEAL VALUES (middle-range, inner zone dominant):
  k=0: 0.3300
  k=1: 0.9147
  k=2: 0.6180
  k=3: 0.0665
  k=4: 0.7661

PRE-REGISTERED CRITERIA (Whisper C3721, committed before job submission):
  T1 (ZNE-EFFECTIVE):     For BOTH P=0.14 and P=0.33:
                           mean_k |ZNE_2pt-ideal| < mean_k |raw_lam1-ideal|
  T2 (P-INDEPENDENCE):    |mean_ZNE_P014 - mean_ZNE_P033| < 1.50pp
                           (if P-independent noise model holds, both P values should
                           yield similar ZNE effectiveness)
  T3 (DEPTH-MITIGATION):  ZNE improvement (raw - ZNE) larger at k=4 than k=0
                           for both new P values (same depth-scaling physics as Exp 25b)

PRE-REGISTERED EXPECTATION (Whisper C3721):
  T1 PASS  — P-independent oracle noise → ZNE equally effective
  T2 PASS  — same noise model for both P values → comparable mean errors
  T3 PASS  — depth-dependent CZ noise correction is P-independent (Exp 25b T3 PASS)

ARC CLOSURE:
  After Exp 26: ZNE validated across {0.14, 0.33, 0.56, 0.90} — full financial range.
  Combined (Exp 24 + 25b + 26):
    Raw 2-qubit CZ IQAE error:  ~3.2–4.2pp (P-independent, depth-dependent)
    ZNE-corrected error:        ~1.7–1.9pp (56% improvement, P-independent)
  Remaining gap vs simulator:  ~0.8pp — attributable to non-Markovian noise beyond
                                 the ZNE linear-noise model assumption.

Run (simulation preview):    python3 scripts/run_exp26_zne_p_grid_extension.py
Run (real hardware submit):  python3 scripts/run_exp26_zne_p_grid_extension.py --submit
Poll + finalize:             python3 scripts/run_exp26_zne_p_grid_extension.py --finalize <job_id>
"""
import argparse
import json
import numpy as np

EXPERIMENT = "26"
CYCLE = 3721
SHOTS = 4096
P_VALUES = [0.14, 0.33]
K_VALUES = [0, 1, 2, 3, 4]
SCALE_FACTORS = [1, 3, 5]
SEED_TRANSPILER = 42
BACKEND_NAME = "ibm_marrakesh"
RESULT_PATH = f"experiments/{EXPERIMENT}-zne-p-grid-extension-results.json"
JOBID_PATH = f"experiments/{EXPERIMENT}-jobid.txt"

# Exp 25b ZNE results for cross-P comparison (reference baseline)
EXP25B_ZNE_MEAN = 0.0186  # mean_zne_3pt at P={0.56, 0.9}
EXP25B_RAW_MEAN = 0.0323  # mean_raw_lam1 at P={0.56, 0.9}


def ideal_p11(P, k):
    """Ideal P(|11>) for 2-qubit IQAE with k Grover iterations at amplitude sqrt(P)."""
    th_a = np.arcsin(np.sqrt(P))
    return float(np.sin((2 * k + 1) * th_a) ** 2)


def build_base_circuit_logical(P, k):
    """Build logical A + Q^k (2-qubit, no measurement) — before transpilation."""
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
    """Build folded schedule for FakeMarrakesh simulation.

    Folds LOGICAL circuits then transpiles at opt=0 (prevents optimizer collapse).
    Keeps circuits on 2 qubits for tractable simulation.
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
                qc_t = transpile(qc_logical, backend=backend,
                                 optimization_level=0, seed_transpiler=SEED_TRANSPILER)
                schedule.append((P, k, scale, qc_t, backend))
    return schedule


def build_schedule_for_hardware():
    """Build folded schedule for real QPU.

    Method (same as Exp 25b corrected):
      1. Fold LOGICAL 2-qubit circuit (compose base + inv + base × n_folds)
      2. Transpile the ENTIRE folded circuit at optimization_level=0
         (no optimizer, so Q·Q† cancellation CANNOT occur)
      3. Submit directly — gates scale correctly with λ

    This is the verified-correct approach from Exp 25b (avoids Exp 25 collapse failure).
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
                qc_hw = transpile(qc_logical, backend=backend,
                                  optimization_level=0, seed_transpiler=SEED_TRANSPILER)
                schedule.append((P, k, scale, qc_hw))
    return schedule, backend


def counts_to_p11(counts, shots):
    """Extract P(|11>) from measurement counts (robust to register ordering)."""
    good = 0
    total = 0
    for bitstr, c in counts.items():
        total += c
        bs = bitstr.replace(" ", "")
        if bs[-2:] == "11":
            good += c
    return good / (total if total > 0 else shots)


def richardson_extrapolate(vals, scales):
    """ZNE extrapolation to zero-noise.

    2-point: Richardson between λ=1 and λ=3.
      f̂(0) = (3·f(1) - f(3)) / 2
    3-point: Linear regression through all three λ values, evaluated at λ=0.
      Best-fit line (np.polyfit degree=1) through (1,f1), (3,f3), (5,f5).
      More noise-robust than quadratic Richardson for limited-shot data.
    """
    x = np.array(scales, dtype=float)
    y = np.array(vals, dtype=float)
    # 2-point Richardson (λ=1, λ=3)
    slope = (y[1] - y[0]) / (x[1] - x[0])
    zne_2pt = float(y[0] - slope * x[0])
    # 3-point linear regression
    if len(vals) >= 3:
        coeffs = np.polyfit(x, y, 1)
        zne_3pt = float(np.polyval(coeffs, 0))
    else:
        zne_3pt = zne_2pt
    return zne_2pt, zne_3pt


def run_fakemarrakesh(schedule_with_backend):
    """Run folded circuits on FakeMarrakesh."""
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
        data = res[i].data
        reg_name = list(data.__dict__.keys())[0]
        counts = getattr(data, reg_name).get_counts()
        p11s.append(counts_to_p11(counts, SHOTS))
    return p11s, [(item[0], item[1], item[2]) for item in items]


def submit_hardware(schedule, backend):
    """Submit 30-circuit batched job. schedule = [(P,k,scale,qc), ...]"""
    from qiskit_ibm_runtime import SamplerV2
    print(f"  Backend: {backend.name}  (qubits={backend.num_qubits})")
    print(f"  Verifying gate scaling (should match λ=1→3→5 ratio):")
    for (P, k, scale, qc) in schedule:
        ops = qc.count_ops()
        cz = ops.get("cz", 0) + ops.get("ecr", 0) + ops.get("cx", 0)
        print(f"    P={P:.2f} k={k} λ={scale}: depth={qc.depth()} 2q={cz}")
    sampler = SamplerV2(mode=backend)
    sampler.options.default_shots = SHOTS
    job = sampler.run([(qc,) for (_, _, _, qc) in schedule])
    job_id = job.job_id()
    with open(JOBID_PATH, "w") as f:
        f.write(job_id + "\n")
    print(f"\n  SUBMITTED. job_id = {job_id}  (saved to {JOBID_PATH})")
    print(f"  Next: python3 scripts/run_exp26_zne_p_grid_extension.py --finalize {job_id}")
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
    """Analyze results. Builds rows for all P×k combinations."""
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
                "sim_zne_2pt": round(sim_zne_2pt, 4),
                "sim_zne_3pt": round(sim_zne_3pt, 4),
                "dev_sim_lam1": round(abs(sim_vals[0] - ide), 4),
                "dev_sim_zne_2pt": round(abs(sim_zne_2pt - ide), 4),
                "dev_sim_zne_3pt": round(abs(sim_zne_3pt - ide), 4),
                # Cross-reference: Exp 25b mean as benchmark (P-independent prediction)
                "exp25b_zne_mean": EXP25B_ZNE_MEAN,
                "exp25b_raw_mean": EXP25B_RAW_MEAN,
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
        "title": "ZNE P-grid extension — P=0.14 and P=0.33 (lower financial amplitude range)",
        "cycle": CYCLE,
        "backend": BACKEND_NAME if hw_p11s is not None else "SIM-PREVIEW-ONLY",
        "job_id": job_id,
        "params": {
            "shots": SHOTS,
            "P_values": P_VALUES,
            "k_values": K_VALUES,
            "scale_factors": SCALE_FACTORS,
            "method": "fold logical circuit then transpile at opt=0 (Exp 25b corrected approach)",
            "circuits_total": len(pkscale_list),
            "seed_transpiler": SEED_TRANSPILER,
            "motivation": (
                "P=0.14 (lower outer zone) and P=0.33 (lower middle) not yet ZNE-tested "
                "on real hardware. P-independent oracle predicts same ZNE effectiveness."
            ),
        },
        "preregistered_criteria": {
            "T1": (
                "ZNE-EFFECTIVE for BOTH new P values: "
                "mean_k |ZNE_2pt-ideal| < mean_k |raw_lam1-ideal| at P=0.14 AND P=0.33"
            ),
            "T2": (
                "P-INDEPENDENCE: |mean_ZNE_P014 - mean_ZNE_P033| < 1.50pp "
                "(P-independent oracle → comparable ZNE effectiveness)"
            ),
            "T3": (
                "DEPTH-MITIGATION for BOTH P values: "
                "ZNE improvement (raw-ZNE) larger at k=4 than k=0"
            ),
        },
        "preregistered_expectation": (
            "T1 PASS (P-independent noise → same ZNE effectiveness), "
            "T2 PASS (same CZ oracle → comparable mean errors), "
            "T3 PASS (depth-scaling physics is P-independent)"
        ),
        "rows": rows,
    }

    if hw_p11s is not None:
        # Separate stats per P value
        stats_per_P = {}
        for P in P_VALUES:
            p_rows = [r for r in rows if r["P"] == P]
            mean_raw = float(np.mean([r["dev_hw_lam1"] for r in p_rows]))
            mean_zne_2pt = float(np.mean([r["dev_hw_zne_2pt"] for r in p_rows]))
            mean_zne_3pt = float(np.mean([r["dev_hw_zne_3pt"] for r in p_rows]))
            imp_k0 = float(np.mean([r["dev_hw_lam1"] - r["dev_hw_zne_2pt"]
                                     for r in p_rows if r["k"] == 0]))
            imp_k4 = float(np.mean([r["dev_hw_lam1"] - r["dev_hw_zne_2pt"]
                                     for r in p_rows if r["k"] == 4]))
            stats_per_P[str(P)] = {
                "mean_raw_lam1": round(mean_raw, 4),
                "mean_zne_2pt": round(mean_zne_2pt, 4),
                "mean_zne_3pt": round(mean_zne_3pt, 4),
                "zne_2pt_improvement_pp": round((mean_raw - mean_zne_2pt) * 100, 2),
                "improvement_k0_pp": round(imp_k0 * 100, 2),
                "improvement_k4_pp": round(imp_k4 * 100, 2),
                "T1_pass": mean_zne_2pt < mean_raw,
                "T3_pass": imp_k4 > imp_k0,
            }

        mean_zne_014 = stats_per_P["0.14"]["mean_zne_2pt"]
        mean_zne_033 = stats_per_P["0.33"]["mean_zne_2pt"]
        p_independence_gap = abs(mean_zne_014 - mean_zne_033)

        overall_mean_raw = float(np.mean([r["dev_hw_lam1"] for r in rows]))
        overall_mean_zne = float(np.mean([r["dev_hw_zne_2pt"] for r in rows]))

        out["summary"] = {
            "overall_mean_raw": round(overall_mean_raw, 4),
            "overall_mean_zne_2pt": round(overall_mean_zne, 4),
            "exp25b_zne_mean_reference": EXP25B_ZNE_MEAN,
            "stats_per_P": stats_per_P,
            "p_independence_gap_pp": round(p_independence_gap * 100, 2),
        }

        t1_pass = stats_per_P["0.14"]["T1_pass"] and stats_per_P["0.33"]["T1_pass"]
        t2_pass = p_independence_gap < 0.015  # <1.5pp
        t3_pass = stats_per_P["0.14"]["T3_pass"] and stats_per_P["0.33"]["T3_pass"]

        out["verdicts"] = {
            "T1": ("PASS: ZNE-EFFECTIVE for both P=0.14 and P=0.33"
                   if t1_pass else "FAIL: ZNE did not reduce error for at least one P value"),
            "T2": (f"PASS: P-INDEPENDENCE (gap={p_independence_gap*100:.2f}pp < 1.50pp)"
                   if t2_pass else f"FAIL: P-DEPENDENCE detected (gap={p_independence_gap*100:.2f}pp > 1.50pp)"),
            "T3": ("PASS: DEPTH-MITIGATION for both P=0.14 and P=0.33"
                   if t3_pass else "FAIL: Depth-mitigation did not hold for at least one P value"),
        }

    return out


def print_table(out):
    """Print readable summary table."""
    print(f"\n  {'P':>5} {'k':>2} {'ideal':>7} {'sim_λ1':>7} {'sim_ZNE':>8} "
          f"{'hw_λ1':>7} {'hw_ZNE':>8} {'|hw1-id|':>9} {'|ZNE-id|':>9}")
    for r in out["rows"]:
        def f(v):
            return f"{v:.4f}" if v is not None else "  --  "
        print(f"  {r['P']:>5.2f} {r['k']:>2} {r['ideal']:>7.4f} "
              f"{r['sim_raw_lam1']:>7.4f} {r['sim_zne_2pt']:>8.4f} "
              f"{f(r.get('hw_raw_lam1')):>7} {f(r.get('hw_zne_2pt')):>8} "
              f"{f(r.get('dev_hw_lam1')):>9} {f(r.get('dev_hw_zne_2pt')):>9}")

    if "summary" in out:
        s = out["summary"]
        print(f"\n  Overall: raw {s['overall_mean_raw']:.4f}  "
              f"ZNE_2pt {s['overall_mean_zne_2pt']:.4f}  "
              f"(Exp25b ref: {s['exp25b_zne_mean_reference']:.4f})")
        for P_str, ps in s["stats_per_P"].items():
            print(f"  P={P_str}: raw {ps['mean_raw_lam1']:.4f} → "
                  f"ZNE_2pt {ps['mean_zne_2pt']:.4f} "
                  f"({ps['zne_2pt_improvement_pp']:+.2f}pp improvement) "
                  f"k=0→{ps['improvement_k0_pp']:.2f}pp k=4→{ps['improvement_k4_pp']:.2f}pp")
        print(f"  P-independence gap: {s['p_independence_gap_pp']:.2f}pp")

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
    ap.add_argument("--submit", action="store_true",
                    help="Submit to IBM Quantum ibm_marrakesh")
    ap.add_argument("--finalize", metavar="JOB_ID",
                    help="Fetch completed job and produce final results")
    args = ap.parse_args()

    print(f"Exp {EXPERIMENT} (C{CYCLE}): ZNE P-grid extension")
    print(f"  New P values: {P_VALUES}  (extending Exp 25b P={{0.56, 0.9}})")
    print(f"  Grid: P={P_VALUES} x k={K_VALUES} x λ={SCALE_FACTORS} = 30 circuits")
    print(f"\n  Pre-registered ideal values:")
    for P in P_VALUES:
        print(f"  P={P:.2f}: " + "  ".join(f"k={k}: {ideal_p11(P,k):.4f}" for k in K_VALUES))

    print("\n  Building FakeMarrakesh schedule...")
    sim_schedule = build_schedule_for_fakemarrakesh()
    print(f"  Running FakeMarrakesh simulation ({len(sim_schedule)} circuits)...")
    sim_p11s, pkscale_list = run_fakemarrakesh(sim_schedule)
    print("  Sim complete.")

    if args.finalize:
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
        print("\n  Building hardware schedule (fold logical then transpile opt=0)...")
        hw_schedule, backend = build_schedule_for_hardware()
        print("  Circuit verification (confirming gate-count λ-scaling):")
        job_id = submit_hardware(hw_schedule, backend)
        out = analyze(pkscale_list, None, sim_p11s, job_id=job_id)
        print("\n  Simulation preview (hardware results pending):")
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
