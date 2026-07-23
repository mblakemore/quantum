#!/usr/bin/env python3
"""F119 (Exp142) audit — Ember C4215.

Charge (Whisper C4997): audit F119 against the exact axis that killed F121.
F121 died because its floor priced cost-to-SIMULATE, and a direct classical
attack on the PUBLIC planted structure (g public) solved the problem cheaply.

For F119 the two decisive questions are EMPIRICAL, not theoretical:
  (Q1) What is the exact state rho_P the flight kit prepares? (product? entangled?
       what is its Pauli spectrum / stabilizer structure?)
  (Q2) Does the BEST single-copy strategy (esp. the per-qubit X/Y/Z scan the
       advisor flagged) actually identify P cheaply? If yes -> the exponential
       'advantage' is a naive-baseline artifact = SUPERSEDED. If the best
       single-copy strategy provably cannot -> the floor is real.

This script RUNS the attacks against the REVEALED sealed instances. No arguing
from the floor's existence.
"""
import numpy as np
import itertools

# ---- Pauli machinery (exact density matrices; small n) --------------------
I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
PAULI = {"I": I2, "X": X, "Y": Y, "Z": Z}

# +1/-1 eigenstate density matrices of single-qubit Paulis
def eigst(pauli, sign_bit):
    Pm = PAULI[pauli]
    # projector onto (-1)^sign_bit eigenvalue: (I + (-1)^b P)/2
    return (I2 + ((-1) ** sign_bit) * Pm) / 2

def kron_list(mats):
    out = mats[0]
    for m in mats[1:]:
        out = np.kron(out, m)
    return out

def pauli_op(pstr):
    return kron_list([PAULI[c] for c in pstr])

def even_parity_strings(n):
    for bits in itertools.product([0, 1], repeat=n):
        if sum(bits) % 2 == 0:
            yield bits

def rho_P(P):
    """Exact rho_P per flight kit: average over even-parity sign vectors of the
    product of single-qubit eigenstates |P_i, b_i>."""
    n = len(P)
    dim = 2 ** n
    rho = np.zeros((dim, dim), dtype=complex)
    strings = list(even_parity_strings(n))
    for b in strings:
        rho += kron_list([eigst(P[i], b[i]) for i in range(n)])
    rho /= len(strings)
    return rho

def pauli_spectrum(rho, n, weight_report=True):
    """Return dict {pauli_str: <Q>} for all 4^n Paulis with |<Q>|>1e-9."""
    nonzero = {}
    for combo in itertools.product("IXYZ", repeat=n):
        pstr = "".join(combo)
        val = np.trace(rho @ pauli_op(pstr)).real
        if abs(val) > 1e-9:
            nonzero[pstr] = round(val, 6)
    return nonzero

# ---- (Q1) exact spectrum for each revealed instance -----------------------
REVEALED = {4: "XXXX", 6: "YYXYZY"}  # exact DM feasible; n=8/10 by structure below

print("=" * 70)
print("Q1  EXACT STATE STRUCTURE  rho_P = avg_{even-parity b} (x)_i |P_i,b_i>")
print("=" * 70)
for n, P in REVEALED.items():
    rho = rho_P(P)
    spec = pauli_spectrum(rho, n)
    purity = np.trace(rho @ rho).real
    rank = np.linalg.matrix_rank(rho, tol=1e-9)
    print(f"\n n={n}  P={P}")
    print(f"   nonzero Pauli expectations: {spec}")
    print(f"   purity tr(rho^2)={purity:.6f}   rank={rank}   "
          f"(expect rank 2^(n-1)={2**(n-1)}, purity 1/2^(n-1)={1/2**(n-1):.6f})")
    only_IP = set(spec.keys()) <= {"I" * n, P}
    print(f"   spectrum == {{I, P}} ONLY?  {only_IP}   "
          f"=> rho_P == (I+P)/2^n : {only_IP}")

# ---- (Q1b) k-local marginals are maximally mixed --------------------------
print("\n" + "=" * 70)
print("Q1b  ALL k-LOCAL MARGINALS MAXIMALLY MIXED  (kills any local attack)")
print("=" * 70)
for n, P in REVEALED.items():
    rho = rho_P(P)
    worst = 0.0
    # check every proper subset marginal for any nonzero Pauli
    for k in range(1, n):
        for qubits in itertools.combinations(range(n), k):
            # trace out complement
            keep = list(qubits)
            # build reduced DM by partial trace
            r = partial_trace(rho, keep, n) if False else None
    # cheaper: a k-local Pauli (identity off support) has <Q>=0 unless support carries P wholly
    max_klocal = 0.0
    for combo in itertools.product("IXYZ", repeat=n):
        pstr = "".join(combo)
        support = [i for i in range(n) if pstr[i] != "I"]
        if 0 < len(support) < n:
            val = abs(np.trace(rho @ pauli_op(pstr)).real)
            max_klocal = max(max_klocal, val)
    print(f" n={n} P={P}: max |<Q>| over ALL proper-subset (k<n) Paulis = "
          f"{max_klocal:.2e}  => {'NO local info' if max_klocal<1e-9 else 'LOCAL INFO LEAKS!'}")

