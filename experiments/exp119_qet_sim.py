#!/usr/bin/env python3
"""exp119_qet_sim.py — Certified Quantum Energy Teleportation, sim tier
(Whisper C4639, horizons-2 Q1, Creator "Run it!").

Hotta minimal QET model (2 qubits), h = k = 1:
  H_A = Z_A + c1,  H_B = Z_B + c1,  V = 2 X_A X_B + c2
  offsets c1 = h^2/sqrt(h^2+k^2) = 1/sqrt(2), c2 = 2k^2/sqrt(h^2+k^2) = sqrt(2)
  chosen so <g|H_A|g> = <g|H_B + V|g> = 0 in the ground state |g>.

Protocol: Alice measures X_A (deposits energy E_A at A), sends the 1-bit outcome
mu; Bob applies Ry(2*mu*theta). Theory: Bob's LOCAL energy E_B = <H_B + V> goes
NEGATIVE — energy extracted at B from classical information alone, and B's
region dips below the local ground level (the exotic-matter flavor).

DERIVATION DISCIPLINE (C4558): nothing below trusts a recalled closed form.
Exact energies come from statevector expectation of the Hamiltonian terms;
theta* comes from a numerical scan (argmin E_B), not a remembered formula.

This tier outputs (results/exp119_feasibility.json):
  - exact E_A / E_B for every arm (ground, qet+, qet-(sign check), scram, def)
  - theta* from the scan and the closed-form candidate for comparison
  - estimator SEs at budget from sampled counts (noiseless + FakeMarrakesh)
  - attenuation preview: FakeMarrakesh E_B vs exact (the W2-risk number)
"""
import json
import os

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector

HERE = os.path.dirname(os.path.abspath(__file__))
H_ = 1.0
K_ = 1.0
NRM = np.sqrt(H_**2 + K_**2)
C1 = H_**2 / NRM
C2 = 2 * K_**2 / NRM
SHOTS = 30000

# ground state of H = Z0 + Z1 + 2 X0X1 + consts (computed, not recalled):
# diagonalize the 4x4 directly.
Z = np.diag([1., -1.])
X = np.array([[0., 1.], [1., 0.]])
I2 = np.eye(2)
HAM = (np.kron(Z, I2) + np.kron(I2, Z) + 2 * np.kron(X, X)
       + (2 * C1 + C2) * np.eye(4))
EVAL, EVEC = np.linalg.eigh(HAM)
G = EVEC[:, 0]                      # ground vector (qubit order: A=q0 kron B=q1)
assert abs(EVAL[0]) < 1e-12, f"offsets should zero the ground energy, got {EVAL[0]}"

# H_B + V and H_A as matrices (A first factor, B second)
HB_V = (np.kron(I2, Z) + 2 * np.kron(X, X)) + (C1 + C2) * np.eye(4)
HA = np.kron(Z, I2) + C1 * np.eye(4)


def prep_angle():
    """|g> = cos(a)|00> - sin(a)|11> — recover a from the eigenvector."""
    # components: G[0] ~ |00>, G[3] ~ |11| (basis order 00,01,10,11)
    a = np.arctan2(-G[3], G[0])
    assert abs(G[1]) + abs(G[2]) < 1e-12
    return a


ALPHA = prep_angle()


def prep(qc, a=None):
    a = ALPHA if a is None else a
    qc.ry(-2 * a, 0)     # cos|0> - sin|1>  (A = qubit 0)
    qc.cx(0, 1)


