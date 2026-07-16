#!/usr/bin/env python3
"""run_exp140b_submit.py — Exp140b: the READOUT-CONTROLLED placement re-test (Whisper C4744).

Fixes the two flaws the 3-chip batch exposed (exp140-hw-result doc):
  (1) READOUT CONFOUND — arm B remapped the observable off the fixed qubits {52,59,72}, whose
      readout varies wildly by chip. FIX: submit readout-calibration circuits and apply tensored
      REM to EVERY arm, so each arm's observable readout is corrected regardless of which physical
      qubits it lands on. After REM the only surviving difference is BULK placement.
  (2) NON-REPRODUCIBLE layout — arm B's noise-aware transpile had no seed. FIX: seed_transpiler.
Replicate on all 3 chips (kingston/marrakesh/fez): does the placement effect survive REM, and does
the marrakesh inversion persist?

Arms (all measure O=Z52 Z59 Z72, ideal f=1.0 at alpha=0):
  A = opt1 + baseline(trivial) layout      C = opt3 + baseline(trivial) layout
  B = opt3 + noise-aware layout (seeded)   [C vs B = pure bulk placement, both opt3, REM-controlled]
Plus 2 calibration circuits (all-|0>, all-|1>) over the UNION of measured physical qubits -> per-qubit
readout errors -> tensored-Z REM contrast factor c_q = 1 - e0_q - e1_q, applied per arm at grading.
Usage: python3 scripts/run_exp140b_submit.py --submit --backend ibm_kingston [--n-init 16 --shots 4000]
"""
import argparse, importlib.util, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("e140", os.path.join(HERE, "run_exp140_submit.py"))
_e = importlib.util.module_from_spec(_spec)
_saved_argv = sys.argv; sys.argv = ["x"]; _spec.loader.exec_module(_e); sys.argv = _saved_argv
OBS, SEED = _e.OBS, 4744
BSEED = 4744  # frozen transpiler seed for the noise-aware arm (reproducible layout)


def obs_phys(tqc):
    """physical qubits carrying logical OBS after transpile."""
    lay = tqc.layout.final_index_layout()
    return [lay[q] for q in OBS]


def cal_circuit(nq, union, ones):
    from qiskit import QuantumCircuit, ClassicalRegister
    qc = QuantumCircuit(nq)
    if ones:
        for q in union:
            qc.x(q)
    cr = ClassicalRegister(len(union), "c")
    qc.add_register(cr)
    for i, q in enumerate(union):
        qc.measure(q, cr[i])
    return qc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--backend", default="ibm_kingston")
    ap.add_argument("--n-init", type=int, default=16)
    ap.add_argument("--shots", type=int, default=4000)
    args = ap.parse_args()

    base = _e.load_ole(); act = _e.active_qubits(base)
    rng = np.random.default_rng(SEED)
    z_list = [[]]
    for _ in range(args.n_init - 1):
        k = rng.integers(1, len(act) // 2)
        z_list.append(sorted(rng.choice(act, size=k, replace=False).tolist()))
    ests = [_e.build_estimator(base, z) for z in z_list]
    sigma = [(1 if sum(1 for b in z if b in OBS) % 2 == 0 else -1) for z in z_list]

    if not args.submit:
        print("dry run — pass --submit to fly"); return

    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    from qiskit import transpile
    svc = QiskitRuntimeService(); backend = svc.backend(args.backend)
    trivial = list(range(base.num_qubits))
    arm_specs = [("A", 1, trivial, None), ("B", 3, None, BSEED), ("C", 3, trivial, None)]

    tqcs, metas = [], []
    arm_phys = {}
    for arm, opt, layout, seed in arm_specs:
        kw = {"optimization_level": opt}
        if layout: kw["initial_layout"] = layout
        if seed is not None: kw["seed_transpiler"] = seed
        # transpile the FIRST estimator once to read the layout (all z share the same layout)
        t0 = transpile(ests[0], backend, **kw)
        arm_phys[arm] = obs_phys(t0)
        for z, s, est in zip(z_list, sigma, ests):
            tqcs.append(transpile(est, backend, **kw)); metas.append({"arm": arm, "z": z, "sigma": s})

    # calibration over the union of measured physical qubits
    union = sorted(set(arm_phys["A"]) | set(arm_phys["B"]) | set(arm_phys["C"]))
    cal0 = transpile(cal_circuit(base.num_qubits, union, False), backend, optimization_level=0, initial_layout=trivial)
    cal1 = transpile(cal_circuit(base.num_qubits, union, True), backend, optimization_level=0, initial_layout=trivial)
    tqcs += [cal0, cal1]
    metas += [{"arm": "CAL0", "union": union}, {"arm": "CAL1", "union": union}]

    sampler = SamplerV2(mode=backend)
    job = sampler.run([(t, None, args.shots) for t in tqcs])
    jid = job.job_id()
    out = os.path.join(HERE, "..", "results", f"exp140b_submit_{jid}.json")
    json.dump({"job": jid, "backend": args.backend, "n_init": args.n_init, "shots": args.shots,
               "obs": OBS, "ideal": 1.0, "arm_phys": arm_phys, "union": union, "metas": metas},
              open(out, "w"), indent=2)
    print(f"SUBMITTED job={jid} ({len(tqcs)} circuits: 3 arms x {args.n_init} + 2 cal) on {args.backend}")
    print(f"  arm measured-phys: A/C={arm_phys['A']}  B={arm_phys['B']}  (REM union {union})")
    print(f"  meta -> {out}")


if __name__ == "__main__":
    main()
