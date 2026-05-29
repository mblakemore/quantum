"""Exp 28: The Gate-Overhead Sign Rule for NISQ Error Mitigation (Whisper C3724).

SCIENTIFIC MOTIVATION (see experiments/28-gate-overhead-sign-rule-preregistration.md):
  Finding 7 ("mitigation is largely futile") and Exp 25-27 ("ZNE+REM = 59% reduction")
  appear to contradict, but Finding 7's data was CROSS-DAY and CROSS-CIRCUIT — and Finding 7
  itself states "±7pp daily drift dwarfs any mitigation gain." Confounded by its own standard.

  HYPOTHESIS (Gate-Overhead Sign Rule): the SIGN of a mitigation technique's effect is
  governed by its residual PAYLOAD-GATE OVERHEAD, not by the error source it targets.
    - zero added payload gates (post-processing REM, extrapolate-away ZNE) -> net POSITIVE
    - residual injected gates (TREM X-twirl, DD pulses, PT framing) -> net NEGATIVE / null

  CONTROLLED TEST (Pearl do(mechanism)): hold the target error source FIXED (readout) and
  vary ONLY the mechanism, on the SAME circuits under ONE calibration snapshot (co-submitted):
      Raw   : no readout correction, 0 added gates  (same-day floor; fix #2 reference)
      REM   : M^-1 post-processing of counts, 0 added gates  -> predict net POSITIVE
      TREM  : X-twirl symmetrization before readout, gates injected -> predict net NEGATIVE/null
  REM vs TREM = identical target (readout), opposite gate overhead. Any gap under one
  calibration snapshot is MECHANISM, not weather — the confound Finding 7 could not remove.

  Full ZNE / ZNE+REM arms retained from Exp 27 for the complete picture and direct
  comparability (P, k grid unchanged).

DESIGN:
  P in {0.56, 0.90}, k in {0,1,2,3,4}, lambda in {1,3} (2-point ZNE).
  TREM mask-00 == raw lambda=1 circuit (reused, not re-submitted).
  TREM mask-11 = X on both qubits before measure, XOR-corrected classically (10 new circuits).
  4 readout calibration circuits.
  Total: 20 ZNE main + 10 TREM(mask-11) + 4 cal = 34 circuits. 4096 shots each.

PRE-REGISTERED CRITERIA (Whisper C3724, FIXED before submission):
  T1 (REM-HELPS):  mean_err(REM)  < mean_err(Raw)
  T2 (SIGN RULE):  mean_err(TREM) > mean_err(REM)   [headline — isolates gate injection]
  T3 (TREM-NULL):  mean_err(TREM) >= mean_err(Raw) - 0.30pp
  Reconciliation: if T1 ^ T2 PASS, Finding 7 is REFINED:
    "gate-injecting mitigation futile; zero-gate-overhead mitigation works" (under matched calib).
  Falsification: T2 FAIL (TREM <= REM) => sign NOT governed by gate overhead => rule REJECTED.

Run (sim preview):   python3 scripts/run_exp28_gate_overhead_sign_rule.py
Run (hardware):      python3 scripts/run_exp28_gate_overhead_sign_rule.py --submit
Finalize:            python3 scripts/run_exp28_gate_overhead_sign_rule.py --finalize <job_id>
"""
import argparse
import json
import os
import numpy as np

EXPERIMENT = "28"
CYCLE = 3724
SHOTS = 4096
P_VALUES = [0.56, 0.90]
K_VALUES = [0, 1, 2, 3, 4]
SCALE_FACTORS = [1, 3]
TREM_MASKS = ["11"]   # mask-00 reused from raw lambda=1; only mask-11 submitted
SEED_TRANSPILER = 42
BACKEND_NAME = "ibm_marrakesh"
RESULT_PATH = f"experiments/{EXPERIMENT}-gate-overhead-sign-rule-results.json"
JOBID_PATH = f"experiments/{EXPERIMENT}-jobid.txt"
CALIB_PATH = f"experiments/{EXPERIMENT}-calibration.json"
N_MAIN = len(P_VALUES) * len(K_VALUES) * len(SCALE_FACTORS)        # 20
N_TREM = len(P_VALUES) * len(K_VALUES) * len(TREM_MASKS)          # 10

