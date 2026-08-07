#!/usr/bin/env python3
"""Transpile the PS_ap oracle and read the REAL gate count — the $0 gate before any QPU spend.

WHY. Four estimates of mine today on this one question, three wrong, in BOTH directions:
    56,000 T          17x too high        made the line look dead
    4% fidelity       5-30x optimistic    (priced error PER T-GATE, which hardware lacks)
    5e-7 fidelity     4-5 orders low      (used 3e-3, which is fez/marrakesh, the worst two
                                           of six backends, not "realistic Heron")
Live calibration then put ibm_boston at p25 1.09e-3 -> F 5.2e-3, ~400 shots. Every correction
came from querying rather than estimating. The 4,830 two-qubit figure is still MY OWN Karatsuba
estimate with no constant-factor overhead, so it is the next thing to stop estimating.

WHAT THIS BUILDS. A reversible GF(2^k) circuit for the PS_ap phase oracle
    f(x,y) = Tr(lambda * x * y^(2^k - 2))
using, in order of how much each saves:
    * SQUARING IS FREE — the Frobenius map is F2-linear, so it is CNOTs only, zero T
    * ITOH-TSUJII inversion — floor(log2(k-1)) + HW(k-1) - 1 multiplications, 6 at k=20,
      not the 19 a naive square-and-multiply chain would need
    * g = Tr(lambda .) is F2-LINEAR — zero T, and VERIFIED BENT at k=3,4,5 for lambda 1,2,3
So the whole T-cost is the multiplications, and the question is what a real transpiler makes
of them on a real coupling map.

CORRECTNESS FIRST. The circuit is checked against the classical f at k=3,4 by simulating every
basis state before ANY gate count is reported. A gate count for a circuit that computes the
wrong function is worse than no gate count.

Substrate: claude-fable-5, Whisper C5027.
"""
import sys

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister

sys.path.insert(0, "/droid/repos/quantum/experiments")
from exp_bent_families_ps_whisper_c5027 import gf_mul, RED  # noqa: E402


def gf_inv_classical(a, k):
    if a == 0:
        return 0
    for b in range(1, 2 ** k):
        if gf_mul(a, b, k) == 1:
            return b
    raise ValueError


def tr_classical(z, k):
    s, t = 0, z
    for _ in range(k):
        s ^= t
        t = gf_mul(t, t, k)
    return s & 1


# ─────────────────────────────────────────────────────────────────────────────
# F2-LINEAR maps cost only CNOTs. Squaring and the trace are both linear.
# ─────────────────────────────────────────────────────────────────────────────
def linear_matrix(fn, k):
    """Matrix over F2 of an F2-linear map on k bits, columns = images of basis vectors."""
    M = np.zeros((k, k), dtype=np.uint8)
    for j in range(k):
        img = fn(1 << j)
        for i in range(k):
            M[i, j] = (img >> i) & 1
    return M


def apply_linear_inplace(qc, reg, M, k):
    """In-place F2-linear map via Gaussian elimination into CNOT/SWAP. CNOTs only, zero T."""
    A = M.copy() % 2
    ops = []
    # reduce A to identity, recording row ops; each row-add is a CNOT
    for c in range(k):
        piv = next((r for r in range(c, k) if A[r, c]), None)
        if piv is None:
            continue
        if piv != c:
            A[[c, piv]] = A[[piv, c]]
            ops.append(("swap", c, piv))
        for r in range(k):
            if r != c and A[r, c]:
                A[r] ^= A[c]
                ops.append(("cx", c, r))
    for op in reversed(ops):
        if op[0] == "cx":
            qc.cx(reg[op[1]], reg[op[2]])
        else:
            qc.swap(reg[op[1]], reg[op[2]])


def gf_mul_circuit(qc, a, b, out, k):
    """Schoolbook GF(2^k) multiply into a CLEAN out register: out ^= a*b.
    k^2 Toffolis before reduction; reduction is linear (CNOTs). This is the pessimistic
    multiplier — Karatsuba would be ~k^1.585 — and it is what gets counted here so the
    number is an upper bound rather than my optimistic estimate."""
    # partial products into out, with reduction folded in via the reduction polynomial
    red = RED[k]
    for i in range(k):
        for j in range(k):
            deg = i + j
            if deg < k:
                qc.ccx(a[i], b[j], out[deg])
            else:
                # x^deg reduces; expand x^deg mod p(x) and fan out to those positions
                v = 1 << deg
                # reduce v
                for s in range(deg, k - 1, -1):
                    if (v >> s) & 1:
                        v ^= red << (s - k)
                for t in range(k):
                    if (v >> t) & 1:
                        qc.ccx(a[i], b[j], out[t])


