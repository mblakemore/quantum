#!/usr/bin/env python3
"""exp114_purification_sim.py — entanglement purification, sim tier
(Whisper C4605, horizons P2 — the network stack's missing layer, confirmed
white space in 115+ findings).

BBPSSW recurrence primitive: two noisy Bell pairs -> bilateral CX -> Z-measure
the sacrificial pair -> keep the survivor iff outcomes AGREE. Self-referenced
frozen gate at prereg: CHSH_purified > CHSH_raw at 5 sigma, same window.

DESIGN PROBLEM this tier solves: our raw pairs are too clean (CHSH ~2.73) for
purification to demonstrate gain — the protocol's own 2 extra CZ would eat the
margin. So noise is INJECTED at a known rate p (single-qubit Pauli twirl on one
half of each pair, exact pooled twirl: deterministic Pauli labels at weighted
shots, our standard trick). This tier sweeps p, maps the purification gain
curve, and picks p* where gain is maximal-and-measurable. Noiseless validator:
at p=0, purified == raw == 2*sqrt(2) (protocol does no harm ideally); gain > 0
for p in the working range (protocol does good).
"""
import itertools
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, transpile  # noqa: E402

SETTINGS = [("a,b", 0.0, np.pi / 4), ("a,bp", 0.0, -np.pi / 4),
            ("ap,b", np.pi / 2, np.pi / 4), ("ap,bp", np.pi / 2, -np.pi / 4)]
COMBO = {"a,b": 1, "a,bp": 1, "ap,b": 1, "ap,bp": -1}
SHOTS = 3000
PAULIS = ["I", "X", "Y", "Z"]


def apply_pauli(qc, q, p):
    if p == "X":
        qc.x(q)
    elif p == "Y":
        qc.y(q)
    elif p == "Z":
        qc.z(q)


def circuit(arm, th_a, th_b, noise_label=("I", "I")):
    """arm 'raw': one noisy pair, CHSH directly. arm 'purified': two noisy pairs,
    BBPSSW, CHSH on survivor + coincidence register.
    Qubit order (linear-chain friendly): B2-A2-A1-B1 = q0,q1,q2,q3 for purified;
    (A1,B1)=(q0,q1) for raw. noise_label = Pauli on the B half of each pair."""
    if arm == "raw":
        qc = QuantumCircuit(2, 1 + 1)
        qc.h(0)
        qc.cx(0, 1)
        apply_pauli(qc, 1, noise_label[0])
        qc.ry(-th_a, 0)
        qc.ry(-th_b, 1)
        qc.measure(0, 0)
        qc.measure(1, 1)
        return qc
    qr = QuantumRegister(4)          # 0=B2, 1=A2, 2=A1, 3=B1
    coin = ClassicalRegister(2, "coin")
    chsh = ClassicalRegister(2, "chsh")
    qc = QuantumCircuit(qr, coin, chsh)
    qc.h(2); qc.cx(2, 3)             # pair 1 (A1,B1) adjacent
    qc.h(1); qc.cx(1, 0)             # pair 2 (A2,B2) adjacent
    apply_pauli(qc, 3, noise_label[0])
    apply_pauli(qc, 0, noise_label[1])
    qc.cx(2, 1)                      # bilateral CX: A1->A2 (adjacent)
    qc.cx(3, 0)                      # B1->B2 (NON-adjacent on a line: cost audited)
    qc.measure(1, coin[0])
    qc.measure(0, coin[1])
    qc.ry(-th_a, 2)
    qc.ry(-th_b, 3)
    qc.measure(2, chsh[0])
    qc.measure(3, chsh[1])
    return qc


def chsh_from_run(backend, arm, p_noise, seed=4605):
    """Exact pooled twirl: weights (1-p+p/4) for I, p/4 for X/Y/Z per noised qubit."""
    labels1 = [("I",), ("X",), ("Y",), ("Z",)]
    w1 = {("I",): 1 - 3 * p_noise / 4, ("X",): p_noise / 4,
          ("Y",): p_noise / 4, ("Z",): p_noise / 4}
    if arm == "raw":
        labels = [(l[0],) for l in labels1]
        weights = {(l[0],): w1[l] for l in labels1}
        labels = [(a, "I") for (a,) in labels]
        weights = {(a, "I"): weights[(a,)] for (a, _) in labels}
    else:
        labels = list(itertools.product(PAULIS, PAULIS))
        weights = {(a, b): w1[(a,)] * w1[(b,)] for a, b in labels}
    S, var_sum, coin_keep, coin_tot = 0.0, 0.0, 0, 0
    for skey, th_a, th_b in SETTINGS:
        num, den = 0.0, 0.0
        for lab in labels:
            w = weights[lab]
            if w < 1e-6:
                continue
            qc = circuit(arm, th_a, th_b, noise_label=lab)
            tqc = transpile(qc, backend, optimization_level=1, seed_transpiler=seed)
            shots = max(int(round(SHOTS * w)), 1)
            counts = backend.run(tqc, shots=shots).result().get_counts()
            for key, v in counts.items():
                toks = key.split()
                if arm == "purified":
                    ch, co = toks[0], toks[1]
                    coin_tot += v
                    if co[0] != co[1]:
                        continue        # coincidence post-selection: keep agree
                    coin_keep += v
                else:
                    ch = toks[0] + toks[1] if len(toks) > 1 else key.replace(" ", "")
                e = 1 if ch.count("1") % 2 == 0 else -1
                num += v * e
                den += v
        E = num / den
        S += COMBO[skey] * E
        var_sum += (1 - E * E) / den
    return S, float(np.sqrt(var_sum)), (coin_keep / coin_tot if coin_tot else 1.0)


def main():
    from qiskit_aer import AerSimulator
    ideal = AerSimulator()
    out = {}
    # noiseless validator at p=0
    s_raw, se_raw, _ = chsh_from_run(ideal, "raw", 0.0)
    s_pur, se_pur, keep = chsh_from_run(ideal, "purified", 0.0)
    print(f"[noiseless p=0] raw S={s_raw:.4f} purified S={s_pur:.4f} keep={keep:.3f}")
    assert abs(s_raw - 2.8284) < 0.1 and abs(s_pur - 2.8284) < 0.1
    print("VALIDATOR PASS: protocol does no harm at p=0 (both = 2sqrt2)")
    # gain curve
    for p in (0.10, 0.20, 0.30, 0.40):
        r = chsh_from_run(ideal, "raw", p)
        u = chsh_from_run(ideal, "purified", p)
        gain = u[0] - r[0]
        out[str(p)] = {"raw": r[0], "purified": u[0], "gain": gain,
                       "keep_rate": u[2]}
        print(f"[ideal p={p}] raw={r[0]:.4f} purified={u[0]:.4f} "
              f"GAIN={gain:+.4f} keep={u[2]:.3f}")
    json.dump(out, open(os.path.join(HERE, "..", "results",
                                     "exp114_gain_curve.json"), "w"), indent=1)
    print("wrote results/exp114_gain_curve.json (FakeMarrakesh tier at freeze, "
          "with p* chosen from this curve)")


if __name__ == "__main__":
    main()
