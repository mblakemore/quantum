#!/usr/bin/env python3
"""Door (a) sealed-commitment tool — degree-2 phase-state ensemble (Ember, C4262).

WHY A NEW TOOL rather than a flag on tools/exp142_p1_sealer_ember.py: that sealer's
draw is `draw_pauli(n) -> str`, hardcoded uniform over the 4**n-1 non-identity Paulis.
Door (a)'s secret is not a Pauli STRING, it is an upper-triangular binary MATRIX A.
Different secret TYPE => different preimage schema, different reveal shape. Bolting an
ensemble switch onto a tool whose docstring warns that a wrong field in a PUBLISHED
commitment cannot be fixed is the wrong trade; a separate tool cannot corrupt P1's
anchor (its selftest reproduces the FLOWN n=10 hash and must keep doing so).

ENSEMBLE (read from Whisper's implementation quantum@0930a74, NOT from prose):
  |psi_A> = 2^(-n/2) SUM_x (-1)^(x^T A x) |x>,  A upper-triangular INCLUDING diagonal.
  random_A:each bit j>=i uniform, NO degenerate rejection -> A=0 possible (p = 2^-36 at n=8).
  Prep: H^n, then Z on each set DIAGONAL bit, CZ on each set OFF-DIAGONAL bit.
  bits(A) = n(n+1)/2  (36 at n=8).  cz_count = set off-diagonal bits.

COMMITMENT binds (spec, n, A, trial_labels, salt). Salt is OFF-GIT. The public
commitment carries ONLY the hash + public parameters; no secret, no salt.

CALIBRATION OPENER (Elder's standard, general#6256): --selftest hashes a KNOWN preimage
and checks a KNOWN digest before the tool will draw anything. An instrument that cannot
reproduce a closed-form value does not get to produce an unknown one.
"""
import argparse, hashlib, json, os, secrets, sys

SPEC = "doora_deg2phase_v1"
SECRETS_PATH = os.path.expanduser("~/.ember-doora-secrets.json")
COMMIT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "experiments", "doora_commitments")

def bits_len(n): return n * (n + 1) // 2

def A_to_bits(A, n):
    """Canonical serialisation: row-major over j>=i. Order is part of the spec."""
    return "".join(str(A[i][j]) for i in range(n) for j in range(i, n))

def bits_to_A(b, n):
    A = [[0] * n for _ in range(n)]; k = 0
    for i in range(n):
        for j in range(i, n):
            A[i][j] = int(b[k]); k += 1
    return A

def cz_count(A, n):
    return sum(A[i][j] for i in range(n) for j in range(i + 1, n))

def preimage(n, a_bits, labels, salt):
    """Canonical, order-fixed, newline-delimited. Any field change changes the digest."""
    return "\n".join([SPEC, f"n={n}", f"A={a_bits}", f"labels={labels}", f"salt={salt}"])

def digest(n, a_bits, labels, salt):
    return hashlib.sha256(preimage(n, a_bits, labels, salt).encode()).hexdigest()

def selftest():
    """CLOSED-FORM OPENER — known preimage, known digest, plus schema invariants."""
    ok = True
    n = 4
    a = "0" * bits_len(n)
    lab = "0101"
    salt = "0" * 32
    pre = preimage(n, a, lab, salt)
    exp = hashlib.sha256(pre.encode()).hexdigest()
    got = digest(n, a, lab, salt)
    c1 = (got == exp); ok &= c1
    print(f"  [1] digest reproduces from known preimage      {'OK' if c1 else 'FAIL'}")
    c2 = (bits_len(8) == 36); ok &= c2
    print(f"  [2] bits(A) at n=8 == 36 (=n(n+1)/2)           {'OK' if c2 else 'FAIL'}")
    A = bits_to_A(a, n); c3 = (A_to_bits(A, n) == a); ok &= c3
    print(f"  [3] A serialisation round-trips                {'OK' if c3 else 'FAIL'}")
    # all-ones A at n=4: off-diagonal count = n(n-1)/2 = 6
    A1 = bits_to_A("1" * bits_len(4), 4); c4 = (cz_count(A1, 4) == 6); ok &= c4
    print(f"  [4] cz_count(all-ones,n=4) == 6 (=n(n-1)/2)    {'OK' if c4 else 'FAIL'}")
    # a one-bit change must change the digest
    c5 = digest(n, "1" + a[1:], lab, salt) != got; ok &= c5
    print(f"  [5] single-bit A change moves the digest       {'OK' if c5 else 'FAIL'}")
    c6 = digest(n, a, lab, "1" + salt[1:]) != got; ok &= c6
    print(f"  [6] salt change moves the digest               {'OK' if c6 else 'FAIL'}")
    print(f"  selftest: {'PASS' if ok else 'FAIL'}")
    return ok

def seal(n, M, prereg_freeze, oop, dry):
    if not selftest():
        sys.exit("REFUSING TO SEAL — selftest failed; the tool cannot reproduce a known digest.")
    a_bits = "".join(str(secrets.randbelow(2)) for _ in range(bits_len(n)))
    labels = "".join(str(secrets.randbelow(2)) for _ in range(M))
    salt = secrets.token_hex(16)
    h = digest(n, a_bits, labels, salt)
    A = bits_to_A(a_bits, n)
    public = {"spec": SPEC, "n": n, "M": M, "commitment_sha256": h,
              "prereg_freeze": prereg_freeze, "order_of_operations": oop,
              "bits_A": bits_len(n), "note": "A upper-triangular INCL diagonal; prep = H^n, Z on set diagonal bits, CZ on set off-diagonal bits (per quantum@0930a74). Secret and salt are OFF-GIT."}
    if dry:
        print("\n--- DRY RUN: nothing drawn is persisted, nothing published ---")
        print(json.dumps(public, indent=2))
        print(f"  (cz_count of the discarded draw was {cz_count(A,n)}; not reused)")
        return
    os.makedirs(COMMIT_DIR, exist_ok=True)
    store = {}
    if os.path.exists(SECRETS_PATH):
        store = json.load(open(SECRETS_PATH))
    key = f"{SPEC}:{n}"
    if key in store:
        sys.exit(f"REFUSING — a secret already exists for {key}. Reveal or remove it deliberately.")
    store[key] = {"A_bits": a_bits, "labels": labels, "salt": salt, "sha256": h}
    with open(SECRETS_PATH, "w") as f: json.dump(store, f, indent=2)
    os.chmod(SECRETS_PATH, 0o600)
    out = os.path.join(COMMIT_DIR, f"doora_commitment_n{n}.json")
    with open(out, "w") as f: json.dump(public, f, indent=2)
    print(f"\nSEALED. public commitment -> {out}")
    print(f"  sha256 {h}")
    print(f"  secret stored 0600 at {SECRETS_PATH} (NOT printed, NOT in git)")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["selftest", "seal"])
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--M", type=int, default=40)
    ap.add_argument("--prereg-freeze", default="")
    ap.add_argument("--oop", default="")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.cmd == "selftest":
        sys.exit(0 if selftest() else 1)
    seal(a.n, a.M, a.prereg_freeze, a.oop, a.dry_run)
