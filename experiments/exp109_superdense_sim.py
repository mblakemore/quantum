#!/usr/bin/env python3
"""exp109_superdense_sim.py — E3 superdense coding, sim tiers (Whisper C4590).

Both feasibility tiers for the prereg, computed not recalled (C4558 rule):
  tier 1: noiseless statevector — theory targets
  tier 2: FakeMarrakesh — noise-model preview at planned shots

Protocol (4 message circuits + 4 no-entanglement null circuits):
  main : Bell pair (H,CX) on (S,R); encode m in {00,01,10,11} as
         {I, X, Z, Z@X} on S; Bell measurement (CX, H); outcome bits = m.
  null : SAME circuits minus the initial Bell prep (R stays |0>, S=|0>
         gets the same encodings, same Bell measurement) — one unassisted
         qubit carries the message; ceiling p_success = 1/2 (two of the
         four encodings are phase-only on |0> and indistinguishable).

Observables: p_success (uniform prior over m; binomial SE) and I(m;outcome).
The frozen WIN gate will reference the unassisted-single-qubit ceiling 0.5.
"""
import json
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector

ENC = {"00": [], "01": ["x"], "10": ["z"], "11": ["z", "x"]}  # applied to S
SHOTS = 4000  # per message circuit (16k/arm total), draft for feasibility


def circuit(m, entangled=True, measured=True):
    qc = QuantumCircuit(2, 2 if measured else 0)
    if entangled:
        qc.h(0)          # S
        qc.cx(0, 1)      # R
    qc.barrier()
    for g in ENC[m]:
        getattr(qc, g)(0)
    qc.barrier()
    qc.cx(0, 1)
    qc.h(0)
    if measured:
        qc.measure([0, 1], [0, 1])   # c0 = phase bit, c1 = flip bit
    return qc


def decode(bits):
    """outcome '<c1><c0>' -> message: c0 = Z bit, c1 = X bit; m = c0 c1."""
    c0, c1 = int(bits[1]), int(bits[0])
    return f"{c0}{c1}"


def mi_from_counts(counts_by_m):
    tot = sum(sum(c.values()) for c in counts_by_m.values())
    pm = {m: sum(c.values()) / tot for m, c in counts_by_m.items()}
    pout = {}
    for m, c in counts_by_m.items():
        for o, n in c.items():
            pout[o] = pout.get(o, 0) + n / tot
    mi = 0.0
    for m, c in counts_by_m.items():
        nm = sum(c.values())
        for o, n in c.items():
            pj = n / tot
            mi += pj * np.log2(pj / (pm[m] * pout[o]))
    return mi


def run_tier(backend=None, label="noiseless"):
    out = {}
    for arm, ent in (("main", True), ("null", False)):
        counts_by_m, succ, tot = {}, 0, 0
        for m in ENC:
            qc = circuit(m, entangled=ent)
            if backend is None:
                sv = Statevector(circuit(m, entangled=ent, measured=False))
                probs = sv.probabilities_dict()
                counts = {k: int(round(v * SHOTS)) for k, v in probs.items()
                          if v > 1e-12}
            else:
                tqc = transpile(qc, backend, optimization_level=1)
                counts = backend.run(tqc, shots=SHOTS).result().get_counts()
            counts_by_m[m] = counts
            for o, n in counts.items():
                tot += n
                if decode(o) == m:
                    succ += n
        p = succ / tot
        se = float(np.sqrt(p * (1 - p) / tot)) if 0 < p < 1 else 0.0
        out[arm] = {"p_success": p, "se": se, "mi_bits": mi_from_counts(counts_by_m),
                    "shots_total": tot}
    print(f"[{label}] main: p={out['main']['p_success']:.4f}±{out['main']['se']:.4f} "
          f"MI={out['main']['mi_bits']:.4f}b | null: p={out['null']['p_success']:.4f} "
          f"MI={out['null']['mi_bits']:.4f}b")
    return out


def main():
    res = {"tier1_noiseless": run_tier(None, "noiseless")}
    from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
    from qiskit_aer import AerSimulator
    backend = AerSimulator.from_backend(FakeMarrakesh())
    res["tier2_fakemarrakesh"] = run_tier(backend, "FakeMarrakesh")
    json.dump(res, open("results/exp109_feasibility.json", "w"), indent=1)
    print("wrote results/exp109_feasibility.json")


if __name__ == "__main__":
    main()
