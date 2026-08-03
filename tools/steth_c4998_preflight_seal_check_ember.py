#!/usr/bin/env python3
"""PRE-FLIGHT seal integrity — does the off-git secret still reproduce the public
commitments? Prints PASS/FAIL per item and NOTHING ELSE.

WHY THIS IS NOT `sealer verify` (Ember C4238): `verify` compares a REVEAL file against
the commitments, so it only exists AFTER the reveal. There was no check for the state
that actually matters — the moment the flight is about to build U from a secret nobody
has looked at in weeks. A rotated, truncated or half-written secrets file would have
produced a U that no commitment covers, and the flight would have looked perfect.

It reveals nothing: it recomputes SHA-256 over salt+spec and compares hashes. The seed,
the salt and the label bits never touch stdout — which is the same discipline that a
grep of a credential file taught me the hard way earlier today.

Run this immediately before any flight that consumes the seal.
"""
import importlib.util, json, os, sys

REPO = "/droid/repos/quantum"
SEALER = os.path.join(REPO, "tools", "exp_steth_c4998_sealer_ember.py")
COMMITS = os.path.join(REPO, "results", "steth_c4998_commitments",
                       "commitments_steth_c4998_ember.json")


def main():
    spec = importlib.util.spec_from_file_location("sealer", SEALER)
    S = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(S)

    C = json.load(open(COMMITS))
    sec = S.load_secrets()
    if not sec:
        print("NO SECRETS FILE — the flight cannot build U. STOP.")
        return 2

    M = C["M"]
    ok = True
    print("PRE-FLIGHT SEAL INTEGRITY (nothing secret is printed)")
    armT = sec.get("armT", sec)
    for k, v in C["armT"].items():
        s = armT.get(k) or armT.get(str(k)) or {}
        try:
            a = S.commit(bytes.fromhex(s["u_salt_hex"]),
                         S.u_spec(int(k), s["u_seed_hex"])) == v["U_hash_sha256"]
            b = S.commit(bytes.fromhex(s["label_salt_hex"]),
                         S.labelT_spec(int(k), M, s["label_bits"])) == v["labels_hash_sha256"]
        except Exception:
            a = b = False
        ok &= a and b
        print(f"  armT k={k:>2}: U {'MATCH' if a else 'MISMATCH'} · "
              f"labels {'MATCH' if b else 'MISMATCH'}")
    for k, v in C["armN"].items():
        s = sec.get("armN", {}).get(k) or sec.get("armN", {}).get(str(k)) or {}
        try:
            a = S.commit(bytes.fromhex(s["label_salt_hex"]),
                         S.labelN_spec(int(k), M, s["label_bits"])) == v["labels_hash_sha256"]
        except Exception:
            a = False
        ok &= a
        print(f"  armN k={k:>2}: labels {'MATCH' if a else 'MISMATCH'}")

    print()
    print("SEAL INTACT — the off-git secret still reproduces every public commitment.\n"
          "The flight may build U from it; nothing is revealed by this check." if ok else
          "SEAL BROKEN — do NOT build U from this secret. Investigate before flying.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
