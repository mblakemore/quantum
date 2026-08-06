#!/usr/bin/env python3
"""P-CCM v1.0 — calibrate C, the per-stabilizer-term runtime on THIS hardware.

THE POINT. Every absolute classical bill in the HSS campaign is extrapolated from the paper's
2016 i5 MATLAB anchor times a x1000 hardware guess whose plausible range spans 160x-4800x —
23 T-gates of certifiable ceiling (measured C5020). That guess exists only because no one had
timed the algorithm's own inner loop on our machine.

THE MEASUREMENT IS APPLES-TO-APPLES AGAINST A PUBLISHED TABLE. Bravyi & Gosset Table I reports
average InnerProduct runtime in ms at n = 10/25/50/75/100 for THEIR MATLAB implementation on a
2.6 GHz i5 Dual Core, for inner products <x~|phi> where phi is a generic stabilizer state and
|x~> = tensor of |0> and H|0>. We replicate that exact setup and time the same quantity.

    ratio = (paper MATLAB on 2016 i5)  /  (this kernel on RACE_CONFIG)

is then a MEASURED implementation+hardware factor on the SAME ALGORITHM — replacing the
x1000 guess with a number, on the axis that dominated the uncertainty.

⚠️ DIRECTION OF ERROR, STATED BECAUSE IT IS THE FLATTERING ONE. This kernel is a NUMPY
REFERENCE implementation, not optimised C. A slower classical solver makes the classical bill
look LARGER, which makes our quantum advantage look BIGGER. So:

    C measured here is an UPPER BOUND on the per-term cost of a best-available solver,
    therefore the classical bill computed from it is an UPPER BOUND,
    therefore any advantage ratio computed from it is an UPPER BOUND ON OUR ADVANTAGE.

An advantage claim must be graded on the classical side's BEST implementation, so this
calibration bounds the classical cost from above and must be reported as such — never as the
classical cost itself. What it DOES settle without that caveat is the SHAPE (does the measured
runtime follow the paper's O(n^3)?), which is implementation-independent.

Substrate: claude-fable-5, Whisper C5020.
"""
import time, json, sys, os
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stabilizer_rank_kernel import (StabState, inner_product, random_state_via_extend,  # noqa: E402
                                    self_test, _inv_gf2)

# Bravyi & Gosset, Table I — MATLAB, 2.6 GHz Intel i5 Dual Core, milliseconds
PAPER_TABLE_I = {
    "MeasurePauli":          {10: 0.27, 25: 0.3, 50: 0.4,  75: 0.5,  100: 0.6},
    "RandomStabilizerState": {10: 0.2,  25: 0.3, 50: 0.8,  75: 1.7,  100: 2.8},
    "InnerProduct":          {10: 0.5,  25: 1.5, 50: 3.5,  75: 6.5,  100: 8.9},
    "ExponentialSum":        {10: 0.3,  25: 0.8, 50: 2.2,  75: 4.4,  100: 8.0},
}
PAPER_CPU = "2.6 GHz Intel i5 Dual Core (2016), MATLAB"


def x_tilde_state(n, xbits):
    """|x~> = tensor_j |x~_j| with |0~>=|0>, |1~>=H|0>.  A stabilizer state with
    k = weight(x): the free coordinates are exactly the positions where x_j = 1."""
    ones = [j for j in range(n) if xbits[j]]
    k = len(ones)
    G = np.zeros((n, n), dtype=np.uint8)
    for a, j in enumerate(ones):
        G[a, j] = 1
    rest = [j for j in range(n) if not xbits[j]]
    for a, j in enumerate(rest):
        G[k + a, j] = 1
    Gi = _inv_gf2(G)
    assert Gi is not None
    return StabState(n, k, np.zeros(n, dtype=np.uint8), G, Gi.T % 2, 0,
                     np.zeros(n, dtype=np.int64), np.zeros((n, n), dtype=np.int64))


def time_inner_product(n, reps, rng):
    """Replicate the paper's Table I setup for InnerProduct: <x~|phi>."""
    pairs = []
    for _ in range(reps):
        phi = random_state_via_extend(n, n, rng)     # generic state, k ~ n (Appendix D)
        x = rng.integers(0, 2, size=n)
        pairs.append((x_tilde_state(n, x), phi))
    t0 = time.perf_counter()
    for xs, phi in pairs:
        inner_product(phi, xs)
    return (time.perf_counter() - t0) / reps * 1000.0   # ms per call


