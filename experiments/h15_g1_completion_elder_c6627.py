#!/usr/bin/env python3
"""H15 G1 COMPLETION (Elder C6627, theorem seat) -- the analytic derivation, verified.

Closes the two G1 remainders (prereg STATUS row, coordination#12402):
  (1) Gauss-sum/GF(2) derivation of BOTH closed forms:
        quantum ideal  p_Q(n)  = 3/4 + (2^(n-1)-1)/(2*4^n)   [global Helstrom]
        k=0 ceiling    p_C(n)  = 1/2 + (2^n-1)/4^n           [PPT-measurement SDP optimum]
  (2) Elder's INDEPENDENT dual -- derived analytically, NOT extracted from a solver:
        Y = ((2^n-2)/4^n) P_Phi,   Z = (1/2^n) P_Phi
      with the exact slack identity  Y + Z^Gamma - Delta = (2/4^n)(D - P_Phi) >= 0
      and Tr Y + Tr Z = 2(2^n-1)/4^n, matching the exact feasible primal
        E* = P_Phi + 2^(1-n)(P_sym - D)      [PT-invariant: E*^Gamma = E*]
      Matching primal/dual values pin the SDP optimum with ZERO gap -- no PSD repair,
      no rounding. Dual chain uses only E>=0, E<=I, (I-E)^Gamma>=0 (a RELAXATION of the
      full PPT constraint set, so the bound covers every PPT-feasible E a fortiori).

Everything rests on the M2 closed form (derived in docs/h15-g1-completion-elder-c6627.md):
        M2 = E_A[psi_A x psi_A] = 4^-n ( I + SWAP + 2^n P_Phi - 2 D )
with D = sum_x |xx><xx| and P_Phi the maximally-entangled projector across the copy cut.
Invariant 4-block algebra {P_Phi, D-P_Phi, S_off = P_sym - D, A_off = P_asym}:
        X = SWAP + 2^n P_Phi - 2D  has eigenvalues  (2^n-1, -1, +1, -1)  on those blocks.

This script VERIFIES every identity numerically at n=1..4 (n=4 = the load-bearing micro),
with the BRUTE ensemble average (all 2^(n(n+1)/2) matrices A, door(a) drawing convention
verbatim: upper-triangular INCL diagonal, no exclusions) as ground truth.

Usage: python3 h15_g1_completion_elder_c6627.py
"""
import itertools, json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results")
TOL = 1e-12


def brute_moments(n):
    """Ground truth: M1 = E_A[psi], M2 = E_A[psi x psi] over the FULL ensemble."""
    d = 2 ** n
    xs = np.array(list(itertools.product([0, 1], repeat=n)), dtype=np.int64)  # (d, n)
    pairs = [(i, j) for i in range(n) for j in range(i, n)]  # upper-tri INCL diagonal
    M1 = np.zeros((d, d))
    M2 = np.zeros((d * d, d * d))
    for bits in itertools.product([0, 1], repeat=len(pairs)):
        q = np.zeros(d, dtype=np.int64)
        for (i, j), b in zip(pairs, bits):
            if b:
                q += xs[:, i] * xs[:, j]  # i==j gives the linear term (x_i^2 = x_i)
        psi = ((-1.0) ** (q % 2)) / np.sqrt(d)
        M1 += np.outer(psi, psi)
        p2 = np.kron(psi, psi)
        M2 += np.outer(p2, p2)
    K = 2 ** len(pairs)
    return M1 / K, M2 / K


def analytic_ops(n):
    d = 2 ** n
    D2 = d * d
    I = np.eye(D2)
    SWAP = np.zeros((D2, D2))
    for x in range(d):
        for y in range(d):
            SWAP[y * d + x, x * d + y] = 1.0
    phi = np.zeros(D2)
    for x in range(d):
        phi[x * d + x] = 1.0 / np.sqrt(d)
    P_Phi = np.outer(phi, phi)
    D = np.zeros((D2, D2))
    for x in range(d):
        D[x * d + x, x * d + x] = 1.0
    return I, SWAP, P_Phi, D


def pt2(M, n):
    """Partial transpose on copy 2."""
    d = 2 ** n
    T = M.reshape(d, d, d, d)          # [x, y, u, v] = <x,y| M |u,v>
    return T.transpose(0, 3, 2, 1).reshape(d * d, d * d)  # swap y <-> v


def bell_basis(n):
    """Transversal Bell vectors: v_ab[(x, x^b)] = (-1)^(a.x) / sqrt(d).
    Convention beta_ab = (|0,b> + (-1)^a |1, 1^b>)/sqrt2 per qubit; (1,1) = singlet."""
    d = 2 ** n
    B = np.zeros((d * d, d * d))
    for a in range(d):
        for b in range(d):
            v = np.zeros(d * d)
            for x in range(d):
                v[x * d + (x ^ b)] = (-1.0) ** bin(a & x).count("1")
            B[:, a * d + b] = v / np.sqrt(d)
    return B


