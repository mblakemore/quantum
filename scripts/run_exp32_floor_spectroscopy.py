"""Exp 32: Transient-Floor Spectroscopy — turning Exp31's confound into signal (Whisper C3739).

CONTEXT. Exp31 (ORQ #1, X-basis cross-backend on ibm_kingston) was INCONCLUSIVE/CONFOUNDED: a
1-CZ Bell state showed ~20pp error (5x worse than the 0.16% CZ + ~1% readout calibration
predicts), the error was FLAT across ZNE folding (gate-count-independent), and all three bases
(XX/YY/ZZ) collapsed to ~0.76 -- the signature of a constant SPAM / layout / transient-device
FLOOR that swamped the gate-noise mechanism Finding 03 describes.

Creator (Discord, C3739) asked three questions about that floor:
  Q1. "Could it be mapped?"
  Q2. "Would more calibration samples before and after help define the vectors we're chasing?"
  Q3. "What about colliding with other perturbations to extrapolate more info from info-rich
       failures?"

This experiment answers all three with one co-submitted job (single calibration snapshot) plus a
SECOND calibration snapshot at finalize time. Four arms, each targeting one question:

  ARM A (Q1 map): SPAM isolation. Prepare each computational basis state |00>,|01>,|10>,|11> with
      X gates only -- NO entangling, NO superposition -- and measure. P(misread) = the pure
      state-prep+measurement (readout-assignment) floor. Isolates the SPAM component.

  ARM B (Q1 map + Q2 vectors): LAYOUT scan. Same lambda=1 Bell <ZZ> on THREE distinct physical CZ
      pairs (pinned initial_layout), with each pair's calibration CZ+readout error recorded. Post
      hoc: does the floor TRACK the recorded per-pair error (-> calibration is right, Exp31 hit a
      bad pair) or is it UNIFORMLY high regardless (-> device-wide transient, calibration stale)?
      This is the "vector" the Creator means: the floor resolved across the layout axis.

  ARM C (Q2 before/after): BOOKEND drift. The pair-0 lambda=1 Bell <ZZ> appears as circuit #0
      (FIRST submitted) and again as the LAST circuit. err_first vs err_last = intra-run drift.
      Combined with submit-time AND finalize-time backend.properties() snapshots, this brackets
      the run: static floor (first==last, snapshots agree) vs transient floor (they diverge).

  ARM D (Q3 collide): COHERENT-PHASE collision scan. Prepare Bell, inject a KNOWN perturbation
      RZ(theta) on q1, sweep theta in {0..7pi/4}, measure <XX>. Ideal <XX> = cos(theta). Fit
      <XX>(theta) = A*cos(theta + phi):
        - A  (amplitude)  = the INCOHERENT (depolarizing/SPAM) attenuation of the floor.
        - phi (phase off) = the COHERENT stray-Z component (a miscalibrated phase shows up as a
          rigid phase offset; pure depolarizing leaves phi=0).
      Colliding the unknown floor with a known coherent knob makes a CONFOUNDED failure info-rich:
      one scan separates the floor into coherent vs incoherent parts -- more than a clean pass yields.

This is the do()/identification discipline (Exp30 IDLE arm, Exp31 flatness check) generalized:
ZNE was do(gate_count) and showed the floor is NOT gate-count. Here we do(basis-prep), do(layout),
do(time-position), do(coherent-phase) to find which variables the floor IS a function of.

PRE-REGISTERED READOUTS (descriptive map, not a single pass/fail -- this is a characterization):
  M1 (SPAM share):     readout floor from Arm A; compare to the ~20pp Bell floor -> SPAM fraction.
  M2 (layout-driven?): corr(floor, recorded per-pair error) across Arm B. HIGH (>0.6) => bad-pair
                       /calibration-valid; LOW + uniformly-high => device-wide transient.
  M3 (drift):          |err_last - err_first| from Arm C; >0.03 => transient within the run.
  M4 (coherent split): A and phi from Arm D. |phi|>0.15 rad => a real coherent component;
                       (1-A) => incoherent floor magnitude.
  VERDICT classes: (i) SPAM-dominated, (ii) bad-pair/layout, (iii) coherent miscalibration,
  (iv) device-wide transient -- decided by which of M1-M4 fires.

Backend ibm_kingston (the device that showed the floor). 8192 shots. opt_level=1 with pinned
initial_layout per arm. One job -> single submit-snapshot; finalize captures the after-snapshot.

Run (sim preview):   python3 scripts/run_exp32_floor_spectroscopy.py
Run (hardware):      python3 scripts/run_exp32_floor_spectroscopy.py --submit
Finalize:            python3 scripts/run_exp32_floor_spectroscopy.py --finalize <job_id>
"""
import argparse
import json
import os
import math
import numpy as np

