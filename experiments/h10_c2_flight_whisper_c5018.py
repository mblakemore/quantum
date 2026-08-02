#!/usr/bin/env python3
"""H10-C2 FLIGHT — Vacuum Harvest with the Exchange Channel Removed (Whisper C5018).
Prereg: docs/h10-c2-prereg-whisper-c5018.md, SEALED 0b0d25be (coordination#3615).
Submission gated on: Creator GO + KA fence (SS5.1) + depth HOLD (SS5.2, transpiled 2q <= 500)
+ calibration hold (SS5.3, median 2q <= 0.5%) + pool re-read (SS5.4).

Design (all frozen; every 2q block is an explicit 4x4 UnitaryGate — the transpiler compiles
each to <=3 CX optimally, and the KA walker applies the IDENTICAL matrices, so there is no
compile-convention gap for a fence to miss):
  prep      X on sites 0..3, then 22 frozen Givens rotations (artifact, exact Slater det)
  evolution r=6 circuit-faithful o2 steps; cut arm skips bond (3,4); tophat coupling
  arms      A1 cut tomography (9 settings x 11k) · A2 full tomography · A4 product (no prep)
            A3 floor (no coupling, Z only, 10k) · A5 cone (RX(pi/2) kick at s1, field-only
            evolution to t, <X_s2>; 8 points x 5k) · A6 books (all-X / all-Y field settings
            + t=0 baselines, 4 x 10k)
Decode: linear-inversion rho-hat -> negativity; bootstrap seed 20260802 (frozen SS3).
"""
import argparse, json, math, os, sys
import importlib.util
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "..", "results")
SCRIPTS = os.path.join(HERE, "..", "scripts")
GIV = json.load(open(os.path.join(RESULTS, "h10_c2_givens_prep_c5018.json")))
ARM = json.load(open(os.path.join(RESULTS, "h10_c2_armbars_r6_c5018.json")))
RTAB = json.load(open(os.path.join(RESULTS, "h10_c2_asflown_r_c5018.json")))
L = 8; NQ = 10; J = 1.0
OM, D, T, LAM, R = 1.5, 3, 2.5, 0.6, 6
S1, S2, CUT = 2, 5, 3
D1, D2 = 8, 9
I2 = np.eye(2); X = np.array([[0, 1], [1, 0]], complex); Y = np.array([[0, -1j], [1j, 0]])
Z = np.diag([1, -1]).astype(complex)
H1 = (X + Z) / np.sqrt(2); SDG = np.diag([1, -1j]).astype(complex)

def u4_of(gen, a):
    w, v = np.linalg.eigh(gen)
    return (v * np.exp(-1j * a * w)) @ v.conj().T

HB = J / 2 * (np.kron(X, X) + np.kron(Y, Y)).real
HC = LAM * np.kron(X, X).real
def givens4(th):
    g = np.eye(4, dtype=complex)
    g[1, 1] = np.cos(th); g[1, 2] = -np.sin(th)
    g[2, 1] = np.sin(th); g[2, 2] = np.cos(th)
    return g

# ---------------- pub IR: (kind, qubits, payload) ----------------
def prep_ops(product=False):
    ops = []
    if product: return ops
    for q in range(4): ops.append(("x1", (q,), None))
    for (i, r, th) in reversed(GIV["rotations"]):
        ops.append(("u4", (i, r), givens4(-th)))
    return ops

def evo_ops(cut, couple=True, t=T, r=R):
    dt = t / r
    Ubh = u4_of(HB, dt / 2); Uc = u4_of(HC, dt)
    ph = np.exp(-1j * dt * np.array([0.0, OM]))
    bonds = [j for j in range(L - 1) if not (cut and j == CUT)]
    ops = []
    for _ in range(r):
        for j in bonds: ops.append(("u4", (j, j + 1), Ubh))
        if couple:
            ops.append(("u4", (S1, D1), Uc)); ops.append(("u4", (S2, D2), Uc))
            ops.append(("ph1", (D1,), ph)); ops.append(("ph1", (D2,), ph))
        for j in reversed(bonds): ops.append(("u4", (j, j + 1), Ubh))
    return ops

BASIS = {"X": "h", "Y": "sdgh", "Z": ""}
def tomo_ops(a, b):
    ops = []
    for (q, p) in ((D1, a), (D2, b)):
        if p == "X": ops.append(("h1", (q,), None))
        elif p == "Y": ops.append(("sdg1", (q,), None)); ops.append(("h1", (q,), None))
    ops.append(("meas", (D1, D2), None))
    return ops

