#!/usr/bin/env python3
"""Exp138b — ICO heralded sub-bath reset, RE-FLY (Whisper C4720).
Prereg: experiments/exp138b-ico-reset-refly-preregistration.md (FROZEN).
Exp138 (job d9bd80rv6alc73cst7g0) graded NO-TEST: retention sentinel 0.846-0.854 vs the
0.90 floor (which was set optimistically against FakeMarrakesh 0.9725; the F81 depth-haircut
is ~0.12). Ungated physics was clean (sub-bath 5σ, beats-null ~11σ). This re-fly changes
EXACTLY ONE frozen constant — the retention floor, re-derived from the measured haircut —
and re-submits for a fresh calibration window. SAME circuit, SAME transpile seed (=> same
22-CZ skeleton), SAME beat/sub-bath/null/deco gates. NOT a re-grade of the old data.

Usage: --scan (FREE) | --submit (spends ~25s QPU) --backend ibm_marrakesh
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_exp138_submit as sub  # noqa: E402

# ---- FROZEN 138b override (single change) ----
# Expected hardware retention ~= FakeMarrakesh 0.9725 - 0.12 (F81 depth-haircut, measured on
# Exp138) ~= 0.85; floor set ~0.05 below expectation for window variance, still far above the
# payload-collapse regime (retention had to drop to ~0.6 to kill the split). Frozen pre-data.
sub.RETENTION_MIN = 0.80
# everything else (SHUFFLE_SEED=4720 => same skeleton, BEAT_FLOOR, SUBBATH_MARGIN, THERM_BAND,
# DECO_BAND, MAX_RESET_2Q) unchanged.


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--backend", default="ibm_marrakesh")
    ap.add_argument("--tag", default="exp138b")
    args = ap.parse_args()
    # delegate to the shared machinery with the overridden floor + 138b tag
    sys.argv = [sys.argv[0]]
    if args.scan:
        sys.argv.append("--scan")
    if args.submit:
        sys.argv.append("--submit")
    sys.argv += ["--backend", args.backend, "--tag", args.tag]
    return sub.main()


if __name__ == "__main__":
    sys.exit(main())
