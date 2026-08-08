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


# ─────────────────────────────────────────────────────────────────────────────
# flight.json EMITTER — CONTRACT v2 (Elder #6352 as amended at #6361 point 2)
#
# v2 amendment, which was MY objection and Elder ratified it: the kit emits RAW 2n-BIT STRINGS.
# The grader derives accept/reject via the frozen parity rule, so that rule lives in EXACTLY ONE
# FILE. A post-processing convention duplicated across emitter and grader can drift, and drift
# between two internally-consistent files is undetectable. Raw strings are also strictly more
# information: the outcome distribution stays auditable instead of collapsing to one bit.
# ─────────────────────────────────────────────────────────────────────────────
def emit_flight_json(rung_results, window_id_by_rung):
    """Assemble contract-v2 flight.json.

    rung_results[n] = {"Q":  [trial][rep] -> raw 2n-bit string,
                       "C1": [trial][rep] -> {"basis_spec": [...], "outcome_bitstring": "..."}}
    Trial order IS the sealed order, so unsealing aligns with no mapping table.
    NOTHING here reads A or a label — the emitter cannot leak what it never receives.
    """
    out = {}
    for n, res in sorted(rung_results.items()):
        if n not in window_id_by_rung:
            raise ValueError(f"rung {n}: window_id REQUIRED — the grader refuses on mismatch, so "
                             f"an absent one must fail here rather than be invented downstream.")
        q, c1 = res["Q"], res["C1"]
        for t, trial in enumerate(q):
            for s in trial:
                if len(s) != 2 * n or set(s) - {"0", "1"}:
                    raise ValueError(f"rung {n} trial {t}: Q record must be a raw {2*n}-bit string")
        out[str(n)] = {"window_id": window_id_by_rung[n], "Q": q, "C1": c1,
                       "contract": "v2-raw-bitstrings"}
    return out


def _emitter_selftest(verbose=True):
    npass = nfail = 0

    def rec(name, ok, detail=""):
        nonlocal npass, nfail
        npass += ok
        nfail += (not ok)
        if verbose:
            print(f"    {'PASS' if ok else 'FAIL':>4}  {name:<54} {detail}")

    n, M = 4, 3
    rr = {n: {"Q": [["0" * (2 * n)] * 2 for _ in range(M)],
              "C1": [[{"basis_spec": [0] * n, "outcome_bitstring": "0" * n}] for _ in range(M)]}}
    j = emit_flight_json(rr, {n: "W1"})
    rec("E1 shape: per-rung key, window_id, contract tag",
        set(j["4"]) == {"window_id", "Q", "C1", "contract"} and j["4"]["contract"] == "v2-raw-bitstrings",
        f"keys={sorted(j['4'])}")
    rec("E2 Q rows are RAW 2n-bit strings (not accept/reject)",
        all(len(s) == 2 * n for tr in j["4"]["Q"] for s in tr), f"width {2*n}")

    try:
        emit_flight_json(rr, {})
        rec("E3 missing window_id REFUSES", False, "it did not raise")
    except ValueError:
        rec("E3 missing window_id REFUSES", True, "cannot be invented downstream")

    bad = {n: {"Q": [[("0" * n)]], "C1": rr[n]["C1"]}}          # planted: half-width record
    try:
        emit_flight_json(bad, {n: "W1"})
        rec("E4 PLANTED wrong-width record is CAUGHT", False, "it did not raise")
    except ValueError:
        rec("E4 PLANTED wrong-width record is CAUGHT", True, "an accept/reject bit would look like this")
    return npass, nfail


# ─────────────────────────────────────────────────────────────────────────────
# MEASUREMENT CIRCUITS — the gap Elder found by reading the v2 source (#6398).
# v1 carried these; the v2 rewrite ported the template, bindings, plan and emitter and DROPPED
# them, so v2 could prepare a state and shape results but could not build what gets submitted.
#
# THE PERMUTATION POINT, gated below because it is silent if wrong: the swap network permutes
# wires. Both copies run the SAME network, so wire i holds the SAME logical qubit in both halves
# and the permutation CANCELS in the transversal Bell pairing. If it did not, ALT would stop
# accepting with probability 1 — which is exactly what Q1 checks.
# ─────────────────────────────────────────────────────────────────────────────
def q_circuit(n, label, A, rng):
    """Q arm: two copies on 2n wires, then a transversal Bell measurement (destructive SWAP).
    ALT (label=1) binds the sealed A in BOTH copies. NULL (label=0) binds a FRESH A' per copy."""
    tmpl, diag, pp, po = swap_network(n)
    full = QuantumCircuit(2 * n, 2 * n)
    for half in (0, n):
        A_use = A if label == 1 else random_A(n, rng)      # FRESH per copy — the V5 pin
        full.compose(tmpl.assign_parameters(bindings(A_use, diag, pp, po)),
                     range(half, half + n), inplace=True)
    for i in range(n):
        full.cx(i, n + i)
        full.h(i)
    full.measure(range(2 * n), range(2 * n))
    return full


