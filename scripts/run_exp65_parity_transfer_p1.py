#!/usr/bin/env python3
"""
Exp65: p=1 QAOA warm-start parity-controlled transfer (4-regular <-> 3-regular, 20 nodes).
Grades Ember pred_c3865_001 at its single pre-registered apparatus-gate (C3914 gate, C3971).

Pre-registration: experiments/exp65-parity-transfer-p1-preregistration.md  (written BEFORE compute)

DV (pre-committed): lift(D->A) = AR(A, theta*_D) - AR_cold(A)   [DIRECT transfer, no re-opt]
  AR(G,theta) = <C(G)>_theta / Cmax(G), EXACT full 2^20 statevector.
  theta*_D    = best-of-K=8 restarts (equalizes donor anchor quality across parities).
  AR_cold(A)  = mean AR(A,.) over R=64 fixed random (gamma,beta) draws.

H1 (=prediction): VALIDATE iff mean lift<0 for BOTH opposite directions AND mean lift>=0 for
                  BOTH same-parity buckets. INVALIDATE otherwise.

Noiseless statevector, local CPU, no QPU budget. Direct numpy simulator (transparent + fast).
Usage: python3 run_exp65_parity_transfer_p1.py [--M 6] [--K 8] [--R 64]
"""
import sys, os, json, time, argparse, itertools
import numpy as np
import networkx as nx
from scipy.optimize import minimize

RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "experiments", "exp65_results.json")


def cut_cost_vector(n, edges):
    """Diagonal MaxCut cost: c[x] = # edges (i,j) with bit_i != bit_j. Length 2^n."""
    idx = np.arange(1 << n, dtype=np.int64)
    bits = ((idx[:, None] >> np.arange(n)[None, :]) & 1).astype(np.int8)  # (2^n, n)
    c = np.zeros(1 << n, dtype=np.float64)
    for (i, j) in edges:
        c += (bits[:, i] ^ bits[:, j])
    return c


def qaoa_p1_ar(c, cmax, gamma, beta, n):
    """Exact AR for p=1 QAOA. State = mixer(beta) . phase(gamma) . |+>^n."""
    N = 1 << n
    psi = np.full(N, 1.0 / np.sqrt(N), dtype=np.complex128)   # |+>^n
    psi = psi * np.exp(-1j * gamma * c)                       # e^{-i gamma C} (diagonal)
    # mixer e^{-i beta sum X} = prod RX(2 beta);  RX(2b) = [[cosb, -i sinb],[-i sinb, cosb]]
    cb, sb = np.cos(beta), np.sin(beta)
    psi = psi.reshape([2] * n)
    for q in range(n):
        psi = np.moveaxis(psi, q, 0)
        a0, a1 = psi[0].copy(), psi[1].copy()
        psi[0] = cb * a0 - 1j * sb * a1
        psi[1] = -1j * sb * a0 + cb * a1
        psi = np.moveaxis(psi, 0, q)
    psi = psi.reshape(N)
    prob = np.abs(psi) ** 2
    exp_c = float(prob @ c)
    return exp_c / cmax


def optimize_donor(c, cmax, n, K, rng):
    """best-of-K restarts; returns (theta*, AR*) maximizing AR. bounds g[0,2pi] b[0,pi]."""
    best_ar, best_th = -1.0, None
    for _ in range(K):
        g0 = rng.uniform(0, 2 * np.pi)
        b0 = rng.uniform(0, np.pi)
        res = minimize(lambda th: -qaoa_p1_ar(c, cmax, th[0], th[1], n),
                       x0=[g0, b0], method="Nelder-Mead",
                       options={"xatol": 1e-4, "fatol": 1e-5, "maxiter": 400})
        ar = -res.fun
        if ar > best_ar:
            best_ar, best_th = ar, res.x
    return best_th, best_ar


