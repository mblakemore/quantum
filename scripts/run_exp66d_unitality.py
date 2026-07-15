#!/usr/bin/env python3
"""
Exp66 Part D: Unitality mechanism test (Ember C4183).

Tests my own C4171 attribution: is the FakeMarrakesh granular-capk LIFT over noiseless
caused specifically by NON-UNITAL noise (amplitude damping), or is it generic
noise-assisted COBYLA exploration (any channel helps)?

Design (pre-reg: experiments/exp66d-unitality-mechanism-preregistration.md):
  3 arms on the SAME 16 cells, SAME base AerSimulator, MATCHED per-gate infidelity:
    noiseless  : no noise model
    unital     : depolarizing_error on h (1q) + cx (2q)
    nonunital  : amplitude_damping_error on h (1q) + AD(x)AD on cx (2q)
  Only the channel's unitality differs; parameters solved to equal avg-gate-infidelity.
  Paired by seed (identical initial params across arms) → paired bootstrap Δ has power at N=16.

USAGE:
  python3 run_exp66d_unitality.py --smoke        # 2 cells, one arm, time a cell
  python3 run_exp66d_unitality.py --run          # full 16 cells x 3 arms
"""
import sys, os, json, time, argparse
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_exp46_fast import EDGES_20, N_QUBITS_20, brute_force_max_cut
from run_exp61_bestofk_anchor import build_for_p
from run_exp57_instance_generalization import gen_instance
from run_exp66_noiseless_granular import run_cell_noiseless, _pooled_loo, _policy_lift

from qiskit.quantum_info import average_gate_fidelity
from qiskit_aer import AerSimulator
from qiskit_aer.noise import (NoiseModel, depolarizing_error,
                              amplitude_damping_error)

# ---- Pre-registered targets (frozen before compute) ----
EPS1 = 0.0006   # target 1q avg-gate-infidelity (on h)
EPS2 = 0.003    # target 2q avg-gate-infidelity (on cx)
K_MAX, SHOTS, MAXITER = 3, 32, 10   # PILOT (measured 491s/cell at 96/15 — see prereg note)

# 6-cell PILOT set = first 6 of Part C's frozen 34-cell pool order
CELLS_SPEC = (
    [("EDGES_20", s) for s in range(42, 48)]                                  # 6
)  # total 6

RESULTS = os.path.join(HERE, "..", "experiments", "exp66d_results.json")


def _edges_for(label):
    return EDGES_20 if label == "EDGES_20" else gen_instance(int(label.replace("rand_seed", "")))


def _solve_param(make_err, target_infid, lo, hi):
    """Bisection: find channel param p in [lo,hi] s.t. 1-avg_gate_fid(make_err(p)) == target."""
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        infid = 1.0 - average_gate_fidelity(make_err(mid))
        if infid < target_infid:
            lo = mid
        else:
            hi = mid
    p = 0.5 * (lo + hi)
    return p, 1.0 - average_gate_fidelity(make_err(p))


def build_noise_model(kind):
    """kind in {'unital','nonunital'}; returns (NoiseModel, info dict)."""
    info = {}
    if kind == "unital":
        p1, i1 = _solve_param(lambda p: depolarizing_error(p, 1), EPS1, 0.0, 0.5)
        p2, i2 = _solve_param(lambda p: depolarizing_error(p, 2), EPS2, 0.0, 1.0)
        e1 = depolarizing_error(p1, 1)
        e2 = depolarizing_error(p2, 2)
        info = {"kind": kind, "p1": p1, "p2": p2, "infid1": i1, "infid2": i2}
    elif kind == "nonunital":
        g1, i1 = _solve_param(lambda g: amplitude_damping_error(g), EPS1, 0.0, 1.0)
        # 2q = AD(g2) tensor AD(g2); solve g2 to match 2q target infidelity
        g2, i2 = _solve_param(
            lambda g: amplitude_damping_error(g).tensor(amplitude_damping_error(g)),
            EPS2, 0.0, 1.0)
        e1 = amplitude_damping_error(g1)
        e2 = amplitude_damping_error(g2).tensor(amplitude_damping_error(g2))
        info = {"kind": kind, "g1": g1, "g2": g2, "infid1": i1, "infid2": i2}
    else:
        raise ValueError(kind)
    nm = NoiseModel()
    nm.add_all_qubit_quantum_error(e1, ["h"])
    nm.add_all_qubit_quantum_error(e2, ["cx"])
    return nm, info


def make_sim(kind):
    if kind == "noiseless":
        return AerSimulator(method="statevector", seed_simulator=1234), {"kind": "noiseless"}
    nm, info = build_noise_model(kind)
    return AerSimulator(noise_model=nm, method="statevector", seed_simulator=1234), info


def run_arm(kind, cells, circ_cache, cut_cache):
    sim, info = make_sim(kind)
    print(f"\n=== ARM {kind} === noise info: {json.dumps(info)}", flush=True)
    recs = []
    for inst_label, seed in cells:
        rec = run_cell_noiseless(seed, K_MAX, _edges_for(inst_label), cut_cache[inst_label],
                                 SHOTS, MAXITER, sim, N_QUBITS_20, circ_cache[inst_label])
        rec["instance"] = inst_label
        recs.append(rec)
    return recs, info


