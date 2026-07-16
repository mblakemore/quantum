#!/usr/bin/env python3
"""Exp142 STAGE-2: stabilizer-elimination arm under readout noise — robust decoder pricing.

Pre-registered Stage-2 assignment (Elder, accepted meeting 2026-07-16 04:44Z):
the ideal stabilizer strategy eliminates a covered wrong candidate on its FIRST
observed -1 parity. Under readout error a flipped bit can fake a -1 on the TRUE
candidate, which is fatal. Robust decoder = per-candidate SPRT:

  observation for covered candidate i: b = e~ . a_i (mod 2), where a_i solves
  a.G = C_i and e~ is the syndrome after iid per-generator-bit flips w.p. q.
  Parity error prob is exactly p_i = (1 - (1-2q)^w_i)/2 with w_i = |a_i|.
  H_wrong: b ~ Bern(1/2).  H_true: b ~ Bern(p_i).
  LLR_i += ln(0.5/p_i) if b==1 else ln(0.5/(1-p_i));  eliminate at LLR >= A_ELIM.

Wald: P(true candidate ever crosses A_ELIM) <= e^-A_ELIM. A_ELIM = ln(100) -> 1%
fatal-elimination bound (matches product-arm SPRT B=-4.6 pricing, f9370a0).

Noise model: readout-only floor at q=1.5%/generator bit, plus a q ladder
{3%, 5%, 8%} standing in for the ~n^2/2-CX Clifford compilation overhead
(effective parity-flip inflation) — the "don't underprice it" caveat. A q level
where stabilizer-robust >= product-SPRT is the crossover where the ideal
strategy loses its lead on hardware.

Comparison baseline: product-arm SPRT at the same q (same barriers A=ln(3^n*100),
B=-A_ELIM), parity error q_true(n) = (1-(1-2q)^n)/2 (all n bits read out).

REPORTED-ALONGSIDE context for the frozen prereg (bd8632b): Stage-2 numbers are
NOT graded constants of the Stage-1 flight.
"""
import numpy as np, itertools, json, sys, time

rng = np.random.default_rng(20260716)
A_ELIM = np.log(100.0)          # 1% fatal false-elimination bound (Wald)

# ---------- F2 helpers (self-contained copy of da3c079 baseline helpers) ----------
def f2_rank(M):
    M = M.copy() % 2; r = 0
    for c in range(M.shape[1]):
        piv = None
        for i in range(r, M.shape[0]):
            if M[i, c]: piv = i; break
        if piv is None: continue
        M[[r, piv]] = M[[piv, r]]
        for i in range(M.shape[0]):
            if i != r and M[i, c]: M[i] ^= M[r]
        r += 1
        if r == M.shape[0]: break
    return r

def f2_solve(G, y):
    n = G.shape[0]
    A = np.concatenate([G.T, y[:, None]], axis=1) % 2
    A = A.copy(); piv = []; r = 0
    for c in range(n):
        p = None
        for i in range(r, A.shape[0]):
            if A[i, c]: p = i; break
        if p is None: piv.append(None); continue
        A[[r, p]] = A[[p, r]]
        for i in range(A.shape[0]):
            if i != r and A[i, c]: A[i] ^= A[r]
        piv.append(r); r += 1
    a = np.zeros(n, dtype=int)
    for c, p in enumerate(piv):
        if p is not None: a[c] = A[p, -1]
    if ((a @ G) % 2 != y % 2).any(): return None
    return a

def sympl_all(C, G, n):
    """symplectic products of every candidate row with every generator row"""
    return ((C[:, None, :n] & G[None, :, n:]).sum(-1)
            + (C[:, None, n:] & G[None, :, :n]).sum(-1)) % 2

def rand_max_isotropic(n):
    gens = []
    while len(gens) < n:
        v = rng.integers(0, 2, 2 * n)
        if not v.any(): continue
        if gens:
            G = np.array(gens)
            s = ((G[:, :n] & v[None, n:]).sum(-1) + (G[:, n:] & v[None, :n]).sum(-1)) % 2
            if s.any(): continue
            if f2_rank(np.vstack([G, v])) != len(gens) + 1: continue
        gens.append(v)
    return np.array(gens)

def candidates_fullweight(n):
    combos = np.array(list(itertools.product([(1, 0), (1, 1), (0, 1)], repeat=n)))
    return np.concatenate([combos[:, :, 0], combos[:, :, 1]], axis=1)