EXP23_1QUBIT_MEAN = 0.0093  # 0.93pp 1-qubit raw baseline


def ideal_p11(P, k):
    th_a = np.arcsin(np.sqrt(P))
    return float(np.sin((2 * k + 1) * th_a) ** 2)


def build_base_circuit_logical(P, k):
    """2-qubit CZ IQAE circuit: A + Q^k (no measurement)."""
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


def build_zne_circuit(P, k, scale):
    """ZNE-folded measured circuit (fold base*base_inv n_folds times)."""
    from qiskit import QuantumCircuit
    base = build_base_circuit_logical(P, k)
    base_inv = base.inverse()
    n_folds = (scale - 1) // 2
    qc = QuantumCircuit(2)
    qc.compose(base, inplace=True)
    for _ in range(n_folds):
        qc.compose(base_inv, inplace=True)
        qc.compose(base, inplace=True)
    qc.measure_all()
    return qc


def build_trem_circuit(P, k, mask):
    """TREM arm: base circuit (lambda=1) + X-twirl (mask) injected before measurement.

    mask is a 2-char string for (q0, q1). Injecting X before readout is the GATE-INJECTING
    mechanism under test. Measured bits are XOR-corrected by the mask in post-processing.
    """
    from qiskit import QuantumCircuit
    base = build_base_circuit_logical(P, k)
    qc = QuantumCircuit(2)
    qc.compose(base, inplace=True)
    # mask string convention: mask[0]=q0 flip, mask[1]=q1 flip
    if mask[0] == "1":
        qc.x(0)
    if mask[1] == "1":
        qc.x(1)
    qc.measure_all()
    return qc


def build_calibration_circuits_logical():
    from qiskit import QuantumCircuit
    cals = []
    for (label, q0, q1) in [("00", 0, 0), ("01", 1, 0), ("10", 0, 1), ("11", 1, 1)]:
        qc = QuantumCircuit(2, 2)
        if q0:
            qc.x(0)
        if q1:
            qc.x(1)
        qc.measure([0, 1], [0, 1])
        cals.append((label, qc))
    return cals


def counts_to_p11(counts, shots):
    good, total = 0, 0
    for bitstr, c in counts.items():
        total += c
        if bitstr.replace(" ", "")[-2:] == "11":
            good += c
    return good / (total if total > 0 else shots)


def counts_to_pvec(counts, shots):
    bs_to_idx = {"00": 0, "01": 1, "10": 2, "11": 3}
    vec = np.zeros(4)
    total = 0
    for bitstr, c in counts.items():
        total += c
        idx = bs_to_idx.get(bitstr.replace(" ", "")[-2:])
        if idx is not None:
            vec[idx] += c
    return vec / (total if total > 0 else shots)


def xor_correct_pvec(pvec, mask):
    """Undo a deterministic readout twirl: measured value = true XOR mask.

    For 2 qubits with index map 00->0,01->1,10->2,11->3, XOR by mask permutes indices.
    """
    mask_int = int(mask[::-1], 2) if False else int(mask, 2)
    # build permutation: corrected[true] = measured[true XOR mask]
    corrected = np.zeros(4)
    for true_idx in range(4):
        meas_idx = true_idx ^ mask_int
        corrected[true_idx] = pvec[meas_idx]
    return corrected


def build_readout_matrix(cal_pvecs):
    M = np.column_stack(cal_pvecs)
    try:
        M_inv = np.linalg.inv(M)
    except np.linalg.LinAlgError:
        M_inv = np.linalg.pinv(M)
    return M, M_inv


def rem_correct(pvec, M_inv):
    p = np.clip(M_inv @ pvec, 0, None)
    s = p.sum()
    return p / s if s > 0 else p


def zne_2pt(y1, y3):
    return (3 * y1 - y3) / 2


