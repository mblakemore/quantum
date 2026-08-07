#!/usr/bin/env python3
"""P-CCM v1.0 — component ②: GADGETIZATION and the Heisenberg reduction to magic-state operators.

WHAT THIS COMPONENT IS. The solver never simulates a Clifford+T circuit forward. It does this:

    T gate  ->  Clifford gadget consuming one |A>, with a measurement
    measurement outcome  ->  a uniform POSTSELECTION bit y_j (paper Sec IV)
    the whole Clifford V_y  ->  propagated ONCE in the HEISENBERG picture onto the t magic qubits

leaving (paper Eq 28)

    P^y_out(x)  =  2^-u <psi|Pi_G|psi>  /  2^-v <psi|Pi_H|psi>

with G, H stabilizer groups in P_t and u, v integers. THE CIRCUIT IS THEN GONE. Everything after
this point acts on t qubits, not n + t, and costs O((n+t)^3) ONCE rather than per term — which is
why Eq 3 carries w(n+t)^3 as an ADDITIVE term outside the 2^(gamma t) factor.

SCOPE, STATED SO IT IS NOT OVERREAD. This file produces (G, H, u, v). It does NOT evaluate
<psi|Pi_G|psi> on the standard form — that needs a general-Pauli projection of a stabilizer state
(component ③), which does not exist yet. The gates below evaluate <psi|Pi_G|psi> with explicit
2^t matrices, which is a VERIFICATION route and not a solver path.

THE T GADGET (paper Fig 2), derived rather than asserted:
    |psi>(x)|A>, CNOT(data -> magic), measure magic -> y
      y=0:  a|0> + b e^{i pi/4}|1>            =  T|psi>
      y=1:  e^{i pi/4}(a|0> + b e^{-i pi/4}|1>) = e^{i pi/4} T^dag|psi>,  fixed by S on data
    so V_y applies CNOT(q, n+j) and then S^{y_j} on q, and postselects magic qubit n+j onto y_j.
    Postselection may be deferred to the end of the circuit because nothing touches magic qubit
    n+j after its CNOT.

THE GATE THAT MATTERS (G3). With the EXACT magic state |A>^(x)t, Eq 18 says the final state of
the n computational qubits is U|0^n> REGARDLESS of y. So

    P^y_out(x) must equal the brute-force P_out(x) for EVERY y, exactly.

That is a sharp, cheap, falsifiable check on the whole pipeline: gadget, conjugation rules,
null-space reduction, and the exponent u — all at once. A phase error anywhere breaks it.

Substrate: claude-fable-5, Whisper C5022. Creator directive: "build the gadgetization".
"""
import itertools
import math
import sys

import numpy as np

I2 = np.eye(2, dtype=complex)
XM = np.array([[0, 1], [1, 0]], dtype=complex)
ZM = np.array([[1, 0], [0, -1]], dtype=complex)
XZ = XM @ ZM                                    # [[0,-1],[1,0]] — the (a,b)=(1,1) generator


# ─────────────────────────────────────────────────────────────────────────────
# Pauli:  P = i^k X^a Z^b   (all X factors left of all Z factors)
# ─────────────────────────────────────────────────────────────────────────────
class Pauli:
    __slots__ = ("k", "a", "b", "m")

    def __init__(self, k, a, b):
        self.a = np.asarray(a, dtype=np.uint8) & 1
        self.b = np.asarray(b, dtype=np.uint8) & 1
        self.k = int(k) % 4
        self.m = len(self.a)

    def copy(self):
        return Pauli(self.k, self.a.copy(), self.b.copy())

    def mul(self, o):
        """(i^k1 X^a1 Z^b1)(i^k2 X^a2 Z^b2). Z^b1 X^a2 = (-1)^(b1.a2) X^a2 Z^b1."""
        swap = int(np.dot(self.b.astype(int), o.a.astype(int))) & 1
        return Pauli(self.k + o.k + 2 * swap, self.a ^ o.a, self.b ^ o.b)

    def is_identity(self):
        return not self.a.any() and not self.b.any()

    def matrix(self):
        """Explicit 2^m matrix. VERIFICATION ONLY."""
        M = np.array([[1.0 + 0j]])
        for j in range(self.m):
            f = (XZ if self.b[j] else XM) if self.a[j] else (ZM if self.b[j] else I2)
            M = np.kron(M, f)
        return (1j ** self.k) * M

    def __repr__(self):
        s = "".join("IXZY"[int(self.a[j]) + 2 * int(self.b[j])] for j in range(self.m))
        return f"i^{self.k}·{s}"


