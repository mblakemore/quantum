#!/usr/bin/env python3
"""Exp142 **P1** hidden-Pauli sealed-commitment tool (Ember, C4216).

WHY THIS EXISTS (the gap it closes)
-----------------------------------
The P1 protocol (n=4/6/8/10 rungs, `p1_allpaulis` ensemble) uses a DIFFERENT
commitment protocol from the Stage-1 tool `tools/exp142_sealer_ember.py`:

                        Stage-1 tool                     P1 (flown)
  preimage    salt_bytes || utf8("exp142|{ens}|{n}|{P}")  utf8(P + '|' + salt_hex)
  secrets     ~/.ember-exp142-secrets.json                ~/.ember-p1-secrets.json
  fields      {P, salt_hex}                               {P, salt, hash}
  draw select prefix  key.startswith("allpauli")          n/a
  tag                 "fullweight_eps1"                   "p1_allpaulis"

Consequence verified at C4216: the Stage-1 tool REJECTS the P1 ensemble tag
outright (`draw_pauli(n,"p1_allpaulis")` -> ValueError: unknown ensemble, because
"p1_allpaulis" does not *start with* "allpauli"), and its preimage/field schema
would produce a hash the P1 consumers cannot verify. So the Stage-1 tool must NOT
be used for P1 rungs.

What the P1 rungs actually used was the seal block INSIDE
`experiments/exp142_p1_submit_ember_c4215.py --submit` (line ~118), which seals
**and builds and flies in one command**, plus HAND-AUTHORED commitment/reveal
JSONs (the submit script only prints the hash; it writes no commitment artifact).

That is fine once. It does not survive a 4-7 rung serial ladder, for two reasons:

  1. SEAT SEPARATION. The ceiling-hunt prereg (§2) orders the court
     GATE -> SEAL (Ember) -> FLIGHT (Whisper) -> BLIND DECODE (Elder) -> REVEAL.
     A seal welded to the flight makes that ordering unimplementable: one seat
     must run the other's step. This is pattern c4215_008 exactly — the
     who-builds-what division is an INTEGRITY MECHANISM, and sealing in the same
     motion as the flight closes the pre-seal inspection window.
  2. HAND-AUTHORED ARTIFACTS. The public commitment JSON and the reveal JSON were
     written by hand per rung. Both are on the unrecoverable side of the protocol:
     a wrong field, spec string, or hash in a PUBLISHED commitment cannot be fixed
     after the flight without destroying the blindness claim it exists to prove.
     (Pattern c4186_001: a never-run path is BROKEN by default; the fix is a
     committed path, not vigilance.)

This tool therefore does exactly the SEAL and REVEAL steps, nothing else — no
build, no submit, no QPU, no backend import. It never needs the decoder and the
decoder never needs it.

PROTOCOL (FROZEN — matches the flown n=4/6/8/10 rungs bit-for-bit)
------------------------------------------------------------------
  preimage = utf8(P + '|' + salt_hex)
  hash     = sha256(preimage).hexdigest()
  salt     = 32 bytes OS entropy, hex (64 chars)
  P        ~ uniform over the 4**n - 1 non-identity Paulis in {I,X,Y,Z}^n
             (I-sites allowed; the all-I string is rejected and redrawn)
  secrets  ~/.ember-p1-secrets.json, key "p1_allpaulis:{n}",
           fields {"P","salt","hash"}, indent=1, chmod 600
           ^ schema preserved EXACTLY so all five existing P1 consumers keep
             working unchanged (consumer-shape discipline, c4108_001):
             exp142_p1_submit_ember_c4215.py, exp142_p1_n10_qarm_flight_whisper_c5013.py,
             exp142_p1_c1_refly_{ember_c4215,alt_c5012,whisperpaid_c5012}.py

DISCLOSED DELIBERATE CHANGE (one, and only one): the P draw uses `secrets.choice`
(CSPRNG) where the submit script used `numpy.random.default_rng()` (OS-seeded
PRNG). Same distribution — uniform over the same 4**n-1 support, which is what
the prereg pins ("p1_allpaulis, OS entropy") — strictly stronger generator. Any
n is supported, including ODD n (verified n=13/17), so a densified ladder
(12/13/14/...) is sealable without a protocol change.

ANCHOR: `selftest` reproduces the FLOWN n=10 commitment hash
d95b281bb3ba89a3f24abdf5758eedddfccb803dc47ac8a387eb78b2a35abc8a from the
revealed artifact. That is a regression test against the real published rung, not
a self-consistency check of this file.

BLINDNESS DISCIPLINE
--------------------
`seal` prints the HASH ONLY, never P. `reveal` prints P — that is its whole job,
and it refuses to run unless a public commitment already exists to be bound by.
Ember does not read decoder code between seal and reveal; Whisper/Elder do not
read the secrets file (honor protocol, same-host filesystem).

USAGE
-----
  seal   --n 12 --prereg-freeze <sha> --oop "<order-of-operations proof>"
  seal   --n 12 ... --dry-run          # show the artifact, draw nothing
  status --n 12                        # what exists for this rung (no secrets shown)
  reveal --n 12 [--verdict-file v.json]
  verify --n 12                        # recompute hash from reveal vs commitment
  selftest                             # flown-anchor + odd-n + refusals + roundtrip
"""
import argparse, hashlib, json, os, secrets, shutil, sys, tempfile
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMMIT_DIR = os.path.join(REPO, "experiments", "exp142_commitments")
SECRETS_PATH = os.path.expanduser("~/.ember-p1-secrets.json")
ENSEMBLE = "p1_allpaulis"
PREIMAGE_SPEC = "sha256(utf8(P + '|' + salt_hex))"
COMMITTER = "Ember (DC15E)"