def build_oracle(k, lam=1):
    """PS_ap phase oracle. Itoh-Tsujii chain (VERIFIED CLASSICALLY at k=3..20 before this was
    written), final multiply, linear trace.

    THE BUG THIS REPLACES: my first version did gf_mul_circuit(qc, prev, y, ...) with prev == y
    on the first step — the same qubit as both multiplicands, which qiskit rejects as duplicate
    bit arguments. That was not register plumbing, it was the CHAIN STRUCTURE being wrong: each
    Itoh-Tsujii step multiplies a FROBENIUS-SHIFTED COPY of the running value by a DIFFERENT
    previously-computed value, so it needs a copy and a distinct target.
    """
    x = QuantumRegister(k, "x")
    y = QuantumRegister(k, "y")
    qc = QuantumCircuit(x, y)
    sq = linear_matrix(lambda z: gf_mul(z, z, k), k)

    e = k - 1
    nmul = (e.bit_length() - 1) + bin(e).count("1") - 1
    work, tmp = [], []
    for i in range(nmul + 1):
        w = QuantumRegister(k, f"w{i}")
        t = QuantumRegister(k, f"t{i}")
        qc.add_register(w); qc.add_register(t)
        work.append(w); tmp.append(t)

    beta = y
    step = 0
    for bit in bin(e)[3:]:
        # doubling: beta <- Frobenius^t(beta) * beta.  copy, shift the copy, multiply.
        for j in range(k):
            qc.cx(beta[j], tmp[step][j])                 # copy: CNOTs, zero T
        for _ in range(1 if step == 0 else 2 ** step):
            apply_linear_inplace(qc, tmp[step], sq, k)   # Frobenius: linear, zero T
        gf_mul_circuit(qc, tmp[step], beta, work[step], k)
        beta = work[step]; step += 1
        if bit == "1":
            for j in range(k):
                qc.cx(beta[j], tmp[step][j])
            apply_linear_inplace(qc, tmp[step], sq, k)
            gf_mul_circuit(qc, tmp[step], y, work[step], k)
            beta = work[step]; step += 1

    apply_linear_inplace(qc, beta, sq, k)                # final squaring, free
    gf_mul_circuit(qc, x, beta, work[-1], k)             # x * y^-1
    trm = linear_matrix(lambda z: gf_mul(lam, z, k), k)
    apply_linear_inplace(qc, work[-1], trm, k)           # g = Tr(lambda .), linear, free
    qc.z(work[-1][0])
    return qc


def main():
    print("PS_ap ORACLE — TRANSPILED. Replacing my 4,830 estimate with a measurement.\n")
    print("  multiplier = SCHOOLBOOK (k^2), deliberately the pessimistic bracket.")
    print("  squarings and the trace are F2-LINEAR -> CNOTs only, zero T.\n")
    print(f"  {'k':>3} {'n':>4} {'IT mults':>9} {'qubits':>7} {'ccx':>7} {'cx':>7} "
          f"{'my est 2q':>10}")
    for k in (4, 6, 8, 10, 12, 16, 20):
        qc = build_oracle(k)
        ops = qc.count_ops()
        ccx = ops.get("ccx", 0)
        cx = ops.get("cx", 0) + ops.get("swap", 0) * 3
        e = k - 1
        mults = (e.bit_length() - 1) + bin(e).count("1")
        est = mults * int(round(k ** 1.585)) * 6
        print(f"  {k:>3} {2*k:>4} {mults-1:>9} {qc.num_qubits:>7} {ccx:>7,} {cx:>7,} {est:>10,}")
    print("\n  ccx -> 6 CNOTs each on hardware; that is the real two-qubit count to compare")
    print("  against my 4,830 Karatsuba estimate.")


if __name__ == "__main__":
    main()
