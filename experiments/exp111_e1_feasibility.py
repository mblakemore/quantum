#!/usr/bin/env python3
"""exp111_e1_feasibility.py — E1 four-arm resource comparison, feasibility tiers
(Whisper C4593, comms path E1; theory tier C4589 = tools/e1_resource_comparison_sim.py).

Arms (all built from the exp105/106 validated primitives):
  switch      : Exp106 build_circuit (4-slot, uniform 4-CZ skeleton)
  paths       : 2-slot coherent routing (c0-sig_a, c1-sig_b); label-dependent
                2-4 CZ — fairness comes from the arm's OWN skeleton-matched
                mixture control, and the depth confound favors paths (shallower),
                i.e. runs AGAINST the switch-wins headline (conservative).
  sw_mix      : switch circuits, control prep pooled {|0>,|1>} (exact classical
                mixture of orders; identical skeletons label-by-label)
  paths_mix   : paths circuits, same prep pooling
  null        : definite order (Exp106 definite=True; control spectator)

Estimators: Exp106 analyze() conventions — pooled conditional R per input, Rbar,
unconditioned D, plus MI(b; C,T). Noiseless tier must reproduce Exp106 theory
(Rbar_switch = 0.5333) and C4589 MI values (0.0488 / 0.0123) = self-validation.
"""
import itertools
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from qiskit import QuantumCircuit, transpile  # noqa: E402
from qiskit.quantum_info import Statevector  # noqa: E402
from exp105_causal_game_feasibility import apply_ctrl_unitary, UNITARIES  # noqa: E402
from exp106_capacity_activation import build_circuit as build_switch  # noqa: E402

PAULIS = ["1", "X", "Y", "Z"]
SHOTS_COH = 1500      # switch / paths / null, per (label, input)
SHOTS_MIX = 750       # mixture arms, per (label, input, prep) — same total per label


def build_paths(a, b, input_bit, ctrl_prep="+"):
    """Coherent path routing: C=0 -> sig_a on T ; C=1 -> sig_b on T.
    ctrl_prep: '+' (H), '0', '1' (mixture pooling preps)."""
    qc = QuantumCircuit(2, 2)
    if input_bit == 1:
        qc.x(1)
    if ctrl_prep == "+":
        qc.h(0)
    elif ctrl_prep == "1":
        qc.x(0)
    apply_ctrl_unitary(qc, a, 0, 1, 0, pad_identity=True)
    apply_ctrl_unitary(qc, b, 0, 1, 1, pad_identity=True)
    qc.barrier()
    qc.h(0)
    qc.measure(0, 0)
    qc.measure(1, 1)
    return qc


def build_switch_prep(a, b, input_bit, ctrl_prep="+"):
    """Switch circuit with overridable control prep (for the mixture arm)."""
    qc = build_switch(a, b, input_bit, definite=False)
    if ctrl_prep == "+":
        return qc
    # rebuild with substituted prep (build_switch hardcodes h(0) as gate index after x)
    qc2 = QuantumCircuit(2, 2)
    if input_bit == 1:
        qc2.x(1)
    if ctrl_prep == "1":
        qc2.x(0)
    started = False
    for inst in qc.data:
        nm = inst.operation.name
        if not started:
            if nm == "h" and inst.qubits[0]._index == 0:
                started = True   # skip the original control prep
            continue
        qc2.append(inst.operation, inst.qubits, inst.clbits)
    return qc2


def pooled_stats(counts_by_key, keys_by_bit):
    """Exp106 analyze() conventions on arbitrary pooling keys."""
    stats = {}
    for bit, keys in keys_by_bit.items():
        pool = {}
        for k in keys:
            for o, v in counts_by_key[k].items():
                pool[o] = pool.get(o, 0) + v
        n = sum(pool.values())
        mz, var = {}, {}
        for c_bit, c_lab in (("0", "plus"), ("1", "minus")):
            n_c = pool.get("0" + c_bit, 0) + pool.get("1" + c_bit, 0)
            z = (pool.get("0" + c_bit, 0) - pool.get("1" + c_bit, 0)) / max(n_c, 1)
            mz[c_lab], var[c_lab] = z, (1 - z * z) / max(n_c, 1)
        stats[bit] = {"R": mz["plus"] - mz["minus"],
                      "varR": var["plus"] + var["minus"],
                      "pool": pool, "n": n}
    Rbar = (stats[0]["R"] - stats[1]["R"]) / 2
    se = float(np.sqrt((stats[0]["varR"] + stats[1]["varR"]) / 4))
    # MI(b ; outcome) from the two pooled dists
    d0 = np.array([stats[0]["pool"].get(o, 0) for o in ("00", "01", "10", "11")],
                  dtype=float)
    d1 = np.array([stats[1]["pool"].get(o, 0) for o in ("00", "01", "10", "11")],
                  dtype=float)
    d0, d1 = d0 / d0.sum(), d1 / d1.sum()
    pout = (d0 + d1) / 2
    mi = 0.0
    for d in (d0, d1):
        for pj, po in zip(d, pout):
            if pj > 1e-15:
                mi += 0.5 * pj * np.log2(pj / po)
    return {"Rbar": Rbar, "SE": se, "mi_bits": float(mi),
            "d0": list(d0), "d1": list(d1),
            "n0": stats[0]["n"], "n1": stats[1]["n"]}


