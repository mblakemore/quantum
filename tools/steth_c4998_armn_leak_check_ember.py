#!/usr/bin/env python3
"""Arm-N leak checks 2-4 — WRITTEN BEFORE THE BUNDLE EXISTS (Ember C4238).

My G2 seal card set four leak-safety requirements for Arm N. The frozen prereg closes
req 1 (block-identity-blind canonicalized decoder input) by construction in the G3
pipeline. Reqs 2-4 were recorded as FLIGHT-COMPILE CHECKS AT SUBMISSION — deferred, by
design, to exactly this moment.

WHY THIS FILE EXISTS BEFORE THE ARTIFACT IT CHECKS: a verification written after seeing
the data can be shaped by the data, and every threshold in it becomes negotiable at the
moment it matters. The thresholds below are declared now, blind, with their reasoning —
the same discipline the flight's own gates are held to. If a bar here turns out to be
wrong, it gets changed by an amendment on the record, not by editing this file quietly
once the bundle lands.

ARM N'S ENTIRE CLAIM is that the two blocks separate because of the COHERENCE being
tested and not because of anything else about them. Each check below is one "anything
else".

    2  READOUT/SPAM PROFILE MATCH  — if drifter qubits read out differently from null
       qubits, marginal 0/1 statistics separate the blocks with no coherence involved.
    3  STRUCTURAL IDENTITY         — if the compiled circuits differ in depth or gate
       content, the decoder can separate on circuit shape.
    4  LABEL-INDEPENDENT ORDER     — if delivery order correlates with the label,
       position alone predicts the answer.

Three-state, like everything else in this campaign: PASS / FAIL / NOT-EVALUABLE. A
missing field is NOT a pass — it is the third state, and it blocks the CLEAR just as a
failure does.

Usage:  steth_c4998_armn_leak_check_ember.py <preflight_bundle.json>
"""
import json
import math
import sys

# ---- PRE-DECLARED THRESHOLDS, blind, with reasons -----------------------------------

# (2) Two blocks are indistinguishable on readout if no per-qubit readout error differs
# by more than this between the matched pairs. 0.005 absolute is roughly the scale of the
# published per-qubit readout spread on this hardware; a gap larger than that is a
# marginal-statistics channel a decoder could use without touching coherence.
READOUT_TOL = 0.005

# The same in aggregate: the mean absolute difference across matched pairs. A set of small
# same-signed differences is a leak even when no single pair exceeds the per-qubit bar.
READOUT_MEAN_TOL = 0.0025

# (4) Label-order independence. With M independent bits, the count of same-label adjacent
# pairs has mean (M-1)/2 and sd sqrt(M-1)/2. A |z| beyond this says order carries label
# information. 3.0 to match the campaign's z_req everywhere else.
ORDER_Z = 3.0


def three_state(ok, evaluable, name, detail):
    state = "NOT-EVALUABLE" if not evaluable else ("PASS" if ok else "FAIL")
    print(f"  [{state:^13}] {name}")
    for line in detail:
        print(f"                  {line}")
    return state


def _pair_stats(drift, null):
    diffs = [abs(float(a) - float(c)) for a, c in zip(drift, null)]
    return max(diffs), sum(diffs) / len(diffs), len(diffs)


def _leg(d, key):
    """One cal read as {drifter:[], null:[]}. Accepts the flat single-cal shape
    (readout.drifter) and the bracketed shape (readout.start.drifter)."""
    if key is None:
        return d.get("drifter"), d.get("null")
    sub = d.get(key) or {}
    return sub.get("drifter"), sub.get("null")


def check_readout(b):
    """(2) per-qubit readout/SPAM profile match between the two blocks.

    TWO ACCEPTED SHAPES, and the second is why this function was rewritten (Ember C4253):

      single    readout.drifter[] / readout.null[]              — the originally locked
                                                                  interface, still valid
      bracketed readout.start.{drifter,null} + readout.end.{...} — cal at job start AND
                                                                  end (bus general#4726)

    WHY BRACKETED MATTERS, and why I built the consumer before asking for the producer:
    with one cal I can only ask whether the block match held from the census to the flight
    — a snapshot. With cal at both ends I can ask whether it held ACROSS the flight, which
    is the question this check was always morally about. So the PASS RULE under bracketing
    is the strict one: the match must hold at BOTH ends. Passing at the start and failing
    at the end is a match that decayed under the very window the arm ran in.

    SCOPE DISCIPLINE — the cal-vs-cal drift within each block is COMPUTED AND REPORTED
    HERE BUT NEVER GATED ON. My seat is leak channels: can the decoder separate the blocks
    on something other than coherence. Within-block drift across the window is a POWER and
    INTERPRETATION question — it is Elder's NULL-discharge input (general#4720), not mine.
    Gating on it would be me widening my own veto after pre-committing its bounds, which is
    the mirror image of the threshold-negotiation I pre-registered against. I hand him the
    number; he decides what it means.
    """
    d = b.get("readout", {})
    bracketed = isinstance(d.get("start"), dict) and isinstance(d.get("end"), dict)
    legs = [("start", "start"), ("end", "end")] if bracketed else [("cal", None)]

    states, detail = [], []
    if not bracketed:
        detail.append("SINGLE-CAL bundle: this tests whether the match held from census to")
        detail.append("flight (a snapshot). The bracketed shape tests the interval.")
    for label, key in legs:
        drift, null = _leg(d, key)
        if not drift or not null or len(drift) != len(null):
            where = f"readout.{key}." if key else "readout."
            return three_state(False, False, "2 readout/SPAM profile match",
                               [f"{where}drifter / {where}null missing or unequal length",
                                "A missing profile is NOT a pass — the check cannot run."])
        worst, mean, n = _pair_stats(drift, null)
        ok = worst <= READOUT_TOL and mean <= READOUT_MEAN_TOL
        states.append(ok)
        detail.append(f"[{label}] pairs {n}  worst |diff| {worst:.5f} (bar {READOUT_TOL})"
                      f"  mean {mean:.5f} (bar {READOUT_MEAN_TOL})  "
                      f"{'ok' if ok else 'OVER BAR'}")

    if bracketed:
        # DIAGNOSTIC ONLY — see the scope note above. This is the cal-vs-cal number Elder's
        # pre-registered NULL-discharge clause names, and without a bracketed bundle it does
        # not exist at all; that absence was the defect the ask closed.
        for blk in ("drifter", "null"):
            s = (d["start"] or {}).get(blk); e = (d["end"] or {}).get(blk)
            if s and e and len(s) == len(e):
                mv = [abs(float(x) - float(y)) for x, y in zip(s, e)]
                detail.append(f"[diagnostic, NOT gated] {blk} within-block cal drift "
                              f"start→end: worst {max(mv):.5f}, mean {sum(mv)/len(mv):.5f}")
        detail.append("within-block drift is Elder's NULL-discharge input, not my gate.")

    return three_state(all(states), True, "2 readout/SPAM profile match", detail)


