"""Exp 34: X-Basis Noise Immunity — Calibration-Gated Retest (Whisper C3746).

OPEN RESEARCH QUESTION #1 (README): "Does X-basis immunity generalize across the heavy-hex
family? Pre-reg gate: >=2x X/Z fidelity ratio on an independent backend."

Exp31 (C3738) ran this on ibm_kingston and came back INCONCLUSIVE: a ~20.36pp gate-independent
fidelity floor swamped the ~3x X/Z mechanism. Exp32 (C3740) floor spectroscopy proved the floor
is LAYOUT-dominated (dead qubit q146: readout 0.518, T1/T2 null, cz error 1.0); on a GOOD pair it
drops to a stable ~9pp. Exp31's flaw (mine): it let the transpiler choose the layout (no
initial_layout) and landed on/near a bad pair. Exp34 fixes the SINGLE variable -- it pins the Bell
to a CALIBRATION-VERIFIED-GOOD coupled pair (a clean do(layout=good) on Exp31). Everything else
(9-circuit basis-resolved ZNE, shots, seed, criteria) is identical to Exp31.

CALIBRATION GATE (pre-registered, see 34-...-preregistration.md):
  A coupled pair (a,b) is ELIGIBLE iff readout(a)<=0.05 AND readout(b)<=0.05 AND T1/T2(a,b) all
  non-null AND cz_error(a,b) < 0.01. SELECT argmin cz_error + 0.25*(ro_a+ro_b). Pin via
  initial_layout=[a,b], opt_level=0 (preserve ZNE folds, C3720), seed_transpiler=42. If ZERO
  pairs pass -> ABORT (never silently fall back to a bad pair).

PRE-REGISTERED CRITERIA (identical to Exp31):
  eXX,eYY,eZZ = mean err across lambda per basis; gamma_basis = OLS slope of err vs lambda.
  T1 (headline, README gate): eZZ/eXX >= 2.0 AND eXX < eZZ
  T2 (Y-injection):           eYY > eXX with eYY-eXX >= 0.02
  T3 (slope ordering):        gamma_ZZ > gamma_XX
  T1 PASS -> Finding 03 = heavy-hex ARCHITECTURAL principle (ORQ#1 upgrade gate met).
  T1 FAIL on a good pair -> CLEAN falsification (not a floor confound): marrakesh-specific.

Run (sim preview):   python3 scripts/run_exp34_xbasis_calgated.py
Run (hardware):      python3 scripts/run_exp34_xbasis_calgated.py --submit
Finalize:            python3 scripts/run_exp34_xbasis_calgated.py --finalize <job_id>
"""
import argparse
import json
import os
import numpy as np

EXPERIMENT = "34"
CYCLE = 3746
SHOTS = 4096
BASES = ["XX", "YY", "ZZ"]
SCALE_FACTORS = [1, 3, 5]
SEED_TRANSPILER = 42
BACKEND_NAME = "ibm_kingston"
RESULT_PATH = f"experiments/{EXPERIMENT}-xbasis-calgated-results.json"
JOBID_PATH = f"experiments/{EXPERIMENT}-jobid.txt"
CALIB_PATH = f"experiments/{EXPERIMENT}-calibration.json"

# Pre-registered calibration gate thresholds
RO_MAX = 0.05         # reject qubit if readout_error > this
CZ_MAX = 0.01         # reject pair if cz/ecr gate_error >= this

IDEAL = {"XX": +1.0, "YY": -1.0, "ZZ": +1.0}
MARRAKESH_REF = {"note": "Finding 03 Bell C3650: <XX> immune (flat), <ZZ> gamma~1.197 accel, "
                         "<YY> gamma~0.707; ZZ/XX err ratio ~3x. Exp31 kingston INCONCLUSIVE "
                         "(20.36pp floor); Exp32 -> floor is layout-dominated, good pair ~9pp."}


# --------------------------------------------------------------------------- circuit build
def build_bell_base():
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    return qc


