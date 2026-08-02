#!/usr/bin/env python3
"""H10-C2 as-flown Trotter pricing (Whisper C5018) — the second door past the depth wall.

L=6 killed the harvest window (SS8 honest negative: N_cut = 0 in all 180 configs — the cut
halves are too small and edge-bound to hold the cross-cut vacuum correlations the detectors
tap). The C1-calibrated ceiling (~475 routed 2q) is instead met by keeping L=8 and reducing
the TROTTER STEP COUNT r, with the coarser-step bias absorbed into AS-FLOWN bars — the C1
SS10 discipline: the registered prediction is the value of the circuit actually flown.

This script evolves the OP configuration with the CIRCUIT-FAITHFUL 2nd-order step sequence
(per step: half-sweep of field bonds in order [cut bond skipped in the cut arm], full-step
detector couplings, reversed half-sweep) and prices depth per r. KA: r=64 must converge to
the exact-evolution campaign value (N_cut = 0.04835, N_full = 0.04225) before smaller r is
read.  OP: Om=1.5, d=3 (s1=2, s2=5), T=2.5, lam=0.6, tophat (L=8).
"""
import json, os, sys
import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import eigsh

L = 8; J = 1.0; NQ = L + 2
OM, D, T, LAM = 1.5, 3, 2.5, 0.6
S1 = 2; S2 = S1 + D; CUT = S1 + D // 2          # bond (3,4)
I2 = np.eye(2); X = np.array([[0, 1], [1, 0]], complex); Y = np.array([[0, -1j], [1j, 0]])

def kron2(A, B): return np.kron(A, B)
HB = J / 2 * (kron2(X, X) + kron2(Y, Y).real + 1j * np.zeros((4, 4)))  # bond generator (real)
HB = J / 2 * (np.kron(X, X) + np.kron(Y, Y)).real
HC = LAM * np.kron(X, X).real                     # detector coupling generator
wB, vB = np.linalg.eigh(HB)
wC, vC = np.linalg.eigh(HC)
wN = np.diag([0.0, OM])                            # detector self-energy |e><e|, |e>=|1>

def u4(w, v, a): return (v * np.exp(-1j * a * w)) @ v.conj().T

def a2(psi, u, q1, q2):
    t = psi.reshape([2] * NQ)
    t = np.moveaxis(np.tensordot(u.reshape(2, 2, 2, 2), t, axes=([2, 3], [q1, q2])),
                    [0, 1], [q1, q2])
    return t.reshape(-1)

def a1d(psi, dvec, q):
    sh = [1] * NQ; sh[q] = 2
    return (psi.reshape([2] * NQ) * dvec.reshape(sh)).reshape(-1)

def vacuum():
    Xs = sp.csr_matrix(X); Ys = sp.csr_matrix(Y)
    def opat(op, q):
        mats = [sp.identity(2, format="csr", dtype=complex)] * L; mats[q] = op
        out = mats[0]
        for m in mats[1:]: out = sp.kron(out, m, format="csr")
        return out
    H = sp.csr_matrix((2 ** L, 2 ** L), dtype=complex)
    for j in range(L - 1):
        H = H + J / 2 * (opat(Xs, j) @ opat(Xs, j + 1) + opat(Ys, j) @ opat(Ys, j + 1))
    w, v = eigsh(H, k=1, which="SA")
    psi = np.zeros(2 ** NQ, complex)
    psi[np.arange(2 ** L) * 4] = v[:, 0]
    return psi

def evolve_trot(psi0, r, cut):
    """Circuit-faithful o2 step: [bond half-sweep fwd] [det couplings + det phases, full]
    [bond half-sweep rev], r steps of dt=T/r, tophat."""
    psi = psi0.copy(); dt = T / r
    bonds = [j for j in range(L - 1) if not (cut and j == CUT)]
    Ubh = u4(wB, vB, dt / 2)
    Uc = u4(wC, vC, dt)
    ph = np.exp(-1j * dt * np.array([0.0, OM]))
    for _ in range(r):
        for j in bonds: psi = a2(psi, Ubh, j, j + 1)
        psi = a2(psi, Uc, S1, L); psi = a2(psi, Uc, S2, L + 1)
        psi = a1d(psi, ph, L); psi = a1d(psi, ph, L + 1)
        for j in reversed(bonds): psi = a2(psi, Ubh, j, j + 1)
    return psi

def negativity(psi):
    m = psi.reshape(2 ** L, 4)
    rho = m.conj().T @ m
    pt = rho.reshape(2, 2, 2, 2).transpose(0, 3, 2, 1).reshape(4, 4)
    ev = np.linalg.eigvalsh(pt)
    return float(-ev[ev < 0].sum())

def depth(r):
    """Logical 2q count: bonds(6 in cut arm)*3CX*2 half-sweeps... each half-sweep gate is one
    e^{-i a (XX+YY)} = 2-3 CX (XY class; price 3) applied 2x per step; det couplings 2 x RXX
    (2 CX) per step; prep = Givens network for the L=8 half-filled Slater det: 4x4=16
    rotations x ~2.5 CX ~ 40."""
    per_step = 6 * 3 * 2 + 2 * 2
    return 40 + r * per_step

def main():
    psi0 = vacuum()
    out = {"OP": {"Om": OM, "d": D, "T": T, "lam": LAM, "env": "tophat", "L": L},
           "exact_reference": {"N_cut": 0.04835, "N_full": 0.04225}, "rows": []}
    for r in (64, 16, 12, 10, 8, 6):
        Nc = negativity(evolve_trot(psi0, r, cut=True))
        Nf = negativity(evolve_trot(psi0, r, cut=False))
        rows = {"r": r, "N_cut": Nc, "N_full": Nf, "logical_2q": depth(r),
                "routed_est_1.6x": int(depth(r) * 1.6)}
        out["rows"].append(rows)
        print(f"r={r:3d}: N_cut={Nc:.5f} N_full={Nf:.5f} logical~{depth(r)} routed~{int(depth(r)*1.6)}")
    ka = abs(out["rows"][0]["N_cut"] - 0.04835)
    out["KA_r64_vs_exact"] = ka
    print(f"KA r=64 vs exact campaign: {ka:.2e} {'PASS' if ka < 2e-3 else 'FAIL — do not read'}")
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results",
                        "h10_c2_asflown_r_c5018.json")
    json.dump(out, open(path, "w"), indent=1, default=float)
    print("->", path)

if __name__ == "__main__":
    main()
