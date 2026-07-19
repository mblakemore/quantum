#!/usr/bin/env python3
"""Exp181 — THE DISTRIBUTED COMPUTER: Bernstein-Vazirani across a cut. C4869.
Alice (data a1,a2) and Bob (oracle ancilla) never touch; every oracle CNOT crosses the cut as an
EJS teleported gate consuming a pre-shared e-bit. The arc's lessons make it architecturally
clean: the X^x correction hits Bob's |-> ancilla = GLOBAL PHASE (dropped); the Z^z correction
commutes through Alice's final H = CLASSICAL XOR at decode (s_i = m_i ^ z_i). So the distributed
algorithm runs with ZERO live feedforward and ZERO mid-circuit measurement — one merged final
measurement layer (Exp179's architecture applied to computation).

Layout: a1=q0, a2=q1, anc=q2, ebit1=(e1=q3, e2=q4), ebit2=(e1=q5, e2=q6).
clbits: c0=m1(q0), c1=m2(q1), c2=z1(q4), c3=z2(q6), c4=q3, c5=q5, c6=anc(q2) [c4-c6 discards].
Arms: local (direct CNOTs) | dist (teleported) | noresource (e-bits |00> — falsifier: every
gate-bearing bit degrades to a coin flip; s=11 lands at the 2-bit guessing floor 0.25).
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

ARMS = ("local", "dist", "noresource")
STRINGS = ("00", "01", "10", "11")   # s = s2 s1 (string index i=1 -> a1=q0, i=2 -> a2=q1)
EBIT = {1: (3, 4), 2: (5, 6)}        # per data qubit: (e1, e2)


def bv_circuit(arm, s):
    """s is 's2s1' as displayed; s1 acts on q0, s2 on q1."""
    qc = QuantumCircuit(7, 7)
    bits = {1: int(s[1]), 2: int(s[0])}
    qc.h(0); qc.h(1)                  # Alice data |+>
    qc.x(2); qc.h(2)                  # Bob ancilla |->
    if arm != "local":                # e-bit prep (dist: Bell; noresource: left |00>)
        for i in (1, 2):
            e1, e2 = EBIT[i]
            if arm == "dist":
                qc.h(e1); qc.cx(e1, e2)
    qc.barrier()
    for i in (1, 2):                  # the oracle: CNOT(a_i -> anc) for s_i = 1
        if not bits[i]:
            continue
        a = i - 1
        if arm == "local":
            qc.cx(a, 2)
        else:
            e1, e2 = EBIT[i]
            qc.cx(a, e1)              # Alice half of EJS (e1 measured at the end; x discarded —
            qc.cx(e2, 2)              #   X^x on the |-> ancilla is global phase)
            qc.h(e2)                  # Bob half; e2's Z-measurement gives z_i -> decode XOR
    qc.barrier()
    qc.h(0); qc.h(1)                  # BV final Hadamards
    qc.barrier()                      # ONE merged measurement layer — no mid-circuit windows
    qc.measure(0, 0); qc.measure(1, 1)
    qc.measure(4, 2); qc.measure(6, 3)
    qc.measure(3, 4); qc.measure(5, 5); qc.measure(2, 6)
    return qc


def decode_shot(bstr, arm, s):
    """Return the decoded 2-bit string 's2s1' for one shot."""
    b = bstr.replace(" ", "")
    m1, m2 = int(b[-1]), int(b[-2])
    z1, z2 = int(b[-3]), int(b[-4])
    if arm != "local":
        if int(s[1]): m1 ^= z1        # frame Z on a1 -> readout flip
        if int(s[0]): m2 ^= z2
    return f"{m2}{m1}"


def analyze(get, shots):
    out = {}
    for arm in ARMS:
        per = {}
        for s in STRINGS:
            counts = get(arm, s)
            tallies = {}
            for bstr, n in counts.items():
                d = decode_shot(bstr, arm, s)
                tallies[d] = tallies.get(d, 0) + n
            p = tallies.get(s, 0) / shots
            modal = max(tallies, key=tallies.get)
            per[s] = {"P_correct": float(p), "modal": modal, "modal_ok": modal == s}
        nontrivial = [per[s]["P_correct"] for s in ("01", "10", "11")]
        out[arm] = {"per_string": per, "avg_nontrivial": float(np.mean(nontrivial))}
    return out


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 8000
    cache = {}
    def get(arm, s):
        if (arm, s) not in cache:
            cache[(arm, s)] = sim.run(bv_circuit(arm, s), shots=shots).result().get_counts()
        return cache[(arm, s)]
    r = analyze(get, shots)
    print("Exp181 selftest (noiseless Aer)")
    for arm in ARMS:
        row = "  ".join(f"{s}:{r[arm]['per_string'][s]['P_correct']:.3f}" for s in STRINGS)
        print(f"  {arm:>10}: {row}  avg(01,10,11)={r[arm]['avg_nontrivial']:.3f}")
    for arm in ("local", "dist"):
        for s in STRINGS:
            assert r[arm]["per_string"][s]["P_correct"] > 0.999, f"{arm}/{s} must be exact"
    nr = r["noresource"]["per_string"]
    assert nr["00"]["P_correct"] > 0.999, "noresource s=00 has no gates -> exact"
    for s in ("01", "10"):
        assert abs(nr[s]["P_correct"] - 0.5) < 0.03, f"noresource {s} must be a coin flip"
    assert abs(nr["11"]["P_correct"] - 0.25) < 0.03, "noresource 11 must hit the guessing floor"
    print("SELFTEST PASS: distributed BV exact with ZERO feedforward and ZERO mid-circuit "
          "measurement (X-correction = global phase on |->; Z-correction = decode XOR); "
          "falsifier degrades to the classical guessing floor. Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    circuits, order = [], []
    for arm in ARMS:
        for s in STRINGS:
            circuits.append(transpile(bv_circuit(arm, s), backend=backend, optimization_level=3))
            order.append([arm, s])
    sampler = SamplerV2(mode=backend); job = sampler.run(circuits, shots=shots)
    manifest = {"exp": 181, "slug": "dist_bv", "backend": backend_name, "shots": shots,
                "job_id": job.job_id(), "order": order,
                "prereg": {"primary": "dist beats noresource on 01/10/11 at >=3 sigma each and on the "
                                      "3-string average at >=5 sigma; dist modal string correct 4/4",
                           "bands": "local all 0.90-0.99; dist 00:0.92-0.99, 01/10:0.78-0.92, "
                                    "11:0.62-0.85, avg 0.68-0.88; noresource 01/10:0.40-0.55, 11:0.18-0.32",
                           "physics": "falsifier floor = classical guessing bound (no e-bit -> coin flips)",
                           "note": "P(11)/P(01) reported as per-gate composition cost vs Exp175 expectation"}}
    out = os.path.join(HERE, "..", "results", "exp181_dist_bv_manifest.json")
    json.dump(manifest, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    mp = os.path.join(HERE, "..", "results", "exp181_dist_bv_manifest.json")
    svc = _get_ibm_service(); man = json.load(open(mp)); res = svc.job(man["job_id"]).result()
    shots = man["shots"]
    raw = {}
    for idx, (arm, s) in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[(arm, s)] = getattr(r0.data, reg).get_counts()
    r = analyze(lambda arm, s: raw[(arm, s)], shots)
    se = lambda p: np.sqrt(max(p * (1 - p), 1e-9) / shots)
    print(f"Exp181 DISTRIBUTED COMPUTER decode | job {man['job_id']} | backend {man['backend']}")
    for arm in ARMS:
        row = "  ".join(f"{s}:{r[arm]['per_string'][s]['P_correct']:.3f}"
                        f"{'*' if not r[arm]['per_string'][s]['modal_ok'] else ''}" for s in STRINGS)
        print(f"  {arm:>10}: {row}  avg={r[arm]['avg_nontrivial']:.3f}   (* = wrong modal string)")
    d, n = r["dist"], r["noresource"]
    sigs = {}
    for s in ("01", "10", "11"):
        dp, np_ = d["per_string"][s]["P_correct"], n["per_string"][s]["P_correct"]
        sigs[s] = (dp - np_) / np.sqrt(se(dp) ** 2 + se(np_) ** 2)
    davg, navg = d["avg_nontrivial"], n["avg_nontrivial"]
    sig_avg = (davg - navg) / np.sqrt(sum(se(d['per_string'][s]['P_correct'])**2 +
                                          se(n['per_string'][s]['P_correct'])**2 for s in ("01","10","11")) / 9)
    modal4 = all(d["per_string"][s]["modal_ok"] for s in STRINGS)
    p11, p01 = d["per_string"]["11"]["P_correct"], d["per_string"]["01"]["P_correct"]
    print(f"\nPER-STRING dist vs noresource: " +
          " ".join(f"{s}:+{sigs[s]:.0f}σ" for s in ("01", "10", "11")))
    print(f"AVERAGE (nontrivial): dist {davg:.3f} vs noresource {navg:.3f} -> +{sig_avg:.0f} sigma")
    print(f"MODAL: distributed computer reads the RIGHT hidden string as top outcome: "
          f"{'4/4 — every program returned its answer' if modal4 else 'FAILED on some string'}")
    print(f"PER-GATE COST (2nd teleported gate): P(11)/P(01) = {p11/p01:.3f}" if p01 > 0 else "")
    ok = all(sigs[s] >= 3 for s in sigs) and sig_avg >= 5 and modal4
    print(f"PRIMARY: {'HELD — TWO PROCESSORS THAT NEVER TOUCHED RAN ONE ALGORITHM AND GOT THE RIGHT ANSWER' if ok else 'NOT HELD (honest accounting above)'}")
    out = {"job_id": man["job_id"], "results": r,
           "sigmas": {k: float(v) for k, v in sigs.items()}, "sigma_avg": float(sig_avg),
           "modal_4of4": bool(modal4), "verdict_ok": bool(ok)}
    json.dump(out, open(os.path.join(HERE, "..", "results", "exp181_dist_bv_decode.json"), "w"), indent=1)
    print("-> results/exp181_dist_bv_decode.json")


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
