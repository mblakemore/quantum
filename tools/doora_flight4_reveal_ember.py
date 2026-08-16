#!/usr/bin/env python3
"""DOOR (a) FLIGHT-4 REVEAL — open the seal (Ember), ONLY after both decoders
committed decisions pre-unseal (Elder ea535661 gen#12292; Whisper gen#12294).

Integrity FIRST: recompute the commitment from the stored preimage using the
SEALER'S OWN FROZEN digest() (flight-3 grading 4e07a22 proved guessed orderings
all fail — the frozen code is the only valid derivation path). Refuse to write
the reveal unless digest(n, A_bits, labels, salt) == the published c31a1c86
commitment. Only then expose A + labels + salt for grading.

Label convention (flight-1/flight-3): '1' = ALT, '0' = NULL.
"""
import sys, os, json, importlib.util

SEALER = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "doora_sealer_ember_c4262.py")
SECRETS = os.path.expanduser("~/.ember-doora-secrets.json")
SEAL_KEY = "doora_deg2phase_v1:8"
N = 8
M = 80
COMMITMENT = "c31a1c861a840318c1baaa07bbb802d4f18876f3dd56b5c8c0a9016b73a6cdaa"
OUT = "results/doora_flight4_REVEAL_ember.json"


def load_sealer():
    s = importlib.util.spec_from_file_location("sealer", SEALER)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def main():
    sealer = load_sealer()
    # The sealer's calibration opener must pass before we trust its digest.
    if not sealer.selftest():
        sys.exit("REFUSE REVEAL: sealer selftest failed — cannot trust digest().")

    sec = json.load(open(SECRETS))[SEAL_KEY]
    a_bits, labels, salt = sec["A_bits"], sec["labels"], sec["salt"]

    # INTEGRITY GATE — recompute with the frozen preimage, compare to published.
    recomputed = sealer.digest(N, a_bits, labels, salt)
    if recomputed != COMMITMENT:
        sys.exit(f"REFUSE REVEAL: recomputed {recomputed[:16]} != committed "
                 f"{COMMITMENT[:16]} — the reveal does NOT match the seal.")
    if sec.get("sha256") != COMMITMENT:
        sys.exit("REFUSE REVEAL: stored sha256 disagrees with published commitment.")
    if len(labels) != M:
        sys.exit(f"REFUSE REVEAL: seal carries {len(labels)} labels, need {M}.")

    A = sealer.bits_to_A(a_bits, N)
    n_alt = labels.count("1")     # '1' = ALT
    n_null = labels.count("0")    # '0' = NULL

    reveal = {
        "spec": "doora_deg2phase_v1", "n": N, "M": M,
        "flight": "flight-4",
        "A_bits": a_bits, "A": A,
        "labels": labels, "salt": salt,
        "commitment_sha256": COMMITMENT,
        "verified_against": recomputed,
        "label_convention": "1=ALT, 0=NULL",
        "sealed_draw": {"ALT": n_alt, "NULL": n_null},
        "decoders_committed_pre_unseal": {
            "elder_decisions_sha256": "ea5356611d4d703b0b184f1c1d60b777e1678d872d59f6013b6f030f5c175bdf",
            "elder_blind_split": "38 ALT / 42 NULL",
            "whisper_blind_split": "38 ALT / 42 NULL"},
        "criterion": "76/80 (frozen, Elder gen#12276)"}

    os.makedirs("results", exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(reveal, f, indent=1)
    print(f"SEAL OPENED — reveal -> {OUT}")
    print(f"  integrity: recomputed digest == committed {COMMITMENT[:16]}  [PASS]")
    print(f"  truth draw: {n_alt} ALT / {n_null} NULL (balanced 40/40 as sealed)")
    print(f"  Elder/Whisper both blind-decoded 38 ALT / 42 NULL -> 2 off balance.")
    print(f"  Elder grades the 80 decisions against these labels at 76/80.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
