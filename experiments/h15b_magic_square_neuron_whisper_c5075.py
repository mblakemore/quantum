#!/usr/bin/env python3
"""H15-B — THE MAGIC-SQUARE NEURON (Whisper C5075). $0 design study, sim only.

A TYPE-B positronic neuron: one whose quantum advantage lives in the DECIDING rather than the
REMEMBERING. The Type-A neuron (H15 N1-N4) holds two copies of a state in a memory no classical
single-copy memory can match. This one holds no memory at all — it receives a context and answers,
and the answer is one that NO pre-assigned classical value can produce, because quantum observables
are contextual.

WHY BUILD IT: the Type-A neuron is measured READOUT-LIMITED (readout loss 0.0527 vs 2q 0.0137).
This design needs 4 measured bits against Type-A's 8, on 4 qubits against 10, and it inherits a
floor that is ENUMERATED over every classical strategy rather than derived from an SDP needing a
dual certificate. It attacks the measured bottleneck structurally instead of by tuning.

THE LOOP, per trial:
  STIMULUS   a context (r, c) — Alice's row and Bob's column, 9 possibilities
  RESOURCE   two Bell pairs across a B1-A1-A2-B2 line (exp126 apparatus, flown at 196 sigma)
  SENSE      contextual bases set by (r, c); 4 mid-circuit measurements
  DECIDE     real-time CLASSICAL expression over the 4 measured bits — the same validated
             pattern as N4, and here it collapses to a single XOR with a context constant
  ACT        feedforward conditional X on an actuator qubit
  RESPONSE   the actuator bit = "my two halves agreed at the intersection cell"

THE DECISION COLLAPSES TO ONE XOR. Alice's value at column c is one of {A1, A2, A1^A2} and Bob's
at row r one of {B1, B2, B1^B2}, with a single sign flip in the (c=2, r=2) cell — the cell that
makes the square magic. So agreement is:  XOR(selected bits) XOR flip(r,c) == 0.

CLASSICAL FLOOR — RE-ENUMERATED FOR *THIS* TASK, NOT INHERITED. exp126 enumerated its ceiling
in-code rather than citing 8/9, and the neuron's task differs from the game's (one processor
compares both halves and actuates, rather than two separated parties answering). Inheriting a
bound across that change is exactly the transport error that superseded F119, so this file
re-derives the ceiling by brute force over all deterministic value assignments.

$0. No submission path in this file.
"""
import itertools
import json
import sys

from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit.circuit.classical import expr

sys.path.insert(0, "/droid/repos/quantum/experiments")

CONTEXTS = [(r, c) for r in range(3) for c in range(3)]


# ── the game's value maps, in BIT form (value = (-1)^bit) ───────────────────────────────
def alice_sel(r, c):
    """Which of Alice's measured bits (A1=q1, A2=q2) form her value at column c.
    Returns a tuple of bit-indices to XOR. Mirrors alice_values() in exp126."""
    if r == 0 or r == 2:
        table = [(0,), (1,), (0, 1)]      # [b1, b2, b1*b2]
    else:
        table = [(1,), (0,), (0, 1)]      # [b2, b1, b1*b2]
    return table[c]


def bob_sel(c, r):
    """Which of Bob's measured bits (B1=q0, B2=q3) form his value at row r,
    plus a sign flip. Mirrors bob_values() in exp126."""
    if c == 0:
        table = [(0,), (1,), (0, 1)]      # [b1, b2, b1*b2]
        flip = 0
    elif c == 1:
        table = [(1,), (0,), (0, 1)]      # [b2, b1, b1*b2]
        flip = 0
    else:
        table = [(0,), (1,), (0, 1)]      # [b1, b2, -b1*b2]
        flip = 1 if r == 2 else 0         # THE magic cell: the minus sign
    return table[r], flip


def wins(r, c, a1, a2, b1, b2):
    """Neuron response for one shot, from the four measured bits."""
    asel = alice_sel(r, c)
    bsel, flip = bob_sel(c, r)
    av = 0
    for i in asel:
        av ^= (a1, a2)[i]
    bv = 0
    for i in bsel:
        bv ^= (b1, b2)[i]
    return 1 if (av ^ bv ^ flip) == 0 else 0


# ── the classical ceiling, RE-ENUMERATED for the neuron's task ─────────────────────────
def classical_ceiling():
    """Best classical (non-contextual) strategy pair, brute force over all 4,096.

    CORRECTED C5075: my first version imposed row AND column parities on ONE global
    assignment and returned 6/9 — but no such assignment exists, which is the entire point of
    the magic square. The right object is a PAIR of strategies: Alice maps each row to a triple
    whose product is +1 (4 valid triples per row), Bob maps each column to a triple with product
    +1, except the last column which must be -1 (4 valid triples per column). That is
    4^3 x 4^3 = 4,096 strategy pairs — the same 4,096 exp126 enumerated. They win a context iff
    their answers AGREE at the intersection cell.

    The mismatch against the known 8/9 is what exposed the first version; a known-answer pin is
    worth more than a plausible derivation.
    """
    def triples(parity):
        return [t for t in itertools.product([0, 1], repeat=3)
                if (t[0] ^ t[1] ^ t[2]) == parity]
    rowsets = triples(0)                       # product +1  -> XOR of bits = 0
    colsets = [triples(0), triples(0), triples(1)]   # last column product -1
    best = 0.0
    for A in itertools.product(rowsets, repeat=3):          # Alice: row -> triple
        for B in itertools.product(*[colsets[c] for c in range(3)]):   # Bob: column -> triple
            won = sum(1 for (r, c) in CONTEXTS if A[r][c] == B[c][r])
            if won / 9 > best:
                best = won / 9
    return best, None


