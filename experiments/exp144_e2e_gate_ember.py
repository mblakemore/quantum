#!/usr/bin/env python3
"""Exp144 §6 PRE-FREEZE PATH-MATRIX GATE — seal → reveal-write → REAL grader verify.

This is the required gate (prereg §6, Elder C6509 / chair C4771): all 3 rungs, >=2
instances each, DUMMY vectors, no secrets. It closes only against the REAL frozen
grader — my own reference verifier proved nothing except that I am self-consistent
with my own reading of the spec (c4185_001: the frozen consumer dictates the schema,
never the producer; my reading is exactly the thing under test).

Exp142 lesson being paid forward: the reveal path was the ONLY never-run production
path and survived on a voluntary last-hour pre-flight. Here it is a gate.
"""
import hashlib
import importlib.util
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))

# Producer half (mine).
spec = importlib.util.spec_from_file_location(
    "sealer", os.path.join(HERE, "exp144_seal_reveal_ember.py"))
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)

# Consumer half (Elder's, frozen candidate) — the AUTHORITY.
gspec = importlib.util.spec_from_file_location(
    "grader", os.path.join(HERE, "exp144_grader.py"))
G = importlib.util.module_from_spec(gspec)
gspec.loader.exec_module(G)

FAILS = 0


def check(label, cond, detail=""):
    global FAILS
    if not cond:
        FAILS += 1
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}{(' — ' + detail) if detail else ''}")


# Dummy instances: 3 rungs x 3 instances (gate needs >=2; do 3).
def dummy(n, k):
    terms = ["X" * n, "X" * (n - 1) + "Y", "X" * (n - 1) + "Z"]
    coeffs = [0.15, -0.20, 0.25]
    salt = hashlib.sha256(f"exp144-dummy-{n}-{k}".encode()).digest()
    return terms, coeffs, salt


print("=== EXP144 E2E GATE: my sealer -> my reveal writer -> ELDER'S REAL GRADER ===")
tmp = tempfile.mkdtemp(prefix="exp144_gate_")

# A. Cross-implementation agreement on the preimage BEFORE any hashing.
# If our two serializers disagree, every hash downstream is meaningless-but-plausible.
print("\n[A] preimage string: my serializer vs the grader's (independent implementations)")
for n in (4, 6, 8):
    for k in (1, 2, 3):
        terms, coeffs, _ = dummy(n, k)
        mine, _, _ = S.canonical_preimage_str(n, k, terms, coeffs)
        theirs = G.preimage_string(n, k, terms, coeffs)
        check(f"A n={n} k={k} preimage identical", mine == theirs,
              "" if mine == theirs else f"\n      mine:   {mine}\n      grader: {theirs}")

# B. THE GATE: seal -> write records -> REAL verify_commitment.
print("\n[B] seal -> reveal-write -> grader.verify_commitment (the gate)")
for n in (4, 6, 8):
    for k in (1, 2, 3):
        terms, coeffs, salt = dummy(n, k)
        digest, _, _, _ = S.commit_hash(salt, n, k, terms, coeffs)
        cpath = os.path.join(tmp, f"commitment_{S.ENS}_n{n}_k{k}.json")
        rpath = os.path.join(tmp, f"reveal_{S.ENS}_n{n}_k{k}.json")
        with open(cpath, "w") as f:
            json.dump(S.commit_record(n, k, digest), f)
        with open(rpath, "w") as f:
            json.dump(S.reveal_record(n, k, salt.hex(), terms, coeffs), f)
        try:
            ok, t, c = G.verify_commitment(cpath, rpath)
        except KeyError as e:
            check(f"B n={n} k={k} REAL grader verifies", False, f"KeyError {e} — SCHEMA MISMATCH")
            continue
        except Exception as e:
            check(f"B n={n} k={k} REAL grader verifies", False, f"{type(e).__name__}: {e}")
            continue
        check(f"B n={n} k={k} REAL grader verifies my records", ok)

# C. Negative controls — a gate that cannot fail is decoration.
print("\n[C] negative controls against the REAL grader")
terms, coeffs, salt = dummy(6, 1)
digest, _, _, _ = S.commit_hash(salt, 6, 1, terms, coeffs)
cpath = os.path.join(tmp, "neg_commit.json")
with open(cpath, "w") as f:
    json.dump(S.commit_record(6, 1, digest), f)

# C1 flipped coefficient sign
rp = os.path.join(tmp, "neg_flip.json")
with open(rp, "w") as f:
    json.dump(S.reveal_record(6, 1, salt.hex(), terms, [0.15, 0.20, 0.25]), f)
check("C1 flipped coeff sign REJECTED", not G.verify_commitment(cpath, rp)[0])

# C2 wrong instance index
rp = os.path.join(tmp, "neg_k.json")
with open(rp, "w") as f:
    json.dump(S.reveal_record(6, 2, salt.hex(), terms, coeffs), f)
check("C2 wrong instance index REJECTED", not G.verify_commitment(cpath, rp)[0])

# C3 wrong salt
rp = os.path.join(tmp, "neg_salt.json")
with open(rp, "w") as f:
    json.dump(S.reveal_record(6, 1, hashlib.sha256(b"wrong").hexdigest(), terms, coeffs), f)
check("C3 wrong salt REJECTED", not G.verify_commitment(cpath, rp)[0])

# C4 PERMUTED input must still VERIFY (canonical sort is the point) — the positive
# control for the ordering rule, and the exact mispair class from Exp142 surface #1.
rp = os.path.join(tmp, "perm.json")
with open(rp, "w") as f:
    json.dump(S.reveal_record(6, 1, salt.hex(), [terms[2], terms[0], terms[1]],
                              [coeffs[2], coeffs[0], coeffs[1]]), f)
check("C4 permuted terms+coeffs (same permutation) still VERIFIES", G.verify_commitment(cpath, rp)[0])

# C5 MISPAIRED: terms permuted but coeffs NOT — different physics, must REJECT.
rp = os.path.join(tmp, "mispair.json")
with open(rp, "w") as f:
    json.dump(S.reveal_record(6, 1, salt.hex(), [terms[2], terms[0], terms[1]], coeffs), f)
check("C5 mispaired terms/coeffs REJECTED (wrong Hamiltonian)", not G.verify_commitment(cpath, rp)[0])

# D. FR-2: the grader must contain no bridge and read only "sha256".
print("\n[D] FR-2 key discipline")
src = open(os.path.join(HERE, "exp144_grader.py")).read()
check("D grader reads 'sha256'", '"sha256"' in src or "'sha256'" in src)
check("D grader has NO hash_sha256 bridge", "hash_sha256" not in src)

print(f"\n=== GATE: {'PASS — §6 path-matrix cell GREEN' if FAILS == 0 else f'FAIL ({FAILS}) — DO NOT FREEZE'} ===")
print(f"scope: 3 rungs x 3 instances, dummy vectors, no secrets touched. Verifier = REAL "
      f"exp144_grader.verify_commitment (not my reference).")
sys.exit(1 if FAILS else 0)
