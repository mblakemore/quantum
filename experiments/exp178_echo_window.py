#!/usr/bin/env python3
"""Exp178 — THE ECHO THROUGH THE WINDOW: is the measurement-window tax coherent? C4865.
Exp177: the mid-circuit measurement window dominates the 2-swap chain deficit (0.330 of 0.516).
This flight inserts a minimal Hahn echo — one simultaneous X on both end-qubits (A,D) at the
midpoint BETWEEN the two measurement windows. X(x)X leaves |Phi+> invariant (no closing gates, no
frame change); each end-qubit's window-1 phase inverts and window-2 cancels it IF the noise is
quasi-static/coherent. Echo-recoverable => software+pulse path. Echo-immune => irreversible
measurement backaction, hardware-only fix.
Arms: live | liveecho | deferred (Pauli frame, Exp177) | defecho (frame+echo, the full stack) |
direct. Frame algebra unchanged from Exp177 (x=c3^c1, z=c2^c0 on D).
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
from exp162_swap import fidelity

ARMS = ("live", "liveecho", "deferred", "defecho", "direct")
FRAMED = ("deferred", "defecho")
ECHOED = ("liveecho", "defecho")
SETTINGS = ("ZZ", "XX", "YY")
WITNESS = 0.5


def _verify_rot(qc, setting, qubits):
    for q in qubits:
        if setting == "XX": qc.h(q)
        elif setting == "YY": qc.sdg(q); qc.h(q)


def chain_circuit(arm, setting):
    """A=q0,B1=q1,B2=q2,C1=q3,C2=q4,D=q5. c0,c1 stage1; c2,c3 stage2; c4=A, c5=D."""
    qc = QuantumCircuit(6, 6)
    if arm == "direct":
        qc.h(0); qc.cx(0, 1)
        _verify_rot(qc, setting, (0, 1))
        qc.measure(0, 4); qc.measure(1, 5)
        return qc
    live = arm in ("live", "liveecho")
    qc.h(0); qc.cx(0, 1)          # Bell(A,B1)
    qc.h(2); qc.cx(2, 3)          # Bell(B2,C1)
    qc.h(4); qc.cx(4, 5)          # Bell(C2,D)
    qc.barrier()
    qc.cx(1, 2); qc.h(1)          # stage-1 Bell measurement window
    qc.measure(1, 0); qc.measure(2, 1)
    if live:
        with qc.if_test((qc.clbits[1], 1)): qc.x(3)
        with qc.if_test((qc.clbits[0], 1)): qc.z(3)
    if arm in ECHOED:
        qc.barrier()
        qc.x(0); qc.x(5)          # midpoint Hahn X on both ends: X(x)X keeps Phi+ invariant
    qc.barrier()
    qc.cx(3, 4); qc.h(3)          # stage-2 Bell measurement window
    qc.measure(3, 2); qc.measure(4, 3)
    if live:
        with qc.if_test((qc.clbits[3], 1)): qc.x(5)
        with qc.if_test((qc.clbits[2], 1)): qc.z(5)
    qc.barrier()
    _verify_rot(qc, setting, (0, 5))
    qc.measure(0, 4); qc.measure(5, 5)
    return qc


def _parity(counts, shots, setting, arm):
    """<A D> from c4,c5; per-shot Pauli-frame correction for FRAMED arms ('c5c4c3c2c1c0')."""
    acc = 0
    for b, n in counts.items():
        b = b.replace(" ", "")
        a = int(b[-5]); d = int(b[-6])
        if arm in FRAMED:
            c0, c1, c2, c3 = int(b[-1]), int(b[-2]), int(b[-3]), int(b[-4])
            if setting == "ZZ": d ^= c3 ^ c1
            elif setting == "XX": d ^= c2 ^ c0
            else: d ^= c0 ^ c1 ^ c2 ^ c3
        acc += (1 - 2 * a) * (1 - 2 * d) * n
    return acc / shots


def analyze(get, shots):
    out = {}
    for arm in ARMS:
        par = {s: _parity(get(arm, s), shots, s, arm) for s in SETTINGS}
        out[arm] = {"F": float(fidelity(par)), **{k: float(v) for k, v in par.items()}}
    return out


def gains(r, shots):
    se_F = 0.75 / np.sqrt(shots); se_d = float(np.sqrt(2) * se_F)
    g_def = r["defecho"]["F"] - r["deferred"]["F"]
    g_live = r["liveecho"]["F"] - r["live"]["F"]
    branch = ("substantially coherent (software+pulse path viable)" if g_def >= 0.10 else
              ("echo-immune -> irreversible measurement backaction (hardware-only fix)"
               if g_def < 0.03 and abs(g_def) <= 2 * se_d else "mixed noise, partial coherence"))
    return {"echo_gain_deferred": float(g_def), "echo_gain_deferred_sigma": float(g_def / se_d),
            "echo_gain_live": float(g_live), "echo_gain_live_sigma": float(g_live / se_d),
            "se_delta": se_d, "branch": branch}


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 8000
    cache = {}
    def get(arm, s):
        if (arm, s) not in cache:
            cache[(arm, s)] = sim.run(chain_circuit(arm, s), shots=shots).result().get_counts()
        return cache[(arm, s)]
    r = analyze(get, shots)
    print("Exp178 selftest (noiseless Aer)")
    for arm in ARMS:
        print(f"  {arm:>8}: ZZ={r[arm]['ZZ']:+.2f} XX={r[arm]['XX']:+.2f} YY={r[arm]['YY']:+.2f} "
              f"-> F={r[arm]['F']:.3f}")
        assert r[arm]["F"] > 0.99, f"{arm} must be exact (echo X(x)X invariance + frame algebra)"
    print("SELFTEST PASS: midpoint X_A X_D leaves Phi+ exactly invariant in live and frame-tracked "
          "chains; all five arms exact noiseless. Cleared to fly.")


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
    manifest = {"exp": 178, "slug": "echo_window", "backend": backend_name, "shots": shots,
                "job_id": job.job_id(), "order": order, "witness": WITNESS,
                "prereg": {"primary": "F(defecho)-F(deferred) > 0 at >=3 sigma",
                           "secondary": "F(liveecho)-F(live) > 0 at >=3 sigma",
                           "branches": ">=+0.10 coherent | <+0.03 & <=2sigma echo-immune (backaction) | else mixed",
                           "band": "live 0.42-0.58; liveecho +0.00-0.15 over live; deferred 0.50-0.62; "
                                   "defecho 0.55-0.75; direct 0.95-0.99; ceiling ref endmeasure 0.885 (Exp177)",
                           "fingerprint": "recovery XX/YY-concentrated, ZZ flat"}}
    out = os.path.join(HERE, "..", "results", "exp178_echo_window_manifest.json")
    json.dump(manifest, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    mp = os.path.join(HERE, "..", "results", "exp178_echo_window_manifest.json")
    svc = _get_ibm_service(); man = json.load(open(mp)); res = svc.job(man["job_id"]).result()
    shots = man["shots"]
    raw = {}
    for idx, (arm, s) in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[(arm, s)] = getattr(r0.data, reg).get_counts()
    r = analyze(lambda arm, s: raw[(arm, s)], shots)
    g = gains(r, shots)
    print(f"Exp178 ECHO THROUGH THE WINDOW decode | job {man['job_id']} | backend {man['backend']}")
    for arm in ARMS:
        print(f"  {arm:>8}: ZZ={r[arm]['ZZ']:+.3f} XX={r[arm]['XX']:+.3f} YY={r[arm]['YY']:+.3f} "
              f"-> F = {r[arm]['F']:.3f}")
    print(f"\nECHO GAIN (frame-tracked chain): {g['echo_gain_deferred']:+.3f} "
          f"({g['echo_gain_deferred_sigma']:+.1f} sigma)")
    print(f"ECHO GAIN (live chain):          {g['echo_gain_live']:+.3f} "
          f"({g['echo_gain_live_sigma']:+.1f} sigma)")
    print(f"BRANCH: {g['branch']}")
    print(f"CEILING: Exp177 endmeasure 0.885 | tonight's best stack: defecho {r['defecho']['F']:.3f}")
    ok = g["echo_gain_deferred"] > 0 and g["echo_gain_deferred_sigma"] >= 3
    print(f"PRIMARY: {'HELD — the window tax is (at least partly) coherent and echo-recoverable' if ok else 'NOT HELD (see branch — a null here is the discriminator firing, not a failed experiment)'}")
    out = {"job_id": man["job_id"], "results": r, "gains": g, "verdict_ok": bool(ok)}
    json.dump(out, open(os.path.join(HERE, "..", "results", "exp178_echo_window_decode.json"), "w"), indent=1)
    print("-> results/exp178_echo_window_decode.json")


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
