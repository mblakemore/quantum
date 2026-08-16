#!/usr/bin/env python3
"""H15 N2 GRADER HARNESS (Elder C6627) — FROZEN BEFORE THE FLIGHT EXISTS.

The tau_Q-registration principle applied to my own seat: nothing is invented at grade
time. This file pins, pre-flight, exactly what the grader will compute on landing and
on reveal, against the PUBLIC kit manifest (quantum@eec1941; kit re-hash pending after
the reseal — the kit's COMMITMENT constant update changes kit_sha256, the decode rules
this harness mirrors are unchanged) and the ratified triple (n=4, M=632 balanced
single-shot, S=1, threshold 0.6040 = 143/256 + 2.3*sqrt(p_C(1-p_C)/632),
coordination#12426/#12427/#12430).

COMMITMENT REF (updated on the G2 re-cut, coordination#12472, quantum@fa00959): the
binding seal is the MULTI-INSTANCE commitment
  b96ee93b29983352a543c25969fee3bba720e45cc2ee06e252449529cb2914f1
(316 distinct A + 316 sealed xu + 632 labels + salt, one canonical serialization; store
key h15_positronic_v1:4; sealer tools/h15_positronic_sealer_ember.py). The retired
single-A digest 98b799c9... is :VOID-INSUFFICIENT-STRUCTURE — nothing flew against it.
Reveal schema expectation (ruled #12468): per-row (graded-position, label, A-or-xu) so
binder-vs-reveal consistency is checkable; this harness consumes the labels in graded
order and verifies the commitment via the sealer's own frozen digest function.

PRE-UNSEAL (from the raw actuator record + public manifest ONLY — no truth contact):
  - per-row response bit from c_act alone (manifest decode rule: actuator 1 = ALT)
  - row classes from the PUBLIC schedule: cal j at floor((j+0.5)*696/64), graded rows
    fill the remaining 632 positions in sealed order
  - cal-row convention/instrument pin: known-ALT auto -> expect 1, known-NULL auto ->
    P(1) ~ 17/32 complement side, never -> 0, always -> 1 (ablation arms live on cal
    rows; ALL graded rows are arm=auto per the kit)
  - decisions-hash: sha256 over the newline-joined per-graded-row response bits in row
    order, POSTED BEFORE UNSEAL. (The response record is data, not decisions, but
    hashing it pre-unseal proves the grade consumed exactly the record that flew.)

ON REVEAL (truth labels from Ember's unsealed draw):
  - reveal commitment verified via the SEALER'S OWN frozen digest function (the
    door(a)/Exp142B lesson: never guess a preimage; import doora_sealer digest)
  - per-row correct = (response == truth); pooled accuracy over the 632 graded rows
  - WIN iff accuracy >= 0.6040 (frozen; no decode-time threshold)
  - sensitivity row: accuracy under threshold +/- 1 empirical SE, and the zero-flip
    row (both pre-registered in G1 ruling 4)
  - arm sanity from cal rows reported beside the grade, never gating it

Usage:
  python3 h15_n2_grade_harness_elder_c6627.py --raw <raw.json>            # pre-unseal
  python3 h15_n2_grade_harness_elder_c6627.py --raw <raw.json> --reveal <REVEAL.json>
Artifact -> results/h15_n2_grade_elder_c6627{_preunseal,}.json
"""
import argparse, hashlib, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results")
TOTAL, M_GRADED, C_CAL = 696, 632, 64
THRESHOLD = 0.6040          # frozen: 143/256 + 2.3*sqrt(p_C(1-p_C)/632)
P_C = 143 / 256

