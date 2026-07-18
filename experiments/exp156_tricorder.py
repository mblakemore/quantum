#!/usr/bin/env python3
"""Exp156 — TRICORDER: scan a real molecule from quantum hardware (H2 dissociation curve).
Creator directive C4845: fly the most frontier/star-trek self-verifying experiments (Ember has 155).
New quantum-chemistry museum wing candidate.

THE AHA. Point the instrument at a hydrogen molecule and read off its physics: bond length,
binding curve, and the electron correlation that classical mean-field theory misses. The entire
chemistry stack is SELF-CONTAINED — STO-3G integrals computed from scratch in numpy
(Szabo-Ostlund closed forms, no chemistry packages), 2x2 CI in the {sigma_g^2, sigma_u^2}
singlet space, mapped to a 2-qubit Hamiltonian in the O'Malley Pauli structure
(Z0, Z1, Z0Z1, X0X1, Y0Y1) with SELF-DERIVED coefficients. Per bond length we prepare the exact
correlated ground state (1 CX) and measure the energy on hardware in 3 bases.

SELF-VERIFYING, three intrinsic falsifiers:
  1. VARIATIONAL BOUND — <psi|H|psi> >= E_ground for ANY state, so hardware noise can only push
     the energy UP. A reading significantly BELOW exact ground = broken instrument.
  2. MATCHED HF CONTROL — identical circuit with theta=0 (Hartree-Fock, no correlation). It must
     sit ABOVE the CI arm by exactly the correlation energy, which GROWS toward dissociation.
     The tricorder must detect electron correlation, not just reproduce one number.
  3. THE CURVE ITSELF — the hardware minimum must land at the real H2 bond length (~0.74 A).

TRUTH-GATES (pre-flight): (A) numpy ab-initio pipeline vs literature STO-3G values at R=1.4 bohr
(E_RHF=-1.1167, E_FCI=-1.1373 Ha) + equilibrium R_e in [0.70,0.78] A; (B) qubit mapping exact-diag
== CI exact-diag, ground in the {|01>,|10>} subspace; (C) noiseless Aer counts-pipeline == exact.

FENCE (headline): minimal STO-3G basis (2 qubits) — we verify hardware against THE MODEL's exact
diagonalization (cross-checked to literature), not against experimental spectroscopy; STO-3G
overbinds vs real H2. A hardware energy readout of a first-principles molecular Hamiltonian,
not a beyond-classical chemistry calculation.

Usage:
  python3 exp156_tricorder.py --selftest
  python3 exp156_tricorder.py --submit [--backend ibm_fez --shots 4096]
  python3 exp156_tricorder.py --decode --manifest ../results/exp156_manifest.json
"""
import argparse, json, os, sys
from math import erf, pi, sqrt, atan2
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

ANG2BOHR = 1.8897259886
# bond-length scan grid (Angstrom): repulsive wall -> equilibrium -> dissociation
R_GRID_ANG = [0.30, 0.40, 0.50, 0.60, 0.7414, 0.90, 1.10, 1.40, 1.80, 2.50]
BASES = ["ZZ", "XX", "YY"]

# ---------------------------------------------------------------------------
# ab initio from scratch: STO-3G H2 in pure numpy (Szabo-Ostlund appendix A)
# ---------------------------------------------------------------------------
# STO-3G expansion of a 1s Slater orbital, zeta=1.24 (H): alpha_i = alpha_i(zeta=1)*zeta^2
STO3G_ALPHA = np.array([2.227660584, 0.405771156, 0.109818]) * 1.24**2
STO3G_D = np.array([0.154328967, 0.535328142, 0.444634542])   # for normalized primitives


def _F0(t):
    """Boys function F0(t) = 0.5*sqrt(pi/t)*erf(sqrt(t)); -> 1 as t -> 0."""
    return 1.0 - t / 3.0 if t < 1e-12 else 0.5 * sqrt(pi / t) * erf(sqrt(t))