# ---------------------------------------------------------------------------
# Schedule construction
# ---------------------------------------------------------------------------
def _build_schedule(transpile_fn):
    """Return schedule_items using a transpile function (P,k,scale or mask circuits)."""
    items = []
    for P in P_VALUES:
        for k in K_VALUES:
            for scale in SCALE_FACTORS:
                qc = transpile_fn(build_zne_circuit(P, k, scale))
                items.append(("main", P, k, scale, qc))
    for P in P_VALUES:
        for k in K_VALUES:
            for mask in TREM_MASKS:
                qc = transpile_fn(build_trem_circuit(P, k, mask))
                items.append(("trem", P, k, mask, qc))
    for (label, qc_cal) in build_calibration_circuits_logical():
        items.append(("cal", label, None, None, transpile_fn(qc_cal)))
    return items


def build_schedule_for_hardware():
    from qiskit import transpile
    from qiskit_ibm_runtime import QiskitRuntimeService
    service = QiskitRuntimeService()
    backend = service.backend(BACKEND_NAME)

    def tfn(qc):
        return transpile(qc, backend=backend, optimization_level=0,
                         seed_transpiler=SEED_TRANSPILER)

    items = _build_schedule(tfn)
    print(f"  Built {len(items)} circuits "
          f"({N_MAIN} ZNE main + {N_TREM} TREM + 4 cal)")
    for it in items:
        if it[0] == "trem":
            ops = it[4].count_ops()
            cz = ops.get("cz", 0) + ops.get("ecr", 0) + ops.get("cx", 0)
            print(f"  TREM P={it[1]} k={it[2]} mask={it[3]}: depth={it[4].depth()} 2q={cz} "
                  f"1q-x={ops.get('x', 0) + ops.get('sx', 0)}")
    return items, backend


def build_schedule_for_fakemarrakesh():
    from qiskit import transpile
    from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
    backend = FakeMarrakesh()

    def tfn(qc):
        return transpile(qc, backend=backend, optimization_level=0,
                         seed_transpiler=SEED_TRANSPILER)

    return _build_schedule(tfn), backend


def submit_hardware(schedule_items, backend):
    from qiskit_ibm_runtime import SamplerV2
    sampler = SamplerV2(mode=backend)
    sampler.options.default_shots = SHOTS
    circuits = [item[4] for item in schedule_items]
    job = sampler.run([(qc,) for qc in circuits])
    job_id = job.job_id()
    with open(JOBID_PATH, "w") as f:
        f.write(job_id + "\n")
    try:
        from calibration_snapshot import capture_calibration
        phys = None
        try:
            phys = schedule_items[0][4].layout.final_index_layout()
        except Exception:
            phys = None
        snap = capture_calibration(backend, physical_qubits=phys)
        with open(CALIB_PATH, "w") as f:
            json.dump(snap, f, indent=4, default=str)
        print(f"  Calibration snapshot saved (updated {snap.get('last_update_date')})")
    except Exception as e:
        print(f"  [warn] calibration snapshot skipped: {e}")
    print(f"\n  SUBMITTED. job_id = {job_id}  ({len(circuits)} circuits)")
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