def build_pubs():
    pubs = []
    for tag, cut, product in (("A1cut", True, False), ("A2full", False, False),
                              ("A4prod", True, True)):
        for a in "XYZ":
            for b in "XYZ":
                ops = prep_ops(product) + evo_ops(cut) + tomo_ops(a, b)
                pubs.append((f"{tag}_{a}{b}", ops, 11000,
                             {"arm": tag, "setting": a + b}))
    pubs.append(("A3floor_ZZ", prep_ops() + evo_ops(True, couple=False) + tomo_ops("Z", "Z"),
                 10000, {"arm": "A3floor", "setting": "ZZ"}))
    for k, t in enumerate([0.35, 0.7, 1.05, 1.4, 1.75, 2.1, 2.45, 2.8]):
        rk = max(2, int(np.ceil(R * t / T)))
        ops = prep_ops() + [("u4k", (S1,), None)] + evo_ops(False, couple=False, t=t, r=rk)
        ops += [("h1", (S2,), None), ("measX", (S2,), None)]
        pubs.append((f"A5cone_t{k}", ops, 5000, {"arm": "A5cone", "t": t, "rk": rk}))
    for tag, basis, evolved in (("A6X1", "X", True), ("A6Y1", "Y", True),
                                ("A6X0", "X", False), ("A6Y0", "Y", False)):
        ops = prep_ops() + (evo_ops(True) if evolved else [])
        for q in range(L):
            if basis == "X": ops.append(("h1", (q,), None))
            else: ops.append(("sdg1", (q,), None)); ops.append(("h1", (q,), None))
        ops.append(("measF", tuple(range(L)), None))
        pubs.append((tag, ops, 10000, {"arm": "A6books", "basis": basis, "evolved": evolved}))
    return pubs

# ---------------- 10q walker ----------------
def a1(psi, u, q):
    t = psi.reshape([2] * NQ)
    t = np.moveaxis(np.tensordot(u, t, axes=([1], [q])), 0, q)
    return t.reshape(-1)

def a2g(psi, u, q1, q2):
    t = psi.reshape([2] * NQ)
    t = np.moveaxis(np.tensordot(u.reshape(2, 2, 2, 2), t, axes=([2, 3], [q1, q2])),
                    [0, 1], [q1, q2])
    return t.reshape(-1)

def walk(ops):
    """Returns exact outcome expectations for the pub's measurement."""
    psi = np.zeros(2 ** NQ, complex); psi[0] = 1.0
    KICK = u4_of(np.kron(X, np.eye(1)).reshape(2, 2) * 0 + X, np.pi / 4)  # RX(pi/2)=e^{-i pi/4 X}
    for kind, q, pl in ops:
        if kind == "x1": psi = a1(psi, X, q[0])
        elif kind == "h1": psi = a1(psi, H1, q[0])
        elif kind == "sdg1": psi = a1(psi, SDG, q[0])
        elif kind == "ph1":
            sh = [1] * NQ; sh[q[0]] = 2
            psi = (psi.reshape([2] * NQ) * pl.reshape(sh)).reshape(-1)
        elif kind == "u4": psi = a2g(psi, pl, q[0], q[1])
        elif kind == "u4k": psi = a1(psi, KICK, q[0])
        elif kind == "meas":
            t = psi.reshape([2] * NQ)
            probs = np.zeros((2, 2))
            for b1 in (0, 1):
                for b2 in (0, 1):
                    idx = [slice(None)] * NQ; idx[q[0]] = b1; idx[q[1]] = b2
                    v = t[tuple(idx)].reshape(-1)
                    probs[b1, b2] = float(np.vdot(v, v).real)
            return {"probs2": probs}
        elif kind == "measX":
            t = psi.reshape([2] * NQ)
            i0 = [slice(None)] * NQ; i0[q[0]] = 0
            i1 = [slice(None)] * NQ; i1[q[0]] = 1
            p0 = float(np.vdot(t[tuple(i0)].reshape(-1), t[tuple(i0)].reshape(-1)).real)
            p1 = float(np.vdot(t[tuple(i1)].reshape(-1), t[tuple(i1)].reshape(-1)).real)
            return {"expX": p0 - p1}
        elif kind == "measF":
            t = psi.reshape([2] * NQ)
            exps = []
            for j in range(L - 1):
                e = 0.0
                for bj in (0, 1):
                    for bk in (0, 1):
                        idx = [slice(None)] * NQ; idx[j] = bj; idx[j + 1] = bk
                        v = t[tuple(idx)].reshape(-1)
                        e += (1 - 2 * bj) * (1 - 2 * bk) * float(np.vdot(v, v).real)
                exps.append(e)
            return {"bond_zz": exps}
    raise RuntimeError("no measurement")

