#!/usr/bin/env python3
"""C4998 steth-advantage distinguishing flight — Ember sealer (G2).

Charge: Whisper C4998 prereg coordination#821 — "G2 @ember: seal-design ack + generation
(arm T: U + trial labels; arm N: labels)". The seal is what makes Thm 7.9 apply (the instance
must be SECRET and Haar-random, else known-structure probes beat the worst-case floor).

PROTOCOL (race-arc hygiene, prereg §3 fences 5-6):
  preimage = salt_bytes(32) || utf8(canonical_spec_string)
  hash     = sha256(preimage), hex.  Salt (32B OS entropy) + all secrets held OFF-GIT.
  Order: G1 closed -> seal (this, G2) -> G3 sims -> G4 GO -> fly -> post decisions -> REVEAL.

WHAT IS SEALED
  Arm T, per rung k in {6,9,12}:
    (U)  a Haar-random k-qubit unitary, committed via a SECRET crypto-random 32-byte SEED.
         The seed deterministically regenerates U by the PINNED draw below (Mezzadri 2007
         QR-of-Ginibre Haar algorithm on numpy default_rng(seed)). Committing the seed binds
         U without materialising/ storing a 2^k x 2^k matrix; the flight compiles U from the
         off-git seed and NEVER commits the circuit (Exp142 discipline: no public description).
    (L)  the trial-label sequence b_t in {NULL=0, ALT=1}^M, M=40, drawn as INDEPENDENT
         crypto-random bits (python secrets). Independent (not balanced 20/20) BY DESIGN:
         a fixed count is a cross-trial constraint that leaks into the per-trial decision path
         (the G2 metadata-leak mandate); independent bits keep each decision data-only.
  Arm N, per sub-block width k in {2,3}:
    (L)  trial labels b_t in {NULL=0(non-drifter block), DRIFT=1(drifter block)}^M, M=40,
         independent crypto-random bits, same reasoning.

PINNED CONVENTION (enters every U preimage; frozen here):
  * Haar draw: z = (randn(d,d)+1j*randn(d,d))/sqrt(2) via numpy.random.default_rng(int.from_bytes(seed)),
    Q,R = qr(z); U = Q @ diag(R_ii/|R_ii|).  (Mezzadri, NOTICES AMS 2007.)
  * qubit order: little-endian, qiskit convention (qubit 0 = least-significant bit).
  * U acts on the k-qubit register in that order; ALT channel = U (compiled once/rung); NULL
    channel = completely depolarizing D (fresh uniform k-qubit Pauli conjugation per copy).

Usage:
  seal    --armT 6,9,12 --armN 2,3 --M 40     draw all, write commitments, store secrets off-git
  reveal  --armT 6,9,12 --armN 2,3            write seeds+salts+labels into commitments dir
  verify                                       recompute every hash from revealed files
"""
import argparse, hashlib, json, os, secrets, sys
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMMIT_DIR = os.path.join(REPO, "results", "steth_c4998_commitments")
SECRETS_PATH = os.path.expanduser("~/.ember-steth-c4998-secrets.json")

HAAR_SPEC = ("draw=Mezzadri2007-QR-Ginibre; rng=numpy.default_rng(int.from_bytes(seed,'big')); "
             "z=(randn(d,d)+1j*randn(d,d))/sqrt2; Q,R=numpy.linalg.qr(z); U=Q@diag(R_ii/abs(R_ii)); "
             "qubit-order=little-endian-qiskit")
LABEL_SPEC = "rule=independent-crypto-random-bits(python-secrets); NULL=0,ALT=1"
ARMN_LABEL_SPEC = "rule=independent-crypto-random-bits(python-secrets); NULL=0(nondrifter),DRIFT=1(drifter)"


def commit(salt: bytes, spec: str) -> str:
    return hashlib.sha256(salt + spec.encode()).hexdigest()


def u_spec(k, seed_hex):
    return f"steth|c4998|armT|U-haar|k={k}|seed={seed_hex}|{HAAR_SPEC}"


def labelT_spec(k, M, bits):
    return f"steth|c4998|armT|labels|k={k}|M={M}|b={bits}|{LABEL_SPEC}"


def labelN_spec(k, M, bits):
    return f"steth|c4998|armN|labels|k={k}|M={M}|b={bits}|{ARMN_LABEL_SPEC}"


# ---- cross-block overlap successor card (C4998 cross-block, coordination#848) ----
# Assignment sequence over {SAME-A=0, SAME-N=1, CROSS=2}, committed via a SECRET seed +
# pinned rule (independent uniform draws). N (~10.5k) frozen at G3'; the seed binds the
# whole stream so any prefix is bound => robust to the count-freeze (generation on freeze).
XBLOCK_RULE = ("alphabet={SAME-A:0,SAME-N:1,CROSS:2}; "
               "draw=independent-uniform; rng=numpy.default_rng(int.from_bytes(seed,'big')); "
               "seq[t]=rng.integers(0,3); N frozen at G3'; per-class counts NOT fixed")


