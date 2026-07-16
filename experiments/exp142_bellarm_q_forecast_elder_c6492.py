#!/usr/bin/env python3
"""Exp142 Bell-arm budget forecast at MEASURED kingston q — Elder C6492.

Question (Amendment A2 strengthener, run while n8/n10 in flight): kingston's
measured cal q_hat (n4 3.67%, n6 4.33% raw; q_used 4.75%/5.51%) is HIGHER than
the FakeMarrakesh noise Gate-2 v2 previewed. Does the quantum (Bell) arm still
identify P within the FROZEN budgets B_q = {8: 90, 10: 110} at that q?

Method: pure symplectic-space MC reusing the FROZEN Gate-2 decoder machinery
(exp142_robust_decoder_sim: calibrate_bell_mapping / calibrate_constraint_sign /
candidate_matrix / decode_success_curve — imported, not re-implemented):
  - hidden full-weight P per trial (uniform over 3^n)
  - ideal Bell outcomes: Q uniform on {<Q,P>_sp = csign[ypar(P)]} (pivot method)
  - Q -> RAW 2n measured bits via the INVERSE of the calibrated Bell mapping
  - iid readout flips at q on the raw bits (same elevated-iid proxy the
    pre-registered Stage-2 sim used; does NOT model CX/prep correlations)
  - raw -> Q via the calibrated mapping, frozen ML decode, success = unique
    argmax == true P at prefix m
Forecast only — grading still uses the frozen decode_meter on hardware data.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import exp142_robust_decoder_sim as g2

rng = np.random.default_rng(64920)

B_Q = {4: 60, 6: 80, 8: 90, 10: 110}


def inverse_mapping(mapping):
    """mapping: (a_bit, b_bit) -> (x, z). Return (x, z) -> (a_bit, b_bit)."""
    inv = {v: k for k, v in mapping.items()}
    assert len(inv) == 4, "Bell mapping not bijective?"
    return inv


def sample_Q_given_P(v_P, c, n, m, rng):
    """m uniform Q (2n bits) with <Q,P>_sp = c. Constraint coeffs s = (P_z | P_x)."""
    s = np.concatenate([v_P[n:], v_P[:n]]).astype(np.int8)
    piv = int(np.flatnonzero(s)[0])
    Q = rng.integers(0, 2, size=(m, 2 * n), dtype=np.int8)
    # solve pivot bit so that Q . s == c (mod 2)
    rest = (Q @ s - Q[:, piv] * s[piv]) % 2
    Q[:, piv] = (c - rest) % 2
    return Q


def q_to_raw(Q, n, inv):
    """(m, 2n) Q bits -> (m, 2n) raw measured bits [a_0..a_{n-1}, b_0..b_{n-1}]."""
    m = Q.shape[0]
    raw = np.zeros_like(Q)
    for i in range(n):
        for r in range(m):
            a, b = inv[(int(Q[r, i]), int(Q[r, n + i]))]
            raw[r, i], raw[r, n + i] = a, b
    return raw


def raw_to_q(raw, n, mapping):
    m = raw.shape[0]
    Q = np.zeros_like(raw)
    for i in range(n):
        for r in range(m):
            x, z = mapping[(int(raw[r, i]), int(raw[r, n + i]))]
            Q[r, i], Q[r, n + i] = x, z
    return Q


def forecast(n, q, trials, mapping, csign, inv):
    cands, cand_M, ypar = g2.candidate_matrix(n)
    m_max = max(2 * B_Q[n], 200)
    grid = sorted(set(list(range(4, 60, 2)) + list(range(60, m_max + 1, 10)) + [B_Q[n]]))
    tally = {m: 0 for m in grid}
    for t in range(trials):
        idx = int(rng.integers(0, len(cands)))
        v_P = cand_M[idx]
        c = csign[int(ypar[idx])]
        Q = sample_Q_given_P(v_P, c, n, m_max, rng)
        raw = q_to_raw(Q, n, inv)
        flips = (rng.random(raw.shape) < q).astype(np.int8)
        raw = (raw + flips) % 2
        Qn = raw_to_q(raw, n, mapping)
        curve = g2.decode_success_curve(Qn, idx, cand_M, ypar, csign, n, grid)
        for m, s in curve.items():
            tally[m] += s
    curve = {m: tally[m] / trials for m in grid}
    return curve


def m99(curve):
    ms = sorted(curve)
    for i, m in enumerate(ms):
        if all(curve[mm] >= 0.99 for mm in ms[i:]):
            return m
    return None


def main():
    print("calibrating Bell mapping from Statevector (frozen-script method)...")
    mapping = g2.calibrate_bell_mapping()
    csign = g2.calibrate_constraint_sign(mapping)
    inv = inverse_mapping(mapping)
    print(f"mapping={mapping} csign={csign}")

    trials = 200
    out = {"method": "iid readout-flip proxy on raw Bell bits at measured kingston q; frozen Gate-2 ML decoder",
           "trials_per_cell": trials, "budgets": B_Q, "cells": []}
    for n in (8, 10):
        for q in (0.044, 0.055, 0.08):
            curve = forecast(n, q, trials, mapping, csign, inv)
            m = m99(curve)
            at_budget = curve.get(B_Q[n])
            verdict = "PASS" if (m is not None and m <= B_Q[n]) else "AT-RISK"
            print(f"n={n} q={q:.3f}: m99={m} budget={B_Q[n]} "
                  f"success@budget={at_budget} -> {verdict}", flush=True)
            out["cells"].append({"n": n, "q": q, "m99": m, "budget": B_Q[n],
                                 "success_at_budget": at_budget, "verdict": verdict})
    path = os.path.join(HERE, "..", "results",
                        "exp142_bellarm_q_forecast_elder_c6492.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    print("->", path)


if __name__ == "__main__":
    main()
