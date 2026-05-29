"""Exp 27: ZNE + Readout Error Mitigation (REM) — Breaking the 1-Qubit Barrier (Whisper C3722).

SCIENTIFIC MOTIVATION:
  ZNE arc (Exp 25–26) closed with 2-point linear extrapolation validated as the OPTIMAL
  strategy. Analysis (C3722) compared 2pt vs 3pt polynomial vs exponential on all existing
  λ=1,3,5 hardware data:
    Raw λ=1:          2.93pp mean error
    ZNE 2-point:      1.58pp (46% improvement — BEST)
    ZNE 3-point:      1.77pp (40% improvement — WORSE than 2pt)
    Exponential fit:  1.72pp (41% improvement — WORSE than 2pt)

  FINDING: Adding scale factors (λ=5,7) and higher-order extrapolation does NOT help.
  The non-Markovian floor (~0.8pp sim, ~1.58pp hardware) cannot be reduced by more
  sophisticated ZNE extrapolation. A DIFFERENT technique is needed.

  KEY INSIGHT: ZNE corrects gate errors by amplifying them and extrapolating to zero.
  But readout errors (measurement bit-flips) are NOT amplified by λ — they appear at the
  END of the circuit regardless of scale factor. Therefore ZNE cannot reduce readout error.
  Readout Error Mitigation (REM) corrects a COMPLEMENTARY error source.

  1-QUBIT BASELINE (Exp 23): 0.93pp mean error (no REM, no ZNE, zero CZ gates)
  2-QUBIT ZNE-ONLY (Exp 25b): 1.58pp (best so far — 0.65pp above 1-qubit raw)
  HYPOTHESIS: ZNE removes ~2.62pp of gate error; REM may remove 0.3-0.8pp of readout
  error, pushing ZNE+REM below the 1-qubit raw threshold (0.93pp).

REM METHODOLOGY:
  Readout calibration uses 4 circuits that prepare each 2-qubit basis state and measure.
  The resulting 4×4 matrix M[measured][prepared] encodes the readout error channel.
  For each main circuit, we apply M^{-1} to the probability vector to recover corrected
  probabilities. This is the "matrix inversion" REM method (simple, no regularization).

  Calibration states: |00>, |01>, |10>, |11>  →  4 extra circuits per job.

DESIGN:
  P ∈ {0.56, 0.90}  (same as Exp 25b — direct comparison)
  k ∈ {0,1,2,3,4}
  λ ∈ {1,3}         (2-point ZNE only — validated optimal by C3722 analysis)
  Main circuits: 2P × 5k × 2λ = 20 circuits
  Calibration circuits: 4 (|00>, |01>, |10>, |11>)
  Total: 24 circuits per job. Shots: 4096 per circuit.

FOUR CONDITIONS COMPARED:
  A. Raw (λ=1, no correction)
  B. ZNE-only (2-point linear extrapolation, no REM)
  C. REM-only (no ZNE, just readout correction at λ=1)
  D. ZNE+REM (ZNE extrapolated estimate corrected via REM)

PRE-REGISTERED CRITERIA (Whisper C3722, 2026-05-29):
  T1 (REM-HELPS): ZNE+REM mean error < ZNE-only mean error
                  → REM adds value on top of ZNE
  T2 (THRESHOLD): ZNE+REM mean error < 1.00pp absolute
                  → approaches 1-qubit raw threshold (0.93pp)
  T3 (DEPTH-DOMINANCE): ZNE-only mean error < REM-only mean error at k≥2
                         → gate error dominates over readout error at high depth;
                         ZNE more powerful than REM at k≥2 (but REM still adds value)

  PRE-REGISTERED EXPECTATIONS (Whisper C3722):
    T1 PASS (REM corrects readout which ZNE cannot touch — complementary mechanisms)
    T2 UNCERTAIN (depends on readout error magnitude; may need >0.58pp REM correction)
    T3 PASS (ZNE is designed for gate noise; gate noise dominates at k≥2)

METHODOLOGICAL NOTES:
  - Calibration circuits are appended AFTER main circuits in the same job (same QPU state)
  - The M^{-1} correction can produce small negative probabilities (unphysical) → clip to 0
    and renormalize. This is standard in matrix-inversion REM.
  - Bitstring convention: Qiskit measure_all() → bitstring "q1q0" (most-significant first)
  - We care about P(|11>) = both qubits in state 1 → bitstring "11"
  - Corrected P(|11>) from full 4×4 matrix inversion uses p_corrected[3] (bitstring "11")
  - Calibration circuits go through the same transpilation pipeline as main circuits,
    ensuring M is calibrated for the same physical qubit layout.

Run (simulation preview):    python3 scripts/run_exp27_zne_rem.py
Run (real hardware submit):   python3 scripts/run_exp27_zne_rem.py --submit
Poll + finalize:              python3 scripts/run_exp27_zne_rem.py --finalize <job_id>
"""
import argparse
import json
import numpy as np

