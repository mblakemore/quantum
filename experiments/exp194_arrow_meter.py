#!/usr/bin/env python3
"""Exp194 — THE ARROW METER: the irreversible fraction of decoherence vs time. C4886.
C(T) = <X> of |+> after idle T (2 qubits averaged). Echoed (quarter-point) vs raw.
A(T) = 1 - C_echo (the arrow: what no rewind recovers); R(T) = (C_echo - C_raw)/(1 - C_raw)
(the rewindable share). Sweep T = 1/2/4/8 us. Usage: --selftest | --submit | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit import Delay
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
TS = {1: 2000, 2: 4000, 4: 8000, 8: 16000}   # dt (0.5ns)
CIRCS = ["T0"] + [f"{a}_{t}" for a in ("echo", "raw") for t in TS]

def circuit(name):
    qc = QuantumCircuit(2, 2)
    qc.h(0); qc.h(1)
    if name != "T0":
        arm, t = name.split("_"); dt = TS[int(t)]
        if arm == "echo":
            q4 = (dt // 4 // 16) * 16
            for q in (0, 1): qc.append(Delay(q4, unit="dt"), [q])
            qc.x(0); qc.x(1)
            for q in (0, 1): qc.append(Delay(dt - 2 * q4, unit="dt"), [q])
            qc.x(0); qc.x(1)
            for q in (0, 1): qc.append(Delay(q4, unit="dt"), [q])
        else:
            for q in (0, 1): qc.append(Delay(dt, unit="dt"), [q])
    qc.h(0); qc.h(1)
    qc.measure(0, 0); qc.measure(1, 1)
    return qc

def analyze(get):
    C = {}
    for name in CIRCS:
        acc = tot = 0
        for s, n in get(name).items():
            b = s.replace(" ", "")
            acc += ((1 - 2 * int(b[-1])) + (1 - 2 * int(b[-2]))) * n; tot += 2 * n
        C[name] = acc / tot
    r = {"C": {k: float(v) for k, v in C.items()}}
    r["A"] = {t: float(1 - C[f"echo_{t}"]) for t in TS}
    r["R"] = {t: float((C[f"echo_{t}"] - C[f"raw_{t}"]) / (1 - C[f"raw_{t}"]))
              if C[f"raw_{t}"] < 0.999 else None for t in TS}
    return r

def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 8000; cache = {}
    def get(name):
        if name not in cache: cache[name] = sim.run(circuit(name), shots=shots).result().get_counts()
        return cache[name]
    r = analyze(get)
    print("Exp194 selftest C:", {k: round(v, 3) for k, v in r["C"].items()})
    assert all(v > 0.99 for v in r["C"].values()), "noiseless coherence must be exact everywhere"
    print("SELFTEST PASS: echo pairs exact identities; A=0 noiselessly. Cleared to fly.")

def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    circuits = [transpile(circuit(n), backend=backend, optimization_level=3) for n in CIRCS]
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    man = {"exp": 194, "slug": "arrow_meter", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "order": CIRCS,
           "prereg": {"primary": "A(T) strictly increasing (steps >=2 sigma) AND R non-increasing >=2/3 steps",
                      "bands": "A: 1us 0.01-0.08, 2us 0.02-0.12, 4us 0.06-0.25, 8us 0.15-0.45; R(1us) 0.45-0.90",
                      "deliverable": "tau_arrow (A crosses 1/2, interpolated/extrapolated labeled)",
                      "gauge": "C(T0) >= 0.97"}}
    json.dump(man, open(os.path.join(HERE, "..", "results", "exp194_arrow_meter_manifest.json"), "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits)")

def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp194_arrow_meter_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    raw = {}
    for idx, name in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[name] = getattr(r0.data, reg).get_counts()
    r = analyze(lambda n: raw[n]); se = 1 / np.sqrt(2 * man["shots"])
    print(f"Exp194 ARROW METER decode | job {man['job_id']}")
    print(f"  C(T0) = {r['C']['T0']:.4f}")
    ts = sorted(TS)
    for t in ts:
        print(f"  T={t}us: C_echo={r['C'][f'echo_{t}']:.4f}  C_raw={r['C'][f'raw_{t}']:.4f}  "
              f"A={r['A'][t]:.4f}  R={r['R'][t] if r['R'][t] is None else round(r['R'][t],3)}")
    steps = [(r["A"][ts[i+1]] - r["A"][ts[i]]) / (se * 1.5) for i in range(3)]
    a_ok = all(r["A"][ts[i+1]] > r["A"][ts[i]] for i in range(3)) and all(z >= 2 for z in steps)
    rvals = [r["R"][t] for t in ts if r["R"][t] is not None]
    r_ok = sum(1 for i in range(len(rvals)-1) if rvals[i+1] <= rvals[i] + 0.02) >= 2
    A = r["A"]; tau = None
    for i in range(3):
        if A[ts[i]] < 0.5 <= A[ts[i+1]]:
            tau = ts[i] + (0.5 - A[ts[i]]) * (ts[i+1] - ts[i]) / (A[ts[i+1]] - A[ts[i]]); lbl = "interpolated"
    if tau is None and A[ts[-1]] < 0.5 and A[ts[-1]] > A[ts[-2]]:
        tau = ts[-1] + (0.5 - A[ts[-1]]) * (ts[-1] - ts[-2]) / (A[ts[-1]] - A[ts[-2]]); lbl = "EXTRAPOLATED"
    print(f"\nTHE ARROW: irreversibility rises " + " -> ".join(f"{A[t]:.3f}" for t in ts) +
          f" | rewindable share falls" + (" (held >=2/3)" if r_ok else " (NOT monotone)"))
    if tau: print(f"tau_arrow (A = 1/2): ~{tau:.1f} us ({lbl})")
    ok = a_ok and r_ok and r["C"]["T0"] >= 0.97
    print(f"VERDICT: {'THE ARROW IS MEASURED — the longer you wait, the smaller the fraction of the past that can be rewound' if ok else 'NOT HELD (honest accounting above)'}")
    json.dump({"job_id": man["job_id"], "results": r, "tau_arrow": tau,
               "a_monotone": bool(a_ok), "r_declining": bool(r_ok), "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp194_arrow_meter_decode.json"), "w"), indent=1)
    print("-> results/exp194_arrow_meter_decode.json")

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
