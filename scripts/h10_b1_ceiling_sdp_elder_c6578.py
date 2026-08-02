#!/usr/bin/env python3
"""
h10_b1_ceiling_sdp_elder_c6578.py — Elder's assigned co-check for H10-B1 (the time-flip scout).

WHAT IS BEING CO-CHECKED. Whisper's B1 prereg rests on four published strategy-class ceilings for
the Box-1 discrimination game (Strömberg et al., photonic time flip):

    parallel use of U,V                                  0.88 <= p <= 0.89
    causally ordered (sequential)                        0.90 <= p <= 0.91
    process matrices / indefinite causal order           0.91 <  p <= 0.92     <- the headline bar
    quantum time flip                                    1 (exact)

The registered verdict is "flip-arm win rate above the 0.92 ceiling at >=5 sigma". **If 0.92 is
wrong, the experiment certifies nothing** — so the bars must be reproduced in-house rather than
inherited. Kill-condition 1 of the scout is exactly "in-house reproduction fails or disagrees".

WHY THIS IS AN SDP. Each class is a convex cone of process matrices, and "best strategy in class"
is a linear objective over that cone — so each ceiling is the optimum of a semidefinite program,
computed exactly rather than searched for.

CONVENTION — the VALIDATED 5-system layout of scripts/causal_game_sdp.py, reused rather than
re-derived: systems [A_I, A_O, B_I, B_O, C_I], each dim 2, total 32. The guess is read from C_I in
the X basis; the process can absorb any rotation, so a fixed readout basis costs no generality.
  CJ of a unitary U on (X_I,X_O):  |U*>> = (I (x) U.conj()) |I>>,  Tr|U*>><<U*| = 2.
  win p = (1/N) sum_pairs Tr[ W . (CJ_U (x) CJ_V (x) |c_correct><c_correct|) ],  c = +/- .
  Normalisation: Tr[W (CJ_U (x) CJ_V (x) I_C)] = 1 for every unitary pair.  Tr W = 4.

CONES — each is either constructed, taken from the validated precedent, or imposed as the literal
meaning of normalisation. NONE is restated from memory, because v1 did exactly that and it failed.
  PARALLEL   Tr_C W = rho^T_{A_I B_I} (x) I_{A_O B_O},  rho >= 0, Tr rho = 1.
             Stated on Tr_C W (not as a product) so prep and readout may share an ancilla.
  CAUSAL     W = W_A + W_B with the precedent's comb constraints for A<B<C and B<A<C.
  PROCESS    W >= 0, Tr W = 4, and normalisation imposed DIRECTLY on sampled unitary pairs.
             Necessary-only => the optimum is an UPPER BOUND on the true process ceiling, which
             is the conservative direction for a bar the flip arm must exceed. Sufficiency is
             then tested on FRESH held-out pairs the constraints never saw.

WHAT v1 GOT WRONG, kept here because the failure is the useful part: v1 used a 4-system tester
picture with the Oreshkov-Costa-Brukner conditions, which assume a TRIVIAL GLOBAL FUTURE. A
tester's measurement is not a trivial future, the cone came out too loose, and the SDP returned
process = 1.0667. A probability above 1 cannot be rounded away — the gate proved the cone wrong
instead of handing me a plausible number.

    python3 scripts/h10_b1_ceiling_sdp_elder_c6578.py --selftest
    python3 scripts/h10_b1_ceiling_sdp_elder_c6578.py            # ceilings on the Pauli subset
"""
import itertools
import json
import sys

import numpy as np
import cvxpy as cp

I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
PAULI = {"I": I2, "X": X, "Y": Y, "Z": Z}
ketII = np.array([1, 0, 0, 1], dtype=complex)      # |00> + |11>

N_SYS = 4
DIM = 2 ** N_SYS
AI, AO, BI, BO = 0, 1, 2, 3


# ---------- tensor helpers ----------
def kron_list(ops):
    out = np.array([[1.0 + 0j]])
    for o in ops:
        out = np.kron(out, o)
    return out


def _perm(order, n=N_SYS):
    """Permutation matrix taking a product written in `order` to natural 0..n-1 ordering."""
    P = np.zeros((2 ** n, 2 ** n))
    for idx in itertools.product([0, 1], repeat=n):
        src = sum(b << (n - 1 - k) for k, b in enumerate(idx))
        nat = [0] * n
        for slot, sysid in enumerate(order):
            nat[sysid] = idx[slot]
        dst = sum(b << (n - 1 - k) for k, b in enumerate(nat))
        P[dst, src] = 1
    return P