def h2_integrals(R_bohr):
    """All AO integrals for H2 in STO-3G at internuclear distance R (bohr), s-functions on the
    z-axis at 0 and R. Returns S12, hcore (2x2), eri (2,2,2,2 chemists' notation), E_nuc."""
    centers = np.array([0.0, R_bohr])
    # fold primitive normalization into contraction coefficients
    coef = STO3G_D * (2.0 * STO3G_ALPHA / pi) ** 0.75
    S = np.zeros((2, 2)); T = np.zeros((2, 2)); V = np.zeros((2, 2))
    for i in range(2):
        for j in range(2):
            AB2 = (centers[i] - centers[j]) ** 2
            for a, ca in zip(STO3G_ALPHA, coef):
                for b, cb in zip(STO3G_ALPHA, coef):
                    p = a + b; K = np.exp(-a * b / p * AB2)
                    P = (a * centers[i] + b * centers[j]) / p
                    S[i, j] += ca * cb * (pi / p) ** 1.5 * K
                    T[i, j] += ca * cb * a * b / p * (3.0 - 2.0 * a * b / p * AB2) * (pi / p) ** 1.5 * K
                    for C in centers:  # both nuclei, Z=1
                        V[i, j] += ca * cb * (-2.0 * pi / p) * K * _F0(p * (P - C) ** 2)
    # renormalize contracted functions (standard coefficients are normalized to ~1e-6 already)
    n = 1.0 / np.sqrt(np.diag(S))
    S = S * np.outer(n, n); T = T * np.outer(n, n); V = V * np.outer(n, n)
    coefN = [coef * n[0], coef * n[1]]
    eri = np.zeros((2, 2, 2, 2))
    for i in range(2):
        for j in range(2):
            for k in range(2):
                for l in range(2):
                    AB2 = (centers[i] - centers[j]) ** 2; CD2 = (centers[k] - centers[l]) ** 2
                    v = 0.0
                    for a, ca in zip(STO3G_ALPHA, coefN[i]):
                        for b, cb in zip(STO3G_ALPHA, coefN[j]):
                            p = a + b; P = (a * centers[i] + b * centers[j]) / p
                            Kab = np.exp(-a * b / p * AB2)
                            for c, cc in zip(STO3G_ALPHA, coefN[k]):
                                for d, cd in zip(STO3G_ALPHA, coefN[l]):
                                    q = c + d; Q = (c * centers[k] + d * centers[l]) / q
                                    Kcd = np.exp(-c * d / q * CD2)
                                    v += (ca * cb * cc * cd * 2.0 * pi ** 2.5
                                          / (p * q * sqrt(p + q)) * Kab * Kcd
                                          * _F0(p * q / (p + q) * (P - Q) ** 2))
                    eri[i, j, k, l] = v
    return S[0, 1], T + V, eri, 1.0 / R_bohr


def h2_ci(R_bohr):
    """2x2 full CI for H2/STO-3G in the {sigma_g^2, sigma_u^2} singlet space.
    Returns dict: H11 (=E_HF), H22, H12, E_fci, ci vector (c_g, c_u)."""
    S12, hcore, eri, Enuc = h2_integrals(R_bohr)
    # symmetry-determined MOs: sigma_g/u = (phi1 +/- phi2)/sqrt(2(1 +/- S12))
    C = np.array([[1.0 / sqrt(2 * (1 + S12)), 1.0 / sqrt(2 * (1 - S12))],
                  [1.0 / sqrt(2 * (1 + S12)), -1.0 / sqrt(2 * (1 - S12))]])  # cols: g, u
    h_mo = C.T @ hcore @ C
    eri_mo = np.einsum("pi,qj,rk,sl,pqrs->ijkl", C, C, C, C, eri, optimize=True)
    g, u = 0, 1
    H11 = 2 * h_mo[g, g] + eri_mo[g, g, g, g] + Enuc          # sigma_g^2 (= RHF energy)
    H22 = 2 * h_mo[u, u] + eri_mo[u, u, u, u] + Enuc          # sigma_u^2
    H12 = eri_mo[g, u, g, u]                                   # K_gu = (gu|gu)
    M = np.array([[H11, H12], [H12, H22]])
    w, v = np.linalg.eigh(M)
    vec = v[:, 0] * np.sign(v[0, 0])                           # c_g >= 0
    return {"R_bohr": R_bohr, "H11": H11, "H22": H22, "H12": H12,
            "E_hf": H11, "E_fci": w[0], "c_g": vec[0], "c_u": vec[1]}


