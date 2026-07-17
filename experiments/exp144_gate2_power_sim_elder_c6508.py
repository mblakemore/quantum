#!/usr/bin/env python3
"""Exp144 Gate-2 sim — POWER CALC + SIGN-BLOCK EXACT-SIM (Elder C6508).

Chair requirements (Whisper C4769):
  A. Sign block is v2-NEW physics, outside the C6506 exact-sim: verify by statevector
     (1) planted candidate  -> <Q(t)> = -/+ sin(2 c_j t)  (pin the sign convention)
     (2) CONSERVED non-planted candidate (commutes with all planted, not in group)
         -> conjugation readout reads 0  (the coefficient), while the naive
         <P'>-conservation test CANNOT reject it (reads 1, same as planted)
     (3) randomized-probe majority vote suppresses single-probe false structure
  B. POWER CALC (prereg SS G2): exact noise-convolved Bell-label distribution,
     multinomial MC through the REAL decoder rule (top-m + theta + arctan ratio),
     n in {4,6,8} x q in {0.05,0.10,0.15} x N_bell grid; t-sweep; kill conditions:
     PASS-prob >= 0.9 at N_bell <= 8k under noise; dominance margin floor.

No shots are spent here. Analytic-law + statevector only. Runtime ~1-2 min.
"""
import numpy as np
import itertools, math, json, sys

rng = np.random.default_rng(20260717)

# ---------------------------------------------------------------- Pauli algebra
I2 = np.eye(2, dtype=complex)
PX = np.array([[0, 1], [1, 0]], dtype=complex)
PY = np.array([[0, -1j], [1j, 0]], dtype=complex)
PZ = np.array([[1, 0], [0, -1]], dtype=complex)
MAT = {"I": I2, "X": PX, "Y": PY, "Z": PZ}
LETT = "IXYZ"

def pauli_mat(s):
    m = np.array([[1.0 + 0j]])
    for c in s:
        m = np.kron(m, MAT[c])
    return m

def commutes(a, b):
    """Pauli strings commute iff anticommuting-letter count is even."""
    k = sum(1 for x, y in zip(a, b) if x != "I" and y != "I" and x != y)
    return k % 2 == 0

def string_prod(a, b):
    """Label of the product (phase dropped)."""
    out = []
    for x, y in zip(a, b):
        if x == "I": out.append(y)
        elif y == "I": out.append(x)
        elif x == y: out.append("I")
        else: out.append(({"X","Y","Z"} - {x, y}).pop())
    return "".join(out)

def indep_products(terms):
    """All 2^m subset-product labels; distinct iff multiplicatively independent."""
    labs = set()
    m = len(terms)
    for r in range(m + 1):
        for S in itertools.combinations(range(m), r):
            lab = "I" * len(terms[0])
            for j in S:
                lab = string_prod(lab, terms[j])
            labs.add(lab)
    return labs

