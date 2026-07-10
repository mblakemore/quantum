#!/usr/bin/env python3
"""
Exp106 — Capacity activation: classical information through TWO completely
depolarizing channels in a superposition of orders (Whisper C4529).

Theory (Ebler-Salek-Chiribella, PRL 120, 120502 (2018)): a completely depolarizing
qubit channel transmits ZERO information; so does any definite-order (or classically
mixed / dynamically ordered) composition of two of them. In the quantum switch with
control |+>, information survives. Exact targets (derived independently C4529 and
consistent with the paper's ~0.049-bit Holevo value):
    P(control=+) = 5/8 = 0.625, input-INDEPENDENT
    target | control=+  ->  (rho + 2I)/5   (retains rho with weight +1/5)
    target | control=-  ->  (2I - rho)/3   (retains rho with weight -1/3)
    discriminator  R(b) := <Z_t | c=+> - <Z_t | c=->  =  +8/15 for input |0>,
                                                        -8/15 for input |1>
    symmetrized    Rbar := (R(0) - R(1))/2  =  8/15 ~ 0.5333 ;  causal value = 0 EXACTLY
    mutual information I(B; C,T) = 0.0489 bits (secondary, reported not graded)

Implementation: full depolarizing channel = uniform mixture of the 4 Paulis
(Kraus sigma_i/2). switch(N1,N2) with mixed-unitary channels decomposes incoherently
over Pauli labels, so running the 16 (i,j) switch-of-Pauli circuits at equal shots
and POOLING counts is the EXACT channel twirl (deterministic weighting, Exp105
precedent). Circuits reuse the Exp105 padded template (apply_ctrl_unitary,
barrier-fenced controlled-1 pads) -> every switch circuit is the identical 4-CZ
skeleton, only locals differ (pair-independent process, C4525 requirement).
Null arm: same Pauli pairs applied in DEFINITE order (control spectator).

Modes: --sim (noiseless gates) | --fake (FakeMarrakesh feasibility) — both FREE.
Submit/grade live in run_exp106_submit.py / grade_exp106.py.
"""
import itertools
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

from exp105_causal_game_feasibility import apply_ctrl_unitary, UNITARIES

PAULIS = ["1", "X", "Y", "Z"]
SHOTS_GAME = 1500
SHOTS_SENT = 2000
R_WIN_FLOOR = 0.10        # frozen: WIN needs Rbar_switch - 5SE > max(0.10, null band)
NULL_BAND = 0.10          # frozen: |Rbar_null| + 5SE must stay below this, else NO-TEST
SENT_MIN_DISC = 1.60      # inherited from Exp105


def build_circuit(a_name, b_name, input_bit, definite=False):
    """Switch (or definite-order) of Paulis with input prep and 2-bit readout.
    q0 = control (X-basis readout, clbit 0), q1 = target (Z-basis readout, clbit 1)."""
    qc = QuantumCircuit(2, 2)
    if input_bit == 1:
        qc.x(1)
    qc.h(0)
    if not definite:
        apply_ctrl_unitary(qc, a_name, 0, 1, 0, pad_identity=True)
        apply_ctrl_unitary(qc, b_name, 0, 1, 1, pad_identity=True)
        qc.barrier()
        apply_ctrl_unitary(qc, b_name, 0, 1, 0, pad_identity=False)
        apply_ctrl_unitary(qc, a_name, 0, 1, 1, pad_identity=False)
    else:
        if a_name != "1":
            qc.unitary(UNITARIES[a_name], [1], label=a_name)
        if b_name != "1":
            qc.unitary(UNITARIES[b_name], [1], label=b_name)
    qc.barrier()
    qc.h(0)
    qc.measure(0, 0)
    qc.measure(1, 1)
    return qc


