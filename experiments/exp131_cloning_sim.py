#!/usr/bin/env python3
"""exp131_cloning_sim.py — THE REPLICATOR'S LEGAL LIMIT: optimal universal
1->2 quantum cloning ceiling, sim tier (Whisper C4670, Horizons-3 H1;
substrate claude-opus-4-8).

THE LAW: no machine copies an unknown qubit perfectly (no-cloning), but the
universe LICENSES imperfect copying at an EXACT rate — the optimal symmetric
universal 1->2 cloner tops out at fidelity F = 5/6 = 0.8333 per copy, EQUAL
for every input state (universality). Proven optimal (Buzek-Hillery 1996;
Bruss et al.; Gisin-Massar). We certify the ceiling AND expose the only way to
"beat" it: a basis-reading cheat that scores >5/6 on one basis is detectably
BELOW it on the conjugate basis — universality is the certificate no cheat can
forge.

The optimal-cloner ancilla-prep angles are NOT taken from memory: this script
NUMERICALLY OPTIMIZES the prep to maximize the worst-case copy fidelity, and
the optimum lands on 5/6 (verified below), then freezes those angles.

Qubits: q0 = input (copy A out), q1 = blank (copy B out), q2 = ancilla.
Cloning network (fixed): CX(0,1) CX(0,2) CX(1,0) CX(2,0).
Prep (optimized, input-independent) on q1,q2.
Cheat: trivial CX(0,1) copy — F=1 on Z basis, F=1/2 on X basis.
"""
import json
import os

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import DensityMatrix, Statevector, partial_trace

HERE = os.path.dirname(os.path.abspath(__file__))

# 6 axis input states as (prep gate list on a 1q circuit, measure-basis tag)
AXIS = {
    "0": ([], "Z", 0), "1": ([("x", 0)], "Z", 1),
    "+": ([("h", 0)], "X", 0), "-": ([("x", 0), ("h", 0)], "X", 1),
    "+i": ([("h", 0), ("s", 0)], "Y", 0),
    "-i": ([("x", 0), ("h", 0), ("s", 0)], "Y", 1),
}


def input_sv(gates):
    qc = QuantumCircuit(1)
    for g, q in gates:
        getattr(qc, g)(q)
    return Statevector(qc)


def prep_circuit(params):
    """Input-independent ancilla prep on q1,q2 (q0 untouched). Angles found by
    the numerical optimizer below (objective = worst-case MEAN copy fidelity
    over the 6 axis states) — the optimum lands on the universal 5/6 cloner."""
    a, b, c, d = params
    qc = QuantumCircuit(3)
    qc.ry(a, 1)
    qc.ry(b, 2)
    qc.cx(1, 2)
    qc.ry(c, 1)
    qc.ry(d, 2)
    return qc


def cloner_circuit(params, input_gates):
    qc = QuantumCircuit(3)
    for g, q in input_gates:
        getattr(qc, g)(q)         # prepare input on q0
    qc.compose(prep_circuit(params), inplace=True)
    qc.cx(0, 1)
    qc.cx(0, 2)
    qc.cx(1, 0)
    qc.cx(2, 0)
    return qc


def copy_fidelities(params):
    """Mean copy fidelity (over A=q0, B=q1) for each axis state."""
    fids = {}
    for name, (gates, _, _) in AXIS.items():
        psi_in = input_sv(gates).data
        sv = Statevector(cloner_circuit(params, gates))
        dm = DensityMatrix(sv)
        rhoA = partial_trace(dm, [1, 2]).data
        rhoB = partial_trace(dm, [0, 2]).data
        fA = float(np.real(psi_in.conj() @ rhoA @ psi_in))
        fB = float(np.real(psi_in.conj() @ rhoB @ psi_in))
        fids[name] = (fA, fB)
    return fids


def worst_mean_fidelity(params):
    """Worst-case MEAN copy fidelity over the 6 axis states. Its maximum is the
    optimal UNIVERSAL cloner: flat across states (universality) at mean 5/6.
    A light symmetry tie-break keeps F_A ~ F_B."""
    fids = copy_fidelities(params)
    base = min((fA + fB) / 2 for fA, fB in fids.values())
    asym = max(abs(fA - fB) for fA, fB in fids.values())
    return base - 0.02 * asym


def optimize():
    """Coordinate-ascent from several seeds; target 5/6."""
    best, best_val = None, -1
    rng = np.random.default_rng(4670)
    seeds = [np.array([np.pi / 4] * 4)] + \
            [rng.uniform(0, np.pi, 4) for _ in range(8)]
    for x0 in seeds:
        x = x0.copy()
        val = worst_mean_fidelity(x)
        for _ in range(60):
            improved = False
            for i in range(4):
                for step in (0.3, 0.1, 0.03, 0.01):
                    for sgn in (+1, -1):
                        xt = x.copy()
                        xt[i] += sgn * step
                        vt = worst_mean_fidelity(xt)
                        if vt > val + 1e-9:
                            x, val, improved = xt, vt, True
            if not improved:
                break
        if val > best_val:
            best_val, best = val, x
    return best, best_val