# The flown n=10 rung — regression anchor for `selftest`.
ANCHOR_N = 10
ANCHOR_HASH = "d95b281bb3ba89a3f24abdf5758eedddfccb803dc47ac8a387eb78b2a35abc8a"


# ---------------------------------------------------------------- protocol core

def commit_hash(P: str, salt_hex: str) -> str:
    """FROZEN preimage. Must not change: published commitments depend on it."""
    return hashlib.sha256((P + "|" + salt_hex).encode()).hexdigest()


def draw_pauli(n: int) -> str:
    """Uniform over the 4**n - 1 non-identity Paulis (I-sites allowed)."""
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")
    while True:
        P = "".join(secrets.choice("IXYZ") for _ in range(n))
        if P.count("I") < n:          # reject the all-identity string only
            return P


def skey(n: int) -> str:
    return f"{ENSEMBLE}:{n}"


def commitment_path(n: int, commit_dir=None) -> str:
    return os.path.join(commit_dir or COMMIT_DIR, f"commitment_{ENSEMBLE}_n{n}.json")


def reveal_path(n: int, commit_dir=None) -> str:
    return os.path.join(commit_dir or COMMIT_DIR, f"reveal_{ENSEMBLE}_n{n}.json")


def load_secrets(path=None):
    p = path or SECRETS_PATH
    if os.path.exists(p):
        with open(p) as f:
            return json.load(f)
    return {}


def save_secrets(d, path=None):
    p = path or SECRETS_PATH
    with open(p, "w") as f:
        json.dump(d, f, indent=1)      # indent=1 preserves the flown file's shape
    os.chmod(p, 0o600)


# -------------------------------------------------------------------- commands

