#!/usr/bin/env python3
"""counterflow_sim_b_whisper_c5080.py — Design B ($0 tier): the Manufactured
Bath — the branch-splitter cascade in counterflow geometry.

Creator direction 2026-08-24: "sim A -> C -> B" (board #192).

WHAT THIS IS (and why it is NOT the closed C4720 cascade). C4720 fed the
cooled TARGET back through a switch whose channels re-thermalize toward the
SAME fixed bath (0.25) — that saturates at 0.177 and inverts on hardware.
Here the CHANNELS' BATHS are themselves the previous stage's cold branches:
exp108 implements a fully-thermalizing channel as SWAP with a fresh ancilla
prepared in the bath state, so "bath = colder" is literally "ancillas prepared
in stage-(k-1) cold-branch states". C4720's own Route C table (bath 0.25 ->
0.185, 0.10 -> 0.058, 0.05 -> 0.027) shows the ratio IMPROVES as baths cool —
but those numbers are input-dependent, so nothing below trusts them: the
supermap is computed exactly on the 16-dim (c,t,a1,a2) space and SELFTESTED
against exp108's frozen values (P+=0.71875, p+=0.184783, p-=0.416667 at
g=0.75, all inputs 0.25) before any cascade is believed.

COUNTERFLOW LEDGER: every stage also emits HOT branches (p- ~ 0.417 and
hotter as the cascade deepens on the + side? measured, not assumed) — the
exhaust stream flowing the other way. Both streams are counted; the hot
parcels are F95's engine feed, not waste, but that coupling is out of scope
here (ledger only).

HARDWARE MODELS (bracketing, from F118's one measured point: theory 0.185 ->
hw ~0.21 at the 22-CZ skeleton):
  I  additive:      p_hw = p_exact + 0.025 per stage output
  II multiplicative: p_hw = (1-a) p_exact + a * p_in, a fit so stage 1
     reproduces 0.21 from 0.25 (attenuation toward the stage input)
Both are per-stage output degradations of the DELIVERED parcel; the lineage
depth per parcel stays ONE switch (ancestry is in the preparation tree, not
the circuit depth of any single qubit) — the structural reason the C4720
inversion does not apply and the thing the sim must make explicit.

RESOURCE TREE (mode "full lineage": target + both ancillas from the cold
pool): parcels_k = 3 * parcels_{k-1} / P+_k ; switches_k = 3*switches_{k-1}+1.
Mode "cheap": target = fresh bath parcel, only ancillas from the cold pool.

OUTPUT: results/counterflow_sim_b_c5080.json + stdout table.
"""
import itertools
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "results", "counterflow_sim_b_c5080.json")

# ---- exact 16-dim switch supermap (order: c, t, a1, a2) ----


def perm_matrix(perm):
    """perm maps basis index -> basis index on (t,a1,a2) 3-bit space."""
    P = np.zeros((8, 8))
    for src, dst in perm.items():
        P[dst, src] = 1.0
    return P


def bits(i):
    return ((i >> 2) & 1, (i >> 1) & 1, i & 1)   # (t, a1, a2)


def idx(t, a1, a2):
    return (t << 2) | (a1 << 1) | a2


# C3 = SWAP(t,a2) after SWAP(t,a1): (t,a1,a2) -> (a1,t,a2) -> (a2,t,a1)
C3 = perm_matrix({i: idx(a2, t, a1) for i in range(8)
                  for t, a1, a2 in [bits(i)]})
C3sq = C3 @ C3

KET0 = np.array([[1.0], [0.0]])
KET1 = np.array([[0.0], [1.0]])
PLUS = (KET0 + KET1) / np.sqrt(2)
U_SWITCH = (np.kron(KET0 @ KET0.T, C3) + np.kron(KET1 @ KET1.T, C3sq))
XPROJ = {+1: (np.eye(2) + np.array([[0, 1], [1, 0]])) / 2,
         -1: (np.eye(2) - np.array([[0, 1], [1, 0]])) / 2}


def tau(p):
    return np.diag([1.0 - p, p])


def switch_map(p_t, p_a1, p_a2):
    """Exact heralded outputs: returns dict with P(+), p1|+, P(-), p1|-."""
    rho = np.kron(PLUS @ PLUS.T, np.kron(tau(p_t), np.kron(tau(p_a1), tau(p_a2))))
    rho = U_SWITCH @ rho @ U_SWITCH.conj().T
    out = {}
    for s in (+1, -1):
        P = np.kron(XPROJ[s], np.eye(8))
        pr = float(np.real(np.trace(P @ rho @ P)))
        cond = P @ rho @ P / pr
        # trace out control, a1, a2 -> target 2x2
        t_rho = np.zeros((2, 2), dtype=complex)
        for c, a1, a2 in itertools.product((0, 1), repeat=3):
            for t_r, t_c in itertools.product((0, 1), repeat=2):
                r = (c << 3) | idx(t_r, a1, a2)
                cc = (c << 3) | idx(t_c, a1, a2)
                t_rho[t_r, t_c] += cond[r, cc]
        out[s] = (pr, float(np.real(t_rho[1, 1])))
    return {"P_plus": out[+1][0], "p_plus": out[+1][1],
            "P_minus": out[-1][0], "p_minus": out[-1][1]}


