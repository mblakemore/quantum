#!/usr/bin/env python3
"""exp132_dfs_cloak_sim.py — THE CLOAKING DEVICE: a decoherence-free-subspace
logical qubit raced against a bare qubit down the delay ladder, sim tier
(Whisper C4671, Horizons-3 H3; substrate claude-opus-4-8).

THE IDEA: encode one logical qubit in the DFS {|01>,|10>} of two physical
qubits. Under COLLECTIVE dephasing (both qubits see the same Z noise) both
basis states pick up the SAME phase -> a global phase -> the logical
coherence is UNTOUCHED. Only DIFFERENTIAL (independent) dephasing decoheres
it. So the DFS logical qubit outlives a bare qubit IFF the hardware's
dephasing is collective enough. Both outcomes are findings (cloak works /
noise too independent) — same discipline as F85/F130.

THE BEAUTIFUL CONFOUND-BREAKER: fake backends model INDEPENDENT noise, so the
fake CANNOT show a DFS benefit (ratio ~ 1). A hardware ratio > 1 is therefore
itself evidence of REAL correlated noise the vendor model misses — this ties
into the campaign's noise-structure arc (X-basis cleaner, Z-biased CZ noise).

PHASE-BLIND coherence (F100 law is standing): logical Pauli X_L = |0L><1L|+hc
= (XX+YY)/2, Y_L = (XY-YX)/2 on the {|01>,|10>} code. Coherence magnitude
C_L = sqrt(<X_L>^2 + <Y_L>^2) is invariant under BOTH a global collective
phase AND a differential ROTATION — it decays only under true dephasing. Bare
qubit: C_b = sqrt(<X>^2 + <Y>^2), the standard phase-blind Ramsey |V|.

Prep: logical |+L> = (|01>+|10>)/sqrt2 via X(q1) H(q0) CX(q0,q1). Bare |+>.
Idle: delay ladder. Normalize each curve to its own t=0 (removes prep-error
offset — the fair comparison is decay RATE, not absolute |V|).

Correlators measured per delay: logical {XX,YY,XY,YX} (4 pubs), bare {X,Y}
(2 pubs). Delays chosen in the T2 decay band.
"""
import json
import os

import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = 8000
DELAYS_US = [0, 30, 60, 120]          # microseconds of idle
LOG_SETTINGS = ["XX", "YY", "XY", "YX"]
BARE_SETTINGS = ["X", "Y"]
ROT = {"X": [("h",)], "Y": [("sdg",), ("h",)]}


def logical_circuit(setting, delay_us, dt=None):
    qc = QuantumCircuit(2, 2)
    qc.x(1)
    qc.h(0)
    qc.cx(0, 1)                        # (|01>+|10>)/sqrt2
    qc.barrier()
    if delay_us > 0:
        qc.delay(delay_us, unit="us")
        qc.delay(delay_us, unit="us")  # per qubit (0 and 1)
    qc.barrier()
    for i, b in enumerate(setting):
        for g in ROT[b]:
            getattr(qc, g[0])(i)
    qc.measure([0, 1], [0, 1])
    return qc


def bare_circuit(setting, delay_us):
    qc = QuantumCircuit(1, 1)
    qc.h(0)
    qc.barrier()
    if delay_us > 0:
        qc.delay(delay_us, unit="us")
    qc.barrier()
    for g in ROT[setting]:
        getattr(qc, g[0])(0)
    qc.measure(0, 0)
    return qc