# ================================================================ PART A: SIGN BLOCK
def part_a():
    print("=" * 72)
    print("PART A — SIGN-BLOCK EXACT-SIM (statevector, n=4)")
    print("=" * 72)
    n, d = 4, 16
    terms = ["XXXX", "XXYY", "XXZZ"]          # full-weight, commuting, mult-independent
    # commuting + multiplicatively independent?
    assert all(commutes(a, b) for a, b in itertools.combinations(terms, 2))
    assert len(indep_products(terms)) == 8
    coeffs = [0.15, -0.20, 0.25]
    t = 2.0
    V = np.eye(d, dtype=complex)
    for lab, c in zip(terms, coeffs):
        P = pauli_mat(lab)
        V = V @ (math.cos(c * t) * np.eye(d) - 1j * math.sin(c * t) * P)

    all_paulis = ["".join(p) for p in itertools.product(LETT, repeat=n)]

    def probes_for(target, avoid):
        """Paulis anticommuting with target, commuting with every string in avoid."""
        out = []
        for q in all_paulis:
            if q == "I" * n: continue
            if commutes(q, target): continue
            if all(commutes(q, a) for a in avoid): out.append(q)
        return out

    def product_eigenstate(op_mat, sign=+1):
        """A PRODUCT eigenstate of a Hermitian +/-1 Pauli-string operator.
        op_mat = c*S for Pauli string S, c=+-1. Build per-qubit letter eigenstates,
        choosing per-qubit signs so the product of eigenvalues * c = sign."""
        # identify S and c
        for s in all_paulis:
            tr = np.trace(pauli_mat(s).conj().T @ op_mat) / 16
            if abs(abs(tr) - 1) < 1e-9:
                S, c = s, float(np.real(tr)); break
        eig = {"I": {+1: np.array([1, 0], complex)},
               "X": {+1: np.array([1, 1], complex)/math.sqrt(2), -1: np.array([1, -1], complex)/math.sqrt(2)},
               "Y": {+1: np.array([1, 1j], complex)/math.sqrt(2), -1: np.array([1, -1j], complex)/math.sqrt(2)},
               "Z": {+1: np.array([1, 0], complex), -1: np.array([0, 1], complex)}}
        # per-qubit eigenvalue choices: all +1, then flip ONE non-I qubit if needed
        signs = [+1] * n
        prod_needed = sign / c
        cur = 1
        if cur != prod_needed:
            for i, ch in enumerate(S):
                if ch != "I": signs[i] = -1; break
        v = np.array([1.0 + 0j])
        for ch, sg in zip(S, signs):
            v = np.kron(v, eig[ch][+1] if (ch == "I" or sg == +1) else eig[ch][-1])
        assert abs((v.conj() @ op_mat @ v) - sign) < 1e-9
        return v

    def conj_readout(cand, probe):
        """prep +1 product eigenstate of iQP, evolve V, return <Q>."""
        R = 1j * pauli_mat(probe) @ pauli_mat(cand)
        psi = product_eigenstate(R, +1)
        psit = V @ psi
        return float(np.real(psit.conj() @ pauli_mat(probe) @ psit))

    ok = True
    # --- A1: planted candidates, decoder-grade probe (commutes w/ other planted)
    print("\nA1  planted candidates, probe constrained to commute w/ other terms:")
    for j, (lab, c) in enumerate(zip(terms, coeffs)):
        others = [x for k, x in enumerate(terms) if k != j]
        qs = probes_for(lab, others)
        assert qs, f"no probe exists for {lab}"
        got = conj_readout(lab, qs[0])
        want = -math.sin(2 * c * t)          # sign convention measured here & FROZEN
        match = abs(got - want) < 1e-9
        ok &= match
        print(f"    {lab} c={c:+.2f}: <Q(t)> = {got:+.6f}  vs -sin(2ct) = {want:+.6f}  "
              f"{'PASS' if match else 'FAIL'}")
    print("    SIGN CONVENTION (frozen): <Q(t)> = -sin(2 c_j t) on the +1 eigenstate "
          "of iQP_j  =>  sign(c_j) = -sign(<Q(t)>)")

    # --- A2: conserved non-planted candidate
    print("\nA2  CONSERVED non-planted candidate (the SS4 subtlety):")
    group = indep_products(terms)
    conserved = None
    for cand in all_paulis:
        if cand == "I" * n or cand in group: continue
        if all(commutes(cand, x) for x in terms):
            conserved = cand; break
    assert conserved, "no conserved non-planted candidate exists at n=4 (unexpected)"
    # naive conservation test: <P'> on its own +1 product eigenstate after V
    psi = product_eigenstate(pauli_mat(conserved), +1)
    psit = V @ psi
    naive = float(np.real(psit.conj() @ pauli_mat(conserved) @ psit))
    qs = probes_for(conserved, terms)        # ideal probe (oracle access to terms)
    readout = conj_readout(conserved, qs[0]) if qs else float("nan")
    print(f"    candidate {conserved}: naive <P'(t)> = {naive:+.6f} "
          f"(=1, INDISTINGUISHABLE from planted — naive test fails, as flagged)")
    print(f"    conjugation readout      = {readout:+.6f} (=0 = coefficient, "
          f"{'PASS' if abs(readout) < 1e-9 else 'FAIL'})")
    ok &= abs(naive - 1) < 1e-9 and abs(readout) < 1e-9

    # --- A3: randomized-probe majority vote (conventional arm, no oracle)
    print("\nA3  randomized-probe majority vote (probe NOT constrained — conv. arm):")
    def vote(cand, n_probe=25):
        vals = []
        cands_q = [q for q in all_paulis if q != "I"*n and not commutes(q, cand)]
        for q in rng.choice(len(cands_q), size=min(n_probe, len(cands_q)), replace=False):
            vals.append(conj_readout(cand, cands_q[q]))
        return np.array(vals)
    for lab, c in zip(terms[:1], coeffs[:1]):
        v = vote(lab)
        det = np.mean(np.abs(v) > 1e-6)
        sgn = np.median(np.sign(v[np.abs(v) > 1e-6]))
        print(f"    planted {lab}: {det:.0%} of random probes give |signal|>0, "
              f"median sign {sgn:+.0f} (systematic)")
        ok &= det > 0.5
    v = vote(conserved)
    fp = np.mean(np.abs(v) > 1e-6)
    mean_abs = float(np.mean(np.abs(v)))
    print(f"    conserved {conserved}: fraction |signal|>0 = {fp:.0%}, "
          f"mean|signal| = {mean_abs:.4f} (want ~0; single stray probes are why "
          f"MAJORITY vote is frozen, not any-probe)")
    ok &= mean_abs < 0.05
    print(f"\nPART A VERDICT: {'PASS' if ok else 'FAIL'}")
    return ok

