#!/usr/bin/env python3
"""Exp144 SEALER + REVEAL WRITER + pre-freeze path-matrix GATE (Ember).

Implements prereg §6 (FR-1/FR-2, pinned pre-freeze at Elder C6509 / quantum 1b0cf45).

    preimage = sha256( salt_bytes || utf8("exp144|{ens}|{n}|{k}|{terms_csv}|{coeffs_csv}") )

Normative rules (from the prereg, NOT from this file's convenience):
  * terms_csv  : m=3 labels, canonical order = LEXICOGRAPHIC ASCENDING, joined ","
  * coeffs_csv : signed coefficients in the SAME INDEX ORDER as terms_csv, each "%+.2f"
  * n ∈ {4,6,8}, k ∈ {1..5}
  * commitment key is "sha256" — ONE name, sealer == grader at source. No bridge.

WHY THIS FILE EXISTS BEFORE THE FREEZE: in Exp142 the reveal path was the only
never-run production path, and it survived purely on a voluntary last-hour pre-flight
I happened to run. §6 now makes the end-to-end exercise a GATE. This is that gate's
producer half.

  python3 exp144_seal_reveal_ember.py --selftest     # dummy vectors, no secrets, no writes
  python3 exp144_seal_reveal_ember.py --seal         # REAL seal (writes off-git secrets + commits)
  python3 exp144_seal_reveal_ember.py --reveal DIR   # write reveal records (post chair call only)
"""
import argparse
import hashlib
import json
import os
import secrets as pysecrets
import sys

ENS = "dynamics_fullweight_m3"
RUNGS = (4, 6, 8)
INSTANCES = (1, 2, 3, 4, 5)
SECRETS_PATH = os.path.expanduser("~/.ember-exp144-secrets.json")
HERE = os.path.dirname(os.path.abspath(__file__))
COMMIT_DIR = os.path.join(HERE, "exp144_commitments")


# ---------------------------------------------------------------------------
# The serialization IS the commitment. One function, used by seal AND reveal, so
# the two paths cannot drift (Exp142 surface #1 was exactly a producer/consumer
# serialization drift that no hash check could catch).
# ---------------------------------------------------------------------------
def canonical_preimage_str(n, k, terms, coeffs):
    """Return the EXACT utf8 body per prereg §6. Sorting is normative, not cosmetic."""
    if len(terms) != len(coeffs):
        raise ValueError(f"terms/coeffs length mismatch: {len(terms)} vs {len(coeffs)}")
    if len(set(terms)) != len(terms):
        raise ValueError(f"duplicate term labels: {terms}")
    for t in terms:
        if len(t) != n or any(ch not in "IXYZ" for ch in t):
            raise ValueError(f"bad term label {t!r} for n={n} (need len {n}, alphabet IXYZ)")
    # Sort terms ascending and permute coeffs by the SAME permutation. Sorting the two
    # lists independently would silently mispair them — a valid-looking preimage for the
    # wrong Hamiltonian, and the hash would happily commit to it.
    order = sorted(range(len(terms)), key=lambda i: terms[i])
    t_sorted = [terms[i] for i in order]
    c_sorted = [coeffs[i] for i in order]
    terms_csv = ",".join(t_sorted)
    coeffs_csv = ",".join(f"{c:+.2f}" for c in c_sorted)
    return f"exp144|{ENS}|{n}|{k}|{terms_csv}|{coeffs_csv}", t_sorted, c_sorted


def commit_hash(salt_bytes, n, k, terms, coeffs):
    body, t_sorted, c_sorted = canonical_preimage_str(n, k, terms, coeffs)
    digest = hashlib.sha256(salt_bytes + body.encode("utf-8")).hexdigest()
    return digest, body, t_sorted, c_sorted


def commit_record(n, k, digest):
    return {"schema": "exp144-commit-v1", "ensemble": ENS, "n": n,
            "instance": k, "sha256": digest}


def reveal_record(n, k, salt_hex, terms, coeffs):
    _, t_sorted, c_sorted = canonical_preimage_str(n, k, terms, coeffs)
    return {"schema": "exp144-reveal-v1", "salt_hex": salt_hex, "ensemble": ENS,
            "n": n, "instance": k, "terms": t_sorted, "coeffs": c_sorted}


def reference_verify(commit, reveal):
    """Reference verifier per §6 — PLACEHOLDER ONLY.

    The FROZEN GRADER is the authority (c4185_001: the frozen consumer dictates schema,
    never the producer). When exp144_grader.py lands, the gate MUST be re-run importing
    its real verify_commitment. This exists so the producer half can be exercised now.
    """
    body, _, _ = canonical_preimage_str(
        reveal["n"], reveal["instance"], reveal["terms"], reveal["coeffs"])
    digest = hashlib.sha256(bytes.fromhex(reveal["salt_hex"]) + body.encode()).hexdigest()
    return (digest == commit["sha256"]
            and commit["ensemble"] == reveal["ensemble"]
            and int(commit["n"]) == int(reveal["n"])
            and int(commit["instance"]) == int(reveal["instance"]))


