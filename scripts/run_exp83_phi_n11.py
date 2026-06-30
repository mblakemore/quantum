#!/usr/bin/env python3
"""
exp83_phi_n11.py — Whisper C4415

Compute classical IIT Phi (PyPhi) for N=11 XOR ring, extending the F52 growth-law
series and tightening the odd-series exponent fit (b_odd) from 2 points (N=7,9) to 3
(N=7,9,11). Pre-registration: experiments/exp83-classical-phi-n11-preregistration.md

Identical protocol to exp76_classical_phi_growth_law.py (Whisper C4412): same XOR ring
topology, same all-ones probe state, same PyPhi config. Classical sim, zero QPU.

Usage:
  python3 run_exp83_phi_n11.py
"""
import numpy as np
import json
import time
import os
import sys

os.environ["PYPHI_WELCOME_OFF"] = "yes"
import pyphi

pyphi.config.PROGRESS_BARS = False
pyphi.config.PARALLEL_CONCEPT_EVALUATION = False

N = 11
RESULTS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "experiments", "exp83_results.json")

KNOWN_SERIES = {3: 1.875, 4: 0.0, 5: 15.15625, 6: 1.875, 7: 49.609375,
                8: 7.5, 9: 115.619, 10: 18.21875}


def build_xor_ring_tpm(n):
    n_states = 2 ** n
    tpm = np.zeros((n_states, n), dtype=float)
    for state_idx in range(n_states):
        state = [(state_idx >> i) & 1 for i in range(n)]
        next_state = [state[(k - 1) % n] ^ state[(k + 1) % n] for k in range(n)]
        next_idx = sum(next_state[i] << i for i in range(n))
        tpm[state_idx, :] = next_state
    return tpm


def build_xor_ring_cm(n):
    cm = np.zeros((n, n), dtype=int)
    for k in range(n):
        cm[k, (k - 1) % n] = 1
        cm[k, (k + 1) % n] = 1
    return cm


def compute_phi_for_state(n, state):
    tpm = build_xor_ring_tpm(n)
    cm = build_xor_ring_cm(n)
    network = pyphi.Network(tpm, cm=cm)
    node_indices = tuple(range(n))
    subsystem = pyphi.Subsystem(network, state, node_indices)
    sia = pyphi.compute.phi(subsystem)
    return sia.phi


def find_image(N):
    """Set of all reachable state-indices (one XOR step from SOME state)."""
    tpm = build_xor_ring_tpm(N)
    image = set()
    for state_idx in range(2 ** N):
        bits = tpm[state_idx]
        idx = sum(int(bits[i]) << i for i in range(N))
        image.add(idx)
    return image


def main():
    print(f"Exp83: Classical XOR Ring Phi, N={N}")
    print(f"PyPhi version: {pyphi.__version__}")
    print(f"Start: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}", flush=True)

    all_ones_idx = (1 << N) - 1
    image = find_image(N)
    state_label = "all_ones"
    if all_ones_idx not in image:
        # DISCOVERED C4415: all-ones has NO pre-image under the XOR-ring map for N=11
        # (verified directly against pyphi's own state_reachable validator, which raises
        # StateUnreachableError -- confirmed empirically, not just by this set-membership
        # check). Re-deriving reachability for N=3..12 shows all-ones is reachable ONLY for
        # N==0 (mod 4) -- i.e. N=4,8,12, NOT the rest of the established series (N=3,5,6,7,
        #9,10,11). This means either the historical N=3..10 series (Ember C4022/C4023,
        # cited in F52) used a DIFFERENT actual state mislabeled as "all_ones" in summary
        # tables, or a PyPhi/dependency version difference is changing reachability behavior
        # across cycles (same meta-pattern as the C4414 COBYLA/scipy drift finding) -- open
        # question, flagged for cross-DC follow-up, NOT resolved here.
        # For N=11 specifically: use the closest REACHABLE state to all-ones (Hamming
        # distance 1 -- "all-ones except one node"). By the ring's rotational symmetry, ALL
        # 11 such states are topologically equivalent (any single-node flip), so the specific
        # choice (flip node N-1) does not introduce arbitrary bias -- this is a principled
        # substitute, not an arbitrary fallback.
        state_label = "all_ones_minus_node10 (all-ones unreachable for N=11; nearest reachable state, Hamming-dist=1, rotationally equivalent to any single-node flip)"
        state = tuple([1] * (N - 1) + [0])
        print(f"  WARNING: all_ones (idx={all_ones_idx}) has no pre-image under the XOR map for N={N}.", flush=True)
        print(f"  Using nearest reachable state instead: {state_label}", flush=True)
    else:
        state = tuple([1] * N)
    print(f"  State: {state_label} = {state}", flush=True)
    t0 = time.time()
    phi_val = compute_phi_for_state(N, state)
    t1 = time.time()
    print(f"  Phi(N={N}, {state_label}) = {phi_val:.5f}", flush=True)
    print(f"  Runtime: {t1-t0:.1f}s", flush=True)

    # Grade against pre-registered predictions
    phi9 = KNOWN_SERIES[9]
    phi7 = KNOWN_SERIES[7]
    phi10 = KNOWN_SERIES[10]
    p1_lo, p1_hi = 100, 320
    p1_pass = p1_lo <= phi_val <= p1_hi
    print(f"\n  P1 ([{p1_lo},{p1_hi}], power-law extrapolation ~179): "
          f"{'CONFIRMED' if p1_pass else 'OUTSIDE RANGE'} (actual {phi_val:.2f})")

    import math
    b_odd_new = math.log(phi_val / phi7) / math.log(N / 7)
    b_even = math.log(phi10 / 7.5) / math.log(10 / 8)  # from Exp76, N=8->10
    p3_diff = abs(b_odd_new - b_even)
    p3_pass = p3_diff < 0.5
    print(f"\n  b_odd (N=7->11, 2-point): {b_odd_new:.2f}")
    print(f"  b_even (N=8->10, from Exp76): {b_even:.2f}")
    print(f"  |diff|: {p3_diff:.2f}")
    print(f"  P3 (same growth rate, |diff|<0.5): {'CONFIRMED' if p3_pass else 'STILL DEVIATES'}")

    ratio_9_11 = phi_val / phi9 if phi9 else float("nan")
    print(f"\n  N=11/N=9 step ratio: {ratio_9_11:.3f} (exploratory, not pre-registered as falsifying)")

    output = {
        "experiment": "exp83",
        "author": "Whisper C4415",
        "date": "2026-06-30",
        "pyphi_version": pyphi.__version__,
        "N": N,
        "state": state_label,
        "state_bits": list(state),
        "all_ones_reachable": all_ones_idx in image,
        "phi": phi_val,
        "runtime_s": t1 - t0,
        "full_series": {**{str(k): v for k, v in KNOWN_SERIES.items()}, "11": phi_val},
        "prediction_results": {
            "P1_phi11_in_range_100_320": "CONFIRMED" if p1_pass else "OUTSIDE RANGE",
            "P3_b_odd_vs_b_even": "CONFIRMED" if p3_pass else "STILL DEVIATES",
            "b_odd_new": b_odd_new,
            "b_even": b_even,
            "ratio_9_11": ratio_9_11,
        },
        "finalized_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    with open(RESULTS_PATH, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n  Results saved: {RESULTS_PATH}")
    print(f"End: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}")


if __name__ == "__main__":
    main()