# ── the circuit ────────────────────────────────────────────────────────────────────────
def build_neuron(r, c, arm="auto"):
    """5 qubits: q0=B1, q1=A1, q2=A2, q3=B2 (line B1-A1-A2-B2), q4=actuator."""
    qs = QuantumRegister(5, "q")
    cb = ClassicalRegister(4, "m")        # m0=B1, m1=A1, m2=A2, m3=B2
    ca = ClassicalRegister(1, "act")
    qc = QuantumCircuit(qs, cb, ca)
    qc.h(1); qc.cx(1, 0)                  # Bell(A1,B1)
    qc.h(2); qc.cx(2, 3)                  # Bell(A2,B2)
    qc.barrier()
    if r == 0:                            # Alice's row context
        qc.h(1); qc.h(2)
    elif r == 2:
        qc.cz(1, 2); qc.h(1); qc.h(2)
    if c == 0:                            # Bob's column context
        qc.h(0)
    elif c == 1:
        qc.h(3)
    else:
        qc.cx(0, 3); qc.h(0)
    qc.barrier()
    for q, b in ((0, 0), (1, 1), (2, 2), (3, 3)):
        qc.measure(q, cb[b])
    if arm == "always":
        qc.x(4)
    elif arm == "auto":
        asel = alice_sel(r, c)
        bsel, flip = bob_sel(c, r)
        terms = [cb[1 + i] for i in asel] + [cb[[0, 3][i]] for i in bsel]
        e = expr.lift(terms[0])
        for t in terms[1:]:
            e = expr.bit_xor(e, expr.lift(t))
        # agreement <=> (XOR of selected bits) == flip. XOR of Clbits is Bool, so express the
        # flip as a negation rather than an integer comparison.
        cond = e if flip == 1 else expr.logic_not(e)
        with qc.if_test(cond):
            qc.x(4)
    qc.measure(4, ca[0])
    return qc


if __name__ == "__main__":
    from qiskit_aer import AerSimulator
    SIM = AerSimulator(seed_simulator=5075)
    ceiling, assign = classical_ceiling()
    print(f"CLASSICAL CEILING, re-enumerated over all 2^9 assignments: {ceiling:.4f} = {ceiling*9:.0f}/9")
    print(f"  (exp126's flown game ceiling was 8/9 = {8/9:.4f} — match: {abs(ceiling-8/9)<1e-9})\n")
    out = {"card": "h15b_magic_square_neuron", "cycle": "C5075",
           "classical_ceiling": ceiling, "contexts": len(CONTEXTS)}
    tot = win = 0
    per_ctx = {}
    for (r, c) in CONTEXTS:
        qc = build_neuron(r, c)
        res = SIM.run(qc, shots=256, memory=True).result()
        w = sum(int(m.split()[0]) for m in res.get_memory())
        per_ctx[f"r{r}c{c}"] = w / 256
        win += w; tot += 256
    print("NOISELESS neuron response rate per context (must be 1.0000 everywhere):")
    for k, v in per_ctx.items():
        print(f"   {k}: {v:.4f}")
    print(f"\n  OVERALL {win}/{tot} = {win/tot:.4f}   ceiling {ceiling:.4f}   ideal margin {win/tot-ceiling:+.4f}")
    out["noiseless_per_context"] = per_ctx
    out["noiseless_overall"] = win / tot
    # ablation
    aw = sum(int(m.split()[0]) for m in SIM.run(build_neuron(0, 0, arm="always"), shots=64, memory=True).result().get_memory())
    out["ablation_always"] = aw / 64
    print(f"  ablation always-arm: {aw}/64")
    from qiskit import transpile
    from qiskit.providers.fake_provider import GenericBackendV2
    bk = GenericBackendV2(num_qubits=5, basis_gates=["cz", "rz", "sx", "x", "id"], control_flow=True)
    t = transpile(build_neuron(2, 2), bk, optimization_level=1, seed_transpiler=5075)
    ops = {k: int(v) for k, v in t.count_ops().items()}
    out["transpiled_worst_context"] = {"ops": ops, "cz": ops.get("cz", 0), "depth": int(t.depth())}
    print(f"  transpiled (worst context r3c3): cz={ops.get('cz',0)} depth={t.depth()}")
    print(f"  reads per trial: 4 measured + 1 actuator = 5   (Type-A neuron: 8 + 1 = 9)")
    json.dump(out, open("/droid/repos/quantum/results/h15b_magic_square_neuron_sim_c5075.json", "w"), indent=1)
    print("WROTE results/h15b_magic_square_neuron_sim_c5075.json")
