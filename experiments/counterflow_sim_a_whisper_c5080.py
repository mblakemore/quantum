#!/usr/bin/env python3
"""counterflow_sim_a_whisper_c5080.py — Design A ($0 tier): the Counterflow Ladder.

Creator direction 2026-08-24: "sim A -> C -> B" (board #192, proposal
docs/counterflow-exchanger-designs-whisper-c5079.md).

MODEL. Two streams of two-level "parcels" (excitation populations), entering at
p_hot / p_cold. A stream on a static chip is a repeated-interaction sequence:
one fresh parcel per tick (MCM reset + prepare = advection). The exchanger has
N stages; a contact is a partial swap of populations with transmissivity tau:
    pH' = (1-tau) pH + tau pC ;  pC' = (1-tau) pC + tau pH
(the population action of a partial-SWAP unitary; coherences play no role in
this design by construction — that question is Design D's).

GEOMETRY = PAIRING ORDER ONLY (the confound-free comparison):
  COUNTERFLOW: H parcels traverse stages 1..N, C parcels traverse N..1.
    Tick schedule: every tick, the H parcel at stage k meets the C parcel at
    stage k; then H parcels shift +1 (exit at N), C parcels shift -1 (exit
    at 1); fresh parcels enter H@1, C@N.
  PARALLEL (co-flow): both streams traverse 1..N in the SAME direction; a
    fresh H,C pair enters together and contacts N times.
Same number of contacts per parcel (N), same tau, same shots.

WITNESS: temperature crossing. eps = (pC_exit - p_cold)/(p_hot - p_cold);
co-flow is capped at eps <= 1/2 (both parcels converge to their mean);
counterflow crosses: pC_exit > pH_exit.

SELFTEST (derivation discipline, C4558 house rule — no recalled formulas):
the N=2, tau=1/2 steady state was hand-solved in the C5079 proposal review:
h_exit = 1/3, c_exit = 2/3 (normalized). The transient simulator must
reproduce it at convergence before anything else is believed.

NOISE MODEL (floors from measured classes, not Fake* optimism — Exp139 lesson):
  - contact cost: 2 CZ; per-CZ depolarizing eps_cz pulls p toward 1/2:
        p -> (1-e) p + e/2 applied to BOTH parcels per contact, e = 2*eps_cz
  - advection cost: reset error r_reset (fresh parcel enters at
        p_prep*(1-r) + r*(bath-ish 0.5 mix) — modeled as p -> (1-r)p + r/2)
  - exit readout: asymmetric flips (r0: 0 read as 1, r1: 1 read as 0)
  - shot noise at SHOTS per exit estimate.
  Ranges swept: eps_cz in {0.3%, 0.6%, 1.0%}, readout r0=r1 in {1%, 2%},
  r_reset in {0.5%, 1.5%} — bracketing marrakesh-class medians. The prereg
  re-derives exact floors from live calibration; this sim asks whether the
  margin survives the CLASS.

OUTPUT: results/counterflow_sim_a_c5080.json + stdout table.
"""
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "results", "counterflow_sim_a_c5080.json")

P_HOT, P_COLD = 0.40, 0.05     # prepared stream temperatures (populations)
SHOTS = 10_000
RNG = np.random.default_rng(20260824)


def contact(ph, pc, tau):
    return (1 - tau) * ph + tau * pc, (1 - tau) * pc + tau * ph


def depol(p, e):
    return (1 - e) * p + e / 2.0


def run_counterflow(n_stages, tau, n_ticks, e_contact=0.0, r_reset=0.0):
    """Time-stepped counterflow. Returns exit-temperature series (post-transient)."""
    H = [None] * n_stages            # H[k] = parcel population at stage k (moving ->)
    C = [None] * n_stages            # C[k] = parcel population at stage k (moving <-)
    h_exits, c_exits = [], []
    # First tick starts with fresh injections; thereafter the per-tick order is
    # contact -> capture exits (parcels that just completed their FINAL contact)
    # -> shift+inject. The first version of this loop captured exits after the
    # shift, reading parcels one contact early — caught by the selftest exactly
    # as intended (values came out swapped: 2/3, 1/3).
    H[0] = depol(P_HOT, r_reset)
    C[-1] = depol(P_COLD, r_reset)
    for _ in range(n_ticks):
        # contacts at every occupied stage
        for k in range(n_stages):
            if H[k] is not None and C[k] is not None:
                ph, pc = contact(H[k], C[k], tau)
                H[k], C[k] = depol(ph, e_contact), depol(pc, e_contact)
        # capture exits: H completes its run at stage N-1, C at stage 0
        if H[-1] is not None:
            h_exits.append(H[-1])
        if C[0] is not None:
            c_exits.append(C[0])
        # shift + inject fresh parcels (advection, with reset error)
        H = [depol(P_HOT, r_reset)] + H[:-1]
        C = C[1:] + [depol(P_COLD, r_reset)]
    return np.array(h_exits), np.array(c_exits)


def run_parallel(n_stages, tau, e_contact=0.0, r_reset=0.0):
    """Co-flow: one H,C pair contacts N times. Steady immediately (no cross-parcel
    coupling), so a single pass IS the exit value."""
    ph, pc = depol(P_HOT, r_reset), depol(P_COLD, r_reset)
    for _ in range(n_stages):
        ph, pc = contact(ph, pc, tau)
        ph, pc = depol(ph, e_contact), depol(pc, e_contact)
    return ph, pc


def readout(p, r0, r1):
    return p * (1 - r1) + (1 - p) * r0


def measured(p, r0, r1, shots):
    """Simulated measured population with readout error + binomial shot noise."""
    pm = readout(p, r0, r1)
    return RNG.binomial(shots, pm) / shots


