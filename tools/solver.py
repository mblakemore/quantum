#!/usr/bin/env python3
"""P-CCM v1.0 — THE SOLVER. All four components wired together on the stabilizer standard form.

    ①b  magic_sparsify      |H^(x)t> -> chi = 2^k product stabilizer terms, equal coefficients
    ②   gadgetize           circuit  -> (G,u),(H,v) on the t magic qubits, Heisenberg, ONCE
    ③   pauli_project       (I+P)/2 on the standard form — general Pauli, no 2^t matrices
    ④   stabilizer_estimator ||psi||^2 by median-of-means over random stabilizer states

    P^y_out(x) = 2^-u ||Pi_G psi||^2 / 2^-v ||Pi_H psi||^2                          [Eq 28]

WHAT CHANGED WITH ③. Until component ③ existed, <psi|Pi_G|psi> had to be evaluated with explicit
2^t matrices, so the solver only ran at sizes where a statevector would have done — the regime where
verification is easy and value is zero. Every step below now runs on (n,k,h,G,Gbar,Q,D,J).

THE EXACT MODE, and why it makes this gateable. Taking L = F_2^t (i.e. k = t) makes the
sparsification EXACT: Eq 35 gives |<H^t|L>|^2 = 2^t nu^(2t) / Z(F_2^t) = 1 identically, since
Z(F_2^t) = (1 + 2^-1/2)^t. So the SAME code path that will run approximately at k < t can be run
exactly at k = t and checked against a brute-force statevector. The approximation is then a
parameter, not a different program.

THE FRAME. |A> = e^{i pi/8} H S-dagger |H>, so (H S-dagger)^(x)t folds into V_y and the decomposition
never leaves the H frame it was built in. Nothing is applied to the chi terms.

Substrate: claude-fable-5, Whisper C5023.
"""
import itertools
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stabilizer_rank_kernel as ref                                        # noqa: E402
import magic_sparsify as ms                                                 # noqa: E402
import gadgetize as gd                                                      # noqa: E402
import pauli_project as pp                                                  # noqa: E402


def magic_terms(t, delta, rng, exact=False):
    """The chi terms of the H-frame decomposition, as (coeff, bitstring) with a materialiser.
    exact=True takes L = F_2^t, for which Eq 35 gives fidelity exactly 1."""
    k = t if exact else max(1, min(t, ms.choose_k(t, delta)))
    if exact:
        M = np.eye(t, dtype=np.uint8)
        Z, _ = ms.z_of_L(ms._pack(M), k)
        fid2 = 1.0
    else:
        M, k, Z, fid2, _ = ms.sparsify(t, delta, rng, max_tries=10, k=k)
    return ms.term_bitstrings(M, k), ms.coefficient(k, Z), fid2, k


def projected_norm2(bitstrings, coeff, generators):
    """||Pi_G psi||^2 for psi = coeff * SUM_a |phi_a>, EXACTLY, via O(chi^2) kernel inner products.

    Pi_G is idempotent and Hermitian, so <psi|Pi_G|psi> = ||Pi_G psi||^2 and each term may be
    projected independently — which is the whole point of the decomposition."""
    projected = []
    for x in bitstrings:
        st = ms.term_stabstate(x)
        res, p = pp.project_group(st, generators)
        if res is not None:
            projected.append((2.0 ** (-p / 2), st))
    tot = 0j
    for fa, sa in projected:
        for fb, sb in projected:
            tot += fa * fb * ref.triple_to_complex(ref.inner_product(sa, sb))
    return float((abs(coeff) ** 2 * tot).real)


def _to_gen(P):
    """gadgetize.Pauli -> (kappa, alpha, beta) for pauli_project. Same i^k X^a Z^b convention."""
    return (P.k, P.a, P.b)


