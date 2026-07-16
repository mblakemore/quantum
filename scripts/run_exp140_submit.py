#!/usr/bin/env python3
"""run_exp140_submit.py — Exp140 bridge-A OLE echo trust-calibration (Whisper C4744).

Frozen prereg: experiments/exp140-ole-stack-vs-mitigation-preregistration-DRAFT-whisper-c4744.md
Sim gate PASSED: experiments/exp140-sim/RESULT-exp140-sim-tier-whisper-c4744.md

Instance: tracker literal operator_loschmidt_echo_49x648 (α=0 echo, ideal f_δ(O)=1.0 exactly).
Observable O = Z52 Z59 Z72. Estimator: prep |z>, run echo, measure O-parity; σ_z-weighted → ideal +1.
Two arms co-submitted (same window → window-controlled):
  A = baseline placement (as-given physical layout)
  B = noise-aware placement stack (opt_level 3 re-layout on live calibration = F57/F58 lever)
Metric |f̂−1|; bridge-A gate |dev_B| < |dev_A|. RAW (pre-rescaling) reported as the mechanism signal;
rescaled-residual is the exploratory real-race metric (a null = underpowered, NOT 'stack fails').
Usage: python3 scripts/run_exp140_submit.py [--scan] [--submit] [--n-init 16] [--shots 4000]
"""
import argparse, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
QASM = os.path.join(HERE, "..", "experiments", "exp140-sim", "ole49.qasm")
OBS = [52, 59, 72]
SEED = 4744

def load_ole():
    import qiskit.qasm3 as q3
    with open(QASM) as f:
        qc = q3.loads(f.read())
    return qc

def active_qubits(qc):
    used = set()
    for inst in qc.data:
        if inst.operation.name == "barrier":
            continue  # barrier spans all qubits; not a real usage
        for q in inst.qubits:
            used.add(qc.find_bit(q).index)
    return sorted(used)

def build_estimator(base, z_bits):
    """prep |z> (X on z_bits) + echo + measure O qubits."""
    from qiskit import QuantumCircuit, ClassicalRegister
    qc = QuantumCircuit(base.num_qubits)
    for b in z_bits:
        qc.x(b)
    qc.compose(base, inplace=True)
    cr = ClassicalRegister(len(OBS), "o")
    qc.add_register(cr)
    for i, q in enumerate(OBS):
        qc.measure(q, cr[i])
    return qc

def parity_from_counts(counts):
    """<O> = avg (-1)^(#ones on the 3 measured obs bits)."""
    tot = sum(counts.values()); e = 0.0
    for bs, c in counts.items():
        ones = bs.replace(" ", "").count("1")
        e += (c/tot) * (1 if ones % 2 == 0 else -1)
    return e

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--backend", default="ibm_marrakesh")
    ap.add_argument("--n-init", type=int, default=16)
    ap.add_argument("--shots", type=int, default=4000)
    args = ap.parse_args()

    base = load_ole()
    act = active_qubits(base)
    print(f"loaded OLE echo: {base.num_qubits} qreg, {len(act)} active qubits, "
          f"{sum(1 for i in base.data if i.operation.num_qubits==2)} 2q gates; obs={OBS}")
    assert all(o in act for o in OBS), "observable qubit not active!"

    rng = np.random.default_rng(SEED)
    # z states: z=0 first (sigma_z=+1), then random over active qubits
    z_list = [[]]
    for _ in range(args.n_init - 1):
        k = rng.integers(1, len(act)//2)
        z_list.append(sorted(rng.choice(act, size=k, replace=False).tolist()))
    ests = [build_estimator(base, z) for z in z_list]
    sigma = [(1 if sum(1 for b in z if b in OBS) % 2 == 0 else -1) for z in z_list]

    if args.scan:
        # NOTE: full 49-active-qubit noiseless sim is infeasible (2^49); ideal is ANALYTIC = 1.0
        # (α=0 echo, U=I, O commutes with disjoint Z-perturbation) and the estimator LOGIC is
        # validated separately on a small echo (validate_and_power.py GATE 1 = 1.0). Scan here
        # only validates that both arms CONSTRUCT + transpile + reports 2q cost.
        print(f"[scan] ideal f_δ(O)=1.0 (analytic); estimator logic validated on small echo (GATE 1).")
        print(f"[scan] measured obs qubits {OBS} all active: OK")
        # transpile both arms to backend, report cost
        try:
            from qiskit_ibm_runtime import QiskitRuntimeService
            from qiskit import transpile
            svc = QiskitRuntimeService(); backend = svc.backend(args.backend)
            tA = transpile(ests[0], backend, optimization_level=1, initial_layout=list(range(base.num_qubits)))
            tB = transpile(ests[0], backend, optimization_level=3)
            def cz(c): return sum(1 for i in c.data if i.operation.num_qubits==2)
            print(f"[scan] Arm A (baseline): 2q={cz(tA)}  depth={tA.depth()}")
            print(f"[scan] Arm B (noise-aware): 2q={cz(tB)}  depth={tB.depth()}")
            print(f"[scan] circuits total = {2*args.n_init} ({args.n_init} z × 2 arms), shots={args.shots}")
        except Exception as e:
            print(f"[scan] backend transpile skipped ({type(e).__name__}: {e})")
        return

    if args.submit:
        from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
        from qiskit import transpile
        svc = QiskitRuntimeService(); backend = svc.backend(args.backend)
        print(f"backend {backend.name} operational={backend.status().operational}")
        tqcs, metas = [], []
        # A = opt1 + baseline layout; B = opt3 + noise-aware layout; C = opt3 + baseline layout.
        # Isolation: A vs C = pure opt-level (same trivial layout); C vs B = PURE placement (same opt3).
        arm_specs = [("A", 1, list(range(base.num_qubits))),
                     ("B", 3, None),
                     ("C", 3, list(range(base.num_qubits)))]
        for arm, opt, layout in arm_specs:
            for z, s, est in zip(z_list, sigma, ests):
                t = transpile(est, backend, optimization_level=opt,
                              initial_layout=layout) if layout else transpile(est, backend, optimization_level=opt)
                tqcs.append(t); metas.append({"arm": arm, "z": z, "sigma": s})
        sampler = SamplerV2(mode=backend)
        job = sampler.run([(t, None, args.shots) for t in tqcs])
        jid = job.job_id()
        out = os.path.join(HERE, "..", "results", f"exp140_submit_{jid}.json")
        json.dump({"job": jid, "backend": args.backend, "n_init": args.n_init,
                   "shots": args.shots, "obs": OBS, "metas": metas,
                   "ideal": 1.0}, open(out, "w"), indent=2)
        print(f"SUBMITTED job={jid}  ({len(tqcs)} circuits)  meta -> {out}")
        return

    ap.print_help()

if __name__ == "__main__":
    main()