def xblock_seq(seed_bytes, N):
    import numpy as np
    rng = np.random.default_rng(int.from_bytes(seed_bytes, "big"))
    return rng.integers(0, 3, size=N).tolist()


def xblock_spec(seed_hex, n_bind):
    return f"steth|c4998|crossblock|assignment|seed={seed_hex}|N_bind={n_bind}|{XBLOCK_RULE}"


XBLOCK_COMMIT = os.path.join(COMMIT_DIR, "commitments_crossblock_c4998_ember.json")
XBLOCK_SECRETS = os.path.expanduser("~/.ember-crossblock-c4998-secrets.json")


def cmd_seal_xblock(args):
    """Seal the cross-block assignment stream: secret seed binds the whole stream up to
    N_bind; flight takes the first N (adaptive within [5500,8000]/class -> <=24k total)."""
    import numpy as np
    os.makedirs(COMMIT_DIR, exist_ok=True)
    if os.path.exists(XBLOCK_SECRETS) and not args.force:
        print("REFUSE: crossblock secret exists (use --force to redraw BEFORE any commit published)")
        return 1
    seed = secrets.token_bytes(32); salt = secrets.token_bytes(32)
    h = commit(salt, xblock_spec(seed.hex(), args.n_bind))
    # sanity: regenerate + class balance at N_bind (no secrets printed)
    seq = xblock_seq(seed, args.n_bind)
    from collections import Counter
    c = Counter(seq)
    json.dump({"seed_hex": seed.hex(), "salt_hex": salt.hex(), "n_bind": args.n_bind},
              open(XBLOCK_SECRETS, "w"), indent=2); os.chmod(XBLOCK_SECRETS, 0o600)
    commitment = {"experiment": "steth_c4998_crossblock_overlap",
                  "sealed_object": "per-SWAP assignment sequence over {SAME-A:0,SAME-N:1,CROSS:2}",
                  "assignment_hash_sha256": h, "N_bind": args.n_bind,
                  "rule": XBLOCK_RULE, "preimage_spec": "salt(32) || utf8(spec_with_seed_and_N_bind)",
                  "flight_rule": "flight consumes the first N (adaptive in [5500,8000]/class); seed binds all N<=N_bind",
                  "committer": "Ember (DC15E)", "timestamp": datetime.now(timezone.utc).isoformat()}
    json.dump(commitment, open(XBLOCK_COMMIT, "w"), indent=2)
    print(f"CROSSBLOCK SEALED (secret off-git {XBLOCK_SECRETS} chmod 600). "
          f"class balance @N_bind={args.n_bind}: SAME-A {c[0]} / SAME-N {c[1]} / CROSS {c[2]}\n"
          f"{json.dumps(commitment, indent=2)}")
    return 0


def cmd_reveal_xblock(args):
    s = json.load(open(XBLOCK_SECRETS))
    json.dump(s, open(os.path.join(COMMIT_DIR, "reveal_crossblock_c4998_ember.json"), "w"), indent=2)
    print("crossblock revealed"); return 0


def cmd_verify_xblock(args):
    C = json.load(open(XBLOCK_COMMIT)); s = json.load(open(XBLOCK_SECRETS))
    h = commit(bytes.fromhex(s["salt_hex"]), xblock_spec(s["seed_hex"], C["N_bind"]))
    ok = h == C["assignment_hash_sha256"]
    print("crossblock VERIFY", "OK" if ok else "FAIL"); return 0 if ok else 1


def selftest_xblock():
    """Dry-run: seed->sequence determinism + commit round-trip. Writes NOTHING (no live seal)."""
    seed = bytes.fromhex("5c" * 32); salt = bytes.fromhex("7e" * 32)
    s1 = xblock_seq(seed, 12000); s2 = xblock_seq(seed, 12000)
    det = s1 == s2
    prefix = xblock_seq(seed, 10500) == s1[:10500]   # any prefix is bound by the seed
    h = commit(salt, xblock_spec(seed.hex()))
    from collections import Counter
    c = Counter(s1)
    print(f"xblock selftest: deterministic={det} prefix-bound={prefix} "
          f"class-counts(N=12000)={{SAME-A:{c[0]},SAME-N:{c[1]},CROSS:{c[2]}}} "
          f"(indep-uniform ~4000 each) commit_len={len(h)}")
    return det and prefix


def load_secrets():
    return json.load(open(SECRETS_PATH)) if os.path.exists(SECRETS_PATH) else {}


def save_secrets(d):
    json.dump(d, open(SECRETS_PATH, "w"), indent=2)
    os.chmod(SECRETS_PATH, 0o600)


def rand_bits(M):
    return "".join("1" if secrets.randbelow(2) else "0" for _ in range(M))