def echo_circuit(setting, delay_us):
    """Active refocusing: Hahn echo (X at midpoint). Refocuses low-frequency
    dephasing -> extends coherence IF the noise is quasi-static/independent.
    The active-protection foil to the DFS's passive protection."""
    qc = QuantumCircuit(1, 1)
    qc.h(0)
    qc.barrier()
    if delay_us > 0:
        qc.delay(delay_us // 2, unit="us")
        qc.x(0)
        qc.delay(delay_us // 2, unit="us")
    qc.barrier()
    for g in ROT[setting]:
        getattr(qc, g[0])(0)
    qc.measure(0, 0)
    return qc


def corr2(counts):
    """<Z1 Z2> parity expectation from 2-bit counts."""
    tot = s = 0
    for k, v in counts.items():
        b = k[-2:]
        par = 1 if b.count("1") % 2 == 0 else -1
        s += par * v
        tot += v
    return s / tot


def exp1(counts):
    tot = s = 0
    for k, v in counts.items():
        s += (1 if k[-1] == "0" else -1) * v
        tot += v
    return s / tot


def logical_coherence(cvals):
    """cvals: dict setting->correlator. X_L=(XX+YY)/2, Y_L=(XY-YX)/2."""
    XL = (cvals["XX"] + cvals["YY"]) / 2
    YL = (cvals["XY"] - cvals["YX"]) / 2
    return float(np.hypot(XL, YL))


def _single_arm(backend, builder, settings, layout, extractor):
    vals = []
    for d in DELAYS_US:
        sv = {}
        for s in settings:
            qc = builder(s, d)
            tqc = transpile(qc, backend, optimization_level=1,
                            seed_transpiler=4671, initial_layout=layout)
            cts = backend.run(tqc, shots=SHOTS).result().get_counts()
            sv[s] = extractor(cts)
        vals.append(sv)
    return vals


def run_tier(backend, label, layout=None):
    lay2 = layout[:2] if layout else None
    lay1 = [layout[0]] if layout else None
    logC = [logical_coherence(sv) for sv in
            _single_arm(backend, logical_circuit, LOG_SETTINGS, lay2, corr2)]
    bareC = [float(np.hypot(sv["X"], sv["Y"])) for sv in
             _single_arm(backend, bare_circuit, BARE_SETTINGS, lay1, exp1)]
    echoC = [float(np.hypot(sv["X"], sv["Y"])) for sv in
             _single_arm(backend, echo_circuit, BARE_SETTINGS, lay1, exp1)]
    norm = lambda c: [v / c[0] for v in c]
    print(f"[{label}] delays(us)={DELAYS_US}")
    print(f"[{label}] logical C={[round(c,4) for c in logC]} norm={[round(c,3) for c in norm(logC)]}")
    print(f"[{label}] bare    C={[round(c,4) for c in bareC]} norm={[round(c,3) for c in norm(bareC)]}")
    print(f"[{label}] echo    C={[round(c,4) for c in echoC]} norm={[round(c,3) for c in norm(echoC)]}")
    return {"delays_us": DELAYS_US, "logical": logC, "bare": bareC,
            "echo": echoC, "logical_norm": norm(logC),
            "bare_norm": norm(bareC), "echo_norm": norm(echoC)}


def fit_decay(norm, delays):
    """T2 from exp fit of normalized coherence; guard against <=0."""
    xs = np.array(delays, float)
    ys = np.array([max(v, 1e-3) for v in norm])
    a, b = np.polyfit(xs, np.log(ys), 1)
    return float(-1 / a) if a < 0 else float("inf")


def main():
    out = {}
    from qiskit_aer import AerSimulator
    from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
    # noiseless: verify phase-blind estimator (C_L=1 all delays, C_b=1)
    nl = run_tier(AerSimulator(), "noiseless")
    ok = all(abs(c - 1) < 0.05 for c in nl["logical"]) and \
        all(abs(c - 1) < 0.05 for c in nl["bare"]) and \
        all(abs(c - 1) < 0.05 for c in nl["echo"])
    out["noiseless"] = nl
    fk = run_tier(AerSimulator.from_backend(FakeMarrakesh()),
                  "fakemarrakesh", layout=[1, 0])
    t2_log = fit_decay(fk["logical_norm"], DELAYS_US)
    t2_bare = fit_decay(fk["bare_norm"], DELAYS_US)
    t2_echo = fit_decay(fk["echo_norm"], DELAYS_US)
    out["fakemarrakesh"] = {**fk, "T2_logical_us": t2_log,
                            "T2_bare_us": t2_bare, "T2_echo_us": t2_echo,
                            "dfs_ratio": t2_log / t2_bare,
                            "echo_ratio": t2_echo / t2_bare}
    print(f"[fake] T2_log={t2_log:.1f} T2_bare={t2_bare:.1f} "
          f"T2_echo={t2_echo:.1f} | DFS_ratio={t2_log/t2_bare:.3f} "
          f"echo_ratio={t2_echo/t2_bare:.3f}")
    print("  (fake models MEMORYLESS+INDEPENDENT noise -> both ratios ~<=1; "
          "real hardware reveals collective(DFS) + low-freq(echo) components)")
    print("PHASE-BLIND ESTIMATOR CHECK (noiseless C=1 all delays):",
          "PASS" if ok else "FAIL")
    out["design_valid"] = bool(ok)
    json.dump(out, open(os.path.join(HERE, "..", "results",
                                     "exp132_feasibility.json"), "w"),
              indent=1, default=float)
    print("wrote results/exp132_feasibility.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
