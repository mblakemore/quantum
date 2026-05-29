"""Exp 30: Gate-Count vs Duration — decomposing the Exp 29 dose-response law (Whisper C3734).

SELF-AUDIT MOTIVATION (see experiments/30-gatecount-vs-duration-decomposition-preregistration.md):
  Exp 29 (C3726) reported a "Gate-Overhead Dose-Response Law": error rises monotonically with
  the NUMBER of injected residual 2q gates (rho=1.0, 0.264 pp/2q). But each injected CZ-pair
  adds, in PERFECT LOCKSTEP, two physically distinct causes:
     H_count    : a discrete per-gate error increment           (the named "gate overhead")
     H_duration : ~2*t_CZ of extra wall-time => more T1/T2 decoherence on the payload qubits
  added_2q_gates = 2D and added_duration ~ 2D*t_CZ are collinear with r=1, so rho=1.0 is
  GUARANTEED BY CONSTRUCTION. The law is NOT identified between gate-count and duration --
  the exact single-driver non-identification flaw Whisper flagged in Ember's IQAE sweep (C3732).

  THE do() THAT SEVERS THE COLLINEARITY: run two dose ladders under one calib snapshot, matched
  at each dose to the SAME added wall-time but differing in gate count:
     GATE arm (= Exp 29): D identity CZ-pairs  -> 2D gates, +~2D*t_CZ duration
     IDLE arm (new)     : barrier-fenced delay  -> 0 gates,  +~2D*t_CZ duration (MATCHED)
  IDLE slope            = pure duration/decoherence marginal cost (gate count fixed at 0).
  GATE - IDLE @ matched = gate-count-specific marginal cost (duration held equal) <- the
                          quantity Exp 29 claimed to measure but could not.

PRE-REGISTERED CRITERIA (Whisper C3734, FIXED before submission):
  T1 (DURATION IS A CAUSE):       slope_idle > 0 AND mean_err_idle(D6)-mean_err_idle(D0) > 0.30pp
  T2 (GATE-SPECIFIC EXCESS):      mean_err_gate(D6)-mean_err_idle(D6) > 0.30pp AND slope_gate>slope_idle
  T3 (survives REM):              REM gate-vs-idle excess at D6 > 0
  VERDICT: T2 PASS => Exp29 law SURVIVES (gate count a cause beyond duration; decompose cost).
           T2 FAIL & T1 PASS => Exp29 law is substantially a DURATION law; C3726 over-claimed.
           T1 FAIL & T2 PASS => effect is ~pure gate-count; original framing vindicated.
  VOID CHECK: if IDLE vs GATE transpiled added-duration differ >5% at any dose, run is VOID.

Run (sim preview):   python3 scripts/run_exp30_gatecount_vs_duration.py
Run (hardware):      python3 scripts/run_exp30_gatecount_vs_duration.py --submit
Finalize:            python3 scripts/run_exp30_gatecount_vs_duration.py --finalize <job_id>
"""
import argparse
import json
import os
import numpy as np

EXPERIMENT = "30"
CYCLE = 3734
SHOTS = 4096
P_VALUES = [0.56, 0.90]
K_VALUES = [0, 1, 2, 3, 4]
DOSES = [0, 2, 4, 6]            # injected identity CZ-pairs (GATE) / matched delay units (IDLE)
SEED_TRANSPILER = 42
BACKEND_NAME = "ibm_marrakesh"
RESULT_PATH = f"experiments/{EXPERIMENT}-gatecount-vs-duration-decomposition-results.json"
JOBID_PATH = f"experiments/{EXPERIMENT}-jobid.txt"
CALIB_PATH = f"experiments/{EXPERIMENT}-calibration.json"
DURATION_TOL = 0.05            # +-5% match tolerance (void check)


def ideal_p11(P, k):
    th_a = np.arcsin(np.sqrt(P))
    return float(np.sin((2 * k + 1) * th_a) ** 2)


def build_base_circuit_logical(P, k):
    """2-qubit CZ IQAE circuit: A + Q^k (no measurement). Identical to Exp 27/28/29."""
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


