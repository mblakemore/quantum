#!/usr/bin/env python3
"""G1 lemma premise checks (Whisper C5073, board #150) — machine verification of P1/P2/P3
from docs/h14-b1-g1-exchange-wlog-lemma-whisper-c5073.md. One code path: every object
imported from h14_b1_reduced_solve."""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from h14_b1_reduced_solve import G512_qstar, exchange512, comb512_A, comb512_B, D512
import cvxpy as cp

N_RANDOM = 8
RNG = np.random.default_rng(51273)


def comb_residuals(cons_fn, W):
    """Numerical residuals of each comb constraint at a CONSTANT W (via cvxpy expressions)."""
    Wc = cp.Constant(W)
    out = []
    for c in cons_fn(Wc):
        lhs, rhs = c.args
        out.append(np.asarray(lhs.value) - np.asarray(rhs.value))
    return out


def main():
    rep = {"card": "h14_b1_g1_lemma_checks", "cycle": "C5073"}
    PI = exchange512()
    # P1: involutive orthogonal permutation
    p1_inv = float(np.max(np.abs(PI @ PI - np.eye(512))))
    p1_sym = float(np.max(np.abs(PI - PI.T)))
    p1_perm = bool(np.all((PI == 0) | (PI == 1)) and np.all(PI.sum(0) == 1) and np.all(PI.sum(1) == 1))
    rep["P1"] = {"max_dev_PI2_minus_I": p1_inv, "max_dev_PI_minus_PIT": p1_sym, "is_0_1_permutation": p1_perm}
    print(f"P1: PI^2=I dev {p1_inv:.1e} · PI=PI^T dev {p1_sym:.1e} · 0/1 doubly-stochastic {p1_perm}")
    assert p1_inv == 0.0 and p1_sym == 0.0 and p1_perm

    # P2: G exchange-invariance
    G = G512_qstar()
    p2 = float(np.linalg.norm(PI @ G @ PI - G))
    rep["P2"] = {"norm_PIGPI_minus_G": p2}
    print(f"P2: ||PI G PI - G|| = {p2:.2e}")
    assert p2 < 1e-8

    # P3: cone covariance on random Hermitian inputs — comb_B residuals of PI W PI must
    # equal (up to factor reordering) comb_A residuals of W, and vice versa. We verify the
    # operational form: W satisfies comb_A EXACTLY iff PI W PI satisfies comb_B EXACTLY,
    # by checking residual NORMS match to machine precision on generic (non-feasible) W.
    worst = 0.0
    for t in range(N_RANDOM):
        X = RNG.normal(size=(512, 512)) + 1j * RNG.normal(size=(512, 512))
        W = (X + X.conj().T) / 2
        ra = [np.linalg.norm(r) for r in comb_residuals(comb512_A, W)]
        rb = [np.linalg.norm(r) for r in comb_residuals(comb512_B, PI @ W @ PI)]
        rb2 = [np.linalg.norm(r) for r in comb_residuals(comb512_B, W)]
        ra2 = [np.linalg.norm(r) for r in comb_residuals(comb512_A, PI @ W @ PI)]
        for x, y in list(zip(ra, rb)) + list(zip(rb2, ra2)):
            worst = max(worst, abs(x - y) / max(x, 1e-12))
    rep["P3"] = {"n_random": N_RANDOM, "worst_relative_residual_mismatch": worst}
    print(f"P3: worst relative residual-norm mismatch over {N_RANDOM} random W (both directions): {worst:.2e}")
    assert worst < 1e-10

    rep["verdict"] = "ALL PREMISES PASS"
    json.dump(rep, open(os.path.join(HERE, "..", "results", "h14_b1_g1_lemma_checks.json"), "w"), indent=1)
    print("ALL PREMISES PASS -> results/h14_b1_g1_lemma_checks.json")


if __name__ == "__main__":
    main()
