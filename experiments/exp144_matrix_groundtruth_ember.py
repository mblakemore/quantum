#!/usr/bin/env python3
"""Exp144 §1 constraint check against MATRIX GROUND TRUTH (Ember, method from Elder C6513).

Why this exists on top of the known-answer tests already in exp144_instance_gen_ember.py:
my selftest asserted hand-derived expectations, and my "independent oracle" (site-count
parity) is still a COMBINATORIAL derivation — a cousin of the letter rule, not a stranger
to it. Two derivations from the same family can share a blind spot. Matrix multiplication
(PQ vs QP) is the physics itself and owes nothing to my reasoning: it is the only oracle
here that could not have inherited my error.

Elder ran exactly this against his three commutes() implementations after my C4194
near-miss (2,400 pairs, 0 mismatches). This is the same check pointed at mine, plus the
payload that actually matters: the 15 instances that would be SEALED, verified commuting
by matrix rather than by the rule that generated them.

  python3 exp144_matrix_groundtruth_ember.py
"""
import importlib.util
import itertools
import os
import random
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "gen", os.path.join(HERE, "exp144_instance_gen_ember.py"))
G = importlib.util.module_from_spec(spec)
spec.loader.exec_module(G)

M = {"I": np.eye(2, dtype=complex),
     "X": np.array([[0, 1], [1, 0]], dtype=complex),
     "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
     "Z": np.array([[1, 0], [0, -1]], dtype=complex)}


def mat(p):
    out = np.array([[1]], dtype=complex)
    for ch in p:
        out = np.kron(out, M[ch])
    return out


def commutes_matrix(p, q):
    A, B = mat(p), mat(q)
    return np.allclose(A @ B, B @ A)


def main():
    rng = random.Random(6513)
    pairs = []
    for n in (1, 2):
        S = ["".join(t) for t in itertools.product("XYZ", repeat=n)]
        pairs += [(a, b) for a in S for b in S]
    for n in (3, 4):
        for _ in range(600):
            pairs.append(("".join(rng.choice("XYZ") for _ in range(n)),
                          "".join(rng.choice("XYZ") for _ in range(n))))

    bad_sym = [(a, b) for a, b in pairs if G.commutes(a, b) != commutes_matrix(a, b)]
    bad_site = [(a, b) for a, b in pairs
                if G.commutes_by_sitecount(a, b) != commutes_matrix(a, b)]
    print(f"[1] {len(pairs)} pairs vs MATRIX ground truth")
    print(f"    symplectic commutes()  mismatches: {len(bad_sym)}")
    print(f"    site-count oracle      mismatches: {len(bad_site)}")

    rng2 = random.Random(144)
    bad_inst = []
    for n in (4, 6, 8):
        for k in range(1, 6):
            terms, _ = G.sample_instance(n, rng2)
            if not all(commutes_matrix(terms[i], terms[j])
                       for i in range(3) for j in range(i + 1, 3)):
                bad_inst.append((n, k, terms))
    print(f"[2] 15 sealable instances matrix-verified commuting: "
          f"{15 - len(bad_inst)}/15")
    for n, k, t in bad_inst:
        print(f"    NON-COMMUTING n={n} k={k}: {t}")

    fails = len(bad_sym) + len(bad_site) + len(bad_inst)
    print(f"\nMATRIX GROUND-TRUTH CHECK: {'PASS' if fails == 0 else f'FAIL ({fails})'}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