def counts_noiseless(qc, shots):
    meas_free = qc.remove_final_measurements(inplace=False)
    sv = Statevector(meas_free)
    probs = sv.probabilities_dict()
    return {k: v * shots for k, v in probs.items() if v > 1e-12}


def run_tier(backend=None, label="noiseless"):
    counts, cz_hist = {}, {}
    arms = []
    for a, b in itertools.product(PAULIS, repeat=2):
        for bit in (0, 1):
            arms.append((f"sw({a},{b})b{bit}", build_switch(a, b, bit), SHOTS_COH, "switch"))
            arms.append((f"pa({a},{b})b{bit}", build_paths(a, b, bit), SHOTS_COH, "paths"))
            arms.append((f"nu({a},{b})b{bit}", build_switch(a, b, bit, definite=True),
                         SHOTS_COH, "null"))
            for prep in ("0", "1"):
                arms.append((f"sm({a},{b})b{bit}p{prep}",
                             build_switch_prep(a, b, bit, prep), SHOTS_MIX, "sw_mix"))
                arms.append((f"pm({a},{b})b{bit}p{prep}",
                             build_paths(a, b, bit, prep), SHOTS_MIX, "paths_mix"))
    for name, qc, shots, kind in arms:
        if backend is None:
            counts[name] = counts_noiseless(qc, shots)
        else:
            tqc = transpile(qc, backend, optimization_level=3, seed_transpiler=4593)
            n2 = sum(1 for i in tqc.data if i.operation.num_qubits == 2
                     and i.operation.name != "barrier")
            cz_hist.setdefault(kind, {}).setdefault(n2, 0)
            cz_hist[kind][n2] += 1
            counts[name] = backend.run(tqc, shots=int(shots)).result().get_counts()

    out = {}
    lab16 = list(itertools.product(PAULIS, repeat=2))
    for kind, pref, preps in (("switch", "sw", [""]), ("paths", "pa", [""]),
                              ("null", "nu", [""]),
                              ("sw_mix", "sm", ["p0", "p1"]),
                              ("paths_mix", "pm", ["p0", "p1"])):
        keys_by_bit = {bit: [f"{pref}({a},{b})b{bit}{p}" for a, b in lab16
                             for p in preps] for bit in (0, 1)}
        out[kind] = pooled_stats(counts, keys_by_bit)
    print(f"[{label}]")
    for k, v in out.items():
        print(f"  {k:10s} Rbar={v['Rbar']:+.4f}±{v['SE']:.4f}  MI={v['mi_bits']:.4f}b")
    if cz_hist:
        print(f"  CZ histograms: {cz_hist}")
        out["_cz_hist"] = cz_hist
    return out


def main():
    res = {"tier1_noiseless": run_tier(None)}
    r = res["tier1_noiseless"]
    assert abs(r["switch"]["Rbar"] - 0.5333) < 0.01, r["switch"]   # Exp106 anchor
    assert abs(r["switch"]["mi_bits"] - 0.0488) < 0.002            # C4589 anchor
    assert abs(r["paths"]["mi_bits"] - 0.0123) < 0.002             # C4589 anchor
    print("self-validation anchors PASS (Exp106 Rbar + C4589 MI both arms)")
    from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
    from qiskit_aer import AerSimulator
    res["tier2_fakemarrakesh"] = run_tier(
        AerSimulator.from_backend(FakeMarrakesh()), "FakeMarrakesh")
    json.dump(res, open(os.path.join(HERE, "..", "results",
                                     "exp111_feasibility.json"), "w"),
              indent=1, default=float)
    print("wrote results/exp111_feasibility.json")


if __name__ == "__main__":
    main()