# ---------------- decode (frozen SS3) ----------------
PAULI = {"X": X, "Y": Y, "Z": Z, "I": I2}
def rho_from_settings(exp2, exp1a, exp1b):
    """Linear inversion from 9 two-qubit correlators + singles."""
    rho = np.eye(4, dtype=complex) / 4
    for a in "XYZ":
        for b in "XYZ":
            rho += exp2[a + b] * np.kron(PAULI[a], PAULI[b]) / 4
    for a in "XYZ":
        rho += exp1a[a] * np.kron(PAULI[a], I2) / 4 + exp1b[a] * np.kron(I2, PAULI[a]) / 4
    return rho

def negativity(rho):
    pt = rho.reshape(2, 2, 2, 2).transpose(0, 3, 2, 1).reshape(4, 4)
    ev = np.linalg.eigvalsh(pt)
    return float(-ev[ev < 0].sum())

def tomo_decode(res_by_setting):
    exp2, e1a, e1b = {}, {"X": [], "Y": [], "Z": []}, {"X": [], "Y": [], "Z": []}
    for ab, probs in res_by_setting.items():
        a, b = ab
        p = probs
        exp2[ab] = p[0, 0] - p[0, 1] - p[1, 0] + p[1, 1]
        e1a[a].append(p[0, 0] + p[0, 1] - p[1, 0] - p[1, 1])
        e1b[b].append(p[0, 0] - p[0, 1] + p[1, 0] - p[1, 1])
    ea = {a: float(np.mean(v)) for a, v in e1a.items()}
    eb = {b: float(np.mean(v)) for b, v in e1b.items()}
    return negativity(rho_from_settings(exp2, ea, eb))

# ---------------- KA fence ----------------
def ka_gate():
    pubs = build_pubs()
    res = {}
    for tag, ops, sh, meta in pubs:
        res[tag] = walk(ops)
    checks = {}
    for arm, ref in (("A1cut", RTAB["rows"][-1]["N_cut"]), ("A2full", RTAB["rows"][-1]["N_full"]),
                     ("A4prod", 0.0)):
        by = {m["setting"]: res[f"{arm}_{m['setting']}"]["probs2"]
              for _, __, ___, m in pubs if m.get("arm") == arm}
        checks[arm] = abs(tomo_decode(by) - ref)
    zz = res["A3floor_ZZ"]["probs2"]
    checks["A3floor_P00"] = abs(zz[0, 0] - 1.0)
    checks["A6_dE"] = abs(_books_dE(res) - ARM["A6_dE_field"])
    ok = all(v < 1e-6 for v in checks.values())
    # A5 cone: no pre-stored numeric target exists (SS3 registers the arm against the exact
    # front table as an OVERLAY row); the walker's own values ARE the as-flown predictions —
    # registered here from committed deterministic code (the bars-v2 pattern) and saved.
    a5 = {m["t"]: res[tg]["expX"] for tg, _, __, m in pubs if m.get("arm") == "A5cone"}
    reg = {"checks": {k: float(v) for k, v in checks.items()},
           "A5_asflown_expX": {str(k): float(v) for k, v in a5.items()},
           "A1_N_cut_ref": RTAB["rows"][-1]["N_cut"], "A2_N_full_ref": RTAB["rows"][-1]["N_full"]}
    json.dump(reg, open(os.path.join(RESULTS, "h10_c2_ka_asflown_c5018.json"), "w"), indent=1)
    print("KA:", {k: f"{v:.2e}" for k, v in checks.items()}, "->", "PASS" if ok else "FAIL")
    print("A5 as-flown registered:", {k: round(v, 4) for k, v in a5.items()})
    return ok, res

def _books_dE(res):
    """<H_f> from bond correlators: J/2(<XX>+<YY>) per bond, evolved minus baseline."""
    def E(x, y): return sum(J / 2 * (bx + by) for bx, by in zip(x, y))
    return (E(res["A6X1"]["bond_zz"], res["A6Y1"]["bond_zz"])
            - E(res["A6X0"]["bond_zz"], res["A6Y0"]["bond_zz"]))