EXPERIMENT = "27"
CYCLE = 3722
SHOTS = 4096
P_VALUES = [0.56, 0.90]
K_VALUES = [0, 1, 2, 3, 4]
SCALE_FACTORS = [1, 3]   # 2-point ZNE only (validated optimal in C3722 analysis)
SEED_TRANSPILER = 42
BACKEND_NAME = "ibm_marrakesh"
RESULT_PATH = f"experiments/{EXPERIMENT}-zne-rem-results.json"
JOBID_PATH = f"experiments/{EXPERIMENT}-jobid.txt"
N_MAIN = len(P_VALUES) * len(K_VALUES) * len(SCALE_FACTORS)  # 20

# Historical baselines from Exp 23 (1-qubit raw) and Exp 25b (ZNE-only best)
EXP23_1QUBIT_MEAN = 0.0093  # 0.93pp — THE TARGET TO BEAT
EXP25B_ZNE_ONLY_MEAN = 0.0158  # 1.58pp — our best 2-qubit result (C3722 reanalysis)

# Exp 25b ZNE-only results for direct comparison
EXP25B_ZNE_2PT = {
    (0.56, 0): 0.0395, (0.56, 1): 0.0038, (0.56, 2): 0.0024,
    (0.56, 3): 0.0175, (0.56, 4): 0.0098,
    (0.90, 0): 0.0213, (0.90, 1): 0.0006, (0.90, 2): 0.0041,
    (0.90, 3): 0.0261, (0.90, 4): 0.0461,
}


def ideal_p11(P, k):
    th_a = np.arcsin(np.sqrt(P))
    return float(np.sin((2 * k + 1) * th_a) ** 2)


def build_base_circuit_logical(P, k):
    """Build logical 2-qubit CZ IQAE circuit: A + Q^k (no measurement)."""
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


def build_calibration_circuits_logical():
    """Build 4 readout calibration circuits (prepare |00>,|01>,|10>,|11> and measure).

    Returns list of (label, circuit) tuples. Label indicates prepared state.
    """
    from qiskit import QuantumCircuit
    cals = []
    for idx, (label, q0, q1) in enumerate([
        ("00", 0, 0),
        ("01", 1, 0),  # qubit 0 = 1, qubit 1 = 0 → bitstring "01"
        ("10", 0, 1),  # qubit 0 = 0, qubit 1 = 1 → bitstring "10"
        ("11", 1, 1),
    ]):
        qc = QuantumCircuit(2, 2)
        if q0:
            qc.x(0)
        if q1:
            qc.x(1)
        qc.measure([0, 1], [0, 1])
        cals.append((label, qc))
    return cals


def counts_to_p11(counts, shots):
    """Extract P(|11>) from measurement counts. Bitstring convention: q1q0 (MSB left)."""
    good = 0
    total = 0
    for bitstr, c in counts.items():
        total += c
        bs = bitstr.replace(" ", "")
        if bs[-2:] == "11":
            good += c
    return good / (total if total > 0 else shots)


def counts_to_pvec(counts, shots):
    """Extract full probability vector [p00, p01, p10, p11] from counts.

    Bitstring convention: q1q0 (MSB left). Maps bitstring to index:
    "00"→0, "01"→1, "10"→2, "11"→3.
    """
    bs_to_idx = {"00": 0, "01": 1, "10": 2, "11": 3}
    vec = np.zeros(4)
    total = 0
    for bitstr, c in counts.items():
        total += c
        bs = bitstr.replace(" ", "")[-2:]  # take last 2 bits
        idx = bs_to_idx.get(bs)
        if idx is not None:
            vec[idx] += c
    return vec / (total if total > 0 else shots)


