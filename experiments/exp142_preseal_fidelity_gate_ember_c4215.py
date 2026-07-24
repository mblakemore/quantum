#!/usr/bin/env python3
"""On-device PRE-SEAL FIDELITY GATE (Ember C4215) — the gate that would have caught exp142c.

LESSON (c4215_003): compiled_G1 / transpile exactness verify the LOGICAL circuit, NOT on-device
fidelity. A prep that is exact in sim can transpile to a depth that noise washes out (exp142c
mixed-state: <P> collapsed to ~0 by CX-star SWAP-depth). THE FIX: before ANY blind seal+run, fly a
KNOWN PUBLIC test-P through the candidate prep on the real backend and confirm the true-basis
parity <P> SURVIVES. Only on PASS do you seal a fresh P and blind-run.

GATE (per candidate prep, per rung n):
  prep rho_test (public P_test), measure in basis P_test -> even-rate p_P (should be ~readout-
  limited); measure in a few WRONG bases -> p_wrong (~0.5). PASS iff p_P >= FLOOR and
  (p_P - mean p_wrong) >= MARGIN. Uses a PUBLIC test-P (never the seal) so the gate is verifiable
  and blind-independent.

  --validate --backend ibm_fez   fly pure-state AND mixed-state preps for the public test-P at
                                 n=4/6/8; report even-rates + PASS/FAIL (demonstrates the gate
                                 PASSES the fidelity-correct pure-state prep and FAILS the washed
                                 mixed-state prep — i.e. it would have caught exp142c pre-blind).
"""
import argparse, json, os, sys, itertools
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import exp142_flight_kit as K
import exp142c_flight_ember_c4215 as C   # mixed-state prep_uc reference

# PUBLIC test-P per rung (documented, NEVER a seal): fixed full-weight pattern
TEST_P = {4: "XYZX", 6: "XYZXYZ", 8: "XYZXYZXY"}
MEAS = {"X": (np.pi/2, 0.0, np.pi), "Y": (np.pi/2, 0.0, np.pi/2), "Z": (0.0, 0.0, 0.0)}
FLOOR = 0.75          # true-basis even-rate must clear this (chance=0.5; <P> >= 0.5)
MARGIN = 0.20         # true-basis must beat wrong-basis by this (clear contrast)
SHOTS = 512


def pure_prep(n, P):
    """Pure-state prep |P, b=0> (single-qubit eigenstates, ZERO entangling gates). n qubits."""
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(n)
    for i in range(n):                       # b=0 -> +1 eigenstate of P_i (even-parity sign vector)
        t, p = K.PREP_ANGLES[(P[i], 0)]
        qc.u(t, p, 0.0, i)
    return qc, n, list(range(n))             # (circuit, nqubits, data qubits)


def mixed_prep(n, P):
    """Mixed-state ancilla-trace prep + U_C (the exp142c delivery, 2n-1 qubits)."""
    qc = C.prep_uc(n, P)
    return qc, 2 * n - 1, list(range(n))


def add_measure(qc, nq, data, A):
    """append measurement rotation (basis A on data qubits) + measure data."""
    from qiskit import QuantumCircuit, ClassicalRegister
    out = qc.copy(); out.add_register(ClassicalRegister(len(data), "c")); out.barrier()
    for k, i in enumerate(data):
        t, p, l = MEAS[A[k]]
        out.u(t, p, l, i)
    out.measure(data, range(len(data)))
    return out


def even_rate(counts):
    ev = sum(v for k, v in counts.items() if bin(int(k, 2)).count("1") % 2 == 0)
    return ev / sum(counts.values())


def wrong_bases(n, P, k=3, seed=7):
    rng = np.random.default_rng(seed); out = []
    while len(out) < k:
        A = "".join(rng.choice(list("XYZ"), n))
        if A != P and A not in out: out.append(A)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--backend", default="ibm_fez")
    args = ap.parse_args()
    if not args.validate:
        print("use --validate"); return 0

    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit import transpile
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(args.backend)
    tgt = backend.target
    ro = sorted(((tgt["measure"][(q,)].error or 0.0), q) for (q,) in tgt["measure"].keys())

    print(f"PRE-SEAL FIDELITY GATE on {backend.name} (FLOOR={FLOOR}, MARGIN={MARGIN}, shots={SHOTS}):")
    print(f"  public test-P: {TEST_P}\n")
    results = {}
    for n in (4, 6, 8):
        P = TEST_P[n]; bases = [P] + wrong_bases(n, P)
        for mode, prepfn in (("pure-state", pure_prep), ("mixed-state", mixed_prep)):
            prep, nq, data = prepfn(n, P)
            layout = [q for _, q in ro[:nq]]
            pubs = []
            for A in bases:
                qc = add_measure(prep, nq, data, A)
                tqc = transpile(qc, backend, initial_layout=layout, optimization_level=1,
                                seed_transpiler=142)
                pubs.append((tqc, None, SHOTS))
            job = SamplerV2(mode=backend).run(pubs)
            res = job.result()
            rates = [even_rate(res[i].data.c.get_counts()) for i in range(len(bases))]
            pP = rates[0]; pw = float(np.mean(rates[1:]))
            passed = pP >= FLOOR and (pP - pw) >= MARGIN
            results[(n, mode)] = {"p_P": round(pP, 3), "p_wrong_mean": round(pw, 3),
                                  "PASS": passed, "job": job.job_id()}
            print(f"  n={n} {mode:11s}: <P>-basis even-rate {pP:.3f}  wrong ~{pw:.3f}  "
                  f"-> {'PASS' if passed else 'FAIL (signal washed)'}  [{job.job_id()}]")
    json.dump(results and {f"{n}_{m}": v for (n, m), v in results.items()},
              open(os.path.join(HERE, "..", "results", "preseal_fidelity_gate_validate.json"), "w"),
              indent=1, default=str)
    print("\nGATE RULE: a candidate prep may seal+blind-run at a rung ONLY if it PASSES here first.")
    print("Expected: pure-state PASSES (0-CZ, fidelity-correct), mixed-state FAILS (deep-CZ washout)")
    print("=> this gate, run before exp142c, would have caught the washout at $0-of-blind-run.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
