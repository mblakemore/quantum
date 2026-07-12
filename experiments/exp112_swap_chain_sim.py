#!/usr/bin/env python3
"""exp112_swap_chain_sim.py — E4 entanglement-swapping chain, sim tiers
(Whisper C4598). CHSH between end qubits after k swap stations, k in {0,1,2}.

Two arms (the Exp110/F90 lesson designed in — feedforward has a measured cost):
  frame  : stations Bell-measure with NO feedforward; CHSH computed BRANCH-RESOLVED
           (per station-outcome branch, the shared state is a known Bell state;
           per-branch sign patterns are FROZEN FROM THE NOISELESS TIER — computed,
           not recalled, C4558 rule)
  active : stations correct via if_test X/Z (validated Exp110 machinery); single
           pooled CHSH
Settings: A in {0, pi/2}, B in {pi/4, -pi/4} (Ry rotations before Z measure);
S = E(a,b) + E(a,b') + E(a',b) - E(a',b'). Noiseless validator: S = 2*sqrt(2)
= 2.8284 for all (arm, k) and every branch sign pattern in {+1,-1}.
"""
import itertools
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, transpile  # noqa: E402

KS = [0, 1, 2]
SETTINGS = [("a", 0.0, "b", np.pi / 4), ("a", 0.0, "bp", -np.pi / 4),
            ("ap", np.pi / 2, "b", np.pi / 4), ("ap", np.pi / 2, "bp", -np.pi / 4)]
SHOTS = 3000


def chain_circuit(k, th_a, th_b, active):
    """k stations: qubits [A, s1a, s1b, s2a, s2b, ..., B]; pairs (A,s1a),(s1b,s2a),
    ..., (skb, B); station i Bell-measures (sia_next...) — layout: 2k+2 qubits."""
    nq = 2 * k + 2
    qr = QuantumRegister(nq)
    crs = [ClassicalRegister(2, f"st{i}") for i in range(k)]
    out = ClassicalRegister(2, "chsh")
    qc = QuantumCircuit(qr, *crs, out)
    # Bell pairs: (0,1), (2,3), ..., (2k, 2k+1)
    for p in range(k + 1):
        qc.h(2 * p)
        qc.cx(2 * p, 2 * p + 1)
    # stations: Bell-measure qubits (1,2), (3,4), ... -> (2i-1, 2i) for i=1..k
    for i in range(1, k + 1):
        m1, m2 = 2 * i - 1, 2 * i
        qc.cx(m1, m2)
        qc.h(m1)
        qc.measure(m1, crs[i - 1][0])   # phase bit
        qc.measure(m2, crs[i - 1][1])   # flip bit
        if active:
            with qc.if_test((crs[i - 1][1], 1)):
                qc.x(nq - 1)
            with qc.if_test((crs[i - 1][0], 1)):
                qc.z(nq - 1)
    # CHSH rotations and measurement on A (q0) and B (q_{nq-1})
    qc.ry(-th_a, 0)
    qc.ry(-th_b, nq - 1)
    qc.measure(0, out[0])
    qc.measure(nq - 1, out[1])
    return qc


def corr_from_counts(chsh_counts):
    n = sum(chsh_counts.values())
    e = sum(v * (1 if k.count("1") % 2 == 0 else -1) for k, v in chsh_counts.items())
    return e / n


def run_tier(backend, label):
    res = {}
    for arm in ("frame", "active"):
        res[arm] = {}
        for k in KS:
            # collect per-setting, per-branch correlations
            eset = {}
            for sa, th_a, sb, th_b in SETTINGS:
                qc = chain_circuit(k, th_a, th_b, active=(arm == "active"))
                tqc = transpile(qc, backend, optimization_level=1,
                                seed_transpiler=4598)
                pub = backend.run(tqc, shots=SHOTS).result()
                counts = pub.get_counts()
                # split joint keys 'chsh stk-1 ... st0' into branch -> chsh counts
                br = {}
                for key, v in counts.items():
                    toks = key.split()
                    chsh, branch = toks[0], " ".join(toks[1:]) or "-"
                    br.setdefault(branch, {}).setdefault(chsh, 0)
                    br[branch][chsh] += v
                eset[(sa, sb)] = {b: (corr_from_counts(c), sum(c.values()))
                                  for b, c in br.items()}
            branches = sorted(set(b for v in eset.values() for b in v))
            res[arm][k] = {"eset": {f"{sa},{sb}": {b: eset[(sa, sb)][b][0]
                                                   for b in eset[(sa, sb)]}
                                    for sa, th_a, sb, th_b in SETTINGS
                                    for sa, sb in [(sa, sb)]},
                           "branch_n": {b: sum(eset[s][b][1] for s in eset
                                               if b in eset[s]) for b in branches}}
    print(f"[{label}] raw per-branch correlations collected "
          f"(frame k=1 branches: {sorted(res['frame'][1]['branch_n'])})")
    return res


