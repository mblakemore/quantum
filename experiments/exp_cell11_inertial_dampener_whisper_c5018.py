#!/usr/bin/env python3
"""CELL 11 — THE INERTIAL DAMPENER (Whisper C5018, Creator "Fly Cell11!" general#4300).

Undo the ship's own motion: the clock-or-coin census (quantum@5201592) measured drift as a
COHERENT epoch rotation (q73: ~0.21 deg/layer, linear in depth, 50-90 sigma/row). A coherent
rotation can be measured and DIALED OUT. This flight certifies exactly that, as a working
feedback machine:

  JOB A (measure the clock): re-fly the census rows (3 depths x 3 bases, uncompensated) at
    the flight epoch -> fresh Bloch vectors v_now(D) -> fit (axis, per-layer angle) of the
    rotation banked-epoch1 -> now, per drifter.
  JOB B (dial it out, same cal window, minutes later): same rows PLUS compensated rows where
    a terminal inverse rotation R^dag(axis, rate*D) — constants FROZEN from Job A's fit — is
    applied to each drifter before measurement. Grade compensated vs BANKED EPOCH-1.

MODEL CLASS (pre-registered): the epoch shift acts on the final single-qubit state as a
FIXED-AXIS rotation linear in depth. The census supports it (constant deg/layer, preserved
length). The dampener claim is exactly the model's engineering test: if the model is right,
terminal inverse rotation restores epoch-1's Bloch vectors.

FROZEN VERDICT RULE (three-state, per drifter per depth, committed BEFORE any flight):
  eligible   : uncompensated |dtheta(now vs epoch1)| > 3 sigma  (there is something to damp)
  DAMPED     : eligible AND compensated |dtheta(comp vs epoch1)| < 3 sigma
  NOT-DAMPED : eligible AND compensated |dtheta| >= 3 sigma
  UNDERPOWERED: not eligible (nothing to damp at this depth — reported, gates nothing)
  Primary target: q73 (the census's 50-90 sigma clock). q23/q26 secondary. q53 (MIXED in the
  census) flies REPORTED-NOT-GATED — its shrinkage component is what compensation cannot fix,
  an informative control, not a gate.
  FREE CONSISTENCY CHECK (physics, not stats): if the fitted axis is ~Z, compensation is an
  Rz before measurement and CANNOT change Z-basis rows — Z rows of comp and uncomp arms must
  agree within noise; a Z-row shift flags a compile error, not physics.
  SAME-CAL GATE: Job B flies only if backend properties last_update_date is UNCHANGED from
  Job A's read; a recal between A and B invalidates the frozen constants -> re-run A.

$0 SELF-TEST: --fit runs the fitter on the BANKED census epochs (1->2), where the answer is
known (~0.21 deg/layer on q73, axis unknown-but-consistent): the fitter must recover a
depth-consistent axis and rate before any QPU is spent.
"""
import json, os, sys, datetime
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
QROOT = os.path.join(HERE, "..")
RES = os.path.join(QROOT, "results")
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(QROOT, "scripts"))

BANKED = ["d9kq85jhdfks73ck12gg", "d9l4ncrjf64c739j1q8g"]   # census epochs 1,2 (Jul 29)
CENSUS = os.path.join(RES, f"exp_drift_purity_probe_census_{BANKED[0]}_{BANKED[1]}.json")
DEPTHS = [160, 280, 400]          # trimmed from census 5 for cost; spans the linear range
SHOTS = 8000
DRIFTERS_GATED = [73, 26, 23]     # q53 reported-not-gated
ACCOUNT = "IBMQ_ALT"              # the probe's account; preflight-checked at submit
BACKEND = "ibm_kingston"


def bloch_from_census(job_key_prefix=None):
    """Banked per-epoch Bloch vectors from the census report: {q: {D: v(3)}} per epoch."""
    rep = json.load(open(CENSUS))
    out = {}
    for j, ep in rep["per_epoch"].items():
        out[j] = {int(q): {r["depth"]: np.array(r["bloch"], float) for r in d["rows"]}
                  for q, d in ep.items()}
    return out