def pauli_Z(m, j, sign=0):
    """(-1)^sign Z_j."""
    b = np.zeros(m, dtype=np.uint8)
    b[j] = 1
    return Pauli(2 * (sign & 1), np.zeros(m, dtype=np.uint8), b)


# ─────────────────────────────────────────────────────────────────────────────
# Clifford conjugation:  conj(P, g) = g P g^dag.   Every rule is gated (G1).
# ─────────────────────────────────────────────────────────────────────────────
def conj(P, gate):
    g, q = gate[0], gate[1:]
    k, a, b = P.k, P.a.copy(), P.b.copy()
    if g == "H":
        j = q[0]
        if a[j] and b[j]:
            k += 2                                   # H(XZ)H = ZX = -XZ
        a[j], b[j] = b[j], a[j]
    elif g == "S":
        j = q[0]
        if a[j]:
            k += 1                                   # SXS' = iXZ,  S(XZ)S' = iX
        b[j] ^= a[j]
    elif g == "SDG":
        j = q[0]
        if a[j]:
            k += 3
        b[j] ^= a[j]
    elif g == "X":
        k += 2 * int(b[q[0]])
    elif g == "Z":
        k += 2 * int(a[q[0]])
    elif g == "Y":
        j = q[0]
        k += 2 * ((int(a[j]) + int(b[j])) & 1)
    elif g == "CNOT":
        c, t = q
        a[t] ^= a[c]
        b[c] ^= b[t]
    elif g == "CZ":
        i, j = q
        k += 2 * (int(a[i]) & int(a[j]))
        b[j] ^= a[i]
        b[i] ^= a[j]
    else:
        raise ValueError(f"not a Clifford gate: {g}")
    return Pauli(k, a, b)


_INV = {"H": "H", "X": "X", "Y": "Y", "Z": "Z", "CNOT": "CNOT", "CZ": "CZ",
        "S": "SDG", "SDG": "S"}


def conj_inv(P, gate):
    """g^dag P g."""
    return conj(P, (_INV[gate[0]],) + tuple(gate[1:]))


def conjugate_through(P, gates):
    """V^dag P V for V = gates applied in list order. Iterate in REVERSE with g^dag P g."""
    for gate in reversed(gates):
        P = conj_inv(P, gate)
    return P


# ─────────────────────────────────────────────────────────────────────────────
# explicit matrices — VERIFICATION ONLY
# ─────────────────────────────────────────────────────────────────────────────
SQ = {
    "H": np.array([[1, 1], [1, -1]], dtype=complex) / math.sqrt(2),
    "S": np.array([[1, 0], [0, 1j]], dtype=complex),
    "SDG": np.array([[1, 0], [0, -1j]], dtype=complex),
    "T": np.array([[1, 0], [0, np.exp(1j * math.pi / 4)]], dtype=complex),
    "X": XM, "Z": ZM, "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
}


