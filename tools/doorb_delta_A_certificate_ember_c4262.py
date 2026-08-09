#!/usr/bin/env python3
"""delta_A — the hardness certificate for door (b)'s unsigned Pauli shadow tomography.

Chen-Gong (arXiv:2404.19105) Theorem 3, verbatim:
    sample complexity WITHOUT quantum memory is lower bounded by  Omega(1/(eps^2 delta_A))
    and upper bounded by  O(log|A| / (eps^2 delta_A))
with
    delta_A := min_{pi in D(A)} max_{|psi>} E_{P~pi} <psi|P|psi>^2 .

WHY THIS FILE EXISTS. Elder ruled (general#7307/#7330) that door (b) does not CITE the
existence claim ("there exists a hard set A") but INSTANTIATES it: draw A in the open,
compute delta_A, publish the certificate BEFORE the seal. A small delta_A is a hard set.
delta_A depends only on A — which is PUBLIC in shadow tomography — while the seal covers
the STATE, so hardness and blindness attach to different objects and never compete.

WHAT IS ACTUALLY COMPUTABLE, stated plainly because it bounds the whole design:
    E_{P~pi} <psi|P|psi>^2  =  tr( M_pi  (rho (x) rho) ),   M_pi = E_{P~pi} P (x) P
so max over |psi> is a maximisation of a linear functional over PRODUCT states rho (x) rho.
That is NOT an eigenvalue problem — it is a best-separable-state problem, NP-hard in
general. Here it is solved by projected power iteration with restarts, which gives a
LOWER bound on the max, hence an UPPER bound on... no:

    ** DIRECTION MATTERS AND IT CUTS AGAINST US. **
    floor ~ 1/delta_A, so a LOWER bound on the floor needs an UPPER bound on delta_A,
    which needs an UPPER bound on max_psi. Power iteration gives a LOWER bound on a max.
    So iterate-and-take-the-best yields an OPTIMISTIC delta_A and an OPTIMISTIC floor.
    A certificate in the honest direction needs an upper bound on the max (e.g. an SDP
    relaxation over the symmetric subspace). NOT IMPLEMENTED HERE — see --honest note.

So this tool reports delta_A_hat (best found) as a DIAGNOSTIC, validates the machinery
against the closed-form case, and refuses to call it a certificate.
"""
import argparse, itertools, json, math
import numpy as np

I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
PAULI = {"I": I2, "X": X, "Y": Y, "Z": Z}


def pauli_matrix(label):
    M = np.array([[1]], dtype=complex)
    for ch in label:
        M = np.kron(M, PAULI[ch])
    return M


def all_labels(n):
    return ["".join(t) for t in itertools.product("IXYZ", repeat=n)]


def expectations(labels, psi):
    """<psi|P|psi> for each P, computed without materialising 4^n matrices at once."""
    out = np.empty(len(labels))
    for i, lab in enumerate(labels):
        out[i] = np.real(np.vdot(psi, pauli_matrix(lab) @ psi))
    return out


def max_over_psi(labels, dim, restarts=12, iters=400, seed=0):
    """Maximise f(psi) = mean_P <psi|P|psi>^2 by projected gradient ascent with restarts.
    Returns (best_value, best_psi). This is a LOWER bound on the true max."""
    rng = np.random.default_rng(seed)
    mats = [pauli_matrix(l) for l in labels]
    best, best_psi = -1.0, None
    for _ in range(restarts):
        psi = rng.normal(size=dim) + 1j * rng.normal(size=dim)
        psi /= np.linalg.norm(psi)
        for _ in range(iters):
            # grad of mean_P <P>^2 is mean_P 2<P> P|psi>
            g = np.zeros(dim, dtype=complex)
            for M in mats:
                Mp = M @ psi
                g += 2.0 * np.real(np.vdot(psi, Mp)) * Mp
            psi = g / np.linalg.norm(g)
        v = float(np.mean([np.real(np.vdot(psi, M @ psi)) ** 2 for M in mats]))
        if v > best:
            best, best_psi = v, psi
    return best, best_psi


