"""Exp 36: Commutation-Aligned Compilation Principle (Whisper C3755).

OPEN RESEARCH QUESTION #7 (README): "Is the X-basis immunity a special case of a broader
'commutation-aligned compilation' principle? Generalize: the measurement error of an observable
should be a smooth function of the angle between its measurement axis and the noise-commuting
axis." See experiments/36-commutation-basis-sweep-preregistration.md.

Finding 03 gives THREE discrete points (err XX < ZZ < YY). This experiment sweeps the measurement
basis CONTINUOUSLY along two flat-ideal meridians anchored at the clean X axis, and tests whether
the noise-sensitivity gamma(theta) follows the predicted cos^2/sin^2 OVERLAP LAW (not just the
ordering). Clean do(measurement-basis angle): state + entangler held fixed, only the
pre-measurement rotation varies.

  Meridian 1 (X->Z), |Phi+>=(|00>+|11>)/sqrt2:  n(eta)=(sin eta,0,cos eta), ideal <nn>=+1 flat.
      pre-meas rotation per qubit = Ry(-eta).  eta: 0=Z .. pi/2=X.
  Meridian 2 (X->Y), |Psi+>=(|01>+|10>)/sqrt2:  n(phi)=(cos phi,sin phi,0), ideal <nn>=+1 flat.
      pre-meas rotation per qubit = Rz(-phi) then Ry(-pi/2).  phi: 0=X .. pi/2=Y.

ZNE global-fold lambda in {1,3,5}; gamma(theta)=OLS slope of err vs lambda. 2 meridians x 7 angles
x 3 lambda = 42 circuits, 4096 shots, single co-submitted job.

CALIBRATION GATE: identical do(layout=good) recipe as Exp34 (validated by Exp32 floor spectroscopy).

PRE-REGISTERED CRITERIA (see preregistration .md):
  G1 (headline): both meridians gamma(theta) fit overlap law (XZ: a+b cos^2 eta; XY: a+b sin^2 phi)
                 with R^2 >= 0.90, and not beaten by a plain linear-in-angle fit.
  G2 (monotonicity): Spearman rho(gamma, overlap) >= +0.9 each meridian.
  G3 (anisotropy):   b_XY > b_XZ AND both b > 0  (Y dirtier than Z; reproduces eYY>eZZ as amplitude)
  G4 (X-endpoint):   |gamma_X(merid1) - gamma_X(merid2)| < 0.03.
  G5 (do-control):   transpiled 2q-gate count constant across angles within a meridian (reported).
  G1&G2&G3 PASS -> commutation-aligned compilation principle CONFIRMED.

Run (sim preview):   python3 scripts/run_exp36_commutation_basis_sweep.py
Run (hardware):      python3 scripts/run_exp36_commutation_basis_sweep.py --submit
Finalize:            python3 scripts/run_exp36_commutation_basis_sweep.py --finalize <job_id>
"""
import argparse
import json
import os
import numpy as np

EXPERIMENT = "36"
CYCLE = 3755
SHOTS = 4096
SCALE_FACTORS = [1, 3, 5]
ANGLES_DEG = [0, 15, 30, 45, 60, 75, 90]
MERIDIANS = ["XZ", "XY"]   # XZ uses |Phi+>, XY uses |Psi+>
SEED_TRANSPILER = 42
BACKEND_NAME = "ibm_marrakesh"
RESULT_PATH = f"experiments/{EXPERIMENT}-commutation-basis-sweep-results.json"
JOBID_PATH = f"experiments/{EXPERIMENT}-jobid.txt"
CALIB_PATH = f"experiments/{EXPERIMENT}-calibration.json"

RO_MAX = 0.05
CZ_MAX = 0.01

# ideal correlator is +1 flat for both meridians by construction (see preregistration)
IDEAL_CORR = 1.0
FINDING03_REF = {"note": "Finding 03 (C3650/C3746): err XX<ZZ<YY; good-pair floor XX~5.9 ZZ~7.1 "
                         "YY~9.1pp; gamma_ZZ>gamma_XX. Exp36 generalizes the 3 points to a "
                         "continuous gamma(theta) overlap-law curve."}


