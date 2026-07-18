#!/usr/bin/env python3
"""Exp180 — THE RELAY KEY: E91 QKD through swapped links, frame-steered sifting. C4867.
The stack (swap 162 + frame 177 + echo 178 + merged window 179) used for its purpose: a
physics-certified key (CHSH S > 2, Ekert) through relay stations nobody trusts.

FRAME-STEERED SIFTING: CHSH angles are non-Clifford, so a pending Pauli frame (x,z) on Bob's
qubit cannot be XORed away. Conjugation gives the exact sifting rule the relay's published
outcomes enable:  X^x Z^z A(theta) Z^z X^x = (-1)^x * A((-1)^(x XOR z) * theta).
Per shot: flip the outcome sign by (-1)^x, steer the effective Bob angle between +-pi/4 by
x XOR z. Every shot lands in a valid CHSH term. Key setting (theta=0) reduces to the XOR rule.

Arms: direct | key1relay (1 swap + frame + engineered Hahn) | key2relay (2 swaps, merged window
+ frame + Hahn) | nomeas (falsifier: no Bell measurement -> never entangled -> S ~ 0).
Settings: 4 CHSH pairs (a in {0,pi/2} x b in {+-pi/4}) + 1 key pair (0,0).
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit import Delay

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

ARMS = ("direct", "key1relay", "key2relay", "nomeas")
A_ANGLES = (0.0, np.pi / 2)
B_ANGLES = (np.pi / 4, -np.pi / 4)
SETTINGS = [("chsh_a0_bp", 0.0, np.pi / 4), ("chsh_a0_bm", 0.0, -np.pi / 4),
            ("chsh_a1_bp", np.pi / 2, np.pi / 4), ("chsh_a1_bm", np.pi / 2, -np.pi / 4),
            ("key", 0.0, 0.0)]


def circuit(arm, ta, tb, delay_dt=0):
    """Ends carry the pair; measure A(q_a)->c4, B(q_b)->c5. Frame bits c0..c3 (chain arms)."""
    qc = QuantumCircuit(6, 6)
    if arm == "direct":
        qa, qb = 0, 1
        qc.h(0); qc.cx(0, 1)
    elif arm == "key1relay":
        qa, qb = 0, 3
        qc.h(0); qc.cx(0, 1)      # Bell(A,B1)
        qc.h(2); qc.cx(2, 3)      # Bell(B2,D)
        qc.barrier()
        qc.cx(1, 2); qc.h(1)      # relay Bell measurement (one window)
        qc.measure(1, 0); qc.measure(2, 1)
        qc.barrier()
        qc.x(0); qc.x(3)          # engineered Hahn on the ends
        if delay_dt > 0:
            qc.append(Delay(delay_dt, unit="dt"), [0]); qc.append(Delay(delay_dt, unit="dt"), [3])
        qc.x(0); qc.x(3)
    else:  # key2relay / nomeas — 2-swap chain, merged single window (Exp179 architecture)
        qa, qb = 0, 5
        qc.h(0); qc.cx(0, 1)      # Bell(A,B1)
        qc.h(2); qc.cx(2, 3)      # Bell(B2,C1)
        qc.h(4); qc.cx(4, 5)      # Bell(C2,D)
        qc.barrier()
        qc.cx(1, 2); qc.h(1)
        qc.cx(3, 4); qc.h(3)
        qc.barrier()
        if arm == "key2relay":
            qc.measure(1, 0); qc.measure(2, 1)   # the merged window
            qc.measure(3, 2); qc.measure(4, 3)
            qc.barrier()
            qc.x(0); qc.x(5)                     # engineered Hahn
            if delay_dt > 0:
                qc.append(Delay(delay_dt, unit="dt"), [0]); qc.append(Delay(delay_dt, unit="dt"), [5])
            qc.x(0); qc.x(5)
        # nomeas: middles never measured -> A and D never entangled (falsifier)
    qc.barrier()
    qc.ry(-ta, qa); qc.ry(-tb, qb)               # measure A(theta) = Ry(-theta) then Z
    qc.measure(qa, 4); qc.measure(qb, 5)
    return qc


def _frame(arm, b):
    """(x, z) pending frame on Bob's qubit from the relay's published bits."""
    if arm == "key1relay":
        return int(b[-2]), int(b[-1])                     # x=c1, z=c0 (Exp162 convention)
    if arm == "key2relay":
        return int(b[-4]) ^ int(b[-2]), int(b[-3]) ^ int(b[-1])   # x=c3^c1, z=c2^c0 (Exp177)
    return 0, 0


def tally(get, shots, arm):
    """Frame-steered sifting -> E[(ta,tb)] for all 4 CHSH terms + key stats."""
    num = {(ta, tb): 0.0 for ta in A_ANGLES for tb in B_ANGLES}
    den = {(ta, tb): 0 for ta in A_ANGLES for tb in B_ANGLES}
    key_n = key_err = 0
    for name, ta, tb in SETTINGS:
        for bstr, n in get(arm, name).items():
            b = bstr.replace(" ", "")
            a_bit = int(b[-5]); d_bit = int(b[-6])
            x, z = _frame(arm, b)
            sign = -1 if x else 1
            eff_tb = tb if (x ^ z) == 0 else -tb
            if name == "key":
                d_corr = d_bit ^ x
                key_n += n; key_err += n * (1 if a_bit != d_corr else 0)
            else:
                num[(ta, eff_tb)] += sign * (1 - 2 * a_bit) * (1 - 2 * d_bit) * n
                den[(ta, eff_tb)] += n
    E = {k: (num[k] / den[k] if den[k] else 0.0) for k in num}
    S = (E[(0.0, np.pi / 4)] + E[(0.0, -np.pi / 4)]
         + E[(np.pi / 2, np.pi / 4)] - E[(np.pi / 2, -np.pi / 4)])
    se_S = float(np.sqrt(sum((1 - E[k] ** 2) / den[k] for k in E if den[k])))
    return {"S": float(S), "se_S": se_S,
            "E": {f"{k[0]:.2f},{k[1]:+.2f}": float(v) for k, v in E.items()},
            "qber": float(key_err / key_n) if key_n else None, "key_bits": int(key_n)}


def analyze(get, shots):
    return {arm: tally(get, shots, arm) for arm in ARMS}


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 8000
    cache = {}
    def get(arm, name):
        if (arm, name) not in cache:
            _, ta, tb = next(s for s in SETTINGS if s[0] == name)
            cache[(arm, name)] = sim.run(circuit(arm, ta, tb), shots=shots).result().get_counts()
        return cache[(arm, name)]
    r = analyze(get, shots)
    print("Exp180 selftest (noiseless Aer)")
    for arm in ARMS:
        q = f"{r[arm]['qber']:.3f}" if r[arm]["qber"] is not None else "-"
        print(f"  {arm:>9}: S={r[arm]['S']:+.3f} (se {r[arm]['se_S']:.3f})  QBER={q}")
    for arm in ("direct", "key1relay", "key2relay"):
        assert r[arm]["S"] > 2.79, f"{arm}: steering decoder must recover S=2sqrt2 exactly"
        assert r[arm]["qber"] < 0.01, f"{arm}: key must be error-free noiseless"
    assert abs(r["nomeas"]["S"]) < 0.15 and abs(r["nomeas"]["qber"] - 0.5) < 0.05, "nomeas must be uncorrelated"
    print("SELFTEST PASS: frame-steered sifting recovers S=2.83 exactly through 1-swap and merged "
          "2-swap links (all (x,z) branches exercised); falsifier flat. Cleared to fly.")


def _measure_delay_dt(backend):
    try:
        dur_s = max(p.duration for (q,), p in backend.target["measure"].items()
                    if p is not None and p.duration)
        dt = backend.dt or 5e-10
        g = getattr(backend.target, "granularity", 16) or 16
        return max(int(round(dur_s / dt / g)) * g, g)
    except Exception as e:
        print(f"  (measure-duration query failed: {e}; falling back to 2800 dt)")
        return 2800


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    delay_dt = _measure_delay_dt(backend)
    print(f"engineered-Hahn delay: {delay_dt} dt")
    circuits, order = [], []
    for arm in ARMS:
        for name, ta, tb in SETTINGS:
            circuits.append(transpile(circuit(arm, ta, tb, delay_dt), backend=backend,
                                      optimization_level=3))
            order.append([arm, name])
    sampler = SamplerV2(mode=backend); job = sampler.run(circuits, shots=shots)
    manifest = {"exp": 180, "slug": "relay_key", "backend": backend_name, "shots": shots,
                "job_id": job.job_id(), "order": order, "delay_dt": int(delay_dt),
                "prereg": {"primary": "S(key1relay) > 2 at >=3 sigma AND QBER(key1relay) < 0.11",
                           "model_test": "S(key2relay) in 1.85-2.10, point 1.97; certified violation "
                                         "would mean plateau pricing too pessimistic",
                           "ordering": "S(direct) > S(key1relay) > S(key2relay) at high sigma",
                           "bands": "S: direct 2.6-2.8, key1 2.10-2.40, key2 1.85-2.10, nomeas |S|<0.15; "
                                    "QBER: direct 1-3%, key1 5-9%, key2 8-13%, nomeas ~50%",
                           "scope": "raw sifted bits + CHSH certificate; no EC/PA/auth"}}
    out = os.path.join(HERE, "..", "results", "exp180_relay_key_manifest.json")
    json.dump(manifest, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    mp = os.path.join(HERE, "..", "results", "exp180_relay_key_manifest.json")
    svc = _get_ibm_service(); man = json.load(open(mp)); res = svc.job(man["job_id"]).result()
    shots = man["shots"]
    raw = {}
    for idx, (arm, name) in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[(arm, name)] = getattr(r0.data, reg).get_counts()
    r = analyze(lambda arm, name: raw[(arm, name)], shots)
    print(f"Exp180 RELAY KEY decode | job {man['job_id']} | backend {man['backend']}")
    for arm in ARMS:
        q = f"{r[arm]['qber']*100:.1f}%" if r[arm]["qber"] is not None else "-"
        nsig = (r[arm]["S"] - 2) / r[arm]["se_S"]
        print(f"  {arm:>9}: S = {r[arm]['S']:+.3f} +- {r[arm]['se_S']:.3f} "
              f"({nsig:+.1f} sigma vs classical 2) | QBER {q}")
    k1, k2 = r["key1relay"], r["key2relay"]
    sig1 = (k1["S"] - 2) / k1["se_S"]
    p_ok = k1["S"] > 2 and sig1 >= 3 and k1["qber"] < 0.11
    print(f"\nPRIMARY: S(key1relay)={k1['S']:.3f} ({sig1:+.1f} sigma over 2), QBER {k1['qber']*100:.1f}% "
          f"-> {'HELD — A PHYSICS-CERTIFIED KEY PASSED THROUGH A RELAY' if p_ok else 'NOT HELD (honest accounting above)'}")
    print(f"MODEL TEST: S(key2relay)={k2['S']:.3f} vs point prediction 1.97 "
          f"(band 1.85-2.10) -> {'IN BAND' if 1.85 <= k2['S'] <= 2.10 else 'OUT OF BAND'}; "
          f"{'certified violation — plateau pricing too pessimistic' if (k2['S']-2)/k2['se_S'] >= 3 else 'no certified violation — consistent with the plateau model'}")
    print(f"ORDERING: direct {r['direct']['S']:.3f} > key1 {k1['S']:.3f} > key2 {k2['S']:.3f} : "
          f"{'HELD' if r['direct']['S'] > k1['S'] > k2['S'] else 'VIOLATED'}")
    print(f"FALSIFIER: nomeas S={r['nomeas']['S']:+.3f}, QBER {r['nomeas']['qber']*100:.0f}% "
          f"({'flat as required' if abs(r['nomeas']['S']) < 0.15 else 'NOT FLAT'})")
    out = {"job_id": man["job_id"], "results": r, "primary_ok": bool(p_ok)}
    json.dump(out, open(os.path.join(HERE, "..", "results", "exp180_relay_key_decode.json"), "w"), indent=1)
    print("-> results/exp180_relay_key_decode.json")


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