def embed_np(op, positions, n=N_SYS):
    """Place `op` (acting on len(positions) qubits, in the given order) into n systems."""
    rest = [i for i in range(n) if i not in positions]
    full = np.kron(op, np.eye(2 ** len(rest), dtype=complex))
    P = _perm(list(positions) + rest, n)
    return P @ full @ P.T


def embed_cvx(expr, positions, n=N_SYS):
    rest = [i for i in range(n) if i not in positions]
    full = cp.kron(expr, np.eye(2 ** len(rest), dtype=complex))
    P = _perm(list(positions) + rest, n)
    return P @ full @ P.T


def ptrace_np(M, trace_axes, n=N_SYS):
    keep = [i for i in range(n) if i not in trace_axes]
    T = M.reshape([2] * n + [2] * n)
    for k, ax in enumerate(sorted(trace_axes, reverse=True)):
        T = np.trace(T, axis1=ax, axis2=ax + n - k)
    d = 2 ** len(keep)
    return T.reshape(d, d)


def ptrace_cvx(expr, trace_axes, n=N_SYS):
    """Partial trace of a cvxpy expression, as an explicit linear map (no reshape tricks)."""
    keep = [i for i in range(n) if i not in trace_axes]
    dk, dt = 2 ** len(keep), 2 ** len(trace_axes)
    P = _perm(keep + list(trace_axes), n)
    out = 0
    for j in range(dt):
        S = np.zeros((dk, dk * dt), dtype=complex)
        for i in range(dk):
            S[i, i * dt + j] = 1.0
        out = out + S @ (P.T @ expr @ P) @ S.conj().T
    return out


def replace_np(M, axes, n=N_SYS):
    """_X M = (Tr_X M) (x) I_X / d_X, put back in natural ordering."""
    red = ptrace_np(M, axes, n)
    keep = [i for i in range(n) if i not in axes]
    d = 2 ** len(axes)
    return embed_np(np.kron(red, np.eye(d, dtype=complex) / d), keep + list(axes), n)


def replace_cvx(expr, axes, n=N_SYS):
    red = ptrace_cvx(expr, axes, n)
    keep = [i for i in range(n) if i not in axes]
    d = 2 ** len(axes)
    return embed_cvx(cp.kron(red, np.eye(d, dtype=complex) / d), keep + list(axes), n)


# ---------- game ----------
def cj(U):
    v = np.kron(I2, U.conj()) @ ketII
    return np.outer(v, v.conj())


def game_op(U, V):
    """G on [A_I,A_O,B_I,B_O]: U's CJ on (0,1), V's CJ on (2,3)."""
    return kron_list([cj(U), cj(V)])


def pauli_pairs():
    """The 15 Pauli pairs of the published 21 — (Y,Y) is excluded in the published set.

    Class rule (derived, matching Whisper's C5016 'odd Y-count <=> M-'): for Paulis
    U^T = eps_U U with eps = -1 iff U == Y, so U V^T = (eps_V/eps_U) U^T V, i.e.
    M+ <=> eps_U eps_V = +1 <=> an EVEN number of Ys in the pair.
    """
    out = []
    for a, b in itertools.product("IXYZ", repeat=2):
        if a == "Y" and b == "Y":
            continue
        ny = (a == "Y") + (b == "Y")
        out.append((f"({a},{b})", PAULI[a], PAULI[b], "M+" if ny % 2 == 0 else "M-"))
    return out


def _rand_state(d, rng):
    v = rng.normal(size=d) + 1j * rng.normal(size=d)
    return v / np.linalg.norm(v)


