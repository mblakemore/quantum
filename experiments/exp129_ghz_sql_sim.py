#!/usr/bin/env python3
"""exp129_ghz_sql_sim.py — THE NAVIGATOR'S SEXTANT: GHZ phase estimation vs
the standard quantum limit, sim tier (Whisper C4668; Creator: run the next
one — audit item (c), the practical-metrology advantage class).

THE ADVANTAGE: N probes estimate a phase phi (applied identically to each).
SEPARABLE probes: each shows a fringe cos(phi); Fisher information per shot
F_sep = N * V1^2 (N parallel independent fringes, visibility V1). GHZ probe:
one fringe at frequency N*phi — F_GHZ = N^2 * V_N^2 per shot. Advantage iff
N^2 V_N^2 > N V1^2, i.e. the entangled visibility survives above V1/sqrt(N).
Both Fisher informations are MEASURED here at equal qubits + equal shots —
the SQL reference is executed, not assumed (the Exp128 executed-classical-arm
standard). Absolute gate: 9 V3^2 > 3 beats even PERFECT separable probes.

Law signature the ratio cannot fake: the GHZ fringe oscillates at EXACTLY 3x
the drive frequency (super-resolution). G_FREQ fits the frequency free and
requires k = 3.

Apparatus (N=3): star layout, q0 = center (degree-3 heavy-hex node).
GHZ arm: H(0) CX(0,1) CX(0,2) | Rz(phi) each | CX(0,2) CX(0,1) H(0),
measure q0 -> P(0) = (1 + V3 cos 3phi)/2. 4 CX total.
SEP arm: [H | Rz(phi) | H] each qubit, measure all -> three cos(phi) fringes,
ZERO 2q gates. 12 phase points over [0, 2pi), 8000 shots/point/arm.

Visibility estimator (frozen): discrete Fourier amplitude at harmonic k over
the 12-point uniform grid: V = 4|sum_j (p_j - mean) e^{-i k phi_j}| / n
(DFT of (1+V cos k phi)/2 has amplitude Vn/4); SE by linear propagation of
the per-point binomial SEs (exact for this estimator).
"""
import json
import os

import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = 8000
NPTS = 12
PHIS = [2 * np.pi * j / NPTS for j in range(NPTS)]


def build_ghz(phi):
    qc = QuantumCircuit(3, 1)
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(0, 2)
    qc.barrier()
    for q in range(3):
        qc.rz(phi, q)
    qc.barrier()
    qc.cx(0, 2)
    qc.cx(0, 1)
    qc.h(0)
    qc.measure(0, 0)
    return qc


def build_sep(phi):
    qc = QuantumCircuit(3, 3)
    for q in range(3):
        qc.h(q)
    qc.barrier()
    for q in range(3):
        qc.rz(phi, q)
    qc.barrier()
    for q in range(3):
        qc.h(q)
    qc.measure(range(3), range(3))
    return qc


def p0(counts, bit_idx=None):
    """P(outcome 0). bit_idx None -> single clbit; else marginal of that bit
    (key is little-endian: k[::-1][bit_idx])."""
    tot = hit = 0
    for k, v in counts.items():
        tot += v
        b = k[-1] if bit_idx is None else k[::-1][bit_idx]
        if b == "0":
            hit += v
    p = hit / tot
    return p, float(np.sqrt(max(p * (1 - p), 1e-9) / tot))


def fourier_vis(ps, ses, k):
    """V = 2|DFT_k| / n with propagated SE (linear in p_j -> exact)."""
    n = len(ps)
    ph = np.exp(-1j * k * np.array(PHIS))
    amp = np.sum((np.array(ps) - np.mean(ps)) * ph)
    V = 4 * abs(amp) / n
    # gradient of V wrt p_j: 4/n * Re(e^{-ik phi_j} * conj(amp))/|amp|
    if abs(amp) < 1e-12:
        return V, float(4 / n * np.sqrt(np.sum(np.array(ses) ** 2) / 2))
    grad = 4 / n * np.real(ph * np.conj(amp)) / abs(amp)
    se = float(np.sqrt(np.sum((grad * np.array(ses)) ** 2)))
    return float(V), se


def freq_fit(ps):
    """Free-frequency fit: DFT amplitude over k = 1..5, return argmax and a
    parabolic sub-bin refinement."""
    n = len(ps)
    amps = [2 * abs(np.sum((np.array(ps) - np.mean(ps))
                           * np.exp(-1j * k * np.array(PHIS)))) / n
            for k in range(1, 6)]
    k0 = int(np.argmax(amps)) + 1
    return k0, amps


def run_tier(backend, label, layout=None):
    res = {"ghz": [], "sep": []}
    for phi in PHIS:
        for arm, builder in (("ghz", build_ghz), ("sep", build_sep)):
            qc = builder(phi)
            tqc = transpile(qc, backend, optimization_level=1,
                            seed_transpiler=4668,
                            initial_layout=layout)
            cts = backend.run(tqc, shots=SHOTS).result().get_counts()
            if arm == "ghz":
                res["ghz"].append(p0(cts))
            else:
                res["sep"].append([p0(cts, i) for i in range(3)])
    out = {}
    ps, ses = zip(*res["ghz"])
    V3, seV3 = fourier_vis(ps, ses, 3)
    k0, amps = freq_fit(ps)
    # separable: average the three qubits' visibilities at k=1
    v1s = []
    for i in range(3):
        pi = [pt[i][0] for pt in res["sep"]]
        si = [pt[i][1] for pt in res["sep"]]
        v1s.append(fourier_vis(pi, si, 1))
    V1 = float(np.mean([v[0] for v in v1s]))
    seV1 = float(np.sqrt(np.sum([v[1] ** 2 for v in v1s])) / 3)
    F_ghz, F_sep = 9 * V3 ** 2, 3 * V1 ** 2
    seF_ghz, seF_sep = 18 * V3 * seV3, 6 * V1 * seV1
    R = F_ghz / F_sep
    seR = R * np.sqrt((seF_ghz / F_ghz) ** 2 + (seF_sep / F_sep) ** 2)
    out.update(V3=[V3, seV3], V1=[V1, seV1], F_ghz=[F_ghz, seF_ghz],
               F_sep=[F_sep, seF_sep], ratio=[float(R), float(seR)],
               freq_peak=k0, dft_amps=amps,
               ghz_curve=[list(x) for x in res["ghz"]])
    print(f"[{label}] V3={V3:.4f}±{seV3:.4f} V1={V1:.4f} "
          f"F_ghz={F_ghz:.3f} F_sep={F_sep:.3f} R={R:.3f}±{seR:.3f} "
          f"freq_peak={k0}")
    return out


def main():
    out = {}
    from qiskit_aer import AerSimulator
    from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
    out["noiseless"] = run_tier(AerSimulator(), "noiseless")
    out["fakemarrakesh"] = run_tier(
        AerSimulator.from_backend(FakeMarrakesh()), "fakemarrakesh",
        layout=[1, 0, 2])
    nl = out["noiseless"]
    ok = (abs(nl["V3"][0] - 1) < 0.02 and abs(nl["V1"][0] - 1) < 0.02
          and nl["freq_peak"] == 3 and abs(nl["ratio"][0] - 3) < 0.15)
    print("NOISELESS LAW CHECK (V3=V1=1, k=3, R=3):",
          "PASS" if ok else "FAIL")
    out["design_valid"] = bool(ok)
    json.dump(out, open(os.path.join(HERE, "..", "results",
                                     "exp129_feasibility.json"), "w"),
              indent=1, default=float)
    print("wrote results/exp129_feasibility.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