def c1_circuit(n, label, A, rng):
    """C1 arm: ONE copy, measured in a FRESH random Pauli basis. Delivery fence: basis redrawn
    per circuit, submitted at shots=1, never batched on a fixed basis (the F119 defect)."""
    tmpl, diag, pp, po = swap_network(n)
    qc = QuantumCircuit(n, n)
    A_use = A if label == 1 else random_A(n, rng)
    qc.compose(tmpl.assign_parameters(bindings(A_use, diag, pp, po)), range(n), inplace=True)
    basis = rng.integers(0, 3, size=n)
    for q in range(n):
        if basis[q] == 1:
            qc.h(q)
        elif basis[q] == 2:
            qc.sdg(q)
            qc.h(q)
    qc.measure(range(n), range(n))
    return qc, [int(b) for b in basis]


def _circuit_selftest(verbose=True):
    """NOTE ON THE PARITY RULE: it appears HERE, in a test, computed independently — it does NOT
    appear in the emitter, which ships raw strings per contract v2. A second instrument checking
    the same quantity is the discipline; a second instrument DERIVING the shipped value is drift."""
    from qiskit.quantum_info import Statevector
    npass = nfail = 0

    def rec(name, ok, detail=""):
        nonlocal npass, nfail
        npass += ok
        nfail += (not ok)
        if verbose:
            print(f"    {'PASS' if ok else 'FAIL':>4}  {name:<54} {detail}")

    n = 3
    rng = np.random.default_rng(4242)

    def accept_prob(qc):
        sv = Statevector.from_instruction(qc.remove_final_measurements(inplace=False))
        p = np.abs(sv.data) ** 2
        tot = 0.0
        for k, amp in enumerate(p):
            if amp < 1e-15:
                continue
            b = format(k, f"0{2*n}b")[::-1]
            singlets = sum(1 for i in range(n) if b[i] == "1" and b[n + i] == "1")
            if singlets % 2 == 0:
                tot += amp
        return tot

    A = random_A(n, rng)
    pa = accept_prob(q_circuit(n, 1, A, rng))
    rec("Q1 ALT accepts with probability 1 (permutation CANCELS)", abs(pa - 1.0) < 1e-9,
        f"P(accept)={pa:.12f}")

    ps = [accept_prob(q_circuit(n, 0, None, rng)) for _ in range(40)]
    want = 0.5 + 2.0 ** (-(n + 1))
    rec("Q2 NULL averages 1/2 + 2^-(n+1)", abs(float(np.mean(ps)) - want) < 0.05,
        f"mean {float(np.mean(ps)):.4f} vs {want:.4f}")

    qc = q_circuit(n, 1, A, rng)
    rec("Q3 Q circuit is 2n wires, all measured",
        qc.num_qubits == 2 * n and qc.num_clbits == 2 * n, f"{qc.num_qubits}q/{qc.num_clbits}c")

    bases = [c1_circuit(n, 0, None, rng)[1] for _ in range(6)]
    rec("Q4 C1 basis redrawn per circuit (delivery fence)", len(set(map(tuple, bases))) > 1,
        f"{len(set(map(tuple, bases)))} distinct in 6")

    c, _ = c1_circuit(n, 1, A, rng)
    rec("Q5 C1 is ONE copy", c.num_qubits == n, f"{c.num_qubits} wires")
    return npass, nfail


def c1_record(raw_counts_key, n):
    """Normalise a qiskit outcome string to QUBIT ORDER: result[i] IS qubit i.

    WHY THIS EXISTS (Elder #6403): the Q accept bit is endianness-INVARIANT for the halves layout
    (full reversal maps pair (i,n+i) to (n-1-i) with components swapped, and the singlet marker
    (1,1) is symmetric) — so Q needs no convention. **C1 IS NOT INVARIANT**: basis_spec[i] must
    meet the outcome of QUBIT i, and qiskit returns the string with qubit 0 RIGHTMOST. Rather than
    document a reversal for the decoder to apply correctly, the kit emits qubit order so there is
    no convention left to get wrong. A convention that must be remembered is a convention that
    will eventually be forgotten."""
    return raw_counts_key[::-1]


def _c1_endianness_selftest(verbose=True):
    from qiskit_aer import AerSimulator
    npass = nfail = 0

    def rec(name, ok, detail=""):
        nonlocal npass, nfail
        npass += ok
        nfail += (not ok)
        if verbose:
            print(f"    {'PASS' if ok else 'FAIL':>4}  {name:<54} {detail}")

    n = 4
    for target in (0, 2, 3):
        qc = QuantumCircuit(n, n)
        qc.x(target)                       # ONLY qubit `target` is |1>
        qc.measure(range(n), range(n))
        key = next(iter(AerSimulator().run(qc, shots=1).result().get_counts()))
        rec(f"C1-E qubit {target} lands at index {target} in qubit order",
            c1_record(key, n)[target] == "1" and key[::-1][target] == "1",
            f"raw '{key}' -> qubit-order '{c1_record(key, n)}'")
    return npass, nfail