# ---------- cones (5-system picture) ----------
# C6578 REBUILD. v1 worked in a 4-system tester picture and applied the Oreshkov-Costa-Brukner
# process conditions, which assume a TRIVIAL GLOBAL FUTURE — but a tester's measurement lives on
# A_O/B_O, so that future is not trivial. The cone came out too loose and the SDP returned
# **process = 1.0667**. A probability above 1 is impossible, so the gates proved the cone wrong
# rather than leaving me with a plausible number. The parallel-subset-process gate caught the same
# defect independently, from a different direction.
#
# The rebuild moves to the precedent's VALIDATED 5-system layout [A_I,A_O,B_I,B_O,C_I], where the
# guess is read from C_I in the X basis and the process absorbs any rotation (so a fixed readout
# basis costs no generality). scripts/causal_game_sdp.py already validates this structure end to
# end (V1 process-vs-circuit, V2 normalisation, V4 switch wins at 1).
#
# HOW THE PROCESS TIER AVOIDS A SECOND HAND-DERIVED CONE. Rather than restate affine conditions
# from memory — the thing that just failed — the normalisation is imposed DIRECTLY as what it
# means: Tr[W (CJ_U (x) CJ_V (x) I_C)] = 1 for unitary pairs, sampled. That is a NECESSARY
# condition, so the optimum over it is an UPPER BOUND on the true process ceiling — which is the
# conservative direction for a bar the flip arm must beat. Sufficiency is then tested on FRESH
# held-out pairs the constraints never saw.
import causal_game_sdp as P                                   # validated precedent machinery

DIM5 = 32
PLUS = np.array([1, 1], dtype=complex) / np.sqrt(2)
MINUS = np.array([1, -1], dtype=complex) / np.sqrt(2)


def _rand_u(rng):
    z = (rng.normal(size=(2, 2)) + 1j * rng.normal(size=(2, 2))) / np.sqrt(2)
    q, r = np.linalg.qr(z)
    return q @ np.diag(np.diag(r) / abs(np.diag(r)))


def norm_ops(n_samp, rng):
    """[CJ_U (x) CJ_V (x) I_C] for sampled unitary pairs — the normalisation generators.

    THE SAMPLE MUST SATURATE THE SPAN. Measured C6578: the span of these operators has rank
    exactly 100 (stable from n=100 to n=800). The first attempt used 48 — UNDER-RANK — so the
    normalisation constrained only a subspace, the optimiser moved in the unconstrained directions,
    and the process tier returned 1.0665. The held-out test caught it at deviation 0.858.
    Enforcing on a spanning sample makes this equivalent to full normalisation over unitary
    channels, rather than a partial condition that merely looks like one.
    """
    ops = []
    for _ in range(n_samp):
        U, V = _rand_u(rng), _rand_u(rng)
        ops.append(kron_list([P.cj_vec(U).reshape(-1, 1) @ P.cj_vec(U).conj().reshape(1, -1),
                              P.cj_vec(V).reshape(-1, 1) @ P.cj_vec(V).conj().reshape(1, -1),
                              np.eye(2, dtype=complex)]))
    return ops


def solve_class(cls, pairs, n_norm=200, solver="SCS", seed=6578):
    rng = np.random.default_rng(seed)
    W = cp.Variable((DIM5, DIM5), hermitian=True)
    cons = [W >> 0]

    if cls == "parallel":
        # Tr_C W = rho^T_{A_I B_I} (x) I_{A_O B_O};  shared ancilla between prep and readout
        # channel is allowed, which is why this is stated on Tr_C W rather than as a product.
        rho = cp.Variable((4, 4), hermitian=True)
        blk = P.embed_cvx(cp.kron(cp.conj(rho), np.eye(4, dtype=complex)), [0, 2, 1, 3], n=4)
        cons += [rho >> 0, cp.real(cp.trace(rho)) == 1, cp.imag(cp.trace(rho)) == 0,
                 P.ptrace_cvx(W, 5, [4]) == blk]
        obj_W = W
    elif cls == "causal":
        WA = cp.Variable((DIM5, DIM5), hermitian=True)
        WB = cp.Variable((DIM5, DIM5), hermitian=True)
        cons = [WA >> 0, WB >> 0,
                cp.real(cp.trace(WA + WB)) == 4, cp.imag(cp.trace(WA + WB)) == 0]
        cons += P.comb_constraints_A(WA) + P.comb_constraints_B(WB)
        obj_W = WA + WB
    elif cls == "process":
        cons += [cp.real(cp.trace(W)) == 4, cp.imag(cp.trace(W)) == 0]
        for Gn in norm_ops(n_norm, rng):
            cons.append(cp.real(cp.trace(Gn @ W)) == 1)
        obj_W = W
    else:
        raise ValueError(cls)

    terms = [cp.real(cp.trace(P.game_op(U, V, PLUS if lab == "M+" else MINUS) @ obj_W))
             for _, U, V, lab in pairs]
    prob = cp.Problem(cp.Maximize(sum(terms) / len(pairs)), cons)
    prob.solve(solver=solver, verbose=False)
    Wval = obj_W.value if cls != "causal" else (WA.value + WB.value)
    return prob.value, prob.status, Wval