def selftest():
    """N=2, tau=1/2, normalized streams (hot=1, cold=0): hand-solved steady state
    h_exit=1/3, c_exit=2/3 (C5079 proposal review)."""
    global P_HOT, P_COLD
    saved = (P_HOT, P_COLD)
    P_HOT, P_COLD = 1.0, 0.0
    h, c = run_counterflow(2, 0.5, 400)
    P_HOT, P_COLD = saved
    ok = abs(h[-1] - 1 / 3) < 1e-9 and abs(c[-1] - 2 / 3) < 1e-9
    return ok, float(h[-1]), float(c[-1])


def main():
    ok, h_st, c_st = selftest()
    print(f"SELFTEST (N=2, tau=1/2 vs hand-solve 1/3, 2/3): "
          f"{'PASS' if ok else 'FAIL'}  h={h_st:.9f} c={c_st:.9f}")
    if not ok:
        raise SystemExit("selftest failed — nothing below is believable")

    results = {"selftest": {"pass": ok, "h": h_st, "c": c_st},
               "p_hot": P_HOT, "p_cold": P_COLD, "shots": SHOTS, "ideal": [],
               "noise_sweep": []}

    gap = P_HOT - P_COLD
    print(f"\nIDEAL steady state (p_hot={P_HOT}, p_cold={P_COLD}, gap={gap}):")
    print(f"{'N':>3} {'tau':>5} {'eps_cf':>7} {'eps_pf':>7} "
          f"{'crossing (pC_x - pH_x)':>22} {'ticks_to_99%':>12}")
    for n in (2, 3, 4):
        for tau in (0.3, 0.5, 0.7):
            h, c = run_counterflow(n, tau, 600)
            # convergence: ticks until within 1% of final crossing value
            cross_series = c - h
            final = cross_series[-1]
            conv = next((i for i, v in enumerate(cross_series)
                         if abs(v - final) <= 0.01 * abs(final)), len(cross_series))
            ph_x, pc_x = run_parallel(n, tau)
            eps_cf = (c[-1] - P_COLD) / gap
            eps_pf = (pc_x - P_COLD) / gap
            crossing = c[-1] - h[-1]
            results["ideal"].append(dict(N=n, tau=tau, eps_cf=eps_cf, eps_pf=eps_pf,
                                         crossing=crossing, ticks_to_conv=conv))
            print(f"{n:>3} {tau:>5.2f} {eps_cf:>7.4f} {eps_pf:>7.4f} "
                  f"{crossing:>22.4f} {conv:>12}")

    print(f"\nNOISE SWEEP (N=3, tau=0.5; crossing +/- shot SE at {SHOTS} shots, "
          f"exit estimates averaged over last 20 parcels):")
    print(f"{'eps_cz':>7} {'readout':>8} {'reset':>6} {'crossing':>9} "
          f"{'SE':>7} {'z':>7} {'null-arm |cross|':>16}")
    for eps_cz in (0.003, 0.006, 0.010):
        for r_read in (0.01, 0.02):
            for r_reset in (0.005, 0.015):
                e_c = 2 * eps_cz  # 2 CZ per contact
                h, c = run_counterflow(3, 0.5, 200, e_contact=e_c, r_reset=r_reset)
                # exit estimates: average the last 20 steady parcels, measured
                h_meas = np.mean([measured(p, r_read, r_read, SHOTS) for p in h[-20:]])
                c_meas = np.mean([measured(p, r_read, r_read, SHOTS) for p in c[-20:]])
                crossing = c_meas - h_meas
                se = np.sqrt(2 * 0.25 / (SHOTS * 20))  # conservative binomial SE
                # NULL ARM: both streams prepared EQUAL (at the mean) — any apparent
                # crossing is apparatus bias; ideal value exactly 0.
                pm = (P_HOT + P_COLD) / 2
                saved = (globals()["P_HOT"], globals()["P_COLD"])
                globals()["P_HOT"] = globals()["P_COLD"] = pm
                hn, cn = run_counterflow(3, 0.5, 200, e_contact=e_c, r_reset=r_reset)
                globals()["P_HOT"], globals()["P_COLD"] = saved
                null_cross = abs(np.mean([measured(p, r_read, r_read, SHOTS)
                                          for p in cn[-20:]])
                                 - np.mean([measured(p, r_read, r_read, SHOTS)
                                            for p in hn[-20:]]))
                z = crossing / se
                results["noise_sweep"].append(dict(
                    eps_cz=eps_cz, r_read=r_read, r_reset=r_reset,
                    crossing=crossing, se=se, z=z, null_crossing=null_cross))
                print(f"{eps_cz:>7.3f} {r_read:>8.2f} {r_reset:>6.3f} "
                      f"{crossing:>9.4f} {se:>7.4f} {z:>7.1f} {null_cross:>16.4f}")

    worst = min(results["noise_sweep"], key=lambda r: r["z"])
    results["verdict"] = {
        "worst_case_z": worst["z"],
        "worst_case_crossing": worst["crossing"],
        "go_recommendation": bool(worst["z"] > 10),
        "note": ("crossing = cold-exit minus hot-exit; co-flow cannot exceed 0 "
                 "at equal capacities. Hardware embedding: N=3 counterflow at "
                 "steady state = 2 qubits per stage pair-row = 6 data qubits + "
                 "resets; ~2 CZ/contact, 3 contacts per parcel.")}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(results, f, indent=2, default=float)
    print(f"\nWORST-CASE noise cell: crossing={worst['crossing']:.4f} "
          f"z={worst['z']:.1f} -> GO recommended: {results['verdict']['go_recommendation']}")
    print(f"wrote {os.path.relpath(OUT, HERE + '/..')}")


if __name__ == "__main__":
    main()
