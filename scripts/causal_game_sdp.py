#!/usr/bin/env python3
"""
Causal discrimination game — SDP reproduction of Araujo et al., NJP 17, 102001 (2015).

Reproduces:
  (1) p_sep ~ 0.9288 for the continuous-measure Chiribella witness (their Eq. 84)
  (2) p_sep ~ 0.8690 for the finite 10-unitary game with SDP-optimized input
      distribution (their Eq. H2/H3), RECOVERING the optimal q_ij they omitted.

Scenario (their Fig. 3 / Eq. 27): parties A, B (qubit in+out) and Charlie (qubit in,
trivial out). System order [A_I, A_O, B_I, B_O, C_I], all dim 2, total 32.
Causally separable cone: W = W_A + W_B, W_X >= 0, W_A a comb for A<B<C, W_B for B<A<C
(their Eqs. 19-27). Comb conditions (trace-and-replace hierarchy, Eqs. 20-21):
  A<B<C:  Tr_C W  = (Tr_{C,BO} W)/2 (x) 1_BO      [no dependence of the past on B_O]
          Tr_{C,BO,BI} W = (Tr_{C,BO,BI,AO} W)/2 (x) 1_AO
CJ convention (their Eq. 79): party applying unitary U contributes |U*>><<U*| on
(X_I, X_O) with |U*>> = (1 (x) U.conj()) |I>>. Charlie: |+-><+-| on C_I.
The witness picks the CORRECT outcome: + for commuting, - for anticommuting.

Validation gates (all must pass before trusting the headline numbers):
  V1 process-vs-circuit: Tr[W_switch G_{UA,UB,c}] == direct circuit simulation
  V2 Tr W_switch = 4;  maximally mixed process gives p_succ = 0.5 on any game
  V3 Clifford-24 twirl == Monte-Carlo Haar twirl (2-design exactness)
  V4 switch wins every game with p = 1
  V5 Pauli-only game: causal bound = 1.0 (no game exists)  [their footnote 8]
  V6 primal at recovered q* == minimax dual value (strong duality cross-check)
Targets: |p_haar - 0.9288| <= 0.001 and |p_finite - 0.8690| <= 0.001.
"""
import itertools
import json
import sys

import numpy as np
import cvxpy as cp

np.set_printoptions(precision=6, suppress=True)
I2 = np.eye(2)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
ketII = np.zeros(4, dtype=complex)
ketII[0] = ketII[3] = 1.0  # |00>+|11>
PLUS = np.array([1, 1], dtype=complex) / np.sqrt(2)
MINUS = np.array([1, -1], dtype=complex) / np.sqrt(2)

N_SYS = 5  # [A_I, A_O, B_I, B_O, C_I]
DIM = 2 ** N_SYS


# ---------- tensor helpers ----------
def kron_list(ops):
    out = np.array([[1.0 + 0j]])
    for o in ops:
        out = np.kron(out, o)
    return out


def perm_matrix(order, n):
    """P maps a state written in system-ordering `order` to natural ordering 0..n-1.
    order[k] = the system index occupying slot k of the source tensor product."""
    d = 2 ** n
    P = np.zeros((d, d))
    for src in range(d):
        bits = [(src >> (n - 1 - k)) & 1 for k in range(n)]  # slot k bit
        dst_bits = [0] * n
        for k, sysidx in enumerate(order):
            dst_bits[sysidx] = bits[k]
        dst = 0
        for b in dst_bits:
            dst = (dst << 1) | b
        P[dst, src] = 1.0
    return P


def embed_np(op, positions, n=N_SYS):
    """Numpy: place operator on `positions`, identity elsewhere."""
    rest = [s for s in range(n) if s not in positions]
    big = np.kron(op, np.eye(2 ** len(rest)))
    P = perm_matrix(list(positions) + rest, n)
    return P @ big @ P.T


def embed_cvx(expr, positions, n=N_SYS):
    rest = [s for s in range(n) if s not in positions]
    big = cp.kron(expr, np.eye(2 ** len(rest))) if rest else expr
    P = perm_matrix(list(positions) + rest, n)
    return P @ big @ P.T