EXPERIMENT = "32"
CYCLE = 3739
SHOTS = 8192
SEED_TRANSPILER = 42
BACKEND_NAME = "ibm_kingston"
N_LAYOUT_PAIRS = 3
PHASE_THETAS = [i * math.pi / 4 for i in range(8)]   # 0, 45, ..., 315 deg
SPAM_STATES = ["00", "01", "10", "11"]
RESULT_PATH = f"experiments/{EXPERIMENT}-floor-spectroscopy-results.json"
JOBID_PATH = f"experiments/{EXPERIMENT}-jobid.txt"
CALIB_PATH = f"experiments/{EXPERIMENT}-calibration.json"
CALIB_FINAL_PATH = f"experiments/{EXPERIMENT}-calibration-finalize.json"
EXP31_BELL_FLOOR_PP = 20.36   # Exp31 kingston mean ZZ error (reference)


# ---- circuit builders (logical 2-qubit; layout pinned at transpile) --------
def build_bell_zz():
    """Bell |Phi+>, measure ZZ directly. Ideal <ZZ>=+1."""
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(2)
    qc.h(0); qc.cx(0, 1)
    qc.measure_all()
    return qc


def build_spam(state):
    """Prepare computational basis |state> with X gates only (no entanglement)."""
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(2)
    if state[0] == "1":
        qc.x(0)
    if state[1] == "1":
        qc.x(1)
    qc.measure_all()
    return qc


def build_phase_collision(theta):
    """Bell, inject RZ(theta) on q1, measure XX (append H,H). Ideal <XX>=cos(theta)."""
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(2)
    qc.h(0); qc.cx(0, 1)
    qc.rz(theta, 1)
    qc.h(0); qc.h(1)        # rotate X-basis onto Z for measurement
    qc.measure_all()
    return qc


def counts_to_zz(counts):
    """<Z x Z> = sum (-1)^(b0^b1) P(b0 b1)."""
    total, acc = 0, 0.0
    for bitstr, c in counts.items():
        bits = bitstr.replace(" ", "")[-2:]
        total += c
        acc += ((-1) ** (int(bits[0]) ^ int(bits[1]))) * c
    return acc / (total if total else SHOTS)


def counts_correct_prob(counts, target):
    """P(measured == target bitstring)."""
    total = sum(counts.values())
    hit = 0
    for bitstr, c in counts.items():
        if bitstr.replace(" ", "")[-2:] == target:
            hit += c
    return hit / (total if total else SHOTS)


def fit_acos(thetas, vals):
    """Fit v = A cos(theta+phi) = c1 cos(theta) + c2 sin(theta). Return A, phi(rad)."""
    th = np.asarray(thetas, float)
    v = np.asarray(vals, float)
    M = np.vstack([np.cos(th), np.sin(th)]).T
    (c1, c2), *_ = np.linalg.lstsq(M, v, rcond=None)
    A = float(math.hypot(c1, c2))
    phi = float(math.atan2(-c2, c1))
    return A, phi


