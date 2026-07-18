#!/usr/bin/env python3
"""Exp176 — THE REPEATER CHAIN: composition-tax dose-response over N = 0, 1, 2 swaps. C4863.
Where does Exp175's composition tax live? Vary the feedforward-window count parametrically in a
PURE link-layer chain: direct Bell (N=0), single swap (N=1, Exp162 replica), two-station repeater
chain (N=2: 3 Bell pairs, sequential Bell measurements + literal per-stage corrections).

SCALING TEST (pre-registered, Werner p=(4F-1)/3): multiplicative model predicts p2 = p1^2/p0.
  Delta2 < -2 sigma  -> tax compounds with window count (dose-response within the link layer).
  |Delta2| <= 2 sigma -> link x link multiplies -> Exp175's tax lives at the link x compute
                         INTERFACE, not in feedforward windows generically.
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
from exp162_swap import fidelity

ARMS = ("direct", "swap1", "swap2")
SETTINGS = ("ZZ", "XX", "YY")
WITNESS = 0.5


def _swap_stage(qc, m1, m2, tgt, c0, c1):
    """Bell-measure (m1,m2), feedforward X/Z onto tgt — one full swap episode (Exp162 layer)."""
    qc.cx(m1, m2); qc.h(m1)
    qc.measure(m1, c0); qc.measure(m2, c1)
    with qc.if_test((qc.clbits[c1], 1)): qc.x(tgt)
    with qc.if_test((qc.clbits[c0], 1)): qc.z(tgt)


def _verify(qc, qa, qb, setting, ca, cb):
    for q in (qa, qb):
        if setting == "XX": qc.h(q)
        elif setting == "YY": qc.sdg(q); qc.h(q)
    qc.measure(qa, ca); qc.measure(qb, cb)


def chain_circuit(arm, setting):
    """direct: A=q0,B=q1. swap1: A=q0,B1=q1,B2=q2,C=q3. swap2: A=q0..D=q5.
    Verify clbits: last two (c4,c5 in a 6-clbit frame used for all arms for uniform decode)."""
    qc = QuantumCircuit(6, 6)
    if arm == "direct":
        qc.h(0); qc.cx(0, 1)
        _verify(qc, 0, 1, setting, 4, 5)
    elif arm == "swap1":
        qc.h(0); qc.cx(0, 1)          # Bell(A,B1)
        qc.h(2); qc.cx(2, 3)          # Bell(B2,C)
        qc.barrier()
        _swap_stage(qc, 1, 2, 3, 0, 1)
        qc.barrier()
        _verify(qc, 0, 3, setting, 4, 5)
    else:  # swap2
        qc.h(0); qc.cx(0, 1)          # Bell(A,B1)
        qc.h(2); qc.cx(2, 3)          # Bell(B2,C1)
        qc.h(4); qc.cx(4, 5)          # Bell(C2,D)
        qc.barrier()
        _swap_stage(qc, 1, 2, 3, 0, 1)   # station 1: A-C1 entangled
        qc.barrier()
        _swap_stage(qc, 3, 4, 5, 2, 3)   # station 2: A-D entangled
        qc.barrier()
        _verify(qc, 0, 5, setting, 4, 5)
    return qc


def _parity(counts, shots):
    """<P P> from clbits c4,c5 (string 'c5c4c3c2c1c0')."""
    acc = 0
    for b, c in counts.items():
        b = b.replace(" ", "")
        s = (1 if b[-5] == "0" else -1) * (1 if b[-6] == "0" else -1)
        acc += s * c
    return acc / shots


def analyze(get, shots):
    out = {}
    for arm in ARMS:
        par = {s: _parity(get(arm, s), shots) for s in SETTINGS}
        out[arm] = {"F": float(fidelity(par)), **{k: float(v) for k, v in par.items()}}
    return out


def scaling(r, shots):
    """Pre-registered: p2_pred = p1^2 / p0 (constant per-swap ratio)."""
    p = lambda F: (4 * F - 1) / 3
    se_F = 0.75 / np.sqrt(shots); se_p = (4 / 3) * se_F
    p0, p1, p2 = (p(r[a]["F"]) for a in ARMS)
    p2_pred = p1 ** 2 / p0
    rel = np.sqrt((2 * se_p / p1) ** 2 + (se_p / p0) ** 2)
    delta = p2 - p2_pred
    se_delta = float(np.sqrt(se_p ** 2 + (p2_pred * rel) ** 2))
    F2_pred = (3 * p2_pred + 1) / 4
    return {"p0": float(p0), "p1": float(p1), "p2": float(p2),
            "p2_pred": float(p2_pred), "F2_pred": float(F2_pred),
            "delta": float(delta), "se_delta": se_delta, "delta_sigma": float(delta / se_delta),
            "verdict": ("multiplicative per-stage — tax localizes to the link x compute interface"
                        if abs(delta) <= 2 * se_delta else
                        ("tax COMPOUNDS with window count (dose-response in the link layer)"
                         if delta < 0 else "sub-multiplicative (chain cheaper than stages)"))}


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 8000
    cache = {}
    def get(arm, s):
        if (arm, s) not in cache:
            cache[(arm, s)] = sim.run(chain_circuit(arm, s), shots=shots).result().get_counts()
        return cache[(arm, s)]
    r = analyze(get, shots)
    print("Exp176 selftest (noiseless Aer)")
    for arm in ARMS:
        print(f"  {arm:>6}: ZZ={r[arm]['ZZ']:+.2f} XX={r[arm]['XX']:+.2f} YY={r[arm]['YY']:+.2f} "
              f"-> F={r[arm]['F']:.3f}")
        assert r[arm]["F"] > 0.99, f"{arm} must give perfect Phi+"
    sc = scaling(r, shots)
    assert abs(sc["delta"]) <= 3 * sc["se_delta"], "noiseless scaling must be consistent with 0"
    print(f"  scaling: p2_pred={sc['p2_pred']:.3f} delta={sc['delta']:+.3f} ({sc['delta_sigma']:+.1f} sigma)")
    print("SELFTEST PASS: two-station repeater chain projects A-D into exact Phi+ through 2 "
          "sequential swap episodes; scaling test null on noiseless sim. Cleared to fly.")


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
    manifest = {"exp": 176, "slug": "chain_tax", "backend": backend_name, "shots": shots,
                "job_id": job.job_id(), "order": order, "witness": WITNESS,
                "prereg": {"primary": "F(swap2) > 1/2 at >=5 sigma (2-station chain certifies end-to-end)",
                           "band": "swap2 F 0.60-0.75; swap1 0.78-0.88; direct 0.95-0.99",
                           "scaling": "p2_pred = p1^2/p0; delta<-2sigma => tax compounds with windows; "
                                      "|delta|<=2sigma => tax lives at link x compute interface (Exp175)",
                           "fingerprint": "if compounding: ZZ >> XX/YY asymmetry grows with N"}}
    out = os.path.join(HERE, "..", "results", "exp176_chain_tax_manifest.json")
    json.dump(manifest, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    mp = os.path.join(HERE, "..", "results", "exp176_chain_tax_manifest.json")
    svc = _get_ibm_service(); man = json.load(open(mp)); res = svc.job(man["job_id"]).result()
    shots = man["shots"]
    raw = {}
    for idx, (arm, s) in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[(arm, s)] = getattr(r0.data, reg).get_counts()
    r = analyze(lambda arm, s: raw[(arm, s)], shots)
    se = 0.75 / np.sqrt(shots)
    sc = scaling(r, shots)
    print(f"Exp176 REPEATER CHAIN decode | job {man['job_id']} | backend {man['backend']}")
    for arm in ARMS:
        print(f"  {arm:>6}: ZZ={r[arm]['ZZ']:+.3f} XX={r[arm]['XX']:+.3f} YY={r[arm]['YY']:+.3f} "
              f"-> F = {r[arm]['F']:.3f}")
    nsig = (r["swap2"]["F"] - WITNESS) / se
    print(f"\nCHAIN WITNESS: F(swap2) = {r['swap2']['F']:.3f} vs 1/2 -> {nsig:.0f} sigma "
          f"(A and D: two stations apart, no shared history)")
    print(f"SCALING: p0={sc['p0']:.3f} p1={sc['p1']:.3f} p2={sc['p2']:.3f} | "
          f"multiplicative pred p2={sc['p2_pred']:.3f} (F={sc['F2_pred']:.3f})")
    print(f"DOSE-RESPONSE: delta={sc['delta']:+.3f} ({sc['delta_sigma']:+.1f} sigma) => {sc['verdict']}")
    ok = r["swap2"]["F"] > WITNESS and nsig > 5
    print(f"VERDICT: {'CHAIN CERTIFIES end-to-end' if ok else 'chain fails the witness (honest accounting above)'}"
          f" | scaling branch: {sc['verdict']}")
    out = {"job_id": man["job_id"], "results": r, "swap2_sigma": float(nsig), "scaling": sc,
           "verdict_ok": bool(ok)}
    json.dump(out, open(os.path.join(HERE, "..", "results", "exp176_chain_tax_decode.json"), "w"), indent=1)
    print("-> results/exp176_chain_tax_decode.json")


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