def ptrace_np(M, keep, n=N_SYS):
    """Partial trace keeping systems `keep` (natural order)."""
    dims = [2] * n
    T = M.reshape(dims + dims)
    traced = [s for s in range(n) if s not in keep]
    for s in sorted(traced, reverse=True):
        T = np.trace(T, axis1=s, axis2=s + (T.ndim // 2))
    return T.reshape(2 ** len(keep), 2 ** len(keep))


def ptrace_cvx(expr, n_axes, trace_axes):
    """cvxpy: trace out axes (list) from expr living on n_axes qubit systems."""
    dims = [2] * n_axes
    out = expr
    for ax in sorted(trace_axes, reverse=True):
        out = cp.partial_trace(out, dims, axis=ax)
        dims = dims[:ax] + dims[ax + 1:]
    return out


# ---------- CJ / switch / games ----------
def cj_vec(U):
    return np.kron(I2, U.conj()) @ ketII  # |U*>>


def game_op(UA, UB, charlie_ket):
    a = cj_vec(UA)
    b = cj_vec(UB)
    return kron_list([np.outer(a, a.conj()), np.outer(b, b.conj()),
                      np.outer(charlie_ket, charlie_ket.conj())])


def build_w_switch(psi=np.array([1, 0], dtype=complex)):
    """Pure switch on [A_I,A_O,B_I,B_O,C,T], control |+> start (branch 0: A first),
    then trace target T."""
    t = np.zeros((2,) * 6, dtype=complex)
    for x in range(2):
        for m in range(2):
            for nn in range(2):
                # branch c=0: A_I=psi, A_O=B_I=m, B_O=T=n
                t[x, m, m, nn, 0, nn] += psi[x]
                # branch c=1: B_I=psi(x), B_O=A_I=m, A_O=T=n
                t[m, nn, x, m, 1, nn] += psi[x]
    v = t.reshape(64) / np.sqrt(2)
    Wfull = np.outer(v, v.conj())
    # trace T (system 5 of 6)
    T6 = Wfull.reshape([2] * 6 + [2] * 6)
    W = np.trace(T6, axis1=5, axis2=11).reshape(32, 32)
    return W


def circuit_prob(UA, UB, charlie_ket, psi=np.array([1, 0], dtype=complex)):
    """Direct simulation: control |+>, branch |0>: A first."""
    out0 = np.kron(np.array([1, 0]), UB @ UA @ psi)
    out1 = np.kron(np.array([0, 1]), UA @ UB @ psi)
    state = (out0 + out1) / np.sqrt(2)
    proj = np.kron(np.outer(charlie_ket, charlie_ket.conj()), I2)
    return np.real(state.conj() @ proj @ state)


# ---------- Clifford 2-design twirl ----------
def clifford_group():
    H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
    S = np.array([[1, 0], [0, 1j]], dtype=complex)

    def canon(U):
        idx = np.argmax(np.abs(U) > 1e-9)
        ph = U.flat[idx] / abs(U.flat[idx])
        V = U / ph
        # +0.0 collapses -0.0 vs 0.0 (distinct bytes, equal value)
        return (np.round(V.real, 6) + 0.0).tobytes() + (np.round(V.imag, 6) + 0.0).tobytes()

    group = {canon(I2): I2}
    frontier = [I2]
    while frontier:
        nxt = []
        for g in frontier:
            for gen in (H, S):
                cand = gen @ g
                key = canon(cand)
                if key not in group:
                    group[key] = cand
                    nxt.append(cand)
        frontier = nxt
    return list(group.values())


def haar_twirl_projector():
    """EXACT Haar twirl for the rep V(U) = U (x) Ubar (x) U (x) Ubar on 4 qubits.

    The two-sided conjugation E[V K V^dag] involves balanced degree-(4,4) moments,
    so no finite 2- or 3-design (e.g. the 24-element Clifford group) is exact.
    Instead: the twirl is the ORTHOGONAL projection (Hilbert-Schmidt) onto the
    commutant {M : [M, V(U)] = 0 for all U} — self-adjoint idempotent = orthogonal
    projector. Compute the commutant as the joint nullspace of commutator
    superoperators for a handful of generic SU(2) elements (global phases cancel
    in V, so SU(2) suffices for U(2))."""
    rng = np.random.default_rng(123)
    rows = []
    d = 16
    for _ in range(8):
        g = np.linalg.qr(rng.normal(size=(2, 2)) + 1j * rng.normal(size=(2, 2)))[0]
        g = g / np.sqrt(np.linalg.det(g).astype(complex))
        V = kron_list([g, g.conj(), g, g.conj()])
        # superoperator of M -> V M - M V  acting on vec(M)
        rows.append(np.kron(V, np.eye(d)) - np.kron(np.eye(d), V.T))
    A = np.vstack(rows)
    _, s, Vh = np.linalg.svd(A)
    ns = Vh[np.sum(s > 1e-10):]  # right-singular vectors with zero singular value
    print(f"  commutant dimension: {ns.shape[0]}")
    return ns  # rows: orthonormal basis of vec'd commutant


def twirl4_exact(K, ns_basis):
    v = K.reshape(-1)
    coeff = ns_basis.conj() @ v
    return (ns_basis.T @ coeff).reshape(K.shape)


# ---------- causal cone constraints ----------
def comb_constraints_A(W):
    """A<B<C comb on [A_I,A_O,B_I,B_O,C]=[0,1,2,3,4]."""
    c = []
    lhs = ptrace_cvx(W, 5, [4])                       # on [0,1,2,3]
    D = ptrace_cvx(W, 5, [3, 4]) / 2                  # on [0,1,2]
    c.append(lhs == cp.kron(D, I2))
    lhs2 = ptrace_cvx(W, 5, [2, 3, 4])                # on [0,1]
    E = ptrace_cvx(W, 5, [1, 2, 3, 4]) / 2            # on [0]
    c.append(lhs2 == cp.kron(E, I2))
    return c


def comb_constraints_B(W):
    """B<A<C: swap roles of (A_I,A_O)<->(B_I,B_O)."""
    c = []
    lhs = ptrace_cvx(W, 5, [4])                       # on [0,1,2,3]
    Dp = ptrace_cvx(W, 5, [1, 4]) / 2                 # on [0,2,3] (A_O traced)
    c.append(lhs == embed_cvx(Dp, [0, 2, 3], n=4))
    lhs2 = ptrace_cvx(W, 5, [0, 1, 4])                # on [2,3]
    Ep = ptrace_cvx(W, 5, [0, 1, 3, 4]) / 2           # on [2]
    c.append(lhs2 == cp.kron(Ep, I2))
    return c


def primal_causal_value(G, solver="CLARABEL"):
    WA = cp.Variable((DIM, DIM), hermitian=True)
    WB = cp.Variable((DIM, DIM), hermitian=True)
    cons = [WA >> 0, WB >> 0, cp.real(cp.trace(WA + WB)) == 4,
            cp.imag(cp.trace(WA + WB)) == 0]
    cons += comb_constraints_A(WA)
    cons += comb_constraints_B(WB)
    prob = cp.Problem(cp.Maximize(cp.real(cp.trace(G @ (WA + WB)))), cons)
    prob.solve(solver=solver)
    return prob.value, prob.status


def dual_witness_terms_A(L1, L2):
    """F_a^dag(L1) + F_b^dag(L2) for order A<B<C.
    L1 on [0,1,2,3] (16x16), L2 on [0,1] (4x4)."""
    t1 = embed_cvx(L1, [0, 1, 2, 3]) \
        - embed_cvx(ptrace_cvx(L1, 4, [3]) / 2, [0, 1, 2])
    t2 = embed_cvx(L2, [0, 1]) \
        - embed_cvx(ptrace_cvx(L2, 2, [1]) / 2, [0])
    return t1 + t2


def dual_witness_terms_B(L1, L2):
    """Order B<A<C. L1 on [0,2,3] (A_O-traced version, 8x8), L2 on [2] (2x2)...
    Careful: dual var for constraint (a') lives on [0,1,2,3] like before; the
    replaced system is A_O (pos 1). Constraint (b') lives on [2,3], replaced A... no:
    (b'): Tr_{0,1,4} W = E' (x) 1_{B_O}, E' on [2]. Dual L2' on [2,3]."""
    t1 = embed_cvx(L1, [0, 1, 2, 3]) \
        - embed_cvx(ptrace_cvx(L1, 4, [1]) / 2, [0, 2, 3])
    t2 = embed_cvx(L2, [2, 3]) \
        - embed_cvx(ptrace_cvx(L2, 2, [1]) / 2, [2])
    return t1 + t2


def minimax_optimal_game(pairs_c, pairs_a, unitaries, solver="CLARABEL"):
    """min over input distribution q of the causal max-success (their Eq. H2).
    Returns p_sep, q_c*, q_a*."""
    Gc = [game_op(unitaries[i], unitaries[j], PLUS) for (i, j) in pairs_c]
    Ga = [game_op(unitaries[i], unitaries[j], MINUS) for (i, j) in pairs_a]

    qc = cp.Variable(len(pairs_c), nonneg=True)
    qa = cp.Variable(len(pairs_a), nonneg=True)
    p = cp.Variable()
    G = sum(qc[k] * Gc[k] for k in range(len(Gc))) \
        + sum(qa[k] * Ga[k] for k in range(len(Ga)))

    LA1 = cp.Variable((16, 16), hermitian=True)
    LA2 = cp.Variable((4, 4), hermitian=True)
    LB1 = cp.Variable((16, 16), hermitian=True)
    LB2 = cp.Variable((4, 4), hermitian=True)

    S_A = (p / 4) * np.eye(DIM) - G - dual_witness_terms_A(LA1, LA2)
    S_B = (p / 4) * np.eye(DIM) - G - dual_witness_terms_B(LB1, LB2)
    cons = [S_A >> 0, S_B >> 0, cp.sum(qc) + cp.sum(qa) == 1]
    prob = cp.Problem(cp.Minimize(p), cons)
    prob.solve(solver=solver)
    return prob.value, qc.value, qa.value, prob.status


def main():
    results = {}
    print("Building exact Haar twirl projector (commutant of U x Ubar x U x Ubar):")
    ns_basis = haar_twirl_projector()

    # ---------- V1/V2: switch process vs direct circuit ----------
    W_switch = build_w_switch()
    results["trace_W_switch"] = float(np.real(np.trace(W_switch)))
    print(f"V2 Tr[W_switch] = {np.trace(W_switch).real:.6f} (expect 4)")
    rng = np.random.default_rng(7)
    max_err = 0.0
    for _ in range(40):
        A_r = np.linalg.qr(rng.normal(size=(2, 2)) + 1j * rng.normal(size=(2, 2)))[0]
        B_r = np.linalg.qr(rng.normal(size=(2, 2)) + 1j * rng.normal(size=(2, 2)))[0]
        for ket in (PLUS, MINUS):
            p_pm = np.real(np.trace(W_switch @ game_op(A_r, B_r, ket)))
            p_ci = circuit_prob(A_r, B_r, ket)
            max_err = max(max_err, abs(p_pm - p_ci))
    results["V1_process_vs_circuit_max_err"] = max_err
    print(f"V1 process-matrix vs circuit max |dp| over 40 random pairs: {max_err:.2e}")
    assert max_err < 1e-9, "CJ convention mismatch!"

    # ---------- V3: twirl exactness ----------
    P_comm = np.diag([1, 0, 0, 1]).astype(complex)  # E_theta |D*>><<D*|
    K_c = np.kron(P_comm, P_comm)
    K_a = np.kron(np.outer(cj_vec(X), cj_vec(X).conj()),
                  np.outer(cj_vec(Z), cj_vec(Z).conj()))
    T_c = twirl4_exact(K_c, ns_basis)
    T_a = twirl4_exact(K_a, ns_basis)
    acc = np.zeros_like(K_c)
    n_mc = 20000
    for _ in range(n_mc):
        g = np.linalg.qr(rng.normal(size=(2, 2)) + 1j * rng.normal(size=(2, 2)))[0]
        G4 = kron_list([g, g.conj(), g, g.conj()])
        acc += G4 @ K_c @ G4.conj().T
    mc_err = np.linalg.norm(acc / n_mc - T_c)
    results["V3_twirl_vs_mc_frobenius"] = float(mc_err)
    print(f"V3 exact commutant twirl vs {n_mc}-sample Haar MC (Frobenius): {mc_err:.4f} "
          f"(expect ~O(1/sqrt(N)) ~ 0.01)")
    # twirl must be idempotent and preserve trace
    print(f"V3b idempotency |T(T(K))-T(K)|: "
          f"{np.linalg.norm(twirl4_exact(T_c, ns_basis) - T_c):.2e}; "
          f"trace preserved: {np.trace(K_c).real:.4f} -> {np.trace(T_c).real:.4f}")

    # ---------- Haar-measure witness (Eq. 84 target 0.9288) ----------
    G_haar = 0.5 * np.kron(T_c, np.outer(PLUS, PLUS.conj())) \
        + 0.5 * np.kron(T_a, np.outer(MINUS, MINUS.conj()))
    p_switch_haar = float(np.real(np.trace(G_haar @ W_switch)))
    p_mixed = float(np.real(np.trace(G_haar @ (np.eye(DIM) / 8))))
    results["V4_switch_haar"] = p_switch_haar
    results["V2b_maximally_mixed_haar"] = p_mixed
    print(f"V4 switch success on Haar witness: {p_switch_haar:.6f} (expect 1)")
    print(f"V2b maximally-mixed process success: {p_mixed:.6f} (expect 0.5)")

    p_haar, status = primal_causal_value(G_haar)
    results["p_sep_haar"] = float(p_haar)
    print(f"\n*** p_sep (Haar/continuous witness) = {p_haar:.6f} "
          f"[{status}] — paper Eq.(84): 0.9288 ***")

    # ---------- finite 10-unitary set ----------
    U_set = [I2, X, Y, Z,
             (X + Y) / np.sqrt(2), (X - Y) / np.sqrt(2),
             (X + Z) / np.sqrt(2), (X - Z) / np.sqrt(2),
             (Y + Z) / np.sqrt(2), (Y - Z) / np.sqrt(2)]
    names = ["1", "X", "Y", "Z", "(X+Y)/r2", "(X-Y)/r2",
             "(X+Z)/r2", "(X-Z)/r2", "(Y+Z)/r2", "(Y-Z)/r2"]
    pairs_c, pairs_a = [], []
    for i, j in itertools.product(range(10), repeat=2):
        comm = np.linalg.norm(U_set[i] @ U_set[j] - U_set[j] @ U_set[i])
        anti = np.linalg.norm(U_set[i] @ U_set[j] + U_set[j] @ U_set[i])
        if comm < 1e-9:
            pairs_c.append((i, j))
        elif anti < 1e-9:
            pairs_a.append((i, j))
    print(f"\nFinite set: {len(pairs_c)} commuting ordered pairs, "
          f"{len(pairs_a)} anticommuting ordered pairs")
    results["n_pairs_commuting"] = len(pairs_c)
    results["n_pairs_anticommuting"] = len(pairs_a)

    # V5: Pauli-only game — bound must hit 1 (footnote 8: no game exists)
    pauli_c = [(i, i) for i in (1, 2, 3)]
    pauli_a = [(i, j) for i in (1, 2, 3) for j in (1, 2, 3) if i != j]
    G_pauli = sum(game_op(U_set[i], U_set[j], PLUS) for i, j in pauli_c) / (2 * len(pauli_c)) \
        + sum(game_op(U_set[i], U_set[j], MINUS) for i, j in pauli_a) / (2 * len(pauli_a))
    p_pauli, _ = primal_causal_value(G_pauli)
    results["V5_p_sep_pauli_only"] = float(p_pauli)
    print(f"V5 Pauli-only game causal bound: {p_pauli:.6f} (expect 1.0 — no game)")

    # ---------- minimax: optimal q_ij (Eq. H2/H3 target 0.8690) ----------
    p_fin, qc_v, qa_v, status = minimax_optimal_game(pairs_c, pairs_a, U_set)
    results["p_sep_finite_optimal"] = float(p_fin)
    print(f"\n*** p_sep (finite 10-set, optimal q) = {p_fin:.6f} "
          f"[{status}] — paper Eq.(H3): 0.8690 ***")

    # V6 cross-check: primal at recovered q*
    G_star = sum(qc_v[k] * game_op(U_set[i], U_set[j], PLUS)
                 for k, (i, j) in enumerate(pairs_c)) \
        + sum(qa_v[k] * game_op(U_set[i], U_set[j], MINUS)
              for k, (i, j) in enumerate(pairs_a))
    p_primal_star, _ = primal_causal_value(G_star)
    results["V6_primal_at_qstar"] = float(p_primal_star)
    print(f"V6 primal at q*: {p_primal_star:.6f} (must equal minimax value)")
    p_switch_star = float(np.real(np.trace(G_star @ W_switch)))
    results["V4b_switch_at_qstar"] = p_switch_star
    print(f"V4b switch success at q*: {p_switch_star:.6f} (expect 1)")

    # the recovered optimal distribution
    qmap_c = {f"({names[i]},{names[j]})": round(float(qc_v[k]), 6)
              for k, (i, j) in enumerate(pairs_c) if qc_v[k] > 1e-5}
    qmap_a = {f"({names[i]},{names[j]})": round(float(qa_v[k]), 6)
              for k, (i, j) in enumerate(pairs_a) if qa_v[k] > 1e-5}
    results["q_star_commuting"] = qmap_c
    results["q_star_anticommuting"] = qmap_a
    results["q_star_commuting_class_weight"] = float(np.sum(qc_v))
    results["q_star_anticommuting_class_weight"] = float(np.sum(qa_v))
    print(f"\nOptimal q* — commuting class weight {np.sum(qc_v):.4f}, "
          f"anticommuting {np.sum(qa_v):.4f}")
    print("q* commuting pairs (nonzero):")
    for k, v in sorted(qmap_c.items(), key=lambda kv: -kv[1]):
        print(f"  {k}: {v}")
    print("q* anticommuting pairs (nonzero):")
    for k, v in sorted(qmap_a.items(), key=lambda kv: -kv[1]):
        print(f"  {k}: {v}")

    # ---------- practical variants for the hardware pre-reg ----------
    # uniform over all valid ordered pairs
    G_unif = sum(game_op(U_set[i], U_set[j], PLUS) for i, j in pairs_c) \
        / (len(pairs_c) + len(pairs_a)) \
        + sum(game_op(U_set[i], U_set[j], MINUS) for i, j in pairs_a) \
        / (len(pairs_c) + len(pairs_a))
    p_unif, _ = primal_causal_value(G_unif)
    results["p_sep_uniform_all_pairs"] = float(p_unif)
    # class-balanced: 1/2 uniform-within-commuting + 1/2 uniform-within-anticommuting
    G_bal = sum(game_op(U_set[i], U_set[j], PLUS) for i, j in pairs_c) / (2 * len(pairs_c)) \
        + sum(game_op(U_set[i], U_set[j], MINUS) for i, j in pairs_a) / (2 * len(pairs_a))
    p_bal, _ = primal_causal_value(G_bal)
    results["p_sep_class_balanced_uniform"] = float(p_bal)
    print(f"\nPre-reg variants: p_sep uniform-all-pairs = {p_unif:.6f}; "
          f"class-balanced uniform = {p_bal:.6f}")
    for lbl, Gv in (("uniform", G_unif), ("balanced", G_bal)):
        results[f"switch_{lbl}"] = float(np.real(np.trace(Gv @ W_switch)))

    out = "../results/causal_game_sdp_qij.json"
    with open(out, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved {out}")

    ok_haar = abs(p_haar - 0.9288) <= 0.001
    ok_fin = abs(p_fin - 0.8690) <= 0.001
    print(f"\nGATE haar 0.9288: {'PASS' if ok_haar else 'FAIL'} ({p_haar:.6f})")
    print(f"GATE finite 0.8690: {'PASS' if ok_fin else 'FAIL'} ({p_fin:.6f})")
    return 0 if (ok_haar and ok_fin) else 1


if __name__ == "__main__":
    sys.exit(main())