def main():
    print("CALIBRATING C — per-stabilizer-term runtime on this hardware\n")

    print("① CORRECTNESS GATE (a timing whose paired verification did not pass is not emitted)")
    p, f, fails = self_test(verbose=False)
    print(f"    {p} passed, {f} failed")
    if f:
        print("    ⛔ GATE NOT PASSED — refusing to emit timings.")
        for x in fails[:6]:
            print(f"      {x}")
        sys.exit(2)
    print("    ✅ gate passed\n")

    rng = np.random.default_rng(20260806)
    NS = [10, 25, 50, 75, 100]
    REPS = {10: 200, 25: 80, 50: 30, 75: 15, 100: 8}

    print("② InnerProduct timing — the paper's Table I setup, replicated")
    print(f"    {'n':>5} {'ours (ms)':>12} {'paper MATLAB (ms)':>19} {'ratio paper/ours':>18}")
    rows = {}
    for n in NS:
        ms = time_inner_product(n, REPS[n], rng)
        pm = PAPER_TABLE_I["InnerProduct"][n]
        rows[n] = {"ours_ms": ms, "paper_ms": pm, "ratio": pm / ms}
        print(f"    {n:>5} {ms:>12.3f} {pm:>19.2f} {pm/ms:>18.3f}")

    print("\n③ SHAPE CHECK — implementation-independent, and the part that needs no caveat")
    ns = np.array(NS, dtype=float)
    ours = np.array([rows[n]["ours_ms"] for n in NS])
    sl_o = np.polyfit(np.log(ns), np.log(ours), 1)[0]
    paper = np.array([PAPER_TABLE_I["InnerProduct"][n] for n in NS])
    sl_p = np.polyfit(np.log(ns), np.log(paper), 1)[0]
    print(f"    log-log slope, ours   {sl_o:+.2f}   (paper's model says O(n^3) asymptotically)")
    print(f"    log-log slope, paper  {sl_p:+.2f}")
    print("    NB both are far below 3 because BOTH are overhead-dominated at these n —")
    print("       the paper's own table grows 17.8x from n=10 to n=100 where n^3 predicts 1000x.")

    # per-unit constants, fitted on the top two points to strip the fixed per-call overhead
    def per_unit(v):
        return (v[-1] - v[-2]) / (ns[-1] ** 3 - ns[-2] ** 3) * 1e6     # ns per n^3 unit
    pu_o, pu_p = per_unit(ours), per_unit(paper)
    print(f"\n    ns per O(n^3) unit, fitted on the top two points:")
    print(f"      ours   {pu_o:>10.2f} ns")
    print(f"      paper  {pu_p:>10.2f} ns")
    print(f"      ratio  {pu_o/pu_p:>10.2f}x   (>1 means OUR reference kernel is SLOWER per unit)")

    out = {
        "card": "stabilizer_term_calibration", "version": "1.0", "cycle": "C5020",
        "substrate": "claude-fable-5",
        "paper_reference": {"cpu": PAPER_CPU, "table": PAPER_TABLE_I["InnerProduct"]},
        "measured_inner_product_ms": {str(k): v for k, v in rows.items()},
        "shape": {"loglog_slope_ours": sl_o, "loglog_slope_paper": sl_p,
                  "note": "both overhead-dominated at tabulated n; per-unit constants fitted on top two points"},
        "per_n3_unit_ns": {"ours": pu_o, "paper": pu_p, "ratio_ours_over_paper": pu_o / pu_p},
        "DIRECTION_OF_ERROR": ("numpy REFERENCE kernel, not optimised C. A slower classical solver "
                               "inflates the classical bill and therefore INFLATES our advantage. "
                               "C measured here is an UPPER BOUND on a best-available solver's per-term "
                               "cost; any advantage computed from it is an UPPER BOUND on our advantage."),
        "what_this_does_not_settle": ("the per-term constant for a BEST-AVAILABLE classical solver. "
                                      "It settles the SHAPE and provides a measured, defensible upper "
                                      "bound replacing the x1000 hardware guess on OUR side of the ratio."),
    }
    dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results",
                       "stabilizer_term_calibration_v1.json")
    with open(dst, "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"\n  written: results/{os.path.basename(dst)}")


if __name__ == "__main__":
    main()
