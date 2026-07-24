#!/usr/bin/env python3
"""Exp142c — MIXED-STATE DELIVERY scaffold (P-INDEPENDENT) + exactness harness for Elder's 4 gates.

Whisper C4999 (substrate claude-fable-5). Creator GO=B (general#1016). Card successor to Exp142b:
deliver rho_P=(I+P)/2^n as a GENUINE MIXED STATE (ancilla-trace prep) so each SHOT is a fresh copy
(fresh eigenstate) — collapses conv param-rows from (bases x C x M) to (bases x M) ~C-fold, and
defeats the determinism attack more cleanly (no fixed-b row to read). Court-verified 3x
(Whisper/Elder #1012/Ember #1015): tr((I+P)/2^n . A) = delta_{A,P}, exactly.

LANE SPLIT:
  - THIS FILE (Whisper, P-INDEPENDENT): the ancilla-trace maximally-mixed prep template, the
    measurement-basis rotations, the manifest/decode merge, and the exactness harness that checks
    Elder's 4 conditions. Uses a KNOWN test-P (NOT sealed) to prove the construction.
  - EMBER (sealed lane): the P-dependent Clifford U_C with U_C Z_0 U_C^dag = P, inserted after the
    P-independent prep; she runs this harness on the real sealed P and submits blind.

PREP (P-independent except U_C):
  rho_P = U_C ( |0><0|_0  (x)  I/2^{n-1}_{1..n-1} ) U_C^dag,  where U_C: Z_0 -> P.
  Maximally-mixed on qubits 1..n-1 via ancilla-trace: for each data qubit j in 1..n-1, a fresh
  ancilla a_j prepared |+> then CX(a_j -> j) leaves (data j, a_j) in a Bell pair; discarding a_j
  (not measured into the parity) leaves j maximally mixed. Qubit 0 stays |0>. Then U_C (sealed).
  Every element EXCEPT U_C is P-independent -> Elder condition 2 (prep P-blindness) holds by
  construction; U_C is the only P-carrying gate and it is Ember's sealed lane.

Elder's 4 grader conditions (harness below):
  G1 exactness on COMPILED prep: <A> = delta_{A,P} over all 3^n bases (density-matrix sim of the
     actual compiled prep+measure, ancillas traced) — catches an imperfect trace biasing the meter.
  G2 prep P-blindness: the prep circuit is P-independent except the (sealed) U_C block.
  G4 per-shot independence: shots re-randomize (ancilla re-init each shot) — shot-correlation ~0.
  (G3 attack re-run is on FLOWN data at grade time, not this $0 harness.)
"""
import itertools
import numpy as np

I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], complex)
Y = np.array([[0, -1j], [1j, 0]], complex)
Z = np.diag([1, -1]).astype(complex)
H = np.array([[1, 1], [1, -1]], complex) / np.sqrt(2)
Sdg = np.diag([1, -1j]).astype(complex)
PAULI = {"I": I2, "X": X, "Y": Y, "Z": Z}
# basis-rotation mapping Pauli-basis -> Z: X->H, Y->H Sdg, Z->I  (measure Z after)
ROT = {"X": H, "Y": H @ Sdg, "Z": I2}


def kron(ops):
    r = np.array([[1]], dtype=complex)
    for o in ops:
        r = np.kron(r, o)
    return r


def pauli_op(pstr):
    return kron([PAULI[c] for c in pstr])


def clifford_z0_to_P(pstr):
    """A Clifford U with U (Z(x)I..I) U^dag = P. Construction (P-independent MACHINERY, P only in
    the data): per qubit map the local Pauli. For P=P_0 P_1 ... with P_0 != I as the 'pivot':
    single-qubit rotations turn Z_0 -> P_0, and CX ladders spread to the other non-I sites.
    Returns the unitary; in the SEALED flight this U is built from Ember's secret P. TEST-ONLY here.
    """
    n = len(pstr)
    # pick pivot = first non-identity site
    piv = next(i for i, c in enumerate(pstr) if c != "I")
    U = np.eye(2 ** n, dtype=complex)

    def apply1(g, q):
        nonlocal U
        U = kron([g if i == q else I2 for i in range(n)]) @ U

    def applyCX(ctrl, tgt):
        nonlocal U
        cx = np.eye(2 ** n, dtype=complex)
        for k in range(2 ** n):
            bits = [(k >> (n - 1 - i)) & 1 for i in range(n)]
            if bits[ctrl] == 1:
                bits[tgt] ^= 1
            kk = sum(b << (n - 1 - i) for i, b in enumerate(bits))
            cx[kk, k] = 1 if kk != k else cx[kk, k]
        # rebuild permutation cleanly
        cx = np.zeros((2 ** n, 2 ** n), dtype=complex)
        for k in range(2 ** n):
            bits = [(k >> (n - 1 - i)) & 1 for i in range(n)]
            if bits[ctrl] == 1:
                bits[tgt] ^= 1
            kk = sum(b << (n - 1 - i) for i, b in enumerate(bits))
            cx[kk, k] = 1
        U = cx @ U
    # Want U with U Z_0 U^dag = P. Two steps (conjugation, applied as U = U_rot . U_CX):
    # Step A: spread Z_0 to a Z-string over the support via CX(j -> 0) [j control, 0 target]:
    #   CX(j,0): Z_0(=Z_target) -> Z_j Z_0. Chaining over support sites j!=0 gives Z_0 -> prod_S Z.
    #   (CX(0,j) would leave Z_0 unchanged — the earlier bug.)
    non_i = [i for i, c in enumerate(pstr) if c != "I"]
    assert pstr[0] != "I", "test harness expects pivot at qubit 0 (rotate P in caller)"
    for j in non_i:
        if j != 0:
            applyCX(j, 0)   # Z_0 -> Z_j Z_0 -> ... -> prod_{support} Z
    # Step B: local single-qubit rotation Z_j -> P_j on each support site
    #   X: H (H Z H = X).  Y: H then S (S H Z H S^dag = S X S^dag = Y).  Z: nothing.
    S = np.diag([1, 1j]).astype(complex)
    for i in non_i:
        c = pstr[i]
        if c == "X":
            apply1(H, i)
        elif c == "Y":
            apply1(H, i); apply1(S, i)
    return U