def gate_matrix(gate, m):
    g, q = gate[0], gate[1:]
    if g in SQ:
        M = np.array([[1.0 + 0j]])
        for j in range(m):
            M = np.kron(M, SQ[g] if j == q[0] else I2)
        return M
    dim = 2 ** m
    M = np.zeros((dim, dim), dtype=complex)
    for s in range(dim):
        bits = [(s >> (m - 1 - j)) & 1 for j in range(m)]
        if g == "CNOT":
            c, t = q
            if bits[c]:
                bits[t] ^= 1
            M[int("".join(map(str, bits)), 2), s] = 1
        elif g == "CZ":
            i, j = q
            M[s, s] = -1 if (bits[i] and bits[j]) else 1
        else:
            raise ValueError(g)
    return M


def circuit_matrix(gates, m):
    M = np.eye(2 ** m, dtype=complex)
    for gate in gates:
        M = gate_matrix(gate, m) @ M
    return M


# ─────────────────────────────────────────────────────────────────────────────
# ② gadgetization
# ─────────────────────────────────────────────────────────────────────────────
def gadgetize(gates, n):
    """Clifford+T circuit on n qubits -> (build_Vy, t).

    build_Vy(y) returns the Clifford gate list on n+t qubits for postselection string y.
    Magic qubit j lives at index n+j and is consumed by the j-th T gate."""
    t = sum(1 for g in gates if g[0] == "T")

    def build(y):
        out, j = [], 0
        for g in gates:
            if g[0] == "T":
                out.append(("CNOT", g[1], n + j))
                if y[j]:
                    out.append(("S", g[1]))
                j += 1
            else:
                out.append(g)
        return out

    return build, t


def _nullspace_f2(M):
    """Basis of {c : c M = 0} for M an (r x n) F2 matrix. Returns rows c of length r."""
    r, n = M.shape
    A = np.concatenate([M.copy() % 2, np.eye(r, dtype=np.uint8)], axis=1)
    row = 0
    for c in range(n):
        piv = None
        for i in range(row, r):
            if A[i, c]:
                piv = i
                break
        if piv is None:
            continue
        A[[row, piv]] = A[[piv, row]]
        for i in range(r):
            if i != row and A[i, c]:
                A[i] ^= A[row]
        row += 1
        if row == r:
            break
    return np.array([A[i, n:] for i in range(r) if not A[i, :n].any()], dtype=np.uint8)


def heisenberg_reduce(gates, n, t, generators):
    """Conjugate `generators` through V and reduce to operators on the t magic qubits.

    Returns (G_elements, u).  <0^n (x) psi| Pi_S' |0^n (x) psi> = 2^-u <psi|Pi_G|psi>,
    where Pi_G = 2^-d SUM over subsets of G_elements and d = |G_elements|.

    HOW. Pi_S' = 2^-r SUM_{P in S'} P.  <0^n|P_A|0^n> vanishes unless P_A is Z-type, and equals
    +1 when it is (both <0|I|0> and <0|Z|0> are 1). The surviving subgroup is the null space of
    the generators' X-parts restricted to the first n qubits; u = r - dim(null)."""
    conjugated = [conjugate_through(P, gates) for P in generators]
    r = len(conjugated)
    M = np.array([P.a[:n] for P in conjugated], dtype=np.uint8)
    null = _nullspace_f2(M) if r else np.zeros((0, 0), dtype=np.uint8)

    G = []
    for cvec in null:
        acc = Pauli(0, np.zeros(n + t, dtype=np.uint8), np.zeros(n + t, dtype=np.uint8))
        for i in range(r):
            if cvec[i]:
                acc = acc.mul(conjugated[i])
        assert not acc.a[:n].any(), "null-space element still has an X part on the data register"
        G.append(Pauli(acc.k, acc.a[n:], acc.b[n:]))       # phase rides with the magic part
    return G, r - len(null)


def projector_matrix(G, t):
    """Pi = 2^-d SUM over all subsets of G. Handles a -I in the group automatically (gives 0)
    and a non-trivial kernel automatically (each element counted |ker| times, which cancels).
    VERIFICATION ONLY — 2^t x 2^t."""
    d = len(G)
    P = np.zeros((2 ** t, 2 ** t), dtype=complex)
    for sub in itertools.product([0, 1], repeat=d):
        acc = Pauli(0, np.zeros(t, dtype=np.uint8), np.zeros(t, dtype=np.uint8))
        for i, s in enumerate(sub):
            if s:
                acc = acc.mul(G[i])
        P += acc.matrix()
    return P / 2 ** d