def heldout_normalisation(Wval, n=25, seed=999):
    """Largest deviation of Tr[W G] from 1 on unitary pairs the constraints NEVER saw.

    This is the sufficiency test. If a sampled-normalisation cone is under-constrained, the
    optimiser will exploit exactly the directions it was not shown, and those show up here.
    """
    rng = np.random.default_rng(seed)
    worst = 0.0
    for Gn in norm_ops(n, rng):
        worst = max(worst, abs(np.real(np.trace(Gn @ Wval)) - 1))
    return worst


# ---------- validation ----------
def selftest():
    """Every gate exists because the matching mistake returns a NUMBER, not an error."""
    rng = np.random.default_rng(6578)
    ok = True

    def check(name, cond, detail=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}{'  ' + detail if detail else ''}")
        if not cond:
            ok = False

    pairs = pauli_pairs()
    check("game set: 15 Pauli pairs, 9 M+ / 6 M-",
          len(pairs) == 15 and sum(p[3] == "M+" for p in pairs) == 9)

    # G1 the TIME FLIP wins with certainty, by direct simulation, independent of every SDP.
    worst = 1.0
    for _, U, V, lab in pairs:
        for _ in range(4):
            t = _rand_state(2, rng)
            b0, b1 = (U @ V.T) @ t, (U.T @ V) @ t
            pl = float(np.real((b0 + b1).conj() @ (b0 + b1))) / 4
            mi = float(np.real((b0 - b1).conj() @ (b0 - b1))) / 4
            worst = min(worst, pl if lab == "M+" else mi)
    check("time-flip arm wins p == 1 on every pair", abs(worst - 1) < 1e-9,
          f"min {worst:.12f}")

    # G2 the precedent's switch process is a KNOWN POSITIVE for the process cone.
    Wsw = P.build_w_switch()
    check("switch W: PSD, Tr == 4", np.linalg.eigvalsh(Wsw).min() > -1e-9
          and abs(np.trace(Wsw).real - 4) < 1e-9)
    check("switch W satisfies sampled normalisation (known positive for process cone)",
          heldout_normalisation(Wsw, n=20, seed=17) < 1e-9,
          f"worst dev {heldout_normalisation(Wsw, n=20, seed=17):.2e}")

    # G3 solve all three tiers; NOTHING may exceed 1 -- v1 returned 1.0667 here.
    vals, Ws = {}, {}
    for cls in ("parallel", "causal", "process"):
        v, st, Wv = solve_class(cls, pairs)
        vals[cls], Ws[cls] = v, Wv
        print(f"        {cls:9s} = {v:.6f}   ({st})")
    check("no tier exceeds probability 1", all(v <= 1 + 1e-4 for v in vals.values()))

    # G4 held-out normalisation on the OPTIMISER'S OWN solution -- catches an under-constrained
    #    cone by testing the directions the constraints never saw.
    for cls in ("parallel", "causal", "process"):
        d = heldout_normalisation(Ws[cls])
        check(f"{cls}: held-out normalisation of the SOLUTION", d < 1e-5, f"worst dev {d:.2e}")

    # G5 class inclusion, solved not asserted.
    check("ordering parallel <= causal <= process",
          vals["parallel"] <= vals["causal"] + 1e-4 <= vals["process"] + 2e-4)

    print("SELFTEST", "PASS" if ok else "FAIL")
    return (0 if ok else 1), vals


def main():
    rc, vals = selftest()
    print()
    print("H10-B1 strategy-class ceilings -- PAULI SUBSET ONLY (15 of the published 21)")
    print("=" * 74)
    for k, v in vals.items():
        print(f"  {k:10s} = {v:.6f}")
    print()
    print("Published bars for the FULL 21-pair game:")
    print("  parallel 0.88-0.89 | causal 0.90-0.91 | process 0.91-0.92 | flip 1 (exact)")
    print("NOT COMPARABLE to those bars: the 6 non-Pauli MII pairs are absent from the repo")
    print("(names only in results/h10_b1_game_reproduction_c5016.json; generator uncommitted).")
    print(json.dumps({"pauli_subset_ceilings": vals, "n_pairs": 15,
                      "process_is_upper_bound": True}, indent=1))
    return rc


if __name__ == "__main__":
    sys.exit(main())
