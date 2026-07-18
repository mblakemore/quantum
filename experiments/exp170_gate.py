#!/usr/bin/env python3
"""Exp170 — GATE TELEPORTATION: a nonlocal CNOT between qubits that never interact. C4860.
Teleport an OPERATION, not a state. The Eisert-Jozsa-Simon nonlocal CNOT uses 1 shared Bell pair
+ feedforward BOTH directions to apply CNOT(A->B) with A and B never directly coupled:
  Alice: CNOT(A, e1), measure e1 -> x, send x.  Bob: X^x on e2, CNOT(e2, B), H-measure e2 -> z.
  Alice: Z^z on A.  Net = CNOT(A->B). The primitive behind distributed / fault-tolerant computation.

SELF-VERIFYING: the teleported CNOT must (1) turn |+>|0> into a BELL PAIR — entanglement between
data qubits that never touched, witness F>1/2 — and (2) reproduce the truth table (|10>->|11>,
|00>->|00>). Arms (one job): teleported / direct-CNOT baseline / no-resource (unentangled e-pair,
must collapse). Usage: --selftest | --submit [--backend ibm_fez --shots 4096] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
from exp162_swap import fidelity

# A=q0 (control), e1=q1, e2=q2, B=q3 (target). clbits: c0=x(e1), c1=z(e2), c2=A, c3=B.
ARMS = ("teleported", "direct", "noresource")
# setting: (name, prepA gates, prepB gates, verify basis on A&B)
SETTINGS = [
    ("bell_ZZ", ["h"], [], "Z"),   # |+>|0> -> Bell; measure ZZ
    ("bell_XX", ["h"], [], "X"),
    ("bell_YY", ["h"], [], "Y"),
    ("tt_10",   ["x"], [], "Z"),   # |1>|0> -> |1>|1|
    ("tt_00",   [],    [], "Z"),   # |0>|0> -> |0>|0>
]


def _apply(qc, gates, q):
    for g in gates:
        getattr(qc, g)(q)


def gate_circuit(arm, prepA, prepB, basis):
    qc = QuantumCircuit(4, 4)
    _apply(qc, prepA, 0); _apply(qc, prepB, 3)
    if arm == "direct":
        qc.cx(0, 3)                              # baseline: the real CNOT
    else:
        if arm != "noresource":
            qc.h(1); qc.cx(1, 2)                 # shared Bell resource (load-bearing)
        qc.barrier()
        qc.cx(0, 1); qc.measure(1, 0)            # Alice: CNOT(A,e1), measure -> x
        with qc.if_test((qc.clbits[0], 1)): qc.x(2)   # Bob: X^x on e2
        qc.cx(2, 3)                              # Bob: CNOT(e2, B)
        qc.h(2); qc.measure(2, 1)               # Bob: H-measure e2 -> z
        with qc.if_test((qc.clbits[1], 1)): qc.z(0)   # Alice: Z^z on A
    qc.barrier()
    for q in (0, 3):
        if basis == "X": qc.h(q)
        elif basis == "Y": qc.sdg(q); qc.h(q)
    qc.measure(0, 2); qc.measure(3, 3)
    return qc


def _bits(counts):
    """(a=c2, b=c3, count). String 'c3c2c1c0'."""
    for s, n in counts.items():
        b = s.replace(" ", "")
        yield int(b[-3]), int(b[-4]), n


def _par(counts, shots):
    return sum((1 - 2 * a) * (1 - 2 * b) * n for a, b, n in _bits(counts)) / shots


def _p(counts, shots, want):
    return sum(n for a, b, n in _bits(counts) if (a, b) == want) / shots


def analyze(get, shots):
    out = {}
    for arm in ARMS:
        zz = _par(get(arm, "bell_ZZ"), shots); xx = _par(get(arm, "bell_XX"), shots)
        yy = _par(get(arm, "bell_YY"), shots)
        Fb = fidelity({"ZZ": zz, "XX": xx, "YY": yy})
        tt = 0.5 * (_p(get(arm, "tt_10"), shots, (1, 1)) + _p(get(arm, "tt_00"), shots, (0, 0)))
        out[arm] = {"F_bell": float(Fb), "truth_table": float(tt),
                    "ZZ": float(zz), "XX": float(xx), "YY": float(yy)}
    return out


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 6000
    cache = {}
    def get(arm, name):
        if (arm, name) not in cache:
            _, pa, pb, bas = next(s for s in SETTINGS if s[0] == name)
            cache[(arm, name)] = sim.run(gate_circuit(arm, pa, pb, bas), shots=shots).result().get_counts()
        return cache[(arm, name)]
    r = analyze(get, shots)
    print("Exp170 selftest (noiseless Aer)")
    for arm in ARMS:
        print(f"  {arm:>11}: F_bell={r[arm]['F_bell']:.3f}  truth_table={r[arm]['truth_table']:.3f}")
    for arm in ("teleported", "direct"):
        assert r[arm]["F_bell"] > 0.99 and r[arm]["truth_table"] > 0.99, f"{arm} must be exact CNOT"
    # Without entanglement the CLASSICAL action survives (truth table ~1) but the entangling/
    # coherent action collapses: F_bell caps at 1/2 (classical correlation, no XX coherence).
    nr = r["noresource"]
    assert nr["F_bell"] < 0.6 and nr["truth_table"] > 0.99, "no-resource must keep the table but lose the entanglement"
    print(f"  no-resource keeps the truth table ({nr['truth_table']:.2f}) but F_bell caps at 1/2 "
          f"({nr['F_bell']:.2f}): the classical action is LOCC, the entangling action needs the e-bit")
    print("SELFTEST PASS: teleported nonlocal CNOT == direct CNOT (Bell F=1, table exact); without the "
          "shared Bell resource F_bell cannot beat 1/2 -> the witness IS the quantum-vs-classical line. Cleared.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    circuits, order = [], []
    for arm in ARMS:
        for name, pa, pb, bas in SETTINGS:
            circuits.append(transpile(gate_circuit(arm, pa, pb, bas), backend=backend, optimization_level=3))
            order.append([arm, name])
    sampler = SamplerV2(mode=backend); job = sampler.run(circuits, shots=shots)
    manifest = {"exp": 170, "slug": "gate", "backend": backend_name, "shots": shots,
                "job_id": job.job_id(), "order": order,
                "prereg": {"primary": "teleported F_bell > 1/2 at >5 sigma AND truth_table > 0.85",
                           "falsifier": "noresource F_bell < 0.6 (caps at 1/2 — classical shadow, no entanglement)",
                           "prediction": "F_bell 0.78-0.90, truth_table 0.88-0.96; direct baseline higher"}}
    out = os.path.join(HERE, "..", "results", "exp170_gate_manifest.json")
    json.dump(manifest, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    mp = os.path.join(HERE, "..", "results", "exp170_gate_manifest.json")
    svc = _get_ibm_service(); man = json.load(open(mp)); res = svc.job(man["job_id"]).result()
    shots = man["shots"]
    raw = {}
    for idx, (arm, name) in enumerate(man["order"]):
        r = res[idx]; reg = list(r.data.keys())[0]
        raw[(arm, name)] = getattr(r.data, reg).get_counts()
    r = analyze(lambda arm, name: raw[(arm, name)], shots)
    se = 0.75 / np.sqrt(shots)
    print(f"Exp170 GATE TELEPORTATION decode | job {man['job_id']} | backend {man['backend']}")
    for arm in ARMS:
        print(f"  {arm:>11}: F_bell={r[arm]['F_bell']:.3f}  truth_table={r[arm]['truth_table']:.3f}  "
              f"(ZZ={r[arm]['ZZ']:+.2f} XX={r[arm]['XX']:+.2f} YY={r[arm]['YY']:+.2f})")
    t = r["teleported"]
    nsig = (t["F_bell"] - 0.5) / se
    ok = t["F_bell"] > 0.5 and nsig > 5 and t["truth_table"] > 0.85 and r["noresource"]["F_bell"] < 0.6
    print(f"\nTELEPORTED nonlocal CNOT: Bell F={t['F_bell']:.3f} ({nsig:.0f} sigma over 1/2) | "
          f"truth table {t['truth_table']:.3f}")
    print(f"DIRECT CNOT (same job): F={r['direct']['F_bell']:.3f}, tt={r['direct']['truth_table']:.3f} "
          f"-> gate-teleport cost {r['direct']['F_bell']-t['F_bell']:+.3f}")
    print(f"FALSIFIER: no-resource F_bell={r['noresource']['F_bell']:.3f} (caps at 1/2: keeps the table "
          f"[{r['noresource']['truth_table']:.2f}] but loses the entanglement — the classical action is LOCC, "
          f"the entangling action needs the e-bit; the witness IS the quantum-vs-classical line)")
    print(f"VERDICT: {'GATE TELEPORTED — an entangling CNOT acted between qubits that never interacted' if ok else 'FAILED a gate (honest accounting above)'}")
    out = {"job_id": man["job_id"], "results": r, "teleported_sigma": float(nsig), "verdict_ok": bool(ok)}
    json.dump(out, open(os.path.join(HERE, "..", "results", "exp170_gate_decode.json"), "w"), indent=1)
    print("-> results/exp170_gate_decode.json")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true"); ap.add_argument("--submit", action="store_true")
    ap.add_argument("--decode", action="store_true")
    ap.add_argument("--backend", default="ibm_fez"); ap.add_argument("--shots", type=int, default=4096)
    a = ap.parse_args()
    if a.selftest: selftest()
    elif a.submit: submit(a.backend, a.shots)
    elif a.decode: decode()
    else: ap.print_help()