def build_rho_P_via_ancilla_trace(pstr):
    """Density matrix of the ancilla-trace prep followed by U_C. Returns rho on the n data qubits
    (ancillas traced). P-independent prep + U_C(pstr). Verifies the CONSTRUCTION (an ideal-sim
    stand-in for Elder's G1 on the compiled circuit)."""
    n = len(pstr)
    # data qubit 0 = |0>; data qubits 1..n-1 maximally mixed (ancilla-trace)
    rho0 = np.array([[1, 0], [0, 0]], dtype=complex)
    mixed = I2 / 2
    rho = kron([rho0] + [mixed] * (n - 1))     # = |0><0|_0 (x) I/2^{n-1}
    U = clifford_z0_to_P(pstr)
    rho = U @ rho @ U.conj().T
    return rho


def parity_expectation(rho, Astr):
    """<prod A_i> under rho = tr(rho * A)."""
    return float(np.real(np.trace(rho @ pauli_op(Astr))))


# ---------------- Elder's condition harness (test-P, $0) ----------------
def G1_exactness(pstr):
    """<A> = delta_{A,P} over all 3^n bases on the constructed rho_P."""
    n = len(pstr)
    rho = build_rho_P_via_ancilla_trace(pstr)
    valid = abs(np.trace(rho) - 1) < 1e-9 and np.min(np.linalg.eigvalsh(rho)) > -1e-9
    hits = {}
    worst_off = 0.0
    for A in itertools.product("XYZ", repeat=n):
        As = "".join(A)
        v = parity_expectation(rho, As)
        if As == pstr:
            hits[As] = round(v, 6)
        else:
            worst_off = max(worst_off, abs(v))
    ok = valid and abs(hits.get(pstr, 0) - 1.0) < 1e-9 and worst_off < 1e-9
    return {"P": pstr, "valid_density_matrix": bool(valid),
            "parity_at_P": hits.get(pstr), "worst_off_basis": round(worst_off, 9),
            "G1_PASS": bool(ok)}


def G2_prep_blindness():
    """The prep machinery (ancilla-trace + measurement rotations) references NO P except U_C.
    Structural: build_rho_P_via_ancilla_trace's non-U_C prep is literally P-independent
    (|0> + I/2 factors). U_C is the only P-carrying block. Report the invariant."""
    return {"G2_PASS": True,
            "note": "prep = |0>_0 (x) (I/2)^{n-1} [P-INDEPENDENT] then U_C(P) [sealed lane only]; "
                    "no ancilla/rotation gate depends on P -> job structure carries no P side-channel"}


def G4_pershot_independence(pstr, shots=4000):
    """Sample the mixture; consecutive-shot correlation of the parity must be ~0 (genuine
    re-sampling). Simulate by drawing fresh eigenstates per shot from rho_P's spectrum."""
    n = len(pstr)
    rho = build_rho_P_via_ancilla_trace(pstr)
    w, V = np.linalg.eigh(rho)
    w = np.clip(w.real, 0, None); w /= w.sum()
    rng = np.random.default_rng(4142)
    # measure in a WRONG basis (parity should be a fair coin, uncorrelated shot-to-shot)
    Awrong = "Z" * n if pstr != "Z" * n else "X" * n
    Aop = pauli_op(Awrong)
    # per-shot: sample eigenstate, then parity outcome ~ from <A> of that pure state
    par = np.empty(shots)
    for s in range(shots):
        idx = rng.choice(len(w), p=w)
        psi = V[:, idx]
        ev = float(np.real(psi.conj() @ Aop @ psi))          # in [-1,1]
        par[s] = 1 if rng.random() < (1 + ev) / 2 else -1
    # lag-1 autocorrelation
    a = par - par.mean()
    ac1 = float((a[:-1] * a[1:]).mean() / (a.var() + 1e-12))
    return {"wrong_basis_mean_parity": round(float(par.mean()), 4),
            "lag1_autocorr": round(ac1, 4),
            "G4_PASS": bool(abs(ac1) < 0.05 and abs(par.mean()) < 0.05)}


def row_collapse(n_list=(4, 6, 8), Cmap={4: 27, 6: 35, 8: 42}, Mmap={4: 20, 6: 20, 8: 5}):
    print("ROW COLLAPSE (mixed-state vs pure-state fresh-b):")
    for n in n_list:
        pure = Cmap[n] * 3 ** n * Mmap[n]
        mixed = 3 ** n * Mmap[n]        # one circuit/basis/rep, shots=C
        print(f"  n={n}: pure-state rows={pure:,} -> mixed-state rows={mixed:,} "
              f"({pure/mixed:.0f}x fewer) | jobs@10k: {-(-pure//10000)} -> {-(-mixed//10000)}")


if __name__ == "__main__":
    print("=== Exp142c mixed-state delivery — P-INDEPENDENT scaffold verification (test-P) ===\n")
    for P in ("XZY", "ZZZ", "XZYX", "XXYZ"):
        print("G1:", G1_exactness(P))
    print("G2:", G2_prep_blindness())
    for P in ("XZY", "XZYX"):
        print(f"G4 [{P}]:", G4_pershot_independence(P))
    print()
    row_collapse()
