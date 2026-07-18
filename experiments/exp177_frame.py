#!/usr/bin/env python3
"""Exp177 — THE PAULI FRAME: buy the composition tax back by deferring corrections. C4864.
Exp176 showed the tax compounds with live feedforward windows. But swap corrections are PAULI
corrections — they commute through Cliffords as a classically-tracked frame, applied in software
at decode (the standard FT/network practice). Four arms decompose the 2-swap chain's deficit:
  live       — Exp176 swap2 replica (mid-circuit measure + live feedforward x2)
  deferred   — mid-circuit measures, NO if_tests; frame applied per-shot in decode
  endmeasure — no mid-circuit measurement at all (everything in the final layer) + frame
  direct     — Bell floor
Frame on D: x = c3^c1, z = c2^c0  ->  flip D's bit by: ZZ c3^c1 | XX c2^c0 | YY c0^c1^c2^c3.
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
from exp162_swap import fidelity

ARMS = ("live", "deferred", "endmeasure", "direct")
FRAMED = ("deferred", "endmeasure")
SETTINGS = ("ZZ", "XX", "YY")
WITNESS = 0.5


def _verify_rot(qc, setting, qubits):
    for q in qubits:
        if setting == "XX": qc.h(q)
        elif setting == "YY": qc.sdg(q); qc.h(q)


def chain_circuit(arm, setting):
    """A=q0,B1=q1,B2=q2,C1=q3,C2=q4,D=q5. clbits c0,c1 stage1; c2,c3 stage2; c4=A, c5=D."""
    qc = QuantumCircuit(6, 6)
    if arm == "direct":
        qc.h(0); qc.cx(0, 1)
        _verify_rot(qc, setting, (0, 1))
        qc.measure(0, 4); qc.measure(1, 5)
        return qc
    qc.h(0); qc.cx(0, 1)          # Bell(A,B1)
    qc.h(2); qc.cx(2, 3)          # Bell(B2,C1)
    qc.h(4); qc.cx(4, 5)          # Bell(C2,D)
    qc.barrier()
    qc.cx(1, 2); qc.h(1)          # stage-1 Bell-basis rotation
    if arm != "endmeasure":
        qc.measure(1, 0); qc.measure(2, 1)
        if arm == "live":
            with qc.if_test((qc.clbits[1], 1)): qc.x(3)
            with qc.if_test((qc.clbits[0], 1)): qc.z(3)
    qc.barrier()
    qc.cx(3, 4); qc.h(3)          # stage-2 Bell-basis rotation
    if arm != "endmeasure":
        qc.measure(3, 2); qc.measure(4, 3)
        if arm == "live":
            with qc.if_test((qc.clbits[3], 1)): qc.x(5)
            with qc.if_test((qc.clbits[2], 1)): qc.z(5)
    qc.barrier()
    _verify_rot(qc, setting, (0, 5))
    if arm == "endmeasure":       # everything lands in one final measurement layer
        qc.measure(1, 0); qc.measure(2, 1); qc.measure(3, 2); qc.measure(4, 3)
    qc.measure(0, 4); qc.measure(5, 5)
    return qc


def _parity(counts, shots, setting, arm):
    """<A D> from c4,c5 with per-shot Pauli-frame correction for FRAMED arms.
    Bitstring 'c5c4c3c2c1c0'."""
    acc = 0
    for b, n in counts.items():
        b = b.replace(" ", "")
        a = int(b[-5]); d = int(b[-6])
        if arm in FRAMED:
            c0, c1, c2, c3 = int(b[-1]), int(b[-2]), int(b[-3]), int(b[-4])
            if setting == "ZZ": d ^= c3 ^ c1
            elif setting == "XX": d ^= c2 ^ c0
            else: d ^= c0 ^ c1 ^ c2 ^ c3
        acc += (1 - 2 * a) * (1 - 2 * d) * n
    return acc / shots


def analyze(get, shots):
    out = {}
    for arm in ARMS:
        par = {s: _parity(get(arm, s), shots, s, arm) for s in SETTINGS}
        out[arm] = {"F": float(fidelity(par)), **{k: float(v) for k, v in par.items()}}
    return out


def decomposition(r, shots):
    se_F = 0.75 / np.sqrt(shots); se_d = float(np.sqrt(2) * se_F)
    d_lat = r["deferred"]["F"] - r["live"]["F"]
    d_meas = r["endmeasure"]["F"] - r["deferred"]["F"]
    d_circ = r["direct"]["F"] - r["endmeasure"]["F"]
    total = r["endmeasure"]["F"] - r["live"]["F"]
    frac = d_lat / total if abs(total) > 1e-9 else float("nan")
    return {"delta_latency": float(d_lat), "delta_latency_sigma": float(d_lat / se_d),
            "delta_measure": float(d_meas), "delta_measure_sigma": float(d_meas / se_d),
            "delta_circuit": float(d_circ), "se_delta": se_d,
            "latency_fraction_of_window_deficit": float(frac)}


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 8000
    cache = {}
    def get(arm, s):
        if (arm, s) not in cache:
            cache[(arm, s)] = sim.run(chain_circuit(arm, s), shots=shots).result().get_counts()
        return cache[(arm, s)]
    r = analyze(get, shots)
    print("Exp177 selftest (noiseless Aer)")
    for arm in ARMS:
        print(f"  {arm:>10}: ZZ={r[arm]['ZZ']:+.2f} XX={r[arm]['XX']:+.2f} YY={r[arm]['YY']:+.2f} "
              f"-> F={r[arm]['F']:.3f}")
        assert r[arm]["F"] > 0.99, f"{arm} must give perfect Phi+ (frame algebra check)"
    print("SELFTEST PASS: live, deferred (software frame), endmeasure (fully deferred measurement), "
          "and direct all exact — the Pauli-frame algebra (x=c3^c1, z=c2^c0 on D) is correct. Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    circuits, order = [], []
    for arm in ARMS:
        for s in SETTINGS:
            circuits.append(transpile(chain_circuit(arm, s), backend=backend, optimization_level=3))
            order.append([arm, s])
    sampler = SamplerV2(mode=backend); job = sampler.run(circuits, shots=shots)
    manifest = {"exp": 177, "slug": "frame", "backend": backend_name, "shots": shots,
                "job_id": job.job_id(), "order": order, "witness": WITNESS,
                "prereg": {"primary": "delta_latency = F(deferred)-F(live) > 0 at >=3 sigma",
                           "magnitude": "latency fraction of window deficit >= 0.6",
                           "band": "live 0.52-0.63; deferred 0.70-0.85; endmeasure 0.76-0.90; direct 0.95-0.99",
                           "fingerprint": "recovery concentrated in XX/YY (dephasing-specific), not ZZ",
                           "falsifier_direction": "delta_latency ~ 0 with large delta_measure => tax is "
                                                  "measurement placement, not classical latency"}}
    out = os.path.join(HERE, "..", "results", "exp177_frame_manifest.json")
    json.dump(manifest, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    mp = os.path.join(HERE, "..", "results", "exp177_frame_manifest.json")
    svc = _get_ibm_service(); man = json.load(open(mp)); res = svc.job(man["job_id"]).result()
    shots = man["shots"]
    raw = {}
    for idx, (arm, s) in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[(arm, s)] = getattr(r0.data, reg).get_counts()
    r = analyze(lambda arm, s: raw[(arm, s)], shots)
    se = 0.75 / np.sqrt(shots)
    dc = decomposition(r, shots)
    print(f"Exp177 PAULI FRAME decode | job {man['job_id']} | backend {man['backend']}")
    for arm in ARMS:
        print(f"  {arm:>10}: ZZ={r[arm]['ZZ']:+.3f} XX={r[arm]['XX']:+.3f} YY={r[arm]['YY']:+.3f} "
              f"-> F = {r[arm]['F']:.3f}")
    print(f"\nDECOMPOSITION of the 2-swap chain deficit (same job):")
    print(f"  latency (deferred-live)      = {dc['delta_latency']:+.3f} ({dc['delta_latency_sigma']:+.1f} sigma)")
    print(f"  measurement (end-deferred)   = {dc['delta_measure']:+.3f} ({dc['delta_measure_sigma']:+.1f} sigma)")
    print(f"  circuit depth (direct-end)   = {dc['delta_circuit']:+.3f}")
    print(f"  latency fraction of window deficit = {dc['latency_fraction_of_window_deficit']:.2f}")
    ok = dc["delta_latency"] > 0 and dc["delta_latency_sigma"] >= 3
    print(f"PRIMARY: {'HELD — frame deferral buys the tax back' if ok else 'NOT HELD (honest accounting above)'}"
          f" | magnitude {'HELD' if dc['latency_fraction_of_window_deficit'] >= 0.6 else 'MISSED'} "
          f"(>=0.6 pre-registered)")
    out = {"job_id": man["job_id"], "results": r, "decomposition": dc, "verdict_ok": bool(ok)}
    json.dump(out, open(os.path.join(HERE, "..", "results", "exp177_frame_decode.json"), "w"), indent=1)
    print("-> results/exp177_frame_decode.json")


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
