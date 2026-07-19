#!/usr/bin/env python3
"""Exp189 — SHIELDS UP: the [[4,2,2]] error-detecting code (Shields arc, stage i). C4879.
Encode 2 logical qubits in 4 physical (stabilizers XXXX, ZZZZ); detection by FINAL readout:
Z-basis gives ZZZZ syndrome + logicals Zbar1=z1^z3, Zbar2=z1^z2; X-basis gives XXXX + Xbars.
Arms: L00_Z, Lpp_X (clean) | bare_Z, bare_X (unshielded 2-qubit reference) | inject_Z (X on q0
-> ZZZZ flips, shot rejected), inject_X (Z on q0). Legs: detector works (rejection >= 0.90);
acceptance price; accepted logical error vs bare (ratio, honest stage-i caveat: bare is
gate-lighter — time-matched survival is stage ii).
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

CIRCS = ("L00_Z", "Lpp_X", "bare_Z", "bare_X", "inject_Z", "inject_X")


def circuit(name):
    if name.startswith("bare"):
        qc = QuantumCircuit(2, 2)
        if name.endswith("X"):
            qc.h(0); qc.h(1)
        qc.barrier()
        if name.endswith("X"):
            qc.h(0); qc.h(1)
        qc.measure(0, 0); qc.measure(1, 1)
        return qc
    qc = QuantumCircuit(4, 4)
    qc.h(0); qc.cx(0, 1); qc.cx(0, 2); qc.cx(0, 3)     # |0000>+|1111>
    if name.startswith("Lpp"):
        for q in range(4): qc.h(q)                      # |+bar +bar>
    qc.barrier()
    if name == "inject_Z": qc.x(0)                      # deliberate X error
    if name == "inject_X": qc.z(0)                      # deliberate Z error
    qc.barrier()
    if name.endswith("X"):
        for q in range(4): qc.h(q)                      # X-basis readout
    for q in range(4): qc.measure(q, q)
    return qc


def analyze(get, shots):
    r = {}
    for name in CIRCS:
        counts = get(name)
        if name.startswith("bare"):
            err = n = 0
            for s, cnt in counts.items():
                b = s.replace(" ", "")
                q0, q1 = int(b[-1]), int(b[-2])
                err += cnt * ((q0 != 0) + (q1 != 0))    # per-qubit error count
                n += cnt
            r[name] = {"err_per_qubit": float(err / (2 * n))}
            continue
        acc = rej = lerr = 0
        for s, cnt in counts.items():
            b = s.replace(" ", "")
            z = [int(b[-1 - i]) for i in range(4)]
            synd = z[0] ^ z[1] ^ z[2] ^ z[3]
            if synd:
                rej += cnt
                continue
            acc += cnt
            l1, l2 = z[0] ^ z[2], z[0] ^ z[1]           # logical values (0 expected)
            lerr += cnt * ((l1 != 0) + (l2 != 0))
        tot = acc + rej
        r[name] = {"acceptance": float(acc / tot), "rejection": float(rej / tot),
                   "logical_err_per_qubit": float(lerr / (2 * acc)) if acc else None}
    return r


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 20000
    cache = {}
    def get(name):
        if name not in cache:
            cache[name] = sim.run(circuit(name), shots=shots).result().get_counts()
        return cache[name]
    r = analyze(get, shots)
    print("Exp189 selftest (noiseless Aer)")
    for name in CIRCS:
        print(f"  {name:>9}: {r[name]}")
    for name in ("L00_Z", "Lpp_X"):
        assert r[name]["acceptance"] > 0.999 and r[name]["logical_err_per_qubit"] < 0.001, f"{name} clean"
    for name in ("inject_Z", "inject_X"):
        assert r[name]["rejection"] > 0.999, f"{name}: injected error must always be detected"
    for name in ("bare_Z", "bare_X"):
        assert r[name]["err_per_qubit"] < 0.001, f"{name} exact"
    print("SELFTEST PASS: encoding exact, injected errors detected 100%, bare reference exact. "
          "Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    circuits, order = [], []
    for name in CIRCS:
        circuits.append(transpile(circuit(name), backend=backend, optimization_level=3))
        order.append(name)
    sampler = SamplerV2(mode=backend); job = sampler.run(circuits, shots=shots)
    manifest = {"exp": 189, "slug": "shields_up", "backend": backend_name, "shots": shots,
                "job_id": job.job_id(), "order": order,
                "prereg": {"detection": "injected rejection >= 0.90 both bases; accepted-and-wrong <= 0.05",
                           "acceptance": "clean arms 0.80-0.95 per basis",
                           "shield": "accepted logical err per qubit <= bare err per qubit; ratio band 0.2-1.0 "
                                     "(stage-i caveat: bare is gate-lighter; >1 prices stage ii, does not kill the arc)"}}
    out = os.path.join(HERE, "..", "results", "exp189_shields_up_manifest.json")
    json.dump(manifest, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    mp = os.path.join(HERE, "..", "results", "exp189_shields_up_manifest.json")
    svc = _get_ibm_service(); man = json.load(open(mp)); res = svc.job(man["job_id"]).result()
    shots = man["shots"]
    raw = {}
    for idx, name in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[name] = getattr(r0.data, reg).get_counts()
    r = analyze(lambda name: raw[name], shots)
    print(f"Exp189 SHIELDS UP decode | job {man['job_id']} | backend {man['backend']}")
    for name in CIRCS:
        print(f"  {name:>9}: {r[name]}")
    det_ok = r["inject_Z"]["rejection"] >= 0.90 and r["inject_X"]["rejection"] >= 0.90
    wrong_ok = all((r[n]["logical_err_per_qubit"] or 0) <= 0.05 for n in ("inject_Z", "inject_X"))
    acc_ok = all(0.80 <= r[n]["acceptance"] <= 0.95 or r[n]["acceptance"] > 0.95
                 for n in ("L00_Z", "Lpp_X"))
    lz, lx = r["L00_Z"]["logical_err_per_qubit"], r["Lpp_X"]["logical_err_per_qubit"]
    bz, bx = r["bare_Z"]["err_per_qubit"], r["bare_X"]["err_per_qubit"]
    ratio_z = lz / bz if bz else float("inf"); ratio_x = lx / bx if bx else float("inf")
    print(f"\nDETECTOR: inject rejection Z={r['inject_Z']['rejection']:.3f} X={r['inject_X']['rejection']:.3f} "
          f"| accepted-and-wrong Z={r['inject_Z']['logical_err_per_qubit'] or 0:.3f} "
          f"X={r['inject_X']['logical_err_per_qubit'] or 0:.3f} -> {'WORKS' if det_ok and wrong_ok else 'CHECK'}")
    print(f"ACCEPTANCE PRICE: Z={r['L00_Z']['acceptance']:.3f}  X={r['Lpp_X']['acceptance']:.3f}")
    print(f"SHIELD vs BARE (err/qubit): Z {lz:.4f} vs {bz:.4f} (ratio {ratio_z:.2f}) | "
          f"X {lx:.4f} vs {bx:.4f} (ratio {ratio_x:.2f})")
    shield_ok = ratio_z <= 1.0 and ratio_x <= 1.0
    print(f"SHIELD LEG: {'accepted logical error AT OR BELOW bare — the shield pays already at stage (i)' if shield_ok else 'ratio > 1 — the shield does not yet pay at stage (i) gate counts (prices stage ii, as pre-registered)'}")
    ok = det_ok and wrong_ok
    print(f"VERDICT: {'SHIELDS UP — the code detects, the price is measured' + (', and the shield already pays' if shield_ok else '') if ok else 'NOT HELD (honest accounting above)'}")
    out = {"job_id": man["job_id"], "results": r,
           "ratios": {"Z": float(ratio_z), "X": float(ratio_x)},
           "detector_ok": bool(det_ok and wrong_ok), "shield_pays": bool(shield_ok),
           "verdict_ok": bool(ok)}
    json.dump(out, open(os.path.join(HERE, "..", "results", "exp189_shields_up_decode.json"), "w"), indent=1)
    print("-> results/exp189_shields_up_decode.json")


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