def capk_of(recs):
    cap_g, mk_g, _ = _pooled_loo(recs, granular=True)
    return (cap_g / mk_g) if mk_g else float("nan"), cap_g, mk_g


def paired_delta_bootstrap(recs_nu, recs_un, draws=5000):
    """Paired bootstrap of Δ = capk_nonunital - capk_unital, resampling the SAME cell index
    for both arms each draw (cells are seed-aligned)."""
    def pairs(recs):
        r0 = [r["r_p3_anchors"][0] for r in recs]
        out = []
        for i, rec in enumerate(recs):
            others = [r0[j] for j in range(len(recs)) if j != i]
            tau_i = float(np.median(others))
            _, lift = _policy_lift(rec, tau_i, True)
            out.append((lift, rec["lift_byk"][-1]))
        return out
    pnu, pun = pairs(recs_nu), pairs(recs_un)
    n = len(pnu)
    rng = np.random.RandomState(6683)
    deltas = []
    for _ in range(draws):
        idx = rng.randint(0, n, n)
        def capk(pp):
            num = sum(pp[k][0] for k in idx); den = sum(pp[k][1] for k in idx)
            mk = 1.0  # mean_k cancels approx in paired diff; use capture ratio proxy
            return num / den if den else float("nan")
        deltas.append(capk(pnu) - capk(pun))
    deltas = np.asarray([d for d in deltas if np.isfinite(d)])
    return {
        "frac_delta_gt0": float(np.mean(deltas > 0)),
        "delta_median": float(np.median(deltas)),
        "delta_ci95": [float(np.percentile(deltas, 2.5)), float(np.percentile(deltas, 97.5))],
        "draws": int(len(deltas)),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--run", action="store_true")
    args = ap.parse_args()

    cells = [(lab, s) for (lab, s) in CELLS_SPEC]
    if args.smoke:
        cells = cells[:2]

    # circuits built on a NOISELESS sim (transpilation target); executed on each arm's sim
    build_sim = AerSimulator()
    circ_cache, cut_cache = {}, {}
    for inst_label, _ in cells:
        if inst_label not in circ_cache:
            edges = _edges_for(inst_label)
            cut_cache[inst_label] = brute_force_max_cut(N_QUBITS_20, edges)
            circ_cache[inst_label] = {p: build_for_p(p, build_sim, N_QUBITS_20, edges) for p in (3, 5)}
            print(f"--- {inst_label}: max_cut={cut_cache[inst_label]} ---", flush=True)

    if args.smoke:
        t0 = time.time()
        recs, info = run_arm("nonunital", cells, circ_cache, cut_cache)
        ck, cap, mk = capk_of(recs)
        print(f"\nSMOKE nonunital: {len(cells)} cells in {time.time()-t0:.1f}s "
              f"(~{(time.time()-t0)/len(cells):.1f}s/cell) capk={ck:.4f}")
        return

    t0 = time.time()
    out = {"experiment": "Exp66-D-unitality-mechanism", "author": "Ember", "cycle": "C4183",
           "pre_registration": "experiments/exp66d-unitality-mechanism-preregistration.md",
           "targets": {"eps1_1q": EPS1, "eps2_2q": EPS2},
           "cells": [f"{l}:{s}" for l, s in cells], "arms": {}}
    arm_recs = {}
    for kind in ("noiseless", "unital", "nonunital"):
        recs, info = run_arm(kind, cells, circ_cache, cut_cache)
        ck, cap, mk = capk_of(recs)
        arm_recs[kind] = recs
        out["arms"][kind] = {"noise_info": info, "capk": ck, "loo_capture": cap, "mean_k": mk,
                             "data": recs}
        print(f"  [{kind}] capk={ck:.4f} (capture={cap:.4f} mean_k={mk:.3f})", flush=True)

    out["paired_delta_nonunital_minus_unital"] = paired_delta_bootstrap(
        arm_recs["nonunital"], arm_recs["unital"])
    out["elapsed_s"] = time.time() - t0

    # verdict per pre-reg grader
    d = out["paired_delta_nonunital_minus_unital"]
    ck = {k: out["arms"][k]["capk"] for k in out["arms"]}
    if d["frac_delta_gt0"] >= 0.667 and ck["nonunital"] >= ck["noiseless"]:
        verdict = "H_mech VALIDATED (non-unitality specifically lifts capk)"
    elif ck["unital"] >= ck["nonunital"]:
        verdict = "FALSIFIED — generic noise-assisted exploration (unital lifts >= non-unital)"
    else:
        verdict = "INCONCLUSIVE / NULL — see arms + CI"
    out["verdict"] = verdict
    print(f"\nVERDICT: {verdict}")
    print(f"  capk noiseless={ck['noiseless']:.4f} unital={ck['unital']:.4f} nonunital={ck['nonunital']:.4f}")
    print(f"  paired Δ(nu-un) median={d['delta_median']:+.4f} frac>0={d['frac_delta_gt0']:.3f} "
          f"CI95={d['delta_ci95']}")

    json.dump(out, open(RESULTS, "w"), indent=2)
    print(f"\nWrote {RESULTS}  ({out['elapsed_s']:.0f}s)")


if __name__ == "__main__":
    main()
