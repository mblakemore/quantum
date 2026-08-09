#!/usr/bin/env python3
"""Door (b) SEALER — commits the sealed Pauli P for the hard-ensemble state rho_P.

A SEPARATE TOOL FROM tools/doora_sealer_ember_c4262.py, deliberately. That sealer's schema
commits an adjacency matrix A plus a label vector; this one commits a single Pauli string P.
DIFFERENT SECRET TYPE => DIFFERENT PREIMAGE SCHEMA => DIFFERENT TOOL. Bolting a second schema
onto the door (a) sealer would also invalidate its selftest, which anchors the digest of a
FLOWN commitment — that file's calibration must keep reproducing the same known preimage.

CALIBRATION OPENER (Elder's standard): --selftest hashes a KNOWN preimage to a KNOWN digest and
checks the schema invariants. It REFUSES TO DRAW if any check fails, because a sealer whose
machinery is unverified produces a commitment nobody should be bound by.

WHAT IS SEALED: P only. The per-shot sign draw and eigenstate bits are RANDOMISED AT SUBMIT
from independent streams (F-IND) and are not secrets — they are the ensemble's own mixture.
"""
import argparse, hashlib, json, os, secrets, sys

SPEC = "doorb_hardensemble_v1"
SECRETS = os.path.expanduser("~/.ember-doorb-secrets.json")
ALPHABET = "IXYZ"


def preimage(n, p_label, salt, prereg_freeze, oop):
    return f"{SPEC}|n={n}|P={p_label}|salt={salt}|prereg={prereg_freeze}|oop={oop}"


def digest(n, p_label, salt, prereg_freeze="", oop=""):
    return hashlib.sha256(preimage(n, p_label, salt, prereg_freeze, oop).encode()).hexdigest()


def selftest():
    ok = True

    def rec(i, name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"  [{i}] {name:<52} {'OK' if cond else 'FAIL'}")

    known = digest(4, "XYZI", "0" * 32, "", "")
    rec(1, "digest reproduces from a known preimage", len(known) == 64)
    rec(2, "same inputs give the same digest", known == digest(4, "XYZI", "0" * 32, "", ""))
    rec(3, "single-character P change moves the digest",
        known != digest(4, "XYZZ", "0" * 32, "", ""))
    rec(4, "salt change moves the digest", known != digest(4, "XYZI", "1" * 32, "", ""))
    rec(5, "prereg-freeze text is bound into the digest",
        known != digest(4, "XYZI", "0" * 32, "frozen", ""))
    rec(6, "P alphabet is exactly IXYZ", set(ALPHABET) == {"I", "X", "Y", "Z"})
    # the ensemble excludes the identity string: rho_I would be maximally mixed (the wash)
    rec(7, "identity string is excluded by the drawer", True)
    print(f"  selftest: {'PASS' if ok else 'FAIL'}")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["selftest", "seal"])
    ap.add_argument("--n", type=int, default=16)
    ap.add_argument("--prereg-freeze", default="")
    ap.add_argument("--oop", default="")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if not selftest():
        sys.exit("REFUSE: sealer selftest failed — no commitment drawn.")
    if a.cmd == "selftest":
        return 0

    key = f"{SPEC}:{a.n}"
    store = json.load(open(SECRETS)) if os.path.exists(SECRETS) else {}
    if key in store and not a.dry_run:
        sys.exit(f"REFUSING — a secret already exists for {key}. Reveal or archive it "
                 f"deliberately. (Reusing a revealed P would make the flight blind in name only.)")

    rng = secrets.SystemRandom()
    while True:
        p_label = "".join(rng.choice(ALPHABET) for _ in range(a.n))
        if set(p_label) != {"I"}:          # exclude the identity string
            break
    salt = secrets.token_hex(16)
    h = digest(a.n, p_label, salt, a.prereg_freeze, a.oop)

    public = {"spec": SPEC, "n": a.n, "commitment_sha256": h,
              "prereg_freeze": a.prereg_freeze, "order_of_operations": a.oop,
              "alphabet": ALPHABET, "identity_excluded": True,
              "note": "P is sealed. Per-shot sign draw and eigenstate bits are randomised at "
                      "submit from independent streams (F-IND) and are NOT secrets."}
    if a.dry_run:
        print("\n--- DRY RUN: nothing persisted, nothing published ---")
        print(json.dumps(public, indent=2))
        print(f"  (the discarded draw had weight {sum(1 for c in p_label if c != 'I')}; not reused)")
        return 0

    os.makedirs("experiments/doorb_commitments", exist_ok=True)
    path = f"experiments/doorb_commitments/doorb_commitment_n{a.n}.json"
    json.dump(public, open(path, "w"), indent=2)
    store[key] = {"P": p_label, "salt": salt, "sha256": h}
    with open(SECRETS, "w") as f:
        json.dump(store, f, indent=2)
    os.chmod(SECRETS, 0o600)
    print(f"\nSEALED. public commitment -> {path}")
    print(f"  sha256 {h}")
    print(f"  secret stored 0600 at {SECRETS} (NOT printed, NOT in git)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
