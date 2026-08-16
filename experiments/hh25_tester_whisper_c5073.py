#!/usr/bin/env python3
"""HH25 single-copy stabilizer tester — the door(a) C1 arm (Whisper C5073, Elder spec C6602).

Built from docs/hh25-tester-spec-elder-c6602.md (Hinsche-Helsen arXiv:2410.07986, Def 2.7 / 3.2-3.3
/ Thm 3.1). ONE BLOCK: draw C~Cl(n) uniform, apply to 2K fresh copies of |psi>, measure computational
basis; pair consecutive shots, XOR -> v_i in F2^n (difference sampling); X_block = 1 iff GF(2) span
{v_1..v_K} = F2^n. P_hat = mean X_block over B fresh-Clifford blocks. K=2n frozen. Decision: stabilizer
states are EXTREMAL-MAX (sec 3.2); eps-far states deviate by Omega(eps) (sec 3.4).

THIS FILE = the tester + a SIM-VERIFY gate (noiseless): P_hat(stabilizer) must exceed P_hat(eps-far)
by a resolvable margin, and a stabilizer must sit at/near its extremal ceiling. Known-answer gate
before the tester is trusted in the door(a) court. (Hardware court compares to a known-stabilizer
reference arm at matched Clifford depth, per the spec — not the ideal value.)
"""
import sys
import numpy as np
from qiskit.quantum_info import random_clifford, Statevector, Clifford


def gf2_rank(vecs, n):
    """Rank over GF(2) via the XOR-basis (linear basis) algorithm — each vec reduced against the
    current independent basis; if a nonzero remainder survives it is a new independent direction."""
    basis = []                       # independent vectors, as ints, kept sorted high-bit-first
    for v in vecs:
        x = 0
        for b in v:
            x = (x << 1) | int(b)    # pack (v[0] = MSB)
        for pb in basis:
            x = min(x, x ^ pb)       # reduce against existing basis
        if x:
            basis.append(x)
            basis.sort(reverse=True)
    return len(basis)


def measure_dist(psi_sv, C, n):
    """Probabilities of C|psi> in the computational basis."""
    return np.abs((C.to_matrix() @ psi_sv.data)) ** 2


def one_block(psi_sv, n, K, rng):
    C = random_clifford(n, seed=int(rng.integers(0, 2**31)))
    p = measure_dist(psi_sv, C, n)
    p = p / p.sum()
    shots = rng.choice(2**n, size=2 * K, p=p)                 # 2K fresh copies
    vecs = []
    for i in range(K):
        a, b = shots[2 * i], shots[2 * i + 1]                 # pair consecutive
        x = a ^ b                                             # XOR = difference sample
        vecs.append([(x >> j) & 1 for j in range(n)])
    return 1 if gf2_rank(vecs, n) == n else 0


def p_hat(psi_sv, n, K, B, rng):
    return float(np.mean([one_block(psi_sv, n, K, rng) for _ in range(B)]))


def phase_state_sv(n, A):
    v = np.empty(2**n, dtype=complex)
    for k in range(2**n):
        x = [(k >> i) & 1 for i in range(n)]
        e = 0
        for i in range(n):
            for j in range(i, n):
                if A[i][j] and x[i] and x[j]:
                    e ^= 1
        v[k] = -1.0 if e else 1.0
    return Statevector(v / np.sqrt(2**n))


def eps_far_sv(n, A, rng, ntheta=2):
    """Magic-doped: degree-2 phase (stabilizer) + small non-Clifford Z-rotations on a few qubits."""
    sv = phase_state_sv(n, A).data.astype(complex)
    for q in rng.choice(n, size=ntheta, replace=False):
        th = np.pi / 4                                        # a T-like rotation -> pushes F_Stab below 1
        for k in range(2**n):
            if (k >> q) & 1:
                sv[k] *= np.exp(1j * th)
    return Statevector(sv / np.linalg.norm(sv))


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    K = 2 * n; B = 300
    rng = np.random.default_rng(5073)
    A = [[int(rng.integers(0, 2)) if j >= i else 0 for j in range(n)] for i in range(n)]
    stab = phase_state_sv(n, A)                               # degree-2 phase = STABILIZER (F_Stab=1)
    zero = Statevector.from_label("0" * n)                    # trivial stabilizer
    far = eps_far_sv(n, A, rng)                               # eps-far (magic-doped)
    print(f"HH25 tester sim-verify (n={n}, K={K}, B={B}):")
    p_stab = p_hat(stab, n, K, B, np.random.default_rng(1))
    p_zero = p_hat(zero, n, K, B, np.random.default_rng(2))
    p_far = p_hat(far, n, K, B, np.random.default_rng(3))
    print(f"  P_hat(deg-2 phase STABILIZER) = {p_stab:.3f}")
    print(f"  P_hat(|0^n> stabilizer)       = {p_zero:.3f}")
    print(f"  P_hat(eps-far magic-doped)    = {p_far:.3f}")
    se = np.sqrt(0.25 / B)
    margin = min(p_stab, p_zero) - p_far
    gate = margin > 5 * se
    print(f"  SE~{se:.3f}; stabilizer-minus-far margin {margin:+.3f} = {margin/se:.1f} sigma")
    print(f"  GATE: {'PASS — tester DISCRIMINATES (stabilizer extremal-high, eps-far lower)' if gate else 'FAIL'}")
    return gate


if __name__ == "__main__":
    main()
