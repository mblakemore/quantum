#!/usr/bin/env python3
"""H10-C2 Givens vacuum prep (Whisper C5018) — the last construction item before prereg.

The L=8 XX-chain ground state is a free-fermion Slater determinant (half filling: the 4
lowest modes of the tridiagonal hopping matrix). Under Jordan-Wigner with ADJACENT-only
rotations, no strings appear: the state is prepared EXACTLY (no variational error) by
  |vac> = [Givens network] |11110000>
where each Givens gate acts on the {|01>,|10>} block of an adjacent pair.

Angle construction: Clements-style elimination of the 8x4 occupied-mode isometry Phi by
adjacent-row Givens rotations until Phi -> [I4; 0]; the inverse sequence applied to
|11110000> prepares the determinant. All rotations REAL (h real symmetric).

KA (gates, all must pass or nothing is read):
  KA-1 isometry elimination exact: residual || G_k...G_1 Phi - [I;0] || < 1e-10
  KA-2 state fidelity: |<eigsh ground | circuit state>| = 1 within 1e-10
  KA-3 energy: <H_f> of the circuit state equals E0 = -4.7588 within 1e-10
Outputs: rotation list (pairs + angles, the FROZEN prep circuit), gate count, and the
depth table update (r=5 row added: the 475-ceiling margin question is settled by numbers,
not hope).
"""
import json, os, sys
import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import eigsh

L = 8; J = 1.0; M = L // 2

# ---- single-particle problem ----
h1 = np.zeros((L, L))
for j in range(L - 1):
    h1[j, j + 1] = h1[j + 1, j] = J
w1, v1 = np.linalg.eigh(h1)
Phi = v1[:, :M].copy()                      # 8x4 occupied isometry (4 lowest modes)

# ---- Clements-style elimination by ADJACENT-row Givens ----
# Repeatedly zero the lowest nonzero entry of each column using rotations on rows (r-1, r),
# sweeping columns left to right, bottom up. Records (r-1, r, theta) with the convention
# G(theta) rows: [c, -s; s, c] applied to rows (r-1, r).
rots = []
Phi_w = Phi.copy()
for c in range(M):
    for r in range(L - 1, c, -1):
        a, b = Phi_w[r - 1, c], Phi_w[r, c]
        if abs(b) < 1e-14: continue
        th = np.arctan2(b, a)               # rotate so row r entry -> 0
        cs, sn = np.cos(th), np.sin(th)
        G = np.eye(L); G[r-1, r-1] = cs; G[r-1, r] = sn; G[r, r-1] = -sn; G[r, r] = cs
        Phi_w = G @ Phi_w
        rots.append((r - 1, r, float(th)))
# fix signs on the diagonal (each column should end +1)
ka1 = 0.0
for c in range(M):
    if Phi_w[c, c] < 0: Phi_w[:, c] *= -1   # column sign = determinant phase freedom, harmless
ka1 = float(np.linalg.norm(Phi_w - np.vstack([np.eye(M), np.zeros((L - M, M))])))

# ---- circuit state: inverse rotations applied to |11110000> ----
def givens4(th):
    g = np.eye(4, dtype=complex)
    g[1, 1] = np.cos(th); g[1, 2] = -np.sin(th)
    g[2, 1] = np.sin(th); g[2, 2] = np.cos(th)
    return g

def a2(psi, u4, q1, q2, n=L):
    t = psi.reshape([2] * n)
    t = np.moveaxis(np.tensordot(u4.reshape(2, 2, 2, 2), t, axes=([2, 3], [q1, q2])),
                    [0, 1], [q1, q2])
    return t.reshape(-1)

psi = np.zeros(2 ** L, complex)
psi[int("11110000", 2)] = 1.0               # sites 0..3 occupied (|1> = occupied), site0 = MSB
for (i, r, th) in reversed(rots):
    psi = a2(psi, givens4(-th), i, r)       # inverse sequence, inverse angles

# ---- KA-2/3 against exact diagonalization ----
Xs = sp.csr_matrix(np.array([[0, 1], [1, 0]], complex))
Ys = sp.csr_matrix(np.array([[0, -1j], [1j, 0]]))
def opat(op, q):
    mats = [sp.identity(2, format="csr", dtype=complex)] * L; mats[q] = op
    out = mats[0]
    for m in mats[1:]: out = sp.kron(out, m, format="csr")
    return out
Hf = sp.csr_matrix((2 ** L, 2 ** L), dtype=complex)
for j in range(L - 1):
    Hf = Hf + J / 2 * (opat(Xs, j) @ opat(Xs, j + 1) + opat(Ys, j) @ opat(Ys, j + 1))
wg, vg = eigsh(Hf, k=1, which="SA")
fid = float(abs(np.vdot(vg[:, 0], psi)))
E_circ = float(np.real(np.vdot(psi, Hf @ psi)))
ka2 = abs(1 - fid); ka3 = abs(E_circ - float(wg[0]))
print(f"KA-1 elimination residual: {ka1:.2e}")
print(f"KA-2 fidelity |<vac|circuit>|: {fid:.12f} (resid {ka2:.2e})")
print(f"KA-3 energy: {E_circ:.6f} vs E0 {float(wg[0]):.6f} (resid {ka3:.2e})")
ok = ka1 < 1e-10 and ka2 < 1e-10 and ka3 < 1e-10
print("GIVENS KA:", "PASS" if ok else "FAIL — DO NOT USE")
n_giv = len(rots)
print(f"rotations: {n_giv}  (CX at 2/rot: {2*n_giv}, at 3/rot: {3*n_giv})")

out = {"L": L, "M": M, "rotations": [[i, r, th] for (i, r, th) in rots],
       "KA": {"elim": ka1, "fid_resid": ka2, "E_resid": ka3, "pass": ok},
       "n_rotations": n_giv,
       "prep_cx": {"at2": 2 * n_giv, "at3": 3 * n_giv},
       "depth_note": ("evolution r=6: 240 2q logical; totals 240+prep -> "
                      f"{240 + 2*n_giv}..{240 + 3*n_giv} logical, x1.6 routing = "
                      f"{int((240 + 2*n_giv)*1.6)}..{int((240 + 3*n_giv)*1.6)} routed "
                      "vs ceiling 475 — prereg carries a transpiled-count HOLD at 500")}
if ok:
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                                     "results", "h10_c2_givens_prep_c5018.json"), "w"),
              indent=1, default=float)
    print("-> results/h10_c2_givens_prep_c5018.json")
sys.exit(0 if ok else 1)
