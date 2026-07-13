#!/usr/bin/env python3
"""exp136_steering_sim.py — ONE-SIDED DEVICE-INDEPENDENCE: quantum steering on
one chip, sim tier (Whisper C4677; the real semi-DI step Exp135 flagged.
Substrate claude-opus-4-8).

WHY STEERING IS THE CHIP-APPROPRIATE CERTIFICATE (Exp135 lesson): the DI CHSH
randomness bound needs no-signaling between two sites, which one chip cannot
enforce. STEERING needs a DIFFERENT, weaker, chip-appropriate assumption:
BOB's measurements are trusted (his own calibrated observables), ALICE is a
black box. A steering-inequality violation then certifies the state is
STEERABLE (hence ENTANGLED) under ONE-SIDED trust. The one-sided no-signaling
it needs (Alice's SETTING must not change Bob's marginal) is STRUCTURALLY
enforced on-chip: Alice's basis rotation is a gate on her qubit only, and the
reduced state on Bob is basis-choice-independent for any bipartite state.

Functional (CJWR linear steering, n=3): S_3 = (1/sqrt3)|<A_x B_x> + <A_y B_y>
+ <A_z B_z>|, LHS (unsteerable) bound = 1, quantum max = sqrt(3) ~ 1.732.
Singlet |Psi-> = (|01>-|10>)/sqrt2 gives <XX>=<YY>=<ZZ>=-1 -> S_3 = sqrt3.

SCOPE (pre-advisor-check, to be confirmed before freeze): this is a ONE-SIDED-DI
entanglement/steerability certificate under Bob-measurement-trust — NOT a
full-DI claim, NOT a no-signaling-free claim. The DI CHSH quantity that
evaporated in Exp135 is replaced by a quantity valid under the weaker,
honestly-holdable one-sided trust.
"""
import json
import math
import os

import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = 20000
AXES = ["X", "Y", "Z"]
ROT = {"X": [("h",)], "Y": [("sdg",), ("h",)], "Z": []}


# Functional signs: |Phi+> has <XX>=+1,<YY>=-1,<ZZ>=+1. The sign-matched
# functional (1/sqrt3)(<XX> - <YY> + <ZZ>) = sqrt3. The -1 on the Y term is
# absorbed into Alice's UNTRUSTED measurement (A_Y -> -A_Y, an arbitrary
# relabel of her outcomes), so the CJWR LHS bound stays exactly 1.
FUNC_SIGN = {"X": +1, "Y": -1, "Z": +1}


def bell_phi_plus(qc):
    qc.h(0)
    qc.cx(0, 1)


def steer_circuit(axis, entangled):
    qc = QuantumCircuit(2, 2)
    if entangled:
        bell_phi_plus(qc)
    else:
        qc.h(0)          # product |+>|0>: unsteerable classical-mimic null
    qc.barrier()
    for g in ROT[axis]:          # Bob (q1) TRUSTED basis
        getattr(qc, g[0])(1)
    for g in ROT[axis]:          # Alice (q0) matched setting (black box)
        getattr(qc, g[0])(0)
    qc.measure([0, 1], [0, 1])
    return qc


def corr(counts):
    tot = s = 0
    for k, v in counts.items():
        s += (1 if k.count("1") % 2 == 0 else -1) * v
        tot += v
    return s / tot


def run_S3(backend, entangled, layout=None):
    cs = {}
    for ax in AXES:
        qc = steer_circuit(ax, entangled)
        tqc = transpile(qc, backend, optimization_level=1,
                        seed_transpiler=4677, initial_layout=layout)
        cts = backend.run(tqc, shots=SHOTS).result().get_counts()
        cs[ax] = corr(cts)
    S3 = abs(sum(FUNC_SIGN[a] * cs[a] for a in AXES)) / math.sqrt(3)
    return S3, cs


def main():
    from qiskit_aer import AerSimulator
    from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
    out = {"lhs_bound": 1.0, "quantum_max": math.sqrt(3)}
    for label, be, lay in (("noiseless", AerSimulator(), None),
                           ("fakemarrakesh",
                            AerSimulator.from_backend(FakeMarrakesh()),
                            [1, 0])):
        S3, cs = run_S3(be, True, lay)
        S3n, _ = run_S3(be, False, lay)
        out[label] = {"S3": S3, "corrs": cs, "S3_null": S3n}
        print(f"[{label}] S3={S3:.4f} (LHS 1.0, quantum max {math.sqrt(3):.4f}) "
              f"S3_null={S3n:.4f}  corrs={ {k: round(v,3) for k,v in cs.items()} }")
    ok = abs(out["noiseless"]["S3"] - math.sqrt(3)) < 0.03 and \
        out["noiseless"]["S3_null"] <= 1.01
    print("NOISELESS CHECK (S3=sqrt3, null<=1):", "PASS" if ok else "FAIL")
    out["design_valid"] = bool(ok)
    json.dump(out, open(os.path.join(HERE, "..", "results",
                                     "exp136_feasibility.json"), "w"),
              indent=1, default=float)
    print("wrote results/exp136_feasibility.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