def build_readout_matrix(cal_pvecs):
    """Build 4×4 readout error matrix M from calibration results.

    M[i][j] = P(measure state i | prepare state j)
    cal_pvecs: list of 4 probability vectors in order (|00>, |01>, |10>, |11>)
    Returns M and its inverse M_inv.
    """
    M = np.column_stack(cal_pvecs)  # each cal_pvec is a column
    try:
        M_inv = np.linalg.inv(M)
    except np.linalg.LinAlgError:
        M_inv = np.linalg.pinv(M)
    return M, M_inv


def rem_correct(pvec, M_inv):
    """Apply REM correction using precomputed M_inv.

    Returns corrected probability vector, clipped to [0,1] and renormalized.
    """
    p_corrected = M_inv @ pvec
    p_corrected = np.clip(p_corrected, 0, None)
    norm = p_corrected.sum()
    if norm > 0:
        p_corrected /= norm
    return p_corrected


def zne_2pt(y1, y3):
    """2-point Richardson linear extrapolation to λ=0: (3y1 - y3) / 2."""
    return (3 * y1 - y3) / 2


def build_schedule_for_fakemarrakesh():
    """Build and run circuits on FakeMarrakesh (opt=0 to preserve folding)."""
    from qiskit import QuantumCircuit, transpile
    from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
    backend = FakeMarrakesh()

    schedule_items = []
    # Main circuits: ZNE folded
    for P in P_VALUES:
        for k in K_VALUES:
            base = build_base_circuit_logical(P, k)
            base_inv = base.inverse()
            for scale in SCALE_FACTORS:
                n_folds = (scale - 1) // 2
                qc = QuantumCircuit(2)
                qc.compose(base, inplace=True)
                for _ in range(n_folds):
                    qc.compose(base_inv, inplace=True)
                    qc.compose(base, inplace=True)
                qc.measure_all()
                qc_t = transpile(qc, backend=backend, optimization_level=0,
                                 seed_transpiler=SEED_TRANSPILER)
                schedule_items.append(("main", P, k, scale, qc_t))

    # Calibration circuits
    cal_defs = build_calibration_circuits_logical()
    for (label, qc_cal) in cal_defs:
        qc_t = transpile(qc_cal, backend=backend, optimization_level=0,
                         seed_transpiler=SEED_TRANSPILER)
        schedule_items.append(("cal", label, None, None, qc_t))

    return schedule_items, backend


def build_schedule_for_hardware():
    """Build circuits for real QPU submission (fold-then-transpile-at-opt0)."""
    from qiskit import QuantumCircuit, transpile
    from qiskit_ibm_runtime import QiskitRuntimeService
    service = QiskitRuntimeService()
    backend = service.backend(BACKEND_NAME)

    schedule_items = []
    print(f"\n=== Building main ZNE circuits (2-point: λ=1,3) ===")
    for P in P_VALUES:
        for k in K_VALUES:
            base = build_base_circuit_logical(P, k)
            base_inv = base.inverse()
            for scale in SCALE_FACTORS:
                n_folds = (scale - 1) // 2
                qc = QuantumCircuit(2)
                qc.compose(base, inplace=True)
                for _ in range(n_folds):
                    qc.compose(base_inv, inplace=True)
                    qc.compose(base, inplace=True)
                qc.measure_all()
                qc_hw = transpile(qc, backend=backend, optimization_level=0,
                                  seed_transpiler=SEED_TRANSPILER)
                ops = qc_hw.count_ops()
                cz = ops.get("cz", 0) + ops.get("ecr", 0) + ops.get("cx", 0)
                print(f"  P={P} k={k} λ={scale}: depth={qc_hw.depth()} 2q={cz}")
                schedule_items.append(("main", P, k, scale, qc_hw))

    print(f"\n=== Building readout calibration circuits ===")
    cal_defs = build_calibration_circuits_logical()
    for (label, qc_cal) in cal_defs:
        qc_hw = transpile(qc_cal, backend=backend, optimization_level=0,
                          seed_transpiler=SEED_TRANSPILER)
        ops_cal = qc_hw.count_ops()
        print(f"  Calibration |{label}>: depth={qc_hw.depth()} ops={dict(ops_cal)}")
        schedule_items.append(("cal", label, None, None, qc_hw))

    print(f"\nTotal circuits: {len(schedule_items)} "
          f"({N_MAIN} main + {len(cal_defs)} calibration)")
    return schedule_items, backend