def all_entries():
    """PUB entries (label, kind, a, b, input_bit, shots) — switch + null, 16 pairs x 2 inputs."""
    ent = []
    for a, b in itertools.product(PAULIS, repeat=2):
        for bit in (0, 1):
            ent.append((f"sw({a},{b})b{bit}", "switch", a, b, bit, SHOTS_GAME))
            ent.append((f"nu({a},{b})b{bit}", "null", a, b, bit, SHOTS_GAME))
    return ent


def analyze(counts_by_label):
    """Pooled conditional statistics per (kind, input). Count keys: 'tc' (clbit1 clbit0);
    control '+' <-> c-bit '0'; target Z: t-bit 0 -> +1, 1 -> -1."""
    out = {}
    for kind in ("switch", "null"):
        stats = {}
        for bit in (0, 1):
            pool = {}
            for a, b in itertools.product(PAULIS, repeat=2):
                lab = ("sw" if kind == "switch" else "nu") + f"({a},{b})b{bit}"
                for k, v in counts_by_label[lab].items():
                    pool[k] = pool.get(k, 0) + v
            n = sum(pool.values())
            n_plus = pool.get("00", 0) + pool.get("10", 0)
            p_plus = n_plus / n
            mz = {}
            var = {}
            for c_bit, c_lab in (("0", "plus"), ("1", "minus")):
                n_c = pool.get("0" + c_bit, 0) + pool.get("1" + c_bit, 0)
                z = (pool.get("0" + c_bit, 0) - pool.get("1" + c_bit, 0)) / max(n_c, 1)
                mz[c_lab] = z
                var[c_lab] = (1 - z * z) / max(n_c, 1)
            R = mz["plus"] - mz["minus"]
            stats[bit] = {"p_plus": p_plus, "R": R,
                          "varR": var["plus"] + var["minus"], "n": n}
        Rbar = (stats[0]["R"] - stats[1]["R"]) / 2
        se = float(np.sqrt((stats[0]["varR"] + stats[1]["varR"]) / 4))
        # UNCONDITIONED target signal D = (<Z_t>_b0 - <Z_t>_b1)/2 — the correct NULL
        # observable (null control is a |+> spectator: conditional-on-minus starves).
        # Theory: D = 0 for the null AND for the switch (information lives ONLY in the
        # control-target correlation) — dual role: null integrity gate + switch signature.
        dz, dvar = [], []
        for bit in (0, 1):
            pool = {}
            for a, b in itertools.product(PAULIS, repeat=2):
                lab = ("sw" if kind == "switch" else "nu") + f"({a},{b})b{bit}"
                for k, v in counts_by_label[lab].items():
                    pool[k] = pool.get(k, 0) + v
            n = sum(pool.values())
            z = (sum(v for k, v in pool.items() if k[0] == "0")
                 - sum(v for k, v in pool.items() if k[0] == "1")) / n
            dz.append(z)
            dvar.append((1 - z * z) / n)
        D = (dz[0] - dz[1]) / 2
        seD = float(np.sqrt((dvar[0] + dvar[1]) / 4))
        out[kind] = {"Rbar": Rbar, "SE": se, "D": D, "SE_D": seD,
                     "p_plus_b0": stats[0]["p_plus"], "p_plus_b1": stats[1]["p_plus"],
                     "R_b0": stats[0]["R"], "R_b1": stats[1]["R"]}
    return out


def mutual_info_bits(counts_by_label, kind="switch"):
    """Empirical I(B; C,T) in bits, uniform prior over input bit."""
    joint = np.zeros((2, 4))  # b x (c,t) with index 2*c + t
    for bit in (0, 1):
        pool = {}
        for a, b in itertools.product(PAULIS, repeat=2):
            lab = ("sw" if kind == "switch" else "nu") + f"({a},{b})b{bit}"
            for k, v in counts_by_label[lab].items():
                pool[k] = pool.get(k, 0) + v
        n = sum(pool.values())
        for k, v in pool.items():
            t, c = int(k[0]), int(k[1])
            joint[bit, 2 * c + t] += v / n
    joint /= 2.0
    pb = joint.sum(axis=1)
    pct = joint.sum(axis=0)
    mi = 0.0
    for i in range(2):
        for j in range(4):
            if joint[i, j] > 0:
                mi += joint[i, j] * np.log2(joint[i, j] / (pb[i] * pct[j]))
    return mi


