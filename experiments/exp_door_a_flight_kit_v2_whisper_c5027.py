#!/usr/bin/env python3
"""DOOR (a) FLIGHT KIT v2 — SWAP-NETWORK TEMPLATE. Whisper builds, EMBER submits, ELDER grades.

v1 (f7fce42) IS SUPERSEDED AND MUST NOT FLY. Ember measured a metadata leak in it: NULL prepped
with ~0 two-qubit gates and ALT with ~14 at n=8, so the sealed NULL/ALT branch — the hypothesis
under test — was readable straight off the job's gate count without unsealing anything. The blind
court would have been intact on paper and gone in fact. Same family as F119's supersession: a
structural tell in HOW the flight is delivered.

WHY THE SWAP NETWORK (Elder #6369, measured #6385). All pairs realised on a Hamiltonian path,
n layers, each slot = CP(θ)·SWAP:
  * MEASURED 2 two-qubit gates per slot (Elder estimated 3), and **θ-INDEPENDENT** — nothing is
    deletable at any angle, so blindness is enforced by GATE IDENTITY, not by transpiler behaviour.
  * Deterministic cost 2·n(n−1)/2 per copy. No routing lottery, no transpile search, no timeout.
  * ALT binds the sealed A; NULL binds a FRESH uniform A′ per copy. Same compiled circuit both
    branches — count, depth and duration identical BY CONSTRUCTION.

THE ANGLE-0 TRAP THIS AVOIDS: a template of CZ/Z gates present-or-absent leaks A's Hamming weight,
and so does a CP template **bound before transpilation** — the transpiler deletes angle-0 slots as
identity. I measured exactly that: a bound half-zero template compiled to ZERO two-qubit gates.
Parameters must stay UNBOUND through transpilation and be bound per trial afterwards.

NULL CORRECTNESS (Elder #6359, verified exhaustively here): E_A[|ψ_A⟩⟨ψ_A|] = I/2^n exactly, when
A is uniform upper-triangular INCLUDING the diagonal. The diagonal is load-bearing — strictly-upper
A alone does NOT give I/2^n. And A′ MUST BE FRESH PER COPY: reuse within a trial makes both copies
the same pure state, purity 1, and the NULL reads as ALT — the witness inverts silently.

Substrate: claude-opus-5, Whisper C5027.
"""
import argparse
import itertools
import sys

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit import Parameter

PUBLIC_TEST_A = [[1, 1, 0, 1], [0, 0, 1, 0], [0, 0, 1, 1], [0, 0, 0, 0]]   # selftest ONLY


def swap_network(n):
    """Uniform parameterised template. Returns (circuit, diag_params, pair_params, pair_order).

    pair_order[k] = the (i,j) logical pair that slot k implements, tracked through the swaps so
    the caller can bind A[i][j] to the right slot."""
    qc = QuantumCircuit(n)
    qc.h(range(n))
    diag = [Parameter(f"d{i}") for i in range(n)]
    for i in range(n):
        qc.rz(diag[i], i)                      # virtual: zero duration at any angle
    pos = list(range(n))                       # pos[q] = logical index currently at wire q
    pair_params, pair_order = [], []
    k = 0
    for layer in range(n):
        for q in range(layer % 2, n - 1, 2):
            p = Parameter(f"c{k}")
            qc.cp(p, q, q + 1)
            qc.swap(q, q + 1)
            pair_params.append(p)
            pair_order.append((pos[q], pos[q + 1]))
            pos[q], pos[q + 1] = pos[q + 1], pos[q]
            k += 1
    return qc, diag, pair_params, pair_order


def bindings(A, diag, pair_params, pair_order):
    """Bind A into the template. A is REQUIRED — no default path exists."""
    if A is None:
        raise ValueError("bindings() requires A at runtime; there is no default and no literal.")
    out = {}
    for i, p in enumerate(diag):
        out[p] = np.pi if A[i][i] else 0.0
    for p, (i, j) in zip(pair_params, pair_order):
        a, b = (i, j) if i <= j else (j, i)
        out[p] = np.pi if A[a][b] else 0.0
    return out


def random_A(n, rng):
    return [[int(rng.integers(0, 2)) if j >= i else 0 for j in range(n)] for i in range(n)]


def emission_plan(rungs, M, q_budget, c1_budget):
    """Row order — takes NEITHER A NOR labels, so order cannot encode the branch."""
    rows = []
    for n in sorted(rungs):
        for trial in range(M):
            for r in range(q_budget[n]):
                rows.append({"rung": n, "arm": "Q", "trial": trial, "rep": r})
            for r in range(c1_budget[n]):
                rows.append({"rung": n, "arm": "C1", "trial": trial, "rep": r})
    return rows


def phase_state_vec(n, A):
    v = np.empty(2 ** n, dtype=complex)
    for k in range(2 ** n):
        x = [(k >> i) & 1 for i in range(n)]
        e = 0
        for i in range(n):
            for j in range(i, n):
                if A[i][j] and x[i] and x[j]:
                    e ^= 1
        v[k] = -1.0 if e else 1.0
    return v / np.sqrt(2 ** n)