def submit_hardware(schedule_items, backend):
    """Submit all circuits (main + calibration) in a single batched job."""
    from qiskit_ibm_runtime import SamplerV2
    sampler = SamplerV2(mode=backend)
    sampler.options.default_shots = SHOTS
    circuits = [item[4] for item in schedule_items]
    job = sampler.run([(qc,) for qc in circuits])
    job_id = job.job_id()
    with open(JOBID_PATH, "w") as f:
        f.write(job_id + "\n")
    print(f"\n  SUBMITTED. job_id = {job_id}")
    print(f"  Total circuits: {len(circuits)} ({N_MAIN} main + 4 cal)")
    print(f"  Saved to {JOBID_PATH}")
    return job_id


def get_counts_from_job(job_id, n_circuits):
    """Fetch counts for all circuits from completed job."""
    from qiskit_ibm_runtime import QiskitRuntimeService
    service = QiskitRuntimeService()
    job = service.job(job_id)
    status = job.status()
    print(f"  job {job_id} status: {status}")
    if str(status) not in ("DONE", "JobStatus.DONE"):
        return None, str(status)
    res = job.result()
    all_counts = []
    for i in range(n_circuits):
        databin = res[i].data
        reg = list(databin.__dict__.keys())[0]
        counts = getattr(databin, reg).get_counts()
        all_counts.append(counts)
    return all_counts, "DONE"


def get_counts_from_fakemarrakesh(schedule_items, backend):
    """Run circuits on FakeMarrakesh and extract counts."""
    from qiskit_aer.primitives import SamplerV2 as AerSampler
    from qiskit_aer.noise import NoiseModel
    nm = NoiseModel.from_backend(backend)
    sampler = AerSampler(options={
        "backend_options": {"noise_model": nm},
        "run_options": {"shots": SHOTS, "seed": SEED_TRANSPILER},
    })
    circuits = [item[4] for item in schedule_items]
    res = sampler.run([(c,) for c in circuits]).result()
    all_counts = []
    for i in range(len(circuits)):
        data = res[i].data
        reg_name = list(data.__dict__.keys())[0]
        counts = getattr(data, reg_name).get_counts()
        all_counts.append(counts)
    return all_counts


