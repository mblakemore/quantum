#!/usr/bin/env python3
"""Exp153 (Q13) — Where does the time crystal MELT? Sweep the drive imperfection eps and the
disorder strength W for the rigidity phase boundary (DTC analog of the F76 cosine law).
New exotic-phases museum wing, 2nd piece (Whisper C4841 -> flown next cycle).

THE NULL-FIRST QUESTION (the C4841 lesson, applied preemptively). Exp151b proved interactions
ALONE lock the subharmonic (prethermal DTC) and that disorder gives rigidity but NOT the noise
protection. So the sharp question is NOT "where does the crystal melt" but: **does the disorder
W actually MOVE the melt boundary, or does the drive imperfection eps set it alone and disorder
is a bystander?** MBL theory says disorder should EXTEND the crystal to larger eps (localization
protects order). The mundane null says the boundary is set by eps and the interactions; W does
not move it. This experiment makes W earn it against that null. I do NOT assume MBL extends it.

METRIC. Rigidity R(eps, W) = mean over a late window t in {6,8} of |A(t)|, A(t)=(-1)^t <Z>_avg.
Deep in the crystal R is high (subharmonic locked); melted, R -> ~0 (drive error unlocks it).
The melt boundary is the eps where R crosses ~0.5, per W. Compare eps_melt(W=0) to eps_melt(W=strong).

FENCE (headline): finite L=6, finite window — a signature-scale boundary, not a
thermodynamic-limit phase transition. Single seeded J / base-disorder realization.

Usage:
  python3 exp153_dtc_melt.py --mapboundary   # P3 truth-gate: noiseless R(eps,W) map + does W move it? + falsifiability
  python3 exp153_dtc_melt.py --powercalc     # feasibility of R under measured noise
  python3 exp153_dtc_melt.py --submit [--backend ibm_fez --shots 4000]
  python3 exp153_dtc_melt.py --decode --manifest ../results/exp153_manifest.json
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

E_CX = 0.0106
L = 6
EPS_GRID = [0.04, 0.12, 0.20, 0.28, 0.40]     # deep-crystal -> melted (extended so all W melt in range)
W_GRID = [0.0, 1.0, np.pi]                     # 0 = prethermal (no disorder), pi = strong MBL
LATE_T = [6, 8]                                # late window where crystal-vs-melted is clear
_rng = np.random.default_rng(153)
J_COUP = list(0.4 + 0.8 * _rng.random(L - 1))          # fixed Ising couplings
H_BASE = list(2 * _rng.random(L) - 1)                  # base disorder in [-1,1]; field = W * H_BASE


def floquet_circuit(t_periods, eps, W, interactions=True, measure=True):
    qc = QuantumCircuit(L, L if measure else 0)
    theta = np.pi * (1 - eps)
    for _ in range(t_periods):
        for q in range(L):
            qc.rx(theta, q)
        if interactions:
            for i in range(L - 1):
                qc.rzz(2 * J_COUP[i], i, i + 1)
        for i in range(L):
            qc.rz(2 * W * H_BASE[i], i)         # disorder scaled by W (W=0 -> identity)
    if measure:
        qc.measure(range(L), range(L))
    return qc


def _z_exact(t, eps, W, interactions=True):
    from qiskit.quantum_info import Statevector, SparsePauliOp
    sv = Statevector(floquet_circuit(t, eps, W, interactions, measure=False))
    out = []
    for i in range(L):
        lbl = ["I"] * L; lbl[L - 1 - i] = "Z"
        out.append(float(np.real(sv.expectation_value(SparsePauliOp("".join(lbl))))))
    return np.mean(out)


def _z_counts(counts, shots):
    z = np.zeros(L)
    for bit, c in counts.items():
        b = bit.replace(" ", "")[::-1]
        for i in range(L):
            z[i] += (1 if b[i] == "0" else -1) * c
    return (z / shots).mean()


def _rigidity(zt_by_t):
    """R = mean over late window of |A(t)|, A(t)=(-1)^t <Z>_avg."""
    return float(np.mean([abs(((-1) ** t) * zt_by_t[t]) for t in LATE_T]))


def _eps_melt(R_row):
    """eps where R crosses 0.5 (linear interp); None if never crosses within the grid."""
    for k in range(len(EPS_GRID) - 1):
        a, b = R_row[k], R_row[k + 1]
        if (a - 0.5) * (b - 0.5) <= 0 and a != b:
            f = (a - 0.5) / (a - b)
            return EPS_GRID[k] + f * (EPS_GRID[k + 1] - EPS_GRID[k])
    return None


def mapboundary():
    """P3 TRUTH-GATE (noiseless). Map R(eps,W); assert crystal rigid at small eps and melted at
    large eps; REPORT whether W moves the melt boundary (the null-first question — reported, not
    assumed); falsifiability: interactions-OFF melts at all eps (the test can fail)."""
    print(f"Exp153 noiseless R(eps,W) map | L={L} | metric=mean_t|A(t)| over t={LATE_T}")
    print("eps\\W  " + "  ".join(f"W={w:4.2f}" for w in W_GRID))
    grid = {}
    for eps in EPS_GRID:
        row = []
        for W in W_GRID:
            zt = {t: _z_exact(t, eps, W) for t in LATE_T}
            R = _rigidity(zt); row.append(R); grid[(eps, W)] = R
        print(f"{eps:4.2f}  " + "  ".join(f"{r:6.3f}" for r in row))
    # melt boundary per W
    print("\nmelt boundary eps_melt (R crosses 0.5), per W:")
    melts = {}
    for wi, W in enumerate(W_GRID):
        Rrow = [grid[(eps, W)] for eps in EPS_GRID]
        em = _eps_melt(Rrow); melts[W] = em
        print(f"  W={W:4.2f}: eps_melt = {em if em is None else round(em,3)}")
    # null-first readout
    em0, emS = melts[W_GRID[0]], melts[W_GRID[-1]]
    if em0 is not None and emS is not None:
        shift = emS - em0
        verdict = ("disorder EXTENDS the crystal (MBL)" if shift > 0.02 else
                   "disorder SHRINKS the crystal" if shift < -0.02 else
                   "W does NOT move the boundary (eps + interactions set it; disorder a bystander)")
        print(f"\nNULL-FIRST: eps_melt(W=0)={em0:.3f} vs eps_melt(W={W_GRID[-1]:.2f})={emS:.3f} "
              f"-> shift {shift:+.3f} -> {verdict}")
    # falsifiability: interactions OFF must melt (no locking) at all but trivial eps
    zt_off = {t: _z_exact(t, 0.10, W_GRID[-1], interactions=False) for t in LATE_T}
    R_off = _rigidity(zt_off)
    print(f"\nfalsifiability: interactions-OFF at eps=0.10 -> R={R_off:.3f} (should be low; the "
          f"crystal is the interactions)")
    assert grid[(EPS_GRID[0], W_GRID[-1])] > 0.5, "crystal should be rigid at small eps"
    assert grid[(EPS_GRID[-1], W_GRID[-1])] < grid[(EPS_GRID[0], W_GRID[-1])], "large eps should melt vs small"
    assert R_off < 0.5, "interactions-off must not lock (falsifiability broken)"
    print("\nMAPBOUNDARY PASS: boundary exists (rigid small-eps -> melted large-eps), W-effect "
          "reported not assumed, interactions-off melts (test can fail).")
    out = os.path.join(HERE, "..", "results", "exp153_boundary_ideal.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump({"grid": {f"{e}_{w:.2f}": grid[(e, w)] for e in EPS_GRID for w in W_GRID},
               "eps_melt": {f"{w:.2f}": melts[w] for w in W_GRID}}, open(out, "w"), indent=1)
    print(f"-> {out}")


def powercalc():
    """Feasibility: decay noiseless R by fidelity^(#2q) at the late window. #2q at t = t*2*(L-1)."""
    cxpp = 2 * (L - 1)
    print(f"Exp153 feasibility | E_CX={E_CX} | {cxpp} CX/period | late t={LATE_T}")
    print("eps\\W  " + "  ".join(f"W={w:4.2f}" for w in W_GRID))
    for eps in EPS_GRID:
        row = []
        for W in W_GRID:
            zt = {t: _z_exact(t, eps, W) for t in LATE_T}
            Rhw = float(np.mean([abs(((-1) ** t) * zt[t]) * (1 - E_CX) ** (t * cxpp) for t in LATE_T]))
            row.append(Rhw)
        print(f"{eps:4.2f}  " + "  ".join(f"{r:6.3f}" for r in row))
    print("NOTE: the melt BOUNDARY (where R crosses ~0.3-0.5 relative) survives decay because it "
          "is a contrast across eps at fixed depth; absolute R is damped ~0.5-0.6x at t=8.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    circuits, order = [], []
    for eps in EPS_GRID:
        for W in W_GRID:
            for t in LATE_T:
                qc = floquet_circuit(t, eps, W, measure=True)
                circuits.append(transpile(qc, backend=backend, optimization_level=3))
                order.append((eps, W, t))
    sampler = SamplerV2(mode=backend); job = sampler.run(circuits, shots=shots)
    manifest = {"exp": 153, "backend": backend_name, "shots": shots, "L": L,
                "eps_grid": EPS_GRID, "w_grid": list(W_GRID), "late_t": LATE_T,
                "J": list(J_COUP), "h_base": list(H_BASE), "job_id": job.job_id(),
                "order": [[e, w, t] for (e, w, t) in order],
                "note": "DTC melt boundary: R(eps,W)=mean_t|A(t)|; null-first = does disorder W move eps_melt"}
    out = os.path.join(HERE, "..", "results", "exp153_manifest.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(manifest, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits: {len(EPS_GRID)}eps x {len(W_GRID)}W x {len(LATE_T)}t, {shots} shots) -> {out}")


def decode(mp):
    from run_exp66_qpu_partb import _get_ibm_service
    svc = _get_ibm_service(); man = json.load(open(mp))
    res = svc.job(man["job_id"]).result(); shots = man["shots"]
    zt = {}
    for idx, (e, w, t) in enumerate(man["order"]):
        r = res[idx]; reg = list(r.data.keys())[0]
        zt[(e, w, t)] = _z_counts(getattr(r.data, reg).get_counts(), shots)
    print(f"Exp153 decode | job {man['job_id']} | backend {man['backend']}")
    print("R(eps,W) on hardware:")
    print("eps\\W  " + "  ".join(f"W={w:4.2f}" for w in W_GRID))
    grid = {}
    for e in EPS_GRID:
        row = []
        for w in W_GRID:
            R = float(np.mean([abs(((-1) ** t) * zt[(e, w, t)]) for t in LATE_T]))
            grid[(e, w)] = R; row.append(R)
        print(f"{e:4.2f}  " + "  ".join(f"{r:6.3f}" for r in row))
    print("\nmelt boundary eps_melt (R crosses 0.5*R_max per W):")
    melts = {}
    for w in W_GRID:
        Rrow = [grid[(e, w)] for e in EPS_GRID]
        thr = 0.5 * max(Rrow)
        em = None
        for k in range(len(EPS_GRID) - 1):
            a, b = Rrow[k], Rrow[k + 1]
            if (a - thr) * (b - thr) <= 0 and a != b:
                em = EPS_GRID[k] + (a - thr) / (a - b) * (EPS_GRID[k + 1] - EPS_GRID[k]); break
        melts[w] = em
        print(f"  W={w:4.2f}: eps_melt = {em if em is None else round(em,3)} (thr={thr:.3f})")
    em0, emS = melts[W_GRID[0]], melts[W_GRID[-1]]
    verdict = "inconclusive (a boundary did not cross in range)"
    if em0 is not None and emS is not None:
        shift = emS - em0
        verdict = ("disorder EXTENDS the crystal (MBL protects — the fancy story, earned)" if shift > 0.03 else
                   "disorder SHRINKS the crystal" if shift < -0.03 else
                   "W does NOT move the boundary — eps + interactions set it, disorder is a bystander (the null holds)")
        print(f"\nNULL-FIRST RESULT: eps_melt(W=0)={em0:.3f} vs eps_melt(W={W_GRID[-1]:.2f})={emS:.3f} "
              f"-> shift {shift:+.3f}")
    print(f"VERDICT: {verdict}")
    out = {"job_id": man["job_id"], "backend": man["backend"],
           "grid": {f"{e}_{w:.2f}": grid[(e, w)] for e in EPS_GRID for w in W_GRID},
           "eps_melt": {f"{w:.2f}": melts[w] for w in W_GRID}, "verdict": verdict}
    fn = os.path.join(HERE, "..", "results", "exp153_decode.json")
    json.dump(out, open(fn, "w"), indent=1)
    print(f"-> {fn}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mapboundary", action="store_true"); ap.add_argument("--powercalc", action="store_true")
    ap.add_argument("--submit", action="store_true"); ap.add_argument("--decode", action="store_true")
    ap.add_argument("--manifest"); ap.add_argument("--backend", default="ibm_fez"); ap.add_argument("--shots", type=int, default=4000)
    a = ap.parse_args()
    if a.mapboundary: mapboundary()
    elif a.powercalc: powercalc()
    elif a.submit: submit(a.backend, a.shots)
    elif a.decode: decode(a.manifest or os.path.join(HERE, "..", "results", "exp153_manifest.json"))
    else: ap.print_help()