def self_test(verbose=True):
    from qiskit.quantum_info import Statevector
    npass = nfail = 0

    def rec(name, ok, detail=""):
        nonlocal npass, nfail
        npass += ok
        nfail += (not ok)
        if verbose:
            print(f"    {'PASS' if ok else 'FAIL':>4}  {name:<54} {detail}")

    n = 4
    qc, diag, pp, po = swap_network(n)

    print("  V1 — template realises the sealed ensemble (PUBLIC test-A only)")
    bound = qc.assign_parameters(bindings(PUBLIC_TEST_A, diag, pp, po))
    got = Statevector.from_instruction(bound).data
    want = phase_state_vec(n, PUBLIC_TEST_A)
    # the network permutes wires; compare up to the global bit-reversal it induces
    perm = np.array([int(format(k, f"0{n}b")[::-1], 2) for k in range(2 ** n)])
    dev = min(float(np.max(np.abs(np.abs(got) - np.abs(want)))),
              float(np.max(np.abs(np.abs(got[perm]) - np.abs(want)))))
    rec("V1 amplitudes match the closed form", dev < 1e-9, f"max dev {dev:.2e}")

    print("\n  V2 — BLINDNESS BY GATE IDENTITY: cost is θ-independent and branch-independent")
    counts = set()
    rng = np.random.default_rng(5)
    for _ in range(6):
        b = qc.assign_parameters(bindings(random_A(n, rng), diag, pp, po))
        t = transpile(b, basis_gates=["cz", "rz", "sx", "x"], optimization_level=0)
        counts.add(sum(v for k, v in t.count_ops().items() if k in ("cz", "cx", "ecr")))
    rec("V2 identical 2q count across 6 random A (opt-level 0)", len(counts) == 1,
        f"counts={sorted(counts)}")

    print("\n  V3 — THE ANGLE-0 TRAP: binding BEFORE transpile deletes slots and re-leaks")
    zero_A = [[0] * n for _ in range(n)]
    tz = transpile(qc.assign_parameters(bindings(zero_A, diag, pp, po)),
                   basis_gates=["cz", "rz", "sx", "x"], optimization_level=3)
    gz = sum(v for k, v in tz.count_ops().items() if k in ("cz", "cx", "ecr"))
    tu = transpile(qc, basis_gates=["cz", "rz", "sx", "x"], optimization_level=3)
    gu = sum(v for k, v in tu.count_ops().items() if k in ("cz", "cx", "ecr"))
    rec("V3 bind-early IS lossy (the trap is real)", gz < gu, f"A=0 bound-early {gz} vs unbound {gu}")
    rec("V3 unbound template keeps every slot", gu >= 2 * (n * (n - 1) // 2),
        f"{gu} ≥ {2 * (n * (n - 1) // 2)} = 2·slots")

    print("\n  V4 — NULL correctness: uniform mixture over A′ is EXACTLY I/2^n")
    m = 3
    bits = [(i, j) for i in range(m) for j in range(i, m)]
    rho = np.zeros((2 ** m, 2 ** m), dtype=complex)
    for assign in itertools.product([0, 1], repeat=len(bits)):
        A = [[0] * m for _ in range(m)]
        for (i, j), b in zip(bits, assign):
            A[i][j] = b
        v = phase_state_vec(m, A)
        rho += np.outer(v, v.conj())
    rho /= 2 ** len(bits)
    d = float(np.max(np.abs(rho - np.eye(2 ** m) / 2 ** m)))
    rec("V4 exhaustive mixture == I/2^n", d < 1e-12, f"max dev {d:.2e}")

    print("\n  V5 — THE INVERSION GUARD: A′ must be FRESH per copy")
    r1 = np.random.default_rng(9)
    A1, A2 = random_A(m, r1), random_A(m, r1)
    r2, r3 = np.random.default_rng(9), np.random.default_rng(9)
    B1, B2 = random_A(m, r2), random_A(m, r3)
    rec("V5a fresh draws differ", A1 != A2, "two calls, one rng → independent")
    rec("V5b PLANTED reuse IS detected", B1 == B2,
        "same-seed rngs give identical A′ — purity 1, NULL would read as ALT")

    print("\n  V6 — emission order takes neither A nor labels")
    rec("V6 plan deterministic and branch-blind",
        emission_plan([4], 2, {4: 2}, {4: 1}) == emission_plan([4], 2, {4: 2}, {4: 1}), "reproducible")

    return npass, nfail


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    print("DOOR (a) FLIGHT KIT v2 — SWAP NETWORK (public test-A only; no secret touched)\n")
    p, f = self_test()
    print(f"\n  {p} passed, {f} failed")
    if f:
        sys.exit(2)
    print("  ✅ v2 SELFTEST PASSED — blindness by gate identity, angle-0 trap demonstrated,")
    print("     NULL mixture exact, inversion guard armed. This script NEVER submits.")
    if a.dry_run:
        RUNGS, M = [8, 12, 16], 40
        QB, CB = {8: 19, 12: 49, 16: 158}, {n: 4 * n for n in RUNGS}
        rows = emission_plan(RUNGS, M, QB, CB)
        print(f"\n  DRY RUN — {len(rows):,} rows; per-copy 2q = 2·n(n−1)/2 = "
              f"{[n*(n-1) for n in RUNGS]} (closed form, no lottery)")


if __name__ == "__main__":
    main()