# --------------------------------------------------------------------------- circuit build
def build_state(meridian):
    """Meridian XZ -> |Phi+>; meridian XY -> |Psi+> (makes the X-Y sweep flat-ideal)."""
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    if meridian == "XY":
        qc.x(1)          # |Phi+> -> |Psi+> = (|01>+|10>)/sqrt2
    return qc


def append_basis_rotation(qc, meridian, angle_rad):
    """Rotate the measurement axis n(theta) to Z so a Z-parity readout gives <nn>(theta)."""
    if meridian == "XZ":
        # n=(sin eta,0,cos eta), eta from Z. Ry(-eta) maps n -> Z.
        qc.ry(-angle_rad, 0)
        qc.ry(-angle_rad, 1)
    elif meridian == "XY":
        # n=(cos phi,sin phi,0), phi from X. Rz(-phi) brings n to X, then Ry(-pi/2) maps X -> Z.
        qc.rz(-angle_rad, 0)
        qc.rz(-angle_rad, 1)
        qc.ry(-np.pi / 2, 0)
        qc.ry(-np.pi / 2, 1)
    return qc


def build_zne_circuit(meridian, angle_deg, scale):
    """Global-folded state prep (scale=1,3,5) + tilted-axis readout rotation + measure_all."""
    from qiskit import QuantumCircuit
    base = build_state(meridian)
    base_inv = base.inverse()
    n_folds = (scale - 1) // 2
    qc = QuantumCircuit(2)
    qc.compose(base, inplace=True)
    for _ in range(n_folds):
        qc.compose(base_inv, inplace=True)
        qc.compose(base, inplace=True)
    append_basis_rotation(qc, meridian, np.deg2rad(angle_deg))
    qc.measure_all()
    return qc


def counts_to_expval(counts, shots):
    total, acc = 0, 0.0
    for bitstr, c in counts.items():
        bits = bitstr.replace(" ", "")[-2:]
        total += c
        parity = (int(bits[0]) ^ int(bits[1]))
        acc += ((-1) ** parity) * c
    return acc / (total if total > 0 else shots)


def ols_slope(xs, ys):
    xs = np.asarray(xs, dtype=float)
    ys = np.asarray(ys, dtype=float)
    A = np.vstack([xs, np.ones_like(xs)]).T
    slope, _ = np.linalg.lstsq(A, ys, rcond=None)[0]
    return float(slope)


