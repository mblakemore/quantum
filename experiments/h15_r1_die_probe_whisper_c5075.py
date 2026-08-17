#!/usr/bin/env python3
"""H15 R1 — DIE PROBE (Whisper C5075). Diagnostic, NOT a claim flight: all
states KNOWN (public seed), no seal, no secrets. Purpose: measure per-die the
three deficit contributors the R1 split could not deconfound from banked data
(`results/h15_r1_deficit_split_c5075.json`), so the N2v2 re-fly is powered by
MEASUREMENTS (banked pattern: phase-aware power models, C5074).

ROW DESIGN per die (96 rows x 1 shot, public seed 5075):
  32 x ALT-TOFFOLI  : known-A neuron, full loop (Toffoli ancilla + MCM +
                      feedforward auto). Measures P(accept|ALT) as flown.
  32 x ALT-SENSOR   : known-A prep + Bell rotation + terminal measure ONLY
                      (no Toffolis, no MCM, no feedforward). parity(bells)
                      computed offline = CLEAN upstream leakage + 8-readout,
                      zero backaction. The number the flown data couldn't give.
  16 x NULL-TOFFOLI : known-xu neuron, full loop. P(accept|NULL) as flown.
  8 x never + 8 x always (known-A, full loop): the parse/ablation contract.
PREDICTIONS (pre-registered, from the R1 split — marrakesh only; kingston is
the measurement): ALT-TOFFOLI accept 0.71 +/- 0.09; ALT-SENSOR parity0
0.70 +/- 0.10; NULL accept 0.53 +/- 0.13; never 0/8, always 8/8.
DECISION RULE (pre-registered): re-fly die = argmax over dies of predicted
N2v2 accuracy = 0.5*ALT_accept_best_variant + 0.5*(1 - NULL_accept), where
best_variant per die = max(ALT-TOFFOLI accept, ALT-SENSOR parity0). If no die
predicts >= 0.66 (threshold 0.6040 + ~2 SE at M=632), the re-fly is NOT
proposed and the wall is the finding.
$0 in this file. No submission path here (separate submit script, gated)."""
import json
import sys

import numpy as np

sys.path.insert(0, "/droid/repos/quantum/experiments")
from h15_n1_synapse_incircuit_whisper_c5074 import build, classical_rule, SIM
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister

PROBE_SEED = 5075
N = 4


def draw_A(rng):
    A = [[0] * N for _ in range(N)]
    for i in range(N):
        for j in range(i, N):
            A[i][j] = int(rng.integers(2))
    return A


def build_sensor_only(A):
    """Prep + Bell rotation + terminal measurement of the 8 bells. No decision
    network, no MCM, no feedforward. Same register layout as the neuron so one
    decoder serves both (act/dec read 0)."""
    qs = QuantumRegister(10, "q")
    c_bell = ClassicalRegister(8, "bell")
    c_dec = ClassicalRegister(1, "dec")
    c_act = ClassicalRegister(1, "act")
    qc = QuantumCircuit(qs, c_bell, c_dec, c_act)
    for base in (0, 4):
        for i in range(N):
            qc.h(base + i)
        for i in range(N):
            for j in range(i, N):
                if A[i][j]:
                    if i == j:
                        qc.z(base + i)
                    else:
                        qc.cz(base + i, base + j)
    qc.barrier()
    for i in range(N):
        qc.cx(i, 4 + i)
        qc.h(i)
    for i in range(N):
        qc.measure(i, c_bell[i])
        qc.measure(4 + i, c_bell[4 + i])
    qc.measure(8, c_dec[0])
    qc.measure(9, c_act[0])
    return qc


def probe_rows():
    """Deterministic public row list: (kind, payload, arm)."""
    rng = np.random.default_rng(PROBE_SEED)
    rows = []
    for _ in range(32):
        rows.append(("ALT_TOFFOLI", draw_A(rng), "auto"))
    for _ in range(32):
        rows.append(("ALT_SENSOR", draw_A(rng), None))
    for _ in range(16):
        rows.append(("NULL_TOFFOLI",
                     (int(rng.integers(16)), int(rng.integers(16))), "auto"))
    for _ in range(8):
        rows.append(("NEVER", draw_A(rng), "never"))
    for _ in range(8):
        rows.append(("ALWAYS", draw_A(rng), "always"))
    return rows


def build_probe():
    circs = []
    for kind, payload, arm in probe_rows():
        if kind == "ALT_SENSOR":
            circs.append(build_sensor_only(payload))
        elif kind == "NULL_TOFFOLI":
            circs.append(build(xu=payload, arm=arm))
        else:
            circs.append(build(A=payload, arm=arm))
    return circs


def decode_probe(mem_lines):
    """Per-row metrics from raw memory lines (same 'act dec bell' shape)."""
    rows = probe_rows()
    out = {"ALT_TOFFOLI": {"n": 0, "accept": 0},
           "ALT_SENSOR": {"n": 0, "parity0": 0},
           "NULL_TOFFOLI": {"n": 0, "accept": 0},
           "NEVER": {"n": 0, "act1": 0}, "ALWAYS": {"n": 0, "act1": 0}}
    for (kind, _, _), mem in zip(rows, mem_lines):
        act, accept_from_bells, dec = classical_rule(mem)
        s = out[kind]
        s["n"] += 1
        if kind == "ALT_TOFFOLI" or kind == "NULL_TOFFOLI":
            s["accept"] += act          # the flown loop's response
        elif kind == "ALT_SENSOR":
            s["parity0"] += accept_from_bells   # offline parity of bells
        else:
            s["act1"] += act
    return out


def selftest():
    circs = build_probe()
    res = SIM.run(circs, shots=1, memory=True).result()
    mems = [res.get_memory(i)[0] for i in range(len(circs))]
    d = decode_probe(mems)
    ok = (d["ALT_TOFFOLI"]["accept"] == 32 and d["ALT_SENSOR"]["parity0"] == 32
          and d["NEVER"]["act1"] == 0 and d["ALWAYS"]["act1"] == 8
          and 2 <= d["NULL_TOFFOLI"]["accept"] <= 14)
    return ok, d


if __name__ == "__main__":
    ok, d = selftest()
    print(f"selftest ok={ok}: {json.dumps(d)}")
    from qiskit import transpile
    from qiskit.providers.fake_provider import GenericBackendV2
    bk = GenericBackendV2(num_qubits=10, basis_gates=["cz", "rz", "sx", "x", "id"],
                          control_flow=True)
    circs = build_probe()
    t0 = transpile(circs[0], bk, optimization_level=1, seed_transpiler=5075)
    t32 = transpile(circs[32], bk, optimization_level=1, seed_transpiler=5075)
    print(f"ALT_TOFFOLI row: 2q={t0.count_ops().get('cz', 0)}  "
          f"ALT_SENSOR row: 2q={t32.count_ops().get('cz', 0)}")
    assert ok, "PROBE SELFTEST FAILED"
    print("PROBE KIT READY (96 rows x 1 shot per die)")