def run_backend(backend, shots_scale=1.0, seed=4529):
    ent = all_entries()
    counts = {}
    for lab, kind, a, b, bit, shots in ent:
        qc = build_circuit(a, b, bit, definite=(kind == "null"))
        tqc = transpile(qc, backend, seed_transpiler=seed, optimization_level=1)
        res = backend.run(tqc, shots=int(shots * shots_scale), seed_simulator=seed).result()
        counts[lab] = res.get_counts()
    return counts


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "--sim"
    if mode == "--sim":
        print("Exp106 NOISELESS sim gates (must pass before any spend)")
        backend = AerSimulator()
        counts = run_backend(backend, shots_scale=4.0)  # extra shots: tight gates
        st = analyze(counts)
        mi = mutual_info_bits(counts, "switch")
        print(f"  switch: Rbar={st['switch']['Rbar']:+.4f} (theory +0.5333) "
              f"SE={st['switch']['SE']:.4f}  P(+|b0)={st['switch']['p_plus_b0']:.4f} "
              f"P(+|b1)={st['switch']['p_plus_b1']:.4f} (theory 0.625)")
        print(f"  null:   D={st['null']['D']:+.4f} (theory 0.0000)  "
              f"switch D={st['switch']['D']:+.4f} (theory 0.0000 — info is in the "
              f"control-target CORRELATION only)")
        print(f"  MI(switch) = {mi:.4f} bits (theory 0.0489)")
        g1 = abs(st["switch"]["Rbar"] - 8 / 15) < 0.02
        g2 = abs(st["null"]["D"]) < 0.02 and abs(st["switch"]["D"]) < 0.02
        g3 = abs(st["switch"]["p_plus_b0"] - 0.625) < 0.01 \
            and abs(st["switch"]["p_plus_b1"] - 0.625) < 0.01
        g4 = abs(mi - 0.0489) < 0.01
        for name, ok in (("G1 Rbar", g1), ("G2 null", g2), ("G3 P(+)", g3), ("G4 MI", g4)):
            print(f"  {name}: {'PASS' if ok else 'FAIL'}")
        return 0 if all((g1, g2, g3, g4)) else 1
    if mode == "--fake":
        print("Exp106 FakeMarrakesh feasibility")
        from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
        backend = AerSimulator.from_backend(FakeMarrakesh())
        counts = run_backend(backend)
        st = analyze(counts)
        mi = mutual_info_bits(counts, "switch")
        print(f"  switch: Rbar={st['switch']['Rbar']:+.4f} SE={st['switch']['SE']:.4f} "
              f"P(+)~{st['switch']['p_plus_b0']:.4f}/{st['switch']['p_plus_b1']:.4f}")
        print(f"  null:   D={st['null']['D']:+.4f} SE_D={st['null']['SE_D']:.4f}  "
              f"switch D={st['switch']['D']:+.4f}")
        print(f"  MI(switch) = {mi:.4f} bits")
        null_ok = abs(st["null"]["D"]) + 5 * st["null"]["SE_D"] < 0.05
        win = null_ok and (st["switch"]["Rbar"] - 5 * st["switch"]["SE"] > R_WIN_FLOOR)
        print(f"  null gate (|D|+5SE < 0.05): {'PASS' if null_ok else 'FAIL'}")
        print(f"  frozen-rule preview on sim: {'WIN' if win else 'not-win'}")
        json.dump({"analyze": st, "mi_bits": mi},
                  open(os.path.join(HERE, "..", "results",
                                    "exp106_feasibility.json"), "w"), indent=1)
        return 0
    print("usage: exp106_capacity_activation.py --sim | --fake")
    return 2


if __name__ == "__main__":
    sys.exit(main())