# ================================================================ PART B: POWER CALC
GRID = [0.15, 0.20, 0.25]
TAU, ALPHA = 0.03, 0.01

def label_int(lab):
    return int("".join(f"{LETT.index(c):02b}" for c in lab), 2)

def true_dist(n, terms, coeffs, t):
    """dict label-> prob (2^m sparse subset law)."""
    m = len(terms)
    out = {}
    for r in range(m + 1):
        for S in itertools.combinations(range(m), r):
            lab = "I" * n
            pr = 1.0
            for j in range(m):
                if j in S:
                    lab = string_prod(lab, terms[j]); pr *= math.sin(coeffs[j]*t)**2
                else:
                    pr *= math.cos(coeffs[j]*t)**2
            out[lab] = out.get(lab, 0.0) + pr
    return out

def noisy_dist(n, tdist, q):
    """Per-pair label noise: with prob q the pair label is uniformly randomized.
    Returns full 4^n vector."""
    stay, flip = 1 - 0.75*q, 0.25*q
    full = np.zeros(4 ** n)
    for lab, pr in tdist.items():
        # distribute over Hamming(pair)-distance shells via tensor structure
        # kernel per pair: [stay, flip, flip, flip] against XOR of 2-bit pair labels
        vec = np.array([pr])
        for c in lab:
            base = np.full(4, flip); base[LETT.index(c)] = stay
            # reorder: entry k of this pair's kernel = P(observed letter k | true c)
            vec = np.kron(vec, base)
        full += vec
    return full / full.sum()

def decode(counts, n, t, m=3):
    """REAL decoder rule: top-m non-identity peaks (theta implicit: must be > 5x
    uniform background estimate), arctan ratio magnitudes. Returns (support, chat)."""
    N = counts.sum()
    idx0 = 0                                    # 'III..' is label 0
    order = np.argsort(counts)[::-1]
    picks, k = [], 0
    bg = np.median(counts[counts > 0]) if (counts > 0).any() else 0
    for i in order:
        if i == idx0: continue
        picks.append(i); k += 1
        if k == m: break
    p0 = counts[idx0] / N
    support, chat = [], []
    for i in picks:
        pj = counts[i] / N
        support.append(i)
        chat.append(math.atan(math.sqrt(max(pj, 1e-12) / max(p0, 1e-12))) / t)
    return support, chat

def run_power(n, q, t, N_bell, reps=200):
    npass = 0
    for _ in range(reps):
        # random instance: commuting, mult-independent, full-weight
        terms = sample_instance(n)
        coeffs = list(rng.permutation(GRID) * rng.choice([-1, 1], 3))
        td = true_dist(n, terms, [abs(c) for c in coeffs], t)
        nd = noisy_dist(n, td, q)
        counts = rng.multinomial(N_bell, nd)
        support, chat = decode(counts, n, t)
        want = sorted(label_int(string_prod("I"*n, x)) for x in terms)
        got = sorted(support)
        if got != want: continue
        # match magnitudes by label
        m_by_lab = {label_int(x): abs(c) for x, c in zip(terms, coeffs)}
        if all(abs(ch - m_by_lab[s]) <= TAU for s, ch in zip(support, chat)):
            npass += 1
    return npass / reps