def analyze(schedule_items, all_counts, job_id=None):
    """Analyze results: compute Raw, ZNE-only, REM-only, ZNE+REM for all P×k cells.

    schedule_items: list of ("main", P, k, scale, qc) or ("cal", label, None, None, qc)
    all_counts: list of count dicts, parallel to schedule_items
    """
    # Separate main and calibration
    main_data = {}   # (P, k, scale) → counts
    cal_data = {}    # label → counts

    for item, counts in zip(schedule_items, all_counts):
        if item[0] == "main":
            _, P, k, scale, _ = item
            main_data[(P, k, scale)] = counts
        elif item[0] == "cal":
            _, label, _, _, _ = item
            cal_data[label] = counts

    # Build REM calibration matrix
    cal_pvecs = []
    for label in ["00", "01", "10", "11"]:
        pvec = counts_to_pvec(cal_data[label], SHOTS)
        cal_pvecs.append(pvec)
        print(f"  Cal |{label}> → pvec = {pvec.round(4)}")

    M, M_inv = build_readout_matrix(cal_pvecs)
    print(f"\n  Readout error matrix M:")
    print(f"  {M.round(4)}")
    readout_p11_error = M[3][3]  # P(measure 11 | prepare 11)
    false_pos_rate = M[3][0]     # P(measure 11 | prepare 00)
    print(f"\n  Readout accuracy at |11>: {readout_p11_error:.4f}  ({readout_p11_error*100:.2f}%)")
    print(f"  False positive rate (P(measure 11 | prepare 00)): {false_pos_rate:.4f}")

    # Analyze main circuits
    rows = []
    print(f"\n{'P':>5} {'k':>3} | {'Ideal':>8} "
          f"{'Raw':>8} {'ZNE':>8} {'REM':>8} {'ZNE+REM':>8} | "
          f"{'|raw|':>7} {'|zne|':>7} {'|rem|':>7} {'|z+r|':>7} | "
          f"Exp25b_ZNE")
    print("-" * 110)

    errors = {"raw": [], "zne": [], "rem": [], "zne_rem": []}

    for P in P_VALUES:
        for k in K_VALUES:
            ide = ideal_p11(P, k)

            counts_lam1 = main_data[(P, k, 1)]
            counts_lam3 = main_data[(P, k, 3)]

            # Raw: λ=1, no correction
            raw_p11 = counts_to_p11(counts_lam1, SHOTS)
            # ZNE-only: 2-point extrapolation, no REM
            zne_lam3 = counts_to_p11(counts_lam3, SHOTS)
            zne_only = zne_2pt(raw_p11, zne_lam3)
            # REM-only: readout correction at λ=1, no ZNE
            raw_pvec = counts_to_pvec(counts_lam1, SHOTS)
            rem_pvec = rem_correct(raw_pvec, M_inv)
            rem_only_p11 = float(rem_pvec[3])
            # ZNE+REM: apply REM correction to both λ=1 and λ=3, then ZNE
            lam3_pvec = counts_to_pvec(counts_lam3, SHOTS)
            rem_lam3 = float(rem_correct(lam3_pvec, M_inv)[3])
            zne_rem = zne_2pt(rem_only_p11, rem_lam3)

            err_raw = abs(raw_p11 - ide)
            err_zne = abs(zne_only - ide)
            err_rem = abs(rem_only_p11 - ide)
            err_zne_rem = abs(zne_rem - ide)

            errors["raw"].append(err_raw)
            errors["zne"].append(err_zne)
            errors["rem"].append(err_rem)
            errors["zne_rem"].append(err_zne_rem)

            exp25b_ref = EXP25B_ZNE_2PT.get((P, k), "?")

            print(f"{P:>5.2f} {k:>3d} | {ide:>8.4f} "
                  f"{raw_p11:>8.4f} {zne_only:>8.4f} {rem_only_p11:>8.4f} {zne_rem:>8.4f} | "
                  f"{err_raw:>7.4f} {err_zne:>7.4f} {err_rem:>7.4f} {err_zne_rem:>7.4f} | "
                  f"{exp25b_ref}")

            rows.append({
                "P": P, "k": k,
                "ideal": round(ide, 4),
                "raw_p11": round(raw_p11, 4),
                "zne_lam1": round(raw_p11, 4),
                "zne_lam3": round(zne_lam3, 4),
                "zne_only": round(zne_only, 4),
                "rem_only": round(rem_only_p11, 4),
                "zne_rem": round(zne_rem, 4),
                "err_raw": round(err_raw, 4),
                "err_zne": round(err_zne, 4),
                "err_rem": round(err_rem, 4),
                "err_zne_rem": round(err_zne_rem, 4),
                "exp25b_zne_2pt_ref": exp25b_ref,
            })

    print("-" * 110)

    mean_raw = np.mean(errors["raw"])
    mean_zne = np.mean(errors["zne"])
    mean_rem = np.mean(errors["rem"])
    mean_zne_rem = np.mean(errors["zne_rem"])

    print(f"\n{'':>8}  Raw: {mean_raw*100:.2f}pp | ZNE-only: {mean_zne*100:.2f}pp | "
          f"REM-only: {mean_rem*100:.2f}pp | ZNE+REM: {mean_zne_rem*100:.2f}pp")

    # Evaluate pre-registered criteria
    print(f"\n=== PRE-REGISTERED CRITERIA ===")

    # T1: ZNE+REM < ZNE-only
    t1_pass = mean_zne_rem < mean_zne
    print(f"T1 (REM-HELPS): ZNE+REM ({mean_zne_rem*100:.2f}pp) < ZNE-only ({mean_zne*100:.2f}pp) "
          f"→ {'PASS' if t1_pass else 'FAIL'}")

    # T2: ZNE+REM < 1.00pp
    t2_pass = mean_zne_rem < 0.01
    print(f"T2 (THRESHOLD): ZNE+REM ({mean_zne_rem*100:.2f}pp) < 1.00pp "
          f"→ {'PASS' if t2_pass else 'FAIL'}")
    one_qubit_beat = mean_zne_rem < EXP23_1QUBIT_MEAN
    print(f"   (Bonus: ZNE+REM vs 1-qubit raw {EXP23_1QUBIT_MEAN*100:.2f}pp: "
          f"{'BETTER' if one_qubit_beat else 'STILL WORSE'})")

    # T3: ZNE-only < REM-only at k≥2
    zne_deep = [errors["zne"][i] for i, (P, k) in
                enumerate([(P, k) for P in P_VALUES for k in K_VALUES]) if k >= 2]
    rem_deep = [errors["rem"][i] for i, (P, k) in
                enumerate([(P, k) for P in P_VALUES for k in K_VALUES]) if k >= 2]
    t3_pass = np.mean(zne_deep) < np.mean(rem_deep)
    print(f"T3 (DEPTH-DOMINANCE): ZNE-only at k≥2 ({np.mean(zne_deep)*100:.2f}pp) < "
          f"REM-only at k≥2 ({np.mean(rem_deep)*100:.2f}pp) "
          f"→ {'PASS' if t3_pass else 'FAIL'}")

    print(f"\n  vs 1-qubit raw baseline (Exp 23): {EXP23_1QUBIT_MEAN*100:.2f}pp")
    print(f"  vs ZNE-only best (Exp 25b):        {EXP25B_ZNE_ONLY_MEAN*100:.2f}pp")

    result = {
        "experiment": EXPERIMENT,
        "title": "ZNE + Readout Error Mitigation (REM) — Breaking the 1-Qubit Barrier",
        "cycle": CYCLE,
        "backend": BACKEND_NAME,
        "job_id": job_id,
        "params": {
            "shots": SHOTS,
            "P_values": P_VALUES,
            "k_values": K_VALUES,
            "scale_factors": SCALE_FACTORS,
            "method": "2-point ZNE (λ=1,3) + 4×4 matrix-inversion REM",
            "circuits_total": len(schedule_items),
            "main_circuits": N_MAIN,
            "cal_circuits": 4,
        },
        "preregistered_criteria": {
            "T1": "ZNE+REM mean error < ZNE-only mean error (REM adds value on top of ZNE)",
            "T2": "ZNE+REM mean error < 1.00pp (approaches 1-qubit raw threshold)",
            "T3": "ZNE-only mean error < REM-only mean error at k>=2 (gate error dominates at depth)",
        },
        "readout_calibration": {
            "M": M.round(4).tolist(),
            "M_inv": M_inv.round(6).tolist(),
            "readout_p11_accuracy": round(readout_p11_error, 4),
            "false_positive_rate": round(false_pos_rate, 4),
        },
        "summary": {
            "mean_raw_pp": round(float(mean_raw) * 100, 2),
            "mean_zne_only_pp": round(float(mean_zne) * 100, 2),
            "mean_rem_only_pp": round(float(mean_rem) * 100, 2),
            "mean_zne_rem_pp": round(float(mean_zne_rem) * 100, 2),
            "exp23_1qubit_raw_pp": round(EXP23_1QUBIT_MEAN * 100, 2),
            "T1": "PASS" if t1_pass else "FAIL",
            "T2": "PASS" if t2_pass else "FAIL",
            "T3": "PASS" if t3_pass else "FAIL",
            "beat_1qubit_raw": bool(one_qubit_beat),
        },
        "rows": rows,
    }

    with open(RESULT_PATH, "w") as f:
        json.dump(result, f, indent=4)
    print(f"\n  Results saved to {RESULT_PATH}")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--submit", action="store_true", help="Submit to real QPU")
    parser.add_argument("--finalize", metavar="JOB_ID", help="Fetch and analyze QPU results")
    parser.add_argument("--sim-only", action="store_true", help="Run simulation only")
    args = parser.parse_args()

    if args.finalize:
        job_id = args.finalize
        print(f"\n=== Fetching Exp {EXPERIMENT} results (job {job_id}) ===")
        # Rebuild schedule to get item metadata (order matters)
        schedule_items, backend = build_schedule_for_hardware()
        all_counts, status = get_counts_from_job(job_id, len(schedule_items))
        if all_counts is None:
            print(f"  Job not done yet (status: {status}). Try again later.")
            return
        print(f"\n=== Analyzing {len(all_counts)} circuits ===")
        analyze(schedule_items, all_counts, job_id=job_id)

    elif args.submit:
        print(f"\n=== Exp {EXPERIMENT}: Building hardware schedule ===")
        schedule_items, backend = build_schedule_for_hardware()
        print(f"\n=== Submitting to {BACKEND_NAME} ===")
        submit_hardware(schedule_items, backend)
        print(f"\n  When job completes, run:")
        print(f"    python3 scripts/run_exp27_zne_rem.py --finalize <job_id>")

    else:
        print(f"\n=== Exp {EXPERIMENT}: FakeMarrakesh simulation preview ===")
        schedule_items, backend = build_schedule_for_fakemarrakesh()
        all_counts = get_counts_from_fakemarrakesh(schedule_items, backend)
        print(f"\n=== Simulation results (FakeMarrakesh) ===")
        analyze(schedule_items, all_counts, job_id="FakeMarrakesh-sim")


if __name__ == "__main__":
    main()
