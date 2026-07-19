#!/usr/bin/env python3
"""Exp186 — THE PRESENT WITH NO DEFINITE PAST: Leggett-Garg with INRM. C4876.
Macrorealism bounds K3 = C12 + C23 - C13 <= 1. A qubit evolving U = Ry(pi/3) per interval,
Q = Z, gives C12 = C23 = +1/2, C13 = -1/2 -> K3 = 3/2: no definite value between looks.
Clumsiness loophole: C23 via Knee-style IDEAL NEGATIVE-RESULT MEASUREMENT — the ancilla couples
only to the value we are NOT crediting; kept rounds are those where the detector provably never
interacted. Controls: dephased c13 (macrorealism restored, K3 -> 3/4) + invasive-vs-INRM
agreement audit. System q0, INRM ancilla q1, dephasing dump q2.
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

TH = np.pi / 3
CIRCS = ("c12", "c13", "c23_plus", "c23_minus", "c13_deph", "c23_invasive")


def circuit(name):
    qc = QuantumCircuit(3, 3)
    qc.ry(TH, 0)                          # interval 1: t1 -> t2  (Q1 = +1 by preparation)
    if name == "c12":
        pass                              # measure at t2
    elif name == "c13":
        qc.ry(TH, 0)                      # interval 2: t2 -> t3, coherence intact
    elif name == "c13_deph":
        qc.cx(0, 2)                       # dephase at t2 (macroreal control)
        qc.ry(TH, 0)
    elif name == "c23_plus":
        qc.cx(0, 1)                       # ancilla fires ONLY if Q2 = -1 (system |1>)
        qc.ry(TH, 0)
    elif name == "c23_minus":
        qc.x(0); qc.cx(0, 1); qc.x(0)     # ancilla fires ONLY if Q2 = +1 (system |0>)
        qc.ry(TH, 0)
    elif name == "c23_invasive":
        qc.cx(0, 1)                       # projective record, BOTH branches kept
        qc.ry(TH, 0)
    qc.measure(0, 0); qc.measure(1, 1); qc.measure(2, 2)
    return qc


def _q(bit):                              # bit 0 -> +1, bit 1 -> -1
    return 1 - 2 * bit


def analyze(get, shots):
    r = {}
    def zexp(name):
        c = get(name); acc = 0
        for s, n in c.items():
            acc += _q(int(s.replace(" ", "")[-1])) * n
        return acc / shots
    r["C12"] = float(zexp("c12"))
    r["C13"] = float(zexp("c13"))
    r["C13_deph"] = float(zexp("c13_deph"))
    # INRM: kept rounds = ancilla did NOT fire (q1 = 0)
    sums = {}
    for name, qval in (("c23_plus", +1), ("c23_minus", -1)):
        c = get(name); s3 = 0; kept = 0
        for s, n in c.items():
            b = s.replace(" ", "")
            if int(b[-2]) == 0:
                kept += n; s3 += _q(int(b[-1])) * n
        sums[name] = (s3 / shots, kept / shots, qval)
    r["C23_inrm"] = float(sums["c23_plus"][0] - sums["c23_minus"][0])
    r["kept_sum"] = float(sums["c23_plus"][1] + sums["c23_minus"][1])
    # invasive: Q2 from ancilla (both branches), Q3 from system
    c = get("c23_invasive"); acc = 0
    for s, n in c.items():
        b = s.replace(" ", "")
        acc += _q(int(b[-2])) * _q(int(b[-1])) * n
    r["C23_inv"] = float(acc / shots)
    r["K3"] = float(r["C12"] + r["C23_inrm"] - r["C13"])
    r["K3_deph"] = float(r["C12"] + r["C23_inrm"] - r["C13_deph"])
    r["inrm_vs_inv"] = float(abs(r["C23_inrm"] - r["C23_inv"]))
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
    print("Exp186 selftest (noiseless Aer)")
    print(f"  C12={r['C12']:+.3f}  C23_inrm={r['C23_inrm']:+.3f}  C13={r['C13']:+.3f}  "
          f"C13_deph={r['C13_deph']:+.3f}")
    print(f"  K3 = {r['K3']:.3f} (LG bound 1, quantum max 1.5) | dephased K3 = {r['K3_deph']:.3f}")
    print(f"  INRM vs invasive: |diff| = {r['inrm_vs_inv']:.3f} | kept sum = {r['kept_sum']:.3f}")
    assert abs(r["K3"] - 1.5) < 0.03, "K3 must be the quantum max 3/2"
    assert abs(r["K3_deph"] - 0.75) < 0.03, "dephased control must restore macrorealism at 3/4"
    assert r["inrm_vs_inv"] < 0.03, "INRM and invasive C23 must agree (QM prediction)"
    assert abs(r["kept_sum"] - 1.0) < 0.02, "INRM kept fractions must sum to 1"
    print("SELFTEST PASS: K3=1.5 via negative-result measurement; dephasing restores the "
          "macrorealist bound at 0.75; INRM == invasive; bookkeeping exact. Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    circuits, order = [], []
    for name in CIRCS:
        circuits.append(transpile(circuit(name), backend=backend, optimization_level=3))
        order.append(name)
    sampler = SamplerV2(mode=backend); job = sampler.run(circuits, shots=shots)
    manifest = {"exp": 186, "slug": "leggett_garg", "backend": backend_name, "shots": shots,
                "job_id": job.job_id(), "order": order,
                "prereg": {"primary": "K3 (INRM C23) > 1 at >=5 sigma; band 1.30-1.48",
                           "correlators": "C12 +0.42..+0.52; C23 +0.40..+0.52; C13 -0.52..-0.40",
                           "macroreal_control": "K3_deph in 0.62-0.88 (ideal 0.75), UNDER the bound",
                           "clumsiness_audit": "|C23_inrm - C23_inv| < 0.06",
                           "bookkeeping": "kept_sum in 0.95-1.05"}}
    out = os.path.join(HERE, "..", "results", "exp186_leggett_garg_manifest.json")
    json.dump(manifest, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    mp = os.path.join(HERE, "..", "results", "exp186_leggett_garg_manifest.json")
    svc = _get_ibm_service(); man = json.load(open(mp)); res = svc.job(man["job_id"]).result()
    shots = man["shots"]
    raw = {}
    for idx, name in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[name] = getattr(r0.data, reg).get_counts()
    r = analyze(lambda name: raw[name], shots)
    se_C = 1.0 / np.sqrt(shots); se_K = float(np.sqrt(3) * se_C)
    nsig = (r["K3"] - 1) / se_K
    print(f"Exp186 LEGGETT-GARG decode | job {man['job_id']} | backend {man['backend']}")
    print(f"  C12 = {r['C12']:+.3f}   C23(INRM) = {r['C23_inrm']:+.3f}   C13 = {r['C13']:+.3f}")
    print(f"  K3 = {r['K3']:.3f}  vs macrorealist bound 1  ->  {nsig:.0f} sigma VIOLATION" if r["K3"] > 1
          else f"  K3 = {r['K3']:.3f} — no violation")
    print(f"  MACROREAL CONTROL: dephase t2 -> C13 = {r['C13_deph']:+.3f} -> K3 = {r['K3_deph']:.3f} "
          f"({'under the bound — classicality restored' if r['K3_deph'] <= 1 else 'ABOVE BOUND?'})")
    print(f"  CLUMSINESS AUDIT: C23 invasive = {r['C23_inv']:+.3f} vs INRM {r['C23_inrm']:+.3f} "
          f"(|diff| {r['inrm_vs_inv']:.3f}) | kept sum {r['kept_sum']:.3f}")
    p_ok = r["K3"] > 1 and nsig >= 5
    ctrl_ok = 0.62 <= r["K3_deph"] <= 0.88
    audit_ok = r["inrm_vs_inv"] < 0.06 and 0.95 <= r["kept_sum"] <= 1.05
    print(f"\nPRIMARY: {'HELD — the qubit had NO definite value between looks' if p_ok else 'NOT HELD'}")
    print(f"CONTROL: {'HELD — decoherence restores macrorealism' if ctrl_ok else 'NOT HELD'}")
    print(f"AUDIT:   {'HELD — non-invasive and invasive agree; the disturbance excuse fails' if audit_ok else 'NOT HELD'}")
    ok = p_ok and ctrl_ok and audit_ok
    print(f"VERDICT: {'THE PRESENT HAS NO DEFINITE PAST — macrorealism violated at ' + format(nsig, '.0f') + ' sigma with negative-result measurements' if ok else 'NOT HELD (honest accounting above)'}")
    out = {"job_id": man["job_id"], "results": r, "K3_sigma": float(nsig),
           "primary_ok": bool(p_ok), "control_ok": bool(ctrl_ok), "audit_ok": bool(audit_ok),
           "verdict_ok": bool(ok)}
    json.dump(out, open(os.path.join(HERE, "..", "results", "exp186_leggett_garg_decode.json"), "w"), indent=1)
    print("-> results/exp186_leggett_garg_decode.json")


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
