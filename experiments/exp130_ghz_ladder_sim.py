#!/usr/bin/env python3
"""exp130_ghz_ladder_sim.py — THE HEISENBERG LADDER: GHZ Fisher advantage up
the N-rungs (N=2..5), sim tier (Whisper C4669; Creator: next one — the
registered Exp129 follow-up. Substrate: claude-opus-4-8).

CLAIM SHAPE (advisor-frozen, honest side): NOT a scaling-exponent fit
(F_GHZ(N)=N^2 V_N^2 is N^2 times an EXPONENTIAL visibility decay, not a power
law — a log-log exponent over 4 points implies a cleanliness we don't have).
Instead: (a) per-rung, does the GHZ Fisher info beat the EXECUTED separable
reference F_sep(N)=sum_i V_1,i^2 over the N physical qubits; (b) plot R(N)
against the ideal Heisenberg line R=N and LOCATE THE TURNOVER N* where
visibility decay pulls R below N; (c) the F85 CONTRAST — cheap-prep metrology
(2(N-1) CX) vs deep capacity activation (110 CX) that inverted at N=3.
BOTH OUTCOMES PRE-REGISTERED: PERSISTS (F_GHZ(5) > F_GHZ(2) at 5s) or
TURNOVER (some N*<5 maximizes) — either is the finding.

SCOPE (advisor, scope-first): GHZ super-resolution buys per-shot Fisher info
∝ N^2 by SPENDING unambiguous range: cos(N phi) fixes phi only within 2pi/N.
The certified object is LOCAL per-shot sensitivity at fixed bias GIVEN prior
confinement to one fringe — NOT unconditional phase-estimation superiority
(that needs adaptive/multi-N protocols to restore range). Prep CX are not
charged against the probe budget (standard metrological accounting).

Apparatus per N: linear chain q0..q_{N-1}. GHZ: H(0), CX(0,1)..CX(N-2,N-1),
Rz(phi) each, reverse CX ladder, H(0), measure q0 -> P0=(1+V_N cos N phi)/2.
2(N-1) CX. SEP: all 5 qubits [H|Rz|H] independently, ZERO 2q, one 16-pt sweep
gives V_1,i per qubit. NPTS=16 (Nyquist 8 > N=5 with headroom). freq scan
k=1..7.
"""
import json
import os

import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = 4000
NPTS = 16
NMAX = 5
LADDER = [2, 3, 4, 5]
PHIS = [2 * np.pi * j / NPTS for j in range(NPTS)]


def build_ghz(n, phi):
    qc = QuantumCircuit(n, 1)
    qc.h(0)
    for i in range(n - 1):
        qc.cx(i, i + 1)
    qc.barrier()
    for q in range(n):
        qc.rz(phi, q)
    qc.barrier()
    for i in reversed(range(n - 1)):
        qc.cx(i, i + 1)
    qc.h(0)
    qc.measure(0, 0)
    return qc


def build_sep_phi(nq, phi):
    qc = QuantumCircuit(nq, nq)
    for q in range(nq):
        qc.h(q)
    qc.barrier()
    for q in range(nq):
        qc.rz(phi, q)
    qc.barrier()
    for q in range(nq):
        qc.h(q)
    qc.measure(range(nq), range(nq))
    return qc


def p0(counts, bit_idx=None):
    tot = hit = 0
    for k, v in counts.items():
        tot += v
        b = k[-1] if bit_idx is None else k[::-1][bit_idx]
        if b == "0":
            hit += v
    p = hit / tot
    return p, float(np.sqrt(max(p * (1 - p), 1e-9) / tot))


def fourier_vis(ps, ses, k):
    """V = 4|DFT_k|/n (DFT of (1+V cos k phi)/2 has amplitude Vn/4);
    SE by exact linear propagation of binomial errors."""
    n = len(ps)
    ph = np.exp(-1j * k * np.array(PHIS))
    amp = np.sum((np.array(ps) - np.mean(ps)) * ph)
    V = 4 * abs(amp) / n
    if abs(amp) < 1e-12:
        return V, float(4 / n * np.sqrt(np.sum(np.array(ses) ** 2) / 2))
    grad = 4 / n * np.real(ph * np.conj(amp)) / abs(amp)
    se = float(np.sqrt(np.sum((grad * np.array(ses)) ** 2)))
    return float(V), se


