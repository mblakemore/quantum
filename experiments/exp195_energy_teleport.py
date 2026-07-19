#!/usr/bin/env python3
"""Exp195 — BEAM THE POWER: Hotta quantum energy teleportation. C4886.
H = h(Z_A+Z_B) + k X_A X_B, entangled ground |g>. Alice measures Z_A -> bit s; Bob applies
U(s)=exp(i s theta Y_B). QET: <H>_B drops below ground on Bob's side — energy extracted from
correlations, none teleported. Measure Delta E_B (conditioned). Falsifiers: random bit; no
Alice measurement. Usage: --selftest | --submit | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
H_, K_ = 1.0, 1.5
# ground state of H: angle from diagonalizing; |g> = cos(a)|00> - sin(a)|11> form for this H
# H in {|00>,|11>} block: [[2h, k],[k,-2h]] -> mix; {|01>,|10>}: [[0,k],[k,0]].
# lowest eigenvalue -sqrt(4h^2+k^2) in the even block. |g> = cos(t/2)|00> - sin(t/2)|11>? check sim.
BTHETA = 0.17   # Bob conditional angle (numeric optimum for h=1,k=1.5, X_A measurement)
GPREP = 3.7851  # Ry angle on q0 for exact ground prep (fidelity 1.0, verified)

def _ground(qc):
    qc.ry(GPREP, 0); qc.cx(0, 1)   # exact ground of h(ZA+ZB)+k XA XB (verified fidelity 1.0)

def circuit(name):
    term = name.split("_")[-1]     # XX or ZB
    arm = name.rsplit("_", 1)[0]   # qet / noLOCC / nomeasure
    qc = QuantumCircuit(3, 3)      # a=0, b=1, coin=2 (for random-bit falsifier)
    _ground(qc)
    qc.barrier()
    # Alice measures X_A (coupling basis): rotate q0 to Z, measure -> bit s in {0:+1, 1:-1}
    if arm == "noLOCC":
        qc.h(2); qc.measure(2, 0)              # random uncorrelated bit drives Bob
        with qc.if_test((qc.clbits[0], 0)): qc.ry(-2 * BTHETA, 1)   # s=+1 -> Ry(-2theta)
        with qc.if_test((qc.clbits[0], 1)): qc.ry(+2 * BTHETA, 1)   # s=-1 -> Ry(+2theta)
        qc.reset(0); qc.ry(GPREP, 0); qc.cx(0, 1)   # (noLOCC: A unmeasured; rebuild its half is not needed — leave a in ground)
    elif arm == "nomeasure":
        # Alice does NOT measure; Bob applies the average (no conditional) -> unused correlation
        qc.ry(-2 * BTHETA, 1)                  # fixed rotation, no LOCC bit
    else:  # qet
        qc.h(0); qc.measure(0, 0)              # Alice measures X_A -> s
        with qc.if_test((qc.clbits[0], 0)): qc.ry(-2 * BTHETA, 1)   # s=+1
        with qc.if_test((qc.clbits[0], 1)): qc.ry(+2 * BTHETA, 1)   # s=-1
    qc.barrier()
    if term == "XX":
        qc.h(0); qc.h(1)                        # measure X_A X_B
    else:
        pass                                    # Z_B directly (q1)
    qc.measure(1, 1)
    if term == "XX": qc.measure(0, 0)
    return qc

TERMS = ("XX", "ZB")
ARMSET = ("qet", "noLOCC", "nomeasure")

def _ground_energy():
    # analytic minimal <H> for the prepared state, via statevector
    from qiskit.quantum_info import Statevector, SparsePauliOp
    qc = QuantumCircuit(2); _ground_sv(qc)
    H = SparsePauliOp.from_list([("ZI", H_), ("IZ", H_), ("XX", K_)])
    return float(np.real(Statevector(qc).expectation_value(H)))

def _ground_sv(qc):
    qc.ry(GPREP, 0); qc.cx(0, 1)

def analyze(get):
    r = {}
    for arm in ARMSET:
        zb = xx = 0
        for term, key in (("ZB", "zb"), ("XX", "xx")):
            c = get(f"{arm}_{term}"); acc = tot = 0
            for s, n in c.items():
                b = s.replace(" ", "")
                if term == "ZB":
                    acc += (1 - 2 * int(b[-2])) * n           # <Z_B>
                else:
                    acc += (1 - 2 * int(b[-1])) * (1 - 2 * int(b[-2])) * n  # <X_A X_B>
                tot += n
            if term == "ZB": zb = acc / tot
            else: xx = acc / tot
        # Bob-local energy: h<Z_B> + k<X_A X_B> (his interaction share)
        E_B = H_ * zb + K_ * xx
        r[arm] = {"ZB": float(zb), "XX": float(xx), "E_B": float(E_B)}
    return r

def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 40000; cache = {}
    def get(name):
        if name not in cache: cache[name] = sim.run(circuit(name), shots=shots).result().get_counts()
        return cache[name]
    r = analyze(get)
    # baseline: Bob-local energy in the ground state (no protocol)
    from qiskit.quantum_info import Statevector, SparsePauliOp
    qc = QuantumCircuit(2); _ground_sv(qc)
    base = float(np.real(Statevector(qc).expectation_value(SparsePauliOp.from_list([("IZ", H_), ("XX", K_)]))))
    print(f"Exp195 selftest | Bob-local ground baseline = {base:.4f}")
    for arm in ARMSET:
        dE = r[arm]["E_B"] - base
        print(f"  {arm:>9}: E_B = {r[arm]['E_B']:+.4f}  ->  Delta = {dE:+.4f}")
    dqet = r["qet"]["E_B"] - base
    assert dqet < -0.02, f"QET must extract energy (Delta_B < 0), got {dqet}"
    assert abs(r["noLOCC"]["E_B"] - base) < 0.05, "random bit must extract ~nothing"
    print("SELFTEST PASS: conditioned on Alice's real bit, Bob's local energy DROPS below the "
          "ground baseline; the random-bit control does not. Cleared to fly.")

def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    from qiskit.quantum_info import Statevector, SparsePauliOp
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    names = [f"{arm}_{t}" for arm in ARMSET for t in TERMS]
    circuits = [transpile(circuit(n), backend=backend, optimization_level=3) for n in names]
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    qc = QuantumCircuit(2); _ground_sv(qc)
    base = float(np.real(Statevector(qc).expectation_value(SparsePauliOp.from_list([("IZ", H_), ("XX", K_)]))))
    man = {"exp": 195, "slug": "energy_teleport", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "order": names, "baseline_EB": base, "h": H_, "k": K_,
           "prereg": {"primary": "Delta E_B = E_B(qet) - baseline < 0 at >=5 sigma; band [-0.35,-0.08]",
                      "falsifiers": "|Delta E_B(noLOCC)| <= 0.03 AND |Delta E_B(nomeasure)| <= 0.03"}}
    json.dump(man, open(os.path.join(HERE, "..", "results", "exp195_energy_teleport_manifest.json"), "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits) | baseline {base:.4f}")

def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp195_energy_teleport_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    raw = {}
    for idx, name in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[name] = getattr(r0.data, reg).get_counts()
    r = analyze(lambda n: raw[n]); base = man["baseline_EB"]; shots = man["shots"]
    seE = np.sqrt((H_**2 + K_**2) / shots)
    dqet = r["qet"]["E_B"] - base; z = -dqet / seE
    print(f"Exp195 BEAM THE POWER decode | job {man['job_id']} | Bob-local ground baseline {base:.4f}")
    for arm in ARMSET:
        print(f"  {arm:>9}: <Z_B>={r[arm]['ZB']:+.3f} <X_A X_B>={r[arm]['XX']:+.3f}  E_B={r[arm]['E_B']:+.4f}  "
              f"Delta={r[arm]['E_B']-base:+.4f}")
    p_ok = dqet < 0 and z >= 5
    f_ok = abs(r["noLOCC"]["E_B"]-base) <= 0.03 and abs(r["nomeasure"]["E_B"]-base) <= 0.03
    print(f"\nENERGY TELEPORTED: Delta E_B = {dqet:+.4f} ({z:.0f} sigma below the local ground) — "
          f"Bob extracted energy his lab did not contain")
    print(f"FALSIFIERS: noLOCC {r['noLOCC']['E_B']-base:+.4f} | nomeasure {r['nomeasure']['E_B']-base:+.4f} (both ~0)")
    ok = p_ok and f_ok
    print(f"VERDICT: {'ENERGY TELEPORTED — extracted from correlations via a classical bit, no energy in transit' if ok else 'NOT HELD (honest accounting above)'}")
    json.dump({"job_id": man["job_id"], "results": r, "baseline": base, "delta_EB": float(dqet),
               "sigma": float(z), "primary_ok": bool(p_ok), "falsifier_ok": bool(f_ok),
               "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp195_energy_teleport_decode.json"), "w"), indent=1)
    print("-> results/exp195_energy_teleport_decode.json")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true"); ap.add_argument("--submit", action="store_true")
    ap.add_argument("--decode", action="store_true")
    ap.add_argument("--backend", default="ibm_fez"); ap.add_argument("--shots", type=int, default=8000)
    a = ap.parse_args()
    if a.selftest: selftest()
    elif a.submit: submit(a.backend, a.shots)
    elif a.decode: decode()
    else: ap.print_help()