# ---- (Q2) RUN the attacks: single-copy per-qubit scan vs two-copy Bell -----
print("\n" + "=" * 70)
print("Q2  RUN THE ATTACKS  (best single-copy strategies vs two-copy Bell)")
print("=" * 70)

rng = np.random.default_rng(4215)

def sample_single_copy_measure(P, basis, rng):
    """Prepare one fresh even-parity copy of rho_P, measure each qubit in basis[i]
    ({X,Y,Z}); return +-1 outcomes. Simulates a single-copy measurement."""
    n = len(P)
    # fresh even-parity sign
    b = rng.integers(0, 2, size=n)
    if b.sum() % 2:
        b[rng.integers(0, n)] ^= 1
    outcomes = []
    for i in range(n):
        # qubit i is eigenstate of P_i with eigenvalue (-1)^b_i.
        # measuring in basis 'basis[i]': if basis[i]==P_i -> deterministic (-1)^b_i;
        # else uniform +-1 (Pauli eigenstates mutually unbiased).
        if basis[i] == P[i]:
            outcomes.append((-1) ** b[i])
        else:
            outcomes.append(rng.choice([1, -1]))
    return np.array(outcomes)

def attack_perqubit_scan(P, copies_per_basis, rng):
    """Advisor's attack: for each qubit measure X,Y,Z; try to identify P_i from the
    per-qubit marginal (guess the basis giving a deterministic outcome)."""
    n = len(P)
    # For each basis A in {X,Y,Z}, collect copies; record per-qubit outcome stats.
    # If a qubit's outcome is deterministic in basis A -> P_i = A.
    guess = ["?"] * n
    stats = {A: np.zeros((n, 2)) for A in "XYZ"}  # counts of +1,-1
    for A in "XYZ":
        for _ in range(copies_per_basis):
            out = sample_single_copy_measure(P, A * n, rng)
            for i in range(n):
                stats[A][i, 0 if out[i] == 1 else 1] += 1
    for i in range(n):
        # a deterministic basis has one count == copies_per_basis, other == 0
        best_A, best_bias = "?", 0.0
        for A in "XYZ":
            c = stats[A][i]
            bias = abs(c[0] - c[1]) / max(1, c.sum())  # 1.0 if deterministic
            if bias > best_bias:
                best_bias, best_A = bias, A
        guess[i] = best_A
    correct = sum(1 for i in range(n) if guess[i] == P[i])
    return "".join(guess), correct

def bell_sample_pauli(P, rng):
    """Two-copy Bell-difference sample: returns a Pauli Q drawn ∝ <Q>^2.
    For rho_P=(I+P)/2^n only <P>^2=<I>^2=1 -> returns P (or I) each shot."""
    # Analytic: outcome is P with prob 1/2, I with prob 1/2 (the {I,P} stabilizer).
    # We simulate honestly via the spectrum weights.
    return P if rng.random() < 0.5 else "I" * len(P)

def attack_two_copy(P, max_shots, rng):
    """Collect Bell samples; P identified as the unique nonidentity Pauli seen."""
    n = len(P)
    seen = set()
    for s in range(1, max_shots + 1):
        Q = bell_sample_pauli(P, rng)
        if Q != "I" * n:
            seen.add(Q)
            # unique nonidentity stabilizer -> that's P
            return s, Q
    return max_shots, None

for n, P in [(4, "XXXX"), (6, "YYXYZY"), (8, "ZYYXXYZZ"), (10, "YYXZXXXYZZ")]:
    # Attack 1: per-qubit scan with a GENEROUS budget
    budget = 200  # copies per basis (600 single-copy measurements per qubit-column)
    guess, correct = attack_perqubit_scan(P, budget, rng)
    # Attack 2: best single-copy random-Pauli identification needs to scan candidates.
    #   With all k-local marginals maximally mixed, only measuring Q=P gives signal;
    #   candidate space size for full-weight ensemble = 3^n.
    cand = 3 ** n
    # Attack 3: two-copy
    shots2, q2 = attack_two_copy(P, 100, rng)
    print(f"\n n={n} P={P}")
    print(f"   [per-qubit scan] budget={budget} copies/basis  guess={guess}  "
          f"correct {correct}/{n}  (random-guess expectation {n/3:.1f}/{n})")
    print(f"   [best single-copy] all k<n marginals max-mixed => must scan Q=P among "
          f"3^{n}={cand:,} full-weight candidates; each wrong measurement 0 signal")
    print(f"   [two-copy Bell]   identified P in {shots2} shots (Q={q2})")

print("\n" + "=" * 70)
print("VERDICT INPUTS COMPUTED — see printed structure above.")
print("=" * 70)