def fit_axis_rate(v1_by_D, v2_by_D):
    """Fit fixed axis n and per-layer rate w minimizing sum |R(n, w*D) v1(D) - v2(D)|^2.
    Coarse-to-fine grid over the sphere + rate; adequate for 3-5 depth points."""
    Ds = sorted(set(v1_by_D) & set(v2_by_D))
    if not Ds:
        return None

    def loss(n, w):
        s = 0.0
        for D in Ds:
            v1, v2 = v1_by_D[D], v2_by_D[D]
            th = np.radians(w * D)
            c, sn = np.cos(th), np.sin(th)
            vr = v1 * c + np.cross(n, v1) * sn + n * np.dot(n, v1) * (1 - c)
            s += float(np.sum((vr - v2) ** 2))
        return s

    best = (None, None, np.inf)
    # coarse sphere grid
    for u in np.linspace(-1, 1, 21):
        for ph in np.linspace(0, 2 * np.pi, 41, endpoint=False):
            r = np.sqrt(max(0.0, 1 - u * u))
            n = np.array([r * np.cos(ph), r * np.sin(ph), u])
            for w in np.linspace(-0.5, 0.5, 101):
                L = loss(n, w)
                if L < best[2]:
                    best = (n, w, L)
    n, w, L = best
    # refine
    for _ in range(3):
        for dn in [0.05, 0.01]:
            cands = [n]
            for ax in range(3):
                for s in (+dn, -dn):
                    m = n.copy(); m[ax] += s; m /= np.linalg.norm(m); cands.append(m)
            for m in cands:
                for w2 in np.linspace(w - 0.02, w + 0.02, 41):
                    L2 = loss(m, w2)
                    if L2 < L:
                        n, w, L = m, w2, L2
    resid = np.sqrt(L / len(Ds))
    return {"axis": [round(float(x), 4) for x in n], "rate_deg_per_layer": round(float(w), 4),
            "rms_resid": round(float(resid), 4), "depths": Ds}


def do_fit_banked():
    ep = bloch_from_census()
    j1, j2 = BANKED
    fits = {}
    for q in sorted(set(ep[j1]) & set(ep[j2])):
        f = fit_axis_rate(ep[j1][q], ep[j2][q])
        fits[q] = f
        print(f"q{q}: axis {f['axis']} rate {f['rate_deg_per_layer']} deg/layer rms {f['rms_resid']}")
    out = os.path.join(RES, "cell11_banked_fit_c5018.json")
    json.dump({"fits": {str(q): f for q, f in fits.items()}, "epochs": BANKED}, open(out, "w"), indent=1)
    print(f"-> {out}")
    return fits