def selftest():
    m = switch_map(0.25, 0.25, 0.25)
    ok = (abs(m["P_plus"] - 0.71875) < 1e-9
          and abs(m["p_plus"] - 0.184783) < 1e-5
          and abs(m["p_minus"] - 0.416667) < 1e-5)
    return ok, m


def main():
    ok, m = selftest()
    print(f"SELFTEST vs exp108 frozen (P+=0.71875, p+=0.184783, p-=0.416667): "
          f"{'PASS' if ok else 'FAIL'}  got P+={m['P_plus']:.6f} "
          f"p+={m['p_plus']:.6f} p-={m['p_minus']:.6f}")
    if not ok:
        raise SystemExit("selftest failed — supermap convention wrong, "
                         "nothing below is believable")

    results = {"selftest": m, "modes": {}}
    ALPHA = None  # fit for model II: (1-a)*0.184783 + a*0.25 = 0.21
    ALPHA = (0.21 - 0.184783) / (0.25 - 0.184783)

    for mode in ("full_lineage", "cheap_target"):
        print(f"\nMODE {mode}  (hw-I: +0.025/stage; hw-II: attenuation "
              f"a={ALPHA:.3f} toward stage input)")
        print(f"{'k':>2} {'p_exact':>8} {'p_hw_I':>7} {'p_hw_II':>7} "
              f"{'P+':>7} {'p_hot_exhaust':>13} {'parcels':>9} {'switches':>8}")
        rows = []
        p_ex, p_h1, p_h2 = 0.25, 0.25, 0.25
        parcels, switches = 1.0, 0.0
        for k in range(1, 7):
            def stage(p_in_cold, raw=0.25):
                t_in = p_in_cold if mode == "full_lineage" else raw
                return switch_map(t_in, p_in_cold, p_in_cold)

            m_ex = stage(p_ex)
            m_h1 = stage(p_h1)
            m_h2 = stage(p_h2)
            p_ex = m_ex["p_plus"]
            p_h1 = min(m_h1["p_plus"] + 0.025, 1.0)
            p_h2 = (1 - ALPHA) * m_h2["p_plus"] + ALPHA * p_h2
            n_pool = 3 if mode == "full_lineage" else 2
            parcels = (n_pool * parcels + (1 if mode == "cheap_target" else 0)) \
                / m_ex["P_plus"]
            switches = n_pool * switches + 1
            rows.append(dict(k=k, p_exact=p_ex, p_hw_I=p_h1, p_hw_II=p_h2,
                             P_plus=m_ex["P_plus"], p_hot=m_ex["p_minus"],
                             parcels=parcels, switches=switches))
            print(f"{k:>2} {p_ex:>8.5f} {p_h1:>7.4f} {p_h2:>7.4f} "
                  f"{m_ex['P_plus']:>7.4f} {m_ex['p_minus']:>13.4f} "
                  f"{parcels:>9.1f} {switches:>8.0f}")
        results["modes"][mode] = rows

    # reference lines
    fl = results["modes"]["full_lineage"]
    below_floor_I = next((r for r in fl if r["p_hw_I"] < 0.177), None)
    below_floor_II = next((r for r in fl if r["p_hw_II"] < 0.177), None)
    results["reference"] = {
        "c4720_fixed_bath_floor": 0.177,
        "f118_hw_stage1": 0.21,
        "first_stage_below_floor_hw_I": below_floor_I["k"] if below_floor_I else None,
        "first_stage_below_floor_hw_II": below_floor_II["k"] if below_floor_II else None,
        "note": ("reset-cold (~0.01) remains the trivial import outside the "
                 "resource scenario; the claim is scenario-bound sub-bath cold "
                 "from warm baths + causal structure only (F118's framing). "
                 "Hot exhaust parcels are F95 engine feed (ledger only here).")}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(results, f, indent=2, default=float)
    fbI = results["reference"]["first_stage_below_floor_hw_I"]
    fbII = results["reference"]["first_stage_below_floor_hw_II"]
    print(f"\nFirst stage below the 0.177 fixed-bath floor: hw-I k={fbI}, "
          f"hw-II k={fbII}")
    print(f"wrote {os.path.relpath(OUT, HERE + '/..')}")


if __name__ == "__main__":
    main()
