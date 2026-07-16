"""Exp142 feasibility sim v2 — corrected learners. Whisper C4745.

Quantum learner (correct): Bell sampling on rho_P (x) rho_P returns a uniform random Pauli Q
COMMUTING with P (for even #Y in P; anticommuting for odd — decoder tests both hypotheses).
Represent Paulis as 2n-bit symplectic vectors; each shot = one linear constraint <Q,P>_sp = 0.
Sequential rank building: stop when constraint span reaches dim 2n-1 -> P is the unique
non-identity solution. Noise: shot corrupted w.p. p_c -> uniform random Pauli (constraint may
be wrong); sim uses detect-and-retry (verification rounds), modeled as inflation factor.

Conventional learner: basis elimination with conf_k scaled to keep family-wise false-accept
< 1%: conf_k = ceil(log2(3^n) ) + 7.
"""
import numpy as np
rng = np.random.default_rng(7)

def sp_inner(u, v, n):
    # symplectic inner product; u,v are 2n-bit (x|z) vectors
    return (u[:n] @ v[n:] + u[n:] @ v[:n]) % 2

def rank_f2(M):
    M = M.copy() % 2
    r = 0
    rows, cols = M.shape
    for c in range(cols):
        piv = None
        for i in range(r, rows):
            if M[i, c]:
                piv = i; break
        if piv is None: continue
        M[[r, piv]] = M[[piv, r]]
        for i in range(rows):
            if i != r and M[i, c]:
                M[i] = (M[i] + M[r]) % 2
        r += 1
    return r

def quantum_shots(n, trials=300):
    """Noiseless shots to identify P: draw uniform Q from commutant of P, count until
    constraint rank = 2n-1."""
    out = []
    for _ in range(trials):
        # random full-weight product Pauli P: per position x,z in {01(Z),10(X),11(Y)}
        P = np.zeros(2*n, dtype=int)
        for i in range(n):
            xz = rng.choice([(1,0),(0,1),(1,1)])
            P[i], P[n+i] = xz
        cons = []
        shots = 0
        while True:
            shots += 1
            # uniform Q with <Q,P>=0: sample random, resample if inner=1 (rejection, p=1/2)
            while True:
                Q = rng.integers(0, 2, size=2*n)
                if sp_inner(Q, P, n) == 0:
                    break
            cons.append(Q)
            # constraint matrix rows: sp form -> swap halves so plain dot works
            M = np.array([np.concatenate([q[n:], q[:n]]) for q in cons])
            if rank_f2(M) >= 2*n - 1:
                out.append(shots)
                break
            if shots > 200: out.append(shots); break
    a = np.array(out)
    return a.mean(), np.percentile(a, 95)

def conventional_shots(n, trials=300):
    """Elimination with scaled conf_k; returns mean shots and accuracy."""
    conf_k = int(np.ceil(n * np.log2(3))) + 7
    res = []
    n_cand = 3**n
    for _ in range(trials):
        true_pos = rng.integers(0, n_cand)
        shots = 0
        pos = 0
        accepted = None
        order_correct = True
        while accepted is None:
            is_true = (pos % n_cand == true_pos)
            streak = 0
            while streak < conf_k:
                shots += 1
                if is_true or rng.random() < 0.5:
                    streak += 1
                else:
                    streak = -1
                    break
            if streak >= conf_k:
                accepted = (pos % n_cand)
            pos += 1
        res.append((shots, accepted == true_pos))
    arr = np.array([s for s, _ in res])
    acc = np.mean([c for _, c in res])
    return arr.mean(), np.percentile(arr, 95), acc

print(f"{'n':>3} | {'Q ideal':>8} | {'Q p95':>6} | {'Q noisy(x1.5)':>13} | {'Conv mean':>10} | {'Conv acc':>8} | {'ratio':>8}")
for n in (4, 6, 8, 10, 12):
    qm, q95 = quantum_shots(n)
    if n <= 10:
        cm, c95, cacc = conventional_shots(n)
        caccs = f"{cacc:.2f}"
    else:
        cm = 3**n + 0.0; caccs = "analytic"
    # noise inflation: ~10 CX @0.4% + 2n readout @1.5% -> p_shot_corrupt ~ 0.3 at n=10;
    # robust decoder overhead modeled at x1.5/(1-p_c); use conservative x2.2 flat
    qn = qm * 2.2
    print(f"{n:3d} | {qm:8.1f} | {q95:6.0f} | {qn:13.1f} | {cm:10.0f} | {caccs:>8} | {cm/qn:7.0f}x")
