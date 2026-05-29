"""Exp 31: X-Basis Noise Immunity — Cross-Backend Replication (Whisper C3738).

OPEN RESEARCH QUESTION #1 (README): "Does X-basis immunity generalize across the heavy-hex
family? Replicate Finding 03 on an independent backend. Pre-reg gate: >=2x X/Z fidelity ratio."

Finding 03 (X-basis immunity) has three confirmations ALL on ibm_marrakesh (Bell C3650,
GHZ-3 C3651, VQE-H2 C3652). The claimed mechanism is architectural: the heavy-hex CZ channel
is Z-dephasing-dominated; the Hadamard for <XX> readout COMMUTES with it (transparent), while
the S-dagger for <YY> readout rotates latent Z-phase noise INTO the measurement axis. If
architectural, it must reproduce on an INDEPENDENT Heron device. This campaign has never left
marrakesh. ibm_kingston is the cleanest available independent backend.

DESIGN: Bell |Phi+> (H q0, CX q0->q1). Ideal <ZZ>=+1, <XX>=+1, <YY>=-1 (all |1|).
Basis-resolved ZNE: global-fold base (base.base_inv.base ...) at lambda in {1,3,5}, then append
the readout rotation:  ZZ -> none;  XX -> H both;  YY -> Sdg then H both;  then measure_all.
err_basis(lambda) = 1 - |<BB>_measured|.  3 bases x 3 lambda = 9 circuits, 4096 shots.
opt_level=0 (preserves folds -- C3720 ZNE-collapse lesson), seed_transpiler=42. One co-submitted
job -> single calibration snapshot (removes the +-7pp cross-day drift of the original 3 confs).

PRE-REGISTERED CRITERIA (FIXED before submission, see 31-...-preregistration.md):
  eXX,eYY,eZZ = mean err across lambda per basis; gamma_basis = OLS slope of err vs lambda.
  T1 (X-IMMUNITY REPLICATES, headline): eZZ/eXX >= 2.0 AND eXX < eZZ   [README gate]
  T2 (Y-INJECTION REPLICATES):          eYY > eXX  with eYY-eXX >= 0.02
  T3 (SLOPE ORDERING):                  gamma_ZZ > gamma_XX
  T1 PASS -> Finding 03 = heavy-hex ARCHITECTURAL principle.
  T1 FAIL -> X-basis immunity is marrakesh substrate/calibration-specific, NOT architectural.

Run (sim preview):   python3 scripts/run_exp31_xbasis_crossbackend.py
Run (hardware):      python3 scripts/run_exp31_xbasis_crossbackend.py --submit
Finalize:            python3 scripts/run_exp31_xbasis_crossbackend.py --finalize <job_id>
"""
import argparse
import json
import os
import numpy as np

EXPERIMENT = "31"
CYCLE = 3738
SHOTS = 4096
BASES = ["XX", "YY", "ZZ"]
SCALE_FACTORS = [1, 3, 5]
SEED_TRANSPILER = 42
BACKEND_NAME = "ibm_kingston"
RESULT_PATH = f"experiments/{EXPERIMENT}-xbasis-crossbackend-results.json"
JOBID_PATH = f"experiments/{EXPERIMENT}-jobid.txt"
CALIB_PATH = f"experiments/{EXPERIMENT}-calibration.json"

IDEAL = {"XX": +1.0, "YY": -1.0, "ZZ": +1.0}
# marrakesh reference (Finding 03 Bell C3650): ZZ/XX error ratio ~3x
MARRAKESH_REF = {"note": "Finding 03 Bell C3650: <XX> immune (flat), <ZZ> gamma~1.197 accel, "
                          "<YY> gamma~0.707; ZZ/XX err ratio ~3x"}


def build_bell_base():
    """Unmeasured Bell-state preparation |Phi+> = (|00>+|11>)/sqrt(2)."""
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
    # basis rotation: map target basis onto the computational (Z) axis
    if basis == "XX":
        qc.h(0)
        qc.h(1)
    elif basis == "YY":
        qc.sdg(0)
        qc.h(0)
        qc.sdg(1)
        qc.h(1)
    # ZZ: measure directly
    qc.measure_all()
    return qc


def counts_to_expval(counts, shots):
    """<B x B> = sum (-1)^(b0 ^ b1) P(b0 b1) from computational-basis counts."""
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


# ---------------------------------------------------------------------------
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

    def tfn(qc):
        return transpile(qc, backend=backend, optimization_level=0,
                         seed_transpiler=SEED_TRANSPILER)

    items = _build_schedule(tfn)
    print(f"  Built {len(items)} circuits on {BACKEND_NAME}")
    for (basis, scale, qc) in items:
        ops = qc.count_ops()
        cz = ops.get("cz", 0) + ops.get("ecr", 0) + ops.get("cx", 0)
        print(f"  {basis} lambda={scale}: depth={qc.depth()} 2q={cz} ops={dict(ops)}")
    return items, backend


