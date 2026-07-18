#!/usr/bin/env python3
"""Exp167 — PURIFY -> QKD: the fatter key. C4858.
The honest rung Exp166 pointed at: purification (Exp165) FIRST, then QKD (Exp166), composed in
one job. A channel degraded by 10us storage (Exp163/164 noise — the class DEJMPS provably fixes)
is run two ways: FADED (one degraded pair -> QKD directly, near-dead) vs PURIFIED (two degraded
pairs -> DEJMPS -> the surviving pair -> QKD, conditioned on coincidence). Same bases, same job:
the secret-fraction DELTA is the whole result — does distilling first fatten the key?

GATES: SF_purified > SF_faded, and purified delivers a positive key + "BEAM ME UP" where faded
cannot. Named risk: DEJMPS depth eats the gain on already-marginal pairs -> honest null pricing
composition depth. Usage: --selftest | --submit [--backend ibm_fez --shots 4096] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
from exp166_qkd import _rot, _E, _qber, _h2, _otp, KEY_BASES, CHSH_BASES

TAU_US = 10.0
ARMS = ("faded", "purified")
MESSAGE = "BEAM ME UP"


def circuit(arm, a_basis, b_basis, tau_us=TAU_US, inject_rz=0.0):
    """faded: Bell(q0,q1)+storage+QKD. purified: +Bell(q2,q3), storage both, DEJMPS, keep
    coincidence(c0,c1), QKD kept pair(q0,q1)->c2,c3. inject_rz: sim-only synthetic dephasing."""
    n = 2 if arm == "faded" else 4
    qc = QuantumCircuit(n, 4)
    qc.h(0); qc.cx(0, 1)
    if arm == "purified":
        qc.h(2); qc.cx(2, 3)
    if tau_us > 0:
        qc.barrier(); [qc.delay(tau_us, q, unit="us") for q in range(n)]
    if inject_rz:
        qc.rz(inject_rz, 1)
        if arm == "purified": qc.rz(inject_rz, 3)
    qc.barrier()
    if arm == "purified":
        qc.rx(np.pi / 2, 0); qc.rx(np.pi / 2, 2)      # DEJMPS A side
        qc.rx(-np.pi / 2, 1); qc.rx(-np.pi / 2, 3)    # B side
        qc.cx(0, 2); qc.cx(1, 3)                       # bilateral CNOTs
        qc.rx(-np.pi / 2, 0); qc.rx(np.pi / 2, 1)      # undo on kept pair
        qc.measure(2, 0); qc.measure(3, 1)             # sacrificial -> c0,c1 (coincidence)
        qc.barrier()
    _rot(qc, 0, a_basis); _rot(qc, 1, b_basis)         # QKD bases on kept pair
    qc.measure(0, 2); qc.measure(1, 3)                 # Alice->c2, Bob->c3
    return qc


def _bits(counts):
    """(a=c2, b=c3, coincidence=c0==c1, count). String 'c3c2c1c0'. Faded: c0=c1=0 -> coin always."""
    for bstr, c in counts.items():
        b = bstr.replace(" ", "")
        yield int(b[-3]), int(b[-4]), (b[-1] == b[-2]), c


def _Eq(counts, shots):
    tot = sum(c for _, _, coin, c in _bits(counts) if coin)
    if tot == 0: return 0.0
    return sum((1 - 2 * a) * (1 - 2 * bb) * c for a, bb, coin, c in _bits(counts) if coin) / tot


def _qberq(counts, shots):
    tot = sum(c for _, _, coin, c in _bits(counts) if coin)
    if tot == 0: return 0.5
    return sum(c for a, bb, coin, c in _bits(counts) if coin and a != bb) / tot


def _psucc(counts, shots):
    return sum(c for _, _, coin, c in _bits(counts) if coin) / shots


def analyze(gc, shots):
    out = {}
    for arm in ARMS:
        E = {(a, b): _Eq(gc(arm, a, b), shots) for a, b in CHSH_BASES}
        S = E[("Z", "W")] + E[("Z", "V")] + E[("X", "W")] - E[("X", "V")]
        qz = _qberq(gc(arm, "Z", "Z"), shots); qx = _qberq(gc(arm, "X", "X"), shots)
        qavg = (qz + qx) / 2
        sf = max(0.0, 1 - 2 * _h2(qavg))
        p = _psucc(gc(arm, "Z", "Z"), shots) if arm == "purified" else 1.0
        abits, bbits = [], []
        for a, bb, coin, c in _bits(gc(arm, "Z", "Z")):
            if coin: abits += [a] * c; bbits += [bb] * c
        out[arm] = {"S": float(S), "qber_z": float(qz), "qber_x": float(qx), "qber_avg": float(qavg),
                    "secret_fraction": float(sf), "p_success": float(p),
                    "alice_key": abits[:len(MESSAGE) * 8], "bob_key": bbits[:len(MESSAGE) * 8]}
    return out


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 6000
    print("Exp167 selftest")
    cache = {}
    def gc(arm, a, b, rz=0.0):
        k = (arm, a, b, rz)
        if k not in cache:
            cache[k] = sim.run(circuit(arm, a, b, TAU_US, rz), shots=shots).result().get_counts()
        return cache[k]
    r = analyze(lambda arm, a, b: gc(arm, a, b, 0.0), shots)
    print(f"  [A] noiseless: faded S={r['faded']['S']:.3f} SF={r['faded']['secret_fraction']:.3f} | "
          f"purified S={r['purified']['S']:.3f} SF={r['purified']['secret_fraction']:.3f} p={r['purified']['p_success']:.2f}")
    assert r["faded"]["S"] > 2.79 and r["purified"]["S"] > 2.79, "noiseless algebra FAIL"
    r2 = analyze(lambda arm, a, b: gc(arm, a, b, 0.9), shots)
    f, p = r2["faded"], r2["purified"]
    print(f"  [B] injected Rz(0.9): faded S={f['S']:.3f} QBER_x={f['qber_x']:.3f} SF={f['secret_fraction']:.3f}")
    print(f"                     purified S={p['S']:.3f} QBER_x={p['qber_x']:.3f} SF={p['secret_fraction']:.3f}")
    assert p["S"] > f["S"] + 0.2 and p["qber_x"] < f["qber_x"] and p["secret_fraction"] > f["secret_fraction"], \
        "purification must fatten the key in sim"
    print("SELFTEST PASS: algebra exact; distillation raises S, lowers QBER, fattens the secret "
          "fraction on the dephasing class. Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    circuits, order = [], []
    for arm in ARMS:
        for a, b in KEY_BASES + CHSH_BASES:
            circuits.append(transpile(circuit(arm, a, b), backend=backend, optimization_level=3))
            order.append([arm, a, b])
    sampler = SamplerV2(mode=backend); job = sampler.run(circuits, shots=shots)
    manifest = {"exp": 167, "slug": "purified_qkd", "backend": backend_name, "shots": shots,
                "job_id": job.job_id(), "order": order, "tau_us": TAU_US, "message": MESSAGE,
                "prereg": {"primary": "SF_purified > SF_faded; purified delivers positive key + OTP",
                           "prediction": "SF_faded 0-0.06, SF_purified 0.10-0.40; P(fatter) 0.6; "
                                         "null = DEJMPS depth eats the gain (prices composition)"}}
    out = os.path.join(HERE, "..", "results", "exp167_purified_qkd_manifest.json")
    json.dump(manifest, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    mp = os.path.join(HERE, "..", "results", "exp167_purified_qkd_manifest.json")
    svc = _get_ibm_service(); man = json.load(open(mp)); res = svc.job(man["job_id"]).result()
    shots = man["shots"]
    raw = {}
    for idx, (arm, a, b) in enumerate(man["order"]):
        r = res[idx]; reg = list(r.data.keys())[0]
        raw[(arm, a, b)] = getattr(r.data, reg).get_counts()
    r = analyze(lambda arm, a, b: raw[(arm, a, b)], shots)
    f, p = r["faded"], r["purified"]
    se_S = 2.0 / np.sqrt(shots)
    print(f"Exp167 PURIFY->QKD decode | job {man['job_id']} | backend {man['backend']} | tau={man['tau_us']}us")
    print(f"  FADED    : S={f['S']:.3f}  QBER z/x={f['qber_z']:.3f}/{f['qber_x']:.3f}  "
          f"secret_fraction={f['secret_fraction']:.3f}")
    print(f"  PURIFIED : S={p['S']:.3f}  QBER z/x={p['qber_z']:.3f}/{p['qber_x']:.3f}  "
          f"secret_fraction={p['secret_fraction']:.3f}  (p_success={p['p_success']:.2f})")
    dSF = p["secret_fraction"] - f["secret_fraction"]
    fatter = p["secret_fraction"] > f["secret_fraction"] and (p["S"] - 2) / se_S > 5
    print(f"\nKEY DELTA: secret fraction {f['secret_fraction']:.3f} -> {p['secret_fraction']:.3f} "
          f"({dSF:+.3f}) | S {f['S']:.2f} -> {p['S']:.2f} | QBER_x {f['qber_x']:.2f} -> {p['qber_x']:.2f}")
    msg = man["message"]
    if p["secret_fraction"] > 0 and len(p["alice_key"]) >= len(msg) * 8:
        enc = _otp(msg, p["alice_key"]); dec = _otp(enc, p["bob_key"]).decode(errors="replace")
        good = sum(1 for x, y in zip(dec, msg) if x == y) / len(msg)
        print(f"PURIFIED CHANNEL: '{msg}' -> {enc.hex()} -> '{dec}' ({100*good:.0f}% chars)")
    fdead = f["secret_fraction"] < 0.02
    print(f"FADED CHANNEL: {'DEAD (no key at this fidelity)' if fdead else 'thin key'} "
          f"— {'purification is what makes the channel usable' if fdead and fatter else 'compare above'}")
    tag = ("PURIFICATION FATTENS THE KEY — distilling first turns a degraded channel into a keyed one"
           if fatter else "NULL — DEJMPS overhead did not net a fatter key at this depth (honest accounting)")
    print(f"VERDICT: {tag}")
    out = {"job_id": man["job_id"], "faded": {k: v for k, v in f.items() if "key" not in k},
           "purified": {k: v for k, v in p.items() if "key" not in k},
           "delta_secret_fraction": float(dSF), "fatter": bool(fatter), "verdict": tag}
    json.dump(out, open(os.path.join(HERE, "..", "results", "exp167_purified_qkd_decode.json"), "w"), indent=1)
    print("-> results/exp167_purified_qkd_decode.json")


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