def cmd_seal(args):
    os.makedirs(COMMIT_DIR, exist_ok=True)
    sec = load_secrets()
    if sec and not args.force:
        print("REFUSE: secrets already exist (use --force to redraw BEFORE any commit published)")
        return 1
    sec = {"armT": {}, "armN": {}, "M": args.M}
    commitments = {"experiment": "steth_c4998_advantage_distinguishing", "M": args.M,
                   "committer": "Ember (DC15E)", "convention": HAAR_SPEC,
                   "timestamp": datetime.now(timezone.utc).isoformat(),
                   "preimage_spec": "salt_bytes(32) || utf8(canonical_spec_string)",
                   "armT": {}, "armN": {}}
    # Arm T: U (secret seed) + labels
    for k in [int(x) for x in args.armT.split(",")] if args.armT else []:
        u_seed = secrets.token_bytes(32); u_salt = secrets.token_bytes(32)
        l_bits = rand_bits(args.M); l_salt = secrets.token_bytes(32)
        uh = commit(u_salt, u_spec(k, u_seed.hex()))
        lh = commit(l_salt, labelT_spec(k, args.M, l_bits))
        sec["armT"][str(k)] = {"u_seed_hex": u_seed.hex(), "u_salt_hex": u_salt.hex(),
                                "label_bits": l_bits, "label_salt_hex": l_salt.hex()}
        commitments["armT"][str(k)] = {"U_hash_sha256": uh, "labels_hash_sha256": lh}
    # Arm N: labels only (blocks are public; sealed bit = which block)
    for k in [int(x) for x in args.armN.split(",")] if args.armN else []:
        l_bits = rand_bits(args.M); l_salt = secrets.token_bytes(32)
        lh = commit(l_salt, labelN_spec(k, args.M, l_bits))
        sec["armN"][str(k)] = {"label_bits": l_bits, "label_salt_hex": l_salt.hex()}
        commitments["armN"][str(k)] = {"labels_hash_sha256": lh}
    save_secrets(sec)
    path = os.path.join(COMMIT_DIR, "commitments_steth_c4998_ember.json")
    json.dump(commitments, open(path, "w"), indent=2)
    print(f"SEALED (secrets off-git at {SECRETS_PATH}, chmod 600). Commitments:\n{json.dumps(commitments, indent=2)}")
    return 0


def cmd_reveal(args):
    sec = load_secrets()
    if not sec:
        print("no secrets to reveal"); return 1
    reveal = {"experiment": "steth_c4998_advantage_distinguishing", "M": sec["M"],
              "revealed": datetime.now(timezone.utc).isoformat(), "armT": {}, "armN": {}}
    for k, v in sec.get("armT", {}).items():
        reveal["armT"][k] = v
    for k, v in sec.get("armN", {}).items():
        reveal["armN"][k] = v
    path = os.path.join(COMMIT_DIR, "reveal_steth_c4998_ember.json")
    json.dump(reveal, open(path, "w"), indent=2)
    print(f"REVEALED -> {path}")
    return 0


def cmd_verify(args):
    cpath = os.path.join(COMMIT_DIR, "commitments_steth_c4998_ember.json")
    rpath = os.path.join(COMMIT_DIR, "reveal_steth_c4998_ember.json")
    C = json.load(open(cpath)); R = json.load(open(rpath)); M = C["M"]; ok = True
    for k, v in C["armT"].items():
        s = R["armT"][k]
        uh = commit(bytes.fromhex(s["u_salt_hex"]), u_spec(int(k), s["u_seed_hex"]))
        lh = commit(bytes.fromhex(s["label_salt_hex"]), labelT_spec(int(k), M, s["label_bits"]))
        ok &= uh == v["U_hash_sha256"] and lh == v["labels_hash_sha256"]
        print(f"armT k={k}: U {'OK' if uh==v['U_hash_sha256'] else 'FAIL'}  "
              f"labels {'OK' if lh==v['labels_hash_sha256'] else 'FAIL'}")
    for k, v in C["armN"].items():
        s = R["armN"][k]
        lh = commit(bytes.fromhex(s["label_salt_hex"]), labelN_spec(int(k), M, s["label_bits"]))
        ok &= lh == v["labels_hash_sha256"]
        print(f"armN k={k}: labels {'OK' if lh==v['labels_hash_sha256'] else 'FAIL'}")
    print("ALL VERIFY" if ok else "VERIFY FAILED"); return 0 if ok else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("seal"); s.add_argument("--armT", default="6,9,12")
    s.add_argument("--armN", default="2,3"); s.add_argument("--M", type=int, default=40)
    s.add_argument("--force", action="store_true"); s.set_defaults(fn=cmd_seal)
    r = sub.add_parser("reveal"); r.add_argument("--armT"); r.add_argument("--armN")
    r.set_defaults(fn=cmd_reveal)
    v = sub.add_parser("verify"); v.set_defaults(fn=cmd_verify)
    xt = sub.add_parser("selftest-xblock"); xt.set_defaults(fn=lambda a: 0 if selftest_xblock() else 1)
    xs = sub.add_parser("seal-xblock"); xs.add_argument("--n_bind", type=int, default=24000)
    xs.add_argument("--force", action="store_true"); xs.set_defaults(fn=cmd_seal_xblock)
    xr = sub.add_parser("reveal-xblock"); xr.set_defaults(fn=cmd_reveal_xblock)
    xv = sub.add_parser("verify-xblock"); xv.set_defaults(fn=cmd_verify_xblock)
    a = ap.parse_args()
    sys.exit(a.fn(a))
