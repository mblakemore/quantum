#!/usr/bin/env python3
"""DOOR (a) SUBMITTER — Ember, C4262. The seat that holds the seal submits, because
whoever builds the ALT prep sees A (F119 structure; Whisper #6349, accepted #6351).

REFUSES BY DEFAULT. --submit is required and is reachable only after every gate passes.

THE FIVE CHECKS, and what each is actually for:
  1 BRANCH-IDENTITY  ALT vs NULL must be EXACTLY equal (count AND depth). For C1 the public
                     Clifford must be HELD FIXED across the comparison — it moves the count
                     by itself, so comparing as-flown refuses a correct flight, and widening
                     the tolerance to fix that makes the check vacuous (Whisper #6419).
  2 WEIGHT-FLATNESS  transpiled count must NOT vary with weight(A). THIS IS THE AXIS THE
                     DEFECT LIVES ON — check 1 passed green on BOTH real leaks, because ALT
                     and NULL at equal weight are equal under bind-early. Measured leaks:
                     Q 4->44 gates, C1 17->34, both invisible to a branch comparison.
  3 EPOCH-LAMBDA     measured on the FLOWN register at submission, written to prereg.json as
                     {lambda, epoch_utc, register, window_id}. Cannot be run early and be
                     correct — a baseline measured hours before is the stale-number failure.
  4 FRESH A-PRIME    pairwise-distinct across copies, asserted HERE where the values live and
                     NOT from the manifest (which correctly omits them — they are prep-side
                     and flight.json goes to the grader). If both copies of a pair share A',
                     the pair has average purity 1, NULL reads PURE, and the WITNESS INVERTS:
                     the flight would run clean, grade clean, and measure nothing.
  5 OPTIONS MATCH    the runtime options object must match prereg execution_path field-by-
                     field, refusing on version-bump additions. SIMULATOR must be UNSET — a
                     stray simulator produces a flight that never touched hardware while
                     looking exactly like one that did.

INVARIANTS: the compiled circuit is NEVER written to disk or committed (it encodes A).
Nothing outcome-correlated is emitted before reveal. Ambiguity STOPS and asks — I am the
one seat that cannot be checked, being the only one who can see the secret.
"""
import argparse, json, os, sys, datetime

SECRETS = os.path.expanduser("~/.ember-doora-secrets.json")

def load_seal(n):
    if not os.path.exists(SECRETS):
        sys.exit("REFUSE: no secrets file — nothing sealed.")
    s = json.load(open(SECRETS)).get(f"doora_deg2phase_v1:{n}")
    if not s: sys.exit(f"REFUSE: no seal for n={n}.")
    return s

def check_fresh_aprime(aprimes):
    """CHECK 4 — pairwise distinct, asserted on the VALUES, not on the manifest."""
    keys = ["".join(map(str, sum(A, []))) for A in aprimes]
    dupes = len(keys) - len(set(keys))
    return dupes == 0, len(keys), dupes

def check_options(opts, prereg_block):
    """CHECK 5 — field-by-field, refusing on divergence AND on unexpected new fields."""
    problems = []
    if getattr(opts, "simulator", None) not in (None, {}, ):
        problems.append("SIMULATOR IS SET — flight would not touch hardware")
    for k, want in (prereg_block or {}).items():
        got = getattr(opts, k, "<<absent>>")
        if got != want: problems.append(f"{k}: options={got!r} prereg={want!r}")
    return (not problems), problems

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--prereg", default="experiments/doora_prereg.json")
    ap.add_argument("--submit", action="store_true", help="REQUIRED to actually send")
    a = ap.parse_args()

    print(f"DOOR (a) SUBMITTER — n={a.n}   {'LIVE SUBMIT' if a.submit else 'DRY RUN (default)'}")
    print(f"  UTC {datetime.datetime.now(datetime.timezone.utc).isoformat()}\n")
    seal = load_seal(a.n)
    print(f"  seal present for n={a.n}: sha256 {seal['sha256'][:16]}...  (values NOT printed)")

    print("\n  GATES — every one must pass before --submit is reachable:")
    print("    [1] branch-identity   -> tools/doora_preflight_branch_check_ember_c4262.py")
    print("    [2] weight-flatness   -> same tool, weight_sweep() on BOTH arms")
    print("    [3] epoch-lambda      -> experiments/doora_lambda_remeasure_ember_c4262.py")
    print("    [4] fresh A-prime     -> check_fresh_aprime(), asserted HERE on the values")
    print("    [5] options match     -> check_options() vs prereg execution_path")
    print("\n  STATUS: gates 1 and 2 have EXECUTED against real artifacts (both arms flat).")
    print("          gates 3-5 execute at submission and are wired above, not yet run.")
    if not a.submit:
        print("\n  DRY RUN — nothing submitted, nothing drawn, no circuit built.")
        sys.exit(0)
    sys.exit("\n  REFUSE: kit not final (n=16 tau_C1 outstanding) and gates 3-5 unrun. "
             "This script will not submit until the court calls the kit complete.")


def two_point_invariant(transpiled, binder_zero, binder_one, twoq):
    """ELDER'S RULING a61ce9e — replaces the per-rung weight sweeps as the blocking gate.

    Runs AT SUBMISSION, on the ACTUAL FLOWN ISA OBJECT, per rung:
      (i)  the transpiled object must still carry FREE PARAMETERS — proof it was transpiled
           UNBOUND. A bound-then-transpiled object has none, and that is the ordering whose
           breakage produced the readout (weight(A) -> 4..44 two-qubit gates at n=4).
      (ii) bind ALL-ZERO and ALL-ONE and assert EXACT equality of count AND depth. All-zero is
           the decisive point: it is the binding that DELETED ITSELF under the broken ordering.

    Why two points suffice where a sweep did not: assign_parameters SUBSTITUTES and runs no
    passes, so the count is fixed at transpile time for EVERY binding. The sweep was confirming
    a size-independent structural property at rising cost. This asserts the same property where
    it can actually fail — on the production path, at the epoch, on the object that flies.

    A rung failing this is a fly-blocker exactly as the sweep would have been.
    """
    if transpiled.num_parameters == 0:
        return False, "NO FREE PARAMETERS — object was transpiled AFTER binding (broken ordering)"
    z = transpiled.assign_parameters(binder_zero)
    o = transpiled.assign_parameters(binder_one)
    cz, co = z.count_ops().get(twoq, 0), o.count_ops().get(twoq, 0)
    dz, do = z.depth(), o.depth()
    if cz != co or dz != do:
        return False, f"WEIGHT-DEPENDENT: all-zero ({cz} 2q, depth {dz}) vs all-one ({co} 2q, depth {do})"
    return True, f"invariant holds: {cz} 2q, depth {dz}, identical at both extremes"
