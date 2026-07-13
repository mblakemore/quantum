#!/usr/bin/env python3
"""exp122_twin_paradox_sim.py — proper-time interferometer, sim tier
(Whisper C4649, horizons-2 Q4). Design: exp122-twin-paradox-design.md.

The quantum twin paradox, information-theoretic core: a path qubit C in
superposition routes an EXCITED clock K through two physical lanes with
different T1 (CSWAP out, shared delay, CSWAP back). The clock's aging marks
the path via spontaneous emission into lane-distinct baths. Law to verify
IN-CODE (C4558 — no recalled formula trusted):
    V(dt) = <X_C> = sqrt(p0 * p1),   p_i = exp(-dt/T1_lane_i)
with the vacuum-twin arm (clock |0>) as the common-mode baseline divisor:
    R(dt) = V_exc / V_vac -> sqrt(p0 p1) (C-dephasing divided out).

Tier 1: exact density-matrix with parametric amplitude damping per branch.
Tier 2: FakeMarrakesh sampled at budget (checks delay relaxation is modeled;
if delays don't decay on fake, flags SIM-GAP and tier 2 is scan-only)."""
import json
import os

import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = 20000


# ---------- Tier 1: exact law by direct Kraus computation ----------
def kraus_ad(gamma):
    K0 = np.array([[1, 0], [0, np.sqrt(1 - gamma)]])
    K1 = np.array([[0, np.sqrt(gamma)], [0, 0]])
    return [K0, K1]


def exact_V(gamma_K, gamma_L, excited=True):
    """Careful accounting (C4649, derived not recalled). Position basis
    (K-pos, L-pos); baths are PHYSICAL (attached to positions).
    Branch C=0: clock stays at K-pos -> damped by K-bath (outcome iK);
                |0> at L-pos -> L-bath outcome iL (nonzero only iL=0).
    Branch C=1: clock travels to L-pos -> damped by L-bath (outcome jL);
                |0> at K-pos (jK, nonzero only jK=0); swap-back returns the
                clock to the K slot, so b1 = kron(kL[jL]clock, kK[jK]|0>).
    Coherence survives only where BOTH physical baths hold identical
    records: iK == jK and iL == jL.
    """
    import itertools
    kK = kraus_ad(gamma_K)
    kL = kraus_ad(gamma_L)
    clock = np.array([0.0, 1.0]) if excited else np.array([1.0, 0.0])
    zero = np.array([1.0, 0.0])
    coh = 0.0 + 0.0j
    for iK, iL, jK, jL in itertools.product(range(2), repeat=4):
        if iK != jK or iL != jL:
            continue
        b0 = np.kron(kK[iK] @ clock, kL[iL] @ zero)
        b1 = np.kron(kL[jL] @ clock, kK[jK] @ zero)
        coh += np.vdot(b1, b0)
    return float(np.real(coh))


def law_check():
    """Verify V = sqrt(p0 p1) for excited, V = 1 for vacuum, numerically."""
    rows = []
    ok = True
    for gK, gL in ((0.1, 0.3), (0.2, 0.2), (0.5, 0.05), (0.0, 0.4)):
        v_exc = exact_V(gK, gL, excited=True)
        v_vac = exact_V(gK, gL, excited=False)
        pred = np.sqrt((1 - gK) * (1 - gL))
        rows.append({"gK": gK, "gL": gL, "V_exc": v_exc, "V_vac": v_vac,
                     "sqrt_p0p1": float(pred)})
        ok &= abs(v_exc - pred) < 1e-12 and abs(v_vac - 1.0) < 1e-12
    return ok, rows


# ---------- circuits (byte-identical builders for flight) ----------
def build(excited, dt_us, measure_clock=False):
    """C=0? K stays home (K-pos). C=1: clock travels to L-pos.
    Qubits: 0=C, 1=K(home lane / clock slot), 2=L(travel lane).
    clbits: c0=C(X basis), c1=K(Z), c2=L(Z)."""
    qc = QuantumCircuit(3, 3)
    qc.h(0)
    if excited:
        qc.x(1)
    qc.cswap(0, 1, 2)
    qc.barrier()                      # structure-invariant: prevents CSWAP
    if dt_us > 0:                     # cancellation at dt=0 (C4650 audit catch)
        qc.delay(int(dt_us * 1000), 1, unit="ns")
        qc.delay(int(dt_us * 1000), 2, unit="ns")
    qc.barrier()
    qc.cswap(0, 1, 2)
    qc.h(0)
    qc.measure(0, 0)
    qc.measure(1, 1)
    qc.measure(2, 2)
    return qc