# note: measuring all qubits in X basis makes <X_j X_{j+1}> = ZZ-correlator of the rotated
# state — bond_zz after the basis rotation IS <XX> (resp <YY>). Same convention on device.

# ---------------- qiskit build + submission ----------------
def to_qiskit(ops):
    from qiskit import QuantumCircuit
    from qiskit.circuit.library import UnitaryGate
    nmeas = 8 if any(k == "measF" for k, _, __ in ops) else (2 if any(k == "meas" for k, _, __ in ops) else 1)
    qc = QuantumCircuit(NQ, nmeas)
    for kind, q, pl in ops:
        if kind == "x1": qc.x(q[0])
        elif kind == "h1": qc.h(q[0])
        elif kind == "sdg1": qc.sdg(q[0])
        elif kind == "u4k": qc.rx(np.pi / 2, q[0])
        elif kind == "ph1":
            qc.p(float(-np.angle(pl[0]) + np.angle(pl[1])), q[0])  # relative phase; global dropped
        elif kind == "u4": qc.append(UnitaryGate(pl), [q[0], q[1]])
        elif kind == "meas": qc.measure(q[0], 0); qc.measure(q[1], 1)
        elif kind == "measX": qc.measure(q[0], 0)
        elif kind == "measF":
            for i, qq in enumerate(q): qc.measure(qq, i)
    return qc

def fly():
    ok, _ = ka_gate()
    if not ok: sys.exit("KA FENCE FAILED — NO SUBMISSION (prereg SS5.1)")
    sys.path.insert(0, SCRIPTS)
    from ibm_multi_account import service_for_submission
    svc = service_for_submission("IBMQ_ALT2")
    u = svc.usage()
    print(f"POOL RE-READ (ALT2): remaining {u['usage_remaining_seconds']}s of {u['usage_limit_seconds']}")
    best = None
    for b in svc.backends():
        st = b.status()
        if st.operational and b.configuration().n_qubits >= NQ:
            if best is None or st.pending_jobs < best[0]: best = (st.pending_jobs, b)
    backend = best[1]
    props = backend.properties()
    errs = [p.value for g in props.gates if len(g.qubits) == 2 for p in g.parameters
            if p.name == "gate_error"]
    med = float(np.median(errs))
    if med > 0.005: sys.exit(f"CALIBRATION HOLD: median 2q {med:.4f} > 0.5% (prereg SS5.3)")
    from qiskit import transpile
    from qiskit_ibm_runtime import SamplerV2
    pubs = build_pubs()
    qcs = [to_qiskit(ops) for _, ops, __, ___ in pubs]
    tq = transpile(qcs, backend, optimization_level=3, seed_transpiler=1104)
    n2q = [sum(1 for inst in t.data if len(inst.qubits) == 2) for t in tq]
    print(f"transpiled 2q counts: min {min(n2q)} median {int(np.median(n2q))} max {max(n2q)}")
    if max(n2q) > 500:
        sys.exit(f"DEPTH HOLD: max transpiled 2q {max(n2q)} > 500 (prereg SS5.2)")
    sampler = SamplerV2(mode=backend)
    job = sampler.run([(t, None, sh) for t, (_, __, sh, ___) in zip(tq, pubs)])
    man = {"experiment": "h10_c2_vacuum_harvest", "cycle": "C5018",
           "prereg": "docs/h10-c2-prereg-whisper-c5018.md SEALED 0b0d25be (coordination#3615)",
           "go": "Creator general#3630 'Go C2' (2026-08-02)",
           "account": "ALT2", "pool_remaining_at_submit_s": u["usage_remaining_seconds"],
           "backend": backend.name, "chain_2q_median": med,
           "pubs": [{"tag": tg, "shots": sh, **mt} for tg, _, sh, mt in pubs],
           "transpiled_2q_counts": n2q, "job_id": job.job_id(),
           "committer": "Whisper (DC15W)"}
    path = os.path.join(RESULTS, "h10_c2_flight_manifest.json")
    json.dump(man, open(path, "w"), indent=1)
    print(f"SUBMITTED: {job.job_id()} -> {path}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--ka", action="store_true")
    ap.add_argument("--fly", action="store_true")
    a = ap.parse_args()
    if a.ka: sys.exit(0 if ka_gate()[0] else 1)
    if a.fly: fly(); sys.exit(0)
    ap.print_help()
