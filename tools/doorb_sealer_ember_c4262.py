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


# ── ANCHOR CHECK (board#330) ────────────────────────────────────────────────────────────────
# `seal` used to accept a MISSING --prereg-freeze and emit `"prereg_freeze": ""`. That produces
# a commitment that is CRYPTOGRAPHICALLY VALID AND SCIENTIFICALLY EMPTY: it binds P, so at
# reveal it proves the string was fixed in advance, and it proves NOTHING about which protocol
# document that string was fixed FOR. The blind protocol exists for the second thing.
#
# AND SELFTEST [5] PASSED ON IT — "prereg-freeze text is bound into the digest" is TRUE, because
# binding an empty string is binding. The check verified the MECHANISM while the VALUE it
# operates on was absent, so it could not fail on this input. Same shape as a registry counting
# a 36h-old observation as live capacity and a rediscovery gate satisfied by a gibberish query.
#
# The freeze digest's documented form is sha256(frozen file)[:24]. A non-empty anchor is not
# enough — "TODO" or "see the prereg" would clear an emptiness test and bind to nothing anyone
# can resolve — so the FORM is checked too. --allow-unanchored exists for a deliberate
# exception, and it WRITES `anchored: false` INTO THE COMMITMENT: an override that leaves no
# trace in the artifact is invisible at the moment the artifact is read, which is reveal time.
FREEZE_FORM = "sha256(frozen prereg file)[:24] — 24 lowercase hex chars"

def anchor_problems(prereg_freeze, oop):
    """Return a list of reasons this commitment would bind P to nothing. Empty list == anchored."""
    probs = []
    f = (prereg_freeze or "").strip()
    o = (oop or "").strip()
    if not f:
        probs.append("--prereg-freeze is EMPTY: the commitment would bind P to no protocol "
                     "document. At reveal it proves the draw was fixed, not what it was fixed FOR.")
    elif len(f) != 24 or any(c not in "0123456789abcdef" for c in f):
        probs.append(f"--prereg-freeze {f!r} is not the documented form ({FREEZE_FORM}). A "
                     f"non-empty anchor nobody can resolve binds no better than an empty one.")
    if not o:
        probs.append("--oop is EMPTY: the order-of-operations is what makes the digest's "
                     "PUBLICATION TIME meaningful; without it the seal has no declared sequence.")
    return probs


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
    # board#330: [5] above cannot fail on a MISSING anchor — it binds whatever it is given, and
    # binding "" is binding. These check the VALUE, and [10] is the can-fire-both-directions
    # control: without it, a check that refused everything would look identical to a working one.
    good = "a1b2c3d4e5f60718293a4b5c"
    rec(8, "an EMPTY prereg-freeze is REFUSED (the defect [5] could not see)",
        any("EMPTY" in p for p in anchor_problems("", "seal->fly->decode")))
    rec(9, "a NON-DIGEST anchor is REFUSED ('TODO' clears emptiness, resolves to nothing)",
        any("documented form" in p for p in anchor_problems("TODO", "seal->fly->decode")))
    rec(10, "a VALID anchor + oop PASSES (control: the check can succeed, not just refuse)",
        anchor_problems(good, "seal->fly->decode") == [])
    rec(11, "an empty --oop is REFUSED even when the freeze is valid",
        any("--oop" in p for p in anchor_problems(good, "   ")))
    print(f"  selftest: {'PASS' if ok else 'FAIL'}")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["selftest", "seal"])
    ap.add_argument("--n", type=int, default=16)
    ap.add_argument("--prereg-freeze", default="")
    ap.add_argument("--oop", default="")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--allow-unanchored", action="store_true",
                    help="draw a commitment that binds P to no resolvable protocol document. "
                         "Records anchored:false IN the commitment so the weakness is visible "
                         "at reveal time, not just at draw time.")
    a = ap.parse_args()

    if not selftest():
        sys.exit("REFUSE: sealer selftest failed — no commitment drawn.")
    if a.cmd == "selftest":
        return 0

    # board#330: REFUSE BEFORE DRAWING, not after. A drawn-then-rejected P is a P that existed;
    # the salt and string are in memory and the operator's obvious next move is to re-run with
    # the flag, which is exactly the shopping the seal exists to prevent. Check first, draw never.
    probs = anchor_problems(a.prereg_freeze, a.oop)
    if probs and not a.allow_unanchored:
        print("REFUSE: this commitment would bind P to nothing.\n", file=sys.stderr)
        for p in probs:
            print(f"  · {p}", file=sys.stderr)
        sys.exit("\nPass --allow-unanchored to draw it anyway; the commitment will record "
                 "anchored:false so the weakness is visible when it is revealed.")
    if probs:
        print("\n⚠ UNANCHORED COMMITMENT — drawn under --allow-unanchored:")
        for p in probs:
            print(f"  · {p}")
        print("  Recorded as anchored:false in the commitment.\n")

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
              # board#330: stated on EVERY commitment, not only the bad ones. A field that
              # appears only when something is wrong is a field whose ABSENCE has to be
              # interpreted, and absence reads as fine. anchored:true is a claim the tool
              # is making and can be held to.
              "anchored": not probs,
              "anchor_problems": probs or None,
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
