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
# CONV-SEED commitments (chair C4776, F2(b) — separate record, FR-1 untouched).
#
#   preimage = sha256( salt_bytes || utf8("exp144|convseed|{n}|{seed_decimal}") )
#
# ONE per rung — the conventional sweep order is per-rung. WHY THIS EXISTS: F2(b) is a
# contamination channel — once accepted support is public/conveyed, an unfrozen candidate
# order could be steered by it. Pre-seeding only closes that if the seed is COMMITTED;
# an uncommitted seed is a number claimed after the fact, i.e. the channel wearing a
# fix's name. So the seed is sealed before any data exists and revealed with the rest.
# ---------------------------------------------------------------------------
CONVSEED_RUNGS = (4, 6, 8)


def convseed_preimage_str(n, seed):
    if not isinstance(seed, int) or seed < 0:
        raise ValueError(f"seed must be a non-negative int, got {seed!r}")
    if n not in CONVSEED_RUNGS:
        raise ValueError(f"n must be one of {CONVSEED_RUNGS}, got {n}")
    return f"exp144|convseed|{n}|{seed}"


def convseed_commit_hash(salt_bytes, n, seed):
    body = convseed_preimage_str(n, seed)
    return hashlib.sha256(salt_bytes + body.encode("utf-8")).hexdigest(), body


def convseed_commit_record(n, digest):
    return {"schema": "exp144-convseed-commit-v1", "ensemble": ENS, "n": n,
            "sha256": digest}


def convseed_reveal_record(n, salt_hex, seed):
    return {"schema": "exp144-convseed-reveal-v1", "salt_hex": salt_hex,
            "ensemble": ENS, "n": n, "seed": seed}


def convseed_reference_verify(commit, reveal):
    """PLACEHOLDER — same caveat as reveal: the frozen grader is the authority."""
    body = convseed_preimage_str(reveal["n"], reveal["seed"])
    digest = hashlib.sha256(bytes.fromhex(reveal["salt_hex"]) + body.encode()).hexdigest()
    return (digest == commit["sha256"]
            and commit["ensemble"] == reveal["ensemble"]
            and int(commit["n"]) == int(reveal["n"]))


def convseed_selftest():
    fails = 0

    def check(label, cond, detail=""):
        nonlocal fails
        if not cond:
            fails += 1
        print(f"  [{'PASS' if cond else 'FAIL'}] {label}{(' — ' + detail) if detail else ''}")

    check("CS0 preimage shape mirrors chair C4776",
          convseed_preimage_str(6, 12345) == "exp144|convseed|6|12345",
          convseed_preimage_str(6, 12345))
    # Round-trip, all 3 rungs.
    for n in CONVSEED_RUNGS:
        seed = 1000 + n
        salt = hashlib.sha256(f"cs-dummy-{n}".encode()).digest()
        d, _ = convseed_commit_hash(salt, n, seed)
        cr, rr = convseed_commit_record(n, d), convseed_reveal_record(n, salt.hex(), seed)
        check(f"CS1 seal->reveal->verify n={n}", convseed_reference_verify(cr, rr))
    # Negatives: a seed commitment that cannot detect a swapped seed is decoration.
    salt = hashlib.sha256(b"cs-neg").digest()
    d, _ = convseed_commit_hash(salt, 6, 777)
    cr = convseed_commit_record(6, d)
    check("CS2 different seed REJECTED",
          not convseed_reference_verify(cr, convseed_reveal_record(6, salt.hex(), 778)))
    check("CS3 different rung REJECTED",
          not convseed_reference_verify(cr, convseed_reveal_record(4, salt.hex(), 777)))
    check("CS4 wrong salt REJECTED",
          not convseed_reference_verify(
              cr, convseed_reveal_record(6, hashlib.sha256(b"x").hexdigest(), 777)))
    check("CS5 key is 'sha256' only (FR-2)",
          "sha256" in cr and "hash_sha256" not in cr)
    for bad, why in [((6, -1), "negative seed"), ((6, "12"), "string seed"), ((5, 1), "bad rung")]:
        try:
            convseed_preimage_str(*bad)
            check(f"CS6 rejects {why}", False, "accepted!")
        except ValueError:
            check(f"CS6 rejects {why}", True)
    return fails


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

    print("\n  --- conv-seed commitments (chair C4776) ---")
    fails += convseed_selftest()

    print(f"\nEXP144 SEAL/REVEAL SELFTEST: {'PASS' if fails == 0 else f'FAIL ({fails})'}")
    print("NOTE: reference_verify is a PLACEHOLDER. The gate is only satisfied when this")
    print("      is re-run against the REAL frozen exp144_grader.verify_commitment.")
    return fails


