#!/usr/bin/env python3
"""Exp252 (H7-P4) — THE SHIELDED TRICORDER: entanglement-enhanced phase sensing (Heisenberg
super-resolution) on silicon.

CLAIM: a GHZ sensor of N qubits accumulates phase N-fold faster than a single qubit. Sweep a phase
dial phi on all N qubits of GHZ_N = (|0..0>+|1..1>)/sqrt2; the parity <X^N>(phi) = cos(N phi) --
its oscillation FREQUENCY (DFT peak) equals N. N=1 is the single-qubit standard-quantum-limit
reference (freq 1); N=2,3,4 show super-resolution (freq 2,3,4). Peak LOCATION is robust to
decoherence (which only reduces amplitude), so the scaling law survives on hardware.

Grading (G11, DFT amplitude): PASS-HEISENBERG if DFT peak frequency == N for N in {2,3,4} AND the
single-qubit reference peaks at 1. Reported: per-N visibility (parity amplitude vs ideal 1.0) as the
metrology contrast. Sweep phi in [0,2pi) at M=9 points; N in {1,2,3,4} = 36 pubs x 4000 shots, shallow
(<=3 CZ). Substrate claude-opus-4-8, Whisper C4963.

Scope: PHYSICAL GHZ (the metrology result). The error-DETECTED (shielded) logical-GHZ version
(Exp219-based, 16 qubits) attenuates the signal at current depth and is named as the next-hardware step,
not flown -- the frequency super-resolution is the clean, robust deliverable."""
import os, sys, json
import numpy as np
from qiskit import QuantumCircuit
HERE = os.path.dirname(os.path.abspath(__file__)); QROOT = os.path.join(HERE, "..")
SHOTS = 4000; M = 9; NS = (1, 2, 3, 4)
PHI = [2 * np.pi * k / M for k in range(M)]

def sensor(N, phi):
    qc = QuantumCircuit(N, N)
    qc.h(0)
    for q in range(1, N): qc.cx(0, q)      # GHZ_N
    for q in range(N): qc.rz(phi, q)        # phase dial (N-fold on the parity)
    for q in range(N): qc.h(q); qc.measure(q, q)   # X-parity readout
    return qc

def build():
    return [(f"N{N}_k{k}", sensor(N, PHI[k]), SHOTS) for N in NS for k in range(M)]

def _parity(counts):
    n = sum(counts.values())
    return sum(c * (1 if k.replace(" ", "").count("1") % 2 == 0 else -1) for k, c in counts.items()) / n

def grade(counts_by_label, out):
    rows = {}; verdict_terms = []
    for N in NS:
        sig = np.array([_parity(counts_by_label[f"N{N}_k{k}"]) for k in range(M)])
        A = np.abs(np.fft.rfft(sig))
        peak = int(np.argmax(A[1:]) + 1)           # ignore DC
        vis = float(2 * A[N] / M) if N < len(A) else 0.0   # amplitude at the expected freq
        ok = (peak == N)
        rows[f"N{N}"] = {"peak_freq": peak, "expected": N, "visibility": round(vis, 3),
                         "peak_at_N": bool(ok), "signal": [round(float(x), 3) for x in sig]}
        if N in (2, 3, 4): verdict_terms.append(ok)
        print(f"  N={N}: DFT peak freq={peak} (expect {N}) {'OK' if ok else 'MISS'}  visibility={vis:.3f}")
    ref_ok = rows["N1"]["peak_freq"] == 1
    verdict = "PASS-HEISENBERG" if (all(verdict_terms) and ref_ok) else "NOT-HELD"
    print(f"  single-qubit reference peaks at {rows['N1']['peak_freq']} (expect 1): {ref_ok}")
    print(f"  VERDICT: {verdict}  (peak freq == N for N=2,3,4 AND ref==1)")
    out.update({"rows": rows, "verdict": verdict})
    return verdict

def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator()
    counts = {lab: sim.run(qc, shots=8000).result().get_counts() for lab, qc, _ in build()}
    out = {}; v = grade(counts, out)
    for N in NS:
        assert out["rows"][f"N{N}"]["peak_freq"] == N, (N, out["rows"][f"N{N}"])
        assert out["rows"][f"N{N}"]["visibility"] > 0.9, (N, "ideal visibility")
    assert v == "PASS-HEISENBERG"
    print("SELFTEST PASS: each GHZ_N oscillates at frequency N (ideal visibility ~1); PASS-HEISENBERG.")
    print("Heisenberg super-resolution: the N=4 sensor resolves phase 4x finer than the single qubit.")

def submit(backend_name):
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    from qiskit import transpile
    svc = QiskitRuntimeService(); backend = svc.backend(backend_name)
    pubs = build()
    circs = [transpile(qc, backend, optimization_level=3, seed_transpiler=29) for _, qc, _ in pubs]
    n2 = [sum(1 for i in c.data if len(i.qubits) == 2) for c in circs]
    assert max(n2) <= 10, n2
    print(f"DEPTH CHECK: {len(circs)} pubs, transpiled 2q {min(n2)}-{max(n2)}")
    job = SamplerV2(mode=backend).run([(c,) for c in circs], shots=SHOTS)
    man = {"job_id": job.job_id(), "backend": backend_name, "labels": [l for l, _, _ in pubs]}
    json.dump(man, open(os.path.join(QROOT, "results", "exp252_manifest.json"), "w"), indent=1)
    print("handle persisted:", man["job_id"])
    res = job.result()
    counts = {lab: res[i].data.c.get_counts() for i, (lab, _, _) in enumerate(pubs)}
    out = {"job_id": man["job_id"], "backend": backend_name, "substrate": "claude-opus-4-8", "M": M}
    grade(counts, out)
    json.dump({"card": out, "counts": counts}, open(os.path.join(QROOT, "results", "exp252_result.json"), "w"), indent=1, default=float)
    print("card -> results/exp252_result.json")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--submit":
        submit(sys.argv[2] if len(sys.argv) > 2 else "ibm_fez")
    else:
        selftest()