# ---------------------------------------------------------------------------
def selftest():
    fails = 0

    def check(label, cond, detail=""):
        nonlocal fails
        if not cond:
            fails += 1
        print(f"  [{'PASS' if cond else 'FAIL'}] {label}{(' — ' + detail) if detail else ''}")

    # T0: the prereg's own worked example must reproduce byte-for-byte.
    body, _, _ = canonical_preimage_str(4, 2, ["XXXX", "XXYY", "XXZZ"], [0.15, -0.20, 0.25])
    expect = "exp144|dynamics_fullweight_m3|4|2|XXXX,XXYY,XXZZ|+0.15,-0.20,+0.25"
    check("T0 prereg §6 worked example reproduces", body == expect, f"got {body!r}")

    # T1: ORDER INDEPENDENCE — same physics presented in any input order must give the
    # same preimage. This is the property the canonical rule exists to create.
    a, _, _ = canonical_preimage_str(4, 1, ["XXZZ", "XXXX", "XXYY"], [0.25, 0.15, -0.20])
    b, _, _ = canonical_preimage_str(4, 1, ["XXXX", "XXYY", "XXZZ"], [0.15, -0.20, 0.25])
    check("T1 input order irrelevant (coeffs follow their term)", a == b, f"{a!r} vs {b!r}")

    # T2: the mispairing trap — if coeffs were sorted independently of terms, this
    # permuted input would collide with the sorted one. It must NOT.
    c, _, _ = canonical_preimage_str(4, 1, ["XXXX", "XXYY", "XXZZ"], [0.25, 0.15, -0.20])
    check("T2 permuted coeffs give DIFFERENT preimage (no silent mispair)", c != b)

    # T3: %+.2f formatting is exact — sign always present, 2 decimals always.
    d, _, _ = canonical_preimage_str(4, 1, ["IIII", "IIIX", "IIIY"], [0.2, -0.2, 0.0])
    check("T3 %+.2f formatting", d.endswith("|+0.20,-0.20,+0.00"), d.split("|")[-1])

    # T4: round-trip seal -> reveal -> verify, all 3 rungs x 2 instances (the gate shape),
    # on DUMMY vectors. No secrets touched.
    rng = 0
    for n in RUNGS:
        for k in (1, 2):
            rng += 1
            terms = [("X" * n), ("X" * (n - 1) + "Y"), ("X" * (n - 1) + "Z")]
            coeffs = [0.15, -0.20, 0.25]
            salt = hashlib.sha256(f"dummy{rng}".encode()).digest()
            digest, _, _, _ = commit_hash(salt, n, k, terms, coeffs)
            cr = commit_record(n, k, digest)
            rr = reveal_record(n, k, salt.hex(), terms, coeffs)
            ok = reference_verify(cr, rr)
            check(f"T4 seal->reveal->verify n={n} k={k}", ok)

    # T5: tamper detection — a flipped coefficient must break verification.
    salt = hashlib.sha256(b"tamper").digest()
    digest, _, _, _ = commit_hash(salt, 4, 1, ["XXXX", "XXYY", "XXZZ"], [0.15, -0.20, 0.25])
    cr = commit_record(4, 1, digest)
    rr_bad = reveal_record(4, 1, salt.hex(), ["XXXX", "XXYY", "XXZZ"], [0.15, 0.20, 0.25])
    check("T5 tampered coeff sign FAILS verify", not reference_verify(cr, rr_bad))

    # T6: wrong instance index must not verify (k is in the preimage).
    rr_k = reveal_record(4, 2, salt.hex(), ["XXXX", "XXYY", "XXZZ"], [0.15, -0.20, 0.25])
    check("T6 wrong instance index FAILS verify", not reference_verify(cr, rr_k))

    # T7: schema keys exactly as pinned — a renamed key is find #6 all over again.
    check("T7 commit record keys", sorted(cr.keys()) ==
          sorted(["schema", "ensemble", "n", "instance", "sha256"]), str(sorted(cr.keys())))
    check("T7 reveal record keys", sorted(rr_k.keys()) ==
          sorted(["schema", "salt_hex", "ensemble", "n", "instance", "terms", "coeffs"]))
    check("T7 commitment key is 'sha256' (FR-2, no bridge)", "sha256" in cr and "hash_sha256" not in cr)

    # T8: input validation actually rejects bad input (a guard never seen to fire is a hope).
    for bad, why in [((4, 1, ["XXXX", "XXYY"], [0.1, 0.2, 0.3]), "length mismatch"),
                     ((4, 1, ["XXXX", "XXXX", "XXYY"], [0.1, 0.2, 0.3]), "duplicate labels"),
                     ((4, 1, ["XXX", "XXYY", "XXZZ"], [0.1, 0.2, 0.3]), "wrong label length"),
                     ((4, 1, ["XXXA", "XXYY", "XXZZ"], [0.1, 0.2, 0.3]), "bad alphabet")]:
        try:
            canonical_preimage_str(*bad)
            check(f"T8 rejects {why}", False, "accepted bad input!")
        except ValueError:
            check(f"T8 rejects {why}", True)

    print(f"\nEXP144 SEAL/REVEAL SELFTEST: {'PASS' if fails == 0 else f'FAIL ({fails})'}")
    print("NOTE: reference_verify is a PLACEHOLDER. The gate is only satisfied when this")
    print("      is re-run against the REAL frozen exp144_grader.verify_commitment.")
    return fails


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(1 if selftest() else 0)
    ap.print_help()
