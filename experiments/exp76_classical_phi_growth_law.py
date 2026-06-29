#!/usr/bin/env python3
"""
exp76_classical_phi_growth_law.py — Whisper C4412 (2026-06-29)

Compute classical IIT Phi (PyPhi) for N=10 XOR ring to test the power law growth model.
Pre-registration: exp76-classical-phi-growth-law-preregistration.md

Context:
  Ember C4022/C4023 found classical Phi for N=5..9 (odd/even growth rate gap).
  F45 theory predicted N=8→0 (nilpotent) and N=9→<49.6 (multiple blocks).
  BOTH predictions were falsified (N=8=7.5, N=9=115.619).
  F52 (Whisper C4412) explains WHY: algebraic decomposability ≠ physical separability.
  This experiment extends the series to N=10 to test the power law Phi ~ a × N^4.8.

Topology:
  N-node ring where each node k's next state = state[(k-1)%N] XOR state[(k+1)%N]
  Same as F43/F45/Ember experiments.

Pre-registered predictions:
  P1: N=10 Phi ∈ [12, 28] (power law: ~17.4)
  P2: Odd/even ratio at N=9/N=10 ∈ [4, 10]

Author: Whisper DC15W C4412 | Classical sim, zero QPU.
"""

import numpy as np
import json
import time
import os
import sys

PYPHI_WELCOME_OFF = os.environ.get("PYPHI_WELCOME_OFF", "")
os.environ["PYPHI_WELCOME_OFF"] = "yes"

import pyphi

# Suppress PyPhi progress bars for cleaner output
pyphi.config.PROGRESS_BARS = False
pyphi.config.PARALLEL_CONCEPT_EVALUATION = False

# ─── Ring topology ──────────────────────────────────────────────────────────

def build_xor_ring_tpm(N):
    """
    Build the (2^N, N) transition probability matrix for an N-node XOR ring.
    Each node k's next state = state[(k-1)%N] XOR state[(k+1)%N].
    Returns a float64 matrix (deterministic: 0.0 or 1.0 entries).
    """
    n_states = 2 ** N
    tpm = np.zeros((n_states, N), dtype=float)
    for state_idx in range(n_states):
        # Decode state
        state = [(state_idx >> i) & 1 for i in range(N)]
        # Compute next state
        next_state = [state[(k - 1) % N] ^ state[(k + 1) % N] for k in range(N)]
        # Encode next state
        next_idx = sum(next_state[i] << i for i in range(N))
        tpm[state_idx, :] = next_state
    return tpm


def build_xor_ring_cm(N):
    """
    Connectivity matrix: node k is connected to k-1 and k+1 (mod N).
    """
    cm = np.zeros((N, N), dtype=int)
    for k in range(N):
        cm[k, (k - 1) % N] = 1
        cm[k, (k + 1) % N] = 1
    return cm


# ─── Single Phi computation ───────────────────────────────────────────────

def compute_phi_for_state(N, state, label=""):
    """Compute PyPhi Phi for a given state tuple."""
    tpm = build_xor_ring_tpm(N)
    cm = build_xor_ring_cm(N)
    network = pyphi.Network(tpm, cm=cm)
    node_indices = tuple(range(N))
    try:
        subsystem = pyphi.Subsystem(network, state, node_indices)
        sia = pyphi.compute.phi(subsystem)
        phi_val = sia.phi
    except Exception as e:
        phi_val = None
        print(f"  ERROR for state {state} ({label}): {e}")
    return phi_val


# ─── Main ─────────────────────────────────────────────────────────────────

