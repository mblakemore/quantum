#!/usr/bin/env python3
"""U2b — fixed-b two-copy reproducibility flight (Whisper C5073, Creator GO general#12081, ALT5).

Tests the U0 build-upon result on-device: does the uniform per-qubit fidelity model f=0.9528
(from door-b/marrakesh, tr2 = f^(2*weight)) hold under an INDEPENDENT prep (fixed-b, not the F122
fresh-b ensemble) and the two-copy observable, flown fresh? Prepares two copies of a KNOWN Pauli
eigenstate |P,b> with a FIXED even-parity b (U3: fixed b makes the overlap meaningful; fresh b
maximally-mixes it), transversal-Bell-measures, estimates tr(P rho)^2 with the validated G2 decoder.

MODES:
  --sim   : Aer noise-model pipeline (recert_edges lineage). GATE: noiseless recovers tr2~1 (pipeline
            correct); noisy gives a finite tr2 (the on-device prediction). MUST pass before --fly.
  --fly   : submit to ibm_marrakesh via IBMQ_ALT5 (service_for_submission pins the free open instance;
            #151 gate blocks any paid/region misroute). Writes job id; decode on landing.

Known P (public, no seal): weight-4 'XYZX'. Fixed b='0000'. n=4 (8 qubits two-copy). ~8192 shots.
U0 prediction: tr2 ~ f^(2*4) = 0.9528^8 = 0.708 (approx; different qubits shift f).
"""
import argparse, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import exp142_flight_kit as K
import exp142_robust_decoder_sim as G2

N = 4
P = "XYZX"
B = "0000"                       # fixed even-parity sign string
SHOTS = 8192
ACCOUNT = "IBMQ_ALT5"
BACKEND = "ibm_marrakesh"
RESULT = os.path.join(HERE, "..", "results", "u2b_flight_c5073.json")


def fixed_b_row():
    """One two-copy prep row for |P,B> in BOTH copies (fixed b), matching quantum_template params."""
    bb = [int(c) for c in (B + B)]            # same b for copy1 and copy2 (2n bits)
    Prep = [P[i % N] for i in range(2 * N)]
    tp = [K.PREP_ANGLES[(Prep[i], bb[i])][0] for i in range(2 * N)]
    pp = [K.PREP_ANGLES[(Prep[i], bb[i])][1] for i in range(2 * N)]
    return tp + pp


def tr2_from_counts(counts, mapping, csign):
    Pb = G2.pauli_to_bits(P); want = csign[P.count("Y") % 2]
    g = t = 0
    for bs, c in counts.items():
        Q = G2.outcome_to_bits(bs, N, mapping)
        g += c * (int(G2.sp_inner(Q, Pb, N)) == want); t += c
    return 2 * (g / t) - 1


def build():
    qc, params = K.quantum_template(N)
    row = fixed_b_row()
    return qc, params, np.array([row])


def sim():
    from qiskit_aer import AerSimulator
    from qiskit_aer.primitives import SamplerV2 as AerSampler
    from qiskit import transpile
    qc, params, rows = build()
    mapping = G2.calibrate_bell_mapping(); csign = G2.calibrate_constraint_sign(mapping)
    # noiseless GATE: pipeline must recover tr2 ~ 1 for the ideal pure eigenstate
    tqc = transpile(qc, AerSimulator(), optimization_level=1, seed_transpiler=142)
    samp = AerSampler()
    r = samp.run([(tqc, K.named_rows(params, rows), SHOTS)]).result()[0]
    tr2_ideal = tr2_from_counts(r.data.c[0].get_counts(), mapping, csign)
    ok = tr2_ideal > 0.90
    print(f"SIM noiseless: tr(P rho)^2 = {tr2_ideal:+.4f}  -> {'GATE PASS (pipeline recovers ~1)' if ok else 'GATE FAIL'}")
    return ok


def fly():
    from qiskit import transpile
    from qiskit_ibm_runtime import SamplerV2
    sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
    import ibm_multi_account as M
    svc = M.service_for_submission(ACCOUNT)          # #151 gate pins ALT5 free open instance
    backend = svc.backend(BACKEND)
    qc, params, rows = build()
    tqc = transpile(qc, backend, optimization_level=1, seed_transpiler=142)
    sampler = SamplerV2(mode=backend)
    job = sampler.run([(tqc, K.named_rows(params, rows), SHOTS)])
    jid = job.job_id()
    print(f"SUBMITTED U2b -> {BACKEND} via {ACCOUNT}: job {jid}")
    json.dump({"card": "u2b_flight", "cycle": "C5073", "job_id": jid, "backend": BACKEND,
               "account": ACCOUNT, "P": P, "b": B, "n": N, "shots": SHOTS,
               "u0_prediction_tr2": 0.9528 ** (2 * N), "status": "SUBMITTED"},
              open(RESULT, "w"), indent=1)
    print(f"-> {RESULT}")
    return jid


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sim", action="store_true")
    ap.add_argument("--fly", action="store_true")
    a = ap.parse_args()
    if a.sim:
        sim()
    elif a.fly:
        if not sim():
            print("SIM GATE FAILED — refusing to fly (C4038 discipline)"); sys.exit(1)
        fly()
    else:
        print("use --sim (verify) or --fly (sim-gate then submit to ALT5)")
