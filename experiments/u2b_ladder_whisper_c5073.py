#!/usr/bin/env python3
"""U2b WEIGHT-LADDER (Whisper C5073, Creator GO general#12091, ALT5/marrakesh).

Proves (or refutes) the U0 model FORM on ONE fixed qubit set: is a SINGLE per-qubit fidelity f
enough to explain tr(P rho)^2 across weights via tr2 = f^(2*weight)? U2b (single w=4) SUPPORTED the
form and gave a local f=0.983; a ladder over w=1..4 on the SAME qubits either proves the form (all
points on one line log(tr2)/2 = w*log f) or refutes it (curvature = the uniform model is incomplete).

SAME QUBITS BY CONSTRUCTION: all weights use the identical quantum_template(4) circuit (8 qubits,
same Bell-measure); only the prep ANGLES differ. Transpile ONCE, bind 4 prep-rows as 4 pubs -> one
layout for every weight. Fixed b=0000 (+1 eigenstates); I-positions prepped as |0> (Z,0).

MODES: --sim (Aer, GATE: every weight recovers tr2~1 noiseless) ; --fly (sim-gate then submit ALT5).
Paulis: w1 XIII · w2 XYII · w3 XYZI · w4 XYZX. ~8192 shots/pub.
"""
import argparse, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import exp142_flight_kit as K
import exp142_robust_decoder_sim as G2

N = 4
PAULIS = ["XIII", "XYII", "XYZI", "XYZX"]     # weights 1,2,3,4
B = "0000"
SHOTS = 8192
ACCOUNT, BACKEND = "IBMQ_ALT5", "ibm_marrakesh"
RESULT = os.path.join(HERE, "..", "results", "u2b_ladder_c5073.json")


def prep_row(P):
    bb = [int(c) for c in (B + B)]
    Pf = [P[i % N] for i in range(2 * N)]
    def ang(i, j):
        key = (Pf[i], bb[i]) if Pf[i] != "I" else ("Z", 0)   # I -> |0>
        return K.PREP_ANGLES[key][j]
    return [ang(i, 0) for i in range(2 * N)] + [ang(i, 1) for i in range(2 * N)]


def tr2(counts, P, mapping, csign):
    Pb = G2.pauli_to_bits(P); want = csign[P.count("Y") % 2]
    g = t = 0
    for bs, c in counts.items():
        Q = G2.outcome_to_bits(bs, N, mapping)
        g += c * (int(G2.sp_inner(Q, Pb, N)) == want); t += c
    return 2 * (g / t) - 1


def rows():
    return np.array([prep_row(P) for P in PAULIS])


def sim():
    from qiskit_aer import AerSimulator
    from qiskit_aer.primitives import SamplerV2 as AerSampler
    from qiskit import transpile
    qc, params = K.quantum_template(N)
    tqc = transpile(qc, AerSimulator(), optimization_level=1, seed_transpiler=142)
    r = AerSampler().run([(tqc, K.named_rows(params, rows()), SHOTS)]).result()[0]
    mp = G2.calibrate_bell_mapping(); cs = G2.calibrate_constraint_sign(mp)
    ok = True
    for i, P in enumerate(PAULIS):
        v = tr2(r.data.c[i].get_counts(), P, mp, cs)
        good = v > 0.90; ok &= good
        print(f"  SIM w{P.count('X')+P.count('Y')+P.count('Z')} {P}: tr2={v:+.4f} {'ok' if good else 'FAIL'}")
    print(f"SIM GATE: {'PASS' if ok else 'FAIL'}")
    return ok


def fly():
    from qiskit import transpile
    from qiskit_ibm_runtime import SamplerV2
    import ibm_multi_account as M
    svc = M.service_for_submission(ACCOUNT); backend = svc.backend(BACKEND)
    qc, params = K.quantum_template(N)
    tqc = transpile(qc, backend, optimization_level=1, seed_transpiler=142)   # ONE layout, all weights
    job = SamplerV2(mode=backend).run([(tqc, K.named_rows(params, rows()), SHOTS)])
    jid = job.job_id()
    print(f"SUBMITTED U2b-ladder -> {BACKEND} via {ACCOUNT}: job {jid}")
    json.dump({"card": "u2b_ladder", "cycle": "C5073", "job_id": jid, "backend": BACKEND,
               "account": ACCOUNT, "paulis": PAULIS, "b": B, "shots": SHOTS, "status": "SUBMITTED"},
              open(RESULT, "w"), indent=1)
    print(f"-> {RESULT}"); return jid


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--sim", action="store_true"); ap.add_argument("--fly", action="store_true")
    a = ap.parse_args()
    if a.sim: sim()
    elif a.fly:
        if not sim(): print("SIM GATE FAILED — refusing to fly"); sys.exit(1)
        fly()
    else: print("use --sim or --fly")
