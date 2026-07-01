#!/usr/bin/env python3
"""
Exp85 (Whisper C4418) — cheaper state-prep for the toric-code Bell proxy (F62's identified
primary lever: our validated CSS encoder cost ~190 real gates vs the author's reported ~14).

KEY INSIGHT: round-0 (no active syndrome extraction) never touches 6 of the code's 8
X-stabilizers -- the witness circuit only references Z_L1, Z_L2, X_L1, X_L2. The bare
computational state |0...0> already satisfies Z_L1 = Z_L2 = +1 TRIVIALLY (Z_L1, Z_L2 are
weight-3 Z-strings; any computational basis state is a +1 eigenstate of any product of Z's).
So for THIS SPECIFIC witness test, the full 8-generator ground-state encoder (34 raw CX, ~190
after routing) is mathematically unnecessary -- any state with the correct Z_L1/Z_L2 eigenvalue
works identically, and |0...0> (the default hardware reset state) already has it for free.

VERIFIED (noiseless sim, this cycle): witness = exactly 2.0000 with ZERO state-prep gates,
matching the full-encoder result bit-for-bit. Real ibm_fez transpile: 18 2q-gates (down from
190) -- landing in the same ballpark as the author's reported ~14 total (numeric proximity only;
we don't know their actual method).

CAUTION -- this changes TWO variables vs the full encoder, not one: gate count AND whether the
prepared state is an encoded superposition (all 8 stabilizers satisfied) or a bare product state
(only 2/8 satisfied). Real-hardware X-stabilizer check on the 6 skipped checks came back ~0 (not
+1), confirming this is genuinely a different, less-protected state, not just a cheaper version
of the same one. So a witness improvement here is NOT a clean isolation of gate count as the
cause -- see findings/F63 "What this shows" for the corrected framing. Demonstrates entanglement
of the unencoded logical operators, a weaker claim than F62's/the author's protected-codeword
claim -- does not "beat" or supersede either.

HONESTY BOUND (do not lose this when reading results): this is NOT a "fault-tolerant encoded"
preparation in the full sense -- it deliberately skips the other 6 stabilizers, which round-0
never needs (no active correction happens at round 0 regardless of how the state was prepared).
This optimization does NOT extend to round-1: syndrome extraction there measures ALL 16 checks,
including the 6 this shortcut skips, and |0...0> does NOT satisfy those (only the full ground
state does) -- using this bare-state trick for round-1 would confound "does extra depth hurt"
with "does measuring not-yet-satisfied stabilizers additionally hurt", a different experiment.
Round-1 must keep using the full encoder (run_exp84b's build_circuit).

Also confirmed: noise-aware placement (quiet_qubits) still adds overhead even on this much
smaller circuit (33 vs 18 gates on ibm_fez) -- the connectivity-mismatch trap from F62 is
structural, not scale-dependent. Default placement used throughout.

Usage:
  python3 run_exp85_bare_state_bell.py --sim-noiseless
  python3 run_exp85_bare_state_bell.py --submit --backend ibm_fez --shots 2000
  python3 run_exp85_bare_state_bell.py --finalize ../experiments/exp85_jobids.json
"""
import sys, os, argparse, json, time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_exp84_toric_bell_proxy import setup_code, corr, grade

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "experiments")
os.makedirs(RESULTS_DIR, exist_ok=True)


def build_circuit(code, basis="Z"):
    """No state-prep encoder -- bare |0...0> already satisfies Z_L1=Z_L2=+1, sufficient for
    round-0's witness (which never references the other 6 stabilizers). See module docstring."""
    from qiskit import QuantumCircuit
    n = code["n"]
    XL1, XL2 = code["XL1"], code["XL2"]
    qc = QuantumCircuit(n + 1, n + 1)
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


def run_noiseless(shots=4000):
    from qiskit import transpile
    from qiskit_aer import AerSimulator

    code = setup_code(L=3)
    n = code["n"]
    sim = AerSimulator(method="statevector")
    results = {}
    gate_stats = {}
    for basis in ["Z", "X"]:
        qc = build_circuit(code, basis)
        tqc = transpile(qc, sim)
        gate_stats[basis] = dict(two_q_gates=sum(1 for i in tqc.data if i.operation.num_qubits == 2),
                                  depth=tqc.depth())
        counts = sim.run(tqc, shots=shots).result().get_counts()
        results[basis] = grade(counts, code, basis, n)
    zz = corr(results["Z"])
    xx_b0 = corr({k: v for k, v in results["X"].items() if k[0] == 0})
    xx_b1 = corr({k: v for k, v in results["X"].items() if k[0] == 1})
    xx_cond = (abs(xx_b0) + abs(xx_b1)) / 2
    return dict(gate_stats=gate_stats, zz=zz, xx_b0=xx_b0, xx_b1=xx_b1, xx_cond=xx_cond, witness=zz + xx_cond)


def submit_hw(backend_name="ibm_fez", shots=2000):
    from qiskit import transpile
    from qiskit_ibm_runtime import SamplerV2
    from run_exp66_qpu_partb import _get_ibm_service

    code = setup_code(L=3)
    service = _get_ibm_service()
    backend = service.backend(backend_name)
    print(f"Backend: {backend.name} | pending_jobs={backend.status().pending_jobs}", flush=True)

    job_ids = {}
    for basis in ["Z", "X"]:
        qc = build_circuit(code, basis)
        tqc = transpile(qc, backend=backend, optimization_level=1, seed_transpiler=42)
        twoq = sum(1 for i in tqc.data if i.operation.num_qubits == 2)
        print(f"  [{basis}-basis] depth={tqc.depth()} 2q-gates={twoq}", flush=True)
        sampler = SamplerV2(mode=backend)
        sampler.options.default_shots = shots
        job = sampler.run([tqc])
        jid = job.job_id()
        job_ids[basis] = jid
        print(f"  [{basis}-basis] submitted job_id={jid}", flush=True)

    manifest = {"backend": backend_name, "shots": shots, "job_ids": job_ids,
                "submitted_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    path = os.path.join(RESULTS_DIR, "exp85_jobids.json")
    with open(path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"\nManifest saved: {path}")
    return manifest


def finalize_hw(manifest_path):
    from run_exp66_qpu_partb import _get_ibm_service
    manifest = json.load(open(manifest_path))
    service = _get_ibm_service()
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
    out = dict(backend=manifest["backend"], zz=zz, xx_b0=xx_b0, xx_b1=xx_b1, xx_cond=xx_cond,
               witness=zz + xx_cond, finalized_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    print(json.dumps(out, indent=2))
    path = os.path.join(RESULTS_DIR, "exp85_results.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Saved: {path}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sim-noiseless", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--finalize", metavar="MANIFEST_PATH")
    ap.add_argument("--backend", default="ibm_fez")
    ap.add_argument("--shots", type=int, default=2000)
    args = ap.parse_args()

    if args.sim_noiseless:
        r = run_noiseless(shots=args.shots if args.shots else 4000)
        print(json.dumps(r, indent=2))
    if args.submit:
        submit_hw(backend_name=args.backend, shots=args.shots)
    if args.finalize:
        finalize_hw(args.finalize)


if __name__ == "__main__":
    main()
