#!/usr/bin/env python3
"""
Exp84b (Whisper C4417) — extends Exp84's toric-code Bell-pair proxy with:
  (1) noise-aware placement (quiet_qubits.pick, Elder F57/F58 lever)
  (2) a real round-1 syndrome-extraction stress test (does an active QEC round
      kill the correlation here, matching the original author's report?)
  (3) real-hardware submission to ibm_fez (the author's own backend)

Builds on run_exp84_toric_bell_proxy.py's validated code construction (CSS-orthogonality,
GF(2)-derived logical operators, fidelity-1.0-cross-checked ground-state encoder) -- imported
directly, not re-derived.

Usage:
  python3 run_exp84b_round1_and_placement.py --sim-round0 [--placement best|none]
  python3 run_exp84b_round1_and_placement.py --sim-round1 [--placement best|none]
  python3 run_exp84b_round1_and_placement.py --submit --rounds 0 --placement best   # ibm_fez
  python3 run_exp84b_round1_and_placement.py --submit --rounds 1 --placement best   # ibm_fez
  python3 run_exp84b_round1_and_placement.py --finalize JID --rounds 0
"""
import sys, os, argparse, json, time
import numpy as np
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_exp84_toric_bell_proxy import setup_code, corr, grade
import quiet_qubits

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "experiments")
JOBIDS_PATH = os.path.join(RESULTS_DIR, "exp84b_jobids.json")
RESULTS_PATH = os.path.join(RESULTS_DIR, "exp84b_results.json")
os.makedirs(RESULTS_DIR, exist_ok=True)


def build_circuit(code, basis="Z", rounds=0):
    """rounds=0: state-prep + entangle + readout (no active QEC).
       rounds=1: state-prep + ONE full syndrome-extraction round (8 X-checks + 8 Z-checks,
                 reused ancilla, NOT used for correction -- pure noise-cost stress test,
                 matching the author's own round-1 framing) + entangle + readout."""
    from qiskit import QuantumCircuit
    n = code["n"]
    HX, HZ = code["HX"], code["HZ"]
    R_HX, pivots = code["R_HX"], code["pivots"]
    XL1, XL2 = code["XL1"], code["XL2"]

    n_anc = 2 if rounds >= 1 else 1   # qubit n = entangling ancilla; qubit n+1 = syndrome ancilla (reused)
    qc = QuantumCircuit(n + n_anc, n + 1)

    # state prep (validated CSS encoder)
    for i in range(len(pivots)):
        p = pivots[i]
        qc.h(p)
        for q in range(n):
            if q != p and R_HX[i, q] == 1:
                qc.cx(p, q)

    if rounds >= 1:
        synd_anc = n + 1
        # X-checks (vertex stabilizers): ancilla |0>, H, CX(anc,q) for q in support, H, measure+reset
        for row in HX:
            support = [q for q in range(n) if row[q]]
            qc.h(synd_anc)
            for q in support:
                qc.cx(synd_anc, q)
            qc.h(synd_anc)
            qc.measure(synd_anc, n)       # classical bit n reused as scratch (not used for correction)
            qc.reset(synd_anc)
        # Z-checks (plaquette stabilizers): ancilla |0>, CX(q,anc) for q in support, measure+reset
        for row in HZ:
            support = [q for q in range(n) if row[q]]
            for q in support:
                qc.cx(q, synd_anc)
            qc.measure(synd_anc, n)
            qc.reset(synd_anc)

    anc = n
    qc.h(anc)
    for q in [i for i, b in enumerate(XL1) if b]:
        qc.cx(anc, q)
    for q in [i for i, b in enumerate(XL2) if b]:
        qc.cx(anc, q)
    qc.h(anc)
    qc.measure(anc, n)
    if basis == "X":
        qc.h(range(n))
    qc.measure(range(n), range(n))
    return qc


def get_initial_layout(backend, code, placement, rounds):
    n_anc = 2 if rounds >= 1 else 1
    n_total = code["n"] + n_anc  # must match build_circuit's actual qubit count for this rounds value
    if placement == "none":
        return None
    pick = quiet_qubits.pick(backend, n_total, mode="best")
    return pick["layout"]