def build_calib(qubit_virtual, dt_us):
    """T1 calibration: excite, delay, measure (virtual 1=K-pos or 2=L-pos)."""
    qc = QuantumCircuit(3, 3)
    qc.x(qubit_virtual)
    if dt_us > 0:
        qc.delay(int(dt_us * 1000), qubit_virtual, unit="ns")
    qc.measure(qubit_virtual, qubit_virtual)
    return qc


def vis_from_counts(counts):
    n = p = 0
    for k, v in counts.items():
        n += v
        if k[2] == "0":            # c0 = C in X basis; 0 <-> +
            p += v
    return 2 * p / n - 1, float(np.sqrt(max(1e-12, (1 - (2 * p / n - 1)**2))
                                        / n))


def main():
    ok, rows = law_check()
    print("LAW CHECK (density-matrix, parametric):",
          "PASS" if ok else "FAIL")
    for r in rows:
        print("  ", json.dumps(r, default=float))
    out = {"law_check_pass": ok, "law_rows": rows}
    if not ok:
        json.dump(out, open(os.path.join(
            HERE, "..", "results", "exp122_feasibility.json"), "w"), indent=1)
        raise SystemExit("law check failed — design wrong, stop")

    # Tier 2: FakeMarrakesh — does the noise model decay delays?
    from qiskit_aer import AerSimulator
    from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
    fake = FakeMarrakesh()
    backend = AerSimulator.from_backend(fake)
    # empirical T1 probe on the fake: survival after 100us
    surv = {}
    for vq in (1, 2):
        qc = build_calib(vq, 100.0)
        tqc = transpile(qc, backend, optimization_level=1,
                        seed_transpiler=4649, initial_layout=[0, 1, 2],
                        scheduling_method="asap")
        cts = backend.run(tqc, shots=SHOTS).result().get_counts()
        alive = sum(v for k, v in cts.items() if k[2 - vq] == "1")
        surv[f"q{vq}_100us"] = alive / SHOTS
    print("fake survival at 100us:", surv)
    delay_modeled = any(s < 0.95 for s in surv.values())
    out["fake_delay_modeled"] = delay_modeled
    out["fake_survival_100us"] = surv

    if delay_modeled:
        ladder = [0.0, 25.0, 50.0, 100.0, 200.0]
        res = {}
        for excited in (True, False):
            curve = []
            for dt in ladder:
                qc = build(excited, dt)
                tqc = transpile(qc, backend, optimization_level=1,
                                seed_transpiler=4649,
                                initial_layout=[0, 1, 2],
                                scheduling_method="asap")
                cts = backend.run(tqc, shots=SHOTS).result().get_counts()
                v, se = vis_from_counts(cts)
                curve.append({"dt_us": dt, "V": v, "SE": se})
            res["excited" if excited else "vacuum"] = curve
            print(("excited" if excited else "vacuum"), "curve:",
                  json.dumps(curve, default=float))
        out["fakemarrakesh"] = res
    else:
        print("SIM-GAP: fake model does not decay delays — hardware-only "
              "law test; tier 2 limited to transpile audit (friction-01 "
              "class, flag in prereg)")
        qc = build(True, 100.0)
        tqc = transpile(qc, backend, optimization_level=1,
                        seed_transpiler=4649, initial_layout=[0, 1, 2],
                        scheduling_method="asap")
        n2 = sum(1 for i in tqc.data if i.operation.num_qubits == 2
                 and i.operation.name != "barrier")
        out["transpile_2q_per_pub"] = n2
        print(f"transpile audit: 2q per interferometer pub = {n2}")

    json.dump(out, open(os.path.join(HERE, "..", "results",
                                     "exp122_feasibility.json"), "w"),
              indent=1, default=float)
    print("wrote results/exp122_feasibility.json")


if __name__ == "__main__":
    main()