def sv_energy(theta, mode):
    """Exact post-protocol <H_B+V>, <H_A> by direct statevector computation.
    mode: 'ground' (no ops) | 'qet' (X-meas + conditional Ry(2*mu*theta)) |
    'scram' (X-meas + Ry with mu replaced by an independent fair coin)."""
    qc = QuantumCircuit(2)
    prep(qc)
    psi = Statevector(qc).data          # order |q1 q0> in qiskit; careful below
    # qiskit statevector index bit order: q1 q0 -> map to (A=q0, B=q1) as
    # amp[a,b] with index = b*2 + a
    amp = np.array([psi[0], psi[2], psi[1], psi[3]])   # (00,01,10,11) A-first
    if mode == "ground":
        rho = np.outer(amp, amp.conj())
    else:
        # project A onto |+/-> (X measurement)
        plus = np.array([1., 1.]) / np.sqrt(2)
        minus = np.array([1., -1.]) / np.sqrt(2)
        rho = np.zeros((4, 4), dtype=complex)
        for mu, vec in ((+1, plus), (-1, minus)):
            P = np.kron(np.outer(vec, vec.conj()), I2)
            branch = P @ amp
            p = np.vdot(branch, branch).real
            if p < 1e-15:
                continue
            if mode == "qet":
                th = mu * theta
            elif mode == "scram":
                th = None               # handled below (coin average)
            if mode == "scram":
                for coin in (+1, -1):
                    U = np.kron(I2, ry_mat(2 * coin * theta))
                    b2 = U @ branch
                    rho += 0.5 * np.outer(b2, b2.conj())
                continue
            U = np.kron(I2, ry_mat(2 * th))
            b2 = U @ branch
            rho += np.outer(b2, b2.conj())
    eb = np.trace(rho @ HB_V).real
    ea = np.trace(rho @ HA).real
    return eb, ea


def ry_mat(t):
    return np.array([[np.cos(t / 2), -np.sin(t / 2)],
                     [np.sin(t / 2), np.cos(t / 2)]])


def build(arm, basis, theta):
    """Flight circuits. arms: ground | qet_ff | qet_def | fixp | fixm.
    basis: zb (measure Z on A,B) | xx (measure X on A?,B).
    ff arms: mid-circuit X measurement of A -> c0, conditional Ry on B."""
    qc = QuantumCircuit(2, 3)   # c0 = Alice X outcome, c1 = A final, c2 = B final
    prep(qc)
    if arm != "ground":
        qc.h(0)
        qc.measure(0, 0)        # Alice X-basis outcome (0 -> mu=+1)
        if arm == "qet_ff":
            with qc.if_test((qc.clbits[0], 0)):
                qc.ry(2 * theta, 1)
            with qc.if_test((qc.clbits[0], 1)):
                qc.ry(-2 * theta, 1)
        elif arm == "fixp":
            qc.ry(2 * theta, 1)
        elif arm == "fixm":
            qc.ry(-2 * theta, 1)
    if basis == "zb":
        if arm != "ground":
            qc.measure(0, 1)    # <Z_A> post-protocol
        else:
            qc.measure(0, 1)
        qc.measure(1, 2)
    else:                        # xx: X_A from c0 (ff) or final H-measure
        if arm == "ground":
            qc.h(0)
            qc.measure(0, 1)
        qc.h(1)
        qc.measure(1, 2)
    return qc


def build_def_cry(basis, theta):
    """Deferred-measurement arm: coherent controlled rotation, no mid-circuit
    measure. Ry(2t) then CRy(-4t): A=0 -> net +2t, A=1 -> net -2t."""
    qc = QuantumCircuit(2, 3)
    prep(qc)
    qc.h(0)
    qc.ry(2 * theta, 1)
    qc.cry(-4 * theta, 0, 1)    # A=0: +2t ; A=1: +2t-4t = -2t  ✓
    qc.measure(0, 0)            # record mu after control (Z basis = X outcome)
    if basis == "zb":
        qc.measure(1, 2)
        # <Z_A>: A was H'ed; its Z now = X of original — cannot recover Z_A here.
    else:
        qc.h(1)
        qc.measure(1, 2)
    return qc