def ols_fit_r2(u, y):
    """Fit y = a + b*u (OLS). Return (a, b, R2)."""
    u = np.asarray(u, dtype=float)
    y = np.asarray(y, dtype=float)
    A = np.vstack([u, np.ones_like(u)]).T
    (b, a), *_ = np.linalg.lstsq(A, y, rcond=None)
    yhat = a + b * u
    ss_res = float(np.sum((y - yhat) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 1e-12 else float("nan")
    return float(a), float(b), float(r2)


def spearman_rho(x, y):
    """Spearman rank correlation (no scipy dependency)."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    rx -= rx.mean()
    ry -= ry.mean()
    denom = np.sqrt(np.sum(rx ** 2) * np.sum(ry ** 2))
    return float(np.sum(rx * ry) / denom) if denom > 1e-12 else float("nan")


# --------------------------------------------------------------------------- calibration gate
def _qubit_metrics(backend, q):
    t1 = t2 = ro = None
    try:
        qp = backend.qubit_properties(q)
        t1 = getattr(qp, "t1", None)
        t2 = getattr(qp, "t2", None)
    except Exception:
        pass
    try:
        meas = backend.target["measure"]
        ip = meas.get((q,))
        if ip is not None and getattr(ip, "error", None) is not None:
            ro = ip.error
    except Exception:
        pass
    if t1 is None or t2 is None or ro is None:
        try:
            props = backend.properties()
            if props is not None:
                if t1 is None:
                    t1 = props.t1(q)
                if t2 is None:
                    t2 = props.t2(q)
                if ro is None:
                    ro = props.readout_error(q)
        except Exception:
            pass
    return t1, t2, ro


def _cz_error(backend, a, b):
    for gname in ("cz", "ecr", "cx"):
        try:
            inst = backend.target[gname]
            ip = inst.get((a, b)) or inst.get((b, a))
            if ip is not None and getattr(ip, "error", None) is not None:
                return gname, ip.error
        except Exception:
            continue
    try:
        props = backend.properties()
        if props is not None:
            for gname in ("cz", "ecr", "cx"):
                try:
                    ge = props.gate_error(gname, [a, b])
                    if ge is not None:
                        return gname, ge
                except Exception:
                    continue
    except Exception:
        pass
    return None, None


def _coupling_edges(backend):
    cm = backend.coupling_map
    edges = set()
    try:
        for a, b in cm.get_edges():
            edges.add((int(a), int(b)))
    except Exception:
        for e in list(cm):
            edges.add((int(e[0]), int(e[1])))
    seen, uniq = set(), []
    for a, b in edges:
        key = (min(a, b), max(a, b))
        if key not in seen:
            seen.add(key)
            uniq.append((a, b))
    return uniq


def select_calibrated_pair(backend):
    candidates = []
    rejects = {"readout": 0, "tnull": 0, "cz": 0, "nocz": 0}
    for (a, b) in _coupling_edges(backend):
        t1a, t2a, roa = _qubit_metrics(backend, a)
        t1b, t2b, rob = _qubit_metrics(backend, b)
        gname, cz = _cz_error(backend, a, b)
        if cz is None:
            rejects["nocz"] += 1
            continue
        if None in (t1a, t2a, t1b, t2b):
            rejects["tnull"] += 1
            continue
        if roa is None or rob is None or roa > RO_MAX or rob > RO_MAX:
            rejects["readout"] += 1
            continue
        if cz >= CZ_MAX:
            rejects["cz"] += 1
            continue
        score = cz + 0.25 * (roa + rob)
        candidates.append({
            "pair": [a, b], "cz_gate": gname, "cz_error": cz,
            "readout_a": roa, "readout_b": rob,
            "t1_a": t1a, "t2_a": t2a, "t1_b": t1b, "t2_b": t2b, "score": score,
        })
    candidates.sort(key=lambda c: c["score"])
    audit = {
        "gate": {"RO_MAX": RO_MAX, "CZ_MAX": CZ_MAX,
                 "scoring": "argmin cz_error + 0.25*(ro_a+ro_b)"},
        "n_edges_scanned": len(_coupling_edges(backend)),
        "n_eligible": len(candidates), "rejects": rejects, "top5": candidates[:5],
    }
    if not candidates:
        return None, audit
    return candidates[0]["pair"], audit


# --------------------------------------------------------------------------- schedule build
def _schedule_keys():
    items = []
    for meridian in MERIDIANS:
        for angle in ANGLES_DEG:
            for scale in SCALE_FACTORS:
                items.append((meridian, angle, scale))
    return items


def _build_schedule(transpile_fn):
    items = []
    for (meridian, angle, scale) in _schedule_keys():
        qc = transpile_fn(build_zne_circuit(meridian, angle, scale))
        items.append((meridian, angle, scale, qc))
    return items


def build_schedule_for_hardware():
    from qiskit import transpile
    from qiskit_ibm_runtime import QiskitRuntimeService
    service = QiskitRuntimeService()
    backend = service.backend(BACKEND_NAME)
    print(f"\n  Selecting calibration-gated layout pair on {BACKEND_NAME}...")
    pair, audit = select_calibrated_pair(backend)
    if pair is None:
        raise RuntimeError(
            f"ABORT: no coupled pair passes the calibration gate "
            f"(RO<={RO_MAX}, cz<{CZ_MAX}, non-null T1/T2). audit={json.dumps(audit, default=str)}")
    best = audit["top5"][0]
    print(f"  Selected pair {pair}  cz({best['cz_gate']})={best['cz_error']:.5f}  "
          f"ro=({best['readout_a']:.4f},{best['readout_b']:.4f})  "
          f"({audit['n_eligible']}/{audit['n_edges_scanned']} pairs eligible)")

    def tfn(qc):
        return transpile(qc, backend=backend, optimization_level=0,
                         seed_transpiler=SEED_TRANSPILER, initial_layout=pair)

    items = _build_schedule(tfn)
    print(f"  Built {len(items)} circuits on {BACKEND_NAME} (pinned to {pair})")
    _print_gate_invariance(items)
    return items, backend, pair, audit


def build_schedule_for_fake():
    from qiskit import transpile
    from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
    backend = FakeMarrakesh()
    print("\n  [sim] Selecting calibration-gated layout pair on FakeMarrakesh...")
    pair, audit = select_calibrated_pair(backend)
    if pair is None:
        print("  [sim] no pair passed gate; using [0,1] for preview only")
        pair = [0, 1]
    else:
        best = audit["top5"][0]
        print(f"  [sim] Selected pair {pair}  cz={best['cz_error']:.5f}  "
              f"({audit['n_eligible']}/{audit['n_edges_scanned']} eligible)")

    def tfn(qc):
        return transpile(qc, backend=backend, optimization_level=0,
                         seed_transpiler=SEED_TRANSPILER, initial_layout=pair)

    items = _build_schedule(tfn)
    _print_gate_invariance(items)
    return items, backend, pair, audit


def _twoq_count(qc):
    ops = qc.count_ops()
    return ops.get("cz", 0) + ops.get("ecr", 0) + ops.get("cx", 0)


def _print_gate_invariance(items):
    """G5 control: 2q-gate count should be constant across angle within (meridian, lambda)."""
    print("  [G5 gate-invariance] 2q-count by (meridian, lambda) across angles:")
    for meridian in MERIDIANS:
        for scale in SCALE_FACTORS:
            counts = [(_twoq_count(qc)) for (m, a, s, qc) in items
                      if m == meridian and s == scale]
            uniq = sorted(set(counts))
            flag = "OK(constant)" if len(uniq) == 1 else f"VARIES {uniq}"
            print(f"    {meridian} lambda={scale}: 2q={uniq if len(uniq) > 1 else uniq[0]}  {flag}")


def submit_hardware(schedule_items, backend, pair, audit):
    from qiskit_ibm_runtime import SamplerV2
    sampler = SamplerV2(mode=backend)
    sampler.options.default_shots = SHOTS
    circuits = [item[3] for item in schedule_items]
    job = sampler.run([(qc,) for qc in circuits])
    job_id = job.job_id()
    with open(JOBID_PATH, "w") as f:
        f.write(job_id + "\n")
    try:
        from calibration_snapshot import capture_calibration
        snap = capture_calibration(backend, physical_qubits=pair)
        snap["selected_pair"] = pair
        snap["pair_selection_audit"] = audit
        with open(CALIB_PATH, "w") as f:
            json.dump(snap, f, indent=4, default=str)
        print(f"  Calibration snapshot saved (updated {snap.get('last_update_date')})")
    except Exception as e:
        print(f"  [warn] calibration snapshot skipped: {e}")
    print(f"\n  SUBMITTED. job_id = {job_id}  ({len(circuits)} circuits) on {BACKEND_NAME} "
          f"pinned to {pair}")
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


def get_counts_from_fake(schedule_items, backend, noiseless=False):
    from qiskit_aer.primitives import SamplerV2 as AerSampler
    opts = {"run_options": {"shots": SHOTS, "seed": SEED_TRANSPILER}}
    if not noiseless:
        from qiskit_aer.noise import NoiseModel
        opts["backend_options"] = {"noise_model": NoiseModel.from_backend(backend)}
    sampler = AerSampler(options=opts)
    circuits = [item[3] for item in schedule_items]
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


# --------------------------------------------------------------------------- analysis
def overlap_predictor(meridian, angle_deg):
    """cos^2(eta) overlap with dirty-Z for XZ; sin^2(phi) overlap with dirty-Y for XY."""
    r = np.deg2rad(angle_deg)
    return float(np.cos(r) ** 2) if meridian == "XZ" else float(np.sin(r) ** 2)


def analyze(schedule_items, all_counts, job_id=None, selected_pair=None, audit=None,
            ideal_check=False):
    data = {}
    for item, counts in zip(schedule_items, all_counts):
        data[(item[0], item[1], item[2])] = counts

    label = "IDEAL <nn>" if ideal_check else "err"
    per = {}   # (meridian, angle) -> {gamma, errs, expvals}
    rows = []
    print(f"\n{'merid':>6} {'ang':>4} | "
          + " ".join([f"l={s}".rjust(8) for s in SCALE_FACTORS])
          + f" | {'gamma':>8}")
    print("-" * 60)
    for meridian in MERIDIANS:
        for angle in ANGLES_DEG:
            errs, evs, lambdas = [], [], []
            for scale in SCALE_FACTORS:
                ev = counts_to_expval(data[(meridian, angle, scale)], SHOTS)
                err = 1.0 - abs(ev)
                errs.append(err)
                evs.append(ev)
                lambdas.append(scale)
                rows.append({"meridian": meridian, "angle_deg": angle, "lambda": scale,
                             "expval": round(ev, 5), "err": round(err, 5)})
            gamma = ols_slope(lambdas, errs)
            per[(meridian, angle)] = {"gamma": gamma, "errs": errs, "expvals": evs}
            shown = " ".join([f"{(evs[i] if ideal_check else errs[i]):8.4f}"
                              for i in range(len(SCALE_FACTORS))])
            print(f"{meridian:>6} {angle:>4} | {shown} | {gamma:>8.4f}")
    print("-" * 60)

    if ideal_check:
        # noiseless construction validation: every <nn> should be ~ +1
        worst = max(abs(per[(m, a)]["expvals"][0] - IDEAL_CORR)
                    for m in MERIDIANS for a in ANGLES_DEG)
        ok = worst < 0.02
        print(f"\n  [IDEAL-CHECK] max |<nn> - (+1)| over all (meridian,angle) at lambda=1 "
              f"= {worst:.4f} -> {'PASS flat-ideal construction valid' if ok else 'FAIL'}")
        return {"ideal_check": True, "max_dev_from_+1": round(worst, 5), "pass": bool(ok)}

    # ---- overlap-law fits per meridian (on gamma(theta), primary) ----
    summary = {}
    fit_audit = {}
    for meridian in MERIDIANS:
        angs = ANGLES_DEG
        gammas = [per[(meridian, a)]["gamma"] for a in angs]
        u = [overlap_predictor(meridian, a) for a in angs]                  # cos^2/sin^2 overlap
        lin = [a for a in angs]                                            # plain angle (deg)
        a_o, b_o, r2_o = ols_fit_r2(u, gammas)
        a_l, b_l, r2_l = ols_fit_r2(lin, gammas)
        rho = spearman_rho(u, gammas)
        fit_audit[meridian] = {
            "overlap_law": {"form": "a+b*cos^2(eta)" if meridian == "XZ" else "a+b*sin^2(phi)",
                            "a": round(a_o, 5), "b": round(b_o, 5), "R2": round(r2_o, 4)},
            "linear_in_angle": {"a": round(a_l, 5), "b_per_deg": round(b_l, 6),
                                "R2": round(r2_l, 4)},
            "spearman_rho_gamma_vs_overlap": round(rho, 4),
            "gamma_by_angle": {a: round(per[(meridian, a)]["gamma"], 5) for a in angs},
        }

    b_xz = fit_audit["XZ"]["overlap_law"]["b"]
    b_xy = fit_audit["XY"]["overlap_law"]["b"]
    r2_xz = fit_audit["XZ"]["overlap_law"]["R2"]
    r2_xy = fit_audit["XY"]["overlap_law"]["R2"]
    rho_xz = fit_audit["XZ"]["spearman_rho_gamma_vs_overlap"]
    rho_xy = fit_audit["XY"]["spearman_rho_gamma_vs_overlap"]
    # X endpoint: XZ at eta=90deg (X), XY at phi=0deg (X)
    gamma_x_m1 = per[("XZ", 90)]["gamma"]
    gamma_x_m2 = per[("XY", 0)]["gamma"]

    # pre-registered gates
    g1 = (r2_xz >= 0.90 and r2_xy >= 0.90
          and r2_xz >= fit_audit["XZ"]["linear_in_angle"]["R2"] - 1e-9
          and r2_xy >= fit_audit["XY"]["linear_in_angle"]["R2"] - 1e-9)
    g2 = (rho_xz >= 0.9 and rho_xy >= 0.9)
    g3 = (b_xy > b_xz and b_xz > 0 and b_xy > 0)
    g4 = abs(gamma_x_m1 - gamma_x_m2) < 0.03

    print(f"\n=== PRE-REGISTERED CRITERIA (Exp36, {BACKEND_NAME}, ORQ#7) ===")
    print(f"  Overlap-law fit gamma(theta):")
    print(f"    XZ (a+b cos^2 eta):  b={b_xz:+.4f}  R2={r2_xz:.3f}  "
          f"(linear R2={fit_audit['XZ']['linear_in_angle']['R2']:.3f})  rho={rho_xz:+.3f}")
    print(f"    XY (a+b sin^2 phi):  b={b_xy:+.4f}  R2={r2_xy:.3f}  "
          f"(linear R2={fit_audit['XY']['linear_in_angle']['R2']:.3f})  rho={rho_xy:+.3f}")
    print(f"  G1 (OVERLAP LAW, R2>=0.90 both, >= linear):           {'PASS' if g1 else 'FAIL'}")
    print(f"  G2 (MONOTONICITY, rho>=+0.9 both):                    {'PASS' if g2 else 'FAIL'}")
    print(f"  G3 (ANISOTROPY, b_XY>b_XZ>0): b_XY={b_xy:+.4f} b_XZ={b_xz:+.4f} "
          f"-> {'PASS' if g3 else 'FAIL'}")
    print(f"  G4 (X-ENDPOINT, |dgamma|<0.03): "
          f"|{gamma_x_m1:+.4f}-{gamma_x_m2:+.4f}|={abs(gamma_x_m1-gamma_x_m2):.4f} "
          f"-> {'PASS' if g4 else 'FAIL'}")

    confirmed = g1 and g2 and g3
    if confirmed:
        verdict = ("COMMUTATION-ALIGNED COMPILATION PRINCIPLE CONFIRMED on ibm_marrakesh: "
                   "Finding 03's X-immunity is one point on a smooth gamma(theta) overlap curve "
                   "(cos^2/sin^2, R2>=0.90), monotone in basis-axis overlap with the noisy "
                   "direction, with Y anti-commuting more strongly than Z (b_XY>b_XZ). The 3-point "
                   "ordering generalizes to a continuous compilation rule: route observables toward "
                   "the noise-commuting axis; the gain is predictable from the misalignment angle.")
    elif g2 and not g1:
        verdict = ("ORDERED BUT NOT OVERLAP-GOVERNED: gamma rises monotonically with basis-axis "
                   "overlap (G2) but the cos^2/sin^2 law does not fit (G1 FAIL) -> the channel has "
                   "higher-order angular structure a single overlap term cannot capture. The "
                   "3-point ordering is real; the clean continuous law is not. ORQ#7 reframed.")
    else:
        verdict = ("Overlap law NOT supported (G1/G2 FAIL). gamma(theta) is not a clean monotone "
                   "function of basis-axis overlap on this pair/day -- inspect calibration drift / "
                   "shot noise before any principle claim.")
    print(f"\nVERDICT: {verdict}")

    result = {
        "experiment": EXPERIMENT,
        "title": "Commutation-Aligned Compilation Principle — basis-angle sweep (ORQ#7)",
        "cycle": CYCLE, "backend": BACKEND_NAME, "job_id": job_id,
        "selected_pair": selected_pair, "pair_selection_audit": audit,
        "open_research_question": "ORQ#7: is X-basis immunity a special case of a broader "
                                  "commutation-aligned compilation principle? Does measurement "
                                  "error follow an overlap law in the basis-axis angle?",
        "finding03_reference": FINDING03_REF,
        "design": {
            "meridian_XZ": "|Phi+>, n(eta)=(sin eta,0,cos eta), ideal <nn>=+1 flat, eta:0=Z..90=X",
            "meridian_XY": "|Psi+>, n(phi)=(cos phi,sin phi,0), ideal <nn>=+1 flat, phi:0=X..90=Y",
            "angles_deg": ANGLES_DEG, "scale_factors": SCALE_FACTORS, "shots": SHOTS,
            "circuits_total": len(schedule_items), "seed_transpiler": SEED_TRANSPILER,
            "calibration_gate": {"RO_MAX": RO_MAX, "CZ_MAX": CZ_MAX},
        },
        "preregistered_criteria": {
            "G1": "both meridians gamma(theta) overlap-law R2>=0.90 AND >= linear-in-angle R2",
            "G2": "Spearman rho(gamma, overlap) >= +0.9 each meridian",
            "G3": "b_XY > b_XZ AND both b>0 (Y dirtier than Z; reproduces eYY>eZZ as amplitude)",
            "G4": "|gamma_X(merid1) - gamma_X(merid2)| < 0.03 (X-endpoint consistency)",
            "G5": "transpiled 2q count constant across angles within a meridian (gate-invariance)",
            "CONFIRM": "G1&G2&G3 PASS -> commutation-aligned compilation principle",
        },
        "calibration": _load_calibration_snapshot(),
        "fits": fit_audit,
        "summary": {
            "b_overlap_XZ": round(b_xz, 5), "R2_overlap_XZ": round(r2_xz, 4), "rho_XZ": round(rho_xz, 4),
            "b_overlap_XY": round(b_xy, 5), "R2_overlap_XY": round(r2_xy, 4), "rho_XY": round(rho_xy, 4),
            "gamma_X_endpoint_merid1": round(gamma_x_m1, 5),
            "gamma_X_endpoint_merid2": round(gamma_x_m2, 5),
            "G1": "PASS" if g1 else "FAIL", "G2": "PASS" if g2 else "FAIL",
            "G3": "PASS" if g3 else "FAIL", "G4": "PASS" if g4 else "FAIL",
            "principle_confirmed": bool(confirmed), "verdict": verdict,
        },
        "rows": rows,
    }
    with open(RESULT_PATH, "w") as f:
        json.dump(result, f, indent=4, default=str)
    print(f"\n  Results saved to {RESULT_PATH}")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--submit", action="store_true")
    parser.add_argument("--finalize", metavar="JOB_ID")
    parser.add_argument("--ideal", action="store_true",
                        help="noiseless construction check (verify ideal <nn>=+1 flat)")
    args = parser.parse_args()

    if args.finalize:
        print(f"\n=== Fetching Exp {EXPERIMENT} (job {args.finalize}) ===")
        schedule_items, _, pair, audit = build_schedule_for_hardware()
        all_counts, status = get_counts_from_job(args.finalize, len(schedule_items))
        if all_counts is None:
            print(f"  Job not done yet ({status}).")
            return
        analyze(schedule_items, all_counts, job_id=args.finalize, selected_pair=pair, audit=audit)
    elif args.submit:
        print(f"\n=== Exp {EXPERIMENT}: building hardware schedule ({BACKEND_NAME}) ===")
        schedule_items, backend, pair, audit = build_schedule_for_hardware()
        print(f"\n=== Submitting to {BACKEND_NAME} ===")
        jid = submit_hardware(schedule_items, backend, pair, audit)
        print(f"\n  Finalize with:  python3 scripts/run_exp36_commutation_basis_sweep.py "
              f"--finalize {jid}")
    else:
        print(f"\n=== Exp {EXPERIMENT}: FakeMarrakesh simulation preview ===")
        schedule_items, backend, pair, audit = build_schedule_for_fake()
        if args.ideal:
            print("  [noiseless ideal-check]")
            all_counts = get_counts_from_fake(schedule_items, backend, noiseless=True)
            analyze(schedule_items, all_counts, job_id="noiseless-sim",
                    selected_pair=pair, audit=audit, ideal_check=True)
        else:
            all_counts = get_counts_from_fake(schedule_items, backend)
            analyze(schedule_items, all_counts, job_id="FakeMarrakesh-sim",
                    selected_pair=pair, audit=audit)


if __name__ == "__main__":
    main()