def build_zne_basis_circuit(basis, scale):
    """Global-folded Bell (scale=1,3,5) + basis-rotation readout + measure_all."""
    from qiskit import QuantumCircuit
    base = build_bell_base()
    base_inv = base.inverse()
    n_folds = (scale - 1) // 2
    qc = QuantumCircuit(2)
    qc.compose(base, inplace=True)
    for _ in range(n_folds):
        qc.compose(base_inv, inplace=True)
        qc.compose(base, inplace=True)
    if basis == "XX":
        qc.h(0)
        qc.h(1)
    elif basis == "YY":
        qc.sdg(0)
        qc.h(0)
        qc.sdg(1)
        qc.h(1)
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


# --------------------------------------------------------------------------- calibration gate
def _qubit_metrics(backend, q):
    """Return (t1, t2, readout_error) for physical qubit q, target-first then properties."""
    t1 = t2 = ro = None
    # modern API: backend.qubit_properties(q)
    try:
        qp = backend.qubit_properties(q)
        t1 = getattr(qp, "t1", None)
        t2 = getattr(qp, "t2", None)
    except Exception:
        pass
    # readout error from target['measure']
    try:
        meas = backend.target["measure"]
        ip = meas.get((q,))
        if ip is not None and getattr(ip, "error", None) is not None:
            ro = ip.error
    except Exception:
        pass
    # legacy fallback: backend.properties()
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
    """2q gate error on edge (a,b), trying cz/ecr/cx, target-first then properties."""
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
    # dedupe undirected
    seen, uniq = set(), []
    for a, b in edges:
        key = (min(a, b), max(a, b))
        if key not in seen:
            seen.add(key)
            uniq.append((a, b))
    return uniq


def select_calibrated_pair(backend):
    """Scan coupling map; return (best_pair, audit_dict). Pre-registered gate + scoring.

    best_pair is [a, b] physical indices, or None if no pair passes the gate.
    """
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
            "t1_a": t1a, "t2_a": t2a, "t1_b": t1b, "t2_b": t2b,
            "score": score,
        })
    candidates.sort(key=lambda c: c["score"])
    audit = {
        "gate": {"RO_MAX": RO_MAX, "CZ_MAX": CZ_MAX,
                 "scoring": "argmin cz_error + 0.25*(ro_a+ro_b)"},
        "n_edges_scanned": len(_coupling_edges(backend)),
        "n_eligible": len(candidates),
        "rejects": rejects,
        "top5": candidates[:5],
    }
    if not candidates:
        return None, audit
    return candidates[0]["pair"], audit


# --------------------------------------------------------------------------- schedule build
def _build_schedule(transpile_fn):
    items = []
    for basis in BASES:
        for scale in SCALE_FACTORS:
            qc = transpile_fn(build_zne_basis_circuit(basis, scale))
            items.append((basis, scale, qc))
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
            f"(RO<={RO_MAX}, cz<{CZ_MAX}, non-null T1/T2). "
            f"Backend too degraded today. audit={json.dumps(audit, default=str)}")
    best = audit["top5"][0]
    print(f"  Selected pair {pair}  cz({best['cz_gate']})={best['cz_error']:.5f}  "
          f"ro=({best['readout_a']:.4f},{best['readout_b']:.4f})  "
          f"({audit['n_eligible']}/{audit['n_edges_scanned']} pairs eligible)")

    def tfn(qc):
        return transpile(qc, backend=backend, optimization_level=0,
                         seed_transpiler=SEED_TRANSPILER, initial_layout=pair)

    items = _build_schedule(tfn)
    print(f"  Built {len(items)} circuits on {BACKEND_NAME} (pinned to {pair})")
    for (basis, scale, qc) in items:
        ops = qc.count_ops()
        cz = ops.get("cz", 0) + ops.get("ecr", 0) + ops.get("cx", 0)
        print(f"  {basis} lambda={scale}: depth={qc.depth()} 2q={cz}")
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
    for (basis, scale, qc) in items:
        ops = qc.count_ops()
        cz = ops.get("cz", 0) + ops.get("ecr", 0) + ops.get("cx", 0)
        print(f"  {basis} lambda={scale}: depth={qc.depth()} 2q={cz}")
    return items, backend, pair, audit


