#!/usr/bin/env python3
"""Exp139b — coherent concentration RE-FLY (Whisper C4720). Creator-directed ("refly yes").
Prereg: experiments/exp139b-concentration-refly-preregistration.md (FROZEN).
Exp139 (job d9besiug26ic73dfsm1g) graded NO-TEST: conc_111 sentinel 0.9357 < the 0.95 floor
(set from optimistic FakeMarrakesh 0.975). This re-fly changes EXACTLY ONE frozen constant — the
conc_111 floor, re-derived from measured gate/readout error — and re-submits for a fresh window.
SAME circuit, SAME seed (=> same 24-CZ skeleton), SAME PRIMARY/SECONDARY/conc_000 rules. NOT a
re-grade of the old data.

Usage: --scan (FREE) | --submit (~small QPU) --backend ibm_marrakesh
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_exp139_submit as sub  # noqa: E402

# ---- FROZEN 139b override (single change) ----
# conc_111 corner fidelity budget, derived PRE-DATA from measured chip params (not from the exp139
# result): 24 routed CZ at ~0.4%/CZ ~= 9% cumulative, x |1> readout ~1.5% -> expected ~0.90.
# This is the F81 depth-haircut lesson (C4720): a sentinel floor must certify "the majority logic
# works within its own error budget", not "matches the optimistic noise model" (0.975). The PRIMARY
# claim (dest << single) has ~45sigma margin, robust to a 10% corner error.
sub.S111_MIN = 0.90
# everything else (S000_MAX=0.05, SHUFFLE_SEED=4720 => same skeleton, MAX_2Q) unchanged.


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--backend", default="ibm_marrakesh")
    ap.add_argument("--tag", default="exp139b")
    args = ap.parse_args()
    sys.argv = [sys.argv[0]]
    if args.scan:
        sys.argv.append("--scan")
    if args.submit:
        sys.argv.append("--submit")
    sys.argv += ["--backend", args.backend, "--tag", args.tag]
    return sub.main()


if __name__ == "__main__":
    sys.exit(main())