# ---- layout pair selection -------------------------------------------------
def select_cz_pairs(backend, n_pairs):
    """Pick n_pairs distinct, qubit-disjoint CZ edges from the coupling map.
    Returns list of (q0,q1). Falls back to first edges if errors unavailable."""
    cmap = None
    try:
        cmap = list(backend.coupling_map.get_edges())
    except Exception:
        try:
            cmap = list(backend.configuration().coupling_map)
        except Exception:
            cmap = [(0, 1), (2, 3), (4, 5)]
    # de-dup undirected
    seen, edges = set(), []
    for (a, b) in cmap:
        key = tuple(sorted((a, b)))
        if key not in seen:
            seen.add(key); edges.append((a, b))
    # try to sort by CZ error (best first) so pair0 is a good pair
    def edge_err(e):
        try:
            props = backend.properties()
            for g in ("cz", "ecr", "cx"):
                try:
                    return props.gate_error(g, list(e))
                except Exception:
                    continue
        except Exception:
            pass
        return 1.0
    try:
        edges.sort(key=edge_err)
    except Exception:
        pass
    # choose qubit-disjoint pairs spread across the sorted list
    chosen, used = [], set()
    idxs = [0, len(edges) // 2, len(edges) - 1] if len(edges) >= 3 else range(len(edges))
    for i in idxs:
        e = edges[i]
        if e[0] in used or e[1] in used:
            # find next disjoint
            for e2 in edges:
                if e2[0] not in used and e2[1] not in used:
                    e = e2; break
        chosen.append(e); used.update(e)
        if len(chosen) >= n_pairs:
            break
    while len(chosen) < n_pairs and len(edges) > len(chosen):
        chosen.append(edges[len(chosen)])
    return chosen[:n_pairs]


def pair_calib(backend, pair):
    try:
        from calibration_snapshot import capture_calibration
        snap = capture_calibration(backend, physical_qubits=list(pair))
        return snap
    except Exception as e:
        return {"available": False, "error": str(e)}


# ---- schedule assembly -----------------------------------------------------
def _assemble(transpile_fn, backend, pairs):
    """Build the full ordered schedule. Each item = (arm, label, circuit, meta)."""
    items = []
    p0 = pairs[0]
    # ARM C bookend FIRST: pair0 Bell ZZ at position 0
    items.append(("C", "bell_zz_first", transpile_fn(build_bell_zz(), p0), {"pair": list(p0)}))
    # ARM A SPAM on pair0
    for s in SPAM_STATES:
        items.append(("A", f"spam_{s}", transpile_fn(build_spam(s), p0), {"pair": list(p0), "state": s}))
    # ARM B layout: pair0 already measured at C; add pair1,2 Bell ZZ
    for idx, pr in enumerate(pairs):
        items.append(("B", f"layout_pair{idx}", transpile_fn(build_bell_zz(), pr),
                       {"pair": list(pr), "pair_idx": idx}))
    # ARM D coherent-phase collision on pair0
    for th in PHASE_THETAS:
        items.append(("D", f"phase_{round(math.degrees(th))}", transpile_fn(build_phase_collision(th), p0),
                       {"pair": list(p0), "theta": th}))
    # ARM C bookend LAST: pair0 Bell ZZ at final position
    items.append(("C", "bell_zz_last", transpile_fn(build_bell_zz(), p0), {"pair": list(p0)}))
    return items


def build_schedule_for_hardware():
    from qiskit import transpile
    from qiskit_ibm_runtime import QiskitRuntimeService
    service = QiskitRuntimeService()
    backend = service.backend(BACKEND_NAME)
    pairs = select_cz_pairs(backend, N_LAYOUT_PAIRS)
    print(f"  Selected layout pairs: {pairs}")
    pair_calibs = {f"pair{i}": pair_calib(backend, p) for i, p in enumerate(pairs)}

    def tfn(qc, pair):
        return transpile(qc, backend=backend, optimization_level=1,
                         initial_layout=list(pair), seed_transpiler=SEED_TRANSPILER)

    items = _assemble(tfn, backend, pairs)
    print(f"  Built {len(items)} circuits on {BACKEND_NAME}")
    return items, backend, pairs, pair_calibs


def build_schedule_for_fake():
    from qiskit import transpile
    from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
    backend = FakeMarrakesh()
    pairs = select_cz_pairs(backend, N_LAYOUT_PAIRS)
    print(f"  (sim) layout pairs: {pairs}")
    pair_calibs = {f"pair{i}": {"available": False} for i in range(len(pairs))}

    def tfn(qc, pair):
        return transpile(qc, backend=backend, optimization_level=1,
                         initial_layout=list(pair), seed_transpiler=SEED_TRANSPILER)

    items = _assemble(tfn, backend, pairs)
    return items, backend, pairs, pair_calibs


def submit_hardware(items, backend, pairs, pair_calibs):
    from qiskit_ibm_runtime import SamplerV2
    sampler = SamplerV2(mode=backend)
    sampler.options.default_shots = SHOTS
    circuits = [it[2] for it in items]
    job = sampler.run([(qc,) for qc in circuits])
    job_id = job.job_id()
    with open(JOBID_PATH, "w") as f:
        f.write(job_id + "\n")
    try:
        from calibration_snapshot import capture_calibration
        snap = capture_calibration(backend, physical_qubits=list(pairs[0]))
        snap["snapshot_phase"] = "submit"
        snap["layout_pairs"] = [list(p) for p in pairs]
        snap["per_pair"] = pair_calibs
        with open(CALIB_PATH, "w") as f:
            json.dump(snap, f, indent=4, default=str)
        print(f"  Submit calibration snapshot saved (updated {snap.get('last_update_date')})")
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
        return None, status, None
    res = job.result()
    all_counts = []
    for i in range(n_circuits):
        databin = res[i].data
        reg = list(databin.__dict__.keys())[0]
        all_counts.append(getattr(databin, reg).get_counts())
    # after-snapshot (Q2 "calibration after")
    after = None
    try:
        from qiskit_ibm_runtime import QiskitRuntimeService as S2
        from calibration_snapshot import capture_calibration
        bk = S2().backend(BACKEND_NAME)
        after = capture_calibration(bk)
        after["snapshot_phase"] = "finalize"
        with open(CALIB_FINAL_PATH, "w") as f:
            json.dump(after, f, indent=4, default=str)
    except Exception as e:
        after = {"available": False, "error": str(e)}
    return all_counts, "DONE", after


def get_counts_from_fake(items, backend):
    from qiskit_aer.primitives import SamplerV2 as AerSampler
    from qiskit_aer.noise import NoiseModel
    nm = NoiseModel.from_backend(backend)
    sampler = AerSampler(options={
        "backend_options": {"noise_model": nm},
        "run_options": {"shots": SHOTS, "seed": SEED_TRANSPILER},
    })
    circuits = [it[2] for it in items]
    res = sampler.run([(c,) for c in circuits]).result()
    out = []
    for i in range(len(circuits)):
        data = res[i].data
        reg = list(data.__dict__.keys())[0]
        out.append(getattr(data, reg).get_counts())
    return out


def _load(path, default):
    try:
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
    except Exception:
        pass
    return default


def analyze(items, all_counts, job_id=None, calib_after=None):
    by = {it[1]: (it[0], it[3], counts) for it, counts in zip(items, all_counts)}

    # ARM A: SPAM readout floor
    spam = {}
    for s in SPAM_STATES:
        arm, meta, counts = by[f"spam_{s}"]
        # prepared logical (q0=s[0], q1=s[1]) reads back little-endian as s[::-1] (qubit0 rightmost)
        pc = counts_correct_prob(counts, s[::-1])
        spam[s] = {"p_correct": round(pc, 5), "readout_err_pp": round((1 - pc) * 100, 3)}
    spam_floor_pp = float(np.mean([spam[s]["readout_err_pp"] for s in SPAM_STATES]))

    # ARM B: layout scan -- floor vs recorded per-pair error
    submit_snap = _load(CALIB_PATH, {})
    per_pair_cal = submit_snap.get("per_pair", {})
    layout = []
    for it in items:
        if it[0] == "B":
            label = it[1]; idx = it[3]["pair_idx"]; pair = it[3]["pair"]
            _, _, counts = by[label]
            zz = counts_to_zz(counts)
            err_pp = (1 - abs(zz)) * 100
            cal = per_pair_cal.get(f"pair{idx}", {})
            rec_cz = cal.get("cz_error_median") or cal.get("two_qubit_error") or cal.get("gate_error")
            rec_ro = cal.get("readout_error_median") or cal.get("readout_error")
            layout.append({"pair_idx": idx, "pair": pair, "zz": round(zz, 5),
                           "floor_err_pp": round(err_pp, 3),
                           "recorded_cz_err": rec_cz, "recorded_readout_err": rec_ro})
    # correlation floor vs recorded error (if available)
    floors = [r["floor_err_pp"] for r in layout]
    recs = [r["recorded_cz_err"] for r in layout if isinstance(r["recorded_cz_err"], (int, float))]
    layout_corr = None
    if len(recs) == len(floors) and len(floors) >= 2 and np.std(recs) > 0 and np.std(floors) > 0:
        layout_corr = float(np.corrcoef(floors, recs)[0, 1])
    floor_uniform = (np.std(floors) < 2.0) and (np.mean(floors) > 8.0)  # all high, little spread

    # ARM C: bookend drift
    zz_first = counts_to_zz(by["bell_zz_first"][2])
    zz_last = counts_to_zz(by["bell_zz_last"][2])
    err_first = (1 - abs(zz_first)) * 100
    err_last = (1 - abs(zz_last)) * 100
    drift_pp = abs(err_last - err_first)

    # ARM D: coherent-phase collision
    thetas, xx_vals = [], []
    for it in items:
        if it[0] == "D":
            th = it[3]["theta"]
            _, _, counts = by[it[1]]
            xx = counts_to_zz(counts)   # after H,H rotation, ZZ-parity == XX
            thetas.append(th); xx_vals.append(xx)
    order = np.argsort(thetas)
    thetas = list(np.array(thetas)[order]); xx_vals = list(np.array(xx_vals)[order])
    A, phi = fit_acos(thetas, xx_vals)
    incoherent_floor = round((1 - A) * 100, 3)
    coherent_phase_rad = round(phi, 4)

    # readouts
    m1_spam = round(spam_floor_pp, 3)
    m1_spam_share = round(spam_floor_pp / EXP31_BELL_FLOOR_PP, 3)
    m3_drift = round(drift_pp, 3)
    m4_phi = coherent_phase_rad
    m4_incoh = incoherent_floor

    # verdict classification
    classes = []
    if m1_spam_share >= 0.6:
        classes.append("SPAM-dominated (readout floor explains most of the Exp31 Bell error)")
    if layout_corr is not None and layout_corr >= 0.6:
        classes.append("bad-pair/layout (floor tracks recorded per-pair error; Exp31 hit a bad pair)")
    if floor_uniform and (layout_corr is None or layout_corr < 0.6):
        classes.append("device-wide transient (floor uniformly high, decoupled from recorded error)")
    if abs(m4_phi) > 0.15:
        classes.append(f"coherent miscalibration (stray phase phi={m4_phi} rad in XX scan)")
    if m3_drift > 3.0:
        classes.append(f"transient-within-run (bookend drift {m3_drift}pp)")
    if not classes:
        classes.append("incoherent/depolarizing floor, no single dominant identified source")

    # calibration before/after delta (Q2)
    cal_delta = None
    if calib_after is None:
        calib_after = _load(CALIB_FINAL_PATH, None)
    if isinstance(calib_after, dict) and submit_snap:
        def g(d, *keys):
            for k in keys:
                if k in d and isinstance(d[k], (int, float)):
                    return d[k]
            return None
        b_ro = g(submit_snap, "readout_error_median", "readout_error")
        a_ro = g(calib_after, "readout_error_median", "readout_error")
        cal_delta = {"submit_update": submit_snap.get("last_update_date"),
                     "finalize_update": calib_after.get("last_update_date"),
                     "readout_err_submit": b_ro, "readout_err_finalize": a_ro,
                     "recalibrated_during_run": (submit_snap.get("last_update_date")
                                                 != calib_after.get("last_update_date"))}

    print(f"\n=== Exp 32 FLOOR SPECTROSCOPY ({BACKEND_NAME}) ===")
    print(f"ARM A (SPAM): readout floor = {m1_spam}pp  (Exp31 Bell floor {EXP31_BELL_FLOOR_PP}pp "
          f"-> SPAM share {m1_spam_share})")
    for s in SPAM_STATES:
        print(f"    |{s}>: readout_err {spam[s]['readout_err_pp']}pp")
    print(f"ARM B (LAYOUT): floors {floors} pp  corr(floor,recorded_cz)="
          f"{layout_corr}  uniform_high={floor_uniform}")
    print(f"ARM C (DRIFT): err_first={round(err_first,3)}pp err_last={round(err_last,3)}pp "
          f"drift={m3_drift}pp")
    print(f"ARM D (COLLISION): <XX>=A*cos(theta+phi) -> A={round(A,4)} (incoherent floor "
          f"{m4_incoh}pp), phi={m4_phi} rad")
    print(f"\nVERDICT (floor map): {'; '.join(classes)}")
    if cal_delta:
        print(f"CAL before/after: recalibrated_during_run={cal_delta['recalibrated_during_run']} "
              f"(submit {cal_delta['submit_update']} -> finalize {cal_delta['finalize_update']})")

    result = {
        "experiment": EXPERIMENT,
        "title": "Transient-Floor Spectroscopy (Exp31 confound -> signal)",
        "cycle": CYCLE, "backend": BACKEND_NAME, "job_id": job_id,
        "answers_creator_questions": {
            "Q1_map": "ARM A (SPAM) + ARM B (layout) decompose the floor by source",
            "Q2_before_after": "submit + finalize calibration snapshots + ARM C bookends",
            "Q3_collide": "ARM D coherent-phase collision separates coherent vs incoherent",
        },
        "exp31_reference_bell_floor_pp": EXP31_BELL_FLOOR_PP,
        "params": {"shots": SHOTS, "n_layout_pairs": N_LAYOUT_PAIRS,
                   "phase_thetas_deg": [round(math.degrees(t)) for t in PHASE_THETAS],
                   "spam_states": SPAM_STATES, "seed_transpiler": SEED_TRANSPILER},
        "arm_A_spam": {"per_state": spam, "readout_floor_pp": m1_spam, "spam_share_of_bell": m1_spam_share},
        "arm_B_layout": {"rows": layout, "corr_floor_vs_recorded_cz": layout_corr,
                          "floor_uniform_high": bool(floor_uniform)},
        "arm_C_drift": {"err_first_pp": round(err_first, 3), "err_last_pp": round(err_last, 3),
                         "drift_pp": m3_drift},
        "arm_D_collision": {"thetas_rad": [round(t, 4) for t in thetas],
                             "xx_vals": [round(v, 5) for v in xx_vals],
                             "fit_amplitude_A": round(A, 5), "coherent_phase_rad": m4_phi,
                             "incoherent_floor_pp": m4_incoh},
        "calibration_submit": submit_snap if submit_snap else _load(CALIB_PATH, {}),
        "calibration_before_after": cal_delta,
        "verdict_classes": classes,
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
        items, _, _, _ = build_schedule_for_hardware()
        all_counts, status, after = get_counts_from_job(args.finalize, len(items))
        if all_counts is None:
            print(f"  Job not done yet ({status}).")
            return
        analyze(items, all_counts, job_id=args.finalize, calib_after=after)
    elif args.submit:
        print(f"\n=== Exp {EXPERIMENT}: building hardware schedule ({BACKEND_NAME}) ===")
        items, backend, pairs, pair_calibs = build_schedule_for_hardware()
        print(f"\n=== Submitting to {BACKEND_NAME} ===")
        jid = submit_hardware(items, backend, pairs, pair_calibs)
        print(f"\n  Finalize with:  python3 scripts/run_exp32_floor_spectroscopy.py --finalize {jid}")
    else:
        print(f"\n=== Exp {EXPERIMENT}: FakeMarrakesh simulation preview ===")
        items, backend, pairs, pair_calibs = build_schedule_for_fake()
        all_counts = get_counts_from_fake(items, backend)
        analyze(items, all_counts, job_id="FakeMarrakesh-sim")


if __name__ == "__main__":
    main()
