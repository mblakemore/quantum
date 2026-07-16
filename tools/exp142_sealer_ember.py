#!/usr/bin/env python3
"""Exp142 hidden-Pauli sealed-commitment tool (Ember, C4184).

Protocol (frozen in meeting 2026-07-16, Whisper C4746 chair + Elder C6490 amendment):
  preimage = salt_bytes || utf8("exp142|{ensemble}|{n}|{P}")
  hash     = sha256(preimage), hex
  salt     = 32 bytes OS entropy (secrets.token_bytes)

One commitment JSON per n in quantum/experiments/exp142_commitments/:
  {n, ensemble, hash, timestamp, committer}
Secrets (salt hex + P) are held OFF-GIT by Ember (~/.ember-exp142-secrets.json,
chmod 600) until reveal. Order of operations: prereg freeze -> seal -> fly -> both
arms submit identifications -> reveal -> grade by hash match.

Ensemble tags are FREE-FORM and must match the frozen prereg string verbatim
(the tag enters the hash preimage). Draw rule selected by prefix:
  fullweight* (e.g. fullweight_eps1) : P uniform over {X,Y,Z}^n   (Stage-1 executed race)
  allpauli*                          : P uniform over 4^n-1 non-identity Paulis

Usage:
  seal   --n 4,6,8,10 --ensemble fullweight_eps1   draw P, write commitments, store secrets
  reveal --n 8 --ensemble fullweight_eps1          write salt+P into commitments dir
  verify --n 8 --ensemble fullweight_eps1          recompute hash from revealed file
Blindness: Ember does not read decoder code between seal and reveal; Whisper/Elder
do not read the secrets file (honor protocol, same-host filesystem).
"""
import argparse, hashlib, json, os, secrets, sys
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMMIT_DIR = os.path.join(REPO, "experiments", "exp142_commitments")
SECRETS_PATH = os.path.expanduser("~/.ember-exp142-secrets.json")


def preimage(salt: bytes, ensemble: str, n: int, P: str) -> bytes:
    return salt + f"exp142|{ensemble}|{n}|{P}".encode()


def draw_pauli(n: int, ensemble: str) -> str:
    # The ensemble TAG is free-form (it enters the hash preimage and must match the
    # frozen prereg string verbatim, e.g. "fullweight_eps1"). The DRAW RULE is
    # selected by prefix: fullweight* -> uniform {X,Y,Z}^n; allpauli*/all-pauli* ->
    # uniform non-identity {I,X,Y,Z}^n.
    key = ensemble.replace("-", "").lower()
    if key.startswith("fullweight"):
        return "".join(secrets.choice("XYZ") for _ in range(n))
    if key.startswith("allpauli"):
        while True:
            p = "".join(secrets.choice("IXYZ") for _ in range(n))
            if set(p) != {"I"}:
                return p
    raise ValueError(f"unknown ensemble {ensemble}")


def load_secrets():
    if os.path.exists(SECRETS_PATH):
        with open(SECRETS_PATH) as f:
            return json.load(f)
    return {}


def save_secrets(d):
    with open(SECRETS_PATH, "w") as f:
        json.dump(d, f, indent=2)
    os.chmod(SECRETS_PATH, 0o600)


def key(ensemble, n):
    return f"{ensemble}:{n}"


def cmd_seal(args):
    os.makedirs(COMMIT_DIR, exist_ok=True)
    sec = load_secrets()
    for n in [int(x) for x in args.n.split(",")]:
        k = key(args.ensemble, n)
        if k in sec and not args.force:
            print(f"REFUSE: {k} already sealed (use --force to redraw BEFORE any commit is published)")
            continue
        salt = secrets.token_bytes(32)
        P = draw_pauli(n, args.ensemble)
        h = hashlib.sha256(preimage(salt, args.ensemble, n, P)).hexdigest()
        sec[k] = {"salt_hex": salt.hex(), "P": P}
        commitment = {
            "n": n,
            "ensemble": args.ensemble,
            "hash_sha256": h,
            "preimage_spec": 'salt_bytes || utf8("exp142|{ensemble}|{n}|{P}")',
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "committer": "Ember (DC15E)",
        }
        path = os.path.join(COMMIT_DIR, f"commitment_{args.ensemble}_n{n}.json")
        with open(path, "w") as f:
            json.dump(commitment, f, indent=2)
        print(f"SEALED {k}: hash={h} -> {path} (secret held off-git)")
    save_secrets(sec)


def cmd_reveal(args):
    sec = load_secrets()
    k = key(args.ensemble, args.n)
    if k not in sec:
        sys.exit(f"no secret for {k}")
    reveal = {"n": args.n, "ensemble": args.ensemble, **sec[k],
              "revealed": datetime.now(timezone.utc).isoformat()}
    path = os.path.join(COMMIT_DIR, f"reveal_{args.ensemble}_n{args.n}.json")
    with open(path, "w") as f:
        json.dump(reveal, f, indent=2)
    print(f"REVEALED {k}: P={sec[k]['P']} -> {path}")


def cmd_verify(args):
    cpath = os.path.join(COMMIT_DIR, f"commitment_{args.ensemble}_n{args.n}.json")
    rpath = os.path.join(COMMIT_DIR, f"reveal_{args.ensemble}_n{args.n}.json")
    with open(cpath) as f:
        c = json.load(f)
    with open(rpath) as f:
        r = json.load(f)
    h = hashlib.sha256(preimage(bytes.fromhex(r["salt_hex"]), r["ensemble"], r["n"], r["P"])).hexdigest()
    ok = h == c["hash_sha256"]
    print(f"{'MATCH' if ok else 'MISMATCH'}: recomputed={h} committed={c['hash_sha256']}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("seal"); s.add_argument("--n", required=True, help="comma list, e.g. 4,6,8,10")
    s.add_argument("--ensemble", default="fullweight_eps1")
    s.add_argument("--force", action="store_true")
    r = sub.add_parser("reveal"); r.add_argument("--n", type=int, required=True)
    r.add_argument("--ensemble", default="fullweight_eps1")
    v = sub.add_parser("verify"); v.add_argument("--n", type=int, required=True)
    v.add_argument("--ensemble", default="fullweight_eps1")
    a = ap.parse_args()
    {"seal": cmd_seal, "reveal": cmd_reveal, "verify": cmd_verify}[a.cmd](a)
