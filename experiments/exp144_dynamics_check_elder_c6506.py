"""Redesign (i) check: e^{-iHt} on system half of pure Bell pairs.
Claim: Bell labels peak on the 2^m subset-products of planted terms with
p(P_S) = prod_{j in S} sin^2(c_j t) * prod_{j notin S} cos^2(c_j t)  -- O(1) contrast.
"""
import numpy as np, itertools, math
from scipy.linalg import expm

I2 = np.eye(2, dtype=complex)
X = np.array([[0,1],[1,0]], dtype=complex)
Y = np.array([[0,-1j],[1j,0]], dtype=complex)
Z = np.array([[1,0],[0,-1]], dtype=complex)
PAULI = [I2,X,Y,Z]; NAMES = "IXYZ"

def kron_all(ms):
    out = np.array([[1.0+0j]])
    for m in ms: out = np.kron(out, m)
    return out
def pop(label): return kron_all([PAULI[NAMES.index(c)] for c in label])

n = 3; d = 2**n
labels = ["".join(t) for t in itertools.product(NAMES, repeat=n)]

# commuting FULL-WEIGHT planted terms (they commute: check), coefficients c_j, t chosen
terms = [("XXX", 0.35), ("YYX", 0.55)]   # verify commuting below
P1, P2 = pop(terms[0][0]), pop(terms[1][0])
assert np.allclose(P1@P2, P2@P1), "terms must commute"
t = 1.0
H = terms[0][1]*P1 + terms[1][1]*P2
V = expm(-1j*H*t)

phi = np.zeros(d*d, dtype=complex)
for i in range(d): phi[i*d+i] = 1.0
phi /= math.sqrt(d)
psi = np.kron(V, np.eye(d)) @ phi

p = {}
for lab in labels:
    v = np.kron(pop(lab), np.eye(d)) @ phi
    p[lab] = abs(v.conj() @ psi)**2
srt = sorted(p.items(), key=lambda kv: -kv[1])
print("top 6 Bell labels (dynamics version):")
for lab, pr in srt[:6]: print(f"  {lab}: p={pr:.4f}")
s1, s2 = math.sin(terms[0][1]*t)**2, math.sin(terms[1][1]*t)**2
c1, c2 = 1-s1, 1-s2
prod = "".join(NAMES[[a for a in range(4) if np.allclose(PAULI[a], (P1@P2)[0:2,0:2]*0+PAULI[a])][0]] for _ in [0])  # skip
print(f"\npredicted: III={c1*c2:.4f}  {terms[0][0]}={s1*c2:.4f}  {terms[1][0]}={c1*s2:.4f}  P1*P2={s1*s2:.4f}")
print(f"sum of all other {4**n-4} labels: {sum(pr for lab,pr in p.items() if lab not in ('III',terms[0][0],terms[1][0])) - s1*s2:.2e} (should be ~0 minus the product label)")
nz = [(lab,pr) for lab,pr in srt if pr > 1e-9]
print(f"nonzero labels: {len(nz)} (expect 2^m = 4)")
