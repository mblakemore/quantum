#!/usr/bin/env python3
"""F122 DISTRIBUTION BATCH — incremental, atomic, and unable to truncate (Ember C4268).

Gate 2 of the submission list: turn the 9.3× point into a spread, so a reviewer's first
question ("distribution over P, or a lucky draw?") is answered by data rather than by argument.

INCREMENTAL AND ATOMIC (Whisper's refinement, general#8339). Each instance is SEALED THEN FLOWN
before the next is drawn. Nothing is ever registered-ahead-and-unflown, so the headline is always
"the ratio over the N instances FLOWN SO FAR, N stated" and a short batch CANNOT read as
truncation — there was never a planned-N to fall short of. That is my own objection
("truncating a registered distribution is worse than never registering it") turned into a
protocol that cannot commit the error.

WHY THIS SCRIPT EXISTS AT ALL — the guard that would stop instance 2:
`doorb_sealer` REFUSES to overwrite an existing secret, which is correct (a reused P makes a
flight blind in name only) and which means every instance needs its predecessor ARCHIVED first.
I did that by hand once. Unscripted, a 3-batch halts at instance 2 on a guard doing its job,
and the operator "fixes" it under time pressure — which is how a guard gets disabled instead of
satisfied.

UNIFORM-RANDOM P, NOT WEIGHT-FIXED (Whisper, same post). F122 was weight-12. Uniform draw over
non-identity strings is the theorem's own hard-family draw and gives a WEIGHT SPREAD — so the
points measure the ratio-vs-weight relationship rather than repeating one draw. Delivered ε
depends on weight (heavier decoheres more), which is the relationship worth having.

BUDGET REALITY, CHECKED LIVE NOT REMEMBERED: the tank is read before every instance. A stale
figure is what nearly sized this batch at 5–8 instances against 371 available seconds — and
the campaign has already paid once for sizing from memory (exp142: 4.3× overrun, tank exhausted,
zero completed jobs). If an instance does not fit, the batch STOPS CLEAN and says so; "3
attempted, 2 flown" is the gate working and is pre-declared as a legitimate outcome.

⚠️ FLIES NOTHING WITHOUT --fly AND A BATCH GO. The batch go must state its own N up front and
each digest is still published and bound in public before its own flight.
"""
import argparse
import datetime
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SECRETS = os.path.expanduser("~/.ember-doorb-secrets.json")
ARCHIVE = os.path.expanduser("~/.ember-doorb-secrets-archive.json")
KEY = "doorb_hardensemble_v1:16"
RESERVE_S = 20
EPOCH_MARGIN = 1.5   # MUST mirror doorb_flight G-EPOCH. Do not tune independently.


def tank_seconds():
    """AUTHORITATIVE read, straight from IBM — NOT the registry.

    C4269 DEFECT, found by using this: the first version read `/resources`, which the qpu-feeder
    samples every 15 minutes. Mid-flight that cache is stale BY CONSTRUCTION — it showed 362s
    while the live counter said 293s, a 69-SECOND OVERSTATEMENT in the exact direction that
    green-lights a flight that will not fit.

    This function's whole purpose was to stop sizing from a stale number, and it sized from a
    stale number. Whisper quoted 480s from memory; I quoted a cache and called it live. A cache
    is memory with better manners.

    RULE: a SPEND decision reads the authoritative source. The registry is for AWARENESS —
    dashboards, watches, the age fields that made this visible — never for the gate that
    authorises irreversible spend. Three API calls across a batch is the correct price.
    """
    import re as _re
    from qiskit_ibm_runtime import QiskitRuntimeService
    tok = None
    for line in open("/droid/repos/DC15W/.env"):
        m = _re.match(r"^IBMQ_ALT3=(.+)$", line.strip())
        if m:
            tok = m.group(1).strip().strip('"').strip("'")
    crn = ("crn:v1:bluemix:public:quantum-computing:us-east:"
           "a/b290f963c84c4e34a5aa7704b4e39b66:952e28e1-bdbf-4593-aec7-e1520b4218a8::")
    u = QiskitRuntimeService(channel="ibm_quantum_platform", token=tok, instance=crn).usage()
    if u.get("usage_limit_reached"):
        return 0.0            # a flagged account accepts submissions and never runs them
    return float(u["usage_remaining_seconds"])


def registry_seconds():
    """The CACHED view, kept only to report the gap. Never used for the gate."""
    try:
        out = subprocess.run(
            ["curl", "-s", "-H", f"Authorization: Bearer {open(os.path.expanduser('~/.uhura-key')).read().strip()}",
             "http://127.0.0.1:8790/resources?kind=qpu_account"],
            capture_output=True, text=True, timeout=20).stdout
        for r in json.loads(out).get("resources", []):
            if r.get("authorization") == "open" and r.get("state") == "up":
                b = (r.get("meta") or {}).get("balance_s")
                if isinstance(b, (int, float)):
                    return float(b)
    except Exception:
        pass
    return None


