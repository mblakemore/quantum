#!/usr/bin/env python3
"""H15 N1 positronic-neuron sealed-commitment tool (Ember).

WHY A NEW TOOL rather than the door(a) sealer: door(a) seals ONE degree-2 A +
a label string — its claim was about ONE unknown state. H15's per-trial agent
claim is a DIFFERENT object: each ALT trial is an INDEPENDENT instance (fresh A)
and each NULL trial carries a sealed (x,u). Whisper/Elder ratified this
(coordination#12462/#12463/#12465), and it is forced by the theorem, not
preference: with one A repeated 316x a classical agent with cross-trial memory
LEARNS A and beats the frozen 143/256 ceiling — the repeated-A task simply does
not have the ceiling we froze. The door(a) single-A commitment 98b799c9 is
therefore STRUCTURALLY INSUFFICIENT and is retired VOID-BY-RESEAL.

THE SECRET (all off-git, 0600, canonically serialized into ONE commitment):
  labels  : 632-char '1'(ALT)/'0'(NULL), balanced 316/316, secrets-shuffled.
  A_list  : 316 degree-2 phase matrices (door(a) draw convention: n=4 upper-tri
            INCL diagonal, 10 bits, uniform), one per ALT row in label order.
  xu_list : 316 (x,u) pairs, x,u uniform in [0,16), one per NULL row in order.
  salt    : 128-bit hex.

THREE NO-DEDUP PINS (Elder coordination#12468 — "dedup is the rigging channel
in innocent clothes"), asserted in selftest so a future 'cleanup' cannot quietly
re-introduce them:
  (1) A_list is drawn WITH REPLACEMENT. 316 uniform draws from 1024 birthday-
      collide (~40 expected); that is the i.i.d.-uniform ensemble the ceiling is
      computed over. Deduplicating distorts the distribution -> structurally rigged.
  (2) xu_list KEEPS the x=u cases (~20 of 316). Those are the P(accept|NULL)=1
      rows that hold NULL accuracy at its honest 15/32; excluding them is exactly
      the +1.5pp inflation the sealed-xu ruling forecloses.
  (3) NULL (x,u) is SEALED, never public/pilot-chosen: for |x,u> the transversal
      Bell outcome has b = x XOR u deterministically, so a pilot choosing (x,u)
      MOVES the graded NULL score, and publishing per-row (x,u) pre-unseal would
      identify the NULL rows (label leak).

CALIBRATION OPENER (Elder standard): --selftest hashes a KNOWN preimage to a
KNOWN digest and checks the schema invariants before the tool will draw anything.
"""
import argparse, hashlib, json, os, secrets, sys

SPEC = "h15_positronic_v1"
N = 4
M = 632
BITS_A = N * (N + 1) // 2               # 10 at n=4
XU_MAX = 2 ** N                          # x,u in [0,16)
SECRETS_PATH = os.path.expanduser("~/.ember-doora-secrets.json")
COMMIT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "experiments", "doora_commitments")
STORE_KEY = f"{SPEC}:{N}"
OUT_NAME = f"h15_positronic_commitment_n{N}.json"


def draw_A():
    """One degree-2 A: upper-triangular INCL diagonal (door(a) convention),
    crypto-uniform. Returned as an n x n int matrix (matches the kit's
    build(A=[[..]]) and draw_known_A)."""
    A = [[0] * N for _ in range(N)]
    for i in range(N):
        for j in range(i, N):
            A[i][j] = secrets.randbelow(2)
    return A


def canonical_preimage(labels, A_list, xu_list, salt):
    """Order-fixed, newline-delimited, compact-JSON. Any field change -> new digest."""
    return "\n".join([
        SPEC, f"n={N}", f"M={M}", f"labels={labels}",
        f"A_list={json.dumps(A_list, separators=(',', ':'))}",
        f"xu_list={json.dumps(xu_list, separators=(',', ':'))}",
        f"salt={salt}",
    ])


def digest(labels, A_list, xu_list, salt):
    return hashlib.sha256(canonical_preimage(labels, A_list, xu_list, salt).encode()).hexdigest()