def cheat_fidelities():
    """Trivial CX(0,1) cloner: F=1 on Z basis, 0.5 on X/Y."""
    fids = {}
    for name, (gates, _, _) in AXIS.items():
        psi_in = input_sv(gates).data
        qc = QuantumCircuit(2)
        for g, q in gates:
            getattr(qc, g)(q)
        qc.cx(0, 1)
        dm = DensityMatrix(Statevector(qc))
        rhoA = partial_trace(dm, [1]).data
        rhoB = partial_trace(dm, [0]).data
        fA = float(np.real(psi_in.conj() @ rhoA @ psi_in))
        fB = float(np.real(psi_in.conj() @ rhoB @ psi_in))
        fids[name] = (fA, fB)
    return fids


BASIS_ROT = {"Z": [], "X": [("h",)], "Y": [("sdg",), ("h",)]}


def measure_circuit(params, name, arm):
    """Prepare input |name>, clone (arm=optimal|cheat), rotate BOTH copies
    (q0,q1) into the input basis, measure both. Copy fidelity = P(match)."""
    gates, basis, expected = AXIS[name]
    nq = 3 if arm == "optimal" else 2
    qc = QuantumCircuit(nq, 2)
    for g, q in gates:
        getattr(qc, g)(0)
    qc.barrier()
    if arm == "optimal":
        qc.compose(prep_circuit(params), inplace=True)
        qc.cx(0, 1)
        qc.cx(0, 2)
        qc.cx(1, 0)
        qc.cx(2, 0)
    else:
        qc.cx(0, 1)
    qc.barrier()
    for q in (0, 1):
        for g in BASIS_ROT[basis]:
            getattr(qc, g[0])(q)
    qc.measure([0, 1], [0, 1])
    return qc, expected


def fake_preview(params):
    from qiskit import transpile
    from qiskit_aer import AerSimulator
    from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
    be = AerSimulator.from_backend(FakeMarrakesh())
    out = {}
    for arm in ("optimal", "cheat"):
        perbasis = {}
        for name, (_, basis, _) in AXIS.items():
            qc, exp = measure_circuit(params, name, arm)
            tqc = transpile(qc, be, optimization_level=1, seed_transpiler=4670,
                            initial_layout=[1, 0, 2][:qc.num_qubits])
            cts = be.run(tqc, shots=8000).result().get_counts()
            tot = sum(cts.values())
            fA = sum(v for k, v in cts.items() if k[::-1][0] == str(exp)) / tot
            fB = sum(v for k, v in cts.items() if k[::-1][1] == str(exp)) / tot
            perbasis.setdefault(basis, []).append((fA + fB) / 2)
        out[arm] = {b: float(np.mean(v)) for b, v in perbasis.items()}
    return out


def main():
    params, val = optimize()
    fids = copy_fidelities(params)
    mean_all = np.mean([(a + b) / 2 for a, b in fids.values()])
    var_all = np.var([(a + b) / 2 for a, b in fids.values()])
    print(f"OPTIMIZED prep angles: {[round(float(p), 5) for p in params]}")
    print(f"worst-mean fidelity = {val:.5f} (target 5/6 = {5/6:.5f})")
    print(f"universal mean = {mean_all:.5f}  cross-state var = {var_all:.2e}")
    for name, (fA, fB) in fids.items():
        print(f"  |{name:>2}>: F_A={fA:.4f} F_B={fB:.4f}")
    ch = cheat_fidelities()
    z_mean = np.mean([sum(ch[s]) / 2 for s in ("0", "1")])
    x_mean = np.mean([sum(ch[s]) / 2 for s in ("+", "-")])
    print(f"CHEAT (CX copy): Z-basis F={z_mean:.4f}  "
          f"X-basis F={x_mean:.4f}  (tell: {z_mean - x_mean:.4f})")
    fk = fake_preview(params)
    opt_min = min(fk["optimal"].values())
    opt_max = max(fk["optimal"].values())
    cheat_min = min(fk["cheat"].values())
    print(f"FAKE optimal per-basis: "
          f"{ {b: round(v, 4) for b, v in fk['optimal'].items()} } "
          f"(min {opt_min:.4f}, spread {opt_max-opt_min:.4f})")
    print(f"FAKE cheat   per-basis: "
          f"{ {b: round(v, 4) for b, v in fk['cheat'].items()} } "
          f"(min {cheat_min:.4f})")
    ok = (abs(val - 5 / 6) < 0.01 and var_all < 1e-3)
    print("DESIGN CHECK (F=5/6 universal, flat):", "PASS" if ok else "FAIL")
    out = {"prep_angles": [float(p) for p in params],
           "worst_mean_fidelity": float(val),
           "universal_mean": float(mean_all),
           "cross_state_var": float(var_all),
           "copy_fidelities": {k: [float(a), float(b)]
                               for k, (a, b) in fids.items()},
           "cheat": {"z_mean": float(z_mean), "x_mean": float(x_mean),
                     "tell": float(z_mean - x_mean)},
           "fake_preview": fk, "ceiling": 5 / 6, "design_valid": bool(ok)}
    json.dump(out, open(os.path.join(HERE, "..", "results",
                                     "exp131_feasibility.json"), "w"),
              indent=1, default=float)
    print("wrote results/exp131_feasibility.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