# ---------- Stage-2 robust stabilizer trial ----------
def stab_robust_trial(n, C, q):
    m = len(C)
    idxP = rng.integers(0, m); P = C[idxP]
    alive = np.ones(m, bool)
    llr = np.zeros(m)
    shots = 0
    while alive.sum() > 1:
        G = rand_max_isotropic(n)
        shots += 1
        s = sympl_all(C, G, n)
        covered = (s == 0).all(axis=1) & alive
        if not covered.any(): continue
        # ideal syndrome: uniform, constrained to e.aP = 0 if true covered
        e = rng.integers(0, 2, n)
        aP = f2_solve(G, P) if covered[idxP] else None
        if aP is not None and (e @ aP) % 2 == 1:
            e[np.where(aP == 1)[0][0]] ^= 1   # bijection onto the even coset
        # readout noise: iid flip each generator bit w.p. q
        e_noisy = e ^ (rng.random(n) < q).astype(int)
        for i in np.where(covered)[0]:
            a = f2_solve(G, C[i])
            if a is None: continue
            w = int(a.sum())
            p = (1.0 - (1.0 - 2.0 * q) ** w) / 2.0
            if p <= 0: p = 1e-12
            b = int((e_noisy @ a) % 2)
            llr[i] += np.log(0.5 / p) if b == 1 else np.log(0.5 / (1.0 - p))
            if llr[i] >= A_ELIM and i != idxP:
                alive[i] = False
            elif llr[i] >= A_ELIM and i == idxP:
                alive[i] = False          # fatal: true eliminated (counted as failure)
    survivor = int(np.where(alive)[0][0]) if alive.any() else -1
    return shots, survivor == idxP

# ---------- product-arm SPRT baseline at the same q (MC over the LLR walk) ----------
def product_sprt_trial(n, q):
    """LLR = ln P(obs|true)/P(obs|wrong); odd shot -> ln(q_true/0.5) < 0,
    even shot -> ln((1-q_true)/0.5) > 0. Accept true at A = ln(3^n * 100)
    (family-wise), eliminate at B = -ln(100). Sequential-with-stopping visits
    ~(3^n-1)/2 wrong bases (uniform true position) then the true basis."""
    q_true = (1.0 - (1.0 - 2.0 * q) ** n) / 2.0
    A = np.log(3.0 ** n * 100.0); B = -A_ELIM
    odd_step = np.log(q_true / 0.5); even_step = np.log((1.0 - q_true) / 0.5)
    total = 0
    for _ in range((3 ** n - 1) // 2):        # wrong bases: odd w.p. 1/2, drift to B
        L = 0.0
        while B < L < A:
            L += odd_step if rng.random() < 0.5 else even_step
            total += 1
    L = 0.0                                    # true basis: odd w.p. q_true, drift to A
    while B < L < A:
        L += odd_step if rng.random() < q_true else even_step
        total += 1
    return total

# ---------- run ----------
if __name__ == "__main__":
    out = {"A_ELIM": float(A_ELIM), "runs": []}
    t0 = time.time()

    for n, q, trials in [(6, 0.015, 10), (6, 0.03, 10), (6, 0.05, 8), (6, 0.08, 6),
                          (8, 0.015, 4), (8, 0.05, 3)]:
        C = candidates_fullweight(n)
        res = [stab_robust_trial(n, C, q) for _ in range(trials)]
        shots = [r[0] for r in res]; succ = [r[1] for r in res]
        ideal = {6: 988, 8: 4833}[n]
        rec = {"arm": "stab_robust", "n": n, "q": q, "trials": trials,
               "mean_shots": float(np.mean(shots)), "std_shots": float(np.std(shots)),
               "success": int(sum(succ)), "inflation_vs_ideal": float(np.mean(shots) / ideal)}
        out["runs"].append(rec)
        print(f"stab_robust n={n} q={q:.3f}: mean {np.mean(shots):,.0f} shots "
              f"({np.mean(shots)/ideal:.2f}x ideal {ideal:,}), success {sum(succ)}/{trials}  "
              f"[{time.time()-t0:.0f}s]", flush=True)

    for n, q, trials in [(6, 0.015, 20), (6, 0.05, 20), (8, 0.015, 10), (8, 0.05, 10)]:
        res = [product_sprt_trial(n, q) for _ in range(trials)]
        succ_note = "MC walk, barriers A=ln(3^n*100), B=-ln(100)"
        rec = {"arm": "product_sprt", "n": n, "q": q, "trials": trials,
               "mean_shots": float(np.mean(res)), "std_shots": float(np.std(res)),
               "note": succ_note}
        out["runs"].append(rec)
        print(f"product_sprt n={n} q={q:.3f}: mean {np.mean(res):,.0f} shots  [{time.time()-t0:.0f}s]", flush=True)

    with open("/droid/repos/quantum/experiments/exp142_stage2_stab_robust_results_elder_c6491.json", "w") as f:
        json.dump(out, f, indent=1)
    print("saved. total %.0fs" % (time.time() - t0))