def cold_ar(c, cmax, n, R, rng):
    g = rng.uniform(0, 2 * np.pi, R)
    b = rng.uniform(0, np.pi, R)
    return float(np.mean([qaoa_p1_ar(c, cmax, g[i], b[i], n) for i in range(R)]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--M", type=int, default=6)   # graphs per degree
    ap.add_argument("--K", type=int, default=8)   # donor restarts
    ap.add_argument("--R", type=int, default=64)  # cold random draws
    ap.add_argument("--n", type=int, default=20)
    args = ap.parse_args()
    n, M, K, R = args.n, args.M, args.K, args.R
    rng = np.random.default_rng(20260625)
    t0 = time.time()

    # --- build parity-controlled graphs ---
    graphs = {}   # label -> dict(c, cmax, th_star, ar_star, ar_cold)
    for deg, par in [(4, "4reg"), (3, "3reg")]:
        for s in range(M):
            G = nx.random_regular_graph(deg, n, seed=1000 + deg * 100 + s)
            edges = list(G.edges())
            c = cut_cost_vector(n, edges)
            cmax = float(c.max())
            th, ar = optimize_donor(c, cmax, n, K, rng)
            arc = cold_ar(c, cmax, n, R, rng)
            lbl = f"{par}_{s}"
            graphs[lbl] = {"par": par, "deg": deg, "c": c, "cmax": cmax,
                           "th_star": th.tolist(), "ar_star": ar, "ar_cold": arc,
                           "n_edges": len(edges)}
            print(f"  built {lbl}: edges={len(edges)} cmax={cmax:.0f} "
                  f"AR*(donor)={ar:.4f} AR_cold={arc:.4f}", flush=True)

    labels = list(graphs.keys())

    # --- transfers (direct, no re-opt): lift = AR(A, theta*_D) - AR_cold(A) ---
    buckets = {"same_4reg": [], "same_3reg": [], "opp_4to3": [], "opp_3to4": []}
    pairs_log = []
    for d_lbl, a_lbl in itertools.permutations(labels, 2):
        D, A = graphs[d_lbl], graphs[a_lbl]
        g, b = D["th_star"]
        ar_warm = qaoa_p1_ar(A["c"], A["cmax"], g, b, n)
        lift = ar_warm - A["ar_cold"]
        dp, ap_ = D["par"], A["par"]
        if dp == ap_ == "4reg":
            bk = "same_4reg"
        elif dp == ap_ == "3reg":
            bk = "same_3reg"
        elif dp == "4reg" and ap_ == "3reg":
            bk = "opp_4to3"
        else:
            bk = "opp_3to4"
        buckets[bk].append(lift)
        pairs_log.append({"donor": d_lbl, "acceptor": a_lbl, "bucket": bk,
                          "ar_warm": ar_warm, "ar_cold": A["ar_cold"], "lift": lift})

    # --- summarize + grade H1 ---
    def stat(v):
        v = np.array(v)
        return {"n": len(v), "mean": float(v.mean()), "std": float(v.std()),
                "pos_frac": float((v > 0).mean()), "min": float(v.min()), "max": float(v.max())}

    summ = {k: stat(v) for k, v in buckets.items()}
    h1 = (summ["opp_4to3"]["mean"] < 0 and summ["opp_3to4"]["mean"] < 0 and
          summ["same_4reg"]["mean"] >= 0 and summ["same_3reg"]["mean"] >= 0)
    verdict = "VALIDATE" if h1 else "INVALIDATE"

    # donor-quality balance (H2 falsification guard)
    ar4 = [graphs[l]["ar_star"] for l in labels if graphs[l]["par"] == "4reg"]
    ar3 = [graphs[l]["ar_star"] for l in labels if graphs[l]["par"] == "3reg"]
    donor_balance = {"4reg_mean_AR*": float(np.mean(ar4)), "3reg_mean_AR*": float(np.mean(ar3)),
                     "gap": float(np.mean(ar4) - np.mean(ar3))}

    print("\n" + "=" * 70)
    print("EXP65 SUMMARY — p=1 parity-controlled warm-start transfer")
    print("=" * 70)
    for k in ["same_4reg", "same_3reg", "opp_4to3", "opp_3to4"]:
        s = summ[k]
        print(f"  {k:10s} n={s['n']:2d} mean_lift={s['mean']:+.4f} std={s['std']:.4f} "
              f"pos={s['pos_frac']:.2f} [{s['min']:+.4f},{s['max']:+.4f}]")
    print(f"\n  donor-quality balance: 4reg AR*={donor_balance['4reg_mean_AR*']:.4f} "
          f"3reg AR*={donor_balance['3reg_mean_AR*']:.4f} gap={donor_balance['gap']:+.4f}")
    print(f"\n  H1 (opp both<0 AND same both>=0): {h1}  ->  VERDICT: {verdict}")
    print(f"  elapsed {time.time()-t0:.1f}s")

    out = {"experiment": "exp65_parity_transfer_p1", "cycle": 3971,
           "params": {"M": M, "K": K, "R": R, "n": n, "p": 1, "rng_seed": 20260625},
           "buckets": summ, "donor_balance": donor_balance,
           "H1_validate": h1, "verdict": verdict, "pairs": pairs_log,
           "graphs": {l: {"par": graphs[l]["par"], "ar_star": graphs[l]["ar_star"],
                          "ar_cold": graphs[l]["ar_cold"], "th_star": graphs[l]["th_star"],
                          "n_edges": graphs[l]["n_edges"], "cmax": graphs[l]["cmax"]}
                      for l in labels},
           "elapsed_s": time.time() - t0}
    json.dump(out, open(RESULTS, "w"), indent=2)
    print(f"  results -> {RESULTS}")


if __name__ == "__main__":
    main()
