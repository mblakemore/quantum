#!/usr/bin/env python3
"""Exp193 — THE FRIEND IN THE MACHINE: Brukner Wigner's-friend Bell test. C4886.
a=q0, F_A=q1, dump_A=q2, b=q3, F_B=q4, dump_B=q5. Bell(a,b); friends measure (CX sys->friend).
Per side, late choice: TRUST (read friend record, theta=0) or OVERRULE (CX undo + measure sys
at +-pi/3). Facts-CHSH <= 2 if facts are absolute; QM 2.5. Decohered arm: copy records to
dumps -> reversal fails -> S -> 1.75 (facts become facts when copied).
Usage: --selftest | --submit | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
PI = np.pi
SETT = ["FF", "FB", "AF", "AB"]
ARMS = ("live", "dec")
A1, B1 = PI/3, -PI/3

def circuit(arm, s):
    qc = QuantumCircuit(6, 6)
    qc.h(0); qc.cx(0, 3)                     # Bell(a,b)
    qc.barrier()
    qc.cx(0, 1); qc.cx(3, 4)                 # the friends measure: facts recorded
    if arm == "dec":
        qc.cx(1, 2); qc.cx(4, 5)             # the facts are COPIED (decoherence)
    qc.barrier()
    aside, bside = s[0], s[1]
    if aside == "A":                          # overrule: undo + rotated measurement
        qc.cx(0, 1); qc.ry(-A1, 0)
    if bside == "B":
        qc.cx(3, 4); qc.ry(-B1, 3)
    qc.barrier()
    qc.measure(0, 0); qc.measure(1, 1); qc.measure(3, 3); qc.measure(4, 4)
    qc.measure(2, 2); qc.measure(5, 5)
    return qc

def analyze(get):
    r = {}
    for arm in ARMS:
        E = {}; marg = {}
        for s in SETT:
            c = get(arm, s); acc = tot = 0; fa = fb = 0
            for bstr, n in c.items():
                b = bstr.replace(" ", "")
                va = int(b[-2]) if s[0] == "F" else int(b[-1])    # A outcome: friend record or sys
                vb = int(b[-5]) if s[1] == "F" else int(b[-4])
                acc += (1 - 2*va) * (1 - 2*vb) * n; tot += n
                fa += (1 - 2*int(b[-2])) * n; fb += (1 - 2*int(b[-5])) * n
            E[s] = acc / tot; marg[s] = (fa / tot, fb / tot)
        S = E["FF"] + E["FB"] + E["AF"] - E["AB"]
        spread = max(abs(marg["FF"][0]-marg["FB"][0]), abs(marg["AF"][1] and 0 or 0),
                     abs(marg["FF"][1]-marg["AF"][1]))
        r[arm] = {"E": {k: float(v) for k, v in E.items()}, "S": float(S),
                  "EFF": float(E["FF"]), "marg_spread": float(spread)}
    return r

def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 20000; cache = {}
    def get(arm, s):
        k = (arm, s)
        if k not in cache: cache[k] = sim.run(circuit(arm, s), shots=shots).result().get_counts()
        return cache[k]
    r = analyze(lambda arm, s: get(arm, s))
    print("Exp193 selftest:", {a: round(r[a]["S"], 3) for a in ARMS}, "| E(F,F):", round(r["live"]["EFF"], 3))
    assert abs(r["live"]["S"] - 2.5) < 0.04, "live facts-CHSH must be 2.5"
    assert abs(r["dec"]["S"] - 1.75) < 0.04, "copied facts must restore absoluteness at 1.75"
    assert r["live"]["EFF"] > 0.99 and r["dec"]["EFF"] > 0.99, "the records must record"
    print("SELFTEST PASS: uncopied facts violate observer-independence (2.5); copied facts obey it (1.75). Cleared to fly.")

def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    circuits, order = [], []
    for arm in ARMS:
        for s in SETT:
            circuits.append(transpile(circuit(arm, s), backend=backend, optimization_level=3))
            order.append([arm, s])
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    man = {"exp": 193, "slug": "wigner_friend", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "order": order,
           "prereg": {"primary": "S_live > 2 at >=5 sigma; band 2.15-2.45",
                      "decoherence": "S_dec 1.55-1.90 AND S_live - S_dec >= 0.30 at >=5 sigma",
                      "gauges": "E(F,F) >= 0.85 both arms; friend-marginal spread < 0.035"}}
    json.dump(man, open(os.path.join(HERE, "..", "results", "exp193_wigner_friend_manifest.json"), "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits)")

def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp193_wigner_friend_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    shots = man["shots"]; raw = {}
    for idx, (arm, s) in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[(arm, s)] = getattr(r0.data, reg).get_counts()
    r = analyze(lambda arm, s: raw[(arm, s)])
    seS = float(np.sqrt(sum((1 - r["live"]["E"][k]**2) / shots for k in r["live"]["E"])))
    zl = (r["live"]["S"] - 2) / seS
    gap = r["live"]["S"] - r["dec"]["S"]; zg = gap / (seS * np.sqrt(2))
    print(f"Exp193 FRIEND IN THE MACHINE decode | job {man['job_id']}")
    for arm in ARMS:
        print(f"  {arm:>4}: S = {r[arm]['S']:.3f}  E = " + " ".join(f"{k}:{v:+.2f}" for k, v in r[arm]["E"].items()))
    p_ok = r["live"]["S"] > 2 and zl >= 5
    d_ok = 1.55 <= r["dec"]["S"] <= 1.90 and gap >= 0.30 and zg >= 5
    g_ok = r["live"]["EFF"] >= 0.85 and r["dec"]["EFF"] >= 0.85
    print(f"\nFACTS-CHSH (live): {r['live']['S']:.3f} vs absolute-facts bound 2 -> {zl:.0f} sigma")
    print(f"COPIED FACTS: {r['dec']['S']:.3f} (bound restored) | gap {gap:+.3f} ({zg:.0f} sigma)")
    print(f"RECORDS RECORD: E(F,F) = {r['live']['EFF']:.3f} / {r['dec']['EFF']:.3f}")
    ok = p_ok and d_ok and g_ok
    print(f"VERDICT: {'FACTS ARE NOT ABSOLUTE until copied — observer-independence violated at ' + format(zl, '.0f') + ' sigma, restored by decoherence' if ok else 'NOT HELD (honest accounting above)'}")
    json.dump({"job_id": man["job_id"], "results": r, "sigma_live": float(zl), "gap": float(gap),
               "primary_ok": bool(p_ok), "dec_ok": bool(d_ok), "gauge_ok": bool(g_ok),
               "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp193_wigner_friend_decode.json"), "w"), indent=1)
    print("-> results/exp193_wigner_friend_decode.json")

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