def build_rows(backend, compensation=None):
    """Census rows at DEPTHS x 3 bases (+cal0/cal1). compensation: {q: (axis, rate)} applies
    terminal inverse rotation before basis change."""
    from exp_crossblock_widesweep import build_twins, DRIFTERS, SEED, NPHYS
    from qiskit import QuantumCircuit, transpile
    twins, active = build_twins(backend)
    drifters_active = [q for q in DRIFTERS if q in active]
    pubs, meta = [], []
    for state, tag in ((0, "cal0"), (1, "cal1")):
        qc = QuantumCircuit(NPHYS)
        if state:
            qc.x(range(NPHYS))
        qc.measure_all()
        pubs.append((transpile(qc, backend, optimization_level=0), None, SHOTS))
        meta.append({"block": tag, "shots": SHOTS})
    for D in DEPTHS:
        for B in ("Z", "X", "Y"):
            qc = twins[D].copy()
            arm = "uncomp"
            if compensation:
                arm = "comp"
                for q in drifters_active:
                    if q in compensation:
                        n, w = compensation[q]
                        th = -np.radians(w * D)          # inverse rotation
                        # decompose axis-angle into Rz*Ry*Rz via rotation matrix -> use qiskit
                        from qiskit.circuit.library import UnitaryGate
                        c, s = np.cos(th / 2), np.sin(th / 2)
                        nx, ny, nz = n
                        U = np.array([[c - 1j * s * nz, -s * (ny + 1j * nx)],
                                      [s * (ny - 1j * nx), c + 1j * s * nz]])
                        qc.append(UnitaryGate(U, label=f"damp{q}"), [q])
            if B == "X":
                for q in drifters_active:
                    qc.h(q)
            elif B == "Y":
                for q in drifters_active:
                    qc.sdg(q); qc.h(q)
            qc.measure_all()
            tqc = transpile(qc, backend, optimization_level=0,
                            initial_layout=list(range(NPHYS)), seed_transpiler=SEED)
            d2q = sum(1 for i in tqc.data if i.operation.num_qubits == 2)
            assert d2q > 0, f"pad-cancel at depth {D} — do not submit"
            pubs.append((tqc, None, SHOTS))
            meta.append({"block": f"{arm}_d{D}_{B}", "depth": D, "basis": B, "arm": arm,
                         "shots": SHOTS})
    return pubs, meta, drifters_active


def submit(job_tag, with_comp):
    from ibm_multi_account import service_for_submission
    from qiskit_ibm_runtime import SamplerV2
    svc = service_for_submission(ACCOUNT)
    u = svc.usage()
    print(f"POOL ({ACCOUNT}): {u['usage_remaining_seconds']}s remaining")
    backend = svc.backend(BACKEND)
    props = backend.properties()
    cal = str(props.last_update_date)
    print(f"{BACKEND} cal epoch: {cal}")
    comp = None
    if with_comp:
        fitA = json.load(open(os.path.join(RES, "cell11_jobA_fit_c5018.json")))
        if fitA["cal_epoch"] != cal:
            sys.exit(f"SAME-CAL GATE FAILED: Job A cal {fitA['cal_epoch']} != now {cal} — re-run Job A")
        comp = {int(q): (np.array(f["axis"]), f["rate_deg_per_layer"])
                for q, f in fitA["fits"].items() if f}
        print(f"[comp] frozen constants from Job A: " +
              " ".join(f"q{q}:{w:.3f}deg/L" for q, (n, w) in comp.items()))
    pubs, meta, drifters = build_rows(backend, compensation=comp)
    # Job B carries BOTH arms: uncompensated controls + compensated rows
    if with_comp:
        pubs_u, meta_u, _ = build_rows(backend, compensation=None)
        pubs += pubs_u[2:]; meta += meta_u[2:]   # skip duplicate cals
    job = SamplerV2(mode=backend).run(pubs)
    man = {"card": f"cell11_inertial_dampener_{job_tag}", "cycle": "C5018",
           "substrate": "claude-fable-5", "backend": BACKEND, "account": ACCOUNT,
           "cal_epoch": cal, "depths": DEPTHS, "shots": SHOTS,
           "drifters_active": drifters, "gated": DRIFTERS_GATED,
           "banked_reference": BANKED[0],
           "go": "Creator general#4300 'Fly Cell11!'",
           "pubs_meta": meta, "job_id": job.job_id(),
           "submit_iso": datetime.datetime.utcnow().isoformat() + "Z"}
    path = os.path.join(RES, f"cell11_{job_tag}_manifest_{job.job_id()}.json")
    json.dump(man, open(path, "w"), indent=1)
    print(f"SUBMITTED {job.job_id()} -> {path}")


if __name__ == "__main__":
    if "--fit" in sys.argv:
        do_fit_banked()
    elif "--joba" in sys.argv:
        submit("jobA", with_comp=False)
    elif "--jobb" in sys.argv:
        submit("jobB", with_comp=True)
    else:
        print("modes: --fit (banked, $0) | --joba | --jobb  (decode via cell11_decode)")
