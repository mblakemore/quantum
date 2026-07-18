#!/usr/bin/env python3
"""Exp168 — GHZ CONFERENCE KEY: a secret key three parties share at once. C4859.
Multi-party subspace channel: one GHZ trio |000>+|111> gives Alice(q0)/Bob(q1)/Charlie(q2) a
SHARED conference key (all measure Z -> the same bit), certified by the MERMIN inequality
(classical bound 2, GHZ reaches 4 — genuine 3-party nonlocality, not three pairwise Bell tests).
Wiretap arm: intercept-resend on Charlie collapses Mermin below 2 and spikes the X/Y-basis error
-> the protocol aborts. Z-basis Eve leaves ZZZ clean (the two-bases lesson, now 3-party).

GATES: honest M > 2 at >5 sigma AND conference QBER < 11% -> broadcast-OTP "ENGAGE" to all three;
Eve M < 2 AND Mermin-basis error high -> aborted. Usage: --selftest|--submit|--decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
from exp166_qkd import _otp, _h2

MERMIN = [("X", "X", "X"), ("X", "Y", "Y"), ("Y", "X", "Y"), ("Y", "Y", "X")]  # M = XXX-XYY-YXY-YYX
KEY_SETTING = ("Z", "Z", "Z")
ARMS = ("honest", "eve")
MESSAGE = "ENGAGE"


def _rot(qc, q, basis):
    if basis == "X":
        qc.h(q)
    elif basis == "Y":
        qc.sdg(q); qc.h(q)


def ghz_circuit(arm, bases):
    """GHZ on q0,q1,q2; optional Eve Z-intercept on Charlie (q2); measure in the given bases."""
    qc = QuantumCircuit(3, 4)
    qc.h(0); qc.cx(0, 1); qc.cx(1, 2)
    qc.barrier()
    if arm == "eve":
        qc.measure(2, 3)                       # intercept-resend collapse of Charlie
        qc.barrier()
    for q, b in enumerate(bases):
        _rot(qc, q, b)
    qc.measure(0, 0); qc.measure(1, 1); qc.measure(2, 2)
    return qc


def _bits(counts):
    """(a=c0, b=c1, c=c2, count). String 'c3c2c1c0'."""
    for bstr, cnt in counts.items():
        s = bstr.replace(" ", "")
        yield int(s[-1]), int(s[-2]), int(s[-3]), cnt


def _E3(counts, shots):
    return sum((1 - 2 * a) * (1 - 2 * b) * (1 - 2 * c) * n for a, b, c, n in _bits(counts)) / shots


def _mermin(gc, shots):
    E = {s: _E3(gc(s), shots) for s in MERMIN}
    return E[MERMIN[0]] - E[MERMIN[1]] - E[MERMIN[2]] - E[MERMIN[3]], E


def _conf_qber(counts, shots):
    """Max pairwise disagreement of the three Z bits (conference-key error)."""
    dab = sum(n for a, b, c, n in _bits(counts) if a != b) / shots
    dac = sum(n for a, b, c, n in _bits(counts) if a != c) / shots
    return max(dab, dac), dab, dac


def analyze(get, shots):
    out = {}
    for arm in ARMS:
        M, E = _mermin(lambda s: get(arm, s), shots)
        kc = get(arm, KEY_SETTING)
        q, dab, dac = _conf_qber(kc, shots)
        sf = max(0.0, 1 - 2 * _h2(q))
        abits, bbits = [], []
        for a, b, c, n in _bits(kc):
            abits += [a] * n; bbits += [b] * n
        out[arm] = {"mermin": float(M), "E": {"".join(s): float(v) for s, v in E.items()},
                    "conf_qber": float(q), "qber_ab": float(dab), "qber_ac": float(dac),
                    "secret_fraction": float(sf),
                    "alice_key": abits[:len(MESSAGE) * 8], "bob_key": bbits[:len(MESSAGE) * 8]}
    return out


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 8000
    cache = {}
    def get(arm, s):
        if (arm, s) not in cache:
            cache[(arm, s)] = sim.run(ghz_circuit(arm, s), shots=shots).result().get_counts()
        return cache[(arm, s)]
    r = analyze(get, shots)
    h, e = r["honest"], r["eve"]
    print("Exp168 selftest (noiseless Aer)")
    print(f"  honest: M={h['mermin']:.3f} (GHZ=4)  conf_QBER={h['conf_qber']:.3f}  SF={h['secret_fraction']:.3f}")
    print(f"  eve:    M={e['mermin']:.3f}  conf_QBER={e['conf_qber']:.3f}")
    enc = _otp(MESSAGE, h["alice_key"]); dec = _otp(enc, h["bob_key"]).decode(errors="replace")
    print(f"  broadcast OTP: '{MESSAGE}' -> {enc.hex()} -> '{dec}'")
    assert h["mermin"] > 3.9 and h["conf_qber"] < 0.01, "honest GHZ FAIL"
    assert e["mermin"] < 2.05 and e["conf_qber"] < 0.05, "eve arm FAIL (M must fall, ZZZ stays clean)"
    assert dec == MESSAGE, "broadcast OTP FAIL"
    print("SELFTEST PASS: Mermin at 4 (GHZ), Eve collapses it below the classical 2 while ZZZ stays "
          "clean, broadcast round-trips. Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    settings = MERMIN + [KEY_SETTING]
    circuits, order = [], []
    for arm in ARMS:
        for s in settings:
            circuits.append(transpile(ghz_circuit(arm, s), backend=backend, optimization_level=3))
            order.append([arm, list(s)])
    sampler = SamplerV2(mode=backend); job = sampler.run(circuits, shots=shots)
    manifest = {"exp": 168, "slug": "conference", "backend": backend_name, "shots": shots,
                "job_id": job.job_id(), "order": order, "message": MESSAGE,
                "prereg": {"honest": "Mermin > 2 at >5 sigma AND conf_qber < 0.11 -> broadcast key",
                           "eve": "Mermin < 2 AND Mermin-basis collapse -> aborted",
                           "prediction": "M 3.0-3.6; conf_qber 4-9%; positive key; Eve M 1.5-2.2"}}
    out = os.path.join(HERE, "..", "results", "exp168_conference_manifest.json")
    json.dump(manifest, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    mp = os.path.join(HERE, "..", "results", "exp168_conference_manifest.json")
    svc = _get_ibm_service(); man = json.load(open(mp)); res = svc.job(man["job_id"]).result()
    shots = man["shots"]
    raw = {}
    for idx, (arm, s) in enumerate(man["order"]):
        r = res[idx]; reg = list(r.data.keys())[0]
        raw[(arm, tuple(s))] = getattr(r.data, reg).get_counts()
    r = analyze(lambda arm, s: raw[(arm, tuple(s))], shots)
    h, e = r["honest"], r["eve"]
    se_M = 4.0 / np.sqrt(shots)
    print(f"Exp168 GHZ CONFERENCE KEY decode | job {man['job_id']} | backend {man['backend']}")
    print(f"HONEST: Mermin M = {h['mermin']:.3f} ({(h['mermin']-2)/se_M:+.0f} sigma over classical 2) | "
          f"conf QBER = {h['conf_qber']:.3f} (A-B {h['qber_ab']:.3f}, A-C {h['qber_ac']:.3f}) | SF = {h['secret_fraction']:.3f}")
    print(f"EVE:    Mermin M = {e['mermin']:.3f} | conf QBER = {e['conf_qber']:.3f} "
          f"(Z-intercept: ZZZ stays clean, Mermin collapses — the two-bases lesson, 3-party)")
    cert = h["mermin"] > 2 and (h["mermin"] - 2) / se_M > 5
    keyok = h["conf_qber"] < 0.11 and h["secret_fraction"] > 0
    eveok = e["mermin"] < 2
    msg = man["message"]
    if cert and keyok and len(h["alice_key"]) >= len(msg) * 8:
        enc = _otp(msg, h["alice_key"]); dec = _otp(enc, h["bob_key"]).decode(errors="replace")
        good = sum(1 for x, y in zip(dec, msg) if x == y) / len(msg)
        print(f"CONFERENCE KEY: broadcast '{msg}' -> {enc.hex()} -> Bob reads '{dec}' ({100*good:.0f}% chars; "
              f"Charlie holds the same key)")
    tag = ("3-PARTY CONFERENCE KEY LIVE — one GHZ trio, one shared key certified by Mermin, wiretap aborts"
           if cert and keyok and eveok else
           "CERTIFIED but no key at this fidelity" if cert and eveok else
           "FAILED a certificate gate (honest accounting above)")
    print(f"VERDICT: {tag}")
    out = {"job_id": man["job_id"], "honest": {k: v for k, v in h.items() if "key" not in k},
           "eve": {k: v for k, v in e.items() if "key" not in k},
           "certified": bool(cert), "key_ok": bool(keyok), "eve_detected": bool(eveok), "verdict": tag}
    json.dump(out, open(os.path.join(HERE, "..", "results", "exp168_conference_decode.json"), "w"), indent=1)
    print("-> results/exp168_conference_decode.json")


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