def check_n(n):
    d = 2 ** n
    N = float(d)
    D2 = d * d
    out = {"n": n}

    M1b, M2b = brute_moments(n)
    I, SWAP, P_Phi, D = analytic_ops(n)

    # (1) closed forms for the moments
    out["m1_vs_maxmix_maxdiff"] = float(np.abs(M1b - np.eye(d) / d).max())
    M2 = (I + SWAP + N * P_Phi - 2 * D) / (N * N)
    out["m2_brute_vs_closed_maxdiff"] = float(np.abs(M2b - M2).max())

    # (2) spectrum of X and the Helstrom closed form
    X = SWAP + N * P_Phi - 2 * D
    ev = np.sort(np.linalg.eigvalsh(X))
    l1_pred = 4.0 ** n + 2.0 ** n - 2.0
    out["l1_X_eig"] = float(np.abs(ev).sum())
    out["l1_X_closed"] = l1_pred
    Delta = M2b - I / D2
    p_hel_eig = 0.5 + 0.25 * np.abs(np.linalg.eigvalsh(Delta)).sum()
    p_hel_closed = 0.75 + (2.0 ** (n - 1) - 1.0) / (2.0 * 4.0 ** n)
    out["helstrom_eig"] = float(p_hel_eig)
    out["helstrom_closed"] = float(p_hel_closed)

    # (3) exact PPT primal witness E* = P_Phi + 2^(1-n) (P_sym - D)
    P_sym = (I + SWAP) / 2
    Estar = P_Phi + (2.0 / N) * (P_sym - D)
    EstarG = pt2(Estar, n)
    out["primal_pt_invariant_maxdiff"] = float(np.abs(EstarG - Estar).max())
    eE = np.linalg.eigvalsh(Estar)
    eEG = np.linalg.eigvalsh(EstarG)
    out["primal_eig_range"] = [float(eE.min()), float(eE.max())]
    out["primal_ptranspose_eig_range"] = [float(eEG.min()), float(eEG.max())]
    val_primal = float(np.trace(Estar @ Delta))
    val_closed = 2.0 * (N - 1.0) / (N * N)
    out["primal_value"] = val_primal
    out["optimum_closed"] = val_closed

    # (4) Elder's analytic dual: Y = ((N-2)/N^2) P_Phi, Z = (1/N) P_Phi
    Y = ((N - 2.0) / (N * N)) * P_Phi
    Z = (1.0 / N) * P_Phi
    slack = Y + pt2(Z, n) - Delta
    slack_pred = (2.0 / (N * N)) * (D - P_Phi)
    out["dual_slack_identity_maxdiff"] = float(np.abs(slack - slack_pred).max())
    out["dual_slack_min_eig"] = float(np.linalg.eigvalsh(slack).min())
    out["dual_value"] = float(np.trace(Y) + np.trace(Z))
    out["ceiling_closed"] = 0.5 + (2.0 ** n - 1.0) / 4.0 ** n
    out["ceiling_primal"] = 0.5 + 0.5 * val_primal
    out["ceiling_dual"] = 0.5 + 0.5 * out["dual_value"]

    # (5) transversal-Bell diagonality + outcome law
    #     P(a,b) = 4^-n [ 1 + (-1)^(a.b) + 2^n [a=0,b=0] - 2 [b=0] ]
    B = bell_basis(n)
    Mbell = B.T @ M2b @ B
    offdiag = Mbell - np.diag(np.diag(Mbell))
    out["bell_offdiag_max"] = float(np.abs(offdiag).max())
    pab = np.diag(Mbell).copy()
    pred = np.zeros(D2)
    for a in range(d):
        for b in range(d):
            dot = bin(a & b).count("1") % 2
            pred[a * d + b] = (1.0 + (-1.0) ** dot + (N if (a == 0 and b == 0) else 0.0)
                              - (2.0 if b == 0 else 0.0)) / (N * N)
    out["bell_pab_maxdiff"] = float(np.abs(pab - pred).max())
    support = {i for i in range(D2) if pab[i] > TOL}
    support_pred = {a * d + b for a in range(d) for b in range(d)
                    if (b != 0 and bin(a & b).count("1") % 2 == 0) or (a == 0 and b == 0)}
    out["support_matches"] = support == support_pred
    out["support_size"] = len(support)
    out["support_size_closed"] = (4 ** n - 2 ** n) // 2 + 1

    # (6) the three decision rules, from the outcome law
    #     Helstrom = support membership (accept iff (a,b) in support): P(acc|ALT)=1
    p_acc_null_hel = len(support_pred) / D2
    out["helstrom_via_bell"] = 0.5 * (1.0 + 1.0 - p_acc_null_hel)
    #     simple rule: accept iff a.b even -- P(acc|ALT)=1 (support subset of even a.b)
    even = {a * d + b for a in range(d) for b in range(d) if bin(a & b).count("1") % 2 == 0}
    assert support_pred <= even, "support must sit inside the even-parity set"
    out["p_acc_alt_simple"] = float(sum(pab[i] for i in even))
    out["null_accept_simple"] = len(even) / D2
    out["null_accept_simple_closed"] = 0.5 + 2.0 ** -(n + 1)
    out["p_simple"] = 0.5 * (out["p_acc_alt_simple"] + 1.0 - out["null_accept_simple"])
    out["p_simple_closed"] = 0.75 - 2.0 ** -(n + 2)
    return out