def pout_gadget(gates, n, Qout, x, y, psi_magic):
    """P^y_out(x) via Eq 28, using explicit matrices for <psi|Pi|psi> (verification route)."""
    build, t = gadgetize(gates, n)
    V = build(y)
    num_gens = [pauli_Z(n + t, j, x[i]) for i, j in enumerate(Qout)] + \
               [pauli_Z(n + t, n + j, y[j]) for j in range(t)]
    den_gens = [pauli_Z(n + t, n + j, y[j]) for j in range(t)]
    G, u = heisenberg_reduce(V, n, t, num_gens)
    H, v = heisenberg_reduce(V, n, t, den_gens)
    num = 2.0 ** (-u) * np.vdot(psi_magic, projector_matrix(G, t) @ psi_magic).real
    den = 2.0 ** (-v) * np.vdot(psi_magic, projector_matrix(H, t) @ psi_magic).real
    return num, den, (num / den if abs(den) > 1e-14 else float("nan")), (G, u, H, v)


def brute_force_pout(gates, n, Qout, x):
    """Oracle: P_out(x) from the explicit statevector of the ORIGINAL Clifford+T circuit."""
    psi = circuit_matrix(gates, n) @ np.eye(2 ** n, dtype=complex)[:, 0]
    tot = 0.0
    for s in range(2 ** n):
        bits = [(s >> (n - 1 - j)) & 1 for j in range(n)]
        if all(bits[q] == x[i] for i, q in enumerate(Qout)):
            tot += abs(psi[s]) ** 2
    return tot


A_STATE = np.array([1.0, np.exp(1j * math.pi / 4)]) / math.sqrt(2)


def a_tensor(t):
    v = np.array([1.0 + 0j])
    for _ in range(t):
        v = np.kron(v, A_STATE)
    return v


def random_circuit(n, ngates, nt, rng):
    gates = []
    kinds = ["H", "S", "X", "Z", "CNOT", "CZ"]
    for _ in range(ngates):
        g = kinds[int(rng.integers(len(kinds)))]
        if g in ("CNOT", "CZ"):
            if n < 2:
                continue
            i, j = rng.choice(n, size=2, replace=False)
            gates.append((g, int(i), int(j)))
        else:
            gates.append((g, int(rng.integers(n))))
    for _ in range(nt):
        gates.insert(int(rng.integers(len(gates) + 1)), ("T", int(rng.integers(n))))
    return gates


