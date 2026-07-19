#!/usr/bin/env python3
"""Exp191 — THE SHIELDED HANDSHAKE: a logical Bell pair between two [[4,2,2]] blocks. C4883.
Shields stage (iii). Block A |+bar 0bar> = Bell(0,1)(x)Bell(2,3); block B |0bar 0bar> = GHZ4;
TRANSVERSAL CNOT (qi -> qi+4, 4 CXs — the FT-native gate) -> logical pair L1 entangled across
blocks while L2 rides along in a PRODUCT state: the in-shot internal control that must sit
exactly AT the separable bound S = <XbarXbar>+<ZbarZbar> <= 1 while L1 crosses it.
Readout: Zbar1 = z0^z2 | z4^z6; Xbar1 = x0^x1 | x4^x5; Zbar2 = z0^z1 | z4^z5;
Xbar2 = x0^x2 | x4^x6; postselect per-block stabilizer parity per basis.
Arms: logical | logical_idle (0.5us quarter-echoed — stage-ii operating point) | nocx | bare.
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit import Delay

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

IDLE_DT = 1000   # ~0.5 us
ARMS = ("logical", "logical_idle", "nocx", "bare")


def _echo_idle(qc, qubits, total_dt):
    q4 = (total_dt // 4 // 16) * 16
    for q in qubits: qc.append(Delay(q4, unit="dt"), [q])
    for q in qubits: qc.x(q)
    for q in qubits: qc.append(Delay(total_dt - 2 * q4, unit="dt"), [q])
    for q in qubits: qc.x(q)
    for q in qubits: qc.append(Delay(q4, unit="dt"), [q])


def circuit(arm, basis):
    if arm == "bare":
        qc = QuantumCircuit(2, 2)
        qc.h(0); qc.cx(0, 1)
        qc.barrier()
        if basis == "X": qc.h(0); qc.h(1)
        qc.measure(0, 0); qc.measure(1, 1)
        return qc
    qc = QuantumCircuit(8, 8)
    qc.h(0); qc.cx(0, 1)          # block A: |+bar 0bar> = Bell(0,1) (x) Bell(2,3)
    qc.h(2); qc.cx(2, 3)
    qc.h(4); qc.cx(4, 5); qc.cx(4, 6); qc.cx(4, 7)   # block B: |0bar 0bar> = GHZ4
    qc.barrier()
    if arm != "nocx":
        for i in range(4): qc.cx(i, i + 4)           # TRANSVERSAL logical CNOT
    qc.barrier()
    if arm == "logical_idle":
        _echo_idle(qc, list(range(8)), IDLE_DT)
        qc.barrier()
    if basis == "X":
        for q in range(8): qc.h(q)
    for q in range(8): qc.measure(q, q)
    return qc


def _stats(counts, basis, arm):
    """Postselect per-block stabilizer parity; logical correlators for L1 and L2."""
    if arm == "bare":
        acc = c = 0
        for s, n in counts.items():
            b = s.replace(" ", "")
            acc += n; c += n * (1 - 2 * (int(b[-1]) ^ int(b[-2])))
        return {"acceptance": 1.0, "corr_L1": c / acc, "corr_L2": None}
    accepted = rej = 0; c1 = c2 = 0
    for s, n in counts.items():
        b = s.replace(" ", "")
        v = [int(b[-1 - i]) for i in range(8)]
        pA = v[0] ^ v[1] ^ v[2] ^ v[3]; pB = v[4] ^ v[5] ^ v[6] ^ v[7]
        if pA or pB:
            rej += n; continue
        accepted += n
        if basis == "Z":
            l1 = (v[0] ^ v[2]) ^ (v[4] ^ v[6]); l2 = (v[0] ^ v[1]) ^ (v[4] ^ v[5])
        else:
            l1 = (v[0] ^ v[1]) ^ (v[4] ^ v[5]); l2 = (v[0] ^ v[2]) ^ (v[4] ^ v[6])
        c1 += n * (1 - 2 * l1); c2 += n * (1 - 2 * l2)
    return {"acceptance": accepted / (accepted + rej),
            "corr_L1": c1 / accepted if accepted else 0.0,
            "corr_L2": c2 / accepted if accepted else 0.0,
            "n_acc": accepted}


def analyze(get):
    r = {}
    for arm in ARMS:
        z = _stats(get(arm, "Z"), "Z", arm)
        x = _stats(get(arm, "X"), "X", arm)
        rec = {"ZZ_L1": float(z["corr_L1"]), "XX_L1": float(x["corr_L1"]),
               "S_L1": float(z["corr_L1"] + x["corr_L1"]),
               "acc_Z": float(z["acceptance"]), "acc_X": float(x["acceptance"])}
        if arm != "bare":
            rec.update({"ZZ_L2": float(z["corr_L2"]), "XX_L2": float(x["corr_L2"]),
                        "S_L2": float(z["corr_L2"] + x["corr_L2"]),
                        "n_acc_Z": z.get("n_acc", 0), "n_acc_X": x.get("n_acc", 0)})
        r[arm] = rec
    return r


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 8000
    cache = {}
    def get(arm, basis):
        k = (arm, basis)
        if k not in cache:
            cache[k] = sim.run(circuit(arm, basis), shots=shots).result().get_counts()
        return cache[k]
    r = analyze(get)
    print("Exp191 selftest (noiseless Aer)")
    for arm in ARMS:
        s2 = f"  S_L2={r[arm]['S_L2']:.3f}" if "S_L2" in r[arm] else ""
        print(f"  {arm:>12}: S_L1={r[arm]['S_L1']:.3f}{s2}  (acc {r[arm]['acc_Z']:.2f}/{r[arm]['acc_X']:.2f})")
    assert abs(r["logical"]["S_L1"] - 2) < 0.03, "logical Bell must be exact"
    assert abs(r["logical"]["S_L2"] - 1) < 0.03, "L2 control must sit EXACTLY at the separable bound"
    assert abs(r["logical_idle"]["S_L1"] - 2) < 0.03 and abs(r["logical_idle"]["S_L2"] - 1) < 0.03
    assert abs(r["nocx"]["S_L1"]) < 0.04 and abs(r["nocx"]["S_L2"] - 1) < 0.03, "nocx: L1 dead, L2 at bound"
    assert abs(r["bare"]["S_L1"] - 2) < 0.03
    print("SELFTEST PASS: transversal CNOT entangles L1 across blocks exactly (S=2) while L2 sits "
          "exactly at the separable bound (S=1) in the same shots; nocx kills L1 only. Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    circuits, order = [], []
    for arm in ARMS:
        for basis in ("Z", "X"):
            circuits.append(transpile(circuit(arm, basis), backend=backend, optimization_level=3))
            order.append([arm, basis])
    sampler = SamplerV2(mode=backend); job = sampler.run(circuits, shots=shots)
    manifest = {"exp": 191, "slug": "logical_bell", "backend": backend_name, "shots": shots,
                "job_id": job.job_id(), "order": order,
                "prereg": {"primary": "S_L1(logical) > 1 at (S-1)/se >= 5; band 1.55-1.85",
                           "internal_control": "S_L2(logical) in 0.85-1.05 (AT the bound)",
                           "operating_point": "S_L1(logical_idle) > 1 at >=5 sigma; band 1.35-1.75",
                           "falsifier": "S_L1(nocx) in -0.10..0.15 AND S_L2(nocx) in 0.85-1.05",
                           "reference": "S_bare 1.80-1.95", "gauges": "block-pair acceptance >= 0.70/basis"}}
    out = os.path.join(HERE, "..", "results", "exp191_logical_bell_manifest.json")
    json.dump(manifest, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    mp = os.path.join(HERE, "..", "results", "exp191_logical_bell_manifest.json")
    svc = _get_ibm_service(); man = json.load(open(mp)); res = svc.job(man["job_id"]).result()
    shots = man["shots"]
    raw = {}
    for idx, (arm, basis) in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[(arm, basis)] = getattr(r0.data, reg).get_counts()
    r = analyze(lambda arm, basis: raw[(arm, basis)])
    def seS(arm):
        nz = r[arm].get("n_acc_Z", shots); nx = r[arm].get("n_acc_X", shots)
        return float(np.sqrt(1 / max(nz, 1) + 1 / max(nx, 1)))
    print(f"Exp191 SHIELDED HANDSHAKE decode | job {man['job_id']} | backend {man['backend']}")
    for arm in ARMS:
        s2 = f"  S_L2={r[arm]['S_L2']:+.3f}" if "S_L2" in r[arm] else ""
        print(f"  {arm:>12}: ZZ={r[arm]['ZZ_L1']:+.3f} XX={r[arm]['XX_L1']:+.3f} -> S_L1={r[arm]['S_L1']:+.3f}{s2} "
              f"(acc {r[arm]['acc_Z']:.3f}/{r[arm]['acc_X']:.3f})")
    sL = r["logical"]["S_L1"]; z = (sL - 1) / seS("logical")
    sLi = r["logical_idle"]["S_L1"]; zi = (sLi - 1) / seS("logical_idle")
    p_ok = sL > 1 and z >= 5
    ctrl_ok = 0.85 <= r["logical"]["S_L2"] <= 1.05
    idle_ok = sLi > 1 and zi >= 5
    f_ok = -0.10 <= r["nocx"]["S_L1"] <= 0.15 and 0.85 <= r["nocx"]["S_L2"] <= 1.05
    print(f"\nPRIMARY: S_L1 = {sL:.3f} vs separable bound 1 -> {z:.0f} sigma "
          f"{'HELD — LOGICAL QUBITS ENTANGLED' if p_ok else 'NOT HELD'}")
    print(f"INTERNAL CONTROL: S_L2 = {r['logical']['S_L2']:.3f} "
          f"{'— the product logical pair sits AT the bound, same shots' if ctrl_ok else '— OFF the bound (CHECK)'}")
    print(f"OPERATING POINT: S_L1(idle 0.5us) = {sLi:.3f} ({zi:.0f} sigma) {'HELD' if idle_ok else 'NOT HELD'}")
    print(f"FALSIFIER: nocx S_L1 = {r['nocx']['S_L1']:+.3f}, S_L2 = {r['nocx']['S_L2']:.3f} "
          f"{'(L1 dead, L2 at bound — as required)' if f_ok else '(CHECK)'}")
    print(f"REFERENCE: S_bare = {r['bare']['S_L1']:.3f}")
    ok = p_ok and ctrl_ok and idle_ok and f_ok
    print(f"VERDICT: {'THE SHIELDED HANDSHAKE — two logical qubits, in two shields, certified entangled (with the product pair calibrating the bound in-shot)' if ok else 'NOT HELD (honest accounting above)'}")
    out = {"job_id": man["job_id"], "results": r, "sigma_primary": float(z), "sigma_idle": float(zi),
           "primary_ok": bool(p_ok), "control_ok": bool(ctrl_ok), "idle_ok": bool(idle_ok),
           "falsifier_ok": bool(f_ok), "verdict_ok": bool(ok)}
    json.dump(out, open(os.path.join(HERE, "..", "results", "exp191_logical_bell_decode.json"), "w"), indent=1)
    print("-> results/exp191_logical_bell_decode.json")


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