def main():
    start_wall = time.time()
    results = {}
    print(f"Exp76: Classical XOR Ring Phi Growth Law")
    print(f"PyPhi version: {pyphi.__version__}")
    print(f"Start: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}")
    print()

    # Test states to probe
    # "all ones" = (1,1,1,...,1) — canonical high-activity state
    # "single on" = (1,0,0,...,0) — minimal activity
    # "alternating" = (1,0,1,0,...) — for even N only

    for N in [8, 10]:  # N=8 as calibration (expected ~7.5), N=10 as new data
        print(f"\n{'='*60}")
        print(f"N = {N}")
        print(f"{'='*60}")
        results[N] = {}

        # Pre-registered primary state: all-ones
        all_ones = tuple([1] * N)
        t0 = time.time()
        print(f"  State: all_ones = {all_ones}")
        phi_ones = compute_phi_for_state(N, all_ones, "all_ones")
        t1 = time.time()
        print(f"  Phi(all_ones) = {phi_ones:.4f}" if phi_ones is not None else "  Phi(all_ones) = ERROR")
        print(f"  Runtime: {t1-t0:.1f}s")
        results[N]["all_ones"] = {"state": list(all_ones), "phi": phi_ones, "runtime_s": t1-t0}

        # Secondary: single-on
        single_on = tuple([1] + [0] * (N - 1))
        print(f"\n  State: single_on = {single_on[:5]}...{single_on[-1]}")
        t0 = time.time()
        phi_single = compute_phi_for_state(N, single_on, "single_on")
        t1 = time.time()
        print(f"  Phi(single_on) = {phi_single:.4f}" if phi_single is not None else "  Phi(single_on) = ERROR")
        print(f"  Runtime: {t1-t0:.1f}s")
        results[N]["single_on"] = {"state": list(single_on), "phi": phi_single, "runtime_s": t1-t0}

        # Secondary: alternating (for even N)
        if N % 2 == 0:
            alt = tuple([i % 2 for i in range(N)])
            print(f"\n  State: alternating = {alt}")
            t0 = time.time()
            phi_alt = compute_phi_for_state(N, alt, "alternating")
            t1 = time.time()
            print(f"  Phi(alternating) = {phi_alt:.4f}" if phi_alt is not None else "  Phi(alternating) = ERROR")
            print(f"  Runtime: {t1-t0:.1f}s")
            results[N]["alternating"] = {"state": list(alt), "phi": phi_alt, "runtime_s": t1-t0}

        print(f"\n  N={N} complete. Total so far: {time.time()-start_wall:.0f}s")

    # Results summary
    total_time = time.time() - start_wall
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")

    known_series = {4: 0.0, 5: 15.156, 6: 1.875, 7: 49.609, 8: 7.5, 9: 115.619}
    print(f"Known series (Ember C4022/C4023):")
    for n, phi in sorted(known_series.items()):
        parity = "odd" if n % 2 == 1 else "even"
        print(f"  N={n} ({parity}): Phi = {phi:.3f}")

    print(f"\nNew results:")
    calibration_ok = False
    if 8 in results:
        phi8 = results[8].get("all_ones", {}).get("phi")
        if phi8 is not None:
            calibration_ok = abs(phi8 - 7.5) < 2.0
            print(f"  N=8 calibration: Phi(all_ones) = {phi8:.4f} (expected ~7.5, {'OK' if calibration_ok else 'MISMATCH'})")

    if 10 in results:
        phi10 = results[10].get("all_ones", {}).get("phi")
        if phi10 is not None:
            in_range = 12 <= phi10 <= 28
            print(f"  N=10 result: Phi(all_ones) = {phi10:.4f}")
            print(f"  P1 ([12,28]): {'CONFIRMED' if in_range else 'OUTSIDE RANGE'}")
            if phi10 > 0:
                ratio_9_10 = 115.619 / phi10
                in_ratio = 4 <= ratio_9_10 <= 10
                print(f"  N=9/N=10 ratio: {ratio_9_10:.2f}")
                print(f"  P3 (ratio [4,10]): {'CONFIRMED' if in_ratio else 'OUTSIDE RANGE'}")

    # Power law fitting if we have N=10
    if 10 in results and results[10].get("all_ones", {}).get("phi") is not None:
        phi10 = results[10]["all_ones"]["phi"]
        # Even series: N=6(1.875), N=8(7.5), N=10(phi10)
        print(f"\n  Even series power law:")
        if phi10 > 0:
            # Fit b from N=8 and N=10
            import math
            b_new = math.log(phi10 / 7.5) / math.log(10 / 8)
            b_old = math.log(7.5 / 1.875) / math.log(8 / 6)
            print(f"    N=6→8 exponent: {b_old:.2f}")
            print(f"    N=8→10 exponent: {b_new:.2f}")
            print(f"    P4 (same b±0.5): {'CONFIRMED' if abs(b_new-b_old) < 0.5 else 'DEVIATION'}")

    print(f"\nTotal runtime: {total_time:.1f}s")
    print(f"End: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}")

    # Save results
    output = {
        "experiment": "exp76",
        "author": "Whisper C4412",
        "date": "2026-06-29",
        "total_runtime_s": total_time,
        "results": results,
        "known_series": known_series,
        "preregistration": "exp76-classical-phi-growth-law-preregistration.md"
    }
    output_file = os.path.join(os.path.dirname(__file__), "exp76_results.json")
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()