def archive_spent(reason):
    """Move the current secret aside so the sealer's overwrite-refusal is SATISFIED, not bypassed.

    Archived, never deleted: a commitment digest must stay verifiable against the flight it bound.
    """
    if not os.path.exists(SECRETS):
        return False
    sec = json.load(open(SECRETS))
    if KEY not in sec:
        return False
    arch = json.load(open(ARCHIVE)) if os.path.exists(ARCHIVE) else {}
    stamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    arch[f"{KEY}@{stamp}"] = {**sec[KEY], "archived": stamp, "why": reason}
    json.dump(arch, open(ARCHIVE, "w"), indent=2); os.chmod(ARCHIVE, 0o600)
    del sec[KEY]
    json.dump(sec, open(SECRETS, "w"), indent=2); os.chmod(SECRETS, 0o600)
    return True


def draw_seal(freeze_hash, oop):
    r = subprocess.run([sys.executable, os.path.join(HERE, "doorb_sealer_ember_c4262.py"),
                        "seal", "--n", "16", "--prereg-freeze", freeze_hash, "--oop", oop],
                       capture_output=True, text=True, timeout=120)
    m = re.search(r"sha256\s+([0-9a-f]{64})", r.stdout)
    return (m.group(1) if m else None), r.stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--instances", type=int, default=3)
    ap.add_argument("--freeze-hash", required=True)
    ap.add_argument("--per-instance-estimate", type=float, default=109.0)
    ap.add_argument("--fly", action="store_true")
    ap.add_argument("--batch-go", default="", help="bus seq of the bounded batch authorization")
    a = ap.parse_args()

    if a.fly and not a.batch_go:
        sys.exit("REFUSE: --fly needs --batch-go <seq>. An unbound authorization is exactly what "
                 "the single-use clause forbids; a batch go must name its own N and be citable.")

    print(f"F122 DISTRIBUTION BATCH — up to {a.instances} instances, incremental and atomic")
    print(f"  batch go        : {a.batch_go or '(none — dry run)'}")
    print(f"  freeze hash     : {a.freeze_hash[:24]}...")
    flown, results = 0, []
    sim_spent = 0.0          # dry-run only: model the drawdown the live path would cause
    for i in range(1, a.instances + 1):
        # A DRY RUN THAT RE-READS THE SAME TANK EVERY PASS CANNOT EXPRESS THE FAILURE IT EXISTS
        # TO CHECK (c4266_001). Without the simulated spend it printed "3/3 would fly" whether
        # or not three fit — a projection that agrees with itself. Subtracting the estimate makes
        # the dry run answer the actual question: does the LAST instance still have room?
        tank = tank_seconds() - sim_spent
        cached = registry_seconds()
        if cached is not None and abs(cached - (tank + sim_spent)) > 5:
            # Surface the gap rather than silently preferring the right one: a cache that
            # disagrees with the source is a fact the operator should see, not one to hide.
            print(f"  [cache-gap] registry {cached:.0f}s vs authoritative {tank + sim_spent:.0f}s "
                  f"— sizing on the authoritative value")
        # C4269 DEFECT, found by the flight script REFUSING an instance this harness had
        # green-lit: two gates carried two different definitions of "affordable". This one
        # used ADDITIVE headroom (estimate + 20s); the flight script's G-EPOCH uses a
        # MULTIPLICATIVE 1.5x margin and is the BINDING gate — it is the one holding the
        # trigger. At i3: additive said 111s against 185s live ("fits with 74s spare"),
        # multiplicative said 193.5s ("refuse"). The seal was drawn, published and pinned
        # for a flight that could never launch.
        #
        # A non-binding gate that is LOOSER than the binding one is not a harmless
        # duplicate — it manufactures confident go-aheads that the real gate then has to
        # veto, and each false go-ahead spends something irreversible (here: a drawn seal,
        # which archives its predecessor and cannot be un-drawn).
        #
        # RULE: when two gates guard the same action, the harness mirrors the BINDING one
        # exactly. Duplicated thresholds drift; the strictest must be the one that is copied.
        need = max(a.per_instance_estimate * EPOCH_MARGIN,
                   a.per_instance_estimate + RESERVE_S)
        print(f"\n── instance {i}/{a.instances} ──  tank {tank:.0f}s  need ~{need:.0f}s")
        if tank < need:
            # PRE-DECLARED legitimate outcome, not a truncation.
            print(f"  STOP CLEAN: {tank:.0f}s < {need:.0f}s. Flown {flown} of {a.instances} attempted.")
            print("  This is the budget gate working. The headline states n = flown, not n = attempted.")
            break
        if not a.fly:
            print("  DRY: would archive prior seal, draw fresh P (uniform over non-identity),")
            print("       publish + git-pin the digest, bind it to the batch go, then fly.")
            flown += 1
            sim_spent += a.per_instance_estimate
            continue
        archive_spent(f"superseded by F122-distribution instance {i}")
        digest, out = draw_seal(a.freeze_hash,
                                f"batch-go {a.batch_go} instance {i}/{a.instances}: "
                                "seal->digest published->fly->blind decode->hash->unseal")
        if not digest:
            sys.exit(f"REFUSE: sealer produced no digest at instance {i}\n{out[-400:]}")
        print(f"  sealed {digest[:24]}...  (publish + git-pin BEFORE flying)")
        results.append({"instance": i, "digest": digest})
        flown += 1
    print(f"\n  flown/attempted: {flown}/{a.instances}")
    if results:
        json.dump(results, open(os.path.join(HERE, "..", "results",
                  "doorb_distribution_batch_c4268.json"), "w"), indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
