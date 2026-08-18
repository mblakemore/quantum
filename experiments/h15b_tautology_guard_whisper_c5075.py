"""EXP228 TAUTOLOGY GUARD applied to the H15-B magic-square neuron (Whisper C5075). $0.

exp228 (C4913, NOT CERTIFIED) failed because each context's three observables came from ONE joint
readout, making the third the algebraic product of the first two: the witness was pinned by
bit-identity and tested nothing. The smoking gun was ZERO VARIANCE. My h15b returned exactly
1.0000 in all nine contexts and shipped WITHOUT a severed-entanglement arm — so the same question
is open on it, and reasoning that "mine is different" is not a measurement.

THE TEST: sever the Bell pairs (drop the CX, leaving a product state). A neuron whose agreement is
carried by ENTANGLEMENT must COLLAPSE toward chance. A neuron whose agreement is a bit-identity
cannot move, because an identity does not care what state it is evaluated on.
"""
import sys, json
sys.path.insert(0, "/droid/repos/quantum/experiments")
from h15b_magic_square_neuron_whisper_c5075 import CONTEXTS, build_neuron, classical_ceiling
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit.circuit.classical import expr
from qiskit_aer import AerSimulator
import h15b_magic_square_neuron_whisper_c5075 as M

SIM = AerSimulator(seed_simulator=5075)

def build_severed(r, c):
    """Identical circuit with the two CX gates removed -> A and B unentangled."""
    qc = build_neuron(r, c)
    out = QuantumCircuit(*qc.qregs, *qc.cregs)
    for inst in qc.data:
        if inst.operation.name == "cx" and len(inst.qubits) == 2:
            q0 = qc.find_bit(inst.qubits[0]).index; q1 = qc.find_bit(inst.qubits[1]).index
            if (q0, q1) in ((1, 0), (2, 3)):     # the two Bell-pair CXs only
                continue
        out.append(inst.operation, inst.qubits, inst.clbits)
    return out

ceil, _ = classical_ceiling()
res = {}
for name, builder in (("entangled", build_neuron), ("SEVERED", build_severed)):
    tot = win = 0; per = {}
    for (r, c) in CONTEXTS:
        m = SIM.run(builder(r, c), shots=1024, memory=True).result().get_memory()
        w = sum(int(x.split()[0]) for x in m)
        per[f"r{r}c{c}"] = w / 1024; win += w; tot += 1024
    res[name] = {"overall": win / tot, "per_context": per}
    print(f"{name:10s} overall {win/tot:.4f}   per-context min {min(per.values()):.4f} max {max(per.values()):.4f}")

drop = res["entangled"]["overall"] - res["SEVERED"]["overall"]
print(f"\nclassical ceiling {ceil:.4f}")
print(f"DROP on severing entanglement: {drop:+.4f}")
verdict = ("TAUTOLOGY — agreement is a bit-identity, unaffected by the state. exp228's failure."
           if abs(drop) < 0.02 else
           "NOT A TAUTOLOGY — the response is carried by the entanglement, as required.")
print(f"VERDICT: {verdict}")
if res["SEVERED"]["overall"] > ceil:
    print("  WARNING: severed arm still BEATS the classical ceiling -> the ceiling or the")
    print("  apparatus is mis-specified; a product state cannot beat a non-contextual bound.")
json.dump({"card":"h15b_tautology_guard","cycle":"C5075","ceiling":ceil,
           "drop_on_severing":drop,"verdict":verdict,**res},
          open("/droid/repos/quantum/results/h15b_tautology_guard_c5075.json","w"), indent=1)
print("\nWROTE results/h15b_tautology_guard_c5075.json")