# ---------------------------------------------------------------------------
# qubit mapping: 2-qubit Hamiltonian, |01> = sigma_g^2, |10> = sigma_u^2
# ---------------------------------------------------------------------------
def qubit_hamiltonian(ci):
    """H = g0*II + g1*Z0 + g2*Z1 + g3*Z0Z1 + g4*X0X1 + g5*Y0Y1 (O'Malley Pauli structure,
    coefficients self-derived from the CI matrix). |00>,|11> get a +2 Ha penalty diagonal so the
    global ground state provably lives in the physical {|01>,|10>} subspace."""
    pen = max(ci["H11"], ci["H22"]) + 2.0
    diag = np.array([pen, ci["H11"], ci["H22"], pen])          # index = 2*q1 + q0
    M = np.array([[1, +1, +1, +1],                             # |00>: Z0=+1, Z1=+1
                  [1, -1, +1, -1],                             # |01>: q0=1
                  [1, +1, -1, -1],                             # |10>: q1=1
                  [1, -1, -1, +1]], dtype=float)               # |11>
    g0, g1, g2, g3 = np.linalg.solve(M, diag)
    g4 = g5 = ci["H12"] / 2.0                                  # (XX+YY)/2 couples |01><10| only
    return np.array([g0, g1, g2, g3, g4, g5])


def h_matrix(gs):
    I = np.eye(2); X = np.array([[0, 1], [1, 0]], dtype=complex)
    Y = np.array([[0, -1j], [1j, 0]]); Z = np.diag([1.0, -1.0]).astype(complex)
    kr = lambda a, b: np.kron(a, b)                            # index = 2*q1+q0 -> kron(q1, q0)
    return (gs[0] * kr(I, I) + gs[1] * kr(I, Z) + gs[2] * kr(Z, I)
            + gs[3] * kr(Z, Z) + gs[4] * kr(X, X) + gs[5] * kr(Y, Y))


def prep_circuit(theta, basis):
    """cos(t/2)|01> + sin(t/2)|10> with ONE CX; theta=0 = Hartree-Fock (matched control, same
    gates). Then rotate to the measurement basis (ZZ direct, XX: H, YY: Sdg+H) and measure."""
    qc = QuantumCircuit(2, 2)
    qc.ry(theta, 1); qc.x(0); qc.cx(1, 0)
    qc.barrier()
    if basis == "XX":
        qc.h(0); qc.h(1)
    elif basis == "YY":
        qc.sdg(0); qc.h(0); qc.sdg(1); qc.h(1)
    qc.measure(0, 0); qc.measure(1, 1)
    return qc


def _expvals(counts, shots):
    """(<Z0>, <Z1>, <Z0Z1>) from a 2-bit counts dict (string 'c1c0')."""
    z0 = z1 = zz = 0
    for b, c in counts.items():
        b = b.replace(" ", "")
        s0 = 1 if b[-1] == "0" else -1
        s1 = 1 if b[-2] == "0" else -1
        z0 += s0 * c; z1 += s1 * c; zz += s0 * s1 * c
    return z0 / shots, z1 / shots, zz / shots


