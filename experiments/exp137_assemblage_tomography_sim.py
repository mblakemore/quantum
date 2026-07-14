#!/usr/bin/env python3
"""exp137_assemblage_tomography_sim.py — ASSEMBLAGE TOMOGRAPHY -> rigorous 1SDI
randomness, sim tier (Whisper C4680; feeds tools/sdp_randomness.py, the capstone
of the trust-ladder arc. Substrate claude-opus-4-8).

Exp136 measured matched-basis correlations only -> Werner-MODEL estimate. This
collects the full ASSEMBLAGE: for each of Alice's (untrusted) settings x in
{X,Y,Z} and outcomes a=+/-1, fully tomograph Bob's (trusted) conditional state
via Bob measurements t in {X,Y,Z}. 3x3 = 9 circuits. Reconstruct
sigma_{a|x} = p(a|x) * (I + sum_t <t>_{a|x} sigma_t)/2, then run the exact SDP
(sdp_randomness.certify) for the RIGOROUS per-device 1SDI H_min (no Werner model).

Bell |Phi+>. Alice setting x: rotate her qubit to measure Pauli-x, outcome a.
Bob tomo t: rotate his qubit to measure Pauli-t, outcome b. Both measured in Z.
"""
import itertools
import json
import math
import os
import sys

import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools"))
from sdp_randomness import (I2, SX, SY, SZ, cjwr_S,  # noqa: E402
                            guessing_probability, hmin)

SHOTS = 20000
AXES = ["X", "Y", "Z"]
ROT = {"X": [("h",)], "Y": [("sdg",), ("h",)], "Z": []}
PAULI = {"X": SX, "Y": SY, "Z": SZ}
SIGN = {"X": 1, "Y": -1, "Z": 1}         # |Phi+> steering-functional signs


def tomo_circuit(x_alice, t_bob, entangled):
    qc = QuantumCircuit(2, 2)
    if entangled:
        qc.h(0)
        qc.cx(0, 1)
    else:
        qc.h(0)                          # product |+>|0>
    qc.barrier()
    for g in ROT[x_alice]:               # Alice (q0, untrusted) setting
        getattr(qc, g[0])(0)
    for g in ROT[t_bob]:                 # Bob (q1, trusted) tomography
        getattr(qc, g[0])(1)
    qc.measure([0, 1], [0, 1])
    return qc


def reconstruct_assemblage(counts_by_xt):
    """counts_by_xt[(x,t)] = {bitstring: n} (bit order q0=Alice, q1=Bob).
    Returns assemblage {(a,x): 2x2}. a in {+1,-1}."""
    asm = {}
    for x in AXES:
        # p(a|x): Alice marginal (average over Bob tomo t, should be t-indep)
        pa = {+1: 0.0, -1: 0.0}
        for t in AXES:
            c = counts_by_xt[(x, t)]
            tot = sum(c.values())
            for k, n in c.items():
                a = +1 if k[::-1][0] == "0" else -1   # q0 = Alice
                pa[a] += n / tot / len(AXES)
        # <t>_{a|x} conditional Bob expectation
        for a in (+1, -1):
            r = {}
            for t in AXES:
                c = counts_by_xt[(x, t)]
                tot = sum(c.values())
                num = 0.0
                den = 0.0
                for k, n in c.items():
                    aa = +1 if k[::-1][0] == "0" else -1
                    bb = +1 if k[::-1][1] == "0" else -1
                    if aa == a:
                        num += bb * n / tot
                        den += n / tot
                r[t] = num / den if den > 1e-9 else 0.0
            bloch = r["X"] * SX + r["Y"] * SY + r["Z"] * SZ
            asm[(a, x)] = pa[a] * (I2 + bloch) / 2
    return asm


def ns_violation(asm):
    """max ||sum_a sigma_{a|x} - rho_bar|| over x (no-signaling check)."""
    rhos = {x: sum(asm[(a, x)] for a in (+1, -1)) for x in AXES}
    rbar = sum(rhos.values()) / len(AXES)
    return max(float(np.linalg.norm(rhos[x] - rbar)) for x in AXES)


def psd_violation(asm):
    """max(-min eigenvalue, 0) over all sigma_{a|x}."""
    v = 0.0
    for m in asm.values():
        ev = np.linalg.eigvalsh((m + m.conj().T) / 2)
        v = max(v, float(-ev.min()))
    return v


def project_valid(asm):
    """Nearest VALID assemblage (PSD + no-signaling) by SDP: minimize
    sum ||sigma - sigma_raw||_F^2 s.t. sigma_{a|x} >= 0 and sum_a sigma_{a|x}
    independent of x. Guarantees the randomness SDP is feasible (exact validity),
    replacing the non-commuting PSD-clip/NS-shift heuristic."""
    import cvxpy as cp
    keys = list(asm.keys())
    v = {k: cp.Variable((2, 2), hermitian=True) for k in keys}
    cons = [v[k] >> 0 for k in keys]
    marg = {x: sum(v[(a, x)] for a in (+1, -1)) for x in AXES}
    for x in AXES[1:]:
        cons.append(marg[x] == marg[AXES[0]])
    obj = cp.Minimize(sum(cp.sum_squares(v[k] - asm[k]) for k in keys))
    cp.Problem(obj, cons).solve(solver=cp.SCS, eps=1e-8, max_iters=50000)
    return {k: np.array(v[k].value) for k in keys}


def run(backend, entangled, layout=None):
    counts = {}
    for x in AXES:
        for t in AXES:
            qc = tomo_circuit(x, t, entangled)
            tqc = transpile(qc, backend, optimization_level=1,
                            seed_transpiler=4680, initial_layout=layout)
            counts[(x, t)] = backend.run(tqc, shots=SHOTS).result().get_counts()
    asm_raw = reconstruct_assemblage(counts)
    nsv, psv = ns_violation(asm_raw), psd_violation(asm_raw)
    asm = project_valid(asm_raw)
    S3 = cjwr_S(asm, {"X": (1, 0, 0), "Y": (0, 1, 0), "Z": (0, 0, 1)},
                signs=SIGN)
    pg, st = guessing_probability(asm, "Z")
    return {"S3": S3, "P_guess": pg, "H_min": hmin(pg),
            "ns_violation": nsv, "psd_violation": psv, "solver": st}


def main():
    from qiskit_aer import AerSimulator
    from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
    out = {}
    for label, be, lay in (("noiseless", AerSimulator(), None),
                           ("fakemarrakesh",
                            AerSimulator.from_backend(FakeMarrakesh()),
                            [1, 0])):
        main_r = run(be, True, lay)
        null_r = run(be, False, lay)
        out[label] = {"main": main_r, "null": null_r}
        print(f"[{label}] MAIN S3={main_r['S3']:.4f} H_min={main_r['H_min']:.4f} "
              f"bits (NSviol={main_r['ns_violation']:.4f} "
              f"PSDviol={main_r['psd_violation']:.4f}) | "
              f"NULL S3={null_r['S3']:.4f} H_min={null_r['H_min']:.4f}")
    ok = out["noiseless"]["main"]["H_min"] > 0.90 and \
        out["noiseless"]["null"]["H_min"] < 0.05
    print("NOISELESS CHECK (main H_min~1, null H_min~0):",
          "PASS" if ok else "FAIL")
    out["design_valid"] = bool(ok)
    json.dump(out, open(os.path.join(HERE, "..", "results",
                                     "exp137_feasibility.json"), "w"),
              indent=1, default=float)
    print("wrote results/exp137_feasibility.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