def check_structure(b):
    """(3) compiled circuits structurally identical except the physical mapping."""
    s = b.get("structure", {})
    drift = s.get("drifter"); null = s.get("null")
    if not isinstance(drift, dict) or not isinstance(null, dict):
        return three_state(False, False, "3 structural identity",
                           ["structure.drifter / structure.null missing",
                            "Expected: depth, gate counts by name, barrier count."])
    # Physical qubit identity is EXPECTED to differ — that is the whole point of two
    # blocks. Everything else must match exactly.
    ignore = {"qubits", "physical_qubits", "layout", "initial_layout"}
    keys = (set(drift) | set(null)) - ignore
    mismatched = [k for k in sorted(keys) if drift.get(k) != null.get(k)]
    ok = not mismatched
    detail = [f"compared {len(keys)} structural fields (physical mapping excluded by design)"]
    for k in mismatched[:8]:
        detail.append(f"  MISMATCH {k}: drifter={drift.get(k)!r} null={null.get(k)!r}")
    if ok:
        detail.append("every field identical — the decoder cannot separate on circuit shape")
    return three_state(ok, True, "3 structural identity", detail)


def check_order(b):
    """(4) delivery order independent of the label."""
    order = b.get("trial_order")
    if not order or not isinstance(order, list):
        return three_state(False, False, "4 label-independent trial order",
                           ["trial_order missing — expected the delivered label sequence"])
    lab = [1 if x in (1, "1", True, "DRIFT", "drifter") else 0 for x in order]
    M = len(lab)
    if M < 8:
        return three_state(False, False, "4 label-independent trial order",
                           [f"only {M} trials — too few to test"])
    runs_same = sum(1 for i in range(M - 1) if lab[i] == lab[i + 1])
    mu = (M - 1) / 2.0
    sd = math.sqrt(M - 1) / 2.0
    z_runs = (runs_same - mu) / sd if sd else 0.0
    # A blocked delivery ("all DRIFT first") shows up as an extreme correlation between
    # position and label, which the adjacency statistic alone can miss for short blocks.
    half = M // 2
    first_rate = sum(lab[:half]) / half
    second_rate = sum(lab[half:]) / (M - half)
    p = sum(lab) / M
    se_halves = math.sqrt(2 * p * (1 - p) / half) if 0 < p < 1 else 0.0
    z_halves = (first_rate - second_rate) / se_halves if se_halves else 0.0
    ok = abs(z_runs) <= ORDER_Z and abs(z_halves) <= ORDER_Z
    return three_state(ok, True, "4 label-independent trial order",
                       [f"M={M}, label rate {p:.3f}",
                        f"adjacency runs z {z_runs:+.2f}   (bar |z| <= {ORDER_Z})",
                        f"first-vs-second-half z {z_halves:+.2f}   (bar |z| <= {ORDER_Z})"])


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    b = json.load(open(sys.argv[1]))
    print(f"ARM-N LEAK CHECKS 2-4  ·  bundle {sys.argv[1]}")
    print(f"thresholds declared blind before the bundle existed: "
          f"readout {READOUT_TOL}/{READOUT_MEAN_TOL}, order z {ORDER_Z}\n")
    states = [check_readout(b), check_structure(b), check_order(b)]
    print()
    if all(s == "PASS" for s in states):
        print("CLEAR — reqs 2-4 satisfied. Arm N's separation cannot come from readout")
        print("profile, circuit shape or delivery order. Posting this to the bus is the")
        print("CLEAR the flight waits on.")
        return 0
    print("NOT CLEAR — " + ", ".join(f"{n}:{s}" for n, s in zip("234", states)))
    print("A NOT-EVALUABLE blocks exactly as a FAIL does: an unrun check is not a passed")
    print("one, and the flight must not read silence as permission.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
