#!/usr/bin/env python3
"""G3 TWO-COPY BELL fidelity gate (Ember C4215) — extends the pre-seal gate to the READOUT.

P1 First Contact (Whisper C5003): the pre-seal gate certified the single-copy PREP (0.99/0.98/0.97,
0-CZ) — necessary, NOT sufficient. The advantage rides on the CROSS-REGISTER two-copy Bell readout,
which is NOT 0-CZ (the fragile weight-n observable that washed exp142c's mixed-state delivery). This
gate certifies the FULL two-copy protocol on-device for a PUBLIC test-P before any seal.

ADVISOR-PINNED (the load-bearing choices):
 (1) Certify the RAW observable the advantage rides on, NOT "the decoder recovered P". The decoder
     absorbs noise (the exp142c 'noise-absorbed-by-C' trap). The raw observable = the per-Bell-sample
     SYMPLECTIC-CONSTRAINT rate: fraction of Bell-sampled Q with <Q,P>_sp = csign (noiseless -> 1.0,
     fully-washed -> 0.5 chance). Exact analog of the prep even-rate. Wrong-P -> ~0.5 contrast.
 (2) Verify the DELIVERED circuit: transpile on the real backend and PRINT the routed 2q-depth of the
     Bell layer (logical-shallow != delivered-shallow — the class that bit exp142c). Don't assert native.
 (3) Pre-register FLOOR/MARGIN and report noiseless-vs-on-device so the Bell readout's contribution is
     isolated from the already-certified prep.

  --validate --backend ibm_fez   noiseless self-check + on-device constraint-rate for public test-P.
"""
import argparse, json, os, sys, itertools
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import exp142_flight_kit as K
import exp142_robust_decoder_sim as G2

TEST_P = {4: "XYZX", 6: "XYZXYZ", 8: "XYZXYZXY"}
FLOOR = 0.75          # constraint-rate must clear this (chance=0.5)
MARGIN = 0.20         # true-P must beat wrong-P constraint-rate by this


def constraint_rate(counts_list, n, P, mapping, csign):
    """RAW observable: fraction of Bell samples whose Q satisfies the P-constraint.
    The expected value is csign[ypar] where ypar = (#Y in P) mod 2 (the decoder's per-candidate
    check). Noiseless & P=true -> 1.0; wrong candidate -> ~0.5; fully washed -> ~0.5."""
    Pb = G2.pauli_to_bits(P); want = csign[P.count("Y") % 2]
    good = tot = 0
    for cts in counts_list:
        for bitstring, c in cts.items():
            Q = G2.outcome_to_bits(bitstring, n, mapping)
            good += c * (int(G2.sp_inner(Q, Pb, n)) == want); tot += c
    return good / tot