# ─────────────────────────────────────────────────────────────────────────────
# GATES
# ─────────────────────────────────────────────────────────────────────────────
def self_test(verbose=True):
    rng = np.random.default_rng(20260807)
    npass = nfail = 0

    def rec(name, ok, detail=""):
        nonlocal npass, nfail
        npass += ok
        nfail += (not ok)
        if verbose:
            print(f"    {'PASS' if ok else 'FAIL':>4}  {name:<48} {detail}")

    print("  G1 — every conjugation rule against explicit matrices, ALL Paulis")
    for m in (1, 2, 3):
        cand = [("H", 0), ("S", 0), ("SDG", 0), ("X", 0), ("Y", 0), ("Z", 0)]
        if m >= 2:
            cand += [("CNOT", 0, 1), ("CZ", 0, 1), ("CNOT", 1, 0)]
        if m >= 3:
            cand += [("CNOT", 2, 0), ("CZ", 1, 2), ("H", 2), ("S", 2)]
        for gate in cand:
            U = gate_matrix(gate, m)
            bad = 0
            for av in itertools.product([0, 1], repeat=m):
                for bv in itertools.product([0, 1], repeat=m):
                    for k in range(4):
                        P = Pauli(k, np.array(av, np.uint8), np.array(bv, np.uint8))
                        want = U @ P.matrix() @ U.conj().T
                        if not np.allclose(conj(P, gate).matrix(), want, atol=1e-10):
                            bad += 1
            rec(f"G1 conj {str(gate):<16} m={m}", bad == 0,
                f"{4*4**m} Paulis, {bad} mismatches")

    print("\n  G2 — the T gadget really implements T (both outcomes, phase included)")
    bad = 0
    for _ in range(50):
        v = rng.normal(size=2) + 1j * rng.normal(size=2)
        v /= np.linalg.norm(v)
        joint = np.kron(v, A_STATE)
        joint = gate_matrix(("CNOT", 0, 1), 2) @ joint
        for y in (0, 1):
            branch = joint[y::2] if False else np.array([joint[0 * 2 + y], joint[1 * 2 + y]])
            if y:
                branch = SQ["S"] @ branch
            want = SQ["T"] @ v
            branch = branch / np.linalg.norm(branch) * np.linalg.norm(want)
            ph = branch[np.argmax(np.abs(want))] / want[np.argmax(np.abs(want))]
            if not np.allclose(branch, ph * want, atol=1e-9) or abs(abs(ph) - 1) > 1e-9:
                bad += 1
    rec("G2 gadget branch == T|psi> up to phase", bad == 0, f"100 branches, {bad} bad")

    print("\n  G3 — P^y_out(x) == brute-force P_out(x) for EVERY y  (Eq 18: y-independence)")
    print("       the whole pipeline at once: gadget, conjugation, null space, and u")
    worst = 0.0
    ncase = 0
    for trial in range(16):
        n = int(rng.integers(2, 6))                 # widened to n<=5, t<=4 to resolve P6
        nt = int(rng.integers(1, 5))
        gates = random_circuit(n, int(rng.integers(3, 10)), nt, rng)
        _, t = gadgetize(gates, n)
        w = int(rng.integers(1, n + 1))
        Qout = sorted(rng.choice(n, size=w, replace=False).tolist())
        x = tuple(int(v) for v in rng.integers(0, 2, size=w))
        want = brute_force_pout(gates, n, Qout, x)
        psi = a_tensor(t)
        for y in itertools.product([0, 1], repeat=t):
            num, den, got, _ = pout_gadget(gates, n, Qout, x, y, psi)
            ncase += 1
            worst = max(worst, abs(got - want))
    rec("G3 P^y_out(x) == P_out(x) for all y", worst < 1e-9,
        f"{ncase} (circuit, y) cases, max |err| = {worst:.2e}")

    print("\n  G4 — the denominator is the postselection weight: p_y = 2^-t for all y")
    worst2 = 0.0
    for trial in range(6):
        n = int(rng.integers(2, 4))
        nt = int(rng.integers(1, 4))
        gates = random_circuit(n, int(rng.integers(3, 8)), nt, rng)
        _, t = gadgetize(gates, n)
        psi = a_tensor(t)
        Qout = [0]
        for y in itertools.product([0, 1], repeat=t):
            _, den, _, _ = pout_gadget(gates, n, Qout, (0,), y, psi)
            worst2 = max(worst2, abs(den - 2.0 ** (-t)))
    rec("G4 p_y = 2^-t exactly", worst2 < 1e-9, f"max |p_y - 2^-t| = {worst2:.2e}")

    print("\n  G5 — SUM_x P^y_out(x) = 1 over the output register")
    worst3 = 0.0
    for trial in range(6):
        n = 3
        gates = random_circuit(n, 6, int(rng.integers(1, 3)), rng)
        _, t = gadgetize(gates, n)
        psi = a_tensor(t)
        Qout = [0, 1]
        y = tuple(int(v) for v in rng.integers(0, 2, size=t))
        s = sum(pout_gadget(gates, n, Qout, xx, y, psi)[2]
                for xx in itertools.product([0, 1], repeat=2))
        worst3 = max(worst3, abs(s - 1.0))
    rec("G5 normalisation over x", worst3 < 1e-9, f"max |SUM_x P - 1| = {worst3:.2e}")

    print("\n  G6 — ①b SWAPPED IN: the SPARSIFIED state end to end, error vs its own bound")
    print("       |A> = e^{i pi/8} H S' |H>, so (HS')^(x)t folds into V_y and the")
    print("       decomposition may stay in the H frame — no per-term Clifford needed")
    import magic_sparsify as ms
    worst6 = 0.0
    bound6 = 0.0
    ncase6 = 0
    for trial in range(8):
        n = int(rng.integers(2, 4))
        nt = int(rng.integers(2, 5))
        gates = random_circuit(n, int(rng.integers(3, 8)), nt, rng)
        build, t = gadgetize(gates, n)
        kk = max(1, min(t - 1, ms.choose_k(t, 0.5)))
        M = ms.random_subspace(t, kk, rng)
        Z, _ = ms.z_of_L(ms._pack(M), kk)
        psi_H = ms.L_statevector(M, kk, Z)                     # approximates |H^(x)t>
        delta = 1.0 - (2 ** kk) * ms.NU ** (2 * t) / Z         # EXACT, from Eq 35
        pre = [g for j in range(t) for g in (("SDG", n + j), ("H", n + j))]
        w = int(rng.integers(1, n + 1))
        Qout = sorted(rng.choice(n, size=w, replace=False).tolist())
        x = tuple(int(v) for v in rng.integers(0, 2, size=w))
        want = brute_force_pout(gates, n, Qout, x)
        for y in itertools.product([0, 1], repeat=t):
            V = pre + build(y)
            ng = [pauli_Z(n + t, j, x[i]) for i, j in enumerate(Qout)] + \
                 [pauli_Z(n + t, n + j, y[j]) for j in range(t)]
            dg = [pauli_Z(n + t, n + j, y[j]) for j in range(t)]
            G, u = heisenberg_reduce(V, n, t, ng)
            Hh, v = heisenberg_reduce(V, n, t, dg)
            num = 2.0 ** (-u) * np.vdot(psi_H, projector_matrix(G, t) @ psi_H).real
            den = 2.0 ** (-v) * np.vdot(psi_H, projector_matrix(Hh, t) @ psi_H).real
            if abs(den) < 1e-14:
                continue
            worst6 = max(worst6, abs(num / den - want))
            ncase6 = ncase6 + 1
        bound6 = max(bound6, math.sqrt(delta))
    rec("G6 sparsified P_out within sqrt(delta)", worst6 <= bound6 + 1e-9,
        f"{ncase6} cases, max |err| = {worst6:.4f}  vs bound sqrt(delta) = {bound6:.4f}")

    return npass, nfail


if __name__ == "__main__":
    print("GADGETIZATION + HEISENBERG REDUCTION — component ② correctness gates\n")
    print("  T -> CNOT(data, magic) + S^y on data, magic postselected onto y")
    print("  V_y propagated in the Heisenberg picture -> (G, u), (H, v) on the t magic qubits")
    print("  P^y_out(x) = 2^-u <psi|Pi_G|psi> / 2^-v <psi|Pi_H|psi>            [Eq 28]\n")
    p, f = self_test()
    print(f"\n  {p} passed, {f} failed")
    if f == 0:
        print("  ✅ GATES PASSED — the circuit is reduced to t-qubit operators, exactly.")
        print("\n  NOT CLAIMED: <psi|Pi_G|psi> is evaluated here with explicit 2^t matrices.")
        print("  Doing it on the standard form needs a general-Pauli projection of a stabilizer")
        print("  state — component ③, which does not exist yet.")
    else:
        print("  ⛔ GATES NOT PASSED.")
        sys.exit(2)
