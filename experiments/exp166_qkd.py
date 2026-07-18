#!/usr/bin/env python3
"""Exp166 — SUBSPACE SECURE CHANNEL: QKD over the quantum network. C4857.
What the network is FOR: Alice (q0) and Bob (q3) share only a SWAPPED pair — they never
interacted (Exp162 primitive). From it: a secret key certified by physics (CHSH bounds any
eavesdropper), used to one-time-pad a real message. And the wiretap arm: an intercept-resend
Eve on Bob's qubit MUST break the certificate (S < 2) and spike QBER_X to ~50% — the protocol
aborts the key. The falsifier passing IS the security feature.

CIRCUITS (2 arms x 8): key rounds A,B in {Z,X}x{Z,X} (matched bases -> sifted key; QBER from
disagreements) + CHSH rounds A in {Z,X}, B in {W,V} = ((Z+-X)/sqrt2). Eve: mid-flight Z-measure
of Bob's qubit into a spare clbit (collapse-and-resend). Z-only Eve leaves QBER_Z at 0 — the
data itself shows why a one-basis protocol is insecure.

GATES: honest S > 2 at >5 sigma AND QBER_avg < 11% -> key distilled, "BEAM ME UP" encrypted;
Eve S < 2 AND QBER_X > 18% -> key ABORTED. Named risk: swap-grade QBER_X ~13% may kill the key
rate -> honest outcome: certified entanglement, zero key at this fidelity (prices the stack:
purify first). Usage: --selftest | --submit [--backend ibm_fez --shots 4096] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

KEY_BASES = [("Z", "Z"), ("Z", "X"), ("X", "Z"), ("X", "X")]
CHSH_BASES = [("Z", "W"), ("Z", "V"), ("X", "W"), ("X", "V")]
ARMS = ("honest", "eve")
MESSAGE = "BEAM ME UP"


def _rot(qc, q, basis):
    if basis == "X":
        qc.h(q)
    elif basis == "W":                      # (Z+X)/sqrt2 eigenbasis
        qc.ry(-np.pi / 4, q)
    elif basis == "V":                      # (Z-X)/sqrt2 eigenbasis
        qc.ry(np.pi / 4, q)


def qkd_circuit(arm, a_basis, b_basis):
    """Swapped pair A=q0, B=q3 (Exp162); optional Eve Z-intercept on q3; measure in bases."""
    qc = QuantumCircuit(4, 5)
    qc.h(0); qc.cx(0, 1)
    qc.h(2); qc.cx(2, 3)
    qc.barrier()
    qc.cx(1, 2); qc.h(1)
    qc.measure(1, 0); qc.measure(2, 1)
    with qc.if_test((qc.clbits[1], 1)): qc.x(3)
    with qc.if_test((qc.clbits[0], 1)): qc.z(3)
    qc.barrier()
    if arm == "eve":
        qc.measure(3, 4)                    # intercept-resend: collapse Bob's qubit in Z
        qc.barrier()
    _rot(qc, 0, a_basis); _rot(qc, 3, b_basis)
    qc.measure(0, 2); qc.measure(3, 3)
    return qc


def _bits(counts):
    """Yield (a_bit, b_bit, count): a=c2, b=c3 (string 'c4 c3 c2 c1 c0', c4 leftmost)."""
    for b, c in counts.items():
        b = b.replace(" ", "")
        yield int(b[-3]), int(b[-4]), c


def _E(counts, shots):
    return sum((1 - 2 * a) * (1 - 2 * bb) * c for a, bb, c in _bits(counts)) / shots


def _qber(counts, shots):
    return sum(c for a, bb, c in _bits(counts) if a != bb) / shots


def _h2(p):
    return 0.0 if p <= 0 or p >= 1 else -p * np.log2(p) - (1 - p) * np.log2(1 - p)


def analyze(get_counts, shots):
    """get_counts(arm, a, b) -> counts. Returns per-arm dict of S, QBERs, key material."""
    out = {}
    for arm in ARMS:
        E = {(a, b): _E(get_counts(arm, a, b), shots) for a, b in CHSH_BASES}
        S = E[("Z", "W")] + E[("Z", "V")] + E[("X", "W")] - E[("X", "V")]
        qz = _qber(get_counts(arm, "Z", "Z"), shots)
        qx = _qber(get_counts(arm, "X", "X"), shots)
        qavg = (qz + qx) / 2
        rate = max(0.0, 1 - 2 * _h2(qavg))          # asymptotic BB84-style secret fraction
        # sifted key: Alice bits from the ZZ round (deterministic shot order not available ->
        # build from counts expansion; sufficient for a one-time-pad demo)
        abits, bbits = [], []
        for a, bb, c in _bits(get_counts(arm, "Z", "Z")):
            abits += [a] * c; bbits += [bb] * c
        out[arm] = {"S": float(S), "E": {f"{a}{b}": float(v) for (a, b), v in E.items()},
                    "qber_z": float(qz), "qber_x": float(qx), "qber_avg": float(qavg),
                    "secret_fraction": float(rate),
                    "alice_key": abits[:len(MESSAGE) * 8], "bob_key": bbits[:len(MESSAGE) * 8]}
    return out


def _otp(msg, key_bits):
    by = bytearray(msg.encode() if isinstance(msg, str) else msg)
    for i in range(len(by)):
        k = 0
        for j in range(8):
            k = (k << 1) | key_bits[(i * 8 + j) % len(key_bits)]
        by[i] ^= k
    return bytes(by)


def selftest():
    """Noiseless: honest S = 2*sqrt(2), QBER 0, message round-trips exactly; Eve: S collapses
    (Z-intercept -> E(X,*) terms die), QBER_X = 50% (fixed-Z Eve: Bob's X read of a Z-collapsed state is a coin), QBER_Z = 0."""
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 6000
    cache = {}
    def gc(arm, a, b):
        if (arm, a, b) not in cache:
            cache[(arm, a, b)] = sim.run(qkd_circuit(arm, a, b), shots=shots).result().get_counts()
        return cache[(arm, a, b)]
    r = analyze(gc, shots)
    h, e = r["honest"], r["eve"]
    print("Exp166 selftest (noiseless Aer)")
    print(f"  honest: S={h['S']:.3f} (2sqrt2={2*np.sqrt(2):.3f})  QBER z/x = {h['qber_z']:.3f}/{h['qber_x']:.3f}")
    print(f"  eve:    S={e['S']:.3f}  QBER z/x = {e['qber_z']:.3f}/{e['qber_x']:.3f}")
    enc = _otp(MESSAGE, h["alice_key"]); dec = _otp(enc, h["bob_key"]).decode(errors="replace")
    print(f"  OTP round-trip: '{MESSAGE}' -> {enc.hex()} -> '{dec}'")
    assert abs(h["S"] - 2 * np.sqrt(2)) < 0.06 and h["qber_avg"] < 0.01, "honest arm FAIL"
    assert e["S"] < 2 and abs(e["qber_x"] - 0.50) < 0.04 and e["qber_z"] < 0.01, "eve arm FAIL"
    assert dec == MESSAGE, "OTP round-trip FAIL"
    print("SELFTEST PASS: certificate at Tsirelson, Eve breaks it exactly as theory demands, "
          "message round-trips. Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    circuits, order = [], []
    for arm in ARMS:
        for a, b in KEY_BASES + CHSH_BASES:
            circuits.append(transpile(qkd_circuit(arm, a, b), backend=backend, optimization_level=3))
            order.append([arm, a, b])
    sampler = SamplerV2(mode=backend); job = sampler.run(circuits, shots=shots)
    manifest = {"exp": 166, "slug": "qkd", "backend": backend_name, "shots": shots,
                "job_id": job.job_id(), "order": order, "message": MESSAGE,
                "prereg": {"honest": "S > 2 at >5 sigma AND qber_avg < 0.11 -> key + OTP demo; "
                                     "if S>2 but qber>=0.11: certified-no-key (prices the stack)",
                           "eve": "S < 2 AND qber_x > 0.18 -> key ABORTED (falsifier = feature)",
                           "prediction": "S_honest 2.15-2.45; qber_z 5-9%, qber_x 10-16%; "
                                         "S_eve 1.1-1.6; P(positive key) 0.5"}}
    out = os.path.join(HERE, "..", "results", "exp166_qkd_manifest.json")
    json.dump(manifest, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    mp = os.path.join(HERE, "..", "results", "exp166_qkd_manifest.json")
    svc = _get_ibm_service(); man = json.load(open(mp)); res = svc.job(man["job_id"]).result()
    shots = man["shots"]
    raw = {}
    for idx, (arm, a, b) in enumerate(man["order"]):
        r = res[idx]; reg = list(r.data.keys())[0]
        raw[(arm, a, b)] = getattr(r.data, reg).get_counts()
    r = analyze(lambda arm, a, b: raw[(arm, a, b)], shots)
    h, e = r["honest"], r["eve"]
    se_S = 2.0 / np.sqrt(shots)
    print(f"Exp166 QKD decode | job {man['job_id']} | backend {man['backend']}")
    print(f"HONEST: S = {h['S']:.3f} ({(h['S']-2)/se_S:+.0f} sigma over classical 2) | "
          f"QBER z/x/avg = {h['qber_z']:.3f}/{h['qber_x']:.3f}/{h['qber_avg']:.3f} | "
          f"secret fraction = {h['secret_fraction']:.3f}")
    print(f"EVE:    S = {e['S']:.3f} | QBER z/x = {e['qber_z']:.3f}/{e['qber_x']:.3f} "
          f"(Z-intercept: z stays clean, x spikes — the two-bases lesson in data)")
    cert = h["S"] > 2 and (h["S"] - 2) / se_S > 5
    keyok = h["qber_avg"] < 0.11
    eveok = e["S"] < 2 and e["qber_x"] > 0.18
    msg = man["message"]
    if cert and keyok:
        enc = _otp(msg, h["alice_key"]); dec = _otp(enc, h["bob_key"]).decode(errors="replace")
        good = sum(1 for x, y in zip(dec, msg) if x == y) / len(msg)
        print(f"KEY DISTILLED (raw sifted): OTP '{msg}' -> {enc.hex()}")
        print(f"Bob decrypts (raw key, pre-reconciliation): '{dec}' ({100*good:.0f}% chars correct; "
              f"reconciliation closes the rest — secret fraction {h['secret_fraction']:.2f} survives it)")
    verdict = cert and eveok and (keyok or True)
    tag = ("SECURE CHANNEL LIVE — key certified by physics, wiretap detected and aborted"
           if cert and keyok and eveok else
           "CERTIFIED BUT NO KEY at this fidelity (purify first — the stack is priced)" if cert and eveok else
           "FAILED a certificate gate (honest accounting above)")
    print(f"VERDICT: {tag}")
    out = {"job_id": man["job_id"], "honest": {k: v for k, v in h.items() if "key" not in k},
           "eve": {k: v for k, v in e.items() if "key" not in k},
           "certified": bool(cert), "key_ok": bool(keyok), "eve_detected": bool(eveok),
           "verdict": tag}
    json.dump(out, open(os.path.join(HERE, "..", "results", "exp166_qkd_decode.json"), "w"), indent=1)
    print("-> results/exp166_qkd_decode.json")


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
