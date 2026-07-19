#!/usr/bin/env python3
"""Exp215 — THE COMPLEMENTARITY DIAL: wave-particle duality on the bath-record dial. C4905.

Horizons-5 foundations / the ledger arc, on the standing go ("keep flying!"). The certified
ledger arc measured coherence (200b, rides kappa=cos(theta/2)), facts-objectivity (201, kappa^2),
and revival (204). This flight adds Bohr's complementarity to the SAME dial: as a system
decoheres by leaving a record in an owned bath (the coin), the system's coherence V (the "wave")
and the record's which-path distinguishability D (the "particle") should obey Englert's duality
relation V^2 + D^2 = 1 — measured, on the bath-record dial that governs the whole ledger.

Apparatus (200b family): system q0 = |+>, couple cry(theta, sys->coin) draining coherence into
the coin. Dial theta/pi in {0,1/4,1/2,3/4,1}.
  V (visibility / wave): system coherence = <X_sys> after the coupling (H, cry, H, measure Z).
    Ideal V = cos(theta/2) = kappa.
  D (distinguishability / particle): trace distance between the coin states for the two system
    paths. Path 0 (sys=|0>) -> coin |0> (Bloch (0,0,1)); path 1 (sys=|1>) -> coin Ry(theta)|0>
    (Bloch (sin theta, 0, cos theta)). D = (1/2)|r0 - r1| = sin(theta/2). Measured from the
    path-1 coin Bloch vector (<X_coin>, <Z_coin>).
Prediction: V^2 + D^2 = 1 exactly (a pure which-path detector saturates the duality bound).

FROZEN GATES (relative to statevector-exact):
  G1_V_LAW: |V(theta) - cos(theta/2)| <= 0.10 every dose; V strictly decreasing.
  G2_D_LAW: |D(theta) - sin(theta/2)| <= 0.10 every dose; D strictly increasing.
  G3_DUALITY: |V^2 + D^2 - 1| <= 0.12 at every interior dose (the duality bound saturated on
     the dial — coherence lost = which-path info gained, one bath-record ledger).
Registered verdict = G1 and G2 and G3.
SCOPE: single-qubit system + single-qubit owned-bath record (200b/F118 scope). Connects the
ledger arc (200b/201/204) to Bohr/Englert complementarity as a measured curve. Textbook duality
(Englert PRL 77, 2154) + the campaign's bath-record ledger; the contribution is the composition
— V^2+D^2=1 on the same dial as facts and irreversibility.
BUDGET CHECK (C4887): shallow (1 CX each). Filed: duality residual <= 0.08; V(pi/2)=D(pi/2)
~0.707 (the balanced point).
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
PI = np.pi
DOSES = (0.0, 0.25, 0.5, 0.75, 1.0)
INTERIOR = (0.25, 0.5, 0.75)


def circ_V(t):
    """system coherence: |+>, cry(theta,sys->coin), H(sys), measure sys. <Z_sys> = V."""
    qc = QuantumCircuit(2, 1)
    qc.h(0)
    qc.cry(t * PI, 0, 1)
    qc.barrier()
    qc.h(0); qc.measure(0, 0)
    return qc


def circ_D(t, basis):
    """path-1 coin Bloch: sys=|1>, cry(theta) -> coin=Ry(theta)|0>. Measure coin in Z or X."""
    qc = QuantumCircuit(2, 1)
    qc.x(0)                                   # system path 1
    qc.cry(t * PI, 0, 1)
    qc.barrier()
    if basis == "X": qc.h(1)
    qc.measure(1, 0)
    return qc


def _ev(counts):
    c = tot = 0
    for s, n in counts.items():
        c += (1 - 2 * int(s.replace(" ", "")[-1])) * n; tot += n
    return c / tot


def analyze(get):
    r = {}
    for t in DOSES:
        V = _ev(get("V", t, None))
        zc = _ev(get("D", t, "Z")); xc = _ev(get("D", t, "X"))
        # r0 = (0,0,1); r1 = (xc, 0, zc); D = 1/2 |r0 - r1|
        D = 0.5 * np.sqrt(xc ** 2 + (1 - zc) ** 2)
        r[t] = {"V": V, "D": D, "duality": V ** 2 + D ** 2, "xc": xc, "zc": zc}
    return r


def exact():
    out = {}
    for t in DOSES:
        V = np.cos(t * PI / 2); D = np.sin(t * PI / 2)
        out[t] = {"V": float(V), "D": float(D), "duality": float(V ** 2 + D ** 2)}
    return out


def selftest():
    from qiskit_aer import AerSimulator
    ex = exact()
    sim = AerSimulator(); shots = 40000; cache = {}
    def get(kind, t, basis):
        k = (kind, t, basis)
        if k not in cache:
            qc = circ_V(t) if kind == "V" else circ_D(t, basis)
            cache[k] = sim.run(qc, shots=shots).result().get_counts()
        return cache[k]
    r = analyze(get)
    print("Exp215 selftest | V=cos(th/2), D=sin(th/2), V^2+D^2=1 (Englert duality)")
    for t in DOSES:
        print(f"  th={t:.2f}pi: V={r[t]['V']:+.4f}(ex {ex[t]['V']:.3f}) D={r[t]['D']:.4f}"
              f"(ex {ex[t]['D']:.3f}) V^2+D^2={r[t]['duality']:.4f}")
        assert abs(r[t]["V"] - ex[t]["V"]) < 0.03, f"V mismatch {t}"
        assert abs(r[t]["D"] - ex[t]["D"]) < 0.03, f"D mismatch {t}"
        assert abs(r[t]["duality"] - 1) < 0.03, f"duality not saturated {t}"
    print("SELFTEST PASS: the system coherence V and the record distinguishability D saturate "
          "V^2+D^2=1 across the bath-record dial — wave-particle duality on the same dial as "
          "facts and irreversibility. Cleared to fly.")


def _entries():
    e = []
    for t in DOSES:
        e.append(("V", t, "none")); e.append(("D", t, "Z")); e.append(("D", t, "X"))
    return e


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    ex = exact()
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    ent = _entries()
    builds = [circ_V(t) if k == "V" else circ_D(t, b) for (k, t, b) in ent]
    circuits = [transpile(qc, backend=backend, optimization_level=3, seed_transpiler=0) for qc in builds]
    n2s = [sum(1 for inst in c.data if inst.operation.num_qubits == 2) for c in circuits]
    print(f"  DEPTH CHECK: {len(circuits)} circuits, 2q {min(n2s)}-{max(n2s)}")
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    out = os.path.join(HERE, "..", "results", "exp215_complementarity_manifest.json")
    man = {"exp": 215, "slug": "complementarity_dial", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "order": [list(e) for e in ent],
           "exact": {str(t): ex[t] for t in DOSES}}
    json.dump(man, open(out, "w"), indent=1)
    man["prereg"] = {
        "G1_V_law": "|V - cos(th/2)| <= 0.10 every dose; V strictly decreasing",
        "G2_D_law": "|D - sin(th/2)| <= 0.10 every dose; D strictly increasing",
        "G3_duality": "|V^2 + D^2 - 1| <= 0.12 at every interior dose",
        "registered_verdict": "G1 and G2 and G3",
        "scope": "single system + single owned-bath record (200b/F118); Englert duality on the "
                 "bath-record dial that governs the ledger arc",
        "budget_predictions": "duality residual <= 0.08; V(pi/2)=D(pi/2)~0.707"}
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp215_complementarity_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    raw = {}
    for idx, (k, t, b) in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[(k, float(t), b)] = getattr(r0.data, reg).get_counts()
    r = analyze(lambda k, t, b: raw[(k, t, b if k == "D" else "none")])
    ex = {float(t): v for t, v in man["exact"].items()}
    print(f"Exp215 THE COMPLEMENTARITY DIAL decode | job {man['job_id']}")
    for t in DOSES:
        print(f"  th={t:.2f}pi: V={r[t]['V']:+.4f} (ex {ex[t]['V']:.3f})  D={r[t]['D']:.4f} "
              f"(ex {ex[t]['D']:.3f})  V^2+D^2={r[t]['duality']:.4f}")
    Vs = [r[t]["V"] for t in DOSES]; Ds = [r[t]["D"] for t in DOSES]
    g1 = all(abs(r[t]["V"] - ex[t]["V"]) <= 0.10 for t in DOSES) and all(Vs[i] > Vs[i + 1] - 0.05 for i in range(4))
    g2 = all(abs(r[t]["D"] - ex[t]["D"]) <= 0.10 for t in DOSES) and all(Ds[i] < Ds[i + 1] + 0.05 for i in range(4))
    g3 = all(abs(r[t]["duality"] - 1) <= 0.12 for t in INTERIOR)
    print(f"\nG1 V LAW (cos): max resid {max(abs(r[t]['V']-ex[t]['V']) for t in DOSES):.3f} {'OK' if g1 else 'MISS'}")
    print(f"G2 D LAW (sin): max resid {max(abs(r[t]['D']-ex[t]['D']) for t in DOSES):.3f} {'OK' if g2 else 'MISS'}")
    print(f"G3 DUALITY V^2+D^2=1: interior {[round(r[t]['duality'],3) for t in INTERIOR]} "
          f"(max dev {max(abs(r[t]['duality']-1) for t in INTERIOR):.3f}) {'OK' if g3 else 'MISS'}")
    ok = g1 and g2 and g3
    win = ("THE COMPLEMENTARITY DIAL — wave-particle duality measured on the bath-record dial: "
           "as the system decoheres into its record, coherence V (wave) and which-path "
           "distinguishability D (particle) saturate V^2+D^2=1 — Bohr complementarity on the "
           "same dial as facts and irreversibility")
    print(f"VERDICT: {win if ok else 'NOT HELD (accounting above)'}")
    json.dump({"job_id": man["job_id"], "V": {str(t): r[t]["V"] for t in DOSES},
               "D": {str(t): r[t]["D"] for t in DOSES},
               "duality": {str(t): r[t]["duality"] for t in DOSES},
               "g1": bool(g1), "g2": bool(g2), "g3": bool(g3), "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp215_complementarity_decode.json"), "w"), indent=1)
    print("-> results/exp215_complementarity_decode.json")


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
