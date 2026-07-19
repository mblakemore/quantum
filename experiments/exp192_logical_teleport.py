#!/usr/bin/env python3
"""Exp192 — THE SHIELDED TRANSPORTER: teleport a logical qubit. C4884. Shields stage (iv).
Blocks M (q0-3), A (q4-7), B (q8-11). Resource = Exp191's logical Bell (A|+bar0bar>, B|0bar0bar>,
transversal CX A->B). Logical Bell measurement = transversal CX(M->A) + M read in X + A read in
Z. B carries |psi_bar> up to Xbar^Zbar1A Zbar^Xbar1M — ALL corrections defer to decode XORs
(Clifford consumption; zero windows, zero feedforward: the Exp181 architecture at the logical
level). Verify: |0bar> -> Zbar1B ^ Zbar1A = 0 ; |+bar> -> Xbar1B ^ Xbar1M = 0.
Postselect all three blocks' stabilizers. Falsifier: skip the A->B CX — the classical action
(|0bar>) survives, the quantum action (|+bar>) dies to a coin flip.
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

ARMS = ("logical", "noresource", "bare")
MSGS = ("0", "+")


def _prep_00(qc, o):      # |0bar 0bar> = GHZ4 at offset o
    qc.h(o); qc.cx(o, o + 1); qc.cx(o, o + 2); qc.cx(o, o + 3)


def _prep_p0(qc, o):      # |+bar 0bar> = Bell(o,o+1) (x) Bell(o+2,o+3)
    qc.h(o); qc.cx(o, o + 1); qc.h(o + 2); qc.cx(o + 2, o + 3)


def circuit(arm, msg):
    if arm == "bare":
        qc = QuantumCircuit(3, 3)
        if msg == "+": qc.h(0)                 # message
        qc.h(1); qc.cx(1, 2)                   # resource Bell(a=1, b=2)
        qc.barrier()
        qc.cx(0, 1)                            # Bell measurement half
        qc.barrier()
        qc.h(0)                                # message read in X
        if msg == "+": qc.h(2)                 # verify basis on b
        qc.measure(0, 0); qc.measure(1, 1); qc.measure(2, 2)
        return qc
    qc = QuantumCircuit(12, 12)
    if msg == "0": _prep_00(qc, 0)             # M = |0bar 0bar>
    else: _prep_p0(qc, 0)                      # M = |+bar 0bar>
    _prep_p0(qc, 4)                            # A = |+bar 0bar>
    _prep_00(qc, 8)                            # B = |0bar 0bar>
    qc.barrier()
    if arm == "logical":
        for i in range(4): qc.cx(4 + i, 8 + i) # resource: transversal CX A->B (the 57-sigma pair)
    qc.barrier()
    for i in range(4): qc.cx(i, 4 + i)         # logical Bell measurement half: transversal CX M->A
    qc.barrier()
    for q in range(4): qc.h(q)                 # M read in X basis
    if msg == "+":
        for q in range(8, 12): qc.h(q)         # B verify in X basis
    for q in range(12): qc.measure(q, q)
    return qc


def _stats(counts, arm, msg):
    if arm == "bare":
        acc = ok = 0
        for s, n in counts.items():
            b = s.replace(" ", "")
            m, a, dest = int(b[-1]), int(b[-2]), int(b[-3])
            acc += n
            bit = dest ^ (a if msg == "0" else m)   # frame: X^a flips Z-verify; Z^m flips X-verify
            ok += n * (1 if bit == 0 else 0)
        return {"acceptance": 1.0, "success": ok / acc}
    acc = rej = ok = 0
    for s, n in counts.items():
        b = s.replace(" ", "")
        v = [int(b[-1 - i]) for i in range(12)]
        pM = v[0] ^ v[1] ^ v[2] ^ v[3]
        pA = v[4] ^ v[5] ^ v[6] ^ v[7]
        pB = v[8] ^ v[9] ^ v[10] ^ v[11]
        if pM or pA or pB:
            rej += n; continue
        acc += n
        xbar_M = v[0] ^ v[1]                        # X-readout of M
        zbar_A = v[4] ^ v[6]                        # Z-readout of A
        if msg == "0":
            bit = (v[8] ^ v[10]) ^ zbar_A           # Zbar1B ^ Zbar1A
        else:
            bit = (v[8] ^ v[9]) ^ xbar_M            # Xbar1B ^ Xbar1M
        ok += n * (1 if bit == 0 else 0)
    tot = acc + rej
    return {"acceptance": acc / tot, "success": ok / acc if acc else 0.0, "n_acc": acc}


def analyze(get):
    return {(arm, msg): _stats(get(arm, msg), arm, msg) for arm in ARMS for msg in MSGS}


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 8000
    cache = {}
    def get(arm, msg):
        k = (arm, msg)
        if k not in cache:
            cache[k] = sim.run(circuit(arm, msg), shots=shots).result().get_counts()
        return cache[k]
    r = analyze(get)
    print("Exp192 selftest (noiseless Aer)")
    for k, v in r.items():
        print(f"  {k[0]:>10} |{k[1]}>: success={v['success']:.3f}  acc={v['acceptance']:.3f}")
    assert r[("logical", "0")]["success"] > 0.999 and r[("logical", "+")]["success"] > 0.999, \
        "the shielded transporter must be exact"
    assert abs(r[("noresource", "0")]["success"] - 0.5) < 0.02 and \
           abs(r[("noresource", "+")]["success"] - 0.5) < 0.02, \
        "without the pair NOTHING flows: both messages must die to coin flips (state teleportation has no classical shadow — unlike gate teleportation, Exp170)"
    assert r[("bare", "0")]["success"] > 0.999 and r[("bare", "+")]["success"] > 0.999
    print("SELFTEST PASS: a logical qubit teleports exactly between shields with zero windows and "
          "all corrections in decode; without the logical e-bit BOTH messages die to coin flips — "
          "state teleportation has no classical shadow (unlike gate teleportation). Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    circuits, order = [], []
    for arm in ARMS:
        for msg in MSGS:
            circuits.append(transpile(circuit(arm, msg), backend=backend, optimization_level=3))
            order.append([arm, msg])
    sampler = SamplerV2(mode=backend); job = sampler.run(circuits, shots=shots)
    manifest = {"exp": 192, "slug": "logical_teleport", "backend": backend_name, "shots": shots,
                "job_id": job.job_id(), "order": order,
                "prereg": {"primary": "P(logical,0) >= 0.85 AND P(logical,+) >= 0.85 AND "
                                      "Dplus = P(+|logical)-P(+|noresource) >= 0.35 at >=5 sigma",
                           "bands": "logical 0: 0.93-0.995; logical +: 0.88-0.98; bare 0.93-0.99",
                           "falsifier": "P(+|noresource) 0.45-0.55 AND P(0|noresource) 0.45-0.55 "
                                        "(PRE-FLIGHT CORRECTION, selftest-caught: state teleportation has NO "
                                        "classical shadow — without the pair nothing flows; my prose borrowed "
                                        "Exp170s GATE-teleport structure where classical info rides the gate chain)",
                           "gauges": "triple-block acceptance >= 0.50"}}
    out = os.path.join(HERE, "..", "results", "exp192_logical_teleport_manifest.json")
    json.dump(manifest, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    mp = os.path.join(HERE, "..", "results", "exp192_logical_teleport_manifest.json")
    svc = _get_ibm_service(); man = json.load(open(mp)); res = svc.job(man["job_id"]).result()
    shots = man["shots"]
    raw = {}
    for idx, (arm, msg) in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[(arm, msg)] = getattr(r0.data, reg).get_counts()
    r = analyze(lambda arm, msg: raw[(arm, msg)])
    se = lambda p, n: np.sqrt(max(p * (1 - p), 1e-9) / max(n, 1))
    print(f"Exp192 SHIELDED TRANSPORTER decode | job {man['job_id']} | backend {man['backend']}")
    for k, v in r.items():
        print(f"  {k[0]:>10} |{k[1]}>: success={v['success']:.4f}  acc={v['acceptance']:.3f}")
    pl0, plp = r[("logical", "0")]["success"], r[("logical", "+")]["success"]
    pn0, pnp = r[("noresource", "0")]["success"], r[("noresource", "+")]["success"]
    nlp = r[("logical", "+")].get("n_acc", shots); nnp = r[("noresource", "+")].get("n_acc", shots)
    dplus = plp - pnp
    zd = dplus / np.sqrt(se(plp, nlp) ** 2 + se(pnp, nnp) ** 2)
    p_ok = pl0 >= 0.85 and plp >= 0.85 and dplus >= 0.35 and zd >= 5
    f_ok = 0.45 <= pnp <= 0.55 and 0.45 <= pn0 <= 0.55
    print(f"\nTHE TRANSPORTER: |0bar> {pl0:.4f} | |+bar> {plp:.4f} (accepted ensembles)")
    print(f"QUANTUM ACTION: D+ = {dplus:+.4f} ({zd:.0f} sigma) — the logical e-bit is the resource")
    print(f"FALSIFIER: noresource |+bar> = {pnp:.4f} | |0bar> = {pn0:.4f} (both must be coin flips: "
          f"state teleportation has NO classical shadow)")
    print(f"REFERENCE: bare {r[('bare','0')]['success']:.4f} / {r[('bare','+')]['success']:.4f}")
    ok = p_ok and f_ok
    print(f"VERDICT: {'THE SHIELDED TRANSPORTER WORKS — a logical qubit teleported between error-detecting shields, zero windows, corrections in software' if ok else 'NOT HELD (honest accounting above)'}")
    out = {"job_id": man["job_id"],
           "results": {f"{k[0]}_{k[1]}": v for k, v in r.items()},
           "D_plus": float(dplus), "sigma_D": float(zd),
           "primary_ok": bool(p_ok), "falsifier_ok": bool(f_ok), "verdict_ok": bool(ok)}
    json.dump(out, open(os.path.join(HERE, "..", "results", "exp192_logical_teleport_decode.json"), "w"), indent=1)
    print("-> results/exp192_logical_teleport_decode.json")


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