def certified_upper_bound(labels, dim):
    """A RIGOROUS upper bound on delta_A, which is the direction a floor needs.

    delta_A = min_pi max_psi f(pi,psi) <= max_psi f(pi_0,psi) for ANY fixed pi_0.
    With pi_0 uniform on A:
        f(pi_0,psi) = (1/|A|) sum_P <psi|P|psi>^2 = tr( M (rho (x) rho) ),  M = (1/|A|) sum_P P(x)P.
    rho (x) rho is a state supported in the SYMMETRIC subspace, so
        max_psi tr(M rho(x)rho) <= lambda_max( Pi_sym M Pi_sym ).
    That is an eigenvalue problem — computable, and it bounds the max from ABOVE.
    Chain: delta_A <= max_psi f(pi_0,.) <= lambda_max(Pi_sym M Pi_sym) =: delta_ub.
    Hence floor >= 1/(eps^2 delta_ub) is HONEST.
    """
    d2 = dim * dim
    Mop = np.zeros((d2, d2), dtype=complex)
    for lab in labels:
        P = pauli_matrix(lab)
        Mop += np.kron(P, P)
    Mop /= len(labels)
    # symmetric-subspace projector: (I + SWAP)/2
    SW = np.zeros((d2, d2), dtype=complex)
    for i in range(dim):
        for j in range(dim):
            SW[i * dim + j, j * dim + i] = 1.0
    Pi = (np.eye(d2) + SW) / 2.0
    Msym = Pi @ Mop @ Pi
    lam = float(np.max(np.linalg.eigvalsh((Msym + Msym.conj().T) / 2)))
    return lam


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--M", type=int, default=None,
                    help="subset size; default 2^n (the saturating size)")
    ap.add_argument("--seed", type=int, default=4262)
    ap.add_argument("--restarts", type=int, default=12)
    args = ap.parse_args()

    n, dim = args.n, 2 ** args.n
    labs = all_labels(n)
    ident = "I" * n

    print(f"delta_A DIAGNOSTIC — n={n}, dim={dim}, |P_n|={len(labs)}")

    # ---- validation against the closed form, which is the only thing here that is certain.
    # For A = P_n and pi uniform: sum_P <psi|P|psi>^2 = 2^n tr(rho^2) = 2^n for pure psi,
    # so the mean is 2^n/4^n = 1/2^n for EVERY psi — the max is attained trivially.
    v_full, _ = max_over_psi(labs, dim, restarts=3, iters=60, seed=args.seed)
    closed = 1.0 / (2 ** n)
    ok = abs(v_full - closed) < 1e-6
    print(f"  [{'PASS' if ok else 'FAIL'}] closed-form check: A=P_n gives "
          f"{v_full:.8f} vs 1/2^n = {closed:.8f}")
    if not ok:
        raise SystemExit("REFUSE: machinery disagrees with the closed form; nothing below is trustworthy")

    # ---- the drawn subset
    M = args.M if args.M else 2 ** n
    pool = [l for l in labs if l != ident]          # identity carries no information
    rng = np.random.default_rng(args.seed)
    idx = rng.choice(len(pool), size=min(M, len(pool)), replace=False)
    A = [pool[i] for i in idx]
    print(f"\n  drawn A: |A|={len(A)} of {len(pool)} non-identity Paulis, seed={args.seed}")

    v, _ = max_over_psi(A, dim, restarts=args.restarts, seed=args.seed)
    pred = math.log(len(A)) / len(A)
    print(f"  delta_A_hat (best of {args.restarts} restarts) = {v:.8f}")
    print(f"  random-subset prediction log(M)/M            = {pred:.8f}   ratio {v/pred:.2f}")
    print(f"  implied floor ~ 1/(eps^2 delta_A):")
    for eps in (0.1, 0.2, 0.3):
        print(f"     eps={eps}:  {1.0/(eps**2 * v):>14,.0f} copies")

    if dim * dim <= 4096:
        ub = certified_upper_bound(A, dim)
        print(f"\n  ✅ CERTIFIED UPPER BOUND on delta_A (lambda_max of Pi_sym M Pi_sym) = {ub:.8f}")
        print(f"     chain: delta_A <= max_psi f(uniform,.) <= lambda_max = {ub:.8f}")
        print(f"     HONEST floor >= 1/(eps^2 delta_ub):")
        for eps in (0.1, 0.2, 0.3):
            print(f"        eps={eps}:  {1.0/(eps**2 * ub):>12,.0f} copies")
        print(f"     (the power-iteration value {v:.6f} sits {'below' if v <= ub else 'ABOVE — BUG'} it, as it must)")
    else:
        ub = None
        print(f"\n  certified bound SKIPPED — needs a {dim*dim}x{dim*dim} eigenproblem")

    print("\n  ⚠ DIRECTION NOTE — the power-iteration number is a DIAGNOSTIC, not the certificate.")
    print("     floor ~ 1/delta_A, so an honest floor needs an UPPER bound on delta_A,")
    print("     i.e. an upper bound on a maximisation. Power iteration lower-bounds a max,")
    print("     so delta_A_hat is OPTIMISTICALLY SMALL and the floor above is OPTIMISTICALLY")
    print("     LARGE. Certifying in the honest direction needs a relaxation (SDP over the")
    print("     symmetric subspace) that is not implemented here.")

    json.dump({"n": n, "M": len(A), "seed": args.seed, "delta_A_hat": v,
               "log_M_over_M": pred, "closed_form_check": v_full,
               "status": "DIAGNOSTIC — not a certificate; bound is in the optimistic direction",
               "A": A if len(A) <= 4096 else "omitted (large)"},
              open(f"results/doorb_deltaA_n{n}_seed{args.seed}.json", "w"), indent=1)
    print(f"\n  -> results/doorb_deltaA_n{n}_seed{args.seed}.json")


if __name__ == "__main__":
    main()
