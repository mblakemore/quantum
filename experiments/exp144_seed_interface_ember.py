#!/usr/bin/env python3
"""Exp144 seed interface check: MY sealed seed -> ELDER'S conv_candidates(n, seed).

A live producer/consumer interface across two authors — precisely the class that voided
Exp142 wave-1 (my sealer wrote secrets flat, the frozen kit read them nested). Type
compatibility is the boring half and is checked here, but the LOAD-BEARING property is
that the seed actually CONTROLS the candidate order:

    if different seeds produced the same order, the per-rung seed commitment would be
    ceremony, F2(b) would still be open, and every downstream hash would certify nothing.

That is the same reasoning as every other gate tonight — the check must be able to FAIL.

  python3 exp144_seed_interface_ember.py
"""
import importlib.util
import os
import secrets
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name, fn):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


K = _load("kit", "exp144_flight_kit.py")
S = _load("sealer", "exp144_seal_reveal_ember.py")

FAILS = 0


def check(label, cond, detail=""):
    global FAILS
    if not cond:
        FAILS += 1
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}{(' — ' + detail) if detail else ''}")


def gen_seed():
    """The shape I will actually seal: 64-bit from a CSPRNG."""
    return secrets.randbits(64)


def main():
    print("=== [1] type/round-trip: my sealed seed through his consumer ===")
    for n in (4, 6, 8):
        s = gen_seed()
        body = S.convseed_preimage_str(n, s)
        check(f"n={n} my preimage accepts a real 64-bit seed",
              body == f"exp144|convseed|{n}|{s}", body[:58])
        order = K.conv_candidates(n, s)
        check(f"n={n} his conv_candidates accepts my seed",
              order is not None and len(order) > 0, f"{len(order)} candidates")

    print("\n=== [2] the property that makes the commitment MEAN something ===")
    for n in (4, 6):
        s1, s2 = gen_seed(), gen_seed()
        a1 = list(K.conv_candidates(n, s1))
        a1b = list(K.conv_candidates(n, s1))
        a2 = list(K.conv_candidates(n, s2))
        check(f"n={n} DETERMINISTIC: same seed -> same order", a1 == a1b)
        check(f"n={n} seed CONTROLS order: different seed -> different order", a1 != a2,
              "" if a1 != a2 else "IDENTICAL for different seeds => seed decorative, F2(b) OPEN")
        check(f"n={n} candidate SET invariant (only the order is seeded)",
              sorted(map(str, a1)) == sorted(map(str, a2)))

    print(f"\nSEED INTERFACE: {'PASS' if FAILS == 0 else f'FAIL ({FAILS})'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