def run_sim(rounds, placement, shots=4000, opt_level=1):
    from qiskit import transpile
    from qiskit_aer import AerSimulator
    from qiskit_ibm_runtime.fake_provider import FakeMarrakesh

    code = setup_code(L=3)
    n = code["n"]
    backend = FakeMarrakesh()
    sim = AerSimulator.from_backend(backend)
    layout = get_initial_layout(backend, code, placement, rounds)

    results = {}
    gate_stats = {}
    for basis in ["Z", "X"]:
        qc = build_circuit(code, basis, rounds=rounds)
        tqc = transpile(qc, sim, optimization_level=opt_level, seed_transpiler=42, initial_layout=layout)
        gate_stats[basis] = dict(
            two_q_gates=sum(1 for instr in tqc.data if instr.operation.num_qubits == 2),
            depth=tqc.depth(),
        )
        counts = sim.run(tqc, shots=shots).result().get_counts()
        # strip the reused-scratch classical bit's contribution: counts keys are full clbit string;
        # grade() expects bits[:n] data + bits[n] ancilla -- our clreg has n+1 bits (data + final anc),
        # scratch reuse of bit n during the circuit gets overwritten by the final measure(anc,n) at the end.
        results[basis] = grade(counts, code, basis, n)

    zz = corr(results["Z"])
    xx_b0 = corr({k: v for k, v in results["X"].items() if k[0] == 0})
    xx_b1 = corr({k: v for k, v in results["X"].items() if k[0] == 1})
    xx_cond = (abs(xx_b0) + abs(xx_b1)) / 2
    witness = zz + xx_cond
    return dict(rounds=rounds, placement=placement, gate_stats=gate_stats,
                zz=zz, xx_b0=xx_b0, xx_b1=xx_b1, xx_cond=xx_cond, witness=witness)


def submit_hw(rounds, placement, backend_name="ibm_fez", shots=4000):
    from qiskit import transpile
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    from run_exp66_qpu_partb import _get_ibm_service

    code = setup_code(L=3)
    service = _get_ibm_service()
    backend = service.backend(backend_name)
    print(f"Backend: {backend.name} | pending_jobs={backend.status().pending_jobs}", flush=True)
    layout = get_initial_layout(backend, code, placement, rounds)
    print(f"Placement={placement}, layout={layout}", flush=True)

    job_ids = {}
    for basis in ["Z", "X"]:
        qc = build_circuit(code, basis, rounds=rounds)
        tqc = transpile(qc, backend=backend, optimization_level=1, seed_transpiler=42, initial_layout=layout)
        twoq = sum(1 for instr in tqc.data if instr.operation.num_qubits == 2)
        print(f"  [{basis}-basis] depth={tqc.depth()} 2q-gates={twoq}", flush=True)
        sampler = SamplerV2(mode=backend)
        sampler.options.default_shots = shots
        job = sampler.run([tqc])
        jid = job.job_id()
        job_ids[basis] = jid
        print(f"  [{basis}-basis] submitted job_id={jid}", flush=True)

    manifest = {"rounds": rounds, "placement": placement, "backend": backend_name,
                "shots": shots, "job_ids": job_ids,
                "submitted_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    path = os.path.join(RESULTS_DIR, f"exp84b_jobids_r{rounds}.json")
    with open(path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"\nManifest saved: {path}")
    return manifest


def finalize_hw(manifest_path, code=None):
    from run_exp66_qpu_partb import _get_ibm_service
    manifest = json.load(open(manifest_path))
    service = _get_ibm_service()
    if code is None:
        code = setup_code(L=3)
    n = code["n"]

    results = {}
    for basis, jid in manifest["job_ids"].items():
        job = service.job(jid)
        status = str(job.status())
        print(f"  [{basis}] job={jid} status={status}", flush=True)
        if "DONE" not in status:
            print("  -> NOT DONE.")
            return None
        res = job.result()
        databin = res[0].data
        reg = list(databin.__dict__.keys())[0]
        counts = getattr(databin, reg).get_counts()
        results[basis] = grade(counts, code, basis, n)

    zz = corr(results["Z"])
    xx_b0 = corr({k: v for k, v in results["X"].items() if k[0] == 0})
    xx_b1 = corr({k: v for k, v in results["X"].items() if k[0] == 1})
    xx_cond = (abs(xx_b0) + abs(xx_b1)) / 2
    witness = zz + xx_cond
    out = dict(rounds=manifest["rounds"], placement=manifest["placement"], backend=manifest["backend"],
               zz=zz, xx_b0=xx_b0, xx_b1=xx_b1, xx_cond=xx_cond, witness=witness,
               finalized_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    print(json.dumps(out, indent=2))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sim-round0", action="store_true")
    ap.add_argument("--sim-round1", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--finalize", metavar="MANIFEST_PATH")
    ap.add_argument("--rounds", type=int, default=0)
    ap.add_argument("--placement", choices=["best", "none"], default="best")
    ap.add_argument("--backend", default="ibm_fez")
    ap.add_argument("--shots", type=int, default=4000)
    args = ap.parse_args()

    if args.sim_round0:
        r = run_sim(0, args.placement, shots=args.shots)
        print(json.dumps(r, indent=2))
    if args.sim_round1:
        r = run_sim(1, args.placement, shots=args.shots)
        print(json.dumps(r, indent=2))
    if args.submit:
        submit_hw(args.rounds, args.placement, backend_name=args.backend, shots=args.shots)
    if args.finalize:
        out = finalize_hw(args.finalize)
        if out:
            path = os.path.join(RESULTS_DIR, f"exp84b_results_r{out['rounds']}.json")
            with open(path, "w") as f:
                json.dump(out, f, indent=2)
            print(f"Saved: {path}")


if __name__ == "__main__":
    main()