def build_gate_dose_circuit(P, k, D):
    """GATE arm == Exp 29: base + D injected logically-identity CZ-pairs (barrier-fenced).
    Adds 2D CZ gates AND ~2D*t_CZ of wall-time (the two are collinear -- that is the point)."""
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(2)
    qc.compose(build_base_circuit_logical(P, k), inplace=True)
    for _ in range(D):
        qc.barrier()
        qc.cz(0, 1)
        qc.barrier()
        qc.cz(0, 1)          # CZ * CZ = identity
    qc.barrier()
    qc.measure_all()
    return qc


def build_idle_dose_circuit(P, k, delay_dt):
    """IDLE arm: base + a barrier-fenced delay of `delay_dt` (dt units) on BOTH payload qubits,
    then measure. ZERO added 2q gates; added wall-time matched to the GATE arm. Logically identity
    (delay does not change the ideal output) so the confound-free property of Exp 29 is preserved."""
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(2)
    qc.compose(build_base_circuit_logical(P, k), inplace=True)
    qc.barrier()
    if delay_dt > 0:
        qc.delay(int(delay_dt), 0, unit="dt")
        qc.delay(int(delay_dt), 1, unit="dt")
    qc.barrier()
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


def ols_slope(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    xm, ym = x.mean(), y.mean()
    denom = ((x - xm) ** 2).sum()
    return float(((x - xm) * (y - ym)).sum() / denom) if denom > 0 else 0.0


# ---------------------------------------------------------------------------
# Duration matching: read the transpiled CZ duration on the laid-out physical
# pair so the IDLE delay reproduces the GATE arm's added wall-time exactly.
# ---------------------------------------------------------------------------
def _cz_duration_dt(transpiled_gate_circuit, target, dt):
    """Return the duration (in dt units) of one native 2q gate in the transpiled circuit."""
    twoq_names = {"cz", "ecr", "cx"}
    for inst in transpiled_gate_circuit.data:
        name = inst.operation.name
        if name in twoq_names:
            qubits = tuple(transpiled_gate_circuit.find_bit(q).index for q in inst.qubits)
            try:
                props = target[name].get(qubits) or target[name].get(qubits[::-1])
                if props is not None and props.duration is not None:
                    return int(round(props.duration / dt))
            except Exception:
                pass
    # fallback: median cz duration on the device
    durs = [p.duration for p in (target["cz"] or {}).values()
            if p is not None and p.duration is not None]
    return int(round(np.median(durs) / dt)) if durs else int(round(68e-9 / dt))


def _added_duration_dt(transpiled_circuit, target, dt):
    """Total duration (dt) contributed by all native 2q gates in a transpiled circuit."""
    twoq_names = {"cz", "ecr", "cx"}
    total = 0
    for inst in transpiled_circuit.data:
        name = inst.operation.name
        if name in twoq_names:
            qubits = tuple(transpiled_circuit.find_bit(q).index for q in inst.qubits)
            try:
                props = target[name].get(qubits) or target[name].get(qubits[::-1])
                if props is not None and props.duration is not None:
                    total += int(round(props.duration / dt))
            except Exception:
                pass
    return total


def _delay_duration_dt(transpiled_circuit, dt):
    """Total explicit delay duration (dt) in a transpiled circuit (IDLE arm wall-time)."""
    total = 0
    for inst in transpiled_circuit.data:
        if inst.operation.name == "delay":
            d = inst.operation.duration
            unit = getattr(inst.operation, "unit", "dt")
            total += int(d) if unit == "dt" else int(round(float(d) / dt))
    return total


# ---------------------------------------------------------------------------
# Schedule construction (GATE ladder + duration-matched IDLE ladder + cal)
# ---------------------------------------------------------------------------
def _build_schedule(transpile_fn, target, dt):
    items = []
    # GATE arm: transpile first so we can read the real CZ duration for matching.
    cz_dt = None
    gate_circuits = {}
    for P in P_VALUES:
        for k in K_VALUES:
            for D in DOSES:
                qc = transpile_fn(build_gate_dose_circuit(P, k, D))
                gate_circuits[(P, k, D)] = qc
                if cz_dt is None and D > 0:
                    cz_dt = _cz_duration_dt(qc, target, dt)
    if cz_dt is None:
        cz_dt = int(round(68e-9 / dt))
    # added wall-time per dose = 2 CZ per pair * D pairs * cz_dt
    delay_per_dose = {D: 2 * D * cz_dt for D in DOSES}

    for (P, k, D), qc in gate_circuits.items():
        items.append(("gate", P, k, D, qc))
    # IDLE arm: D=0 shares the GATE D0 baseline (same circuit), so skip D=0 here.
    for P in P_VALUES:
        for k in K_VALUES:
            for D in DOSES:
                if D == 0:
                    continue
                qc = transpile_fn(build_idle_dose_circuit(P, k, delay_per_dose[D]))
                items.append(("idle", P, k, D, qc))
    for (label, qc_cal) in build_calibration_circuits_logical():
        items.append(("cal", label, None, None, transpile_fn(qc_cal)))
    return items, cz_dt, delay_per_dose


def _verify_duration_match(items, target, dt, cz_dt, delay_per_dose):
    """Void-check: IDLE delay wall-time must match GATE injected-gate wall-time within tol."""
    print("\n  DURATION-MATCH VERIFICATION (void check, tol +-5%):")
    print(f"  {'D':>2} | {'GATE +2qdur(dt)':>16} | {'IDLE delay(dt)':>15} | {'match':>7}")
    ok = True
    base_gate = {}
    for D in DOSES:
        g = next(it for it in items if it[0] == "gate" and it[2] == 2 and it[3] == D)
        base_gate[D] = _added_duration_dt(g[4], target, dt)
    base0 = base_gate[0]
    for D in DOSES:
        if D == 0:
            continue
        added_gate = base_gate[D] - base0
        idle = next(it for it in items if it[0] == "idle" and it[2] == 2 and it[3] == D)
        added_idle = _delay_duration_dt(idle[4], dt)
        # idle adds delay on both qubits but wall-time (critical path) = per-qubit delay
        per_qubit_idle = added_idle // 2 if added_idle else 0
        rel = abs(per_qubit_idle - added_gate) / added_gate if added_gate else 1.0
        good = rel <= DURATION_TOL
        ok = ok and good
        print(f"  {D:>2} | {added_gate:>16} | {per_qubit_idle:>15} | "
              f"{'OK' if good else f'OFF {rel*100:.0f}%':>7}")
    print(f"  => duration match {'CONFIRMED' if ok else 'FAILED (run VOID if hardware)'}")
    return ok


def build_schedule_for_hardware():
    from qiskit import transpile
    from qiskit_ibm_runtime import QiskitRuntimeService
    service = QiskitRuntimeService()
    backend = service.backend(BACKEND_NAME)
    target, dt = backend.target, backend.target.dt

    def tfn(qc):
        return transpile(qc, backend=backend, optimization_level=0,
                         seed_transpiler=SEED_TRANSPILER)

    items, cz_dt, dpd = _build_schedule(tfn, target, dt)
    print(f"  Built {len(items)} circuits  (cz={cz_dt}dt={cz_dt*dt*1e9:.0f}ns)")
    _verify_duration_match(items, target, dt, cz_dt, dpd)
    return items, backend


def build_schedule_for_fakemarrakesh():
    from qiskit import transpile
    from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
    backend = FakeMarrakesh()
    target, dt = backend.target, backend.target.dt

    def tfn(qc):
        return transpile(qc, backend=backend, optimization_level=0,
                         seed_transpiler=SEED_TRANSPILER)

    items, cz_dt, dpd = _build_schedule(tfn, target, dt)
    print(f"  Built {len(items)} circuits  (cz={cz_dt}dt={cz_dt*dt*1e9:.0f}ns)")
    _verify_duration_match(items, target, dt, cz_dt, dpd)
    return items, backend, cz_dt, dt


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


def analyze(schedule_items, all_counts, cz_dt, dt, job_id=None):
    gate_data, idle_data, cal_data = {}, {}, {}
    for item, counts in zip(schedule_items, all_counts):
        if item[0] == "gate":
            gate_data[(item[1], item[2], item[3])] = counts
        elif item[0] == "idle":
            idle_data[(item[1], item[2], item[3])] = counts
        elif item[0] == "cal":
            cal_data[item[1]] = counts

    cal_pvecs = [counts_to_pvec(cal_data[l], SHOTS) for l in ["00", "01", "10", "11"]]
    M, M_inv = build_readout_matrix(cal_pvecs)
    print(f"\n  Readout |11> acc: {M[3][3]*100:.2f}%  false-pos P(11|00): {M[3][0]:.4f}")

    # IDLE D0 == GATE D0 (shared baseline)
    for P in P_VALUES:
        for k in K_VALUES:
            idle_data[(P, k, 0)] = gate_data[(P, k, 0)]

    added_dur_ns = {D: 2 * D * cz_dt * dt * 1e9 for D in DOSES}   # matched added wall-time / dose

    def arm_means(data):
        raw = {D: [] for D in DOSES}; rem = {D: [] for D in DOSES}
        for P in P_VALUES:
            for k in K_VALUES:
                ide = ideal_p11(P, k)
                for D in DOSES:
                    pvec = counts_to_pvec(data[(P, k, D)], SHOTS)
                    raw[D].append(abs(float(pvec[3]) - ide))
                    rem[D].append(abs(float(rem_correct(pvec, M_inv)[3]) - ide))
        return ({D: float(np.mean(raw[D])) for D in DOSES},
                {D: float(np.mean(rem[D])) for D in DOSES})

    g_raw, g_rem = arm_means(gate_data)
    i_raw, i_rem = arm_means(idle_data)

    print(f"\n  {'D':>2} {'+dur(ns)':>9} | {'GATE|raw|':>9} {'IDLE|raw|':>9} {'excess':>8}"
          f" | {'GATE|rem|':>9} {'IDLE|rem|':>9}")
    print("-" * 70)
    for D in DOSES:
        print(f"  {D:>2} {added_dur_ns[D]:>9.0f} | {g_raw[D]*100:>8.2f}p {i_raw[D]*100:>8.2f}p "
              f"{(g_raw[D]-i_raw[D])*100:>7.2f}p | {g_rem[D]*100:>8.2f}p {i_rem[D]*100:>8.2f}p")

    x = [added_dur_ns[D] for D in DOSES]
    slope_gate = ols_slope(x, [g_raw[D] for D in DOSES]) * 100.0 * 1000   # pp per us
    slope_idle = ols_slope(x, [i_raw[D] for D in DOSES]) * 100.0 * 1000
    top = DOSES[-1]
    excess_top_pp = (g_raw[top] - i_raw[top]) * 100.0
    excess_top_rem_pp = (g_rem[top] - i_rem[top]) * 100.0
    idle_gap_pp = (i_raw[top] - i_raw[0]) * 100.0

    t1 = (slope_idle > 0) and (idle_gap_pp > 0.30)
    t2 = (excess_top_pp > 0.30) and (slope_gate > slope_idle)
    t3 = excess_top_rem_pp > 0

    print(f"\n=== PRE-REGISTERED CRITERIA (Gate-Count vs Duration Decomposition) ===")
    print(f"  slope_gate = {slope_gate:+.3f} pp/us   slope_idle = {slope_idle:+.3f} pp/us"
          f"   gate-specific excess slope = {slope_gate-slope_idle:+.3f} pp/us")
    print(f"T1 (DURATION IS A CAUSE): slope_idle>0 & idle D6-D0 gap={idle_gap_pp:+.2f}pp>0.30"
          f"  -> {'PASS' if t1 else 'FAIL'}")
    print(f"T2 (GATE-SPECIFIC EXCESS): D6 gate-idle={excess_top_pp:+.2f}pp>0.30 & "
          f"slope_gate>slope_idle  -> {'PASS' if t2 else 'FAIL'}")
    print(f"T3 (survives REM): D6 REM gate-idle excess={excess_top_rem_pp:+.2f}pp>0"
          f"  -> {'PASS' if t3 else 'FAIL'}")

    if t2:
        verdict = ("EXP29 LAW SURVIVES AUDIT — gate count is a cause beyond matched-duration "
                   "decoherence; total cost decomposes into duration + gate-specific components.")
    elif t1 and not t2:
        verdict = ("EXP29 LAW NOT IDENTIFIED AS GATE-COUNT — degradation is substantially a "
                   "DURATION/decoherence law; C3726 'gate-overhead' label over-claimed the mechanism.")
    else:
        verdict = "Neither axis resolves at this dose range — revisit dose scale."
    print(f"\nVERDICT: {verdict}")

    result = {
        "experiment": EXPERIMENT,
        "title": "Gate-Count vs Duration: Decomposing the Exp 29 Dose-Response Law",
        "cycle": CYCLE, "backend": BACKEND_NAME, "job_id": job_id,
        "audits": "Exp 29 (C3726) gate-overhead dose-response law for count-vs-duration confound",
        "hypothesis": "Exp29's rho=1.0 dose trend confounds gate-COUNT with circuit-DURATION "
                      "(collinear r=1). IDLE arm holds duration fixed at matched added wall-time "
                      "with 0 added gates; GATE-IDLE excess identifies the gate-count-specific cost.",
        "params": {"shots": SHOTS, "P_values": P_VALUES, "k_values": K_VALUES, "doses": DOSES,
                   "cz_duration_dt": cz_dt, "dt_s": dt,
                   "added_duration_ns_by_dose": {f"D{D}": round(added_dur_ns[D], 1) for D in DOSES},
                   "circuits_total": len(schedule_items)},
        "preregistered_criteria": {
            "T1": "slope_idle>0 AND mean_err_idle(D6)-mean_err_idle(D0)>0.30pp (duration is a cause)",
            "T2": "mean_err_gate(D6)-mean_err_idle(D6)>0.30pp AND slope_gate>slope_idle (gate-specific excess)",
            "T3": "REM gate-vs-idle excess at D6 > 0 (gate-induced, not readout)",
            "verdict_map": "T2 PASS=>law survives; T2 FAIL&T1 PASS=>duration law (C3726 over-claimed); "
                           "T1 FAIL&T2 PASS=>pure gate-count",
            "void_check": "IDLE vs GATE added-duration must match within 5% at each dose else VOID",
        },
        "calibration": _load_calibration_snapshot(),
        "readout_calibration": {"readout_p11_accuracy": round(float(M[3][3]), 4),
                                "false_positive_rate": round(float(M[3][0]), 4)},
        "summary": {
            "gate_err_raw_pp_by_dose": {f"D{D}": round(g_raw[D] * 100, 2) for D in DOSES},
            "idle_err_raw_pp_by_dose": {f"D{D}": round(i_raw[D] * 100, 2) for D in DOSES},
            "gate_err_rem_pp_by_dose": {f"D{D}": round(g_rem[D] * 100, 2) for D in DOSES},
            "idle_err_rem_pp_by_dose": {f"D{D}": round(i_rem[D] * 100, 2) for D in DOSES},
            "slope_gate_pp_per_us": round(slope_gate, 3),
            "slope_idle_pp_per_us": round(slope_idle, 3),
            "gate_specific_excess_slope_pp_per_us": round(slope_gate - slope_idle, 3),
            "excess_top_dose_pp": round(excess_top_pp, 2),
            "excess_top_dose_rem_pp": round(excess_top_rem_pp, 2),
            "T1": "PASS" if t1 else "FAIL", "T2": "PASS" if t2 else "FAIL",
            "T3": "PASS" if t3 else "FAIL",
            "verdict": verdict,
        },
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
        items, backend = build_schedule_for_hardware()
        cz_dt = items and next((_cz_duration_dt(it[4], backend.target, backend.target.dt)
                                for it in items if it[0] == "gate" and it[3] > 0), 17)
        all_counts, status = get_counts_from_job(args.finalize, len(items))
        if all_counts is None:
            print(f"  Job not done yet ({status}).")
            return
        analyze(items, all_counts, cz_dt, backend.target.dt, job_id=args.finalize)
    elif args.submit:
        print(f"\n=== Exp {EXPERIMENT}: building hardware schedule ===")
        items, backend = build_schedule_for_hardware()
        print(f"\n=== Submitting to {BACKEND_NAME} ===")
        jid = submit_hardware(items, backend)
        print(f"\n  Finalize:  python3 scripts/run_exp30_gatecount_vs_duration.py --finalize {jid}")
    else:
        print(f"\n=== Exp {EXPERIMENT}: FakeMarrakesh simulation preview ===")
        items, backend, cz_dt, dt = build_schedule_for_fakemarrakesh()
        all_counts = get_counts_from_fakemarrakesh(items, backend)
        analyze(items, all_counts, cz_dt, dt, job_id="FakeMarrakesh-sim")


if __name__ == "__main__":
    main()