ROWS = 8               # distinct fresh-b copy-pairs (constraint is b-independent; varying b checks it)
SHOTS_PER_ROW = 256    # ROWS*SHOTS_PER_ROW = 2048 Bell samples per (n, arm)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--sim-only", action="store_true", help="noiseless self-check only, no QPU")
    ap.add_argument("--predict", action="store_true",
                    help="$0: routed Bell-layer depth + NOISE-MODEL washout prediction (NO job submit)")
    ap.add_argument("--backend", default="ibm_fez")
    args = ap.parse_args()
    if not (args.validate or args.sim_only or args.predict):
        print("use --predict ($0 depth+noise-model) / --validate (fly) / --sim-only"); return 0

    def extract_cl(pub_result, nrows):
        """Per-param-row counts from a SamplerV2 pub result (runtime OR aer primitives — same API).
        Index the shaped BitArray per row so pooling is explicit and version-robust."""
        c = pub_result.data.c
        out = []
        for i in range(nrows):
            try:
                out.append(c[i].get_counts())
            except Exception:
                out.append(c.get_counts())   # unshaped fallback (single row)
        return out

    def rates(cl, n, P):
        rP = constraint_rate(cl, n, P, mapping, csign)
        wrong = next(A for A in ("".join(t) for t in itertools.product("XYZ", repeat=n)) if A != P)
        rW = constraint_rate(cl, n, wrong, mapping, csign)
        return rP, rW

    mapping = G2.calibrate_bell_mapping()
    csign = G2.calibrate_constraint_sign(mapping)
    print(f"G3 TWO-COPY BELL GATE (FLOOR={FLOOR}, MARGIN={MARGIN}, "
          f"{ROWS} rows x {SHOTS_PER_ROW} shots, csign={csign})")
    print("  certifying the FROZEN kit's quantum_template (the actual flight arm), public test-P:")
    print(f"  {TEST_P}\n")

    # ---- (0) NOISELESS self-check through the SAME SamplerV2 path (validates observable+plumbing) ----
    from qiskit_aer.primitives import SamplerV2 as AerSampler
    aer = AerSampler()
    print("NOISELESS self-check (real flight circuit, same SamplerV2 extraction as flight):")
    for n in (4, 6):
        qc, params = K.quantum_template(n)
        rows, _ = K.quantum_param_rows(TEST_P[n], ROWS, np.random.default_rng(4215 + n))
        pr = aer.run([(qc, K.named_rows(params, rows), SHOTS_PER_ROW)]).result()[0]
        rP, rW = rates(extract_cl(pr, len(rows)), n, TEST_P[n])
        print(f"  n={n}: constraint-rate true-P={rP:.3f} (expect 1.0)  wrong-P={rW:.3f} (expect ~0.5)")
    print()
    if args.sim_only:
        print("sim-only: observable + SamplerV2 plumbing validated. Re-run with --validate to fly.")
        return 0

    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit import transpile
    svc = _get_ibm_service(); backend = svc.backend(args.backend)

    # ---- (P) $0 PREDICT: routed Bell-layer depth + noise-model washout prediction, NO job submit ----
    if args.predict:
        from qiskit_aer import AerSimulator
        from qiskit_aer.noise import NoiseModel
        nm = NoiseModel.from_backend(backend)
        noisy = AerSampler(options={"backend_options": {"noise_model": nm}})
        print(f"$0 PREDICT on {backend.name} noise model (NO QPU submitted):")
        pred = {}
        for n in (4, 6, 8):
            q_layout, _, bell_pairs = K.pick_layouts(backend, n)
            qc, params = K.quantum_template(n)
            tqc = transpile(qc, backend, initial_layout=q_layout, optimization_level=1, seed_transpiler=142)
            twoq = sum(1 for inst in tqc.data if inst.operation.num_qubits == 2)
            depth2q = tqc.depth(lambda inst: inst.operation.num_qubits == 2)
            rows, _ = K.quantum_param_rows(TEST_P[n], ROWS, np.random.default_rng(99 + n))
            pr = noisy.run([(tqc, K.named_rows(params, rows), SHOTS_PER_ROW)]).result()[0]
            rP, rW = rates(extract_cl(pr, len(rows)), n, TEST_P[n])
            would = rP >= FLOOR and (rP - rW) >= MARGIN
            pred[n] = {"pred_rate_P": round(rP, 3), "pred_rate_wrong": round(rW, 3),
                       "routed_2q_gates": int(twoq), "routed_2q_depth": int(depth2q),
                       "bell_pairs": bell_pairs, "WOULD_PASS": bool(would)}
            print(f"  n={n}: PRED Bell-rate P={rP:.3f} wrong={rW:.3f}  routed 2q: {twoq} gates / "
                  f"depth {depth2q} (edges {bell_pairs})  -> would {'PASS' if would else 'FAIL'}")
        json.dump({str(k): v for k, v in pred.items()},
                  open(os.path.join(HERE, "..", "results", "g3_twocopy_bell_gate_predict.json"), "w"),
                  indent=1, default=str)
        print("\n$0 PREDICT complete (no QPU). routed depth = advisor #2 (delivered != assumed);")
        print("noise-model rate = washout forecast. Fly (--validate) only confirms a predicted PASS.")
        return 0

    # ---- on-device: fly the delivered template, print routed Bell-layer 2q-depth, constraint-rate ----
    from qiskit_ibm_runtime import SamplerV2
    print(f"ON-DEVICE {backend.name}:")
    results = {}
    for n in (4, 6, 8):
        q_layout, conv_layout, bell_pairs = K.pick_layouts(backend, n)  # copy1 then copy2 on Bell edges
        qc, params = K.quantum_template(n)
        tqc = transpile(qc, backend, initial_layout=q_layout, optimization_level=1, seed_transpiler=142)
        # (2) routed 2q count/depth of the DELIVERED circuit (don't assume native)
        twoq = sum(1 for inst in tqc.data if inst.operation.num_qubits == 2)
        depth2q = tqc.depth(lambda inst: inst.operation.num_qubits == 2)
        rows, _ = K.quantum_param_rows(TEST_P[n], ROWS, np.random.default_rng())  # OS entropy, fresh b
        job = SamplerV2(mode=backend).run([(tqc, K.named_rows(params, rows), SHOTS_PER_ROW)])
        rP, rW = rates(extract_cl(job.result()[0], len(rows)), n, TEST_P[n])
        passed = rP >= FLOOR and (rP - rW) >= MARGIN
        results[n] = {"constraint_rate_P": round(rP, 3), "constraint_rate_wrong": round(rW, 3),
                      "routed_2q_gates": int(twoq), "routed_2q_depth": int(depth2q),
                      "bell_pairs": bell_pairs, "PASS": bool(passed), "job": job.job_id()}
        print(f"  n={n}: Bell constraint-rate P={rP:.3f} wrong={rW:.3f}  routed 2q: {twoq} gates / "
              f"depth {depth2q}  -> {'PASS' if passed else 'FAIL (Bell readout washed)'}  [{job.job_id()}]")
    json.dump({str(k): v for k, v in results.items()},
              open(os.path.join(HERE, "..", "results", "g3_twocopy_bell_gate_validate.json"), "w"),
              indent=1, default=str)
    print("\nG3 VERDICT: the two-copy Bell READOUT is certified deliverable ONLY if it PASSES here")
    print("(prep already certified ~0.99). If it washes, the P1 advantage is not executable this epoch.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
