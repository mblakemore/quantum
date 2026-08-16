#!/usr/bin/env python3
"""PER-QUBIT FIDELITY SPECTROMETER, extended (Whisper C5073, Creator GO general#12100, ALT5/marrakesh).

Generalizes the U2b weight-ladder to N qubits: a cumulative-support Pauli ladder (w=1..N, each
weight adds ONE qubit) read out per-qubit two-copy fidelity from the ratios:
  tr2(w) = prod_{i<w} f_qi^2  ->  f_q(w-1) = sqrt(tr2(w)/tr2(w-1)).
One transpiled quantum_template(N) circuit, N prep-row pubs -> SAME physical layout for every weight
(the property that makes the ratio a clean per-qubit read). Fixed b=0 (+1 eigenstates); I-sites -> |0>.

MODES: --sim (Aer GATE: every weight recovers tr2~1 noiseless) ; --fly (sim-gate then submit ALT5).
N=10 by default (reads 10 per-qubit fidelities). ~8192 shots/weight, one pub with N rows.
"""
import argparse, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import exp142_flight_kit as K
import exp142_robust_decoder_sim as G2

N = 10
SHOTS = 8192
ACCOUNT, BACKEND = "IBMQ_ALT5", "ibm_marrakesh"
RESULT = os.path.join(HERE, "..", "results", "u2b_spectrometer_c5073.json")
LETTERS = "XYZ"


def paulis():
    return ["".join(LETTERS[i % 3] for i in range(w)) + "I" * (N - w) for w in range(1, N + 1)]


def prep_row(P):
    b = [0] * (2 * N)
    Pf = [P[i % N] for i in range(2 * N)]
    def ang(i, j):
        key = (Pf[i], b[i]) if Pf[i] != "I" else ("Z", 0)
        return K.PREP_ANGLES[key][j]
    return [ang(i, 0) for i in range(2 * N)] + [ang(i, 1) for i in range(2 * N)]


def tr2(counts, P, mp, cs):
    Pb = G2.pauli_to_bits(P); want = cs[P.count("Y") % 2]
    g = t = 0
    for bs, c in counts.items():
        Q = G2.outcome_to_bits(bs, N, mp)
        g += c * (int(G2.sp_inner(Q, Pb, N)) == want); t += c
    return 2 * (g / t) - 1


def rows():
    return np.array([prep_row(P) for P in paulis()])


def sim():
    from qiskit_aer import AerSimulator
    from qiskit_aer.primitives import SamplerV2 as AerSampler
    from qiskit import transpile
    qc, params = K.quantum_template(N)
    tqc = transpile(qc, AerSimulator(), optimization_level=1, seed_transpiler=142)
    r = AerSampler().run([(tqc, K.named_rows(params, rows()), SHOTS)]).result()[0]
    mp = G2.calibrate_bell_mapping(); cs = G2.calibrate_constraint_sign(mp)
    ok = True
    for i, P in enumerate(paulis()):
        v = tr2(r.data.c[i].get_counts(), P, mp, cs); good = v > 0.85; ok &= good
        print(f"  SIM w{i+1}: tr2={v:+.4f} {'ok' if good else 'FAIL'}")
    print(f"SIM GATE: {'PASS' if ok else 'FAIL'}")
    return ok


def fly():
    from qiskit import transpile
    from qiskit_ibm_runtime import SamplerV2
    import ibm_multi_account as M
    svc = M.service_for_submission(ACCOUNT); backend = svc.backend(BACKEND)
    qc, params = K.quantum_template(N)
    tqc = transpile(qc, backend, optimization_level=1, seed_transpiler=142)
    job = SamplerV2(mode=backend).run([(tqc, K.named_rows(params, rows()), SHOTS)])
    jid = job.job_id()
    print(f"SUBMITTED spectrometer N={N} -> {BACKEND} via {ACCOUNT}: job {jid}")
    json.dump({"card": "u2b_spectrometer", "cycle": "C5073", "job_id": jid, "backend": BACKEND,
               "account": ACCOUNT, "N": N, "paulis": paulis(), "shots": SHOTS, "status": "SUBMITTED"},
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
