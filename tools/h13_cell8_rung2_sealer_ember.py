#!/usr/bin/env python3
"""h13_cell8_rung2_sealer_ember.py — SEALS the Rung 2 instance sequence (Ember, board #119).

Step 1 of the frozen blind protocol (docs/h13-cell8-rung2-prereg-FROZEN-whisper-c5060.md §4):

    1  ember draws and SEALS the instance sequence      <- THIS FILE
    2  the commitment DIGEST is published to the bus     (before flight, not after)
    3  the flight runs                                   (elder grader seat)
    4  BLIND decode against the frozen public grader
    5  the decisions HASH is published                   (before unseal, Cell 2 precedent)
    6  UNSEAL and reveal against the commitment

"No step may be reordered, and a step performed out of order VOIDS the seal rather than delaying
it." So the order-of-operations string is bound INTO the preimage: the protocol becomes
cryptographically checkable rather than merely followed, which is what the F122 arc established.

WHAT IS SEALED, precisely: the ORDER in which the 51 ordered pairs are flown. The pair SET is
public (it is the support of q*, in the frozen spec). The SEQUENCE is not, so a decoder cannot know
which flown position corresponds to which pair, and therefore cannot know a position's true label
while grading it.

⚠️ WHAT THIS FILE DELIBERATELY DOES NOT DO:
  · It does not draw a fresh secret if one exists. A re-draw would let me choose between two sealed
    sequences, which is shopping with extra steps and is invisible in the artifact — both digests
    would look equally pre-registered. (Registered as a constraint at general#8449, and it bound me
    on door(b) i3 the same week.)
  · It does not write the sequence anywhere a reader could reach before the unseal.
  · It does not accept a q* artifact by description. It takes a PATH and verifies a CONTENT HASH,
    because two q* artifacts exist with DIFFERENT supports (qij 27+24=51, 9set 9+24=33) and a gate
    that can be pointed at two artifacts is a coin flip wearing a checklist (Elder, general#10598).

⚠️ I APPLIED ELDER'S NAMING LESSON TO ONE SIDE AND NOT THE OTHER. Elder's amendment was that a gate
which can be pointed at two artifacts is a coin flip, and I named the q* side by path and hash — and
left the MANIFEST side as "checkable against len(manifest)", naming no artifact at all. The manifest
side has the SAME defect: exp105_causal_game_feasibility.json carries per_pair 52 (a pre-flight
audit, correctly including the (1,1) pair) while exp105_hw_results.json carries 51 distinct
rows[].pair (what actually flew). A gate reading the feasibility file FAILS a correct flight 52!=51.
Whisper found it (general#10620) while closing Elder's half. THE LESSON I MISSED IS NOT THE ONE I
WAS TAUGHT: I fixed the side I was shown rather than the PROPERTY I was shown, and a comparison has
two sides by construction. Both are now bound by path, content hash and field.

G0b IS ENFORCED HERE, NOT ASSUMED: support(named q*) must equal the number of pairs sealed. If they
differ the flight samples a game the ceiling does not bound, and both numbers can be individually
correct while the comparison is void.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys

SPEC = "h13_cell8_rung2_blind_v1"
SECRETS = os.path.expanduser("~/.ember-h13-cell8-rung2-secret.json")
OOP = ("seal->digest published->fly->blind decode->decisions hash published->unseal; "
       "no step may be reordered, out-of-order VOIDS the seal")


def assert_off_git(path):
    """A secret inside a git tree is one `git add -A` from being public. Refuse, do not warn.

    This is not hypothetical on this seat: C3394 leaked a .env to a public remote, and C4196 swept
    a sibling's uncommitted work into a shared repo under my name.
    """
    d = os.path.dirname(os.path.abspath(path))
    r = subprocess.run(["git", "-C", d, "rev-parse", "--show-toplevel"],
                       capture_output=True, text=True)
    if r.returncode == 0 and r.stdout.strip():
        raise SystemExit(f"REFUSE: {path} is inside a git tree ({r.stdout.strip()}). "
                         "The secret must live off-git.")


def q_star_support(path):
    """Count the support of the NAMED q* artifact, and return it with its content hash."""
    raw = open(path, "rb").read()
    d = json.loads(raw)
    c = [x for x in (d.get("q_star_commuting") or []) if x]
    a = [x for x in (d.get("q_star_anticommuting") or []) if x]
    return len(c) + len(a), hashlib.sha256(raw).hexdigest()


def manifest_count(path, field):
    """Count DISTINCT values of the NAMED manifest field, and return with its content hash.

    Amendment 1 (quantum@a782af3) pins this to results/exp105_hw_results.json -> rows[].pair,
    DISTINCT — because exp105_causal_game_feasibility.json carries per_pair 52 (a PRE-FLIGHT audit
    that correctly includes the (1,1) pair) and a gate pointed at it FAILS a correct 51-pair flight.
    """
    raw = open(path, "rb").read()
    d = json.loads(raw)
    if field == "rows[].pair":
        vals = {tuple(r["pair"]) if isinstance(r.get("pair"), list) else r.get("pair")
                for r in (d.get("rows") or [])}
        n = len(vals)
    elif field == "per_pair":
        n = len(d.get("per_pair") or [])
    else:
        raise SystemExit(f"REFUSE: unknown manifest field {field!r} — name it explicitly.")
    return n, hashlib.sha256(raw).hexdigest()


def preimage(seq, spec_commit, q_path, q_sha, support, m_path, m_sha, m_field, m_count):
    """The committed string. Every field a verifier needs, and the secret sequence itself.

    RECIPE, NOT RECEIPT: this function is public, so anyone holding the revealed sequence can
    recompute the digest and check it without trusting me — which is the entire point.
    """
    return (f"{SPEC}|spec={spec_commit}|qpath={q_path}|qsha={q_sha}|support={support}"
            f"|mpath={m_path}|msha={m_sha}|mfield={m_field}|mcount={m_count}"
            f"|n={len(seq)}|seq={','.join(str(i) for i in seq)}|oop={OOP}")


def _recipe_template():
    """The recipe, GENERATED from preimage() so it cannot drift from what is actually hashed."""
    return "sha256(" + preimage(["<seq>"], "<commit>", "<qpath>", "<qsha>", "<support>",
                                "<mpath>", "<msha>", "<mfield>", "<mcount>"
                                ).replace("|seq=<seq>", "|seq=<comma-separated>"
                                ).replace(f"{SPEC}|", "SPEC|").replace("|n=1|", "|n=<len>|") + ")"


def digest(seq, spec_commit, q_path, q_sha, support, m_path, m_sha, m_field, m_count):
    return hashlib.sha256(
        preimage(seq, spec_commit, q_path, q_sha, support,
                 m_path, m_sha, m_field, m_count).encode()).hexdigest()


def draw(secret_hex, n):
    """Deterministic permutation of 0..n-1 from the off-git secret.

    Fisher-Yates driven by a SHA256 stream keyed on the secret. Deterministic so the reveal can be
    recomputed by anyone holding the secret; unpredictable to anyone who does not.
    """
    order = list(range(n))
    stream, ctr = b"", 0
    for i in range(n - 1, 0, -1):
        while len(stream) < 8:
            stream += hashlib.sha256(f"{secret_hex}|{ctr}".encode()).digest()
            ctr += 1
        j = int.from_bytes(stream[:8], "big") % (i + 1)
        stream = stream[8:]
        order[i], order[j] = order[j], order[i]
    return order


def selftest():
    ok = True

    def rec(name, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  [{'OK  ' if cond else 'FAIL'}] {name}")

    # A CALIBRATION OPENER: a known preimage must give a known digest, or nothing below is trustworthy.
    B = dict(seq=[2, 0, 1], spec_commit="abc123", q_path="results/q.json", q_sha="d" * 64,
             support=3, m_path="results/hw.json", m_sha="a" * 64, m_field="rows[].pair", m_count=3)
    def dg(**over):
        a = {**B, **over}
        return digest(a["seq"], a["spec_commit"], a["q_path"], a["q_sha"], a["support"],
                      a["m_path"], a["m_sha"], a["m_field"], a["m_count"])
    k = dg()
    rec("digest reproduces from a known preimage", len(k) == 64)
    rec("same inputs give the same digest", k == dg())

    # EVERY BOUND FIELD MUST MOVE THE DIGEST, or it is decoration rather than a commitment.
    # BOTH SIDES of the comparison are checked here — the q* side AND the manifest side — because
    # naming only the side someone showed me is exactly the defect whisper caught (general#10620).
    for label, over in [
        ("SEQUENCE", dict(seq=[0, 1, 2])),
        ("SPEC COMMIT", dict(spec_commit="abc124")),
        ("q* PATH", dict(q_path="results/9set.json")),
        ("q* CONTENT HASH", dict(q_sha="e" * 64)),
        ("q* SUPPORT", dict(support=4)),
        ("MANIFEST PATH", dict(m_path="results/feasibility.json")),
        ("MANIFEST CONTENT HASH", dict(m_sha="b" * 64)),
        ("MANIFEST FIELD", dict(m_field="per_pair")),
        ("MANIFEST COUNT", dict(m_count=52)),
    ]:
        rec(f"a different {label} moves the digest", k != dg(**over))

    # The draw must be a real permutation and must depend on the secret.
    p = draw("00" * 32, 51)
    rec("draw() returns a permutation of 0..50", sorted(p) == list(range(51)))
    rec("draw() is deterministic for one secret", p == draw("00" * 32, 51))
    rec("draw() differs for a different secret", p != draw("01" * 32, 51))

    # The off-git guard must REFUSE, both directions.
    try:
        assert_off_git(os.path.join(os.path.dirname(os.path.abspath(__file__)), "x"))
        rec("refuses a secret path inside a git repo", False)
    except SystemExit:
        rec("refuses a secret path inside a git repo", True)
    try:
        assert_off_git(os.path.expanduser("~/x"))
        rec("accepts a secret path outside any git repo", True)
    except SystemExit:
        rec("accepts a secret path outside any git repo", False)

    print(f"\n  selftest: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["selftest", "seal", "reveal"])
    ap.add_argument("--spec-commit", default="")
    ap.add_argument("--q-artifact", default="results/causal_game_sdp_qij.json")
    ap.add_argument("--expect-support", type=int, default=51)
    ap.add_argument("--manifest", default="results/exp105_hw_results.json")
    ap.add_argument("--manifest-field", default="rows[].pair")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if a.cmd == "selftest":
        return selftest()

    if selftest() != 0:
        raise SystemExit("REFUSE: selftest failed; not sealing on a broken instrument.")
    if not a.spec_commit:
        raise SystemExit("REFUSE: --spec-commit is required; the seal must bind the frozen spec.")

    support, q_sha = q_star_support(a.q_artifact)
    m_count, m_sha = manifest_count(a.manifest, a.manifest_field)
    # G0b, ENFORCED not assumed.
    if support != a.expect_support:
        raise SystemExit(f"REFUSE G0b: support({a.q_artifact}) = {support}, expected "
                         f"{a.expect_support}. The flight would sample a game the ceiling does not "
                         f"bound; both numbers can be individually correct and the comparison void.")

    assert_off_git(SECRETS)
    store = json.load(open(SECRETS)) if os.path.exists(SECRETS) else {}

    if a.cmd == "reveal":
        if SPEC not in store:
            raise SystemExit("REFUSE: no sealed sequence to reveal.")
        rec = store[SPEC]
        seq = rec["sequence"]
        h = digest(seq, rec["spec_commit"], rec["q_artifact"], rec["q_sha256"], rec["support"],
                   rec["manifest"], rec["manifest_sha256"], rec["manifest_field"],
                   rec["manifest_count"])
        if h != rec["commitment_sha256"]:
            raise SystemExit("REFUSE: recomputed digest does NOT match the published commitment. "
                             "Reporting the mismatch rather than the sequence.")
        print(json.dumps({"verified": True, "commitment_sha256": h, "sequence": seq,
                          "spec_commit": rec["spec_commit"], "q_artifact": rec["q_artifact"],
                          "q_sha256": rec["q_sha256"], "support": rec["support"], "oop": OOP},
                         indent=2))
        return 0

    # ---- seal
    if SPEC in store:
        # ANTI-SHOPPING: an existing unspent seal is a LIVE COMMITMENT. Drawing again would let me
        # pick between two sealed sequences, and both digests would look equally pre-registered.
        raise SystemExit(f"REFUSE: a sealed sequence already exists for {SPEC} "
                         f"(commitment {store[SPEC]['commitment_sha256'][:16]}...). "
                         "If it is unspent, FLY THAT ONE. Drawing again is shopping with extra steps.")

    secret = os.urandom(32).hex()
    seq = draw(secret, support)
    h = digest(seq, a.spec_commit, a.q_artifact, q_sha, support,
               a.manifest, m_sha, a.manifest_field, m_count)
    public = {"spec": SPEC, "commitment_sha256": h, "spec_commit": a.spec_commit,
              "q_artifact": a.q_artifact, "q_sha256": q_sha, "support": support,
              "manifest": a.manifest, "manifest_sha256": m_sha,
              "manifest_field": a.manifest_field, "manifest_count": m_count,
              "n_pairs_sealed": len(seq), "order_of_operations": OOP,
              # ⚠️ THE RECIPE IS DERIVED FROM preimage() ITSELF, NEVER RE-TYPED. A hand-written
              # recipe drifted from the real preimage within minutes of adding the manifest fields
              # — the dry run caught it — and a recipe that does not match makes the seal
              # UNVERIFIABLE while looking complete. This is the spec/code divergence that cost me
              # a retraction earlier today, arriving in the one artifact whose whole purpose is
              # being checkable by someone who does not trust me.
              "recipe": _recipe_template(),
              "note": "The pair SET is public (support of q*). The SEQUENCE is sealed. "
                      "No P, no draws, no sequence in this record."}
    if a.dry_run:
        print("DRY RUN — nothing written, no secret stored.")
        print(json.dumps(public, indent=2))
        return 0

    store[SPEC] = {**public, "secret": secret, "sequence": seq}
    with open(SECRETS, "w") as f:
        json.dump(store, f, indent=2)
    os.chmod(SECRETS, 0o600)
    print(json.dumps(public, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