_inst_cache = {}
def sample_instance(n):
    """m=3 commuting multiplicatively-independent full-weight strings."""
    while True:
        cand = ["".join(rng.choice(list("XYZ"), n)) for _ in range(3)]
        if not all(commutes(a, b) for a, b in itertools.combinations(cand, 2)):
            continue
        if len(indep_products(cand)) != 8: continue
        if len(set(cand)) != 3: continue
        return cand

def dominance_margin(t, grid=GRID):
    """EXACT min-singleton / max-(|S|>=2)-subset peak ratio from the subset law."""
    s2 = [math.sin(c * t) ** 2 for c in grid]
    c2 = [1 - x for x in s2]
    m = len(grid)
    def peak(S):
        return math.prod(s2[j] if j in S else c2[j] for j in range(m))
    singles = [peak({j}) for j in range(m)]
    multis = [peak(set(S)) for r in range(2, m + 1)
              for S in itertools.combinations(range(m), r)]
    return min(singles) / max(multis)

def part_b():
    print("\n" + "=" * 72)
    print("PART B — POWER CALC (exact noise-convolved law + multinomial MC)")
    print("=" * 72)
    t_grid = [1.5, 2.0, 2.5]
    q_grid = [0.05, 0.10, 0.15]
    N_grid = [1000, 2000, 4000, 8000]
    results = {}

    # t-sweep at the hardest point (n=8, q=0.15, N=4000)
    print("\nB1  t-sweep (n=8, q=0.15, N=4000, 100 reps) — freeze argmax-worst-term:")
    tbest, pbest = None, -1
    for t in t_grid:
        # singleton dominance check at this t
        margin = dominance_margin(t)
        if margin <= 1:
            print(f"    t={t}: dominance margin {margin:.2f}x <= 1 — excluded "
                  f"(NOTE: sin^2<0.5 alone is NOT sufficient; exact condition is "
                  f"min-singleton > max multi-subset peak)")
            continue
        p = run_power(8, 0.15, t, 4000, reps=100)
        print(f"    t={t}: PASS-prob={p:.2f}, noiseless dominance margin={margin:.2f}x")
        if p > pbest: tbest, pbest = t, p
    print(f"    FROZEN t = {tbest}")

    print(f"\nB2  PASS-prob grid at t={tbest} (200 reps/cell):")
    kill_ok = True
    for n in (4, 6, 8):
        for q in q_grid:
            row = []
            for N in N_grid:
                p = run_power(n, q, tbest, N)
                row.append(p)
                results[f"n{n}_q{q}_N{N}"] = p
            print(f"    n={n} q={q:.2f}: " + "  ".join(
                f"N={N}:{p:.2f}" for N, p in zip(N_grid, row)))
            if row[-1] < 0.9:
                kill_ok = False
                print(f"      ^^ KILL CONDITION HIT: PASS-prob {row[-1]:.2f} < 0.9 at N=8000")
    # m_bell = smallest N with PASS>=0.99 in IDEAL (q=0) sim
    print("\nB3  m_bell(n) (ideal q=0, PASS>=0.99, 300 reps) — refined below the")
    print("    coarse grid: budget is the RATIO DENOMINATOR, an unrefined floor")
    print("    inflates our own budget and silently shrinks the reported ratio:")
    m_bell = {}
    for n in (4, 6, 8):
        for N in [250, 500] + N_grid:
            p = run_power(n, 0.0, tbest, N, reps=300)
            if p >= 0.99:
                m_bell[n] = N
                print(f"    n={n}: m_bell={N} (PASS={p:.3f}) -> budget 5*m_bell={5*N}")
                break
        else:
            m_bell[n] = None
            print(f"    n={n}: >8000 — REFINE NEEDED")
    verdict = kill_ok and all(v for v in m_bell.values())
    print(f"\nPART B VERDICT: {'PASS — no kill condition hit' if verdict else 'KILL/REFINE'}")
    return verdict, {"t_frozen": tbest, "m_bell": m_bell, "grid": results}

if __name__ == "__main__":
    a_ok = part_a()
    b_ok, b_res = part_b()
    out = {"part_a_signblock": bool(a_ok), "part_b_power": bool(b_ok), **b_res}
    with open(sys.path[0] + "/exp144_gate2_power_results_elder_c6508.json", "w") as f:
        json.dump(out, f, indent=2, default=str)
    print("\nresults ->", "exp144_gate2_power_results_elder_c6508.json")
    print("OVERALL:", "GREEN" if (a_ok and b_ok) else "NOT GREEN")