def chsh_from(eset_by_setting, signs=None):
    """S with optional per-branch sign matrix {branch: {setting: +-1}}."""
    total, weight = 0.0, 0
    combo = {"a,b": 1, "a,bp": 1, "ap,b": 1, "ap,bp": -1}
    # pooled over branches with per-branch, per-setting signs
    branches = set(b for v in eset_by_setting.values() for b in v)
    Svals = {}
    for b in branches:
        s = 0.0
        for st, e_by_b in eset_by_setting.items():
            sg = signs[b][st] if signs else 1
            s += combo[st] * sg * e_by_b[b]
        Svals[b] = s
    return Svals


def main():
    from qiskit_aer import AerSimulator
    ideal = AerSimulator()
    t1 = run_tier(ideal, "noiseless")
    # derive frozen per-branch signs from noiseless frame arm: sign(e) per setting
    # frozen sign = branch sign RELATIVE to the Phi+ reference pattern (+,+,+,-):
    # raw sign(e) alone double-counts the CHSH combination's own -1 coefficient
    # (validator caught this: k=0 read S=1.45 = 2sqrt2 with one term flipped)
    REF = {"a,b": 1, "a,bp": 1, "ap,b": 1, "ap,bp": -1}
    signs = {}
    for k in KS:
        signs[k] = {}
        for st, e_by_b in t1["frame"][k]["eset"].items():
            for b, e in e_by_b.items():
                signs[k].setdefault(b, {})[st] = (1 if e >= 0 else -1) * REF[st]
    # validator: per-branch S with frozen signs must be 2.8284 everywhere
    ok = True
    for arm in ("frame", "active"):
        for k in KS:
            sv = chsh_from(t1[arm][k]["eset"],
                           signs[k] if arm == "frame" else
                           {b: {st: 1 for st in ("a,b", "a,bp", "ap,b", "ap,bp")}
                            for b in t1[arm][k]["eset"]["a,b"]})
            ns = t1[arm][k]["branch_n"]
            for b, s in sv.items():
                # tolerance = 5*SE(S); per-branch per-setting n = branch_n/4;
                # sign/wiring errors show as ~1.4 jumps, far outside 5*SE
                n_b = max(ns.get(b, 1) / 4, 1)
                tol = 5 * 2 * np.sqrt(0.5 / n_b)
                if abs(s - 2.8284) > tol:
                    print(f"  VALIDATOR MISS {arm} k={k} branch={b}: S={s:.4f} "
                          f"(tol {tol:.3f})")
                    ok = False
    print("VALIDATOR", "PASS: every branch S = 2sqrt2 with frozen signs" if ok
          else "FAIL")
    assert ok
    from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
    t2 = run_tier(AerSimulator.from_backend(FakeMarrakesh()), "FakeMarrakesh")
    # preview pooled S per (arm,k)
    preview = {}
    for arm in ("frame", "active"):
        preview[arm] = {}
        for k in KS:
            sgn = (signs[k] if arm == "frame" else
                   {b: {st: 1 for st in ("a,b", "a,bp", "ap,b", "ap,bp")}
                    for b in t2[arm][k]["eset"]["a,b"]})
            sv = chsh_from(t2[arm][k]["eset"], sgn)
            ns = t2[arm][k]["branch_n"]
            tot = sum(ns.values())
            preview[arm][k] = float(sum(sv[b] * ns.get(b, 0) for b in sv) / tot)
        print(f"  {arm:7s} preview S: " +
              "  ".join(f"k={k}: {preview[arm][k]:.4f}" for k in KS))
    json.dump({"signs_frozen": {str(k): signs[k] for k in KS},
               "preview_S": preview},
              open(os.path.join(HERE, "..", "results", "exp112_feasibility.json"),
                   "w"), indent=1)
    print("wrote results/exp112_feasibility.json")


if __name__ == "__main__":
    main()
