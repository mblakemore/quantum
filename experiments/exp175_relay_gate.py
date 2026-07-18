#!/usr/bin/env python3
"""Exp175 — THE RELAY COMPUTER: a nonlocal CNOT through a swapped e-bit. C4862.
Composes Exp162 (entanglement swapping) + Exp170 (EJS gate teleportation): the e-bit consumed by
the nonlocal CNOT is itself created by a Bell-measurement relay — the minimal quantum-internet
stack (link layer -> compute layer) end to end in one job.

Roles: DA=q0 (data control), eA=q1, M1=q2, M2=q3 (relay middles), eB=q4, DB=q5 (data target).
clbits: c0,c1 = relay Bell measurement; c2 = x (Alice), c3 = z (Bob); c4 = A, c5 = B verify.

ARMS: relaygate (swap then EJS) | directebit (EJS via local Bell — Exp170 replica) | swaponly
(link quality gauge) | cnot (plain CNOT anchor) | noresource (falsifier: table survives, F<=1/2).
COMPOSITION TEST (pre-registered): with p=(4F-1)/3, predict
  p_pred(relaygate) = p(directebit) * p(swaponly) / p(cnot)
from same-job baselines; measured-vs-predicted tests whether stacked layers price multiplicatively.
Usage: --selftest | --submit [--backend ibm_fez --shots 4096] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
from exp162_swap import fidelity

ARMS = ("relaygate", "directebit", "swaponly", "cnot", "noresource")
GATE_ARMS = ("relaygate", "directebit", "cnot", "noresource")
SETTINGS = [
    ("bell_ZZ", ["h"], [], "Z"),   # |+>|0> -> Bell; measure ZZ
    ("bell_XX", ["h"], [], "X"),
    ("bell_YY", ["h"], [], "Y"),
    ("tt_10",   ["x"], [], "Z"),   # |1>|0> -> |1>|1>
    ("tt_00",   [],    [], "Z"),   # |0>|0> -> |0>|0>
]
BELL_SETTINGS = ("bell_ZZ", "bell_XX", "bell_YY")


def _apply(qc, gates, q):
    for g in gates:
        getattr(qc, g)(q)


def _basis(qc, basis, qubits):
    for q in qubits:
        if basis == "X": qc.h(q)
        elif basis == "Y": qc.sdg(q); qc.h(q)


def _swap_layer(qc):
    """Exp162 layer: project (eA,eB) into Phi+ via Bell measurement on the middles."""
    qc.h(1); qc.cx(1, 2)                          # Bell(eA, M1)
    qc.h(3); qc.cx(3, 4)                          # Bell(M2, eB)
    qc.barrier()
    qc.cx(2, 3); qc.h(2)                          # Bell measurement on the relay middles
    qc.measure(2, 0); qc.measure(3, 1)
    with qc.if_test((qc.clbits[1], 1)): qc.x(4)   # feedforward corrections on eB
    with qc.if_test((qc.clbits[0], 1)): qc.z(4)


def circuit(arm, prepA, prepB, basis):
    qc = QuantumCircuit(6, 6)
    if arm == "swaponly":
        _swap_layer(qc)
        qc.barrier()
        _basis(qc, basis, (1, 4))
        qc.measure(1, 4); qc.measure(4, 5)        # verify the swapped e-bit itself
        return qc
    _apply(qc, prepA, 0); _apply(qc, prepB, 5)
    if arm == "cnot":
        qc.cx(0, 5)                               # plain gate anchor
    else:
        if arm == "relaygate":
            _swap_layer(qc)                       # e-bit from the relay
        elif arm == "directebit":
            qc.h(1); qc.cx(1, 4)                  # e-bit prepared locally (Exp170 replica)
        # noresource: no e-bit at all
        qc.barrier()
        qc.cx(0, 1); qc.measure(1, 2)             # Alice: CNOT(DA,eA), measure -> x
        with qc.if_test((qc.clbits[2], 1)): qc.x(4)    # Bob: X^x on eB
        qc.cx(4, 5)                               # Bob: CNOT(eB, DB)
        qc.h(4); qc.measure(4, 3)                 # Bob: H-measure eB -> z
        with qc.if_test((qc.clbits[3], 1)): qc.z(0)    # Alice: Z^z on DA
    qc.barrier()
    _basis(qc, basis, (0, 5))
    qc.measure(0, 4); qc.measure(5, 5)
    return qc


def _bits(counts):
    """(a=c4, b=c5, count). String 'c5c4c3c2c1c0'."""
    for s, n in counts.items():
        b = s.replace(" ", "")
        yield int(b[-5]), int(b[-6]), n


def _par(counts, shots):
    return sum((1 - 2 * a) * (1 - 2 * b) * n for a, b, n in _bits(counts)) / shots


def _p(counts, shots, want):
    return sum(n for a, b, n in _bits(counts) if (a, b) == want) / shots


def analyze(get, shots):
    out = {}
    for arm in ARMS:
        zz = _par(get(arm, "bell_ZZ"), shots); xx = _par(get(arm, "bell_XX"), shots)
        yy = _par(get(arm, "bell_YY"), shots)
        rec = {"F_bell": float(fidelity({"ZZ": zz, "XX": xx, "YY": yy})),
               "ZZ": float(zz), "XX": float(xx), "YY": float(yy)}
        if arm != "swaponly":
            rec["truth_table"] = float(0.5 * (_p(get(arm, "tt_10"), shots, (1, 1))
                                              + _p(get(arm, "tt_00"), shots, (0, 0))))
        out[arm] = rec
    return out


def composition(r, shots):
    """Pre-registered test: p_pred(relaygate) = p(directebit)*p(swaponly)/p(cnot)."""
    p = lambda F: (4 * F - 1) / 3
    se_F = 0.75 / np.sqrt(shots); se_p = (4 / 3) * se_F
    pd, ps, pc = p(r["directebit"]["F_bell"]), p(r["swaponly"]["F_bell"]), p(r["cnot"]["F_bell"])
    p_pred = pd * ps / pc
    rel = np.sqrt(sum((se_p / x) ** 2 for x in (pd, ps, pc)))
    F_pred = (3 * p_pred + 1) / 4
    se_Fpred = (3 / 4) * p_pred * rel
    delta = r["relaygate"]["F_bell"] - F_pred
    se_delta = float(np.sqrt(se_F ** 2 + se_Fpred ** 2))
    return {"F_pred": float(F_pred), "delta": float(delta), "se_delta": se_delta,
            "delta_sigma": float(delta / se_delta),
            "verdict": ("multiplicative" if abs(delta) <= 2 * se_delta
                        else ("super-multiplicative interaction (stack costs extra)" if delta < 0
                              else "sub-multiplicative (stack cheaper than layers)"))}


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 6000
    cache = {}
    def get(arm, name):
        if (arm, name) not in cache:
            _, pa, pb, bas = next(s for s in SETTINGS if s[0] == name)
            cache[(arm, name)] = sim.run(circuit(arm, pa, pb, bas), shots=shots).result().get_counts()
        return cache[(arm, name)]
    r = analyze(get, shots)
    print("Exp175 selftest (noiseless Aer)")
    for arm in ARMS:
        tt = f"  truth_table={r[arm]['truth_table']:.3f}" if "truth_table" in r[arm] else ""
        print(f"  {arm:>10}: F_bell={r[arm]['F_bell']:.3f}{tt}")
    for arm in ("relaygate", "directebit", "cnot"):
        assert r[arm]["F_bell"] > 0.99 and r[arm]["truth_table"] > 0.99, f"{arm} must be an exact CNOT"
    assert r["swaponly"]["F_bell"] > 0.99, "swap layer must give perfect Phi+"
    nr = r["noresource"]
    assert nr["F_bell"] < 0.6 and nr["truth_table"] > 0.99, "no-resource must keep table, cap at 1/2"
    c = composition(r, shots)
    assert abs(c["delta"]) <= 3 * c["se_delta"], "noiseless composition must be consistent with 0"
    print(f"  composition: F_pred={c['F_pred']:.3f} delta={c['delta']:+.3f} ({c['delta_sigma']:+.1f} sigma)")
    print("SELFTEST PASS: relay-fed nonlocal CNOT exact through the full stack (swap -> EJS, 4 "
          "feedforward layers); falsifier keeps the table and caps at 1/2. Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    circuits, order = [], []
    for arm in ARMS:
        for name, pa, pb, bas in SETTINGS:
            if arm == "swaponly" and name not in BELL_SETTINGS:
                continue
            circuits.append(transpile(circuit(arm, pa, pb, bas), backend=backend, optimization_level=3))
            order.append([arm, name])
    sampler = SamplerV2(mode=backend); job = sampler.run(circuits, shots=shots)
    manifest = {"exp": 175, "slug": "relay_gate", "backend": backend_name, "shots": shots,
                "job_id": job.job_id(), "order": order,
                "prereg": {"primary": "relaygate F_bell > 1/2 at >=5 sigma AND truth_table > 0.82",
                           "band": "relaygate F_bell 0.58-0.73; tt 0.78-0.88",
                           "composition": "p_pred = p(directebit)*p(swaponly)/p(cnot); |delta|<=2sigma "
                                          "=> layers price multiplicatively",
                           "falsifier": "noresource truth_table > 0.85 AND F_bell < 0.6",
                           "gauges": "swaponly 0.72-0.90, directebit 0.72-0.85, cnot 0.95-0.99"}}
    out = os.path.join(HERE, "..", "results", "exp175_relay_gate_manifest.json")
    json.dump(manifest, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    mp = os.path.join(HERE, "..", "results", "exp175_relay_gate_manifest.json")
    svc = _get_ibm_service(); man = json.load(open(mp)); res = svc.job(man["job_id"]).result()
    shots = man["shots"]
    raw = {}
    for idx, (arm, name) in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[(arm, name)] = getattr(r0.data, reg).get_counts()
    r = analyze(lambda arm, name: raw[(arm, name)], shots)
    se = 0.75 / np.sqrt(shots)
    print(f"Exp175 RELAY COMPUTER decode | job {man['job_id']} | backend {man['backend']}")
    for arm in ARMS:
        tt = f"  tt={r[arm]['truth_table']:.3f}" if "truth_table" in r[arm] else ""
        print(f"  {arm:>10}: F_bell={r[arm]['F_bell']:.3f}{tt}  "
              f"(ZZ={r[arm]['ZZ']:+.2f} XX={r[arm]['XX']:+.2f} YY={r[arm]['YY']:+.2f})")
    t = r["relaygate"]; nsig = (t["F_bell"] - 0.5) / se
    c = composition(r, shots)
    ok = (t["F_bell"] > 0.5 and nsig > 5 and t["truth_table"] > 0.82
          and r["noresource"]["F_bell"] < 0.6 and r["noresource"]["truth_table"] > 0.85)
    print(f"\nRELAY-FED nonlocal CNOT: Bell F={t['F_bell']:.3f} ({nsig:.0f} sigma over the 1/2 witness) "
          f"| truth table {t['truth_table']:.3f}")
    print(f"STACK ACCOUNTING (same job): cnot {r['cnot']['F_bell']:.3f} -> directebit "
          f"{r['directebit']['F_bell']:.3f} (EJS cost) -> relaygate {t['F_bell']:.3f} (relay cost); "
          f"link quality swaponly {r['swaponly']['F_bell']:.3f}")
    print(f"COMPOSITION TEST: F_pred={c['F_pred']:.3f} vs measured {t['F_bell']:.3f} -> "
          f"delta={c['delta']:+.3f} ({c['delta_sigma']:+.1f} sigma) => {c['verdict']}")
    print(f"FALSIFIER: no-resource F_bell={r['noresource']['F_bell']:.3f}, "
          f"tt={r['noresource']['truth_table']:.2f} (classical shadow: table survives, witness caps)")
    print(f"VERDICT: {'RELAY COMPUTER WORKS — an entangling gate ran between qubits that never met, on an e-bit from a relay neither controls' if ok else 'FAILED a gate (honest accounting above)'}")
    out = {"job_id": man["job_id"], "results": r, "relaygate_sigma": float(nsig),
           "composition": c, "verdict_ok": bool(ok)}
    json.dump(out, open(os.path.join(HERE, "..", "results", "exp175_relay_gate_decode.json"), "w"), indent=1)
    print("-> results/exp175_relay_gate_decode.json")


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