def solve_pout(gates, n, Qout, x, y, bitstrings, coeff):
    """P^y_out(x) entirely on the standard form."""
    build, t = gd.gadgetize(gates, n)
    pre = [g for j in range(t) for g in (("SDG", n + j), ("H", n + j))]     # |A> = e^{i pi/8} H S' |H>
    V = pre + build(y)
    num_gens = [gd.pauli_Z(n + t, q, x[i]) for i, q in enumerate(Qout)] + \
               [gd.pauli_Z(n + t, n + j, y[j]) for j in range(t)]
    den_gens = [gd.pauli_Z(n + t, n + j, y[j]) for j in range(t)]
    G, u = gd.heisenberg_reduce(V, n, t, num_gens)
    H, v = gd.heisenberg_reduce(V, n, t, den_gens)
    num = 2.0 ** (-u) * projected_norm2(bitstrings, coeff, [_to_gen(P) for P in G])
    den = 2.0 ** (-v) * projected_norm2(bitstrings, coeff, [_to_gen(P) for P in H])
    return num, den, (num / den if abs(den) > 1e-14 else float("nan"))


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
            print(f"    {'PASS' if ok else 'FAIL':>4}  {name:<46} {detail}")

    print("  S0 — L = F_2^t makes the decomposition EXACT (Eq 35 gives fidelity 1)")
    worst0 = 0.0
    for t in (2, 4, 6, 8):
        bs, co, fid2, k = magic_terms(t, 0.5, rng, exact=True)
        psi = np.zeros(2 ** t, dtype=complex)
        for xx in bs:
            psi += co * ms.term_statevector(xx)
        worst0 = max(worst0, float(np.max(np.abs(psi - ms.h_tensor(t)))))
    rec("S0 exact mode reproduces |H^(x)t>", worst0 < 1e-12, f"max |err| = {worst0:.2e}")

    print("\n  S1 — FULL SOLVER on the standard form vs brute force, EXACT mode")
    print("       no 2^t matrices anywhere on this path")
    worst1 = 0.0
    ncase = 0
    p1vals = []
    for trial in range(14):
        n = int(rng.integers(1, 4))
        nt = int(rng.integers(1, 4))
        gates = [("H", q) for q in range(n)]                    # T-sensitive, as in S2
        gates += gd.random_circuit(n, int(rng.integers(2, 6)), nt, rng) + [("H", 0)]
        _, t = gd.gadgetize(gates, n)
        bs, co, _, _ = magic_terms(t, 0.5, rng, exact=True)
        Qout = [0]
        xx = (int(rng.integers(2)),)
        want = gd.brute_force_pout(gates, n, Qout, xx)
        p1vals.append(want)
        for y in itertools.product([0, 1], repeat=t):
            _, den, got = solve_pout(gates, n, Qout, xx, y, bs, co)
            if not math.isfinite(got):
                continue
            ncase += 1
            worst1 = max(worst1, abs(got - want))
    nondeg = [p for p in p1vals if abs(p - 0.5) > 0.05 and 1e-9 < p < 1 - 1e-9]
    rec("S1a VACUITY GUARD: P_out actually varies", len(nondeg) >= 3,
        f"{len(nondeg)}/{len(p1vals)} circuits non-degenerate, "
        f"P_out in [{min(p1vals):.3f}, {max(p1vals):.3f}]")
    rec("S1b solver == brute force, all y", worst1 < 1e-9,
        f"{ncase} (circuit, y) cases, max |err| = {worst1:.2e}")

    print("\n  S2 — APPROXIMATE mode: same code path at k < t, error vs its own bound")
    print("       WITH A VACUITY GUARD. The first version of this gate could not fail: random")
    print("       Clifford+T circuits on 2-3 qubits give P_out in {0, 1/2, 1} almost always, and")
    print("       P = 1/2 is protected by symmetry — the approximation scales numerator and")
    print("       denominator alike, so the RATIO is exact no matter how bad the state is. It")
    print("       reported max |err| = 0.0000 over 96 cases while testing nothing.")
    worst2 = 0.0
    bound2 = 0.0
    ncase2 = 0
    pvals = []
    for trial in range(40):
        n = int(rng.integers(1, 3))
        nt = int(rng.integers(3, 6))
        # T-SENSITIVE by construction: open and close in the X basis so the T phases show up
        # in the measured probability instead of cancelling.
        gates = [("H", q) for q in range(n)]
        gates += gd.random_circuit(n, int(rng.integers(1, 4)), nt, rng)
        gates += [("H", 0)]
        _, t = gd.gadgetize(gates, n)
        bs, co, fid2, k = magic_terms(t, 0.5, rng, exact=False)
        if k >= t:
            continue
        Qout, xx = [0], (0,)
        want = gd.brute_force_pout(gates, n, Qout, xx)
        if abs(want - 0.5) < 0.05 or want < 1e-9 or want > 1 - 1e-9:
            continue                                   # degenerate: cannot discriminate
        delta = 1.0 - fid2
        pvals.append(want)
        for y in itertools.product([0, 1], repeat=t):
            _, den, got = solve_pout(gates, n, Qout, xx, y, bs, co)
            if not math.isfinite(got):
                continue
            ncase2 += 1
            worst2 = max(worst2, abs(got - want))
        bound2 = max(bound2, math.sqrt(delta))
    spread = (max(pvals) - min(pvals)) if pvals else 0.0
    rec("S2a VACUITY GUARD: P_out actually varies", len(pvals) >= 3 and spread > 0.05,
        f"{len(pvals)} circuits, P_out in [{min(pvals):.3f}, {max(pvals):.3f}]" if pvals
        else "NO non-degenerate circuits — gate would be vacuous")
    rec("S2b approximate within sqrt(delta)", ncase2 > 0 and worst2 <= bound2 + 1e-9,
        f"{ncase2} cases, max |err| = {worst2:.4f} vs bound {bound2:.4f}")

    print("\n  S3 — the estimator ④ against the exact O(chi^2) norm, same projected terms")
    import stabilizer_estimator as se
    worst3 = 0.0
    for trial in range(4):
        n = 2
        gates = gd.random_circuit(n, 5, int(rng.integers(2, 4)), rng)
        build, t = gd.gadgetize(gates, n)
        bs, co, _, _ = magic_terms(t, 0.5, rng, exact=True)
        y = tuple(int(v) for v in rng.integers(0, 2, size=t))
        pre = [g for j in range(t) for g in (("SDG", n + j), ("H", n + j))]
        V = pre + build(y)
        den_gens = [gd.pauli_Z(n + t, n + j, y[j]) for j in range(t)]
        H, v = gd.heisenberg_reduce(V, n, t, den_gens)
        gens = [_to_gen(P) for P in H]
        terms, coeffs = [], []
        for xb in bs:
            st = ms.term_stabstate(xb)
            res, p = pp.project_group(st, gens)
            if res is not None:
                terms.append(st)
                coeffs.append(co * 2.0 ** (-p / 2))
        if not terms:
            continue
        ex = se.exact_norm2(terms, coeffs)
        xi, _ = se.estimate_norm2(terms, coeffs, t, 0.5, 0.2, rng)
        if ex > 1e-12:
            worst3 = max(worst3, abs(xi / ex - 1))
    rec("S3 estimator tracks the exact norm", worst3 < 1.5, f"max rel dev = {worst3:.3f}")

    return npass, nfail


if __name__ == "__main__":
    print("THE SOLVER — all four components on the stabilizer standard form\n")
    print("  ①b sparsify  ②gadgetize  ③pauli_project  ④estimator")
    print("  P^y_out(x) = 2^-u ||Pi_G psi||^2 / 2^-v ||Pi_H psi||^2\n")
    p, f = self_test()
    print(f"\n  {p} passed, {f} failed")
    if f == 0:
        print("  ✅ GATES PASSED — the solver runs end to end on the standard form.")
    else:
        print("  ⛔ GATES NOT PASSED.")
        sys.exit(2)