# ─────────────────────────────────────────────────────────────────────────────
# C1 ARM v3 — HH25 AS THE PAPER WRITES IT (Elder's primary-text read, #6410)
#
# WHAT WAS WRONG: c1_circuit measured each qubit in a fresh LOCAL Pauli basis — the folk
# product-basis strategy. HH25's tester samples a uniformly random ENTANGLING Clifford C from
# Cl(n), measures in the computational basis of that frame, and the statistic is COMPUTATIONAL
# DIFFERENCE SAMPLING: two copies measured in the SAME frame, output a⊕b ∈ F₂ⁿ, decided by a
# linear-dependence/spanning test. Local rotations cannot express it. Flying the local version
# would measure the separation against a SUB-BEST attack — the F119 mechanism, kill criterion 1.
#
# THE FENCE RE-SCOPING (Elder's ruling, this row is mine): the F119 fence said "fresh randomness
# per copy, no fixed-basis batching" — but HH25 REQUIRES one C across the copies of a round;
# differences taken across different frames are meaningless. The fence's purpose was blocking a
# PREPARATION-side artifact. So: **fresh PREPARATION randomness per copy (NULL A′ fresh per copy),
# and the MEASUREMENT schedule follows the pre-registered HH25 round structure — same public
# random C within a round, fresh C per round.** C is public randomness; it touches nothing sealed.
#
# COPY ACCOUNTING: each difference sample consumes 2 COPIES. C1 remains k=0 memory — the two
# copies are measured separately and XORed CLASSICALLY, no quantum memory anywhere.
# I own the circuits and the round records; the difference→rank→spanning statistic is Elder's.
# ─────────────────────────────────────────────────────────────────────────────
def c1_round_circuits(n, label, A, rng, copies_per_round=2):
    """One HH25 round: draw C ~ Cl(n) ONCE, measure `copies_per_round` copies in that frame."""
    from qiskit.quantum_info import random_clifford
    C = random_clifford(n, seed=int(rng.integers(1 << 30)))
    tmpl, diag, pp, po = swap_network(n)
    out = []
    for _ in range(copies_per_round):
        qc = QuantumCircuit(n, n)
        A_use = A if label == 1 else random_A(n, rng)      # PREP randomness stays fresh per copy
        qc.compose(tmpl.assign_parameters(bindings(A_use, diag, pp, po)), range(n), inplace=True)
        qc.compose(C.to_circuit(), range(n), inplace=True)  # SAME frame this round.
        # to_circuit() NOT to_instruction(): the raw Clifford instruction is opaque to Aer
        # ('unknown instruction: Clifford') and would not have survived submission either.
        # Found by RUNNING the cross-file agreement rather than by reading the kit.
        qc.measure(range(n), range(n))
        out.append(qc)
    return out, C


def c1_round_record(clifford_spec, raw_keys, n):
    """Contract v3: per-ROUND record. Outcomes in QUBIT ORDER (the C1-E fix carries)."""
    return {"clifford_spec": clifford_spec,
            "outcomes": [c1_record(k, n) for k in raw_keys],
            "copies_consumed": len(raw_keys)}


def _c1_v3_selftest(verbose=True):
    npass = nfail = 0

    def rec(name, ok, detail=""):
        nonlocal npass, nfail
        npass += ok
        nfail += (not ok)
        if verbose:
            print(f"    {'PASS' if ok else 'FAIL':>4}  {name:<54} {detail}")

    n = 4
    rng = np.random.default_rng(2026)
    A = random_A(n, rng)

    r1, C1_ = c1_round_circuits(n, 1, A, rng)
    r2, C2_ = c1_round_circuits(n, 1, A, rng)
    rec("R1 SAME Clifford frame within a round", len(r1) == 2 and C1_ == C1_, "one C, two copies")
    rec("R2 FRESH Clifford across rounds", C1_ != C2_, "differences need per-round frames")

    nulls = [c1_round_circuits(n, 0, None, rng)[0] for _ in range(4)]
    rec("R3 NULL prep randomness still fresh PER COPY",
        len({str(c.data) for rr in nulls for c in rr}) > 1,
        "preparation fence intact under the re-scoping")

    rec("R4 each difference sample consumes 2 COPIES",
        c1_round_record("spec", ["0000", "0000"], n)["copies_consumed"] == 2,
        "k=0 memory: measured separately, XORed classically")

    frames = {str(c1_round_circuits(n, 1, A, rng)[1]) for _ in range(5)}
    rec("R5 five rounds give five distinct frames", len(frames) == 5, f"{len(frames)} distinct")

    recd = c1_round_record("spec", ["0001"], n)
    rec("R6 outcomes emitted in QUBIT ORDER", recd["outcomes"][0] == "1000",
        "raw '0001' -> '1000', qubit 0 at index 0")
    return npass, nfail
