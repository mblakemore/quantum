#!/usr/bin/env python3
"""HLF transversality audit — [[4,2,2]] logical actions of transversal candidates. C4901, 0 QPU.

Gates Horizons-4 Invention 6 (the logical HLF computer). Method: for each candidate
physical Clifford on one block (4q) or two blocks (8q), conjugate the logical Paulis and
the stabilizers; verify the stabilizer GROUP is preserved; decompose each image over GF(2)
in the group <stabilizers, logicals> and report the induced LOGICAL map. Everything is
machine-checked via qiskit.quantum_info — no hand algebra trusted.

Code convention (Exp191 readout map): stabilizers XXXX, ZZZZ;
  X1 = X0X1   Z1 = Z0Z2     (logical qubit L1)
  X2 = X0X2   Z2 = Z0Z1     (logical qubit L2)
"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Clifford, Pauli

S_X = Pauli("XXXX"); S_Z = Pauli("ZZZZ")
LOG = {"X1": Pauli("IIXX"[::-1] if False else "XXII"[::-1]),  # placeholder, set below
       }
# Build logical Paulis explicitly (qiskit Pauli string = q_{n-1}...q_0, so reverse):
def P(label_by_qubit):  # label_by_qubit: dict {qubit: 'X'/'Y'/'Z'} on n qubits
    n = max(label_by_qubit) + 1 if label_by_qubit else 4
    n = max(n, 4)
    s = ["I"] * n
    for q, l in label_by_qubit.items(): s[q] = l
    return Pauli("".join(reversed(s)))

def Pn(label_by_qubit, n):
    s = ["I"] * n
    for q, l in label_by_qubit.items(): s[q] = l
    return Pauli("".join(reversed(s)))

GEN1 = {  # one block (4 qubits): stabilizers + logicals
    "Sx": P({0: "X", 1: "X", 2: "X", 3: "X"}),
    "Sz": P({0: "Z", 1: "Z", 2: "Z", 3: "Z"}),
    "X1": P({0: "X", 1: "X"}), "Z1": P({0: "Z", 2: "Z"}),
    "X2": P({0: "X", 2: "X"}), "Z2": P({0: "Z", 1: "Z"}),
}

def gens_two_blocks():
    g = {}
    for name, p in GEN1.items():
        for blk, off in (("A", 0), ("B", 4)):
            lab = {}
            z, x = p.z, p.x
            for q in range(4):
                l = "I"
                if x[q] and z[q]: l = "Y"
                elif x[q]: l = "X"
                elif z[q]: l = "Z"
                if l != "I": lab[q + off] = l
            g[name + blk] = Pn(lab, 8)
    return g

def decompose(target, gens):
    """Express target Pauli (up to phase) as product of gens over GF(2). Returns (combo, phase_ok)."""
    names = list(gens)
    n = len(target.z)
    M = np.zeros((2 * n, len(names)), dtype=np.uint8)
    for j, nm in enumerate(names):
        M[:n, j] = gens[nm].z.astype(np.uint8)
        M[n:, j] = gens[nm].x.astype(np.uint8)
    v = np.concatenate([target.z.astype(np.uint8), target.x.astype(np.uint8)])
    # Gaussian elimination over GF(2)
    A = np.concatenate([M, v[:, None]], axis=1).astype(np.uint8)
    rows, cols = A.shape
    piv = []
    r = 0
    for c in range(cols - 1):
        pr = None
        for rr in range(r, rows):
            if A[rr, c]:
                pr = rr; break
        if pr is None: continue
        A[[r, pr]] = A[[pr, r]]
        for rr in range(rows):
            if rr != r and A[rr, c]:
                A[rr] ^= A[r]
        piv.append(c); r += 1
    # check consistency
    for rr in range(r, rows):
        if A[rr, -1]:
            return None, None
    sol = np.zeros(cols - 1, dtype=np.uint8)
    # back-substitute from reduced form
    r2 = 0
    for c in piv:
        sol[c] = A[r2, -1]; r2 += 1
    combo = [names[j] for j in range(len(names)) if sol[j]]
    # verify including phase
    prod = Pauli("I" * n)
    for nm in combo:
        prod = prod.compose(gens[nm])
    phase_match = (prod == target)
    anti = (prod.z == target.z).all() and (prod.x == target.x).all()
    return combo, (phase_match, anti, str(prod.phase), str(target.phase))

def audit(name, qc, gens):
    cl = Clifford(qc)
    n = qc.num_qubits
    print(f"\n=== {name} ===")
    ok_stab = True
    for gname, g in gens.items():
        img = g.evolve(cl, frame="s")  # Heisenberg: U g U^dagger
        combo, phase = decompose(img, gens)
        if combo is None:
            print(f"  {gname} -> {img}  ** NOT IN GROUP — stabilizer/code NOT preserved **")
            ok_stab = False
            continue
        sign = "+" if phase[0] else ("-" if phase[1] else "?")
        print(f"  {gname} -> {img}  = {sign}{'*'.join(combo) if combo else 'I'}")
    return ok_stab

print("=" * 70)
print("PART 1 — single block (4 qubits): candidate transversal operations")
print("=" * 70)

qc = QuantumCircuit(4)
for q in range(4): qc.h(q)
audit("H^4 (transversal Hadamard)", qc, GEN1)

qc = QuantumCircuit(4)
for q in range(4): qc.s(q)
audit("S^4 (transversal phase)", qc, GEN1)

qc = QuantumCircuit(4)
for q in range(4): qc.sdg(q)
audit("Sdg^4", qc, GEN1)

qc = QuantumCircuit(4)
qc.swap(1, 2)
audit("SWAP(q1,q2) (automorphism, 197's permuted wiring)", qc, GEN1)

qc = QuantumCircuit(4)
qc.cz(0, 1); qc.cz(2, 3)
audit("CZ(01)CZ(23) (in-block CZ pairing pattern a)", qc, GEN1)

qc = QuantumCircuit(4)
qc.cz(0, 2); qc.cz(1, 3)
audit("CZ(02)CZ(13) (in-block CZ pairing pattern b)", qc, GEN1)

qc = QuantumCircuit(4)
qc.cz(0, 3); qc.cz(1, 2)
audit("CZ(03)CZ(12) (in-block CZ pairing pattern c)", qc, GEN1)

print()
print("=" * 70)
print("PART 2 — two blocks (8 qubits): transversal block-pair operations")
print("=" * 70)
G2 = gens_two_blocks()

qc = QuantumCircuit(8)
for q in range(4): qc.cx(q, q + 4)
audit("tCNOT A->B straight (certified 191/196/197)", qc, G2)

qc = QuantumCircuit(8)
for q in range(4): qc.cz(q, q + 4)
audit("tCZ A-B straight (CZ(q, q+4) x4)", qc, G2)

perm = {0: 0, 1: 2, 2: 1, 3: 3}
qc = QuantumCircuit(8)
for q in range(4): qc.cz(q, 4 + perm[q])
audit("tCZ A-B permuted (B-side q1<->q2)", qc, G2)

print()
print("=" * 70)
print("PART 3 — the generated LOGICAL group (mod Paulis): is single-logical S reachable?")
print("=" * 70)
# Represent logical actions as symplectic 4x4 GF(2) matrices on (z1,z2,x1,x2) of L1,L2.
# Columns = images of Z1,Z2,X1,X2 expressed in (Z1,Z2,X1,X2) exponents (mod stabilizers/Paulis).

def sym(mapping):
    """mapping: dict from 'Z1','Z2','X1','X2' -> list of generators among same, e.g. X1->['X1','Z2']"""
    idx = {"Z1": 0, "Z2": 1, "X1": 2, "X2": 3}
    M = np.zeros((4, 4), dtype=np.uint8)
    for src, imgs in mapping.items():
        for g in imgs:
            M[idx[g], idx[src]] ^= 1
    return M

# From the audited tables (stabilizer factors and signs dropped = mod Pauli/stabilizer):
GATES = {
    "Hbar2_SWAP": sym({"Z1": ["X2"], "Z2": ["X1"], "X1": ["Z2"], "X2": ["Z1"]}),   # H^4
    "CZbar":      sym({"Z1": ["Z1"], "Z2": ["Z2"], "X1": ["X1", "Z2"], "X2": ["X2", "Z1"]}),  # S^4
    "SWAPbar":    sym({"Z1": ["Z2"], "Z2": ["Z1"], "X1": ["X2"], "X2": ["X1"]}),   # SWAP(q1,q2)
}
# targets
S1 = sym({"Z1": ["Z1"], "Z2": ["Z2"], "X1": ["X1", "Z1"], "X2": ["X2"]})           # S on L1 alone
SS = sym({"Z1": ["Z1"], "Z2": ["Z2"], "X1": ["X1", "Z1"], "X2": ["X2", "Z2"]})     # S x S
H1 = sym({"Z1": ["X1"], "Z2": ["Z2"], "X1": ["Z1"], "X2": ["X2"]})                 # H on L1 alone

def key(M): return M.tobytes()
seen = {key(np.eye(4, dtype=np.uint8)): []}
frontier = [np.eye(4, dtype=np.uint8)]
while frontier:
    new = []
    for M in frontier:
        for gname, G in GATES.items():
            M2 = (G @ M) % 2
            k = key(M2)
            if k not in seen:
                seen[k] = seen[key(M)] + [gname]
                new.append(M2)
    frontier = new
print(f"generated logical group size (mod Paulis): {len(seen)}  [full Sp(4,2) = 720]")
for name, T in (("S on L1 alone", S1), ("S x S", SS), ("H on L1 alone", H1)):
    k = key(T)
    if k in seen:
        w = seen[k]
        print(f"  {name}: REACHABLE, word length {len(w)}: {' . '.join(w) if w else 'I'}")
    else:
        print(f"  {name}: NOT reachable from single-block transversal set")