def counts_energy(counts_zb, counts_xx, arm):
    """E_B, E_A and SEs from two-basis counts. Convention: bitstrings are
    c2 c1 c0 (qiskit right-to-left clbit order)."""
    def expec(counts, which):
        n = tot = 0
        for k, v in counts.items():
            tot += v
            if which == "zb_B":
                bit = int(k[0])                    # c2 = B final (Z)
                n += v * (1 - 2 * bit)
            elif which == "zb_A":
                bit = int(k[1])                    # c1 = A final (Z)
                n += v * (1 - 2 * bit)
            elif which == "xx":
                bB = int(k[0])
                if arm == "ground" or arm == "qet_def":
                    bA = int(k[1]) if arm == "ground" else int(k[2])
                else:
                    bA = int(k[2])                 # c0 = Alice X outcome
                n += v * (1 - 2 * bB) * (1 - 2 * bA)
        return n / tot, tot
    zB, nz = expec(counts_zb, "zb_B")
    xx, nx = expec(counts_xx, "xx")
    eb = zB + 2 * xx + C1 + C2
    se = np.sqrt((1 - zB * zB) / nz + 4 * (1 - xx * xx) / nx)
    if arm in ("ground", "qet_ff", "fixp", "fixm"):
        zA, _ = expec(counts_zb, "zb_A")
        ea = zA + C1
    else:
        ea = None
    return eb, se, ea


def main():
    from qiskit_aer import AerSimulator
    # 1) theta scan (exact) — freeze theta* by argmin, not by formula
    grid = np.linspace(0.01, 0.6, 60)
    ebs = [sv_energy(t, "qet")[0] for t in grid]
    tstar = float(grid[int(np.argmin(ebs))])
    fine = np.linspace(max(0.01, tstar - 0.02), tstar + 0.02, 81)
    ebs_f = [sv_energy(t, "qet")[0] for t in fine]
    tstar = float(fine[int(np.argmin(ebs_f))])
    exact = {
        "theta_star": tstar,
        "alpha_prep": float(ALPHA),
        "E_B_ground": sv_energy(tstar, "ground")[0],
        "E_A_ground": sv_energy(tstar, "ground")[1],
        "E_B_qet": float(min(ebs_f)),
        "E_A_qet": sv_energy(tstar, "qet")[1],
        "E_B_scram": sv_energy(tstar, "scram")[0],
    }
    print("EXACT:", json.dumps(exact, indent=1))
    assert exact["E_B_qet"] < -0.05, "dip too small — model wired wrong?"
    assert abs(exact["E_B_ground"]) < 1e-9
    assert exact["E_B_scram"] > exact["E_B_qet"] + 0.05

    # 2) sampled tiers
    out = {"exact": exact}
    for label, backend in (("noiseless", AerSimulator()),
                           ("fakemarrakesh", None)):
        if label == "fakemarrakesh":
            from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
            backend = AerSimulator.from_backend(FakeMarrakesh())
        res = {}
        for arm in ("ground", "qet_ff", "qet_def", "fixp", "fixm"):
            cts = {}
            for basis in ("zb", "xx"):
                qc = (build_def_cry(basis, tstar) if arm == "qet_def"
                      else build(arm, basis, tstar))
                tqc = transpile(qc, backend, optimization_level=1,
                                seed_transpiler=4639,
                                initial_layout=[0, 1]
                                if label != "noiseless" else None)
                cts[basis] = backend.run(tqc, shots=SHOTS).result().get_counts()
            eb, se, ea = counts_energy(cts["zb"], cts["xx"], arm)
            res[arm] = {"E_B": eb, "SE": se, "E_A": ea}
            print(f"[{label}] {arm:8s} E_B={eb:+.4f}±{se:.4f}"
                  + (f"  E_A={ea:+.4f}" if ea is not None else ""))
        res["E_B_scram_pooled"] = 0.5 * (res["fixp"]["E_B"] + res["fixm"]["E_B"])
        out[label] = res

    # 3) headline preview numbers
    fm = out["fakemarrakesh"]
    out["preview"] = {
        "diff_ff_vs_ground": fm["qet_ff"]["E_B"] - fm["ground"]["E_B"],
        "diff_ff_vs_scram": fm["qet_ff"]["E_B"] - fm["E_B_scram_pooled"],
        "attenuation_note": "noise adds POSITIVE bias to every E_B (constant "
                            "offsets don't attenuate) — one-sided-safe: noise "
                            "cannot manufacture a dip",
    }
    print("PREVIEW:", json.dumps(out["preview"], indent=1, default=float))
    json.dump(out, open(os.path.join(HERE, "..", "results",
                                     "exp119_feasibility.json"), "w"),
              indent=1, default=float)
    print("wrote results/exp119_feasibility.json")


if __name__ == "__main__":
    main()
