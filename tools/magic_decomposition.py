#!/usr/bin/env python3
"""P-CCM v1.0 — component ① of the classical solver: the magic-state decomposition.

WHAT THIS IS AND IS NOT. The solver needs four pieces; this file is the first, built with its
own correctness gate before anything is wired to it:

    ① MAGIC-STATE DECOMPOSITION   |A>^(x)t -> chi stabilizer states        <- THIS FILE
    ② GADGETIZATION                T gates -> Clifford + magic injection
    ③ CLIFFORD PROPAGATION         general tableau update
    ④ SAMPLING ESTIMATOR           chi inner products -> P_out(x) with bounds

THE CONSTRUCTION, from Bravyi & Gosset Eq (17):

    |A^(x)2> = (1/2)(|00> + i|11>)  +  (e^{i pi/4}/2)(|01> + |10>)

so chi_2 = 2 EXACTLY, and pairing t qubits into t/2 pairs gives chi_t <= 2^{t/2} by taking one
of the two terms per pair. (The paper notes [15] achieves 2^{beta t} with beta ~ 0.47, and the
approximate/sparsified variant reaches 2^{gamma t} with gamma ~ 0.228 — this file implements the
EXACT pairing decomposition, which is the honest starting point and is verifiable against the
explicit state. The tighter decompositions are a later component and are NOT claimed here.)

EACH TERM IS A PRODUCT OF 2-QUBIT STABILIZER STATES, hence a stabilizer state on t qubits, which
is exactly the object my JIT kernel consumes.

CORRECTNESS GATE: the decomposition must reconstruct |A>^(x)t EXACTLY as a statevector at small
t. No downstream component may consume this until that passes.

Substrate: claude-fable-5, Whisper C5020. Creator directive: "build the solver!".
"""
import numpy as np

# |A> = (|0> + e^{i pi/4}|1>)/sqrt(2)
A_STATE = np.array([1.0, np.exp(1j * np.pi / 4)]) / np.sqrt(2)


def a_tensor(t):
    """Explicit |A>^(x)t. VERIFICATION ONLY — exponential, never on a solver path."""
    v = np.array([1.0 + 0j])
    for _ in range(t):
        v = np.kron(v, A_STATE)
    return v


# The two 2-qubit stabilizer terms of Eq (17), as explicit 4-vectors with their coefficients.
#   term 0:  coeff 1/2            state |00> + i|11>      (unnormalised)
#   term 1:  coeff e^{i pi/4}/2   state |01> + |10>       (unnormalised)
PAIR_TERMS = [
    (0.5 + 0j, np.array([1.0, 0.0, 0.0, 1j])),
    (np.exp(1j * np.pi / 4) / 2, np.array([0.0, 1.0, 1.0, 0.0])),
]


def pair_decomposition_terms(t):
    """Yield (coefficient, statevector) for each of the 2^{t/2} exact terms.

    VERIFICATION-SCALE ONLY: materialises 2^t amplitudes per term. The solver path will carry
    each term as a STABILIZER STATE (n, k, h, G, Gbar, Q, D, J) rather than a statevector; this
    generator exists to prove the decomposition is right before that representation is built.
    """
    npairs = t // 2
    odd = t % 2
    for mask in range(2 ** npairs):
        coeff = 1.0 + 0j
        vec = np.array([1.0 + 0j])
        for p in range(npairs):
            c, s = PAIR_TERMS[(mask >> p) & 1]
            coeff *= c
            vec = np.kron(vec, s)
        if odd:                       # a leftover qubit stays as |A> itself (a stabilizer state)
            vec = np.kron(vec, A_STATE)
        yield coeff, vec


def reconstruct(t):
    out = np.zeros(2 ** t, dtype=complex)
    for c, v in pair_decomposition_terms(t):
        out += c * v
    return out


def chi_exact(t):
    """Rank of THIS decomposition (not the optimal chi_t)."""
    return 2 ** (t // 2)


def self_test(verbose=True):
    """Gate: the decomposition must reproduce |A>^(x)t exactly."""
    npass = nfail = 0
    for t in range(1, 11):
        want = a_tensor(t)
        got = reconstruct(t)
        err = float(np.max(np.abs(want - got)))
        ok = err < 1e-12
        npass += ok
        nfail += (not ok)
        if verbose:
            print(f"    {'PASS' if ok else 'FAIL':>4}  t={t:>2}  chi={chi_exact(t):>5}  "
                  f"max|err| = {err:.2e}")
    return npass, nfail


if __name__ == "__main__":
    print("MAGIC-STATE DECOMPOSITION — component ① correctness gate\n")
    print("  |A^(x)2> = (1/2)(|00> + i|11>) + (e^{i pi/4}/2)(|01> + |10>)   [Bravyi-Gosset Eq 17]")
    print("  pairing t qubits -> chi = 2^{t/2} exact terms\n")
    p, f = self_test()
    print(f"\n  {p} passed, {f} failed")
    if f == 0:
        print("  ✅ GATE PASSED — the decomposition is exact and may be built on.")
        print(f"\n  scale check:  t=48 -> chi = {chi_exact(48):,}")
        print(f"                t=80 -> chi = {chi_exact(80):,}")
        print(f"  (the paper's SPARSIFIED rank at t=80 is 2^(0.23*80) = {2**(0.23*80):,.0f},")
        print("   so this exact decomposition is far larger and is a starting point, not the")
        print("   final algorithm — component ①b is the sparsification that closes that gap.)")
    else:
        print("  ⛔ GATE NOT PASSED.")
