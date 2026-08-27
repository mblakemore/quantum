#!/usr/bin/env python3
"""
Dihedral-HSP hardware-demo — $0 build (Whisper C5085).
Full N=8 + N=16 recovery via the Kuperberg sieve, ideal + noisy (from_backend / representative).

Dihedral HSP over D_N  ==  hidden-shift problem (find s in Z_N).
After the abelian Fourier step, each oracle sample is a COSET (phase) state
    |psi_k> = (|0> + w^{k s}|1>)/sqrt2,   w = e^{2pi i/N},   k KNOWN, s HIDDEN.
Kuperberg SIEVE: combine pairs of coset states (CNOT + herald) to manufacture states
with useful k = N/2^{m+1} (2^{n-1-m}), which reads bit m of s after a phase correction
by the already-recovered lower bits.  Subexponential 2^O(sqrt log N) in general; for
small N it is 1-2 combination rounds per bit -- which is exactly why small N is flyable.

FRAME: labeled ENGINEERING demonstration. NO advantage (small-N brute force is trivial),
NO scaling/crypto claim. Graded only by: does the quantum machinery recover s, and does it
survive hardware noise?  (Flight-A frame.)
"""
import numpy as np, sys
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel

def coset(qc, q, k, s, N):
    """oracle-produced coset state |psi_k> on qubit q. k KNOWN, s HIDDEN."""
    qc.h(q); qc.p(2*np.pi*k*s/N, q)

def find_pair(k, N):
    """a sieve pair (a,b,herald) with a+b=k (h0) or a-b=k (h1) mod N, a,b in 1..N-1, != k."""
    for a in range(1, N):
        for b in range(1, N):
            if a == k or b == k: continue
            if (a+b) % N == k % N: return a, b, 0
            if (a-b) % N == k % N: return a, b, 1
    # fallback: k itself is a legitimately-measured coset state (0-round)
    return k, None, None

def known_phase(N, m, low_bits):
    """the phase Prod_{j<m} e^{i pi s_j / 2^{m-j}} to correct out of the k=2^{n-1-m} state."""
    th = 0.0
    for j, sj in enumerate(low_bits):      # low_bits[j] = s_j for j<m
        th += np.pi * sj / (2**(m-j))
    return th

def recover_bit_circuit(N, s, m, low_bits):
    """one circuit: sieve to k=2^{n-1-m}, phase-correct by low_bits, X-read -> s_m."""
    n = int(np.log2(N)); k = 2**(n-1-m)
    a, b, herald = find_pair(k, N)
    if b is None:                          # 0-round: raw coset state at k
        qc = QuantumCircuit(1, 1)
        coset(qc, 0, k, s, N)
        qc.p(-known_phase(N, m, low_bits), 0)
        qc.h(0); qc.measure(0, 0)
        return qc, None                    # no herald clbit
    qc = QuantumCircuit(2, 2)
    coset(qc, 0, a, s, N)                   # control
    coset(qc, 1, b, s, N)                   # target
    qc.cx(0, 1)                            # Kuperberg combination
    qc.measure(1, 1)                       # herald: 0->|psi_{a+b}>, 1->|psi_{a-b}>
    qc.p(-known_phase(N, m, low_bits), 0)  # correct known lower-bit phase
    qc.h(0); qc.measure(0, 0)              # X-read control = s_m (when heralded)
    return qc, herald

def recover_full(N, s, sim, shots, use_recovered=True):
    """recover all n bits of s. returns (recovered_s, per_bit_ok list vs TRUE bit)."""
    n = int(np.log2(N)); rec = []; per_bit_ok = []
    for m in range(n):
        low = rec if use_recovered else [ (s>>j)&1 for j in range(m) ]
        qc, herald = recover_bit_circuit(N, s, m, low)
        cts = sim.run(transpile(qc, sim), shots=shots).result().get_counts()
        # keep heralded shots (clbit1==herald) if there is a herald; read clbit0
        def bit0(key): return key.replace(' ', '')[-1]
        def bit1(key): return key.replace(' ', '')[-2]
        if herald is None:
            kept = cts
        else:
            kept = {k_: v for k_, v in cts.items() if bit1(k_) == str(herald)}
        tot = sum(kept.values()); ones = sum(v for k_, v in kept.items() if bit0(k_) == '1')
        b = 1 if tot and ones/tot > 0.5 else 0
        rec.append(b)
        per_bit_ok.append(b == ((s>>m) & 1))
    rs = sum(b << m for m, b in enumerate(rec))
    return rs, per_bit_ok

def run_case(N, sim, shots, label, use_recovered=True):
    n = int(np.log2(N)); full_ok = 0; bit_ok = 0; bit_tot = 0
    for s in range(N):
        rs, pb = recover_full(N, s, sim, shots, use_recovered)
        full_ok += (rs == s); bit_ok += sum(pb); bit_tot += n
    print(f"  [{label}] N={N}: full-string {full_ok}/{N} exact | per-bit {bit_ok}/{bit_tot} "
          f"({100*bit_ok/bit_tot:.1f}%)")
    return full_ok, N, bit_ok, bit_tot

def transpiled_cost(N, sim):
    qc, _ = recover_bit_circuit(N, 5 % N, 0, [])
    isa = transpile(qc, basis_gates=['cx','rz','sx','x','h'], optimization_level=1)
    twoq = sum(1 for i in isa.data if i.operation.name in ('cx','cz'))
    return twoq, isa.depth()

if __name__ == '__main__':
    ideal = AerSimulator()
    print("=== IDEAL SIM (full recovery, using RECOVERED lower bits = error-propagating) ===")
    run_case(8,  ideal, 8000, "ideal")
    run_case(16, ideal, 8000, "ideal")
    for N in (8, 16):
        t, d = transpiled_cost(N, ideal)
        print(f"  N={N} per-bit circuit transpiled: 2q={t}, depth={d}")

    # ---- noise: try from_backend noise model; fall back to representative ibm_fez ----
    print("\n=== NOISY SIM ===")
    noisy = None; src = None
    try:
        from qiskit_ibm_runtime import QiskitRuntimeService
        svc = QiskitRuntimeService()
        be = svc.backend('ibm_fez')
        nm = NoiseModel.from_backend(be)
        noisy = AerSimulator(noise_model=nm); src = 'from_backend ibm_fez (EXACT)'
    except Exception as e:
        print(f"  (from_backend unavailable: {str(e)[:70]}; using representative model)")
        from qiskit_aer.noise import depolarizing_error, ReadoutError
        nm = NoiseModel()
        nm.add_all_qubit_quantum_error(depolarizing_error(0.004, 2), ['cx'])
        nm.add_all_qubit_quantum_error(depolarizing_error(0.0004, 1), ['sx','x','h'])
        nm.add_all_qubit_readout_error(ReadoutError([[0.993,0.007],[0.007,0.993]]))
        noisy = AerSimulator(noise_model=nm); src = 'representative (0.4% 2q, 0.7% readout)'
    print(f"  noise source: {src}")
    run_case(8,  noisy, 20000, "noisy")
    run_case(16, noisy, 20000, "noisy")