def get_counts_from_fakemarrakesh(schedule_items, backend):
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
    main_data, trem_data, cal_data = {}, {}, {}
    for item, counts in zip(schedule_items, all_counts):
        if item[0] == "main":
            main_data[(item[1], item[2], item[3])] = counts
        elif item[0] == "trem":
            trem_data[(item[1], item[2], item[3])] = counts
        elif item[0] == "cal":
            cal_data[item[1]] = counts

    cal_pvecs = [counts_to_pvec(cal_data[l], SHOTS) for l in ["00", "01", "10", "11"]]
    M, M_inv = build_readout_matrix(cal_pvecs)
    print(f"\n  Readout matrix M (diag = accuracy):\n  {M.round(4)}")
    print(f"  Readout accuracy |11>: {M[3][3]*100:.2f}%  |  false-pos P(11|00): {M[3][0]:.4f}")

    errors = {"raw": [], "rem": [], "trem": [], "zne": [], "zne_rem": []}
    rows = []
    print(f"\n{'P':>5} {'k':>3} | {'ideal':>7} {'raw':>7} {'REM':>7} {'TREM':>7} {'ZNE':>7} {'Z+R':>7}"
          f" | {'|raw|':>6} {'|REM|':>6} {'|TREM|':>6}")
    print("-" * 96)
    for P in P_VALUES:
        for k in K_VALUES:
            ide = ideal_p11(P, k)
            c1 = main_data[(P, k, 1)]
            c3 = main_data[(P, k, 3)]

            raw_pvec = counts_to_pvec(c1, SHOTS)
            raw_p11 = float(raw_pvec[3])

            # REM: M^-1 post-processing (0 added gates)
            rem_p11 = float(rem_correct(raw_pvec, M_inv)[3])

            # TREM: twirl-symmetrize (gates injected), NO M^-1.
            #   mask-00 == raw; mask-11 from trem_data, XOR-corrected.
            mask00_pvec = raw_pvec
            mask11_meas = counts_to_pvec(trem_data[(P, k, "11")], SHOTS)
            mask11_corr = xor_correct_pvec(mask11_meas, "11")
            trem_pvec = (mask00_pvec + mask11_corr) / 2.0
            trem_p11 = float(trem_pvec[3])

            # ZNE (extrapolate-away gates) and ZNE+REM (from Exp27 method)
            zne_p11 = zne_2pt(raw_p11, float(counts_to_pvec(c3, SHOTS)[3]))
            rem_l3 = float(rem_correct(counts_to_pvec(c3, SHOTS), M_inv)[3])
            zne_rem = zne_2pt(rem_p11, rem_l3)

            e = {"raw": abs(raw_p11 - ide), "rem": abs(rem_p11 - ide),
                 "trem": abs(trem_p11 - ide), "zne": abs(zne_p11 - ide),
                 "zne_rem": abs(zne_rem - ide)}
            for key in errors:
                errors[key].append(e[key])

            print(f"{P:>5.2f} {k:>3d} | {ide:>7.4f} {raw_p11:>7.4f} {rem_p11:>7.4f} "
                  f"{trem_p11:>7.4f} {zne_p11:>7.4f} {zne_rem:>7.4f} | "
                  f"{e['raw']:>6.4f} {e['rem']:>6.4f} {e['trem']:>6.4f}")
            rows.append({"P": P, "k": k, "ideal": round(ide, 4),
                         "raw_p11": round(raw_p11, 4), "rem_p11": round(rem_p11, 4),
                         "trem_p11": round(trem_p11, 4), "zne_p11": round(zne_p11, 4),
                         "zne_rem_p11": round(zne_rem, 4),
                         "err_raw": round(e["raw"], 4), "err_rem": round(e["rem"], 4),
                         "err_trem": round(e["trem"], 4), "err_zne": round(e["zne"], 4),
                         "err_zne_rem": round(e["zne_rem"], 4)})
    print("-" * 96)

    m = {key: float(np.mean(v)) for key, v in errors.items()}
    print(f"\n  MEAN ERROR: raw={m['raw']*100:.2f}pp  REM={m['rem']*100:.2f}pp  "
          f"TREM={m['trem']*100:.2f}pp  ZNE={m['zne']*100:.2f}pp  ZNE+REM={m['zne_rem']*100:.2f}pp")

    # Pre-registered criteria
    t1 = m["rem"] < m["raw"]
    t2 = m["trem"] > m["rem"]
    t3 = m["trem"] >= m["raw"] - 0.003
    print(f"\n=== PRE-REGISTERED CRITERIA (Gate-Overhead Sign Rule) ===")
    print(f"T1 (REM-HELPS):  REM {m['rem']*100:.2f}pp < raw {m['raw']*100:.2f}pp"
          f"  -> {'PASS' if t1 else 'FAIL'}")
    print(f"T2 (SIGN RULE):  TREM {m['trem']*100:.2f}pp > REM {m['rem']*100:.2f}pp"
          f"  -> {'PASS' if t2 else 'FAIL'}  [headline]")
    print(f"T3 (TREM-NULL):  TREM {m['trem']*100:.2f}pp >= raw-0.30pp "
          f"({(m['raw']-0.003)*100:.2f}pp)  -> {'PASS' if t3 else 'FAIL'}")
    reconciled = t1 and t2
    print(f"\nRECONCILIATION: {'CONFIRMED' if reconciled else 'NOT confirmed'} — "
          f"{'Finding 7 REFINED: gate-injecting mitigation futile, zero-gate-overhead works'
             if reconciled else 'sign rule not supported by this run'}")
    print(f"  REM-Raw (post-proc effect): {(m['rem']-m['raw'])*100:+.2f}pp  |  "
          f"TREM-Raw (gate-inject effect): {(m['trem']-m['raw'])*100:+.2f}pp")

    result = {
        "experiment": EXPERIMENT,
        "title": "The Gate-Overhead Sign Rule for NISQ Error Mitigation",
        "cycle": CYCLE, "backend": BACKEND_NAME, "job_id": job_id,
        "hypothesis": "Sign of a mitigation's effect is governed by residual payload-gate "
                      "overhead, not the targeted error source. Controlled test holds target "
                      "(readout) fixed, varies mechanism (Raw/REM/TREM) under one calib snapshot.",
        "params": {"shots": SHOTS, "P_values": P_VALUES, "k_values": K_VALUES,
                   "scale_factors": SCALE_FACTORS, "trem_masks": TREM_MASKS,
                   "circuits_total": len(schedule_items)},
        "preregistered_criteria": {
            "T1": "mean_err(REM) < mean_err(Raw)",
            "T2": "mean_err(TREM) > mean_err(REM)  [headline: isolates gate injection]",
            "T3": "mean_err(TREM) >= mean_err(Raw) - 0.30pp",
            "reconciliation": "T1 AND T2 => Finding 7 refined (gate-injecting futile; "
                              "zero-gate-overhead works, under matched calibration)",
            "falsification": "T2 FAIL (TREM <= REM) => rule rejected",
        },
        "calibration": _load_calibration_snapshot(),
        "readout_calibration": {"M": M.round(4).tolist(),
                                "readout_p11_accuracy": round(float(M[3][3]), 4),
                                "false_positive_rate": round(float(M[3][0]), 4)},
        "summary": {
            "mean_raw_pp": round(m["raw"] * 100, 2),
            "mean_rem_pp": round(m["rem"] * 100, 2),
            "mean_trem_pp": round(m["trem"] * 100, 2),
            "mean_zne_pp": round(m["zne"] * 100, 2),
            "mean_zne_rem_pp": round(m["zne_rem"] * 100, 2),
            "rem_minus_raw_pp": round((m["rem"] - m["raw"]) * 100, 2),
            "trem_minus_raw_pp": round((m["trem"] - m["raw"]) * 100, 2),
            "T1": "PASS" if t1 else "FAIL",
            "T2": "PASS" if t2 else "FAIL",
            "T3": "PASS" if t3 else "FAIL",
            "reconciliation_confirmed": bool(reconciled),
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
        print(f"\n=== Exp {EXPERIMENT}: building hardware schedule ===")
        schedule_items, backend = build_schedule_for_hardware()
        print(f"\n=== Submitting to {BACKEND_NAME} ===")
        jid = submit_hardware(schedule_items, backend)
        print(f"\n  Finalize with:  python3 scripts/run_exp28_gate_overhead_sign_rule.py "
              f"--finalize {jid}")
    else:
        print(f"\n=== Exp {EXPERIMENT}: FakeMarrakesh simulation preview ===")
        schedule_items, backend = build_schedule_for_fakemarrakesh()
        all_counts = get_counts_from_fakemarrakesh(schedule_items, backend)
        analyze(schedule_items, all_counts, job_id="FakeMarrakesh-sim")


if __name__ == "__main__":
    main()
