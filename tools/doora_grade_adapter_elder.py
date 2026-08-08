#!/usr/bin/env python3
"""DOOR (a) GRADE-INPUT ADAPTER — Elder C6593. Reshapes committed artifacts into the
exact field contract grade mode expects. NO decision logic lives here; every number is
copied from a hash-committed or frozen file. The grader itself is UNTOUCHED.

Three mechanical reshapes, each documented:
 1. grade-flight: decisions.json trials → [{"decisions": {...}}] wrappers (grade mode's
    shape), plus window_id. C1 = [] (C1 left hardware; empty arm → grade emits the
    pre-registered UNGRADEABLE/descriptive branch, which IS the single-rung report).
 2. grade-prereg view: pilot view + per-rung Q_grid=[154] (copies units — decisions are
    keyed by copies, 2 x 77 pairs), C1_grid=[], and top-level "alpha": 0.05 — the
    REPORTING alpha, = 1 - reporting_ci_level, carried under the banned-term mapping the
    two-alphas rule (#6320) defines: epsilon_trial sizes shots; reporting CIs are 95%.
 3. labels adapter (at unseal): maps Ember's published labels to "ALT"/"NULL" strings in
    sealed trial order. Refuses if count != 40 or values unmappable.
"""
import json, os, sys

REPO = "/droid/repos/quantum"
DEC = os.path.join(REPO, "results/doora_decisions_n8_elder_c6593.json")
PILOT = os.path.join(REPO, "experiments/doora_prereg_c6593_pilot_n8.json")
GF = os.path.join(REPO, "results/doora_gradeflight_n8_elder_c6593.json")
GP = os.path.join(REPO, "experiments/doora_prereg_c6593_pilot_n8_grade.json")

def build_views():
    dec = json.load(open(DEC))
    r8 = dec["rungs"]["8"]
    gf = {"8": {"window_id": r8["window_id"],
                "Q": [{"decisions": t} for t in r8["Q"]],
                "C1": []},
          "_provenance": "mechanical reshape of hash-committed decisions "
                         "(sha256 0ca59ad2..., quantum@30c6f02); no values altered"}
    json.dump(gf, open(GF, "w"), indent=1)

    p = json.load(open(PILOT))
    p["alpha"] = 0.05
    p["alpha_note"] = ("REPORTING alpha = 1 - reporting_ci_level per two-alphas rule "
                      "(#6320); grade mode's required key, mapped mechanically — "
                      "epsilon_trial (0.01) sized shots and is untouched")
    rung = p["rungs"][0]
    rung["Q_grid"] = [154]
    rung["C1_grid"] = []
    json.dump(p, open(GP, "w"), indent=1)
    print(f"wrote {GF}\nwrote {GP}")

def labels_file(raw_labels_path, out_path):
    """Map Ember's unsealed labels to grade-mode shape: {'8': ['ALT'|'NULL' x 40]}."""
    raw = json.load(open(raw_labels_path))
    lab = raw if isinstance(raw, list) else raw.get("labels") or raw.get("8")
    if lab is None or len(lab) != 40:
        sys.exit(f"REFUSE: expected 40 labels, got {None if lab is None else len(lab)}")
    m = {1: "ALT", 0: "NULL", "1": "ALT", "0": "NULL", "ALT": "ALT", "NULL": "NULL"}
    try:
        mapped = [m[x] for x in lab]
    except KeyError as e:
        sys.exit(f"REFUSE: unmappable label {e} — confirm Ember's convention explicitly")
    json.dump({"8": mapped}, open(out_path, "w"), indent=1)
    print(f"wrote {out_path}  (ALT={mapped.count('ALT')}, NULL={mapped.count('NULL')})")

if __name__ == "__main__":
    if len(sys.argv) == 3:
        labels_file(sys.argv[1], sys.argv[2])
    else:
        build_views()