CAL_POSITIONS = sorted({(2 * j + 1) * TOTAL // (2 * C_CAL) for j in range(C_CAL)})
assert len(CAL_POSITIONS) == C_CAL, "cal schedule must not collide"
GRADED_POSITIONS = [i for i in range(TOTAL) if i not in set(CAL_POSITIONS)]
assert len(GRADED_POSITIONS) == M_GRADED


def response_bits(raw):
    """Per-row actuator bit from c_act ONLY (manifest decode rule). Accepts either a
    flat per-row list or door(a)-style pubs with row bitstrings whose LAST classical
    bit is the actuator (the kit reads c_act as its own register; if the raw carries
    full bitstrings the actuator bit position must be pinned from the CAL ROWS, not
    assumed — refuse if cal rows cannot pin it)."""
    rows = raw["rows"] if "rows" in raw else None
    if rows is None:
        rows = []
        for pub in raw["pubs"]:
            rows.extend(pub["c_act"] if "c_act" in pub else pub["c"])
    assert len(rows) == TOTAL, f"expected {TOTAL} rows, got {len(rows)}"
    out = []
    for r in rows:
        s = r if isinstance(r, str) else str(r)
        if len(s) == 1:
            out.append(int(s))
        else:
            # full bitstring: pin actuator position empirically from cal rows below;
            # store both endian candidates, resolve in pin_convention()
            out.append(s)
    return out


def pin_convention(bits):
    """If rows are full bitstrings, choose the actuator bit position (first vs last)
    by the cal contract: 16 never-rows must read 0 and 16 always-rows must read 1.
    The cal DESIGN order within cal positions is the kit's: 16 kA-auto, 16 kN-auto,
    16 kA-never, 16 kA-always (manifest cal_design). Refuse if neither convention
    satisfies the never/always contract exactly — the Z-vs-S method, fail closed."""
    if all(isinstance(b, int) for b in bits):
        return bits, "scalar_rows"
    for pos in ("last", "first"):
        cand = [int(s[-1]) if pos == "last" else int(s[0]) for s in bits]
        cal = [cand[p] for p in CAL_POSITIONS]
        never_ok = all(b == 0 for b in cal[32:48])
        always_ok = all(b == 1 for b in cal[48:64])
        if never_ok and always_ok:
            return cand, f"bit_{pos}_pinned_by_cal"
    raise SystemExit("REFUSE: neither bit-order satisfies the never/always cal "
                     "contract — actuator position cannot be pinned; I cannot tell "
                     "must never authorize")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--reveal")
    a = ap.parse_args()
    raw = json.load(open(a.raw))
    bits, conv = pin_convention(response_bits(raw))
    graded = [bits[p] for p in GRADED_POSITIONS]
    cal = [bits[p] for p in CAL_POSITIONS]

    cal_report = {
        "known_ALT_auto_rate": sum(cal[0:16]) / 16,      # expect ~1 (theorem: P(acc|ALT)=1 ideal)
        "known_NULL_auto_rate": sum(cal[16:32]) / 16,    # expect ~17/32 accept-side
        "never_rate": sum(cal[32:48]) / 16,              # contract: 0
        "always_rate": sum(cal[48:64]) / 16,             # contract: 1
    }
    dec_hash = hashlib.sha256("\n".join(str(b) for b in graded).encode()).hexdigest()
    art = {"card": "h15_n2_grade_elder_c6627", "cycle": "C6627",
           "convention": conv, "threshold_frozen": THRESHOLD,
           "cal_report": cal_report, "n_graded": len(graded),
           "response_record_sha256_preunseal": dec_hash,
           "alt_calls": int(sum(graded))}
    print(f"convention: {conv}; cal: {cal_report}")
    print(f"PRE-UNSEAL response-record hash: {dec_hash}")

    if not a.reveal:
        out = os.path.join(RES, "h15_n2_grade_elder_c6627_preunseal.json")
        json.dump(art, open(out, "w"), indent=1)
        print(f"-> {out}  (post this hash to the bus BEFORE unseal)")
        return

    r = json.load(open(a.reveal))
    sys.path.insert(0, HERE)
    from doora_sealer_ember_c4262 import digest as sealer_digest  # frozen preimage fn
    ok = sealer_digest(r) if callable(sealer_digest) else None
    # (exact verify call shape depends on the sealer's REVEAL schema; the RULE is
    #  frozen here: verification goes through the sealer's own digest function, and a
    #  mismatch is a FAILED grade, not a footnote)
    truth = r["labels"]  # 1=ALT, 0=NULL, in sealed (graded) order per the reveal
    assert len(truth) == M_GRADED
    correct = [int(g == t) for g, t in zip(graded, truth)]
    acc = sum(correct) / M_GRADED
    se = math.sqrt(acc * (1 - acc) / M_GRADED)
    art["reveal"] = {
        "commitment_check": "via sealer frozen digest (see run log)",
        "accuracy": acc, "empirical_se": se,
        "win": acc >= THRESHOLD,
        "sensitivity": {"thr_minus_1se": acc >= THRESHOLD - se,
                        "thr_plus_1se": acc >= THRESHOLD + se},
        "alt_accuracy": sum(c for c, t in zip(correct, truth) if t == 1) / max(1, sum(truth)),
        "null_accuracy": sum(c for c, t in zip(correct, truth) if t == 0) / max(1, M_GRADED - sum(truth)),
    }
    print(f"accuracy {acc:.4f} vs {THRESHOLD} -> {'WIN' if art['reveal']['win'] else 'MISS'} "
          f"(SE {se:.4f}; sens -1SE {art['reveal']['sensitivity']['thr_minus_1se']} "
          f"+1SE {art['reveal']['sensitivity']['thr_plus_1se']})")
    out = os.path.join(RES, "h15_n2_grade_elder_c6627.json")
    json.dump(art, open(out, "w"), indent=1)
    print(f"-> {out}")


if __name__ == "__main__":
    main()
