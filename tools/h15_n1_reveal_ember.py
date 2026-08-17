#!/usr/bin/env python3
"""H15 N1 REVEAL — open the multi-instance seal (Ember), ONLY after both
decoders commit decisions pre-unseal. Integrity FIRST: recompute the commitment
from the stored secret via the SEALER's frozen digest (never a guessed
preimage); refuse unless it == the published b96ee93b. Then emit the truth in
Elder's requested per-row schema (graded flight-position, label, A-or-xu) so
binder-vs-reveal consistency is checkable post-flight.

Label convention: '1'=ALT (correct actuator response 1), '0'=NULL (correct 0).
"""
import sys, os, json, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
SEALER_PATH = os.path.join(HERE, "h15_positronic_sealer_ember.py")
KIT_PATH = os.path.join(os.path.dirname(HERE), "experiments",
                        "h15_n2_public_kit_whisper_c5074.py")
SECRETS = os.path.expanduser("~/.ember-doora-secrets.json")
STORE_KEY = "h15_positronic_v1:4"
COMMITMENT = "b96ee93b29983352a543c25969fee3bba720e45cc2ee06e252449529cb2914f1"
OUT = "results/h15_n1_REVEAL_ember.json"

# Filled from Elder/Whisper pre-unseal posts at open time:
ELDER_DECISIONS_SHA256 = "PENDING"
ELDER_ACC = "PENDING"
WHISPER_ACC = "PENDING"


def load(path, name):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    try:
        s.loader.exec_module(m)
    except SystemExit:
        pass
    return m


def main():
    sealer = load(SEALER_PATH, "h15sealer")
    kit = load(KIT_PATH, "kit")
    if not sealer.selftest():
        sys.exit("REFUSE REVEAL: sealer selftest failed.")

    sec = json.load(open(SECRETS))[STORE_KEY]
    labels, A_list, xu_list, salt = sec["labels"], sec["A_list"], sec["xu_list"], sec["salt"]
    recomputed = sealer.digest(labels, A_list, xu_list, salt)
    if recomputed != COMMITMENT or sec.get("sha256") != COMMITMENT:
        sys.exit(f"REFUSE REVEAL: recomputed {recomputed[:16]} != committed {COMMITMENT[:16]}.")

    # graded flight-positions = all positions minus the public cal positions, in order
    cpos = set(kit.cal_positions())
    graded_positions = [p for p in range(kit.TOTAL) if p not in cpos]
    if len(graded_positions) != kit.M:
        sys.exit(f"REFUSE: {len(graded_positions)} graded positions != {kit.M}.")

    per_row, ka, kn = [], 0, 0
    for gi, ch in enumerate(labels):
        row = {"graded_index": gi, "flight_position": graded_positions[gi],
               "label": "ALT" if ch == "1" else "NULL",
               "correct_act": 1 if ch == "1" else 0}
        if ch == "1":
            row["A"] = A_list[ka]; ka += 1
        else:
            row["xu"] = list(xu_list[kn]); kn += 1
        per_row.append(row)

    n_alt = labels.count("1")
    reveal = {"spec": "h15_positronic_v1", "n": kit.N, "M": kit.M, "flight": "N1",
              "commitment_sha256": COMMITMENT, "verified_against": recomputed,
              "label_convention": "1=ALT(correct act 1), 0=NULL(correct act 0)",
              "sealed_draw": {"ALT": n_alt, "NULL": kit.M - n_alt},
              "salt": salt, "per_row": per_row,
              "decoders_committed_pre_unseal": {
                  "elder_decisions_sha256": ELDER_DECISIONS_SHA256,
                  "elder_accuracy": ELDER_ACC, "whisper_accuracy": WHISPER_ACC},
              "criterion": "0.6040 = 143/256 + 2.3*sqrt(p_C(1-p_C)/632) (frozen)"}
    os.makedirs("results", exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(reveal, f, indent=1)
    print(f"SEAL OPENED — reveal -> {OUT}")
    print(f"  integrity: recomputed digest == committed {COMMITMENT[:16]}  [PASS]")
    print(f"  truth draw: {n_alt} ALT / {kit.M - n_alt} NULL (balanced as sealed)")
    print(f"  per-row schema: (graded_index, flight_position, label, A-or-xu) x {kit.M}")
    print(f"  Elder grades c_act vs correct_act at frozen 0.6040.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
