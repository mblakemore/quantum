#!/usr/bin/env python3
"""Exp144 SUBMIT SEAM check — my sealed instance -> Elder's builders (Ember).

The kit ships build+selftest and states "submit modes are EMBER's (sealed-committer)",
so the submit driver is mine and THIS is the seam between us.

Exp142's wave-1 void lived at exactly this seam — but there it was a FILE SCHEMA (the
frozen kit read ~/.ember-exp142-secrets.json nested; my sealer wrote it flat; hashes all
valid, flight invalid). Exp144 eliminates that bug class BY CONSTRUCTION: the kit parses
no secrets file at all (verified — no open()/expanduser of any secret path), and takes
terms/coeffs as function ARGUMENTS. The implicit cross-author file schema became an
explicit function signature. What remains checkable is whether MY output shape matches
HIS parameters, plus that the manifests the decoders receive stay P-independent.

METHOD NOTE, kept deliberately: v1 of this check FAILED 6/6 and the fault was ENTIRELY
mine — I invented build_quantum_job(n, k, terms, coeffs) when there is no k (the quantum
manifest is instance-independent by design), and unpacked 2 values from build_conv_job,
which returns 3. Had I reported that as an interface bug it would have been a false alarm
at another DC's expense. Read the consumer; never assume it. (c4185_001 — committed while
testing for c4185_001.)

  python3 exp144_submit_seam_ember.py
"""
import importlib.util
import os
import random
import secrets as pysec
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name, fn):
    s = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


K = _load("kit", "exp144_flight_kit.py")
G = _load("gen", "exp144_instance_gen_ember.py")

FAILS = 0


def check(label, cond, detail=""):
    global FAILS
    if not cond:
        FAILS += 1
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}{(' — ' + detail) if detail else ''}")


def main():
    rng = random.Random(4194)
    for n in (4, 6, 8):
        terms, coeffs = G.sample_instance(n, rng)
        seed = pysec.randbits(64)

        pubs, man = K.build_quantum_job(n, terms, coeffs)
        check(f"n={n} build_quantum_job(n, terms, coeffs)", len(pubs) > 0, f"{len(pubs)} pubs")

        pubs2, man2, meta = K.build_conv_job(n, 1, terms, coeffs, wave=1, seed=seed)
        check(f"n={n} build_conv_job(..., seed=my sealed seed)", len(pubs2) > 0,
              f"{len(pubs2)} pubs, {len(meta)} row_meta")

        # The manifests go to the DECODERS. Blindness is a property of these objects.
        leaked = [t for t in terms if t in str(man)]
        check(f"n={n} quantum manifest P-INDEPENDENT", not leaked,
              f"LEAKED {leaked}" if leaked else "layout+shots only")

        # The conv manifest legitimately enumerates candidates (the truth is among 3^n).
        # The failure mode is LABELLING which candidate is planted.
        flags = [w for w in ("planted", "truth", "answer", "secret")
                 if w in str(man2).lower()]
        check(f"n={n} conv manifest does not FLAG the planted terms", not flags,
              f"contains {flags}" if flags else "candidates unlabelled")

    print(f"\nSUBMIT SEAM: {'PASS' if FAILS == 0 else f'FAIL ({FAILS})'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