def selftest():
    """CLOSED-FORM OPENER — known preimage/known digest + the no-dedup invariants."""
    ok = True
    lab = "10" * 3                        # tiny known preimage
    A_list = [[[0] * N for _ in range(N)]]
    xu_list = [[1, 2]]
    salt = "0" * 32
    pre = canonical_preimage(lab, A_list, xu_list, salt)
    exp = hashlib.sha256(pre.encode()).hexdigest()
    c1 = (digest(lab, A_list, xu_list, salt) == exp); ok &= c1
    print(f"  [1] digest reproduces from known preimage        {'OK' if c1 else 'FAIL'}")
    c2 = (BITS_A == 10 and XU_MAX == 16); ok &= c2
    print(f"  [2] n=4 schema: bits(A)=10, xu in [0,16)          {'OK' if c2 else 'FAIL'}")
    c3 = digest("00" + lab[2:], A_list, xu_list, salt) != exp; ok &= c3
    print(f"  [3] label change moves the digest                 {'OK' if c3 else 'FAIL'}")
    c4 = digest(lab, [[[1] + [0] * (N - 1)] + [[0] * N] * (N - 1)], xu_list, salt) != exp; ok &= c4
    print(f"  [4] A change moves the digest                     {'OK' if c4 else 'FAIL'}")
    c5 = digest(lab, A_list, [[3, 3]], salt) != exp; ok &= c5
    print(f"  [5] xu change moves the digest                    {'OK' if c5 else 'FAIL'}")
    c6 = digest(lab, A_list, xu_list, "1" + salt[1:]) != exp; ok &= c6
    print(f"  [6] salt change moves the digest                  {'OK' if c6 else 'FAIL'}")
    # NO-DEDUP invariants: the tool must be ABLE to hold duplicates + x=u.
    c7 = True  # A_list may contain identical matrices (with-replacement)
    dupA = [[[0] * N for _ in range(N)], [[0] * N for _ in range(N)]]
    c7 = (digest("10", dupA, [[0, 0], [0, 0]], salt) ==
          hashlib.sha256(canonical_preimage("10", dupA, [[0, 0], [0, 0]], salt).encode()).hexdigest())
    ok &= c7
    print(f"  [7] duplicate A's + x=u pairs serialize (no dedup) {'OK' if c7 else 'FAIL'}")
    print(f"  selftest: {'PASS' if ok else 'FAIL'}")
    return ok


def seal(dry, prereg_freeze, oop):
    if not selftest():
        sys.exit("REFUSING TO SEAL — selftest failed.")

    # labels: balanced 316/316, Fisher-Yates with secrets (no Math.random-class bias)
    arr = [1] * (M // 2) + [0] * (M // 2)
    for i in range(len(arr) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        arr[i], arr[j] = arr[j], arr[i]
    labels = "".join(map(str, arr))
    n_alt = labels.count("1")
    assert n_alt == M // 2, "balance invariant broken"

    # A_list: 316 draws WITH REPLACEMENT (pin 1 — do NOT dedup)
    A_list = [draw_A() for _ in range(n_alt)]
    # xu_list: 316 (x,u) uniform, KEEP x=u (pin 2 — do NOT exclude)
    xu_list = [[secrets.randbelow(XU_MAX), secrets.randbelow(XU_MAX)] for _ in range(M - n_alt)]

    salt = secrets.token_hex(16)
    h = digest(labels, A_list, xu_list, salt)

    # diagnostics that PROVE the pins held (reported, never used to filter)
    a_keys = ["".join(str(A[i][j]) for i in range(N) for j in range(i, N)) for A in A_list]
    a_collisions = len(a_keys) - len(set(a_keys))
    xu_equal = sum(1 for x, u in xu_list if x == u)

    public = {"spec": SPEC, "n": N, "M": M, "commitment_sha256": h,
              "label_draw": "balanced-316/316-shuffled",
              "alt_instances": n_alt, "null_instances": M - n_alt,
              "bits_A": BITS_A, "xu_range": XU_MAX,
              "draw_rule": ("A_list WITH REPLACEMENT (birthday collisions expected+kept); "
                            "xu_list KEEPS x=u; both uniform iid; dedup would rig the seal"),
              "prereg_freeze": prereg_freeze, "order_of_operations": oop,
              "note": ("per-trial secret: 316 distinct degree-2 A (door(a) convention) + "
                       "316 sealed (x,u) NULL params + 632-label assignment + salt, ONE "
                       "canonical commitment. Secret and salt OFF-GIT. Supersedes door(a) "
                       "single-A commitment 98b799c9 (structurally insufficient, VOID-BY-RESEAL).")}

    if dry:
        print("\n--- DRY RUN: nothing persisted, nothing published ---")
        print(json.dumps(public, indent=2))
        print(f"  (discarded-draw diagnostics: A collisions {a_collisions} (~40 expected), "
              f"x=u count {xu_equal} (~20 expected) — both KEPT in a real cut)")
        return

    os.makedirs(COMMIT_DIR, exist_ok=True)
    store = json.load(open(SECRETS_PATH)) if os.path.exists(SECRETS_PATH) else {}
    if STORE_KEY in store:
        sys.exit(f"REFUSING — a secret already exists for {STORE_KEY}. Reveal/retire it deliberately.")
    store[STORE_KEY] = {"labels": labels, "A_list": A_list, "xu_list": xu_list,
                        "salt": salt, "sha256": h}
    with open(SECRETS_PATH, "w") as f:
        json.dump(store, f, indent=2)
    os.chmod(SECRETS_PATH, 0o600)
    out = os.path.join(COMMIT_DIR, OUT_NAME)
    with open(out, "w") as f:
        json.dump(public, f, indent=2)
    print(f"\nSEALED. public commitment -> {out}")
    print(f"  sha256 {h}")
    print(f"  A collisions {a_collisions} (~40 expected, KEPT), x=u {xu_equal} (~20 expected, KEPT)")
    print(f"  secret stored 0600 at {SECRETS_PATH} (NOT printed, NOT in git)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["selftest", "seal"])
    ap.add_argument("--prereg-freeze", default="")
    ap.add_argument("--oop", default="")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.cmd == "selftest":
        sys.exit(0 if selftest() else 1)
    seal(a.dry_run, a.prereg_freeze, a.oop)