def cmd_seal(args, commit_dir=None, secrets_path=None):
    n = args.n
    cpath = commitment_path(n, commit_dir)
    sec = load_secrets(secrets_path)

    # REFUSAL 1 (no override): a PUBLISHED commitment is immutable. Re-sealing
    # behind a public hash is the one move that silently destroys blindness.
    if os.path.exists(cpath):
        print(f"REFUSE: {cpath} already exists — a published commitment is IMMUTABLE.\n"
              f"        Re-sealing behind a public hash would void the rung's blindness.\n"
              f"        To re-run a rung, use a NEW n or a new ensemble tag in a new prereg.")
        return 3

    # REFUSAL 2 (overridable only while nothing is published): stale secret.
    if skey(n) in sec and not args.force:
        print(f"REFUSE: secret {skey(n)} already held (no commitment published yet).\n"
              f"        Use --force to redraw — safe ONLY because nothing is public.")
        return 3

    if args.dry_run:
        print(f"DRY-RUN n={n}: would draw P ~ uniform over 4^{n}-1 = {4**n - 1} non-identity Paulis,\n"
              f"  salt = 32B OS entropy (hex), hash = {PREIMAGE_SPEC},\n"
              f"  commitment -> {cpath}\n"
              f"  secret     -> {secrets_path or SECRETS_PATH} key {skey(n)} (chmod 600)\n"
              f"  NOTHING DRAWN, NOTHING WRITTEN.")
        return 0

    P = draw_pauli(n)
    salt = secrets.token_hex(32)
    h = commit_hash(P, salt)

    # Secret first, then the public commitment: if we crash between the two, we
    # hold an unpublished secret (recoverable) rather than a published hash with
    # no secret behind it (unrecoverable — the rung could never be revealed).
    sec[skey(n)] = {"P": P, "salt": salt, "hash": h}
    save_secrets(sec, secrets_path)

    commitment = {
        "n": n,
        "ensemble": ENSEMBLE,
        "hash_sha256": h,
        "preimage_spec": f"{PREIMAGE_SPEC}  [FROZEN, prereg 4.3 @ {args.prereg_freeze}]",
        "prereg_freeze_commit": args.prereg_freeze,
        "order_of_operations_proof": args.oop,
        "sealer_tool": "tools/exp142_p1_sealer_ember.py (C4216)",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "committer": COMMITTER,
    }
    os.makedirs(os.path.dirname(cpath), exist_ok=True)
    with open(cpath, "w") as f:
        json.dump(commitment, f, indent=2)

    print(f"SEALED n={n}  hash (PUBLIC) = {h}")
    print(f"  commitment -> {cpath}   [COMMIT THIS]")
    print(f"  secret held off-git at {secrets_path or SECRETS_PATH} (chmod 600); P NOT printed by design")
    return 0


def cmd_status(args, commit_dir=None, secrets_path=None):
    n = args.n
    cpath, rpath = commitment_path(n, commit_dir), reveal_path(n, commit_dir)
    sec = load_secrets(secrets_path)
    held = skey(n) in sec
    print(f"rung n={n} ({ENSEMBLE}):")
    print(f"  secret held      : {'YES' if held else 'no'}")
    print(f"  commitment public: {'YES  ' + json.load(open(cpath))['hash_sha256'][:16] + '…' if os.path.exists(cpath) else 'no'}")
    print(f"  revealed         : {'YES' if os.path.exists(rpath) else 'no'}")
    if held and not os.path.exists(cpath):
        print("  ⚠ secret without published commitment — seal did not finish; safe to --force redraw")
    if os.path.exists(cpath) and not held:
        print("  ⚠ PUBLISHED COMMITMENT WITH NO SECRET — this rung can never be revealed. Escalate.")
    return 0


def cmd_reveal(args, commit_dir=None, secrets_path=None):
    n = args.n
    cpath, rpath = commitment_path(n, commit_dir), reveal_path(n, commit_dir)
    sec = load_secrets(secrets_path)

    if not os.path.exists(cpath):
        print(f"REFUSE: no published commitment at {cpath} — nothing to be bound by.\n"
              f"        Revealing a P that was never publicly committed proves nothing.")
        return 3
    if skey(n) not in sec:
        print(f"REFUSE: no secret for {skey(n)}.")
        return 3

    s = sec[skey(n)]
    committed = json.load(open(cpath))["hash_sha256"]
    recomputed = commit_hash(s["P"], s["salt"])
    if recomputed != committed:
        print(f"ABORT: secret/commitment DESYNC for n={n}.\n"
              f"  recomputed {recomputed}\n  committed  {committed}\n"
              f"  Refusing to publish a reveal that does not open the public hash. Escalate to the court.")
        return 4

    reveal = {
        "n": n,
        "ensemble": ENSEMBLE,
        "P": s["P"],
        "salt_hex": s["salt"],
        "commit_hash_sha256": committed,
        "preimage_spec": json.load(open(cpath))["preimage_spec"],
        "revealed": datetime.now(timezone.utc).isoformat(),
        "revealer": COMMITTER,
    }
    if args.verdict_file:
        reveal["verdict"] = json.load(open(args.verdict_file))
    with open(rpath, "w") as f:
        json.dump(reveal, f, indent=1)
    print(f"REVEALED n={n}: P = {s['P']}")
    print(f"  hash opens the public commitment: {committed[:16]}… ✓")
    print(f"  -> {rpath}   [COMMIT THIS]")
    return 0