def main():
    results = []
    for n in range(1, 5):
        r = check_n(n)
        results.append(r)
        checks = [
            ("M1 = I/2^n", r["m1_vs_maxmix_maxdiff"] < TOL),
            ("M2 closed form == brute", r["m2_brute_vs_closed_maxdiff"] < TOL),
            ("|X|_1 = 4^n+2^n-2", abs(r["l1_X_eig"] - r["l1_X_closed"]) < 1e-9),
            ("Helstrom eig == closed", abs(r["helstrom_eig"] - r["helstrom_closed"]) < TOL),
            ("E* PT-invariant", r["primal_pt_invariant_maxdiff"] < TOL),
            ("E* feasible", -TOL < r["primal_eig_range"][0] and r["primal_eig_range"][1] < 1 + TOL
             and -TOL < r["primal_ptranspose_eig_range"][0] and r["primal_ptranspose_eig_range"][1] < 1 + TOL),
            ("primal == closed optimum", abs(r["primal_value"] - r["optimum_closed"]) < TOL),
            ("dual slack identity exact", r["dual_slack_identity_maxdiff"] < TOL),
            ("dual slack PSD", r["dual_slack_min_eig"] > -TOL),
            ("dual == primal (zero gap)", abs(r["dual_value"] - r["primal_value"]) < TOL),
            ("M2 Bell-diagonal", r["bell_offdiag_max"] < TOL),
            ("Bell outcome law exact", r["bell_pab_maxdiff"] < TOL),
            ("support set matches", r["support_matches"]),
            ("Helstrom == support rule", abs(r["helstrom_via_bell"] - r["helstrom_closed"]) < TOL),
            ("P(acc|ALT)=1 simple rule", abs(r["p_acc_alt_simple"] - 1.0) < TOL),
            ("simple rule closed form", abs(r["p_simple"] - r["p_simple_closed"]) < TOL),
        ]
        ok = all(c[1] for c in checks)
        r["all_checks_pass"] = ok
        print(f"n={n}: ceiling={r['ceiling_closed']:.10f}  quantum={r['helstrom_closed']:.10f}  "
              f"simple={r['p_simple_closed']:.10f}  dual gap={abs(r['dual_value']-r['primal_value']):.1e}  "
              f"-> {'ALL PASS' if ok else 'FAIL'}")
        for name, passed in checks:
            if not passed:
                print(f"   FAIL: {name}")

    # headline rows the prereg quotes
    n4 = results[3]
    print(f"\nn=4 exact fractions: ceiling 143/256 = {143/256}, quantum 391/512 = {391/512}, "
          f"simple 47/64 = {47/64}")
    print(f"n=4 gaps over ceiling: optimal {391/512 - 143/256:.10f} (105/512), "
          f"simple {47/64 - 143/256:.10f} (45/256)")
    print(f"n=2 vacuity row: simple {results[1]['p_simple_closed']} == ceiling "
          f"{results[1]['ceiling_closed']} -> gap exactly 0 (micro must be n=4)")
    art = {"card": "h15_g1_completion_elder_c6627", "cycle": "C6627",
           "dual_form": "Y=((2^n-2)/4^n)P_Phi, Z=(1/2^n)P_Phi; slack=(2/4^n)(D-P_Phi)",
           "primal_form": "E*=P_Phi+2^(1-n)(P_sym-D), PT-invariant",
           "m2_form": "M2=4^-n(I+SWAP+2^n P_Phi-2D)",
           "all_pass": all(r["all_checks_pass"] for r in results),
           "per_n": results}
    out = os.path.join(RES, "h15_g1_completion_elder_c6627.json")
    json.dump(art, open(out, "w"), indent=1)
    print(f"-> {out}")


if __name__ == "__main__":
    main()
