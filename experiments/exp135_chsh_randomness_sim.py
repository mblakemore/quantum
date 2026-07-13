#!/usr/bin/env python3
"""exp135_chsh_randomness_sim.py — CERTIFIED RANDOMNESS ON ONE CHIP: WHAT CHSH
CAN AND CANNOT CERTIFY (Whisper C4676; audit item (d), advisor-scoped.
Substrate claude-opus-4-8).

THE HONEST FRAME (advisor C4676, load-bearing): the device-independent bound
H_min >= 1 - log2(1 + sqrt(2 - S^2/4)) converts CHSH -> entropy ONLY under
NO-SIGNALING between the two measurement sites. On ONE chip (two qubits sharing
control lines, calibration, readout) no-signaling is NOT enforced: a fully
deterministic classical device whose sites talk through the shared control can
output S = 2*sqrt(2) with EXACTLY ZERO entropy. So the DI number is NOT a usable
on-chip certificate. We therefore report:

  (1) WITNESS (frozen, gated): S > 2 at 5 sigma = the device behaves quantumly,
      excluding a no-entanglement classical mimic (null arm S <= 2). Plus the
      Tsirelson honesty check S <= 2*sqrt(2) (exceeding = apparatus error).
  (2) TRUSTED-DEVICE randomness (usable, under an EXPLICIT device-trust
      assumption): if we trust the device performs the modeled projective
      measurements, Born-rule min-entropy is 1 bit / measured qubit; CHSH is the
      health-check that rules out a classical mimic. The certification rests on
      the TRUST, not on Bell.
  (3) DI COUNTERFACTUAL (reported, NOT usable): the min-entropy the DI bound
      WOULD give IF loopholes were closed (space-like separation we do not have),
      labeled what-if / instrument characterization — NOT a certificate.

No "certified bits > 0" gate — that would bake the overclaim into the freeze.

CHSH: |Phi+> = (|00>+|11>)/sqrt2. Alice A0=Z(0), A1=X(pi/2); Bob B0=pi/4,
B1=-pi/4. Measure observable cos(phi)Z+sin(phi)X via Ry(-phi) then Z.
S = E00 + E01 + E10 - E11 (ideal 2*sqrt2).
"""
import json
import math
import os

import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = 20000
A_ANG = {"A0": 0.0, "A1": math.pi / 2}
B_ANG = {"B0": math.pi / 4, "B1": -math.pi / 4}
SETTINGS = [("A0", "B0", +1), ("A0", "B1", +1),
            ("A1", "B0", +1), ("A1", "B1", -1)]


def bell_pair(qc):
    qc.h(0)
    qc.cx(0, 1)


def chsh_circuit(a, b, entangled):
    qc = QuantumCircuit(2, 2)
    if entangled:
        bell_pair(qc)
    else:
        qc.h(0)          # product state |+>|0>: a classical-mimic null
    qc.barrier()
    qc.ry(-A_ANG[a], 0)
    qc.ry(-B_ANG[b], 1)
    qc.measure([0, 1], [0, 1])
    return qc


def corr(counts):
    tot = s = 0
    for k, v in counts.items():
        par = 1 if k.count("1") % 2 == 0 else -1
        s += par * v
        tot += v
    return s / tot, tot


def di_hmin(S):
    """DI min-entropy bound (Pironio 2010) — reported as COUNTERFACTUAL only."""
    if S <= 2:
        return 0.0
    val = 2 - S * S / 4
    if val < 0:
        val = 0.0
    return 1 - math.log2(1 + math.sqrt(val))


def run_S(backend, entangled, layout=None):
    S, corrs = 0.0, {}
    for a, b, sign in SETTINGS:
        qc = chsh_circuit(a, b, entangled)
        tqc = transpile(qc, backend, optimization_level=1,
                        seed_transpiler=4676, initial_layout=layout)
        cts = backend.run(tqc, shots=SHOTS).result().get_counts()
        e, _ = corr(cts)
        corrs[f"{a}{b}"] = e
        S += sign * e
    return S, corrs


def main():
    from qiskit_aer import AerSimulator
    from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
    out = {"tsirelson": 2 * math.sqrt(2)}
    for label, be, lay in (("noiseless", AerSimulator(), None),
                           ("fakemarrakesh",
                            AerSimulator.from_backend(FakeMarrakesh()),
                            [1, 0])):
        S, corrs = run_S(be, True, lay)
        Snull, _ = run_S(be, False, lay)
        out[label] = {"S": S, "corrs": corrs, "S_null": Snull,
                      "di_hmin_counterfactual": di_hmin(S),
                      "trusted_hmin_per_qubit": 1.0}
        print(f"[{label}] S={S:.4f} (Tsirelson {2*math.sqrt(2):.4f}) "
              f"S_null={Snull:.4f} | DI-counterfactual H_min={di_hmin(S):.4f}/use "
              f"(NOT usable on-chip) | trusted Born H_min=1.0/qubit")
    ok = abs(out["noiseless"]["S"] - 2 * math.sqrt(2)) < 0.02 and \
        out["noiseless"]["S_null"] <= 2.01
    print("NOISELESS CHECK (S=2sqrt2, null<=2):", "PASS" if ok else "FAIL")
    out["design_valid"] = bool(ok)
    json.dump(out, open(os.path.join(HERE, "..", "results",
                                     "exp135_feasibility.json"), "w"),
              indent=1, default=float)
    print("wrote results/exp135_feasibility.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