def energy_from_counts(gs, counts_by_basis, shots):
    """E = g0 + g1<Z0> + g2<Z1> + g3<Z0Z1> + g4<XX> + g5<YY>; sigma from binomial shot noise."""
    z0, z1, zz = _expvals(counts_by_basis["ZZ"], shots)
    _, _, xx = _expvals(counts_by_basis["XX"], shots)
    _, _, yy = _expvals(counts_by_basis["YY"], shots)
    E = gs[0] + gs[1] * z0 + gs[2] * z1 + gs[3] * zz + gs[4] * xx + gs[5] * yy
    var = sum(g * g * (1 - p * p) / shots for g, p in
              zip(gs[1:], [z0, z1, zz, xx, yy]))
    return float(E), float(np.sqrt(var))


def scan_points():
    """Per-R everything the flight needs: CI truth, qubit coefficients, prep angle."""
    pts = []
    for R_ang in R_GRID_ANG:
        ci = h2_ci(R_ang * ANG2BOHR)
        gs = qubit_hamiltonian(ci)
        theta = 2.0 * atan2(ci["c_u"], ci["c_g"])
        pts.append({"R_ang": R_ang, "ci": ci, "gs": gs, "theta": theta})
    return pts


# ---------------------------------------------------------------------------
def selftest():
    print("Exp156 TRICORDER selftest")
    # GATE A — ab-initio pipeline vs literature (Szabo-Ostlund R=1.4 bohr benchmarks)
    ref = h2_ci(1.4)
    print(f"[A] R=1.4 bohr: E_RHF={ref['E_hf']:.4f} (lit -1.1167), E_FCI={ref['E_fci']:.4f} (lit -1.1373)")
    assert abs(ref["E_hf"] - (-1.1167)) < 0.005, "RHF vs literature FAIL"
    assert abs(ref["E_fci"] - (-1.1373)) < 0.005, "FCI vs literature FAIL"
    fine = np.arange(0.5, 1.1, 0.005)
    E_fine = [h2_ci(r * ANG2BOHR)["E_fci"] for r in fine]
    Re = fine[int(np.argmin(E_fine))]
    print(f"[A] equilibrium R_e = {Re:.3f} A (STO-3G FCI ~0.735, experimental 0.741)")
    assert 0.70 < Re < 0.78, "equilibrium bond length FAIL"

    # GATE B — qubit mapping: exact-diag of the 2-qubit H == CI, ground in the subspace
    for pt in scan_points():
        w, v = np.linalg.eigh(h_matrix(pt["gs"]))
        assert abs(w[0] - pt["ci"]["E_fci"]) < 1e-10, "mapping eigenvalue FAIL"
        assert abs(v[0, 0]) < 1e-10 and abs(v[3, 0]) < 1e-10, "ground leaked out of subspace FAIL"
    print("[B] qubit mapping exact-diag == CI ground at all 10 R; ground confined to {|01>,|10>}")

    # GATE C — full counts pipeline on noiseless Aer == exact (both arms)
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 30000
    worst_ci = worst_hf = 0.0
    for pt in scan_points():
        cb_ci, cb_hf = {}, {}
        for basis in BASES:
            for arm, theta, store in (("ci", pt["theta"], cb_ci), ("hf", 0.0, cb_hf)):
                qc = prep_circuit(theta, basis)
                store[basis] = sim.run(qc, shots=shots).result().get_counts()
        E_ci, s_ci = energy_from_counts(pt["gs"], cb_ci, shots)
        E_hf, s_hf = energy_from_counts(pt["gs"], cb_hf, shots)
        worst_ci = max(worst_ci, abs(E_ci - pt["ci"]["E_fci"]))
        worst_hf = max(worst_hf, abs(E_hf - pt["ci"]["E_hf"]))
    print(f"[C] noiseless counts pipeline: worst |E-exact| CI arm {worst_ci*1000:.1f} mHa, "
          f"HF arm {worst_hf*1000:.1f} mHa (shot noise ~5 mHa scale)")
    assert worst_ci < 0.02 and worst_hf < 0.02, "counts pipeline FAIL"

    # FALSIFIABILITY — correlation energy must grow toward dissociation (HF control can fail)
    c_eq = h2_ci(0.7414 * ANG2BOHR); c_far = h2_ci(2.5 * ANG2BOHR)
    gap_eq = c_eq["E_hf"] - c_eq["E_fci"]; gap_far = c_far["E_hf"] - c_far["E_fci"]
    print(f"[F] correlation energy: {gap_eq*1000:.1f} mHa at 0.74 A -> {gap_far*1000:.1f} mHa at 2.5 A "
          f"(grows {gap_far/gap_eq:.0f}x; the HF arm MUST diverge from the CI arm at large R)")
    assert gap_far > 5 * gap_eq, "correlation-growth falsifier FAIL"
    print("SELFTEST PASS: ab-initio pipeline matches literature, mapping exact, counts pipeline "
          "exact, correlation falsifier armed. Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    pts = scan_points()
    circuits, order = [], []
    for i, pt in enumerate(pts):
        for arm, theta in (("ci", pt["theta"]), ("hf", 0.0)):
            for basis in BASES:
                qc = prep_circuit(theta, basis)
                circuits.append(transpile(qc, backend=backend, optimization_level=3))
                order.append([i, arm, basis])
    sampler = SamplerV2(mode=backend); job = sampler.run(circuits, shots=shots)
    manifest = {"exp": 156, "backend": backend_name, "shots": shots, "job_id": job.job_id(),
                "order": order, "R_grid_ang": R_GRID_ANG,
                "exact": [{"R_ang": pt["R_ang"], "E_fci": pt["ci"]["E_fci"],
                           "E_hf": pt["ci"]["E_hf"], "gs": pt["gs"].tolist(),
                           "theta": pt["theta"]} for pt in pts],
                "note": "H2 dissociation curve, self-contained ab-initio -> 2-qubit H; CI arm vs "
                        "matched HF control, 3 bases each; variational bound + correlation falsifier"}
    out = os.path.join(HERE, "..", "results", "exp156_manifest.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(manifest, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits: 10 R x {{ci,hf}} x 3 bases, "
          f"{shots} shots) -> {out}")


def decode(mp):
    from run_exp66_qpu_partb import _get_ibm_service
    svc = _get_ibm_service(); man = json.load(open(mp)); res = svc.job(man["job_id"]).result()
    shots = man["shots"]
    counts = {}  # (i, arm) -> {basis: counts}
    for idx, (i, arm, basis) in enumerate(man["order"]):
        r = res[idx]; reg = list(r.data.keys())[0]
        counts.setdefault((i, arm), {})[basis] = getattr(r.data, reg).get_counts()
    rows = []
    print(f"Exp156 TRICORDER decode | job {man['job_id']} | backend {man['backend']}")
    print(f"{'R(A)':>6} {'E_hw(CI)':>10} {'+-':>6} {'E_exact':>9} {'dE(mHa)':>8} "
          f"{'E_hw(HF)':>10} {'E_HF':>9} {'corr_hw':>8} {'corr_ex':>8}")
    viol = 0
    for i, ex in enumerate(man["exact"]):
        gs = np.array(ex["gs"])
        E_ci, s_ci = energy_from_counts(gs, counts[(i, "ci")], shots)
        E_hf, s_hf = energy_from_counts(gs, counts[(i, "hf")], shots)
        dE = (E_ci - ex["E_fci"]) * 1000
        corr_hw = (E_hf - E_ci) * 1000; corr_ex = (ex["E_hf"] - ex["E_fci"]) * 1000
        below = E_ci < ex["E_fci"] - 3 * s_ci
        viol += below
        rows.append({"R_ang": ex["R_ang"], "E_ci_hw": E_ci, "sigma_ci": s_ci,
                     "E_hf_hw": E_hf, "sigma_hf": s_hf, "E_fci_exact": ex["E_fci"],
                     "E_hf_exact": ex["E_hf"], "variational_violation": bool(below)})
        print(f"{ex['R_ang']:>6.2f} {E_ci:>10.4f} {s_ci:>6.4f} {ex['E_fci']:>9.4f} {dE:>8.1f} "
              f"{E_hf:>10.4f} {ex['E_hf']:>9.4f} {corr_hw:>8.1f} {corr_ex:>8.1f}"
              + ("  <-- BELOW GROUND (instrument fault!)" if below else ""))
    # equilibrium bond length from the hardware curve (parabola through min and neighbors)
    E_curve = [r["E_ci_hw"] for r in rows]; R_curve = [r["R_ang"] for r in rows]
    k = int(np.argmin(E_curve)); k = min(max(k, 1), len(rows) - 2)
    a, b, c = np.polyfit(R_curve[k - 1:k + 2], E_curve[k - 1:k + 2], 2)
    Re_hw = -b / (2 * a)
    # correlation detection at the far point (2.5 A): HF-CI gap vs exact prediction
    far = rows[-1]; corr_gap = far["E_hf_hw"] - far["E_ci_hw"]
    corr_sig = corr_gap / np.sqrt(far["sigma_ci"] ** 2 + far["sigma_hf"] ** 2)
    corr_pred = far["E_hf_exact"] - far["E_fci_exact"]
    mean_dE = float(np.mean([(r["E_ci_hw"] - r["E_fci_exact"]) for r in rows])) * 1000
    print(f"\nVARIATIONAL BOUND: {viol}/10 points below exact ground (>3 sigma) "
          f"{'-> INSTRUMENT FAULT' if viol else '-> clean (noise pushes UP only, as it must)'}")
    print(f"BOND LENGTH from hardware curve: R_e = {Re_hw:.3f} A (model exact ~0.735, real H2 0.741)")
    print(f"CORRELATION DETECTED at 2.5 A: HF-CI gap = {corr_gap*1000:.0f} mHa "
          f"({corr_sig:.0f} sigma; exact prediction {corr_pred*1000:.0f} mHa)")
    print(f"MEAN ENERGY ERROR (CI arm, 10 points): {mean_dE:+.1f} mHa "
          f"(chemical accuracy = 1.6 mHa; raw hardware, no mitigation)")
    ok = (viol == 0) and (0.65 < Re_hw < 0.85) and (corr_sig > 5) and (corr_gap > 0.5 * corr_pred)
    print(f"VERDICT: {'TRICORDER READS THE MOLECULE — curve, bond length, and correlation all recovered' if ok else 'degraded reading (see rows; honest accounting above)'}")
    out = {"job_id": man["job_id"], "backend": man["backend"], "rows": rows,
           "Re_hw_ang": float(Re_hw), "corr_gap_far_mHa": float(corr_gap * 1000),
           "corr_pred_far_mHa": float(corr_pred * 1000), "corr_sigma": float(corr_sig),
           "mean_dE_mHa": mean_dE, "variational_violations": int(viol), "verdict_ok": bool(ok)}
    fn = os.path.join(HERE, "..", "results", "exp156_decode.json")
    json.dump(out, open(fn, "w"), indent=1)
    print(f"-> {fn}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true"); ap.add_argument("--submit", action="store_true")
    ap.add_argument("--decode", action="store_true"); ap.add_argument("--manifest")
    ap.add_argument("--backend", default="ibm_fez"); ap.add_argument("--shots", type=int, default=4096)
    a = ap.parse_args()
    if a.selftest: selftest()
    elif a.submit: submit(a.backend, a.shots)
    elif a.decode: decode(a.manifest or os.path.join(HERE, "..", "results", "exp156_manifest.json"))
    else: ap.print_help()