def freq_scan(ps):
    """DFT amplitude over k=1..7, return argmax and the amp list."""
    n = len(ps)
    amps = [2 * abs(np.sum((np.array(ps) - np.mean(ps))
                           * np.exp(-1j * k * np.array(PHIS)))) / n
            for k in range(1, NPTS // 2)]
    k0 = int(np.argmax(amps)) + 1
    return k0, amps


def run_tier(backend, label, layout=None):
    # SEP: one sweep, all NMAX qubits
    sep = []
    for phi in PHIS:
        qc = build_sep_phi(NMAX, phi)
        tqc = transpile(qc, backend, optimization_level=1,
                        seed_transpiler=4669,
                        initial_layout=layout[:NMAX] if layout else None)
        cts = backend.run(tqc, shots=SHOTS).result().get_counts()
        sep.append([p0(cts, i) for i in range(NMAX)])
    V1 = []
    for i in range(NMAX):
        pi = [pt[i][0] for pt in sep]
        si = [pt[i][1] for pt in sep]
        V1.append(fourier_vis(pi, si, 1))
    out = {"V1": V1, "rungs": {}}
    for n in LADDER:
        curve = []
        for phi in PHIS:
            qc = build_ghz(n, phi)
            tqc = transpile(qc, backend, optimization_level=1,
                            seed_transpiler=4669,
                            initial_layout=layout[:n] if layout else None)
            cts = backend.run(tqc, shots=SHOTS).result().get_counts()
            curve.append(p0(cts))
        ps, ses = zip(*curve)
        VN, seVN = fourier_vis(ps, ses, n)
        k0, amps = freq_scan(ps)
        F_ghz = n ** 2 * VN ** 2
        seF_ghz = 2 * n ** 2 * VN * seVN
        F_sep = float(np.sum([V1[i][0] ** 2 for i in range(n)]))
        seF_sep = float(np.sqrt(np.sum(
            [(2 * V1[i][0] * V1[i][1]) ** 2 for i in range(n)])))
        R = F_ghz / F_sep
        seR = R * np.sqrt((seF_ghz / F_ghz) ** 2 + (seF_sep / F_sep) ** 2)
        out["rungs"][n] = {
            "VN": [VN, seVN], "F_ghz": [F_ghz, seF_ghz],
            "F_sep": [F_sep, seF_sep], "R": [float(R), float(seR)],
            "R_ideal": n, "freq_peak": k0, "freq_amps": amps}
        print(f"[{label}] N={n} ({2*(n-1)}CX) VN={VN:.4f} "
              f"F_ghz={F_ghz:.2f} F_sep={F_sep:.2f} R={R:.3f} "
              f"(ideal {n}) peak_k={k0}")
    fg = {n: out["rungs"][n]["F_ghz"][0] for n in LADDER}
    nstar = max(fg, key=fg.get)
    out["Fghz_argmax"] = nstar
    out["persists"] = fg[5] > fg[2]
    print(f"[{label}] F_ghz argmax N*={nstar} | "
          f"persists(F5>F2)={out['persists']}")
    return out


def main():
    out = {}
    from qiskit_aer import AerSimulator
    from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
    out["noiseless"] = run_tier(AerSimulator(), "noiseless")
    out["fakemarrakesh"] = run_tier(
        AerSimulator.from_backend(FakeMarrakesh()), "fakemarrakesh",
        layout=[1, 0, 2, 3, 4])
    nl = out["noiseless"]
    ok = all(abs(nl["rungs"][n]["VN"][0] - 1) < 0.03
             and nl["rungs"][n]["freq_peak"] == n for n in LADDER)
    ok &= all(abs(nl["rungs"][n]["R"][0] - n) < 0.15 for n in LADDER)
    print("NOISELESS LAW CHECK (VN=1, peak=N, R=N all rungs):",
          "PASS" if ok else "FAIL")
    out["design_valid"] = bool(ok)
    json.dump(out, open(os.path.join(HERE, "..", "results",
                                     "exp130_feasibility.json"), "w"),
              indent=1, default=float)
    print("wrote results/exp130_feasibility.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