# ---------------------------------------------------------------------------
# REAL SEAL PATH (§6). Runs ONCE, at freeze, after the prereg hash is verified.
#
# Order is deliberate and mirrors Exp142 C4185: VERIFY -> GENERATE -> VALIDATE ->
# SEAL -> BACKUP. Nothing is written until every instance has passed validation
# against MATRIX ground truth — not against the rule that generated it (c4194_001:
# a validator that reuses the primitive it validates is an echo; my own commutes()
# was wrong for an hour tonight and 15/15 "passed").
# ---------------------------------------------------------------------------
def _matrix_commutes(p_str, q_str):
    """Ground truth: PQ == QP by actual matrix multiplication. Imported lazily so the
    selftest path has no numpy dependency."""
    import numpy as np
    M = {"I": np.eye(2, dtype=complex),
         "X": np.array([[0, 1], [1, 0]], dtype=complex),
         "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
         "Z": np.array([[1, 0], [0, -1]], dtype=complex)}
    def mat(t):
        out = np.array([[1]], dtype=complex)
        for ch in t:
            out = np.kron(out, M[ch])
        return out
    A, B = mat(p_str), mat(q_str)
    return bool(np.allclose(A @ B, B @ A))


def do_seal(prereg_sha=None, force=False):
    """Generate + validate + seal 15 instances and 3 conv-seeds. Writes:
      ~/.ember-exp144-secrets.json  (chmod 600, off-git)  — salts + plaintext + seeds
      exp144_commitments/commitment_{ENS}_n{N}_k{K}.json   (15, committed)
      exp144_commitments/commit_convseed_n{N}.json         (3, committed — grader's name)
    Returns 0 on success. Refuses to overwrite an existing seal without --force.
    """
    import importlib.util
    import random
    import stat

    if os.path.exists(SECRETS_PATH) and not force:
        print(f"REFUSING: {SECRETS_PATH} already exists. A second seal would silently "
              f"replace committed truth. Use --force only if the prior seal was never "
              f"committed/flown.")
        return 2

    # The generator is a separate module (§1 rules live there, with their own oracles).
    gspec = importlib.util.spec_from_file_location(
        "gen", os.path.join(HERE, "exp144_instance_gen_ember.py"))
    GEN = importlib.util.module_from_spec(gspec)
    gspec.loader.exec_module(GEN)

    rng = random.SystemRandom()   # instance sampling: OS entropy, not reproducible by design
    secrets_blob = {"_meta": "Exp144 sealed truth (Ember). Off-git, chmod 600. "
                             "Encrypted backup committed; passphrase Creator-only.",
                    "ensemble": ENS, "prereg_sha": prereg_sha,
                    "instances": {}, "convseeds": {}}
    commits = []

    print("=== GENERATE + VALIDATE (nothing written yet) ===")
    for n in RUNGS:
        secrets_blob["instances"][str(n)] = {}
        for k in INSTANCES:
            terms, coeffs = GEN.sample_instance(n, rng)

            # Validate by the §1 rules...
            errs = GEN.validate_instance(n, terms, coeffs)
            if errs:
                print(f"  ABORT n={n} k={k}: {errs}")
                return 3
            # ...and then by GROUND TRUTH, which owes nothing to those rules.
            for i in range(len(terms)):
                for j in range(i + 1, len(terms)):
                    if not _matrix_commutes(terms[i], terms[j]):
                        print(f"  ABORT n={n} k={k}: {terms[i]},{terms[j]} NON-COMMUTING BY MATRIX")
                        return 3

            salt = pysecrets.token_bytes(32)
            digest, body, t_sorted, c_sorted = commit_hash(salt, n, k, terms, coeffs)
            secrets_blob["instances"][str(n)][str(k)] = {
                "salt_hex": salt.hex(), "terms": t_sorted, "coeffs": c_sorted}
            commits.append((f"commitment_{ENS}_n{n}_k{k}.json",
                            commit_record(n, k, digest)))
            print(f"  n={n} k={k}: sealed  hash {digest[:12]}  (matrix-verified)")

    for n in CONVSEED_RUNGS:
        seed = pysecrets.randbits(64)
        salt = pysecrets.token_bytes(32)
        digest, _ = convseed_commit_hash(salt, n, seed)
        secrets_blob["convseeds"][str(n)] = {"salt_hex": salt.hex(), "seed": seed}
        commits.append((f"commit_convseed_n{n}.json", convseed_commit_record(n, digest)))
        print(f"  convseed n={n}: sealed  hash {digest[:12]}")

    # Round-trip EVERY commitment before anything touches disk: if a reveal built from
    # this blob would not verify, the seal is worthless and must not be written.
    print("\n=== PRE-WRITE ROUND-TRIP (reveal must verify against every commitment) ===")
    bad = 0
    for n in RUNGS:
        for k in INSTANCES:
            e = secrets_blob["instances"][str(n)][str(k)]
            cr = next(c for f, c in commits if f == f"commitment_{ENS}_n{n}_k{k}.json")
            rr = reveal_record(n, k, e["salt_hex"], e["terms"], e["coeffs"])
            if not reference_verify(cr, rr):
                print(f"  ABORT: n={n} k={k} reveal does NOT verify against its commitment")
                bad += 1
    for n in CONVSEED_RUNGS:
        e = secrets_blob["convseeds"][str(n)]
        cr = next(c for f, c in commits if f == f"commit_convseed_n{n}.json")
        rr = convseed_reveal_record(n, e["salt_hex"], e["seed"])
        if not convseed_reference_verify(cr, rr):
            print(f"  ABORT: convseed n={n} does NOT verify")
            bad += 1
    if bad:
        return 4
    print(f"  {len(commits)}/{len(commits)} round-trip clean")

    # Only now write.
    os.makedirs(COMMIT_DIR, exist_ok=True)
    with open(SECRETS_PATH, "w") as f:
        json.dump(secrets_blob, f, indent=1)
    os.chmod(SECRETS_PATH, stat.S_IRUSR | stat.S_IWUSR)   # 600
    for fname, rec in commits:
        with open(os.path.join(COMMIT_DIR, fname), "w") as f:
            json.dump(rec, f, indent=1)

    print(f"\nSEALED: {len(commits)} commitments -> {COMMIT_DIR}")
    print(f"        secrets -> {SECRETS_PATH} (chmod 600, off-git)")
    print("NEXT (do not skip — C4187 SPOF fix): AES-256 encrypt the secrets file, commit the")
    print("      ciphertext, email the passphrase to Creator ONLY. Loss of this machine before")
    print("      reveal is otherwise unrecoverable and voids the whole experiment.")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--seal", action="store_true", help="REAL seal — writes secrets + commitments")
    ap.add_argument("--prereg-sha", default=None, help="frozen prereg sha256, recorded in secrets")
    ap.add_argument("--force", action="store_true", help="overwrite an existing seal (dangerous)")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(1 if selftest() else 0)
    if a.seal:
        sys.exit(do_seal(prereg_sha=a.prereg_sha, force=a.force))
    ap.print_help()