def cmd_verify(args, commit_dir=None, secrets_path=None):
    n = args.n
    c = json.load(open(commitment_path(n, commit_dir)))
    r = json.load(open(reveal_path(n, commit_dir)))
    salt = r.get("salt_hex") or r.get("salt")
    h = commit_hash(r["P"], salt)
    ok = h == c["hash_sha256"]
    print(f"n={n} {'MATCH' if ok else 'MISMATCH'}: recomputed={h} committed={c['hash_sha256']}")
    return 0 if ok else 1


# -------------------------------------------------------------------- selftest

def cmd_selftest(args, **kw):
    fails = []

    def check(name, cond, detail=""):
        print(f"  {'PASS' if cond else 'FAIL'}  {name}{'' if cond else '  <- ' + detail}")
        if not cond:
            fails.append(name)

    print("P1 SEALER SELFTEST")
    print("\n[1] FLOWN ANCHOR — reproduce the published n=10 rung from its revealed artifact")
    rp = reveal_path(ANCHOR_N)
    if os.path.exists(rp):
        r = json.load(open(rp))
        h = commit_hash(r["P"], r.get("salt_hex") or r.get("salt"))
        check(f"n={ANCHOR_N} hash == flown {ANCHOR_HASH[:16]}…", h == ANCHOR_HASH, f"got {h}")
        cp = commitment_path(ANCHOR_N)
        if os.path.exists(cp):
            check("flown commitment file agrees",
                  json.load(open(cp))["hash_sha256"] == ANCHOR_HASH)
    else:
        check("flown n=10 reveal artifact present", False, f"missing {rp}")

    print("\n[2] DRAW — support, non-identity, ODD n (densified ladder)")
    for n in (12, 13, 14, 15, 16, 17, 18):
        P = draw_pauli(n)
        check(f"n={n} draw len/alphabet/non-identity",
              len(P) == n and set(P) <= set("IXYZ") and P.count("I") < n, P)
    # distribution sanity: I-sites must actually occur (all-Paulis, not full-weight)
    seen_I = any("I" in draw_pauli(12) for _ in range(60))
    check("I-sites occur (all-Paulis ensemble, not full-weight)", seen_I)

    print("\n[3] STAGE-1 TOOL IS NOT INTERCHANGEABLE (the divergence this tool exists for)")
    s1 = os.path.join(REPO, "tools", "exp142_sealer_ember.py")
    if os.path.exists(s1):
        import importlib.util
        spec = importlib.util.spec_from_file_location("_s1", s1)
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        rejected = False
        try:
            m.draw_pauli(12, ENSEMBLE)
        except ValueError:
            rejected = True
        check(f"Stage-1 tool rejects '{ENSEMBLE}' (documented, not assumed)", rejected,
              "Stage-1 now accepts the P1 tag — re-check which protocol it applies")
        # and its preimage genuinely differs
        check("Stage-1 preimage differs from P1 preimage",
              hashlib.sha256(m.preimage(b"\x00" * 32, ENSEMBLE, 4, "XYZI")).hexdigest()
              != commit_hash("XYZI", ("00" * 32)))

    print("\n[4] ROUNDTRIP + REFUSALS in a sandbox (no real artifacts touched)")
    tmp = tempfile.mkdtemp(prefix="p1sealer-")
    try:
        cdir = os.path.join(tmp, "commitments"); os.makedirs(cdir)
        spath = os.path.join(tmp, "secrets.json")

        class A:  # arg shim
            n = 13; prereg_freeze = "deadbeef"; oop = "selftest"; force = False
            dry_run = False; verdict_file = None

        check("dry-run writes nothing",
              (setattr(A, "dry_run", True),
               cmd_seal(A, cdir, spath) == 0,
               not os.path.exists(commitment_path(13, cdir)))[1:] == (True, True))
        A.dry_run = False
        check("seal ok (odd n=13)", cmd_seal(A, cdir, spath) == 0)
        check("commitment written", os.path.exists(commitment_path(13, cdir)))
        check("secret written chmod 600",
              os.path.exists(spath) and (os.stat(spath).st_mode & 0o777) == 0o600)
        check("re-seal REFUSED behind published commitment (even with --force)",
              (setattr(A, "force", True), cmd_seal(A, cdir, spath) == 3)[1])
        A.force = False
        check("reveal ok", cmd_reveal(A, cdir, spath) == 0)
        check("verify MATCH", cmd_verify(A, cdir, spath) == 0)

        # secret-without-commitment is the recoverable direction
        A.n = 15
        s = load_secrets(spath); s[skey(15)] = {"P": "X" * 15, "salt": "ab" * 32, "hash": "x"}
        save_secrets(s, spath)
        check("stale secret, no commitment -> REFUSE without --force", cmd_seal(A, cdir, spath) == 3)
        A.force = True
        check("stale secret, no commitment -> --force allowed", cmd_seal(A, cdir, spath) == 0)

        # reveal with no commitment must refuse
        A.n = 17; A.force = False
        s = load_secrets(spath); s[skey(17)] = {"P": "Z" * 17, "salt": "cd" * 32, "hash": "y"}
        save_secrets(s, spath)
        check("reveal REFUSED with no published commitment", cmd_reveal(A, cdir, spath) == 3)

        # desync must abort, not publish
        A.n = 18
        class B(A): n = 18
        cmd_seal(B, cdir, spath)
        s = load_secrets(spath); s[skey(18)]["P"] = "Y" * 18   # tamper
        save_secrets(s, spath)
        check("secret/commitment DESYNC aborts (does not publish)",
              cmd_reveal(B, cdir, spath) == 4 and not os.path.exists(reveal_path(18, cdir)))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"\n{'ALL PASS' if not fails else 'FAILURES: ' + ', '.join(fails)}")
    return 0 if not fails else 1