def submit_hardware(schedule_items, backend, pair, audit):
    from qiskit_ibm_runtime import SamplerV2
    sampler = SamplerV2(mode=backend)
    sampler.options.default_shots = SHOTS
    circuits = [item[2] for item in schedule_items]
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


def get_counts_from_fake(schedule_items, backend):
    from qiskit_aer.primitives import SamplerV2 as AerSampler
    from qiskit_aer.noise import NoiseModel
    nm = NoiseModel.from_backend(backend)
    sampler = AerSampler(options={
        "backend_options": {"noise_model": nm},
        "run_options": {"shots": SHOTS, "seed": SEED_TRANSPILER},
    })
    circuits = [item[2] for item in schedule_items]
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


def analyze(schedule_items, all_counts, job_id=None, selected_pair=None, audit=None):
    data = {}
    for item, counts in zip(schedule_items, all_counts):
        data[(item[0], item[1])] = counts

    per_basis = {}
    rows = []
    print(f"\n{'basis':>6} {'lambda':>7} | {'<BB>':>8} {'ideal':>6} {'err':>8}")
    print("-" * 44)
    for basis in BASES:
        errs, lambdas = [], []
        for scale in SCALE_FACTORS:
            ev = counts_to_expval(data[(basis, scale)], SHOTS)
            err = 1.0 - abs(ev)
            errs.append(err)
            lambdas.append(scale)
            rows.append({"basis": basis, "lambda": scale, "expval": round(ev, 5),
                         "ideal": IDEAL[basis], "err": round(err, 5)})
            print(f"{basis:>6} {scale:>7} | {ev:>8.4f} {IDEAL[basis]:>6.1f} {err:>8.4f}")
        per_basis[basis] = {
            "mean_err": float(np.mean(errs)),
            "gamma": ols_slope(lambdas, errs),
            "errs": [round(e, 5) for e in errs],
        }
    print("-" * 44)

    eXX = per_basis["XX"]["mean_err"]
    eYY = per_basis["YY"]["mean_err"]
    eZZ = per_basis["ZZ"]["mean_err"]
    gXX = per_basis["XX"]["gamma"]
    gZZ = per_basis["ZZ"]["gamma"]
    ratio_zx = eZZ / eXX if eXX > 1e-9 else float("inf")

    print(f"\n  SELECTED PAIR: {selected_pair}")
    print(f"  MEAN ERR: XX={eXX*100:.2f}pp  YY={eYY*100:.2f}pp  ZZ={eZZ*100:.2f}pp")
    print(f"  ZZ/XX error ratio = {ratio_zx:.2f}x   (marrakesh Finding 03 ref ~3x)")
    print(f"  SLOPE gamma: XX={gXX:+.4f}  ZZ={gZZ:+.4f}")

    t1 = (ratio_zx >= 2.0) and (eXX < eZZ)
    t2 = (eYY > eXX) and ((eYY - eXX) >= 0.02)
    t3 = gZZ > gXX
    print(f"\n=== PRE-REGISTERED CRITERIA (Exp34, {BACKEND_NAME}, calibration-gated) ===")
    print(f"T1 (X-IMMUNITY, headline): ZZ/XX={ratio_zx:.2f}x >= 2.0 AND eXX<eZZ "
          f"-> {'PASS' if t1 else 'FAIL'}")
    print(f"T2 (Y-INJECTION):          eYY {eYY*100:.2f}pp > eXX {eXX*100:.2f}pp (+>=2pp) "
          f"-> {'PASS' if t2 else 'FAIL'}")
    print(f"T3 (SLOPE ORDERING):       gamma_ZZ {gZZ:+.4f} > gamma_XX {gXX:+.4f} "
          f"-> {'PASS' if t3 else 'FAIL'}")
    if t1:
        verdict = ("Finding 03 X-basis immunity REPLICATES on an independent Heron device "
                   "(calibration-gated good pair) -> upgrades from marrakesh-specific observation "
                   "to heavy-hex ARCHITECTURAL principle. ORQ#1 upgrade gate MET.")
    else:
        verdict = ("On a calibration-verified-good pair, X-basis immunity does NOT meet the >=2x "
                   "gate -> CLEAN falsification (not a floor confound): the effect is marrakesh "
                   "substrate/calibration-specific, NOT architectural. Finding 03 framing needs "
                   "downgrade.")
    print(f"\nVERDICT: {verdict}")

    result = {
        "experiment": EXPERIMENT,
        "title": "X-Basis Noise Immunity — Calibration-Gated Retest (ORQ #1)",
        "cycle": CYCLE, "backend": BACKEND_NAME, "job_id": job_id,
        "selected_pair": selected_pair,
        "pair_selection_audit": audit,
        "open_research_question": "Does X-basis immunity (Finding 03) generalize across the "
                                  "heavy-hex family? Pre-reg gate: >=2x X/Z fidelity ratio on an "
                                  "independent backend. (Calibration-gated retest of Exp31.)",
        "marrakesh_reference": MARRAKESH_REF,
        "params": {"shots": SHOTS, "bases": BASES, "scale_factors": SCALE_FACTORS,
                   "circuits_total": len(schedule_items), "seed_transpiler": SEED_TRANSPILER,
                   "calibration_gate": {"RO_MAX": RO_MAX, "CZ_MAX": CZ_MAX}},
        "preregistered_criteria": {
            "T1": "eZZ/eXX >= 2.0 AND eXX < eZZ  [headline: README >=2x gate]",
            "T2": "eYY > eXX with eYY-eXX >= 0.02  [S-dagger injection signature]",
            "T3": "gamma_ZZ > gamma_XX  [Z-basis scales steeper under ZNE]",
            "T1_PASS": "Finding 03 = heavy-hex architectural principle (ORQ#1 upgrade met)",
            "T1_FAIL": "clean falsification on good pair: marrakesh substrate-specific",
        },
        "calibration": _load_calibration_snapshot(),
        "per_basis": {b: {"mean_err_pp": round(per_basis[b]["mean_err"] * 100, 3),
                          "gamma": round(per_basis[b]["gamma"], 5),
                          "errs": per_basis[b]["errs"]} for b in BASES},
        "summary": {
            "mean_err_XX_pp": round(eXX * 100, 3),
            "mean_err_YY_pp": round(eYY * 100, 3),
            "mean_err_ZZ_pp": round(eZZ * 100, 3),
            "ZZ_over_XX_ratio": round(ratio_zx, 3),
            "gamma_XX": round(gXX, 5),
            "gamma_ZZ": round(gZZ, 5),
            "T1": "PASS" if t1 else "FAIL",
            "T2": "PASS" if t2 else "FAIL",
            "T3": "PASS" if t3 else "FAIL",
            "verdict": verdict,
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
    args = parser.parse_args()

    if args.finalize:
        print(f"\n=== Fetching Exp {EXPERIMENT} (job {args.finalize}) ===")
        schedule_items, _, pair, audit = build_schedule_for_hardware()
        all_counts, status = get_counts_from_job(args.finalize, len(schedule_items))
        if all_counts is None:
            print(f"  Job not done yet ({status}).")
            return
        analyze(schedule_items, all_counts, job_id=args.finalize,
                selected_pair=pair, audit=audit)
    elif args.submit:
        print(f"\n=== Exp {EXPERIMENT}: building hardware schedule ({BACKEND_NAME}) ===")
        schedule_items, backend, pair, audit = build_schedule_for_hardware()
        print(f"\n=== Submitting to {BACKEND_NAME} ===")
        jid = submit_hardware(schedule_items, backend, pair, audit)
        print(f"\n  Finalize with:  python3 scripts/run_exp34_xbasis_calgated.py "
              f"--finalize {jid}")
    else:
        print(f"\n=== Exp {EXPERIMENT}: FakeMarrakesh simulation preview ===")
        schedule_items, backend, pair, audit = build_schedule_for_fake()
        all_counts = get_counts_from_fake(schedule_items, backend)
        analyze(schedule_items, all_counts, job_id="FakeMarrakesh-sim",
                selected_pair=pair, audit=audit)


if __name__ == "__main__":
    main()