def build_schedule_for_fake():
    from qiskit import transpile
    from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
    backend = FakeMarrakesh()

    def tfn(qc):
        return transpile(qc, backend=backend, optimization_level=0,
                         seed_transpiler=SEED_TRANSPILER)

    items = _build_schedule(tfn)
    for (basis, scale, qc) in items:
        ops = qc.count_ops()
        cz = ops.get("cz", 0) + ops.get("ecr", 0) + ops.get("cx", 0)
        print(f"  {basis} lambda={scale}: depth={qc.depth()} 2q={cz}")
    return items, backend


def submit_hardware(schedule_items, backend):
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
        try:
            phys = schedule_items[0][2].layout.final_index_layout()
        except Exception:
            phys = None
        snap = capture_calibration(backend, physical_qubits=phys)
        with open(CALIB_PATH, "w") as f:
            json.dump(snap, f, indent=4, default=str)
        print(f"  Calibration snapshot saved (updated {snap.get('last_update_date')})")
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


def analyze(schedule_items, all_counts, job_id=None):
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

    print(f"\n  MEAN ERR: XX={eXX*100:.2f}pp  YY={eYY*100:.2f}pp  ZZ={eZZ*100:.2f}pp")
    print(f"  ZZ/XX error ratio = {ratio_zx:.2f}x   (marrakesh Finding 03 ref ~3x)")
    print(f"  SLOPE gamma: XX={gXX:+.4f}  ZZ={gZZ:+.4f}")

    t1 = (ratio_zx >= 2.0) and (eXX < eZZ)
    t2 = (eYY > eXX) and ((eYY - eXX) >= 0.02)
    t3 = gZZ > gXX
    print(f"\n=== PRE-REGISTERED CRITERIA (Exp31, {BACKEND_NAME}) ===")
    print(f"T1 (X-IMMUNITY, headline): ZZ/XX={ratio_zx:.2f}x >= 2.0 AND eXX<eZZ "
          f"-> {'PASS' if t1 else 'FAIL'}")
    print(f"T2 (Y-INJECTION):          eYY {eYY*100:.2f}pp > eXX {eXX*100:.2f}pp (+>=2pp) "
          f"-> {'PASS' if t2 else 'FAIL'}")
    print(f"T3 (SLOPE ORDERING):       gamma_ZZ {gZZ:+.4f} > gamma_XX {gXX:+.4f} "
          f"-> {'PASS' if t3 else 'FAIL'}")
    if t1:
        verdict = ("Finding 03 X-basis immunity REPLICATES on an independent Heron device "
                   "-> upgrades from marrakesh-specific observation to heavy-hex ARCHITECTURAL "
                   "principle.")
    else:
        verdict = ("X-basis immunity does NOT meet the >=2x gate on this backend -> the effect "
                   "is marrakesh substrate/calibration-specific, NOT architectural. Finding 03's "
                   "'first-class compilation concern' framing requires downgrade.")
    print(f"\nVERDICT: {verdict}")

    result = {
        "experiment": EXPERIMENT,
        "title": "X-Basis Noise Immunity — Cross-Backend Replication (ORQ #1)",
        "cycle": CYCLE, "backend": BACKEND_NAME, "job_id": job_id,
        "open_research_question": "Does X-basis immunity (Finding 03) generalize across the "
                                  "heavy-hex family? Pre-reg gate: >=2x X/Z fidelity ratio on "
                                  "an independent backend.",
        "marrakesh_reference": MARRAKESH_REF,
        "params": {"shots": SHOTS, "bases": BASES, "scale_factors": SCALE_FACTORS,
                   "circuits_total": len(schedule_items), "seed_transpiler": SEED_TRANSPILER},
        "preregistered_criteria": {
            "T1": "eZZ/eXX >= 2.0 AND eXX < eZZ  [headline: README >=2x gate]",
            "T2": "eYY > eXX with eYY-eXX >= 0.02  [S-dagger injection signature]",
            "T3": "gamma_ZZ > gamma_XX  [Z-basis scales steeper under ZNE]",
            "T1_PASS": "Finding 03 = heavy-hex architectural principle",
            "T1_FAIL": "X-basis immunity is marrakesh substrate-specific, not architectural",
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
        print(f"\n  Finalize with:  python3 scripts/run_exp31_xbasis_crossbackend.py "
              f"--finalize {jid}")
    else:
        print(f"\n=== Exp {EXPERIMENT}: FakeMarrakesh simulation preview ===")
        schedule_items, backend = build_schedule_for_fake()
        all_counts = get_counts_from_fake(schedule_items, backend)
        analyze(schedule_items, all_counts, job_id="FakeMarrakesh-sim")


if __name__ == "__main__":
    main()