# ------------------------------------------------------------------------ main

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("seal", help="draw P, write secret + PUBLIC commitment (no flight, no QPU)")
    s.add_argument("--n", type=int, required=True)
    s.add_argument("--prereg-freeze", required=True, help="frozen prereg commit sha (enters the artifact)")
    s.add_argument("--oop", required=True, help="order-of-operations proof: what was committed BEFORE this seal")
    s.add_argument("--force", action="store_true", help="redraw a held secret — only if nothing is published")
    s.add_argument("--dry-run", action="store_true")

    st = sub.add_parser("status", help="what exists for a rung (shows no secrets)")
    st.add_argument("--n", type=int, required=True)

    r = sub.add_parser("reveal", help="publish P + salt, bound by the existing public commitment")
    r.add_argument("--n", type=int, required=True)
    r.add_argument("--verdict-file", help="optional JSON folded into the reveal artifact")

    v = sub.add_parser("verify", help="recompute the hash from the reveal artifact")
    v.add_argument("--n", type=int, required=True)

    sub.add_parser("selftest", help="flown-anchor + odd-n + divergence + refusal paths")

    a = ap.parse_args()
    sys.exit({"seal": cmd_seal, "status": cmd_status, "reveal": cmd_reveal,
              "verify": cmd_verify, "selftest": cmd_selftest}[a.cmd](a))
