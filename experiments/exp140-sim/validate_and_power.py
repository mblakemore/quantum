#!/usr/bin/env python3
"""Exp140 pre-flight validation + delta-power (Whisper C4744, advisor-gated before QPU).

HARD GATE 1 (estimator correctness): build a SMALL echo analog (statevector) and confirm the
mirror-parity estimator returns EXACTLY 1.0 noiselessly. If not, the 49q estimator is mis-built.

GATE 2 (delta power, NOT a beta reversal): the kill-gate validated the SIGNAL |f-1|; bridge A's
metric is the DELTA |dev_stack| - |dev_mit|. A mirror echo refocuses COHERENT error; only the
incoherent part survives, and global rescaling can collapse both arms toward 1.0 -> the delta may
be buried even when each arm's deviation isn't. Here we ASSUME a stack benefit (p_stack < p_mit)
purely to SIZE SHOTS (a budget question, we've already decided to fly) and report whether the
delta clears 3*SE at the ack budget.
"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, Operator
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

rng = np.random.default_rng(20260715)

# ---------- small echo analog: U (forward) . perturbation(disjoint) . U^dag (backward) ----------
# line of nq qubits; O = Z on obs (3 disjoint from pert). U = one brickwork layer of ZZ + X rots.
def u_layer(qc, qs, theta_zz=np.pi/4, theta_x=0.37):
    for i in range(0, len(qs)-1, 2):
        qc.rzz(2*theta_zz, qs[i], qs[i+1])
    for q in qs: qc.rx(2*theta_x, q)
    for i in range(1, len(qs)-1, 2):
        qc.rzz(2*theta_zz, qs[i], qs[i+1])

def build_echo(nq=8, L=2, obs=(5,6,7), pert=(0,1,2), delta=0.15, prep_bits=None):
    qs = list(range(nq))
    qc = QuantumCircuit(nq)
    if prep_bits:
        for b in prep_bits: qc.x(b)          # |z> prep = front X gates (bare QASM assumes |0..0>)
    for _ in range(L): u_layer(qc, qs)        # forward U
    for q in pert: qc.rz(2*delta, q)          # perturbation V_delta (Z-type, disjoint from O)
    # backward U^dag (inverse layers, reversed)
    for _ in range(L):
        # inverse of u_layer
        for i in range(1, len(qs)-1, 2): qc.rzz(-2*np.pi/4, qs[i], qs[i+1])
        for q in qs: qc.rx(-2*0.37, q)
        for i in range(0, len(qs)-1, 2): qc.rzz(-2*np.pi/4, qs[i], qs[i+1])
    return qc, obs

# ---------- mirror-parity estimator: f = <z| circuit |z> weighted, ideal = 1.0 ----------
def parity_expectation_sv(qc, obs):
    """noiseless: <O> under the echo starting from |0>. O=Z on obs. Ideal echo -> +1."""
    sv = Statevector.from_instruction(qc)
    # <Z_a Z_b Z_c> via diagonal Z-parity on the statevector probabilities
    probs = sv.probabilities_dict()
    e = 0.0
    for bitstr, p in probs.items():
        # qiskit bitstring is qN..q0 left-to-right; index from the right
        bits = bitstr[::-1]
        par = sum(int(bits[q]) for q in obs) % 2
        e += p * (1 if par == 0 else -1)
    return e

print("="*68)
print("GATE 1 — estimator returns 1.0 noiselessly (mirror echo, |0..0> input)")
qc, obs = build_echo()
f0 = parity_expectation_sv(qc, obs)
print(f"  noiseless <O> for the echo = {f0:+.6f}  (ideal 1.000000)")
# also a random |z> to confirm sigma_z-weighted estimator = 1
zbits = [1,3,4]
qcz, _ = build_echo(prep_bits=zbits)
fz = parity_expectation_sv(qcz, obs)
sigma_z = 1 if (sum(1 for b in zbits if b in obs) % 2)==0 else -1
print(f"  random z={zbits}: <O>={fz:+.6f}, sigma_z={sigma_z:+d}, sigma_z*<O>={sigma_z*fz:+.6f} (ideal +1)")
GATE1 = abs(f0-1.0) < 1e-9 and abs(sigma_z*fz - 1.0) < 1e-9
print(f"  GATE 1: {'PASS' if GATE1 else 'FAIL — estimator mis-built, do NOT fly'}")

# ---------- GATE 2 — delta power under noise + global rescaling ----------
print("="*68)
print("GATE 2 — delta power: does |dev_mit| - |dev_stack| clear 3*SE? (mirror refocus risk)")
def noisy_expectation(qc, obs, p2, shots=200000):
    nm = NoiseModel()
    nm.add_all_qubit_quantum_error(depolarizing_error(p2, 2), ['rzz'])
    nm.add_all_qubit_quantum_error(depolarizing_error(p2/10, 1), ['rx','rz'])
    sim = AerSimulator(noise_model=nm)
    mc = qc.copy(); mc.measure_all()
    from qiskit import transpile
    res = sim.run(transpile(mc, sim), shots=shots).result().get_counts()
    e=0.0; tot=sum(res.values())
    for bitstr,c in res.items():
        bits=bitstr[::-1]; par=sum(int(bits[q]) for q in obs)%2
        e += (c/tot)*(1 if par==0 else -1)
    return e

# scale the small-echo per-gate p so its total attenuation ~ matches the 49q lightcone at a given p_eff.
# small echo has ~ (L*2)*(nq-1) ~ 28 2q gates; 49q has N_eff=542. Use representative small-p to see the delta mechanics.
for p_mit, p_stack in [(5e-3,2e-3),(8e-3,3e-3)]:
    f_mit  = noisy_expectation(qc, obs, p_mit)
    f_stk  = noisy_expectation(qc, obs, p_stack)
    # global rescaling: divide by an estimated attenuation A_hat (here: from a mirror-cal = the same circuit's
    # measured f on a trusted-truth run; idealized as the arm's own decay -> rescales toward 1, leaving residual 0
    # in this homogeneous model). Report RAW deviations (rescaling residual is model-dependent; raw is the honest
    # visible signal and the conservative-large delta).
    dev_mit = abs(f_mit-1.0); dev_stk = abs(f_stk-1.0); delta = dev_mit-dev_stk
    for n_init,shots in [(24,4000),(30,8000)]:
        se3 = 3.0/np.sqrt(n_init*shots)
        verdict = "RESOLVABLE" if delta>se3 else "BURIED (<3SE)"
        print(f"  p_mit={p_mit:.0e} p_stk={p_stack:.0e}: f_mit={f_mit:.3f} f_stk={f_stk:.3f} "
              f"RAW delta={delta:.3f} | {n_init}x{shots} 3SE={se3:.4f} -> {verdict}")
print("\nNOTE: RAW delta (no rescaling) is the strawman the contenders' 'Global rescaling' removes.")
print("The honest hardware test still needs the rescaled-residual delta, which this homogeneous")
print("small model cannot produce (rescaling->0 residual). => the mirror-refocus/rescaling")
print("collapse risk the advisor flagged is REAL and only the hardware (heterogeneous) run resolves it.")
